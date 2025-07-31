import datetime
import copy
import uuid
import random
import json
from typing import Dict, List, Any, Optional, Union

# Current time for realistic date generation
current_datetime = datetime.datetime.now()

DEFAULT_STATE: Dict[str, Any] = {
    "users": {},
}

_user_email_to_uuid_map = {} # Global map to resolve email to UUIDs

def generate_random_past_timestamp(max_days_ago=365):
    days_ago = random.randint(1, max_days_ago)
    return str(int((current_datetime - datetime.timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).timestamp() * 1000))

def generate_future_timestamp(max_days_from_now=365):
    days_from_now = random.randint(1, max_days_from_now)
    return str(int((current_datetime + datetime.timedelta(days=days_from_now, hours=random.randint(0, 23), minutes=random.randint(0, 59))).timestamp() * 1000))

def generate_email(first_name, last_name):
    domains = ["example.com", "mail.net", "corp.org", "outlook.biz", "email.co"]
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"

def _create_user_data(email, first_name, last_name, friends_emails, gmail_data):
    user_id = str(uuid.uuid4())
    _user_email_to_uuid_map[email] = user_id

    # Friends emails will be resolved to UUIDs after all users are created
    friends_ids = friends_emails

    processed_gmail_data = copy.deepcopy(gmail_data)
    
    # --- Process messages ---
    new_messages = {}
    original_message_id_map = {} # Map original message ID to new UUID
    for msg_id_old, msg_data in processed_gmail_data.get("messages", {}).items():
        new_msg_id = str(uuid.uuid4())
        original_message_id_map[msg_id_old] = new_msg_id # Store mapping
        msg_data["id"] = new_msg_id
        msg_data["threadId"] = str(uuid.uuid4()) # Each message gets a new threadId initially
        
        # Ensure internalDate is a string representing milliseconds timestamp
        if "internalDate" in msg_data and isinstance(msg_data["internalDate"], datetime.datetime):
            msg_data["internalDate"] = str(int(msg_data["internalDate"].timestamp() * 1000))
        elif "internalDate" not in msg_data:
            msg_data["internalDate"] = generate_random_past_timestamp()
            
        # Add basic headers if missing for realism
        if "payload" not in msg_data:
            msg_data["payload"] = {"headers": []}
        if "headers" not in msg_data["payload"]:
            msg_data["payload"]["headers"] = []

        new_messages[new_msg_id] = msg_data
    processed_gmail_data["messages"] = new_messages

    # --- Rebuild threads with new message IDs and consistent thread IDs ---
    final_threads = {}
    
    # First pass: map old thread IDs to new thread IDs and assign messages
    old_thread_to_new_thread_map = {}
    for msg_id_new, msg_data in processed_gmail_data["messages"].items():
        # If this message was part of an old thread, ensure its new threadId is consistent
        original_thread_id = None
        for old_thread_id, old_thread_data in gmail_data.get("threads", {}).items():
            if any(m.get("id") == msg_data.get("original_id") for m in old_thread_data.get("messages", [])):
                original_thread_id = old_thread_id
                break

        if original_thread_id:
            if original_thread_id not in old_thread_to_new_thread_map:
                old_thread_to_new_thread_map[original_thread_id] = str(uuid.uuid4())
            msg_data["threadId"] = old_thread_to_new_thread_map[original_thread_id]
        else:
            # If it wasn't part of an old thread, it keeps its randomly assigned new threadId
            pass
        
        thread_id = msg_data["threadId"]
        if thread_id not in final_threads:
            final_threads[thread_id] = {"id": thread_id, "snippet": msg_data.get("snippet", "No snippet"), "messages": [], "historyId": str(random.randint(1000000000000, 9999999999999))}
        final_threads[thread_id]["messages"].append({"id": msg_id_new})
        
        # Update thread snippet to be the latest message's snippet (or earliest unread)
        # This is a simplification; real Gmail thread snippets are more complex
        current_snippet_ts = int(msg_data["internalDate"])
        thread_snippet_ts = int(final_threads[thread_id].get("snippet_timestamp", 0))

        if current_snippet_ts > thread_snippet_ts:
             final_threads[thread_id]["snippet"] = msg_data.get("snippet", "No snippet")
             final_threads[thread_id]["snippet_timestamp"] = current_snippet_ts


    processed_gmail_data["threads"] = final_threads

    # --- Process drafts ---
    new_drafts = {}
    for draft_id_old, draft_data in processed_gmail_data.get("drafts", {}).items():
        new_draft_id = str(uuid.uuid4())
        draft_data["id"] = new_draft_id
        # Ensure 'to' and 'from' fields are populated for drafts for realism
        if "to" not in draft_data["message"]:
             draft_data["message"]["to"] = random.choice(["colleague@hostinger.com", "client@hostinger.net"])
        if "from" not in draft_data["message"]:
             draft_data["message"]["from"] = email # Drafts are from the current user
        new_drafts[new_draft_id] = draft_data
    processed_gmail_data["drafts"] = new_drafts
    
    # --- Process labels ---
    new_labels = {}
    for label_id_old, label_data in processed_gmail_data.get("labels", {}).items():
        new_label_id = str(uuid.uuid4()) # Labels can also have UUIDs for consistency
        label_data["id"] = new_label_id
        new_labels[new_label_id] = label_data
    processed_gmail_data["labels"] = new_labels

    # Add default system labels if missing from the initial data
    default_system_labels = ["INBOX", "STARRED", "SPAM", "TRASH", "DRAFT", "SENT", "IMPORTANT", "UNREAD"]
    for sys_label in default_system_labels:
        if sys_label not in [lbl_data["name"] for lbl_data in processed_gmail_data["labels"].values()]:
            processed_gmail_data["labels"][str(uuid.uuid4())] = {
                "id": str(uuid.uuid4()),
                "name": sys_label,
                "messageListVisibility": "show",
                "labelListVisibility": "labelShow",
                "type": "system"
            }


    return user_id, {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "friends": friends_ids, # These will be resolved to UUIDs later
        "password_hash": "dummy_hash",
        "gmail_data": processed_gmail_data,
        "last_active": generate_random_past_timestamp(30), # New field: last active timestamp
        "timezone": random.choice(["America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"]), # New field
        "is_premium_user": random.choice([True, False, False]), # New field, 33% chance
    }

