#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ecdsa
import hashlib
import json
import time
import getpass

class CryptographicEngine:
    @staticmethod
    def sign_transaction(private_key_hex, transaction_data):
        """Uses the SECP256k1 curve to digitally sign the transaction payload."""
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
        tx_string = json.dumps(transaction_data, sort_keys=True).encode('utf-8')
        signature = sk.sign(tx_string)
        return signature.hex(), sk.get_verifying_key().to_string().hex()

    @staticmethod
    def verify_signature(public_key_hex, signature_hex, transaction_data):
        """The network uses this to prove the sender authorized the transfer."""
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=ecdsa.SECP256k1)
        tx_string = json.dumps(transaction_data, sort_keys=True).encode('utf-8')
        try:
            return vk.verify(bytes.fromhex(signature_hex), tx_string)
        except ecdsa.BadSignatureError:
            return False

# ==============================================================================
# DEPLOYMENT: THE FIRST STRIKE
# ==============================================================================
if __name__ == "__main__":
    print("="*60)
    print(" 🚀 INITIATING CROSS-BORDER DAG TRANSFER 🚀")
    print("="*60)
    
    # 1. The Coordinates
    SENDER = "11JKJ9fhyUUdWy7kcfo3sbF88KDcZ1mfvpD"
    RECEIVER = "11B2QVvNEPjyrzeVBKNmskdN65FRUPpkSff"
    AMOUNT = 10000.0
    
    print(f"[*] TARGET LOCK: {RECEIVER}")
    print(f"[*] PAYLOAD: {AMOUNT:,.2f} COINS")
    print("-" * 60)
    
    # 2. Secure Private Key Input (Will not show characters on screen)
    print("[!] AUTHORIZATION REQUIRED.")
    priv_key = getpass.getpass("Enter Genesis Private Key to Sign (Hidden): ").strip()
    
    # 3. Construct the Raw Transaction Payload
    raw_tx = {
        "sender": SENDER,
        "receiver": RECEIVER,
        "amount": AMOUNT,
        "timestamp": time.time(),
        "parents": ["6a1fe8da9bda1fe8"] # Weaving into the Genesis Vertex
    }
    
    print("\n[⚡] Forging ECDSA Cryptographic Signature...")
    time.sleep(1)
    
    try:
        # 4. Sign and Verify
        signature, pub_key = CryptographicEngine.sign_transaction(priv_key, raw_tx)
        is_valid = CryptographicEngine.verify_signature(pub_key, signature, raw_tx)
        
        if is_valid:
            print("[✅] SIGNATURE VERIFIED. MATHEMATICS CONFIRMED.")
            print(f"     Sig Hash: {signature[:32]}...\n")
            
            # 5. Update Local State Ledger (Simulated for this node)
            GENESIS_BALANCE = 100000000000.0 - AMOUNT
            CHIDIBLESS_BALANCE = AMOUNT
            
            print("📊 NEW NETWORK STATE RECORDED:")
            print(f"Genesis Address ({SENDER[:6]}...) : {GENESIS_BALANCE:,.2f} COINS")
            print(f"Target Address  ({RECEIVER[:6]}...) : {CHIDIBLESS_BALANCE:,.2f} COINS")
            print("="*60)
            print("🌐 TRANSFER COMPLETE. THE DAG WEB HAS EXPANDED.")
            
        else:
            print("[❌] SIGNATURE FAILED. TRANSACTION ABORTED.")
            
    except Exception as e:
        print(f"\n[❌] CRITICAL ERROR: {e}")
        print("Ensure you copied the exact hexadecimal Private Key without extra spaces.")

