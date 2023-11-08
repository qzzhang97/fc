from audioop import reverse
from cgi import print_arguments
import heapq
import copy
import time
import numpy as np 
import os
from multiprocessing import Process, Value, Array, Queue

INF = 1024

"""
--SHORTEST PATH BETWEEN ANY SRC-DST PAIR--
    0
  / |  \ 
 1  2   3
 \  /\  /
  4    5
   \  /
    6
topo_matrix = [
    [0, 1, 1, 1, INF, INF, INF],
    [1, 0, INF, INF, 1, INF, INF],
    [1, INF, 0, INF, 1, 1, INF],
    [1, INF, INF, 0, INF, 1, INF],
    [INF, 1, 1, INF, 0, INF, 1],
    [INF, INF, 1, 1, INF, 0, 1],
    [INF, INF, INF, INF, 1, 1, 0]
]
"""
def test_cal_shortest_path():
  topo_matrix = [
    [0, 1, 1, 1, INF, INF, INF],
    [1, 0, INF, INF, 1, INF, INF],
    [1, INF, 0, INF, 1, 1, INF],
    [1, INF, INF, 0, INF, 1, INF],
    [INF, 1, 1, INF, 0, INF, 1],
    [INF, INF, 1, 1, INF, 0, 1],
    [INF, INF, INF, INF, 1, 1, 0]
  ]
  switches = 7
  sp_path = cal_shortest_path(topo_matrix, switches)
  print(sp_path[0][6])
  print(sp_path[5][0])

"""
FIND ALL SHORTEST PATHS BETWEEN ANY SRC-DST PAIRS
"""
def dijkstra_algo(topo, switches, src):
  pq = []
  pre = [[] for _ in range(switches)]
  visited = [False for _ in range(switches)]
  dis = [INF for _ in range(switches)]
  dis[src] = 0
  ## pair: (distance, u) src->u 
  # print(dis)
  heapq.heappush(pq, [0, src])
  
  while len(pq) > 0:
    pair = heapq.heappop(pq)
    u = pair[1]
    # print("loops")
    if visited[u]: continue
    visited[u] = True
    
    for v in range(switches):

      if topo[u][v] != 1: continue
      # print("v-{}".format(v))
      if dis[v] > dis[u] + topo[u][v]:
        # print("aoo")
        dis[v] = dis[u] + topo[u][v]
        del pre[v][:]
        pre[v].append(u)
        if not visited[v]: heapq.heappush(pq, [dis[v], v])
      elif dis[v] == dis[u] + topo[u][v]:
        pre[v].append(u)
        if not visited[v]: heapq.heappush(pq, [dis[v], v])
  # print(pre)
  return pre

def dfs(pre, paths, path, src, dst, cur):
  if cur == src:
    path.append(src)
    # print("dfs {}".format(path))
    deepPath = copy.deepcopy(path)
    deepPath.reverse()
    paths.append(deepPath)

    path.pop()
    return
  
  for i in range(len(pre[cur])):
    path.append(cur)
    dfs(pre, paths, path, src, dst, pre[cur][i])
    path.pop()
    
def read_path(shortest_path_pair, path_file):
    path_f = open(path_file, mode='r')
    lines = path_f.read().splitlines()
    path_f.close()
            
    idx = 0
    l0 = [int(x) for x in lines[idx].split()]
    pairs = l0[0]

    idx += 1
    for _ in range(pairs):
        l = [int(x) for x in lines[idx].split()]
        idx +=1
        src = l[0]
        dst = l[1]
        path_num = l[2]
        # print(l)
        for _ in range(path_num):
            shortest_path_pair[ src ][ dst ].append([int(x) for x in lines[idx].split()][ 1 : ])
            idx += 1
    # print('read', shortest_path_pair[58][106])


