import streamlit as st
import time
import hashlib
from backend import pouw  # make sure this path is correct

st.set_page_config(page_title="Decentralized AI Moderation - PoUW", layout="wide")

st.title("Decentralized AI Moderation Prototype - PoUW Demo")

# --- Submit Work Simulation ---
st.header("Submit Work")

node_id = st.text_input("Node ID", "node_1")
steps = st.number_input("Steps performed (simulated ML work)", min_value=1, value=1000)

if st.button("Submit Work"):
    # Generate a pseudo hash representing work updates
    updates_hash = hashlib.sha256(str(time.time()).encode()).hexdigest()
    
    # Submit work to PoUW
    event = pouw.submit_work(node_id=node_id, updates_hash=updates_hash, steps=steps)
    
    st.success("✅ Work submitted successfully!")
    st.markdown(f"- **Node ID:** {node_id}\n- **Reward:** {event['reward']} tokens\n- **Timestamp:** {event['ts']}")
    st.json(event)

# --- Show Aggregated Rewards ---
st.header("Aggregated PoUW Rewards")

agg_rewards = pouw.summarize_rewards()
if agg_rewards:
    st.table(agg_rewards)
else:
    st.info("No work submitted yet. Submit some work above to see rewards here.")
