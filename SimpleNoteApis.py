from typing import Dict, Union, Literal, List

DEFAULT_STATE = {
    "notes": {},
    "note_counter": 0
}

class SimpleNoteApis:
    def __init__(self):
        self.notes: Dict[int, Dict] = DEFAULT_STATE["notes"]  # note_id -> note data
        self.note_counter: int = DEFAULT_STATE["note_counter"]
        self._api_description = "This tool belongs to the SimpleNoteApis, which provides core functionality for note management."

    def search_notes(
        self,
        query: str,
        tags: list[str] | None,
        pinned: bool | None,
        dont_reorder_pinned: bool,
        page_index: int,
        page_limit: int,
        sort_by: str | None,
        user: str,
    ) -> Dict[str, Union[bool, list]]:
        """
        Search for notes based on various criteria.

        Args:
            query (str): Search query string.
            tags (list[str] | None): List of tags to filter by.
            pinned (bool | None): Filter by pinned status.
            dont_reorder_pinned (bool): Whether to keep pinned notes at top.
            page_index (int): Pagination page index.
            page_limit (int): Number of items per page.
            sort_by (str | None): Field to sort by.
            user (str): The user identifier.

        Returns:
            Dict[str, Union[bool, list]]: Dictionary with search results.
        """
        results = []
        
        for note_id, note in self.notes.items():
            matches_query = query.lower() in note["title"].lower() or query.lower() in note["content"].lower()
            matches_tags = tags is None or all(tag in note["tags"] for tag in tags)
            matches_pinned = pinned is None or note["pinned"] == pinned
            
            if matches_query and matches_tags and matches_pinned:
                results.append(note)
        
        # Simple sorting (in a real implementation, we'd have more sophisticated sorting)
        if sort_by == "title":
            results.sort(key=lambda x: x["title"])
        elif sort_by == "date":
            results.sort(key=lambda x: x["id"])  # Using ID as proxy for creation date
            
        # Simple pagination
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
            note_id (int): ID of the note.
            user (str): The user identifier.

        Returns:
            Dict[str, Union[bool, str, list]]: Dictionary with note details.
        """
        if note_id not in self.notes:
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
        tags: list[str] | None,
        pinned: bool,
        user: str,
    ) -> Dict[str, Union[bool, int]]:
        """
        Create a new note.

        Args:
            title (str): Title of the note.
            content (str): Content of the note.
            tags (list[str] | None): List of tags for the note.
            pinned (bool): Whether the note should be pinned.
            user (str): The user identifier.

        Returns:
            Dict[str, Union[bool, int]]: Dictionary with creation status and note ID.
        """
        note_id = self.note_counter
        self.notes[note_id] = {
            "id": note_id,
            "title": title,
            "content": content,
            "tags": tags or [],
            "pinned": pinned,
            "user": user
        }
        self.note_counter += 1
        return {"status": True, "id": note_id}

    def update_note(
        self,
        note_id: int,
        title: str | None,
        content: str | None,
        tags: list[str] | None,
        pinned: bool | None,
        user: str,
    ) -> Dict[str, bool]:
        """
        Update an existing note.

        Args:
            note_id (int): ID of the note to update.
            title (str | None): New title (optional).
            content (str | None): New content (optional).
            tags (list[str] | None): New tags (optional).
            pinned (bool | None): New pinned status (optional).
            user (str): The user identifier.

        Returns:
            Dict[str, bool]: Dictionary with update status.
        """
        if note_id not in self.notes:
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
        user: str,
    ) -> Dict[str, bool]:
        """
        Add content to an existing note.

        Args:
            note_id (int): ID of the note.
            append_or_prepend (Literal["append", "prepend"]): Where to add the content.
            added_content (str): Content to add.
            user (str): The user identifier.

        Returns:
            Dict[str, bool]: Dictionary with update status.
        """
        if note_id not in self.notes:
            return {"status": False}
        
        note = self.notes[note_id]
        if append_or_prepend == "append":
            note["content"] += "\n" + added_content
        else:
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
            user (str): The user identifier.

        Returns:
            Dict[str, bool]: Dictionary with deletion status.
        """
        if note_id not in self.notes:
            return {"status": False}
        
        del self.notes[note_id]
        return {"status": True}