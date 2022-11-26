import sys

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
        all_paths = {}
        for i in self.entities:
            dist = self.dijkstra(i)
            all_paths[i.id] = dist
        return all_paths

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
        paths = {i.id: [] for i in self.entities}
        paths[src] = [src]
        
        for i in self.entities:
            x = self.min_distance(dist, sptSet)
            sptSet[x] = True
            for y in self.entities:
                if self.graph[x][y.id] > 0 and sptSet[y.id] == False and dist[y.id] > dist[x] + self.graph[x][y.id]:
                    dist[y.id] = dist[x] + self.graph[x][y.id]
                    paths[y.id].extend(paths[x])
                    paths[y.id].append(y.id)

        return paths
