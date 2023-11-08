import matplotlib as mpl 

mpl.use('Agg')
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

import matplotlib.pyplot as plt 
import numpy as np
import os

if __name__ == "__main__":
    cdf_files = [
        "../../traffic_gen/WebSearch_distribution.txt",
    ]

    cdf = {}
    for f_name in cdf_files:
        file = open(f_name)
        cdf[f_name] = []
        percentile = []
        size = []
        for line in file.readlines():
            d = line.replace('\n','').split(' ')
            size.append(int(d[0]))
            percentile.append(float(d[1]))
        cdf[f_name].append(size)
        cdf[f_name].append(percentile)
    fig, ax = plt.subplots(figsize=(6,4))
    for f_name in cdf_files:   
        ax.plot(np.log(np.array(cdf[f_name][0])), cdf[f_name][1],  'r-', lw=2, label=f_name.replace("../../traffic_gen/", "").replace(".txt", ""))
    
    # xlabels = [i * 20 for i in range(6)]

    ax.tick_params(axis='x', labelsize=20) 
    ax.tick_params(axis='y', labelsize=20) 
    ax.set_ylabel("CDF", fontsize=22)
    ax.set_xlabel("ln(SIZE)", fontsize=22)
    
    ax.grid(ls='--')
    fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
    fig.tight_layout()
    plt.savefig(fname, bbox_inches='tight')
