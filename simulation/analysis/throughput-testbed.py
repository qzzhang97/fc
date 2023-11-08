from turtle import color
import matplotlib as mpl 
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.use('Agg')
mpl.rcParams['hatch.linewidth'] = 2

import matplotlib.pyplot as plt 
import numpy as np
import os



if __name__ == "__main__":
  """
  settings: 128 switches
  ports of virtual layers: [3, 5, 5, 3]
  """

  second = [sec for sec in range(1, 21)]
  up_down_throughputs = [489.76, 456.65, 426.26, 410.99, 395.75, 391.12, 393.11, 391.35, 388.08, 390.12,
                        389.36, 388.19, 388.69, 387.56, 389.58, 389.34,  389.44, 389.33, 387.22, 388.79]
  edst_throughputs = [411.27, 278.60, 219.68, 219.13, 253.26, 263.51, 270.21, 271.44, 271.82, 277.44, 
                      277.69, 279.18, 277.32, 275.01, 279.36, 280.87, 279.49, 278.13, 279.40, 276.64]
  ecmp_throughputs = [459.16, 370.52, 270.58, 180.21, 95.93, 95.11, 95.75, 93.78, 93.40, 93.70,
                      135.26, 160.40, 221.51, 260.73, 284.18, 286.18, 292.36, 297.47, 298.91, 301.86]
  
  up_down_throughputs = np.array( up_down_throughputs) * 8 / 1024
  edst_throughputs = np.array( edst_throughputs) * 8 / 1024
  ecmp_throughputs = np.array( ecmp_throughputs) * 8 / 1024
  x = np.arange(len(second))
  width = 0.2
  fig, ax = plt.subplots(figsize=(6,4))

  ax.plot(x[::2] , edst_throughputs[::2], color='forestgreen', marker='*',  lw=2, label='EDST')
  ax.plot(x[::2] , up_down_throughputs[::2], color="orange", marker='o', lw=2, label='VIRTUAL UP-DOWN')
  ax.plot(x[::2] , ecmp_throughputs[::2], color="coral", marker='^', lw=2, label='ECMP')
  print(x[::2])
  ax.set_xticks(x[::2])
  ax.set_xticklabels(second[::2])
  ax.set_yticks([i * 2 for i in range(4)])
  ax.set_xlabel("Seconds", fontsize=20)
  ax.set_ylabel("Average Throughput(Gb/s)", fontsize=20)
  ax.tick_params(axis='x', labelsize=18) 
  ax.tick_params(axis='y', labelsize=18) 
  
  
  ax.legend(loc='upper right', fontsize='large')
  
  plt.grid(ls='--')
  fig.tight_layout()


  fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
  # print(fname)
  plt.savefig(fname, bbox_inches='tight')
