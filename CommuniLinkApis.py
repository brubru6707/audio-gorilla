import time
import random
import uuid
from copy import deepcopy
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

# Current time for realistic date generation
current_datetime = datetime.now()

class CommuniLinkUser:
    def __init__(self, user_id: str, email: str = None):
        self.user_id = user_id
        self.email = email

DEFAULT_COMMUNILINK_STATE = {
    "users": {},
    "current_user_id": None,
    "billing_history": [],
    "support_tickets": [],
    "service_plans": {
        "basic": {"price_per_sms": 0.05, "price_per_minute": 0.10, "description": "Basic communication plan: Affordable messaging and calling rates."},
        "premium": {"price_per_sms": 0.02, "price_per_minute": 0.05, "description": "Premium communication plan: Enjoy significantly lower rates on SMS and calls, plus priority support."},
        "unlimited": {"price_per_sms": 0.00, "price_per_minute": 0.00, "monthly_fee": 30.00, "description": "Unlimited plan: All SMS and calls are free within the network for a flat monthly fee."},
    },
    "active_plan": "basic", # This likely refers to a global default, not per user. We'll set user-specific plans below.
    "network_status": "operational",
    "network_logs": [], # Added for more general state
    "system_notifications": [], # Added for more general state
}

_user_email_to_uuid_map = {} # Global map to resolve email to UUIDs

def generate_random_past_date(max_days_ago=365):
    days_ago = random.randint(1, max_days_ago)
    return (current_datetime - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).isoformat()

def generate_phone_number():
    # Generates a realistic-looking US phone number
    area_code = random.randint(200, 999)
    prefix = random.randint(100, 999)
    line_number = random.randint(1000, 9999)
    return f"+1{area_code}{prefix}{line_number}"

def _create_user_data(email, first_name, last_name, phone_number, balance, friends_emails, sms_history, call_history, settings, service_plan):
    user_id = str(uuid.uuid4())
    _user_email_to_uuid_map[email] = user_id

    # Resolve friends immediately for newly created users
    friends_ids = []
    for friend_email in friends_emails:
        friends_ids.append(_user_email_to_uuid_map.get(friend_email, friend_email)) # Use uuid if exists, otherwise keep email for later resolution

    # Process SMS history, ensuring sender_id and receiver_id are UUIDs where possible
    processed_sms_history = []
    for sms in sms_history:
        sms_entry = {**sms, "sms_id": str(uuid.uuid4())}
        if not sms.get("is_external"):
            sms_entry["sender_id"] = _user_email_to_uuid_map.get(sms.get("sender"), sms.get("sender"))
            sms_entry["receiver_id"] = _user_email_to_uuid_map.get(sms.get("receiver"), sms.get("receiver"))
        processed_sms_history.append(sms_entry)

    # Process Call history, ensuring caller_id and receiver_id are UUIDs where possible
    processed_call_history = []
    for call in call_history:
        call_entry = {**call, "call_id": str(uuid.uuid4())}
        if not call.get("is_external"):
            call_entry["caller_id"] = _user_email_to_uuid_map.get(call.get("caller"), call.get("caller"))
            call_entry["receiver_id"] = _user_email_to_uuid_map.get(call.get("receiver"), call.get("receiver"))
        processed_call_history.append(call_entry)

    return user_id, {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone_number": phone_number,
        "balance": balance,
        "sms_history": processed_sms_history,
        "call_history": processed_call_history,
        "settings": settings,
        "friends": friends_ids, # These will be resolved to UUIDs later
        "password_hash": "dummy_hash",
        "service_plan": service_plan, # User-specific service plan
        "last_login": generate_random_past_date(30), # New: Last login time
        "is_active": random.choice([True, True, False]), # New: User activity status
    }

