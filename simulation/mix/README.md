# 一些文件含义
## fct.txt文件格式
Eg output:
```
0b000301 0b000101 10000 100 2000000 2000000000 502008 171840
```
Sip:0b000301, Dip:0b000301, Sport: 10000, Dport:100, size:2000000Byte, start_time(ns): 2000000000, FCT(ns):502008, standalone_fct(ns):171840。standalone FCT我猜是指网络中没有其他流和这个流竞争的完成时间。
## flow.txt文件line含义
Eg Line
```
2 1 3 100 200000000 2
```
src_node: 2, dst_node: 1, priority_group: 3, dst_port: 100, size(Packet Count): 200000000, start_time(s):2。假设每个packet大小为1000byte，则该流的大小近似为200 000 000 * 1000 = 200 000 000 000(bytes) = 200Gbytes.

## topology.txt文件含义
Eg line
```
0 1 100Gbps 0.001ms 0
```
src_node:0, dst_node:1, link_speed:100Gbps, link_delay: 0.001ms, error rate:0。

## fat.txt
* 20 ToR switches.
* 20 Aggregation Switches.
* 16 Core switches.
* Each ToR connect 16 hosts.

## gen topology
Generate topology file. 此文件只会生成单个Pod内的拓扑文件
```
python topology_gen.py -f ./pod_250/pod_250.txt -n 500 -t 25 -a 25
```

## gen trace
generate trace file
```
python trace_gen.py -f pod_500/trace.txt -t 550
```

## Exp实验(Now Doing and TODO)
1. 根据流量矩阵来计算核心层的拓扑结构。
2. 根据流量矩阵生成流量来验证效果。

## Traffic Aware Topology
### Topology Computation

### Traffic Generation
