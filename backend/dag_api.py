#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flask_cors import CORS
import ecdsa
import hashlib
import json
import time
import os
from ecdsa.util import sigdecode_der

# Core Architecture Modules
from sovereign_vm import execute_smart_contract
from state_storage import load_ledger_state, save_ledger_state, load_tx_history, log_transaction
from txid_forge import generate_txid
from p2p_mesh import SovereignMeshNode

app = Flask(__name__)
CORS(app)

# ==========================================
# 🌐 SOVEREIGN MAINNET (ULTRA INTEGRATED V3.0)
# ==========================================

MAINNET_GENESIS = {
    "SOVb1dab6f1a43527d5cc9296f4391e33a009": {"SOV": 100000000.0}, # CENTRAL RESERVE
    "SOV_Deployer_Node": {"SOV": 5000.0},
    "SOV_BURN_VAULT": {"SOV": 0.0}                                # The Black Hole
}

print("[\033[93mBOOT\033[0m] Initializing Sovereign Layer-0 P2P Mesh Baseline...")
# Instantiating P2P Node on Port 6000. This auto-generates layer0_node.wallet_address,
# layer0_node.private_key, and layer0_node.public_key natively.
layer0_node = SovereignMeshNode(port=6000)

print("[\033[93mBOOT\033[0m] Loading Persistent Ledger Snapshots...")
network_state = load_ledger_state(MAINNET_GENESIS)

def verify_signature(public_key_hex, signature_hex, tx_data):
    """Validates transaction authenticity using curve SECP256k1 over DER structures."""
    try:
        if public_key_hex.startswith('04'):
            public_key_bytes = bytes.fromhex(public_key_hex)[1:]
        else:
            public_key_bytes = bytes.fromhex(public_key_hex)
            
        public_key = ecdsa.VerifyingKey.from_string(public_key_bytes, curve=ecdsa.SECP256k1)
        tx_string = json.dumps(tx_data, sort_keys=True)
        return public_key.verify(
            bytes.fromhex(signature_hex), 
            tx_string.encode('utf-8'), 
            hashfunc=hashlib.sha256, 
            sigdecode=sigdecode_der
        )
    except:
        return False

def sync_p2p_graph_to_state():
    """Traverses uncommitted P2P graph vertices to dynamically calculate state mutations."""
    for v_hash, payload in list(layer0_node.graph_vertices.items()):
        # Avoid processing network-level structural fields as asset tickers
        sender = payload.get("sender")
        recipient = payload.get("recipient") or payload.get("receiver")
        amount = float(payload.get("amount", 0))
        ticker = payload.get("ticker", "SOV").upper()
        tx_type = payload.get("type", "TRANSFER")

        # Skip processing if vertex records represent standard internal metrics
        if not sender or not recipient or amount <= 0:
            continue

        # Process standard mutations inside memory pool if not already written
        if tx_type == "TRANSFER":
            if sender in network_state and network_state[sender].get(ticker, 0.0) >= amount:
                if recipient not in network_state:
                    network_state[recipient] = {}
                if ticker not in network_state[recipient]:
                    network_state[recipient][ticker] = 0.0
                
                network_state[sender][ticker] -= amount
                network_state[recipient][ticker] += amount

# --- ROUTE 1: GLOBAL NETWORK RADAR ---
@app.route('/network/status', methods=['GET'])
def get_status():
    sync_p2p_graph_to_state()
    return jsonify({
        "status": "SECURE", 
        "architecture": "RPC_GATEWAY_V3.0_PROD", 
        "burn_vault": network_state.get("SOV_BURN_VAULT", {}).get("SOV", 0.0),
        "mesh_peers_connected": len(layer0_node.peers),
        "total_vertices_in_dag": len(layer0_node.graph_vertices),
        "rpc_wallet_identity": layer0_node.wallet_address
    })

# --- ROUTE 2: UNIFIED LEDGER EXPLORER ---
@app.route('/balance/<wallet>', methods=['GET'])
def get_balance(wallet):
    sync_p2p_graph_to_state()
    if wallet not in network_state:
        return jsonify({"balances": {"SOV": 0.0}})

    clean_balances = {}
    for key, value in network_state[wallet].items():
        if key not in ["faucet_claimed", "ip_logs"]:
            clean_balances[key] = value

    return jsonify({"balances": clean_balances})

