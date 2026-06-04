import time
import random
import sys
import hashlib
import uuid

def log_status(prefix, message, color="\033[94m"):
    # Clear formatting code constant
    ENDC = "\033[0m"
    print(f"{color}[{prefix}]{ENDC} {message}")
    sys.stdout.flush()

def generate_vertex_hash(parent_hashes, internal_data):
    payload = "".join(parent_hashes) + str(internal_data) + str(time.time())
    return hashlib.sha256(payload.encode()).hexdigest()[:16]

def boot_sequence():
    print("\033[95m" + "="*60 + "\033[0m")
    print("\033[92m   SOVEREIGN LAYER-0 DECENTRALIZED DIRECTED ACYCLIC GRAPH \033[0m")
    print("\033[92m               CORE ENGINE - ALPHA VERSION 8.3            \033[0m")
    print("\033[95m" + "="*60 + "\033[0m")
    time.sleep(1)
    
    node_id = str(uuid.uuid4())[:8]
    log_status("SYSTEM", f"Initializing localized workspace components... OK")
    log_status("SYSTEM", f"Assigned Node Operational Identity: [SOV-NODE-{node_id.upper()}]")
    time.sleep(0.8)
    
    log_status("ENGINE", "Loading V8.3 automated routing protocol weights...", "\033[93m")
    time.sleep(1.2)
    log_status("ENGINE", "V8.3 Risk mitigation layers and transaction validation matrices active.", "\033[93m")
    
    log_status("NETWORK", "Scanning for bootstrap seed-nodes on peer matrix...")
    time.sleep(1.5)
    peers = [f"192.168.1.{random.randint(10,254)}:8080" for _ in range(3)]
    log_status("NETWORK", f"Connected to {len(peers)} validation peers: {', '.join(peers)}")
    time.sleep(1)
    
    log_status("DAG", "Syncing ledger topology from genesis vertex...", "\033[92m")
    time.sleep(1.5)
    return node_id

def execute_node_loop(node_id):
    known_vertices = ["0000a1b2c3d4e5f6"]
    accumulated_sov = 0.0
    
    log_status("DAG", "Asynchronous network processing loop initiated. Mining fair-share vertices.", "\033[92m")
    print("-" * 60)
    
    try:
        while True:
            time.sleep(random.uniform(0.5, 2.0))
            
            # Simulate processing incoming transactions via graph routing
            tx_count = random.randint(5, 35)
            parents = random.sample(known_vertices, min(len(known_vertices), 2))
            
            # Generate new vertex in the graph
            new_vertex = generate_vertex_hash(parents, tx_count)
            known_vertices.append(new_vertex)
            
            # Keep memory bounds clean in simulation
            if len(known_vertices) > 20:
                known_vertices.pop(0)
                
            # Earn simulated SOV allocation tokens
            fee_earned = round(tx_count * 0.0043, 5)
            accumulated_sov += fee_earned
            
            # Output operational telemetry metrics
            log_status(
                "VERIFICATION", 
                f"Vertex [{new_vertex}] forged. Parents: {parents}. Validated {tx_count} txs.", 
                "\033[96m"
            )
            log_status(
                "BALANCES", 
                f"Total Rewards Earned: {round(accumulated_sov, 5)} SOV | Yield Allocation: Stable", 
                "\033[92m"
            )
            print("." * 40)
            
    except KeyboardInterrupt:
        print("\n")
        log_status("SYSTEM", "Shutdown signal detected. Gracefully closing vertex consensus channels.")
        log_status("SYSTEM", "Node state successfully serialized to local storage disk. Offline.")

if __name__ == "__main__":
    nid = boot_sequence()
    execute_node_loop(nid)
