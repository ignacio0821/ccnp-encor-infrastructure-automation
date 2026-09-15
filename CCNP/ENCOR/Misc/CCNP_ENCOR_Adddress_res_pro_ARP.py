# Abstract Logic problem solution statement / Pseudocode and logic gates

# 1) Abstract logic problem statement

# 2) Syntax research -- Audit logic gates for pythonic precision

# 3) visual flow mapping -- graph gate vectors & secondary boundaries

# 4) implementation & peer review -- Code out gates from blank document safely

# 5) Rigorous testing -- Manual local verification


# Logic Gate _:Section 1: Source Host - Layer 3 Logical Addressing
# IF destination_ip network matches my network:
#     next_hop = destination_ip
# ELSE:
#     next_hop = default_gateway_ip
#
# send packet down to Layer 2 using next_hop

# Logic Gate _: Layer 2 physical address
# look up next_hop_ip in my ARP table to get its MAC address
#
# IF MAC address is found:
#     wrap packet inside an Ethernet frame
#     set destination MAC = next_hop_mac
#     send frame onto the physical wire
# ELSE:
#     trigger the ARP discovery process to find the missing MAC



# Logic Gate _:  Intro to ARP#
# IF destination_ip is already in my ARP table:
#     use that known MAC address
#     send packet
# ELSE:
#     mark IP as "incomplete" in table
#     build ARP Request (Opcode 1)
#     send as broadcast (FF:FF:FF:FF:FF:FF)
#     wait for host to reply
#     save new MAC to ARP table


# Logic Gate _:  ARP Message Format
# Build ARP message packet:
#     set types (Ethernet, IPv4, lengths 6 and 4)
#     set opcode (1 for request, 2 for reply)
#     insert source IP/MAC and target IP/MAC
#
# wrap inside Ethernet frame:
#     set source/dest MAC addresses
#     set EtherType = 0x0806 (this tags it as ARP)
#     append error checking trailer (FCS)


# Logic Gate _: ARP Process
# For every machine that hears the broadcast:
#     IF target_ip matches my own IP:
#         save sender's IP and MAC into my local ARP table
#         build ARP Reply (Opcode 2) using MY MAC address
#         send frame as UNICAST directly back to sender's MAC
#     ELSE:
#         ignore and drop packet

# Logic Gate _: Proxy ARP
# IF proxy_arp is turned off globally or on interface:
#     drop packet
#
# IF target_ip is on my own local wire network segment:
#     drop packet (let the actual host answer itself)
#
# IF target_ip exists in my routing table:
#     build ARP Reply (Opcode 2)
#     put MY ROUTER MAC as the source for that target_ip
#     unicast reply back to sender
# ELSE:
#     drop packet (network unreachable)

# Logic Gate _: Gratuitous ARP
# build unsolicited ARP reply (Opcode 2)
#     set source IP = my own IP
#     set target IP = my own IP
#     set source MAC = my own MAC
#     send as broadcast (FF:FF:FF:FF:FF:FF)
#
# when other hosts receive it:
#     IF sender_ip matches my own IP:
#         log critical error: "IP CONFLICT DETECTED!"
#     IF sender_ip is already in my ARP table:
#         update old entry with this new announced MAC address











# Logic Gate_A: Layer 3 provides the end-to-end logical addressing. source host ip address to the destination ip address
# ==============================================================================
# CONCEPT: Layer 3 provides the end-to-end logical addressing from the
#          source host IP address to the destination IP address.
# ==============================================================================
#     if (source_ip & subnet_mask) == (destination_ip & subnet_mask):
#         return "Packet delivered locally."
#     else:
#         return "Forwarding to next hop router."
# 1) why we need Layer 2 and Layer 3 addresses


# Logic Gate_A.1: // Layer 3 passes the destination IP down and asks Layer 2 for delivery
# FUNCTION Layer2_Physical_Delivery(Packet, Next_Hop_IP):
#
#     // Step 1: Check if the destination is on the local segment
#     IF Next_Hop_IP == Packet.Destination_IP THEN
#         // Target is on the same local segment
#         Target_MAC = ARP_LOOKUP(Packet.Destination_IP)
#         Frame = ENCAPSULATE_LAYER2(Packet, Target_MAC)
#         TRANSMIT_ON_WIRE(Frame)
#         RETURN "Delivered directly to the end host."
#
#     ELSE
#         // Target is on a different subnet, deliver to the gateway instead
#         Gateway_MAC = ARP_LOOKUP(Default_Gateway_IP)
#         Frame = ENCAPSULATE_LAYER2(Packet, Gateway_MAC)
#         TRANSMIT_ON_WIRE(Frame)
#         RETURN "Forwarded to the default gateway."
#     ENDIF
#
# ENDFUNCTION
# 1) why we need Layer 2 and Layer 3 addresses


