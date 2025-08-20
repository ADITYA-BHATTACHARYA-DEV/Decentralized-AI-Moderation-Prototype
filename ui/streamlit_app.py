import streamlit as st
import requests, time, os

API = os.environ.get("MOD_API", "http://localhost:5001")
st.set_page_config(page_title="Decentralized Moderation Prototype", layout="wide")
st.title("🕸️ Decentralized AI Moderation — Live Prototype")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Controls / Governance")

    if st.button("Run Federated Round"):
        r = requests.post(f"{API}/federated_round")
        st.success(r.json() if r.status_code == 200 else "Failed!")

    if st.button("Show PoUW Rewards"):
        r = requests.get(f"{API}/pouw_rewards")
        st.info(r.json() if r.status_code == 200 else "Failed!")

    st.subheader("Preferences")
    moderation_level = st.selectbox("Moderation Sensitivity", ["Strict", "Medium", "Lenient"])
    show_proofs = st.checkbox("Show Proof Panels", True)

    st.subheader("Navigation")
    tab = st.radio("Choose View", ["Live Feed", "Leaderboard", "Transparency"])

# ---------------- Last Post Engagement ----------------
if "last_cid" in st.session_state:
    cid = st.session_state["last_cid"]

    st.markdown("---")
    st.subheader(f"Interact with Last Post: {cid}")

    # Initialize engagement counts
    for key in ["likes", "comments", "shares"]:
        state_key = f"{key}_{cid}_last"
        if state_key not in st.session_state:
            st.session_state[state_key] = 0

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👍 Like", key=f"like_{cid}_last"):
            st.session_state[f"likes_{cid}_last"] += 1
        st.write(f"{st.session_state[f'likes_{cid}_last']} Likes")
    with c2:
        if st.button("💬 Comment", key=f"comment_{cid}_last"):
            st.session_state[f"comments_{cid}_last"] += 1
        st.write(f"{st.session_state[f'comments_{cid}_last']} Comments")
    with c3:
        if st.button("🔗 Share", key=f"share_{cid}_last"):
            st.session_state[f"shares_{cid}_last"] += 1
        st.write(f"{st.session_state[f'shares_{cid}_last']} Shares")

    if st.button("File Transparent Appeal", key=f"appeal_{cid}_last"):
        st.info("Appeal submitted to community governance feed.")

    if show_proofs:
        with st.expander("🔍 Proofs & Transparency"):
            r = requests.get(f"{API}/status/{cid}")
            if r.status_code == 200:
                rec = r.json()["record"]
                st.markdown(f"- **Merkle Root:** `{rec.get('merkle_root')}`")
                
                vdf_seconds = rec.get('vdf', {}).get('seconds', 0)
                if vdf_seconds:
                    if st.button(f"Start VDF Countdown ({vdf_seconds} sec)", key=f"vdf_btn_{cid}"):
                        for remaining in range(vdf_seconds, 0, -1):
                            st.write(f"⏳ VDF Delay Remaining: {remaining} sec")
                            time.sleep(1)
                
                st.markdown(f"- **ZKP Status:** `{rec.get('zkp', {}).get('status','Unknown')}`")
                st.markdown(f"- **Blockchain Tx:** [View on Explorer]({rec.get('blockchain_tx','#')})")

