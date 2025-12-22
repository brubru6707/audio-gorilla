"""
Inspired by https://appworld.dev/

Uses stateful design
"""
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
        Initializes the CommuniLinkApis instance by setting up in-memory data stores for
        SMS messaging, voice calling, billing, and support functionality.
        
        The instance state includes:
            - users: Dictionary of user accounts with phone numbers, SMS/call history, balances
            - current_user_id: The ID of the currently logged-in user (None if no user logged in)
            - billing_history: List of billing transaction records
            - support_tickets: List of customer support tickets
            - service_plans: Dictionary of available service plans with pricing
            - active_plan: The currently active service plan identifier
            - network_status: Current operational status of the network
        
        Side Effects:
            - Initializes all state dictionaries and lists to empty
            - Loads DEFAULT_COMMUNILINK_STATE to populate with default scenario data
            - Sets _api_description for API identification
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
        Loads a predefined scenario into the backend's state, replacing all current data
        with the scenario's data or falling back to defaults for missing keys.
        
        Args:
            scenario (Dict): A dictionary representing the complete state to load. Expected keys:
                - users (Dict): User account data with phone numbers and histories
                - current_user_id (Optional[str]): Currently logged-in user ID
                - billing_history (List[Dict]): Transaction history records
                - support_tickets (List[Dict]): Customer support ticket records
                - service_plans (Dict): Available service plans with pricing
                - active_plan (str): Currently active service plan identifier
                - network_status (str): Network operational status
        
        Side Effects:
            - Replaces all instance state variables with scenario data
            - Falls back to DEFAULT_COMMUNILINK_STATE for any missing keys
            - Prints confirmation message with current_user_id to console
        
        Notes:
            - Used for testing with different scenarios
            - Creates deep copy of default state to prevent mutation
            - Preserves data integrity by using get() with defaults
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
        """
        Retrieves a user's unique ID by searching for their email address.
        
        Args:
            email (str): The email address to search for. Case-sensitive exact match.
        
        Returns:
            Optional[str]: The user's UUID if found, None if no user has that email.
        
        Notes:
            - Linear search through all users (O(n) complexity)
            - Returns first matching email (assumes emails are unique)
        """
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """
        Retrieves a user's email address by their unique ID.
        
        Args:
            user_id (str): The unique UUID identifier of the user.
        
        Returns:
            Optional[str]: The user's email address if user found, None otherwise.
        """
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _get_user_id_by_phone(self, phone_number: str) -> Optional[str]:
        """
        Retrieves a user's unique ID by searching for their phone number.
        
        Args:
            phone_number (str): The phone number to search for in E.164 format (e.g., "+15559876543").
                               Case-sensitive exact match.
        
        Returns:
            Optional[str]: The user's UUID if found, None if no user has that phone number.
        
        Notes:
            - Linear search through all users (O(n) complexity)
            - Returns first matching phone number (assumes phone numbers are unique)
        """
        for user_id, user_data in self.users.items():
            if user_data.get("phone_number") == phone_number:
                return user_id
        return None

    def _get_user_phone_by_id(self, user_id: str) -> Optional[str]:
        """
        Retrieves a user's phone number by their unique ID.
        
        Args:
            user_id (str): The unique UUID identifier of the user.
        
        Returns:
            Optional[str]: The user's phone number if user found, None otherwise.
        """
        user_data = self.users.get(user_id)
        return user_data.get("phone_number") if user_data else None

    def _generate_unique_id(self) -> str:
        """
        Generates a new unique identifier using UUID4 for entities like SMS messages,
        calls, tickets, and transactions.
        
        Returns:
            str: A unique UUID string (e.g., "abc-123-def-456...").
        
        Notes:
            - Uses uuid.uuid4() for random UUID generation
            - Extremely low probability of collisions
        """
        return str(uuid.uuid4())

    def _require_login(self) -> Optional[Dict[str, Union[bool, str]]]:
        """
        Validates that a user is currently logged in and their session is valid.
        
        Returns:
            Optional[Dict[str, Union[bool, str]]]: None if user is logged in (validation passes),
                                                   otherwise returns error dictionary with:
                                                   - status (bool): False
                                                   - message (str): Error description
        
        Error Cases:
            - No user logged in: {"status": False, "message": "User must be logged in to perform this action."}
            - Invalid session (user deleted): {"status": False, "message": "Invalid session. Please log in again."}
        
        Usage Pattern:
            Used at the start of protected methods to enforce authentication:
            >>> login_check = self._require_login()
            >>> if login_check:
            >>>     return {"code": "NOT_AUTHENTICATED", "message": login_check["message"]}
        
        Notes:
            - Validates both current_user_id existence and user record existence
            - Clears current_user_id if user record not found (session cleanup)
        """
        if not self.current_user_id:
            return {"status": False, "message": "User must be logged in to perform this action."}
        if self.current_user_id not in self.users:
            self.current_user_id = None
            return {"status": False, "message": "Invalid session. Please log in again."}
        return None

    def _get_current_user_id(self) -> Optional[str]:
        """
        Retrieves the unique ID of the currently logged-in user.
        
        Returns:
            Optional[str]: The UUID of the current user, or None if no user is logged in.
        """
        return self.current_user_id

    def _get_current_user_data(self) -> Optional[Dict]:
        """
        Retrieves the complete data record for the currently logged-in user.
        
        Returns:
            Optional[Dict]: The current user's data dictionary containing all user information,
                           or None if no user is logged in or user record not found.
        """
        if not self.current_user_id:
            return None
        return self.users.get(self.current_user_id)

    def _get_current_user_phone(self) -> Optional[str]:
        """
        Retrieves the phone number of the currently logged-in user.
        
        Returns:
            Optional[str]: The current user's phone number in E.164 format, or None if
                          no user is logged in or user has no phone number.
        """
        user_data = self._get_current_user_data()
        return user_data.get("phone_number") if user_data else None

    def login_user(self, email: str, password: str) -> Dict[str, Union[bool, str]]:
        """
        Authenticates a user by validating credentials and establishing an active session.
        
        Args:
            email (str): The user's email address. Must match the email used during registration.
            password (str): The user's password. Must match the hashed password stored in the system.
        
        Returns:
            Dict[str, Union[bool, str]]: Authentication result dictionary containing:
                - login_status (bool): True if login successful, False otherwise
                - message (str): Success or error message
                - user_id (str): The authenticated user's UUID (only on success)
                - phone_number (str): The user's phone number (only on success)
        
        Error Cases:
            - Invalid credentials: {"login_status": False, "message": "Invalid email or password."}
              (same message for both email not found and password mismatch for security)
        
        Side Effects:
            - Sets self.current_user_id to the authenticated user's UUID on success
            - Prints confirmation message to console
        
        Example:
            >>> api.login_user("john@example.com", "password123")
            {"login_status": True, "message": "Login successful.", "user_id": "abc-123...", "phone_number": "+15551234567"}
        
        Notes:
            - Password is hashed using hash() and last 48 characters stored
            - Only one user can be logged in at a time in this simulation
            - Does not create session tokens or expiration
        """
        user_id = self._get_user_id_by_email(email)
        if not user_id:
            return {"login_status": False, "message": "Invalid email or password."}
        
        user_data = self.users[user_id]
        password_hash = str(hash(password))[-48:]
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
        Terminates the current user's session by clearing the authentication state.
        
        Returns:
            Dict[str, Union[bool, str]]: Logout result dictionary containing:
                - logout_status (bool): True if logout successful, False if no user logged in
                - message (str): Success or error message
        
        Error Cases:
            - No user logged in: {"logout_status": False, "message": "No user is currently logged in."}
        
        Side Effects:
            - Sets self.current_user_id to None, clearing the session
            - Prints confirmation message with user email to console
            - User's data remains intact; only the session reference is removed
        
        Example:
            >>> api.logout_user()
            {"logout_status": True, "message": "Logout successful."}
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
        Registers a new user account with the system by creating a unique user ID and
        initializing their profile with default values.
        
        Args:
            first_name (str): The user's first name.
            last_name (str): The user's last name.
            email (str): The user's email address. Must be unique across all users.
            password (str): The user's password. Stored as hash (last 48 chars of hash digest).
            phone_number (str): The user's phone number in E.164 format (e.g., "+15551234567").
                               Must be unique across all users.
        
        Returns:
            Dict[str, Union[bool, str]]: Registration result dictionary containing:
                - register_status (bool): True if registration successful, False otherwise
                - message (str): Success message with user_id, or error description
                - user_id (str): The newly generated UUID for the user (only on success)
        
        Error Cases:
            - Email already exists: {"register_status": False, "message": "Email already registered."}
            - Phone already exists: {"register_status": False, "message": "Phone number already registered."}
        
        Side Effects:
            - Creates new user record in self.users with UUID key
            - Initializes user with balance=0.0, empty sms_history, empty call_history,
              empty friends list, default settings (notifications enabled, voicemail enabled)
            - Password hashed using hash() function, last 48 characters stored
            - Prints confirmation message to console
        
        Example:
            >>> api.register_user("John", "Doe", "john@example.com", "pass123", "+15551234567")
            {"register_status": True, "message": "Registration successful.", "user_id": "abc-123..."}
        
        Notes:
            - Does not automatically log in the user after registration
            - Password hashing is for simulation only (not cryptographically secure)
            - Settings initialized with all notifications and voicemail enabled
        """
        # Check if email already exists
        if self._get_user_id_by_email(email):
            return {"register_status": False, "message": "Email already registered."}
        
        # Check if phone number already exists
        if self._get_user_id_by_phone(phone_number):
            return {"register_status": False, "message": "Phone number already registered."}
        
        # Create new user
        new_user_id = self._generate_unique_id()
        password_hash = str(hash(password))[-48:]
        
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

    def send_sms( self,  to_number: str,  message: str, priority: str = "normal", delivery_receipt: bool = True, schedule_time: Optional[str] = None, max_retries: int = 3, message_type: str = "text"
    ) -> Dict[str, Union[str, int]]:
        """
        Sends an SMS message from the currently logged-in user to the specified recipient,
        with support for priority levels, scheduling, and delivery tracking.
        
        Args:
            to_number (str): The recipient's phone number in E.164 format (e.g., "+15559876543").
            message (str): The text content of the SMS message.
            priority (str, optional): Message priority level. Valid values: "low", "normal", "high".
                                     Affects cost multiplier (low=0.8x, normal=1.0x, high=1.5x).
                                     Default is "normal".
            delivery_receipt (bool, optional): Whether to request delivery receipt. Default is True.
            schedule_time (Optional[str], optional): ISO timestamp for scheduled delivery (e.g., "2025-12-13T15:30:00").
                                                     If None, sends immediately. Default is None.
            max_retries (int, optional): Maximum retry attempts if delivery fails. Default is 3.
            message_type (str, optional): Type of message. Valid values: "text", "marketing", "transactional".
                                         Default is "text".
        
        Returns:
            Dict[str, Union[str, int]]: SMS sending result dictionary containing:
                - id (str): The unique UUID of the SMS message
                - from (str): Sender's phone number
                - to (str): Recipient's phone number
                - message (str): The message text
                - status (str): Message status ("queued", "scheduled", "delivered")
                - timestamp (str): ISO timestamp when message was created
                - priority (str): Priority level used
                - delivery_receipt (bool): Delivery receipt setting (only if not scheduled)
                - schedule_time (str): Scheduled delivery time (only if scheduled)
        
        Error Cases:
            - Not logged in: {"code": "NOT_AUTHENTICATED", "message": "User must be logged in..."}
            - Missing params: {"code": "MISSING_PARAMS", "message": "Missing required parameters: to_number and message."}
            - Invalid priority: {"code": "INVALID_PRIORITY", "message": "Priority must be 'low', 'normal', or 'high'."}
            - Invalid type: {"code": "INVALID_MESSAGE_TYPE", "message": "Message type must be 'text', 'marketing', or 'transactional'."}
            - Insufficient balance: {"code": "INSUFFICIENT_BALANCE", "message": "Insufficient balance to send SMS."}
        
        Side Effects:
            - Deducts SMS cost from sender's balance (cost = plan_price * priority_multiplier)
            - Creates billing transaction record
            - Adds SMS to sender's sms_history
            - Adds SMS to receiver's sms_history (if receiver is in system)
            - Sets status to "delivered" for immediate sends, "scheduled" for future sends
            - Prints status messages to console
        
        Example:
            >>> api.send_sms("+15559876543", "Hello, how are you?", priority="high")
            {"id": "sms-abc...", "from": "+15551234567", "to": "+15559876543",
             "message": "Hello, how are you?", "status": "delivered", "timestamp": "2025-12-13T10:30:00",
             "priority": "high", "delivery_receipt": True}
        
        Notes:
            - External numbers (not in system) are supported
            - Scheduled messages remain in "scheduled" status until schedule_time
            - Status progression: queued → sent → delivered (immediate) or queued → scheduled (future)
            - Cost varies by priority: low (80%), normal (100%), high (150%)
            - Simulates delivery instantly without actual time delay
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
        Retrieves the current delivery status of a previously sent SMS message by its ID.
        
        Args:
            message_id (str): The unique UUID identifier of the SMS message to check.
        
        Returns:
            Dict[str, Union[str, int]]: SMS status result dictionary containing:
                - id (str): The SMS message's unique identifier
                - from (str): Sender's phone number
                - to (str): Recipient's phone number
                - message (str): The message text
                - status (str): Current message status (e.g., "queued", "sent", "delivered", "failed")
                - timestamp (str): ISO timestamp when message was created
        
        Error Cases:
            - Message not found: {"code": "SMS_NOT_FOUND", "message": "SMS message with ID 'xxx' not found."}
        
        Side Effects:
            - Prints status retrieval confirmation to console
        
        Example:
            >>> api.get_sms_status("sms-abc-123")
            {"id": "sms-abc-123", "from": "+15551234567", "to": "+15559876543",
             "message": "Hello", "status": "delivered", "timestamp": "2025-12-13T10:30:00"}
        
        Notes:
            - Searches through all users' sms_history to find the message
            - Does not require user login
            - Status reflects most recent state of the message
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
        Initiates an outbound voice call from the currently logged-in user with support for
        various call types, quality levels, and advanced features.
        
        Args:
            to_number (str): The recipient's phone number in E.164 format (e.g., "+15559876543").
            call_type (str, optional): Type of call. Valid values: "voice", "video", "conference".
                                      Affects cost multiplier (voice=1.0x, video=2.0x, conference=2.5x).
                                      Default is "voice".
            recording_enabled (bool, optional): Whether to record the call. Adds $0.05/min cost.
                                               Default is False.
            caller_id_display (bool, optional): Whether to display caller ID to recipient. Default is True.
            call_forwarding (Optional[str], optional): Phone number to forward call to if unanswered.
                                                      Default is None.
            voicemail_enabled (bool, optional): Whether voicemail is available if unanswered. Default is True.
            call_quality (str, optional): Call quality setting. Valid values: "standard", "hd", "premium".
                                         Affects cost multiplier (standard=1.0x, hd=1.3x, premium=1.8x).
                                         Default is "standard".
        
        Returns:
            Dict[str, Union[str, int, float]]: Voice call result dictionary containing:
                - call_id (str): The unique UUID of the call
                - from (str): Caller's phone number
                - to (str): Recipient's phone number
                - audioUrl (str): Mock URL for call audio recording
                - status (str): Call status ("completed", "failed", etc.)
                - timestamp (str): ISO timestamp when call was initiated
                - duration (int): Call duration in seconds
                - call_type (str): Type of call used
                - call_quality (str): Quality level used
                - recording_url (str): Mock URL for call recording (only if recording_enabled=True)
        
        Error Cases:
            - Not logged in: {"code": "NOT_AUTHENTICATED", "message": "User must be logged in..."}
            - Missing params: {"code": "MISSING_PARAMS", "message": "Missing required parameter: to_number."}
            - Invalid call type: {"code": "INVALID_CALL_TYPE", "message": "Call type must be 'voice', 'video', or 'conference'."}
            - Invalid quality: {"code": "INVALID_CALL_QUALITY", "message": "Call quality must be 'standard', 'hd', or 'premium'."}
            - Insufficient balance: {"code": "INSUFFICIENT_BALANCE", "message": "Insufficient balance to make call."}
        
        Side Effects:
            - Deducts call cost from caller's balance (calculated before call for validation)
            - Cost = plan_rate * (duration/60) * quality_multiplier * type_multiplier + recording_cost
            - Creates billing transaction record with detailed description
            - Adds call to caller's call_history
            - Adds call to receiver's call_history (if receiver is in system)
            - Generates random call duration (30-120 seconds)
            - Sets status to "completed" after simulated call
            - Prints status messages to console
        
        Example:
            >>> api.make_voice_call("+15559876543", call_type="video", call_quality="hd", recording_enabled=True)
            {"call_id": "call-xyz...", "from": "+15551234567", "to": "+15559876543",
             "audioUrl": "https://audio.mock/call-xyz.mp3", "status": "completed",
             "timestamp": "2025-12-13T10:30:00", "duration": 87, "call_type": "video",
             "call_quality": "hd", "recording_url": "https://recordings.mock/call-xyz.mp3"}
        
        Notes:
            - Balance check occurs BEFORE call to prevent insufficient funds during call
            - External numbers (not in system) are supported
            - Status progression simulated: initiated → ringing → in-progress → completed
            - Call duration randomly generated (30-120 seconds)
            - Recording adds $0.05 per minute to base cost
            - Quality and type multipliers stack (e.g., video + hd = 2.0 * 1.3 = 2.6x base cost)
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

        # Generate call duration before initiating to check balance
        call_duration_ = round(random.uniform(30, 120))

        # Calculate cost before making the call
        quality_multiplier = {"standard": 1.0, "hd": 1.3, "premium": 1.8}
        type_multiplier = {"voice": 1.0, "video": 2.0, "conference": 2.5}
        
        call_cost = (self.service_plans[self.active_plan]["price_per_minute"] * 
                     (call_duration_ / 60) * 
                     quality_multiplier[call_quality] * 
                     type_multiplier[call_type])
        
        # Add recording cost if enabled
        if recording_enabled:
            call_cost += 0.05 * (call_duration_ / 60)  # $0.05 per minute for recording
        
        # Check balance BEFORE making the call
        if caller_user["balance"] < call_cost:
            print(f"Call not initiated due to insufficient balance for user {caller_user['email']}.")
            return {"code": "INSUFFICIENT_BALANCE", "message": "Insufficient balance to make call."}

        # Now proceed with the call since balance is sufficient
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
        # time.sleep(min(call_duration_ / 10, 2))

        new_call["duration"] = call_duration_

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
        Retrieves the current status of a previously initiated voice call by its ID.
        
        Args:
            call_id (str): The unique UUID identifier of the voice call to check.
        
        Returns:
            Dict[str, Union[str, int, float]]: Voice call status result dictionary containing:
                - call_id (str): The call's unique identifier
                - from (str): Caller's phone number
                - to (str): Recipient's phone number
                - audioUrl (str): Mock URL for call audio
                - status (str): Current call status (e.g., "initiated", "ringing", "in-progress", "completed")
                - timestamp (str): ISO timestamp when call was initiated
                - duration (int/float): Call duration in seconds (if completed)
        
        Error Cases:
            - Call not found: {"code": "CALL_NOT_FOUND", "message": "Voice call with ID 'xxx' not found."}
        
        Side Effects:
            - Prints status retrieval confirmation to console
        
        Example:
            >>> api.get_voice_call_status("call-xyz-789")
            {"call_id": "call-xyz-789", "from": "+15551234567", "to": "+15559876543",
             "audioUrl": "https://audio.mock/call-xyz-789.mp3", "status": "completed",
             "timestamp": "2025-12-13T10:30:00", "duration": 87}
        
        Notes:
            - Searches through all users' call_history to find the call
            - Does not require user login
            - Status reflects most recent state of the call
            - Note in code indicates time.sleep was removed for testing
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
        Retrieves all SMS messages for the currently logged-in user, including both sent
        and received messages with full user information.
        
        Returns:
            Dict[str, Union[List[Dict], str]]: SMS messages result dictionary containing:
                - sms_messages (List[Dict]): List of all SMS message objects, each with:
                    - sms_id (str): Message's unique identifier
                    - sender (str): Sender's phone number
                    - sender_id (str): Sender's user ID
                    - sender_email (str): Sender's email (if not external)
                    - receiver (str): Receiver's phone number
                    - receiver_email (str): Receiver's email (if not external)
                    - message (str): Message text
                    - status (str): Message status
                    - timestamp (str): Message timestamp
                    - priority (str): Priority level
                    - delivery_receipt (bool): Delivery receipt setting
                    - schedule_time (str): Scheduled time (if applicable)
                    - max_retries (int): Max retry attempts
                    - message_type (str): Message type
                    - retry_count (int): Current retry count
                    - is_external (bool): Whether message involves external number
                - status (str): Always "success" when retrieved successfully
        
        Error Cases:
            - Not logged in: {"code": "NOT_AUTHENTICATED", "message": "User must be logged in...", "sms_messages": []}
        
        Example:
            >>> api.get_all_sms_messages()
            {"sms_messages": [{...}, {...}], "status": "success"}
        
        Notes:
            - Returns empty list if user has no SMS history
            - Includes both sent and received messages
            - Adds sender_email and receiver_email by looking up user IDs
            - External messages marked with is_external flag
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
        Retrieves all voice calls for the currently logged-in user, including both placed
        and received calls with full user information.
        
        Returns:
            Dict[str, Union[List[Dict], str]]: Voice calls result dictionary containing:
                - voice_calls (List[Dict]): List of all voice call objects, each with:
                    - call_id (str): Call's unique identifier
                    - caller (str): Caller's phone number
                    - caller_id (str): Caller's user ID
                    - caller_email (str): Caller's email (if not external)
                    - receiver (str): Receiver's phone number
                    - receiver_email (str): Receiver's email (if not external)
                    - duration_minutes (int): Planned call duration
                    - duration (int): Actual call duration in seconds
                    - status (str): Call status
                    - timestamp (str): Call timestamp
                    - type (str): Call type (voice/video/conference)
                    - is_external (bool): Whether call involves external number
                    - recording_enabled (bool): Recording setting
                    - caller_id_display (bool): Caller ID display setting
                    - call_forwarding (str): Call forwarding number
                    - voicemail_enabled (bool): Voicemail setting
                    - call_quality (str): Quality level
                    - audioUrl (str): Mock audio URL
                    - recordingUrl (str): Mock recording URL (if recording enabled)
                - status (str): Always "success" when retrieved successfully
        
        Error Cases:
            - Not logged in: {"code": "NOT_AUTHENTICATED", "message": "User must be logged in...", "voice_calls": []}
        
        Example:
            >>> api.get_all_voice_calls()
            {"voice_calls": [{...}, {...}], "status": "success"}
        
        Notes:
            - Returns empty list if user has no call history
            - Includes both placed and received calls
            - Adds caller_email and receiver_email by looking up user IDs
            - External calls marked with is_external flag
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

    def get_user_info(self) -> Dict[str, Union[str, Dict, bool]]:
        """
        Retrieves comprehensive information about the currently logged-in user including
        profile details, balance, settings, and active service plan.
        
        Returns:
            Dict[str, Union[str, Dict, bool]]: User information result dictionary containing:
                - user_id (str): User's unique identifier
                - first_name (str): User's first name
                - last_name (str): User's last name
                - email (str): User's email address
                - phone_number (str): User's phone number
                - balance (float): User's current account balance
                - settings (Dict): User's settings dictionary with:
                    - notification_preferences (Dict): Notification settings
                    - voicemail_enabled (bool): Voicemail setting
                    - call_blocking (List): Blocked numbers list
                    - etc.
                - active_plan (str): Name of user's currently active service plan
                - status (str): Always "success" when retrieved successfully
        
        Error Cases:
            - Not logged in: {"code": "NOT_AUTHENTICATED", "message": "User must be logged in...", "user_info": {}}
        
        Side Effects:
            - Prints user info retrieval confirmation to console
        
        Example:
            >>> api.get_user_info()
            {"user_id": "user-abc-123", "first_name": "Alice", "last_name": "Johnson",
             "email": "alice@example.com", "phone_number": "+15551234567", "balance": 47.30,
             "settings": {...}, "active_plan": "Premium Plan", "status": "success"}
        
        Notes:
            - Returns complete user profile in one call
            - Does not include password hash
            - Settings contain notification preferences, voicemail, and call blocking
            - Active plan is None if user has no service plan
        """
        login_check = self._require_login()
        if login_check:
            return {"code": "NOT_AUTHENTICATED", "message": login_check["message"], "voice_calls": []}
        
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
        Retrieves comprehensive information about the currently logged-in user including
        profile details, balance, settings, and active service plan.
        
        Returns:
            Dict[str, Union[str, Dict, bool]]: User information result dictionary containing:
                - user (Dict): User data dictionary with:
                    - user_id (str): User's unique identifier
                    - first_name (str): User's first name
                    - last_name (str): User's last name
                    - email (str): User's email address
                    - phone_number (str): User's phone number
                    - balance (float): User's current account balance
                    - settings (Dict): User's settings dictionary
                    - sms_history (List): User's SMS history
                    - call_history (List): User's call history
                    - friends (List[str]): List of friend email addresses
                    - (password_hash excluded from response)
                - status (str): Always "success" when retrieved successfully
        
        Error Cases:
            - Not logged in: {"code": "NOT_AUTHENTICATED", "message": "User must be logged in..."}
        
        Example:
            >>> api.get_user_info()
            {"user": {"user_id": "user-abc-123", "first_name": "Alice", "last_name": "Johnson",
             "email": "alice@example.com", "phone_number": "+15551234567", "balance": 47.30,
             "friends": ["bob@example.com", "charlie@example.com"], ...}, "status": "success"}
        
        Notes:
            - Returns complete user profile in one call
            - Password hash is excluded for security
            - Friend UIDs are converted to email addresses
            - Includes complete SMS and call history
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
        Updates the settings for the currently logged-in user, with options to validate
        and merge settings with existing configuration.
        
        Args:
            settings (Dict): Dictionary containing the settings to update. Examples include:
                - sms_notifications (bool): Enable/disable SMS notifications
                - email_notifications (bool): Enable/disable email notifications
                - voicemail_enabled (bool): Enable/disable voicemail
                - call_blocking (List[str]): List of blocked phone numbers
                - call_forwarding (str): Number to forward calls to
                - do_not_disturb (bool): Do not disturb mode
            validate_settings (bool): Whether to validate settings before applying. Default is True.
                When True, performs validation checks on setting values.
            merge_with_existing (bool): Whether to merge with existing settings (True) or replace
                entirely (False). Default is True.
        
        Returns:
            Dict[str, Union[Dict, str]]: Settings update result dictionary containing:
                - settings (Dict): The updated user settings dictionary
                - status (str): Always "success" when settings updated successfully
        
        Error Cases:
            - Not logged in: {"code": "NOT_AUTHENTICATED", "message": "User must be logged in..."}
        
        Side Effects:
            - Updates user's settings in state
            - When merge_with_existing=False, replaces all existing settings
            - When merge_with_existing=True, updates only specified keys
            - Prints settings update confirmation to console
        
        Example:
            >>> api.update_user_settings({
            ...     "sms_notifications": False,
            ...     "email_notifications": True
            ... }, validate_settings=True, merge_with_existing=True)
            {"settings": {"sms_notifications": False, "email_notifications": True, ...}, "status": "success"}
        
        Notes:
            - Partial updates supported when merge_with_existing=True
            - Validation behavior controlled by validate_settings parameter
            - Settings structure is flexible and not strictly enforced
            - No validation logic currently implemented even when validate_settings=True
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
        Retrieves the billing history for the currently logged-in user with optional
        filtering by date range, transaction type, and result limit.
        
        Args:
            start_date (Optional[str]): ISO timestamp to filter records from this date onwards.
                Format: "YYYY-MM-DDTHH:MM:SS". If None, no lower date bound. Default is None.
            end_date (Optional[str]): ISO timestamp to filter records up to this date.
                Format: "YYYY-MM-DDTHH:MM:SS". If None, no upper date bound. Default is None.
            transaction_type (Optional[str]): Filter by transaction type. Valid values:
                - "sms_charge": SMS sending charges
                - "voice_call_charge": Voice call charges
                - "refund": Refund transactions
                - None: No type filtering (all types). Default is None.
            limit (int): Maximum number of records to return. Applied after filtering.
                Default is 100.
        
        Returns:
            Dict[str, Union[List[Dict], str]]: Billing history result dictionary containing:
                - billing_history (List[Dict]): List of billing transaction objects, each with:
                    - transaction_id (str): Transaction's unique identifier
                    - type (str): Transaction type (sms_charge, voice_call_charge, refund)
                    - user_id (str): User's unique identifier
                    - amount (float): Transaction amount (negative for charges, positive for refunds)
                    - date (str): ISO timestamp of transaction
                    - description (str): Transaction description (if present)
                - status (str): Always "success" when retrieved successfully
        
        Error Cases:
            - Not logged in: {"code": "NOT_AUTHENTICATED", "message": "User must be logged in...", "billing_history": []}
        
        Example:
            >>> api.get_billing_history(start_date="2025-01-01T00:00:00",
            ...                          transaction_type="sms_charge", limit=10)
            {"billing_history": [{"transaction_id": "txn-xyz", "type": "sms_charge",
             "amount": -0.15, "date": "2025-01-05T10:30:00", ...}], "status": "success"}
        
        Notes:
            - Returns only transactions for the logged-in user
            - Date filtering is inclusive on both ends
            - Results are sorted by date (most recent first)
            - Charges have negative amounts, refunds have positive amounts
            - Limit is applied after all other filters
            - Empty list returned if no transactions match filters
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
        Creates a new support ticket for the currently logged-in user with customizable
        priority, category, and contact preferences.
        
        Args:
            subject (str): The subject/title of the support ticket. Brief summary of the issue.
            description (str): Detailed description of the issue or request.
            priority (str): Priority level for the ticket. Valid values:
                - "low": Non-urgent issues
                - "medium": Normal priority (default)
                - "high": Important issues requiring prompt attention
                - "urgent": Critical issues requiring immediate attention
                Default is "medium".
            category (str): Ticket category for routing. Valid values:
                - "general": General inquiries
                - "billing": Billing and payment issues
                - "technical": Technical support
                - "account": Account management issues
                Default is "general".
            attachments (Optional[List[str]]): List of attachment URLs or file paths to include
                with the ticket. Default is None (no attachments).
            preferred_contact_method (str): Preferred method for support team to respond. Valid values:
                - "email": Contact via email (default)
                - "phone": Contact via phone call
                - "sms": Contact via SMS message
                Default is "email".
        
        Returns:
            Dict[str, Union[Dict, str]]: Support ticket creation result dictionary containing:
                - ticket (Dict): The created support ticket object with:
                    - ticket_id (str): Ticket's unique identifier
                    - user_id (str): User's unique identifier
                    - user_email (str): User's email address
                    - subject (str): Ticket subject
                    - description (str): Ticket description
                    - priority (str): Priority level
                    - category (str): Ticket category
                    - status (str): Current status (initially "open")
                    - created_at (str): ISO timestamp of ticket creation
                    - updated_at (str): ISO timestamp of last update
                    - attachments (List[str]): List of attachment URLs
                    - preferred_contact_method (str): Preferred contact method
                - status (str): Always "success" when ticket created successfully
        
        Error Cases:
            - Not logged in: {"code": "NOT_AUTHENTICATED", "message": "User must be logged in..."}
            - Missing subject: {"code": "MISSING_PARAMS", "message": "Subject is required..."}
            - Missing description: {"code": "MISSING_PARAMS", "message": "Description is required..."}
            - Invalid priority: {"code": "INVALID_PRIORITY", "message": "Priority must be 'low', 'medium', 'high', or 'urgent'."}
            - Invalid category: {"code": "INVALID_CATEGORY", "message": "Category must be 'general', 'billing', 'technical', or 'account'."}
        
        Side Effects:
            - Adds ticket to support_tickets list
            - Prints ticket creation confirmation to console
        
        Example:
            >>> api.create_support_ticket(
            ...     "Cannot send SMS",
            ...     "I'm unable to send SMS messages since yesterday",
            ...     priority="high",
            ...     category="technical"
            ... )
            {"ticket": {"ticket_id": "ticket-xyz-789", "subject": "Cannot send SMS",
             "status": "open", "priority": "high", ...}, "status": "success"}
        
        Notes:
            - Ticket status starts as "open"
            - Both created_at and updated_at timestamps initially set to same value
            - Attachments are stored as-is without validation
            - Ticket IDs are unique UUIDs
            - Support tickets stored in self.support_tickets list
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
        Retrieves the current network operational status of the CommuniLink service,
        indicating whether the network is operational, under maintenance, or experiencing issues.
        
        Returns:
            Dict[str, str]: Network status result dictionary containing:
                - status (str): Always "success" indicating API call succeeded
                - message (str): Current network status message. Common values:
                    - "operational": Network fully operational
                    - "degraded": Experiencing performance issues
                    - "maintenance": Under scheduled maintenance
                    - "outage": Service unavailable
        
        Example:
            >>> api.get_network_status()
            {"status": "success", "message": "operational"}
        
        Notes:
            - Does not require user login
            - Returns simulated status from self.network_status
            - Status is set during initialization or via _load_scenario
            - In production, would query real network monitoring systems
            - Time delay removed for testing (see commented time.sleep)
        """
        # time.sleep(0.05)
        return {"status": "success", "message": self.network_status}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the backend to its default state. This is a utility
        function for testing purposes and not a standard API endpoint for production use.
        
        Returns:
            Dict[str, bool]: Reset operation result dictionary containing:
                - success (bool): Always True indicating reset succeeded
                - status (bool): Always True indicating operation completed
        
        Side Effects:
            - Reloads default state using DEFAULT_COMMUNILINK_STATE
            - Clears current_user_id (logs out any logged-in user)
            - Resets all users to default scenario users
            - Clears all billing history
            - Clears all support tickets
            - Resets service plans to defaults
            - Resets network status to default
            - Prints reset confirmation to console
        
        Example:
            >>> api.reset_data()
            {"success": True, "status": True}
        
        Notes:
            - Used primarily in unit tests to ensure clean state between tests
            - All changes made during testing session are lost
            - Does not require user login
            - Calls _load_scenario with DEFAULT_COMMUNILINK_STATE
            - Cannot be undone - all current data is lost
        """
        self._load_scenario(DEFAULT_COMMUNILINK_STATE)
        print("CommuniLinkApis: All data reset to default state.")
        return {"success": True, "status": True}