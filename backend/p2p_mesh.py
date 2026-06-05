#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import json
import hashlib
import time
import random
from ecdsa import SigningKey, VerifyingKey, SECP256k1

class SovereignMeshNode:
    def __init__(self, host='0.0.0.0', port=6000):
        self.host = host
        self.port = port
        self.peers = []             # Active socket connections
        self.graph_vertices = {}    # Local DAG State Storage
        
        # Generate session identity keys (SECP256k1 Curve)
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.verifying_key
        self.wallet_address = f"SOV_{hashlib.sha256(self.public_key.to_string()).hexdigest()[:20]}"
        
        # Start TCP listening server
        server_thread = threading.Thread(target=self.start_listening, daemon=True)
        server_thread.start()
        print(f"[\033[92m+\033[0m] P2P Mesh Node online.")
        print(f"[\033[92m+\033[0m] Local Node Wallet: \033[93m{self.wallet_address}\033[0m")
        print(f"[\033[92m+\033[0m] Listening for network peers on port: {self.port}")

    def start_listening(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)
        
        while True:
            try:
                conn, addr = server_socket.accept()
                self.peers.append(conn)
                print(f"\n[\033[94m>\033[0m] Inbound connection established from secure peer {addr[0]}:{addr[1]}")
                threading.Thread(target=self.handle_peer, args=(conn, addr), daemon=True).start()
            except Exception as e:
                print(f"[\033[91mX\033[0m] Server accept exception: {e}")

    def connect_to_peer(self, peer_ip, peer_port):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer_ip, int(peer_port)))
            self.peers.append(peer_socket)
            print(f"[\033[92m✓\033[0m] Mapped edge to peer mesh at {peer_ip}:{peer_port}")
            threading.Thread(target=self.handle_peer, args=(peer_socket, (peer_ip, peer_port)), daemon=True).start()
        except Exception as e:
            print(f"[\033[91mX\033[0m] Connection to peer failed: {e}")

    def verify_vertex_signature(self, payload):
        """Cryptographically validates the sender's signature over the vertex contents."""
        try:
            sender_pub_hex = payload.get("public_key")
            signature_hex = payload.get("signature")
            
            # Reconstruct signed message base data (sans signature tracking components)
            base_data = {
                "sender": payload.get("sender"),
                "recipient": payload.get("recipient"),
                "amount": payload.get("amount"),
                "timestamp": payload.get("timestamp"),
                "parents": payload.get("parents")
            }
            message_bytes = json.dumps(base_data, sort_keys=True).encode('utf-8')
            
            # ECDSA Verification Math Execution
            vk = VerifyingKey.from_string(bytes.fromhex(sender_pub_hex), curve=SECP256k1)
            return vk.verify(bytes.fromhex(signature_hex), message_bytes)
        except:
            return False

    def handle_peer(self, conn, addr):
        while True:
            try:
                data = conn.recv(16384)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                if message.get("type") == "VERTEX_BROADCAST":
                    v_hash = message.get("hash")
                    payload = message.get("payload")
                    
                    if v_hash not in self.graph_vertices:
                        # 1. SECURITY FILTER: Drop fake signatures instantly
                        if not self.verify_vertex_signature(payload):
                            print(f"\n\033[91m[⚠️ SECURITY ALERT] Vertex [{v_hash[:12]}] failed ECDSA verification!\033[0m")
                            continue
                            
                        # 2. CONSENSUS FILTER: Enforce Proof-of-Work (Target: 4 Zeros)
                        if not v_hash.startswith('0000'):
                            print(f"\n\033[91m[⚠️ SPAM ALERT] Vertex [{v_hash[:12]}] rejected. Insufficient CPU work.\033[0m")
                            continue

                        # 3. ANTI-FORGERY FILTER: Verify hash computation
                        recalc_string = json.dumps(payload, sort_keys=True)
                        if hashlib.sha256(recalc_string.encode('utf-8')).hexdigest() != v_hash:
                            print(f"\n\033[91m[⚠️ DATA FORGERY] Vertex hash structure mismatch!\033[0m")
                            continue

                        print(f"\n[\033[96mDAG\033[0m] Vertex [{v_hash[:12]}...] verified cryptographically. CPU Work Valid. Syncing graph state.")
                        self.graph_vertices[v_hash] = payload
                        self.broadcast_vertex(payload, exclude_conn=conn, auto_sign=False)

            except:
                break
                
        if conn in self.peers:
            self.peers.remove(conn)
        print(f"\n[\033[93m!\033[0m] Connection with peer {addr[0]} disconnected.")

    def broadcast_vertex(self, payload, exclude_conn=None, auto_sign=True):
        """Assembles edges, signs payload, performs CPU PoW mining, and floods the network."""
        if auto_sign:
            existing_hashes = list(self.graph_vertices.keys())
            parents = random.sample(existing_hashes, min(2, len(existing_hashes))) if existing_hashes else ["GENESIS_VERTEX"]
            payload["parents"] = parents
            
            # Core Signatures Engine
            message_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
            signature = self.private_key.sign(message_bytes)
            
            payload["public_key"] = self.public_key.to_string().hex()
            payload["signature"] = signature.hex()

            # --- TRUE PROOF OF WORK (MINING) ---
            print("\n[\033[93mMINING\033[0m] CPU engaging cryptographic Proof-of-Work (Target: 0000...)")
            nonce = 0
            start_time = time.time()
            
            while True:
                payload["nonce"] = nonce
                vertex_string = json.dumps(payload, sort_keys=True)
                v_hash = hashlib.sha256(vertex_string.encode('utf-8')).hexdigest()
                
                # Check if hash meets the difficulty target (4 leading zeros)
                if v_hash.startswith('0000'):
                    elapsed = time.time() - start_time
                    print(f"[\033[92mSUCCESS\033[0m] Mathematical vertex sealed in {elapsed:.2f}s: [{v_hash[:16]}...]")
                    break
                nonce += 1
        else:
            # If we are just forwarding another node's already-mined data
            vertex_string = json.dumps(payload, sort_keys=True)
            v_hash = hashlib.sha256(vertex_string.encode('utf-8')).hexdigest()

        self.graph_vertices[v_hash] = payload
        
        message = json.dumps({
            "type": "VERTEX_BROADCAST",
            "hash": v_hash,
            "payload": payload
        })
        
        for peer in self.peers:
            if peer != exclude_conn:
                try:
                    peer.sendall(message.encode('utf-8'))
                except:
                    pass


