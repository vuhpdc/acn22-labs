import sys

class Graph:
    def __init__(self, servers, switches):
        servers.extend(switches)
        self.entities = servers
        self.graph = {}
        for i in self.entities:
            self.graph[i.dpid] = {}
            for j in self.entities:
                self.graph[i.dpid][j.dpid] = 0

    def identify_neighbours(self):
        for i in self.entities:
            for j in i.edges:
                if i.dpid != j.lnode.dpid:
                    self.graph[i.dpid][j.lnode.dpid] = 1
                else:
                    self.graph[i.dpid][j.rnode.dpid] = 1

    def find_min_distance(self):
        self.identify_neighbours()
        all_paths = {}
        for i in self.entities:
            dist = self.dijkstra(i)
            all_paths[i.dpid] = dist
        return all_paths

    def min_distance(self, dist, sptSet):
        min = sys.maxsize
        min_index = 0

        for u in self.entities:
            if dist[u.dpid] < min and sptSet[u.dpid] == False:
                min = dist[u.dpid]
                min_index = u.dpid

        return min_index

    def dijkstra(self, src):
        dist = {i.dpid: sys.maxsize for i in self.entities}
        dist[src.dpid] = 0
        sptSet = {i.dpid: False for i in self.entities}
        paths = {i.dpid: [] for i in self.entities}
        paths[src] = [src]
        
        for i in self.entities:
            x = self.min_distance(dist, sptSet)
            sptSet[x] = True
            for y in self.entities:
                if self.graph[x][y.dpid] > 0 and sptSet[y.dpid] == False and dist[y.dpid] > dist[x] + self.graph[x][y.dpid]:
                    dist[y.dpid] = dist[x] + self.graph[x][y.dpid]
                    paths[y.dpid].extend(paths[x])
                    paths[y.dpid].append(y.dpid)

        return paths
