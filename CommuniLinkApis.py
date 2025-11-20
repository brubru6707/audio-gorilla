"""
Inspired by https://appworld.dev/

Uses stateful design
"""
import time
import random
import uuid
from copy import deepcopy
from typing import Dict, List, Optional, Union
from datetime import datetime
from state_loader import load_default_state

DEFAULT_COMMUNILINK_STATE = load_default_state("CommuniLinkApis")

class CommuniLinkApis:
    """
    An API class for CommuniLink, simulating SMS messaging and voice calling
    functionality.
    """
    def __init__(self):
        """
        Initializes the CommuniLinkApis instance, setting up the in-memory
        data stores for SMS messages and voice calls, and loading the default
        scenario.
        """
        self.users: Dict = {}
        self.current_user_id: Optional[str] = None
        self.billing_history: List[Dict] = []
        self.support_tickets: List[Dict] = []
        self.service_plans: Dict = {}
        self.active_plan: str = ""
        self.network_status: str = ""
        self._api_description = "This tool belongs to the CommuniLink API, which provides core functionality for SMS messaging and voice calls."
        self._load_scenario(DEFAULT_COMMUNILINK_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain keys like "users", "current_user_id", etc.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_COMMUNILINK_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.current_user_id = scenario.get("current_user_id", DEFAULT_STATE_COPY["current_user_id"])
        self.billing_history = scenario.get("billing_history", DEFAULT_STATE_COPY["billing_history"])
        self.support_tickets = scenario.get("support_tickets", DEFAULT_STATE_COPY["support_tickets"])
        self.service_plans = scenario.get("service_plans", DEFAULT_STATE_COPY["service_plans"])
        self.active_plan = scenario.get("active_plan", DEFAULT_STATE_COPY["active_plan"])
        self.network_status = scenario.get("network_status", DEFAULT_STATE_COPY["network_status"])

        print(f"CommuniLinkApis: Loaded scenario. Current User ID: {self.current_user_id}")

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """Helper to get user_id from email."""
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """Helper to get user email from user_id."""
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _get_user_id_by_phone(self, phone_number: str) -> Optional[str]:
        """Helper to get user_id from phone number."""
        for user_id, user_data in self.users.items():
            if user_data.get("phone_number") == phone_number:
                return user_id
        return None

    def _get_user_phone_by_id(self, user_id: str) -> Optional[str]:
        """Helper to get phone number from user_id."""
        user_data = self.users.get(user_id)
        return user_data.get("phone_number") if user_data else None

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for entities.
        """
        return str(uuid.uuid4())

    def _require_login(self) -> Optional[Dict[str, Union[bool, str]]]:
        """Check if user is logged in. Returns error dict if not logged in, None if logged in."""
        if not self.current_user_id:
            return {"status": False, "message": "User must be logged in to perform this action."}
        if self.current_user_id not in self.users:
            self.current_user_id = None
            return {"status": False, "message": "Invalid session. Please log in again."}
        return None

    def _get_current_user_id(self) -> Optional[str]:
        """Get the current logged-in user's ID."""
        return self.current_user_id

    def _get_current_user_data(self) -> Optional[Dict]:
        """Get the current logged-in user's data."""
        if not self.current_user_id:
            return None
        return self.users.get(self.current_user_id)

    def _get_current_user_phone(self) -> Optional[str]:
        """Get the current logged-in user's phone number."""
        user_data = self._get_current_user_data()
        return user_data.get("phone_number") if user_data else None

    def login_user(self, email: str, password: str) -> Dict[str, Union[bool, str]]:
        """
        Authenticates a user and creates a session.
        
        Args:
            email (str): The user's email address.
            password (str): The user's password.
        
        Returns:
            Dict: Success status and message, along with user info if successful.
        """
        user_id = self._get_user_id_by_email(email)
        if not user_id:
            return {"login_status": False, "message": "Invalid email or password."}
        
        user_data = self.users[user_id]
        # Simple password verification (in production, use proper hashing)
        password_hash = str(hash(password))[-48:]  # Match hash format
        if user_data.get("password_hash") != password_hash:
            return {"login_status": False, "message": "Invalid email or password."}
        
        self.current_user_id = user_id
        print(f"CommuniLinkApis: User logged in - {email}")
        
        return {
            "login_status": True,
            "message": "Login successful.",
            "user_id": user_id,
            "phone_number": user_data.get("phone_number")
        }

    def logout_user(self) -> Dict[str, Union[bool, str]]:
        """
        Logs out the current user by clearing the session.
        
        Returns:
            Dict: Success status and message.
        """
        if not self.current_user_id:
            return {"logout_status": False, "message": "No user is currently logged in."}
        
        print(f"CommuniLinkApis: User logged out - {self._get_user_email_by_id(self.current_user_id)}")
        self.current_user_id = None
        
        return {"logout_status": True, "message": "Logout successful."}

    def register_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        phone_number: str
    ) -> Dict[str, Union[bool, str]]:
        """
        Registers a new user and creates their account.
        
        Args:
            first_name (str): User's first name.
            last_name (str): User's last name.
            email (str): User's email address.
            password (str): User's password.
            phone_number (str): User's phone number in E.164 format.
        
        Returns:
            Dict: Success status, message, and user_id if successful.
        """
        # Check if email already exists
        if self._get_user_id_by_email(email):
            return {"register_status": False, "message": "Email already registered."}
        
        # Check if phone number already exists
        if self._get_user_id_by_phone(phone_number):
            return {"register_status": False, "message": "Phone number already registered."}
        
        # Create new user
        new_user_id = self._generate_unique_id()
        password_hash = str(hash(password))[-48:]  # Simple hash (in production, use proper hashing)
        
        self.users[new_user_id] = {
            "user_id": new_user_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone_number,
            "password_hash": password_hash,
            "balance": 0.0,
            "sms_history": [],
            "call_history": [],
            "friends": [],
            "settings": {
                "sms_notifications": True,
                "call_notifications": True,
                "voicemail_enabled": True
            }
        }
        
        print(f"CommuniLinkApis: New user registered - {email}")
        
        return {
            "register_status": True,
            "message": "Registration successful.",
            "user_id": new_user_id
        }

    def send_sms(
        self, 
        to_number: str, 
        message: str,
        priority: str = "normal",
        delivery_receipt: bool = True,
        schedule_time: Optional[str] = None,
        max_retries: int = 3,
        message_type: str = "text"
    ) -> Dict[str, Union[str, int]]:
        """
        Sends an SMS message from the currently logged-in user to the specified recipient.
        
        Args:
            to_number (str): The recipient's phone number (E.164 format, e.g., "+15559876543").
            message (str): The text content of the SMS.
            priority (str): Message priority level - "low", "normal", or "high". Default is "normal".
            delivery_receipt (bool): Whether to request a delivery receipt. Default is True.
            schedule_time (Optional[str]): ISO timestamp to schedule message for future delivery. Default is None (send immediately).
            max_retries (int): Maximum number of retry attempts if delivery fails. Default is 3.
            message_type (str): Type of message - "text", "marketing", or "transactional". Default is "text".
        
        Returns:
            Dict: A dictionary representing the simulated SMS message object,
                  including 'id', 'from', 'to', 'message', 'status', and 'timestamp'.
                  Returns an error dictionary if user not logged in or parameters invalid.
        """
        login_check = self._require_login()
        if login_check:
            return {"code": "NOT_AUTHENTICATED", "message": login_check["message"]}
        
        if not to_number or not message:
            return {"code": "MISSING_PARAMS", "message": "Missing required parameters: to_number and message."}
        
        # Validate priority
        if priority not in ["low", "normal", "high"]:
            return {"code": "INVALID_PRIORITY", "message": "Priority must be 'low', 'normal', or 'high'."}
        
        # Validate message_type
        if message_type not in ["text", "marketing", "transactional"]:
            return {"code": "INVALID_MESSAGE_TYPE", "message": "Message type must be 'text', 'marketing', or 'transactional'."}
        
        sender_user_id = self._get_current_user_id()
        sender_user = self._get_current_user_data()
        from_number = self._get_current_user_phone()

        # Apply priority-based cost multiplier
        cost_multiplier = {"low": 0.8, "normal": 1.0, "high": 1.5}
        sms_cost = self.service_plans[self.active_plan]["price_per_sms"] * cost_multiplier[priority]
        
        if sender_user["balance"] < sms_cost:
            return {"code": "INSUFFICIENT_BALANCE", "message": "Insufficient balance to send SMS."}
        
        sender_user["balance"] -= sms_cost
        self.billing_history.append({
            "transaction_id": self._generate_unique_id(),
            "type": "sms_charge",
            "user_id": sender_user_id,
            "amount": -sms_cost,
            "date": datetime.now().isoformat(),
            "description": f"SMS to {to_number} (priority: {priority}, type: {message_type})"
        })
        new_sms_id = self._generate_unique_id()
        new_sms = {
            "sms_id": new_sms_id,
            "sender": from_number,
            "sender_id": sender_user_id,
            "receiver": to_number,
            "message": message,
            "status": "queued" if not schedule_time else "scheduled", 
            # ^ can't necessarily queue for actual phones, but can for APIs
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "delivery_receipt": delivery_receipt,
            "schedule_time": schedule_time,
            "max_retries": max_retries,
            "message_type": message_type,
            "retry_count": 0
        }
        
        receiver_user_id = self._get_user_id_by_phone(to_number)
        is_external = receiver_user_id is None # potentially sends to a 'none' external user
        new_sms["is_external"] = is_external

        sender_user["sms_history"].append(new_sms)
        if receiver_user_id:
            receiver_user = self.users[receiver_user_id]
            receiver_user["sms_history"].append(new_sms)
            print(f"SMS queued: ID={new_sms['sms_id']} from {sender_user['email']} to {receiver_user['email']} (priority: {priority})")
        else:
            print(f"SMS queued: ID={new_sms['sms_id']} from {sender_user['email']} to external number {to_number} (priority: {priority})")

        # If scheduled, don't progress status yet
        if schedule_time:
            print(f"SMS ID={new_sms['sms_id']} scheduled for {schedule_time}")
            return {
                "id": new_sms["sms_id"],
                "from": new_sms["sender"],
                "to": new_sms["receiver"],
                "message": new_sms["message"],
                "status": new_sms["status"],
                "timestamp": new_sms["timestamp"],
                "schedule_time": schedule_time,
                "priority": priority
            }
        # simulate status progression
        # time.sleep(0.1)
        # new_sms["status"] = "sent"
        # time.sleep(0.2)
        new_sms["status"] = "delivered"
        print(f"SMS ID={new_sms['sms_id']} status updated to 'delivered'")

        return {
            "id": new_sms["sms_id"],
            "from": new_sms["sender"],
            "to": new_sms["receiver"],
            "message": new_sms["message"],
            "status": new_sms["status"],
            "timestamp": new_sms["timestamp"],
            "priority": priority,
            "delivery_receipt": delivery_receipt
        }

    def get_sms_status(self, message_id: str) -> Dict[str, Union[str, int]]:
        """
        Retrieves the current status of a previously sent SMS message.
        Args:
            message_id (str): The unique ID of the SMS message to check.
        Returns:
            Dict: A dictionary representing the SMS message object if found,
                  or an error dictionary if not found.
        """
        # simulate status progression
        # time.sleep(0.05)
        sms = None
        for user_data in self.users.values():
            sms = next((msg for msg in user_data["sms_history"] if msg["sms_id"] == message_id), None)
            if sms:
                break
        if not sms:
            return {"code": "SMS_NOT_FOUND", "message": f"SMS message with ID '{message_id}' not found."}
        print(f"SMS status retrieved for ID={message_id}: {sms['status']}")
        return {
            "id": sms["sms_id"],
            "from": sms["sender"],
            "to": sms["receiver"],
            "message": sms["message"],
            "status": sms["status"],
            "timestamp": sms["timestamp"]
        }

    def make_voice_call(
        self, 
        to_number: str,
        call_type: str = "voice",
        recording_enabled: bool = False,
        caller_id_display: bool = True,
        call_forwarding: Optional[str] = None,
        voicemail_enabled: bool = True,
        call_quality: str = "standard"
    ) -> Dict[str, Union[str, int, float]]:
        """
        Initiates an outbound voice call from the currently logged-in user.
        
        Args:
            to_number (str): The recipient's phone number (E.164 format).
            call_type (str): Type of call - "voice", "video", or "conference". Default is "voice".
            recording_enabled (bool): Whether to record the call. Default is False.
            caller_id_display (bool): Whether to display caller ID to recipient. Default is True.
            call_forwarding (Optional[str]): Phone number to forward call to if unanswered. Default is None.
            voicemail_enabled (bool): Whether voicemail is available if unanswered. Default is True.
            call_quality (str): Call quality setting - "standard", "hd", or "premium". Default is "standard".

        Returns:
            Dict: A dictionary representing the simulated voice call object,
                  including 'id', 'from', 'to', 'status', 'timestamp',
                  and 'duration' (if completed). Returns an error dictionary
                  if user not logged in or parameters invalid.
        """
        login_check = self._require_login()
        if login_check:
            return {"code": "NOT_AUTHENTICATED", "message": login_check["message"]}
        
        if not to_number:
            return {"code": "MISSING_PARAMS", "message": "Missing required parameter: to_number."}

        # Validate call_type
        if call_type not in ["voice", "video", "conference"]:
            return {"code": "INVALID_CALL_TYPE", "message": "Call type must be 'voice', 'video', or 'conference'."}
        
        # Validate call_quality
        if call_quality not in ["standard", "hd", "premium"]:
            return {"code": "INVALID_CALL_QUALITY", "message": "Call quality must be 'standard', 'hd', or 'premium'."}

        caller_user_id = self._get_current_user_id()
        caller_user = self._get_current_user_data()
        from_number = self._get_current_user_phone()

        new_call_id = self._generate_unique_id()
        new_call = {
            "call_id": new_call_id,
            "caller_id": caller_user_id,
            "caller": from_number,
            "receiver": to_number,
            "duration_minutes": random.randint(1, 59),
            "status": "initiated",
            "timestamp": datetime.now().isoformat(),
            "type": call_type,
            "is_external": False,
            "recording_enabled": recording_enabled,
            "caller_id_display": caller_id_display,
            "call_forwarding": call_forwarding,
            "voicemail_enabled": voicemail_enabled,
            "call_quality": call_quality
        }
        
        receiver_user_id = self._get_user_id_by_phone(to_number)
        is_external = receiver_user_id is None
        new_call["is_external"] = is_external

        caller_user["call_history"].append(new_call)
        if receiver_user_id:
            receiver_user = self.users[receiver_user_id]
            receiver_user["call_history"].append(new_call)
            print(f"Call initiated: ID={new_call['call_id']} from {caller_user['email']} to {receiver_user['email']}")
        else:
            print(f"Call initiated: ID={new_call['call_id']} from {caller_user['email']} to external number {to_number}")

        # time.sleep(0.15)
        # new_call["status"] = "ringing"
        # time.sleep(0.5)
        new_call["status"] = "in-progress"
        
        call_duration_ = round(random.uniform(30, 120))
        # time.sleep(min(call_duration_ / 10, 2))

        new_call["duration"] = call_duration_

        # Apply quality-based cost multiplier
        quality_multiplier = {"standard": 1.0, "hd": 1.3, "premium": 1.8}
        type_multiplier = {"voice": 1.0, "video": 2.0, "conference": 2.5}
        
        call_cost = (self.service_plans[self.active_plan]["price_per_minute"] * 
                     (new_call["duration"] / 60) * 
                     quality_multiplier[call_quality] * 
                     type_multiplier[call_type])
        
        # Add recording cost if enabled
        if recording_enabled:
            call_cost += 0.05 * (new_call["duration"] / 60)  # $0.05 per minute for recording
        
        if caller_user["balance"] < call_cost:
            new_call["status"] = "failed_insufficient_balance"
            print(f"Call ID={new_call['call_id']} failed due to insufficient balance.")
            return {"code": "INSUFFICIENT_BALANCE", "message": "Insufficient balance to make call."}

        caller_user["balance"] -= call_cost
        self.billing_history.append({
            "transaction_id": self._generate_unique_id(),
            "type": "voice_call_charge",
            "user_id": caller_user_id,
            "amount": -call_cost,
            "date": datetime.now().isoformat(),
            "description": f"{call_type.capitalize()} call to {to_number}, duration {new_call['duration']}s, quality: {call_quality}"
        })
        
        new_call["status"] = "completed"
        print(f"Call ID={new_call['call_id']} status updated to 'completed'")
        
        # attach a mock audio URL for the call
        new_call["audioUrl"] = f"https://audio.mock/{new_call_id}.mp3"
        
        # Add recording URL if recording was enabled
        if recording_enabled:
            new_call["recordingUrl"] = f"https://recordings.mock/{new_call_id}.mp3"
        
        return {
            "call_id": new_call["call_id"],
            "from": new_call["caller"],
            "to": new_call["receiver"],
            "audioUrl": new_call["audioUrl"],
            "status": new_call["status"],
            "timestamp": new_call["timestamp"],
            "duration": new_call["duration"],
            "call_type": call_type,
            "call_quality": call_quality,
            "recording_url": new_call.get("recordingUrl")
        }

    # shouldn't be able to work b/c of time.sleep removal, but keeping for structure and realism
    def get_voice_call_status(self, call_id: str) -> Dict[str, Union[str, int, float]]:
        """
        Retrieves the current status of a previously initiated voice call.

        Args:
            call_id (str): The unique ID of the voice call to check.

        Returns:
            Dict: A dictionary representing the voice call object if found,
                  or an error dictionary if not found.
        """
        # time.sleep(0.05)
        call = None
        for user_data in self.users.values():
            call = next((c for c in user_data["call_history"] if c["call_id"] == call_id), None)
            if call:
                break

        if not call:
            return {"code": "CALL_NOT_FOUND", "message": f"Voice call with ID '{call_id}' not found."}

        print(f"Call status retrieved for ID={call_id}: {call['status']}")
        return {
            "call_id": call["call_id"],
            "from": call["caller"],
            "to": call["receiver"],
            "audioUrl": call.get("audioUrl"),
            "status": call["status"],
            "timestamp": call["timestamp"],
            "duration": call.get("duration")
        }

    def get_all_sms_messages(self) -> Dict[str, Union[List[Dict], str]]:
        """
        Retrieves all SMS messages for the currently logged-in user.

        Returns:
            Dict: A dictionary containing a list of the user's SMS messages,
                  or an error dictionary if user not logged in.
        """
        login_check = self._require_login()
        if login_check:
            return {"code": "NOT_AUTHENTICATED", "message": login_check["message"], "sms_messages": []}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        all_sms_messages = []

        for msg in user_data["sms_history"]:
            msg_copy = deepcopy(msg)
            if "sender_id" in msg_copy and not msg_copy.get("is_external"):
                msg_copy["sender_email"] = self._get_user_email_by_id(msg_copy["sender_id"])
            if not msg_copy.get("is_external"):
                receiver_user_id = self._get_user_id_by_phone(msg_copy["receiver"])
                if receiver_user_id:
                    msg_copy["receiver_email"] = self._get_user_email_by_id(receiver_user_id)
            all_sms_messages.append(msg_copy)

        return {"sms_messages": all_sms_messages, "status": "success"}

    def get_all_voice_calls(self) -> Dict[str, Union[List[Dict], str]]:
        """
        Retrieves all voice calls for the currently logged-in user.

        Returns:
            Dict: A dictionary containing a list of the user's voice calls,
                  or an error dictionary if user not logged in.
        """
        login_check = self._require_login()
        if login_check:
            return {"code": "NOT_AUTHENTICATED", "message": login_check["message"], "voice_calls": []}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        all_voice_calls = []

        for call in user_data["call_history"]:
            call_copy = deepcopy(call)
            if "caller_id" in call_copy and not call_copy.get("is_external"):
                call_copy["caller_email"] = self._get_user_email_by_id(call_copy["caller_id"])
            if not call_copy.get("is_external"):
                receiver_user_id = self._get_user_id_by_phone(call_copy["receiver"])
                if receiver_user_id:
                    call_copy["receiver_email"] = self._get_user_email_by_id(receiver_user_id)
            all_voice_calls.append(call_copy)
        
        return {"voice_calls": all_voice_calls, "status": "success"}

    def get_user_info(self) -> Dict[str, Union[Dict, str]]:
        """
        Retrieves detailed information for the currently logged-in user.

        Returns:
            Dict: A dictionary containing the user's information,
                  or an error dictionary if user not logged in.
        """
        login_check = self._require_login()
        if login_check:
            return {"code": "NOT_AUTHENTICATED", "message": login_check["message"]}

        user_id = self._get_current_user_id()
        user_info_copy = deepcopy(self.users[user_id])
        
        friend_emails = []
        for friend_uid in user_info_copy.get("friends", []):
            friend_email = self._get_user_email_by_id(friend_uid)
            if friend_email:
                friend_emails.append(friend_email)
        user_info_copy["friends"] = friend_emails

        user_info_copy.pop("password_hash", None)
        return {"user": user_info_copy, "status": "success"}

    def update_user_settings(
        self, 
        settings: Dict,
        validate_settings: bool = True,
        merge_with_existing: bool = True
    ) -> Dict[str, Union[Dict, str]]:
        """
        Updates the settings for the currently logged-in user.

        Args:
            settings (Dict): A dictionary containing the settings to update (e.g., {"sms_notifications": False}).
            validate_settings (bool): Whether to validate settings before applying. Default is True.
            merge_with_existing (bool): Whether to merge with existing settings or replace. Default is True.

        Returns:
            Dict: A dictionary containing the updated user's settings,
                  or an error dictionary if user not logged in.
        """
        login_check = self._require_login()
        if login_check:
            return {"code": "NOT_AUTHENTICATED", "message": login_check["message"]}

        user_id = self._get_current_user_id()

        # Validate settings if requested
        if validate_settings:
            valid_keys = ["sms_notifications", "call_notifications", "voicemail_enabled", "call_forwarding", "do_not_disturb"]
            for key in settings.keys():
                if key not in valid_keys:
                    return {"code": "INVALID_SETTING", "message": f"Invalid setting key: {key}. Valid keys: {valid_keys}"}

        if merge_with_existing:
            self.users[user_id]["settings"].update(settings)
        else:
            self.users[user_id]["settings"] = settings
            
        return {"updated_settings": deepcopy(self.users[user_id]["settings"]), "status": "success", "message": "User settings updated successfully."}

    def get_billing_history(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        transaction_type: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Union[List[Dict], str]]:
        """
        Retrieves the billing history for the currently logged-in user.

        Args:
            start_date (Optional[str]): ISO timestamp to filter records from this date. Default is None.
            end_date (Optional[str]): ISO timestamp to filter records up to this date. Default is None.
            transaction_type (Optional[str]): Filter by type - "sms_charge", "voice_call_charge", "refund". Default is None.
            limit (int): Maximum number of records to return. Default is 100.

        Returns:
            Dict: A dictionary containing a list of billing records,
                  or an error dictionary if user not logged in.
        """
        login_check = self._require_login()
        if login_check:
            return {"code": "NOT_AUTHENTICATED", "message": login_check["message"], "billing_history": []}
        
        user_id = self._get_current_user_id()
        user_email = self._get_user_email_by_id(user_id)
        filtered_history = []
        
        for record in self.billing_history:
            if record.get("user_id") != user_id:
                continue
            
            # Apply date filters
            record_date = record.get("date", "")
            if start_date and record_date < start_date:
                continue
            if end_date and record_date > end_date:
                continue
            
            # Apply transaction type filter
            if transaction_type and record.get("type") != transaction_type:
                continue
            
            record_copy = deepcopy(record)
            record_copy["user_email"] = user_email
            filtered_history.append(record_copy)
        
        # Apply limit
        filtered_history = filtered_history[:limit]
        
        return {"billing_history": filtered_history, "status": "success", "total_records": len(filtered_history)}

    def create_support_ticket(
        self, 
        subject: str, 
        description: str,
        priority: str = "medium",
        category: str = "general",
        attachments: Optional[List[str]] = None,
        preferred_contact_method: str = "email"
    ) -> Dict[str, Union[Dict, str]]:
        """
        Creates a new support ticket for the currently logged-in user.

        Args:
            subject (str): The subject of the support ticket.
            description (str): A detailed description of the issue.
            priority (str): Priority level - "low", "medium", "high", or "urgent". Default is "medium".
            category (str): Ticket category - "general", "billing", "technical", or "account". Default is "general".
            attachments (Optional[List[str]]): List of attachment URLs/paths. Default is None.
            preferred_contact_method (str): Preferred contact method - "email", "phone", or "sms". Default is "email".

        Returns:
            Dict: A dictionary representing the created support ticket,
                  or an error dictionary if user not logged in.
        """
        login_check = self._require_login()
        if login_check:
            return {"code": "NOT_AUTHENTICATED", "message": login_check["message"]}

        user_id = self._get_current_user_id()
        user_email = self._get_user_email_by_id(user_id)

        # Validate priority
        if priority not in ["low", "medium", "high", "urgent"]:
            return {"code": "INVALID_PRIORITY", "message": "Priority must be 'low', 'medium', 'high', or 'urgent'."}
        
        # Validate category
        if category not in ["general", "billing", "technical", "account"]:
            return {"code": "INVALID_CATEGORY", "message": "Category must be 'general', 'billing', 'technical', or 'account'."}
        
        # Validate contact method
        if preferred_contact_method not in ["email", "phone", "sms"]:
            return {"code": "INVALID_CONTACT_METHOD", "message": "Contact method must be 'email', 'phone', or 'sms'."}

        ticket_id = self._generate_unique_id()
        new_ticket = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "subject": subject,
            "description": description,
            "priority": priority,
            "category": category,
            "attachments": attachments or [],
            "preferred_contact_method": preferred_contact_method,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        self.support_tickets.append(new_ticket)
        print(f"Support ticket created: ID={new_ticket['ticket_id']} for {user_email} (priority: {priority}, category: {category})")
        
        ticket_for_display = deepcopy(new_ticket)
        ticket_for_display["user_email"] = user_email

        # tests expect the key 'ticket' and the ticket to contain 'ticket_id'
        return {"ticket": ticket_for_display, "status": "success", "message": "Support ticket created successfully."}

    def get_network_status(self) -> Dict[str, str]:
        """
        Retrieves the current network operational status of the CommuniLink service.

        Returns:
            Dict: A dictionary indicating the network status.
        """
        # time.sleep(0.05)
        return {"status": "success", "message": self.network_status}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self._load_scenario(DEFAULT_COMMUNILINK_STATE)
        print("CommuniLinkApis: All data reset to default state.")
        return {"success": True, "status": True}