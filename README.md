# N01 — Network Diagnostic CLI

A Python-based network diagnostics learning project focused on **DNS resolution, TCP connectivity testing, and packet-level troubleshooting**.

This project is part of my hands-on learning journey in Network Engineering and Cybersecurity. The goal is to develop practical networking skills by combining Python programming with Linux networking tools and controlled lab environments.

**Project Status:** In Development — DNS and TCP fundamentals completed.

## 1. Project Objectives

- Understand how DNS resolution works.
- Develop a Python-based DNS checker.
- Test TCP connectivity using Python sockets.
- Distinguish between successful connections, connection refusals, and timeouts.
- Understand the TCP three-way handshake.
- Build an isolated networking lab using Linux Network Namespaces.
- Analyze network packets using `tcpdump`.
- Simulate network failures using Linux firewall rules.
- Practice evidence-based network troubleshooting.

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | DNS resolution and TCP connectivity checks |
| Python `socket` | Low-level networking operations |
| Linux | Lab environment |
| Network Namespaces | Isolated client and server environments |
| Virtual Ethernet (veth) | Connecting network namespaces |
| `iproute2` | Configuring interfaces and routing |
| `tcpdump` | Packet capture and analysis |
| `iptables` | Simulating firewall DROP and REJECT |
| Git / GitHub | Version control and documentation |

No external Python packages are required for the current diagnostic functions.

## 3. Repository Structure

```text
Project-N01-Network-Diagnostic-CLI/
├── .gitignore
├── dns_checker.py
├── network_diag.py
├── tcp_checker.py
├── setup_lab.sh
└── README.md
```

### File Descriptions

| File | Description |
|---|---|
| `dns_checker.py` | DNS resolution function |
| `network_diag.py` | Current interactive entry point for DNS checking |
| `tcp_checker.py` | TCP connectivity checking function |
| `setup_lab.sh` | Creates an isolated client/server networking lab |
| `.gitignore` | Excludes Python cache, virtual environments, and local configuration files |

**Note:** The DNS and TCP checking functions have been implemented, but TCP checking is not yet integrated into the main interactive CLI.

## 4. Lab 01 — DNS Resolution

### Objective

Resolve a domain name to an IPv4 address using Python.

The DNS checker uses:

```python
socket.gethostbyname(domain)
```

It handles DNS resolution failures using `socket.gaierror`.

### Run the DNS Checker

```bash
python3 network_diag.py
```

### Example: Successful Resolution

```text
Enter domain: google.com
[PASS] IP: <resolved IPv4 address>
```

### Example: DNS Resolution Failure

```text
Enter domain: test.invalid
[FAIL] DNS Resolution Failed
```

### Example: Empty Input

```text
Enter domain:
[ERROR] Domain cannot be empty
```

### Key Learning

Successful DNS resolution only confirms that a hostname can be resolved to an IP address. It does not guarantee that a server is reachable or that a TCP service is available.

## 5. Lab 02 — TCP Connectivity Testing

### Objective

Determine whether a TCP connection can be established to a specified IP address and port.

The TCP checker uses:

```python
socket.create_connection((ip, port), timeout=5)
```

The current implementation handles:

- Successful TCP connection
- `ConnectionRefusedError`
- `socket.timeout`

A five-second connection timeout is configured.

### Run the TCP Checker

Start a local test server in one terminal:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

In another terminal, run:

```bash
python3 -c 'from tcp_checker import check_tcp; print(check_tcp("127.0.0.1", 8000))'
```

Expected result when the server is listening:

```text
True
```

If the server is not listening, a typical result is:

```text
[REFUSED] Connection refused
False
```

A TCP timeout can be produced by a network condition where connection attempts receive no response within the configured timeout.

### Key Learning

A TCP connection check tests whether the connection can be established. It does not verify the correctness of the application protocol or its response.

## 6. Lab 02.2 — TCP Troubleshooting with Network Namespaces

### Objective

Create a controlled client/server environment to observe TCP connections and simulate network failures.

The experiments cover three scenarios:

1. Normal TCP connection
2. Firewall DROP causing TCP timeout
3. Firewall REJECT causing connection refusal

### Network Topology

```text
          Linux Host
  +----------------------------------+
  |                                  |
  |  n01-client         n01-server    |
  |                                  |
  |  10.10.1.1/24       10.10.1.2/24 |
  |                                  |
  |    veth-c <-------> veth-s        |
  |                                  |
  |  TCP Checker        HTTP Server   |
  |                     Port 8000    |
  |                                  |
  +----------------------------------+
```

