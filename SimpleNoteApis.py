import datetime
import copy
import uuid
import random
from typing import Dict, List, Any, Optional, Union, Literal

_user_alias_to_uuid_map = {}

def generate_random_datetime_iso(days_ago_min=0, days_ago_max=365):
    """Generates a random ISO 8601 formatted datetime string (with Z for UTC) in the past."""
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
    folder_count = 0 # Placeholder for a potential future key for folders, if notes support them

    for old_note_id, note_content in processed_note_data.get("notes", {}).items():
        new_note_id = str(uuid.uuid4())
        note_content_copy = copy.deepcopy(note_content) # Ensure we don't modify original references

        note_content_copy["id"] = new_note_id
        note_content_copy["user"] = user_id # Ensure user_id is the UUID

        # Handle created_at and updated_at
        created_at_str = note_content_copy.get("created_at")
        updated_at_str = note_content_copy.get("updated_at")

        # Generate created_at if missing or empty
        if not created_at_str:
            created_at_str = generate_random_datetime_iso(days_ago_min=7, days_ago_max=365) # Last week to last year
            note_content_copy["created_at"] = created_at_str
        
        # Ensure created_at is a valid ISO format
        try:
            created_dt = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        except ValueError:
            created_at_str = generate_random_datetime_iso(days_ago_min=7, days_ago_max=365)
            created_dt = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            note_content_copy["created_at"] = created_at_str

        # Generate updated_at if missing or empty, ensuring it's after created_at
        if not updated_at_str:
            updated_dt = created_dt + datetime.timedelta(seconds=random.randint(60, 86400 * 30)) # 1 min to 30 days after creation
            note_content_copy["updated_at"] = updated_dt.isoformat(timespec='seconds').replace('+00:00', 'Z')
        else:
            try:
                updated_dt = datetime.datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                if updated_dt < created_dt: # Ensure updated_at is not before created_at
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
        "total_notes_count": len(new_notes), # New field
        "last_note_activity": (latest_note_activity or datetime.datetime.now(datetime.timezone.utc)).isoformat().replace('+00:00', 'Z') # New field, use now if no notes
    }

