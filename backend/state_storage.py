import json
import os

# The permanent hard drives
DB_FILE = "dag_ledger_state.json"
TX_DB_FILE = "dag_tx_history.json" # <-- NEW: The Explorer Database

# --- LEDGER BALANCE FUNCTIONS ---
def load_ledger_state(default_state):
    """Boots up the balances."""
    if not os.path.exists(DB_FILE):
        save_ledger_state(default_state)
        return default_state
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_ledger_state(state_data):
    """Saves current balances."""
    with open(DB_FILE, 'w') as f:
        json.dump(state_data, f, indent=4)

# --- NEW: TRANSACTION HISTORY FUNCTIONS ---
def load_tx_history():
    """Reads the massive public history log."""
    if not os.path.exists(TX_DB_FILE):
        return {}
    with open(TX_DB_FILE, 'r') as f:
        return json.load(f)

def log_transaction(txid, tx_details):
    """Permanently writes a new transaction receipt to the SSD."""
    history = load_tx_history()
    history[txid] = tx_details
    with open(TX_DB_FILE, 'w') as f:
        json.dump(history, f, indent=4)
    print(f"[💾] TXID {txid[:10]}... PERMANENTLY LOGGED TO SSD")
