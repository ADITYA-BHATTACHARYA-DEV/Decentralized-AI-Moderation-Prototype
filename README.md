# Decentralized AI-Powered Content Moderation — Prototype (MVP)

This repo is a **minimal working prototype** demonstrating the core ideas:
- **Local AI moderation** and **federated aggregation** (simulated).
- **Tamper evidence** via Merkle roots.
- **Anchoring** to a blockchain smart contract (solidity + example scripts).
- **ZKP placeholder** to show how a simple policy-proof would fit (Circom/snarkjs scaffolding).
- **Verifiable Delay Function (VDF)** (simulated).
- **Proof-of-Useful-Work (PoUW)** demonstration (nodes contribute training and submit proofs).
- **DAG execution** (simulation with `networkx`).
- **UI** via Streamlit + simple Flask API.

> ⚠️ This is a prototype for learning and demos. **Do not use in production.**

## Quick start

### 1) Python setup
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Run the Flask API (backend)
```bash
export FLASK_APP=backend/app.py
flask run --port 5001
```
It exposes:
- `POST /submit_content` — submit text.
- `GET  /status/<content_id>` — fetch moderation result/proofs.
- `POST /federated_round` — run one federated learning round (simulated).

### 3) Run the Streamlit dashboard (UI)
```bash
streamlit run ui/streamlit_app.py
```
Use it to submit content and view moderation decisions, Merkle roots, VDF delays, DAG plan and (mock) on-chain anchors.

### 4) (Optional) Solidity contract
Install Node.js, `pnpm` or `npm`, then inside `backend/blockchain`:
```bash
npm install
npx hardhat compile
npx hardhat test
npx hardhat run scripts/deploy.js --network hardhat
```
Copy the deployed address to `backend/blockchain/addresses.json` (created on first run).

### 5) ZKP (placeholder scaffolding)
Requires `circom` and `snarkjs` installed globally.
```bash
cd backend/zkp
./compile.sh
node verify.js
```
This demonstrates where a simple “policy satisfied” proof attaches to a moderation result.

---

## Repo layout

```
backend/
  app.py                      # Flask API
  core/
    model.py                  # Tiny keyword model + hook for HuggingFace model (optional)
    federated.py              # Simulated federated learning (FedAvg)
    merkle.py                 # Merkle tree utilities
    vdf.py                    # Simulated verifiable delay function
    pouw.py                   # Proof-of-Useful-Work simulator
    dag.py                    # DAG scheduling of moderation steps
    storage.py                # Simple local persistence (json)
  blockchain/
    contracts/AuditRegistry.sol
    scripts/deploy.js
    scripts/anchor.js
    addresses.json            # Populated after deploy
    abi/                      # ABI written here on compile
  zkp/
    circuits/policy.circom
    compile.sh
    verify.js
ui/
  streamlit_app.py            # Dashboard
requirements.txt
tests/
  e2e_demo.py                 # End-to-end demonstration
```

## Notes
- AI model is intentionally lightweight for MVP. Swap in a DistilBERT classifier in `core/model.py` when ready.
- ZKP, VDF, and blockchain steps are **toy** integrations to show the path; harden them for real use.
- You can replace Flask+Streamlit with a React SPA against the same API endpoints later.