# --- Initial Users (provided in the prompt) ---
users_initial_data = [
    ("alice.smith@hostinger.net", "Alice", "Smith", ["bob.johnson@hostinger.com", "charlie.davis@hostinger.org"], {
        "profile": {
            "emailAddress": "alice.smith@hostinger.net",
            "messagesTotal": 1500,
            "threadsTotal": 500,
            "historyId": "9876543210987"
        },
        "drafts": {
            "draft_abc_123": {
                "id": "draft_abc_123",
                "message": {
                    "to": "project.team@hostinger.com",
                    "subject": "Project Status Update",
                    "body": "Hi team, here's the latest on our project. We're on track for completion."
                }
            }
        },
        "labels": {
            "label_important_client": {
                "id": "label_important_client",
                "name": "Important Clients",
                "messageListVisibility": "show",
                "labelListVisibility": "show",
                "type": "user"
            }
        },
        "messages": {
            "msg_1": {
                "id": "msg_1",
                "threadId": "thread_1",
                "snippet": "Meeting tomorrow at 10 AM.",
                "payload": {"headers": [{"name": "Subject", "value": "Meeting"}]},
                "internalDate": current_datetime.timestamp() * 1000 - random.randint(1000, 100000000), # Ensure it's a number for processing, then converted to string
                "labelIds": ["INBOX", "UNREAD"],
                "original_id": "msg_1", # Keep original_id to link back to threads
            },
            "msg_2": {
                "id": "msg_2",
                "threadId": "thread_1",
                "snippet": "Don't forget the deadline.",
                "payload": {"headers": [{"name": "Subject", "value": "Deadline"}]},
                "internalDate": (current_datetime - datetime.timedelta(days=1)).timestamp() * 1000 - random.randint(1000, 100000000),
                "labelIds": ["INBOX", "UNREAD"],
                "original_id": "msg_2",
            }
        },
        "threads": {
            "thread_1": {
                "id": "thread_1",
                "snippet": "Meeting tomorrow at 10 AM.",
                "messages": [{"id": "msg_1"}, {"id": "msg_2"}],
                "historyId": "9876543210989"
            }
        }
    }),
    ("bob.johnson@hostinger.com", "Bob", "Johnson", ["alice.smith@hostinger.net"], {
        "profile": {
            "emailAddress": "bob.johnson@hostinger.com",
            "messagesTotal": 800,
            "threadsTotal": 300,
            "historyId": "1234567890123"
        },
        "drafts": {},
        "labels": {
            "label_personal": {
                "id": "label_personal",
                "name": "Personal",
                "messageListVisibility": "show",
                "labelListVisibility": "show",
                "type": "user"
            }
        },
        "messages": {
            "msg_3": {
                "id": "msg_3",
                "threadId": "thread_2",
                "snippet": "Project update.",
                "payload": {"headers": [{"name": "Subject", "value": "Project"}]},
                "internalDate": current_datetime.timestamp() * 1000 - random.randint(1000, 100000000),
                "labelIds": ["INBOX"],
                "original_id": "msg_3",
            }
        },
        "threads": {
            "thread_2": {
                "id": "thread_2",
                "snippet": "Project update.",
                "messages": [{"id": "msg_3"}],
                "historyId": "1234567890125"
            }
        }
    }),
    ("charlie.davis@hostinger.org", "Charlie", "Davis", ["alice.smith@hostinger.net"], {
        "profile": {
            "emailAddress": "charlie.davis@hostinger.org",
            "messagesTotal": 300,
            "threadsTotal": 100,
            "historyId": "0987654321098"
        },
        "drafts": {},
        "labels": {},
        "messages": {},
        "threads": {}
    })
]

