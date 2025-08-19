
import datetime
import copy
import uuid
import random
import json
from typing import Dict, Any
import json
from fake_data import first_names, last_names, email_bodies, email_subjects, email_snippets, domains
current_datetime = datetime.datetime.now()

DEFAULT_STATE: Dict[str, Any] = {
    "users": {},
}
_user_email_to_uuid_map = {}

def generate_random_past_timestamp(max_days_ago=365):
    days_ago = random.randint(1, max_days_ago)
    return str(int((current_datetime - datetime.timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).timestamp() * 1000))

def generate_future_timestamp(max_days_from_now=365):
    days_from_now = random.randint(1, max_days_from_now)
    return str(int((current_datetime + datetime.timedelta(days=days_from_now, hours=random.randint(0, 23), minutes=random.randint(0, 59))).timestamp() * 1000))

def generate_email(first_name, last_name):
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"

def _create_user_data(email, first_name, last_name, recipients_emails, gmail_data):
    user_id = str(uuid.uuid4())
    _user_email_to_uuid_map[email] = user_id
    recipients_ids = recipients_emails
    processed_gmail_data = copy.deepcopy(gmail_data)
    new_messages = {}
    original_message_id_map = {}
    for msg_id_old, msg_data in processed_gmail_data.get("messages", {}).items():
        new_msg_id = str(uuid.uuid4())
        original_message_id_map[msg_id_old] = new_msg_id
        msg_data["id"] = new_msg_id
        msg_data["threadId"] = str(uuid.uuid4())
        if "internalDate" in msg_data and isinstance(msg_data["internalDate"], datetime.datetime):
            msg_data["internalDate"] = str(int(msg_data["internalDate"].timestamp() * 1000))
        elif "internalDate" not in msg_data:
            msg_data["internalDate"] = generate_random_past_timestamp()
        if "payload" not in msg_data:
            msg_data["payload"] = {"headers": []}
        if "headers" not in msg_data["payload"]:
            msg_data["payload"]["headers"] = []
        new_messages[new_msg_id] = msg_data
    processed_gmail_data["messages"] = new_messages
    final_threads = {}
    old_thread_to_new_thread_map = {}
    for msg_id_new, msg_data in processed_gmail_data["messages"].items():
        original_thread_id = None
        for old_thread_id, old_thread_data in gmail_data.get("threads", {}).items():
            if any(m.get("id") == msg_data.get("original_id") for m in old_thread_data.get("messages", [])):
                original_thread_id = old_thread_id
                break
        if original_thread_id:
            if original_thread_id not in old_thread_to_new_thread_map:
                old_thread_to_new_thread_map[original_thread_id] = str(uuid.uuid4())
            msg_data["threadId"] = old_thread_to_new_thread_map[original_thread_id]
        thread_id = msg_data["threadId"]
        if thread_id not in final_threads:
            final_threads[thread_id] = {"id": thread_id, "snippet": msg_data.get("snippet", "No snippet"), "messages": [], "historyId": str(random.randint(1000000000000, 9999999999999))}
        final_threads[thread_id]["messages"].append({"id": msg_id_new})
        current_snippet_ts = int(msg_data["internalDate"])
        thread_snippet_ts = int(final_threads[thread_id].get("snippet_timestamp", 0))
        if current_snippet_ts > thread_snippet_ts:
             final_threads[thread_id]["snippet"] = msg_data.get("snippet", "No snippet")
             final_threads[thread_id]["snippet_timestamp"] = current_snippet_ts
    processed_gmail_data["threads"] = final_threads
    new_drafts = {}
    for _, draft_data in processed_gmail_data.get("drafts", {}).items():
        new_draft_id = str(uuid.uuid4())
        draft_data["id"] = new_draft_id
        if "to" not in draft_data["message"]:
             draft_data["message"]["to"] = random.choice(["colleague@hostinger.com", "client@hostinger.net"])
        if "from" not in draft_data["message"]:
             draft_data["message"]["from"] = email
        new_drafts[new_draft_id] = draft_data
    processed_gmail_data["drafts"] = new_drafts
    new_labels = {}
    for _, label_data in processed_gmail_data.get("labels", {}).items():
        new_label_id = str(uuid.uuid4())
        label_data["id"] = new_label_id
        new_labels[new_label_id] = label_data
    processed_gmail_data["labels"] = new_labels
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
        "recipients": recipients_ids,
        "password_hash": uuid.uuid4().hex + ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16)),
        "gmail_data": processed_gmail_data,
        "last_active": generate_random_past_timestamp(30),
        "timezone": random.choice(["America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"]),
    }

