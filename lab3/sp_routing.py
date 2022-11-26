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
from djikstra import Graph


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
        self.switch_to_ip = {}
        self.server_to_server_sp = {}

        g1 = Graph(self.topo_net.servers, self.topo_net.switches)
        all_distance = g1.find_min_distance()
        for src_host in self.topo_net.servers:
            if(src_host.type == 'H'):
                for dst_host in self.topo_net.servers:
                    if(dst_host.type == 'H' and src_host.id != dst_host.id):
                        path = all_distance[src_host.id][dst_host.id][:-1]
                        self.server_to_server_sp[(src_host.ip, dst_host.ip)] = path

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
            self.port_to_switch[(dst_dpid, src_dpid)] = (dst_port, src_port)

            if src_dpid in self.switches:
                self.switch_to_switch_ports[src_dpid].add(src_port)
            if dst_dpid in self.switches:
                self.switch_to_switch_ports[dst_dpid].add(dst_port)

        for switch in self.switch_ports:
            self.switch_to_host_ports[switch] = self.switch_ports[switch] - \
                self.switch_to_switch_ports[switch]

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
        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]
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

        eth = pkt.get_protocols(ethernet.ethernet)[0]
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        
        if ip_pkt:
            src_ipv4 = ip_pkt.src
            src_mac = eth_pkt.src
            dst_ipv4 = ip_pkt.dst

            self.ip_sp_forwarding(dpid, in_port, msg,
                                  eth.ethertype, src_ipv4, dst_ipv4)

        if arp_pkt:
            arp_src_ip = arp_pkt.src_ip
            arp_dst_ip = arp_pkt.dst_ip
            mac = arp_pkt.src_mac

            if in_port in self.switch_to_host_ports[dpid]:
                if (dpid, in_port) not in self.switch_to_ip:
                    self.switch_to_ip.setdefault((dpid, in_port), None)
                    self.switch_to_ip[(dpid, in_port)] = (arp_src_ip, mac)

            # check if we have the destination ip mapped to a switch and port
            server_details = self.get_server_details(arp_dst_ip)
            if server_details:
                # if we have it mapped then forward the packet to the known port
                datapath_dst, out_port = server_details[0], server_details[1]
                datapath = self.datapaths[datapath_dst]
                actions = [(datapath.ofproto_parser.OFPActionOutput(out_port))]
                out = datapath.ofproto_parser.OFPPacketOut(
                    datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                    data=msg.data, in_port=ofproto.OFPP_CONTROLLER, actions=actions)
                datapath.send_msg(out)
            else:
                # if we do not know it then we will start sending packets explicitly to each switch that we have calculated from the links
                for dpid in self.switch_to_host_ports:
                    for port in self.switch_to_host_ports[dpid]:
                        if (dpid, port) not in self.switch_to_ip.keys():
                            datapath = self.datapaths[dpid]
                            actions = [
                                (datapath.ofproto_parser.OFPActionOutput(port))]
                            out = datapath.ofproto_parser.OFPPacketOut(
                                datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                data=msg.data, in_port=ofproto.OFPP_CONTROLLER, actions=actions)
                            datapath.send_msg(out)

    def get_server_details(self, server_ip):
        for key in self.switch_to_ip.keys():
            if self.switch_to_ip[key][0] == server_ip:
                return key
        return None

    def ip_sp_forwarding(self, dpid, in_port, msg, eth_type, ip_src, ip_dst):
        datapath = msg.datapath
        parser = datapath.ofproto_parser

        result = self.get_switches_details(dpid, in_port, ip_src, ip_dst)
        if result:
            src_sw, dst_sw, to_dst_port = result[0], result[1], result[2]
            if dst_sw:
                # Path has already calculated, just get it.
                to_dst_match = parser.OFPMatch(eth_type=eth_type, ipv4_dst=ip_dst)
                port_no = self.set_sp_forwarding(ip_src, ip_dst, src_sw, dst_sw, to_dst_port, to_dst_match)
                # send packet forward
                actions = [(datapath.ofproto_parser.OFPActionOutput(port_no))]
                out = datapath.ofproto_parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,data=msg.data, in_port=in_port, actions=actions)
                if out:
                    datapath.send_msg(out)
        return
    
    def set_sp_forwarding(self,
                          ip_src,
                          ip_dst,
                          src_dpid, 
                          dst_dpid, 
                          to_port_no,
                          to_dst_match):
        path = self.server_to_server_sp[(ip_src, ip_dst)]
        if len(path) == 1:
            dp = self.datapaths[src_dpid]
            actions = [dp.ofproto_parser.OFPActionOutput(to_port_no)]
            self.add_flow(dp, 10, to_dst_match, actions)
            port_no = to_port_no
        else:
            for index, dpid in enumerate(path[:-1]):
                port_no = self.port_to_switch[(int(path[index][1:]), int(path[index + 1][1:]))][0]
                dp = self.datapaths[int(dpid[1:])]
                actions = [dp.ofproto_parser.OFPActionOutput(port_no)]
                self.add_flow(dp, 10, to_dst_match, actions)
            dst_dp = self.datapaths[dst_dpid]
            actions = [dst_dp.ofproto_parser.OFPActionOutput(to_port_no)]
            self.add_flow(dst_dp, 10, to_dst_match, actions)
            port_no = self.port_to_switch[(int(path[0][1:]), int(path[1][1:]))][0]
        
        return port_no

    def get_switches_details(self, dpid, in_port, src_ip, dst_ip):
        src_sw = dpid
        dst_sw = None
        dst_port = None

        src_location = self.get_server_details(src_ip)
        if in_port in self.switch_to_host_ports[dpid]:
            if (dpid,  in_port) == src_location:
                src_sw = src_location[0]
            else:
                return None

        dst_location = self.get_server_details(dst_ip)
        if dst_location:
            dst_sw = dst_location[0]
            dst_port = dst_location[1]
        return src_sw, dst_sw, dst_port
