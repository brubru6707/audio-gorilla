import uuid
import time
import random
import json
from datetime import datetime, timedelta

"""Slack Backend Generator

Generates a DEFAULT_STATE compatible with SlackApis.py for demos and tests.
The data model is intentionally lightweight – if SlackApis grows new features,
just regenerate this file with additional keys.
"""

_users = [
    {"id": "U001", "name": "alice", "real_name": "Alice Johnson", "email": "alice.johnson@gmail.com"},
    {"id": "U002", "name": "bob", "real_name": "Robert Lee", "email": "robert.lee@outlook.com"},
    {"id": "U003", "name": "carol", "real_name": "Carol Garcia", "email": "carol.garcia@yahoo.com"},
    {"id": "U004", "name": "dave", "real_name": "David Smith", "email": "david.smith@fastmail.com"},
    {"id": "U005", "name": "eve", "real_name": "Evelyn Chen", "email": "evelyn.chen@icloud.com"},
]

# Generate additional users for a richer workspace
first_names = ["Liam", "Olivia", "Noah", "Emma", "Ava", "William", "Sophia", "James", "Isabella", "Benjamin",
               "Mia", "Lucas", "Charlotte", "Mason", "Amelia", "Ethan", "Harper", "Alexander", "Evelyn", "Henry"]
last_names = ["Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White",
              "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee"]
email_domains = ["gmail.com", "yahoo.com", "outlook.com", "proton.me", "icloud.com"]

for idx in range(6, 36):  # create 30 total users
    first = random.choice(first_names)
    last = random.choice(last_names)
    uid = f"U{idx:03d}"
    _users.append({
        "id": uid,
        "name": first.lower(),
        "real_name": f"{first} {last}",
        "email": f"{first.lower()}.{last.lower()}@{random.choice(email_domains)}"
    })

_channels = [
    {"id": "C001", "name": "general", "is_channel": True, "topic": "General discussion", "purpose": "Company-wide chatter"},
    {"id": "C002", "name": "random", "is_channel": True, "topic": "Random", "purpose": "Non-work banter"},
]

# Add more public project channels
project_names = ["frontend", "backend", "design", "marketing", "sales", "support", "devops", "research"]
for pname in project_names:
    cid = f"C{uuid.uuid4().hex[:6]}"
    _channels.append({"id": cid, "name": pname, "is_channel": True, "topic": f"{pname.title()} discussions", "purpose": f"All about {pname}"})

# Generate a couple of IM / MPIM channels for flavour
for u in ["U003", "U004"]:
    cid = f"D{uuid.uuid4().hex[:6]}"
    _channels.append({"id": cid, "is_im": True, "user": u, "users": [u]})

messages: list[dict] = []
threads: dict[str, list] = {}

# Generate 500 random messages across channels
for _ in range(500):
    channel = random.choice(_channels)["id"]
    ts = str(time.time())
    user = random.choice(_users)["id"]
    message = {
        "type": "message",
        "user": user,
        "text": random.choice([
            "Hello world!", "How's it going?", "Did you deploy the fix?",
            "Lunch time", "🚀", "Anyone up for coffee?",
        ]),
        "ts": ts,
        "channel": channel,
    }
    messages.append(message)

    # Maybe turn it into a thread reply
    if random.random() < 0.25:
        thread_ts = message["ts"]
        num_replies = random.randint(1, 3)
        threads[thread_ts] = []
        for _ in range(num_replies):
            reply_ts = str(time.time())
            reply = {
                "type": "message",
                "user": random.choice(_users)["id"],
                "text": random.choice(["👍", "Sounds good", "I'll check."]),
                "ts": reply_ts,
                "channel": channel,
                "thread_ts": thread_ts,
            }
            threads[thread_ts].append(reply)
            messages.append(reply)

# Simple reminder store
reminders = {}
for uid in ["U001", "U002"]:
    rid = f"R{uuid.uuid4().hex[:6]}"
    reminders[rid] = {
        "id": rid,
        "user": uid,
        "text": "Stand-up meeting",
        "time": int(time.time()) + 3600,
        "complete": False,
    }

DEFAULT_STATE = {
    "users": {u["id"]: u for u in _users},
    "channels": {c["id"]: c for c in _channels},
    "messages": messages,
    "threads": threads,
    "reminders": reminders,
    "files": {},
    "reactions": {},
    "pins": {c["id"]: [] for c in _channels},
    "dnd": {u["id"]: {"dnd_enabled": False} for u in _users},
    "emoji": {":wave:": "https://emoji.url/wave.png", ":tada:": "https://emoji.url/tada.png"},
    "team_info": {"id": "T123", "name": "Mock Team", "domain": "mockteam"},
    "generated_at": datetime.utcnow().isoformat() + "Z",
}

if __name__ == "__main__":
    print("Slack backend generated 💬")
    print(f"Users     : {len(DEFAULT_STATE['users'])}")
    print(f"Channels  : {len(DEFAULT_STATE['channels'])}")
    print(f"Messages  : {len(DEFAULT_STATE['messages'])}")

    # with open('diverse_slack_state.json', 'w') as f:
    #     json.dump(DEFAULT_STATE, f, indent=2) 