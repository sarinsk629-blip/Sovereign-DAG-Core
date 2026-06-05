#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import json
import time

class SovereignDAG:
    def __init__(self, genesis_address: str, total_supply: float):
        self.transactions = {}  # The Spiderweb (DAG history)
        self.balances = {}      # The State Ledger (Who owns what)
        self.genesis_address = genesis_address
        self.total_supply = total_supply
        
        self._mint_genesis_vertex()

    def _mint_genesis_vertex(self):
        """Creates the center of the DAG web and funds the network treasury."""
        print(f"[⚡] INITIATING GENESIS PROTOCOL...")
        time.sleep(1)
        
        # The Genesis Transaction
        genesis_tx = {
            "sender": "0x0000000000000000000000000000000000000000", # The Void
            "receiver": self.genesis_address,
            "amount": self.total_supply,
            "timestamp": time.time(),
            "parents": [] # No parents. It is the beginning of time.
        }
        
        # Cryptographically hash the transaction to create its ID
        tx_string = json.dumps(genesis_tx, sort_keys=True).encode('utf-8')
        tx_id = hashlib.sha256(tx_string).hexdigest()
        
        # Lock it into the State Ledger
        self.transactions[tx_id] = genesis_tx
        self.balances[self.genesis_address] = self.total_supply
        
        print(f"[✅] GENESIS VERTEX FORGED. Web ID: {tx_id[:16]}...")
        print(f"[🏦] NETWORK TREASURY FULLY FUNDED.\n")

    def get_balance(self, address: str):
        """Queries the ledger for an address's holdings."""
        return self.balances.get(address, 0.0)

# ==============================================================================
# MAIN EXECUTION: DEPLOYING THE ECONOMY
# ==============================================================================
if __name__ == "__main__":
    print("="*60)
    print(" ⚖️ SOVEREIGN DAG STATE LEDGER V1.0 ⚖️")
    print("="*60)
    
    # YOUR EXACT GENESIS WALLET ADDRESS
    treasury_address = "11JKJ9fhyUUdWy7kcfo3sbF88KDcZ1mfvpD"
    
    # Total Supply: 100 Billion Coins (For Micro-Economy Scaling)
    MAX_SUPPLY = 100000000000.0 
    
    # Ignite the Ledger
    dag_network = SovereignDAG(genesis_address=treasury_address, total_supply=MAX_SUPPLY)
    
    # Read the current reality of the network
    print("📊 CURRENT NETWORK STATE:")
    print(f"Address : {treasury_address}")
    print(f"Balance : {dag_network.get_balance(treasury_address):,.2f} COINS")
    print("="*60)
