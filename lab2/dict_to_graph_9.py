import pickle
import matplotlib.pyplot as plt
import numpy as np
import sys
f = open("dict.pickle","rb")
ld_dict = pickle.load(f)


def func_yen_8():
    edge_count={}
    for server_pairs in ld_dict.keys():
        count = 0
        for paths in ld_dict[server_pairs]:
            if count == 8:
                break
            count+=1
            for nodes in range(0,len(paths)-1):
                a = paths[nodes]
                b = paths[nodes+1]
                try:
                    edge_count[(a,b)] += 1
                except:
                    edge_count[(a,b)] = 1
    return edge_count

def func_ecmp(cnt):
    edge_count={}
    for server_pairs in ld_dict.keys():
        count = 0
        shp = len(ld_dict[server_pairs][0])
        for paths in ld_dict[server_pairs]:
            if count == cnt or shp != len(paths):
                break
            count+=1
            for nodes in range(1,len(paths)-2):
                a = paths[nodes]
                b = paths[nodes+1]
                try:
                    edge_count[(a,b)] += 1
                except:
                    edge_count[(a,b)] = 1
    return edge_count


w8_edge_count = func_yen_8()
ecmp8 = func_ecmp(8)
ecmp64 = func_ecmp(64)


lstw8 = list(w8_edge_count.values())
lstw8.sort()
plt.plot(lstw8,'b',label="8 shortest paths")

lste8 = list(ecmp8.values())
lste8.sort()
plt.plot(lste8,'g',label="8 way ECMP")

lste64 = list(ecmp64.values())
lste64.sort()
plt.plot(lste64,'y',label="64 way ECMP")
plt.legend()
plt.savefig("jelly_fish_graph9.jpg")