import random
import uuid
from datetime import datetime, timedelta
import json
from fake_data import first_names, last_names, domains

current_datetime = datetime.now()

class CommuniLinkUser:
    def __init__(self, user_id: str, email: str = None):
        self.user_id = user_id
        self.email = email

DEFAULT_COMMUNILINK_STATE = {
    "users": {},
    "billing_history": [],
    "support_tickets": [],
    "service_plans": {
        "basic": {"price_per_sms": 0.05, "price_per_minute": 0.10, "description": "Basic communication plan: Affordable messaging and calling rates."},
        "premium": {"price_per_sms": 0.02, "price_per_minute": 0.05, "description": "Premium communication plan: Enjoy significantly lower rates on SMS and calls, plus priority support."},
        "unlimited": {"price_per_sms": 0.00, "price_per_minute": 0.00, "monthly_fee": 30.00, "description": "Unlimited plan: All SMS and calls are free within the network for a flat monthly fee."},
    },
    "active_plan": "basic",
    "network_status": "operational",
    "network_logs": [],
    "system_notifications": [],
}

_user_email_to_uuid_map = {}

def generate_random_past_date(max_days_ago=365):
    days_ago = random.randint(1, max_days_ago)
    return (current_datetime - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).isoformat()

def generate_phone_number():
    area_code = random.randint(200, 999)
    prefix = random.randint(100, 999)
    line_number = random.randint(1000, 9999)
    return f"+1{area_code}{prefix}{line_number}"

def generate_fake_email():
    randomName = f"{random.choice(first_names)} {random.choice(last_names)}"
    randomDomain = random.choice(domains)
    return f"{randomName.replace(' ', '.').lower()}@{randomDomain}"

def _create_user_data(email, first_name, last_name, phone_number, balance, contacts_emails, sms_history, call_history, settings, service_plan):
    user_id = str(uuid.uuid4())
    _user_email_to_uuid_map[email] = user_id
    contacts_ids = []
    for contact_email in contacts_emails:
        contacts_ids.append(_user_email_to_uuid_map.get(contact_email, contact_email))
    processed_sms_history = []
    for sms in sms_history:
        sms_entry = {**sms, "sms_id": str(uuid.uuid4())}
        if not sms.get("is_external"):
            sms_entry["sender_id"] = _user_email_to_uuid_map.get(sms.get("sender"), sms.get("sender"))
            sms_entry["receiver_id"] = _user_email_to_uuid_map.get(sms.get("receiver"), sms.get("receiver"))
        processed_sms_history.append(sms_entry)
    processed_call_history = []
    for call in call_history:
        call_entry = {**call, "call_id": str(uuid.uuid4())}
        if not call.get("is_external"):
            call_entry["caller_id"] = _user_email_to_uuid_map.get(call.get("caller"), call.get("caller"))
            call_entry["receiver_id"] = _user_email_to_uuid_map.get(call.get("receiver"), call.get("receiver"))
        processed_call_history.append(call_entry)
    password_hash = uuid.uuid4().hex + ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    return user_id, {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone_number": phone_number,
        "balance": balance,
        "sms_history": processed_sms_history,
        "call_history": processed_call_history,
        "settings": settings,
        "contacts": contacts_ids,
        "password_hash": password_hash,
        "service_plan": service_plan,
        "last_login": generate_random_past_date(30),
        "is_active": random.choice([True, True, False]),
    }

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

for email, first_name, last_name, phone_number, balance, contacts_emails, sms_hist, call_hist, settings, service_plan in users_initial_data:
    user_id, user_data = _create_user_data(email, first_name, last_name, phone_number, balance, contacts_emails, sms_hist, call_hist, settings, service_plan)
    DEFAULT_COMMUNILINK_STATE["users"][user_id] = user_data

current_user_emails = list(_user_email_to_uuid_map.keys())

