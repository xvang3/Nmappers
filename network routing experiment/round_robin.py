# Template/strucure idea taken from: https://github.com/PM-Abhishek/LoadBalancing-in-SDN 
# Adapted to use iPerf clients/servers and to be configured for Mininet

#!/usr/bin/python3
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types

class RoundRobinSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    # Virtual MAC address for the load balancer
    VIRTUAL_MAC = '00:00:00:00:00:01'

    def __init__(self, *args, **kwargs):
        super(RoundRobinSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.server_ips = ['10.0.0.6', '10.0.0.7', '10.0.0.8', '10.0.0.9', '10.0.0.10']
        self.current_server = 0
        self.ip_to_mac = {}  # This will be a dictionary mapping IP to MAC for servers

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        dst = eth.dst
        src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        self.mac_to_port[dpid][src] = in_port

        # Check for the virtual MAC address as the destination
        if dst == self.VIRTUAL_MAC:
            # Implement round-robin selection
            chosen_server_ip = self.server_ips[self.current_server]
            self.current_server = (self.current_server + 1) % len(self.server_ips)
            chosen_server_mac = self.ip_to_mac.get(chosen_server_ip)

            # If the server's MAC address is known, send the packet directly there
            if chosen_server_mac:
                actions = [parser.OFPActionSetField(eth_dst=chosen_server_mac),
                           parser.OFPActionOutput(self.mac_to_port[dpid][chosen_server_mac])]
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                out_port = ofproto.OFPP_FLOOD
                actions = [parser.OFPActionOutput(out_port)]
        else:
            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
                actions = [parser.OFPActionOutput(out_port)]
            else:
                out_port = ofproto.OFPP_FLOOD
                actions = [parser.OFPActionOutput(out_port)]

            # Install a flow to avoid packet_in next time
            if out_port != ofproto.OFPP_FLOOD:
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                self.add_flow(datapath, 1, match, actions)

        # Send packet out to either the selected server or flood it
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)



