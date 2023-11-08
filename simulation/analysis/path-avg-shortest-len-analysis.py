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
  
  ecmp_avg_shortest_path_len = [2.84, 2.96, 3.14]
  edst_avg_shortest_path_len = [4.22, 4.80, 6.00]
  up_down_avg_shortest_path_len = [3.13, 3.29, 3.50]
  
  x_marker = ["(64, [2,4,4,2])", "(128, [2,6,6,2])", "(256, [3,7,7,3])"]
  
  x = np.arange(len(x_marker))
  width = 0.20
  fig, ax = plt.subplots(figsize=(6,4))

  ax.bar(x - width, ecmp_avg_shortest_path_len, width, label="ECMP", color='lightgreen', ec='gray', hatch='*')
  ax.bar(x, up_down_avg_shortest_path_len, width, label="VIRTUAL UP-DOWN", color='tan', ec='gray', hatch='.')
  ax.bar(x + width, edst_avg_shortest_path_len, width, label="EDST", color='hotpink', ec='gray', hatch='-')
  
  # ax.text(0, -1, "(64, [2, 4, 4, 2])", fontsize=12,rotation=-15)

  ax.set_xticks(x)
  ax.set_xticklabels(x_marker, fontsize=18, rotation=-10)
  ax.set_yticks([i * 2 for i in range(5)])
  # ax.set_xlabel("Number of Switches", fontsize=20)
  ax.set_ylabel("Average Shortest Path Len", fontsize=20)
  ax.tick_params(axis='x', labelsize=18) 
  ax.tick_params(axis='y', labelsize=18) 
  
  
  ax.legend(loc='upper left', fontsize='large')
  
  plt.grid(ls='--')
  fig.tight_layout()


  fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
  # print(fname)
  plt.savefig(fname, bbox_inches='tight')
