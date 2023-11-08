from email.mime import base
import sys
import random
import math
import heapq
from custom_rand import CustomRand
import numpy as np
import math
import yaml

import networkx as nx
import sys
sys.path.append('TUB')
from topo_repo import topology

random.seed(6699)

class Flow:
	def __init__(self, src, dst, size, t):
		self.src, self.dst, self.size, self.t = src, dst, size, t
	def __str__(self):
		return "%d %d 3 100 %d %.9f"%(self.src, self.dst, self.size, self.t)
	def __lt__(self, other):
		return self.t < other.t

def translate_bandwidth(b):
	if b == None:
		return None
	if type(b)!=str:
		return None
	if b[-1] == 'G':
		return float(b[:-1])*1e9
	if b[-1] == 'M':
		return float(b[:-1])*1e6
	if b[-1] == 'K':
		return float(b[:-1])*1e3
	return float(b)

def poisson(lam):
	return -math.log(1-random.random())*lam


def gen_all_to_all_TM(switches, hosts, switch_recv_bandwidth):
    tm = np.zeros(shape=(switches, switches))
    for i in range(switches):
        for j in range(switches):
            if i == j: continue
            # tm[i][j] = 1
            tm[i][j] = switch_recv_bandwidth / float(switches - 1)
    
    hosts_per_tor = hosts // switches
    server_level_a2a_tm = np.zeros((hosts, hosts))
    for src_ToR in range(switches):
        for dst_ToR in range(switches):
            if tm[src_ToR][dst_ToR] > 0:
                for i in range(hosts_per_tor):
                    for j in range(hosts_per_tor):
                        src_host = src_ToR * host_per_tor + i
                        dst_host = dst_ToR * host_per_tor + j
                        server_level_a2a_tm[src_host][dst_host] = tm[src_ToR][dst_ToR] / host_per_tor / hosts_per_tor

    return tm, server_level_a2a_tm

def my_permutation_tm(switches, switch_recv_bandwidth):
    tm = np.zeros(shape=(switches, switches))
    perm = np.random.permutation(switches)
    # print('perm=', perm)
    for i in range(len(perm)):
        tm[i][perm[i]] = switch_recv_bandwidth
        # tm[perm[i]][i] = switch_recv_bandwidth
    for i in range(len(perm)):
        if tm[i][i] != 0:
            return my_permutation_tm(switches, switch_recv_bandwidth)
    return tm

def gen_random_matrix(switches, hosts, switch_recv_bandwidth):
    # print('gen random')
    combinations = switches // 8
    o2o_tms = []
    for i in range(combinations):
        o2o_tms.append(my_permutation_tm(switches, switch_recv_bandwidth))
    rands = np.random.rand(combinations)
    rands = rands / np.sum(rands)
    # print(rands)
    tor_level_rnd_tm = np.zeros((switches, switches))
    for i in range(combinations):
        tor_level_rnd_tm += o2o_tms[i] * rands[i]
    
    host_per_tor = hosts // switches
    server_level_rnd_tm = np.zeros((hosts, hosts))
    for src_ToR in range(switches):
        for dst_ToR in range(switches):
            if tor_level_rnd_tm[src_ToR][dst_ToR] > 0:
                for i in range(host_per_tor):
                    for j in range(host_per_tor):
                        src_host = src_ToR * host_per_tor + i
                        dst_host = dst_ToR * host_per_tor + j
                        server_level_rnd_tm[src_host][dst_host] = tor_level_rnd_tm[src_ToR][dst_ToR] / host_per_tor / host_per_tor
    
    return tor_level_rnd_tm, server_level_rnd_tm

def read_topo(mat_file):
    mat_f = open(mat_file, mode='r')
    lines = mat_f.read().splitlines()
    to_host, switches, sw2sw_links, servers = map(int, lines[0].split())
    topo_matrix = np.zeros((switches, switches))
    # print('switch=', switches)
    for line in lines[1:]:
        data = list(map(int, line.split()))
        topo_matrix[data[0]][data[1]] = 1
        topo_matrix[data[1]][data[0]] = 1
    return topo_matrix, switches, to_host, servers

