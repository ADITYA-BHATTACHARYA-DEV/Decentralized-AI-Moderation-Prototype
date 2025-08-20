import networkx as nx
from typing import Dict, Any

def build_moderation_dag(content_id: str) -> nx.DiGraph:
    g = nx.DiGraph()
    g.add_node("ingest", label="Ingest content")
    g.add_node("local_inference", label="Local AI inference")
    g.add_node("vdf", label="VDF delay")
    g.add_node("merkle", label="Merkle root")
    g.add_node("anchor", label="Anchor on-chain")
    g.add_node("zkp", label="ZKP verify (mock)")
    g.add_node("finalize", label="Finalize decision")
    g.add_edges_from([
        ("ingest","local_inference"),
        ("local_inference","vdf"),
        ("local_inference","merkle"),
        ("merkle","anchor"),
        ("vdf","finalize"),
        ("anchor","finalize"),
        ("zkp","finalize")
    ])
    return g

def to_json(g: nx.DiGraph) -> Dict[str, Any]:
    return {
        "nodes":[{"id":n, **g.nodes[n]} for n in g.nodes],
        "edges":[{"u":u, "v":v} for u,v in g.edges]
    }
