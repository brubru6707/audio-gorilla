from typing import Dict, List, Any, Literal
from datetime import datetime
import random

DEFAULT_STATE = {
    "users": {},
    "contacts": {},
    "text_messages": {},
    "voice_messages": {},
    "alarms": {},
    "current_user": None,
    "password_reset_codes": {},
    "contact_counter": 0,
    "message_counter": 0,
    "alarm_counter": 0
}

class PhoneApis:
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.contacts: Dict[int, Dict[str, Any]] = {}
        self.text_messages: Dict[int, Dict[str, Any]] = {}
        self.voice_messages: Dict[int, Dict[str, Any]] = {}
        self.alarms: Dict[int, Dict[str, Any]] = {}
        self.current_user: str | None = None
        self.password_reset_codes: Dict[str, str] = {}
        self.contact_counter: int = 0
        self.message_counter: int = 0
        self.alarm_counter: int = 0
        self._api_description = "This tool belongs to the PhoneAPI, which provides core functionality for phone operations including contacts, messaging, and alarms."

    def _load_scenario(self, scenario: dict) -> None:
        """Load a scenario into the PhoneAPI instance."""
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.contacts = scenario.get("contacts", DEFAULT_STATE_COPY["contacts"])
        self.text_messages = scenario.get("text_messages", DEFAULT_STATE_COPY["text_messages"])
        self.voice_messages = scenario.get("voice_messages", DEFAULT_STATE_COPY["voice_messages"])
        self.alarms = scenario.get("alarms", DEFAULT_STATE_COPY["alarms"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.password_reset_codes = scenario.get("password_reset_codes", DEFAULT_STATE_COPY["password_reset_codes"])
        self.contact_counter = scenario.get("contact_counter", DEFAULT_STATE_COPY["contact_counter"])
        self.message_counter = scenario.get("message_counter", DEFAULT_STATE_COPY["message_counter"])
        self.alarm_counter = scenario.get("alarm_counter", DEFAULT_STATE_COPY["alarm_counter"])

    def send_password_reset_code(self, phone_number: str) -> Dict[str, bool]:
        """
        Send a password reset code to the specified phone number.

        Args:
            phone_number (str): Phone number to send the reset code to.

        Returns:
            Dict[str, bool]: Dictionary with send status.
        """
        if phone_number not in self.users:
            return {"send_status": False}
        
        reset_code = str(random.randint(100000, 999999))
        self.password_reset_codes[phone_number] = reset_code
        # In a real implementation, we would send the code via SMS
        return {"send_status": True}

    def reset_password(self, phone_number: str, password_reset_code: str, new_password: str) -> Dict[str, bool]:
        """
        Reset user's password using the reset code.

        Args:
            phone_number (str): User's phone number.
            password_reset_code (str): The reset code received by the user.
            new_password (str): New password to set.

        Returns:
            Dict[str, bool]: Dictionary with reset status.
        """
        if (phone_number not in self.users or 
            phone_number not in self.password_reset_codes or 
            self.password_reset_codes[phone_number] != password_reset_code):
            return {"reset_status": False}
        
        self.users[phone_number]["password"] = new_password
        del self.password_reset_codes[phone_number]
        return {"reset_status": True}

    def show_profile(self, phone_number: str) -> Dict[str, bool]:
        """
        Show user profile for the specified phone number.

        Args:
            phone_number (str): Phone number of the user to show profile for.

        Returns:
            Dict[str, bool]: Dictionary with profile status.
        """
        if phone_number not in self.users:
            return {"profile_status": False}
        return {"profile_status": True}

    def show_account(self, user: str) -> Dict[str, bool]:
        """
        Show account details for the current user.

        Args:
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with account status.
        """
        if self.current_user is None:
            return {"account_status": False}
        return {"account_status": True}

    def update_account_name(self, first_name: str | None, last_name: str | None, user: str) -> Dict[str, bool]:
        """
        Update the account name for the current user.

        Args:
            first_name (str | None): New first name (optional).
            last_name (str | None): New last name (optional).
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with update status.
        """
        if self.current_user is None:
            return {"update_status": False}
        
        if first_name is not None:
            self.users[self.current_user]["first_name"] = first_name
        if last_name is not None:
            self.users[self.current_user]["last_name"] = last_name
            
        return {"update_status": True}

    def delete_account(self, user: str) -> Dict[str, bool]:
        """
        Delete the current user's account.

        Args:
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with deletion status.
        """
        if self.current_user is None:
            return {"deletion_status": False}
        
        del self.users[self.current_user]
        self.current_user = None
        return {"deletion_status": True}

    def show_contact_relationships(self, user: str) -> Dict[str, bool]:
        """
        Show contact relationships for the current user.

        Args:
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with relationships status.
        """
        if self.current_user is None:
            return {"relationships_status": False}
        return {"relationships_status": True}

    def search_contacts(self, query: str, relationship: str, page_index: int, page_limit: int, user: str) -> Dict[str, bool]:
        """
        Search contacts based on query and relationship.

        Args:
            query (str): Search query.
            relationship (str): Relationship filter.
            page_index (int): Pagination index.
            page_limit (int): Number of items per page.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with search status.
        """
        if self.current_user is None:
            return {"search_status": False}
        return {"search_status": True}

    def add_contact(self, first_name: str, last_name: str, phone_number: str, email: str | None, relationships: list[str] | None, birthday: str | None, home_address: str | None, work_address: str | None, user: str) -> Dict[str, bool]:
        """
        Add a new contact for the current user.

        Args:
            first_name (str): Contact's first name.
            last_name (str): Contact's last name.
            phone_number (str): Contact's phone number.
            email (str | None): Contact's email (optional).
            relationships (list[str] | None): List of relationships (optional).
            birthday (str | None): Contact's birthday (optional).
            home_address (str | None): Contact's home address (optional).
            work_address (str | None): Contact's work address (optional).
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with add status.
        """
        if self.current_user is None:
            return {"add_status": False}
        
        contact = {
            "id": self.contact_counter,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "email": email,
            "relationships": relationships or [],
            "birthday": birthday,
            "home_address": home_address,
            "work_address": work_address,
            "owner": self.current_user
        }
        
        self.contacts[self.contact_counter] = contact
        self.users[self.current_user]["contacts"].append(self.contact_counter)
        self.contact_counter += 1
        return {"add_status": True}

    def update_contact(self, contact_id: int, first_name: str | None, last_name: str | None, phone_number: str | None, email: str | None, relationships: list[str] | None, birthday: str | None, home_address: str | None, work_address: str | None, user: str) -> Dict[str, bool]:
        """
        Update an existing contact.

        Args:
            contact_id (int): ID of the contact to update.
            first_name (str | None): New first name (optional).
            last_name (str | None): New last name (optional).
            phone_number (str | None): New phone number (optional).
            email (str | None): New email (optional).
            relationships (list[str] | None): New relationships (optional).
            birthday (str | None): New birthday (optional).
            home_address (str | None): New home address (optional).
            work_address (str | None): New work address (optional).
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with update status.
        """
        if self.current_user is None or contact_id not in self.contacts:
            return {"update_status": False}
            
        contact = self.contacts[contact_id]
        if contact["owner"] != self.current_user:
            return {"update_status": False}
            
        if first_name is not None:
            contact["first_name"] = first_name
        if last_name is not None:
            contact["last_name"] = last_name
        if phone_number is not None:
            contact["phone_number"] = phone_number
        if email is not None:
            contact["email"] = email
        if relationships is not None:
            contact["relationships"] = relationships
        if birthday is not None:
            contact["birthday"] = birthday
        if home_address is not None:
            contact["home_address"] = home_address
        if work_address is not None:
            contact["work_address"] = work_address
            
        return {"update_status": True}

    def delete_contact(self, contact_id: int, user: str) -> Dict[str, bool]:
        """
        Delete a contact.

        Args:
            contact_id (int): ID of the contact to delete.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with deletion status.
        """
        if self.current_user is None or contact_id not in self.contacts:
            return {"deletion_status": False}
            
        contact = self.contacts[contact_id]
        if contact["owner"] != self.current_user:
            return {"deletion_status": False}
            
        del self.contacts[contact_id]
        self.users[self.current_user]["contacts"].remove(contact_id)
        return {"deletion_status": True}

    def show_text_message_window(self, phone_number: str, min_datetime: str, max_datetime: str, pagination_order: Literal["ascending", "descending"], page_index: int, page_limit: int, user: str) -> Dict[str, bool]:
        """
        Show text messages within a time window.

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

    def search_text_messages(self, query: str, phone_number: str | None, only_latest_per_contact: bool, page_index: int, page_limit: int, sort_by: str | None, user: str) -> Dict[str, bool]:
        """
        Search text messages.

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

    def show_text_message(self, text_message_id: int, user: str) -> Dict[str, bool]:
        """
        Show a specific text message.

        Args:
            text_message_id (int): ID of the text message.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with message status.
        """
        if self.current_user is None or text_message_id not in self.text_messages:
            return {"message_status": False}
        return {"message_status": True}

    def send_text_message(self, phone_number: str, message: str, user: str) -> Dict[str, bool]:
        """
        Send a text message.

        Args:
            phone_number (str): Recipient's phone number.
            message (str): Message content.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with send status.
        """
        if self.current_user is None:
            return {"send_status": False}
            
        text_message = {
            "id": self.message_counter,
            "sender": self.current_user,
            "recipient": phone_number,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        
        self.text_messages[self.message_counter] = text_message
        self.message_counter += 1
        return {"send_status": True}

    def delete_text_message(self, text_message_id: int, user: str) -> Dict[str, bool]:
        """
        Delete a text message.

        Args:
            text_message_id (int): ID of the message to delete.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with deletion status.
        """
        if self.current_user is None or text_message_id not in self.text_messages:
            return {"deletion_status": False}
            
        message = self.text_messages[text_message_id]
        if message["sender"] != self.current_user and message["recipient"] != self.current_user:
            return {"deletion_status": False}
            
        del self.text_messages[text_message_id]
        return {"deletion_status": True}

    def show_alarms(self, page_index: int, page_limit: int, user: str) -> Dict[str, bool]:
        """
        Show alarms for the current user.

        Args:
            page_index (int): Pagination index.
            page_limit (int): Number of items per page.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with alarms status.
        """
        if self.current_user is None:
            return {"alarms_status": False}
        return {"alarms_status": True}

    def show_alarm(self, alarm_id: int, user: str) -> Dict[str, bool]:
        """
        Show a specific alarm.

        Args:
            alarm_id (int): ID of the alarm.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with alarm status.
        """
        if self.current_user is None or alarm_id not in self.alarms:
            return {"alarm_status": False}
        return {"alarm_status": True}

    def create_alarm(self, time: str, repeat_days: list[Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]] | None, label: str | None, enabled: bool, snooze_minutes: int, vibration: bool, user: str) -> Dict[str, bool]:
        """
        Create a new alarm.

        Args:
            time (str): Alarm time.
            repeat_days (list[Literal] | None): Days to repeat (optional).
            label (str | None): Alarm label (optional).
            enabled (bool): Whether alarm is enabled.
            snooze_minutes (int): Snooze duration in minutes.
            vibration (bool): Whether vibration is enabled.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with creation status.
        """
        if self.current_user is None:
            return {"creation_status": False}
            
        alarm = {
            "id": self.alarm_counter,
            "time": time,
            "repeat_days": repeat_days or [],
            "label": label,
            "enabled": enabled,
            "snooze_minutes": snooze_minutes,
            "vibration": vibration,
            "owner": self.current_user
        }
        
        self.alarms[self.alarm_counter] = alarm
        self.users[self.current_user]["alarms"].append(self.alarm_counter)
        self.alarm_counter += 1
        return {"creation_status": True}

    def update_alarm(self, alarm_id: int, time: str | None, repeat_days: list[Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]] | None, label: str | None, enabled: bool | None, snooze_minutes: int | None, vibration: bool | None, user: str) -> Dict[str, bool]:
        """
        Update an existing alarm.

        Args:
            alarm_id (int): ID of the alarm to update.
            time (str | None): New time (optional).
            repeat_days (list[Literal] | None): New repeat days (optional).
            label (str | None): New label (optional).
            enabled (bool | None): New enabled status (optional).
            snooze_minutes (int | None): New snooze duration (optional).
            vibration (bool | None): New vibration status (optional).
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with update status.
        """
        if self.current_user is None or alarm_id not in self.alarms:
            return {"update_status": False}
            
        alarm = self.alarms[alarm_id]
        if alarm["owner"] != self.current_user:
            return {"update_status": False}
            
        if time is not None:
            alarm["time"] = time
        if repeat_days is not None:
            alarm["repeat_days"] = repeat_days
        if label is not None:
            alarm["label"] = label
        if enabled is not None:
            alarm["enabled"] = enabled
        if snooze_minutes is not None:
            alarm["snooze_minutes"] = snooze_minutes
        if vibration is not None:
            alarm["vibration"] = vibration
            
        return {"update_status": True}

    def delete_alarm(self, alarm_id: int, user: str) -> Dict[str, bool]:
        """
        Delete an alarm.

        Args:
            alarm_id (int): ID of the alarm to delete.
            user (str): The current user object.

        Returns:
            Dict[str, bool]: Dictionary with deletion status.
        """
        if self.current_user is None or alarm_id not in self.alarms:
            return {"deletion_status": False}
            
        alarm = self.alarms[alarm_id]
        if alarm["owner"] != self.current_user:
            return {"deletion_status": False}
            
        del self.alarms[alarm_id]
        self.users[self.current_user]["alarms"].remove(alarm_id)
        return {"deletion_status": True}

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