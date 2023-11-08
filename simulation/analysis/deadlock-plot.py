import matplotlib as mpl 

mpl.use('Agg')
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

import matplotlib.pyplot as plt 
import numpy as np
import os



flow_key_fmt = "{}+{}-{}*{}"
interval_start = 2000000000
interval_end = 2700000000
win_start = interval_start
win_len = 7000000

class Flow:
    def __init__(self, shost, dhost, sport, dport, size, start_time, end_time=-1):
        self.shost = shost
        self.dhost = dhost
        self.sport = sport
        self.dport = dport
        self.size = size
        self.start_time = start_time
        self.end_time = end_time
        
    def flow_key(self):
        return hash(flow_key_fmt.format(self.shost, self.dhost, self.sport, self.dport))

def cal_avg_rates(path_to_fct_file, path_to_pkt_file, flows):
    
    interval_start = 2000000000
    interval_end = 2700000000
    win_start = interval_start
    win_len = 7000000

    fct_f = open(path_to_fct_file, mode='r')
    pkts = []
    for line in fct_f.read().splitlines():
        d = line.split(' ')
        flow_key = hash( flow_key_fmt.format(d[0], d[1], 10000, d[2]) )
        if not flows.has_key( flow_key ): continue
        flows[ flow_key ].end_time = int(d[3])


    pkt_f = open(path_to_pkt_file, mode='r')
    for line in pkt_f.read().splitlines():
        pkts.append(line)
    pkt_f.close()

    real_time_rates = {}
    for flow_key in flows.keys():
        real_time_rates[ flow_key ] = [0 for _ in range( (interval_end - interval_start) / win_len ) ]
    

    while win_start < interval_end:
        win_end = win_start + win_len
        mapped_idx = (win_start - interval_start) / win_len
        # print("mapped idx", win_start, interval_end, mapped_idx)
        for line in pkts:
            d = line.split(' ')

            mapped_flow_key = hash( flow_key_fmt.format(d[0], d[1], 10000, 100) )
            if not real_time_rates.has_key( flow_key ): continue
            # mapped_flow_start_t = flows[mapped_flow_key].start_time
            # mapped_flow_end_t = flows[mapped_flow_key].end_time
            # print(win_end, mapped_idx)
            real_time_rates[mapped_flow_key][mapped_idx] += int(d[3]) # pkt size
        win_start += win_len
    ## The number of intervals is (interval_end - interval_start) / win_len
    avg_flow_rate = [0 for _ in range( (interval_end - interval_start) / win_len )]

    # real_time_rates = np.array(real_time_rates)
    # p rint( real_time_rates)
    for  idx in range( len(avg_flow_rate) ):
        sum_rate = 0.0
        active = 0
        for key in real_time_rates.keys():
            if real_time_rates[key] != 0: active+=1
            sum_rate += (real_time_rates[ key ][ idx ] * 8 / (win_len * 1e-9) )
        avg_flow_rate[idx] = sum_rate / active
    # print(avg_flow_rate)
    return avg_flow_rate

if __name__ == "__main__":

    path_to_ecmp_fct_file = "../mix/failure-exps/deadlock/output/ecmp/fct.txt"
    path_to_ecmp_pkt_file = "../mix/failure-exps/deadlock/output/ecmp/pkt.txt"

    path_to_up_down_fct_file = "../mix/failure-exps/deadlock/output/up-down/fct.txt"
    path_to_up_down_pkt_file = "../mix/failure-exps/deadlock/output/up-down/pkt.txt"

    path_to_flow_file = "../mix/failure-exps/deadlock/traffic/flow.txt"
    flow_f = open(path_to_flow_file, mode='r')
    flows = {}
    

    
    for line in flow_f.read().splitlines():
        
        flow_info = line.split(' ')
        if len(flow_info) < 2: continue
        flow_key = hash(flow_key_fmt.format(
            flow_info[0],
            flow_info[1],
            10000,
            100
        ))
        # print( flow_key )
        flows[flow_key] = Flow(
            int(flow_info[0]),
            int(flow_info[1]),
            10000,
            int(flow_info[3]),
            int(flow_info[4]),
            start_time=int(float(flow_info[5]) * 1e9),
            end_time=-1
        )

    # ecmp_rate = cal_avg_rates(path_to_ecmp_fct_file, path_to_ecmp_fct_file, flows)
    # up_down_rate = cal_avg_rates(path_to_up_down_fct_file, path_to_up_down_pkt_file, flows)

    a = [0 for _ in range(10)]
    a[1] = 99
    print(a)
    

    # fig, ax = plt.subplots(figsize=(6,4))
    # # for f_name in cdf_files:   
    # ax.plot(np.range(len(ecmp_rate)), ecmp_rate,  'r-', lw=2, label="ecmp")
    # ax.plot(np.range(len(ecmp_rate)), up_down_rate,  'r-', lw=2, label="up-down")
    
    
    # ax.tick_params(axis='x', labelsize=20) 
    # ax.tick_params(axis='y', labelsize=20) 
    # ax.set_ylabel("REAL-TIME RATES", fontsize=22)
    # ax.set_xlabel("ln(SIZE)", fontsize=22)
    
    # ax.grid(ls='--')
    # fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
    # fig.tight_layout()
    # plt.savefig(fname, bbox_inches='tight')

