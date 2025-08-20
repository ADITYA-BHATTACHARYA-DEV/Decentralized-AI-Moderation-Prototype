from flask import Flask, request, jsonify, render_template, redirect, url_for
from core import storage, model, merkle, vdf, federated, pouw, dag
import hashlib, json, time

app = Flask(__name__)

MODEL_HASH = hashlib.sha256(b"toy-model-v1").hexdigest()

# ----- UI ROUTES -----

@app.get("/")
def home():
    """Home feed"""
    # Load recent content IDs
    content_list = storage.list_json(prefix="cnt")
    posts = [storage.load_json(cid) for cid in content_list]
    return render_template("home.html", posts=posts)

@app.get("/post/<cid>")
def post_details(cid: str):
    """Post details & proofs page"""
    record = storage.load_json(f"{cid}.json", default=None)
    if not record:
        return "Post not found", 404
    return render_template("post.html", post=record)

@app.get("/create_post")
def create_post():
    """Post creation page"""
    return render_template("create_post.html")

@app.get("/governance")
def governance():
    """Governance and voting panel"""
    cases = federated.get_governance_cases()
    return render_template("governance.html", cases=cases)

@app.get("/rewards")
def rewards():
    """User contribution and rewards page"""
    user_rewards = pouw.summarize_rewards()
    return render_template("rewards.html", rewards=user_rewards)

@app.get("/audit")
def audit():
    """Audit and history center"""
    logs = storage.list_json(prefix="cnt")
    return render_template("audit.html", logs=logs)

# ----- API ROUTES (existing) -----
@app.post("/submit_content")
def submit_content():
    data = request.get_json(force=True)
    text = data.get("text","")
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
        "proofs": [[(merkle.to_hex(s), pos) for (s,pos) in p] for p in proofs],
        "model_hash": "0x"+MODEL_HASH,
        "ts": time.time(),
        "dag": dag.to_json(dag.build_moderation_dag(cid)),
        "zkp": {"status":"placeholder", "verified": False}
    }
    storage.save_json(f"{cid}.json", record)
    return jsonify({"ok": True, "content_id": cid, "merkle_root": record["merkle_root"]})

@app.get("/status/<cid>")
def status(cid: str):
    rec = storage.load_json(f"{cid}.json", default=None)
    if not rec: return jsonify({"ok": False, "error":"not found"}), 404
    return jsonify({"ok": True, "record": rec})

@app.post("/federated_round")
def fed_round():
    st, updates = federated.run_round()
    updates_hex = hashlib.sha256(json.dumps(updates).encode()).hexdigest()
    event = pouw.submit_work("node-local", updates_hex, steps=len(updates))
    return jsonify({"ok": True, "state": st, "pouw_event": event})

@app.get("/pouw_rewards")
def api_rewards():
    return jsonify({"ok": True, "rewards": pouw.summarize_rewards()})

if __name__ == "__main__":
    app.run(port=5001, debug=True)