def process_task(switches, topo_matrix, process_id, a, b, path_num_arr, path_len_arr):
  print("ECMP Process: %d started" % (process_id))
  start_time = time.time()
  shortest_paths_of_any_pair = {}
  for i in range(switches):
    shortest_paths_of_any_pair[i] = {}
    for j in range(switches):
      shortest_paths_of_any_pair[i][j] = []
  
  avg_num_paths = 0
  avg_path_len = 0
  pairs = 0
  for src in range(a, b):
    pre = dijkstra_algo(topo_matrix, switches, src)
    for dst in range(src + 1, switches):
      paths = []
      path = []
      dfs(pre, paths, path, src, dst, dst)
      # print(paths)
      shortest_paths_of_any_pair[src][dst] = paths
      dst_to_src_paths = []
      for path in paths:
          copyPath = copy.deepcopy(path)
          copyPath.reverse()
          dst_to_src_paths.append(copyPath)
      shortest_paths_of_any_pair[dst][src] = dst_to_src_paths
      pairs += 1
      avg_num_paths += len(paths)
      avg_path_len += len(paths[0])
  avg_num_paths /= float(pairs)
  avg_path_len /= float(pairs)
  path_num_arr[process_id] = avg_num_paths
  path_len_arr[process_id] = avg_path_len
  end_time = time.time()
  print("Process {} run@{:.2f}s".format(process_id, end_time - start_time))
  # if process_id == 0:
  #   print(shortest_paths_of_any_pair[58][106])
  # q.put(shortest_paths_of_any_pair) 
  f = open('temp/ecmp_temp%d' % (process_id), mode='w')
  f.write("%d\n" % (pairs * 2))
  for src in range(switches):
    for dst in range(switches):
      paths = shortest_paths_of_any_pair[src][dst]
      if len(paths) == 0:continue
      f.write("%d %d %d\n" % (src, dst, len(paths)))
      for path in paths:
        f.write("%d %s\n" % (len(path), " ".join(map(str, path))))


def cal_shortest_path(topo_matrix, switches):
  num_process = 8
  path_num_arr = Array('d', range(num_process))
  # shortest_path_len_arr = Array('d', range(num_process))
  path_len_arr = Array('d', range(num_process))
  
  shortest_path_pairs = {}
  for i in range(switches):
    shortest_path_pairs[i] = {}
    for j in range(switches):
      shortest_path_pairs[i][j] = []
  
  task_split = []
  task_split.append(0)
  for i in range(1, num_process ):
    task_split.append(i * (switches // num_process))
  task_split.append(switches)
  print("tasks=", task_split)
  processes = []
  for i in range(num_process):
    # unit = switches // num_process
    processes.append(Process(target=process_task, args=(switches, topo_matrix, i, task_split[i], task_split[i + 1], path_num_arr, path_len_arr)))
    
  for p in processes:
    p.start()

  for p in processes:
    p.join()
  print("Avg_num_of_paths: {:.2f}, avg_path_len: {:.2f}, avg_shortest_path_len: {:.2f}".format(np.average(path_num_arr), np.average(path_len_arr), np.average(path_len_arr), np.average(path_len_arr) ) )

  
  for process_id in range(num_process):
    path_file = "temp/ecmp_temp%d" % (process_id)
    read_path(shortest_path_pairs, path_file)
    os.remove(path_file)
  return shortest_path_pairs
  
def cal_path(topo_dir, path_ofile):
    mat_f = open(topo_dir, mode='r')
    lines = mat_f.read().splitlines()
    to_host, switches, sw2sw_links, servers = map(int, lines[0].split())
    topo_matrix = np.zeros((switches, switches))
    print('switch=', switches)
    for line in lines[2:]:
        data = list(map(int, line.split()))
        topo_matrix[data[0]][data[1]] = 1
        topo_matrix[data[1]][data[0]] = 1
    
    shortest_path_pairs = cal_shortest_path(topo_matrix, switches)
    
    print("write path to output file")
    path_f = open(path_ofile, mode='w')
    path_f.write("%d %d %d\n" % (switches * (switches - 1), to_host, switches) )
    for i in range(switches):
      for j in range(switches):
        if i == j: continue
        paths = shortest_path_pairs[i][j]
        if len(paths) == 0:
          print("err", i, j)
          exit(-1)
        path_f.write("%d %d %d\n" % (i, j, len(paths) ) )
        for path in paths:
          path_f.write("%d %s\n" % ( len(path), " ".join(map(str, path) ) ) )
        
if __name__ == "__main__":
    cal_path("demo_mat", "topo/ecmp/path.txt")
    # cal_path("disjoint-path/topo/fc_3000_4", "disjoint-path/path/ecmp_3000_4")