# --- Initial Users Data ---
users_initial_data = [
    ("jdoe", "John", "Doe", "john.doe@noted.com", {
        "notes": {
            0: { # This 0 will be replaced by a UUID by _create_user_data
                "id": 0,
                "title": "Onboarding Checklist for New Devs",
                "content": "1. Set up dev environment. 2. Clone repositories. 3. Attend morning stand-up. 4. Review coding standards.",
                "tags": ["work", "onboarding", "dev"],
                "pinned": True,
                "user": "jdoe", # Will be replaced by UUID
                "created_at": "", # Will be generated
                "updated_at": "", # Will be generated
                "color": "yellow", # New field for initial data
                "archived": False, # New field for initial data
                "priority": "high" # New field for initial data
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

# --- Generate 48 more diverse and realistic users ---
first_names = ["Sophia", "Liam", "Olivia", "Noah", "Ava", "Jackson", "Isabella", "Aiden", "Mia", "Lucas", "Harper", "Ethan", "Evelyn", "Mason", "Abigail", "Caleb", "Charlotte", "Logan", "Amelia", "Michael", "Ella", "Jacob", "Aria", "Daniel", "Chloe", "Samuel", "Grace", "David", "Victoria", "Joseph", "Penelope", "Matthew", "Riley", "Benjamin", "Layla", "Andrew", "Lily", "Gabriel", "Natalie", "Christopher", "Hannah", "James", "Zoe", "Ryan", "Scarlett", "Nathan", "Addison", "Christian", "Aubrey", "Joshua"]
last_names = ["Chen", "Kim", "Singh", "Lopez", "Garcia", "Nguyen", "Davis", "Jackson", "Harris", "White", "Moore", "Clark", "Lewis", "Baker", "Adams", "Hill", "Nelson", "Carter", "Mitchell", "Roberts", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders"]
email_domains = ["noted.com", "quickjot.net", "mindscribe.org", "simplenote.app", "ideahub.co"]
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

for i in range(48): # Generate 48 additional users
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{random.choice(email_domains)}"
    alias = f"{first.lower()}{last.lower()}{random.randint(10, 99)}"

    # Ensure unique alias and email
    while alias in _user_alias_to_uuid_map or email in [u["email"] for u in DEFAULT_STATE["users"].values()]:
        alias = f"{first.lower()}{last.lower()}{random.randint(10, 99)}"
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{random.choice(email_domains)}"

    new_note_data = {
        "notes": {}
    }

    num_notes = random.randint(5, 50)
    for n_idx in range(num_notes):
        note_id_temp = n_idx # Temporary ID, will be replaced by UUID
        
        note_title = random.choice(note_titles)
        note_content = random.choice(note_contents)
        
        # Generate random tags (1 to 4 tags)
        num_tags = random.randint(1, 4)
        tags = random.sample(common_tags, num_tags)
        
        pinned = random.random() < 0.15 # 15% chance to be pinned
        archived = random.random() < 0.10 # 10% chance to be archived
        
        created_at_dt = generate_random_datetime_iso(days_ago_min=7, days_ago_max=730) # Last week to 2 years ago
        # Ensure updated_at is after created_at
        created_dt_obj = datetime.datetime.fromisoformat(created_at_dt.replace('Z', '+00:00'))
        updated_at_dt_obj = created_dt_obj + datetime.timedelta(seconds=random.randint(60, 86400 * 60)) # 1 minute to 60 days after creation
        updated_at_str = updated_at_dt_obj.isoformat(timespec='seconds').replace('+00:00', 'Z')


        new_note_data["notes"][note_id_temp] = {
            "id": note_id_temp, # Will be replaced by UUID
            "title": f"{note_title} ({random.randint(1,99)})", # Add random number for uniqueness
            "content": note_content,
            "tags": tags,
            "pinned": pinned,
            "user": alias, # Will be replaced by UUID
            "created_at": created_at_dt,
            "updated_at": updated_at_str,
            "color": random.choice(note_colors), # New field
            "archived": archived, # New field
            "priority": random.choice(note_priorities), # New field
            "shared_with": [random.choice(current_user_aliases)] if random.random() < 0.05 and current_user_aliases else [], # 5% chance to be shared
            "reminders": [
                {"timestamp": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=random.randint(1, 30))).isoformat().replace('+00:00', 'Z'), "status": random.choice(["active", "completed"])}
            ] if random.random() < 0.2 else [] # 20% chance to have reminders
        }

    user_id, user_data = _create_user_data(alias, first, last, email, new_note_data)
    DEFAULT_STATE["users"][user_id] = user_data
    current_user_aliases.append(alias) # Add new user alias to potential shared_with list for subsequent users

# --- Output the generated DEFAULT_STATE ---
import json

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")

# Save the generated DEFAULT_STATE to a JSON file
# output_filename = 'diverse_simple_note_state.json'
# with open(output_filename, 'w') as f:
#     json.dump(DEFAULT_STATE, f, indent=2)

print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

# Optionally, print a sample user's data for review
# if DEFAULT_STATE["users"]:
#     sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(0, len(DEFAULT_STATE["users"]) - 1)]
#     print(f"\nSample data for user {DEFAULT_STATE['users'][sample_user_id]['first_name']} {DEFAULT_STATE['users'][sample_user_id]['last_name']}:")
#     print(json.dumps(DEFAULT_STATE["users"][sample_user_id], indent=2))

class SimpleNoteApis:
    """
    A dummy API class for simulating Simple Note operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the SimpleNoteApis instance, setting up the in-memory
        data stores and loading the default scenario.
        """
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the SimpleNote API, which provides core functionality for managing notes."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain a "users" key.
        """
        DEFAULT_STATE_COPY = copy.deepcopy(scenario)
        self.users = DEFAULT_STATE_COPY.get("users", {})
        print("SimpleNoteApis: Loaded scenario with users and their UUIDs.")

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for dummy entities (notes).
        """
        return str(uuid.uuid4())

    def _get_user_id_by_alias(self, alias: str) -> Optional[str]:
        """Helper to get user_id (UUID) from alias (simple string)."""
        for user_id, user_data in self.users.items():
            if user_data.get("alias") == alias:
                return user_id
        return None

    def _get_user_alias_by_id(self, user_id: str) -> Optional[str]:
        """Helper to get user alias (simple string) from user_id (UUID)."""
        user_data = self.users.get(user_id)
        return user_data.get("alias") if user_data else None

    def _get_user_note_data(self, user_alias: str) -> Optional[Dict]:
        """Helper to get a user's note data."""
        internal_user_id = self._get_user_id_by_alias(user_alias)
        if not internal_user_id:
            return None
        return self.users.get(internal_user_id, {}).get("note_data")

    def show_account(self, user: str) -> Dict[str, Union[bool, Dict]]:
        """
        Shows the account information for the current user.

        Args:
            user (str): The user identifier.

        Returns:
            Dict: A dictionary containing 'status' (bool) and 'profile_data' (Dict) if successful.
        """
        internal_user_id = self._get_user_id_by_alias(user)
        if not internal_user_id:
            return {"status": False, "profile_data": {}}

        user_data = self.users.get(internal_user_id)
        if user_data:
            profile = {
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "email": user_data["email"],
                "alias": user_data["alias"]
            }
            return {"status": True, "profile_data": profile}
        return {"status": False, "profile_data": {}}

    def list_notes(
        self, user: str, tag: Optional[str] = None, pinned: Optional[bool] = None
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Lists all notes for a specific user, with optional filtering by tag or pinned status.

        Args:
            user (str): The user identifier.
            tag (Optional[str]): If provided, only notes with this tag will be returned.
            pinned (Optional[bool]): If True, only pinned notes; if False, only unpinned notes.

        Returns:
            Dict: A dictionary containing 'status' (bool) and 'notes' (List[Dict]) if successful.
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False, "notes": []}

        notes = user_note_data.get("notes", {})
        filtered_notes = []

        for note_id, note_content in notes.items():
            if tag and tag not in note_content.get("tags", []):
                continue
            if pinned is not None and note_content.get("pinned") != pinned:
                continue
            filtered_notes.append(copy.deepcopy(note_content))

        return {"status": True, "notes": filtered_notes}

    def get_note(self, note_id: str, user: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves a single note by its ID for a specific user.

        Args:
            note_id (str): The ID of the note to retrieve.
            user (str): The user identifier.

        Returns:
            Dict: A dictionary containing 'status' (bool) and 'note' (Dict) if successful.
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False, "note": {}}

        notes = user_note_data.get("notes", {})
        note = notes.get(note_id)
        if note:
            return {"status": True, "note": copy.deepcopy(note)}
        return {"status": False, "note": {}}

    def create_note(
        self,
        user: str,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        pinned: bool = False,
    ) -> Dict[str, Union[bool, Dict]]:
        """
        Creates a new note for a specific user.

        Args:
            user (str): The user identifier.
            title (str): The title of the new note.
            content (str): The content of the new note.
            tags (Optional[List[str]]): A list of tags for the note.
            pinned (bool): Whether the note should be pinned.

        Returns:
            Dict: A dictionary containing 'status' (bool) and 'note' (Dict) if successful.
        """
        internal_user_id = self._get_user_id_by_alias(user)
        if not internal_user_id:
            return {"status": False, "message": "User not found."}

        user_note_data = self.users[internal_user_id].get("note_data")
        if user_note_data is None:
            user_note_data = {"notes": {}}
            self.users[internal_user_id]["note_data"] = user_note_data

        notes = user_note_data.get("notes")

        new_note_id = self._generate_unique_id()
        current_time_iso = datetime.datetime.now().isoformat() + "Z"

        new_note = {
            "id": new_note_id,
            "title": title,
            "content": content,
            "tags": tags if tags is not None else [],
            "pinned": pinned,
            "user": internal_user_id,
            "created_at": current_time_iso,
            "updated_at": current_time_iso,
        }
        notes[new_note_id] = new_note

        print(f"Note '{title}' created for {user} with ID: {new_note_id}")
        return {"status": True, "note": new_note}

    def update_note_content(
        self,
        note_id: str,
        user: str,
        new_content: str,
        new_title: Optional[str] = None,
        new_tags: Optional[List[str]] = None,
        new_pinned_status: Optional[bool] = None,
    ) -> Dict[str, bool]:
        """
        Updates the content, title, tags, or pinned status of an existing note.

        Args:
            note_id (str): ID of the note to update.
            user (str): The user identifier.
            new_content (str): The new content for the note.
            new_title (Optional[str]): The new title for the note.
            new_tags (Optional[List[str]]): The new list of tags for the note.
            new_pinned_status (Optional[bool]): The new pinned status for the note.

        Returns:
            Dict[str, bool]: A dictionary containing 'status' (bool) indicating success or failure.
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False}

        notes = user_note_data.get("notes", {})
        if note_id not in notes:
            return {"status": False}

        note = notes[note_id]
        note["content"] = new_content
        if new_title is not None:
            note["title"] = new_title
        if new_tags is not None:
            note["tags"] = new_tags
        if new_pinned_status is not None:
            note["pinned"] = new_pinned_status
        
        note["updated_at"] = datetime.datetime.now().isoformat() + "Z"

        return {"status": True}

    def append_or_prepend_note_content(
        self,
        note_id: str,
        user: str,
        added_content: str,
        append_or_prepend: Literal["append", "prepend"] = "append",
    ) -> Dict[str, bool]:
        """
        Appends or prepends content to an existing note.

        Args:
            note_id (str): ID of the note to modify.
            user (str): The user identifier.
            added_content (str): Content to add.
            append_or_prepend (Literal["append", "prepend"]): Whether to append or prepend.

        Returns:
            Dict[str, bool]: A dictionary containing 'status' (bool) indicating success or failure.
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False}

        notes = user_note_data.get("notes", {})
        if note_id not in notes:
            return {"status": False}

        note = notes[note_id]
        if append_or_prepend == "append":
            note["content"] += "\n" + added_content
        else:
            note["content"] = added_content + "\n" + note["content"]
        
        note["updated_at"] = datetime.datetime.now().isoformat() + "Z"

        return {"status": True}

    def delete_note(
        self,
        note_id: str,
        user: str,
    ) -> Dict[str, bool]:
        """
        Delete a note.

        Args:
            note_id (str): ID of the note to delete.
            user (str): The user identifier. Only notes belonging to this user can be deleted.

        Returns:
            Dict[str, bool]: A dictionary containing:
                             - "status" (bool): True if the note was deleted successfully,
                                                False if the note was not found or does not
                                                belong to the specified user.
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False}

        notes = user_note_data.get("notes", {})
        if note_id in notes:
            del notes[note_id]
            return {"status": True}
        return {"status": False}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self._load_scenario(DEFAULT_STATE)
        print("SimpleNoteApis: All dummy data reset to default state.")
        return {"reset_status": True}