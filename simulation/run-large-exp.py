import os

if __name__ == "__main__":
    patterns = ["a2a", "worst", "random"]
    rates = [30, 70, 100]
    ecmp_cmd_fmt = "python2 waf --run 'scratch/fc mix/failure-exps/large/config/ecmp/%s/%d/config.txt' > out/ecmp_%s_%d & "
    clos_cmd_fmt = "python2 waf --run 'scratch/fat-tree mix/failure-exps/large/config/clos/%s/%d/config.txt' > out/clos_%s_%d & "
    disjoint_cmd_fmt = "python2 waf --run 'scratch/fc mix/failure-exps/large/config/disjoint/%s/%d/config.txt' > out/disjoint_%s_%d & "
    edst_cmd_fmt = "python2 waf --run 'scratch/fc mix/failure-exps/large/config/edst/%s/%d/config.txt' > out/edst_%s_%d & "
    
    """
    RUN: edst (skewed )
    DONE: clos, ecmp, disjoint
    """
    os.system("python2 waf --run 'scratch/fc mix/failure-exps/large/config/edst/%s/%d/config.txt' > out/edst_%s_%d & " % ("worst", 30, "worst", 30)) 
    # os.system("python2 waf --run 'scratch/fc mix/failure-exps/large/config/disjoint/%s/%d/config.txt' > out/edst_%s_%d & " % ("worst", 100, "worst", 100)) 
    # os.system("python2 waf --run 'scratch/fc mix/failure-exps/large/config/disjoint/%s/%d/config.txt' > out/edst_%s_%d & " % ("worst", 70, "worst", 70)) 
    
    # rates = [30, 70, 100]
    # patterns = ['worst']
    # rates = [30]
    # for pattern in patterns:
    #    for rate in rates:
    #         os.system(ecmp_cmd_fmt % (pattern, rate, pattern, rate))
            # os.system(clos_cmd_fmt % (pattern, rate, pattern, rate))
            # os.system(ecmp_cmd_fmt % (pattern, rate, pattern, rate))
            # os.system(disjoint_cmd_fmt % (pattern, rate, pattern, rate))
