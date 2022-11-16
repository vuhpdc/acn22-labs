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

# endregion

# region JellyFish


def getRandomSwitch(currentSwitch, switchList, totalOpenPorts):

    if len(switchList) > 0:
        tempRandomServer = random.choice(switchList)
        tempRandomServerName = tempRandomServer.id

        # print("tempRandomServerName",tempRandomServerName)

        if currentSwitch.is_neighbor(tempRandomServer):
            switchList.remove(tempRandomServer)
            return getRandomSwitch(currentSwitch, switchList, totalOpenPorts)
        elif totalOpenPorts[tempRandomServerName] == 0:
            switchList.remove(tempRandomServer)
            return getRandomSwitch(currentSwitch, switchList, totalOpenPorts)
        else:
            return tempRandomServer

    else:
        return -1


def getRandomAvailableSwitch(switchList, totalOpenPorts):

    tempRandomServer = random.choice(switchList)
    tempRandomServerName = tempRandomServer.id

    if totalOpenPorts[tempRandomServerName] == 0:
        return tempRandomServer
    else:
        return getRandomAvailableSwitch(switchList, totalOpenPorts)


def GetRandomEdge(randomSwitch):
    edgeList = randomSwitch.edges.copy()
    for edge in edgeList:
        if edge.rnode.id.startswith("c"):
            edgeList.remove(edge)
            # return GetRandomEdge(randomSwitch)

    return random.choice(edgeList)


def CheckforMultGraphs(currentNode, visitedList, paths, path_id, final_node_id):
    for edge in currentNode.edges:
        #print("current=",currentNode.id,"r=",edge.rnode.id, "l=",edge.lnode.id, "path_id=",path_id, "total=",len(currentNode.edges))

        if edge.lnode.id == final_node_id:
            #print("L End Reached")
            visitedList[path_id].append(edge.lnode.id)
            #print("visited list", path_id, visitedList[path_id])
            return True

        elif edge.rnode.id == final_node_id:
            #print("R End Reached")
            visitedList[path_id].append(edge.rnode.id)
            #print("visited list", path_id, visitedList[path_id])
            return True

        if not edge.rnode.id.startswith("c") and edge.rnode.id not in visitedList[path_id]:
            #print("R NOde not present", currentNode.id, edge.rnode.id)
            visitedList[path_id].append(edge.rnode.id)
            if CheckforMultGraphs(edge.rnode, visitedList, paths, path_id, final_node_id):
                return True

        if not edge.lnode.id.startswith("c") and edge.lnode.id not in visitedList[path_id]:
            #print("L NOde not present", currentNode.id, edge.lnode.id)
            visitedList[path_id].append(edge.lnode.id)
            if CheckforMultGraphs(edge.lnode, visitedList, paths, path_id, final_node_id):
                return True

    return False


def CheckAllConn(totalOpenPorts, switchList, num_ports):
    index = 0
    for op in totalOpenPorts:
        if totalOpenPorts[op] < num_ports and totalOpenPorts[op] > 0:
            # print("Switches Open:", op, totalOpenPorts[op])
            currentSwitch = switchList[index]

            randomSwitch = getRandomAvailableSwitch(switchList, totalOpenPorts)

            diffConn = num_ports - totalOpenPorts[op]
            if diffConn == 1:
                # print("Diff conn one")
                # Select a random edge to sever old connection and start a new connection
                currentEdge = GetRandomEdge(currentSwitch)
                randomEdge = GetRandomEdge(randomSwitch)

                # Remove neighbours for current switch
                currentSwitch.remove_edge(currentEdge)
                randomSwitch.remove_edge(randomEdge)

                # form new connections
                currentSwitch.add_edge(randomEdge)
                randomSwitch.add_edge(currentEdge)
                totalOpenPorts[op] -= 1

            else:
                # print("Doing Someting Awesome", diffConn)
                for i in range(0, diffConn):
                    # Select a random edge to sever old connection and start a new connection
                    randomEdge = GetRandomEdge(randomSwitch)
                    randomEdgeSwitch = randomEdge.rnode

                    # Remove neighbours for random switch
                    randomSwitch.remove_edge(randomEdge)

                    # form new connections
                    currentSwitch.add_edge(randomEdgeSwitch)
                    currentSwitch.add_edge(randomSwitch)
                    totalOpenPorts[op] -= 2

                #CheckAllConn(totalOpenPorts, switchList, num_ports)
        index += 1