current_user_emails = list(_user_email_to_uuid_map.keys())

for i in range(47):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = generate_email(first, last)
    while email in _user_email_to_uuid_map:
        email = generate_email(first, last)
    num_recipients = random.randint(0, 5)
    possible_recipients_emails = list(_user_email_to_uuid_map.keys())
    recipients_for_new_user = random.sample(possible_recipients_emails, min(num_recipients, len(possible_recipients_emails)))
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
    num_drafts = random.randint(0, 2)
    for _ in range(num_drafts):
        draft_id = str(uuid.uuid4())
        new_gmail_data["drafts"][draft_id] = {
            "id": draft_id,
            "message": {
                "to": generate_email(random.choice(first_names), random.choice(last_names)),
                "from": email,
                "subject": random.choice(email_subjects),
                "body": random.choice(email_bodies).format(
                    sender_name=f"{first} {last}",
                    sender_first=first,
                    recipient_type=random.choice(["colleague", "client", "team", "partner"])
                )
            }
        }
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
    
    num_messages = random.randint(5, 50)
    user_message_ids = []

    first2 = random.choice(first_names)
    last2 = random.choice(last_names)
    all_possible_recipients = list(_user_email_to_uuid_map.keys()) + [generate_email(first2, last2)]
    
    for msg_idx in range(num_messages):
        msg_id_old_placeholder = f"temp_msg_{i}_{msg_idx}"
        sender = random.choice([email, random.choice(recipients_for_new_user) if recipients_for_new_user else generate_email("random", "sender")])
        recipient = random.choice([email, random.choice(all_possible_recipients)])
        headers = [
            {"name": "From", "value": sender},
            {"name": "To", "value": recipient},
            {"name": "Subject", "value": random.choice(email_subjects)}
        ]
        is_unread = random.random() < 0.3
        label_ids = ["INBOX"]
        if is_unread:
            label_ids.append("UNREAD")
        if random.random() < 0.1:
            label_ids.append("STARRED")
        if random.random() < 0.05:
            label_ids.append("SPAM")
        new_gmail_data["messages"][msg_id_old_placeholder] = {
            "id": msg_id_old_placeholder,
            "threadId": f"temp_thread_{i}_{msg_idx}",
            "snippet": random.choice(email_snippets),
            "payload": {"headers": headers},
            "internalDate": generate_random_past_timestamp(365),
            "labelIds": label_ids,
            "original_id": msg_id_old_placeholder,
        }
        user_message_ids.append(msg_id_old_placeholder)
    num_threads_to_create = random.randint(min(5, num_messages // 2), min(15, num_messages // 2))
    threads_dict_for_user = {}
    if user_message_ids:
        for _ in range(num_threads_to_create // 2):
            if len(user_message_ids) >= 2:
                thread_msg_ids = random.sample(user_message_ids, random.randint(2, min(5, len(user_message_ids))) )
                thread_uuid = str(uuid.uuid4())
                for mid in thread_msg_ids:
                    new_gmail_data["messages"][mid]["threadId"] = thread_uuid
                user_message_ids = [m for m in user_message_ids if m not in thread_msg_ids]
        for msg_id in user_message_ids:
            new_gmail_data["messages"][msg_id]["threadId"] = str(uuid.uuid4())
    user_id, user_data = _create_user_data(email, first, last, recipients_for_new_user, new_gmail_data)
    DEFAULT_STATE["users"][user_id] = user_data
    current_user_emails.append(email)

all_user_uuids = list(_user_email_to_uuid_map.values())

for user_id, user_data in DEFAULT_STATE["users"].items():
    resolved_recipients = []
    for recipient_item in user_data["recipients"]:
        if recipient_item in _user_email_to_uuid_map:
            resolved_recipients.append(_user_email_to_uuid_map[recipient_item])
        elif recipient_item in all_user_uuids:
            resolved_recipients.append(recipient_item)
    user_data["recipients"] = list(set([f for f in resolved_recipients if f != user_id]))

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")

output_filename = 'diverse_gmail_state.json'

with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

if DEFAULT_STATE["users"]:
    sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(0, len(DEFAULT_STATE["users"]) - 1)]
    print(f"\nSample data for user {DEFAULT_STATE['users'][sample_user_id]['first_name']} {DEFAULT_STATE['users'][sample_user_id]['last_name']}:")
    print(json.dumps(DEFAULT_STATE["users"][sample_user_id], indent=2))