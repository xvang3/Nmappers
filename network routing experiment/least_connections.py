# Template/structure idea taken from: https://github.com/Deepak281295/LoadBalancing-in-SDN
# Adapted with Mininet Simple Switch 13 for Mininet configuration

#!/usr/bin/python3
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types

class LeastConnectionsSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    # Virtual MAC address for the load balancer
    VIRTUAL_MAC = '00:00:00:00:00:01'

    def __init__(self, *args, **kwargs):
        super(LeastConnectionsSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.server_ips = ['10.0.0.6', '10.0.0.7', '10.0.0.8', '10.0.0.9', '10.0.0.10']
        self.server_load = {ip: 0 for ip in self.server_ips}  # Initialize server load
        self.ip_to_mac = {}  # Mapping IP to MAC for servers

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
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    def get_least_connections_server(self):
        # Select the server with the minimum number of connections
        chosen_server_ip = min(self.server_load, key=self.server_load.get)
        self.server_load[chosen_server_ip] += 1  # Increment the connection count
        return chosen_server_ip

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
            # Ignore LLDP packets
            return
        dst = eth.dst
        src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        self.mac_to_port[dpid][src] = in_port

        if dst == self.VIRTUAL_MAC:
            # Implement least connections selection
            chosen_server_ip = self.get_least_connections_server()
            chosen_server_mac = self.ip_to_mac.get(chosen_server_ip)

            if chosen_server_mac:
                actions = [parser.OFPActionSetField(eth_dst=chosen_server_mac),
                           parser.OFPActionOutput(self.mac_to_port[dpid][chosen_server_mac])]
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                    return
                else:
                    self.add_flow(datapath, 1, match, actions)
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
                # Since this is a simple example without tracking actual connections
                # We do not check for buffer_id and always install the flow
                self.add_flow(datapath, 1, match, actions)

        # Send packet out to either the selected server or flood it
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)


