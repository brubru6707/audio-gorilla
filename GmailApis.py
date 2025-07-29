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
             draft_data["message"]["to"] = random.choice(["colleague@example.com", "client@example.net"])
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
    ("alice.smith@example.net", "Alice", "Smith", ["bob.johnson@example.com", "charlie.davis@example.org"], {
        "profile": {
            "emailAddress": "alice.smith@example.net",
            "messagesTotal": 1500,
            "threadsTotal": 500,
            "historyId": "9876543210987"
        },
        "drafts": {
            "draft_abc_123": {
                "id": "draft_abc_123",
                "message": {
                    "to": "project.team@example.com",
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
    ("bob.johnson@example.com", "Bob", "Johnson", ["alice.smith@example.net"], {
        "profile": {
            "emailAddress": "bob.johnson@example.com",
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
    ("charlie.davis@example.org", "Charlie", "Davis", ["alice.smith@example.net"], {
        "profile": {
            "emailAddress": "charlie.davis@example.org",
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

# Save the generated DEFAULT_STATE to a JSON file
# output_filename = 'diverse_gmail_state.json'
# with open(output_filename, 'w') as f:
#     json.dump(DEFAULT_STATE, f, indent=2)

print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

# Optionally, print a sample user's data for review
# if DEFAULT_STATE["users"]:
#     sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(0, len(DEFAULT_STATE["users"]) - 1)]
#     print(f"\nSample data for user {DEFAULT_STATE['users'][sample_user_id]['first_name']} {DEFAULT_STATE['users'][sample_user_id]['last_name']}:")
#     print(json.dumps(DEFAULT_STATE["users"][sample_user_id], indent=2))

class GmailApis:
    """
    A dummy API class for simulating Gmail operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the Gmail API, which provides core functionality for managing emails, drafts, and labels."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        DEFAULT_STATE_COPY = copy.deepcopy(DEFAULT_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        print("GmailApis: Loaded scenario with users and their UUIDs.")

    def _generate_id(self) -> str:
        return str(uuid.uuid4())

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _get_user_gmail_data(self, user_id: str) -> Optional[Dict]:
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return None
        return self.users.get(internal_user_id, {}).get("gmail_data")

    def _get_user_threads_data(self, user_id: str) -> Optional[Dict]:
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("threads") if gmail_data else None

    def _get_user_messages_data(self, user_id: str) -> Optional[Dict]:
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("messages") if gmail_data else None

    def _get_user_drafts_data(self, user_id: str) -> Optional[Dict]:
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("drafts") if gmail_data else None

    def _get_user_labels_data(self, user_id: str) -> Optional[Dict]:
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("labels") if gmail_data else None

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return None
        
        user_data = self.users.get(internal_user_id)
        return user_data.get("gmail_data", {}).get("profile") if user_data else None

    def list_messages(
        self,
        user_id: str,
        query: Optional[str] = None,
        label_ids: Optional[List[str]] = None,
        page_token: Optional[str] = None,
        max_results: int = 10,
    ) -> Dict[str, Union[List[Dict], str, int]]:
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return {"messages": [], "resultSizeEstimate": 0}

        filtered_messages = []
        for msg_id, msg_data in messages.items():
            match = True
            if query and query.lower() not in msg_data.get("snippet", "").lower() and \
               query.lower() not in msg_data.get("payload", {}).get("headers", [{"value":""}])[0].get("value", "").lower():
                match = False
            if label_ids:
                msg_labels = set(msg_data.get("labelIds", []))
                if not all(label in msg_labels for label in label_ids):
                    match = False
            
            if match:
                filtered_messages.append({
                    "id": msg_data["id"],
                    "threadId": msg_data["threadId"],
                    "snippet": msg_data["snippet"],
                    "labelIds": msg_data["labelIds"]
                })

        start_index = 0
        if page_token:
            try:
                start_index = int(page_token)
            except ValueError:
                start_index = 0

        paginated_messages = filtered_messages[start_index : start_index + max_results]
        next_page_token = str(start_index + max_results) if start_index + max_results < len(filtered_messages) else None

        return {
            "messages": paginated_messages,
            "nextPageToken": next_page_token,
            "resultSizeEstimate": len(filtered_messages)
        }

    def get_message(
        self, user_id: str, msg_id: str, format: str = "full"
    ) -> Optional[Dict[str, Any]]:
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return None
        
        message = messages.get(msg_id)
        if message:
            if format == "minimal":
                return {"id": message["id"], "threadId": message["threadId"], "snippet": message["snippet"]}
            elif format == "raw":
                return {"id": message["id"], "raw": "dummy_raw_content_for_" + message["id"]}
            return copy.deepcopy(message)
        return None

    def send_message(
        self, user_id: str, to: str, subject: str, body: str, thread_id: Optional[str] = None
    ) -> Dict[str, Union[str, Dict]]:
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"error": "User not found."}

        gmail_data = self.users[internal_user_id].get("gmail_data")
        if not gmail_data:
            return {"error": "Gmail data not available for user."}

        new_msg_id = self._generate_id()
        if not thread_id:
            thread_id = self._generate_id()

        new_message = {
            "id": new_msg_id,
            "threadId": thread_id,
            "snippet": body[:100] + "...",
            "payload": {
                "headers": [
                    {"name": "To", "value": to},
                    {"name": "From", "value": user_id},
                    {"name": "Subject", "value": subject}
                ],
                "body": {"data": body}
            },
            "internalDate": str(int(datetime.datetime.now().timestamp() * 1000)),
            "labelIds": ["SENT", "INBOX"]
        }

        gmail_data["messages"][new_msg_id] = new_message
        if thread_id not in gmail_data["threads"]:
            gmail_data["threads"][thread_id] = {"id": thread_id, "messages": []}
        gmail_data["threads"][thread_id]["messages"].append({"id": new_msg_id})
        gmail_data["profile"]["messagesTotal"] = gmail_data["profile"].get("messagesTotal", 0) + 1
        gmail_data["profile"]["threadsTotal"] = len(gmail_data["threads"])

        recipient_user_id = self._get_user_id_by_email(to)
        if recipient_user_id and recipient_user_id != internal_user_id:
            recipient_gmail_data = self.users[recipient_user_id].get("gmail_data")
            if recipient_gmail_data:
                recipient_message = copy.deepcopy(new_message)
                recipient_message["labelIds"] = ["INBOX", "UNREAD"]
                recipient_gmail_data["messages"][new_msg_id] = recipient_message
                if thread_id not in recipient_gmail_data["threads"]:
                    recipient_gmail_data["threads"][thread_id] = {"id": thread_id, "messages": []}
                recipient_gmail_data["threads"][thread_id]["messages"].append({"id": new_msg_id})
                recipient_gmail_data["profile"]["messagesTotal"] = recipient_gmail_data["profile"].get("messagesTotal", 0) + 1
                recipient_gmail_data["profile"]["threadsTotal"] = len(recipient_gmail_data["threads"])

        print(f"Dummy email sent: from {user_id} to {to}, subject '{subject}'")
        return {"id": new_msg_id, "threadId": thread_id}

    def delete_message(self, user_id: str, msg_id: str) -> Dict[str, Union[bool, str]]:
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return {"success": False, "message": "User not found or no messages data."}
        
        if msg_id in messages:
            thread_id = messages[msg_id]["threadId"]
            del messages[msg_id]
            
            threads = self._get_user_threads_data(user_id)
            if threads and thread_id in threads:
                threads[thread_id]["messages"] = [m for m in threads[thread_id]["messages"] if m["id"] != msg_id]
                if not threads[thread_id]["messages"]:
                    del threads[thread_id]

            internal_user_id = self._get_user_id_by_email(user_id)
            if internal_user_id:
                profile = self.users[internal_user_id].get("gmail_data", {}).get("profile")
                if profile:
                    profile["messagesTotal"] = max(0, profile.get("messagesTotal", 0) - 1)
                    profile["threadsTotal"] = len(threads) if threads else 0

            print(f"Dummy message deleted: ID={msg_id} for user {user_id}")
            return {"success": True, "message": f"Message {msg_id} deleted."}
        return {"success": False, "message": f"Message {msg_id} not found."}

    def list_drafts(
        self, user_id: str, page_token: Optional[str] = None, max_results: int = 10
    ) -> Dict[str, Union[List[Dict], str, int]]:
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return {"drafts": [], "resultSizeEstimate": 0}

        all_drafts = list(drafts.values())
        
        start_index = 0
        if page_token:
            try:
                start_index = int(page_token)
            except ValueError:
                start_index = 0

        paginated_drafts = all_drafts[start_index : start_index + max_results]
        next_page_token = str(start_index + max_results) if start_index + max_results < len(all_drafts) else None

        formatted_drafts = [{"id": d["id"], "message": d["message"]} for d in paginated_drafts]

        return {
            "drafts": formatted_drafts,
            "nextPageToken": next_page_token,
            "resultSizeEstimate": len(all_drafts)
        }

    def get_draft(self, user_id: str, draft_id: str) -> Optional[Dict[str, Any]]:
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return None
        
        draft = drafts.get(draft_id)
        if draft:
            return copy.deepcopy(draft)
        return None

    def create_draft(
        self, user_id: str, to: str, subject: str, body: str
    ) -> Dict[str, Union[str, Dict]]:
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"error": "User not found."}

        gmail_data = self.users[internal_user_id].get("gmail_data")
        if not gmail_data:
            return {"error": "Gmail data not available for user."}

        new_draft_id = self._generate_id()
        new_draft = {
            "id": new_draft_id,
            "message": {
                "to": to,
                "subject": subject,
                "body": body
            }
        }
        gmail_data["drafts"][new_draft_id] = new_draft
        print(f"Dummy draft created: ID={new_draft_id} for user {user_id}")
        return {"id": new_draft_id, "message": new_draft["message"]}

    def update_draft(
        self, user_id: str, draft_id: str, to: str, subject: str, body: str
    ) -> Dict[str, Union[str, Dict]]:
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return {"error": "User not found or no drafts data."}

        if draft_id in drafts:
            drafts[draft_id]["message"]["to"] = to
            drafts[draft_id]["message"]["subject"] = subject
            drafts[draft_id]["message"]["body"] = body
            print(f"Dummy draft updated: ID={draft_id} for user {user_id}")
            return {"id": draft_id, "message": drafts[draft_id]["message"]}
        return {"error": f"Draft {draft_id} not found."}

    def delete_draft(self, user_id: str, draft_id: str) -> Dict[str, Union[bool, str]]:
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return {"success": False, "message": "User not found or no drafts data."}
        
        if draft_id in drafts:
            del drafts[draft_id]
            print(f"Dummy draft deleted: ID={draft_id} for user {user_id}")
            return {"success": True, "message": f"Draft {draft_id} deleted."}
        return {"success": False, "message": f"Draft {draft_id} not found."}

    def list_labels(self, user_id: str) -> Dict[str, Union[List[Dict], str]]:
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return {"labels": []}
        
        formatted_labels = [copy.deepcopy(label) for label in labels.values()]
        return {"labels": formatted_labels}

    def get_label(self, user_id: str, label_id: str) -> Optional[Dict[str, Any]]:
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return None
        
        label = labels.get(label_id)
        if label:
            return copy.deepcopy(label)
        return None

    def create_label(self, user_id: str, label_name: str) -> Dict[str, Union[str, Dict]]:
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"error": "User not found."}

        gmail_data = self.users[internal_user_id].get("gmail_data")
        if not gmail_data:
            return {"error": "Gmail data not available for user."}
        
        labels = gmail_data.get("labels")
        if labels is None:
            gmail_data["labels"] = {}
            labels = gmail_data["labels"]

        new_label_id = self._generate_id()
        new_label = {
            "id": new_label_id,
            "name": label_name,
            "messageListVisibility": "show",
            "labelListVisibility": "show",
            "type": "user"
        }
        labels[new_label_id] = new_label
        print(f"Dummy label created: ID={new_label_id}, Name='{label_name}' for user {user_id}")
        return {"id": new_label_id, "name": label_name}

    def update_label(self, user_id: str, label_id: str, new_label_name: str) -> Dict[str, Union[str, Dict]]:
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return {"error": "User not found or no labels data."}
        
        if label_id in labels:
            labels[label_id]["name"] = new_label_name
            print(f"Dummy label updated: ID={label_id}, New Name='{new_label_name}' for user {user_id}")
            return {"id": label_id, "name": new_label_name}
        return {"error": f"Label {label_id} not found."}

    def delete_label(self, user_id: str, label_id: str) -> Dict[str, Union[bool, str]]:
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return {"success": False, "message": "User not found or no labels data."}
        
        if label_id in labels:
            del labels[label_id]
            print(f"Dummy label deleted: ID={label_id} for user {user_id}")
            return {"success": True, "message": f"Label {label_id} deleted."}
        return {"success": False, "message": f"Label {label_id} not found."}

    def modify_message(
        self, user_id: str, message_id: str, modify_request: Dict[str, List[str]]
    ) -> Optional[Dict[str, Any]]:
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return None
        
        message = messages.get(message_id)
        if not message:
            return None

        current_labels = set(message.get("labelIds", []))
        
        add_labels = set(modify_request.get("addLabelIds", []))
        remove_labels = set(modify_request.get("removeLabelIds", []))

        message["labelIds"] = list(current_labels.union(add_labels))
        message["labelIds"] = list(set(message["labelIds"]) - remove_labels)

        print(f"Dummy message modified: ID={message_id}, New Labels={message['labelIds']} for user {user_id}")
        return copy.deepcopy(message)

    def get_thread(
        self, user_id: str, thread_id: str, format: str = "full"
    ) -> Optional[Dict[str, Any]]:
        threads = self._get_user_threads_data(user_id)
        messages_data = self._get_user_messages_data(user_id)
        if threads is None or messages_data is None:
            return None
        
        thread = threads.get(thread_id)
        if not thread:
            return None

        thread_copy = copy.deepcopy(thread)
        detailed_messages = []
        for msg_summary in thread_copy.get("messages", []):
            msg_id = msg_summary.get("id")
            if msg_id and msg_id in messages_data:
                message = messages_data[msg_id]
                if format == "minimal":
                    detailed_messages.append({"id": message["id"], "threadId": message["threadId"], "snippet": message["snippet"]})
                elif format == "raw":
                    detailed_messages.append({"id": message["id"], "raw": "dummy_raw_content_for_" + message["id"]})
                else:
                    detailed_messages.append(copy.deepcopy(message))
        thread_copy["messages"] = detailed_messages

        return thread_copy

    def modify_thread(
        self, user_id: str, thread_id: str, modify_request: Dict[str, List[str]]
    ) -> Optional[Dict[str, Any]]:
        threads = self._get_user_threads_data(user_id)
        messages = self._get_user_messages_data(user_id)
        if threads is None or messages is None:
            return None

        thread = threads.get(thread_id)
        if not thread:
            return None

        add_labels = set(modify_request.get("addLabelIds", []))
        remove_labels = set(modify_request.get("removeLabelIds", []))

        for msg_data_summary in thread.get("messages", []):
            msg_id = msg_data_summary["id"]
            if msg_id in messages:
                current_labels = set(messages[msg_id].get("labelIds", []))
                messages[msg_id]["labelIds"] = list(current_labels.union(add_labels))
                messages[msg_id]["labelIds"] = list(set(messages[msg_id]["labelIds"]) - remove_labels)
        
        print(f"Dummy thread modified: ID={thread_id} for user {user_id}. Labels applied to contained messages.")
        return self.get_thread(user_id, thread_id, format="full")

    def reset_data(self) -> Dict[str, bool]:
        self._load_scenario(DEFAULT_STATE)
        print("GmailApis: All dummy data reset to default state.")
        return {"reset_status": True}