if __name__ == '__main__':
    print("="*65)
    print("\033[91m   SOVEREIGN LAYER-0: ECDSA SECURED P2P ENGINE   \033[0m")
    print("="*65)
    
    bind_port = input("[CONFIG] Enter port to bind node (Default 6000): ").strip()
    bind_port = int(bind_port) if bind_port else 6000
    
    node = SovereignMeshNode(port=bind_port)
    time.sleep(0.5)
    
    while True:
        print("\n\033[95m[1]\033[0m Connect to Peer Node")
        print("\033[95m[2]\033[0m Broadcast Secure Transaction Vertex")
        print("\033[95m[3]\033[0m View Local Graph State (DAG)")
        choice = input(">> ").strip()
        
        if choice == '1':
            ip = input("Peer IP: ")
            p_port = input("Peer Port: ")
            node.connect_to_peer(ip, p_port)
        elif choice == '2':
            recipient = input("Recipient Wallet Address: ").strip()
            amount = input("Amount to Transfer: ").strip()
            if recipient and amount:
                payload = {
                    "sender": node.wallet_address,
                    "recipient": recipient,
                    "amount": float(amount),
                    "timestamp": time.time()
                }
                node.broadcast_vertex(payload)
                print("[\033[92m✓\033[0m] Transaction signed, verified locally, and broadcasted.")
        elif choice == '3':
            print(f"\n--- ACTIVE GRAPH TOPOLOGY: {len(node.graph_vertices)} VERTICES ---")
            print(json.dumps(node.graph_vertices, indent=2))
