import matplotlib as mpl 
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.use('Agg')
mpl.rcParams['hatch.linewidth'] = 2

import matplotlib.pyplot as plt 
import numpy as np
import os

if __name__ == "__main__":

  # x_marker = ["64", "128", "256"]
  
  num_ecmp_paths = [3.29, 4.69, 6.99]
  num_edst_paths = [6, 8, 10]
  num_up_down_paths = [11.03, 15.50, 22.19]
  
  x_marker = ["(64, [2,4,4,2])", "(128, [2,6,6,2])", "(256, [3,7,7,3])"]
  
  x = np.arange(len(x_marker))
  width = 0.20
  fig, ax = plt.subplots(figsize=(6,4))

  ax.bar(x - width, num_ecmp_paths, width, label="ECMP", color='lightgreen', ec='gray', hatch='*')
  ax.bar(x, num_up_down_paths, width, label="VIRTUAL UP-DOWN", color='tan', ec='gray', hatch='.')
  ax.bar(x + width, num_edst_paths, width, label="EDST", color='hotpink', ec='gray', hatch='-')
  
  # ax.text(0, -1, "(64, [2, 4, 4, 2])", fontsize=12,rotation=-15)

  ax.set_xticks(x)
  ax.set_xticklabels(x_marker, fontsize=18, rotation=-10)
  ax.set_yticks([i * 5 for i in range(6)])
  # ax.set_xlabel("Number of Switches", fontsize=20)
  ax.set_ylabel("Number of Paths", fontsize=20)
  ax.tick_params(axis='x', labelsize=18) 
  ax.tick_params(axis='y', labelsize=18) 
  
  
  ax.legend(loc='upper left', fontsize='large')
  
  plt.grid(ls='--')
  fig.tight_layout()


  fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
  # print(fname)
  plt.savefig(fname, bbox_inches='tight')
