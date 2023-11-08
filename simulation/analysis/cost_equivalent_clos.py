import numpy as np

def max_throughput(N, p, h0):
    print("N=%d p=%d h0=%d" % (N, p, h0))
    for L in range(2, 6):
        h_optimal = ((2 * L - 2) * h0 * p) / float(p + (2 * L - 3) * h0)
        if h_optimal > p:
            break
        optimal_ratio = (p - h0) / ((2 * L - 2) * h0)
        maximum_servers = (2 * (p / 2) ** (L - 1)) * h_optimal
        print("L: %d, h_optimal: %.2f, optimal ratio: %.2f maximum servers: %.2f" % (L, h_optimal, optimal_ratio, maximum_servers))

if __name__ == "__main__":
    max_throughput(N=100, p=64, h0=24)
    max_throughput(N=200, p=64, h0=24)
    max_throughput(N=300, p=64, h0=24)