# Populate initial users
for email, first_name, last_name, friends_emails, gmail_data in users_initial_data:
    user_id, user_data = _create_user_data(email, first_name, last_name, friends_emails, gmail_data)
    DEFAULT_STATE["users"][user_id] = user_data

# --- Generate 47 more diverse and realistic users ---
first_names = ["Sophia", "Liam", "Olivia", "Noah", "Ava", "Jackson", "Isabella", "Aiden", "Mia", "Lucas", "Harper", "Ethan", "Evelyn", "Mason", "Abigail", "Caleb", "Charlotte", "Logan", "Amelia", "Michael", "Ella", "Jacob", "Aria", "Daniel", "Chloe", "Samuel", "Grace", "David", "Victoria", "Joseph", "Penelope", "Matthew", "Riley", "Benjamin", "Layla", "Andrew", "Lily", "Gabriel", "Natalie", "Christopher", "Hannah", "James", "Zoe", "Ryan", "Scarlett", "Nathan", "Addison", "Christian", "Aubrey", "Joshua"]
last_names = ["Chen", "Kim", "Singh", "Lopez", "Garcia", "Nguyen", "Davis", "Jackson", "Harris", "White", "Moore", "Clark", "Lewis", "Baker", "Adams", "Hill", "Nelson", "Carter", "Mitchell", "Roberts", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders"]

current_user_emails = list(_user_email_to_uuid_map.keys())

for i in range(47): # Generate 47 additional users (3 existing + 47 new = 50 total)
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = generate_email(first, last)
    
    # Ensure unique email
    while email in _user_email_to_uuid_map:
        email = generate_email(first, last)

    # Select friends from existing users
    num_friends = random.randint(0, 5)
    possible_friends_emails = list(_user_email_to_uuid_map.keys())
    # Ensure they don't add themselves as a friend and try to add existing users
    friends_for_new_user = random.sample(possible_friends_emails, min(num_friends, len(possible_friends_emails)))

    # Generate realistic Gmail data
    new_gmail_data = {
        "profile": {
            "emailAddress": email,
            "messagesTotal": random.randint(50, 5000),
            "threadsTotal": random.randint(20, 1500),
            "historyId": str(random.randint(1000000000000, 9999999999999))
        },
        "drafts": {},
        "labels": {},
        "messages": {},
        "threads": {}
    }

    # Add random drafts
    num_drafts = random.randint(0, 2)
    for _ in range(num_drafts):
        draft_id = str(uuid.uuid4())
        new_gmail_data["drafts"][draft_id] = {
            "id": draft_id,
            "message": {
                "to": generate_email(random.choice(first_names), random.choice(last_names)),
                "from": email,
                "subject": random.choice(["Follow up on meeting", "Question about project X", "Regarding your inquiry", "Draft email for client"]),
                "body": "This is a draft message. [Placeholder for content]"
            }
        }

    # Add random labels
    num_labels = random.randint(0, 4)
    for _ in range(num_labels):
        label_id = str(uuid.uuid4())
        label_name = random.choice(["Work", "Personal", "Family", "Receipts", "Travel", "Urgent", "Archive"])
        new_gmail_data["labels"][label_id] = {
            "id": label_id,
            "name": label_name,
            "messageListVisibility": random.choice(["show", "hide"]),
            "labelListVisibility": random.choice(["labelShow", "labelHide"]),
            "type": "user"
        }
    
    # Add random messages and threads
    num_messages = random.randint(5, 50)
    user_message_ids = [] # To link messages within threads later
    all_possible_recipients = list(_user_email_to_uuid_map.keys()) + [generate_email("external", "user")] # Include external too

    for msg_idx in range(num_messages):
        msg_id_old_placeholder = f"temp_msg_{i}_{msg_idx}" # Use temporary IDs for internal _create_user_data logic
        sender = random.choice([email, random.choice(friends_for_new_user) if friends_for_new_user else generate_email("random", "sender")])
        recipient = random.choice([email, random.choice(all_possible_recipients)])
        
        # Ensure 'from' and 'to' headers are present in payload
        headers = [
            {"name": "From", "value": sender},
            {"name": "To", "value": recipient},
            {"name": "Subject", "value": random.choice(["Hello!", "Re: Your question", "Meeting reminder", "Update", "Checking in", "Fwd: Interesting article"])}
        ]
        
        # Determine if it's an unread message
        is_unread = random.random() < 0.3 # 30% chance of being unread
        label_ids = ["INBOX"]
        if is_unread:
            label_ids.append("UNREAD")
        if random.random() < 0.1: # 10% chance of being starred
            label_ids.append("STARRED")
        if random.random() < 0.05: # 5% chance of being spam
            label_ids.append("SPAM")

        new_gmail_data["messages"][msg_id_old_placeholder] = {
            "id": msg_id_old_placeholder, # This will be replaced by UUID
            "threadId": f"temp_thread_{i}_{msg_idx}", # This will be replaced by UUID
            "snippet": random.choice(["Just checking in.", "Acknowledged.", "Will do.", "Thanks!", "Got it."]),
            "payload": {"headers": headers},
            "internalDate": generate_random_past_timestamp(365),
            "labelIds": label_ids,
            "original_id": msg_id_old_placeholder,
        }
        user_message_ids.append(msg_id_old_placeholder)

    # Simulate conversations by linking some messages into threads
    num_threads_to_create = random.randint(min(5, num_messages // 2), min(15, num_messages // 2))
    
    # Ensure messages that should be in the same thread actually are
    threads_dict_for_user = {}
    if user_message_ids:
        # Create some multi-message threads
        for _ in range(num_threads_to_create // 2):
            if len(user_message_ids) >= 2:
                thread_msg_ids = random.sample(user_message_ids, random.randint(2, min(5, len(user_message_ids))))
                thread_uuid = str(uuid.uuid4())
                for mid in thread_msg_ids:
                    # Update the temporary threadId in the message data
                    new_gmail_data["messages"][mid]["threadId"] = thread_uuid
                
                # Remove these messages from the pool so they don't form new threads
                user_message_ids = [m for m in user_message_ids if m not in thread_msg_ids]
    
        # Any remaining messages that didn't get grouped into a multi-message thread become single-message threads
        for msg_id in user_message_ids:
            new_gmail_data["messages"][msg_id]["threadId"] = str(uuid.uuid4())


    # The _create_user_data function will handle the final UUID generation for messages and threads.
    user_id, user_data = _create_user_data(email, first, last, friends_for_new_user, new_gmail_data)
    DEFAULT_STATE["users"][user_id] = user_data
    current_user_emails.append(email) # Add new user to possible friends for subsequent users


# --- Final Resolution of Friends (needed because some friends might have been added later) ---
all_user_uuids = list(_user_email_to_uuid_map.values())
for user_id, user_data in DEFAULT_STATE["users"].items():
    resolved_friends = []
    for friend_item in user_data["friends"]:
        if friend_item in _user_email_to_uuid_map: # Check if it's an email that has a UUID now
            resolved_friends.append(_user_email_to_uuid_map[friend_item])
        elif friend_item in all_user_uuids: # Already a UUID
            resolved_friends.append(friend_item)
        # If it's an email that wasn't found (e.g., placeholder for non-Gmail user), or an invalid ID, skip it
    
    # Ensure friends list only contains valid UUIDs and no duplicates, and not self
    user_data["friends"] = list(set([f for f in resolved_friends if f != user_id]))


# --- Output the generated DEFAULT_STATE ---
# This part is crucial: we are printing the full, static DEFAULT_STATE
# to a JSON file so you can load it consistently.
import json

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")

output_filename = 'diverse_gmail_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

# print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

# Optionally, print a sample user's data for review
# if DEFAULT_STATE["users"]:
#     sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(0, len(DEFAULT_STATE["users"]) - 1)]
#     print(f"\nSample data for user {DEFAULT_STATE['users'][sample_user_id]['first_name']} {DEFAULT_STATE['users'][sample_user_id]['last_name']}:")
#     print(json.dumps(DEFAULT_STATE["users"][sample_user_id], indent=2))