# --- Initial Users (provided in the prompt) ---
users_initial_data = [
    ("alice.smith@communi.link", "Alice", "Smith", "+12025550101", 100.00, ["bob.johnson@communi.link", "charlie.brown@communi.link"],
     [
         {"sender": "alice.smith@communi.link", "receiver": "bob.johnson@communi.link", "message": "Hey Bob, planning anything for the weekend?", "timestamp": (current_datetime - timedelta(days=2, hours=10)).isoformat()},
         {"sender": "bob.johnson@communi.link", "receiver": "alice.smith@communi.link", "message": "Just chilling. Wanna grab coffee?", "timestamp": (current_datetime - timedelta(days=2, hours=9, minutes=30)).isoformat()},
         {"sender": "alice.smith@communi.link", "receiver": "+12025550105", "message": "Reminder: Dentist appointment tomorrow at 2 PM.", "timestamp": (current_datetime - timedelta(hours=5)).isoformat(), "is_external": True},
     ],
     [
         {"caller": "alice.smith@communi.link", "receiver": "charlie.brown@communi.link", "duration_minutes": 5, "timestamp": (current_datetime - timedelta(days=3)).isoformat(), "type": "outgoing"},
         {"caller": "diana.miller@communi.link", "receiver": "alice.smith@communi.link", "duration_minutes": 2, "timestamp": (current_datetime - timedelta(days=1)).isoformat(), "type": "incoming"},
     ],
     {"sms_notifications": True, "call_forwarding_enabled": False, "call_forwarding_number": ""}, "premium"),

    ("bob.johnson@communi.link", "Robert", "Johnson", "+12025550102", 50.00, ["alice.smith@communi.link", "charlie.brown@communi.link"],
     [
         {"sender": "bob.johnson@communi.link", "receiver": "alice.smith@communi.link", "message": "Just chilling. Wanna grab coffee?", "timestamp": (current_datetime - timedelta(days=2, hours=9, minutes=30)).isoformat()},
     ],
     [
         {"caller": "bob.johnson@communi.link", "receiver": "+12025550103", "duration_minutes": 10, "timestamp": (current_datetime - timedelta(hours=12)).isoformat(), "type": "outgoing", "is_external": True},
     ],
     {"sms_notifications": False, "call_forwarding_enabled": True, "call_forwarding_number": "+12025550103"}, "basic"),

    ("charlie.brown@communi.link", "Charles", "Brown", "+12025550104", 250.00, ["alice.smith@communi.link", "bob.johnson@communi.link", "diana.miller@communi.link"],
     [
         {"sender": "charlie.brown@communi.link", "receiver": "alice.smith@communi.link", "message": "Don't forget our meeting at 3 PM!", "timestamp": (current_datetime - timedelta(hours=2)).isoformat()},
     ],
     [
         {"caller": "alice.smith@communi.link", "receiver": "charlie.brown@communi.link", "duration_minutes": 5, "timestamp": (current_datetime - timedelta(days=3)).isoformat(), "type": "incoming"},
     ],
     {"sms_notifications": True, "call_forwarding_enabled": False, "call_forwarding_number": ""}, "unlimited"),

    ("diana.miller@communi.link", "Diana", "Miller", "+12025550105", 180.50, ["charlie.brown@communi.link"],
     [
         {"sender": "diana.miller@communi.link", "receiver": "charlie.brown@communi.link", "message": "Got the report ready for review.", "timestamp": (current_datetime - timedelta(hours=4)).isoformat()},
     ],
     [
         {"caller": "diana.miller@communi.link", "receiver": "alice.smith@communi.link", "duration_minutes": 2, "timestamp": (current_datetime - timedelta(days=1)).isoformat(), "type": "outgoing"},
         {"caller": "charlie.brown@communi.link", "receiver": "diana.miller@communi.link", "duration_minutes": 7, "timestamp": (current_datetime - timedelta(hours=6)).isoformat(), "type": "incoming"},
     ],
     {"sms_notifications": True, "call_forwarding_enabled": True, "call_forwarding_number": "+12025550106"}, "premium"),

    ("eva.gonzalez@communi.link", "Eva", "Gonzalez", "+12025550107", 75.20, [],
     [],
     [
         {"caller": "eva.gonzalez@communi.link", "receiver": "+12025550108", "duration_minutes": 1, "timestamp": (current_datetime - timedelta(minutes=30)).isoformat(), "type": "outgoing", "is_external": True},
     ],
     {"sms_notifications": False, "call_forwarding_enabled": False, "call_forwarding_number": ""}, "basic"),

    ("frank.white@communi.link", "Frank", "White", "+12025550109", 300.00, ["alice.smith@communi.link"],
     [
         {"sender": "frank.white@communi.link", "receiver": "alice.smith@communi.link", "message": "Let's catch up soon!", "timestamp": (current_datetime - timedelta(days=7)).isoformat()},
     ],
     [],
     {"sms_notifications": True, "call_forwarding_enabled": False, "call_forwarding_number": ""}, "unlimited")
]

# Populate initial users
for email, first_name, last_name, phone_number, balance, friends_emails, sms_hist, call_hist, settings, service_plan in users_initial_data:
    user_id, user_data = _create_user_data(email, first_name, last_name, phone_number, balance, friends_emails, sms_hist, call_hist, settings, service_plan)
    DEFAULT_COMMUNILINK_STATE["users"][user_id] = user_data

