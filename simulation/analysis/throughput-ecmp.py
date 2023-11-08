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
  routings = ["ECMP-LP", "DISJOINT-LP", "EDST-LP"]
  patterns = ["WORST", "A2A"]
  num_exps = 5
  throughput_map = {}
  for pattern in patterns:
    throughput_map[pattern] = {}
    for routing in routings:
      throughput_map[pattern][routing] = {}
      for switch in switches:
        throughput_map[pattern][routing][switch] = []
  th_f = open('ecmp', mode='r')
  lines = th_f.read().splitlines()
  for line in lines:
    data = line.replace('throughput: ', '').split(' ')
    pattern = data[0]
    routing = data[1]
    switch = int(data[2])
    throughput = float(data[3])
    throughput_map[pattern][routing][switch].append(throughput)
    # print(throughput_map[topo][routing][to_host])
  


  fc_ecmp_throughputs = []

  pattern = "WORST"
  # print(throughput_map)
  for switch in switches:
    throughput_map[pattern]["ECMP-LP"][switch] = np.sum(throughput_map[pattern]["ECMP-LP"][switch]) / num_exps
    fc_ecmp_throughputs.append(throughput_map[pattern]["ECMP-LP"][switch])


  fc_ecmp_throughputs = np.array(fc_ecmp_throughputs, dtype=float)

  # print(fc_ecmp_throughputs, jf_ecmp_throughputs, xp_ecmp_throughputs)

  x = np.arange(len(switches))
  width = 0.2
  fig, ax = plt.subplots(figsize=(6,4))

#   ax.plot(x , fc_edst_throughputs, marker='+', lw=2, label='EDST')
#   ax.plot(x , fc_disjoint_throughputs, marker='o', lw=2, label='DISJOINT')
  ax.plot(x , fc_ecmp_throughputs, marker='^', lw=2, label='ECMP')

  ax.set_xticks(x)
  ax.set_xticklabels(np.array(switches) * to_hosts)
  ax.set_yticks([i * 0.2 for i in range(6)])
  ax.set_xlabel("Number of Servers", fontsize=20)
  ax.set_ylabel("Throughput\n(Average 5 runs)", fontsize=20)
  ax.tick_params(axis='x', labelsize=12) 
  ax.tick_params(axis='y', labelsize=18) 
  
  
  ax.legend(loc='upper right', fontsize='large')
  
  plt.grid(ls='--')
  fig.tight_layout()


  fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
  # print(fname)
  plt.savefig(fname, bbox_inches='tight')
