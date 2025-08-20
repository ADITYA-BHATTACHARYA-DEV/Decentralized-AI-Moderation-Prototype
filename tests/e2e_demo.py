import requests, time, json

API = "http://localhost:5001"

def main():
    txt = "This is a test with hate and threat words."
    r = requests.post(f"{API}/submit_content", json={"text": txt})
    data = r.json()
    cid = data["content_id"]
    print("Submitted:", data)

    s = requests.get(f"{API}/status/{cid}").json()
    print("Status:", json.dumps(s, indent=2))

    fr = requests.post(f"{API}/federated_round").json()
    print("Fed round:", json.dumps(fr, indent=2))

    rw = requests.get(f"{API}/pouw_rewards").json()
    print("Rewards:", json.dumps(rw, indent=2))

if __name__ == "__main__":
    main()
