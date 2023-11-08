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

  
  path_to_clos_fct_file = "../mix/failure-exps/large/output/clos/o2o/%d/fct.txt"
  path_to_disjoint_fct_file = "../mix/failure-exps/large/output/disjoint/o2o/%d/fct.txt"
  path_to_ecmp_fct_file = "../mix/failure-exps/large/output/ecmp/o2o/%d/fct.txt"
  path_to_edst_fct_file = "../mix/failure-exps/large/output/edst/o2o/%d/fct.txt"
  
  clos = []
  ecmps = []
  disjoints = []
  edsts = []

  p = 50
  rates = [30, 70, 100]
  for rate in rates:
    clos.append(np.percentile(get_fct(path_to_clos_fct_file % (rate) ), p) / 1e6)
    ecmps.append(np.percentile(get_fct(path_to_ecmp_fct_file % (rate) ), p) / 1e6)
    disjoints.append(np.percentile(get_fct(path_to_disjoint_fct_file % (rate) ), p) / 1e6)
    edsts.append(np.percentile(get_fct(path_to_edst_fct_file % (rate) ), p) / 1e6)

  for rate in rates:
    print('clos',get_avg_throughput(path_to_clos_fct_file % (rate) ))
    print('disjoint',get_avg_throughput(path_to_disjoint_fct_file % (rate) ))
    print('ecmp', get_avg_throughput(path_to_ecmp_fct_file % (rate) ))
    print('edst', get_avg_throughput(path_to_edst_fct_file % (rate) ))

  x = np.arange(len(rates))
  width = 0.2
  fig, ax = plt.subplots(figsize=(6,4))

  ax.bar(x - 3 * width / 2, ecmps, width, label='ECMP', color='lightgreen', ec='gray', hatch='*')
  ax.bar(x - width / 2, disjoints, width, label='DISJOINT', color='hotpink', ec='gray', hatch='-')
  ax.bar(x + width / 2, clos, width, label='CLOS', color='tan', ec='gray', hatch='.')
  ax.bar(x + 3 * width / 2, edsts, width, label='EDST', color='mediumturquoise', ec='gray', hatch='//')
  
  ax.set_xticks(x)
  ax.set_xticklabels(rates)
  ax.set_yticks([i * 300 for i in range(7)])
  ax.set_xlabel("Flow Rate", fontsize=20)
  ax.set_ylabel("50th Percentile FCT(ms)", fontsize=20)
  ax.tick_params(axis='x', labelsize=18) 
  ax.tick_params(axis='y', labelsize=18) 
  
  ax.legend(loc='upper left', fontsize='large')
  
  plt.grid(ls='--')
  fig.tight_layout()


  fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
  # print(fname)
  plt.savefig(fname, bbox_inches='tight')
