import datetime
import json
import copy
import uuid
import random
import re
from typing import Dict, Any
from fake_data import first_names, last_names, domains, user_count, first_and_last_names, states, card_names, transaction_notes

_initial_user_email_to_uuid_map = {}
_initial_payment_card_id_map = {}
_initial_transaction_id_map = {}
_initial_notification_id_map = {}

def _convert_initial_data_to_uuids(initial_data: Dict[str, Any]) -> Dict[str, Any]:
    converted_data = copy.deepcopy(initial_data)

    global _initial_user_email_to_uuid_map
    global _initial_payment_card_id_map
    global _initial_transaction_id_map
    global _initial_notification_id_map

    _initial_user_email_to_uuid_map = {}
    _initial_payment_card_id_map = {}
    _initial_transaction_id_map = {}
    _initial_notification_id_map = {}

    new_users = {}
    for email, user_data in converted_data.get("users", {}).items():
        user_id = str(uuid.uuid4())
        _initial_user_email_to_uuid_map[email] = user_id
        user_data["id"] = user_id
        new_users[user_id] = user_data
    converted_data["users"] = new_users

    for user_uuid, user_data in converted_data["users"].items():
        if "friends" in user_data:
            user_data["friends"] = [
                _initial_user_email_to_uuid_map.get(friend_email, friend_email)
                for friend_email in user_data["friends"]
            ]
            user_data["friends"] = [
                friend_id for friend_id in user_data["friends"]
                if friend_id in converted_data["users"]
            ]

        new_payment_cards = {}
        for old_card_id, card_data in user_data.get("payment_cards", {}).items():
            new_card_uuid = str(uuid.uuid4())
            _initial_payment_card_id_map[(user_uuid, old_card_id)] = new_card_uuid

            card_data["id"] = new_card_uuid
            original_card_num = str(card_data.get("card_number", "2343"))
            card_data["card_number"] = f"4542 3453 2343 {original_card_num[-4:]}"
            if "cvv_number" in card_data:
                del card_data["cvv_number"]
            
            if "created_at" not in card_data:
                card_data["created_at"] = generate_random_iso_timestamp(days_ago_min=365, days_ago_max=365*3)
            card_data["last_modified"] = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=90)

            if "card_type" not in card_data:
                card_data["card_type"] = random.choice(["Visa", "Mastercard", "Amex", "Discover"])
            if "billing_address" not in card_data:
                card_data["billing_address"] = f"{random.randint(100,999)} {random.choice(['Main', 'Oak', 'Pine'])} St, {random.choice(['Springfield', 'Rivertown'])}, {random.choice(['FL', 'GA', 'AL', 'NC'])} {random.randint(10000, 99999)}"

            new_payment_cards[new_card_uuid] = card_data
        user_data["payment_cards"] = new_payment_cards

    new_transactions = {}
    for old_transaction_id, transaction_data in converted_data.get("transactions", {}).items():
        new_transaction_uuid = str(uuid.uuid4())
        _initial_transaction_id_map[old_transaction_id] = new_transaction_uuid

        transaction_data["id"] = new_transaction_uuid
        
        sender_email = transaction_data.get("sender")
        receiver_email = transaction_data.get("receiver")
        transaction_data["sender"] = _initial_user_email_to_uuid_map.get(sender_email, sender_email)
        transaction_data["receiver"] = _initial_user_email_to_uuid_map.get(receiver_email, receiver_email)
        
        if "timestamp" in transaction_data and not isinstance(transaction_data["timestamp"], str):
             transaction_data["timestamp"] = datetime.datetime.fromtimestamp(transaction_data["timestamp"], datetime.timezone.utc).isoformat(timespec='milliseconds') + "Z"
        elif "timestamp" not in transaction_data:
            transaction_data["timestamp"] = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365)

        if "transaction_type" not in transaction_data:
            transaction_data["transaction_type"] = random.choice(["peer_to_peer", "bill_payment", "deposit", "withdrawal"])
        if "fee" not in transaction_data:
            transaction_data["fee"] = round(random.uniform(0.00, 1.50), 2) if transaction_data["amount"] > 10 else 0.00
        if "currency" not in transaction_data:
            transaction_data["currency"] = "USD"
        
        new_transactions[new_transaction_uuid] = transaction_data
    converted_data["transactions"] = new_transactions

    new_notifications = {}
    for old_notification_id, notification_data in converted_data.get("notifications", {}).items():
        new_notification_uuid = str(uuid.uuid4())
        _initial_notification_id_map[old_notification_id] = new_notification_uuid

        notification_data["id"] = new_notification_uuid
        
        notification_user_email = notification_data.get("user")
        notification_data["user"] = _initial_user_email_to_uuid_map.get(notification_user_email, notification_user_email)
        
        if "notification_time" in notification_data and not isinstance(notification_data["notification_time"], str):
             notification_data["notification_time"] = datetime.datetime.fromtimestamp(notification_data["notification_time"], datetime.timezone.utc).isoformat(timespec='milliseconds') + "Z"
        elif "notification_time" not in notification_data:
            notification_data["notification_time"] = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=90)

        if "priority" not in notification_data:
            notification_data["priority"] = random.choice(["high", "medium", "low"])
        if "channel" not in notification_data:
            notification_data["channel"] = random.choice(["app", "email", "sms"])

        new_notifications[new_notification_uuid] = notification_data
    converted_data["notifications"] = new_notifications

    return converted_data

