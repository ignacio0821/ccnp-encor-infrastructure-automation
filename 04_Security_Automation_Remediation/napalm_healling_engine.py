import urllib3
from napalm import get_network_driver

# Suppress background warning banners from virtualized sandbox testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# TARGET INVENTORY CLUSTER (CCNP ENCOR FLAGSHIP CORE ROUTERS)
CORE_BACKBONE = [
    {"hostname": "Core-01", "ip": "192.168.91.133"},
    {"hostname": "Core-02", "ip": "192.168.91.137"}
]

USERNAME = "admin"
PASSWORD = "Cisco123"


def execute_napalm_closed_loop_healing():
    print("[*] Initializing NAPALM Closed-Loop Self-Healing Engine...")
    print("=" * 80)

    # Initialize the vendor-agnostic Cisco IOS network driver platform
    driver = get_network_driver('ios')

    for device in CORE_BACKBONE:
        print(f"[>] Establishing secure SSH channel to {device['hostname']} ({device['ip']})...")

        # Instantiate connection session dictionary bindings
        router = driver(hostname=device['ip'], username=USERNAME, password=PASSWORD)

        try:
            router.open()

            # PHASE 1: READ ACTIVE STATE CONFIG LAYER
            print("    - Parsing running configuration database text...")
            config_data = router.get_config()
            running_config = config_data.get('running', '')

            # Setup specific text constraints targeting your data link interface block
            target_intf = "interface GigabitEthernet0/1"
            degraded_string = "ip mtu 1200"

            # Isolate the specific interface block schema from the running-config text string
            is_degraded = False
            if target_intf in running_config:
                # Segment the configuration file starting immediately from our target interface
                after_interface = running_config.split(target_intf)[1]
                # Split at the first structural boundary delimiter '!'
                interface_block_code = after_interface.split('!')[0]

                # Check for the explicit presence of the degraded parameter statement lines
                if degraded_string in interface_block_code:
                    is_degraded = True

            # PHASE 2 & 3: EVALUATE DRIFT & REMEDIATE STATE (The Step 7 Logic Gate Check)
            if is_degraded:
                print(
                    f"    [! DRIFT DETECTED ]: Hidden parameters degraded on GigabitEthernet0/1. Launching remediation...")

                # Construct the clear text candidate configuration delta block template
                remediation_template = (
                    "interface GigabitEthernet0/1\n"
                    " description REMEDIATED_BY_BOUNDED_NAPALM_AUTOMATION_ENGINE\n"
                    " no ip mtu\n"
                    " ip tcp adjust-mss 1360\n"
                    "exit\n"
                )

                # Stage configuration parameters inside candidate configuration database cache
                router.load_merge_candidate(config=remediation_template)

                # Pull the pending configuration delta differences
                diff = router.compare_config()

                if diff:
                    print("    [+] Pending Configuration Changes:")
                    print(diff)

                    # Force commit parameters natively to active memory datastores
                    router.commit_config()
                    print(f"    [+ HEALING SUCCESS ]: Configuration constraints applied successfully.")
                else:
                    print("    [+ STATE VERIFIED ]: Candidate changes matched running config. Skipping push.")
            else:
                print(
                    f"    [+ STATE VERIFIED ]: Interface matches standard 1500 MTU parameters. Bypassing network write operations.")

            router.close()

        except Exception as error_trace:
            print(f"    [-] CRITICAL REMEDIATION FAILURE on {device['hostname']}: {error_trace}")

        print("-" * 80)

    print("[*] Closed-Loop NAPALM Cluster Remediation Process Finished.")


if __name__ == "__main__":
    execute_napalm_closed_loop_healing()
