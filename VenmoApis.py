import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional, Union
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("VenmoApis")

class EmailStr(str):
    pass

class User:
    def __init__(self, email: EmailStr):
        self.email = email
        
class VenmoApis:
    """
    A dummy API class for simulating Venmo operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the VenmoApis instance, setting up the in-memory
        data stores and loading the default scenario.
        """
        self._api_description = "This tool simulates Venmo payment and social functionalities."
        self.users: Dict[str, Any] = {} # Keyed by user UUID
        self.transactions: Dict[str, Any] = {} # Keyed by transaction UUID
        self.notifications: Dict[str, Any] = {} # Keyed by notification UUID
        self.current_user: Optional[str] = None # Stores the UUID of the current user
        self._payment_card_lookup_map: Dict[tuple[str, str], str] = {}
        
        self._load_scenario(DEFAULT_STATE)
        self._populate_lookup_maps()

    def _populate_lookup_maps(self):
        """Populates the internal maps for looking up IDs after loading scenario."""
        self._payment_card_lookup_map = {}
        for user_uuid, user_data in self.users.items():
            payment_cards = user_data.get("payment_cards", {})
            for card_uuid, card_data in payment_cards.items():
                # We stored the original_card_id as the key in RAW_DEFAULT_STATE,
                # but it's not a direct property in the converted card_data.
                # If we need to map a *string* card_id from the API call to a UUID,
                # we need to ensure this mapping is handled during conversion or here.
                # For simplicity, if the API takes `card_id: str`, we assume it's a UUID.
                # If it takes `payment_method_id: int`, we would need a map from int to UUID.
                # Given the user's request for "long complex string", I'm assuming such inputs are UUIDs.
                pass # No direct mapping needed for old_card_id if API takes UUIDs for card_id

        # Rebuild transaction and notification lookup maps from the current state (already UUIDs)
        # These are direct lookups by UUID, so no extra map needed for "old" IDs


    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain "users", "transactions", "notifications".
        """
        # Create deep copy to ensure the original DEFAULT_STATE is not modified
        self.users = copy.deepcopy(scenario.get("users", {}))
        self.transactions = copy.deepcopy(scenario.get("transactions", {}))
        self.notifications = copy.deepcopy(scenario.get("notifications", {}))
        self.current_user = scenario.get("current_user") # This will already be a UUID after conversion

        self._populate_lookup_maps() # Repopulate map on load
        print("VenmoApis: Loaded scenario with UUIDs for users, transactions, and notifications.")

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for dummy entities.
        """
        return str(uuid.uuid4())

    def _get_user_data(self, user: User) -> Optional[Dict[str, Any]]:
        """Helper to get a user's data based on User object (email to UUID mapping)."""
        target_user_uuid = None
        for user_id, user_data in self.users.items():
            if user_data.get("email") == user.email:
                target_user_uuid = user_id
                break
        
        if not target_user_uuid:
            return None # User not found by email

        return self.users.get(target_user_uuid)

    def _update_user_data(self, user: User, key: str, value: Any) -> bool:
        """Helper to update a specific key in a user's data by User object."""
        target_user_uuid = None
        for user_id, user_data in self.users.items():
            if user_data.get("email") == user.email:
                target_user_uuid = user_id
                break
        
        if not target_user_uuid:
            return False # User not found by email

        if target_user_uuid in self.users:
            self.users[target_user_uuid][key] = value
            return True
        return False
    
    def _get_user_uuid_from_email(self, email: str) -> Optional[str]:
        """Helper to get user UUID from email."""
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_from_uuid(self, user_uuid: str) -> Optional[str]:
        """Helper to get user email from UUID."""
        user_data = self.users.get(user_uuid)
        return user_data.get("email") if user_data else None


    def set_current_user(self, user_email: str) -> Dict[str, bool]:
        """
        Sets the current authenticated user for the API session.

        Args:
            user_email (str): The email address of the user to set as current.

        Returns:
            Dict[str, bool]: A dictionary with 'status' indicating success or failure.
        """
        user_uuid = self._get_user_uuid_from_email(user_email)
        if user_uuid:
            self.current_user = user_uuid
            return {"status": True, "message": f"Current user set to {user_email} (ID: {user_uuid})."}
        return {"status": False, "message": f"User with email {user_email} not found."}

    def show_account(self, user: User) -> Dict[str, Any]:
        """
        Shows the current user's account details including metadata.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'account_status' (bool) and 'account_details' (Dict) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"account_status": False, "account_details": {}}
        
        # Enhanced account details including backend metadata
        account_details = {
            "id": user_data.get("id"),
            "email": user_data.get("email"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "balance": user_data.get("balance", 0.0),
            "registration_date": user_data.get("registration_date"),
            "last_login_date": user_data.get("last_login_date"),
            "is_premium": user_data.get("is_premium", False),
            "total_friends": len(user_data.get("friends", [])),
            "total_payment_cards": len(user_data.get("payment_cards", {}))
        }
        
        return {"account_status": True, "account_details": account_details}

    def list_friends(self, user: User) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Lists the friends of the current user.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'friends_status' (bool) and 'friends' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"friends_status": False, "friends": []}
        
        friend_uuids = user_data.get("friends", [])
        friends_list = []
        for friend_uuid in friend_uuids:
            friend_data = self.users.get(friend_uuid)
            if friend_data:
                friends_list.append({
                    "id": friend_data["id"],
                    "email": friend_data["email"],
                    "first_name": friend_data["first_name"],
                    "last_name": friend_data["last_name"]
                })
        return {"friends_status": True, "friends": friends_list}

    def send_money(self, sender_user: User, receiver_email: str, amount: float, note: str) -> Dict[str, Union[bool, str]]:
        """
        Sends money from the current user to another user.

        Args:
            sender_user (User): The user sending the money.
            receiver_email (str): The email of the receiver.
            amount (float): The amount of money to send.
            note (str): A note for the transaction.

        Returns:
            Dict: A dictionary containing 'send_status' (bool) and 'message' (str).
        """
        sender_data = self._get_user_data(sender_user)
        receiver_uuid = self._get_user_uuid_from_email(receiver_email)
        receiver_data = self.users.get(receiver_uuid)

        if not sender_data:
            return {"send_status": False, "message": f"Sender user {sender_user.email} not found."}
        if not receiver_data:
            return {"send_status": False, "message": f"Receiver user {receiver_email} not found."}
        if sender_data["balance"] < amount:
            return {"send_status": False, "message": "Insufficient balance."}
        if amount <= 0:
            return {"send_status": False, "message": "Amount must be positive."}

        sender_data["balance"] -= amount
        receiver_data["balance"] += amount

        transaction_id = self._generate_unique_id()
        new_transaction = {
            "id": transaction_id,
            "sender": sender_data["id"],
            "receiver": receiver_data["id"],
            "amount": amount,
            "note": note,
            "status": "completed",
            "timestamp": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        }
        self.transactions[transaction_id] = new_transaction
        
        # Create notifications for sender and receiver
        self.notifications[self._generate_unique_id()] = {
            "id": self._generate_unique_id(), # New UUID for notification
            "user": sender_data["id"],
            "type": "payment_sent",
            "message": f"You sent ${amount:.2f} to {receiver_data['first_name']} {receiver_data['last_name']}.",
            "read": False,
            "notification_time": new_transaction["timestamp"]
        }
        self.notifications[self._generate_unique_id()] = {
            "id": self._generate_unique_id(), # New UUID for notification
            "user": receiver_data["id"],
            "type": "payment_received",
            "message": f"You received ${amount:.2f} from {sender_data['first_name']} {sender_data['last_name']}.",
            "read": False,
            "notification_time": new_transaction["timestamp"]
        }

        print(f"Transaction {transaction_id}: {sender_user.email} sent ${amount} to {receiver_email}")
        return {"send_status": True, "transaction_id": transaction_id}

    def request_money(self, sender_user: User, receiver_email: str, amount: float, note: str) -> Dict[str, Union[bool, str]]:
        """
        Requests money from another user to the current user.

        Args:
            sender_user (User): The user requesting the money (will be the receiver of the payment).
            receiver_email (str): The email of the user from whom money is requested (will be the sender of the payment).
            amount (float): The amount of money to request.
            note (str): A note for the request.

        Returns:
            Dict: A dictionary containing 'request_status' (bool) and 'message' (str).
        """
        requester_data = self._get_user_data(sender_user) # This is the person initiating the request
        payer_uuid = self._get_user_uuid_from_email(receiver_email)
        payer_data = self.users.get(payer_uuid)

        if not requester_data:
            return {"request_status": False, "message": f"Requester user {sender_user.email} not found."}
        if not payer_data:
            return {"request_status": False, "message": f"Payer user {receiver_email} not found."}
        if amount <= 0:
            return {"request_status": False, "message": "Amount must be positive."}

        transaction_id = self._generate_unique_id()
        new_transaction = {
            "id": transaction_id,
            "sender": payer_data["id"], # Payer is sender in the actual payment
            "receiver": requester_data["id"], # Requester is receiver in the actual payment
            "amount": amount,
            "note": note,
            "status": "pending", # Request starts as pending
            "timestamp": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        }
        self.transactions[transaction_id] = new_transaction

        # Create notifications for requester and payer
        self.notifications[self._generate_unique_id()] = {
            "id": self._generate_unique_id(), # New UUID for notification
            "user": requester_data["id"],
            "type": "payment_request_sent",
            "message": f"You requested ${amount:.2f} from {payer_data['first_name']} {payer_data['last_name']}.",
            "read": False,
            "notification_time": new_transaction["timestamp"]
        }
        self.notifications[self._generate_unique_id()] = {
            "id": self._generate_unique_id(), # New UUID for notification
            "user": payer_data["id"],
            "type": "payment_request_received",
            "message": f"{requester_data['first_name']} {requester_data['last_name']} requested ${amount:.2f}.",
            "read": False,
            "notification_time": new_transaction["timestamp"]
        }

        print(f"Transaction {transaction_id}: {sender_user.email} requested ${amount} from {receiver_email}")
        return {"request_status": True, "transaction_id": transaction_id}
    
    def get_transaction_details(self, transaction_id: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves details of a specific transaction.

        Args:
            transaction_id (str): The ID (UUID) of the transaction.

        Returns:
            Dict: A dictionary containing 'transaction_status' (bool) and 'transaction_details' (Dict) if successful.
        """
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            return {"transaction_status": False, "transaction_details": {}}
        return {"transaction_status": True, "transaction_details": copy.deepcopy(transaction)}

    def list_user_transactions(self, user: User) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Lists all transactions (sent and received) for the current user.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'transactions_status' (bool) and 'transactions' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"transactions_status": False, "transactions": []}

        user_transactions = [
            copy.deepcopy(t) for t in self.transactions.values()
            if t["sender"] == user_data["id"] or t["receiver"] == user_data["id"]
        ]
        user_transactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True) # Sort by timestamp
        return {"transactions_status": True, "transactions": user_transactions}

    def add_payment_card(
        self,
        user: User,
        card_name: str,
        owner_name: str,
        card_number: str, 
        expiry_year: int,
        expiry_month: int,
        cvv_number: str,
        is_default: bool = False,
    ) -> Dict[str, Union[bool, str]]:
        """
        Adds a new payment card for the current user.

        Args:
            user (User): The current user object.
            card_name (str): A nickname for the card (e.g., "My Visa").
            owner_name (str): The name of the card owner.
            card_number (str): The full card number.
            expiry_year (int): The expiry year (e.g., 2028).
            expiry_month (int): The expiry month (1-12).
            cvv_number (str): The CVV number. (Not stored for realism)
            is_default (bool): Whether this card should be set as default.

        Returns:
            Dict: A dictionary containing 'add_status' (bool) and 'card_id' (str) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"add_status": False, "message": "User not found."}

        # Basic validation (dummy)
        if not (1 <= expiry_month <= 12):
            return {"add_status": False, "message": "Invalid expiry month."}
        if not (datetime.datetime.now().year <= expiry_year <= datetime.datetime.now().year + 10):
            return {"add_status": False, "message": "Invalid expiry year."}
        # Mask card number for storage
        masked_card_number = f"**** **** **** {card_number[-4:]}" if len(card_number) >= 4 else "****"

        new_card_uuid = self._generate_unique_id()
        new_card = {
            "id": new_card_uuid,
            "card_name": card_name,
            "owner_name": owner_name,
            "card_number": masked_card_number,
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
            "is_default": is_default,
            "created_at": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z",
            "last_modified": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        }

        user_payment_cards = user_data.get("payment_cards", {})
        
        # If new card is default, set existing default to false
        if is_default:
            for card_id, card_info in user_payment_cards.items():
                if card_info.get("is_default"):
                    user_payment_cards[card_id]["is_default"] = False
                    break

        user_payment_cards[new_card_uuid] = new_card
        self._update_user_data(user, "payment_cards", user_payment_cards)

        return {"add_status": True, "card_id": new_card_uuid}

    def list_payment_methods(self, user: User) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Lists all payment methods associated with the current user.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'payment_methods_status' (bool) and 'payment_methods' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"payment_methods_status": False, "payment_methods": []}

        payment_methods = list(user_data.get("payment_cards", {}).values())
        return {"payment_methods_status": True, "payment_methods": copy.deepcopy(payment_methods)}

    # Signature change: payment_method_id from int to str (UUID) for realism
    def set_default_payment_method(self, user: User, payment_method_id: str) -> Dict[str, bool]:
        """
        Set a specific payment method as the default for the current user.

        Args:
            user (User): The current user object.
            payment_method_id (str): The ID (UUID) of the payment method to set as default.

        Returns:
            Dict[str, bool]: {"set_default_status": True} if successful, {"set_default_status": False} otherwise.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"set_default_status": False, "message": "User not found."}

        user_payment_cards = user_data.get("payment_cards", {})
        if payment_method_id not in user_payment_cards:
            return {"set_default_status": False, "message": f"Payment method with ID {payment_method_id} not found."}

        # Clear any existing default for this user
        for card_id, card_info in user_payment_cards.items():
            if card_info.get("is_default"):
                user_payment_cards[card_id]["is_default"] = False
                user_payment_cards[card_id]["last_modified"] = datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"

        user_payment_cards[payment_method_id]["is_default"] = True
        user_payment_cards[payment_method_id]["last_modified"] = datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        self._update_user_data(user, "payment_cards", user_payment_cards)
        return {"set_default_status": True}

    # Signature change: payment_method_id from int to str (UUID) for realism
    def delete_payment_method(self, user: User, payment_method_id: str) -> Dict[str, bool]:
        """
        Delete a specific payment method for the current user.

        Args:
            user (User): The current user object.
            payment_method_id (str): The ID (UUID) of the payment method to delete.

        Returns:
            Dict[str, bool]: {"delete_status": True} if successful, {"delete_status": False} otherwise.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"delete_status": False, "message": "User not found."}

        user_payment_cards = user_data.get("payment_cards", {})
        if payment_method_id not in user_payment_cards:
            return {"delete_status": False, "message": f"Payment method with ID {payment_method_id} not found."}
        
        del user_payment_cards[payment_method_id]
        self._update_user_data(user, "payment_cards", user_payment_cards)
        return {"delete_status": True}

    # ================
    # Notifications
    # ================

    def get_unread_notification_count(self) -> Dict[str, Union[bool, int]]:
        """
        Retrieves the count of unread notifications for the current user.

        Returns:
            Dict: A dictionary containing 'count_status' (bool) and 'unread_count' (int).
        """
        if not self.current_user:
            return {"count_status": False, "unread_count": 0, "message": "No current user set."}
        
        unread_count = sum(1 for notif in self.notifications.values() if notif["user"] == self.current_user and not notif["read"])
        return {"count_status": True, "unread_count": unread_count}

    def delete_all_my_notifications(self) -> Dict[str, bool]:
        """
        Delete all notifications for the current user.

        Returns:
            Dict: A dictionary containing 'delete_status' (bool).
        """
        if not self.current_user:
            return {"delete_status": False, "message": "No current user set."}
        
        to_delete_ids = [nid for nid, notif in self.notifications.items() if notif["user"] == self.current_user]
        for nid in to_delete_ids:
            if nid in self.notifications: # Check before deleting
                del self.notifications[nid]
        
        return {"delete_status": True}

    def mark_my_notifications(self, read_status: bool) -> Dict[str, bool]:
        """
        Mark all notifications for the current user as read or unread.

        Args:
            read_status (bool): Whether to mark as read (True) or unread (False).

        Returns:
            Dict: A dictionary containing 'mark_status' (bool).
        """
        if not self.current_user:
            return {"mark_status": False, "message": "No current user set."}
        
        for notif in self.notifications.values():
            if notif["user"] == self.current_user:
                notif["read"] = read_status
        
        return {"mark_status": True}

    def get_account_analytics(self, user: User) -> Dict[str, Any]:
        """
        Get analytics and summary information for the user's account.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing account analytics.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"analytics_status": False, "analytics": {}}

        user_uuid = user_data["id"]
        
        # Count transactions where user is sender or receiver
        sent_transactions = [t for t in self.transactions.values() if t.get("sender") == user_uuid]
        received_transactions = [t for t in self.transactions.values() if t.get("receiver") == user_uuid]
        
        total_sent = sum(t.get("amount", 0) for t in sent_transactions)
        total_received = sum(t.get("amount", 0) for t in received_transactions)
        
        # Count notifications
        user_notifications = [n for n in self.notifications.values() if n.get("user") == user_uuid]
        unread_notifications = [n for n in user_notifications if not n.get("read", False)]
        
        analytics = {
            "registration_date": user_data.get("registration_date"),
            "last_login_date": user_data.get("last_login_date"),
            "is_premium": user_data.get("is_premium", False),
            "current_balance": user_data.get("balance", 0.0),
            "total_friends": len(user_data.get("friends", [])),
            "total_payment_cards": len(user_data.get("payment_cards", {})),
            "transactions_sent": len(sent_transactions),
            "transactions_received": len(received_transactions),
            "total_amount_sent": round(total_sent, 2),
            "total_amount_received": round(total_received, 2),
            "net_amount": round(total_received - total_sent, 2),
            "total_notifications": len(user_notifications),
            "unread_notifications": len(unread_notifications)
        }
        
        return {"analytics_status": True, "analytics": analytics}

    def get_transaction_history(self, user: User, limit: int = 50) -> Dict[str, Any]:
        """
        Get transaction history for the user.

        Args:
            user (User): The current user object.
            limit (int): Maximum number of transactions to return.

        Returns:
            Dict: A dictionary containing transaction history.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"history_status": False, "transactions": []}

        user_uuid = user_data["id"]
        
        # Get all transactions involving the user
        user_transactions = []
        for transaction in self.transactions.values():
            if transaction.get("sender") == user_uuid or transaction.get("receiver") == user_uuid:
                # Add transaction direction for clarity
                transaction_copy = copy.deepcopy(transaction)
                if transaction.get("sender") == user_uuid:
                    transaction_copy["direction"] = "sent"
                    # Get receiver info
                    receiver_data = self.users.get(transaction.get("receiver"))
                    if receiver_data:
                        transaction_copy["other_party"] = {
                            "email": receiver_data.get("email"),
                            "name": f"{receiver_data.get('first_name', '')} {receiver_data.get('last_name', '')}".strip()
                        }
                else:
                    transaction_copy["direction"] = "received"
                    # Get sender info  
                    sender_data = self.users.get(transaction.get("sender"))
                    if sender_data:
                        transaction_copy["other_party"] = {
                            "email": sender_data.get("email"),
                            "name": f"{sender_data.get('first_name', '')} {sender_data.get('last_name', '')}".strip()
                        }
                
                user_transactions.append(transaction_copy)
        
        # Sort by timestamp (most recent first)
        user_transactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "history_status": True, 
            "transactions": user_transactions[:limit],
            "total_transactions": len(user_transactions)
        }

    def upgrade_to_premium(self, user: User) -> Dict[str, bool]:
        """
        Upgrade user account to premium status.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary indicating success status.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"upgrade_status": False, "message": "User not found."}

        if user_data.get("is_premium", False):
            return {"upgrade_status": False, "message": "User is already premium."}

        user_data["is_premium"] = True
        user_data["last_login_date"] = datetime.datetime.now().isoformat() + "Z"
        
        return {"upgrade_status": True, "message": "Successfully upgraded to premium."}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self._load_scenario(DEFAULT_STATE)
        print("VenmoApis: All dummy data reset to default state.")
        return {"reset_status": True}