# Logic Gate_B: FUNCTION Resolve_L3_To_L2(Next_Hop_IP, ARP_Cache):
#
#     // Step 1: Check if the L2 MAC address is already known locally
#     IF Next_Hop_IP EXISTS IN ARP_Cache THEN
#         Target_MAC = ARP_Cache[Next_Hop_IP]
#         RETURN Target_MAC // Known L2 address found
#     ENDIF
#
#     // Step 2: If unknown, the sender must learn it via a broadcast
#     // Target MAC is set to FF:FF:FF:FF:FF:FF so every device processes it
#     ARP_Request_Frame = CREATE_ARP_REQUEST(
#         Sender_IP = Local_IP,
#         Sender_MAC = Local_MAC,
#         Target_IP = Next_Hop_IP,
#         Destination_MAC = "FF:FF:FF:FF:FF:FF"
#     )
#
#     BROADCAST_ON_LOCAL_SEGMENT(ARP_Request_Frame)
#
#     // Step 3: Wait for the specific target to reply
#     ARP_Reply_Frame = WAIT_FOR_ARP_REPLY(From = Next_Hop_IP)
#
#     // Step 4: Map the newly learned L2 address and update cache
#     Learned_MAC = ARP_Reply_Frame.Sender_MAC
#     ARP_Cache[Next_Hop_IP] = Learned_MAC
#
#     RETURN Learned_MAC
# ENDFUNCTION


# Logic Gate_C:FUNCTION Encapsulate_ARP_Frame(Source_MAC, Destination_MAC, ARP_Message_Payload):
#     // Create the outer Layer 2 container
#     Ethernet_Frame = CREATE_NEW_FRAME()
#
#     // Write standard Ethernet Header fields
#     Ethernet_Frame.Destination_MAC = Destination_MAC // e.g., FF:FF:FF:FF:FF:FF for requests
#     Ethernet_Frame.Source_MAC = Source_MAC           // Sender's physical address
#     Ethernet_Frame.EtherType = 0x0806                 // Identifies payload explicitly as ARP [1]
#
#     // Inject the raw ARP payload directly inside the frame
#     Ethernet_Frame.Payload = ARP_Message_Payload
#
#     // Append the Layer 2 trailer for error checking
#     Ethernet_Frame.Trailer_FCS = CALCULATE_CRC32(Ethernet_Frame)
#
#     RETURN Ethernet_Frame
# ENDFUNCTION

# FUNCTION Create_ARP_Message_Payload(Opcode, Sender_MAC, Sender_IP, Target_IP, Target_MAC="00:00:00:00:00:00"):
#     ARP_Payload = CREATE_EMPTY_STRUCTURE()
#
#     // Hardware & Protocol Specifications
#     ARP_Payload.Hardware_Type = 0x0001      // 1 = Ethernet (10Mb)
#     ARP_Payload.Protocol_Type = 0x0800      // 0x0800 = IPv4 [1]
#     ARP_Payload.Hardware_Size = 6           // MAC addresses are 6 bytes (48 bits)
#     ARP_Payload.Protocol_Size = 4           // IPv4 addresses are 4 bytes (32 bits)
#
#     // Operation Code Determination
#     // Opcode 1 = Request, Opcode 2 = Reply
#     ARP_Payload.Opcode = Opcode
#
#     // Addressing Bindings (The Core Mapping)
#     ARP_Payload.Sender_Hardware_Address = Sender_MAC
#     ARP_Payload.Sender_Protocol_Address = Sender_IP
#
#     // For a Request (Opcode 1), Target MAC is unknown, so it defaults to zeros
#     ARP_Payload.Target_Hardware_Address = Target_MAC
#     ARP_Payload.Target_Protocol_Address = Target_IP
#
#     RETURN ARP_Payload
# ENDFUNCTION
# 2) Intro to ARP#


