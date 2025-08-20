from __future__ import annotations
import json, os, time, uuid
from typing import Any, Dict

BASE = os.environ.get("MOD_STORE", ".store")
os.makedirs(BASE, exist_ok=True)

def _path(name: str) -> str:
    return os.path.join(BASE, name)

def save_json(name: str, data: Dict[str, Any]) -> None:
    """Standard save with pretty formatting."""
    with open(_path(name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_json_atomic(name: str, data: Dict[str, Any]) -> None:
    """Atomic save to prevent partial writes."""
    tmp = _path(f"{name}.tmp")
    final = _path(name)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, final)

def save_json_versioned(name: str, data: Dict[str, Any]) -> None:
    """Save with timestamp suffix for versioning."""
    ts = time.strftime("%Y%m%d-%H%M%S")
    versioned = f"{name}.{ts}.json"
    save_json(versioned, data)

def load_json(name: str, default: Dict[str, Any] | None = None) -> Dict[str, Any] | None:
    """Load JSON file or return default."""
    p = _path(name)
    if not os.path.exists(p): return default
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def list_json(prefix: str = "") -> list[str]:
    """List all JSON files with optional prefix filter."""
    return sorted([
        f for f in os.listdir(BASE)
        if f.startswith(prefix) and f.endswith(".json")
    ])

def new_id(prefix: str = "cnt") -> str:
    """Generate a compact unique ID."""
    return f"{prefix}_{uuid.uuid4().hex[:10]}"