# --- Generate 44 more diverse and realistic users ---
first_names = ["Sophia", "Liam", "Olivia", "Noah", "Ava", "Jackson", "Isabella", "Aiden", "Mia", "Lucas", "Harper", "Ethan", "Evelyn", "Mason", "Abigail", "Caleb", "Charlotte", "Logan", "Amelia", "Michael", "Ella", "Jacob", "Aria", "Daniel", "Chloe", "Samuel", "Grace", "David", "Victoria", "Joseph", "Penelope", "Matthew", "Riley", "Benjamin", "Layla", "Andrew", "Lily", "Gabriel", "Natalie", "Christopher", "Hannah", "James", "Zoe", "Ryan", "Scarlett", "Nathan", "Addison", "Christian", "Aubrey", "Joshua"]
last_names = ["Chen", "Kim", "Singh", "Lopez", "Garcia", "Nguyen", "Davis", "Jackson", "Harris", "White", "Moore", "Clark", "Lewis", "Baker", "Adams", "Hill", "Nelson", "Carter", "Mitchell", "Roberts", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders"]

current_user_emails = list(_user_email_to_uuid_map.keys())

for i in range(44): # Generate 44 additional users
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}{random.randint(1,999)}@communi.link"
    
    # Ensure unique email
    while email in _user_email_to_uuid_map:
        email = f"{first.lower()}.{last.lower()}{random.randint(1,999)}@communi.link"

    phone = generate_phone_number()
    balance = round(random.uniform(5.00, 1000.00), 2)

    # Select friends from existing users
    num_friends = random.randint(0, 5)
    possible_friends_emails = list(_user_email_to_uuid_map.keys())
    # Ensure they don't add themselves as a friend and try to add existing users
    friends_for_new_user = random.sample(possible_friends_emails, min(num_friends, len(possible_friends_emails)))

    # Generate realistic SMS history
    sms_history = []
    num_sms = random.randint(0, 5)
    for _ in range(num_sms):
        receiver_email = random.choice(current_user_emails + [generate_phone_number() + "@external.com"]) # Mix internal/external
        sms_history.append({
            "sender": email,
            "receiver": receiver_email,
            "message": random.choice(["Hi there!", "Are you free later?", "Got it, thanks!", "See you soon!", "On my way."]),
            "timestamp": generate_random_past_date(90),
            "is_external": "@external.com" in receiver_email or "+" in receiver_email
        })
        # Add a reciprocal message from receiver if internal
        if "@communi.link" in receiver_email:
             sms_history.append({
                "sender": receiver_email,
                "receiver": email,
                "message": random.choice(["Hey!", "Yep!", "Sounds good!", "Awesome!"]),
                "timestamp": generate_random_past_date(89),
                "is_external": False
            })

    # Generate realistic Call history
    call_history = []
    num_calls = random.randint(0, 3)
    for _ in range(num_calls):
        call_type = random.choice(["outgoing", "incoming"])
        duration = random.randint(1, 30)
        external_call = random.random() < 0.3 # 30% chance of external call
        
        if external_call:
            other_party = generate_phone_number()
            caller_email_or_number = email if call_type == "outgoing" else other_party
            receiver_email_or_number = other_party if call_type == "outgoing" else email
        else:
            other_party_email = random.choice(current_user_emails)
            caller_email_or_number = email if call_type == "outgoing" else other_party_email
            receiver_email_or_number = other_party_email if call_type == "outgoing" else email
        
        call_history.append({
            "caller": caller_email_or_number,
            "receiver": receiver_email_or_number,
            "duration_minutes": duration,
            "timestamp": generate_random_past_date(90),
            "type": call_type,
            "is_external": external_call
        })


    settings = {
        "sms_notifications": random.choice([True, False]),
        "call_forwarding_enabled": random.choice([True, False]),
        "call_forwarding_number": generate_phone_number() if random.random() < 0.2 else "" # 20% have forwarding
    }
    service_plan = random.choice(list(DEFAULT_COMMUNILINK_STATE["service_plans"].keys()))

    user_id, user_data = _create_user_data(email, first, last, phone, balance, friends_for_new_user, sms_history, call_history, settings, service_plan)
    DEFAULT_COMMUNILINK_STATE["users"][user_id] = user_data
    current_user_emails.append(email) # Add new user to possible friends for subsequent users

# --- Final Resolution of Friends (needed because some friends might have been added later) ---
all_user_uuids = list(_user_email_to_uuid_map.values())
for user_id, user_data in DEFAULT_COMMUNILINK_STATE["users"].items():
    resolved_friends = []
    for friend_item in user_data["friends"]:
        if friend_item in _user_email_to_uuid_map: # Check if it's an email that has a UUID now
            resolved_friends.append(_user_email_to_uuid_map[friend_item])
        elif friend_item in all_user_uuids: # Already a UUID
            resolved_friends.append(friend_item)
        # If it's an email that wasn't found (e.g., placeholder for non-CommuniLink user), or an invalid ID, skip it
    
    # Ensure friends list only contains valid UUIDs and no duplicates, and not self
    user_data["friends"] = list(set([f for f in resolved_friends if f != user_id]))


# --- Add more diverse billing history ---
all_user_ids = list(DEFAULT_COMMUNILINK_STATE["users"].keys())
billing_types = ["plan_charge", "sms_charge", "call_charge", "top_up"]
descriptions = {
    "plan_charge": ["Monthly {plan} plan charge", "Subscription renewal for {plan} plan"],
    "sms_charge": ["SMS charge for {count} messages", "Messaging fees for recent activity"],
    "call_charge": ["Call charge for {minutes} minutes", "Voice call charges"],
    "top_up": ["Account top-up via credit card", "Credit added to balance", "Payment received"]
}

for _ in range(70): # Add 70 more billing records
    user_id = random.choice(all_user_ids)
    user_email = DEFAULT_COMMUNILINK_STATE["users"][user_id]["email"]
    user_plan = DEFAULT_COMMUNILINK_STATE["users"][user_id]["service_plan"]
    
    trans_type = random.choice(billing_types)
    amount = 0.0

    if trans_type == "plan_charge":
        amount = -DEFAULT_COMMUNILINK_STATE["service_plans"][user_plan].get("monthly_fee", round(random.uniform(5.00, 20.00), 2))
        desc = random.choice(descriptions[trans_type]).format(plan=user_plan.capitalize())
    elif trans_type == "sms_charge":
        count = random.randint(1, 50)
        cost_per_sms = DEFAULT_COMMUNILINK_STATE["service_plans"][user_plan]["price_per_sms"]
        amount = -round(count * cost_per_sms, 2)
        desc = random.choice(descriptions[trans_type]).format(count=count)
    elif trans_type == "call_charge":
        minutes = random.randint(1, 120)
        cost_per_minute = DEFAULT_COMMUNILINK_STATE["service_plans"][user_plan]["price_per_minute"]
        amount = -round(minutes * cost_per_minute, 2)
        desc = random.choice(descriptions[trans_type]).format(minutes=minutes)
    else: # top_up
        amount = round(random.uniform(10.00, 100.00), 2)
        desc = random.choice(descriptions[trans_type])

    DEFAULT_COMMUNILINK_STATE["billing_history"].append({
        "transaction_id": str(uuid.uuid4()),
        "user_id": user_id,
        "type": trans_type,
        "amount": amount,
        "date": generate_random_past_date(180),
        "description": desc
    })

