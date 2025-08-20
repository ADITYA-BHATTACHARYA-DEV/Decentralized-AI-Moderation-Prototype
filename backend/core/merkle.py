from __future__ import annotations
import hashlib
from typing import List, Tuple

def _hash(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def leaf_hash(item: bytes) -> bytes:
    return _hash(b'\x00' + item)

def node_hash(left: bytes, right: bytes) -> bytes:
    return _hash(b'\x01' + left + right)

def build_merkle(leaves: List[bytes]) -> Tuple[bytes, List[List[bytes]]]:
    if not leaves:
        empty = _hash(b"")
        return empty, []
    level = [leaf_hash(l) for l in leaves]
    tree = [level]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            a = level[i]
            b = level[i+1] if i+1 < len(level) else a
            nxt.append(node_hash(a, b))
        level = nxt
        tree.append(level)
    return level[0], tree

def proof_for_index(tree: List[List[bytes]], index: int) -> List[Tuple[bytes, str]]:
    proof = []
    idx = index
    for level in tree[:-1]:
        sib = idx ^ 1
        sibling = level[sib] if sib < len(level) else level[idx]
        pos = "right" if idx % 2 == 0 else "left"
        proof.append((sibling, pos))
        idx //= 2
    return proof

def verify_proof(leaf: bytes, proof, root: bytes) -> bool:
    cur = leaf_hash(leaf)
    for sibling, pos in proof:
        if pos == "right":
            cur = node_hash(cur, sibling)
        else:
            cur = node_hash(sibling, cur)
    return cur == root

def to_hex(b: bytes) -> str:
    return "0x" + b.hex()
