from typing import Dict, List, Any, Literal
from datetime import datetime
from copy import deepcopy
import random

DEFAULT_STATE = {
    "users": {},
    "voice_messages": {},
    "current_user": None,
    "password_reset_codes": {},
    "message_counter": 0
}

class PhoneApis:
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.voice_messages: Dict[int, Dict[str, Any]] = {}
        self.current_user: str | None = None
        self.password_reset_codes: Dict[str, str] = {}
        self.message_counter: int = 0
        self._api_description = "This tool belongs to the PhoneAPI, which provides core functionality for voice message operations."

    def _load_scenario(self, scenario: dict) -> None:
        """Load a scenario into the PhoneAPI instance."""
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.voice_messages = scenario.get("voice_messages", DEFAULT_STATE_COPY["voice_messages"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.password_reset_codes = scenario.get("password_reset_codes", DEFAULT_STATE_COPY["password_reset_codes"])
        self.message_counter = scenario.get("message_counter", DEFAULT_STATE_COPY["message_counter"])

    def show_voice_message_window(self, phone_number: str, min_datetime: str, max_datetime: str, pagination_order: Literal["ascending", "descending"], page_index: int, page_limit: int, user: str) -> Dict[str, bool]:
        """
        Show voice messages within a time window.

        Args:
            phone_number (str): Contact's phone number.
            min_datetime (str): Minimum datetime for messages.
            max_datetime (str): Maximum datetime for messages.
            pagination_order (Literal["ascending", "descending"]): Order of messages.
            page_index (int): Pagination index.
            page_limit (int): Number of items per page.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with messages status.
        """
        if self.current_user is None:
            return {"messages_status": False}
        return {"messages_status": True}

    def search_voice_messages(self, query: str, phone_number: str | None, only_latest_per_contact: bool, page_index: int, page_limit: int, sort_by: str | None, user: str) -> Dict[str, bool]:
        """
        Search voice messages.

        Args:
            query (str): Search query.
            phone_number (str | None): Filter by phone number (optional).
            only_latest_per_contact (bool): Return only latest per contact.
            page_index (int): Pagination index.
            page_limit (int): Number of items per page.
            sort_by (str | None): Sort field (optional).
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with search status.
        """
        if self.current_user is None:
            return {"search_status": False}
        return {"search_status": True}

    def show_voice_message(self, voice_message_id: int, user: str) -> Dict[str, bool]:
        """
        Show a specific voice message.

        Args:
            voice_message_id (int): ID of the voice message.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with message status.
        """
        if self.current_user is None or voice_message_id not in self.voice_messages:
            return {"message_status": False}
        return {"message_status": True}

    def send_voice_message(self, phone_number: str, message: str, user: str) -> Dict[str, bool]:
        """
        Send a voice message.

        Args:
            phone_number (str): Recipient's phone number.
            message (str): Message content.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with send status.
        """
        if self.current_user is None:
            return {"send_status": False}
            
        voice_message = {
            "id": self.message_counter,
            "sender": self.current_user,
            "recipient": phone_number,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "played": False
        }
        
        self.voice_messages[self.message_counter] = voice_message
        self.message_counter += 1
        return {"send_status": True}

    def delete_voice_message(self, voice_message_id: int, user: str) -> Dict[str, bool]:
        """
        Delete a voice message.

        Args:
            voice_message_id (int): ID of the message to delete.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with deletion status.
        """
        if self.current_user is None or voice_message_id not in self.voice_messages:
            return {"deletion_status": False}
            
        message = self.voice_messages[voice_message_id]
        if message["sender"] != self.current_user and message["recipient"] != self.current_user:
            return {"deletion_status": False}
            
        del self.voice_messages[voice_message_id]
        return {"deletion_status": True}

    def get_current_date_and_time(self) -> Dict[str, bool]:
        """
        Get the current date and time.

        Returns:
            Dict[str, bool]: Dictionary with datetime status.
        """
        return {"datetime_status": True}