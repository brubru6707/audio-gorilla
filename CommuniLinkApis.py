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
        Loads a predefined scenario into the dummy backend's state.
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

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for dummy entities.
        """
        return str(uuid.uuid4())

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

        sender_user_id = None
        for u_id, user_data in self.users.items():
            if user_data["phone_number"] == from_number:
                sender_user_id = u_id
                break
        
        if not sender_user_id:
            return {"code": "INVALID_FROM_NUMBER", "message": "Sender phone number not associated with any user."}
        
        sender_user = self.users[sender_user_id]

        sms_cost = self.service_plans[self.active_plan]["price_per_sms"]
        if sender_user["balance"] < sms_cost:
            return {"code": "INSUFFICIENT_BALANCE", "message": "Insufficient balance to send SMS."}
        
        sender_user["balance"] -= sms_cost
        self.billing_history.append({
            "transaction_id": self._generate_unique_id(),
            "type": "sms_charge",
            "user_id": sender_user_id,
            "amount": -sms_cost,
            "date": datetime.now().isoformat(),
            "description": f"SMS to {to_number}"
        })
# hi
        new_sms_id = self._generate_unique_id()
        new_sms = {
            "sms_id": new_sms_id,
            "sender": from_number,
            "sender_id": sender_user_id,
            "receiver": to_number,
            "message": message,
            "status": "queued",
            "timestamp": datetime.now().isoformat()
        }
        
        is_external = True
        receiver_user_id = None
        for u_id, user_data in self.users.items():
            if user_data["phone_number"] == to_number:
                receiver_user_id = u_id
                is_external = False
                break
        
        new_sms["is_external"] = is_external

        sender_user["sms_history"].append(new_sms)
        if receiver_user_id:
            receiver_user = self.users[receiver_user_id]
            receiver_user["sms_history"].append(new_sms)
            print(f"Dummy SMS queued: ID={new_sms['sms_id']} from {sender_user['email']} to {receiver_user['email']}")
        else:
            print(f"Dummy SMS queued: ID={new_sms['sms_id']} from {sender_user['email']} to external number {to_number}")

        time.sleep(0.1)
        new_sms["status"] = "sent"
        time.sleep(0.2)
        new_sms["status"] = "delivered"
        print(f"Dummy SMS ID={new_sms['sms_id']} status updated to 'delivered'")

        return {
            "id": new_sms["sms_id"],
            "from": new_sms["sender"],
            "to": new_sms["receiver"],
            "message": new_sms["message"],
            "status": new_sms["status"],
            "timestamp": new_sms["timestamp"]
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
        time.sleep(0.05)
        sms = None
        for user_data in self.users.values():
            sms = next((msg for msg in user_data["sms_history"] if msg["sms_id"] == message_id), None)
            if sms:
                break

        if not sms:
            return {"code": "SMS_NOT_FOUND", "message": f"SMS message with ID '{message_id}' not found."}

        print(f"Dummy SMS status retrieved for ID={message_id}: {sms['status']}")
        return {
            "id": sms["sms_id"],
            "from": sms["sender"],
            "to": sms["receiver"],
            "message": sms["message"],
            "status": sms["status"],
            "timestamp": sms["timestamp"]
        }

    def make_voice_call(self, from_number: str, to_number: str, audio_url: Optional[str] = None) -> Dict[str, Union[str, int, float]]:
        """
        Simulates initiating an outbound voice call. The call status progresses
        from 'initiated' to 'ringing', 'in-progress', and then 'completed'
        over a simulated time.

        Args:
            from_number (str): The caller's phone number (E.164 format).
            to_number (str): The recipient's phone number (E.164 format).
            audio_url (Optional[str]): Optional URL for audio to play to the recipient
                                       upon connection (e.g., "https://CommuniLink.com/welcome.mp3").

        Returns:
            Dict: A dictionary representing the simulated voice call object,
                  including 'id', 'from', 'to', 'audioUrl', 'status', 'timestamp',
                  and 'duration' (if completed). Returns an error dictionary
                  if parameters are missing.
        """
        if not from_number or not to_number:
            return {"code": "MISSING_PARAMS", "message": "Missing required parameters: from_number and to_number."}

        caller_user_id = None
        for u_id, user_data in self.users.items():
            if user_data["phone_number"] == from_number:
                caller_user_id = u_id
                break

        if not caller_user_id:
            return {"code": "INVALID_FROM_NUMBER", "message": "Caller phone number not associated with any user."}
        
        caller_user = self.users[caller_user_id]

        new_call_id = self._generate_unique_id()
        new_call = {
            "call_id": new_call_id,
            "caller": from_number,
            "caller_id": caller_user_id,
            "receiver": to_number,
            "audioUrl": audio_url,
            "status": "initiated",
            "timestamp": datetime.now().isoformat(),
            "duration": 0
        }
        
        is_external = True
        receiver_user_id = None
        for u_id, user_data in self.users.items():
            if user_data["phone_number"] == to_number:
                receiver_user_id = u_id
                is_external = False
                break
        
        new_call["is_external"] = is_external

        caller_user["call_history"].append(new_call)
        if receiver_user_id:
            receiver_user = self.users[receiver_user_id]
            receiver_user["call_history"].append(new_call)
            print(f"Dummy Call initiated: ID={new_call['call_id']} from {caller_user['email']} to {receiver_user['email']}")
        else:
            print(f"Dummy Call initiated: ID={new_call['call_id']} from {caller_user['email']} to external number {to_number}")

        time.sleep(0.15)
        new_call["status"] = "ringing"
        time.sleep(0.5)
        new_call["status"] = "in-progress"
        
        call_duration_seconds = round(random.uniform(30, 120))
        time.sleep(min(call_duration_seconds / 10, 2))
        
        new_call["duration"] = call_duration_seconds
        
        call_cost = self.service_plans[self.active_plan]["price_per_minute"] * (new_call["duration"] / 60)
        
        if caller_user["balance"] < call_cost:
            new_call["status"] = "failed_insufficient_balance"
            print(f"Dummy Call ID={new_call['call_id']} failed due to insufficient balance.")
            return {"code": "INSUFFICIENT_BALANCE", "message": "Insufficient balance to make call."}

        caller_user["balance"] -= call_cost
        self.billing_history.append({
            "transaction_id": self._generate_unique_id(),
            "type": "voice_call_charge",
            "user_id": caller_user_id,
            "amount": -call_cost,
            "date": datetime.now().isoformat(),
            "description": f"Call to {to_number}, duration {new_call['duration']}s"
        })
        
        new_call["status"] = "completed"
        print(f"Dummy Call ID={new_call['call_id']} status updated to 'completed'")
        
        return {
            "id": new_call["call_id"],
            "from": new_call["caller"],
            "to": new_call["receiver"],
            "audioUrl": new_call["audioUrl"],
            "status": new_call["status"],
            "timestamp": new_call["timestamp"],
            "duration": new_call["duration"]
        }

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
        for user_data in self.users.values():
            call = next((c for c in user_data["call_history"] if c["call_id"] == call_id), None)
            if call:
                break

        if not call:
            return {"code": "CALL_NOT_FOUND", "message": f"Voice call with ID '{call_id}' not found."}

        print(f"Dummy Call status retrieved for ID={call_id}: {call['status']}")
        return {
            "id": call["call_id"],
            "from": call["caller"],
            "to": call["receiver"],
            "audioUrl": call["audioUrl"],
            "status": call["status"],
            "timestamp": call["timestamp"],
            "duration": call["duration"]
        }

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
        all_sms_messages = []

        if user_email:
            user_id = self._get_user_id_by_email(user_email)
            if not user_id:
                return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}
            user_data = self.users[user_id]
            for msg in user_data["sms_history"]:
                msg_copy = deepcopy(msg)
                if "sender_id" in msg_copy and not msg_copy.get("is_external"):
                    msg_copy["sender_email"] = self._get_user_email_by_id(msg_copy["sender_id"])
                if not msg_copy.get("is_external"):
                    receiver_user_id = self._get_user_id_by_email(msg_copy["receiver"])
                    if receiver_user_id:
                        msg_copy["receiver_email"] = msg_copy["receiver"]
                    else:
                        receiver_user_id_from_phone = None
                        for u_id, u_data in self.users.items():
                            if u_data["phone_number"] == msg_copy["receiver"]:
                                receiver_user_id_from_phone = u_id
                                break
                        if receiver_user_id_from_phone:
                            msg_copy["receiver_email"] = self._get_user_email_by_id(receiver_user_id_from_phone)

                all_sms_messages.append(msg_copy)
        else:
            for user_data in self.users.values():
                for msg in user_data["sms_history"]:
                    msg_copy = deepcopy(msg)
                    if "sender_id" in msg_copy and not msg_copy.get("is_external"):
                        msg_copy["sender_email"] = self._get_user_email_by_id(msg_copy["sender_id"])
                    if not msg_copy.get("is_external"):
                        receiver_user_id = self._get_user_id_by_email(msg_copy["receiver"])
                        if receiver_user_id:
                            msg_copy["receiver_email"] = msg_copy["receiver"]
                        else:
                            receiver_user_id_from_phone = None
                            for u_id, u_data in self.users.items():
                                if u_data["phone_number"] == msg_copy["receiver"]:
                                    receiver_user_id_from_phone = u_id
                                    break
                            if receiver_user_id_from_phone:
                                msg_copy["receiver_email"] = self._get_user_email_by_id(receiver_user_id_from_phone)
                    all_sms_messages.append(msg_copy)
        
        unique_sms = []
        seen_sms_ids = set()
        for sms in all_sms_messages:
            if sms["sms_id"] not in seen_sms_ids:
                unique_sms.append(sms)
                seen_sms_ids.add(sms["sms_id"])

        return {"sms_messages": unique_sms, "status": "success"}

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
        all_voice_calls = []

        if user_email:
            user_id = self._get_user_id_by_email(user_email)
            if not user_id:
                return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}
            user_data = self.users[user_id]
            for call in user_data["call_history"]:
                call_copy = deepcopy(call)
                if "caller_id" in call_copy and not call_copy.get("is_external"):
                    call_copy["caller_email"] = self._get_user_email_by_id(call_copy["caller_id"])
                if not call_copy.get("is_external"):
                    receiver_user_id = self._get_user_id_by_email(call_copy["receiver"])
                    if receiver_user_id:
                        call_copy["receiver_email"] = call_copy["receiver"]
                    else:
                        receiver_user_id_from_phone = None
                        for u_id, u_data in self.users.items():
                            if u_data["phone_number"] == call_copy["receiver"]:
                                receiver_user_id_from_phone = u_id
                                break
                        if receiver_user_id_from_phone:
                            call_copy["receiver_email"] = self._get_user_email_by_id(receiver_user_id_from_phone)
                all_voice_calls.append(call_copy)
        else:
            for user_data in self.users.values():
                for call in user_data["call_history"]:
                    call_copy = deepcopy(call)
                    if "caller_id" in call_copy and not call_copy.get("is_external"):
                        call_copy["caller_email"] = self._get_user_email_by_id(call_copy["caller_id"])
                    if not call_copy.get("is_external"):
                        receiver_user_id = self._get_user_id_by_email(call_copy["receiver"])
                        if receiver_user_id:
                            call_copy["receiver_email"] = call_copy["receiver"]
                        else:
                            receiver_user_id_from_phone = None
                            for u_id, u_data in self.users.items():
                                if u_data["phone_number"] == call_copy["receiver"]:
                                    receiver_user_id_from_phone = u_id
                                    break
                            if receiver_user_id_from_phone:
                                call_copy["receiver_email"] = self._get_user_email_by_id(receiver_user_id_from_phone)
                    all_voice_calls.append(call_copy)
        
        unique_calls = []
        seen_call_ids = set()
        for call in all_voice_calls:
            if call["call_id"] not in seen_call_ids:
                unique_calls.append(call)
                seen_call_ids.add(call["call_id"])

        return {"voice_calls": unique_calls, "status": "success"}

    def get_user_info(self, user_email: str) -> Dict[str, Union[Dict, str]]:
        """
        Retrieves detailed information for a specific user.

        Args:
            user_email (str): The email of the user to retrieve information for.

        Returns:
            Dict: A dictionary containing the user's information,
                  or an error dictionary if user not found.
        """
        user_id = self._get_user_id_by_email(user_email)
        if not user_id:
            return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}

        user_info_copy = deepcopy(self.users[user_id])
        
        friend_emails = []
        for friend_uid in user_info_copy.get("friends", []):
            friend_email = self._get_user_email_by_id(friend_uid)
            if friend_email:
                friend_emails.append(friend_email)
        user_info_copy["friends"] = friend_emails

        user_info_copy.pop("password_hash", None)

        return {"user_info": user_info_copy, "status": "success"}

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
        user_id = self._get_user_id_by_email(user_email)
        if not user_id:
            return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}

        self.users[user_id]["settings"].update(settings)
        return {"updated_settings": deepcopy(self.users[user_id]["settings"]), "status": "success", "message": "User settings updated successfully."}

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
        filtered_history = []
        if user_email:
            user_id = self._get_user_id_by_email(user_email)
            if not user_id:
                return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}
            
            for record in self.billing_history:
                if record.get("user_id") == user_id:
                    record_copy = deepcopy(record)
                    record_copy["user_email"] = user_email
                    filtered_history.append(record_copy)
        else:
            for record in self.billing_history:
                record_copy = deepcopy(record)
                record_copy["user_email"] = self._get_user_email_by_id(record_copy.get("user_id"))
                filtered_history.append(record_copy)
                
        return {"billing_history": filtered_history, "status": "success"}

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
        user_id = self._get_user_id_by_email(user_email)
        if not user_id:
            return {"code": "USER_NOT_FOUND", "message": f"User with email '{user_email}' not found."}

        ticket_id = self._generate_unique_id()
        new_ticket = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "subject": subject,
            "description": description,
            "status": "open",
            "created_at": datetime.now().isoformat()
        }
        self.support_tickets.append(new_ticket)
        print(f"Support ticket created: ID={new_ticket['ticket_id']} for {user_email}")
        
        ticket_for_display = deepcopy(new_ticket)
        ticket_for_display["user_email"] = user_email

        return {"support_ticket": ticket_for_display, "status": "success", "message": "Support ticket created successfully."}

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