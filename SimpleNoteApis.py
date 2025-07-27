import datetime
import copy
from typing import Dict, List, Any, Optional, Union, Literal

DEFAULT_STATE = {
    "users": {
        "jdoe": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@noted.com",
            "note_data": {
                "notes": {
                    0: {
                        "id": 0,
                        "title": "Onboarding Checklist for New Devs",
                        "content": "1. Set up dev environment. 2. Clone repositories. 3. Attend morning stand-up. 4. Review coding standards.",
                        "tags": ["work", "onboarding", "dev"],
                        "pinned": True,
                        "user": "jdoe"
                    },
                    1: {
                        "id": 1,
                        "title": "Weekend Hike Gear List",
                        "content": "Backpack, water bottles, trail mix, first-aid kit, comfortable boots, rain jacket.",
                        "tags": ["personal", "hiking", "weekend"],
                        "pinned": False,
                        "user": "jdoe"
                    },
                    2: {
                        "id": 2,
                        "title": "Q3 Marketing Campaign Brainstorm",
                        "content": "Focus on social media engagement. Explore TikTok ads. Partner with influencers in niche markets.",
                        "tags": ["work", "marketing", "ideas"],
                        "pinned": True,
                        "user": "jdoe"
                    }
                },
                "note_counter": 3
            }
        },
        "jsmith": {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@noted.com",
            "note_data": {
                "notes": {
                    3: {
                        "id": 3,
                        "title": "Team Meeting Agenda - July 26",
                        "content": "Review sprint progress, discuss blocker issues, allocate tasks for next sprint, open floor for questions.",
                        "tags": ["work", "meeting", "agile"],
                        "pinned": True,
                        "user": "jsmith"
                    },
                    4: {
                        "id": 4,
                        "title": "Healthy Dinner Recipes to Try",
                        "content": "Quinoa salad with roasted vegetables, baked salmon with asparagus, lentil soup.",
                        "tags": ["personal", "cooking", "health"],
                        "pinned": False,
                        "user": "jsmith"
                    }
                },
                "note_counter": 5
            }
        },
        "achang": {
            "first_name": "Alex",
            "last_name": "Chang",
            "email": "alex.chang@noted.com",
            "note_data": {
                "notes": {
                    5: {
                        "id": 5,
                        "title": "Research Paper Outline",
                        "content": "Introduction: Background, Thesis. Body Paragraph 1: Supporting evidence. Body Paragraph 2: Counterarguments. Conclusion: Summary, Future work.",
                        "tags": ["academic", "research", "writing"],
                        "pinned": False,
                        "user": "achang"
                    },
                    6: {
                        "id": 6,
                        "title": "Gym Workout Plan - Week 1",
                        "content": "Monday: Chest/Triceps. Wednesday: Back/Biceps. Friday: Legs/Shoulders. Cardio on rest days.",
                        "tags": ["personal", "fitness", "workout"],
                        "pinned": True,
                        "user": "achang"
                    },
                    7: {
                        "id": 7,
                        "title": "Book Recommendations for Summer",
                        "content": "Dune by Frank Herbert, The Midnight Library by Matt Haig, Project Hail Mary by Andy Weir.",
                        "tags": ["personal", "books", "reading"],
                        "pinned": False,
                        "user": "achang"
                    }
                },
                "note_counter": 8
            }
        },
        "sgupta": {
            "first_name": "Sarah",
            "last_name": "Gupta",
            "email": "sarah.gupta@noted.com",
            "note_data": {
                "notes": {
                    8: {
                        "id": 8,
                        "title": "Client Feedback - Project Alpha",
                        "content": "Client requested changes to UI color scheme and added a new reporting feature. Schedule follow-up meeting.",
                        "tags": ["work", "client", "project"],
                        "pinned": True,
                        "user": "sgupta"
                    },
                    9: {
                        "id": 9,
                        "title": "Vacation Planning - Europe Trip",
                        "content": "Research flights to Paris. Book accommodation in Rome. Plan itinerary for Barcelona.",
                        "tags": ["personal", "travel", "vacation"],
                        "pinned": False,
                        "user": "sgupta"
                    }
                },
                "note_counter": 10
            }
        }
    },
    "global_note_counter": 10
}

class SimpleNoteApis:
    def __init__(self, state: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes the SimpleNoteApis instance and loads the default scenario.
        """
        self.state: Dict[str, Any] = copy.deepcopy(state if state is not None else DEFAULT_STATE)
        self._api_description = "This tool belongs to the SimpleNoteApis, which provides core functionality for note management."

    def _get_user_note_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user-specific note data.

        Args:
            user_id (str): The ID of the user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's note data, or None if not found.
        """
        return self.state["users"].get(user_id, {}).get("note_data")

    def search_notes(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        pinned: Optional[bool] = None,
        page_index: int = 0,
        page_limit: int = 10,
        sort_by: Optional[str] = None,
        user: str = ""
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
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False, "notes": []}

        notes = user_note_data.get("notes", {})
        results = []

        for _, note in notes.items():
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

        return {"status": True, "notes": copy.deepcopy(paginated_results)}

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
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False}

        notes = user_note_data.get("notes", {})
        if note_id not in notes:
            return {"status": False}

        note = notes[note_id]
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
        pinned: bool = False,
        user: str = ""
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
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False}

        notes = user_note_data.get("notes")
        if notes is None:
            return {"status": False}

        # Use the global note counter for unique IDs across all users
        note_id = self.state["global_note_counter"]
        self.state["global_note_counter"] += 1

        new_note = {
            "id": note_id,
            "title": title,
            "content": content,
            "tags": tags or [],
            "pinned": pinned,
            "user": user
        }
        notes[note_id] = new_note
        return {"status": True, "id": note_id}

    def update_note(
        self,
        note_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        pinned: Optional[bool] = None,
        user: str = ""
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
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False}

        notes = user_note_data.get("notes", {})
        if note_id not in notes:
            return {"status": False}

        note = notes[note_id]
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
        user: str = ""
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
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False}

        notes = user_note_data.get("notes", {})
        if note_id not in notes:
            return {"status": False}

        note = notes[note_id]
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
        user_note_data = self._get_user_note_data(user)
        if user_note_data is None:
            return {"status": False}

        notes = user_note_data.get("notes", {})
        if note_id not in notes:
            return {"status": False}

        del notes[note_id]
        return {"status": True}