def gen_worst_tm(mat_file, arrival_rate):
    topo_matrix, switches, to_hosts, hosts = read_topo(mat_file)
    print('worst', switches, to_hosts, hosts)
    G = nx.Graph()
    for src in range(switches):
        for dst in range(switches):
            if topo_matrix[src][dst] == 1:
                G.add_edge(src, dst)
    
    tor_list = [tor_sid for tor_sid in range(switches)]
    demand_list = {}
    for sid in range(switches):
        demand_list[sid] = to_hosts

    topo = topology.Topology(G, tor_list, demand_list)
    # tub = topo.get_tub()
    # print("topo_type=%s hosts=%s, TUB=%.2f" % (topo_type, hosts, tub))

    tor_level_worst_tm = np.zeros((switches, switches))
    
    ## tm is a dictionary
    tm, _ = topo.get_near_worst_case_traffic_matrix()

    server_level_worst_tm = np.zeros((hosts, hosts))
    for key in tm.keys():
        src = key[0]
        dst = key[1]
        # print(tm[key])
        tor_level_worst_tm[src][dst] = tm[key]
    
    
    
    ## convert ToR-level matrix to Server-level Traffic Matrix
    host_per_tor = hosts // switches
    for src_ToR in range(switches):
        for dst_ToR in range(switches):
            if tor_level_worst_tm[src_ToR][dst_ToR] > 0:
                for i in range(host_per_tor):
                    for j in range(host_per_tor):
                        src_host = src_ToR * host_per_tor + i
                        dst_host = dst_ToR * host_per_tor + j
                        server_level_worst_tm[src_host][dst_host] = tor_level_worst_tm[src_ToR][dst_ToR] / host_per_tor / host_per_tor
    tor_level_worst_tm = tor_level_worst_tm * arrival_rate
    server_level_worst_tm = server_level_worst_tm * arrival_rate
    return tor_level_worst_tm, server_level_worst_tm


def gen_skewed_TM(switches, switch_recv_bandwidth, theta, phi):
    tm = np.zeros(shape=(switches, switches))
    ### theta: fraction of hot racks
    ### phi: concentrated traffic at hot rack switches
    N_hot = int(math.ceil(switches * theta))
    N_cold = switches - N_hot
    # print(f"hot racks : {N_hot}")
    hot_rack_ids = []
    while len(hot_rack_ids) < N_hot:
        rack_id = random.randint(0, switches - 1)
        while rack_id in hot_rack_ids:
            rack_id = random.randint(0, switches - 1)
        hot_rack_ids.append(rack_id)
    # print("hot rack ids: ", hot_rack_ids)

    p_hot_to_hot = phi * phi / (N_hot * N_hot)
    p_cold_to_cold = (1 - phi) * (1 - phi) / (N_cold * N_cold)
    p_hot_to_cold = phi * (1 - phi) / (N_cold * N_hot)
    # print(f"p_hot_to_hot: {p_hot_to_hot}, p_cold_to_cold: {p_cold_to_cold}, p_hot_to_cold: {p_hot_to_cold}")
    s_hot = 0
    for i in range(switches):
        for j in range(switches):
            if i == j: continue
            if i in hot_rack_ids and j in hot_rack_ids:
                tm[i][j] = p_hot_to_hot * switch_recv_bandwidth * switches * 0.3
                s_hot += tm[i][j]
            elif not i in hot_rack_ids and not j in hot_rack_ids:
                tm[i][j] = p_cold_to_cold * switch_recv_bandwidth * switches * 0.3
            else:
                tm[i][j] = p_hot_to_cold * switch_recv_bandwidth * switches * 0.3
                s_hot += tm[i][j]
    return tm


