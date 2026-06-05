import math

def execute_smart_contract(contract_code, contract_address, current_state):
    """The Sovereign Virtual Machine (SVM) Sandbox."""
    print(f"\n[⚙️] SVM BOOT SEQUENCE: Spinning up sandbox for {contract_address}...")
    
    local_memory = {
        "state": current_state,          
        "math": math,                    
        "execution_result": "FAILED"     
    }
    
    try:
        exec(contract_code, {"__builtins__": {}}, local_memory)
        print(f"[✅] SVM EXECUTION: {local_memory['execution_result']}")
        return True, local_memory.get("state")
        
    except Exception as e:
        print(f"[🚨] SVM FATAL CRASH: {e}")
        return False, current_state

if __name__ == "__main__":
    print("="*60)
    print("📈 SOVEREIGN VM: ALGORITHMIC TRADING TRIGGER")
    print("="*60)
    
    # The Global Market State
    test_network_state = {
        "SOV_Price": 155.0,           # The current market price
        "Bot_Wallet": 5000.0,         # The algorithm's holding balance
        "Exchange_Liquidity": 10000.0 # The market pool
    }
    
    # ---------------------------------------------------------
    # THE SMART CONTRACT: High-Frequency Take-Profit Algorithm
    # ---------------------------------------------------------
    user_contract = """
# Step 1: Read Market Data
current_price = state.get("SOV_Price", 0)
my_balance = state.get("Bot_Wallet", 0)

# Step 2: Risk Management & Execution Logic
target_price = 150.0
trade_size = 50.0

if current_price >= target_price and my_balance >= trade_size:
    # Execute Take-Profit Order
    state["Bot_Wallet"] -= trade_size
    state["Exchange_Liquidity"] += trade_size
    execution_result = "SUCCESS: Take-Profit Triggered at 150.0+"
else:
    execution_result = "HOLD: Market conditions not met."
"""
    # ---------------------------------------------------------
    
    print(f"[>] INITIAL STATE: {test_network_state}")
    print("[>] Injecting Algorithmic Contract into SVM...")
    
    success, new_state = execute_smart_contract(user_contract, "Algo_Bot_V1", test_network_state)
    
    print(f"\n[>] FINAL NETWORK STATE: {new_state}")
    print("="*60 + "\n")