# Logic Gate_D: // Define the data model for the ARP Message Format
# STRUCTURE ARP_Message:
#     Hardware_Type          : 16-bit Integer // Default: 0x0001
#     Protocol_Type          : 16-bit Integer // Default: 0x0800
#     Hardware_Length        : 8-bit Integer  // Default: 0x06
#     Protocol_Length        : 8-bit Integer  // Default: 0x04
#     Opcode                 : 16-bit Integer // 1 = Request, 2 = Reply
#     Sender_Hardware_Addr   : 48-bit MAC
#     Sender_Protocol_Addr   : 32-bit IP
#     Target_Hardware_Addr   : 48-bit MAC
#     Target_Protocol_Addr   : 32-bit IP
# ENDSTRUCTURE
#
# FUNCTION Build_ARP_Message(Opcode, Src_MAC, Src_IP, Dest_IP, Dest_MAC="00:00:00:00:00:00"):
#     // Instantiate the fixed-format fields
#     Msg = NEW ARP_Message()
#     Msg.Hardware_Type   = 0x0001
#     Msg.Protocol_Type   = 0x0800
#     Msg.Hardware_Length = 0x06
#     Msg.Protocol_Length = 0x04
#
#     // Assign dynamic operational variables
#     Msg.Opcode               = Opcode
#     Msg.Sender_Hardware_Addr = Src_MAC
#     Msg.Sender_Protocol_Addr = Src_IP
#     Msg.Target_Hardware_Addr = Dest_MAC
#     Msg.Target_Protocol_Addr = Dest_IP
#
#     RETURN Msg
# ENDFUNCTION

# FUNCTION Package_For_Wire(ARP_Payload, Local_MAC, L2_Destination_MAC):
#     Ethernet_Frame = CREATE_NEW_FRAME()
#
#     // Apply the Layer 2 Outer Header
#     Ethernet_Frame.Destination_MAC = L2_Destination_MAC // Broadcast or Unicast
#     Ethernet_Frame.Source_MAC      = Local_MAC
#     Ethernet_Frame.EtherType       = 0x0806              // Explicitly tags frame as ARP
#
#     // Nest the payload
#     Ethernet_Frame.Data_Payload    = ARP_Payload
#
#     // Generate the standard Layer 2 Frame Check Sequence (Trailer)
#     Ethernet_Frame.Trailer_FCS     = CALCULATE_CRC32(Ethernet_Frame)
#
#     RETURN Ethernet_Frame
# ENDFUNCTION
# 3) ARP Message Format