for i in range(44):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}{random.randint(1,999)}@communi.link"
    while email in _user_email_to_uuid_map:
        email = f"{first.lower()}.{last.lower()}{random.randint(1,999)}@communi.link"
    phone = generate_phone_number()
    balance = round(random.uniform(5.00, 1000.00), 2)
    num_contacts = random.randint(0, 5)
    possible_contacts_emails = list(_user_email_to_uuid_map.keys())
    contacts_for_new_user = random.sample(possible_contacts_emails, min(num_contacts, len(possible_contacts_emails)))
    sms_history = []
    num_sms = random.randint(0, 5)
    for _ in range(num_sms):
        receiver_email = random.choice(current_user_emails + [generate_phone_number() + "@external.com"])
        sms_history.append({
            "sender": email,
            "receiver": receiver_email,
            "message": random.choice(["Hi there!", "Are you free later?", "Got it, thanks!", "See you soon!", "On my way."]),
            "timestamp": generate_random_past_date(90),
            "is_external": "@external.com" in receiver_email or "+" in receiver_email
        })
        if "@communi.link" in receiver_email:
             sms_history.append({
                "sender": receiver_email,
                "receiver": email,
                "message": random.choice(["Hey!", "Yep!", "Sounds good!", "Awesome!"]),
                "timestamp": generate_random_past_date(89),
                "is_external": False
            })
    call_history = []
    num_calls = random.randint(0, 3)
    for _ in range(num_calls):
        call_type = random.choice(["outgoing", "incoming"])
        duration = random.randint(1, 30)
        external_call = random.random() < 0.3
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
        "call_forwarding_number": generate_phone_number() if random.random() < 0.2 else ""
    }
    service_plan = random.choice(list(DEFAULT_COMMUNILINK_STATE["service_plans"].keys()))
    user_id, user_data = _create_user_data(email, first, last, phone, balance, contacts_for_new_user, sms_history, call_history, settings, service_plan)
    DEFAULT_COMMUNILINK_STATE["users"][user_id] = user_data
    current_user_emails.append(email)

all_user_uuids = list(_user_email_to_uuid_map.values())
for user_id, user_data in DEFAULT_COMMUNILINK_STATE["users"].items():
    resolved_contacts = []
    for contact_item in user_data["contacts"]:
        if contact_item in _user_email_to_uuid_map:
            resolved_contacts.append(_user_email_to_uuid_map[contact_item])
        elif contact_item in all_user_uuids:
            resolved_contacts.append(contact_item)
    user_data["contacts"] = list(set([f for f in resolved_contacts if f != user_id]))

all_user_ids = list(DEFAULT_COMMUNILINK_STATE["users"].keys())
billing_types = ["plan_charge", "sms_charge", "call_charge", "top_up"]
descriptions = {
    "plan_charge": ["Monthly {plan} plan charge", "Subscription renewal for {plan} plan"],
    "sms_charge": ["SMS charge for {count} messages", "Messaging fees for recent activity"],
    "call_charge": ["Call charge for {minutes} minutes", "Voice call charges"],
    "top_up": ["Account top-up via credit card", "Credit added to balance", "Payment received"]
}

for _ in range(70):
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
    else:
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

for _ in range(25):
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

network_log_messages = [
    "API endpoint /user/profile accessed by user {user_id}",
    "SMS sent from {sender_id} to {receiver_id}",
    "Call initiated by {caller_id}",
    "Database backup completed successfully",
    "System load: {load_percentage}%",
    "New user registered: {user_id}",
    "Payment processed for transaction {transaction_id}"
]

for _ in range(100):
    log_time = generate_random_past_date(10)
    log_message = random.choice(network_log_messages)
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

for _ in range(5):
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
        "is_read": random.choice([True, False, False])
    })

print(f"Total number of users generated: {len(DEFAULT_COMMUNILINK_STATE['users'])}")
print(f"Total billing history records: {len(DEFAULT_COMMUNILINK_STATE['billing_history'])}")
print(f"Total support tickets: {len(DEFAULT_COMMUNILINK_STATE['support_tickets'])}")
print(f"Total network logs: {len(DEFAULT_COMMUNILINK_STATE['network_logs'])}")
print(f"Total system notifications: {len(DEFAULT_COMMUNILINK_STATE['system_notifications'])}")

with open('diverse_communi_link_state.json', 'w') as f:
    json.dump(DEFAULT_COMMUNILINK_STATE, f, indent=2)
