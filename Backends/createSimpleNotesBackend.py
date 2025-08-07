import datetime
import copy
import uuid
import random
import json
from typing import Dict, Any

_user_alias_to_uuid_map = {}

def generate_random_datetime_iso(days_ago_min=0, days_ago_max=365):
    delta_days = random.randint(days_ago_min, days_ago_max)
    time_offset = datetime.timedelta(days=delta_days, 
                                     hours=random.randint(0, 23), 
                                     minutes=random.randint(0, 59), 
                                     seconds=random.randint(0, 59))
    dt = datetime.datetime.now(datetime.timezone.utc) - time_offset
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

def _create_user_data(alias: str, first_name: str, last_name: str, email: str, note_data: Dict[str, Any]):
    user_id = str(uuid.uuid4())
    _user_alias_to_uuid_map[alias] = user_id

    processed_note_data = copy.deepcopy(note_data)
    new_notes = {}
    
    latest_note_activity = None
    folder_count = 0

    for old_note_id, note_content in processed_note_data.get("notes", {}).items():
        new_note_id = str(uuid.uuid4())
        note_content_copy = copy.deepcopy(note_content)

        note_content_copy["id"] = new_note_id
        note_content_copy["user"] = user_id

        created_at_str = note_content_copy.get("created_at")
        updated_at_str = note_content_copy.get("updated_at")

        if not created_at_str:
            created_at_str = generate_random_datetime_iso(days_ago_min=7, days_ago_max=365)
            note_content_copy["created_at"] = created_at_str
        
        try:
            created_dt = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        except ValueError:
            created_at_str = generate_random_datetime_iso(days_ago_min=7, days_ago_max=365)
            created_dt = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            note_content_copy["created_at"] = created_at_str

        if not updated_at_str:
            updated_dt = created_dt + datetime.timedelta(seconds=random.randint(60, 86400 * 30))
            note_content_copy["updated_at"] = updated_dt.isoformat(timespec='seconds').replace('+00:00', 'Z')
        else:
            try:
                updated_dt = datetime.datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                if updated_dt < created_dt:
                    updated_dt = created_dt + datetime.timedelta(seconds=random.randint(60, 86400 * 30))
                    note_content_copy["updated_at"] = updated_dt.isoformat(timespec='seconds').replace('+00:00', 'Z')
            except ValueError:
                updated_dt = created_dt + datetime.timedelta(seconds=random.randint(60, 86400 * 30))
                note_content_copy["updated_at"] = updated_dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

        if latest_note_activity is None or updated_dt > latest_note_activity:
            latest_note_activity = updated_dt

        new_notes[new_note_id] = note_content_copy
    
    processed_note_data["notes"] = new_notes

    return user_id, {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "alias": alias,
        "note_data": processed_note_data,
        "total_notes_count": len(new_notes),
        "last_note_activity": (latest_note_activity or datetime.datetime.now(datetime.timezone.utc)).isoformat().replace('+00:00', 'Z')
    }

users_initial_data = [
    ("jdoe", "John", "Doe", "john.doe@noted.com", {
        "notes": {
            0: {
                "id": 0,
                "title": "Onboarding Checklist for New Devs",
                "content": "1. Set up dev environment. 2. Clone repositories. 3. Attend morning stand-up. 4. Review coding standards.",
                "tags": ["work", "onboarding", "dev"],
                "pinned": True,
                "user": "jdoe",
                "created_at": "",
                "updated_at": "",
                "color": "yellow",
                "archived": False,
                "priority": "high"
            },
            1: {
                "id": 1,
                "title": "Weekend Hike Gear List",
                "content": "Backpack, water bottles, trail mix, first-aid kit, comfortable boots, rain jacket.",
                "tags": ["personal", "hiking", "weekend"],
                "pinned": False,
                "user": "jdoe",
                "created_at": "",
                "updated_at": ""
            },
            2: {
                "id": 2,
                "title": "Q3 Marketing Campaign Brainstorm",
                "content": "Focus on social media engagement. Explore TikTok ads. Partner with influencers in niche markets.",
                "tags": ["work", "marketing", "ideas"],
                "pinned": False,
                "user": "jdoe",
                "created_at": "",
                "updated_at": ""
            }
        }
    }),
    ("msmith", "Maria", "Smith", "maria.smith@noted.com", {
        "notes": {
            3: {
                "id": 3,
                "title": "Grocery List",
                "content": "Milk, Eggs, Bread, Butter, Cheese, Apples, Bananas.",
                "tags": ["personal", "shopping"],
                "pinned": True,
                "user": "msmith",
                "created_at": "",
                "updated_at": "",
                "color": "blue",
                "archived": False,
                "priority": "medium"
            }
        }
    })
]

DEFAULT_STATE: Dict[str, Any] = {
    "users": {},
}

for alias, first_name, last_name, email, note_data in users_initial_data:
    user_id, user_data = _create_user_data(alias, first_name, last_name, email, note_data)
    DEFAULT_STATE["users"][user_id] = user_data

