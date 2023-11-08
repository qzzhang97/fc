# !/usr/bin/python3
# coding=utf-8
from optparse import OptionParser
# random.seed(1)
    
def fat_tree(bw=1, topo_dir="", trace_dir=""):
    pod_num = 4
    host_per_ToR = 18
    tor_switches_num = 16 * 4
    agg_switches_num = 14 * 4
    core_switches_num = 28
    hosts_num = host_per_ToR * tor_switches_num
    # print("%d pods" % (pod_num))
    # print(f"ToR: {tor_switches_num}, Agg: {agg_switches_num}, Core: {core_switches_num} Pods: {pod_num}, host: {hosts_num}" )
    host_ids = [id for id in range(hosts_num)]
    tor_switch_ids = [id + hosts_num for id in range(tor_switches_num)]
    agg_switches_ids = [hosts_num + tor_switches_num + id for id in range(agg_switches_num)]
    core_switch_ids = [id + hosts_num + tor_switches_num + agg_switches_num for id in range(core_switches_num)]

    # print(core_switch_ids)
    """
    calculate bandwidth
    """
    h2tor_link = hosts_num
    tor2agg_link = 16 * 14 * 4
    agg2core_link = 14 * 14 * 4
    # print("host links: %d, Tor_to_Agg links: %d Agg_to_Core links: %d" % (h2tor_link, tor2agg_link, agg2core_link))

    # topo is the topo file path
    topo_file = open(topo_dir, mode='w')
    links = h2tor_link + tor2agg_link + agg2core_link
    total_nodes = hosts_num + tor_switches_num + core_switches_num + agg_switches_num
    switch_nodes = tor_switches_num + core_switches_num + agg_switches_num
    topo_file.write("%d %d %d\n" % (total_nodes, switch_nodes, links) )

    switches = []
    switches.extend(tor_switch_ids)
    switches.extend(agg_switches_ids)
    switches.extend(core_switch_ids)
    # print("switch ids: ", switches)
    topo_file.write("%s\n" % ( " ".join(map(str, switches)) ) )
    
    ## connect host to ToR switches.
    for host_id in host_ids:
        # print('hid', host_id)
        topo_file.write("%d %d %.2fGbps %dns 0.000000\n" % (host_id, tor_switch_ids[host_id // host_per_ToR], bw, 1000) )
        
    ## connect ToR switches to Agg switches
    tor_per_pod = tor_switches_num // pod_num
    agg_per_pod = agg_switches_num // pod_num
    # print("ToR_Per_Pod: {} Agg_Per_Pod: {}".format(tor_per_pod, agg_per_pod))
    for pod in range(pod_num):
        for i in range(agg_per_pod):
            agg_idx = pod * agg_per_pod + i
            # each aggregation switch will be connect to every ToR of current pod
            for j in range(tor_per_pod):
                tor_idx = pod * tor_per_pod + j
                topo_file.write("%d %d %.2fGbps %dns 0.000000\n" % (tor_switch_ids[tor_idx], agg_switches_ids[agg_idx], bw, 1000) )

    # ## connect Agg switches to Core switches
    for pod in range(pod_num):
        for i in range(agg_per_pod):
            agg_id = pod * agg_per_pod + i
            if i % 2 == 0:
                for core_id in range(core_switches_num // 2):
                    # print(core_id)
                    topo_file.write("%d %d %.2fGbps %dns 0.000000\n" % (agg_switches_ids[agg_id], core_switch_ids[core_id], bw, 1000) )
            else:
                for core_id in range(core_switches_num // 2, core_switches_num):
                    topo_file.write("%d %d %.2fGbps %dns 0.000000\n" % (agg_switches_ids[agg_id], core_switch_ids[core_id], bw, 1000) )
    topo_file.close()

    """
    generate trace file
    """
    trace_file = open(trace_dir, mode='w')
    trace_file.write("%d\n" % (total_nodes))
    trace_file.write("%s\n" % (" ".join( map(str, [id for id in range(total_nodes)]) ) ) )
    trace_file.close()
    
    return True

if __name__ == "__main__":
    topo_fmt = "./topo/clos/topo.txt"
    trace_fmt = "./trace/clos/trace.txt"
    
    ret = fat_tree(
        bw=25,
        topo_dir=(topo_fmt), 
        trace_dir=(trace_fmt)
    )
