from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np

# Minimal keyword scorer (placeholder). Swap with DistilBERT later.
BAD_WORDS = {"hate", "violence", "terror", "threat", "kill"}

@dataclass
class InferenceResult:
    label: str
    score: float
    policy_flags: List[str]

def local_infer(text: str) -> InferenceResult:
    toks = set([t.strip(".,!?;:").lower() for t in text.split()])
    hits = BAD_WORDS.intersection(toks)
    score = min(1.0, len(hits)/3.0)
    label = "reject" if score >= 0.5 else "allow"
    flags = list(hits)
    return InferenceResult(label=label, score=score, policy_flags=flags)

# --- Federated training simulation (toy FedAvg on scalar) ---
def simulate_client_update(seed: int, grad: float) -> float:
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 0.05)
    return grad + noise

def fedavg(updates: List[float]) -> float:
    return float(np.mean(updates)) if updates else 0.0
