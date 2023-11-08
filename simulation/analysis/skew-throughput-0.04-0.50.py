import matplotlib as mpl 
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.use('Agg')
mpl.rcParams['hatch.linewidth'] = 4
import matplotlib.pyplot as plt 
import numpy as np
import os


def get_avg_throughput(fct_file):
  f = open(fct_file, mode='r')
  throughtputs = []
  fcts = []
  for line in f.read().splitlines():
    # print(line)
    data = line.split(' ')
    # print(line)
    size = int(data[4])
    fct = int(data[6])

    fcts.append(fct)
    """
    unit is Gbps
    """
    throughtput = float(size * 8) / (fct) 
    throughtputs.append(throughtput)
  f.close()
  return np.average(throughtputs)

if __name__ == "__main__":
  a = 0.05
  
  fat_fct_file = "../mix/output/fat-tree/dcqcn/skew/pfc/web/0.04/0.50/fct.txt" 
  fc_ecmp_fct_file = "../mix/output/fc-ecmp/dcqcn/skew/64/pfc/web/0.04/0.50/fct.txt"
  fc_weighted_fct_file = "../mix/output/fc-weighted/dcqcn/skew/64/pfc/web/0.04/0.50/fct.txt"
  fc_uniform_fct_file = "../mix/output/fc-uniform/dcqcn/skew/64/pfc/web/0.04/0.50/fct.txt"
  fc_lp_fct_file = "../mix/output/fc-lp/dcqcn/skew/64/pfc/web/0.04/0.50/fct.txt"
  fc_cong_fct_file = "../mix/output/fc/dcqcn/skew/64/pfc/web/0.04/0.50/fct.txt"

  edst_weighted_fct_file = "../mix/output/edst-weighted/dcqcn/skew/64/pfc/web/0.04/0.50/fct.txt"
  edst_uniform_fct_file = "../mix/output/edst-uniform/dcqcn/skew/64/pfc/web/0.04/0.50/fct.txt"
  edst_lp_fct_file = "../mix/output/edst-lp/dcqcn/skew/64/pfc/web/0.04/0.50/fct.txt"
  edst_cong_fct_file = "../mix/output/edst/dcqcn/skew/64/pfc/web/0.04/0.50/fct.txt"
  


  
  labels = ["CLOS", "ECMP", "FC","EDST"]
  throughtputs = [
    get_avg_throughput(fat_fct_file),
    get_avg_throughput(fc_ecmp_fct_file), 
    # get_avg_throughput(fc_lp_fct_file), 
    get_avg_throughput(fc_weighted_fct_file), 
    # get_avg_throughput(fc_cong_fct_file), 
    # get_avg_throughput(edst_lp_fct_file), 
    get_avg_throughput(edst_weighted_fct_file), 
    # get_avg_throughput(edst_cong_fct_file)
  ]
  # print(throughtputs)
  x = np.arange(len(labels))
  fig, ax = plt.subplots(figsize=(6,4))
  ax.bar(x, throughtputs, width=0.45, color='mediumturquoise', ec='gray', hatch='//')
# Add some text for labels, title and custom x-axis tick labels, etc.
  ax.set_ylabel('Average Per-flow\n Throughput(Gbps)', fontsize=20)
  
  ax.set_xticks(x)
  ax.set_yticks([i * 0.20 for i in range(6)])
  ax.set_xticklabels(labels, fontsize=20)
  ax.tick_params(axis='x', labelsize=18) 
  ax.tick_params(axis='y', labelsize=18) 
  
  ax.grid(ls='--')

  fig.tight_layout()

  fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
  # print(fname)
  plt.savefig(fname, bbox_inches='tight')
