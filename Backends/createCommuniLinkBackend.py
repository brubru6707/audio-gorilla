import random
import uuid
from datetime import datetime, timedelta
import json
from fake_data import first_names, last_names, domains, communilink_conversations, first_and_last_names, user_count

# --- Constants and Initial State ---

# Set the timestamp at the beginning for consistency across the script.
CURRENT_DATETIME = datetime.now()

DEFAULT_COMMUNILINK_STATE = {
    "users": {},
    "billing_history": [],
    "support_tickets": [],
    "service_plans": {
        "basic": {"price_per_sms": 0.05, "price_per_minute": 0.10, "description": "Basic communication plan: Affordable messaging and calling rates."},
        "premium": {"price_per_sms": 0.02, "price_per_minute": 0.05, "description": "Premium communication plan: Enjoy lower rates and priority support."},
        "unlimited": {"price_per_sms": 0.00, "price_per_minute": 0.00, "monthly_fee": 30.00, "description": "Unlimited plan: Free SMS and calls for a flat monthly fee."},
    },
    "active_plan": "basic",
    "network_status": "operational",
    "network_logs": [],
    "system_notifications": [],
}

# --- Helper Functions ---

def generate_random_past_date(max_days_ago=365):
    """Generates a random ISO formatted datetime string in the past."""
    days_ago = random.randint(1, max_days_ago)
    random_past_time = CURRENT_DATETIME - timedelta(
        days=days_ago, 
        hours=random.randint(0, 23), 
        minutes=random.randint(0, 59)
    )
    return random_past_time.isoformat()

def generate_phone_number():
    """Generates a random US-style phone number."""
    return f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"

def generate_fake_email(first, last):
    """Generates a plausible fake email from a first and last name."""
    random_domain = random.choice(domains)
    return f"{first.replace(' ', '.').lower()}.{last.replace(' ', '.').lower()}@{random_domain}"

# --- Main Data Generation Logic ---

