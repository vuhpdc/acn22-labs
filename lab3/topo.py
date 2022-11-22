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

import sys
import random
import queue
from random import randrange
import math

# region graph

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
    def __init__(self, id, type, ip, dpid = None):
        self.edges = []
        self.id = id
        self.type = type
        self.ip = ip
        self.dpid = dpid

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

# endregion

# region FatTree


class Fattree:

    def __init__(self, num_ports):
        # initialize arrays for switches and servers
        self.core_switches = []
        self.aggregate_switches = []
        self.edge_switches = []

        self.servers = []
        self.switches = []

        self.counter = 1

        # calculating max counts of servers and switches
        self.num_ports = num_ports
        self.max_pod_count = num_ports
        self.max_core_switch_count = int((num_ports / 2) ** 2)

        # generate the topology
        self.generate()

    def generate(self):

        # TODO: code for generating the fat-tree topology

        # generate pods
        for pod_number in range(0, self.max_pod_count):
            self.generate_pods(pod_number)

        # add core switches
        for j in range(1, int(self.num_ports/2) + 1):
            for i in range(1, int(self.num_ports/2) + 1):
                core_switch = Node('N{}'.format(
                    self.counter), 'switch', self.get_core_switch_ip(j, i))
                self.counter += 1
                # core_switch.data = self.addSwitch(core_switch.id)
                # self.core_switches.append(core_switch.data)
                self.core_switches.append(core_switch)
                self.switches.append(core_switch)

                # link core switches and aggregate switches
        for core_switch_number in range(self.max_core_switch_count):
            link_number = int(core_switch_number // (self.num_ports / 2))
            for pod_number in range(0, self.max_pod_count):
                # self.addLink(core_switch.data, self.aggregate_switches[pod_number][link_number].data)
                self.core_switches[core_switch_number].add_edge(
                    self.aggregate_switches[pod_number][link_number])

    def generate_pods(self, pod_number):
        # local variables
        pod_edge_switches = []
        pod_aggregate_switches = []

        # add edge switches
        for edge_switch_number in range(0, int(self.num_ports/2)):
            edge_switch = Node('N{}'.format(self.counter), 'switch', self.get_pod_switch_ip(
                pod_number, edge_switch_number))
            self.counter += 1
            # edge_switch.data = self.addSwitch(edge_switch.id)
            # pod_edge_switches.append(edge_switch.data)
            pod_edge_switches.append(edge_switch)
            self.switches.append(edge_switch)
        self.edge_switches.append(pod_edge_switches)

        # add servers and link them to edge switches
        for edge_switch_index, edge_switch in enumerate(pod_edge_switches):
            for server_number in range(2, int(self.num_ports / 2) + 2):
                # add server
                server = Node('N{}'.format(self.counter), 'server', self.get_server_ip(
                    pod_number, edge_switch_index, server_number))
                self.counter += 1
                # server.data = self.addHost(server.id)
                self.servers.append(server)

                # add link
                # self.addLink(edge_switch.data, server.data)
                edge_switch.add_edge(server)

        # add aggregate switches
        for aggregate_switch_number in range(int(self.num_ports/2), self.num_ports):
            aggregate_switch = Node('N{}'.format(self.counter), 'switch', self.get_pod_switch_ip(
                pod_number, aggregate_switch_number))
            self.counter += 1
            # aggregate_switch.data = self.addSwitch(aggregate_switch.id)
            # pod_aggregate_switches.append(aggregate_switch.data)
            pod_aggregate_switches.append(aggregate_switch)
            self.switches.append(aggregate_switch)
        self.aggregate_switches.append(pod_aggregate_switches)

        # link aggregate switches and edge switches
        for aggregate_switch in pod_aggregate_switches:
            for edge_switch in pod_edge_switches:
                # self.addLink(aggregate_switch.data, edge_switch.data)
                aggregate_switch.add_edge(edge_switch)

    def get_server_ip(self, pod_number, switch_number, server_number):
        return '10.{}.{}.{}'.format(pod_number, switch_number, server_number)

    def get_pod_switch_ip(self, pod_number, switch_number):
        return '10.{}.{}.1'.format(pod_number, switch_number)

    def get_core_switch_ip(self, j, i):
        return '10.{}.{}.{}'.format(self.num_ports, j, i)

# endregion
