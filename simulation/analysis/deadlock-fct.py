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
  return fcts[:1252]

if __name__ == "__main__":

  percentiles = [30, 50, 80, 90, 99]
  path_to_ecmp_fct_file = "../mix/failure-exps/scripts/deadlock/output/ecmp/fct.txt"
    
  path_to_up_down_fct_file = "../mix/failure-exps/scripts/deadlock/output/up-down/fct.txt"
  path_to_edst_fct_file = "../mix/failure-exps/scripts/deadlock/output/edst/fct.txt"
  
  ecmps = []
  up_downs = []
  edsts = []

  for p in percentiles:
    ecmps.append(np.percentile(get_fct(path_to_ecmp_fct_file), p) / 1e6)
    up_downs.append(np.percentile(get_fct(path_to_up_down_fct_file), p) / 1e6)
    edsts.append(np.percentile(get_fct(path_to_edst_fct_file), p) / 1e6)
  
  x = np.arange(len(percentiles))
  width = 0.28
  fig, ax = plt.subplots(figsize=(6,4))

  ax.bar(x - width, ecmps, width, label='ECMP', color='lightgreen', ec='gray', hatch='*')
  ax.bar(x, up_downs, width, label='VIRTUAL UP-DOWN', color='hotpink', ec='gray', hatch='-')
  ax.bar(x + width, edsts, width, label='EDST', color='tan', ec='gray', hatch='.')
  
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
