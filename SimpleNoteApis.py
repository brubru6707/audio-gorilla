from typing import Dict, Union, Literal

class SimpleNoteApis:
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
        ...
    # def login(
    #     self,
    #     data: OAuth2PasswordRequestForm,
    # ) -> Dict[str, Union[bool, str]]:
    #     """
    #     Log in a user with email and password.

    #     Args:
    #         data (OAuth2PasswordRequestForm): Form containing username (email) and password.

    #     Returns:
    #         Dict[str, Union[bool, str]]: Dictionary with login status and access token if successful.
    #     """
    #     ...
    # def logout(
    #     self,
    #     request: Request,
    # ) -> Dict[str, bool]:
    #     """
    #     Log out the current user.

    #     Args:
    #         request (Request): The request object.

    #     Returns:
    #         Dict[str, bool]: Dictionary with logout status.
    #     """
    #     ...
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
        ...
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
        ...
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
        ...
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
        ...
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
        ...
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
        ...
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
        ...
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
        ...
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
        ...
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
        ...
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
        ...
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
        ...
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
        ...
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
        ...