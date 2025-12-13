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
        Initializes the VenmoApis instance with in-memory data stores for simulating Venmo operations.
        
        Sets up empty dictionaries for users, transactions, and notifications, then loads the default
        scenario data. This simulated backend allows for testing Venmo payment workflows without
        connecting to actual Venmo servers.
        
        Side Effects:
            - Creates empty data stores for users, transactions, and notifications
            - Loads default state from scenario file
            - Initializes authentication state (no user authenticated)
        
        Note:
            This is a simulation class for development/testing. All data is stored in memory
            and will be lost when the instance is destroyed.
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
        Loads a predefined scenario into the backend's state for testing or initialization.
        
        Replaces all current data (users, transactions, notifications) with the provided scenario
        data. Creates deep copies to ensure the source scenario object remains unmodified.
        This is useful for resetting state between tests or loading specific test scenarios.

        Args:
            scenario (Dict): A dictionary containing the complete state to load. Expected keys:
                - "users" (Dict[str, Any]): User data keyed by UUID
                - "transactions" (Dict[str, Any]): Transaction data keyed by transaction UUID
                - "notifications" (Dict[str, Any]): Notification data keyed by notification UUID
                
        Side Effects:
            - Completely replaces users, transactions, and notifications data
            - Does NOT reset authentication state (access_token, current_user_id)
            
        Note:
            Uses deep copy to prevent accidental modification of the source scenario.
        """
        # Create deep copy to ensure the original DEFAULT_STATE is not modified
        self.users = copy.deepcopy(scenario.get("users", {}))
        self.transactions = copy.deepcopy(scenario.get("transactions", {}))
        self.notifications = copy.deepcopy(scenario.get("notifications", {}))

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID string for creating new entities (users, transactions, notifications).
        
        Uses Python's uuid.uuid4() to generate a random UUID, ensuring global uniqueness
        across all entity types in the simulated backend.
        
        Returns:
            str: A UUID string in standard format (e.g., "550e8400-e29b-41d4-a716-446655440000")
            
        Note:
            This is used internally for all entity creation to guarantee unique identifiers.
        """
        return str(uuid.uuid4())

    def authenticate(self, access_token: str) -> Dict[str, Any]:
        """
        Authenticates a user with the Venmo API using an OAuth 2.0 access token.
        
        Simulates the Venmo OAuth 2.0 authentication flow. Validates the token format,
        extracts the user email from the token, locates the corresponding user in the
        backend, and establishes an authenticated session.
        
        Args:
            access_token (str): OAuth 2.0 access token in format "token_{email}"
                Example: "token_alice@example.com" for user with that email
        
        Returns:
            Dict[str, Any]: Authenticated user's profile object with structure:
                {
                    "id": str,                      # User UUID
                    "username": str,                # Generated from email
                    "display_name": str,            # Full name or username
                    "first_name": str,              # User's first name
                    "last_name": str,               # User's last name
                    "profile_picture_url": str,     # Profile picture URL
                    "date_created": str,            # ISO 8601 timestamp
                    "email": str                    # User's email address
                }
            
        Raises:
            Exception: If token format is invalid (doesn't start with "token_")
            Exception: If no user exists with the email extracted from the token
            
        Side Effects:
            - Sets self.access_token to the provided token
            - Sets self.current_user_id to the authenticated user's UUID
            - Subsequent API calls will be made in context of this user
            
        Example:
            >>> api = VenmoApis()
            >>> profile = api.authenticate("token_alice@example.com")
            >>> print(profile["username"])  # "alice"
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
        Internal guard method that verifies a user is authenticated before accessing protected resources.
        
        Checks that both access_token and current_user_id are set, indicating a successful
        authentication. This should be called at the start of every method that requires authentication.
        
        Raises:
            Exception: If either access_token or current_user_id is None (user not authenticated)
                Error message: "Authentication required - call authenticate() first"
                
        Note:
            This is an internal helper method used by all protected endpoints.
        """
        if not self.access_token or not self.current_user_id:
            raise Exception("Authentication required - call authenticate() first")

    def _enrich_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches raw backend user data with standard Venmo API fields for consistent responses.
        
        Transforms minimal backend user data into the full structure expected by the Venmo API.
        Generates username from email, creates display name from first/last name, adds
        default profile picture URL, and normalizes timestamps.
        
        Args:
            user_data (Dict[str, Any]): Raw user data from backend containing:
                - "id": User UUID
                - "email": User email (optional)
                - "first_name": First name (optional)
                - "last_name": Last name (optional)
                - "registration_date": Registration timestamp (optional)
            
        Returns:
            Dict[str, Any]: Enriched user data with additional fields:
                - "username": Generated from email (part before @) or "user_{id_prefix}"
                - "display_name": "{first_name} {last_name}" or username if name missing
                - "profile_picture_url": Default Venmo placeholder image URL
                - "date_created": ISO 8601 timestamp (from registration_date or now)
                - "phone": Always None (privacy)
                Plus all original fields from user_data
                
        Note:
            This is an internal helper that doesn't modify the original user_data dict.
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
        Returns a standardized user object suitable for inclusion in API responses.
        
        Calls _enrich_user() to add computed fields, then returns only the public-facing
        subset of user data appropriate for API responses (excludes sensitive fields like
        balance, payment methods, etc.).
        
        Args:
            user_data (Dict[str, Any]): Raw user data from backend
            
        Returns:
            Dict[str, Any]: Public user profile object with fields:
                {
                    "id": str,                      # User UUID
                    "username": str,                # Generated username
                    "display_name": str,            # Full name or username
                    "first_name": str,              # First name
                    "last_name": str,               # Last name
                    "profile_picture_url": str,     # Profile picture URL
                    "date_created": str,            # ISO 8601 registration timestamp
                    "email": str                    # Email address
                }
                
        Note:
            This creates a clean public profile without sensitive financial data.
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
        """
        Internal helper that looks up a user's UUID by their email address.
        
        Iterates through all users in the backend to find one with a matching email.
        This enables user lookup by email in addition to UUID for convenience.
        
        Args:
            email (str): The email address to search for
            
        Returns:
            Optional[str]: The user's UUID if found, None if no user has that email
            
        Note:
            This performs a linear search through all users. For production systems,
            an email-to-UUID index would be more efficient.
        """
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def get_profile(self) -> Dict[str, Any]:
        """
        Retrieves the complete profile for the currently authenticated user.
        
        Matches the Venmo API GET /v1/me endpoint. Returns the user's public profile
        information plus private financial data (balance) and social statistics.

        Returns:
            Dict[str, Any]: Complete user profile with structure:
                {
                    "id": str,                      # User UUID
                    "username": str,                # Generated username
                    "display_name": str,            # Full name or username
                    "first_name": str,              # First name
                    "last_name": str,               # Last name
                    "profile_picture_url": str,     # Profile picture URL
                    "date_created": str,            # ISO 8601 registration timestamp
                    "email": str,                   # Email address
                    "balance": float,               # Current Venmo balance in USD
                    "friends_count": int,           # Number of friends
                    "is_premium": bool              # Premium account status
                }
            
        Raises:
            Exception: If not authenticated (no user logged in)
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> profile = api.get_profile()
            >>> print(f"Balance: ${profile['balance']:.2f}")  # "Balance: $100.00"
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
        Lists the friends of the authenticated user with pagination support.
        
        Matches the Venmo API GET /v1/users/{user_id}/friends endpoint. Returns a paginated
        list of user objects representing the authenticated user's friends in the Venmo network.

        Args:
            limit (int, optional): Maximum number of friends to return per page. Defaults to 50.
                Valid range: 1-200
            offset (int, optional): Number of friends to skip from the start (for pagination).
                Defaults to 0. Use this to fetch subsequent pages:
                - Page 1: offset=0, limit=50
                - Page 2: offset=50, limit=50
                - Page 3: offset=100, limit=50

        Returns:
            Dict[str, Any]: Paginated response with structure:
                {
                    "data": List[Dict[str, Any]],  # List of friend user objects (see _get_enriched_user)
                    "pagination": {
                        "limit": int,               # Items per page (echoed from input)
                        "offset": int,              # Current offset (echoed from input)
                        "total": int                # Total number of friends (all pages)
                    }
                }
            
        Raises:
            Exception: If not authenticated (no user logged in)
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> response = api.get_friends(limit=10, offset=0)
            >>> print(f"Showing {len(response['data'])} of {response['pagination']['total']} friends")
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
        Sends money from the authenticated user to another user (creates a payment transaction).
        
        Matches the Venmo API POST /v1/payments endpoint. Transfers the specified amount from
        the authenticated user's Venmo balance to the recipient's balance. The transaction is
        immediately settled (completed).

        Args:
            user_id (str): The recipient's user ID (UUID) or email address.
                Accepts either format:
                - UUID: "550e8400-e29b-41d4-a716-446655440000"
                - Email: "bob@example.com"
            amount (float): The amount of money to send in USD. Must be positive.
                Example: 25.50 for $25.50
            note (str): A message/description for the payment.
                Required by Venmo to provide context for the transaction.
                Example: "Dinner last night" or "Rent payment"
            audience (str, optional): Privacy level for the transaction. Defaults to "private".
                Valid values:
                - "public": Visible to everyone on Venmo
                - "friends": Visible only to your Venmo friends
                - "private": Visible only to you and the recipient
            payment_method_id (Optional[str], optional): Specific payment method to use.
                If None, uses the default or Venmo balance. Defaults to None.

        Returns:
            Dict[str, Any]: Payment transaction object with structure:
                {
                    "id": str,                      # Transaction UUID
                    "payment_id": str,              # Same as id (Venmo convention)
                    "status": "settled",            # Transaction completed immediately
                    "date_created": str,            # ISO 8601 timestamp with milliseconds
                    "date_completed": str,          # ISO 8601 timestamp (same as created)
                    "date_updated": str,            # ISO 8601 timestamp
                    "amount": float,                # Payment amount in USD
                    "note": str,                    # Payment description
                    "audience": str,                # Privacy level
                    "action": "pay",                # Always "pay" for payments
                    "actor": Dict[str, Any],        # Sender's user profile (enriched)
                    "target": {                     # Recipient information
                        "type": "user",
                        "user": Dict[str, Any]      # Recipient's user profile (enriched)
                    },
                    "payment_method_id": str        # Payment method used (or None)
                }
            
        Raises:
            Exception: If not authenticated (no user logged in)
            Exception: If recipient user_id/email not found in system
            Exception: If audience is not one of: "public", "friends", "private"
            Exception: If payment_method_id is provided but doesn't exist for the user
            Exception: If sender's balance is insufficient for the payment amount
            Exception: If amount is not positive (must be > 0)
            
        Side Effects:
            - Deducts amount from authenticated user's balance
            - Adds amount to recipient's balance
            - Creates new transaction record in system
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> payment = api.create_payment(
            ...     user_id="bob@example.com",
            ...     amount=25.50,
            ...     note="Dinner last night",
            ...     audience="friends"
            ... )
            >>> print(f"Sent ${payment['amount']} to {payment['target']['user']['display_name']}")
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
        
        Matches the Venmo API POST /v1/payments endpoint with type=charge. Unlike create_payment(),
        this creates a pending request that the other user must approve. No money is transferred
        immediately; the transaction remains in "pending" status until the recipient pays.

        Args:
            user_id (str): The user ID (UUID) or email address of the person to request money from.
                Accepts either format:
                - UUID: "550e8400-e29b-41d4-a716-446655440000"
                - Email: "charlie@example.com"
            amount (float): The amount of money to request in USD. Must be positive.
                Example: 15.00 for $15.00
            note (str): A message explaining why you're requesting money.
                Required by Venmo to provide context.
                Example: "Your share of the pizza" or "Concert ticket"
            audience (str, optional): Privacy level for the request. Defaults to "private".
                Valid values:
                - "public": Visible to everyone on Venmo
                - "friends": Visible only to your Venmo friends
                - "private": Visible only to you and the recipient

        Returns:
            Dict[str, Any]: Payment request transaction object with structure:
                {
                    "id": str,                      # Transaction UUID
                    "payment_id": str,              # Same as id (Venmo convention)
                    "status": "pending",            # Awaiting recipient approval
                    "date_created": str,            # ISO 8601 timestamp with milliseconds
                    "date_updated": str,            # ISO 8601 timestamp
                    "amount": float,                # Requested amount in USD
                    "note": str,                    # Request description
                    "audience": str,                # Privacy level
                    "action": "charge",             # Always "charge" for requests
                    "actor": Dict[str, Any],        # Requester's user profile (enriched)
                    "target": {                     # Recipient information
                        "type": "user",
                        "user": Dict[str, Any]      # Payer's user profile (enriched)
                    }
                }
                Note: No "date_completed" field since transaction is pending
            
        Raises:
            Exception: If not authenticated (no user logged in)
            Exception: If payer user_id/email not found in system
            Exception: If audience is not one of: "public", "friends", "private"
            Exception: If amount is not positive (must be > 0)
            
        Side Effects:
            - Creates new pending transaction record in system
            - No balance changes until request is paid
            
        Note:
            In the real Venmo API, the recipient would receive a notification and could
            approve or deny the request. This simulation creates the request but doesn't
            implement the approval workflow.
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> charge = api.create_charge(
            ...     user_id="bob@example.com",
            ...     amount=30.00,
            ...     note="Your half of the Uber",
            ...     audience="private"
            ... )
            >>> print(f"Requested ${charge['amount']} from {charge['target']['user']['display_name']}")
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
        Retrieves detailed information about a specific payment or charge transaction.
        
        Matches the Venmo API GET /v1/payments/{payment_id} endpoint. Returns the complete
        transaction object including sender, recipient, amount, status, and timestamps.

        Args:
            payment_id (str): The unique identifier (UUID) of the payment/charge to retrieve.
                This is the "id" or "payment_id" field from a transaction object.
                Example: "550e8400-e29b-41d4-a716-446655440000"

        Returns:
            Dict[str, Any]: Complete payment/charge transaction object. Structure varies by action:
                
                For payments (action="pay"):
                {
                    "id": str,
                    "payment_id": str,
                    "status": "settled",
                    "date_created": str,
                    "date_completed": str,
                    "date_updated": str,
                    "amount": float,
                    "note": str,
                    "audience": str,
                    "action": "pay",
                    "actor": Dict[str, Any],        # Sender profile
                    "target": Dict[str, Any],       # Recipient profile
                    "payment_method_id": str
                }
                
                For charges (action="charge"):
                {
                    "id": str,
                    "payment_id": str,
                    "status": "pending",
                    "date_created": str,
                    "date_updated": str,
                    "amount": float,
                    "note": str,
                    "audience": str,
                    "action": "charge",
                    "actor": Dict[str, Any],        # Requester profile
                    "target": Dict[str, Any]        # Payer profile
                }
            
        Raises:
            Exception: If payment_id doesn't exist in the system
                Error message: "Payment {payment_id} not found"
            
        Note:
            This method doesn't require the authenticated user to be involved in the
            transaction (no authentication check). In a production system, you'd
            typically restrict access to transactions the user is involved in.
            
        Example:
            >>> payment = api.get_payment("550e8400-e29b-41d4-a716-446655440000")
            >>> print(f"{payment['action']}: ${payment['amount']} - {payment['note']}")
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
        Lists all transactions for the authenticated user with filtering and pagination.
        
        Matches the Venmo API GET /v1/payments endpoint. Returns transactions where the
        authenticated user is either the sender (actor) or recipient (target). Results
        are sorted by creation date (most recent first) and support status filtering.

        Args:
            limit (int, optional): Maximum number of transactions to return per page.
                Defaults to 50. Valid range: 1-200
            offset (int, optional): Number of transactions to skip from the start (for pagination).
                Defaults to 0. Use to fetch subsequent pages:
                - Page 1: offset=0, limit=50
                - Page 2: offset=50, limit=50
            status (Optional[str], optional): Filter transactions by status. Defaults to None (all).
                Valid values:
                - "settled": Completed payments (money transferred)
                - "pending": Pending payment requests (awaiting approval)
                - "cancelled": Cancelled transactions
                - None: Returns all transactions regardless of status

        Returns:
            Dict[str, Any]: Paginated transaction list with structure:
                {
                    "data": List[Dict[str, Any]],  # List of transaction objects
                    "pagination": {
                        "limit": int,               # Items per page (echoed from input)
                        "offset": int,              # Current offset (echoed from input)
                        "total": int                # Total matching transactions (all pages)
                    }
                }
                
                Each transaction object has the structure described in get_payment().
            
        Raises:
            Exception: If not authenticated (no user logged in)
            
        Side Effects:
            None - read-only operation
            
        Note:
            - Transactions are always sorted by date_created (descending/newest first)
            - Includes both sent and received transactions
            - The status filter is applied after user filtering, before pagination
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> # Get first page of all transactions
            >>> response = api.get_transactions(limit=10)
            >>> print(f"Showing {len(response['data'])} of {response['pagination']['total']}")
            >>> 
            >>> # Get only pending payment requests
            >>> pending = api.get_transactions(status="pending")
            >>> for tx in pending['data']:
            ...     print(f"Pending ${tx['amount']}: {tx['note']}")
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
        Adds a new credit or debit card as a payment method for the authenticated user.
        
        Matches the Venmo API POST /v1/payment-methods endpoint. Validates card information,
        masks the card number for security (only stores last 4 digits), determines card brand
        from the card number, and stores the payment method for future use.

        Args:
            card_number (str): Full credit/debit card number (will be masked after validation).
                Typically 13-19 digits. Example: "4532123456789012"
            expiry_month (int): Card expiration month as integer.
                Valid range: 1-12 (January=1, December=12)
            expiry_year (int): Card expiration year as 4-digit integer.
                Valid range: current_year to current_year+20
                Example: 2027
            cvv (str): Card verification value (CVV/CVC code).
                Must be 3 digits (most cards) or 4 digits (American Express)
                NOT stored after validation (security requirement)
            billing_zip (str): Billing ZIP code associated with the card.
                Used for address verification. Example: "10001"

        Returns:
            Dict[str, Any]: Payment method object with structure:
                {
                    "id": str,                      # Unique payment method UUID
                    "type": "card",                 # Always "card" for card payments
                    "card": {
                        "last_four": str,           # Last 4 digits of card (masked)
                        "brand": str,               # Card brand: "visa", "mastercard", "discover", "unknown"
                        "expiration_month": int,    # Expiry month (1-12)
                        "expiration_year": int      # Expiry year (4 digits)
                    },
                    "is_default": bool,             # False for new cards (use set_default to change)
                    "date_created": str             # ISO 8601 timestamp with milliseconds
                }
            
        Raises:
            Exception: If not authenticated (no user logged in)
            Exception: If expiry_month is not in range 1-12
                Error: "Invalid expiry month. Must be 1-12."
            Exception: If expiry_year is not in valid range (current_year to current_year+20)
                Error: "Invalid expiry year. Must be between {current_year} and {current_year + 20}."
            Exception: If CVV length is not 3 or 4 digits
                Error: "Invalid CVV. Must be 3 or 4 digits."
            
        Side Effects:
            - Adds payment method to user's payment_methods dictionary
            - CVV is validated but NOT stored (security best practice)
            - Full card number is masked; only last 4 digits retained
            
        Note:
            Card brand detection logic:
            - First digit 4 → Visa
            - First digit 5 → Mastercard
            - First digit 3 or 6 → Discover
            - Other → Unknown
            
            New payment methods are NOT set as default automatically. Use
            set_default_payment_method() to make it the default.
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> card = api.add_payment_method(
            ...     card_number="4532123456789012",
            ...     expiry_month=12,
            ...     expiry_year=2027,
            ...     cvv="123",
            ...     billing_zip="10001"
            ... )
            >>> print(f"Added {card['card']['brand']} ending in {card['card']['last_four']}")
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
        Retrieves all payment methods (credit/debit cards) for the authenticated user.
        
        Matches the Venmo API GET /v1/payment-methods endpoint. Returns a list of all stored
        payment methods with their masked card details, brand information, and default status.

        Returns:
            List[Dict[str, Any]]: List of payment method objects, each with structure:
                [
                    {
                        "id": str,                      # Unique payment method UUID
                        "type": "card",                 # Always "card" for card payments
                        "card": {
                            "last_four": str,           # Last 4 digits (e.g., "9012")
                            "brand": str,               # "visa", "mastercard", "discover", "unknown"
                            "expiration_month": int,    # 1-12
                            "expiration_year": int      # 4-digit year
                        },
                        "is_default": bool,             # True if this is the default payment method
                        "date_created": str             # ISO 8601 timestamp
                    },
                    ...
                ]
                
                Returns empty list [] if no payment methods are stored.
            
        Raises:
            Exception: If not authenticated (no user logged in)
            
        Note:
            - Full card numbers are never returned (security)
            - Only one payment method can have is_default=True
            - List order is not guaranteed (not sorted)
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> methods = api.get_payment_methods()
            >>> for method in methods:
            ...     default = " (default)" if method['is_default'] else ""
            ...     print(f"{method['card']['brand']} **** {method['card']['last_four']}{default}")
        """
        self._ensure_authenticated()
        user_data = self.users[self.current_user_id]
        payment_methods = list(user_data.get("payment_methods", {}).values())
        return copy.deepcopy(payment_methods)

    def set_default_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """
        Sets a specific payment method as the default for the authenticated user.
        
        Matches the Venmo API PUT /v1/payment-methods/{payment_method_id}/default endpoint.
        The default payment method is automatically used for transactions when no specific
        payment method is specified. Only one payment method can be default at a time.

        Args:
            payment_method_id (str): The UUID of the payment method to set as default.
                Must be a payment method that belongs to the authenticated user.
                Example: "550e8400-e29b-41d4-a716-446655440000"

        Returns:
            Dict[str, Any]: The updated payment method object with is_default=True:
                {
                    "id": str,
                    "type": "card",
                    "card": {
                        "last_four": str,
                        "brand": str,
                        "expiration_month": int,
                        "expiration_year": int
                    },
                    "is_default": True,             # Now set to True
                    "date_created": str
                }
            
        Raises:
            Exception: If not authenticated (no user logged in)
            Exception: If payment_method_id doesn't exist in user's payment methods
                Error message: "Payment method {payment_method_id} not found"
            
        Side Effects:
            - Sets is_default=False on all other payment methods for this user
            - Sets is_default=True on the specified payment method
            - Changes which payment method is used by default in transactions
            
        Note:
            This operation is idempotent - calling it multiple times with the same
            payment_method_id has no additional effect after the first call.
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> methods = api.get_payment_methods()
            >>> new_default = api.set_default_payment_method(methods[1]['id'])
            >>> print(f"Default payment method is now {new_default['card']['brand']}")
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
        Permanently deletes a payment method from the authenticated user's account.
        
        Matches the Venmo API DELETE /v1/payment-methods/{payment_method_id} endpoint.
        Once deleted, the payment method cannot be recovered and cannot be used for
        future transactions.

        Args:
            payment_method_id (str): The UUID of the payment method to delete.
                Must be a payment method that belongs to the authenticated user.
                Example: "550e8400-e29b-41d4-a716-446655440000"

        Returns:
            None: No return value on successful deletion
            
        Raises:
            Exception: If not authenticated (no user logged in)
            Exception: If payment_method_id doesn't exist in user's payment methods
                Error message: "Payment method {payment_method_id} not found"
            
        Side Effects:
            - Permanently removes payment method from user's payment_methods dictionary
            - If this was the default payment method, no new default is automatically selected
            - Past transactions using this payment method are NOT affected
            
        Warning:
            If you delete the default payment method, you should set a new default
            using set_default_payment_method() before making new payments.
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> methods = api.get_payment_methods()
            >>> old_card_id = methods[0]['id']
            >>> api.delete_payment_method(old_card_id)
            >>> print(f"Deleted payment method {old_card_id}")
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
        
        Counts all notifications belonging to the authenticated user where the 'read' flag
        is False. This is typically used to display notification badges in the UI.

        Returns:
            int: The number of unread notifications. Returns 0 if no unread notifications exist.
            
        Raises:
            Exception: If not authenticated (no user logged in)
            
        Note:
            - Only counts notifications for the authenticated user
            - Does NOT mark notifications as read (use mark_notifications_as_read for that)
            - This is a read-only operation with no side effects
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> unread = api.get_unread_notification_count()
            >>> print(f"You have {unread} unread notification(s)")
        """
        self._ensure_authenticated()
        unread_count = sum(
            1 for notif in self.notifications.values() 
            if notif["user"] == self.current_user_id and not notif["read"]
        )
        return unread_count

    def delete_all_notifications(self) -> None:
        """
        Permanently deletes all notifications for the authenticated user.
        
        Removes all notification records belonging to the authenticated user from the system.
        Both read and unread notifications are deleted. This action cannot be undone.

        Returns:
            None: No return value on successful deletion
            
        Raises:
            Exception: If not authenticated (no user logged in)
            
        Side Effects:
            - Permanently removes all notifications for the authenticated user
            - Other users' notifications are not affected
            - Unread notification count becomes 0 after this operation
            
        Warning:
            This operation is irreversible. Deleted notifications cannot be recovered.
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> api.delete_all_notifications()
            >>> print(f"Unread count: {api.get_unread_notification_count()}")  # 0
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
        Updates the read status for all notifications belonging to the authenticated user.
        
        Allows bulk marking of all user notifications as either read or unread. This is
        typically used to clear notification badges or to mark all notifications unread
        for testing purposes.

        Args:
            read_status (bool, optional): The read status to set for all notifications.
                - True: Mark all notifications as read (default)
                - False: Mark all notifications as unread
                Defaults to True.

        Returns:
            None: No return value on successful update
            
        Raises:
            Exception: If not authenticated (no user logged in)
            
        Side Effects:
            - Updates the 'read' field for all user notifications to the specified status
            - Affects unread notification count returned by get_unread_notification_count()
            - Does NOT delete notifications (use delete_all_notifications for that)
            
        Note:
            - Only affects notifications for the authenticated user
            - This is an all-or-nothing operation (no selective marking)
            - Notifications are NOT deleted, only their read status is changed
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> # Mark all as read
            >>> api.mark_notifications_as_read(True)
            >>> print(f"Unread: {api.get_unread_notification_count()}")  # 0
            >>> 
            >>> # Mark all as unread (for testing)
            >>> api.mark_notifications_as_read(False)
            >>> print(f"Unread: {api.get_unread_notification_count()}")  # Returns total count
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
        Retrieves the current Venmo balance for the authenticated user's account.
        
        Matches the Venmo API GET /v1/me/balance endpoint. Returns the user's available
        Venmo balance in USD, which can be used for payments or transferred to a bank account.

        Returns:
            float: Current account balance in USD (dollars and cents).
                Example: 125.50 represents $125.50
                Can be 0.0 if no balance
                Can be negative if user has outstanding debts (though Venmo typically prevents this)
            
        Raises:
            Exception: If not authenticated (no user logged in)
            
        Note:
            - This is the balance available for sending payments
            - Balance increases when receiving money (create_payment as recipient)
            - Balance decreases when sending money (create_payment as sender)
            - Pending charges do NOT affect the balance until they're paid
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> balance = api.get_account_balance()
            >>> print(f"Your Venmo balance: ${balance:.2f}")
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
        Retrieves transaction history with analytics summary for the authenticated user.
        
        Custom endpoint that combines transaction listing with financial analytics. Returns
        filtered, sorted transactions plus summary statistics about sending/receiving patterns.
        More comprehensive than get_transactions() by including analytics calculations.

        Args:
            limit (int, optional): Maximum number of transactions to return.
                Defaults to 50. Unlike get_transactions(), this applies after ALL filtering.
            start_date (Optional[str], optional): Filter transactions created on or after this date.
                Must be in ISO 8601 format: "YYYY-MM-DDTHH:MM:SS.sssZ"
                Example: "2024-01-01T00:00:00.000Z"
                Defaults to None (no start date filter).
            end_date (Optional[str], optional): Filter transactions created on or before this date.
                Must be in ISO 8601 format: "YYYY-MM-DDTHH:MM:SS.sssZ"
                Example: "2024-12-31T23:59:59.999Z"
                Defaults to None (no end date filter).

        Returns:
            Dict[str, Any]: Transaction history with analytics:
                {
                    "transactions": List[Dict[str, Any]],  # Up to 'limit' transactions, each with:
                        # - All fields from get_payment() documentation
                        # - "direction": "sent" or "received" (added for convenience)
                    "analytics": {
                        "total_count": int,         # Total matching transactions (all pages)
                        "total_sent": float,        # Sum of settled payments sent (USD)
                        "total_received": float,    # Sum of settled payments received (USD)
                        "net_amount": float         # total_received - total_sent (USD)
                    }
                }
            
        Raises:
            Exception: If not authenticated (no user logged in)
            
        Note:
            - Transactions are sorted by date_created (descending/newest first)
            - Only includes transactions where user is actor OR target
            - Date filtering uses string comparison (ISO 8601 format sorts correctly)
            - Analytics only count "settled" transactions (pending/cancelled excluded)
            - The "direction" field is added to each transaction:
              * "sent": User is the actor (sender)
              * "received": User is the target (recipient)
            
        Example:
            >>> api.authenticate("token_alice@example.com")
            >>> history = api.get_transaction_history(
            ...     limit=10,
            ...     start_date="2024-01-01T00:00:00.000Z",
            ...     end_date="2024-12-31T23:59:59.999Z"
            ... )
            >>> analytics = history['analytics']
            >>> print(f"Sent: ${analytics['total_sent']:.2f}")
            >>> print(f"Received: ${analytics['total_received']:.2f}")
            >>> print(f"Net: ${analytics['net_amount']:.2f}")
            >>> 
            >>> for tx in history['transactions']:
            ...     direction = "→" if tx['direction'] == "sent" else "←"
            ...     print(f"{direction} ${tx['amount']:.2f}: {tx['note']}")
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
        Resets the entire simulated backend to its default state for testing purposes.
        
        This is a utility function for development and testing, not a standard Venmo API endpoint.
        Reloads the default scenario data and clears authentication state, effectively resetting
        the simulation to a clean starting point.

        Returns:
            None: No return value. Prints confirmation message to console.
            
        Side Effects:
            - Reloads all data (users, transactions, notifications) from DEFAULT_STATE
            - Clears authentication: access_token set to None
            - Clears current user: current_user_id set to None
            - All in-memory changes since initialization are lost
            - Any data added during the session is erased
            
        Warning:
            This is destructive! All changes made during the session (new payments,
            added payment methods, etc.) will be lost. Use with caution.
            
        Note:
            - This method does NOT require authentication
            - After reset, you must call authenticate() again before using protected endpoints
            - Useful for resetting state between test cases
            
        Example:
            >>> api = VenmoApis()
            >>> api.authenticate("token_alice@example.com")
            >>> api.create_payment("bob@example.com", 50.0, "Test")
            >>> api.reset_data()  # Prints: "VenmoApis: All data reset to default state."
            >>> # Now must authenticate again
            >>> api.authenticate("token_alice@example.com")
        """
        self._load_scenario(DEFAULT_STATE)
        self.access_token = None
        self.current_user_id = None
        print("VenmoApis: All data reset to default state.")