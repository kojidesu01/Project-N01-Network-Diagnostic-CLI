#!/bin/bash
set -e

# 1. Create namespaces
ip netns add n01-client
ip netns add n01-server

# 2. Create virtual ethernet
ip link add veth-c type veth peer name veth-s

# 3. Move interfaces
ip link set veth-c netns n01-client
ip link set veth-s netns n01-server

# 4. Assign IP addresses
ip -n n01-client addr add 10.10.1.1/24 dev veth-c
ip -n n01-server addr add 10.10.1.2/24 dev veth-s

# 5. Enable interfaces
ip -n n01-client link set veth-c up
ip -n n01-server link set veth-s up

# 6. Enable loopback
ip -n n01-client link set lo up
ip -n n01-server link set lo up

echo "[PASS] Network Lab setup complete"