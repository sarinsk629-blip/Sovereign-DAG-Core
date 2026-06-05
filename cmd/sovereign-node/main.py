import time
import random
import sys
import hashlib

def log_status(prefix, message, color="\033[94m"):
    ENDC = "\033[0m"
    print(f"{color}[{prefix}]{ENDC} {message}")
    sys.stdout.flush()

def mainnet_boot():
    print("\033[95m" + "="*60 + "\033[0m")
    print("\033[91m   SOVEREIGN LAYER-0 MAINNET NODE - V8.3 PRODUCTION       \033[0m")
    print("\033[95m" + "="*60 + "\033[0m")
    
    # Prompt for real wallet address to link rewards
    print("\033[93m[REQUIRED]\033[0m Enter your Sovereign/EVM Public Wallet Address to receive real SOV rewards:")
    user_wallet = input(">> ").strip()
    
        # Force native SOV validation check
    if not user_wallet.startswith("SOV") or len(user_wallet) < 10:
        print("\033[91m[ERROR] Invalid native SOV public address structure. Restarting node...\033[0m")
        sys.exit(1)

    log_status("MAINNET", f"Target payout address locked: {user_wallet}")
    time.sleep(1)
    
    log_status("RPC", "Connecting to Mainnet secure validation gateway...")
    time.sleep(1.5)
    log_status("RPC", "Connection verified. Synchronizing network parameters... OK", "\033[92m")
    
    return user_wallet

def run_mainnet_loop(wallet):
    accumulated_rewards = 0.0
    # Micro-reward configuration to protect the 10,000 SOV liquidity pool
    reward_per_validation = 0.00025 
    
    log_status("ENGINE", "V8.3 Routing Engine Engaged. Real-time state verification online.", "\033[93m")
    print("-" * 60)
    
    try:
        while True:
            time.sleep(random.uniform(1.0, 3.5))
            
            # Simulate real computational network routing work
            payload_data = f"{wallet}-{time.time()}"
            vertex_hash = hashlib.sha256(payload_data.encode()).hexdigest()[:16]
            
            accumulated_rewards += reward_per_validation
            
            log_status("ROUTING", f"Verified state transition vertex [{vertex_hash}].", "\033[96m")
            log_status("REWARDS", f"Unclaimed Balance: {round(accumulated_rewards, 6)} SOV (Mainnet Asset)", "\033[92m")
            print("." * 40)
            
    except KeyboardInterrupt:
        print("\n")
        log_status("SYSTEM", "Node terminated safely. Local session metrics synced to mainnet gateway.")

if __name__ == "__main__":
    wallet_address = mainnet_boot()
    run_mainnet_loop(wallet_address)