# --- ROUTE 3: SPAM-RESISTANT PROOF-OF-WORK FAUCET ---
@app.route('/faucet/<wallet>', methods=['POST'])
def faucet(wallet):
    genesis_address = "SOVb1dab6f1a43527d5cc9296f4391e33a009"
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)

    if wallet not in network_state:
        network_state[wallet] = {"SOV": 0.0}

    if network_state[wallet].get("faucet_claimed", False):
        return jsonify({"status": "FAILED", "reason": "Address already funded via active ledger allocations."}), 400

    if "global_ip_logs" not in network_state:
        network_state["global_ip_logs"] = {}

    if network_state["global_ip_logs"].get(client_ip, False):
        return jsonify({"status": "FAILED", "reason": "Your physical device has already claimed an iteration allocation."}), 400

    # Assemble structured execution payload
    payload = {
        "type": "FAUCET_DISPENSE",
        "sender": genesis_address,
        "recipient": wallet,
        "amount": 1.0,
        "ticker": "SOV",
        "timestamp": time.time()
    }

    print(f"\n[\033[95mRPC\033[0m] Processing faucet request for {wallet}. Routing through PoW Engine...")
    # Route via auto-signature because faucet triggers directly from backend system identity
    layer0_node.broadcast_vertex(payload, auto_sign=True)

    # Mutate locally to ensure instantaneous response times
    network_state[genesis_address]["SOV"] -= 1.0
    network_state[wallet]["SOV"] += 1.0
    network_state[wallet]["faucet_claimed"] = True
    network_state["global_ip_logs"][client_ip] = True

    txid = generate_txid("FAUCET_SYSTEM", wallet, 1.0, "SYSTEM_AUTO_SIG")
    save_ledger_state(network_state)
    log_transaction(txid, payload)

    return jsonify({"status": "SUCCESS", "message": "1.0 SOV Mined and Dispensed successfully.", "txid": txid})

# --- ROUTE 4: P2P TRANSFER (ECDSA + WORK PROOF ENFORCED) ---
@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json
    sender = data.get('sender')
    recipient = data.get('recipient')
    amount = float(data.get('amount'))
    ticker = data.get('ticker', 'SOV').upper()
    public_key = data.get('public_key')
    signature = data.get('signature')

    # 1. Validation check over standard structures
    tx_data = {"sender": sender, "recipient": recipient, "amount": amount, "ticker": ticker}
    if not verify_signature(public_key, signature, tx_data):
        return jsonify({"status": "FAILED", "reason": "SECURITY ALERT: Cryptographic Signature Invalid."}), 401

    # 2. State verification checks
    if sender not in network_state or network_state.get(sender, {}).get(ticker, 0.0) < amount:
        return jsonify({"status": "FAILED", "reason": f"Insufficient {ticker} balance context."}), 400

    # 3. Compile structural vertex components
    payload = {
        "type": "TRANSFER",
        "sender": sender,
        "recipient": recipient,
        "amount": amount,
        "ticker": ticker,
        "public_key": public_key,
        "signature": signature,
        "timestamp": time.time()
    }

    print(f"\n[\033[95mRPC\033[0m] Inbound transaction valid. Commencing local network graph mining...")
    # Pass transaction payload to the mesh node with auto_sign=False,
    # preserving the original sender's cryptographic signature
    layer0_node.broadcast_vertex(payload, auto_sign=False)

    # 4. Mutate tracking maps
    if recipient not in network_state:
        network_state[recipient] = {}
    if ticker not in network_state[recipient]:
        network_state[recipient][ticker] = 0.0

    network_state[sender][ticker] -= amount
    network_state[recipient][ticker] += amount

    txid = generate_txid("TRANSFER", sender, amount, signature)
    save_ledger_state(network_state)
    log_transaction(txid, tx_data)

    return jsonify({"status": "SUCCESS", "message": f"Successfully mined and broadcasted {amount} {ticker}!", "txid": txid})

# --- ROUTE 5: BLOCK EXPLORER PARSER ---
@app.route('/history', methods=['GET'])
def get_history():
    try:
        if not os.path.exists('dag_tx_history.json'):
            return jsonify({"transactions": []})

        with open('dag_tx_history.json', 'r') as f:
            raw_data = json.load(f)

        history_list = []
        if isinstance(raw_data, dict):
            for txid, details in raw_data.items():
                history_list.append({"txid": txid, "details": details})
        else:
            history_list = raw_data

        return jsonify({"transactions": history_list[::-1]})
    except:
        return jsonify({"transactions": []})