# ---------------- Helper: Render Card ----------------
def render_card(cid, idx):
    r = requests.get(f"{API}/status/{cid}")
    if r.status_code != 200: return st.empty()

    rec = r.json()["record"]
    inf = rec.get("inference", {})
    score = inf.get("score", 0)
    label = inf.get("label", "unknown")
    flags = rec.get("policy_flags", [])

    badge_text, badge_color = {
        "safe": ("✅ Accepted", "green"),
        "flagged": ("⚠ Flagged", "orange"),
        "rejected": ("❌ Rejected", "red")
    }.get(label, ("❓ Unknown", "gray"))

    st.markdown(
        "<div style='border:1px solid #ddd; border-radius:12px; padding:10px; margin-bottom:10px; box-shadow:2px 2px 8px #eee;'>",
        unsafe_allow_html=True
    )
    st.markdown(f"<h5>@{rec.get('content_id')}</h5>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{badge_color}; font-weight:bold'>{badge_text}</span>", unsafe_allow_html=True)
    st.caption(f"Confidence: {score*100:.1f}% | Flags: {', '.join(flags)}")
    st.write(rec.get("text"))

    media_files = st.session_state.get("media_blobs", {}).get(cid, [])
    for media in media_files:
        if media.type.startswith("image/"):
            st.image(media, use_container_width=True)
        elif media.type.startswith("video/"):
            st.video(media, use_container_width=True)

    # Like button + counter
    like_count = rec.get("likes", 0)
    cols = st.columns([1, 6])
    with cols[0]:
        if st.button("👍", key=f"like_{cid}_{idx}"):
            requests.post(f"{API}/like/{cid}")
            st.rerun()  # updated from experimental_rerun

    with cols[1]:
        st.caption(f"{like_count} likes")

    # Comment section
    with st.expander("💬 Comments"):
        comment_input = st.text_input("Write a comment...", key=f"comment_input_{cid}_{idx}")
        if st.button("Submit Comment", key=f"submit_comment_{cid}_{idx}"):
            payload = {"comment": comment_input}
            requests.post(f"{API}/comment/{cid}", json=payload)
            st.success("Comment submitted!")

        rc = requests.get(f"{API}/comments/{cid}")
        if rc.status_code == 200:
            comments = rc.json().get("comments", [])
            for c in comments:
                st.markdown(f"- *{c['user']}*: {c['text']}")

    if badge_text != "✅ Accepted":
        if st.button("File Transparent Appeal", key=f"appeal_{cid}_{idx}"):
            st.info("Appeal submitted to community governance feed.")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Live Feed ----------------
if tab == "Live Feed":
    with st.expander("📤 Submit New Post"):
        text = st.text_area("Write your post...", "")
        attach_media = st.file_uploader("Attach Images/Videos", type=["png", "jpg", "jpeg", "mp4"], accept_multiple_files=True)

        if st.button("Submit for Moderation"):
            payload = {"text": text, "media": [f.name for f in attach_media] if attach_media else []}
            r = requests.post(f"{API}/submit_content", json=payload)
            if r.status_code == 200:
                cid = r.json().get("content_id")
                st.session_state.setdefault("live_cids", []).insert(0, cid)
                st.session_state["last_cid"] = cid
                st.session_state.setdefault("media_blobs", {})[cid] = attach_media
                st.success(f"Content submitted! Content ID: {cid}")
            else:
                st.error("Submission failed!")

    st.subheader("📰 Live Moderation Feed")

    if "live_cids" not in st.session_state: st.session_state["live_cids"] = []
    if "load_count" not in st.session_state: st.session_state["load_count"] = 6

    if st.button("🔄 Refresh Feed"):
        try:
            r = requests.get(f"{API}/latest_content")
            if r.status_code == 200:
                new_cids = r.json().get("latest_ids", [])
                for cid in reversed(new_cids):
                    if cid not in st.session_state["live_cids"]:
                        st.session_state["live_cids"].insert(0, cid)
        except:
            st.warning("Failed to fetch latest content.")

    cards_per_row = 3
    cids = st.session_state["live_cids"]
    display_cids = cids[:st.session_state["load_count"]]

    for i in range(0, len(display_cids), cards_per_row):
        row = st.columns(cards_per_row)
        for j in range(cards_per_row):
            if i + j < len(display_cids):
                with row[j]: render_card(display_cids[i + j], i + j)

    if len(cids) > st.session_state["load_count"]:
        if st.button("⬇ Load More Posts"):
            st.session_state["load_count"] += 6
            st.experimental_rerun()

# ---------------- Leaderboard ----------------
elif tab == "Leaderboard":
    st.subheader("🏆 Most Liked Posts")
    try:
        r = requests.get(f"{API}/leaderboard")
        if r.status_code == 200 and r.json().get("ok"):
            top = r.json().get("top_liked", [])
            if not top:
                st.info("No liked posts yet. Be the first to like something!")
            else:
                cols = st.columns(2)
                for i, rec in enumerate(top):
                    with cols[i % 2]:
                        st.markdown(f"**@{rec['content_id']}**")
                        st.caption(f"👍 {rec['likes']} likes")
                        st.write(rec['text'])
                        st.markdown("---")
        else:
            st.error("Failed to load leaderboard.")
    except Exception as e:
        st.error(f"Error fetching leaderboard: {e}")

# ---------------- Transparency ----------------
elif tab == "Transparency":
    st.subheader("🌐 Global Transparency Feed")
    try:
        r = requests.get(f"{API}/pouw_rewards")
        if r.status_code == 200 and r.json().get("rewards"):
            rewards = r.json()["rewards"]
            st.dataframe(rewards)
        else:
            st.info("No global feed data available yet.")
    except Exception as e:
        st.error(f"Error fetching transparency feed: {e}")