# Logic Gate_E: 1. FUNCTION Execute_ARP_Workflow(Source_Host, Destination_IP, ARP_Cache):
#
#     // ==========================================
#     // STEP 1: CHECK ARP CACHE FOR AN ENTRY
#     // ==========================================
#     IF Destination_IP EXISTS IN ARP_Cache THEN
#         IF ARP_Cache[Destination_IP].Status == "COMPLETE" THEN
#             PRINT "[DEBUG ARP] Cache hit. No need to proceed with ARP."
#             RETURN ARP_Cache[Destination_IP].MAC_Address
#         ENDIF
#     ELSE
#         PRINT "[DEBUG ARP] Cache miss. Creating incomplete entry."
#         ARP_Cache[Destination_IP] = { "MAC_Address": "00:00:00:00:00:00", "Status": "INCOMPLETE" }
#     ENDIF
#
#     // ==========================================
#     // STEP 2: GENERATE AND BROADCAST ARP REQUEST
#     // ==========================================
#     PRINT "[DEBUG ARP] Generating ARP Request Message."
#     ARP_Request = Build_ARP_Message(
#         Opcode = 1, // Request
#         Src_MAC = Source_Host.MAC,
#         Src_IP = Source_Host.IP,
#         Dest_IP = Destination_IP,
#         Dest_MAC = "00:00:00:00:00:00"
#     )
#
#     Ethernet_Frame = Package_For_Wire(ARP_Request, Source_Host.MAC, "FF:FF:FF:FF:FF:FF")
#     TRANSMIT_BROADCAST_ON_WIRE(Ethernet_Frame)
#
#     // ==========================================
#     // STEP 3: PROCESS ARP REQUEST (Destination Side)
#     // ==========================================
#     // Every host on the segment receives the broadcast frame
#     FOR EACH Host ON Local_Network_Segment DO
#         IF Host.IP == ARP_Request.Target_Protocol_Address THEN
#             PRINT "[DEBUG ARP] Target host matched IP: " + Host.IP
#
#             // Update destination's cache with sender's info (Proactive caching)
#             Host.ARP_Cache[ARP_Request.Sender_Protocol_Address] = {
#                 "MAC_Address": ARP_Request.Sender_Hardware_Addr,
#                 "Status": "COMPLETE"
#             }
#
#             // ==========================================
#             // STEP 4: GENERATE & SEND UNICAST REPLY
#             // ==========================================
#             PRINT "[DEBUG ARP] Generating Unicast ARP Reply Message."
#             ARP_Reply = Build_ARP_Message(
#                 Opcode = 2, // Reply
#                 Src_MAC = Host.MAC,
#                 Src_IP = Host.IP,
#                 Dest_IP = ARP_Request.Sender_Protocol_Address,
#                 Dest_MAC = ARP_Request.Sender_Hardware_Addr
#             )
#
#             // Notice Destination MAC is Unicast (Directly to the source)
#             Reply_Frame = Package_For_Wire(ARP_Reply, Host.MAC, ARP_Request.Sender_Hardware_Addr)
#             TRANSMIT_UNICAST_ON_WIRE(Reply_Frame, Destination = ARP_Request.Sender_Hardware_Addr)
#             BREAK
#         ELSE
#             // Non-matching hosts drop the broadcast frame at the ARP layer
#             DROP_PACKET(ARP_Request)
#         ENDIF
#     ENDFOR
#
#     // ==========================================
#     // FINAL UPDATE: Source processes reply and updates table
#     // ==========================================
#     Source_Host.ARP_Cache[Destination_IP] = {
#         "MAC_Address": ARP_Reply.Sender_Hardware_Addr,
#         "Status": "COMPLETE"
#     }
#     PRINT "[DEBUG ARP] ARP Table updated successfully."
#
# ENDFUNCTION
#
# # 1. INIT CAPTURE
# [DEBUG ARP] Checking local cache for 192.168.1.50...
# [DEBUG ARP] IP not found. Marking 192.168.1.50 as INCOMPLETE in tables.
#
# # 2. ARP REQUEST PACKET CAPTURE
# Frame 1: 64 bytes on wire
#     Ethernet II, Src: 00:aa:bb:cc:dd:11, Dst: ff:ff:ff:ff:ff:ff
#         EtherType: 0x0806 (ARP)
#     Address Resolution Protocol (request)
#         Hardware type: Ethernet (1)
#         Protocol type: IPv4 (0x0800)
#         Opcode: request (1)
#         Sender MAC address: 00:aa:bb:cc:dd:11 (192.168.1.10)
#         Target MAC address: 00:00:00:00:00:00 (192.168.1.50)
#
# # 3. PROCESS & UPDATE CACHE (Destination Side)
# [DEBUG ARP] 192.168.1.50 received Request. Learning mapping: 192.168.1.10 -> 00:aa:bb:cc:dd:11
#
# # 4. ARP REPLY PACKET CAPTURE
# Frame 2: 64 bytes on wire
#     Ethernet II, Src: 00:aa:bb:cc:ee:55, Dst: 00:aa:bb:cc:dd:11
#         EtherType: 0x0806 (ARP)
#     Address Resolution Protocol (reply)
#         Opcode: reply (2)
#         Sender MAC address: 00:aa:bb:cc:ee:55 (192.168.1.50)
#         Target MAC address: 00:aa:bb:cc:dd:11 (192.168.1.10)
#
# # 5. FINAL ARPTABLES VERIFICATION
# [DEBUG ARP] Source Host Cache updated.
# Protocol  Address          Age (min)  Hardware Addr   Type   Interface
# Internet  192.168.1.50            0   00aa.bbcc.ee55  ARPA   Vlan1
# 4) ARP Process


# IF proxy_arp is off:
#     drop packet
#
# IF target_ip is on my own local wire:
#     drop packet (let the host answer itself)
#
# IF target_ip is in my routing table:
#     send reply using MY MAC address
# ELSE:
#     drop packet