# --- Add more diverse support tickets ---
ticket_subjects = [
    "Connectivity Issue", "Billing Discrepancy", "Account Suspension",
    "Feature Request", "Bug Report", "Password Reset", "Call Quality",
    "SMS Delivery Failure", "Plan Upgrade/Downgrade", "Spam Report"
]
ticket_statuses = ["open", "pending", "closed"]
agent_notes_options = [
    "Investigating connection logs.", "Forwarded to billing department.",
    "Resolved, user account reactivated.", "Added to feature backlog.",
    "Acknowledged, team looking into it.", "Password reset link sent.",
    "Adjusted call quality settings.", "Checked delivery reports, re-sent.",
    "Plan change processed.", "User blocked, reported to security."
]

for _ in range(25): # Add 25 more support tickets
    user_id = random.choice(all_user_ids)
    subject = random.choice(ticket_subjects)
    status = random.choice(ticket_statuses)
    
    created_at = generate_random_past_date(90)
    resolved_at = None
    agent_notes = None

    if status == "closed":
        resolved_at = (datetime.fromisoformat(created_at) + timedelta(days=random.randint(1, 10))).isoformat()
        agent_notes = random.choice(agent_notes_options)
    elif status == "pending":
        agent_notes = random.choice(agent_notes_options)

    DEFAULT_COMMUNILINK_STATE["support_tickets"].append({
        "ticket_id": str(uuid.uuid4()),
        "user_id": user_id,
        "subject": subject,
        "status": status,
        "description": f"Problem with: {subject.lower()}.",
        "created_at": created_at,
        "resolved_at": resolved_at,
        "agent_notes": agent_notes
    })

# --- Add network logs and system notifications ---
network_log_messages = [
    "API endpoint /user/profile accessed by user {user_id}",
    "SMS sent from {sender_id} to {receiver_id}",
    "Call initiated by {caller_id}",
    "Database backup completed successfully",
    "System load: {load_percentage}%",
    "New user registered: {user_id}",
    "Payment processed for transaction {transaction_id}"
]

for _ in range(100): # Add 100 network logs
    log_time = generate_random_past_date(10)
    log_message = random.choice(network_log_messages)
    
    # Try to insert real IDs where placeholders exist
    if "{user_id}" in log_message and all_user_ids:
        log_message = log_message.replace("{user_id}", random.choice(all_user_ids))
    if "{sender_id}" in log_message and all_user_ids:
        log_message = log_message.replace("{sender_id}", random.choice(all_user_ids))
    if "{receiver_id}" in log_message and all_user_ids:
        log_message = log_message.replace("{receiver_id}", random.choice(all_user_ids))
    if "{caller_id}" in log_message and all_user_ids:
        log_message = log_message.replace("{caller_id}", random.choice(all_user_ids))
    if "{load_percentage}" in log_message:
        log_message = log_message.replace("{load_percentage}", str(random.randint(10, 90)))
    if "{transaction_id}" in log_message and DEFAULT_COMMUNILINK_STATE["billing_history"]:
        log_message = log_message.replace("{transaction_id}", random.choice([t["transaction_id"] for t in DEFAULT_COMMUNILINK_STATE["billing_history"]]))

    DEFAULT_COMMUNILINK_STATE["network_logs"].append({
        "timestamp": log_time,
        "level": random.choice(["INFO", "WARNING", "ERROR"]),
        "message": log_message
    })

system_notification_messages = [
    "Scheduled maintenance: All services will be affected on {date} from {time_start} to {time_end} EDT.",
    "New feature alert: Group calling is now available!",
    "Security update: Please review our updated privacy policy.",
    "Service restoration: All services are now fully operational.",
    "Promotion: Get 50% off your next month with code {promo_code}!",
    "Network congestion detected in your area, calls may experience slight delay."
]

