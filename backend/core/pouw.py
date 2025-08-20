import time, json, os, hashlib, random
from .storage import load_json, save_json

LEDGER = "pouw.json"

def submit_work(node_id: str, updates_hash: str, steps: int) -> dict:
    rec = load_json(LEDGER, default={"events": []})
    event = {
        "node": node_id,
        "updates": updates_hash,
        "steps": steps,
        "reward": round(steps * 0.001, 6),
        "ts": time.time()
    }
    rec["events"].append(event)
    save_json(LEDGER, rec)
    return event

def summarize_rewards() -> dict:
    rec = load_json(LEDGER, default={"events": []})
    agg = {}
    for e in rec["events"]:
        agg[e["node"]] = agg.get(e["node"], 0.0) + e["reward"]
    return agg
