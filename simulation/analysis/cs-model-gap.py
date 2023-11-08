import matplotlib as mpl 
mpl.use('Agg')
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

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

def get_ones_in_array(array):
  ones = 0
  rows = array.shape[0]
  cols = array.shape[1]
  for i in range(rows):
    for j in range(cols):
      if array[i][j] > 1:
        ones += 1
  return float(ones) / (rows * cols) * 100

if __name__ == "__main__":

  clients = [i * 4 * 4 for i in range(1, 9)]
  servers = [i * 4 * 4 for i in range(1, 9)]


  fat_fct_fmt = "../mix/output/fat-tree/dcqcn/cs-model/pfc/web/C%d-S%d/fct.txt"
  
  fc_ecmp_fct_fmt = "../mix/output/fc-ecmp/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  fc_uniform_fct_fmt = "../mix/output/fc-uniform/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  fc_weighted_fct_fmt = "../mix/output/fc-weighted/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  fc_lp_fct_fmt = "../mix/output/fc-lp/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"

  edst_uniform_fct_fmt = "../mix/output/edst-uniform/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  edst_weighted_fct_fmt = "../mix/output/edst-weighted/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  edst_lp_fct_fmt = "../mix/output/edst-lp/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  
  fat_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  ecmp_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')

  fc_uniform_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  fc_weighted_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  fc_lp_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')

  edst_uniform_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  edst_weighted_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  edst_lp_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
 

  hosts_every_rack = 4
  for i in range(len(clients)):
    for j in range(len(servers)):
      fat_fct_file = fat_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      fat_throughtputs[i][j] = get_avg_throughtput(fat_fct_file)

      fc_ecmp_fct_file = fc_ecmp_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      ecmp_throughtputs[i][j] = get_avg_throughtput(fc_ecmp_fct_file)

      fc_uniform_fct_file = fc_uniform_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      fc_uniform_throughtputs[i][j] = get_avg_throughtput(fc_uniform_fct_file)

      fc_weighted_fct_file = fc_weighted_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      fc_weighted_throughtputs[i][j] = get_avg_throughtput(fc_weighted_fct_file)

      fc_lp_fct_file = fc_lp_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      fc_lp_throughtputs[i][j] = get_avg_throughtput(fc_lp_fct_file)

      edst_uniform_fct_file = edst_uniform_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      edst_uniform_throughtputs[i][j] = get_avg_throughtput(edst_uniform_fct_file)

      edst_weighted_fct_file = edst_weighted_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      edst_weighted_throughtputs[i][j] = get_avg_throughtput(edst_weighted_fct_file)

      edst_lp_fct_file = edst_lp_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      edst_lp_throughtputs[i][j] = get_avg_throughtput(edst_lp_fct_file)

  print('FC compares with CLOS: ') 
  print("FC_uniform / clos: %.2f p: %d" % ( 
    (fc_uniform_throughtputs / fat_throughtputs).sum() / 64, 
    get_ones_in_array(fc_uniform_throughtputs / fat_throughtputs)))
  
  print('FC_weighted / clos: %.2f p: %d' % (
    (fc_weighted_throughtputs / fat_throughtputs).sum() / 64, 
    get_ones_in_array(fc_weighted_throughtputs / fat_throughtputs)))
  print('FC_lp / clos: %.2f p: %d' % (
    (fc_lp_throughtputs / fat_throughtputs).sum() / 64, 
    get_ones_in_array(fc_lp_throughtputs / fat_throughtputs)))
  # print('edst_uniform / clos: %.2f' % ((edst_uniform_throughtputs / fat_throughtputs).sum() / 64))
  # print('edst_lp / clos: %.2f' % ((edst_lp_throughtputs / fat_throughtputs).sum() / 64))
  # print('edst_weighted / clos: %.2f' % ((edst_weighted_throughtputs / fat_throughtputs).sum() / 64))
  print('\n')

  print('FC compares with ECMP')
  print('FC_uniform / ecmp: %.2f p: %d' % (
    (fc_uniform_throughtputs / ecmp_throughtputs).sum() / 64, 
    get_ones_in_array(fc_uniform_throughtputs / ecmp_throughtputs)))
  print('FC_weighted / ecmp: %.2f p: %d' % (
    (fc_weighted_throughtputs / ecmp_throughtputs).sum() / 64, 
    get_ones_in_array(fc_weighted_throughtputs / ecmp_throughtputs)))
  print('FC_lp / ecmp: %.2f p: %d' % (
    (fc_lp_throughtputs / ecmp_throughtputs).sum() / 64, 
    get_ones_in_array(fc_lp_throughtputs / ecmp_throughtputs)))
  # print('edst_uniform / ecmp: %.2f' % ((edst_uniform_throughtputs / ecmp_throughtputs).sum() / 64))
  # print('edst_lp / ecmp: %.2f' % ((edst_lp_throughtputs / ecmp_throughtputs).sum() / 64))
  # print('edst_weighted / ecmp: %.2f' % ((edst_weighted_throughtputs / ecmp_throughtputs).sum() / 64))
  print('\n')
  print('FC compares with EDST')
  print('FC_uniform / edst_uniform: %.2fx p: %d' % (
    ((fc_uniform_throughtputs)/ edst_uniform_throughtputs).sum() / 64, 
    get_ones_in_array(fc_uniform_throughtputs / edst_uniform_throughtputs)))
  print('FC_weighted / edst_weighted: %.2fx p: %d' % (
    ((fc_weighted_throughtputs)/ edst_weighted_throughtputs).sum() / 64, 
    get_ones_in_array(fc_weighted_throughtputs / edst_weighted_throughtputs)))
  print('FC_lp / edst_lp: %.2fx p: %d' % (
    ((fc_lp_throughtputs)/ edst_lp_throughtputs).sum() / 64, 
    get_ones_in_array(fc_lp_throughtputs / edst_lp_throughtputs) ))
  