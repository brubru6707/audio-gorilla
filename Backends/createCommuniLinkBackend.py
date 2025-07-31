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
