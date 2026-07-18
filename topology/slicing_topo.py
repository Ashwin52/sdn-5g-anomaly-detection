#!/usr/bin/env python3
"""
slicing_topo.py
Custom Mininet topology simulating 5G-style network slices using
differentiated link bandwidth/delay (TCLink) as a proxy for slice QoS.

Slices simulated:
  - eMBB  (h1, h2): high bandwidth, higher delay tolerance (video/data)
  - URLLC (h3, h4): low bandwidth, ultra-low delay (critical control)
  - mMTC  (h5, h6): low bandwidth, high delay tolerance (IoT sensors)

Run with:
  sudo python3 slicing_topo.py
"""

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel


def build_network():
    net = Mininet(controller=RemoteController, link=TCLink)

    print("*** Adding controller")
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    print("*** Adding switch")
    s1 = net.addSwitch('s1')

    print("*** Adding hosts for each slice")
    # eMBB - high bandwidth, standard delay
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')

    # URLLC - lower bandwidth, but near-zero delay (priority traffic)
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')

    # mMTC - low bandwidth, higher delay tolerance (IoT-style)
    h5 = net.addHost('h5', ip='10.0.0.5')
    h6 = net.addHost('h6', ip='10.0.0.6')

    print("*** Creating links with slice-specific QoS parameters")
    # eMBB: high bandwidth (100 Mbps), moderate delay
    net.addLink(h1, s1, cls=TCLink, bw=100, delay='5ms')
    net.addLink(h2, s1, cls=TCLink, bw=100, delay='5ms')

    # URLLC: lower bandwidth (10 Mbps) but ultra-low delay - priority slice
    net.addLink(h3, s1, cls=TCLink, bw=10, delay='1ms')
    net.addLink(h4, s1, cls=TCLink, bw=10, delay='1ms')

    # mMTC: very low bandwidth (2 Mbps), higher delay tolerance
    net.addLink(h5, s1, cls=TCLink, bw=2, delay='20ms')
    net.addLink(h6, s1, cls=TCLink, bw=2, delay='20ms')

    print("*** Starting network")
    net.start()

    print("\n*** Slice Summary ***")
    print("eMBB  (h1-h2):  100 Mbps, 5ms delay   -> high-bandwidth data/video")
    print("URLLC (h3-h4):  10 Mbps,  1ms delay   -> low-latency critical control")
    print("mMTC  (h5-h6):  2 Mbps,   20ms delay  -> IoT sensor traffic")

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    build_network()
