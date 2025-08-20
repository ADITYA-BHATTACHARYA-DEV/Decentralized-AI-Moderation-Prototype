from __future__ import annotations
from flask import Flask, request, jsonify
from core import storage, model, merkle, vdf, federated, pouw, dag
import time, json, os, hashlib

app = Flask(__name__)

MODEL_HASH = hashlib.sha256(b"toy-model-v1").hexdigest()

@app.get("/")
def home():
    return "Backend is running!"

@app.post("/submit_content")
def submit_content():
    data = request.get_json(force=True)
    text = data.get("text", "")
    cid = storage.new_id("cnt")
    inf = model.local_infer(text)
    vdf_hex, vdf_secs = vdf.vdf_delay(text.encode("utf-8"), difficulty=50000)

    leaves = [
        f"content_id:{cid}".encode(),
        f"label:{inf.label}".encode(),
        f"score:{inf.score}".encode(),
        f"flags:{','.join(inf.policy_flags)}".encode(),
        f"vdf:{vdf_hex}".encode()
    ]
    root, tree = merkle.build_merkle(leaves)
    proofs = [merkle.proof_for_index(tree, i) for i in range(len(leaves))]

    record = {
        "content_id": cid,
        "text": text,
        "inference": inf.__dict__,
        "vdf": {"output": vdf_hex, "seconds": vdf_secs},
        "merkle_root": merkle.to_hex(root),
        "proofs": [[(merkle.to_hex(s), pos) for (s, pos) in p] for p in proofs],
        "model_hash": "0x" + MODEL_HASH,
        "ts": time.time(),
        "dag": dag.to_json(dag.build_moderation_dag(cid)),
        "zkp": {"status": "placeholder", "verified": False},
        "likes": 0,
        "comments": []
    }
    storage.save_json(f"{cid}.json", record)
    return jsonify({"ok": True, "content_id": cid, "merkle_root": record["merkle_root"]})

@app.get("/status/<cid>")
def status(cid: str):
    rec = storage.load_json(f"{cid}.json", default=None)
    if not rec:
        return jsonify({"ok": False, "error": "not found"}), 404
    return jsonify({"ok": True, "record": rec})

@app.post("/like/<cid>")
def like_content(cid: str):
    rec = storage.load_json(f"{cid}.json", default=None)
    if not rec:
        return jsonify({"ok": False, "error": "not found"}), 404
    rec["likes"] = rec.get("likes", 0) + 1
    storage.save_json(f"{cid}.json", rec)
    return jsonify({"ok": True, "likes": rec["likes"]})

@app.post("/comment/<cid>")
def comment_content(cid: str):
    rec = storage.load_json(f"{cid}.json", default=None)
    if not rec:
        return jsonify({"ok": False, "error": "not found"}), 404
    data = request.get_json(force=True)
    comment = {
        "user": data.get("user", "anonymous"),
        "text": data.get("comment", ""),
        "ts": time.time()
    }
    rec.setdefault("comments", []).append(comment)
    storage.save_json(f"{cid}.json", rec)
    return jsonify({"ok": True, "comment": comment})

@app.get("/comments/<cid>")
def get_comments(cid: str):
    rec = storage.load_json(f"{cid}.json", default=None)
    if not rec:
        return jsonify({"ok": False, "error": "not found"}), 404
    return jsonify({"ok": True, "comments": rec.get("comments", [])})

@app.post("/federated_round")
def fed_round():
    st, updates = federated.run_round()
    updates_hex = hashlib.sha256(json.dumps(updates).encode()).hexdigest()
    event = pouw.submit_work("node-local", updates_hex, steps=len(updates))
    return jsonify({"ok": True, "state": st, "pouw_event": event})

@app.get("/pouw_rewards")
def rewards():
    return jsonify({"ok": True, "rewards": pouw.summarize_rewards()})

@app.post("/governance_vote/<case_id>")
def governance_vote(case_id: str):
    data = request.get_json(force=True)
    vote = data.get("vote")
    return jsonify({"ok": True, "case_id": case_id, "vote": vote})

if __name__ == "__main__":
    app.run(port=5001, debug=True)


@app.get("/leaderboard")
def leaderboard():
    from core import storage  # adjust import if needed
    all_records = []
    for fname in storage.list_json(prefix="cnt"):
        rec = storage.load_json(fname, default=None)
        if rec:
            all_records.append({
                "content_id": rec["content_id"],
                "likes": rec.get("likes", 0),
                "text": rec.get("text", "")[:100]
            })
    top = sorted(all_records, key=lambda r: r["likes"], reverse=True)[:10]
    return jsonify({"ok": True, "top_liked": top})
