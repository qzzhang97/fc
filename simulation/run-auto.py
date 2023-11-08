import os
import time


SLEEP_UNIT = 5 * 60
cmds = []


EDST_KWOD = "edst"
DISJOINT_KWOD = "disjoint"
CLOS_KWOD = "clos"
ECMP_KWOD = "ecmp"

CLOS_PARALLEL_NUM = 9
ECMP_PARALLEL_NUM = 9
DISJOINT_PARALLEL_NUM = 3
EDST_PARALLEL_NUM = 1

parallel_conf = {
    CLOS_KWOD : CLOS_PARALLEL_NUM,
    ECMP_KWOD : ECMP_PARALLEL_NUM,
    DISJOINT_KWOD : DISJOINT_PARALLEL_NUM,
    EDST_KWOD : EDST_PARALLEL_NUM,
}

def check_over(keyword):
    cmd = "ps axu|grep %s > keyword_log" % (keyword)
    # print(cmd)
    os.system(cmd)
    keyf = open('keyword_log', mode='r')
    lines = keyf.read().splitlines()
    keyf.close()
    # print(len(lines))
    is_over = (len(lines) == 2)
    # print(is_over)
    return is_over

def auto():
    patterns = ["a2a", "worst", "random"]
    # patterns = ["random_1", "random_2", "random_3", "random_4", "random_5"]
    patterns = ["random"]
    rates = [30, 70, 100]
    clos_cmd_fmt = "python2 waf --run 'scratch/fat-tree mix/failure-exps/large/config/clos/%s/%d/config.txt' > out/rnd/clos_%s_%d &"
    ecmp_cmd_fmt = "python2 waf --run 'scratch/fc mix/failure-exps/large/config/ecmp/%s/%d/config.txt' > out/rnd/ecmp_%s_%d &"
    disjoint_cmd_fmt = "python2 waf --run 'scratch/fc mix/failure-exps/large/config/disjoint/%s/%d/config.txt' > out/rnd/disjoint_%s_%d &"
    edst_cmd_fmt = "python2 waf --run 'scratch/fc mix/failure-exps/large/config/edst/%s/%d/config.txt' > out/rnd/edst_%s_%d &"
    
    clos_tasks = []
    ecmp_tasks = []
    edst_tasks = []
    disjoint_tasks = []
    for pattern in patterns:
       for rate in rates:
            clos_tasks.append(clos_cmd_fmt % (pattern, rate, pattern, rate))
            ecmp_tasks.append(ecmp_cmd_fmt % (pattern, rate, pattern, rate))
            disjoint_tasks.append(disjoint_cmd_fmt % (pattern, rate, pattern, rate))
            edst_tasks.append(edst_cmd_fmt % (pattern, rate, pattern, rate))

    all_tasks = {
        CLOS_KWOD : clos_tasks,
        ECMP_KWOD : ecmp_tasks,
        DISJOINT_KWOD : disjoint_tasks,
        EDST_KWOD : edst_tasks,
    }
    # rerun = []
    # for key in all_tasks:
    #     for cmd in all_tasks[key]:
    #         print(cmd)
            
    execution_order = [CLOS_KWOD, ECMP_KWOD, DISJOINT_KWOD, EDST_KWOD, '']
    # for od in execution_order:
    #     if od == '':
    #         print('ov')
    running_index = 0
    running_task = execution_order[running_index]
    bg = time.time(),
    while True:
        cur_time = time.strftime("%Y-%m-%d %H:%M:%S")
        if check_over(running_task):
            if len(all_tasks[running_task]) != 0:
                for _ in range(parallel_conf[running_task]):
                    # execute task
                    if len(all_tasks[running_task]) > 0:
                        to_run_cmd = all_tasks[running_task][0]
                        print('%s START [%s]' % (cur_time, to_run_cmd))
                        os.system(to_run_cmd)
                        all_tasks[running_task].remove(to_run_cmd)
            else:
                print('%s CHANGE TASK [%s]->[%s]' % (cur_time, execution_order[running_index], execution_order[running_index + 1]))
                running_index += 1
                running_task = execution_order[running_index]
                for _ in range(parallel_conf[running_task]):
                    if len(all_tasks[running_task]) > 0:
                        to_run_cmd = all_tasks[running_task][0]
                        print('%s START [%s]' % (cur_time, to_run_cmd))
                        os.system(to_run_cmd)
                        all_tasks[running_task].remove(to_run_cmd)
        else:
            print("%s: CHECK [%s] TASK NOT OVER" % (cur_time, running_task))
            
        if running_task == '':
            print("%s: ALL TASKS ARE OVER EXIT LOOP" % (cur_time))
            break
        
        time.sleep(SLEEP_UNIT)
        
    ed = time.time()
    print('total %ds' % (ed - bg))



if __name__ == "__main__":
    # print(time.strftime("%Y-%m-%d %H:%M:%S"))
    auto()