class Jellyfish:

    def __init__(self, num_servers, num_switches, num_ports):
        self.servers = []
        self.switches = []
        self.generate(num_servers, num_switches, num_ports)

    def generate(self, num_servers, num_switches, num_ports):

        # TODO: code for generating the jellyfish topology
        ServerPerSwitch = math.ceil((num_servers/num_switches))

        # Define the total openports
        totalOpenPorts = {}

        # print("Servers per switch", num_servers, num_switches, ServerPerSwitch)
        if num_ports < ServerPerSwitch:
            # print("Not Enough Ports", num_ports, ServerPerSwitch)
            return

        # Lets add servers and switches and connect them
        for i in range(0, num_switches):
            switchId = "s"+str(i)
            totalOpenPorts[switchId] = num_ports

            tempSwitchNode = Node(switchId, "switch")
            self.switches.append(tempSwitchNode)

            # Create n servers and link them to the switches

            # Get the total of servers that were already created
            CurrentServerNo = len(self.servers)

            # Loop over the next set of servers and add them to the switch
            for s in range(CurrentServerNo, CurrentServerNo+ServerPerSwitch):
                if s < num_servers:
                    # Cretes a new server as a node
                    tempServerNode = Node("c"+str(s), "server")
                    self.servers.append(tempServerNode)

                    # Add an edge between the server and switch
                    tempSwitchNode.add_edge(tempServerNode)
                    totalOpenPorts[switchId] -= 1

        # Lets connect the switches together
        for currentSwitch in self.switches:
            #print("current switch id", currentSwitch.id)
            for i in range(0, totalOpenPorts[currentSwitch.id]):
                switchList = self.switches.copy()
                randomSwitch = getRandomSwitch(
                    currentSwitch, switchList, totalOpenPorts)

                if randomSwitch == -1:
                    continue

                # Add an edge between the server and switch
                currentSwitch.add_edge(randomSwitch)
                totalOpenPorts[currentSwitch.id] -= 1
                totalOpenPorts[randomSwitch.id] -= 1

                #print("randomSwitch",currentSwitch.id, randomSwitch.id, i)

        # Print the remaining open ports
        # for op in totalOpenPorts:
            #print("Switches Open:",op, totalOpenPorts[op])

        switchList = self.switches.copy()
        CheckAllConn(totalOpenPorts, switchList, num_ports)

        start_server_id = "c0"
        visitedList = {}
        paths = {}
        for server in self.servers:
            path_id = start_server_id+"_"+server.id
            visitedList[path_id] = [start_server_id]
            multigraph = CheckforMultGraphs(
                self.servers[0], visitedList, paths, path_id, server.id)
            if not multigraph:
                print("No path for", self.servers[0].id, server.id)
                self.servers = []
                self.switches = []
                self.generate(num_servers, num_switches, num_ports)
                break

        # for currentSwitch in self.switches:
        # 	print("Switch Id:", currentSwitch.id)
        # 	#print("->", currentSwitch.edges)
        # 	if len(currentSwitch.edges) < num_ports:
        # 		for edge in currentSwitch.edges:
        # 			print("     ->",edge.lnode.id, edge.rnode.id)
        # 	else:
        # 		print("    -> All Conn Full")

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
        for core_switch_number in range(0, self.max_core_switch_count):
            core_switch = Node('CS_' + str(pod_number) +
                               '_' + str(core_switch_number), 'switch')
            # core_switch.data = self.addSwitch(core_switch.id)
            # self.core_switches.append(core_switch.data)
            self.core_switches.append(core_switch)
            self.switches.append(core_switch)

            # link core switches and aggregate switches
            link_number = int(core_switch_number // (self.num_ports / 2))
            for pod_number in range(0, self.max_pod_count):
                # self.addLink(core_switch.data, self.aggregate_switches[pod_number][link_number].data)
                core_switch.add_edge(
                    self.aggregate_switches[pod_number][link_number])

    def generate_pods(self, pod_number):
        # local variables
        pod_edge_switches = []
        pod_aggregate_switches = []

        # add edge switches
        for edge_switch_number in range(0, int(self.num_ports/2)):
            edge_switch = Node('ES_' + str(pod_number) +
                               '_' + str(edge_switch_number), 'switch')
            # edge_switch.data = self.addSwitch(edge_switch.id)
            # pod_edge_switches.append(edge_switch.data)
            pod_edge_switches.append(edge_switch)
            self.switches.append(edge_switch)
        self.edge_switches.append(pod_edge_switches)

        # add servers and link them to edge switches
        for edge_switch_index, edge_switch in enumerate(pod_edge_switches):
            for server_number in range(2, int(self.num_ports / 2) + 2):
                # add server
                server = Node('H_' + str(pod_number) + '_' +
                              str(edge_switch_index) + '_' + str(server_number), 'server')
                # server.data = self.addHost(server.id)
                self.servers.append(server)

                # add link
                # self.addLink(edge_switch.data, server.data)
                edge_switch.add_edge(server)

        # add aggregate switches
        for aggregate_switch_number in range(int(self.num_ports/2), self.num_ports):
            aggregate_switch = Node(
                'AS_' + str(pod_number) + '_' + str(aggregate_switch_number), 'switch')
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

# endregion

# region DCell


def getAvailableServer(currentDcell, serverConn, n):
	for i in range(currentDcell, currentDcell+n):
		if serverConn[i] == 1:
			serverConn[i] += 1
			return i


class DCell:

	def __init__(self, n):
		self.servers = []
		self.switches = []
		self.generate(n)

	def generate(self, n):
		serverConn = []
		# Lets add servers and switches and connect them
		for i in range(0, n+1):
			switchId = "s"+str(i)

			tempSwitchNode = Node(switchId, "switch")
			self.switches.append(tempSwitchNode)

			# Create n servers and link them to the switches

			# Get the total of servers that were already created
			CurrentServerCount = len(self.servers)

			# Loop over the next set of servers and add them to the switch
			for s in range(0, n):
				# Cretes a new server as a node
				server_id = "c."+str(i)+"."+str(s)
				tempServerNode = Node(server_id, "server")
				self.servers.append(tempServerNode)

				serverConn.append(1)
				# Add an edge between the server and switch
				tempSwitchNode.add_edge(tempServerNode)

		conn = []
		for dcell in range(0, n):
			for server_no in range(0, n):
				server_index = dcell*n + server_no

				if serverConn[server_index] != 1:
					continue

				server_node = self.servers[server_index]

				next_server_index = 0
				# if server_no+1 < n:
				next_server_index = (server_no+1)*n

				avail_index = getAvailableServer(
					next_server_index, serverConn, n)

				if avail_index and avail_index >= 0:
					next_server_node = self.servers[avail_index]
					server_node.add_edge(next_server_node)
					conn.append([server_node.id, next_server_node.id])

					serverConn[server_index] += 1
				else:
					break

# endregion

# region BCube


class BCube:

    def __init__(self, num_levels, num_ports):
        self.servers = []
        self.switches = []

        # lists
        self.servers_in_bcubes = []
        self.switches_in_levels = []

        # calculate the number of servers and switches
        self.max_servers = int(num_ports ** (num_levels + 1))
        self.max_servers_per_bcube = int(num_ports ** num_levels)
        self.max_switches_per_level = int(num_ports ** num_levels)
        self.max_bcubes_per_level = int(num_ports)
        self.max_level_of_switches = int(num_levels + 1)
        self.max_ports_in_server = int(num_levels + 1)

        self.generate(num_levels, num_ports)

    def generate(self, num_levels, num_ports):

        # generate hosts
        for bcube_num in range(self.max_bcubes_per_level):
            servers_in_bcube = []
            for server_num in range(self.max_servers_per_bcube):
                server = Node('H_' + str(bcube_num) + '_' +
                              str(server_num), 'server')
                servers_in_bcube.append(server)
                self.servers.append(server)
            self.servers_in_bcubes.append(servers_in_bcube)

        # generate switches for each level
        for switch_level_number in range(self.max_level_of_switches):
            switches_in_level = []
            for switch_number in range(self.max_switches_per_level):
                switch = Node('S_' + str(switch_level_number) +
                              '_' + str(switch_number), 'switch')
                switches_in_level.append(switch)
                self.switches.append(switch)
            self.switches_in_levels.append(switches_in_level)

        for level in range(self.max_switches_per_level):
            hop = num_ports ** level
            max_server_count = num_ports ** (level + 1)
            current_server_count = 0
            count = 0

            for switch in range(row_switches):
                if (current_server_count == max_server_count):
                    count = count + 1
                    current_server_count = 0

                for port in range(num_ports):
                    connected_server = int(switch % (
                        max_server_count / num_ports)) + (port * hop) + (count * max_server_count)

                    self.switches_in_levels[level][switch].add_edge(
                        self.servers[connected_server])
                    # print(
                    #     self.switches_in_levels[level][switch].id, '->', self.servers[connected_server].id)

                    current_server_count += 1

# endregion
