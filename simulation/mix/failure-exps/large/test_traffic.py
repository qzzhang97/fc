import sys
import random
import math
import heapq


random.seed(6699)

class Flow:
	def __init__(self, src, dst, size, t):
		self.src, self.dst, self.size, self.t = src, dst, size, t
	def __str__(self):
		return "%d %d 3 100 %d %.9f"%(self.src, self.dst, self.size, self.t)
	def __lt__(self, other):
		return self.t < other.t

def generate(ofile="traffic/worst/30/flow.txt"):
    flows = []
    switches = 144
    hosts_per_sw = 8
    base_t = 2000000000
    for src_sw in range(switches):
        for dst_sw in range(switches):
            if src_sw == dst_sw: continue
            src_host = src_sw * hosts_per_sw
            dst_host = dst_sw * hosts_per_sw
            flows.append( Flow(src_host, dst_host, 1000, (base_t + 1000 * src_sw)* 1e-9) )
    
    out = open(ofile, "w")
    out.write("%d\n" % (len(flows)))

    heapq.heapify(flows)
    while len(flows) > 0:
        out.write("%s 0\n" % (flows[0]))
        heapq.heappop(flows)



if __name__ == "__main__":
    generate()
