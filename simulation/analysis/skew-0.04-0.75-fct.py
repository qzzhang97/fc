import matplotlib as mpl 
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.use('Agg')
mpl.rcParams['hatch.linewidth'] = 2

import matplotlib.pyplot as plt 
import numpy as np
import os

def get_fct(file_path):
  # print(file_path)
  fcts = []
  f = open(file_path, mode='r')
  for line in f.read().splitlines():
    fcts.append( int(line.split(' ')[6]) )
  f.close()
  # print(file_path, len(fcts))
  return fcts

if __name__ == "__main__":
  a = 0.05
  
  fat_fct_file = "../mix/output/fat-tree/dcqcn/skew/pfc/web/0.04/0.75/fct.txt" 
  fc_ecmp_fct_file = "../mix/output/fc-ecmp/dcqcn/skew/64/pfc/web/0.04/0.75/fct.txt"
  fc_weighted_fct_file = "../mix/output/fc-weighted/dcqcn/skew/64/pfc/web/0.04/0.75/fct.txt"
  fc_uniform_fct_file = "../mix/output/fc-uniform/dcqcn/skew/64/pfc/web/0.04/0.75/fct.txt"
  fc_lp_fct_file = "../mix/output/fc-lp/dcqcn/skew/64/pfc/web/0.04/0.75/fct.txt"
  fc_cong_fct_file = "../mix/output/fc/dcqcn/skew/64/pfc/web/0.04/0.75/fct.txt"

  edst_weighted_fct_file = "../mix/output/edst-weighted/dcqcn/skew/64/pfc/web/0.04/0.75/fct.txt"
  edst_uniform_fct_file = "../mix/output/edst-uniform/dcqcn/skew/64/pfc/web/0.04/0.75/fct.txt"
  edst_lp_fct_file = "../mix/output/edst-lp/dcqcn/skew/64/pfc/web/0.04/0.75/fct.txt"
  edst_cong_fct_file = "../mix/output/edst/dcqcn/skew/64/pfc/web/0.04/0.75/fct.txt"
  
  percentiles = [30, 50, 80, 90, 99]
  fat_trees = []
  fc_ecmps = []
  fcs = []
  fc_weights = []
  fc_uniforms = []
  fc_lps = []

  edsts = []
  edst_weights = []
  edst_uniforms = []
  edst_lps = []
  for p in percentiles:
    fat_trees.append(np.percentile(get_fct(fat_fct_file), p) / 1e6)
    fc_ecmps.append(np.percentile(get_fct(fc_ecmp_fct_file), p) / 1e6)
    fc_weights.append(np.percentile(get_fct(fc_weighted_fct_file), p) / 1e6)
    edst_weights.append(np.percentile(get_fct(edst_weighted_fct_file), p) / 1e6)
  
  print("clos fct", fat_trees)
  print("ecmp fct", fc_ecmps)
  print("edst fct", edst_weights)
  print("fc fct", fc_weights)

  x = np.arange(len(percentiles))
  width = 0.2
  fig, ax = plt.subplots(figsize=(6,4))

  ax.bar(x - 3*width/2, fat_trees, width, label='CLOS', color='tan', ec='gray', hatch='//')
  ax.bar(x - width/2, fc_ecmps, width, label='ECMP', color='lightgreen', ec='gray', hatch='*')
  ax.bar(x + width/2, edst_weights, width, label='EDST', color='turquoise', ec='gray', hatch='-')
  ax.bar(x + 3*width/2, fc_weights, width, label='FC', color='hotpink', ec='gray', hatch='.')

  ax.set_xticks(x)
  ax.set_xticklabels(percentiles)
  ax.set_yticks([i * 100 for i in range(7)])
  ax.set_xlabel("Percentile", fontsize=20)
  ax.set_ylabel("FCT(ms)", fontsize=20)
  ax.tick_params(axis='x', labelsize=18) 
  ax.tick_params(axis='y', labelsize=18) 
  
  
  ax.legend(loc='upper left', fontsize='large')
  
  plt.grid(ls='--')
  fig.tight_layout()


  fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
  # print(fname)
  plt.savefig(fname, bbox_inches='tight')
