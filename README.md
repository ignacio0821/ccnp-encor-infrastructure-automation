# 🛰️ CCNP ENCOR Flagship Automation & Closed-Loop Remediation Matrix

An enterprise-grade data center transit backbone built within Cisco Modeling Labs (CML), automated natively over secure management vectors using multi-layer Python programmatic frameworks.

## 🗂️ Core Workspace Architecture

| Engineering Directory | Operational Focus & Target Asset |
| :--- | :--- |
| **`00_Design_Blueprints_Pseudocode`** | Language-agnostic logic gates and automated self-healing flow charts. |
| **`04_Security_Automation_Remediation`** | Idempotent Python scripts executing secure NAPALM configurations over SSH channels. |
| **`Assets`** | Authoritative 20-Node dual-stack IPAM reference network document matrix sheet. |

---

## 💥 Chaos Engineering Objective: The OSPF MTU "Silent Killer"

This infrastructure focuses on programmatically detecting and repairing **"Silent Killer" interface mismatches** that traditional monitoring tools frequently miss.

### 🔬 The Failure Mechanism
* **The Degradation:** A point-to-point transit link interface is forcefully restricted to an IP MTU of `1200` bytes.
* **The Trap:** OSPF neighbors remain deceptively stable at `FULL` until a process clears or an interface flaps.
* **The Protocol Loop:** Once memory resets, the routers get permanently trapped in the `EXSTART/EXCHANGE` loop, constantly retransmitting Database Description (DBD) packets (`ospf.type == 2`) that fail the path size limits.

### 📐 Automated Remediation Logic Gate
```text
IF Router_Interface_MTU LESS THAN 1500 THEN
    PRINT "[!] SILENT KILLER DRIFT DETECTED: OSPF Adjacency Is At Risk!"
    DEPLOY RESTCONF/NAPALM PATH MUTATION: "no ip mtu" + "ip tcp adjust-mss 1360"
ELSE
    PRINT "[+] STATE VERIFIED: OSPF Path is Structurally Sound."
END IF
```

### 🛡️ Idempotent Design Rules
The automated remediation utility (`napalm_healing_engine.py`) enforces strict production idempotency:
1. **Pass 1 (Remediation):** Scans the backbone text, flags configuration drift, and applies the candidate fix.
2. **Pass 2 (Verification):** Re-interrogates the network immediately after. Because parameters match target constraints, the script bypasses all write operations and cleanly returns an exit code of `0`.
