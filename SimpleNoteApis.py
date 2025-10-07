import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional, Union, Literal
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("SimpleNoteApis")
# If the file doesn't exist with snake_case, try the actual filename
if not DEFAULT_STATE:
    import json
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, 'Backends', 'diverse_simple_notes_state.json')
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            DEFAULT_STATE = json.load(f)
        print(f"Successfully loaded Simple Notes state from: {json_file_path}")
    except:
        DEFAULT_STATE = {}

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
        self, 
        user: str, 
        tag: Optional[str] = None, 
        pinned: Optional[bool] = None,
        color: Optional[str] = None,
        archived: Optional[bool] = None,
        priority: Optional[str] = None,
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Lists all notes for a specific user, with optional filtering by tag, pinned status, color, archived status, or priority.

        Args:
            user (str): The user identifier.
            tag (Optional[str]): If provided, only notes with this tag will be returned.
            pinned (Optional[bool]): If True, only pinned notes; if False, only unpinned notes.
            color (Optional[str]): If provided, only notes with this color will be returned.
            archived (Optional[bool]): If True, only archived notes; if False, only unarchived notes.
            priority (Optional[str]): If provided, only notes with this priority will be returned.

        Returns:
            Dict: A dictionary containing 'status' (bool) and 'notes' (List[Dict]) if successful.
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False, "notes": []}

        notes = user_note_data.get("notes", {})
        filtered_notes = []

        for note_id, note_content in notes.items():
            # Tag filtering
            if tag:
                note_tags = note_content.get("tags", [])
                if isinstance(note_tags, str):
                    note_tags = note_tags.split(" | ")
                if tag not in note_tags:
                    continue
            
            # Pinned filtering
            if pinned is not None and note_content.get("pinned") != pinned:
                continue
            
            # Color filtering
            if color and note_content.get("color") != color:
                continue
            
            # Archived filtering
            if archived is not None and note_content.get("archived") != archived:
                continue
            
            # Priority filtering
            if priority and note_content.get("priority") != priority:
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
        color: str = "yellow",
        archived: bool = False,
        priority: str = "medium",
    ) -> Dict[str, Union[bool, Dict]]:
        """
        Creates a new note for a specific user.

        Args:
            user (str): The user identifier.
            title (str): The title of the new note.
            content (str): The content of the new note.
            tags (Optional[List[str]]): A list of tags for the note.
            pinned (bool): Whether the note should be pinned.
            color (str): The color of the note (yellow, blue, green, pink, white, purple).
            archived (bool): Whether the note should be archived.
            priority (str): The priority of the note (low, medium, high).

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
            "color": color,
            "archived": archived,
            "priority": priority,
            "shared_with": [],
            "reminders": [],
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
        new_color: Optional[str] = None,
        new_archived_status: Optional[bool] = None,
        new_priority: Optional[str] = None,
    ) -> Dict[str, bool]:
        """
        Updates the content, title, tags, pinned status, color, archived status, or priority of an existing note.

        Args:
            note_id (str): ID of the note to update.
            user (str): The user identifier.
            new_content (str): The new content for the note.
            new_title (Optional[str]): The new title for the note.
            new_tags (Optional[List[str]]): The new list of tags for the note.
            new_pinned_status (Optional[bool]): The new pinned status for the note.
            new_color (Optional[str]): The new color for the note.
            new_archived_status (Optional[bool]): The new archived status for the note.
            new_priority (Optional[str]): The new priority for the note.

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
        if new_color is not None:
            note["color"] = new_color
        if new_archived_status is not None:
            note["archived"] = new_archived_status
        if new_priority is not None:
            note["priority"] = new_priority
        
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

    def share_note(
        self,
        note_id: str,
        user: str,
        share_with_alias: str,
    ) -> Dict[str, bool]:
        """
        Share a note with another user by alias.

        Args:
            note_id (str): ID of the note to share.
            user (str): The user identifier (note owner).
            share_with_alias (str): The alias of the user to share with.

        Returns:
            Dict[str, bool]: A dictionary containing 'status' (bool) indicating success or failure.
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False}

        # Check if the target user exists
        target_user_id = self._get_user_id_by_alias(share_with_alias)
        if not target_user_id:
            return {"status": False}

        notes = user_note_data.get("notes", {})
        if note_id not in notes:
            return {"status": False}

        note = notes[note_id]
        shared_with = note.get("shared_with", [])
        if share_with_alias not in shared_with:
            shared_with.append(share_with_alias)
            note["shared_with"] = shared_with
            note["updated_at"] = datetime.datetime.now().isoformat() + "Z"

        return {"status": True}

    def add_reminder(
        self,
        note_id: str,
        user: str,
        reminder_timestamp: str,
        status: str = "active",
    ) -> Dict[str, bool]:
        """
        Add a reminder to a note.

        Args:
            note_id (str): ID of the note.
            user (str): The user identifier.
            reminder_timestamp (str): ISO timestamp for the reminder.
            status (str): Status of the reminder (active, completed).

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
        reminders = note.get("reminders", [])
        reminders.append({
            "timestamp": reminder_timestamp,
            "status": status
        })
        note["reminders"] = reminders
        note["updated_at"] = datetime.datetime.now().isoformat() + "Z"

        return {"status": True}

    def search_notes(
        self,
        user: str,
        query: str,
        search_in_content: bool = True,
        search_in_title: bool = True,
        search_in_tags: bool = True,
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Search for notes based on a query string.

        Args:
            user (str): The user identifier.
            query (str): The search query.
            search_in_content (bool): Whether to search in note content.
            search_in_title (bool): Whether to search in note titles.
            search_in_tags (bool): Whether to search in note tags.

        Returns:
            Dict: A dictionary containing 'status' (bool) and 'notes' (List[Dict]) if successful.
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False, "notes": []}

        notes = user_note_data.get("notes", {})
        query_lower = query.lower()
        matching_notes = []

        for note_id, note_content in notes.items():
            match_found = False
            
            if search_in_title and query_lower in note_content.get("title", "").lower():
                match_found = True
            
            if search_in_content and query_lower in note_content.get("content", "").lower():
                match_found = True
            
            if search_in_tags:
                tags = note_content.get("tags", [])
                if isinstance(tags, str):
                    tags = tags.split(" | ")
                if any(query_lower in tag.lower() for tag in tags):
                    match_found = True
            
            if match_found:
                matching_notes.append(copy.deepcopy(note_content))

        return {"status": True, "notes": matching_notes}

    def get_notes_by_color(
        self,
        user: str,
        color: str,
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Get all notes of a specific color for a user.

        Args:
            user (str): The user identifier.
            color (str): The color to filter by.

        Returns:
            Dict: A dictionary containing 'status' (bool) and 'notes' (List[Dict]) if successful.
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False, "notes": []}

        notes = user_note_data.get("notes", {})
        colored_notes = []

        for note_id, note_content in notes.items():
            if note_content.get("color") == color:
                colored_notes.append(copy.deepcopy(note_content))

        return {"status": True, "notes": colored_notes}

    def get_notes_by_priority(
        self,
        user: str,
        priority: str,
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Get all notes of a specific priority for a user.

        Args:
            user (str): The user identifier.
            priority (str): The priority to filter by (low, medium, high).

        Returns:
            Dict: A dictionary containing 'status' (bool) and 'notes' (List[Dict]) if successful.
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False, "notes": []}

        notes = user_note_data.get("notes", {})
        priority_notes = []

        for note_id, note_content in notes.items():
            if note_content.get("priority") == priority:
                priority_notes.append(copy.deepcopy(note_content))

        return {"status": True, "notes": priority_notes}

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