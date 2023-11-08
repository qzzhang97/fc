from curses import echo
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

  
  path_to_clos_fct_file = "../mix/failure-exps/large/output/clos/random_%d/%d/fct.txt"
  path_to_disjoint_fct_file = "../mix/failure-exps/large/output/disjoint/random_%d/%d/fct.txt"
  path_to_ecmp_fct_file = "../mix/failure-exps/large/output/ecmp/random_%d/%d/fct.txt"
  path_to_edst_fct_file = "../mix/failure-exps/large/output/edst/random_%d/%d/fct.txt"
  

  random_exps = 3
  p = 90
  clos = np.zeros((1,3))
  ecmp = np.zeros((1,3))
  disjoint = np.zeros((1,3))
  edst = np.zeros((1,3))
  rates = [30, 70, 100]
  for i in range(1, random_exps + 1):
    p_fct_clos = [] 
    p_fct_ecmp = [] 
    p_fct_disjoint = [] 
    p_fct_edst = [] 
    for rate in rates:
      # print(i, rate)
      
      p_fct_clos.append(np.percentile(get_fct(path_to_clos_fct_file % (i, rate) ), p) / 1e6)
      # print('ecmp')
      p_fct_ecmp.append(np.percentile(get_fct(path_to_ecmp_fct_file % (i, rate) ), p) / 1e6)
      # print('disjoint')
      p_fct_disjoint.append(np.percentile(get_fct(path_to_disjoint_fct_file % (i, rate) ), p) / 1e6)
      p_fct_edst.append(np.percentile(get_fct(path_to_edst_fct_file % (i, rate) ), p) / 1e6)
      
    
    # print('f_fct_clos', p_fct_clos)
    # print('f_fct_ecmp', p_fct_ecmp)
    # print('f_fct_disjoint', p_fct_disjoint)
    # print('f_fct_edst', p_fct_edst)
    clos += np.array(p_fct_clos)
    ecmp += np.array(p_fct_ecmp)
    disjoint += np.array(p_fct_disjoint)
    edst += np.array(p_fct_edst)
  # print(ecmp)
  clos /= random_exps
  ecmp /= random_exps
  disjoint /= random_exps
  edst /= random_exps
  # print(ecmp)
  # or rate in rates:
  #   # clos.append(np.percentile(get_fct(path_to_clos_fct_file % (rate) ), p) / 1e6)
  #   # ecmps.append(np.percentile(get_fct(path_to_ecmp_fct_file % (rate) ), p) / 1e6)
  #   # disjoints.append(np.percentile(get_fct(path_to_disjoint_fct_file % (rate) ), p) / 1e6)
  #   edsts.append(np.percentile(get_fct(path_to_edst_fct_file % (rate) ), p) / 1e6)


  # print('updown', disjoints)
  # print('edst', edsts)
  x = np.arange(len(rates))
  width = 0.2
  fig, ax = plt.subplots(figsize=(6,4))

  ax.bar(x - 3 * width / 2, ecmp[0], width, label='ECMP', color='lightgreen', ec='gray', hatch='*')
  ax.bar(x - width / 2, disjoint[0], width, label='DISJOINT', color='hotpink', ec='gray', hatch='-')
  ax.bar(x + width / 2, clos[0], width, label='CLOS', color='tan', ec='gray', hatch='.')
  ax.bar(x + 3 * width / 2, edst[0], width, label='EDST', color='mediumturquoise', ec='gray', hatch='//')
  
  ax.set_xticks(x)
  ax.set_xticklabels(rates)
  ax.set_yticks([i * 400 for i in range(6)])
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