def main():
    """Main function to generate the entire dataset."""
    
    # =========================================================================
    # PASS 1: Create user shells with unique emails and basic info.
    # This allows us to create relationships in Pass 2 from a complete user list.
    # =========================================================================
    print("PASS 1: Creating user shells...")
    user_shells = []
    email_to_uuid_map = {}
    existing_emails = set()

    # Create a list of all names to generate, combining specific and random users
    names_to_generate = [(name.partition(" ")[0], name.partition(" ")[2]) for name in first_and_last_names]
    names_to_generate.extend([(None, None)] * user_count)

    for first_name_spec, last_name_spec in names_to_generate:
        first_name = first_name_spec or random.choice(first_names)
        last_name = last_name_spec or random.choice(last_names)
        
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"
        while email in existing_emails:
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}@{random.choice(domains)}"
        
        existing_emails.add(email)
        user_id = str(uuid.uuid4())
        email_to_uuid_map[email] = user_id
        
        user_shells.append({
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": generate_phone_number()
        })
    
    all_user_ids = list(email_to_uuid_map.values())
    all_user_emails = list(email_to_uuid_map.keys())

    # =========================================================================
    # PASS 2: Populate detailed information for each user.
    # Now we can create realistic contacts, SMS, and call histories.
    # =========================================================================
    print("PASS 2: Populating user details and relationships...")
    for shell in user_shells:
        user_id = shell["user_id"]
        
        # --- Generate Contacts ---
        num_contacts = random.randint(2, 15)
        # Ensure user is not in their own contact list
        other_user_ids = [uid for uid in all_user_ids if uid != user_id]
        contacts = random.sample(other_user_ids, min(num_contacts, len(other_user_ids)))

        # --- Generate SMS History ---
        sms_history = []
        for _ in range(random.randint(0, 5)):
            convo_key = random.choice(list(communilink_conversations.keys()))
            # The other participant can be an existing user or an external number
            other_party_email = random.choice(all_user_emails) if random.random() > 0.2 else generate_fake_email("external", "contact")
            
            for user_alias, message in communilink_conversations[convo_key]:
                sender_email = shell["email"] if user_alias == "user_1" else other_party_email
                receiver_email = other_party_email if user_alias == "user_1" else shell["email"]
                sms_history.append({
                    "sms_id": str(uuid.uuid4()),
                    "sender_id": email_to_uuid_map.get(sender_email),
                    "receiver_id": email_to_uuid_map.get(receiver_email),
                    "sender": sender_email,
                    "receiver": receiver_email,
                    "message": message,
                    "timestamp": generate_random_past_date(90),
                    "is_external": email_to_uuid_map.get(other_party_email) is None
                })

        # --- Generate Call History ---
        call_history = []
        for _ in range(random.randint(0, 8)):
            is_external = random.random() < 0.3
            call_type = random.choice(["outgoing", "incoming"])
            
            if is_external:
                other_party = generate_phone_number()
                caller = shell["email"] if call_type == "outgoing" else other_party
                receiver = other_party if call_type == "outgoing" else shell["email"]
            else:
                other_party_email = random.choice([e for e in all_user_emails if e != shell["email"]])
                caller = shell["email"] if call_type == "outgoing" else other_party_email
                receiver = other_party_email if call_type == "outgoing" else shell["email"]
            
            call_history.append({
                "call_id": str(uuid.uuid4()),
                "caller_id": email_to_uuid_map.get(caller),
                "receiver_id": email_to_uuid_map.get(receiver),
                "caller": caller,
                "receiver": receiver,
                "duration_minutes": random.randint(1, 30),
                "timestamp": generate_random_past_date(90),
                "type": call_type,
                "is_external": is_external
            })
            
        # --- Assemble Final User Object ---
        DEFAULT_COMMUNILINK_STATE["users"][user_id] = {
            **shell,
            "balance": round(random.uniform(5.00, 1000.00), 2),
            "sms_history": sms_history,
            "call_history": call_history,
            "contacts": contacts,
            "service_plan": random.choice(list(DEFAULT_COMMUNILINK_STATE["service_plans"].keys())),
            "password_hash": uuid.uuid4().hex + ''.join(random.choices('abcdef0123456789', k=16)),
            "settings": {
                "sms_notifications": random.choice([True, False]),
                "call_forwarding_enabled": random.choice([True, False]),
                "call_forwarding_number": generate_phone_number() if random.random() < 0.2 else ""
            },
            "last_login": generate_random_past_date(30),
            "is_active": random.choice([True, True, False]),
        }

    # =========================================================================
    # PASS 3: Generate related top-level data (billing, tickets, logs).
    # =========================================================================
    print("PASS 3: Generating billing, tickets, and logs...")
    if not all_user_ids:
        print("No users generated, skipping billing, tickets, and logs.")
        return

    # --- Generate Billing History ---
    billing_types = ["plan_charge", "sms_charge", "call_charge", "top_up"]
    for _ in range(70):
        user_id = random.choice(all_user_ids)
        user = DEFAULT_COMMUNILINK_STATE["users"][user_id]
        plan = user["service_plan"]
        trans_type = random.choice(billing_types)
        amount = 0.0
        desc = ""
        
        if trans_type == "plan_charge":
            fee = DEFAULT_COMMUNILINK_STATE["service_plans"][plan].get("monthly_fee", 0)
            if fee > 0:
                amount, desc = -fee, f"Monthly {plan.capitalize()} plan charge"
        elif trans_type == "sms_charge":
            count = random.randint(1, 50)
            amount = -round(count * DEFAULT_COMMUNILINK_STATE["service_plans"][plan]["price_per_sms"], 2)
            desc = f"SMS charge for {count} messages"
        elif trans_type == "call_charge":
            minutes = random.randint(1, 120)
            amount = -round(minutes * DEFAULT_COMMUNILINK_STATE["service_plans"][plan]["price_per_minute"], 2)
            desc = f"Call charge for {minutes} minutes"
        else: # top_up
            amount = round(random.uniform(10.00, 100.00), 2)
            desc = "Account top-up via credit card"

        if amount != 0:
            DEFAULT_COMMUNILINK_STATE["billing_history"].append({
                "transaction_id": str(uuid.uuid4()), "user_id": user_id, "type": trans_type,
                "amount": amount, "date": generate_random_past_date(180), "description": desc
            })

    # --- Generate Support Tickets ---
    ticket_subjects = ["Connectivity Issue", "Billing Discrepancy", "Feature Request", "Bug Report", "Call Quality"]
    for _ in range(25):
        created_at = datetime.fromisoformat(generate_random_past_date(90))
        status = random.choice(["open", "pending", "closed"])
        DEFAULT_COMMUNILINK_STATE["support_tickets"].append({
            "ticket_id": str(uuid.uuid4()), "user_id": random.choice(all_user_ids),
            "subject": random.choice(ticket_subjects), "status": status,
            "description": "User is reporting an issue regarding their service.",
            "created_at": created_at.isoformat(),
            "resolved_at": (created_at + timedelta(days=random.randint(1, 10))).isoformat() if status == "closed" else None,
        })

    # --- Generate Network Logs ---
    for _ in range(100):
        DEFAULT_COMMUNILINK_STATE["network_logs"].append({
            "timestamp": generate_random_past_date(10),
            "level": random.choice(["INFO", "INFO", "INFO", "WARNING", "ERROR"]),
            "message": f"API endpoint call by user {random.choice(all_user_ids)}"
        })
        
    # --- Generate System Notifications ---
    for _ in range(5):
        future_date = (CURRENT_DATETIME + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        DEFAULT_COMMUNILINK_STATE["system_notifications"].append({
            "notification_id": str(uuid.uuid4()), "timestamp": generate_random_past_date(7),
            "message": f"Scheduled maintenance will occur on {future_date} from 02:00 to 04:00 EDT.",
            "is_read": random.choice([True, False, False])
        })


if __name__ == "__main__":
    main()
    
    # --- Final Output and File Write ---
    print("-" * 50)
    print(f"Total number of users generated: {len(DEFAULT_COMMUNILINK_STATE['users'])}")
    print(f"Total billing history records: {len(DEFAULT_COMMUNILINK_STATE['billing_history'])}")
    print(f"Total support tickets: {len(DEFAULT_COMMUNILINK_STATE['support_tickets'])}")
    print(f"Total network logs: {len(DEFAULT_COMMUNILINK_STATE['network_logs'])}")
    print(f"Total system notifications: {len(DEFAULT_COMMUNILINK_STATE['system_notifications'])}")
    print("-" * 50)

    try:
        with open('diverse_communi_link_state.json', 'w') as f:
            json.dump(DEFAULT_COMMUNILINK_STATE, f, indent=2)
        print("Successfully saved data to diverse_communi_link_state.json")
    except IOError as e:
        print(f"Error saving file: {e}")