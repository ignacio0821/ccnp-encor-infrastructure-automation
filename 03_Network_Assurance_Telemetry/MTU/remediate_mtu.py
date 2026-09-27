"""
CCNP ENCOR / CCNA DevNet - Automated OSPF MTU Remediation Engine
Design: Decoupled YAML Variable Processing with Legacy SSH Key-Exchange Overrides
"""

import sys
from napalm import get_network_driver
import yaml

def main():
    print("[*] Initializing Remediation Framework...")

    # 1. Dynamically read environment variables from the configuration file
    try:
        with open("remediation.yaml", "r") as f:
            config_data = yaml.safe_load(f)
        node = config_data["target_node"]
    except FileNotFoundError:
        print("[CRITICAL] Configuration file 'remediation.yaml' was not found!")
        sys.exit(1)
    except KeyError:
        print("[CRITICAL] Malformed YAML! 'target_node' key block is missing.")
        sys.exit(1)

    # 2. Instantiate the NAPALM abstraction driver with Paramiko Handshake Overrides
    driver = get_network_driver("ios")
    device = driver(
        hostname=node["hostname"],
        username=node["username"],
        password=node["password"],
        optional_args={
            "secret": node["secret"],
            # CRITICAL BYPASS: Forces Paramiko to allow legacy DH-Group14-SHA1 key exchanges
            "disabled_algorithms": {"kex": []}
        }
    )

    # 3. Connect to the device and execute state verification gates
    try:
        device.open()
        print(f"[+] Connected successfully to target node: {node['hostname']}")

        # Pull live operational telemetry using the generic CLI method
        print("[*] Retrieving active OSPF neighbor tables via CLI extraction...")

        # Passes the raw command to the router; returns a dictionary keyed by the command string
        cli_output = device.cli(["show ip ospf neighbor"])
        ospf_table = cli_output.get("show ip ospf neighbor", "")

        print("\n--- LIVE OSPF TABLE CONSOLE TEXT ---")
        print(ospf_table)
        print("------------------------------------\n")

        chaos_detected = False

        # Parse the raw text data directly for protocol state markers
        if "EXSTART" in ospf_table.upper() or "EXCHANGE" in ospf_table.upper():
            print("[🚨 CHAOS DETECTED] Control plane lock found inside the CLI output strings!")
            chaos_detected = True


        # 4. Remediation Logic Gate
        if chaos_detected:
            print(f"[*] Compiling atomic correction payload for interface {node['interface']}...")

            # Build the explicit, targeted IOS interface configuration snippet
            remediation_payload = (
                f"interface {node['interface']}\n"
                f" ip mtu {node['correct_mtu']}\n"
                "end\n"
            )

            # Push the candidate change configuration cleanly to the device memory
            print("[*] Loading candidate correction strings into device memory...")
            device.load_merge_candidate(config=remediation_payload)

            # View the planned changes to confirm accuracy before saving
            print("\n--- PENDING CANDIDATE DIFF TRACKING ---")
            print(device.compare_config())
            print("----------------------------------------\n")

            # Commit the change permanently into production running-config
            print("[+] Committing changes! Pushing configuration modifications live...")
            device.commit_config()
            print(f"[✅ RESOLVED] Interface {node['interface']} successfully updated to MTU {node['correct_mtu']}.")

        else:
            print("[✅ CLEAR] All tracked OSPF adjacencies are clean. No action required.")

    except Exception as e:
        print(f"[CRITICAL ERROR] Execution failed: {e}")
        sys.exit(1)

    finally:
        # Guarantee that the SSH management terminal session closes cleanly
        device.close()
        print("[*] SSH connection safely terminated. Engine offline.")

if __name__ == "__main__":
    main()
