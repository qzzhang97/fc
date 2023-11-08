import matplotlib.pyplot as plt

class CompletedPkt:
    def __init__(self, snode, sport, payload, pct_ns):
        self.snode = snode
        self.sport = sport
        self.payload = payload
        self.pct_ns = pct_ns

def filter_flow_pkts(completed_pkts, snode, sport):
    ret = []
    for pkt in completed_pkts:
        if pkt.snode == snode and pkt.sport == sport:
            ret.append(pkt)
    return ret

def cal_throughput(completed_pkts):
    times = []
    throughputs = []
    base_t = 2000000000
    payload = 1000
    for pkt in completed_pkts:
        cur_t = pkt.pct_ns
        throughputs.append(payload * 8 / (cur_t - base_t) )
        base_t = cur_t
        times.append(cur_t)
        payload = pkt.payload
    return times, throughputs
            

if __name__ == "__main__":
    CCs = [
        "dcqcn",
        "hpcc"   
    ]
    shosts = [0,1]
    completed_pkts = {"dcqcn":[], "hpcc":[]}
    for cc in CCs:
        file = "../simulation/mix/pcn/pkt_%s.txt" % cc 
        f = open(file, mode='r')
        for line in f.readlines():
            d = line.split(' ')
            completed_pkts[cc].append(
                CompletedPkt(
                    snode=int(d[0]),
                    sport=int(d[1]),
                    payload=int(d[2]),
                    pct_ns=int(d[3])
                )
            )
    flows = {"dcqcn":{}, "hpcc":{}}
    for cc in CCs:
        print(cc)
        for host in shosts:
            flows[cc][host] = filter_flow_pkts(completed_pkts[cc], host, 10000)
            # print( len(flows[host]) )
    
    t1, th1 = cal_throughput(flows["dcqcn"][0])   
    t2, th2 = cal_throughput(flows["dcqcn"][1])
    # print(t1[:10])
    # print(t2[:10])
    plt.plot(t1, th1, 'g', label="dcqcn")
    plt.plot(t2, th2, 'r',label='hpcc')
    plt.legend()
    plt.title("Converge Test")
    plt.xlabel("Time (ns)")
    plt.ylabel("Throughput (Gbps)")
    plt.show()
    
            



    
