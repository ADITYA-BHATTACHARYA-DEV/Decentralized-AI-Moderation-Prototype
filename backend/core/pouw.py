import streamlit as st
import time
import hashlib
from backend import pouw  # adjust import path if needed

st.title("Decentralized AI Moderation Prototype - PoUW Demo")

# --- Submit Work Simulation ---
st.header("Submit Work")

node_id = st.text_input("Node ID", "node_1")
steps = st.number_input("Steps performed (simulated ML work)", min_value=1, value=1000)

if st.button("Submit Work"):
    # Simulate an updates hash (placeholder for actual federated updates)
    updates_hash = hashlib.sha256(str(time.time()).encode()).hexdigest()
    
    event = pouw.submit_work(node_id=node_id, updates_hash=updates_hash, steps=steps)
    
    st.success(f"Work submitted!\nReward: {event['reward']} tokens\nTimestamp: {event['ts']}")
    st.json(event)

# --- Show Aggregated Rewards ---
st.header("Aggregated PoUW Rewards")
agg_rewards = pouw.summarize_rewards()
if agg_rewards:
    st.table(agg_rewards)
else:
    st.info("No work submitted yet.")
