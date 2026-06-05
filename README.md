# Sovereign DAG Core Engine (V2.0 Master Upgrade)

Welcome to the official repository for the Sovereign Core Architecture. This project represents a cryptographically secure, high-performance transactional asset engine running on an advanced Python stack.

## 📐 Current Architectural Topology

The project is currently configured as a **Secure Centralized Ledger API Backend with Remote Client Telemetry**. This setup enables active testing of transactional validation math, custom tokens, and constant product pricing invariants before expanding into decentralized P2P cluster syncing.

### 🧠 Core Features Implemented
* **True Cryptographic Security**: Complete signature verification using the ECDSA protocol over the standard `SECP256k1` curve.
* **Automated Liquidity Pricing Engine**: Built-in Automated Market Maker (AMM) capabilities within the core asset bridge.
* **SRC-20 Token Protocol**: Integrated token minting layers featuring systemic token burning functions.
* **Persistent Local State Storage**: Full read/write state engine syncing directly to disk via secure JSON database states.

---

## 📂 Repository File Index

* `/backend/dag_api.py`: The master Flask application layer controlling state mutations and cryptographic validation.
* `/cmd/sovereign-node/main.py`: The user-facing terminal interface designed to pull live network state telemetry from the running API gateway over HTTP.

Note: *The legacy V8.3 simulated routing loop has been deprecated and replaced with live V2.0 HTTP gateway tracking.*
