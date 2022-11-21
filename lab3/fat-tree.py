# This code is part of the Advanced Computer Networks (ACN) course at VU
# Amsterdam.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

#!/usr/bin/env python3

# A dirty workaround to import topo.py from lab2

import os
import subprocess
import time

import mininet
import mininet.clean
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import lg, info
from mininet.link import TCLink
from mininet.node import Node, OVSKernelSwitch, RemoteController
from mininet.topo import Topo
from mininet.util import waitListening, custom

import topo


class FattreeNet(Topo):
    """
    Create a fat-tree network in Mininet
    """

    def __init__(self, ft_topo):

        Topo.__init__(self)

        # TODO: please complete the network generation logic here
        self.servers_dict = {}
        self.switches_dict = {}
        self.nodes_dict = {}
        
        for switch in ft_topo.switches:
            self.switches_dict[switch.id] = self.addSwitch(switch.id, ip=switch.ip, dpid=switch.dpid)
            
        for server in ft_topo.servers:
            self.servers_dict[server.id] = self.addHost(server.id, ip=server.ip, dpid=switch.dpid)
            
        self.nodes_dict = {**self.servers_dict, **self.switches_dict}
        
        self.edges_list = list(set([(edge.lnode.id, edge.rnode.id) for switch in ft_topo.switches for edge in switch.edges]))
        for edge in self.edges_list:
            self.addLink(self.nodes_dict[edge[0]], self.nodes_dict[edge[1]])

def make_mininet_instance(graph_topo):

    net_topo = FattreeNet(graph_topo)
    net = Mininet(topo=net_topo, controller=None, autoSetMacs=True)
    net.addController('c0', controller=RemoteController,
                      ip="127.0.0.1", port=6653)
    return net


def run(graph_topo):

    # Run the Mininet CLI with a given topology
    lg.setLogLevel('info')
    mininet.clean.cleanup()
    net = make_mininet_instance(graph_topo)

    info('*** Starting network ***\n')
    net.start()
    info('*** Running CLI ***\n')
    CLI(net)
    info('*** Stopping network ***\n')
    net.stop()


ft_topo = topo.Fattree(4)
run(ft_topo)
