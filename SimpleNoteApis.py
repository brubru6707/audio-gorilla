from typing import Dict, Union, Literal, List
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm

DEFAULT_STATE = {
    "users": {},
    "notes": {},
    "note_counter": 0,
    "verification_codes": {},
    "reset_codes": {},
    "sessions": {}
}

class SimpleNoteApis:
    def __init__(self):
        self.users: Dict[str, Dict] = DEFAULT_STATE["users"]  # email -> user data
        self.notes: Dict[int, Dict] = DEFAULT_STATE["notes"]  # note_id -> note data
        self.note_counter: int = DEFAULT_STATE["note_counter"]
        self.verification_codes: Dict[str, str] = DEFAULT_STATE["verification_codes"]  # email -> code
        self.reset_codes: Dict[str, str] = DEFAULT_STATE["reset_codes"]  # email -> code
        self.sessions: Dict[str, str] = DEFAULT_STATE["sessions"]  # token -> email

    def signup(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
    ) -> Dict[str, bool]:
        """
        Sign up a new user with first name, last name, email and password.

        Args:
            first_name (str): First name of the user.
            last_name (str): Last name of the user.
            email (str): Email of the user.
            password (str): Password of the user.

        Returns:
            Dict[str, bool]: Dictionary with signup status.
        """
        if email in self.users:
            return {"status": False}
        
        self.users[email] = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "verified": False
        }
        return {"status": True}

    def login(
        self,
        data: OAuth2PasswordRequestForm,
    ) -> Dict[str, Union[bool, str]]:
        """
        Log in a user with email and password.

        Args:
            data (OAuth2PasswordRequestForm): Form containing username (email) and password.

        Returns:
            Dict[str, Union[bool, str]]: Dictionary with login status and access token if successful.
        """
        email = data.username
        password = data.password
        
        if email not in self.users or self.users[email]["password"] != password:
            return {"status": False, "token": ""}
        
        if not self.users[email]["verified"]:
            return {"status": False, "token": ""}
        
        token = f"token_{email}_{len(self.sessions)}"
        self.sessions[token] = email
        return {"status": True, "token": token}

    def logout(
        self,
        request: Request,
    ) -> Dict[str, bool]:
        """
        Log out the current user.

        Args:
            request (Request): The request object.

        Returns:
            Dict[str, bool]: Dictionary with logout status.
        """
        token = request.headers.get("authorization", "").replace("Bearer ", "")
        if token in self.sessions:
            del self.sessions[token]
            return {"status": True}
        return {"status": False}

    def send_verification_code(
        self,
        email: str,
    ) -> Dict[str, bool]:
        """
        Send a verification code to the user's email.

        Args:
            email (str): Email of the user.

        Returns:
            Dict[str, bool]: Dictionary with send status.
        """
        if email not in self.users:
            return {"status": False}
        
        code = str(hash(email))[-6:]
        self.verification_codes[email] = code
        # In a real implementation, we would send the code via email here
        return {"status": True}

    def verify_account(
        self,
        email: str,
        verification_code: str,
    ) -> Dict[str, bool]:
        """
        Verify user's account with the verification code.

        Args:
            email (str): Email of the user.
            verification_code (str): Verification code sent to the user.

        Returns:
            Dict[str, bool]: Dictionary with verification status.
        """
        if email not in self.users or email not in self.verification_codes:
            return {"status": False}
        
        if self.verification_codes[email] == verification_code:
            self.users[email]["verified"] = True
            del self.verification_codes[email]
            return {"status": True}
        return {"status": False}

    def send_password_reset_code(
        self,
        email: str,
    ) -> Dict[str, bool]:
        """
        Send a password reset code to the user's email.

        Args:
            email (str): Email of the user.

        Returns:
            Dict[str, bool]: Dictionary with send status.
        """
        if email not in self.users:
            return {"status": False}
        
        code = str(hash(email + "reset"))[-6:]
        self.reset_codes[email] = code
        # In a real implementation, we would send the code via email here
        return {"status": True}

    def reset_password(
        self,
        email: str,
        password_reset_code: str,
        new_password: str,
    ) -> Dict[str, bool]:
        """
        Reset user's password with the reset code.

        Args:
            email (str): Email of the user.
            password_reset_code (str): Password reset code sent to the user.
            new_password (str): New password for the user.

        Returns:
            Dict[str, bool]: Dictionary with reset status.
        """
        if email not in self.users or email not in self.reset_codes:
            return {"status": False}
        
        if self.reset_codes[email] == password_reset_code:
            self.users[email]["password"] = new_password
            del self.reset_codes[email]
            return {"status": True}
        return {"status": False}

    def show_profile(
        self,
        email: str,
    ) -> Dict[str, Union[str, bool]]:
        """
        Show user's profile information.

        Args:
            email (str): Email of the user.

        Returns:
            Dict[str, Union[str, bool]]: Dictionary with user's profile information.
        """
        if email not in self.users:
            return {"status": False}
        
        user = self.users[email]
        return {
            "status": True,
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"]
        }

    def show_account(
        self,
        user: str,
    ) -> Dict[str, Union[str, bool]]:
        """
        Show detailed account information.

        Args:
            user (User): The user object.

        Returns:
            Dict[str, Union[str, bool]]: Dictionary with account information.
        """
        email = user  # Assuming 'user' is the email in this simplified version
        if email not in self.users:
            return {"status": False}
        
        user_data = self.users[email]
        return {
            "status": True,
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "email": user_data["email"],
            "verified": user_data["verified"]
        }

    def update_account_name(
        self,
        first_name: str | None,
        last_name: str | None,
        user: str,
    ) -> Dict[str, bool]:
        """
        Update user's first and/or last name.

        Args:
            first_name (str | None): New first name (optional).
            last_name (str | None): New last name (optional).
            user (User): The user object.

        Returns:
            Dict[str, bool]: Dictionary with update status.
        """
        email = user  # Assuming 'user' is the email in this simplified version
        if email not in self.users:
            return {"status": False}
        
        if first_name is not None:
            self.users[email]["first_name"] = first_name
        if last_name is not None:
            self.users[email]["last_name"] = last_name
            
        return {"status": True}

    def delete_account(
        self,
        user: str,
    ) -> Dict[str, bool]:
        """
        Delete user's account.

        Args:
            user (User): The user object.

        Returns:
            Dict[str, bool]: Dictionary with deletion status.
        """
        email = user  # Assuming 'user' is the email in this simplified version
        if email not in self.users:
            return {"status": False}
        
        # Delete all user's notes
        notes_to_delete = [note_id for note_id, note in self.notes.items() if note["user"] == email]
        for note_id in notes_to_delete:
            del self.notes[note_id]
            
        del self.users[email]
        return {"status": True}

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
            user (User): The user object.

        Returns:
            Dict[str, Union[bool, list]]: Dictionary with search results.
        """
        email = user  # Assuming 'user' is the email in this simplified version
        results = []
        
        for note_id, note in self.notes.items():
            if note["user"] != email:
                continue
                
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
    ) -> Dict[str, Union[bool, str, list]]:
        """
        Show details of a specific note.

        Args:
            note_id (int): ID of the note.
            user (User): The user object.

        Returns:
            Dict[str, Union[bool, str, list]]: Dictionary with note details.
        """
        email = user  # Assuming 'user' is the email in this simplified version
        if note_id not in self.notes or self.notes[note_id]["user"] != email:
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
            user (User): The user object.

        Returns:
            Dict[str, Union[bool, int]]: Dictionary with creation status and note ID.
        """
        email = user  # Assuming 'user' is the email in this simplified version
        if email not in self.users:
            return {"status": False, "id": -1}
        
        note_id = self.note_counter
        self.notes[note_id] = {
            "id": note_id,
            "title": title,
            "content": content,
            "tags": tags or [],
            "pinned": pinned,
            "user": email
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
            user (User): The user object.

        Returns:
            Dict[str, bool]: Dictionary with update status.
        """
        email = user  # Assuming 'user' is the email in this simplified version
        if note_id not in self.notes or self.notes[note_id]["user"] != email:
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
            user (User): The user object.

        Returns:
            Dict[str, bool]: Dictionary with update status.
        """
        email = user  # Assuming 'user' is the email in this simplified version
        if note_id not in self.notes or self.notes[note_id]["user"] != email:
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
            user (User): The user object.

        Returns:
            Dict[str, bool]: Dictionary with deletion status.
        """
        email = user  # Assuming 'user' is the email in this simplified version
        if note_id not in self.notes or self.notes[note_id]["user"] != email:
            return {"status": False}
        
        del self.notes[note_id]
        return {"status": True}