#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flask_cors import CORS
import ecdsa, hashlib, json, time, os
from ecdsa.util import sigdecode_der

from sovereign_vm import execute_smart_contract
from state_storage import load_ledger_state, save_ledger_state, load_tx_history, log_transaction
from txid_forge import generate_txid

app = Flask(__name__)
CORS(app)

# ==========================================
# 🌐 SOVEREIGN MAINNET (V2.0 MASTER UPGRADE)
# ==========================================

mainnet_genesis = {
    "SOVb1dab6f1a43527d5cc9296f4391e33a009": {"SOV": 100000000.0}, # TRUE MAINNET CENTRAL BANK
    "SOV_Deployer_Node": {"SOV": 5000.0}, 
    "SOV_BURN_VAULT": {"SOV": 0.0} # The Black Hole
}

network_state = load_ledger_state(mainnet_genesis)

def verify_signature(public_key_hex, signature_hex, tx_data):
    try:
        if public_key_hex.startswith('04'):
            public_key_bytes = bytes.fromhex(public_key_hex)[1:]
        else:
            public_key_bytes = bytes.fromhex(public_key_hex)
        public_key = ecdsa.VerifyingKey.from_string(public_key_bytes, curve=ecdsa.SECP256k1)
        tx_string = json.dumps(tx_data, sort_keys=True)
        return public_key.verify(bytes.fromhex(signature_hex), tx_string.encode('utf-8'), hashfunc=hashlib.sha256, sigdecode=sigdecode_der)
    except:
        return False

@app.route('/network/status', methods=['GET'])
def get_status():
    return jsonify({"status": "SECURE", "architecture": "MAINNET_V2.0", "burn_vault": network_state["SOV_BURN_VAULT"]["SOV"]})

@app.route('/balance/<wallet>', methods=['GET'])
def get_balance(wallet):
    if wallet not in network_state:
        return jsonify({"balances": {"SOV": 0.0}})

    clean_balances = {}
    for key, value in network_state[wallet].items():
        if key not in ["faucet_claimed", "ip_logs"]:
            clean_balances[key] = value

    return jsonify({"balances": clean_balances})

# --- LAYER-0: THE SOVEREIGN FAUCET ---
@app.route('/faucet/<wallet>', methods=['POST'])
def faucet(wallet):
    genesis_address = "SOVb1dab6f1a43527d5cc9296f4391e33a009"
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)

    if wallet not in network_state:
        network_state[wallet] = {"SOV": 0.0}

    if network_state[wallet].get("faucet_claimed", False) == True:
        return jsonify({"status": "FAILED", "reason": "Address already funded."}), 400

    if "global_ip_logs" not in network_state:
        network_state["global_ip_logs"] = {}

    if network_state["global_ip_logs"].get(client_ip, False) == True:
        return jsonify({"status": "FAILED", "reason": "Your physical device has already claimed a drop."}), 400

    network_state[genesis_address]["SOV"] -= 1.0
    network_state[wallet]["SOV"] += 1.0
    network_state[wallet]["faucet_claimed"] = True
    network_state["global_ip_logs"][client_ip] = True

    txid = generate_txid("FAUCET_SYSTEM", wallet, 1.0, "SYSTEM_AUTO_SIG")
    save_ledger_state(network_state)
    return jsonify({"status": "SUCCESS", "message": "1.0 SOV Dispensed.", "txid": txid})

# --- LAYER-0: PEER-TO-PEER TRANSFER ---
@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json
    sender = data.get('sender')
    recipient = data.get('recipient')
    amount = float(data.get('amount'))
    ticker = data.get('ticker', 'SOV')

    if recipient not in network_state:
        network_state[recipient] = {}
    if ticker not in network_state[recipient]:
        network_state[recipient][ticker] = 0.0

    sender_balance = network_state.get(sender, {}).get(ticker, 0.0)
    if sender_balance < amount:
        return jsonify({"status": "FAILED", "reason": f"Insufficient {ticker} balance."}), 400

    network_state[sender][ticker] -= amount
    network_state[recipient][ticker] += amount

    txid = generate_txid("TRANSFER", sender, amount, data.get('signature', 'SIG_VERIFIED'))
    save_ledger_state(network_state)
    log_transaction(txid, {"type": "TRANSFER", "sender": sender, "recipient": recipient, "amount": amount, "ticker": ticker})

    return jsonify({"status": "SUCCESS", "message": f"Successfully sent {amount} {ticker}!", "txid": txid})

# --- LAYER-0: PUBLIC EXPLORER ---
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
    except Exception as e:
        return jsonify({"transactions": []})

# --- LAYER-0: DEX POOL INITIALIZATION ---
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

# --- LAYER-0: LIVE DEX PRICING RADAR ---
@app.route('/live_price', methods=['GET'])
def live_price():
    initialize_dex_pool() 
    current_price = network_state["DEX_POOL"]["USDT"] / network_state["DEX_POOL"]["SOV"]
    return jsonify({
        "price": current_price,
        "pool_sov": network_state["DEX_POOL"]["SOV"],
        "pool_usdt": network_state["DEX_POOL"]["USDT"]
    })

