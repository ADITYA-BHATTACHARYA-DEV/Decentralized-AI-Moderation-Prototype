from __future__ import annotations
import json, os, time, uuid
from typing import Any, Dict

BASE = os.environ.get("MOD_STORE", ".store")
os.makedirs(BASE, exist_ok=True)

def _path(name: str) -> str:
    return os.path.join(BASE, name)

def save_json(name: str, data: Dict[str, Any]) -> None:
    with open(_path(name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(name: str, default=None):
    p = _path(name)
    if not os.path.exists(p): return default
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def new_id(prefix="cnt") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"
