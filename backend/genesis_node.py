#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 ⚖️ THE GENESIS NODE V1.0 — DAG P2P PROTOCOL ⚖️
 =====================================================================
 Component 1: Micro-Proof-of-Work (Sybil Attack Prevention)
 Component 2: Raw TCP Socket Listener (Peer-to-Peer Communication)
 =====================================================================
"""

import hashlib
import time
import socket
import threading

# --- 1. THE PHYSICS ENGINE (Micro-PoW) ---
def micro_pow(challenge: str, difficulty: int = 4):
    """
    Forces a connecting node to spend computational energy solving a hash.
    A difficulty of 4 requires finding a hash starting with '0000'.
    """
    print(f"\n[⚡] Initiating Micro-PoW...")
    print(f"[⚡] Target Difficulty: {difficulty} Zeros")
    
    prefix = "0" * difficulty
    nonce = 0
    start_time = time.time()
    
    while True:
        # We hash the challenge string combined with a guessing number (nonce)
        payload = f"{challenge}{nonce}".encode('utf-8')
        hash_result = hashlib.sha256(payload).hexdigest()
        
        if hash_result.startswith(prefix):
            elapsed = time.time() - start_time
            print(f"[✅] PoW Solved in {elapsed:.4f} seconds!")
            print(f"     Nonce: {nonce}")
            print(f"     Hash:  {hash_result}")
            return nonce, hash_result
        
        nonce += 1

# --- 2. THE P2P BRIDGE (Socket Listener) ---
def handle_peer(client_socket, address):
    print(f"\n[🌍] INCOMING CONNECTION DETECTED FROM: {address}")
    client_socket.send(b"Welcome to the Genesis Node. Identify yourself.\n")
    
    # Simulating a required handshake
    client_socket.send(b"Solve Micro-PoW to enter the network...\n")
    time.sleep(1)
    
    client_socket.close()
    print(f"[-] Connection with {address} closed securely.")

def start_tcp_server(host='0.0.0.0', port=8888):
    """Opens the raw port to listen for global connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"\n[🏛️] GENESIS NODE ACTIVE.")
        print(f"[📡] Listening for global P2P connections on Port {port}...")
        
        while True:
            client_sock, addr = server.accept()
            # Handle each new connection in a separate background thread
            peer_thread = threading.Thread(target=handle_peer, args=(client_sock, addr))
            peer_thread.start()
            
    except KeyboardInterrupt:
        print("\n[!] Shutting down Genesis Node.")
        server.close()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("="*50)
    print(" ⚖️ INITIALIZING SOVEREIGN DAG ARCHITECTURE ⚖️")
    print("="*50)
    
    # Test the CPU physics locally first
    test_challenge = "Genesis_Block_West_Bengal"
    micro_pow(test_challenge, difficulty=4)
    
    # Open the network
    start_tcp_server()