Both namespaces exist on the same Linux host and communicate through a virtual Ethernet pair.

### 6.1 Create the Lab Environment

Run the included setup script:

```bash
sudo bash setup_lab.sh
```

The script:

- Creates `n01-client` and `n01-server`.
- Creates a virtual Ethernet pair.
- Assigns IP addresses to both interfaces.
- Enables the virtual Ethernet interfaces.
- Enables loopback interfaces.

**Important:** The current setup script creates the environment from scratch and does not automatically reset existing namespaces. If the namespaces already exist, remove the previous lab environment before running the script again.

### 6.2 Verify Network Connectivity

Run:

```bash
sudo ip netns exec n01-client ping -c 2 10.10.1.2
```

Observed result:

```text
2 packets transmitted, 2 received, 0% packet loss
```

This confirms successful ICMP communication between the namespaces.

### 6.3 Start the TCP Server

Inside the server namespace:

```bash
sudo ip netns exec n01-server \
  python3 -m http.server 8000 --bind 10.10.1.2
```

Keep this process running in a separate terminal.

Test TCP connectivity from the client namespace:

```bash
sudo ip netns exec n01-client \
  python3 -c 'from tcp_checker import check_tcp; print(check_tcp("10.10.1.2", 8000))'
```

Observed result:

```text
True
```

## 7. Packet Analysis — TCP Three-Way Handshake

Use `tcpdump` inside the server namespace:

```bash
sudo ip netns exec n01-server \
  tcpdump -ni veth-s -l -c 3 'tcp port 8000' 2>&1 | cat
```

Run the TCP checker again from another terminal.

### Observed Packet Sequence

```text
Client -> Server: Flags [S]
Server -> Client: Flags [S.]
Client -> Server: Flags [.]
```

### Analysis

| Packet | TCP Flag | Meaning |
|---|---|---|
| 1 | SYN | Client requests a connection |
| 2 | SYN-ACK | Server acknowledges and accepts the request |
| 3 | ACK | Client confirms the connection |

The observed handshake confirms successful TCP connection establishment.

The client uses a temporary source port, while the server listens on TCP port 8000.

## 8. Firewall Experiment — DROP

### Objective

Simulate a TCP connection timeout by silently dropping incoming TCP packets.

### Apply the Firewall Rule

```bash
sudo ip netns exec n01-server \
  iptables -I INPUT 1 -p tcp --dport 8000 -j DROP
```

This rule affects TCP packets destined for port 8000 inside `n01-server`.

### Capture TCP Packets

```bash
sudo ip netns exec n01-server \
  tcpdump -ni veth-s -l -c 3 'tcp port 8000' 2>&1 | cat
```

Run the TCP checker while the capture is active.

### Observed Packet Sequence

```text
Client -> Server: SYN
Client -> Server: SYN (retransmission)
Client -> Server: SYN (retransmission)
```

No SYN-ACK response was observed.

### Python Result

```text
[TIMEOUT] Connection timed out
False
```

### Analysis

The client sends SYN packets but receives no response because the firewall silently drops the incoming packets.

The TCP stack retransmits SYN packets while attempting to establish the connection.

Once the configured timeout is reached, Python reports a connection timeout.

**Important observation:** `tcpdump` can capture packets arriving at the server interface even when they are later dropped by the firewall INPUT chain.

### Remove the DROP Rule

```bash
sudo ip netns exec n01-server \
  iptables -D INPUT -p tcp --dport 8000 -j DROP
```

## 9. Firewall Experiment — REJECT

### Objective

Understand how explicitly rejecting a TCP connection differs from silently dropping packets.

### Apply the Firewall Rule

```bash
sudo ip netns exec n01-server \
  iptables -I INPUT 1 -p tcp --dport 8000 -j REJECT
```

In this experiment, the default IPv4 iptables rejection behavior generated an ICMP Port Unreachable response.

### Capture TCP and ICMP

```bash
sudo ip netns exec n01-server \
  tcpdump -ni veth-s -l -c 2 '(tcp port 8000) or icmp' 2>&1 | cat
```

### Observed Packet Sequence

```text
10.10.1.1 -> 10.10.1.2:8000: TCP SYN
10.10.1.2 -> 10.10.1.1: ICMP tcp port 8000 unreachable
```

### Python Result

```text
[REFUSED] Connection refused
False
```

### Analysis

Unlike DROP, the REJECT rule actively informs the client that the connection is not permitted.

