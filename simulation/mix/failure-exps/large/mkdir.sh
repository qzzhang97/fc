#!/bin/bash
# rm -rf config/ output/ topo/ trace/ traffic/ tm/

exps=(clos ecmp disjoint edst)
patterns=(random_1 random_2 random_3 random_4 random_5)
rates=(30 70 100)
# random_num = (1 2 3 4 5)
echo "mkdirs ..."
for exp in ${exps[@]};
do
    for pattern in ${patterns[@]};
    do  
        for rate in ${rates[@]};
        do
            output_dir="output/$exp/$pattern/$rate"
            traffic_dir="traffic/$pattern/$rate"
            config_dir="config/$exp/$pattern/$rate"
            # trace_dir="../large/trace/$exp/"
            # topo_dir="../large/topo/$exp/"
            mkdir -p $config_dir $output_dir $traffic_dir $topo_dir $trace_dir
        done
    done
done

mkdir tm/

# ##
# echo "large conf files ..."
# python3 clos-1152.py 
# python fc.py
# python traffic.py
# python conf.py
# echo "COMPUTE EDST and DISJOINT PATHS..."
# sh run.sh