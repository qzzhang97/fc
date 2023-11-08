from array import array
import matplotlib as mpl 
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.use('Agg')
mpl.rcParams['hatch.linewidth'] = 2

import matplotlib.pyplot as plt 
import numpy as np
import os


def cost_equivalent_clos():
  pass

if __name__ == "__main__":
  to_hosts = 24
  switches = [100, 200, 300, 400, 500, 600, 800, 1000]
  routings = ["ecmp", "edst", "disjoint", "ksp8", "ksp16", "ksp"]
  patterns = ["WORST", "A2A"]
  throughput_map = {}
  for pattern in patterns:
    throughput_map[pattern] = {}
    for routing in routings:
      throughput_map[pattern][routing] = {}
      for switch in switches:
        throughput_map[pattern][routing][switch] = 0.0
  th_f = open('worst', mode='r')
  lines = th_f.read().splitlines()
  for line in lines:
    data = line.split(' ')
    a2a_pattern = data[2]
    worst_pattern = data[4]
    switch = int(data[1])
    routing = data[6]
    a2a_throughput = float(data[3])
    worst_throughput = float(data[5])
    throughput_map[a2a_pattern][routing][switch] = a2a_throughput
    throughput_map[worst_pattern][routing][switch] = worst_throughput

  fc_edst_throughputs = []
  fc_disjoint_throughputs = []
  fc_ecmp_throughputs = []
  fc_ksp8_throughputs = []
  fc_ksp16_throughputs = []
  fc_ksp24_throughputs = []
  equal_cost_clos = [0.42 for _ in range(len(switches))]
  pattern = "A2A"
  # print(throughput_map)
  for switch in switches:
    # print(throughput_map["FC"]["ECMP"][to_host])
    fc_edst_throughputs.append(throughput_map[pattern]["edst"][switch])
    fc_disjoint_throughputs.append(throughput_map[pattern]["disjoint"][switch])
    fc_ecmp_throughputs.append(throughput_map[pattern]["ecmp"][switch])
    
    fc_ksp8_throughputs.append(throughput_map[pattern]["ksp8"][switch])
    fc_ksp16_throughputs.append(throughput_map[pattern]["ksp16"][switch])
    fc_ksp24_throughputs.append(throughput_map[pattern]["ksp"][switch])


  fc_edst_throughputs = np.array(fc_edst_throughputs, dtype=float)
  fc_disjoint_throughputs = np.array(fc_disjoint_throughputs, dtype=float)
  fc_ecmp_throughputs = np.array(fc_ecmp_throughputs, dtype=float)
  fc_ksp8_throughputs = np.array(fc_ksp8_throughputs, dtype=float)
  fc_ksp16_throughputs = np.array(fc_ksp16_throughputs, dtype=float)
  fc_ksp24_throughputs = np.array(fc_ksp24_throughputs, dtype=float)

  # print(fc_ecmp_throughputs, jf_ecmp_throughputs, xp_ecmp_throughputs)

  x = np.arange(len(switches))
  width = 0.2
  fig, ax = plt.subplots(figsize=(6,4))

  ax.plot(x , fc_edst_throughputs, marker='s', lw=2, label='EDST')
  ax.plot(x , fc_disjoint_throughputs, marker='o', lw=2, label='DISJOINT')
  ax.plot(x , fc_ecmp_throughputs, marker='^', lw=2, label='ECMP')
  ax.plot(x , fc_ksp8_throughputs, marker='<', lw=2, label='KSP-8')
  # ax.plot(x , fc_ksp16_throughputs, marker='^', lw=2, label='KSP-16')
  ax.plot(x , fc_ksp24_throughputs, marker='h', lw=2, label='KSP-24')
  ax.plot(x , equal_cost_clos, marker='x', lw=2, label='EQUAL COST CLOS')

  ax.set_xticks(x)
  ax.set_xticklabels(np.array(switches) * to_hosts)
  ax.set_yticks([i * 0.4 for i in range(6)])
  ax.set_xlabel("Number of Servers", fontsize=12)
  ax.set_ylabel("Throughput", fontsize=20)
  ax.tick_params(axis='x', labelsize=12) 
  ax.tick_params(axis='y', labelsize=12) 
  
  
  ax.legend(loc='upper right', fontsize='large')
  
  plt.grid(ls='--')
  fig.tight_layout()


  fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
  # print(fname)
  plt.savefig(fname, bbox_inches='tight')
