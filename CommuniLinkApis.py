import time
import random
from copy import deepcopy
from typing import Dict, List, Optional, Union


DEFAULT_COMMUNILINK_STATE = {
    "users": {
        "user1@example.com": {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "user1@example.com",
            "phone_number": "+15551234567",
            "balance": 100.00,
            "sms_history": [],
            "call_history": [],
            "settings": {
                "sms_notifications": True,
                "call_forwarding_enabled": False,
                "call_forwarding_number": ""
            },
            "friends": ["user2@example.com", "user3@example.com"]
        },
        "user2@example.com": {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "user2@example.com",
            "phone_number": "+15559876543",
            "balance": 50.00,
            "sms_history": [],
            "call_history": [],
            "settings": {
                "sms_notifications": False,
                "call_forwarding_enabled": True,
                "call_forwarding_number": "+15551112222"
            },
            "friends": ["user1@example.com", "user3@example.com"]
        },
        "user3@example.com": {
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "user3@example.com",
            "phone_number": "+15553334444",
            "balance": 250.00,
            "sms_history": [],
            "call_history": [],
            "settings": {
                "sms_notifications": True,
                "call_forwarding_enabled": False,
                "call_forwarding_number": ""
            },
            "friends": ["user1@example.com", "user2@example.com"]
        }
    },
    "current_user": "user1@example.com",
    "sms_counter": 0,
    "call_counter": 0,
    "billing_history": [],
    "support_tickets": [],
    "service_plans": {
        "basic": {"price_per_sms": 0.05, "price_per_minute": 0.10, "description": "Basic communication plan"},
        "premium": {"price_per_sms": 0.02, "price_per_minute": 0.05, "description": "Premium communication plan with lower rates"}
    },
    "active_plan": "basic",
    "network_status": "operational"
}

