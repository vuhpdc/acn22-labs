import matplotlib.pyplot as plt
import networkx as nx
import topo

# Same setup for Jellyfish and Fattree
num_servers = 16
num_switches = 20
num_ports = 4
core = []
aggr = []
edge = []

# jf_topo = topo.Jellyfish(num_servers, num_switches, num_ports)
ft_topo = topo.Fattree(num_ports)
for i in range(len(ft_topo.switches)):
    if (ft_topo.switches[i].type == "Core Switch"):
        core.append(ft_topo.switches[i])
    elif ft_topo.switches[i].type == "Aggregation Switch":
        aggr.append(ft_topo.switches[i])
    else:
        edge.append(ft_topo.switches[i])
        
G  = nx.Graph()
G.add_nodes_from(ft_topo.servers)
G.add_nodes_from(ft_topo.switches)
G.add_edges_from(ft_topo.links)
# nx.draw(G)
pos=nx.spring_layout(G)
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_nodes(G, pos,node_color="#1302f5",nodelist=core)
nx.draw_networkx_nodes(G, pos,node_color="#6044db",nodelist=aggr)
nx.draw_networkx_nodes(G, pos,node_color="#03fcf8",nodelist=edge)
nx.draw_networkx_nodes(G,pos, node_color="#ff0070",nodelist=ft_topo.servers)
plt.show()