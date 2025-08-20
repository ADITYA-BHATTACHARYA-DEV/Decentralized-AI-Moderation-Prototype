import hashlib, time
from typing import Tuple

def vdf_delay(message: bytes, difficulty: int = 200000) -> Tuple[str, float]:
    """Simulated VDF: repeated hashing with a step counter.
    Returns (final_hex, seconds_taken).
    Increase difficulty for longer delay.
    """
    start = time.time()
    h = hashlib.sha256(message).digest()
    for i in range(difficulty):
        h = hashlib.sha256(h + i.to_bytes(4, 'big')).digest()
    end = time.time()
    return "0x" + h.hex(), end - start
