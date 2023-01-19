#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 2023
@author: rodolphe.gintz@igf.finances.gouv.fr
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as tick
from matplotlib.ticker import ScalarFormatter as SF
import locale

# unités françaises : virgule, sépérateur de milliers, unité monétaire
locale.setlocale(locale.LC_ALL, "fr_FR")
plt.rcParams['axes.formatter.use_locale'] = True
monetaire = lambda x, pos=0:'{:,}'.format(int(x)).replace(",", " ")+" €"

# Charte graphique (DSS / IGF)
direction = 'DSS'
charte = {'DSS':{'font' : 'Marianne', 
          'couleurs' : ["#7f7f7f", "#ec792b", "#7f7f7f", 'blue']},
          'IGF':{'font' : 'Cambria', 
          'couleurs' : ['#d69a00', "#008000", 'black', '#C00000']}}
try: 
  plt.rcParams['font.family'] = charte[direction]['font']
except Exception:
    pass
color_ag = charte[direction]['couleurs'][0]
color_cible= charte[direction]['couleurs'][1]
color_axe= charte[direction]['couleurs'][2]
color_delta = charte[direction]['couleurs'][3]

# paramètres généraux : SMIC, seuils de calcul de l'avantage différentiel
smic = 11.07 #SMIC horaire brut au 1er juillet 2022
seuils = [1, 1.3, 2] #seuils de calcul de l'avantage différentiel
x_max = 4 #nb de SMIC max du graphique

# définition des mesures générales en fonction du salaire x, exprimé en part de SMIC
RDBS = lambda x: (x<1.6)*(1.6-x)*smic*.3205*52*35/.6
bandeau_maladie = lambda x: (x<2.5)*x*smic*.06*52*35
bandeau_famille = lambda x: (x<3.5)*x*smic*.018*52*35
ag = lambda x: RDBS(x)+ bandeau_maladie(x) + bandeau_famille(x)
legende_ag = "Droit commun - montant annuel des allègements généraux"

# définition des mesures ciblées sous la forme de dictionnaire de mesures
dispositifs = {
  'ZRR':{'legende' : "ZRR - montant annuel y compris exonérations maladie et famille",
  'reduction': lambda x: (x<1.5)*x*smic*0.209*52*35\
                         + (x>=1.5)*(x<2.4)*(2.4-x)*smic*.209*1.5*52*35/.9                  
                         + bandeau_maladie(x)+bandeau_famille(x)},
  'DFPE':{'legende' : "Déduction forfaitaire pour les particuliers emploeyeurs",
    'reduction': lambda x: 3640},
  'ZRD':{'legende' : "ZRD - montant annuel y compris exonérations maladie et famille",
    'reduction': lambda x: (x<1.4)*x*smic*0.209*52*35\
                           + (x>=1.4)*(x<2.4)*(2.4-x)*smic*.209*1.4*52*35                  
                           + bandeau_maladie(x)+bandeau_famille(x)},
  'ZFU':{'legende' : "ZFU - montant annuel y compris exonérations maladie et famille",
    'reduction': lambda x: (x<1.4)*x*smic*0.209*52*35\
                          + (x>=1.4)*(x<2)*(2-x)*smic*.209*1.4*52*35/.6                  
                          + bandeau_maladie(x)+bandeau_famille(x)},
  'BER':{'legende' : "BER - montant annuel y compris exonérations maladie et famille",
    'reduction': lambda x: (x<1.4)*x*smic*0.209*52*35\
                          + (x>=1.4)*smic*.209*1.4*52*35                  
                          + bandeau_maladie(x)+bandeau_famille(x)}
}

for nom, dispositif in dispositifs.items():
  x = np.linspace(1, x_max, 1000)
  y = [ag(i) for i in x]
  z = [dispositif['reduction'](i) for i in x]
  
  plt.rcParams["figure.figsize"] = (12,6)
  fig, ax = plt.subplots()
  
  ax.xaxis.set_major_locator(plt.MultipleLocator(0.5))
  ax.xaxis.set_minor_locator(plt.MultipleLocator(0.1))
  ax.xaxis.set_minor_formatter(SF())
  ax.tick_params(axis='x', which ='major', labelsize=10, color = color_axe, labelcolor = color_axe)
  ax.tick_params(axis='x', which ='minor', labelsize=6, color = 'none', labelcolor = color_axe, rotation=90)
  ax.yaxis.set_major_locator(plt.MultipleLocator(1000))
  ax.tick_params(axis='y', which ='major', labelsize=10, color = color_axe, labelcolor = color_axe)
  
  ax.yaxis.set_major_formatter(tick.FuncFormatter(monetaire))
  
  ax.spines[['left', 'right', 'top', 'bottom']].set_visible(False)
  [t.set_visible(False) for t in ax.get_yticklines()]
  [t.set_visible(False) for t in ax.get_xticklines()]
  
  ax.grid(which='major', axis='x', linewidth=0.75, linestyle='-', color='0.9')
  ax.grid(which='minor', axis='x', linewidth=0.25, linestyle='-', color='0.9')
  ax.grid(which='major', axis='y', linewidth=0.75, linestyle='-', color='0.9')
  ax.grid(which='minor', axis='y', linewidth=0.25, linestyle='-', color='0.9')
  
  ax.axis([1, x_max, 0, 1E4])
  line1, = ax.plot(x, y, color= color_ag, linewidth=2, label=legende_ag)
  line2, = ax.plot(x, z, color = color_cible, linewidth=2, ls='--', label=dispositif['legende'])
  
  ax.legend(handles=[line1, line2], loc='upper right', edgecolor = 'none', facecolor = 'none')
  
  for seuil in seuils:
      ax.annotate("", xy=(seuil, ag(seuil)), xycoords='data',
              xytext=(seuil, dispositif['reduction'](seuil)), textcoords='data',
              arrowprops=dict(arrowstyle="<->",
              connectionstyle="arc3", color = color_delta))
      
      if abs(ag(seuil)-dispositif['reduction'](seuil))>10:
        pos = -1+2*(ag(seuil)<dispositif['reduction'](seuil))
        
        ax.annotate(monetaire(ag(seuil),0), xy=(seuil, ag(seuil)),  
                xycoords='data', xytext = (0, -2-6*pos), textcoords='offset points', size = 8,
                bbox=dict(boxstyle="round,pad=.3", fc=color_ag, ec='none'))
        ax.annotate(monetaire(dispositif['reduction'](seuil)), xy=(seuil, dispositif['reduction'](seuil)), 
                xycoords='data', xytext=(0, -2+6*pos), textcoords='offset points', size = 8,
                bbox=dict(boxstyle="round,pad=.3", fc=color_cible, ec='none'))
        ax.annotate(r'$\Delta = $' + monetaire((dispositif['reduction'](seuil)-ag(seuil))), 
                xy=(seuil, (dispositif['reduction'](seuil)+ag(seuil))/2),  xycoords='data',
                xytext=(5, 0), textcoords='offset points', size = 8, color = color_delta,
                bbox=dict(boxstyle="round4,pad=.5", ec = 'none', fc='none'))
      else:
        ax.annotate(monetaire(ag(seuil),0), xy=(seuil, ag(seuil)),  
                xycoords='data', xytext = (0, -8), textcoords='offset points', size = 8,
                bbox=dict(boxstyle="round,pad=.3", fc=color_ag, ec='none'))
        
  fig.savefig('ADL_'+nom+'.svg')