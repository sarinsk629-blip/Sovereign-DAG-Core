import hashlib
import time

def generate_txid(sender, receiver, amount, signature):
    """Forges a unique cryptographic receipt for a transaction."""
    # Capture the exact millisecond
    timestamp = str(time.time())
    
    # Package the raw data
    raw_data = f"{sender}{receiver}{amount}{signature}{timestamp}"
    
    # Mathematically crush the data into a 64-character hash
    txid = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
    
    return f"0x{txid}"

if __name__ == "__main__":
    print("\n" + "="*55)
    print("🧾 SOVEREIGN TxID FORGE: SECURE SERVER TEST")
    print("="*55)
    
    # Test Data
    test_sender = "11JKJ9fhyUUdWy7kcfo3sbF88KDcZ1mfvpD"
    test_receiver = "SOVac1ecd57b262711320eb336d763446455f"
    test_amount = 5000.0
    test_signature = "30450221008af465467f04e8a71ea2e1dbb661"
    
    receipt = generate_txid(test_sender, test_receiver, test_amount, test_signature)
    
    print(f"[✅] PERMANENT TRANSACTION ID FORGED:\n{receipt}")
    print("="*55 + "\n")
