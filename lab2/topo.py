# Copyright 2020 Lin Wang

# This code is part of the Advanced Computer Networks (2020) course at Vrije
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

import sys
import random
import queue


# Class for an edge in the graph
class Edge:
    def __init__(self):
        self.lnode = None
        self.rnode = None

    def remove(self):
        self.lnode.edges.remove(self)
        self.rnode.edges.remove(self)
        self.lnode = None
        self.rnode = None


# Class for a node in the graph
class Node:
    def __init__(self, id, type):
        self.edges = []
        self.id = id
        self.type = type

    # Add an edge connected to another node
    def add_edge(self, node):
        edge = Edge()
        edge.lnode = self
        edge.rnode = node
        self.edges.append(edge)
        node.edges.append(edge)
        return edge

    # Remove an edge from the node
    def remove_edge(self, edge):
        self.edges.remove(edge)

    # Decide if another node is a neighbor
    def is_neighbor(self, node):
        for edge in self.edges:
            if edge.lnode == node or edge.rnode == node:
                return True
        return False


# class Jellyfish:

#     def __init__(self, num_servers, num_switches, num_ports):
#         self.servers = []
#         self.switches = []
#         self.generate(num_servers, num_switches, num_ports)

#     def generate(self, num_servers, num_switches, num_ports):
        
#         # TODO: code for generating the jellyfish topology

class Fattree:

    def __init__(self, num_ports):
        self.servers = []
        self.switches = []
        self.links = []
        self.generate(num_ports)

    def generate(self, num_ports):

        iCoreLayerSwitch = int((num_ports / 2) ** 2)
        iAggLayerSwitch = int(num_ports * num_ports / 2)
        iEdgeLayerSwitch = int(num_ports * num_ports / 2)
        totalSwitches = int((5 * (num_ports ** 2)) / 4)
        ihost = int(((num_ports ** 3)) / 4)
        hosteachpod = int(((num_ports ** 2)) / 4)
        CoreIP = 0
        a = 0
        e = 0

        # Create Switches and Servers

        for x in range(0, totalSwitches + 1):
            if x < iCoreLayerSwitch:
                self.switches.append(Node(x, "Core Switch"))
            if x > iCoreLayerSwitch and x <= (iCoreLayerSwitch + iAggLayerSwitch):
                self.switches.append(Node(a, "Aggregation Switch"))
                a = a + 1
            if x > (iCoreLayerSwitch + iAggLayerSwitch) and x <= (
                    iCoreLayerSwitch + iAggLayerSwitch + iEdgeLayerSwitch):
                self.switches.append(Node(e, "Edge Switch"))
                e = e + 1

        for x in range(0, ihost):
            self.servers.append(Node(x, "Server"))

        # Create Links
        end = int(num_ports / 2)

        # Core Switches to Aggregation Switches
        for x in range(0, iAggLayerSwitch, end):
            for i in range(0, end):
                for j in range(0, end):
                    self.switches[i * end + j].add_edge(self.switches[iCoreLayerSwitch + x + i])
                    self.links.append([self.switches[i * end + j], self.switches[iCoreLayerSwitch + x + i]])

        # Aggregation Switches to Edge Switches
        for x in range(0, iAggLayerSwitch, end):
            for i in range(0, end):
                for j in range(0, end):
                    self.switches[iCoreLayerSwitch+x+i].add_edge(self.switches[iCoreLayerSwitch+iAggLayerSwitch+x+j])
                    self.links.append([self.switches[iCoreLayerSwitch+x+i], self.switches[iCoreLayerSwitch+iAggLayerSwitch+x+j]])

        # Edge Switches to servers
        for x in range(0, iEdgeLayerSwitch):
            for i in range(0, end):
                self.switches[iCoreLayerSwitch + iAggLayerSwitch + x].add_edge(self.servers[end * x + i])
                self.links.append([self.switches[iCoreLayerSwitch + iAggLayerSwitch + x], self.servers[end * x + i]])