# Logic Gate_F: FUNCTION Process_Incoming_ARP_Request(Router, Incoming_Interface, ARP_Request):
#
#     // Condition 1: Proxy ARP must be enabled globally/on the interface
#     IF Router.Proxy_ARP_Enabled == FALSE OR Incoming_Interface.Proxy_ARP_Enabled == FALSE THEN
#         DROP_PACKET(ARP_Request)
#         RETURN "Proxy ARP disabled. Request ignored."
#     ENDIF
#
#     Target_IP = ARP_Request.Target_Protocol_Address
#
#     // Condition 2: Is the target IP on the SAME subnet as the incoming interface?
#     // A router will NOT proxy for devices that are on the same local segment.
#     IF (Target_IP AND Incoming_Interface.Subnet_Mask) == (Incoming_Interface.IP AND Incoming_Interface.Subnet_Mask) THEN
#         DROP_PACKET(ARP_Request)
#         RETURN "Target is local to the sender. Let the host answer itself."
#     ENDIF
#
#     // Condition 3: Does the router know how to reach this remote network?
#     Best_Route = LOOKUP_ROUTING_TABLE(Router.Routing_Table, Target_IP)
#
#     IF Best_Route IS NOT NULL THEN
#         // Proxy ARP Match! The router answers using its OWN interface MAC address.
#         PRINT "[DEBUG PROXY-ARP] Proxying for Target IP: " + Target_IP
#
#         ARP_Reply = Build_ARP_Message(
#             Opcode = 2, // Reply
#             Src_MAC = Incoming_Interface.MAC_Address, // Router puts its own MAC here!
#             Src_IP = Target_IP,                       // Router claims to own the target IP
#             Dest_IP = ARP_Request.Sender_Protocol_Address,
#             Dest_MAC = ARP_Request.Sender_Hardware_Addr
#         )
#
#         Reply_Frame = Package_For_Wire(ARP_Reply, Incoming_Interface.MAC_Address, ARP_Request.Sender_Hardware_Addr)
#         TRANSMIT_UNICAST_ON_WIRE(Reply_Frame, Destination = ARP_Request.Sender_Hardware_Addr)
#
#         RETURN "Proxy ARP Reply Sent."
#     ELSE
#         DROP_PACKET(ARP_Request)
#         RETURN "Target network unreachable. Router dropped request."
#     ENDIF
#
# ENDFUNCTION
# # 1. HOST A SENDS MISCONFIGURED REQUEST
# [DEBUG ARP] Host_A (192.168.1.10) broadcasting for 10.0.0.5... (Incorrectly thinks it's local)
#
# # 2. ROUTER INTERCEPTS VIA PROXY ARP ENGINE
# [DEBUG PROXY-ARP] Received ARP request on Gi0/0 for 10.0.0.5.
# [DEBUG PROXY-ARP] Target 10.0.0.5 is remote. Interface Gi0/0 Proxy ARP status: ENABLED (Default).
# [DEBUG PROXY-ARP] Routing table check: 10.0.0.0/24 is reachable via Gi0/1. Proceeding.
#
# # 3. ROUTER SENDS SPOOFED REPLY
# [DEBUG PROXY-ARP] Sending Unicast Reply to Host_A: 10.0.0.5 is at 00:00:0c:9f:f0:01 (Router's Gi0/0 MAC)
#
# # 4. HOST A ARP TABLE VERIFICATION
# Protocol  Address          Age (min)  Hardware Addr   Type   Interface
# Internet  192.168.1.1             0   0000.0c9f.f001  ARPA   Vlan1  (Actual Gateway)
# Internet  10.0.0.5                0   0000.0c9f.f001  ARPA   Vlan1  (Proxied Destination)
# Proxy ARP


# Logic Gate_G: FUNCTION Broadcast_Gratuitous_ARP(Interface, Trigger_Reason):
#     PRINT "[DEBUG GARP] Triggered: " + Trigger_Reason
#
#     // Step 1: Build the specialized GARP Message payload
#     // Both sender and target fields match the local interface details
#     GARP_Payload = Build_ARP_Message(
#         Opcode = 2,                             // Force Operation Code 2 (Reply)
#         Src_MAC = Interface.Physical_MAC,       // Local hardware address
#         Src_IP  = Interface.Logical_IP,         // Local protocol address
#         Dest_IP = Interface.Logical_IP,         // Target IP matches Sender IP (Unsolicited)
#         Dest_MAC = "FF:FF:FF:FF:FF:FF"           // Target MAC is set to broadcast or ignored
#     )
#
#     // Step 2: Encapsulate into an Ethernet frame destined for EVERYONE
#     Ethernet_Frame = Package_For_Wire(
#         ARP_Payload = GARP_Payload,
#         Local_MAC = Interface.Physical_MAC,
#         L2_Destination_MAC = "FF:FF:FF:FF:FF:FF" // Broadcast Layer 2 delivery
#     )
#
#     // Step 3: Send onto the segment
#     TRANSMIT_BROADCAST_ON_WIRE(Ethernet_Frame)
#     PRINT "[DEBUG GARP] Unsolicited ARP Reply transmitted successfully."
# ENDFUNCTION

