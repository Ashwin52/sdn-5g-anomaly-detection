#!/usr/bin/env python3
"""
normal_traffic.py
Generates normal, low-rate traffic between two hosts.
Run this INSIDE a Mininet host (e.g., via 'mininet> h1 python3 normal_traffic.py <dst_ip>')
"""

import sys
import time
import random
from scapy.all import IP, TCP, ICMP, send

def generate_normal_traffic(dst_ip, duration=30):
    print(f"[normal] Sending normal traffic to {dst_ip} for {duration} seconds...")
    start = time.time()

    while time.time() - start < duration:
        choice = random.choice(["icmp", "tcp"])

        if choice == "icmp":
            pkt = IP(dst=dst_ip) / ICMP()
        else:
            pkt = IP(dst=dst_ip) / TCP(dport=random.choice([80, 443, 22]), flags="S")

        send(pkt, verbose=0)

        # Normal traffic: random gap between 0.5 - 2 seconds (low rate)
        time.sleep(random.uniform(0.5, 2.0))

    print("[normal] Done.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 normal_traffic.py <destination_ip> [duration_seconds]")
        sys.exit(1)

    dst_ip = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    generate_normal_traffic(dst_ip, duration)
