import networkx as nx
import topo
import sys
import matplotlib.pyplot as plt
import sys
import random
import queue
from random import randrange
import math


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


class GraphVisualization:

    def __init__(self):

        # visual is a list which stores all
        # the set of edges that constitutes a
        # graph
        self.visual = []

    # addEdge function inputs the vertices of an
    # edge and appends it to the visual list
    def addEdge(self, a, b):
        temp = [a, b]
        self.visual.append(temp)

    # In visualize function G is an object of
    # class Graph given by networkx G.add_edges_from(visual)
    # creates a graph with a given list
    # nx.draw_networkx(G) - plots the graph
    # plt.show() - displays the graph
    def visualize(self):
        G = nx.Graph()
        G.add_edges_from(self.visual)
        fig = plt.figure(2, figsize=(15, 15))
        nx.draw_networkx(G, node_size=1000, font_size=24)
        plt.show()


num_servers = 20
num_switches = 10
num_ports = 4
jf_topo = topo.Jellyfish(num_servers, num_switches, num_ports)
ft_topo = topo.Fattree(num_ports)
bc_topo = topo.BCube(1, 4)

g1 = Graph(jf_topo.servers, jf_topo.switches)
g1.identify_neighbours()
jgv = GraphVisualization()
for i in g1.graph:
    for j in g1.graph[i]:
        if g1.graph[i][j] == 1:
            jgv.addEdge(i, j)

jgv.visualize()

g1 = Graph(ft_topo.servers, ft_topo.switches)
g1.identify_neighbours()
jgv = GraphVisualization()
for i in g1.graph:
    for j in g1.graph[i]:
        if g1.graph[i][j] == 1:
            jgv.addEdge(i, j)

jgv.visualize()


g1 = Graph(bc_topo.servers, bc_topo.switches)
g1.identify_neighbours()
jgv = GraphVisualization()
for i in g1.graph:
    for j in g1.graph[i]:
        if g1.graph[i][j] == 1:
            jgv.addEdge(i, j)

jgv.visualize()