# FUNCTION Process_Incoming_GARP(Local_Host, Received_GARP_Frame):
#     Payload = Received_GARP_Frame.Data_Payload
#
#     // Safety Loop Check: Did I send this myself?
#     IF Payload.Sender_Hardware_Addr == Local_Host.MAC THEN
#         RETURN // Ignore loopback broadcast
#     ENDIF
#
#     // Use Case Verification 1: Duplicate IP Address Detection (ACD)
#     IF Payload.Sender_Protocol_Addr == Local_Host.IP THEN
#         LOG_CRITICAL_ERROR("IP Address Conflict Detected for: " + Local_Host.IP)
#         SEND_CONSOLE_ALERT("MAC conflict: " + Payload.Sender_Hardware_Addr)
#         RETURN
#     ENDIF
#
#     // Use Case Verification 2: Cache Update / MAC Flapping Remediation
#     IF Payload.Sender_Protocol_Addr EXISTS IN Local_Host.ARP_Cache THEN
#         // Dynamically update old cached MAC address with the newly announced MAC
#         Old_MAC = Local_Host.ARP_Cache[Payload.Sender_Protocol_Addr].MAC_Address
#
#         IF Old_MAC != Payload.Sender_Hardware_Addr THEN
#             Local_Host.ARP_Cache[Payload.Sender_Protocol_Addr].MAC_Address = Payload.Sender_Hardware_Addr
#             PRINT "[DEBUG GARP] Dynamically updated cache mapping for " + Payload.Sender_Protocol_Addr
#         ENDIF
#     ENDIF
# ENDFUNCTION

# # 1. PRIMARY DEVICE FAILS, ACCELERATED HA EVENTS TRIGGERED
# [SYSTEM LOG] HSRP Active Router State Transition: Standby -> Active
#
# # 2. GARP PACKET CAPTURE ON THE LOCAL WIRE
# Frame 42: 64 bytes on wire
#     Ethernet II, Src: 00:00:0c:07:ac:01 (Virtual HA MAC), Dst: ff:ff:ff:ff:ff:ff
#         EtherType: 0x0806 (ARP)
#     Address Resolution Protocol (reply/unsolicited)
#         Hardware type: Ethernet (1)
#         Protocol type: IPv4 (0x0800)
#         Opcode: reply (2)
#         Sender MAC address: 00:00:0c:07:ac:01 (192.168.1.1)
#         Target MAC address: ff:ff:ff:ff:ff:ff (192.168.1.1)
#
# # 3. INTERMEDIATE LAYERS DYNAMIC TABLE FLUSH
# [DEBUG GARP] Network endpoints notified. Switch CAM table mappings updated to new physical port interface.
# 6) Gratuitous ARP















================================================================================
LAYER 3 & LAYER 2 NETWORK AUTOMATION MASTER FRAMEWORK
================================================================================

[STEP 1: LAYER 3 LOGICAL ADDRESSING & SUBMISSION]
--------------------------------------------------------------------------------
CONCEPT: End-to-end logical addressing from source host to destination IP.

IF (source_ip AND subnet_mask) == (destination_ip AND subnet_mask) THEN
    Next_Hop_IP = destination_ip          // Delivered locally on same segment
ELSE
    Next_Hop_IP = default_gateway_ip      // Forwarded to next hop router
ENDIF

PASS DOWN TO STEP 2 -> Resolve_L3_To_L2(Next_Hop_IP)


[STEP 2: THE ARP BRIDGE]
--------------------------------------------------------------------------------
CONCEPT: Map a known L3 address to an unknown 48-bit L2 hardware address.

FUNCTION Resolve_L3_To_L2(Next_Hop_IP, ARP_Cache):
    IF Next_Hop_IP EXISTS IN ARP_Cache THEN
        RETURN ARP_Cache[Next_Hop_IP]     // Use known hardware address
    ELSE
        BROADCAST_ARP_REQUEST("FF:FF:FF:FF:FF:FF" for Next_Hop_IP)
        ARP_Reply = WAIT_FOR_REPLY()
        ARP_Cache[Next_Hop_IP] = ARP_Reply.Sender_MAC
        RETURN ARP_Reply.Sender_MAC       // Learned L2 address mapped
    ENDIF
ENDFUNCTION


[STEP 3: LAYER 2 PHYSICAL DELIVERY]
--------------------------------------------------------------------------------
CONCEPT: Physical address passes the packet to the next hop on the local wire.

FUNCTION Layer2_Physical_Delivery(Packet, Target_MAC):
    Frame = ENCAPSULATE_LAYER2(Packet, Destination_MAC = Target_MAC)
    TRANSMIT_ON_PHYSICAL_WIRE(Frame)
ENDFUNCTION
================================================================================