# --- ROUTE 6: AUTOMATED MARKET MAKER PRICING RADAR ---
def initialize_dex_pool():
    genesis_address = "SOVb1dab6f1a43527d5cc9296f4391e33a009"
    if "DEX_POOL" not in network_state:
        initial_sov = 10000.0
        initial_usdt = 100.0

        if genesis_address not in network_state:
            network_state[genesis_address] = {"SOV": 100000000.0}

        network_state[genesis_address]["SOV"] -= initial_sov
        network_state["DEX_POOL"] = {"SOV": initial_sov, "USDT": initial_usdt}

        txid = generate_txid("SYSTEM", "DEX_POOL", initial_sov, "LIQUIDITY_GENESIS")
        log_transaction(txid, {"type": "LIQUIDITY_GENESIS", "sender": genesis_address, "amount": initial_sov})
        save_ledger_state(network_state)

@app.route('/live_price', methods=['GET'])
def live_price():
    initialize_dex_pool()
    current_price = network_state["DEX_POOL"]["USDT"] / network_state["DEX_POOL"]["SOV"]
    return jsonify({
        "price": current_price,
        "pool_sov": network_state["DEX_POOL"]["SOV"],
        "pool_usdt": network_state["DEX_POOL"]["USDT"]
    })

# --- ROUTE 7: INTER-CHAIN AMM ROUTER ---
@app.route('/bridge_deposit', methods=['POST'])
def bridge_deposit():
    data = request.json
    wallet = data.get('wallet')
    usdt_paid = float(data.get('usdt_paid'))
    bsc_tx_hash = data.get('bsc_tx_hash')

    if "used_tx_hashes" not in network_state:
        network_state["used_tx_hashes"] = {}
    if bsc_tx_hash in network_state["used_tx_hashes"]:
        return jsonify({"status": "FAILED", "reason": "Cross-chain footprint already executed."}), 400

    initialize_dex_pool()

    pool_sov = network_state["DEX_POOL"]["SOV"]
    pool_usdt = network_state["DEX_POOL"]["USDT"]
    k = pool_sov * pool_usdt

    new_pool_usdt = pool_usdt + usdt_paid
    new_pool_sov = k / new_pool_usdt
    sov_to_dispense = pool_sov - new_pool_sov

    # Route update action via background network mining mechanics
    payload = {
        "type": "BRIDGE_SWAP",
        "sender": "BSC_CROSSCHAIN_BRIDGE",
        "recipient": wallet,
        "amount": sov_to_dispense,
        "ticker": "SOV",
        "timestamp": time.time()
    }
    layer0_node.broadcast_vertex(payload, auto_sign=True)

    network_state["DEX_POOL"]["USDT"] = new_pool_usdt
    network_state["DEX_POOL"]["SOV"] = new_pool_sov

    if wallet not in network_state:
        network_state[wallet] = {"SOV": 0.0}
    network_state[wallet]["SOV"] += sov_to_dispense
    network_state["used_tx_hashes"][bsc_tx_hash] = True

    txid = generate_txid("AMM_PURCHASE", wallet, sov_to_dispense, "BSC_VERIFIED")
    save_ledger_state(network_state)
    log_transaction(txid, {"type": "AMM_PURCHASE", "usdt_deposited": usdt_paid, "sov_dispensed": sov_to_dispense})

    new_price = new_pool_usdt / new_pool_sov
    return jsonify({"status": "SUCCESS", "message": f"{sov_to_dispense:.2f} SOV secured! New Price Target: ${new_price:.4f}", "txid": txid})

# --- ROUTE 8: RESERVE LIQUIDITY PROVISIONING ---
@app.route('/admin_inject', methods=['POST'])
def admin_inject():
    data = request.json
    wallet = data.get('wallet')
    sov_to_inject = float(data.get('sov_amount', 0))
    genesis_address = "SOVb1dab6f1a43527d5cc9296f4391e33a009"

    if wallet != genesis_address:
        return jsonify({"status": "FAILED", "reason": "SECURITY BREACH: Operations restricted to Central Bank allocations."}), 403

    if network_state.get(genesis_address, {}).get("SOV", 0) < sov_to_inject:
        return jsonify({"status": "FAILED", "reason": "Insufficient balance limits in target allocations."}), 400

    if "DEX_POOL" not in network_state:
        return jsonify({"status": "FAILED", "reason": "Trading Floor mechanics uninitialized."}), 400

    payload = {
        "type": "LIQUIDITY_INJECTION",
        "sender": genesis_address,
        "recipient": "DEX_POOL",
        "amount": sov_to_inject,
        "ticker": "SOV",
        "timestamp": time.time()
    }
    layer0_node.broadcast_vertex(payload, auto_sign=True)

    network_state[genesis_address]["SOV"] -= sov_to_inject
    network_state["DEX_POOL"]["SOV"] += sov_to_inject

    txid = generate_txid("LIQUIDITY_INJECTION", genesis_address, sov_to_inject, data.get('signature', 'SIG_VERIFIED'))
    save_ledger_state(network_state)
    log_transaction(txid, {"type": "LIQUIDITY_INJECTION", "sender": genesis_address, "sov_injected": sov_to_inject})

    new_price = network_state["DEX_POOL"]["USDT"] / network_state["DEX_POOL"]["SOV"]
    return jsonify({"status": "SUCCESS", "message": f"INJECTION SYSTEM LIVE: {sov_to_inject} SOV moved to pool floor. Price Index: ${new_price:.6f}"})

