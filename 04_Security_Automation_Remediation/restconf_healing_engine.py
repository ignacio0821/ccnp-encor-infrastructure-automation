import requests
import urllib3
import json

# Suppress self-signed SSL warning banners from virtualized sandboxes
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# TARGET INVENTORY CLUSTER (CCNP ENCOR CORE MATRIX)
CORE_BACKBONE = [
    {"hostname": "Core-01", "ip": "192.168.91.133"},
    {"hostname": "Core-02", "ip": "192.168.91.137"}
]

AUTH = ("admin", "Cisco123")
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}


def execute_closed_loop_healing():
    # Canonical path targeting the native Cisco GigabitEthernet container for interface 1
    native_path = "/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1"
    url_suffix = "?content=config"

    print("[*] Initializing Native Cisco Closed-Loop Self-Healing Engine...")
    print("=" * 80)

    for device in CORE_BACKBONE:
        url = f"https://{device['ip']}:443{native_path}{url_suffix}"
        print(f"[>] Interrogating {device['hostname']} ({device['ip']}) via Cisco-IOS-XE Native model...")

        try:
            # PHASE 1 & 2: READ AND EVALUATE STATE (The Step 7 Logic Gate)
            response = requests.get(url, headers=HEADERS, auth=AUTH, verify=False, timeout=4)

            if response.status_code == 200:
                data = response.json()
                gi_interface = data.get("Cisco-IOS-XE-native:GigabitEthernet", {})

                # Dig into the native Cisco IP container tree blocks
                ip_configs = gi_interface.get("ip", {})

                # Extract the native MTU value (Default to 1500 if the 'mtu' key doesn't exist in running-config)
                current_mtu = ip_configs.get("mtu", 1500)

                print(f"    - Current Cisco Native Interface MTU State: {current_mtu} bytes")

                # PHASE 3: AUTOMATED REMEDIATION PUSH (Step 9 Overwrite)
                if current_mtu < 1500:
                    print(
                        f"    [! DRIFT DETECTED ]: Link parameters degraded. Launching native remediation template...")

                    # Remediation payload forcing perfect MTU and standard TCP MSS optimization constraints natively
                    remediation_payload = {
                        "Cisco-IOS-XE-native:GigabitEthernet": {
                            "name": "1",
                            "description": "REMEDIATED_BY_AUTOMATION_ENGINE_PERFECT_STATE",
                            "ip": {
                                "mtu": 1500,
                                "tcp": {
                                    "adjust-mss": 1360
                                }
                            }
                        }
                    }

                    # Using PUT to target the interface container and overwrite the broken state
                    repair_url = f"https://{device['ip']}:443{native_path}"
                    repair_response = requests.put(
                        url=repair_url,
                        headers=HEADERS,
                        auth=AUTH,
                        data=json.dumps(remediation_payload),
                        verify=False,
                        timeout=5
                    )

                    if repair_response.status_code in (200, 201, 204):
                        print(
                            f"    [+ HEALING SUCCESS ]: Native link remediated to 1500 MTU & 1360 MSS successfully (HTTP {repair_response.status_code}).")
                    else:
                        print(
                            f"    [-] HEALING FAILED  : Node rejected native payload. HTTP Code: {repair_response.status_code}")
                else:
                    print(f"    [+ STATE VERIFIED ]: Link is running perfectly. No remediation required.")
            else:
                print(f"    [-] ERROR: Unable to retrieve native schema data. HTTP Code: {response.status_code}")

        except requests.exceptions.RequestException as error_trace:
            print(f"    [-] CRITICAL FAILURE: Network execution breakdown: {error_trace}")

        print("-" * 80)

    print("[*] Closed-Loop Native Cluster Evaluation Finished.")


if __name__ == "__main__":
    execute_closed_loop_healing()
