# Inspired by https://appworld.dev/

import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional, Union, Literal
from state_loader import load_default_state
import re

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
    An API class for simulating Simple Note operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the SimpleNoteApis instance with in-memory backend for development and testing.
        
        Sets up data structures for managing users and their notes, then loads default scenario
        data to provide a realistic testing environment.
        
        Side Effects:
            - Initializes self.users as empty dictionary (populated by _load_scenario)
            - Sets self._api_description with API identification string
            - Loads DEFAULT_STATE scenario data via _load_scenario()
            - Prints confirmation message about loaded scenario
            
        Note:
            This is a simulated API for development/testing purposes, not connected to real
            SimpleNote servers. All data exists only in memory and is lost when the instance
            is destroyed.
            
        Example:
            >>> api = SimpleNoteApis()
            SimpleNoteApis: Loaded scenario with users and their UUIDs.
            >>> # API is now ready to use with pre-loaded test data
        """
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the SimpleNote API, which provides core functionality for managing notes."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the backend's state for testing or reset purposes.
        
        Replaces the current user and note data with the provided scenario, enabling consistent
        test environments or state resets during development.

        Args:
            scenario (Dict): Complete state dictionary to load. Expected structure:
                {
                    "users": {
                        "user-uuid-123": {
                            "first_name": str,
                            "last_name": str,
                            "email": str,
                            "alias": str,
                            "note_data": {
                                "notes": {
                                    "note-uuid": {...},
                                    ...
                                }
                            }
                        },
                        ...
                    }
                }
                If "users" key is missing, initializes with empty dict.
                
        Side Effects:
            - Deep copies scenario to prevent external modifications
            - Replaces self.users entirely with scenario data
            - Prints confirmation message with user count
            - All previous state is lost (existing notes, users, etc.)
            
        Note:
            Creates deep copy of scenario to ensure the original DEFAULT_STATE
            remains unmodified for future resets.
            
        Example:
            >>> api = SimpleNoteApis()
            >>> custom_scenario = {"users": {...}}
            >>> api._load_scenario(custom_scenario)
            SimpleNoteApis: Loaded scenario with users and their UUIDs.
        """
        DEFAULT_STATE_COPY = copy.deepcopy(scenario)
        self.users = DEFAULT_STATE_COPY.get("users", {})
        print("SimpleNoteApis: Loaded scenario with users and their UUIDs.")

    def _generate_unique_id(self) -> str:
        """
        Generates a universally unique identifier (UUID) for new notes.
        
        Returns:
            str: A new UUID v4 string in standard format (e.g., "550e8400-e29b-41d4-a716-446655440000")
            
        Note:
            Uses Python's uuid.uuid4() which generates cryptographically strong random UUIDs.
            Collision probability is effectively zero for practical purposes.
            
        Example:
            >>> api = SimpleNoteApis()
            >>> note_id = api._generate_unique_id()
            >>> len(note_id)  # Standard UUID string length
            36
        """
        return str(uuid.uuid4())

    def _get_user_id_by_alias(self, alias: str) -> Optional[str]:
        """
        Resolves a user alias (human-readable name) to internal UUID identifier.
        
        Searches all users to find the one matching the provided alias string.

        Args:
            alias (str): The user's alias (simple string identifier).
                Example: "john_doe", "alice"

        Returns:
            Optional[str]: The user's UUID if found, None if no user has that alias.
                Example return: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
                
        Note:
            Performs linear search through all users. Alias must match exactly (case-sensitive).
            
        Example:
            >>> api = SimpleNoteApis()
            >>> user_id = api._get_user_id_by_alias("alice")
            >>> if user_id:
            ...     print(f"Found user: {user_id}")
        """
        for user_id, user_data in self.users.items():
            if user_data.get("alias") == alias:
                return user_id
        return None

    def _get_user_alias_by_id(self, user_id: str) -> Optional[str]:
        """
        Resolves an internal UUID identifier to user alias (human-readable name).
        
        Reverse lookup of _get_user_id_by_alias, converting UUID to simple string alias.

        Args:
            user_id (str): The user's UUID identifier.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[str]: The user's alias if user exists, None if user not found.
                Example return: "alice", "john_doe"
                
        Example:
            >>> api = SimpleNoteApis()
            >>> alias = api._get_user_alias_by_id("user-uuid-123")
            >>> print(f"User alias: {alias}")
        """
        user_data = self.users.get(user_id)
        return user_data.get("alias") if user_data else None

    def _get_user_note_data(self, user_alias: str) -> Optional[Dict]:
        """
        Retrieves a user's complete note data structure by alias.
        
        Combines user lookup with note data access for convenient data retrieval.

        Args:
            user_alias (str): The user's alias (simple string identifier).
                Example: "alice", "john_doe"

        Returns:
            Optional[Dict]: The user's note_data dictionary if found, None if user doesn't exist.
                Success structure: {"notes": {"note-uuid": {...}, ...}}
                Returns None if user not found or has no note_data.
                
        Note:
            Returns reference to actual data structure (not a copy), allowing direct modification.
            
        Example:
            >>> api = SimpleNoteApis()
            >>> note_data = api._get_user_note_data("alice")
            >>> if note_data:
            ...     notes = note_data.get("notes", {})
            ...     print(f"User has {len(notes)} notes")
        """
        internal_user_id = self._get_user_id_by_alias(user_alias)
        if not internal_user_id:
            return None
        return self.users.get(internal_user_id, {}).get("note_data")

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves complete user information by user ID, including credentials.
        This method is intended for AI model context lookup during testing scenarios.
        
        Args:
            user_id (str): The unique UUID identifier of the user to retrieve.
        
        Returns:
            Dict[str, Any]: User data dictionary containing all user fields including credentials.
                Returns error dictionary if user not found with status=False and message.
        
        Notes:
            - This is a public method specifically for AI model context resolution
            - Exposes credentials intentionally for testing/simulation purposes
            - Should not be used in production environments
        """
        user_data = self.users.get(user_id)
        if not user_data:
            return {
                "status": False,
                "message": f"User with ID {user_id} not found."
            }
        
        # Return complete user data including the user_id itself
        result = {"user_id": user_id}
        result.update(user_data)
        return result

    def show_account(self, user: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves comprehensive account profile information for a user.
        
        Returns basic profile data including name, email, and alias for the specified user.
        This is typically used for account settings or profile display.

        Args:
            user (str): The user's alias (simple string identifier).
                Example: "alice", "john_doe"

        Returns:
            Dict[str, Union[bool, Dict]]: Response dictionary with structure:
                Success: {
                    "status": True,
                    "profile_data": {
                        "first_name": str,
                        "last_name": str,
                        "email": str,
                        "alias": str
                    }
                }
                Failure (user not found): {
                    "status": False,
                    "profile_data": {}
                }
                
        Note:
            Returns a new dictionary (not a reference to internal data) to prevent
            accidental modifications to the backend state.
            
        Example:
            >>> api = SimpleNoteApis()
            >>> result = api.show_account("alice")
            >>> if result["status"]:
            ...     profile = result["profile_data"]
            ...     print(f"{profile['first_name']} {profile['last_name']}")
            ...     print(f"Email: {profile['email']}")
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
        sort_by: str = "updated",
        sort_order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves a filtered and sorted list of notes for a user with pagination support.
        
        Provides flexible filtering by multiple criteria (tags, pinned status, color, archived
        status, priority) and customizable sorting. Supports pagination for large note collections.

        Args:
            user (str): The user's alias (simple string identifier).
                Example: "alice", "john_doe"
            tag (Optional[str]): Filter by specific tag. Only notes containing this tag are returned.
                Example: "work", "personal", "urgent"
                Default: None (no tag filtering)
            pinned (Optional[bool]): Filter by pinned status.
                True: Only pinned notes
                False: Only unpinned notes
                None: Include both (no filtering)
                Default: None
            color (Optional[str]): Filter by note color.
                Valid values: "yellow", "blue", "green", "pink", "white", "purple"
                Default: None (no color filtering)
            archived (Optional[bool]): Filter by archived status.
                True: Only archived notes
                False: Only active (non-archived) notes
                None: Include both
                Default: None
            priority (Optional[str]): Filter by priority level.
                Valid values: "low", "medium", "high"
                Default: None (no priority filtering)
            sort_by (str): Field to sort results by.
                Valid values: "created", "updated", "title", "priority"
                Default: "updated"
            sort_order (str): Sort direction.
                "asc": Ascending order (oldest/lowest first)
                "desc": Descending order (newest/highest first)
                Default: "desc"
            limit (int): Maximum number of notes to return per page.
                Default: 100
            offset (int): Number of notes to skip for pagination.
                Example: offset=100 with limit=50 returns notes 101-150
                Default: 0

        Returns:
            Dict[str, Union[bool, List[Dict]]]: Response dictionary with structure:
                Success: {
                    "status": True,
                    "notes": [
                        {
                            "id": str,
                            "title": str,
                            "content": str,
                            "tags": List[str],
                            "pinned": bool,
                            "color": str,
                            "archived": bool,
                            "priority": str,
                            "font_size": str,
                            "encrypted": bool,
                            "share_permissions": str,
                            "shared_with": List,
                            "reminders": List,
                            "user": str,
                            "created_at": str,
                            "updated_at": str
                        },
                        ...
                    ],
                    "total_count": int  # Total matching notes before pagination
                }
                Failure (user not found): {"status": False, "notes": []}
                Error (invalid parameters): {"status": False, "notes": [], "message": str}
                
        Error Cases:
            - Invalid sort_by: {"status": False, "notes": [], "message": "Invalid sort_by. Must be 'created', 'updated', 'title', or 'priority'."}
            - Invalid sort_order: {"status": False, "notes": [], "message": "Invalid sort_order. Must be 'asc' or 'desc'."}
            - User not found: {"status": False, "notes": []}
            
        Note:
            - Returns deep copies of note objects to prevent accidental modifications
            - All filters are applied cumulatively (AND logic)
            - Priority sorting: low=1, medium=2, high=3
            - Tags can be stored as string (" | " separated) or list
            - total_count reflects results after filtering but before pagination
            
        Example:
            >>> api = SimpleNoteApis()
            >>> # Get top 10 high-priority work notes sorted by update time
            >>> result = api.list_notes(
            ...     user="alice",
            ...     tag="work",
            ...     priority="high",
            ...     sort_by="updated",
            ...     sort_order="desc",
            ...     limit=10
            ... )
            >>> if result["status"]:
            ...     print(f"Found {result['total_count']} matching notes")
            ...     for note in result["notes"]:
            ...         print(f"- {note['title']}")
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False, "notes": []}

        # Validate sort parameters
        if sort_by not in ["created", "updated", "title", "priority"]:
            return {"status": False, "notes": [], "message": "Invalid sort_by. Must be 'created', 'updated', 'title', or 'priority'."}
        
        if sort_order not in ["asc", "desc"]:
            return {"status": False, "notes": [], "message": "Invalid sort_order. Must be 'asc' or 'desc'."}

        notes = user_note_data.get("notes", {})
        filtered_notes = []

        for _, note_content in notes.items():
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

        # Sort notes
        priority_order = {"low": 1, "medium": 2, "high": 3}
        if sort_by == "created":
            filtered_notes.sort(key=lambda x: x.get("created_at", ""), reverse=(sort_order == "desc"))
        elif sort_by == "updated":
            filtered_notes.sort(key=lambda x: x.get("updated_at", ""), reverse=(sort_order == "desc"))
        elif sort_by == "title":
            filtered_notes.sort(key=lambda x: x.get("title", "").lower(), reverse=(sort_order == "desc"))
        elif sort_by == "priority":
            filtered_notes.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 2), reverse=(sort_order == "desc"))

        # Apply pagination
        total_count = len(filtered_notes)
        paginated_notes = filtered_notes[offset:offset + limit]

        return {"status": True, "notes": paginated_notes, "total_count": total_count}

    def get_note(self, note_id: str, user: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves complete details of a specific note by its ID.
        
        Returns all note data including content, metadata, tags, sharing info, and reminders.
        Useful for displaying full note details or editing.

        Args:
            note_id (str): The note's UUID identifier.
                Example: "550e8400-e29b-41d4-a716-446655440000"
            user (str): The user's alias (simple string identifier) who owns the note.
                Example: "alice", "john_doe"

        Returns:
            Dict[str, Union[bool, Dict]]: Response dictionary with structure:
                Success: {
                    "status": True,
                    "note": {
                        "id": str,
                        "title": str,
                        "content": str,
                        "tags": List[str],
                        "pinned": bool,
                        "color": str,
                        "archived": bool,
                        "priority": str,
                        "font_size": str,
                        "encrypted": bool,
                        "share_permissions": str,
                        "shared_with": List[Dict],
                        "reminders": List[Dict],
                        "user": str,              # User UUID
                        "created_at": str,        # ISO 8601 timestamp
                        "updated_at": str         # ISO 8601 timestamp
                    }
                }
                Failure (user or note not found): {"status": False, "note": {}}
                
        Note:
            Returns a deep copy of the note to prevent accidental modifications to backend data.
            
        Example:
            >>> api = SimpleNoteApis()
            >>> result = api.get_note(note_id="note-uuid-123", user="alice")
            >>> if result["status"]:
            ...     note = result["note"]
            ...     print(f"Title: {note['title']}")
            ...     print(f"Content: {note['content']}")
            ...     print(f"Tags: {', '.join(note['tags'])}")
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
        font_size: str = "normal",
        encrypted: bool = False,
        share_permissions: str = "view_only"
    ) -> Dict[str, Union[bool, Dict]]:
        """
        Creates a new note with specified properties for a user.
        
        Generates a new note with unique UUID, initializes all metadata fields, and adds it
        to the user's note collection. Supports extensive customization including visual
        properties, security settings, and default sharing permissions.

        Args:
            user (str): The user's alias (simple string identifier) who will own the note.
                Example: "alice", "john_doe"
            title (str): The note's title/subject line.
                Example: "Meeting Notes", "Shopping List"
            content (str): The main text content of the note.
                Can be plain text or formatted markdown.
            tags (Optional[List[str]]): List of tags for categorization.
                Example: ["work", "urgent"], ["personal", "todo"]
                Default: [] (empty list)
            pinned (bool): Whether note should appear pinned at top of lists.
                Default: False
            color (str): Visual color theme for the note.
                Valid values: "yellow", "blue", "green", "pink", "white", "purple"
                Default: "yellow"
            archived (bool): Whether note starts in archived state.
                Default: False (active note)
            priority (str): Priority level for sorting and filtering.
                Valid values: "low", "medium", "high"
                Default: "medium"
            font_size (str): Display font size preference.
                Valid values: "small", "normal", "large"
                Default: "normal"
            encrypted (bool): Whether note content should be encrypted.
                Default: False
            share_permissions (str): Default permissions when sharing this note.
                Valid values:
                - "view_only": Recipients can only read
                - "edit": Recipients can modify content
                - "full": Recipients have complete control
                Default: "view_only"

        Returns:
            Dict[str, Union[bool, Dict]]: Response dictionary with structure:
                Success: {
                    "status": True,
                    "note": {
                        "id": str,                    # Generated UUID
                        "title": str,
                        "content": str,
                        "tags": List[str],
                        "pinned": bool,
                        "color": str,
                        "archived": bool,
                        "priority": str,
                        "font_size": str,
                        "encrypted": bool,
                        "share_permissions": str,
                        "shared_with": [],           # Initially empty
                        "reminders": [],              # Initially empty
                        "user": str,                  # User UUID (not alias)
                        "created_at": str,            # ISO 8601 timestamp
                        "updated_at": str             # ISO 8601 timestamp (same as created_at)
                    }
                }
                Error: {"status": False, "message": str} with descriptive error message
                
        Error Cases:
            - User not found: {"status": False, "message": "User not found."}
            - Invalid font_size: {"status": False, "message": "Invalid font size. Must be 'small', 'normal', or 'large'."}
            - Invalid share_permissions: {"status": False, "message": "Invalid share permissions. Must be 'view_only', 'edit', or 'full'."}
            
        Side Effects:
            - Generates new UUID for note ID
            - Adds note to user's note_data.notes dictionary
            - If user has no note_data, initializes it
            - Prints confirmation message to console with note ID and properties
            - Sets created_at and updated_at to current timestamp
            
        Note:
            - Note ID is auto-generated and guaranteed unique
            - Both created_at and updated_at are set to the same value initially
            - Tags default to empty list if not provided
            - shared_with and reminders lists are always initialized empty
            
        Example:
            >>> api = SimpleNoteApis()
            >>> result = api.create_note(
            ...     user="alice",
            ...     title="Project Ideas",
            ...     content="1. Implement search\n2. Add dark mode",
            ...     tags=["work", "development"],
            ...     priority="high",
            ...     color="blue",
            ...     pinned=True
            ... )
            Note 'Project Ideas' created for alice with ID: 550e8400-... (encrypted: False, priority: high)
            >>> if result["status"]:
            ...     note_id = result["note"]["id"]
            ...     print(f"Created note: {note_id}")
        """
        internal_user_id = self._get_user_id_by_alias(user)
        if not internal_user_id:
            return {"status": False, "message": "User not found."}

        # Validate font_size
        if font_size not in ["small", "normal", "large"]:
            return {"status": False, "message": "Invalid font size. Must be 'small', 'normal', or 'large'."}
        
        # Validate share_permissions
        if share_permissions not in ["view_only", "edit", "full"]:
            return {"status": False, "message": "Invalid share permissions. Must be 'view_only', 'edit', or 'full'."}

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
            "font_size": font_size,
            "encrypted": encrypted,
            "share_permissions": share_permissions,
            "shared_with": [],
            "reminders": [],
            "user": internal_user_id,
            "created_at": current_time_iso,
            "updated_at": current_time_iso,
        }
        notes[new_note_id] = new_note

        print(f"Note '{title}' created for {user} with ID: {new_note_id} (encrypted: {encrypted}, priority: {priority})")
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
        Updates content and metadata of an existing note.
        
        Allows modification of multiple note properties in a single operation. All fields
        are optional except new_content, enabling targeted updates without affecting
        other properties.

        Args:
            note_id (str): UUID of the note to update.
                Example: "550e8400-e29b-41d4-a716-446655440000"
            user (str): The user's alias (simple string identifier) who owns the note.
                Example: "alice", "john_doe"
            new_content (str): The new text content for the note (required).
                Completely replaces existing content.
            new_title (Optional[str]): New title for the note.
                If None, title remains unchanged.
                Default: None
            new_tags (Optional[List[str]]): New tag list.
                If None, tags remain unchanged.
                Example: ["work", "urgent"]
                Default: None
            new_pinned_status (Optional[bool]): New pinned state.
                If None, pinned status remains unchanged.
                Default: None
            new_color (Optional[str]): New color theme.
                If None, color remains unchanged.
                Valid values: "yellow", "blue", "green", "pink", "white", "purple"
                Default: None
            new_archived_status (Optional[bool]): New archived state.
                If None, archived status remains unchanged.
                Default: None
            new_priority (Optional[str]): New priority level.
                If None, priority remains unchanged.
                Valid values: "low", "medium", "high"
                Default: None

        Returns:
            Dict[str, bool]: Response dictionary:
                Success: {"status": True}
                Failure: {"status": False} - user or note not found
                
        Side Effects:
            - Modifies note content directly in backend storage
            - Updates specified metadata fields
            - Sets updated_at to current timestamp (ISO 8601 format)
            - Unchanged fields retain their original values
            
        Note:
            Only new_content is required; all other parameters are truly optional.
            Pass None (or omit) for any field you don't want to change.
            
        Example:
            >>> api = SimpleNoteApis()
            >>> # Update just content and priority
            >>> result = api.update_note_content(
            ...     note_id="note-uuid-123",
            ...     user="alice",
            ...     new_content="Updated meeting notes with action items",
            ...     new_priority="high"
            ... )
            >>> if result["status"]:
            ...     print("Note updated successfully")
            >>> 
            >>> # Update multiple properties at once
            >>> result = api.update_note_content(
            ...     note_id="note-uuid-456",
            ...     user="alice",
            ...     new_content="Final version",
            ...     new_title="Completed Project",
            ...     new_archived_status=True,
            ...     new_color="green"
            ... )
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
        Adds content to the beginning or end of an existing note without replacing it.
        
        Useful for incrementally building notes, adding updates, or prepending context.
        Automatically inserts newline separator between existing and new content.

        Args:
            note_id (str): UUID of the note to modify.
                Example: "550e8400-e29b-41d4-a716-446655440000"
            user (str): The user's alias (simple string identifier) who owns the note.
                Example: "alice", "john_doe"
            added_content (str): Text to add to the note.
                Example: "Update: Meeting rescheduled to 3pm"
            append_or_prepend (Literal["append", "prepend"]): Where to add the content.
                "append": Add to end of note (after existing content)
                "prepend": Add to beginning of note (before existing content)
                Default: "append"

        Returns:
            Dict[str, bool]: Response dictionary:
                Success: {"status": True}
                Failure: {"status": False} - user or note not found
                
        Side Effects:
            - Modifies note content by concatenating new text with newline separator
            - Updates updated_at timestamp to current time
            - Does not modify other note properties (title, tags, etc.)
            
        Note:
            - Automatically adds "\n" separator between existing and new content
            - For append: existing_content + "\n" + added_content
            - For prepend: added_content + "\n" + existing_content
            - Does not check for duplicate content
            
        Example:
            >>> api = SimpleNoteApis()
            >>> # Append new information to existing note
            >>> result = api.append_or_prepend_note_content(
            ...     note_id="note-uuid-123",
            ...     user="alice",
            ...     added_content="Update: Project approved by management",
            ...     append_or_prepend="append"
            ... )
            >>> 
            >>> # Prepend urgent notice at top
            >>> result = api.append_or_prepend_note_content(
            ...     note_id="note-uuid-456",
            ...     user="alice",
            ...     added_content="URGENT: Deadline moved to tomorrow!",
            ...     append_or_prepend="prepend"
            ... )
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
        Permanently deletes a note from a user's collection.
        
        Removes the note entirely from the backend storage. This operation cannot be undone.
        Only the note owner can delete their notes.

        Args:
            note_id (str): UUID of the note to delete.
                Example: "550e8400-e29b-41d4-a716-446655440000"
            user (str): The user's alias (simple string identifier) who owns the note.
                Only notes belonging to this user can be deleted.
                Example: "alice", "john_doe"

        Returns:
            Dict[str, bool]: Response dictionary:
                Success: {"status": True} - note deleted successfully
                Failure: {"status": False} - user not found or note not found/not owned by user
                
        Side Effects:
            - Permanently removes note from backend storage
            - All note data is lost (content, metadata, sharing info, reminders)
            - Cannot be undone or recovered
            
        Note:
            - User must own the note to delete it (verified by user alias)
            - Shared users cannot delete notes they don't own
            - Returns False if note doesn't exist or belongs to different user
            
        Example:
            >>> api = SimpleNoteApis()
            >>> result = api.delete_note(note_id="note-uuid-123", user="alice")
            >>> if result["status"]:
            ...     print("Note deleted successfully")
            >>> else:
            ...     print("Failed to delete note - not found or access denied")
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
        permissions: str = "view_only",
        notify_recipient: bool = True,
        allow_reshare: bool = False
    ) -> Dict[str, bool]:
        """
        Shares a note with another user, granting specified access permissions.
        
        Adds a user to the note's shared_with list with configurable permissions and
        resharing controls. Optionally sends notification to recipient.

        Args:
            note_id (str): UUID of the note to share.
                Example: "550e8400-e29b-41d4-a716-446655440000"
            user (str): The note owner's alias (simple string identifier).
                Example: "alice"
            share_with_alias (str): Alias of the user to share with.
                Must be an existing user in the system.
                Example: "bob", "charlie"
            permissions (str): Access level granted to recipient.
                Valid values:
                - "view_only": Can read but not modify (safest)
                - "edit": Can modify content
                - "full": Complete control (can delete, reshare)
                Default: "view_only"
            notify_recipient (bool): Whether to send notification to recipient.
                If True, prints notification message to console.
                Default: True
            allow_reshare (bool): Whether recipient can share with others.
                False: Recipient cannot share further (recommended for sensitive notes)
                True: Recipient can share with additional users
                Default: False

        Returns:
            Dict[str, bool]: Response dictionary:
                Success: {"status": True}
                Failure: {"status": False} - various error conditions
                
        Error Cases:
            - User (owner) not found: {"status": False}
            - Target user (share_with_alias) not found: {"status": False}
            - Invalid permissions value: {"status": False}
            - Note not found: {"status": False}
            
        Side Effects:
            - Adds or updates entry in note's shared_with list with permissions and metadata
            - Updates note's updated_at timestamp
            - If already shared with user, updates existing permissions
            - Converts old string-based sharing format to new dict format if needed
            - If notify_recipient=True, prints notification to console
            
        Note:
            - If note is already shared with the user, updates their permissions
            - Sharing info includes: alias, permissions, allow_reshare flag, and shared_at timestamp
            - Old format (list of strings) is automatically migrated to new format (list of dicts)
            - Notification is simulated via console print, not actual email/message
            
        Example:
            >>> api = SimpleNoteApis()
            >>> # Share with view-only access
            >>> result = api.share_note(
            ...     note_id="note-uuid-123",
            ...     user="alice",
            ...     share_with_alias="bob",
            ...     permissions="view_only",
            ...     notify_recipient=True
            ... )
            Notification sent to bob about shared note: Meeting Notes
            >>> 
            >>> # Share with edit permissions and resharing
            >>> result = api.share_note(
            ...     note_id="note-uuid-456",
            ...     user="alice",
            ...     share_with_alias="charlie",
            ...     permissions="edit",
            ...     allow_reshare=True,
            ...     notify_recipient=False
            ... )
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False}

        # Check if the target user exists
        target_user_id = self._get_user_id_by_alias(share_with_alias)
        if not target_user_id:
            return {"status": False}

        # Validate permissions
        if permissions not in ["view_only", "edit", "full"]:
            return {"status": False}

        notes = user_note_data.get("notes", {})
        if note_id not in notes:
            return {"status": False}

        note = notes[note_id]
        shared_with = note.get("shared_with", [])
        
        # Store sharing information with permissions
        share_info = {
            "alias": share_with_alias,
            "permissions": permissions,
            "allow_reshare": allow_reshare,
            "shared_at": datetime.datetime.now().isoformat() + "Z"
        }
        
        # Convert old string format to dict format if needed
        if shared_with and isinstance(shared_with[0], str):
            shared_with = [{"alias": alias, "permissions": "view_only", "allow_reshare": False, "shared_at": datetime.datetime.now().isoformat() + "Z"} for alias in shared_with]
        
        # Check if already shared and update or add
        existing_share = next((s for s in shared_with if isinstance(s, dict) and s.get("alias") == share_with_alias), None)
        if existing_share:
            existing_share.update(share_info)
        else:
            shared_with.append(share_info)
        
        note["shared_with"] = shared_with
        note["updated_at"] = datetime.datetime.now().isoformat() + "Z"
        
        if notify_recipient:
            print(f"Notification sent to {share_with_alias} about shared note: {note.get('title')}")

        return {"status": True}

    def add_reminder(
        self,
        note_id: str,
        user: str,
        reminder_timestamp: str,
        status: str = "active",
        repeat_interval: Optional[str] = None,
        notification_method: str = "app",
        custom_message: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Adds a time-based reminder to a note with configurable notification settings.
        
        Creates a reminder that will alert the user at the specified time. Supports
        recurring reminders, multiple notification methods, and custom messages.

        Args:
            note_id (str): UUID of the note to add reminder to.
                Example: "550e8400-e29b-41d4-a716-446655440000"
            user (str): The user's alias (simple string identifier) who owns the note.
                Example: "alice", "john_doe"
            reminder_timestamp (str): When to trigger the reminder (ISO 8601 format).
                Example: "2025-12-15T14:30:00Z", "2025-12-20T09:00:00-05:00"
            status (str): Current reminder status.
                Valid values: "active", "completed"
                Default: "active"
            repeat_interval (Optional[str]): Recurring reminder schedule.
                Valid values:
                - None: One-time reminder (default)
                - "daily": Repeats every day
                - "weekly": Repeats every week
                - "monthly": Repeats every month
                Default: None
            notification_method (str): How to deliver the reminder.
                Valid values:
                - "app": In-app notification (default)
                - "email": Email notification
                - "sms": SMS text message
                Default: "app"
            custom_message (Optional[str]): Custom reminder text.
                If None, uses default message based on note title.
                Example: "Don't forget to review!"
                Default: None

        Returns:
            Dict[str, bool]: Response dictionary:
                Success: {"status": True}
                Failure: {"status": False} - various error conditions
                
        Error Cases:
            - User not found: {"status": False}
            - Note not found: {"status": False}
            - Invalid repeat_interval: {"status": False}
            - Invalid notification_method: {"status": False}
            
        Side Effects:
            - Appends reminder object to note's reminders list
            - Updates note's updated_at timestamp
            - Reminder includes creation timestamp
            
        Note:
            - Multiple reminders can be added to the same note
            - Reminders are stored but not actively triggered (simulation only)
            - created_at timestamp is auto-generated for each reminder
            - Real implementation would integrate with notification system
            
        Example:
            >>> api = SimpleNoteApis()
            >>> # Add one-time reminder
            >>> result = api.add_reminder(
            ...     note_id="note-uuid-123",
            ...     user="alice",
            ...     reminder_timestamp="2025-12-20T09:00:00Z",
            ...     notification_method="email",
            ...     custom_message="Time for weekly review!"
            ... )
            >>> 
            >>> # Add daily recurring reminder
            >>> result = api.add_reminder(
            ...     note_id="note-uuid-456",
            ...     user="alice",
            ...     reminder_timestamp="2025-12-15T08:00:00Z",
            ...     repeat_interval="daily",
            ...     notification_method="app"
            ... )
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False}

        notes = user_note_data.get("notes", {})
        if note_id not in notes:
            return {"status": False}

        # Validate repeat_interval if provided
        if repeat_interval and repeat_interval not in ["daily", "weekly", "monthly"]:
            return {"status": False}
        
        # Validate notification_method
        if notification_method not in ["app", "email", "sms"]:
            return {"status": False}

        note = notes[note_id]
        reminders = note.get("reminders", [])
        reminders.append({
            "timestamp": reminder_timestamp,
            "status": status,
            "repeat_interval": repeat_interval,
            "notification_method": notification_method,
            "custom_message": custom_message,
            "created_at": datetime.datetime.now().isoformat() + "Z"
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
        case_sensitive: bool = False,
        whole_word_only: bool = False,
        include_archived: bool = False
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Searches for notes matching a query string with flexible search options.
        
        Performs text search across note titles, content, and tags with configurable
        search behavior including case sensitivity and word boundary matching.

        Args:
            user (str): The user's alias (simple string identifier).
                Example: "alice", "john_doe"
            query (str): The text to search for.
                Example: "meeting", "project deadline", "urgent"
            search_in_content (bool): Whether to search within note content/body.
                Default: True
            search_in_title (bool): Whether to search within note titles.
                Default: True
            search_in_tags (bool): Whether to search within note tags.
                Default: True
            case_sensitive (bool): Whether to match case exactly.
                False: "Meeting" matches "meeting", "MEETING", etc.
                True: "Meeting" only matches "Meeting"
                Default: False
            whole_word_only (bool): Whether to match complete words only.
                False: "meet" matches "meeting", "meets", etc. (substring match)
                True: "meet" only matches " meet " as whole word
                Uses regex word boundaries (\b) for matching.
                Default: False
            include_archived (bool): Whether to include archived notes in results.
                False: Only search active notes
                True: Search both active and archived notes
                Default: False

        Returns:
            Dict[str, Union[bool, List[Dict]]]: Response dictionary with structure:
                Success: {
                    "status": True,
                    "notes": [
                        {  # Complete note objects for each match
                            "id": str,
                            "title": str,
                            "content": str,
                            "tags": List[str],
                            # ... all other note fields
                        },
                        ...
                    ]
                }
                Failure (user not found): {"status": False, "notes": []}
                
        Note:
            - Returns deep copies of matching notes to prevent accidental modifications
            - If all search_in_* flags are False, no matches will be found
            - Multiple search locations (title/content/tags) are OR combined (match any)
            - Tags can be stored as string (" | " separated) or list format
            - Uses Python regex for whole_word_only matching
            - Archived notes excluded by default to avoid clutter
            
        Example:
            >>> api = SimpleNoteApis()
            >>> # Case-insensitive search in all fields
            >>> result = api.search_notes(
            ...     user="alice",
            ...     query="meeting"
            ... )
            >>> if result["status"]:
            ...     print(f"Found {len(result['notes'])} notes")
            ...     for note in result['notes']:
            ...         print(f"- {note['title']}")
            >>> 
            >>> # Precise whole-word search, case-sensitive, include archived
            >>> result = api.search_notes(
            ...     user="alice",
            ...     query="Project",
            ...     case_sensitive=True,
            ...     whole_word_only=True,
            ...     include_archived=True,
            ...     search_in_content=False  # Only search titles and tags
            ... )
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False, "notes": []}

        notes = user_note_data.get("notes", {})
        search_query = query if case_sensitive else query.lower()
        matching_notes = []
        
        for _, note_content in notes.items():
            # Skip archived notes if not included
            if not include_archived and note_content.get("archived", False):
                continue
            
            match_found = False
            
            if search_in_title:
                title = note_content.get("title", "")
                search_text = title if case_sensitive else title.lower()
                if whole_word_only:
                    if re.search(r'\b' + re.escape(search_query) + r'\b', search_text):
                        match_found = True
                else:
                    if search_query in search_text:
                        match_found = True
            
            if search_in_content:
                content = note_content.get("content", "")
                search_text = content if case_sensitive else content.lower()
                if whole_word_only:
                    if re.search(r'\b' + re.escape(search_query) + r'\b', search_text):
                        match_found = True
                else:
                    if search_query in search_text:
                        match_found = True
            
            if search_in_tags:
                tags = note_content.get("tags", [])
                if isinstance(tags, str):
                    tags = tags.split(" | ")
                for tag in tags:
                    search_tag = tag if case_sensitive else tag.lower()
                    if whole_word_only:
                        if re.search(r'\b' + re.escape(search_query) + r'\b', search_tag):
                            match_found = True
                            break
                    else:
                        if search_query in search_tag:
                            match_found = True
                            break
            
            if match_found:
                matching_notes.append(copy.deepcopy(note_content))

        return {"status": True, "notes": matching_notes}

    def get_notes_by_color(
        self,
        user: str,
        color: str,
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves all notes with a specific color theme for a user.
        
        Filters notes by their visual color property, useful for color-based
        organization and visual grouping.

        Args:
            user (str): The user's alias (simple string identifier).
                Example: "alice", "john_doe"
            color (str): The color to filter by.
                Valid values: "yellow", "blue", "green", "pink", "white", "purple"
                Must match exactly (case-sensitive).
                Example: "blue", "green"

        Returns:
            Dict[str, Union[bool, List[Dict]]]: Response dictionary with structure:
                Success: {
                    "status": True,
                    "notes": [  # List of complete note objects with matching color
                        {
                            "id": str,
                            "title": str,
                            "color": str,  # Will match the requested color
                            # ... all other note fields
                        },
                        ...
                    ]
                }
                Failure (user not found): {"status": False, "notes": []}
                
        Note:
            - Returns deep copies of matching notes to prevent accidental modifications
            - Returns empty list if no notes match the color or user not found
            - Includes both active and archived notes with the specified color
            - Color names are case-sensitive
            
        Example:
            >>> api = SimpleNoteApis()
            >>> result = api.get_notes_by_color(user="alice", color="blue")
            >>> if result["status"]:
            ...     print(f"Found {len(result['notes'])} blue notes")
            ...     for note in result['notes']:
            ...         print(f"- {note['title']}")
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False, "notes": []}

        notes = user_note_data.get("notes", {})
        colored_notes = []

        for _, note_content in notes.items():
            if note_content.get("color") == color:
                colored_notes.append(copy.deepcopy(note_content))

        return {"status": True, "notes": colored_notes}

    def get_notes_by_priority(
        self,
        user: str,
        priority: str,
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves all notes with a specific priority level for a user.
        
        Filters notes by their priority property, useful for task management
        and importance-based organization.

        Args:
            user (str): The user's alias (simple string identifier).
                Example: "alice", "john_doe"
            priority (str): The priority level to filter by.
                Valid values: "low", "medium", "high"
                Must match exactly (case-sensitive).
                Example: "high", "medium"

        Returns:
            Dict[str, Union[bool, List[Dict]]]: Response dictionary with structure:
                Success: {
                    "status": True,
                    "notes": [  # List of complete note objects with matching priority
                        {
                            "id": str,
                            "title": str,
                            "priority": str,  # Will match the requested priority
                            # ... all other note fields
                        },
                        ...
                    ]
                }
                Failure (user not found): {"status": False, "notes": []}
                
        Note:
            - Returns deep copies of matching notes to prevent accidental modifications
            - Returns empty list if no notes match the priority or user not found
            - Includes both active and archived notes with the specified priority
            - Priority values are case-sensitive
            - Useful for filtering urgent tasks or low-priority backlog items
            
        Example:
            >>> api = SimpleNoteApis()
            >>> # Get all high-priority notes
            >>> result = api.get_notes_by_priority(user="alice", priority="high")
            >>> if result["status"]:
            ...     print(f"Found {len(result['notes'])} high-priority notes")
            ...     for note in result['notes']:
            ...         print(f"- {note['title']}")
            >>> 
            >>> # Get low-priority backlog
            >>> backlog = api.get_notes_by_priority(user="alice", priority="low")
        """
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False, "notes": []}

        notes = user_note_data.get("notes", {})
        priority_notes = []

        for _, note_content in notes.items():
            if note_content.get("priority") == priority:
                priority_notes.append(copy.deepcopy(note_content))

        return {"status": True, "notes": priority_notes}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the backend to its initial default state.
        
        Reloads the default scenario data, clearing all user modifications including created
        notes, updated content, and changed settings. This is a utility function for testing
        purposes and is not a standard SimpleNote API endpoint.

        Returns:
            Dict[str, bool]: Status dictionary:
                {"reset_status": True} indicating successful reset
                
        Side Effects:
            - Reloads all backend data from DEFAULT_STATE scenario
            - Resets self.users with all note data
            - All user modifications are lost (created/updated/deleted notes)
            - Prints confirmation message to console
            
        Note:
            - This is a test utility method not present in real SimpleNote API
            - Use for resetting test environments between test runs
            - All in-memory changes are discarded (no persistence)
            - Useful for ensuring clean state in automated testing
            - Returns original users and notes from loaded scenario file
            
        Example:
            >>> api = SimpleNoteApis()
            >>> # Make some changes...
            >>> api.create_note(user="alice", title="Test", content="Test content")
            >>> api.delete_note(note_id="existing-note-uuid", user="alice")
            >>> # ... do some testing ...
            >>> result = api.reset_data()  # Clean slate for next test
            SimpleNoteApis: All data reset to default state.
            >>> # All changes reverted, back to default state
        """
        self._load_scenario(DEFAULT_STATE)
        print("SimpleNoteApis: All data reset to default state.")
        return {"reset_status": True}