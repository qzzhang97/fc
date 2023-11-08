from array import array
import matplotlib as mpl 
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.use('Agg')
mpl.rcParams['hatch.linewidth'] = 2

import matplotlib.pyplot as plt 
import numpy as np
import os


def read_path(path_file):
    print(path_file)
    path_f = open(path_file, mode='r')
    lines = path_f.read().splitlines()
    path_f.close()
            
    idx = 0
    l0 = [int(x) for x in lines[idx].split(' ')]
    pairs = l0[0]
    host_per_sw = l0[1]
    switches = l0[2]
    # print("sw", switches)

    path_pair = {}
    for i in range(switches):
        path_pair[i] = {}
        for j in range(switches):
            path_pair[i][j] = []
    

    idx += 1
    for _ in range(pairs):
        l = [int(x) for x in lines[idx].split(' ')]
        idx +=1
        src = l[0]
        dst = l[1]
        path_num = l[2]
        for _ in range(path_num):
            path_pair[ src ][ dst ].append([int(x) for x in lines[idx].split(' ')][ 1 : ])
            idx += 1
    
    avg_num_paths = 0.0
    pairs = 0.0
    avg_shortest_path_length = 0.0
    for src in range(switches):
        for dst in range(switches):
            if src == dst: continue
            paths = path_pair[src][dst]
            pairs += 1.0
            avg_shortest_path_length += len(paths[0])
            avg_num_paths += len(paths)
    return avg_num_paths / pairs, avg_shortest_path_length / pairs

if __name__ == "__main__":
    to_hosts = 24
    switches = [100, 200, 300, 400, 500, 600, 800, 1000]
    ks = [3,3,3,4,4,4,4,4]
    aspls = []
    for idx in range(len(switches)):
        switch = switches[idx]
        k = ks[idx]
        aspl = 0.0
        for i in range(5):
            sed = 2 * i + 1
            path_fmt = "../mix/failure-exps/scripts/throughput/path/ecmp_%d_%d_sed_%d"
            path_file = path_fmt % (switch, k, sed)
            avg_shortest_path_length, _ = read_path(path_file)
            aspl += avg_shortest_path_length
        aspl /= 5.0
        aspls.append(aspl)
    
    print('plot aspl image')
    
    x = np.arange(len(switches))
    width = 0.2
    fig, ax = plt.subplots(figsize=(6,4))

    ax.plot(x , aspls, marker='^', lw=2, label='ECMP')
    xtick_labels = [2.4, 4.8, 7.2, 9.6, 12.0, 14.4, 19.2, 24]
    ax.set_xticks(x)
    ax.set_xticklabels(np.array(switches) * to_hosts)
    ax.set_yticks([i * 0.2 for i in range(6)])
    ax.set_xlabel("Number of Servers (K)", fontsize=20)
    ax.set_ylabel("ASPL of ECMP", fontsize=20)
    ax.tick_params(axis='x', labelsize=18) 
    ax.tick_params(axis='y', labelsize=18) 


    ax.legend(loc='upper right', fontsize='large')

    plt.grid(ls='--')
    fig.tight_layout()


    fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
    # print(fname)
    plt.savefig(fname, bbox_inches='tight')
