import heapq

class Flow:
	def __init__(self, src, dst, size, t):
		self.src, self.dst, self.size, self.t = src, dst, size, t
	def __str__(self):
		return "%d %d 3 100 %d %.9f"%(self.src, self.dst, self.size, self.t)
	def __lt__(self, other):
		return self.t < other.t

def modify(src_flow_file, dst_flow_file):
    src_f = open(src_flow_file, mode='r')
    src_flows = src_f.read().splitlines()
    flows = []
    for flow_content in src_flows[1:]:
        data = flow_content.split()
        flows.append(
            Flow(
                src=int(data[0]),
                dst=int(data[1]),
                size=1000,
                t = float(data[5])
            )
        )
    
    out = open(dst_flow_file, "w")
    out.write("%d\n" % (len(flows)))
    heapq.heapify(flows)
    while len(flows) > 0:
        out.write("%s 0\n" % (flows[0]))
        heapq.heappop(flows)
        
if __name__ == "__main__":
    modify("traffic/worst/30/flow.txt", "traffic/worst/30/flow2.txt")