# --- ROUTE 9: LAYER-2 SRC-20 ASSET FACTORY ---
@app.route('/token/mint', methods=['POST'])
def mint_src20():
    data = request.get_json()
    sender = data.get('sender')
    ticker = data.get('ticker').upper()
    supply = float(data.get('supply', 0))
    public_key = data.get('public_key')
    signature = data.get('signature')

    tx_data = {"sender": sender, "ticker": ticker, "supply": supply}
    if not verify_signature(public_key, signature, tx_data):
         return jsonify({"status": "FAILED", "reason": "Cryptographic Verification Mismatch"}), 401

    sender_wallet = network_state.get(sender, {"SOV": 0.0})
    if sender_wallet.get("SOV", 0.0) < 500.0:
        return jsonify({"status": "FAILED", "reason": "Insufficient processing resources. 500.0 SOV required to trigger factory metrics."}), 400

    if ticker in sender_wallet:
        return jsonify({"status": "FAILED", "reason": f"Asset Identifier {ticker} occupies explicit allocations inside target workspace."}), 400

    payload = {
        "type": "SRC20_MINT",
        "sender": sender,
        "recipient": "SRC20_FACTORY",
        "amount": 500.0,
        "ticker": "SOV",
        "mint_ticker": ticker,
        "mint_supply": supply,
        "timestamp": time.time()
    }
    layer0_node.broadcast_vertex(payload, auto_sign=False)

    # Process operations and route burning action through state maps
    sender_wallet["SOV"] -= 500.0
    if "SOV_BURN_VAULT" not in network_state:
        network_state["SOV_BURN_VAULT"] = {"SOV": 0.0}
    network_state["SOV_BURN_VAULT"]["SOV"] += 500.0

    sender_wallet[ticker] = supply
    network_state[sender] = sender_wallet

    txid = generate_txid(sender, "SRC20_FACTORY", 500.0, signature)
    save_ledger_state(network_state)
    log_transaction(txid, {"type": "MINT_SRC20", "sender": sender, "ticker": ticker, "supply": supply, "burned": 500.0})

    return jsonify({"status": "SUCCESS", "message": f"Asset Factory Processing Complete: {supply} {ticker} issued.", "txid": txid})

# --- ROUTE 10: ALTERNATIVE MULTI-ASSET LAYER-1 ROUTER ---
@app.route('/transaction/send', methods=['POST'])
def send_transaction():
    data = request.get_json()
    sender = data.get('sender')
    receiver = data.get('receiver')
    amount = float(data.get('amount', 0))
    ticker = data.get('ticker', 'SOV').upper()
    public_key = data.get('public_key')
    signature = data.get('signature')

    tx_data = {"sender": sender, "receiver": receiver, "amount": amount, "ticker": ticker}
    if not verify_signature(public_key, signature, tx_data):
        return jsonify({"status": "FAILED", "reason": "Cryptographic signature validation failure."}), 401

    if network_state.get(sender, {}).get(ticker, 0.0) < amount:
        return jsonify({"status": "FAILED", "reason": "Insufficient balance metrics over tracking assets."}), 400

    payload = {
        "type": "TRANSFER",
        "sender": sender,
        "recipient": receiver,
        "amount": amount,
        "ticker": ticker,
        "public_key": public_key,
        "signature": signature,
        "timestamp": time.time()
    }
    layer0_node.broadcast_vertex(payload, auto_sign=False)

    network_state[sender][ticker] -= amount
    if receiver not in network_state:
        network_state[receiver] = {}
    network_state[receiver][ticker] = network_state[receiver].get(ticker, 0.0) + amount

    txid = generate_txid(sender, receiver, amount, signature)
    save_ledger_state(network_state)
    log_transaction(txid, {"type": "TRANSFER", "sender": sender, "receiver": receiver, "amount": amount, "ticker": ticker})

    return jsonify({"status": "SUCCESS", "txid": txid})

if __name__ == '__main__':
    print("="*75)
    print("🌐 SOVEREIGN UNIFIED RPC GATEWAY V3.0 - FRONTEND WEB TO P2P MESH BRIDGE ONLINE")
    print("="*75)
    app.run(host='0.0.0.0', port=5000)
