# Automated Control-Plane Remediation Engine (OSPF MTU Mismatch)

# STATUS: ACTIVE ENGINEERING SPRINT — WORK IN PROGRESS (WIP)
> *This repository serves as a live laboratory log notebook documenting model-driven telemetry, automated protocol remediation scripts, and infrastructure-as-code patterns.*

---

# Automated Control-Plane Remediation Engine (OSPF MTU Mismatch)

## Architectural Overview
This repository contains a self-healing infrastructure automation engine...

This repository contains a self-healing infrastructure automation engine built to detect and remediate protocol-stalling state conflicts at Layer 3. Specifically, it resolves asymmetric Maximum Transmission Unit (MTU) mismatches that trap Cisco Open Shortest Path First (OSPF) adjacencies in the `EXSTART`/`EXCHANGE` negotiation loop.

The script automates state collection by pulling active router configurations using secure, cryptographically adapted SSH tunnels. It then reviews terminal tables using conditional text parsing algorithms and triggers targeted configuration modifications via transactional atomic merging.

## 🛠️ Core Technology Stack
*   **Automation Platform:** NAPALM (Network Automation and Programmability Abstraction Layer with Multi-OS support)
*   **Underlying Drivers:** Netmiko / Paramiko SSH Transport Core
*   **Data Serialization:** YAML v1.2 (Decoupled environment configuration)
*   **Lab Infrastructure:** Cisco Modeling Labs (CML) / Cisco IOS

