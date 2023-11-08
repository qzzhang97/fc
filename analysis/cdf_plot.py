import matplotlib.pyplot as plt 

if __name__ == "__main__":
    cdf_files = [
        # "../traffic_gen/AliStorage2019.txt",
        # "../traffic_gen/FbHdp_distribution.txt",
        "../traffic_gen/WebSearch_distribution.txt",
    ]

    cdf = {}
    for f_name in cdf_files:
        file = open(f_name)
        cdf[f_name] = []
        percentile = []
        size = []
        for line in file.readlines():
            d = line.replace('\n','').split(' ')
            size.append(int(d[0]))
            percentile.append(float(d[1]))
        cdf[f_name].append(size)
        cdf[f_name].append(percentile)
    for f_name in cdf_files:   
        plt.plot(cdf[f_name][1], cdf[f_name][0], 'r-^', label=f_name.replace("../traffic_gen/", "").replace(".txt", ""))
    plt.xlabel("CDF")
    plt.ylabel("SIZE(Bytes)")
    plt.legend()
    plt.grid('-.')
    plt.show()
        
        