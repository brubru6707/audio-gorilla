from typing import Dict, Union, Optional, Literal, List
from copy import deepcopy

# Dummy backend data for SimpleNoteApis
DEFAULT_STATE = {
    "notes": {
        0: {
            "id": 0,
            "title": "My First Note",
            "content": "This is the content of my first note. It's about getting started.",
            "tags": ["personal", "getting-started"],
            "pinned": True,
            "user": "user123"
        },
        1: {
            "id": 1,
            "title": "Grocery List",
            "content": "Milk, Eggs, Bread, Butter, Coffee",
            "tags": ["shopping", "food"],
            "pinned": False,
            "user": "user123"
        },
        2: {
            "id": 2,
            "title": "Project Ideas",
            "content": "Brainstorming new features for the app. Need to consider user feedback.",
            "tags": ["work", "ideas", "development"],
            "pinned": True,
            "user": "user123"
        },
        3: {
            "id": 3,
            "title": "Meeting Minutes",
            "content": "Discussed Q3 strategy and next steps for marketing campaign.",
            "tags": ["work", "meeting"],
            "pinned": False,
            "user": "user456" # Note for a different user
        }
    },
    "note_counter": 4 # Next available ID for a new note
}

class SimpleNoteApis:
    def __init__(self):
        """
        Initializes the SimpleNoteApis instance and loads the default scenario.
        """
        self.notes: Dict[int, Dict] = {}  # note_id -> note data
        self.note_counter: int = 0
        self._api_description = "This tool belongs to the SimpleNoteApis, which provides core functionality for note management."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: dict) -> None:
        """
        Loads a scenario into the SimpleNoteApis instance.
        This method is used to set up the initial state of the API for testing or specific scenarios.

        Args:
            scenario (dict): A dictionary containing the initial state for notes and note_counter.
        """
        # Create a deep copy of the default state to avoid modifying the original DEFAULT_STATE
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)

        # Populate instance variables using data from the scenario or default values
        self.notes = scenario.get("notes", DEFAULT_STATE_COPY["notes"])
        self.note_counter = scenario.get("note_counter", DEFAULT_STATE_COPY["note_counter"])

    def search_notes(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        pinned: Optional[bool] = None,
        page_index: int = 0, # Default to first page
        page_limit: int = 10, # Default to 10 items per page
        sort_by: Optional[str] = None,
        user: str = "" # Added user parameter to filter notes by owner
    ) -> Dict[str, Union[bool, list]]:
        """
        Search for notes based on various criteria.

        Args:
            query (str): Search query string to match against note titles and content.
            tags (Optional[List[str]]): List of tags to filter notes by. Only notes
                                        containing ALL specified tags will be returned.
            pinned (Optional[bool]): Filter by pinned status. True for pinned notes,
                                     False for unpinned, None for all.
            page_index (int): Pagination page index (0-based).
            page_limit (int): Number of items per page.
            sort_by (Optional[str]): Field to sort by. Supported values: "title", "date".
                                     If None, no specific sorting is applied beyond initial filtering order.
            user (str): The user identifier. Only notes belonging to this user will be searched.

        Returns:
            Dict[str, Union[bool, list]]: A dictionary containing:
                                          - "status" (bool): True if the search was successful.
                                          - "notes" (list): A list of dictionaries, where each dictionary
                                                            represents a matching note.
        """
        results = []

        for note_id, note in self.notes.items():
            # Filter by user
            if user and note.get("user") != user:
                continue

            # Filter by query in title or content
            matches_query = query.lower() in note["title"].lower() or query.lower() in note["content"].lower()

            # Filter by tags (all tags must be present)
            matches_tags = tags is None or all(tag in note["tags"] for tag in tags)

            # Filter by pinned status
            matches_pinned = pinned is None or note["pinned"] == pinned

            if matches_query and matches_tags and matches_pinned:
                results.append(note)

        # Apply sorting
        if sort_by == "title":
            results.sort(key=lambda x: x["title"].lower())
        elif sort_by == "date":
            # Using ID as a proxy for creation date, assuming IDs are sequential
            results.sort(key=lambda x: x["id"])

        # Apply pagination
        start = page_index * page_limit
        end = start + page_limit
        paginated_results = results[start:end]

        return {"status": True, "notes": paginated_results}

    def show_note(
        self,
        note_id: int,
        user: str,
    ) -> Dict[str, Union[bool, str, list, int]]:
        """
        Show details of a specific note.

        Args:
            note_id (int): ID of the note to retrieve.
            user (str): The user identifier. Only notes belonging to this user can be shown.

        Returns:
            Dict[str, Union[bool, str, list, int]]: A dictionary containing:
                                                    - "status" (bool): True if the note was found and belongs to the user.
                                                    - "id" (int): The ID of the note.
                                                    - "title" (str): The title of the note.
                                                    - "content" (str): The content of the note.
                                                    - "tags" (list): A list of tags associated with the note.
                                                    - "pinned" (bool): The pinned status of the note.
                                                    Returns {"status": False} if the note is not found or
                                                    does not belong to the specified user.
        """
        if note_id not in self.notes or self.notes[note_id].get("user") != user:
            return {"status": False}

        note = self.notes[note_id]
        return {
            "status": True,
            "id": note_id,
            "title": note["title"],
            "content": note["content"],
            "tags": note["tags"],
            "pinned": note["pinned"]
        }

    def create_note(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        pinned: bool = False, # Default to not pinned
        user: str = "" # User who is creating the note
    ) -> Dict[str, Union[bool, int]]:
        """
        Create a new note.

        Args:
            title (str): Title of the new note.
            content (str): Content of the new note.
            tags (Optional[List[str]]): List of tags for the note. Defaults to an empty list if None.
            pinned (bool): Whether the note should be pinned. Defaults to False.
            user (str): The user identifier who is creating this note.

        Returns:
            Dict[str, Union[bool, int]]: A dictionary containing:
                                          - "status" (bool): True if the note was created successfully.
                                          - "id" (int): The ID of the newly created note.
        """
        note_id = self.note_counter
        self.notes[note_id] = {
            "id": note_id,
            "title": title,
            "content": content,
            "tags": tags or [], # Ensure tags is always a list
            "pinned": pinned,
            "user": user
        }
        self.note_counter += 1
        return {"status": True, "id": note_id}

    def update_note(
        self,
        note_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        pinned: Optional[bool] = None,
        user: str = "" # User who is updating the note
    ) -> Dict[str, bool]:
        """
        Update an existing note.

        Args:
            note_id (int): ID of the note to update.
            title (Optional[str]): New title for the note. If None, the title is not changed.
            content (Optional[str]): New content for the note. If None, the content is not changed.
            tags (Optional[List[str]]): New list of tags for the note. If None, tags are not changed.
            pinned (Optional[bool]): New pinned status for the note. If None, pinned status is not changed.
            user (str): The user identifier who is updating this note. Only notes belonging
                        to this user can be updated.

        Returns:
            Dict[str, bool]: A dictionary containing:
                             - "status" (bool): True if the note was updated successfully,
                                                False if the note was not found or does not
                                                belong to the specified user.
        """
        if note_id not in self.notes or self.notes[note_id].get("user") != user:
            return {"status": False}

        note = self.notes[note_id]
        if title is not None:
            note["title"] = title
        if content is not None:
            note["content"] = content
        if tags is not None:
            note["tags"] = tags
        if pinned is not None:
            note["pinned"] = pinned

        return {"status": True}

    def add_content_to_note(
        self,
        note_id: int,
        append_or_prepend: Literal["append", "prepend"],
        added_content: str,
        user: str = "" # User who is modifying the note
    ) -> Dict[str, bool]:
        """
        Add content to an existing note, either by appending or prepending.

        Args:
            note_id (int): ID of the note to modify.
            append_or_prepend (Literal["append", "prepend"]): Specifies where to add the content.
                                                               "append" adds to the end, "prepend" adds to the beginning.
            added_content (str): The content string to add to the note.
            user (str): The user identifier who is modifying this note. Only notes belonging
                        to this user can be modified.

        Returns:
            Dict[str, bool]: A dictionary containing:
                             - "status" (bool): True if the content was added successfully,
                                                False if the note was not found or does not
                                                belong to the specified user.
        """
        if note_id not in self.notes or self.notes[note_id].get("user") != user:
            return {"status": False}

        note = self.notes[note_id]
        if append_or_prepend == "append":
            note["content"] += "\n" + added_content
        else: # prepend
            note["content"] = added_content + "\n" + note["content"]

        return {"status": True}

    def delete_note(
        self,
        note_id: int,
        user: str,
    ) -> Dict[str, bool]:
        """
        Delete a note.

        Args:
            note_id (int): ID of the note to delete.
            user (str): The user identifier. Only notes belonging to this user can be deleted.

        Returns:
            Dict[str, bool]: A dictionary containing:
                             - "status" (bool): True if the note was deleted successfully,
                                                False if the note was not found or does not
                                                belong to the specified user.
        """
        if note_id not in self.notes or self.notes[note_id].get("user") != user:
            return {"status": False}

        del self.notes[note_id]
        return {"status": True}