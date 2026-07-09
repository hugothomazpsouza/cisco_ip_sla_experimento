# 🌐 High-Availability Network Resilience: Cisco IP SLA & Object Tracking

[![Platform](https://img.shields.io/badge/Platform-EVE--NG%20%7C%20Cisco%20IOL-blue)](https://www.eve-ng.net/)
[![OS](<https://img.shields.io/badge/Cisco%20IOS-15.4(2)T4-orange>)](https://www.cisco.com/)
[![Focus](https://img.shields.io/badge/Research-M.Sc.%20Network%20Resilience-success)](https://github.com/)

This repository contains the emulation infrastructure, validation scripts, and network configurations used for the **Floating Static Routing with Active Monitoring (Cisco IP SLA + Object Tracking)** case study.

This experiment serves as a **reference model (Tradicional Baseline)** for my Master's research. It establishes a performance benchmark for convergence time and downtime of the traditional Control Plane, comparing it against Programmable Data Plane architectures (Software-Defined Networking - P4 / BMv2 with In-Band Telemetry).

---

## 🏗️ Experiment Architecture and Topology

The environment was emulated on the **EVE-NG** platform using **Cisco IOS on Linux (IOL / iOU 15.4)** images for the routers and **Linux (Ubuntu/Alpine)** nodes for the end hosts and traffic generators.

```text
       [ Host-3: Traffic Generator / Noise ]
                       | (192.168.3.10/24)
                       | e0/2
                 +-----+-----+
                 |    R2     | (Primary Transit - QoS 500 Kbps)
                 +-----+-----+
                 / e0/0     \ e0/1
    (10.1.12.0/30) /           \ (10.1.24.0/30)
               e0/0 /             \ e0/0
+-----+-----+      /               \      +-----+-----+
|    R1     |-----+                 +-----|    R4     |
+-----+-----+ e0/1                   e0/1 +-----+-----+
   | e0/2     \                         /    | e0/2
   |           \                       /     |
   |            +---------------------+      |
   |              |        R3       |        |
   |              +-----------------+        |
   |               (Backup Transit)          |
   |               (10.1.13.0/30 &           |
   |                10.1.34.0/30)            |
+--+--------+                             +--+--------+
|  Host-1   |                             |  Host-2   |
| (Source)  |                             | (Destination)|
+-----------+                             +-----------+
192.168.1.10                              192.168.2.10
```

> **Note:** To simulate this environment, you need an EVE-NG setup (or another network emulation platform) and the appropriate Cisco images.

### 📁 Configuration Files

All complete and ready-to-use router configurations (`R1.cfg`, `R2.cfg`, `R3.cfg`, and `R4.cfg`) are located in the `routers_config/` folder of this repository.

### ⚙️ Implemented Mechanics Summary (Example on R1)

- **Carrier-Delay Zeroing (`carrier-delay msec 0`)**: Removes the debouncing delay from the virtual interface for instant detection of physical/virtual link failures.
- **Probe Pinning (`ip route 10.1.24.2 255.255.255.255 10.1.12.2`)**: A `/32` host route that forces the ICMP test to pass exclusively through the primary link, preventing routing loops and flapping.
- **Active Monitoring (`ip sla 1`)**: An ICMP probe is sent every 1 second (`frequency 1`), with degradation and failure tolerance calibrated at a 150 ms threshold (`timeout 150` / `threshold 150`).
- **Floating Routes**: The main route is tied to the tracker (`track 10`) with a default Administrative Distance (AD) of 1, and the contingency route via R3 is configured with an AD of 20.

---

## 🖥️ Hosts Configuration

Access the hosts and edit the network interfaces file:

```bash
sudo vim /etc/network/interfaces
```

Add the following configurations for each respective host:

**Host-1**

```text
auto eth0
iface eth0 inet static
    address 192.168.1.10
    netmask 255.255.255.0
    gateway 192.168.1.1
```

**Host-2**

```text
auto eth0
iface eth0 inet static
    address 192.168.2.10
    netmask 255.255.255.0
    gateway 192.168.2.1
```

**Host-3**

```text
auto eth0
iface eth0 inet static
    address 192.168.3.10
    netmask 255.255.255.0
    gateway 192.168.3.1
```

### Applying Configurations

After saving the file on each host, restart the network service to apply the configurations:

```bash
/etc/init.d/networking restart
# or
sudo systemctl restart networking
```

---

## 🧪 Testing

### Connectivity Test (Host-1 to Host-2)

Run the following command from Host-1:

```bash
sudo ping -O -D 192.168.2.10
```

- The `-D` flag adds a UNIX Timestamp (in seconds.milliseconds) before each packet.
- The `-O` flag forces `ping` to print a warning line even when a packet is lost ("no answer yet").

### Flood Test (Host-3 to Host-2)

To simulate a flood (network congestion/noise), run the following command from Host-3:

```bash
sudo ping -f -s 65000 192.168.2.10
```