first_names = ["Sophia", "Liam", "Olivia", "Noah", "Ava", "Jackson", "Isabella", "Aiden", "Mia", "Lucas", "Harper", "Ethan", "Evelyn", "Mason", "Abigail", "Caleb", "Charlotte", "Logan", "Amelia", "Michael", "Ella", "Jacob", "Aria", "Daniel", "Chloe", "Samuel", "Grace", "David", "Victoria", "Joseph", "Penelope", "Matthew", "Riley", "Benjamin", "Layla", "Andrew", "Lily", "Gabriel", "Natalie", "Christopher", "Hannah", "James", "Zoe", "Ryan", "Scarlett", "Nathan", "Addison", "Christian", "Aubrey", "Joshua"]
last_names = ["Chen", "Kim", "Singh", "Lopez", "Garcia", "Nguyen", "Davis", "Jackson", "Harris", "White", "Moore", "Clark", "Lewis", "Baker", "Adams", "Hill", "Nelson", "Carter", "Mitchell", "Roberts", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders"]
email_domains = ["noted.com", "quickjot.net", "mindscribe.org", "simplenotes.app", "ideahub.co"]
note_titles = [
    "Meeting Recap", "Project X Updates", "To-Do List", "Daily Journal Entry",
    "Recipe Ideas", "Book Recommendations", "Travel Plans", "Shopping List",
    "Client Feedback", "Bug Report", "Feature Request", "Learning Notes",
    "Fitness Goals", "Home Renovation Ideas", "Financial Reminders"
]
note_contents = [
    "Discussed Q3 strategy, action items include: finalize budget, assign roles, schedule next sync.",
    "User authentication flow revised. Need to implement OAuth2 for secure login. Test edge cases.",
    "Buy milk, eggs, bread. Call dry cleaning. Schedule dentist appointment for next month.",
    "Reflecting on today's challenges. Faced a difficult coding problem but eventually solved it. Feeling accomplished.",
    "Ingredients for pasta primavera: zucchini, bell peppers, cherry tomatoes, basil, pasta, olive oil, garlic.",
    "Recommended reading: 'Clean Code' by Robert C. Martin, 'The Pragmatic Programmer' by Andrew Hunt and David Thomas.",
    "Trip to Japan: research flights to Tokyo, book ryokan in Kyoto, explore Hakone day trip options.",
    "Task list for tomorrow: finish report, reply to Sarah, prepare for client demo, review pull request #123.",
    "CSS styling issue on mobile. Elements overlapping. Consider using flexbox or grid for better responsiveness.",
    "Learning Python generators. They allow lazy evaluation, saving memory for large datasets. 'yield' keyword is key.",
    "Garden update: tomatoes are thriving, basil needs pruning, planted new batch of lettuce.",
    "Dream interpretation: flying suggests freedom and ambition. Falling indicates loss of control.",
    "Morning routine: wake up, meditate for 10 min, light stretching, healthy breakfast.",
    "New marketing campaign: focus on visual content. Short video ads for social media platforms.",
    "Remember to renew passport by end of year. Check expiry date and required documents."
]
common_tags = ["work", "personal", "project", "ideas", "urgent", "todo", "finance", "health", "travel", "recipes", "meeting", "dev", "marketing", "learning", "home"]
note_colors = ["yellow", "blue", "green", "pink", "white", "purple"]
note_priorities = ["low", "medium", "high"]

current_user_aliases = list(_user_alias_to_uuid_map.keys())

for i in range(48):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{random.choice(email_domains)}"
    alias = f"{first.lower()}{last.lower()}{random.randint(10, 99)}"

    while alias in _user_alias_to_uuid_map or email in [u["email"] for u in DEFAULT_STATE["users"].values()]:
        alias = f"{first.lower()}{last.lower()}{random.randint(10, 99)}"
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{random.choice(email_domains)}"

    new_note_data = {
        "notes": {}
    }

    num_notes = random.randint(5, 50)
    for n_idx in range(num_notes):
        note_id_temp = n_idx
        
        note_title = random.choice(note_titles)
        note_content = random.choice(note_contents)
        
        num_tags = random.randint(1, 4)
        tags = random.sample(common_tags, num_tags)
        
        pinned = random.random() < 0.15
        archived = random.random() < 0.10
        
        created_at_dt = generate_random_datetime_iso(days_ago_min=7, days_ago_max=730)
        created_dt_obj = datetime.datetime.fromisoformat(created_at_dt.replace('Z', '+00:00'))
        updated_at_dt_obj = created_dt_obj + datetime.timedelta(seconds=random.randint(60, 86400 * 60))
        updated_at_str = updated_at_dt_obj.isoformat(timespec='seconds').replace('+00:00', 'Z')

        new_note_data["notes"][note_id_temp] = {
            "id": note_id_temp,
            "title": f"{note_title} ({random.randint(1,99)})",
            "content": note_content,
            "tags": tags,
            "pinned": pinned,
            "user": alias,
            "created_at": created_at_dt,
            "updated_at": updated_at_str,
            "color": random.choice(note_colors),
            "archived": archived,
            "priority": random.choice(note_priorities),
            "shared_with": [random.choice(current_user_aliases)] if random.random() < 0.05 and current_user_aliases else [],
            "reminders": [
                {"timestamp": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=random.randint(1, 30))).isoformat().replace('+00:00', 'Z'), "status": random.choice(["active", "completed"])}
            ] if random.random() < 0.2 else []
        }

    user_id, user_data = _create_user_data(alias, first, last, email, new_note_data)
    DEFAULT_STATE["users"][user_id] = user_data
    current_user_aliases.append(alias)

import json

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")

output_filename = 'diverse_simple_notes_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

if DEFAULT_STATE["users"]:
    sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(0, len(DEFAULT_STATE["users"]) - 1)]
    print(f"\nSample data for user {DEFAULT_STATE['users'][sample_user_id]['first_name']} {DEFAULT_STATE['users'][sample_user_id]['last_name']}:")
    print(json.dumps(DEFAULT_STATE["users"][sample_user_id], indent=2))