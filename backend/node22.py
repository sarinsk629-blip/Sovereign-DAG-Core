#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import time
import socket
import threading

def handle_peer(client_socket, address):
    print(f"\n[🌍] INCOMING CONNECTION FROM: {address}")
    client_socket.send(b"Welcome to the Sovereign DAG. Genesis Node Active.\n")
    
    # 1. Send the challenge
    challenge_string = "DAG_Auth_Strike"
    client_socket.send(f"CHALLENGE:{challenge_string}\n".encode('utf-8'))
    
    try:
        # 2. Wait for Chidibless's terminal to send the solution
        client_socket.settimeout(15.0) # Give him 15 seconds to solve it
        response = client_socket.recv(1024).decode('utf-8').strip()
        print(f"[*] Received Nonce from Peer: {response}")
        
        # 3. Mathematically verify his answer
        payload = f"{challenge_string}{response}".encode('utf-8')
        hash_result = hashlib.sha256(payload).hexdigest()
        
        if hash_result.startswith("0000"):
            print(f"[✅] ACCESS GRANTED. Valid Hash: {hash_result}")
            client_socket.send(b"ACCESS GRANTED. YOU ARE NOW SYNCHRONIZED TO THE NETWORK.\n")
            # In the future, this is where you would sync the ledger data
        else:
            print(f"[❌] ACCESS DENIED. Invalid Hash.")
            client_socket.send(b"ACCESS DENIED. INVALID HASH PHYSICS.\n")
            
    except socket.timeout:
        print("[!] Peer took too long to solve the PoW. Dropping connection.")
    except Exception as e:
        print(f"[!] Connection Error: {e}")
        
    client_socket.close()
    print(f"[-] Connection closed securely.")

def start_tcp_server(host='0.0.0.0', port=8888):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"\n[🏛️] GENESIS NODE V2 ACTIVE.")
        print(f"[📡] Listening for global P2P connections on Port {port}...")
        
        while True:
            client_sock, addr = server.accept()
            peer_thread = threading.Thread(target=handle_peer, args=(client_sock, addr))
            peer_thread.start()
    except KeyboardInterrupt:
        server.close()

if __name__ == "__main__":
    start_tcp_server()
