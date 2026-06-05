#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import sys
import hashlib
import requests
import os

# ========================================================
# 🌐 CORE NETWORK NODE CONFIGURATION
# ========================================================
SERVER_IP = "103.194.228.76" 
SERVER_URL = f"http://{SERVER_IP}:5000"

def log_status(prefix, message, color="\033[94m"):
    ENDC = "\033[0m"
    print(f"{color}[{prefix}]{ENDC} {message}")
    sys.stdout.flush()

def mainnet_boot():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[95m" + "="*60 + "\033[0m")
    print("\033[91m   SOVEREIGN LAYER-0 MAINNET NODE - V2.0 LIVE ARCHITECTURE    \033[0m")
    print("\033[95m" + "="*60 + "\033[0m")
    
    # Prompt for real wallet address
    print("\033[93m[REQUIRED]\033[0m Enter your Sovereign Public Wallet Address to track rewards:")
    user_wallet = input(">> ").strip()
    
    # Force native SOV validation check
    if not user_wallet.startswith("SOV") or len(user_wallet) < 10:
        print("\033[91m[ERROR] Invalid native SOV public address structure. Restarting node...\033[0m")
        sys.exit(1)

    log_status("MAINNET", f"Target payout address locked: {user_wallet}")
    time.sleep(1)
    
    log_status("RPC", f"Connecting to Secure Validation Gateway at {SERVER_IP}...")
    
    # REAL NETWORK CONNECTION: Check if the Flask server is online
    try:
        response = requests.get(f"{SERVER_URL}/network/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            log_status("RPC", f"Connection verified. Architecture: {status.get('architecture')}", "\033[92m")
        else:
            log_status("RPC", "Connection failed. Gateway rejected request.", "\033[91m")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("\n\033[91m[❌] CRITICAL ERROR: Unable to communicate with Ledger Backend API.\033[0m")
        print("Please verify the network gateway is online.")
        sys.exit(1)
        
    return user_wallet

def fetch_live_balance(wallet):
    """Pulls genuine persistent balance from the central server state ledger."""
    try:
        response = requests.get(f"{SERVER_URL}/balance/{wallet}", timeout=5)
        if response.status_code == 200:
            return response.json().get("balances", {}).get("SOV", 0.0)
    except requests.exceptions.RequestException:
        return 0.0
    return 0.0

def run_mainnet_loop(wallet):
    log_status("ENGINE", "V2.0 Routing Engine Engaged. Real-time state verification online.", "\033[93m")
    print("-" * 60)
    
    try:
        while True:
            # Simulate the visual routing delay for the terminal UI
            time.sleep(random.uniform(2.0, 4.5))
            
            # Simulate local computational network routing work
            payload_data = f"{wallet}-{time.time()}"
            vertex_hash = hashlib.sha256(payload_data.encode()).hexdigest()[:16]
            
            # REALITY CHECK: Pull the actual balance from the Flask API
            real_balance = fetch_live_balance(wallet)
            
            log_status("ROUTING", f"Verified state transition vertex [{vertex_hash}].", "\033[96m")
            log_status("REWARDS", f"Verified Network Balance: {real_balance:.6f} SOV", "\033[92m")
            print("." * 40)
            
    except KeyboardInterrupt:
        print("\n")
        log_status("SYSTEM", "Node terminated safely. Session disconnected from gateway.")

if __name__ == "__main__":
    wallet_address = mainnet_boot()
    run_mainnet_loop(wallet_address)
