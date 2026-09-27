#


# Loop through every line in the ARP table dump:
#     Extract the IP address and the MAC address
#
#     // Check 1: Catch duplicate MAC mappings (ARP Spoofing)
#     IF this MAC address is already tied to a DIFFERENT IP in our list:
#         Flag as SUSPICIOUS: "Potential ARP Spoofing Attack Detected!"
#
#     // Check 2: Catch unauthorized device claiming the Gateway
#     IF the IP is our Default Gateway BUT the MAC does not match our known Router MAC:
#         Flag as CRITICAL: "Man-in-the-Middle Attack on Gateway!"
#
#     Save this IP and MAC pair to our list to check against the next lines


#
# FUNCTION Parse_And_Verify_ARP_Table(ARP_Dump_Text, Known_Gateway_IP, True_Gateway_MAC):
#     Seen_Mappings = EMPTY_DICTIONARY // Keys will be MACs, Values will be IPs
#
#     FOR EACH Line IN ARP_Dump_Text DO
#         IF Line CONTAINS Valid_IP AND Valid_MAC THEN
#             Current_IP  = EXTRACT_IP(Line)
#             Current_MAC = EXTRACT_MAC(Line)
#
#             // Validate Gateway Integrity (SCOR Security Rule)
#             IF Current_IP == Known_Gateway_IP AND Current_MAC != True_Gateway_MAC THEN
#                 TRIGGER_ALERT("CRITICAL: Rogue gateway detected at MAC " + Current_MAC)
#             ENDIF
#
#             // Validate Unique Bindings (One MAC should not own multiple active IPs)
#             IF Current_MAC EXISTS IN Seen_Mappings THEN
#                 Previous_IP = Seen_Mappings[Current_MAC]
#                 IF Previous_IP != Current_IP THEN
#                     TRIGGER_ALERT("WARNING: MAC " + Current_MAC + " is claiming both " + Previous_IP + " and " + Current_IP)
#                 ENDIF
#             ELSE
#                 Seen_Mappings[Current_MAC] = Current_IP
#             ENDIF
#         ENDIF
#     ENDFOR
# ENDFUNCTION


# Raw multi-line CLI output from the router (Your Gate 1 Input)
raw_cli_output = """
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  192.168.1.1             -   0000.0c9f.f001  ARPA   Vlan1
Internet  192.168.1.50            0   0000.aaaa.bbbb  ARPA   Vlan1
Internet  10.0.0.5               15   00aa.bbcc.dddd  STATIC Vlan1
"""

# ==============================================================================
# GATE 1: INGESTION STRING SPLIT
# ==============================================================================
# Split the massive text block into individual rows using the newline character
all_rows = raw_cli_output.strip().split("\n")

# ==============================================================================
# GATE 2 & 3: THREAT FILTERING & DATA EXTRACTION
# ==============================================================================
for row in all_rows:
    # Clean up hidden spaces and skip the header line
    clean_row = row.strip()
    if clean_row.startswith("Protocol") or not clean_row:
        continue  # Skip this loop iteration and move to the next row

    # Convert the row to lowercase so matches aren't missed due to capital letters
    lowercase_row = clean_row.lower()

    # Check for threats (Gate 2 Rules)
    if "static" in lowercase_row or "0000.aaaa.bbbb" in lowercase_row:
        # Split the row by any chunk of whitespace (Gate 3 Data Extraction)
        # This converts "Internet 192.168.1.50 0 0000.aaaa.bbbb" into a list
        fields = clean_row.split()

        # Python lists start counting at 0!
        # fields[0] = "Internet"
        # fields[1] = IP Address (Your 2nd item)
        # fields[2] = Age
        # fields[3] = MAC Address (Your 4th item)
        extracted_ip = fields[1]
        extracted_mac = fields[3]

        # Output the clean alert to the console
        print(f"🚨 THREAT DETECTED: IP {extracted_ip} is using Bad MAC {extracted_mac}")