In this experiment, the firewall responded using ICMP Port Unreachable, causing the TCP connection attempt to fail immediately.

A firewall can also be configured to reject TCP connections with a TCP RST using `--reject-with tcp-reset`.

Therefore, `Connection refused` does not always mean the server application is stopped. Firewall rejection is another possible cause.

### Remove the REJECT Rule

```bash
sudo ip netns exec n01-server \
  iptables -D INPUT -p tcp --dport 8000 -j REJECT
```

Verify the rules:

```bash
sudo ip netns exec n01-server \
  iptables -L INPUT -n --line-numbers
```

## 10. Final Verification

After removing the firewall rules, the client successfully established a TCP connection again.

Observed packet sequence:

```text
Client -> Server: SYN
Server -> Client: SYN-ACK
```

Final Python result:

```text
True
```

This confirms that the simulated firewall restrictions were removed and the server could accept TCP connections again.

## 11. Experiment Results

| Scenario | Network Evidence | TCP Checker Result |
|---|---|---|
| Normal connection | SYN → SYN-ACK → ACK | `True` |
| Firewall DROP | SYN retransmissions, no response | `TIMEOUT` |
| Firewall REJECT | SYN → ICMP Port Unreachable | `REFUSED` |
| Firewall removed | SYN → SYN-ACK | `True` |

### Important Troubleshooting Lessons

**Ping success does not guarantee TCP service availability.**

ICMP communication may work even when a firewall blocks a specific TCP port.

**A timeout does not automatically mean the server is down.**

It indicates that a connection could not be established within the configured timeout. Packet loss, filtering, routing problems, and other conditions may cause this.

**Connection refused does not always mean the application is stopped.**

A TCP RST or certain ICMP error responses may cause a connection refusal. Firewall behavior must also be considered.

**Packet captures provide evidence, not always the complete root cause.**

Additional checks, such as inspecting firewall rules and verifying listening services with `ss`, may be necessary.

## 12. Troubleshooting Workflow

A practical workflow learned during this lab:

```text
User reports a connection problem
              |
              v
       Check DNS resolution
              |
              v
       Check IP reachability
              |
              v
       Test TCP connection
              |
              v
       Capture network packets
              |
              v
    Identify observed behavior
       /       |        \
  Connected  Timeout   Refused
       \       |        /
              v
     Investigate possible causes
              |
              v
     Apply a targeted solution
              |
              v
       Retest and verify
```

This process emphasizes verifying each assumption using observable evidence.

## 13. Current Limitations

This is an educational project and is still under development.

Current limitations include:

- TCP checking is not yet integrated into the main interactive CLI.
- DNS resolution currently uses `socket.gethostbyname()` for IPv4 lookup.
- TCP checking handles connection refusal and timeout, but not every possible socket error.
- Target selection and port input are not yet exposed through a complete CLI interface.
- Packet capture and firewall experiments currently require manual commands.
- Automated tests have not yet been added.

## 14. Planned Improvements

- Integrate DNS and TCP checks into a single CLI.
- Add input validation for IP addresses and ports.
- Improve socket error handling.
- Add configurable TCP timeouts.
- Create clearer diagnostic output.
- Add automated tests.
- Expand troubleshooting scenarios.
- Add structured diagnostic reports.

## 15. Lab Cleanup

Stop the HTTP server and packet-capture processes before cleaning up the environment.

Remove any firewall rules added for testing, then delete the two network namespaces:

```bash
sudo ip netns del n01-client
sudo ip netns del n01-server
```

The virtual Ethernet interfaces created inside the namespaces will normally be removed with them once no processes retain those network namespaces.

These commands affect the isolated lab namespaces, not the host's primary network interfaces.

## 16. What I Learned

Through this project, I gained practical experience with:

- Python socket programming
- DNS resolution and error handling
- TCP connection establishment
- TCP handshake analysis
- SYN retransmissions
- ICMP Echo Request and Echo Reply
- TCP RST and ICMP error messages
- Linux Network Namespaces
- Virtual Ethernet interfaces
- Routing and interface inspection
- Linux firewall behavior
- Packet-level network troubleshooting

The most valuable lesson was learning to **identify network problems using packet-level evidence rather than making assumptions based only on application error messages**.

---

**Author:** [kojidesu01](https://github.com/kojidesu01)

**Repository:** [Project-N01-Network-Diagnostic-CLI](https://github.com/kojidesu01/Project-N01-Network-Diagnostic-CLI)

**Focus:** Network Engineering · Cybersecurity · Python · Linux