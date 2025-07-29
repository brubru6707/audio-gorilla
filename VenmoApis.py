import datetime
import copy
import uuid
import random
from typing import Dict, List, Any, Optional, Union, Literal

# Class definitions for type hinting, as per previous files
class EmailStr(str):
    pass

class User:
    def __init__(self, email: EmailStr):
        self.email = email

# Global mappings for initial data conversion from old string/int IDs/emails to new UUIDs
_initial_user_email_to_uuid_map = {}
_initial_payment_card_id_map = {} # Map (user_uuid, original_card_id_string) to new_card_uuid
_initial_transaction_id_map = {} # Map original_int_id to new_transaction_uuid
_initial_notification_id_map = {} # Map original_int_id to new_notification_uuid


def _convert_initial_data_to_uuids(initial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Converts the initial RAW_DEFAULT_STATE data to use UUIDs for all relevant IDs and adds realism."""

    converted_data = copy.deepcopy(initial_data)

    # Reset maps for a clean conversion
    global _initial_user_email_to_uuid_map
    global _initial_payment_card_id_map
    global _initial_transaction_id_map
    global _initial_notification_id_map

    _initial_user_email_to_uuid_map = {}
    _initial_payment_card_id_map = {}
    _initial_transaction_id_map = {}
    _initial_notification_id_map = {}

    current_time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds') + "Z"

    # Convert users and their friends, and map emails to UUIDs first
    new_users = {}
    for email, user_data in converted_data.get("users", {}).items():
        user_id = str(uuid.uuid4())
        _initial_user_email_to_uuid_map[email] = user_id
        user_data["id"] = user_id # Add a UUID ID to the user data itself
        new_users[user_id] = user_data
    converted_data["users"] = new_users

    # Now that user UUIDs are generated, update friends lists and payment cards
    for user_uuid, user_data in converted_data["users"].items():
        # Update friends to UUIDs
        if "friends" in user_data:
            user_data["friends"] = [
                _initial_user_email_to_uuid_map.get(friend_email, friend_email)
                for friend_email in user_data["friends"]
            ]
            # Clean up friends list to ensure they are valid UUIDs, remove if not mapped
            user_data["friends"] = [
                friend_id for friend_id in user_data["friends"]
                if friend_id in converted_data["users"]
            ]

        # Convert payment cards to UUIDs and add realism
        new_payment_cards = {}
        for old_card_id, card_data in user_data.get("payment_cards", {}).items():
            new_card_uuid = str(uuid.uuid4())
            _initial_payment_card_id_map[(user_uuid, old_card_id)] = new_card_uuid

            card_data["id"] = new_card_uuid
            # Mask card number (last 4 digits visible)
            original_card_num = str(card_data.get("card_number", "0000"))
            card_data["card_number"] = f"**** **** **** {original_card_num[-4:]}"
            # Remove CVV for realism
            if "cvv_number" in card_data:
                del card_data["cvv_number"]
            
            # Add timestamps for creation/modification
            if "created_at" not in card_data:
                card_data["created_at"] = generate_random_iso_timestamp(days_ago_min=365, days_ago_max=365*3) # 1-3 years ago
            card_data["last_modified"] = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=90) # Last 90 days

            # Add card_type
            if "card_type" not in card_data:
                card_data["card_type"] = random.choice(["Visa", "Mastercard", "Amex", "Discover"])
            # Add billing_address
            if "billing_address" not in card_data:
                card_data["billing_address"] = f"{random.randint(100,999)} {random.choice(['Main', 'Oak', 'Pine'])} St, {random.choice(['Springfield', 'Rivertown'])}, {random.choice(['FL', 'GA', 'AL', 'NC'])} {random.randint(10000, 99999)}"


            new_payment_cards[new_card_uuid] = card_data
        user_data["payment_cards"] = new_payment_cards

    # Convert transactions
    new_transactions = {}
    for old_transaction_id, transaction_data in converted_data.get("transactions", {}).items():
        new_transaction_uuid = str(uuid.uuid4())
        _initial_transaction_id_map[old_transaction_id] = new_transaction_uuid

        transaction_data["id"] = new_transaction_uuid
        
        # Convert sender/receiver emails to UUIDs
        sender_email = transaction_data.get("sender")
        receiver_email = transaction_data.get("receiver")
        transaction_data["sender"] = _initial_user_email_to_uuid_map.get(sender_email, sender_email)
        transaction_data["receiver"] = _initial_user_email_to_uuid_map.get(receiver_email, receiver_email)
        
        # Ensure timestamp is ISO 8601
        if "timestamp" in transaction_data and not isinstance(transaction_data["timestamp"], str):
             transaction_data["timestamp"] = datetime.datetime.fromtimestamp(transaction_data["timestamp"], datetime.timezone.utc).isoformat(timespec='milliseconds') + "Z"
        elif "timestamp" not in transaction_data:
            transaction_data["timestamp"] = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365) # Last year

        # Add transaction_type if not present
        if "transaction_type" not in transaction_data:
            transaction_data["transaction_type"] = random.choice(["peer_to_peer", "bill_payment", "deposit", "withdrawal"])
        # Add fee if not present
        if "fee" not in transaction_data:
            transaction_data["fee"] = round(random.uniform(0.00, 1.50), 2) if transaction_data["amount"] > 10 else 0.00
        # Add currency
        if "currency" not in transaction_data:
            transaction_data["currency"] = "USD"
        
        new_transactions[new_transaction_uuid] = transaction_data
    converted_data["transactions"] = new_transactions

    # Convert notifications
    new_notifications = {}
    for old_notification_id, notification_data in converted_data.get("notifications", {}).items():
        new_notification_uuid = str(uuid.uuid4())
        _initial_notification_id_map[old_notification_id] = new_notification_uuid

        notification_data["id"] = new_notification_uuid
        
        # Convert user email to UUID
        notification_user_email = notification_data.get("user")
        notification_data["user"] = _initial_user_email_to_uuid_map.get(notification_user_email, notification_user_email)
        
        # Ensure timestamp is ISO 8601
        if "notification_time" in notification_data and not isinstance(notification_data["notification_time"], str):
             notification_data["notification_time"] = datetime.datetime.fromtimestamp(notification_data["notification_time"], datetime.timezone.utc).isoformat(timespec='milliseconds') + "Z"
        elif "notification_time" not in notification_data:
            notification_data["notification_time"] = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=90) # Last 90 days

        # Add priority if not present
        if "priority" not in notification_data:
            notification_data["priority"] = random.choice(["high", "medium", "low"])
        # Add channel
        if "channel" not in notification_data:
            notification_data["channel"] = random.choice(["app", "email", "sms"])

        new_notifications[new_notification_uuid] = notification_data
    converted_data["notifications"] = new_notifications


    # If current_user is set, convert it to UUID
    if converted_data.get("current_user") and converted_data["current_user"] in _initial_user_email_to_uuid_map:
        converted_data["current_user"] = _initial_user_email_to_uuid_map[converted_data["current_user"]]

    return converted_data

# Define the initial raw state with string/integer IDs and emails for conversion
# --- THIS BLOCK MUST BE BEFORE THE DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE) LINE ---
RAW_DEFAULT_STATE = {
    "current_user": "alice.smith@gmail.com",
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
            "payment_cards": {} # No cards for Diana initially
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
            "timestamp": datetime.datetime.now().timestamp() - 86400 # 1 day ago
        },
        2: {
            "id": 2,
            "sender": "bob.johnson@yahoo.com",
            "receiver": "charlie.brown@outlook.com",
            "amount": 5.00,
            "note": "Coffee money",
            "status": "pending",
            "timestamp": datetime.datetime.now().timestamp() - 3600 # 1 hour ago
        },
        3: {
            "id": 3,
            "sender": "alice.smith@gmail.com",
            "receiver": "alice.smith@gmail.com", # Self-payment example
            "amount": 10.00,
            "note": "Test payment to self",
            "status": "completed",
            "timestamp": datetime.datetime.now().timestamp() - 7200 # 2 hours ago
        }
    },
    "notifications": {
        1: {
            "id": 1,
            "user": "alice.smith@gmail.com",
            "type": "payment_received",
            "message": "You received $20.00 from Bob Johnson.",
            "read": False,
            "notification_time": datetime.datetime.now().timestamp() - 86300 # Just after the transaction
        },
        2: {
            "id": 2,
            "user": "charlie.brown@outlook.com",
            "type": "payment_request",
            "message": "Bob Johnson requested $5.00.",
            "read": False,
            "notification_time": datetime.datetime.now().timestamp() - 3500 # Just after the transaction
        },
        3: {
            "id": 3,
            "user": "alice.smith@gmail.com",
            "type": "friend_request",
            "message": "Diana Prince sent you a friend request.",
            "read": True,
            "notification_time": datetime.datetime.now().timestamp() - 172800 # 2 days ago
        }
    }
}


# --- Helper functions for generating diverse data ---
def generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365*5):
    """Generates a random ISO 8601 formatted datetime string (with Z for UTC) in the past."""
    delta_days = random.randint(days_ago_min, days_ago_max)
    time_offset = datetime.timedelta(days=delta_days, 
                                     hours=random.randint(0, 23), 
                                     minutes=random.randint(0, 59), 
                                     seconds=random.randint(0, 59))
    dt = datetime.datetime.now(datetime.timezone.utc) - time_offset
    return dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

# --- Data for generating new users ---
first_names = ["Olivia", "Liam", "Emma", "Noah", "Charlotte", "James", "Amelia", "Oliver", "Sophia", "Elijah", "Isabella", "William", "Ava", "Lucas", "Mia", "Henry", "Evelyn", "Theodore", "Harper", "Benjamin", "Luna", "Michael", "Ella", "Alexander", "Aurora", "Daniel", "Chloe", "Jacob", "Grace", "Logan", "Penelope", "Jackson", "Riley", "Sebastian", "Lily", "Aiden", "Nora", "Matthew", "Zoey", "Samuel", "Mila", "David", "Sofia", "Joseph", "Aria", "John", "Eleanor", "Gabriel", "Scarlett", "Anthony"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"]
email_domains = ["example.com", "mail.net", "web.org", "inbox.co", "domain.app", "email.xyz", "securemail.io", "fastmail.cc"]
card_names = ["Personal Card", "Work Card", "Travel Card", "Savings Card", "Main Account"]
billing_cities = ["Orlando", "Miami", "Tampa", "Jacksonville", "Atlanta", "Charlotte", "Nashville", "New Orleans"]
billing_states = ["FL", "GA", "AL", "NC", "SC", "MS", "TN"]
transaction_notes = [
    "Dinner with friends", "Groceries", "Online shopping", "Rent payment",
    "Coffee break", "Subscription service", "Movie tickets", "Gas refill",
    "Utilities bill", "Gift for birthday", "Lunch meeting", "Gym membership",
    "Car maintenance", "Donation", "Book purchase", "Travel expenses"
]
notification_messages = {
    "payment_received": ["You received ${amount:.2f} from {sender_name}.", "${sender_name} sent you ${amount:.2f}.", "A payment of ${amount:.2f} arrived from {sender_name}."],
    "payment_sent": ["You sent ${amount:.2f} to {receiver_name}.", "Payment of ${amount:.2f} to {receiver_name} completed.", "Your transaction to {receiver_name} for ${amount:.2f} was successful."],
    "payment_request": ["{sender_name} requested ${amount:.2f}.", "You have a pending request for ${amount:.2f} from {sender_name}.", "Action required: {sender_name} is requesting ${amount:.2f}."],
    "friend_request": ["{sender_name} sent you a friend request.", "New friend request from {sender_name}.", "You have a pending friend request from {sender_name}."],
    "balance_update": ["Your balance has been updated to ${balance:.2f}.", "Balance update: ${balance:.2f} available.", "Your new balance is ${balance:.2f}."],
    "security_alert": ["Unusual login detected.", "Suspicious activity on your account.", "Please verify a recent login from a new device."]
}

# The actual DEFAULT_STATE used by the API will be the converted one
# --- THIS LINE MUST BE AFTER THE RAW_DEFAULT_STATE DICTIONARY IS DEFINED ---
DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)

# --- Generate additional data ---
num_initial_users = len(RAW_DEFAULT_STATE["users"])
num_users_to_add = 50 - num_initial_users # Aim for 50 total users

# Collect existing user UUIDs for friend linking
all_user_uuids = list(DEFAULT_STATE["users"].keys())
existing_user_emails = set([DEFAULT_STATE["users"][uid]["email"] for uid in DEFAULT_STATE["users"].keys()])


# Generate additional users
for i in range(num_users_to_add):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}{random.randint(100, 9999)}@{random.choice(email_domains)}"
    
    # Ensure unique email
    while email in existing_user_emails:
        email = f"{first.lower()}.{last.lower()}{random.randint(100, 9999)}@{random.choice(email_domains)}"
    
    existing_user_emails.add(email) # Add new email to set of existing emails

    user_id = str(uuid.uuid4())
    _initial_user_email_to_uuid_map[email] = user_id # Add to map for friend linking

    # Generate friends for new user
    num_friends = random.randint(0, min(8, len(all_user_uuids)))
    friends_list_uuids = random.sample(all_user_uuids, num_friends)
    
    # Add a couple of payment cards
    user_payment_cards = {}
    num_cards = random.choices([0, 1, 2], weights=[0.2, 0.6, 0.2], k=1)[0] # 20% no card, 60% one, 20% two
    for c_idx in range(num_cards):
        card_uuid = str(uuid.uuid4())
        card_type = random.choice(["Visa", "Mastercard", "Amex", "Discover"])
        expiry_year = random.randint(2026, 2035)
        expiry_month = random.randint(1, 12)
        last_four = ''.join(random.choices('0123456789', k=4))
        full_card_number_prefix = {
            "Visa": "4", "Mastercard": "5", "Amex": "34", "Discover": "6011"
        }.get(card_type, "9") # Placeholder for start of card number
        card_number_masked = f"{full_card_number_prefix}{'X'*(15 - len(full_card_number_prefix))}{last_four}"

        user_payment_cards[card_uuid] = {
            "id": card_uuid,
            "card_name": f"{random.choice(card_names)} ({card_type})",
            "owner_name": f"{first} {last}",
            "card_number": card_number_masked,
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
            "is_default": (c_idx == 0), # First card is default
            "card_type": card_type,
            "billing_address": f"{random.randint(100, 999)} {random.choice(['Park', 'Lake', 'Main', 'Cedar'])} Ave, {random.choice(billing_cities)}, {random.choice(billing_states)} {random.randint(10000, 99999)}",
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
        "registration_date": generate_random_iso_timestamp(days_ago_min=365*2, days_ago_max=365*5), # 2-5 years ago
        "last_login_date": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=30), # Last 30 days
        "is_premium": random.random() < 0.3 # 30% premium users
    }
    DEFAULT_STATE["users"][user_id] = new_user_data
    all_user_uuids.append(user_id) # Add the new user's UUID to the list for subsequent friend linking


# Generate additional transactions
initial_transaction_count = len(DEFAULT_STATE["transactions"])
num_transactions_to_add = 70 # Aim for 70 new transactions
for i in range(num_transactions_to_add):
    sender_uuid = random.choice(all_user_uuids)
    receiver_uuid = random.choice([u_id for u_id in all_user_uuids if u_id != sender_uuid]) # Receiver must be different

    amount = round(random.uniform(1.00, 200.00), 2)
    transaction_type = random.choice(["peer_to_peer", "bill_payment", "deposit", "withdrawal", "refund"])
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

# Generate additional notifications
initial_notification_count = len(DEFAULT_STATE["notifications"])
num_notifications_to_add = 100 # Aim for 100 new notifications
for i in range(num_notifications_to_add):
    user_uuid = random.choice(all_user_uuids)
    notification_type = random.choice(list(notification_messages.keys()))
    
    # Customize message based on type
    message_template = random.choice(notification_messages[notification_type])
    message_params = {}
    if "amount" in message_template:
        message_params["amount"] = round(random.uniform(5.00, 150.00), 2)
    if "{sender_name}" in message_template:
        sender_info = DEFAULT_STATE["users"].get(random.choice(all_user_uuids))
        message_params["sender_name"] = sender_info["first_name"] if sender_info else "Someone"
    if "{receiver_name}" in message_template:
        receiver_info = DEFAULT_STATE["users"].get(random.choice(all_user_uuids))
        message_params["receiver_name"] = receiver_info["first_name"] if receiver_info else "Someone"
    if "{balance}" in message_template:
        message_params["balance"] = round(random.uniform(10.00, 600.00), 2)

    message = message_template.format(**message_params)

    notification_uuid = str(uuid.uuid4())
    DEFAULT_STATE["notifications"][notification_uuid] = {
        "id": notification_uuid,
        "user": user_uuid,
        "type": notification_type,
        "message": message,
        "read": random.random() < 0.7, # 70% chance read
        "notification_time": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=90),
        "priority": random.choice(["high", "medium", "low"]),
        "channel": random.choice(["app", "email", "sms"])
    }

# --- Final pass to ensure all friend UUIDs are valid and populate current_user if needed ---
# This is crucial in case friends were added as emails for users generated *later* in the loop
for user_id, user_data in DEFAULT_STATE["users"].items():
    if "friends" in user_data:
        updated_friends = []
        for friend_identifier in user_data["friends"]:
            if friend_identifier in _initial_user_email_to_uuid_map: # It's an initial email that was mapped
                updated_friends.append(_initial_user_email_to_uuid_map[friend_identifier])
            elif friend_identifier in DEFAULT_STATE["users"]: # It's already a UUID that exists
                updated_friends.append(friend_identifier)
            # If it's an email that wasn't mapped (e.g., a typo or non-existent), we drop it.
            # Or if it's a UUID not in DEFAULT_STATE users (shouldn't happen with current logic)
        user_data["friends"] = list(set(updated_friends)) # Use set to remove duplicates if any

# Ensure the "current_user" is set to a UUID and exists in the users dictionary
if DEFAULT_STATE.get("current_user") and DEFAULT_STATE["current_user"] in _initial_user_email_to_uuid_map:
    DEFAULT_STATE["current_user"] = _initial_user_email_to_uuid_map[RAW_DEFAULT_STATE["current_user"]]
elif DEFAULT_STATE["users"]: # If original current_user wasn't found, pick a random existing one
    DEFAULT_STATE["current_user"] = random.choice(list(DEFAULT_STATE["users"].keys()))
else:
    DEFAULT_STATE["current_user"] = None # No users to set as current

# --- Output the generated DEFAULT_STATE ---
import json
output_filename = 'diverse_finance_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Total number of users: {len(DEFAULT_STATE['users'])}")
print(f"Total number of transactions: {len(DEFAULT_STATE['transactions'])}")
print(f"Total number of notifications: {len(DEFAULT_STATE['notifications'])}")
print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

class VenmoApis:
    """
    A dummy API class for simulating Venmo operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the VenmoApis instance, setting up the in-memory
        data stores and loading the default scenario.
        """
        self._api_description = "This tool simulates Venmo payment and social functionalities."
        self.users: Dict[str, Any] = {} # Keyed by user UUID
        self.transactions: Dict[str, Any] = {} # Keyed by transaction UUID
        self.notifications: Dict[str, Any] = {} # Keyed by notification UUID
        self.current_user: Optional[str] = None # Stores the UUID of the current user

        # Internal map for efficient lookup of original string card IDs to new UUIDs per user
        # {(user_uuid, original_card_id_string): card_uuid}
        self._payment_card_lookup_map: Dict[tuple[str, str], str] = {}
        
        self._load_scenario(DEFAULT_STATE)
        self._populate_lookup_maps()

    def _populate_lookup_maps(self):
        """Populates the internal maps for looking up IDs after loading scenario."""
        self._payment_card_lookup_map = {}
        for user_uuid, user_data in self.users.items():
            payment_cards = user_data.get("payment_cards", {})
            for card_uuid, card_data in payment_cards.items():
                # We stored the original_card_id as the key in RAW_DEFAULT_STATE,
                # but it's not a direct property in the converted card_data.
                # If we need to map a *string* card_id from the API call to a UUID,
                # we need to ensure this mapping is handled during conversion or here.
                # For simplicity, if the API takes `card_id: str`, we assume it's a UUID.
                # If it takes `payment_method_id: int`, we would need a map from int to UUID.
                # Given the user's request for "long complex string", I'm assuming such inputs are UUIDs.
                pass # No direct mapping needed for old_card_id if API takes UUIDs for card_id

        # Rebuild transaction and notification lookup maps from the current state (already UUIDs)
        # These are direct lookups by UUID, so no extra map needed for "old" IDs


    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain "users", "transactions", "notifications".
        """
        # Create deep copy to ensure the original DEFAULT_STATE is not modified
        self.users = copy.deepcopy(scenario.get("users", {}))
        self.transactions = copy.deepcopy(scenario.get("transactions", {}))
        self.notifications = copy.deepcopy(scenario.get("notifications", {}))
        self.current_user = scenario.get("current_user") # This will already be a UUID after conversion

        self._populate_lookup_maps() # Repopulate map on load
        print("VenmoApis: Loaded scenario with UUIDs for users, transactions, and notifications.")

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for dummy entities.
        """
        return str(uuid.uuid4())

    def _get_user_data(self, user: User) -> Optional[Dict[str, Any]]:
        """Helper to get a user's data based on User object (email to UUID mapping)."""
        target_user_uuid = None
        for user_id, user_data in self.users.items():
            if user_data.get("email") == user.email:
                target_user_uuid = user_id
                break
        
        if not target_user_uuid:
            return None # User not found by email

        return self.users.get(target_user_uuid)

    def _update_user_data(self, user: User, key: str, value: Any) -> bool:
        """Helper to update a specific key in a user's data by User object."""
        target_user_uuid = None
        for user_id, user_data in self.users.items():
            if user_data.get("email") == user.email:
                target_user_uuid = user_id
                break
        
        if not target_user_uuid:
            return False # User not found by email

        if target_user_uuid in self.users:
            self.users[target_user_uuid][key] = value
            return True
        return False
    
    def _get_user_uuid_from_email(self, email: str) -> Optional[str]:
        """Helper to get user UUID from email."""
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_from_uuid(self, user_uuid: str) -> Optional[str]:
        """Helper to get user email from UUID."""
        user_data = self.users.get(user_uuid)
        return user_data.get("email") if user_data else None


    def set_current_user(self, user_email: str) -> Dict[str, bool]:
        """
        Sets the current authenticated user for the API session.

        Args:
            user_email (str): The email address of the user to set as current.

        Returns:
            Dict[str, bool]: A dictionary with 'status' indicating success or failure.
        """
        user_uuid = self._get_user_uuid_from_email(user_email)
        if user_uuid:
            self.current_user = user_uuid
            return {"status": True, "message": f"Current user set to {user_email} (ID: {user_uuid})."}
        return {"status": False, "message": f"User with email {user_email} not found."}

    # ================
    # Account & Profile
    # ================

    def show_account(self, user: User) -> Dict[str, Any]:
        """
        Shows the current user's account details.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'account_status' (bool) and 'account_details' (Dict) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"account_status": False, "account_details": {}}
        return {"account_status": True, "account_details": copy.deepcopy(user_data)}

    def list_friends(self, user: User) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Lists the friends of the current user.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'friends_status' (bool) and 'friends' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"friends_status": False, "friends": []}
        
        friend_uuids = user_data.get("friends", [])
        friends_list = []
        for friend_uuid in friend_uuids:
            friend_data = self.users.get(friend_uuid)
            if friend_data:
                friends_list.append({
                    "id": friend_data["id"],
                    "email": friend_data["email"],
                    "first_name": friend_data["first_name"],
                    "last_name": friend_data["last_name"]
                })
        return {"friends_status": True, "friends": friends_list}

    # ================
    # Money Transfers
    # ================

    def send_money(self, sender_user: User, receiver_email: str, amount: float, note: str) -> Dict[str, Union[bool, str]]:
        """
        Sends money from the current user to another user.

        Args:
            sender_user (User): The user sending the money.
            receiver_email (str): The email of the receiver.
            amount (float): The amount of money to send.
            note (str): A note for the transaction.

        Returns:
            Dict: A dictionary containing 'send_status' (bool) and 'message' (str).
        """
        sender_data = self._get_user_data(sender_user)
        receiver_uuid = self._get_user_uuid_from_email(receiver_email)
        receiver_data = self.users.get(receiver_uuid)

        if not sender_data:
            return {"send_status": False, "message": f"Sender user {sender_user.email} not found."}
        if not receiver_data:
            return {"send_status": False, "message": f"Receiver user {receiver_email} not found."}
        if sender_data["balance"] < amount:
            return {"send_status": False, "message": "Insufficient balance."}
        if amount <= 0:
            return {"send_status": False, "message": "Amount must be positive."}

        sender_data["balance"] -= amount
        receiver_data["balance"] += amount

        transaction_id = self._generate_unique_id()
        new_transaction = {
            "id": transaction_id,
            "sender": sender_data["id"],
            "receiver": receiver_data["id"],
            "amount": amount,
            "note": note,
            "status": "completed",
            "timestamp": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        }
        self.transactions[transaction_id] = new_transaction
        
        # Create notifications for sender and receiver
        self.notifications[self._generate_unique_id()] = {
            "id": self._generate_unique_id(), # New UUID for notification
            "user": sender_data["id"],
            "type": "payment_sent",
            "message": f"You sent ${amount:.2f} to {receiver_data['first_name']} {receiver_data['last_name']}.",
            "read": False,
            "notification_time": new_transaction["timestamp"]
        }
        self.notifications[self._generate_unique_id()] = {
            "id": self._generate_unique_id(), # New UUID for notification
            "user": receiver_data["id"],
            "type": "payment_received",
            "message": f"You received ${amount:.2f} from {sender_data['first_name']} {sender_data['last_name']}.",
            "read": False,
            "notification_time": new_transaction["timestamp"]
        }

        print(f"Transaction {transaction_id}: {sender_user.email} sent ${amount} to {receiver_email}")
        return {"send_status": True, "transaction_id": transaction_id}

    def request_money(self, sender_user: User, receiver_email: str, amount: float, note: str) -> Dict[str, Union[bool, str]]:
        """
        Requests money from another user to the current user.

        Args:
            sender_user (User): The user requesting the money (will be the receiver of the payment).
            receiver_email (str): The email of the user from whom money is requested (will be the sender of the payment).
            amount (float): The amount of money to request.
            note (str): A note for the request.

        Returns:
            Dict: A dictionary containing 'request_status' (bool) and 'message' (str).
        """
        requester_data = self._get_user_data(sender_user) # This is the person initiating the request
        payer_uuid = self._get_user_uuid_from_email(receiver_email)
        payer_data = self.users.get(payer_uuid)

        if not requester_data:
            return {"request_status": False, "message": f"Requester user {sender_user.email} not found."}
        if not payer_data:
            return {"request_status": False, "message": f"Payer user {receiver_email} not found."}
        if amount <= 0:
            return {"request_status": False, "message": "Amount must be positive."}

        transaction_id = self._generate_unique_id()
        new_transaction = {
            "id": transaction_id,
            "sender": payer_data["id"], # Payer is sender in the actual payment
            "receiver": requester_data["id"], # Requester is receiver in the actual payment
            "amount": amount,
            "note": note,
            "status": "pending", # Request starts as pending
            "timestamp": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        }
        self.transactions[transaction_id] = new_transaction

        # Create notifications for requester and payer
        self.notifications[self._generate_unique_id()] = {
            "id": self._generate_unique_id(), # New UUID for notification
            "user": requester_data["id"],
            "type": "payment_request_sent",
            "message": f"You requested ${amount:.2f} from {payer_data['first_name']} {payer_data['last_name']}.",
            "read": False,
            "notification_time": new_transaction["timestamp"]
        }
        self.notifications[self._generate_unique_id()] = {
            "id": self._generate_unique_id(), # New UUID for notification
            "user": payer_data["id"],
            "type": "payment_request_received",
            "message": f"{requester_data['first_name']} {requester_data['last_name']} requested ${amount:.2f}.",
            "read": False,
            "notification_time": new_transaction["timestamp"]
        }

        print(f"Transaction {transaction_id}: {sender_user.email} requested ${amount} from {receiver_email}")
        return {"request_status": True, "transaction_id": transaction_id}
    
    # Signature change: transaction_id from int to str (UUID) for realism
    def get_transaction_details(self, transaction_id: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves details of a specific transaction.

        Args:
            transaction_id (str): The ID (UUID) of the transaction.

        Returns:
            Dict: A dictionary containing 'transaction_status' (bool) and 'transaction_details' (Dict) if successful.
        """
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            return {"transaction_status": False, "transaction_details": {}}
        return {"transaction_status": True, "transaction_details": copy.deepcopy(transaction)}

    def list_user_transactions(self, user: User) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Lists all transactions (sent and received) for the current user.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'transactions_status' (bool) and 'transactions' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"transactions_status": False, "transactions": []}

        user_transactions = [
            copy.deepcopy(t) for t in self.transactions.values()
            if t["sender"] == user_data["id"] or t["receiver"] == user_data["id"]
        ]
        user_transactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True) # Sort by timestamp
        return {"transactions_status": True, "transactions": user_transactions}

    # ================
    # Payment Methods
    # ================

    def add_payment_card(
        self,
        user: User,
        card_name: str,
        owner_name: str,
        card_number: str, # Assume this can be full number for input, then masked
        expiry_year: int,
        expiry_month: int,
        cvv_number: str, # Will not store, just for input validation (dummy)
        is_default: bool = False,
    ) -> Dict[str, Union[bool, str]]:
        """
        Adds a new payment card for the current user.

        Args:
            user (User): The current user object.
            card_name (str): A nickname for the card (e.g., "My Visa").
            owner_name (str): The name of the card owner.
            card_number (str): The full card number.
            expiry_year (int): The expiry year (e.g., 2028).
            expiry_month (int): The expiry month (1-12).
            cvv_number (str): The CVV number. (Not stored for realism)
            is_default (bool): Whether this card should be set as default.

        Returns:
            Dict: A dictionary containing 'add_status' (bool) and 'card_id' (str) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"add_status": False, "message": "User not found."}

        # Basic validation (dummy)
        if not (1 <= expiry_month <= 12):
            return {"add_status": False, "message": "Invalid expiry month."}
        if not (datetime.datetime.now().year <= expiry_year <= datetime.datetime.now().year + 10):
            return {"add_status": False, "message": "Invalid expiry year."}
        # Mask card number for storage
        masked_card_number = f"**** **** **** {card_number[-4:]}" if len(card_number) >= 4 else "****"

        new_card_uuid = self._generate_unique_id()
        new_card = {
            "id": new_card_uuid,
            "card_name": card_name,
            "owner_name": owner_name,
            "card_number": masked_card_number,
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
            "is_default": is_default,
            "created_at": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z",
            "last_modified": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        }

        user_payment_cards = user_data.get("payment_cards", {})
        
        # If new card is default, set existing default to false
        if is_default:
            for card_id, card_info in user_payment_cards.items():
                if card_info.get("is_default"):
                    user_payment_cards[card_id]["is_default"] = False
                    break

        user_payment_cards[new_card_uuid] = new_card
        self._update_user_data(user, "payment_cards", user_payment_cards)

        return {"add_status": True, "card_id": new_card_uuid}


    def list_payment_methods(self, user: User) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Lists all payment methods associated with the current user.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'payment_methods_status' (bool) and 'payment_methods' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"payment_methods_status": False, "payment_methods": []}

        payment_methods = list(user_data.get("payment_cards", {}).values())
        return {"payment_methods_status": True, "payment_methods": copy.deepcopy(payment_methods)}

    # Signature change: payment_method_id from int to str (UUID) for realism
    def set_default_payment_method(self, user: User, payment_method_id: str) -> Dict[str, bool]:
        """
        Set a specific payment method as the default for the current user.

        Args:
            user (User): The current user object.
            payment_method_id (str): The ID (UUID) of the payment method to set as default.

        Returns:
            Dict[str, bool]: {"set_default_status": True} if successful, {"set_default_status": False} otherwise.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"set_default_status": False, "message": "User not found."}

        user_payment_cards = user_data.get("payment_cards", {})
        if payment_method_id not in user_payment_cards:
            return {"set_default_status": False, "message": f"Payment method with ID {payment_method_id} not found."}

        # Clear any existing default for this user
        for card_id, card_info in user_payment_cards.items():
            if card_info.get("is_default"):
                user_payment_cards[card_id]["is_default"] = False
                user_payment_cards[card_id]["last_modified"] = datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"

        user_payment_cards[payment_method_id]["is_default"] = True
        user_payment_cards[payment_method_id]["last_modified"] = datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        self._update_user_data(user, "payment_cards", user_payment_cards)
        return {"set_default_status": True}

    # Signature change: payment_method_id from int to str (UUID) for realism
    def delete_payment_method(self, user: User, payment_method_id: str) -> Dict[str, bool]:
        """
        Delete a specific payment method for the current user.

        Args:
            user (User): The current user object.
            payment_method_id (str): The ID (UUID) of the payment method to delete.

        Returns:
            Dict[str, bool]: {"delete_status": True} if successful, {"delete_status": False} otherwise.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"delete_status": False, "message": "User not found."}

        user_payment_cards = user_data.get("payment_cards", {})
        if payment_method_id not in user_payment_cards:
            return {"delete_status": False, "message": f"Payment method with ID {payment_method_id} not found."}
        
        del user_payment_cards[payment_method_id]
        self._update_user_data(user, "payment_cards", user_payment_cards)
        return {"delete_status": True}

    # ================
    # Notifications
    # ================

    def get_unread_notification_count(self) -> Dict[str, Union[bool, int]]:
        """
        Retrieves the count of unread notifications for the current user.

        Returns:
            Dict: A dictionary containing 'count_status' (bool) and 'unread_count' (int).
        """
        if not self.current_user:
            return {"count_status": False, "unread_count": 0, "message": "No current user set."}
        
        unread_count = sum(1 for notif in self.notifications.values() if notif["user"] == self.current_user and not notif["read"])
        return {"count_status": True, "unread_count": unread_count}

    def delete_all_my_notifications(self) -> Dict[str, bool]:
        """
        Delete all notifications for the current user.

        Returns:
            Dict: A dictionary containing 'delete_status' (bool).
        """
        if not self.current_user:
            return {"delete_status": False, "message": "No current user set."}
        
        to_delete_ids = [nid for nid, notif in self.notifications.items() if notif["user"] == self.current_user]
        for nid in to_delete_ids:
            if nid in self.notifications: # Check before deleting
                del self.notifications[nid]
        
        return {"delete_status": True}

    def mark_my_notifications(self, read_status: bool) -> Dict[str, bool]:
        """
        Mark all notifications for the current user as read or unread.

        Args:
            read_status (bool): Whether to mark as read (True) or unread (False).

        Returns:
            Dict: A dictionary containing 'mark_status' (bool).
        """
        if not self.current_user:
            return {"mark_status": False, "message": "No current user set."}
        
        for notif in self.notifications.values():
            if notif["user"] == self.current_user:
                notif["read"] = read_status
        
        return {"mark_status": True}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        # Re-run the initial data conversion to reset maps and UUIDs
        global DEFAULT_STATE
        DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)
        self._load_scenario(DEFAULT_STATE)
        print("VenmoApis: All dummy data reset to default state.")
        return {"reset_status": True}