for _ in range(5): # Add a few system notifications
    notification_message = random.choice(system_notification_messages)
    if "{date}" in notification_message:
        future_date = (current_datetime + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        time_start = f"{random.randint(8, 10):02d}:00"
        time_end = f"{random.randint(11, 13):02d}:00"
        notification_message = notification_message.replace("{date}", future_date).replace("{time_start}", time_start).replace("{time_end}", time_end)
    if "{promo_code}" in notification_message:
        notification_message = notification_message.replace("{promo_code}", "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8)))
        
    DEFAULT_COMMUNILINK_STATE["system_notifications"].append({
        "notification_id": str(uuid.uuid4()),
        "timestamp": generate_random_past_date(7),
        "message": notification_message,
        "is_read": random.choice([True, False, False]) # More likely to be unread if recent
    })


# --- Set current_user_id ---
if "alice.smith@communi.link" in _user_email_to_uuid_map:
    DEFAULT_COMMUNILINK_STATE["current_user_id"] = _user_email_to_uuid_map["alice.smith@communi.link"]
elif all_user_ids: # Fallback to a random user if Alice isn't present
    DEFAULT_COMMUNILINK_STATE["current_user_id"] = random.choice(all_user_ids)


# --- Output the generated DEFAULT_COMMUNILINK_STATE ---
import json

# For demonstration, print counts and a sample of a user
print(f"Total number of users generated: {len(DEFAULT_COMMUNILINK_STATE['users'])}")
print(f"Total billing history records: {len(DEFAULT_COMMUNILINK_STATE['billing_history'])}")
print(f"Total support tickets: {len(DEFAULT_COMMUNILINK_STATE['support_tickets'])}")
print(f"Total network logs: {len(DEFAULT_COMMUNILINK_STATE['network_logs'])}")
print(f"Total system notifications: {len(DEFAULT_COMMUNILINK_STATE['system_notifications'])}")

# To see a full example, uncomment the following and save to a file
# with open('diverse_communi_link_state.json', 'w') as f:
#     json.dump(DEFAULT_COMMUNILINK_STATE, f, indent=2)

# To print a single user's data as a sample:
if DEFAULT_COMMUNILINK_STATE["current_user_id"]:
    print("\nSample Current User Data:")
    print(json.dumps(DEFAULT_COMMUNILINK_STATE["users"][DEFAULT_COMMUNILINK_STATE["current_user_id"]], indent=2))

class CommuniLinkApis:
    """
    A dummy API class for CommuniLink, simulating SMS messaging and voice calling
    functionality. This class provides an in-memory backend for development
    and testing purposes without making actual API calls.
    """

    def __init__(self):
        """
        Initializes the CommuniLinkApis instance, setting up the in-memory
        data stores for SMS messages and voice calls, and loading the default
        scenario.
        """
        self.users: Dict = {}
        self.current_user_id: Optional[str] = None
        self.billing_history: List[Dict] = []
        self.support_tickets: List[Dict] = []
        self.service_plans: Dict = {}
        self.active_plan: str = ""
        self.network_status: str = ""

        self._api_description = "This tool belongs to the CommuniLink API, which provides core functionality for SMS messaging and voice calls."
        self._load_scenario(DEFAULT_COMMUNILINK_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain keys like "users", "current_user_id", etc.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_COMMUNILINK_STATE)

        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.current_user_id = scenario.get("current_user_id", DEFAULT_STATE_COPY["current_user_id"])
        self.billing_history = scenario.get("billing_history", DEFAULT_STATE_COPY["billing_history"])
        self.support_tickets = scenario.get("support_tickets", DEFAULT_STATE_COPY["support_tickets"])
        self.service_plans = scenario.get("service_plans", DEFAULT_STATE_COPY["service_plans"])
        self.active_plan = scenario.get("active_plan", DEFAULT_STATE_COPY["active_plan"])
        self.network_status = scenario.get("network_status", DEFAULT_STATE_COPY["network_status"])

        print(f"CommuniLinkApis: Loaded scenario. Current User ID: {self.current_user_id}")

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """Helper to get user_id from email."""
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """Helper to get user email from user_id."""
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for dummy entities.
        """
        return str(uuid.uuid4())

    def send_sms(self, from_number: str, to_number: str, message: str) -> Dict[str, Union[str, int]]:
        """
        Simulates sending an SMS message. The message status progresses
        from 'queued' to 'sent' and then 'delivered' over a short simulated time.

        Args:
            from_number (str): The sender's phone number (E.164 format, e.g., "+15551234567").
            to_number (str): The recipient's phone number (E.164 format, e.g., "+15559876543").
            message (str): The text content of the SMS.

        Returns:
            Dict: A dictionary representing the simulated SMS message object,
                  including 'id', 'from', 'to', 'message', 'status', and 'timestamp'.
                  Returns an error dictionary if parameters are missing.
        """
        if not from_number or not to_number or not message:
            return {"code": "MISSING_PARAMS", "message": "Missing required parameters: from_number, to_number, and message."}

        sender_user_id = None
        for u_id, user_data in self.users.items():
            if user_data["phone_number"] == from_number:
                sender_user_id = u_id
                break
        
        if not sender_user_id:
            return {"code": "INVALID_FROM_NUMBER", "message": "Sender phone number not associated with any user."}
        
        sender_user = self.users[sender_user_id]

        sms_cost = self.service_plans[self.active_plan]["price_per_sms"]
        if sender_user["balance"] < sms_cost:
            return {"code": "INSUFFICIENT_BALANCE", "message": "Insufficient balance to send SMS."}
        
        sender_user["balance"] -= sms_cost
        self.billing_history.append({
            "transaction_id": self._generate_unique_id(),
            "type": "sms_charge",
            "user_id": sender_user_id,
            "amount": -sms_cost,
            "date": datetime.now().isoformat(),
            "description": f"SMS to {to_number}"
        })

        new_sms_id = self._generate_unique_id()
        new_sms = {
            "sms_id": new_sms_id,
            "sender": from_number,
            "sender_id": sender_user_id,
            "receiver": to_number,
            "message": message,
            "status": "queued",
            "timestamp": datetime.now().isoformat()
        }
        
        is_external = True
        receiver_user_id = None
        for u_id, user_data in self.users.items():
            if user_data["phone_number"] == to_number:
                receiver_user_id = u_id
                is_external = False
                break
        
        new_sms["is_external"] = is_external

        sender_user["sms_history"].append(new_sms)
        if receiver_user_id:
            receiver_user = self.users[receiver_user_id]
            receiver_user["sms_history"].append(new_sms)
            print(f"Dummy SMS queued: ID={new_sms['sms_id']} from {sender_user['email']} to {receiver_user['email']}")
        else:
            print(f"Dummy SMS queued: ID={new_sms['sms_id']} from {sender_user['email']} to external number {to_number}")

        time.sleep(0.1)
        new_sms["status"] = "sent"
        time.sleep(0.2)
        new_sms["status"] = "delivered"
        print(f"Dummy SMS ID={new_sms['sms_id']} status updated to 'delivered'")

        return {
            "id": new_sms["sms_id"],
            "from": new_sms["sender"],
            "to": new_sms["receiver"],
            "message": new_sms["message"],
            "status": new_sms["status"],
            "timestamp": new_sms["timestamp"]
        }

    def get_sms_status(self, message_id: str) -> Dict[str, Union[str, int]]:
        """
        Retrieves the current status of a previously sent SMS message.

        Args:
            message_id (str): The unique ID of the SMS message to check.

        Returns:
            Dict: A dictionary representing the SMS message object if found,
                  or an error dictionary if not found.
        """
        time.sleep(0.05)
        sms = None
        for user_data in self.users.values():
            sms = next((msg for msg in user_data["sms_history"] if msg["sms_id"] == message_id), None)
            if sms:
                break

        if not sms:
            return {"code": "SMS_NOT_FOUND", "message": f"SMS message with ID '{message_id}' not found."}

        print(f"Dummy SMS status retrieved for ID={message_id}: {sms['status']}")
        return {
            "id": sms["sms_id"],
            "from": sms["sender"],
            "to": sms["receiver"],
            "message": sms["message"],
            "status": sms["status"],
            "timestamp": sms["timestamp"]
        }

    def make_voice_call(self, from_number: str, to_number: str, audio_url: Optional[str] = None) -> Dict[str, Union[str, int, float]]:
        """
        Simulates initiating an outbound voice call. The call status progresses
        from 'initiated' to 'ringing', 'in-progress', and then 'completed'
        over a simulated time.

        Args:
            from_number (str): The caller's phone number (E.164 format).
            to_number (str): The recipient's phone number (E.164 format).
            audio_url (Optional[str]): Optional URL for audio to play to the recipient
                                       upon connection (e.g., "https://example.com/welcome.mp3").

        Returns:
            Dict: A dictionary representing the simulated voice call object,
                  including 'id', 'from', 'to', 'audioUrl', 'status', 'timestamp',
                  and 'duration' (if completed). Returns an error dictionary
                  if parameters are missing.
        """
        if not from_number or not to_number:
            return {"code": "MISSING_PARAMS", "message": "Missing required parameters: from_number and to_number."}

        caller_user_id = None
        for u_id, user_data in self.users.items():
            if user_data["phone_number"] == from_number:
                caller_user_id = u_id
                break

        if not caller_user_id:
            return {"code": "INVALID_FROM_NUMBER", "message": "Caller phone number not associated with any user."}
        
        caller_user = self.users[caller_user_id]

        new_call_id = self._generate_unique_id()
        new_call = {
            "call_id": new_call_id,
            "caller": from_number,
            "caller_id": caller_user_id,
            "receiver": to_number,
            "audioUrl": audio_url,
            "status": "initiated",
            "timestamp": datetime.now().isoformat(),
            "duration": 0
        }
        
        is_external = True
        receiver_user_id = None
        for u_id, user_data in self.users.items():
            if user_data["phone_number"] == to_number:
                receiver_user_id = u_id
                is_external = False
                break
        
        new_call["is_external"] = is_external

        caller_user["call_history"].append(new_call)
        if receiver_user_id:
            receiver_user = self.users[receiver_user_id]
            receiver_user["call_history"].append(new_call)
            print(f"Dummy Call initiated: ID={new_call['call_id']} from {caller_user['email']} to {receiver_user['email']}")
        else:
            print(f"Dummy Call initiated: ID={new_call['call_id']} from {caller_user['email']} to external number {to_number}")

        time.sleep(0.15)
        new_call["status"] = "ringing"
        time.sleep(0.5)
        new_call["status"] = "in-progress"
        
        call_duration_seconds = round(random.uniform(30, 120))
        time.sleep(min(call_duration_seconds / 10, 2))
        
        new_call["duration"] = call_duration_seconds
        
        call_cost = self.service_plans[self.active_plan]["price_per_minute"] * (new_call["duration"] / 60)
        
        if caller_user["balance"] < call_cost:
            new_call["status"] = "failed_insufficient_balance"
            print(f"Dummy Call ID={new_call['call_id']} failed due to insufficient balance.")
            return {"code": "INSUFFICIENT_BALANCE", "message": "Insufficient balance to make call."}

        caller_user["balance"] -= call_cost
        self.billing_history.append({
            "transaction_id": self._generate_unique_id(),
            "type": "voice_call_charge",
            "user_id": caller_user_id,
            "amount": -call_cost,
            "date": datetime.now().isoformat(),
            "description": f"Call to {to_number}, duration {new_call['duration']}s"
        })
        
        new_call["status"] = "completed"
        print(f"Dummy Call ID={new_call['call_id']} status updated to 'completed'")
        
        return {
            "id": new_call["call_id"],
            "from": new_call["caller"],
            "to": new_call["receiver"],
            "audioUrl": new_call["audioUrl"],
            "status": new_call["status"],
            "timestamp": new_call["timestamp"],
            "duration": new_call["duration"]
        }

    def get_voice_call_status(self, call_id: str) -> Dict[str, Union[str, int, float]]:
        """
        Retrieves the current status of a previously initiated voice call.

        Args:
            call_id (str): The unique ID of the voice call to check.

        Returns:
            Dict: A dictionary representing the voice call object if found,
                  or an error dictionary if not found.
        """
        time.sleep(0.05)
        call = None
        for user_data in self.users.values():
            call = next((c for c in user_data["call_history"] if c["call_id"] == call_id), None)
            if call:
                break

        if not call:
            return {"code": "CALL_NOT_FOUND", "message": f"Voice call with ID '{call_id}' not found."}

        print(f"Dummy Call status retrieved for ID={call_id}: {call['status']}")
        return {
            "id": call["call_id"],
            "from": call["caller"],
            "to": call["receiver"],
            "audioUrl": call["audioUrl"],
            "status": call["status"],
            "timestamp": call["timestamp"],
            "duration": call["duration"]
        }

    def get_all_sms_messages(self, user_email: Optional[str] = None) -> Dict[str, Union[List[Dict], str]]:
        """
        Retrieves all simulated SMS messages stored in the dummy backend,
        optionally filtered by user email.

        Args:
            user_email (Optional[str]): If provided, only SMS messages for this user will be returned.

        Returns:
            Dict: A dictionary containing a list of all SMS messages,
                  or an error dictionary if user not found.
        """
        time.sleep(0.05)
        all_sms_messages = []

        if user_email:
            user_id = self._get_user_id_by_email(user_email)
            if not user_id:
                return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}
            user_data = self.users[user_id]
            for msg in user_data["sms_history"]:
                msg_copy = deepcopy(msg)
                if "sender_id" in msg_copy and not msg_copy.get("is_external"):
                    msg_copy["sender_email"] = self._get_user_email_by_id(msg_copy["sender_id"])
                if not msg_copy.get("is_external"):
                    receiver_user_id = self._get_user_id_by_email(msg_copy["receiver"])
                    if receiver_user_id:
                        msg_copy["receiver_email"] = msg_copy["receiver"]
                    else:
                        receiver_user_id_from_phone = None
                        for u_id, u_data in self.users.items():
                            if u_data["phone_number"] == msg_copy["receiver"]:
                                receiver_user_id_from_phone = u_id
                                break
                        if receiver_user_id_from_phone:
                            msg_copy["receiver_email"] = self._get_user_email_by_id(receiver_user_id_from_phone)

                all_sms_messages.append(msg_copy)
        else:
            for user_data in self.users.values():
                for msg in user_data["sms_history"]:
                    msg_copy = deepcopy(msg)
                    if "sender_id" in msg_copy and not msg_copy.get("is_external"):
                        msg_copy["sender_email"] = self._get_user_email_by_id(msg_copy["sender_id"])
                    if not msg_copy.get("is_external"):
                        receiver_user_id = self._get_user_id_by_email(msg_copy["receiver"])
                        if receiver_user_id:
                            msg_copy["receiver_email"] = msg_copy["receiver"]
                        else:
                            receiver_user_id_from_phone = None
                            for u_id, u_data in self.users.items():
                                if u_data["phone_number"] == msg_copy["receiver"]:
                                    receiver_user_id_from_phone = u_id
                                    break
                            if receiver_user_id_from_phone:
                                msg_copy["receiver_email"] = self._get_user_email_by_id(receiver_user_id_from_phone)
                    all_sms_messages.append(msg_copy)
        
        unique_sms = []
        seen_sms_ids = set()
        for sms in all_sms_messages:
            if sms["sms_id"] not in seen_sms_ids:
                unique_sms.append(sms)
                seen_sms_ids.add(sms["sms_id"])

        return {"sms_messages": unique_sms, "status": "success"}

    def get_all_voice_calls(self, user_email: Optional[str] = None) -> Dict[str, Union[List[Dict], str]]:
        """
        Retrieves all simulated voice calls stored in the dummy backend,
        optionally filtered by user email.

        Args:
            user_email (Optional[str]): If provided, only voice calls for this user will be returned.

        Returns:
            Dict: A dictionary containing a list of all voice calls,
                  or an error dictionary if user not found.
        """
        time.sleep(0.05)
        all_voice_calls = []

        if user_email:
            user_id = self._get_user_id_by_email(user_email)
            if not user_id:
                return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}
            user_data = self.users[user_id]
            for call in user_data["call_history"]:
                call_copy = deepcopy(call)
                if "caller_id" in call_copy and not call_copy.get("is_external"):
                    call_copy["caller_email"] = self._get_user_email_by_id(call_copy["caller_id"])
                if not call_copy.get("is_external"):
                    receiver_user_id = self._get_user_id_by_email(call_copy["receiver"])
                    if receiver_user_id:
                        call_copy["receiver_email"] = call_copy["receiver"]
                    else:
                        receiver_user_id_from_phone = None
                        for u_id, u_data in self.users.items():
                            if u_data["phone_number"] == call_copy["receiver"]:
                                receiver_user_id_from_phone = u_id
                                break
                        if receiver_user_id_from_phone:
                            call_copy["receiver_email"] = self._get_user_email_by_id(receiver_user_id_from_phone)
                all_voice_calls.append(call_copy)
        else:
            for user_data in self.users.values():
                for call in user_data["call_history"]:
                    call_copy = deepcopy(call)
                    if "caller_id" in call_copy and not call_copy.get("is_external"):
                        call_copy["caller_email"] = self._get_user_email_by_id(call_copy["caller_id"])
                    if not call_copy.get("is_external"):
                        receiver_user_id = self._get_user_id_by_email(call_copy["receiver"])
                        if receiver_user_id:
                            call_copy["receiver_email"] = call_copy["receiver"]
                        else:
                            receiver_user_id_from_phone = None
                            for u_id, u_data in self.users.items():
                                if u_data["phone_number"] == call_copy["receiver"]:
                                    receiver_user_id_from_phone = u_id
                                    break
                            if receiver_user_id_from_phone:
                                call_copy["receiver_email"] = self._get_user_email_by_id(receiver_user_id_from_phone)
                    all_voice_calls.append(call_copy)
        
        unique_calls = []
        seen_call_ids = set()
        for call in all_voice_calls:
            if call["call_id"] not in seen_call_ids:
                unique_calls.append(call)
                seen_call_ids.add(call["call_id"])

        return {"voice_calls": unique_calls, "status": "success"}

    def get_user_info(self, user_email: str) -> Dict[str, Union[Dict, str]]:
        """
        Retrieves detailed information for a specific user.

        Args:
            user_email (str): The email of the user to retrieve information for.

        Returns:
            Dict: A dictionary containing the user's information,
                  or an error dictionary if user not found.
        """
        user_id = self._get_user_id_by_email(user_email)
        if not user_id:
            return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}

        user_info_copy = deepcopy(self.users[user_id])
        
        friend_emails = []
        for friend_uid in user_info_copy.get("friends", []):
            friend_email = self._get_user_email_by_id(friend_uid)
            if friend_email:
                friend_emails.append(friend_email)
        user_info_copy["friends"] = friend_emails

        user_info_copy.pop("password_hash", None)

        return {"user_info": user_info_copy, "status": "success"}

    def update_user_settings(self, user_email: str, settings: Dict) -> Dict[str, Union[Dict, str]]:
        """
        Updates the settings for a specific user.

        Args:
            user_email (str): The email of the user whose settings are to be updated.
            settings (Dict): A dictionary containing the settings to update (e.g., {"sms_notifications": False}).

        Returns:
            Dict: A dictionary containing the updated user's settings,
                  or an error dictionary if user not found.
        """
        user_id = self._get_user_id_by_email(user_email)
        if not user_id:
            return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}

        self.users[user_id]["settings"].update(settings)
        return {"updated_settings": deepcopy(self.users[user_id]["settings"]), "status": "success", "message": "User settings updated successfully."}

    def get_billing_history(self, user_email: Optional[str] = None) -> Dict[str, Union[List[Dict], str]]:
        """
        Retrieves the billing history for all users or a specific user.

        Args:
            user_email (Optional[str]): If provided, filters billing history for this user.

        Returns:
            Dict: A dictionary containing a list of billing records,
                  or an error dictionary if user not found.
        """
        time.sleep(0.05)
        filtered_history = []
        if user_email:
            user_id = self._get_user_id_by_email(user_email)
            if not user_id:
                return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}
            
            for record in self.billing_history:
                if record.get("user_id") == user_id:
                    record_copy = deepcopy(record)
                    record_copy["user_email"] = user_email
                    filtered_history.append(record_copy)
        else:
            for record in self.billing_history:
                record_copy = deepcopy(record)
                record_copy["user_email"] = self._get_user_email_by_id(record_copy.get("user_id"))
                filtered_history.append(record_copy)
                
        return {"billing_history": filtered_history, "status": "success"}

    def create_support_ticket(self, user_email: str, subject: str, description: str) -> Dict[str, Union[Dict, str]]:
        """
        Creates a new support ticket for a user.

        Args:
            user_email (str): The email of the user creating the ticket.
            subject (str): The subject of the support ticket.
            description (str): A detailed description of the issue.

        Returns:
            Dict: A dictionary representing the created support ticket,
                  or an error dictionary if user not found.
        """
        user_id = self._get_user_id_by_email(user_email)
        if not user_id:
            return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}

        ticket_id = self._generate_unique_id()
        new_ticket = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "subject": subject,
            "description": description,
            "status": "open",
            "created_at": datetime.now().isoformat()
        }
        self.support_tickets.append(new_ticket)
        print(f"Support ticket created: ID={new_ticket['ticket_id']} for {user_email}")
        
        ticket_for_display = deepcopy(new_ticket)
        ticket_for_display["user_email"] = user_email

        return {"support_ticket": ticket_for_display, "status": "success", "message": "Support ticket created successfully."}

    def get_network_status(self) -> Dict[str, str]:
        """
        Retrieves the current network operational status of the CommuniLink service.

        Returns:
            Dict: A dictionary indicating the network status.
        """
        time.sleep(0.05)
        return {"network_status": self.network_status, "status": "success"}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self._load_scenario(DEFAULT_COMMUNILINK_STATE)
        print("CommuniLinkApis: All dummy data reset to default state.")
        return {"reset_status": True}