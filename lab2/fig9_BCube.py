# This code is part of the Advanced Computer Networks course at Vrije
# Universiteit Amsterdam.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import topo
import sys
import copy
import pickle
import random
def gen_server_pairs(servers):
    server_pairs = []
    all_servers_copy = servers[:]
    for sender in servers:
        recvr = random.choice(list(set(all_servers_copy)-set([sender])))
        server_pairs.append((sender.id,recvr.id))
        all_servers_copy.remove(recvr)
    return server_pairs


class Graph:
    def __init__(self, servers, switches):
        self.servers = servers
        self.server_pairs = gen_server_pairs(self.servers)
        self.entities = []
        for i in servers:
            self.entities.append(i)
        for i in switches:
            self.entities.append(i)

        self.graph = {}
        for i in self.entities:
            self.graph[i.id] = {}
            for j in self.entities:
                self.graph[i.id][j.id] = 0

    def identify_neighbours(self):
        for i in self.entities:
            for j in i.edges:
                if i.id != j.lnode.id:
                    self.graph[i.id][j.lnode.id] = 1
                else:
                    self.graph[i.id][j.rnode.id] = 1

    def find_k_paths(self, K):
        all_distance = {}
        print(len(self.server_pairs))
        for (src, dst) in self.server_pairs:
            self.identify_neighbours()
            A = []
            A.append(self.dijkstra(src)[1][dst])
            spl = len(self.dijkstra(src)[1][dst])
            B = []
            for kpath in range(1, K):
                if len(A) < kpath:
                    break
                for i in range(len(A[kpath-1])-2):
                    spurNode = A[kpath-1][i]
                    rootPath = A[kpath-1][:i+1]
                    for p in A:
                        if rootPath == p[:i+1]:
                            if len(p) > i+1:
                                self.graph[p[i]][p[i+1]] = 0
                                self.graph[p[i+1]][p[i]] = 0

                    for j in range(len(rootPath)-1):
                        node = rootPath[j]
                        for k in self.graph[node]:
                            self.graph[node][k] = 0
                        for k in self.graph:
                            self.graph[k][node] = 0

                    spurPath = self.dijkstra(spurNode)[1][dst]
                    if len(spurPath) > 1 and spurPath[-1] == dst:
                        totalPath = []
                        for j in rootPath:
                            totalPath.append(j)
                        for k in spurPath[1:]:
                            totalPath.append(k)

                        if totalPath not in B:
                            B.append(copy.deepcopy(totalPath))

                    self.identify_neighbours()
                if B == []:
                    break
                min = sys.maxsize
                min_path = -1
                for paths in range(len(B)):
                    if len(B[paths]) < min:
                        min_path = paths
                        min = len(B[paths])

                # ECMP for 64way
                if kpath >= 8:
                    if len(B[min_path]) != spl:
                        break

                if B[min_path] not in A:
                    A.append(copy.deepcopy(B[min_path]))  # deep copy

                del B[min_path]

            all_distance[(src, dst)] = A  # deep copy
        return all_distance

    def find_min_distance(self):
        self.identify_neighbours()
        all_distance = {}
        for i in self.servers:
            dist = self.dijkstra(i.id)
            all_distance[i.id] = dist[0]
            print(dist[1]['c1'])
            break
        return all_distance

    def min_distance(self, dist, sptSet):
        min = sys.maxsize
        min_index = 0
        for u in self.entities:
            if dist[u.id] < min and sptSet[u.id] == False:
                min = dist[u.id]
                min_index = u.id

        return min_index

    def dijkstra(self, src):
        dist = {i.id: sys.maxsize for i in self.entities}
        dist[src] = 0
        sptSet = {i.id: False for i in self.entities}
        paths = {i.id: [] for i in self.entities}
        paths[src] = [src]
        for i in self.entities:
            x = self.min_distance(dist, sptSet)
            sptSet[x] = True
            for y in self.entities:
                try:
                    if self.graph[x][y.id] > 0 and sptSet[y.id] == False and dist[y.id] > dist[x] + self.graph[x][y.id]:
                        paths[y.id].extend(paths[x])
                        # paths[y.id].append(x)
                        paths[y.id].append(y.id)
                        dist[y.id] = dist[x] + self.graph[x][y.id]
                except:
                    break
        #print(src.id, paths)
        return dist, paths

# Setup for BCube
number_of_levels = 3
number_of_ports = 4

# TODO: code for reproducing Figure 9 in the jellyfish paper
bc_topo = topo.BCube(number_of_levels, number_of_ports)
g1 = Graph(bc_topo.servers, bc_topo.switches)
all_distance = g1.find_k_paths(64)
f = open("Bcube.pickle", "wb")
pickle.dump(all_distance, f, protocol=pickle.HIGHEST_PROTOCOL)

