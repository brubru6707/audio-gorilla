# Inspired by AppWorld

import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("VenmoApis")

class User:
    def __init__(self, email: str):
        self.email = email

class VenmoApis:
    """
    An API class for simulating Venmo operations.
    This class provides an in-memory backend for development and testing purposes.
    Matches the real Venmo API structure and authentication.
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
        self.access_token: Optional[str] = None
        self.current_user_id: Optional[str] = None
        
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain "users", "transactions", "notifications".
        """
        # Create deep copy to ensure the original DEFAULT_STATE is not modified
        self.users = copy.deepcopy(scenario.get("users", {}))
        self.transactions = copy.deepcopy(scenario.get("transactions", {}))
        self.notifications = copy.deepcopy(scenario.get("notifications", {}))

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for entities.
        """
        return str(uuid.uuid4())

    def authenticate(self, access_token: str) -> Dict[str, Any]:
        """
        Authenticates with Venmo API using OAuth 2.0 access token.
        Simulates token validation and user identification.
        
        Args:
            access_token: OAuth 2.0 access token (format: "token_{email}")
        
        Returns:
            User profile object
            
        Raises:
            Exception: If token is invalid
        """
        # Validate token format
        if not access_token or not access_token.startswith("token_"):
            raise Exception("Invalid access token")
        
        # Extract user email from token
        email = access_token.replace("token_", "")
        
        # Find user by email
        user_id = None
        for uid, user_data in self.users.items():
            if user_data.get("email") == email:
                user_id = uid
                break
        
        if not user_id:
            raise Exception("Invalid access token - user not found")
        
        # Set authenticated user
        self.access_token = access_token
        self.current_user_id = user_id
        
        # Return user profile (matching Venmo API structure)
        return self._get_enriched_user(self.users[user_id])

    def _ensure_authenticated(self) -> None:
        """
        Verifies that a user is authenticated before accessing protected resources.
        
        Raises:
            Exception: If no user is authenticated
        """
        if not self.access_token or not self.current_user_id:
            raise Exception("Authentication required - call authenticate() first")

    def _enrich_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches user data with standard Venmo API fields.
        
        Args:
            user_data: Raw user data from backend
            
        Returns:
            Enriched user data with standard Venmo fields
        """
        # Generate username from email or name
        email = user_data.get("email", "")
        username = email.split("@")[0] if email else f"user_{user_data.get('id', '')[:8]}"
        
        # Generate display name
        first_name = user_data.get("first_name", "")
        last_name = user_data.get("last_name", "")
        display_name = f"{first_name} {last_name}".strip() or username
        
        enriched = copy.deepcopy(user_data)
        enriched.update({
            "username": username,
            "display_name": display_name,
            "profile_picture_url": f"https://venmo.s3.amazonaws.com/no-image.gif",
            "date_created": user_data.get("registration_date", datetime.datetime.now().isoformat() + "Z"),
            "phone": None,  # Privacy - not exposed
        })
        
        return enriched

    def _get_enriched_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns enriched user data for API responses.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            User object with standard Venmo fields
        """
        enriched = self._enrich_user(user_data)
        return {
            "id": enriched["id"],
            "username": enriched["username"],
            "display_name": enriched["display_name"],
            "first_name": enriched.get("first_name"),
            "last_name": enriched.get("last_name"),
            "profile_picture_url": enriched["profile_picture_url"],
            "date_created": enriched["date_created"],
            "email": enriched.get("email"),
        }

    def _get_user_uuid_from_email(self, email: str) -> Optional[str]:
        """Helper to get user UUID from email."""
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def get_profile(self) -> Dict[str, Any]:
        """
        Gets the authenticated user's profile.
        Matches GET /v1/me endpoint.

        Returns:
            User profile object
            
        Raises:
            Exception: If not authenticated
        """
        self._ensure_authenticated()
        user_data = self.users[self.current_user_id]
        
        enriched = self._get_enriched_user(user_data)
        enriched["balance"] = user_data.get("balance", 0.0)
        enriched["friends_count"] = len(user_data.get("friends", []))
        enriched["is_premium"] = user_data.get("is_premium", False)
        
        return enriched

    def get_friends(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Lists the friends of the authenticated user.
        Matches GET /v1/users/{user_id}/friends endpoint.

        Args:
            limit: Maximum number of friends to return
            offset: Number of friends to skip (for pagination)

        Returns:
            Paginated list of friend objects
            
        Raises:
            Exception: If not authenticated
        """
        self._ensure_authenticated()
        user_data = self.users[self.current_user_id]
        
        friend_uuids = user_data.get("friends", [])
        friends_list = []
        for friend_uuid in friend_uuids[offset:offset + limit]:
            friend_data = self.users.get(friend_uuid)
            if friend_data:
                friends_list.append(self._get_enriched_user(friend_data))
        
        return {
            "data": friends_list,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(friend_uuids)
            }
        }

    def create_payment(
        self, 
        user_id: str,
        amount: float, 
        note: str,
        audience: str = "private",
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends money from the authenticated user to another user.
        Matches POST /v1/payments endpoint.

        Args:
            user_id: The ID or email of the receiver
            amount: The amount of money to send
            note: A note for the transaction
            audience: Privacy level - "public", "friends", or "private"
            payment_method_id: Specific payment method ID to use

        Returns:
            Payment object
            
        Raises:
            Exception: If not authenticated or validation fails
        """
        self._ensure_authenticated()
        sender_data = self.users[self.current_user_id]
        
        # Find receiver by ID or email
        receiver_uuid = user_id if user_id in self.users else self._get_user_uuid_from_email(user_id)
        if not receiver_uuid or receiver_uuid not in self.users:
            raise Exception(f"User {user_id} not found")
        
        receiver_data = self.users[receiver_uuid]
        
        # Validate audience
        if audience not in ["public", "friends", "private"]:
            raise Exception("Invalid audience. Must be 'public', 'friends', or 'private'")
        
        # Validate payment method if specified
        if payment_method_id:
            user_payment_methods = sender_data.get("payment_methods", {})
            if payment_method_id not in user_payment_methods:
                raise Exception("Invalid payment method ID")
        
        if sender_data["balance"] < amount:
            raise Exception("Insufficient balance")
        if amount <= 0:
            raise Exception("Amount must be positive")

        sender_data["balance"] -= amount
        receiver_data["balance"] += amount

        transaction_id = self._generate_unique_id()
        timestamp = datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        
        new_transaction = {
            "id": transaction_id,
            "payment_id": transaction_id,  # Venmo uses payment_id
            "status": "settled",
            "date_created": timestamp,
            "date_completed": timestamp,
            "date_updated": timestamp,
            "amount": amount,
            "note": note,
            "audience": audience,
            "action": "pay",
            "actor": self._get_enriched_user(sender_data),
            "target": {
                "type": "user",
                "user": self._get_enriched_user(receiver_data),
            },
            "payment_method_id": payment_method_id,
        }
        self.transactions[transaction_id] = new_transaction
        
        return new_transaction

    def create_charge(
        self, 
        user_id: str,
        amount: float, 
        note: str,
        audience: str = "private"
    ) -> Dict[str, Any]:
        """
        Requests money from another user (creates a charge/payment request).
        Matches POST /v1/payments endpoint with type=charge.

        Args:
            user_id: The ID or email of the user to request money from
            amount: The amount of money to request
            note: A note for the request
            audience: Privacy level - "public", "friends", or "private"

        Returns:
            Payment request object
            
        Raises:
            Exception: If not authenticated or validation fails
        """
        self._ensure_authenticated()
        requester_data = self.users[self.current_user_id]
        
        # Find payer by ID or email
        payer_uuid = user_id if user_id in self.users else self._get_user_uuid_from_email(user_id)
        if not payer_uuid or payer_uuid not in self.users:
            raise Exception(f"User {user_id} not found")
        
        payer_data = self.users[payer_uuid]
        
        # Validate audience
        if audience not in ["public", "friends", "private"]:
            raise Exception("Invalid audience. Must be 'public', 'friends', or 'private'")
        
        if amount <= 0:
            raise Exception("Amount must be positive")

        transaction_id = self._generate_unique_id()
        timestamp = datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        
        new_transaction = {
            "id": transaction_id,
            "payment_id": transaction_id,
            "status": "pending",
            "date_created": timestamp,
            "date_updated": timestamp,
            "amount": amount,
            "note": note,
            "audience": audience,
            "action": "charge",
            "actor": self._get_enriched_user(requester_data),
            "target": {
                "type": "user",
                "user": self._get_enriched_user(payer_data),
            },
        }
        self.transactions[transaction_id] = new_transaction
        
        return new_transaction
    
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Retrieves details of a specific payment/transaction.
        Matches GET /v1/payments/{payment_id} endpoint.

        Args:
            payment_id: The ID of the payment

        Returns:
            Payment object
            
        Raises:
            Exception: If payment not found
        """
        payment = self.transactions.get(payment_id)
        if not payment:
            raise Exception(f"Payment {payment_id} not found")
        return copy.deepcopy(payment)

    def get_transactions(
        self, 
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lists transactions for the authenticated user.
        Matches GET /v1/payments endpoint.

        Args:
            limit: Maximum number of transactions to return (default 50)
            offset: Number of transactions to skip for pagination (default 0)
            status: Filter by status - "settled", "pending", "cancelled" (optional)

        Returns:
            Paginated transaction list
            
        Raises:
            Exception: If not authenticated
        """
        self._ensure_authenticated()
        user_data = self.users[self.current_user_id]

        user_transactions = []
        for t in self.transactions.values():
            # Include if user is actor or target
            actor_id = None
            if isinstance(t.get("actor"), dict):
                actor_id = t["actor"].get("id")
            
            target_id = None
            if isinstance(t.get("target"), dict):
                target_user = t["target"].get("user", {})
                if isinstance(target_user, dict):
                    target_id = target_user.get("id")
            
            if actor_id != user_data["id"] and target_id != user_data["id"]:
                continue
            
            # Apply status filter
            if status and t.get("status") != status:
                continue
            
            user_transactions.append(copy.deepcopy(t))
        
        # Sort by date_created (most recent first)
        user_transactions.sort(key=lambda x: x.get("date_created", ""), reverse=True)
        
        # Apply pagination
        total = len(user_transactions)
        paginated_transactions = user_transactions[offset:offset + limit]
        
        return {
            "data": paginated_transactions,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total
            }
        }

    def add_payment_method(
        self,
        card_number: str, 
        expiry_month: int,
        expiry_year: int,
        cvv: str,
        billing_zip: str
    ) -> Dict[str, Any]:
        """
        Adds a new payment method (credit/debit card) to the authenticated user's account.
        Matches POST /v1/payment-methods endpoint.

        Args:
            card_number: Full card number (will be masked in storage)
            expiry_month: Card expiry month (1-12)
            expiry_year: Card expiry year (YYYY)
            cvv: CVV code (not stored)
            billing_zip: Billing ZIP code

        Returns:
            Payment method object
            
        Raises:
            Exception: If not authenticated or validation fails
        """
        self._ensure_authenticated()
        user_data = self.users[self.current_user_id]

        # Basic validation
        if not (1 <= expiry_month <= 12):
            raise Exception("Invalid expiry month. Must be 1-12.")
        
        current_year = datetime.datetime.now().year
        if not (current_year <= expiry_year <= current_year + 20):
            raise Exception(f"Invalid expiry year. Must be between {current_year} and {current_year + 20}.")
        
        if len(cvv) not in [3, 4]:
            raise Exception("Invalid CVV. Must be 3 or 4 digits.")
        
        # Mask card number for storage (only last 4 digits visible)
        last_four = card_number[-4:] if len(card_number) >= 4 else card_number
        
        # Determine card type from first digit
        first_digit = card_number[0] if card_number else ""
        card_type = "unknown"
        if first_digit == "4":
            card_type = "visa"
        elif first_digit == "5":
            card_type = "mastercard"
        elif first_digit in ["3", "6"]:
            card_type = "discover"

        payment_method_id = self._generate_unique_id()
        timestamp = datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        
        new_payment_method = {
            "id": payment_method_id,
            "type": "card",
            "card": {
                "last_four": last_four,
                "brand": card_type,
                "expiration_month": expiry_month,
                "expiration_year": expiry_year
            },
            "is_default": False,
            "date_created": timestamp
        }

        user_payment_methods = user_data.get("payment_methods", {})
        user_payment_methods[payment_method_id] = new_payment_method
        user_data["payment_methods"] = user_payment_methods

        return copy.deepcopy(new_payment_method)

    def get_payment_methods(self) -> List[Dict[str, Any]]:
        """
        Lists all payment methods for the authenticated user.
        Matches GET /v1/payment-methods endpoint.

        Returns:
            List of payment method objects
            
        Raises:
            Exception: If not authenticated
        """
        self._ensure_authenticated()
        user_data = self.users[self.current_user_id]
        payment_methods = list(user_data.get("payment_methods", {}).values())
        return copy.deepcopy(payment_methods)

    def set_default_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """
        Sets a specific payment method as the default for the authenticated user.
        Matches PUT /v1/payment-methods/{payment_method_id}/default endpoint.

        Args:
            payment_method_id: The ID of the payment method to set as default

        Returns:
            Updated payment method object
            
        Raises:
            Exception: If not authenticated or payment method not found
        """
        self._ensure_authenticated()
        user_data = self.users[self.current_user_id]

        user_payment_methods = user_data.get("payment_methods", {})
        if payment_method_id not in user_payment_methods:
            raise Exception(f"Payment method {payment_method_id} not found")

        # Clear any existing default
        for _, pm_data in user_payment_methods.items():
            pm_data["is_default"] = False

        # Set new default
        user_payment_methods[payment_method_id]["is_default"] = True
        return copy.deepcopy(user_payment_methods[payment_method_id])

    def delete_payment_method(self, payment_method_id: str) -> None:
        """
        Deletes a payment method for the authenticated user.
        Matches DELETE /v1/payment-methods/{payment_method_id} endpoint.

        Args:
            payment_method_id: The ID of the payment method to delete

        Raises:
            Exception: If not authenticated or payment method not found
        """
        self._ensure_authenticated()
        user_data = self.users[self.current_user_id]

        user_payment_methods = user_data.get("payment_methods", {})
        if payment_method_id not in user_payment_methods:
            raise Exception(f"Payment method {payment_method_id} not found")
        
        del user_payment_methods[payment_method_id]

    # ================
    # Notifications
    # ================

    def get_unread_notification_count(self) -> int:
        """
        Retrieves the count of unread notifications for the authenticated user.

        Returns:
            Count of unread notifications
            
        Raises:
            Exception: If not authenticated
        """
        self._ensure_authenticated()
        unread_count = sum(
            1 for notif in self.notifications.values() 
            if notif["user"] == self.current_user_id and not notif["read"]
        )
        return unread_count

    def delete_all_notifications(self) -> None:
        """
        Deletes all notifications for the authenticated user.

        Raises:
            Exception: If not authenticated
        """
        self._ensure_authenticated()
        to_delete_ids = [
            nid for nid, notif in self.notifications.items() 
            if notif["user"] == self.current_user_id
        ]
        for nid in to_delete_ids:
            if nid in self.notifications:
                del self.notifications[nid]

    def mark_notifications_as_read(self, read_status: bool = True) -> None:
        """
        Marks all notifications for the authenticated user as read or unread.

        Args:
            read_status: Whether to mark as read (True) or unread (False)

        Raises:
            Exception: If not authenticated
        """
        self._ensure_authenticated()
        for notif in self.notifications.values():
            if notif["user"] == self.current_user_id:
                notif["read"] = read_status

    # ================
    # Analytics & Premium
    # ================

    def get_account_balance(self) -> float:
        """
        Gets the current Venmo balance for the authenticated user.
        Matches GET /v1/me/balance endpoint.

        Returns:
            Account balance
            
        Raises:
            Exception: If not authenticated
        """
        self._ensure_authenticated()
        user_data = self.users[self.current_user_id]
        return user_data.get("balance", 0.0)

    def get_transaction_history(
        self,
        limit: int = 50,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gets transaction history with analytics for the authenticated user.
        Custom endpoint that combines transaction listing with summary stats.

        Args:
            limit: Maximum number of transactions to return
            start_date: Filter transactions after this date (ISO format, optional)
            end_date: Filter transactions before this date (ISO format, optional)

        Returns:
            Transaction history with analytics
            
        Raises:
            Exception: If not authenticated
        """
        self._ensure_authenticated()
        user_data = self.users[self.current_user_id]
        user_id = user_data["id"]
        
        # Get all transactions involving the user
        user_transactions = []
        for transaction in self.transactions.values():
            # Check if user is involved
            actor_id = None
            if isinstance(transaction.get("actor"), dict):
                actor_id = transaction["actor"].get("id")
            
            target_id = None
            if isinstance(transaction.get("target"), dict):
                target_user = transaction["target"].get("user", {})
                if isinstance(target_user, dict):
                    target_id = target_user.get("id")
            
            if actor_id != user_id and target_id != user_id:
                continue
            
            # Apply date filters
            tx_date = transaction.get("date_created", "")
            if start_date and tx_date < start_date:
                continue
            if end_date and tx_date > end_date:
                continue
            
            # Add direction info
            transaction_copy = copy.deepcopy(transaction)
            if actor_id == user_id:
                transaction_copy["direction"] = "sent"
            else:
                transaction_copy["direction"] = "received"
            
            user_transactions.append(transaction_copy)
        
        # Sort by date (most recent first)
        user_transactions.sort(key=lambda x: x.get("date_created", ""), reverse=True)
        
        # Calculate analytics
        total_sent = sum(
            t.get("amount", 0) for t in user_transactions 
            if t.get("direction") == "sent" and t.get("status") == "settled"
        )
        total_received = sum(
            t.get("amount", 0) for t in user_transactions 
            if t.get("direction") == "received" and t.get("status") == "settled"
        )
        
        return {
            "transactions": user_transactions[:limit],
            "analytics": {
                "total_count": len(user_transactions),
                "total_sent": round(total_sent, 2),
                "total_received": round(total_received, 2),
                "net_amount": round(total_received - total_sent, 2)
            }
        }

    def reset_data(self) -> None:
        """
        Resets all simulated data to default state.
        This is a utility function for testing, not a standard API endpoint.
        """
        self._load_scenario(DEFAULT_STATE)
        self.access_token = None
        self.current_user_id = None
        print("VenmoApis: All data reset to default state.")