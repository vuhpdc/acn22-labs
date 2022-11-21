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

#!/usr/bin/env python3

from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ipv4
from ryu.lib.packet import arp
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types

from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase

import copy
import topo

class SPRouter(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SPRouter, self).__init__(*args, **kwargs)
        self.topo_net = topo.Fattree(4)
        # Holds the topology data and structure
        self.topo_raw_switches = []
        self.topo_raw_links = []
        
        self.switches = []
        self.datapaths = {}
        # switch to port mapping
        self.port_to_switch = {}
        
        # port mappings
        self.switch_ports = {}
        self.switch_to_switch_ports = {}
        self.switch_to_host_ports = {}
        
        # switch and port to ip mapping
        self.switch_to_ip= {}
        
        self.mac_to_port = {}


    # Topology discovery
    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):

        # # Switches and links in the network
        # switches = get_switch(self, None)
        # links = get_link(self, None)
        
        # The Function get_switch(self, None) outputs the list of switches.
        self.topo_raw_switches = copy.copy(get_switch(self, None))
        # The Function get_link(self, None) outputs the list of links.
        self.topo_raw_links = copy.copy(get_link(self, None))
        # get all the ports from switches
        for switch in self.topo_raw_switches:
            dpid = switch.dp.id
            self.datapaths[dpid] = switch.dp
            self.switch_ports.setdefault(dpid, set())
            self.switch_to_switch_ports.setdefault(dpid, set())
            self.switch_to_host_ports.setdefault(dpid, set())
            
            for port in switch.ports:
                self.switch_ports[dpid].add(port.port_no)
                
        self.switches = self.switch_ports.keys()
                
        for link in self.topo_raw_links:
            src_dpid = link.src.dpid
            dst_dpid = link.dst.dpid
            src_port = link.src.port_no
            dst_port = link.dst.port_no
            
            self.port_to_switch[(src_dpid, dst_dpid)] = (src_port, dst_port)
            
            if src_dpid in self.switches:
                self.switch_to_switch_ports[src_dpid].add(src_port)
            if dst_dpid in self.switches:
                self.switch_to_switch_ports[dst_dpid].add(dst_port)
        
        for switch in self.switch_ports:
            self.switch_to_host_ports[switch] = self.switch_ports[switch] - self.switch_to_switch_ports[switch]
            

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install entry-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)


    # Add a flow entry to the flow-table
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Construct flow_mod message and send it
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # TODO: handle new packets at the controller
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        self.mac_to_port.setdefault(dpid, {})
        
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        
        print('Switches: ', self.switches)
        print('Switch Ports: ', self.switch_ports)
        print('Host Ports: ', self.switch_to_host_ports)
        print('Switch to Switch Ports: ', self.switch_to_switch_ports)
        
        
        if ip_pkt:
            src_ipv4 = ip_pkt.src
            src_mac = eth_pkt.src
            dst_ipv4 = ip_pkt.dst
            
            print('switch: {}, in_port: {}, src_ip: {}, dst_ip: {}, src_mac: {}'.format(dpid, in_port, src_ipv4, dst_ipv4, src_mac))
            # if src_ipv4 != '0.0.0.0' and src_ipv4 != '255.255.255.255':
            #     self.register_access_info(datapath.id, in_port, src_ipv4, src_mac)

        if arp_pkt:
            arp_src_ip = arp_pkt.src_ip
            arp_dst_ip = arp_pkt.dst_ip
            mac = arp_pkt.src_mac
            
            print('switch: {}, in_port: {}, arp_src_ip: {}, arp_dst_ip: {}, src_mac: {}'.format(dpid, in_port, arp_src_ip, arp_dst_ip, mac))
            # Record the access info
            # self.register_access_info(datapath.id, in_port, arp_src_ip, mac)

        
        # print(switches)
        # print(links)
        
