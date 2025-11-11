#!/usr/bin/env python3
import datetime
import copy
import uuid
import random
import json
import base64
from typing import Dict, Any, List, Tuple

from .fake_data import first_names, last_names, email_bodies, email_subjects, email_snippets, domains, timezones, first_and_last_names, user_count

# Set a fixed start time for consistent "now" across the script
current_datetime = datetime.datetime.now()

DEFAULT_STATE: Dict[str, Any] = {
    "users": {},
}
_user_email_to_uuid_map: Dict[str, str] = {}

def generate_gmail_id() -> str:
    """Generates a Gmail-style hex ID (16 characters)."""
    return ''.join(random.choices('0123456789abcdef', k=16))

def generate_history_id() -> str:
    """Generates a history ID (large integer string)."""
    return str(random.randint(10**12, 10**13 - 1))

def generate_random_past_timestamp(max_days_ago=365) -> str:
    """Generates a random timestamp string in milliseconds from the past."""
    delta = datetime.timedelta(
        days=random.randint(1, max_days_ago),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    return str(int((current_datetime - delta).timestamp() * 1000))

def generate_email(first_name: str, last_name: str) -> str:
    """Generates a semi-random email address."""
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"

def _create_user_data(email: str, first_name: str, last_name: str, recipients_emails: List[str], gmail_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Processes raw generated data into the final user state, creating UUIDs and structuring data correctly.
    """
    user_id = str(uuid.uuid4())
    _user_email_to_uuid_map[email] = user_id

    processed_gmail_data = copy.deepcopy(gmail_data)

    # --- Process Messages: Assign final Gmail-style hex IDs ---
    new_messages = {}
    for _, msg_data in processed_gmail_data.get("messages", {}).items():
        new_msg_id = generate_gmail_id()
        msg_data["id"] = new_msg_id
        
        # Add missing realistic fields
        msg_data["historyId"] = generate_history_id()
        
        # Calculate size estimate
        body_data = msg_data.get("payload", {}).get("body", {}).get("data", "")
        headers = msg_data.get("payload", {}).get("headers", [])
        body_size = len(body_data)
        headers_size = sum(len(h.get("name", "") + h.get("value", "")) for h in headers)
        msg_data["sizeEstimate"] = body_size + headers_size + 100
        
        # Ensure payload has mimeType
        if "payload" in msg_data:
            msg_data["payload"]["mimeType"] = msg_data["payload"].get("mimeType", "text/plain")
            
            # Add Message-ID and Date headers if missing
            header_names = {h["name"] for h in headers}
            if "Message-ID" not in header_names:
                msg_data["payload"]["headers"].append({
                    "name": "Message-ID",
                    "value": f"<{new_msg_id}@mail.gmail.com>"
                })
            if "Date" not in header_names:
                msg_timestamp = int(msg_data.get("internalDate", "0"))
                date_str = datetime.datetime.fromtimestamp(msg_timestamp / 1000).strftime("%a, %d %b %Y %H:%M:%S %z")
                msg_data["payload"]["headers"].append({
                    "name": "Date",
                    "value": date_str
                })
            
            # Encode body data in base64url if not already
            if "body" in msg_data["payload"] and "data" in msg_data["payload"]["body"]:
                body_text = msg_data["payload"]["body"]["data"]
                if body_text and not all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=' for c in body_text):
                    msg_data["payload"]["body"]["data"] = base64.urlsafe_b64encode(body_text.encode('utf-8')).decode('utf-8')
                msg_data["payload"]["body"]["size"] = len(msg_data["payload"]["body"]["data"])
        
        # internalDate is already a string from generate_random_past_timestamp
        new_messages[new_msg_id] = msg_data
    processed_gmail_data["messages"] = new_messages

    # --- Process Threads: Group messages by their existing threadId, use hex IDs ---
    final_threads = {}
    thread_id_mapping = {}  # Map old thread IDs to new hex IDs
    
    for msg_id, msg_data in processed_gmail_data["messages"].items():
        old_thread_id = msg_data["threadId"]
        
        # Create new hex thread ID if we haven't seen this thread before
        if old_thread_id not in thread_id_mapping:
            thread_id_mapping[old_thread_id] = generate_gmail_id()
        
        thread_id = thread_id_mapping[old_thread_id]
        msg_data["threadId"] = thread_id  # Update message with new thread ID
        
        if thread_id not in final_threads:
            final_threads[thread_id] = {
                "id": thread_id,
                "messages": [],
                "snippet": "", # We'll set this to the latest message's snippet
                "historyId": generate_history_id(),
                "_latest_timestamp": 0
            }
        final_threads[thread_id]["messages"].append({"id": msg_id})
        
        # Determine the latest snippet for the thread
        current_msg_ts = int(msg_data["internalDate"])
        if current_msg_ts > final_threads[thread_id]["_latest_timestamp"]:
            final_threads[thread_id]["_latest_timestamp"] = current_msg_ts
            final_threads[thread_id]["snippet"] = msg_data.get("snippet", "No snippet available.")

    # Clean up temporary timestamp key
    for thread_id in final_threads:
        del final_threads[thread_id]["_latest_timestamp"]

    processed_gmail_data["threads"] = final_threads
    
    # --- Process Drafts and Labels with hex IDs ---
    new_drafts = {}
    for draft_data in processed_gmail_data.get("drafts", {}).values():
        draft_id = generate_gmail_id()
        draft_data["id"] = draft_id
        new_drafts[draft_id] = draft_data
    processed_gmail_data["drafts"] = new_drafts
    
    new_labels = {}
    for label_data in processed_gmail_data.get("labels", {}).values():
        label_id = generate_gmail_id()
        label_data["id"] = label_id
        new_labels[label_id] = label_data
    processed_gmail_data["labels"] = new_labels
    
    # Ensure default system labels exist
    default_system_labels = ["INBOX", "STARRED", "SPAM", "TRASH", "DRAFT", "SENT", "IMPORTANT", "UNREAD"]
    existing_label_names = {lbl["name"] for lbl in processed_gmail_data["labels"].values()}
    for label_name in default_system_labels:
        if label_name not in existing_label_names:
            label_id = generate_gmail_id()
            processed_gmail_data["labels"][label_id] = {
                "id": label_id, 
                "name": label_name, 
                "type": "system",
                "messageListVisibility": "show",
                "labelListVisibility": "labelShow"
            }

    # --- Final User Object ---
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "recipients": recipients_emails, # Still emails, will be resolved to UUIDs later
        "password_hash": uuid.uuid4().hex,
        "gmail_data": processed_gmail_data,
        "last_active": generate_random_past_timestamp(30),
        "timezone": random.choice(timezones),
    }
    return user_id, user_data

def generate_user_details(first_name: str, last_name: str, email: str, all_user_emails: List[str]) -> Dict[str, Any]:
    """Generates the detailed message and recipient data for a single user."""
    # Select a random number of recipients from the full list of users
    num_recipients = random.randint(2, 15)
    recipients_for_new_user = random.sample(
        [e for e in all_user_emails if e != email], 
        min(num_recipients, len(all_user_emails) - 1)
    )

    # Generate messages count first for realistic totals
    num_messages = random.randint(20, 70)
    
    new_gmail_data = {
        "profile": {
            "emailAddress": email,
            "messagesTotal": num_messages + random.randint(0, 50),  # Close to actual with small variance
            "threadsTotal": random.randint(max(1, num_messages // 4), num_messages // 2),  # Realistic thread count
            "historyId": str(random.randint(10**12, 10**13 - 1))
        },
        "drafts": {}, "labels": {}, "messages": {}, "threads": {}
    }

    # Generate a few random drafts with proper Gmail structure
    for _ in range(random.randint(0, 2)):
        draft_id = f"temp_draft_{uuid.uuid4()}"
        draft_msg_id = str(uuid.uuid4())
        new_gmail_data["drafts"][draft_id] = {
            "id": draft_id,
            "message": {
                "id": draft_msg_id,
                "threadId": draft_msg_id,
                "labelIds": ["DRAFT"],
                "snippet": "Draft message",
                "payload": {
                    "mimeType": "text/plain",
                    "body": {
                        "size": random.randint(50, 2000),
                        "data": ""
                    },
                    "headers": [
                        {"name": "To", "value": random.choice(all_user_emails)},
                        {"name": "From", "value": email},
                        {"name": "Subject", "value": random.choice(email_subjects)}
                    ]
                }
            }
        }

    # Generate a few random labels
    for _ in range(random.randint(0, 4)):
        label_id = f"temp_label_{uuid.uuid4()}"
        new_gmail_data["labels"][label_id] = {
            "id": label_id, "name": random.choice(["Work", "Personal", "Travel", "Urgent"]), "type": "user"
        }

    # Generate messages and group them into threads
    temp_messages = {}
    
    # Create realistic contact patterns: frequent contacts vs. random people
    frequent_contacts = random.sample(recipients_for_new_user, min(5, len(recipients_for_new_user)))
    occasional_contacts = [e for e in recipients_for_new_user if e not in frequent_contacts]
    random_contacts = [generate_email(random.choice(first_names), random.choice(last_names)) for _ in range(3)]
    
    all_possible_recipients = frequent_contacts + occasional_contacts + random_contacts

    for _ in range(num_messages):
        msg_id = f"temp_msg_{uuid.uuid4()}"
        
        # Realistic sender patterns: 60% received, 40% sent
        is_received = random.random() < 0.6
        
        if is_received:
            # Weight towards frequent contacts: 70% frequent, 20% occasional, 10% random
            sender_pool = random.choices(
                [frequent_contacts, occasional_contacts, random_contacts],
                weights=[70, 20, 10]
            )[0]
            sender = random.choice(sender_pool) if sender_pool else random.choice(all_possible_recipients)
            recipient = email
        else:
            # When sending, also favor frequent contacts
            sender = email
            recipient_pool = random.choices(
                [frequent_contacts, occasional_contacts, random_contacts],
                weights=[60, 30, 10]
            )[0]
            recipient = random.choice(recipient_pool) if recipient_pool else random.choice(all_possible_recipients)
        
        # Realistic label distribution
        label_ids = ["INBOX"] if recipient == email else ["SENT"]
        
        # More realistic percentages for labels
        if "INBOX" in label_ids:
            if random.random() < 0.15: label_ids.append("UNREAD")  # 15% unread (more realistic)
            if random.random() < 0.05: label_ids.append("IMPORTANT")  # 5% important
            if random.random() < 0.02: label_ids.append("SPAM")  # 2% spam
        
        if random.random() < 0.08: label_ids.append("STARRED")  # 8% starred (slightly more realistic)

        # Generate timestamp once for consistency
        message_timestamp = generate_random_past_timestamp(365)
        message_datetime = datetime.datetime.fromtimestamp(int(message_timestamp)/1000)
        
        temp_messages[msg_id] = {
            "id": msg_id, 
            "threadId": msg_id, # Default threadId to msgId
            "snippet": random.choice(email_snippets),
            "payload": {
                "mimeType": "text/plain",
                "body": {
                    "size": random.randint(100, 5000),
                    "data": ""  # Base64 encoded content would go here
                },
                "headers": [
                    {"name": "From", "value": sender}, 
                    {"name": "To", "value": recipient}, 
                    {"name": "Subject", "value": random.choice(email_subjects)},
                    {"name": "Date", "value": message_datetime.strftime("%a, %d %b %Y %H:%M:%S +0000")},
                    {"name": "Message-ID", "value": f"<{uuid.uuid4()}@gmail.com>"}
                ]
            },
            "internalDate": message_timestamp, 
            "labelIds": label_ids,
            "sizeEstimate": random.randint(1000, 8000)
        }
    
    # Create threads by grouping some messages with realistic patterns
    message_ids = list(temp_messages.keys())
    random.shuffle(message_ids)
    
    # Leave about 40% as single-message threads (realistic for Gmail)
    target_threaded_messages = int(len(message_ids) * 0.6)
    threaded_count = 0
    
    while threaded_count < target_threaded_messages and len(message_ids) >= 2:
        # Weighted thread sizes: 2(40%), 3(35%), 4(20%), 5(5%)
        thread_size = random.choices([2, 3, 4, 5], weights=[40, 35, 20, 5])[0]
        if len(message_ids) < thread_size: 
            thread_size = len(message_ids)
        
        thread_msg_ids = [message_ids.pop() for _ in range(thread_size)]
        thread_uuid = str(uuid.uuid4())
        for mid in thread_msg_ids:
            temp_messages[mid]["threadId"] = thread_uuid
        threaded_count += thread_size

    new_gmail_data["messages"] = temp_messages
    
    # Return all generated data for the user
    return _create_user_data(email, first_name, last_name, recipients_for_new_user, new_gmail_data)


def main():
    """Main function to generate and save the user data."""
    # --- PASS 1: Generate all user identities (name, email) first ---
    print("PASS 1: Generating user identities...")
    all_users_to_generate = []
    generated_emails = set()

    # Add users from the predefined list
    for name in first_and_last_names:
        first, _, last = name.partition(" ")
        all_users_to_generate.append({"first_name": first, "last_name": last})

    # Add randomly generated users
    for _ in range(user_count):
        all_users_to_generate.append({"first_name": random.choice(first_names), "last_name": random.choice(last_names)})
    
    # Assign a unique email to each user
    for user_info in all_users_to_generate:
        email = generate_email(user_info["first_name"], user_info["last_name"])
        while email in generated_emails:
            email = generate_email(user_info["first_name"], user_info["last_name"])
        generated_emails.add(email)
        user_info["email"] = email

    all_user_emails = list(generated_emails)
    print(f"Generated {len(all_user_emails)} unique user identities.")

    # --- PASS 2: Generate detailed data for each user ---
    print("\nPASS 2: Generating detailed user data (messages, threads, etc.)...")
    for user_info in all_users_to_generate:
        user_id, user_data = generate_user_details(
            user_info["first_name"], user_info["last_name"], user_info["email"], all_user_emails
        )
        DEFAULT_STATE["users"][user_id] = user_data
    
    print(f"Generated details for {len(DEFAULT_STATE['users'])} users.")

    # --- PASS 3: Resolve recipient emails to UUIDs ---
    print("\nPASS 3: Resolving recipient email addresses to user UUIDs...")
    for user_id, user_data in DEFAULT_STATE["users"].items():
        resolved_recipients = {
            _user_email_to_uuid_map[email] for email in user_data["recipients"] 
            if email in _user_email_to_uuid_map and _user_email_to_uuid_map[email] != user_id
        }
        user_data["recipients"] = list(resolved_recipients)

    # --- Save to file ---
    output_filename = 'diverse_gmail_state.json'
    print(f"\nSaving generated state to '{output_filename}'...")
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_STATE, f, indent=2, ensure_ascii=False, separators=(',', ': '))
        
        # Validate the saved JSON
        with open(output_filename, 'r', encoding='utf-8') as f:
            json.load(f)
        
        print(f"✓ Successfully saved and validated {len(DEFAULT_STATE['users'])} users")
        
        # Show file size
        import os
        file_size = os.path.getsize(output_filename)
        print(f"✓ File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
    except json.JSONEncodeError as e:
        print(f"✗ JSON encoding error: {e}")
    except Exception as e:
        print(f"✗ Error saving file: {e}")
    
    print("Done!")

if __name__ == "__main__":
    main()