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
from ryu.lib.packet import ether_types
from ryu.lib.packet import ethernet

from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase

import copy
import topo

class FTRouter(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(FTRouter, self).__init__(*args, **kwargs)
        self.topo_net = topo.Fattree(4)        
        # Holds the topology data and structure
        self.topo_raw_switches = []
        self.topo_raw_links = []
        
        self.switches = []
        self.datapaths = {}
        
        self.mac_to_port = mac_to_port.MacToPortTable()
        self.switch_ip_to_dpid = {}
        self.switch_dpid_to_node = {}
        self.switch_port_to_ip = {}


    # Topology discovery
    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        self.topo_raw_switches = copy.copy(get_switch(self, None))
        
        # map switches to ips and node objects
        for switch in self.topo_raw_switches:
            dpid = switch.dp.id
            self.datapaths[dpid] = switch.dp
            
            for topo_switch in self.topo_net.switches:
                if(int(topo_switch.id[1:]) == dpid):
                    self.switch_ip_to_dpid[topo_switch.ip] = dpid
                    self.switch_dpid_to_node[dpid] = topo_switch
        
        # map all the ports in a switch to the ips that it is connected to
        for switch in self.topo_raw_switches:
            dpid = switch.dp.id
            self.datapaths[dpid] = switch.dp
            
            self.switch_port_to_ip.setdefault(dpid, {})
            links = get_link(self, dpid)
            for link in links:
                switch = self.switch_dpid_to_node.get(link.dst.dpid)
                if(not switch):
                    continue
                self.switch_port_to_ip[dpid][link.src.port_no] = switch.ip
                
        self.set_ft_forwarding()


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
    
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Construct flow_mod message and send it
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)       
        
    def set_ft_forwarding(self):
        print('setting up', len(self.topo_raw_switches))
        # flatten the topo switch list
        edge_switches = [item for sublist in self.topo_net.edge_switches for item in sublist]
        aggregate_switches = [item for sublist in self.topo_net.aggregate_switches for item in sublist]
        
        # set the rules for all edge switchs
        for switch in edge_switches:
            # many switches are missing from get_switch inititally :'(
            dpid = self.switch_ip_to_dpid.get(switch.ip)
            if(not dpid):
                continue
            datapath = get_switch(self, dpid)[0].dp
            parser = datapath.ofproto_parser
            for index, outport in enumerate(self.get_ports_to_upper_level(dpid)):
                host_id = 2 + index
                match = parser.OFPMatch(
                    eth_type=ether_types.ETH_TYPE_IP,
                    ipv4_dst=('0.0.0.{}'.format(host_id), '0.0.0.255'),
                )
                actions = [parser.OFPActionOutput(outport)]
                self.add_flow(datapath, 1, match, actions)
                
        # set the rules for all aggregate switchs
        for switch in aggregate_switches:
            # need to get lower node port and IP
            # many switches are missing from get_switch inititally :'(
            dpid = self.switch_ip_to_dpid.get(switch.ip)
            if(not dpid):
                continue
            datapath = get_switch(self, dpid)[0].dp
            parser = datapath.ofproto_parser
            for outport in self.get_ports_to_lower_level(dpid):
                next_hop_ip_list = self.switch_port_to_ip.get(dpid)
                if(next_hop_ip_list):
                    next_hop_ip = next_hop_ip_list.get(outport)
                    if(not next_hop_ip):
                        continue
                else:
                    continue
                match = parser.OFPMatch(
                    eth_type=ether_types.ETH_TYPE_IP,
                    ipv4_dst=(next_hop_ip, '255.255.255.0'),
                )
                actions = [parser.OFPActionOutput(outport)]
                self.add_flow(datapath, 1, match, actions)
            for index, outport in enumerate(self.get_ports_to_upper_level(dpid)):
                host_id = 2 + index
                match = parser.OFPMatch(
                    eth_type=ether_types.ETH_TYPE_IP,
                    ipv4_dst=('0.0.0.{}'.format(host_id), '0.0.0.255'),
                )
                actions = [parser.OFPActionOutput(outport)]
                self.add_flow(datapath, 2, match, actions)
                
        # set the rules for all core switches
        for switch in self.topo_net.core_switches:
            # many switches are missing from get_switch inititally :'(
            dpid = self.switch_ip_to_dpid.get(switch.ip)
            if(not dpid):
                continue
            datapath = get_switch(self, dpid)[0].dp
            parser = datapath.ofproto_parser
            for outport in self.get_ports_to_lower_level(dpid):
                next_hop_ip_list = self.switch_port_to_ip.get(dpid)
                if(next_hop_ip_list):
                    next_hop_ip = next_hop_ip_list.get(outport)
                    if(not next_hop_ip):
                        continue
                else:
                    continue
                match = parser.OFPMatch(
                    eth_type=ether_types.ETH_TYPE_IP,
                    ipv4_dst=(next_hop_ip, '255.255.0.0'),
                )
                actions = [parser.OFPActionOutput(outport)]
                self.add_flow(datapath, 1, match, actions)

    def get_ports_to_upper_level(self, dpid):
        ports = []
        links = get_link(self, dpid)
        src_switch_type = self.switch_dpid_to_node[dpid].type
        for link in links:
            dst_switch_type = self.switch_dpid_to_node[link.dst.dpid].type
            if src_switch_type == 'ES' and (dst_switch_type == 'AS' or dst_switch_type == 'CS'):
                ports.append(link.src.port_no)
            elif src_switch_type == 'AS' and dst_switch_type == 'CS':
                ports.append(link.src.port_no)
        return ports

    def get_ports_to_lower_level(self, dpid):
        ports = []
        switch = get_switch(self, dpid)
        upper_port = self.get_ports_to_upper_level(dpid)
        
        for port in switch[0].ports:
            if port.port_no not in upper_port:
                ports.append(port.port_no)

        return ports

    def get_ports_to_flood(self, dpid, in_port):
        switch_type = self.switch_dpid_to_node[dpid].type
        ports = []
        if switch_type == 'CS':
            ports.extend(self.get_ports_to_lower_level(dpid))
            ports.remove(in_port)
        else:
            if in_port in self.get_ports_to_upper_level(dpid):
                ports = self.get_ports_to_lower_level(dpid)
            else:
                ports.extend(self.get_ports_to_lower_level(dpid))
                ports.remove(in_port)
                ports.append(self.get_ports_to_upper_level(dpid)[0])

        return ports

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        
        # print(self.switch_ip_to_dpid)
        if ip_pkt:
            print('Reached ip')
        
        if arp_pkt:
            # add rule when packet is coming to the edge switch from the host
            if self.switch_dpid_to_node[dpid].type == 'ES' and in_port not in self.get_ports_to_upper_level(dpid):
                match = parser.OFPMatch(
                    eth_type=ether_types.ETH_TYPE_IP, ipv4_dst=arp_pkt.src_ip
                )
                actions = [parser.OFPActionOutput(in_port)]
                self.add_flow(datapath, 2, match, actions)

            # add mac address to port to table
            actions = []
            eth = pkt.get_protocol(ethernet.ethernet)
            mac_src = eth.src
            mac_dst = eth.dst
            self.mac_to_port.dpid_add(dpid)
            self.mac_to_port.port_add(dpid, in_port, haddr_to_bin(mac_src))

            # if we find the destination port in the mac table add that as the action
            dst_port = self.mac_to_port.port_get(dpid, haddr_to_bin(mac_dst))
            if dst_port:
                actions.append(parser.OFPActionOutput(dst_port))
            else:
                # else we flood to other ports
                flood_ports = self.get_ports_to_flood(dpid, in_port)
                for dst_port in flood_ports:
                    actions.append(parser.OFPActionOutput(dst_port))

            out = parser.OFPPacketOut(
                datapath=datapath,
                in_port=in_port,
                actions=actions,
                buffer_id=datapath.ofproto.OFP_NO_BUFFER,
                data=msg.data,
            )
            datapath.send_msg(out)
