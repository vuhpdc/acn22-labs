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
import matplotlib.pyplot as plt


class Graph:
    def __init__(self, servers, switches):
        servers.extend(switches)
        self.entities = servers
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

    def find_min_distance(self):
        self.identify_neighbours()
        all_distance = {}
        for i in self.entities:
            dist = self.dijkstra(i)
            all_distance[i.id] = dist
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
        dist[src.id] = 0
        sptSet = {i.id: False for i in self.entities}

        for i in self.entities:
            x = self.min_distance(dist, sptSet)
            sptSet[x] = True
            for y in self.entities:
                if self.graph[x][y.id] > 0 and sptSet[y.id] == False and dist[y.id] > dist[x] + self.graph[x][y.id]:
                    dist[y.id] = dist[x] + self.graph[x][y.id]

        return dist


def gen_server_pairs(servers):
    server_pairs = {}
    for i in range(len(servers)):
        for j in range(i+1, len(servers)):
            server_pairs[(servers[i].id, servers[j].id)] = -1
    return server_pairs


def frequency(server_pairs, all_distance):
    histogram = {}
    total = 0
    for i in server_pairs:
        total += 1
        server_pairs[i] = all_distance[i[0]][i[1]]
        try:
            histogram[str(all_distance[i[0]][i[1]])] += 1
        except:
            histogram[str(all_distance[i[0]][i[1]])] = 1

    for i in histogram:
        histogram[i] /= total

    return histogram


#Configuration
num_servers = 686
num_switches = 245
num_ports = 14

# run jelly fish 10 times
j_v_l = []
for i in range(10):
    jf_topo = topo.Jellyfish(num_servers, num_switches, num_ports)
    # For JellyFish
    server_pairs = gen_server_pairs(jf_topo.servers)
    g1 = Graph(jf_topo.servers, jf_topo.switches)
    all_distance = g1.find_min_distance()
    jelly_histo = frequency(server_pairs, all_distance)
    j_k = [*jelly_histo.keys()]
    j_v = [*jelly_histo.values()]
    j_v_l.append(j_v)
    j_k = [int(x) for x in j_k]

print(j_v_l)
j_v = [sum(x)/len(x) for x in zip(*j_v_l)]
print(j_v)


ft_topo = topo.Fattree(num_ports)
# For fat tree
server_pairs = gen_server_pairs(ft_topo.servers)
g2 = Graph(ft_topo.servers, ft_topo.switches)
all_distance = g2.find_min_distance()
fat_histo = frequency(server_pairs, all_distance)
f_k = [*fat_histo.keys()]
f_v = [*fat_histo.values()]
f_k = [int(x) for x in f_k]

c = list(set(f_k + j_k))

f_k = [x + 0.3 for x in f_k]

print(f_k, j_k, c)

plt.bar(j_k, j_v, width=0.3, label='JellyFish')
plt.bar(f_k, f_v, width=0.3, label='FatTree')
plt.xlabel('Path length')
plt.ylabel('Fraction of Server Pairs')
plt.xticks([int(x) + 0.3 for x in c], c)
plt.legend()

plt.savefig('Figure_1c.jpg')
