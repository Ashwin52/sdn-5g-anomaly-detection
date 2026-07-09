from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
import time
import csv
import os

log = core.getLogger()

CSV_PATH = os.path.expanduser("~/pox/flow_stats.csv")

if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "src_mac", "dst_mac", "in_port", "out_port", "packet_count", "byte_count"])


class CustomSwitch (object):
    def __init__ (self, connection):
        self.connection = connection
        self.mac_to_port = {}
        self.flow_table = {}
        connection.addListeners(self)

    def resend_packet (self, packet_in, out_port):
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        self.connection.send(msg)

    def log_flow_stat (self, src, dst, in_port, out_port, packet_len):
        flow_key = (src, dst)

        if flow_key not in self.flow_table:
            self.flow_table[flow_key] = {
                "packet_count": 0,
                "byte_count": 0,
                "first_seen": time.time()
            }

        stat = self.flow_table[flow_key]
        stat["packet_count"] += 1
        stat["byte_count"] += packet_len

        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                time.time(), src, dst, in_port, out_port,
                stat["packet_count"], stat["byte_count"]
            ])

    def act_like_switch (self, packet, packet_in):
        self.mac_to_port[packet.src] = packet_in.in_port

        if packet.dst in self.mac_to_port:
            out_port = self.mac_to_port[packet.dst]

            packet_len = len(packet_in.data) if packet_in.data else 0
            self.log_flow_stat(str(packet.src), str(packet.dst),
                                packet_in.in_port, out_port, packet_len)

            log.info("Flow: %s -> %s | port %s | len %sB",
                      packet.src, packet.dst, out_port, packet_len)

            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet)
            msg.idle_timeout = 10
            msg.hard_timeout = 30
            msg.actions.append(of.ofp_action_output(port=out_port))
            msg.data = packet_in
            self.connection.send(msg)
        else:
            self.resend_packet(packet_in, of.OFPP_ALL)

    def _handle_PacketIn (self, event):
        packet = event.parsed
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp
        self.act_like_switch(packet, packet_in)


def launch ():
    def start_switch (event):
        log.info("Controlling switch %s", dpid_to_str(event.dpid))
        CustomSwitch(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
    log.info("Flow stats will be logged to: %s", CSV_PATH)
