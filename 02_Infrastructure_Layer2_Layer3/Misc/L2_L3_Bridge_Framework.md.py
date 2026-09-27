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
