import streamlit as st
import requests, time, os

# Use environment variable for API endpoint (or default to localhost for local testing)
API = os.environ.get("MOD_API", "http://localhost:5001")

st.set_page_config(page_title="Decentralized AI Moderation — Prototype", layout="wide")
st.title("🕸️ Decentralized AI Moderation — Prototype")

# ---------------- Sidebar: Controls ----------------
with st.sidebar:
    st.header("Controls / Governance")
    
    if st.button("Run Federated Round"):
        try:
            r = requests.post(f"{API}/federated_round")
            st.success(r.json())
        except Exception as e:
            st.error(f"Failed to run federated round: {e}")

    if st.button("Show PoUW Rewards"):
        try:
            r = requests.get(f"{API}/pouw_rewards")
            st.info(r.json())
        except Exception as e:
            st.error(f"Failed to fetch rewards: {e}")

    st.subheader("Preferences")
    moderation_level = st.selectbox("Moderation Sensitivity", ["Strict", "Medium", "Lenient"])
    show_proofs = st.checkbox("Show Proof Panels", True)

# ---------------- Columns ----------------
col1, col2 = st.columns([2, 3])

# --------------- Content Submission ----------------
with col1:
    st.subheader("Submit Content / Post")
    text = st.text_area("Write your post...", "I hate that this is violent!")
    attach_media = st.file_uploader("Attach Images/Videos", type=["png","jpg","mp4"], accept_multiple_files=True)
    
    if st.button("Submit for Moderation"):
        try:
            payload = {"text": text}
            r = requests.post(f"{API}/submit_content", json=payload)
            r.raise_for_status()
            cid = r.json().get("content_id")
            st.session_state["last_cid"] = cid
            st.success(f"Content submitted! Content ID: {cid}")
        except Exception as e:
            st.error(f"Submission failed: {e}")

# ---------------- Content Display ----------------
with col2:
    st.subheader("Content Feed & Proofs")
    cid = st.text_input("Enter Content ID to View", st.session_state.get("last_cid",""))
    
    if st.button("Load Post") and cid:
        try:
            r = requests.get(f"{API}/status/{cid}")
            r.raise_for_status()
            rec = r.json()["record"]

            # Content card
            st.markdown(f"### @{rec.get('content_id')} — {time.ctime(rec.get('ts'))}")
            st.write(rec.get("text"))

            # Moderation Badge
            inf = rec.get("inference", {})
            score = inf.get("score",0)
            label = inf.get("label","unknown")
            flags = inf.get("policy_flags",[])
            
            badge = "✅ Accepted" if label=="safe" else "⚠ Flagged" if label=="flagged" else "❌ Rejected"
            st.markdown(f"**Moderation:** {badge} | Confidence: {score*100:.1f}% | Flags: {','.join(flags)}")

            # Proof / Transparency Panel
            if show_proofs:
                st.markdown("#### Transparency & Proofs")
                st.markdown(f"- **Merkle Root:** {rec.get('merkle_root')}")
                st.markdown(f"- **VDF Delay:** {rec.get('vdf',{}).get('seconds')} seconds")
                st.markdown(f"- **ZKP Status:** {rec.get('zkp',{}).get('status')}")
                st.markdown(f"- **Blockchain Tx:** Placeholder link")

            # Engagement simulation
            st.markdown("#### Engagement")
            st.button("👍 Like")
            st.button("💬 Comment")
            st.button("🔗 Share")
            
            # Appeals
            if badge != "✅ Accepted":
                if st.button("File Transparent Appeal"):
                    st.info("Appeal submitted to community governance feed.")

        except Exception as e:
            st.error(f"Failed to load content: {e}")

# ---------------- Global Feed / Audit ----------------
st.markdown("---")
st.subheader("Global Transparency Feed (recently moderated posts)")
try:
    r = requests.get(f"{API}/pouw_rewards")  # Placeholder: Replace with actual global feed endpoint
    r.raise_for_status()
    rewards = r.json().get("rewards",[])
    if rewards:
        st.table(rewards)
    else:
        st.info("No global feed data available yet.")
except Exception as e:
    st.error(f"Failed to load global feed: {e}")