# --- LAYER-0: REAL-WORLD BRIDGE (AMM) ---
@app.route('/bridge_deposit', methods=['POST'])
def bridge_deposit():
    data = request.json
    wallet = data.get('wallet')
    usdt_paid = float(data.get('usdt_paid'))
    bsc_tx_hash = data.get('bsc_tx_hash')

    if "used_tx_hashes" not in network_state:
        network_state["used_tx_hashes"] = {}
    if bsc_tx_hash in network_state["used_tx_hashes"]:
        return jsonify({"status": "FAILED", "reason": "Transaction already processed."}), 400

    initialize_dex_pool()

    pool_sov = network_state["DEX_POOL"]["SOV"]
    pool_usdt = network_state["DEX_POOL"]["USDT"]
    k = pool_sov * pool_usdt

    new_pool_usdt = pool_usdt + usdt_paid
    new_pool_sov = k / new_pool_usdt
    sov_to_dispense = pool_sov - new_pool_sov

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
    return jsonify({"status": "SUCCESS", "message": f"{sov_to_dispense:.2f} SOV secured! New Global Price: ${new_price:.4f}"})

# --- LAYER-0: CENTRAL BANK INJECTION ---
@app.route('/admin_inject', methods=['POST'])
def admin_inject():
    data = request.json
    wallet = data.get('wallet')
    sov_to_inject = float(data.get('sov_amount', 0))
    genesis_address = "SOVb1dab6f1a43527d5cc9296f4391e33a009"

    if wallet != genesis_address:
        return jsonify({"status": "FAILED", "reason": "SECURITY BREACH: Only the Central Bank can inject liquidity."}), 403

    if network_state.get(genesis_address, {}).get("SOV", 0) < sov_to_inject:
        return jsonify({"status": "FAILED", "reason": "Insufficient SOV in the Genesis Reserve."}), 400

    if "DEX_POOL" not in network_state:
        return jsonify({"status": "FAILED", "reason": "DEX Pool not initialized yet."}), 400

    network_state[genesis_address]["SOV"] -= sov_to_inject
    network_state["DEX_POOL"]["SOV"] += sov_to_inject

    txid = generate_txid("LIQUIDITY_INJECTION", genesis_address, sov_to_inject, data.get('signature', 'SIG_VERIFIED'))
    save_ledger_state(network_state)
    log_transaction(txid, {"type": "LIQUIDITY_INJECTION", "sender": genesis_address, "sov_injected": sov_to_inject})

    new_price = network_state["DEX_POOL"]["USDT"] / network_state["DEX_POOL"]["SOV"]
    return jsonify({"status": "SUCCESS", "message": f"INJECTION COMPLETE: {sov_to_inject} SOV moved to Trading Floor. New Price: ${new_price:.6f}"})

# --- LAYER-2: SRC-20 TOKEN FACTORY ---
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
         return jsonify({"status": "FAILED", "reason": "Cryptographic Forgery Detected"}), 401

    sender_wallet = network_state.get(sender, {"SOV": 0.0})
    if sender_wallet.get("SOV", 0.0) < 500.0:
        return jsonify({"status": "FAILED", "reason": "Insufficient SOV. 500 SOV Required to Mint."}), 400

    sender_wallet["SOV"] -= 500.0
    network_state["SOV_BURN_VAULT"]["SOV"] += 500.0

    if ticker in sender_wallet:
        return jsonify({"status": "FAILED", "reason": f"Ticker {ticker} already exists in wallet"}), 400

    sender_wallet[ticker] = supply
    network_state[sender] = sender_wallet

    txid = generate_txid(sender, "SRC20_FACTORY", 500.0, signature)
    save_ledger_state(network_state)
    log_transaction(txid, {"type": "MINT_SRC20", "sender": sender, "ticker": ticker, "supply": supply, "burned": 500.0})

    return jsonify({"status": "SUCCESS", "message": f"{supply} {ticker} Minted.", "txid": txid})

# --- LAYER-1: MULTI-ASSET TRANSFERS ---
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
        return jsonify({"status": "FAILED"}), 401

    if network_state.get(sender, {}).get(ticker, 0.0) < amount: 
        return jsonify({"status": "FAILED", "reason": "Insufficient Physics"}), 400

    network_state[sender][ticker] -= amount
    if receiver not in network_state: 
        network_state[receiver] = {}
    network_state[receiver][ticker] = network_state[receiver].get(ticker, 0.0) + amount

    txid = generate_txid(sender, receiver, amount, signature)
    save_ledger_state(network_state)
    log_transaction(txid, {"type": "TRANSFER", "sender": sender, "receiver": receiver, "amount": amount, "ticker": ticker})

    return jsonify({"status": "SUCCESS", "txid": txid})

if __name__ == '__main__':
    print("="*65)
    print("[🌐] SOVEREIGN MAINNET V2.0 (CENTRAL BANK SECURED) LIVE")
    print("="*65)
    app.run(host='0.0.0.0', port=5000)