RAW_DEFAULT_STATE = {
    "users": {
        "alice.smith@gmail.com": {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@gmail.com",
            "balance": 100.00,
            "friends": ["bob.johnson@yahoo.com", "charlie.brown@outlook.com"],
            "payment_cards": {
                "card_1": {"card_name": "My Debit Card", "owner_name": "Alice Smith", "card_number": "4111222233334444", "expiry_year": 2028, "expiry_month": 12, "cvv_number": "123", "is_default": True}
            }
        },
        "bob.johnson@yahoo.com": {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@yahoo.com",
            "balance": 50.00,
            "friends": ["alice.smith@gmail.com", "diana.prince@protonmail.com"],
            "payment_cards": {
                "card_1": {"card_name": "Bob's Visa", "owner_name": "Bob Johnson", "card_number": "4222333344445555", "expiry_year": 2027, "expiry_month": 11, "cvv_number": "456", "is_default": True}
            }
        },
        "charlie.brown@outlook.com": {
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "charlie.brown@outlook.com",
            "balance": 25.50,
            "friends": ["alice.smith@gmail.com"],
            "payment_cards": {
                "card_1": {"card_name": "Charlie's Amex", "owner_name": "Charlie Brown", "card_number": "3777888899990000", "expiry_year": 2026, "expiry_month": 9, "cvv_number": "789", "is_default": True}
            }
        },
        "diana.prince@protonmail.com": {
            "first_name": "Diana",
            "last_name": "Prince",
            "email": "diana.prince@protonmail.com",
            "balance": 150.00,
            "friends": ["bob.johnson@yahoo.com"],
            "payment_cards": {}
        }
    },
    "transactions": {
        1: {
            "id": 1,
            "sender": "alice.smith@gmail.com",
            "receiver": "bob.johnson@yahoo.com",
            "amount": 20.00,
            "note": "For dinner last night",
            "status": "completed",
            "timestamp": datetime.datetime.now().timestamp() - 86400
        },
        2: {
            "id": 2,
            "sender": "bob.johnson@yahoo.com",
            "receiver": "charlie.brown@outlook.com",
            "amount": 5.00,
            "note": "Coffee money",
            "status": "pending",
            "timestamp": datetime.datetime.now().timestamp() - 3600
        },
        3: {
            "id": 3,
            "sender": "alice.smith@gmail.com",
            "receiver": "alice.smith@gmail.com",
            "amount": 10.00,
            "note": "Test payment to self",
            "status": "completed",
            "timestamp": datetime.datetime.now().timestamp() - 7200
        }
    },
    "notifications": {
        1: {
            "id": 1,
            "user": "alice.smith@gmail.com",
            "type": "payment_received",
            "message": "You received $20.00 from Bob Johnson.",
            "read": False,
            "notification_time": datetime.datetime.now().timestamp() - 86300
        },
        2: {
            "id": 2,
            "user": "charlie.brown@outlook.com",
            "type": "payment_request",
            "message": "Bob Johnson requested $5.00.",
            "read": False,
            "notification_time": datetime.datetime.now().timestamp() - 3500
        },
        3: {
            "id": 3,
            "user": "alice.smith@gmail.com",
            "type": "friend_request",
            "message": "Diana Prince sent you a friend request.",
            "read": True,
            "notification_time": datetime.datetime.now().timestamp() - 172800
        }
    }
}

def generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365*5):
    delta_days = random.randint(days_ago_min, days_ago_max)
    time_offset = datetime.timedelta(days=delta_days, 
                                     hours=random.randint(0, 23), 
                                     minutes=random.randint(0, 59), 
                                     seconds=random.randint(0, 59))
    dt = datetime.datetime.now(datetime.timezone.utc) - time_offset
    return dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

billing_cities = ["Orlando", "Miami", "Tampa", "Jacksonville", "Atlanta", "Charlotte", "Nashville", "New Orleans"]
notification_messages = {
    "payment_received": ["You received ${amount:.2f} from {sender_name}.", "${sender_name} sent you ${amount:.2f}.", "A payment of ${amount:.2f} arrived from {sender_name}."],
    "payment_sent": ["You sent ${amount:.2f} to {receiver_name}.", "Payment of ${amount:.2f} to {receiver_name} completed.", "Your transaction to {receiver_name} for ${amount:.2f} was successful."],
    "payment_request": ["{sender_name} requested ${amount:.2f}.", "You have a pending request for ${amount:.2f} from {sender_name}.", "Action required: {sender_name} is requesting ${amount:.2f}."],
    "friend_request": ["{sender_name} sent you a friend request.", "New friend request from {sender_name}.", "You have a pending friend request from {sender_name}."],
    "balance_update": ["Your balance has been updated to ${balance:.2f}.", "Balance update: ${balance:.2f} available.", "Your new balance is ${balance:.2f}."],
    "security_alert": ["Unusual login detected.", "Suspicious activity on your account.", "Please verify a recent login from a new device."]
}

DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)

num_initial_users = len(RAW_DEFAULT_STATE["users"])
all_user_uuids = list(DEFAULT_STATE["users"].keys())
existing_user_emails = set([DEFAULT_STATE["users"][uid]["email"] for uid in DEFAULT_STATE["users"].keys()])

for i in range(len(first_and_last_names) + user_count):
    first = random.choice(first_names) if i < user_count else first_and_last_names[i - user_count].partition(" ")[0]
    last = random.choice(last_names) if i < user_count else first_and_last_names[i - user_count].partition(" ")[2]
    email = f"{first.lower()}.{last.lower()}{random.randint(100, 9999)}@{random.choice(domains)}"
    
    while email in existing_user_emails:
        email = f"{first.lower()}.{last.lower()}{random.randint(100, 9999)}@{random.choice(domains)}"
    
    existing_user_emails.add(email)

    user_id = str(uuid.uuid4())
    _initial_user_email_to_uuid_map[email] = user_id

    num_friends = random.randint(0, min(8, len(all_user_uuids)))
    friends_list_uuids = random.sample(all_user_uuids, num_friends)
    
    user_payment_cards = {}
    num_cards = random.choices([0, 1, 2], weights=[0.2, 0.6, 0.2], k=1)[0]
    for c_idx in range(num_cards):
        card_uuid = str(uuid.uuid4())
        card_type = random.choice(["Visa", "Mastercard", "Amex", "Discover"])
        expiry_year = random.randint(2026, 2035)
        expiry_month = random.randint(1, 12)
        def generate_fake_card_number(card_type):
            if card_type == "Visa":
                prefix = "4"
                remaining_digits = 15
            elif card_type == "Mastercard":
                prefix = "5"
                remaining_digits = 15
            elif card_type == "Amex":
                prefix = random.choice(["34", "37"])
                remaining_digits = 13
            elif card_type == "Discover":
                prefix = "6011"
                remaining_digits = 12
            else:
                prefix = "9"
                remaining_digits = 15
            
            
            card_digits = prefix + ''.join(random.choices('0123456789', k=remaining_digits))
            
            
            formatted_card = ' '.join([card_digits[i:i+4] for i in range(0, len(card_digits), 4)])
            return formatted_card
        
        card_number_fake = generate_fake_card_number(card_type)
        random_state = random.choice(states)
        user_payment_cards[card_uuid] = {
            "id": card_uuid,
            "card_name": f"{random.choice(card_names)} ({card_type})",
            "owner_name": f"{first} {last}",
            "card_number": card_number_fake,
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
            "is_default": (c_idx == 0),
            "card_type": card_type,
            "billing_address": f"{random.randint(100, 999)} {random.choice(['Park', 'Lake', 'Main', 'Cedar'])} Ave, {random.choice(billing_cities[random_state])}, {random_state} {random.randint(10000, 99999)}",
            "created_at": generate_random_iso_timestamp(days_ago_min=365, days_ago_max=365*3),
            "last_modified": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=90)
        }

    new_user_data = {
        "id": user_id,
        "first_name": first,
        "last_name": last,
        "email": email,
        "balance": round(random.uniform(5.00, 500.00), 2),
        "friends": friends_list_uuids,
        "payment_cards": user_payment_cards,
        "registration_date": generate_random_iso_timestamp(days_ago_min=365*2, days_ago_max=365*5),
        "last_login_date": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=30),
        "is_premium": random.random() < 0.3
    }
    DEFAULT_STATE["users"][user_id] = new_user_data
    all_user_uuids.append(user_id)