def generate(num_ToRs, total_hosts, host_bw, mlu, host_to_host_tm, duration, ofile, cdf_file):
    host_per_ToR = total_hosts // num_ToRs
    host_ids = []
    base_t = 0
    port = 80
    flows = []
    time = duration * 1e9 # 1000 000 000ns
    
    f = open(cdf_file,"r")
    cdf = []
    for line in f.readlines():
        x,y = map(float, line.strip().split(' '))
        cdf.append([x,y])
    customRand = CustomRand()
    if not customRand.setCdf(cdf):
        print ("Error: Not valid cdf")
        sys.exit(0)

    # unit is byte. Commented by qizhou.zqz.
    flow_avg_size = customRand.getAvg()
    print("hosts_per_ToR: {}, flow_avg_size: {}byte".format(host_per_ToR, flow_avg_size))
    for i in range(num_ToRs):
        host_ids.append([i * host_per_ToR + j for j in range(host_per_ToR)])

    flows = []
    generated_size  = 0
    # print('single line=', np.sum(host_to_host_tm[0]))
    for src_host in range(total_hosts):
        for dst_host in range(total_hosts):
            if src_host == dst_host or host_to_host_tm[src_host][dst_host] == 0:
                continue
            # host2host taffic limit, Gb to bytes.
            h2h_traffic = (host_to_host_tm[src_host][dst_host] * 1e9 / 8) * (float(time) / 1000000000)

            estimated_flow_num = int(math.ceil(h2h_traffic / flow_avg_size))
            has_gen = 0
            stop_gen = False
            # print(src_host, dst_host, estimated_flow_num)
            for flow_num in range(1, estimated_flow_num + 1):
                # inter_t = int(poisson(flow_avg_inter))
                inter_t = random.randint(0, time)
                # size = p2p_traffic / estimated_flow_num
                size = 0 
                if estimated_flow_num == 1: size = h2h_traffic
                else: size = int(customRand.rand())
                
                if has_gen + size >= h2h_traffic:
                    size = h2h_traffic - has_gen
                    stop_gen = True
                
                if size == 0: size = 1

                flows.append( Flow(src_host, dst_host, size, (base_t + inter_t) * 1e-9) )
                generated_size += size
                has_gen += size
                
                if stop_gen: break
    
    print("tm: {:.2f}Gb generated: {:.2f}".format(np.sum(host_to_host_tm), generated_size * 8 / 1e9))
    ## Final step
    ## write flow to output file
    out = open(ofile, "w")

    out.write("%d\n" % (len(flows)))

    heapq.heapify(flows)
    while len(flows) > 0:
        out.write("%s 0\n" % (flows[0]))
        heapq.heappop(flows)

def write_tm(tm, tm_dir):
    tm_f = open(tm_dir, mode='w')
    sw = len(tm)
    tm_f.write("%d\n" % (sw))
    for i in range(sw):
        tm_f.write("%s\n" % (" ".join(map(str, tm[i]))))
    tm_f.close()

if __name__ == "__main__":
    with open('common.yaml','r') as f:
        data = yaml.load(f)

    num_tors = data['fc']['switches']
    host_per_tor = data['fc']['to_hosts']
    hosts = num_tors * host_per_tor
    rates = [30, 70, 100]
    time = 0.1 # 0.2s
    
    for rate in rates:
        tor_level_a2a_tm, server_level_a2a_tm = gen_all_to_all_TM(num_tors, hosts, host_per_tor * (rate / float(100)))
        write_tm(tor_level_a2a_tm, "tm/a2a_%d" % (rate))
        mlu = rate / float(100)
        generate(
            num_ToRs=num_tors,
            total_hosts=hosts,
            host_bw=1,
            mlu = mlu,
            host_to_host_tm = server_level_a2a_tm,
            duration=time,
            ofile='traffic/a2a/%d/flow.txt' % (rate),
            cdf_file='web_1G.txt'
        )

        tor_level_worst_tm, server_level_worst_tm = gen_worst_tm("demo_mat", rate / float(100))
        write_tm(tor_level_worst_tm, "tm/worst_%d" % (rate))
        generate(
            num_ToRs=num_tors,
            total_hosts=hosts,
            host_bw=1,
            mlu = mlu,
            host_to_host_tm = server_level_worst_tm,
            duration=time,
            ofile='traffic/worst/%d/flow.txt' % (rate),
            cdf_file='web_1G.txt'
        )

        tor_level_rnd_tm, server_level_rnd_tm = gen_random_matrix(num_tors, hosts, host_per_tor * (rate / float(100)))
        write_tm(tor_level_rnd_tm, "tm/random_%d" % (rate))
        generate(
            num_ToRs=num_tors,
            total_hosts=hosts,
            host_bw=1,
            mlu = mlu,
            host_to_host_tm = server_level_rnd_tm,
            duration=time,
            ofile='traffic/random/%d/flow.txt' % (rate),
            cdf_file='web_1G.txt'
        )