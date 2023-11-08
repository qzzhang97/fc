import matplotlib as mpl 
mpl.use('Agg')
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
import numpy as np
import matplotlib.pyplot as plt
import os


# import pandas as pd
# %matplotlib inline
  
def get_fct(file_path):
  # print(file_path)
  fcts = []
  f = open(file_path, mode='r')
  for line in f.read().splitlines():
    fcts.append( int(line.split(' ')[6]) )
  f.close()
  # print(file_path, len(fcts))
  return fcts

def get_avg_throughtput(fct_file):
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

def cdf(ax, x, plot=True, *args, **kwargs):
  # print(x)
  x, y = sorted(x), np.arange(len(x)) / float(len(x))
  # print(x, y)
  return ax.plot(x, y, *args, **kwargs) if plot else (x, y)

if __name__ == "__main__":

  clients = [i * 4 * 4 for i in range(1, 9)]
  servers = [i * 4 * 4 for i in range(1, 9)]
  

  path_to_clos_fct_file = "../mix/failure-exps/large/output/clos/%s/%d/fct.txt"
  path_to_disjoint_fct_file = "../mix/failure-exps/large/output/disjoint/%s/%d/fct.txt"
  path_to_ecmp_fct_file = "../mix/failure-exps/large/output/ecmp/%s/%d/fct.txt"
  path_to_edst_fct_file = "../mix/failure-exps/large/output/edst/%s/%d/fct.txt"
  

  clos_fcts_30 = None
  clos_fcts_70 = None
  clos_fcts_100 = None
  ecmp_fcts_30 = None
  ecmp_fcts_70 = None
  ecmp_fcts_100 = None
  disjoint_fcts_30 = None
  disjoint_fcts_70 = None
  disjoint_fcts_100 = None
  edst_fcts = None

  pattern = "a2a"
  clos_fcts_30 = np.array(get_fct(path_to_clos_fct_file % (pattern, 30) ) ) / 1e6
  clos_fcts_70 = np.array(get_fct(path_to_clos_fct_file % (pattern, 70) ) ) / 1e6
  clos_fcts_100 = np.array(get_fct(path_to_clos_fct_file % (pattern, 100) ) ) / 1e6
  
  ecmp_fcts_30 = np.array(get_fct(path_to_ecmp_fct_file % (pattern, 30) ) ) / 1e6
  ecmp_fcts_70 = np.array(get_fct(path_to_ecmp_fct_file % (pattern, 70) ) ) / 1e6
  ecmp_fcts_100 = np.array(get_fct(path_to_ecmp_fct_file % (pattern, 100) ) ) / 1e6
  
  disjoint_fcts_30 = np.array(get_fct(path_to_disjoint_fct_file % (pattern, 30) ) ) / 1e6
  disjoint_fcts_70 = np.array(get_fct(path_to_disjoint_fct_file % (pattern, 70) ) ) / 1e6
  disjoint_fcts_100 = np.array(get_fct(path_to_disjoint_fct_file % (pattern, 100) ) ) / 1e6

  
  fig, ax = plt.subplots(figsize=(8,4))

  cdf(ax, clos_fcts_30, lw=3,  label='CLOS-30')
  cdf(ax, clos_fcts_70, lw=3, label='CLOS-70')
  cdf(ax, clos_fcts_100, lw=3, label='CLOS-100')
  cdf(ax, ecmp_fcts_30, lw=3, label='ECMP-30')
  cdf(ax, ecmp_fcts_70, lw=3, label='ECMP-70')
  cdf(ax, ecmp_fcts_100, lw=3, label='ECMP-100')
  cdf(ax, disjoint_fcts_30, lw=3, label='DISJOINT-30')
  cdf(ax, disjoint_fcts_70, lw=3, label='DISJOINT-70')
  cdf(ax, disjoint_fcts_100, lw=3, label='DISJOINT-100')


  labels = [i * 50 for i in range(0, 5)]
  x = np.arange(len(labels))
  ax.set_xticks(labels)
  ax.set_yticks([i * 0.25 for i in range(0, 5)])

  ax.tick_params('x', labelsize=20)
  ax.tick_params('y', labelsize=20)

  ax.set_ylabel("CDF", fontsize=22)
  ax.set_xlabel("FCT(ms)", fontsize=22)

  plt.grid(ls='--')
  plt.legend(loc='lower right',fontsize='x-large')
  fig.tight_layout()
  fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
  # print(fname)
  plt.savefig(fname, bbox_inches='tight')
