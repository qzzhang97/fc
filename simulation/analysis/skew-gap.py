import matplotlib as mpl 

mpl.use('Agg')

import matplotlib.pyplot as plt 
import numpy as np

def get_fct(file_path):
  # print(file_path)
  fcts = []
  f = open(file_path, mode='r')
  for line in f.read().splitlines():
    fcts.append( int(line.split(' ')[6]) )
  f.close()
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
  # print(fct_file, len(throughtputs))
#   print(fct_file, np.percentile(fcts, 99) / 1e6)
  return np.average(throughtputs)


if __name__ == "__main__":
  a = 0.05
  thetas = [0.04]
  phis = [0.25, 0.50, 0.75]
  fat_fct_fmt = "../mix/output/fat-tree/dcqcn/skew/pfc/web/%.2f/%.2f/fct.txt" 
  fc_ecmp_fct_fmt = "../mix/output/fc-ecmp/dcqcn/skew/64/pfc/web/%.2f/%.2f/fct.txt"
  fc_weighted_fct_fmt = "../mix/output/fc-weighted/dcqcn/skew/64/pfc/web/%.2f/%.2f/fct.txt"
  edst_weighted_fct_fmt = "../mix/output/edst-weighted/dcqcn/skew/64/pfc/web/%.2f/%.2f/fct.txt"
  
  clos_99t = np.zeros((1,3))
  ecmp_99t = np.zeros((1,3))
  fc_99t = np.zeros((1,3))
  edst_99t = np.zeros((1,3))

  clos_th = np.zeros((1,3))
  ecmp_th = np.zeros((1,3))
  fc_th = np.zeros((1,3))
  edst_th = np.zeros((1,3))
  
  for i in range(len(thetas)):
    for j in range(len(phis)):
      fat_fct_file = fat_fct_fmt % (thetas[i], phis[j])
      fc_ecmp_fct_file = fc_ecmp_fct_fmt % (thetas[i], phis[j])
      fc_fct_file = fc_weighted_fct_fmt % (thetas[i], phis[j])
      edst_fct_file = edst_weighted_fct_fmt % (thetas[i], phis[j])
      
      clos_99t[i][j] = np.percentile(get_fct(fat_fct_file), 99) / 1e6
      ecmp_99t[i][j] = np.percentile(get_fct(fc_ecmp_fct_file), 99) / 1e6
      fc_99t[i][j] = np.percentile(get_fct(fc_fct_file), 99) / 1e6
      edst_99t[i][j] = np.percentile(get_fct(edst_fct_file), 99) / 1e6

      clos_th[i][j] = get_avg_throughput(fat_fct_file)
      ecmp_th[i][j] = get_avg_throughput(fc_ecmp_fct_file)
      fc_th[i][j] = get_avg_throughput(fc_fct_file)
      edst_th[i][j] = get_avg_throughput(edst_fct_file)


  print('clos 99t', clos_99t)
  print('ecmp 99 fct', ecmp_99t)
  print('fc weighted 99 fct', fc_99t)
  print('edst 99 fct', edst_99t)


  print("Clos / fc FCT reduce: ", clos_99t / fc_99t) 
  print("ECMP / fc FCT reduce: ", ecmp_99t / fc_99t)
  print("edst / fc FCT reduce: ", edst_99t / fc_99t)

  print("fct improvements")
  print('reduce fct edst / fc: ', (edst_99t / fc_99t).sum() / 3)
  print('reduce fct clos / fc: ', (clos_99t / fc_99t).sum() / 3)
  print('reduce fct ecmp / fc: ', (ecmp_99t / fc_99t).sum() / 3)

  print("throughput improvements")
  print('fc / edst th improvements: ', ((fc_th - edst_th ) / edst_th).sum() / 3)
  print('fc / clos th improvements: ', ((fc_th - clos_th) / clos_th).sum() / 3)
  print('fc / ecmp th gaps: ', ((fc_th - ecmp_th) / ecmp_th).sum() / 3)
  # print('fc / edst fct improvements: ', (fc_99t / edst_99t).sum() / 6)
