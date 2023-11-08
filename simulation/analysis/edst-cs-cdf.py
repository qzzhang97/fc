import matplotlib as mpl 
mpl.use('Agg')
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
import numpy as np
import matplotlib.pyplot as plt


# import pandas as pd
# %matplotlib inline
  

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
  

  fat_fct_fmt = "../mix/output/fat-tree/dcqcn/cs-model/pfc/web/C%d-S%d/fct.txt"
  edst_ecmp_fct_fmt = "../mix/output/fc-ecmp/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  edst_lp_fct_fmt = "../mix/output/edst-lp/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  edst_weighted_fct_fmt = "../mix/output/edst-weighted/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  edst_uniform_fct_fmt = "../mix/output/edst-uniform/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  
  fat_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  edst_ecmp_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  edst_lp_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  edst_uniform_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  edst_weighted_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  hosts_every_rack = 4
  for i in range(len(clients)):
    for j in range(len(servers)):
      fat_fct_file = fat_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      fat_throughtputs[i][j] = get_avg_throughtput(fat_fct_file)

      edst_ecmp_fct_file = edst_ecmp_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      edst_ecmp_throughtputs[i][j] = get_avg_throughtput(edst_ecmp_fct_file)

      edst_lp_fct_file = edst_lp_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      edst_lp_throughtputs[i][j] = get_avg_throughtput(edst_lp_fct_file)

      edst_uniform_fct_file = edst_uniform_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      edst_uniform_throughtputs[i][j] = get_avg_throughtput(edst_uniform_fct_file)

      edst_weighted_fct_file = edst_weighted_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      edst_weighted_throughtputs[i][j] = get_avg_throughtput(edst_weighted_fct_file)
  
  fig, ax = plt.subplots(figsize=(8,4))

  cdf(ax,fat_throughtputs.flatten(), ls='--', lw=3, color='b', label='CLOS')
  cdf(ax, edst_ecmp_throughtputs.flatten(), ls='-.', lw=3, color='g', label='ECMP')
  cdf(ax, edst_lp_throughtputs.flatten(), ls=':', lw=3, color='r', label='EDST-LP')
  cdf(ax, edst_weighted_throughtputs.flatten(), ls='-', lw=3, color='y', label='EDST-WEIGHTED')
  cdf(ax, edst_uniform_throughtputs.flatten(), ls='-', lw=3, color='c', label='EDST-UNIFROM')

  labels = [i * 0.25 for i in range(0, 5)]
  x = np.arange(len(labels))
  ax.set_xticks(labels)
  ax.set_yticks([i * 0.25 for i in range(0, 5)])

  ax.tick_params('x', labelsize=20)
  ax.tick_params('y', labelsize=20)

  ax.set_ylabel("CDF", fontsize=22)
  ax.set_xlabel("Average Per-flow Throughput(Gbps)", fontsize=22)

  plt.grid(ls='--')
  plt.legend(loc='lower right',fontsize='x-large')
  fig.tight_layout()
  plt.savefig('images/edst-cs-cdf.pdf', bbox_inches='tight')