class CommuniLinkApis:
    """
    A dummy API class for CommuniLink, simulating SMS messaging and voice calling
    functionality. This class provides an in-memory backend for development
    and testing purposes without making actual API calls.
    """

    def __init__(self):
        """
        Initializes the CommuniLinkApis instance, setting up the in-memory
        data stores for SMS messages and voice calls, and loading the default
        scenario.
        """
        self.users: Dict = {}
        self.current_user: str = ""
        self.sms_counter: int = 0
        self.call_counter: int = 0
        self.billing_history: List[Dict] = []
        self.support_tickets: List[Dict] = []
        self.service_plans: Dict = {}
        self.active_plan: str = ""
        self.network_status: str = ""

        self._api_description = "This tool belongs to the CommuniLink API, which provides core functionality for SMS messaging and voice calls."
        self._load_scenario(DEFAULT_COMMUNILINK_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain keys like "sms_messages",
                             "voice_calls", etc.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_COMMUNILINK_STATE)

        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.sms_counter = scenario.get("sms_counter", DEFAULT_STATE_COPY["sms_counter"])
        self.call_counter = scenario.get("call_counter", DEFAULT_STATE_COPY["call_counter"])
        self.billing_history = scenario.get("billing_history", DEFAULT_STATE_COPY["billing_history"])
        self.support_tickets = scenario.get("support_tickets", DEFAULT_STATE_COPY["support_tickets"])
        self.service_plans = scenario.get("service_plans", DEFAULT_STATE_COPY["service_plans"])
        self.active_plan = scenario.get("active_plan", DEFAULT_STATE_COPY["active_plan"])
        self.network_status = scenario.get("network_status", DEFAULT_STATE_COPY["network_status"])

        self.sms_messages = []
        self.voice_calls = []
        for user_email in self.users:
            self.sms_messages.extend(self.users[user_email]["sms_history"])
            self.voice_calls.extend(self.users[user_email]["call_history"])


        print(f"CommuniLinkApis: Loaded scenario. Current User: {self.current_user}")

    def _generate_unique_id(self, prefix: str) -> str:
        """
        Generates a unique ID for dummy entities (SMS messages, voice calls).

        Args:
            prefix (str): A prefix for the ID (e.g., "sms", "call").

        Returns:
            str: A unique ID string.
        """
        timestamp = int(time.time() * 1000)
        random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
        return f"{prefix}-{timestamp}-{random_suffix}"

    def send_sms(self, from_number: str, to_number: str, message: str) -> Dict[str, Union[str, int]]:
        """
        Simulates sending an SMS message. The message status progresses
        from 'queued' to 'sent' and then 'delivered' over a short simulated time.

        Args:
            from_number (str): The sender's phone number (E.164 format, e.g., "+15551234567").
            to_number (str): The recipient's phone number (E.164 format, e.g., "+15559876543").
            message (str): The text content of the SMS.

        Returns:
            Dict: A dictionary representing the simulated SMS message object,
                  including 'id', 'from', 'to', 'message', 'status', and 'timestamp'.
                  Returns an error dictionary if parameters are missing.
        """
        if not from_number or not to_number or not message:
            return {"code": "MISSING_PARAMS", "message": "Missing required parameters: from_number, to_number, and message."}

        sender_user = next((user for user in self.users.values() if user["phone_number"] == from_number), None)
        if not sender_user:
            return {"code": "INVALID_FROM_NUMBER", "message": "Sender phone number not associated with any user."}

        sms_cost = self.service_plans[self.active_plan]["price_per_sms"]
        if sender_user["balance"] < sms_cost:
            return {"code": "INSUFFICIENT_BALANCE", "message": "Insufficient balance to send SMS."}
        sender_user["balance"] -= sms_cost
        self.billing_history.append({
            "type": "sms",
            "user_email": sender_user["email"],
            "amount": sms_cost,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "description": f"SMS to {to_number}"
        })

        self.sms_counter += 1
        new_sms = {
            "id": self._generate_unique_id("sms"),
            "from": from_number,
            "to": to_number,
            "message": message,
            "status": "queued",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        }
        sender_user["sms_history"].append(new_sms)
        print(f"Dummy SMS queued: ID={new_sms['id']} from {sender_user['email']}")

        time.sleep(0.1)
        new_sms["status"] = "sent"
        time.sleep(0.2)
        new_sms["status"] = "delivered"
        print(f"Dummy SMS ID={new_sms['id']} status updated to 'delivered'")

        return new_sms

    def get_sms_status(self, message_id: str) -> Dict[str, Union[str, int]]:
        """
        Retrieves the current status of a previously sent SMS message.

        Args:
            message_id (str): The unique ID of the SMS message to check.

        Returns:
            Dict: A dictionary representing the SMS message object if found,
                  or an error dictionary if not found.
        """
        time.sleep(0.05)
        sms = None
        for user in self.users.values():
            sms = next((msg for msg in user["sms_history"] if msg["id"] == message_id), None)
            if sms:
                break

        if not sms:
            return {"code": "SMS_NOT_FOUND", "message": f"SMS message with ID '{message_id}' not found."}

        print(f"Dummy SMS status retrieved for ID={message_id}: {sms['status']}")
        return sms

    def make_voice_call(self, from_number: str, to_number: str, audio_url: Optional[str] = None) -> Dict[str, Union[str, int, float]]:
        """
        Simulates initiating an outbound voice call. The call status progresses
        from 'initiated' to 'ringing', 'in-progress', and then 'completed'
        over a simulated time.

        Args:
            from_number (str): The caller's phone number (E.164 format).
            to_number (str): The recipient's phone number (E.164 format).
            audio_url (Optional[str]): Optional URL for audio to play to the recipient
                                       upon connection (e.g., "https://example.com/welcome.mp3").

        Returns:
            Dict: A dictionary representing the simulated voice call object,
                  including 'id', 'from', 'to', 'audioUrl', 'status', 'timestamp',
                  and 'duration' (if completed). Returns an error dictionary
                  if parameters are missing.
        """
        if not from_number or not to_number:
            return {"code": "MISSING_PARAMS", "message": "Missing required parameters: from_number and to_number."}

        caller_user = next((user for user in self.users.values() if user["phone_number"] == from_number), None)
        if not caller_user:
            return {"code": "INVALID_FROM_NUMBER", "message": "Caller phone number not associated with any user."}

        new_call = {
            "id": self._generate_unique_id("call"),
            "from": from_number,
            "to": to_number,
            "audioUrl": audio_url,
            "status": "initiated",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "duration": 0
        }
        caller_user["call_history"].append(new_call)
        print(f"Dummy Call initiated: ID={new_call['id']} from {caller_user['email']}")

        time.sleep(0.15)
        new_call["status"] = "ringing"
        time.sleep(0.5)
        new_call["status"] = "in-progress"
        
        call_duration = round(random.uniform(2, 5))
        time.sleep(call_duration)
        
        new_call["status"] = "completed"
        new_call["duration"] = round(random.uniform(30, 120))

        call_cost = self.service_plans[self.active_plan]["price_per_minute"] * (new_call["duration"] / 60)
        if caller_user["balance"] < call_cost:
            new_call["status"] = "failed_insufficient_balance"
            print(f"Dummy Call ID={new_call['id']} failed due to insufficient balance.")
            return {"code": "INSUFFICIENT_BALANCE", "message": "Insufficient balance to make call."}

        caller_user["balance"] -= call_cost
        self.billing_history.append({
            "type": "voice_call",
            "user_email": caller_user["email"],
            "amount": call_cost,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "description": f"Call to {to_number}, duration {new_call['duration']}s"
        })

        print(f"Dummy Call ID={new_call['id']} status updated to 'completed'")
        self.call_counter += 1
        
        return new_call

    def get_voice_call_status(self, call_id: str) -> Dict[str, Union[str, int, float]]:
        """
        Retrieves the current status of a previously initiated voice call.

        Args:
            call_id (str): The unique ID of the voice call to check.

        Returns:
            Dict: A dictionary representing the voice call object if found,
                  or an error dictionary if not found.
        """
        time.sleep(0.05)
        call = None
        for user in self.users.values():
            call = next((c for c in user["call_history"] if c["id"] == call_id), None)
            if call:
                break

        if not call:
            return {"code": "CALL_NOT_FOUND", "message": f"Voice call with ID '{call_id}' not found."}

        print(f"Dummy Call status retrieved for ID={call_id}: {call['status']}")
        return call

    def get_all_sms_messages(self, user_email: Optional[str] = None) -> Dict[str, Union[List[Dict], str]]:
        """
        Retrieves all simulated SMS messages stored in the dummy backend,
        optionally filtered by user email.

        Args:
            user_email (Optional[str]): If provided, only SMS messages for this user will be returned.

        Returns:
            Dict: A dictionary containing a list of all SMS messages,
                  or an error dictionary if user not found.
        """
        time.sleep(0.05)
        if user_email:
            user = self.users.get(user_email)
            if not user:
                return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}
            return {"sms_messages": deepcopy(user["sms_history"]), "status": "success"}
        else:
            all_sms = []
            for user in self.users.values():
                all_sms.extend(user["sms_history"])
            return {"sms_messages": deepcopy(all_sms), "status": "success"}

    def get_all_voice_calls(self, user_email: Optional[str] = None) -> Dict[str, Union[List[Dict], str]]:
        """
        Retrieves all simulated voice calls stored in the dummy backend,
        optionally filtered by user email.

        Args:
            user_email (Optional[str]): If provided, only voice calls for this user will be returned.

        Returns:
            Dict: A dictionary containing a list of all voice calls,
                  or an error dictionary if user not found.
        """
        time.sleep(0.05)
        if user_email:
            user = self.users.get(user_email)
            if not user:
                return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}
            return {"voice_calls": deepcopy(user["call_history"]), "status": "success"}
        else:
            all_calls = []
            for user in self.users.values():
                all_calls.extend(user["call_history"])
            return {"voice_calls": deepcopy(all_calls), "status": "success"}

    def get_user_info(self, user_email: str) -> Dict[str, Union[Dict, str]]:
        """
        Retrieves detailed information for a specific user.

        Args:
            user_email (str): The email of the user to retrieve information for.

        Returns:
            Dict: A dictionary containing the user's information,
                  or an error dictionary if user not found.
        """
        user = self.users.get(user_email)
        if not user:
            return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}

        return {"user_info": deepcopy(user), "status": "success"}

    def update_user_settings(self, user_email: str, settings: Dict) -> Dict[str, Union[Dict, str]]:
        """
        Updates the settings for a specific user.

        Args:
            user_email (str): The email of the user whose settings are to be updated.
            settings (Dict): A dictionary containing the settings to update (e.g., {"sms_notifications": False}).

        Returns:
            Dict: A dictionary containing the updated user's settings,
                  or an error dictionary if user not found.
        """
        user = self.users.get(user_email)
        if not user:
            return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}

        user["settings"].update(settings)
        return {"updated_settings": deepcopy(user["settings"]), "status": "success", "message": "User settings updated successfully."}

    def get_billing_history(self, user_email: Optional[str] = None) -> Dict[str, Union[List[Dict], str]]:
        """
        Retrieves the billing history for all users or a specific user.

        Args:
            user_email (Optional[str]): If provided, filters billing history for this user.

        Returns:
            Dict: A dictionary containing a list of billing records,
                  or an error dictionary if user not found.
        """
        time.sleep(0.05)
        if user_email:
            user = self.users.get(user_email)
            if not user:
                return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}
            user_billing_history = [record for record in self.billing_history if record.get("user_email") == user_email]
            return {"billing_history": deepcopy(user_billing_history), "status": "success"}
        else:
            return {"billing_history": deepcopy(self.billing_history), "status": "success"}

    def create_support_ticket(self, user_email: str, subject: str, description: str) -> Dict[str, Union[Dict, str]]:
        """
        Creates a new support ticket for a user.

        Args:
            user_email (str): The email of the user creating the ticket.
            subject (str): The subject of the support ticket.
            description (str): A detailed description of the issue.

        Returns:
            Dict: A dictionary representing the created support ticket,
                  or an error dictionary if user not found.
        """
        user = self.users.get(user_email)
        if not user:
            return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}

        ticket_id = self._generate_unique_id("ticket")
        new_ticket = {
            "id": ticket_id,
            "user_email": user_email,
            "subject": subject,
            "description": description,
            "status": "open",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        }
        self.support_tickets.append(new_ticket)
        print(f"Support ticket created: ID={new_ticket['id']} for {user_email}")
        return {"support_ticket": deepcopy(new_ticket), "status": "success", "message": "Support ticket created successfully."}

    def get_network_status(self) -> Dict[str, str]:
        """
        Retrieves the current network operational status of the CommuniLink service.

        Returns:
            Dict: A dictionary indicating the network status.
        """
        time.sleep(0.05)
        return {"network_status": self.network_status, "status": "success"}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self._load_scenario(DEFAULT_COMMUNILINK_STATE)
        print("CommuniLinkApis: All dummy data reset to default state.")
        return {"reset_status": True}