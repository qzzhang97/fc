import matplotlib as mpl 
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.use('Agg')
mpl.rcParams['hatch.linewidth'] = 2

import matplotlib.pyplot as plt 
import numpy as np
import os

if __name__ == "__main__":

  x_marker = ["FC", "Xpander", "Jellyfish"]
  
  fc_probs = [0, 0.20, 0.57]
  xpander_probs = [0.14, 0.39, 0.68]
  jf_probs = [0.06, 0.20, 0.58]
  
  xpander_txt = ["(32, 7)", "(64, 15)", "(128, 15)"]
  jf_txt = ["(32, 7)", "(64, 12)", "(128, 16)"]
  fc_txt = ["(32, 10, [3, 5, 2])", "(64, 12, [2, 4, 4, 2])", "(128, 16, [3, 5, 5, 3])"]
  
  x = np.arange(len(x_marker))
  width = 0.20
  fig, ax = plt.subplots(figsize=(6,4))

  ax.bar(x - width, fc_probs, width, label="FC", color='lightgreen', ec='gray', hatch='*')
  ax.bar(x, xpander_probs, width, label="Xpander", color='hotpink', ec='gray', hatch='-')
  ax.bar(x + width, jf_probs, width, label="Jellyfish", color='tan', ec='gray', hatch='.')
  
  # ax.text(-0.2,0, "(64, 12, [2, 4, 4, 2])", rotation=-45)

  ax.set_xticks(x)
  ax.set_xticklabels(x_marker)
  ax.set_yticks([i * 0.2 for i in range(6)])
  ax.set_xlabel("Topology", fontsize=20)
  ax.set_ylabel("Probability", fontsize=20)
  ax.tick_params(axis='x', labelsize=18) 
  ax.tick_params(axis='y', labelsize=18) 
  
  
  ax.legend(loc='upper left', fontsize='large')
  
  plt.grid(ls='--')
  fig.tight_layout()


  fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
  # print(fname)
  plt.savefig(fname, bbox_inches='tight')
