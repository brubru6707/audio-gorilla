import datetime
import copy
import uuid
import random
import json
from typing import Dict, Any
from fake_data import note_title_and_content, first_names, last_names, domains

_user_alias_to_uuid_map = {}

def generate_random_datetime_iso(days_ago_min=0, days_ago_max=365):
    delta_days = random.randint(days_ago_min, days_ago_max)
    time_offset = datetime.timedelta(
        days=delta_days,
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    dt = datetime.datetime.now(datetime.timezone.utc) - time_offset
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

common_tags = [
    {
        "tag": "work",
        "words": ["work", "job", "career", "office", "business", "company", "employee", "boss", "colleague", "presentation", "report", "professional", "desk", "email", "tasks"]
    },
    {
        "tag": "personal",
        "words": ["personal", "private", "family", "mom", "dad", "friend", "thoughts", "feelings", "life", "self", "mind", "soul", "journal", "diary", "hobbies", "recreation"]
    },
    {
        "tag": "project",
        "words": ["project", "task", "assignment", "report", "deadline", "milestone", "team", "client", "phase", "development", "plan", "update", "notes", "progress", "completion"]
    },
    {
        "tag": "ideas",
        "words": ["idea", "ideas", "brainstorm", "concept", "thought", "creative", "inspiration", "innovation", "design", "plan", "strategy", "app", "solution", "proposal", "invention"]
    },
    {
        "tag": "urgent",
        "words": ["urgent", "important", "critical", "immediate", "emergency", "now", "priority", "crucial", "essential", "must", "needed", "fast", "asap", "due"]
    },
    {
        "tag": "todo",
        "words": ["todo", "to-do", "list", "tasks", "errands", "chores", "schedule", "plan", "checklist", "agenda", "daily", "weekly", "monthly", "routine", "remember", "don't forget"]
    },
    {
        "tag": "finance",
        "words": ["finance", "financial", "budget", "money", "invest", "save", "expense", "income", "bill", "debt", "loan", "bank", "credit", "tax", "fund", "economy"]
    },
    {
        "tag": "health",
        "words": ["health", "healthy", "exercise", "workout", "fitness", "diet", "doctor", "dentist", "appointment", "medicine", "symptoms", "illness", "nutrition", "wellness", "mental", "physical"]
    },
    {
        "tag": "travel",
        "words": ["travel", "trip", "vacation", "journey", "flight", "hotel", "destination", "packing", "itinerary", "explore", "adventure", "tour", "hike", "roadtrip", "abroad", "getaway"]
    },
    {
        "tag": "recipes",
        "words": ["recipe", "recipes", "cook", "cooking", "bake", "ingredients", "food", "meal", "dinner", "lunch", "breakfast", "dish", "cuisine", "kitchen", "prep", "bake", "delicious"]
    },
    {
        "tag": "meeting",
        "words": ["meeting", "agenda", "discussion", "notes", "summary", "minutes", "conference", "call", "schedule", "team", "client", "attendees", "topic", "review", "presentation"]
    },
    {
        "tag": "dev",
        "words": ["dev", "development", "code", "programming", "software", "bug", "release", "test", "feature", "framework", "api", "database", "git", "repo", "script", "app"]
    },
    {
        "tag": "marketing",
        "words": ["marketing", "campaign", "ads", "social media", "promotion", "brand", "market", "strategy", "audience", "content", "analytics", "seo", "sales", "business", "pr"]
    },
    {
        "tag": "learning",
        "words": ["learning", "study", "class", "lecture", "school", "course", "notes", "homework", "education", "topic", "subject", "research", "knowledge", "skill", "understand", "read", "book"]
    },
    {
        "tag": "home",
        "words": ["home", "house", "apartment", "maintenance", "chores", "cleaning", "decor", "living", "kitchen", "room", "garden", "rent", "mortgage", "appliances", "utilities", "bills"]
    }
]
note_colors = ["yellow", "blue", "green", "pink", "white", "purple"]
note_priorities = ["low", "medium", "high"]

def get_note_tags(note):
    all_note_words = set((note['title'] + " " + note['content']).lower().split())
    relevant_tags = []
    
    for tag_map in common_tags:
        if any(keyword in all_note_words for keyword in tag_map['words']):
            relevant_tags.append(tag_map['tag'])
    
    return " | ".join(relevant_tags) if relevant_tags else "untagged"

def _create_user_data(alias: str, first_name: str, last_name: str, email: str, note_data: Dict[str, Any]):
    user_id = str(uuid.uuid4())
    _user_alias_to_uuid_map[alias] = user_id

    processed_note_data = copy.deepcopy(note_data)
    new_notes = {}
    latest_note_activity = None

    for _, note_content in processed_note_data.get("notes", {}).items():
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

DEFAULT_STATE: Dict[str, Any] = {
    "users": {},
}

note_titles = [note['title'] for note in note_title_and_content]
note_contents = [note['content'] for note in note_title_and_content]

current_user_aliases = list(_user_alias_to_uuid_map.keys())

notes = note_title_and_content

for i in range(48):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{random.choice(domains)}"
    alias = f"{first.lower()}{last.lower()}{random.randint(10, 99)}"

    while alias in _user_alias_to_uuid_map or email in [u["email"] for u in DEFAULT_STATE["users"].values()]:
        alias = f"{first.lower()}{last.lower()}{random.randint(10, 99)}"
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{random.choice(domains)}"

    new_note_data = {
        "notes": {}
    }

    num_notes = random.randint(5, 50)
    for n_idx in range(num_notes):
        note_id_temp = n_idx
        
        note_data_from_list = random.choice(notes)
        note_title = note_data_from_list['title']
        note_content = note_data_from_list['content']
        
        tags = get_note_tags(note_data_from_list)

        pinned = random.random() < 0.15
        archived = random.random() < 0.10
        
        created_at_dt = generate_random_datetime_iso(days_ago_min=7, days_ago_max=730)
        created_dt_obj = datetime.datetime.fromisoformat(created_at_dt.replace('Z', '+00:00'))
        updated_at_dt_obj = created_dt_obj + datetime.timedelta(seconds=random.randint(60, 86400 * 60))
        updated_at_str = updated_at_dt_obj.isoformat(timespec='seconds').replace('+00:00', 'Z')

        new_note_data["notes"][note_id_temp] = {
            "id": note_id_temp,
            "title": f"{note_title}",
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

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")

output_filename = 'diverse_simple_notes_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Generated DEFAULT_STATE saved to '{output_filename}'")