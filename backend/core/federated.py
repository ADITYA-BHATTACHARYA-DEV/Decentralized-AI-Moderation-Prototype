from __future__ import annotations
from .storage import load_json, save_json
from .model import simulate_client_update, fedavg
import time, os

STATE = "fed_state.json"

def get_state():
    st = load_json(STATE, default={"round":0, "param":0.0, "history":[]})
    return st

def run_round(num_clients: int = 5, base_grad: float = 0.1):
    st = get_state()
    updates = [simulate_client_update(seed=st["round"]*100+i, grad=base_grad) for i in range(num_clients)]
    delta = fedavg(updates)
    st["param"] += delta
    st["round"] += 1
    st["history"].append({"round": st["round"], "delta": delta, "param": st["param"], "ts": time.time()})
    save_json(STATE, st)
    return st, updates