initial_transaction_count = len(DEFAULT_STATE["transactions"])
num_transactions_to_add = 70
for i in range(num_transactions_to_add):
    sender_uuid = random.choice(all_user_uuids)
    receiver_uuid = random.choice([u_id for u_id in all_user_uuids if u_id != sender_uuid])

    amount = round(random.uniform(1.00, 200.00), 2)
    transaction_type = random.choice(["payment", "charge"])
    status = random.choice(["completed", "pending", "failed"])
    note = random.choice(transaction_notes)

    transaction_uuid = str(uuid.uuid4())
    DEFAULT_STATE["transactions"][transaction_uuid] = {
        "id": transaction_uuid,
        "sender": sender_uuid,
        "receiver": receiver_uuid,
        "amount": amount,
        "note": note,
        "status": status,
        "timestamp": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365),
        "transaction_type": transaction_type,
        "fee": round(random.uniform(0.00, 1.50), 2) if amount > 10 and transaction_type != "refund" else 0.00,
        "currency": "USD"
    }

initial_notification_count = len(DEFAULT_STATE["notifications"])
num_notifications_to_add = 100
for i in range(num_notifications_to_add):
    user_uuid = random.choice(all_user_uuids)
    notification_type = random.choice(list(notification_messages.keys()))
    
    message_template = random.choice(notification_messages[notification_type])
    
    placeholders = re.findall(r'{(\w+)(?::\.2f)?}', message_template)
    message_params = {}

    for placeholder in placeholders:
        if placeholder == "amount":
            message_params["amount"] = round(random.uniform(5.00, 150.00), 2)
        elif placeholder == "sender_name":
            sender_info = DEFAULT_STATE["users"].get(random.choice(all_user_uuids))
            message_params["sender_name"] = sender_info["first_name"] if sender_info else "Someone"
        elif placeholder == "receiver_name":
            receiver_info = DEFAULT_STATE["users"].get(random.choice(all_user_uuids))
            message_params["receiver_name"] = receiver_info["first_name"] if receiver_info else "Someone"
        elif placeholder == "balance":
            message_params["balance"] = round(random.uniform(10.00, 600.00), 2)
    
    message = message_template.format(**message_params)

    notification_uuid = str(uuid.uuid4())
    DEFAULT_STATE["notifications"][notification_uuid] = {
        "id": notification_uuid,
        "user": user_uuid,
        "type": notification_type,
        "message": message,
        "read": random.random() < 0.7,
        "notification_time": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=90),
        "priority": random.choice(["high", "medium", "low"]),
        "channel": random.choice(["app", "email", "sms"])
    }

for user_id, user_data in DEFAULT_STATE["users"].items():
    if "friends" in user_data:
        updated_friends = []
        for friend_identifier in user_data["friends"]:
            if friend_identifier in _initial_user_email_to_uuid_map:
                updated_friends.append(_initial_user_email_to_uuid_map[friend_identifier])
            elif friend_identifier in DEFAULT_STATE["users"]:
                updated_friends.append(friend_identifier)
        user_data["friends"] = list(set(updated_friends))

output_filename = 'diverse_venmo_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Total number of users: {len(DEFAULT_STATE['users'])}")
print(f"Total number of transactions: {len(DEFAULT_STATE['transactions'])}")
print(f"Total number of notifications: {len(DEFAULT_STATE['notifications'])}")
print(f"Generated DEFAULT_STATE saved to '{output_filename}'")
