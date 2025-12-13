import uuid
from typing import Dict, List, Union, Literal, Any
from datetime import datetime, timedelta
from copy import deepcopy
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("AmazonApis")

class AmazonApis:
    """
    Inspired by https://appworld.dev/

    Amazon this is a simulated implementation of common Amazon-like functionalities.
    It takes inspiration from AppWorld's signature style and output, but not the inside of the code
    """
    
    def __init__(self):
        """
        Initializes the AmazonApis instance by creating a fresh state from the default
        scenario, including users, products, orders, promotions, and all related data.
        
        The state contains:
            - users: Dictionary of user accounts with balances, carts, orders, addresses, payment cards
            - products: Dictionary of available products with prices, stock, and descriptions
            - current_user: The ID of the currently logged-in user (None if no user logged in)
            - promotions: Dictionary of promotional codes with discount percentages
            - product_reviews: Dictionary mapping product IDs to lists of reviews
            - product_questions: Dictionary mapping product IDs to Q&A pairs
            - sellers: Dictionary of seller information
        
        Side Effects:
            - Creates deep copy of DEFAULT_STATE to ensure state isolation
            - Sets _api_description field for API identification
        """
        self.state = deepcopy(DEFAULT_STATE)
        self._api_description = "Amazon API simulation inspired by AppWorld's style."

    def _get_current_user_id(self) -> Union[str, None]:
        """
        Retrieves the ID of the currently authenticated user from the session state.
        
        Returns:
            Union[str, None]: The UUID string of the logged-in user, or None if no user
                              is currently logged in. Used for authentication checks and
                              retrieving user-specific data.
        
        Notes:
            - Does not validate if the user_id actually exists in the users dictionary
            - Returns None immediately after initialization or after logout
        """
        return self.state.get("current_user")

    def _require_login(self) -> Dict[str, Union[bool, str]]:
        """
        Validates that a user is currently logged in and authorized to perform actions.
        
        Returns:
            Dict[str, Union[bool, str]]: None if user is logged in (validation passes),
                                          otherwise returns error dictionary with:
                                          - status (bool): False
                                          - message (str): "You must be logged in to perform this action."
        
        Usage Pattern:
            Used at the start of protected methods to enforce authentication:
            >>> login_check = self._require_login()
            >>> if login_check:
            >>>     return {"some_status": False, "message": login_check["message"]}
        
        Notes:
            - Only checks if current_user is set, does not validate user existence
            - Callers typically return immediately if this returns a non-None value
        """
        if not self._get_current_user_id():
            return {"status": False, "message": "You must be logged in to perform this action."}
        return None

    def _get_user_data(self, user_id: str) -> Union[Dict, None]:
        """
        Retrieves the complete data record for a specific user by their ID.
        
        Args:
            user_id (str): The unique UUID identifier of the user to retrieve.
        
        Returns:
            Union[Dict, None]: The user's data dictionary if found, containing fields like:
                               - first_name (str): User's first name
                               - last_name (str): User's last name
                               - email (str): User's email address
                               - balance (float): Account balance
                               - cart (Dict): Shopping cart contents
                               - orders (Dict): Order history
                               - addresses (Dict): Saved addresses
                               - payment_cards (Dict): Saved payment methods
                               - wish_list (List): Wish list items
                               Returns None if user_id not found.
        
        Notes:
            - Does not modify or validate the user data
            - Returns reference to actual state data, not a copy
        """
        return self.state["users"].get(user_id)

    def _get_current_user_data(self) -> Union[Dict, None]:
        """
        Retrieves the complete data record for the currently logged-in user.
        
        Returns:
            Union[Dict, None]: The current user's data dictionary if logged in (see _get_user_data
                               for structure), or None if no user is logged in or user_id is invalid.
        
        Notes:
            - Convenience method combining _get_current_user_id and _get_user_data
            - Returns None if no user is logged in (current_user is None)
            - Returns None if current_user_id exists but user record was deleted
        """
        user_id = self._get_current_user_id()
        if user_id:
            return self.state["users"].get(user_id)
        return None

    def _update_user_data(self, user_id: str, key: str, value: Any):
        """
        Updates a specific field in a user's data record.
        
        Args:
            user_id (str): The unique UUID identifier of the user to update.
            key (str): The field name to update (e.g., "balance", "cart", "orders").
            value (Any): The new value to assign to the field.
        
        Side Effects:
            - Modifies the user's data in self.state["users"][user_id][key] in-place
            - No effect if user_id does not exist in users dictionary
        
        Notes:
            - Does not validate the key or value types
            - Silently fails if user_id not found (no error raised)
            - Can be used to update any field including nested dictionaries and lists
        """
        if user_id in self.state["users"]:
            self.state["users"][user_id][key] = value

    def register_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        phone_number: str) -> Dict[str, Union[bool, str]]:
        """
        Registers a new user account with the system by creating a unique user ID and
        initializing their profile with default values.
        
        Args:
            first_name (str): The user's first name.
            last_name (str): The user's last name.
            email (str): The user's email address. Must be unique across all users.
                        Used as the primary identifier for login.
            password (str): The user's password. Stored in plain text (not secure - simulation only).
            phone_number (str): The user's phone number for contact purposes.
        
        Returns:
            Dict[str, Union[bool, str]]: Registration result dictionary containing:
                - register_status (bool): True if registration successful, False otherwise
                - message (str): Success message with new user ID, or error description
        
        Error Cases:
            - Email already exists: {"register_status": False, "message": "User with this email already exists."}
        
        Side Effects:
            - Creates new user record in self.state["users"] with UUID key
            - Initializes user with balance=0.0, empty cart, empty orders, empty payment methods,
              empty addresses, empty wish_list, empty prime_subscriptions, empty returns
        
        Example:
            >>> api.register_user("John", "Doe", "john@example.com", "password123", "+1234567890")
            {"register_status": True, "message": "User john@example.com registered successfully with ID abc-123..."}
        """
        for _, user_data in self.state["users"].items():
            if user_data["email"] == email:
                return {"register_status": False, "message": "User with this email already exists."}

        new_user_id = str(uuid.uuid4())
        self.state["users"][new_user_id] = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "phone_number": phone_number,
            "balance": 0.0,
            "payment_cards": {},
            "addresses": {},
            "cart": {},
            "wish_list": [],
            "orders": {},
            "prime_subscriptions": {},
            "returns": {},
        }
        return {"register_status": True, "message": f"User {email} registered successfully with ID {new_user_id}."}

    def login_user(self, email: str, password: str) -> Dict[str, Union[bool, str]]:
        """
        Authenticates a user by validating their credentials and establishing an active session.
        
        Args:
            email (str): The email address of the user attempting to login. Must match
                        the email used during registration.
            password (str): The password for authentication. Must match exactly (case-sensitive).
        
        Returns:
            Dict[str, Union[bool, str]]: Authentication result dictionary containing:
                - login_status (bool): True if login successful, False otherwise
                - message (str): Success message with email, or error description
        
        Error Cases:
            - Invalid credentials: {"login_status": False, "message": "Invalid email or password."}
              (same message for both email not found and password mismatch for security)
        
        Side Effects:
            - Sets self.state["current_user"] to the authenticated user's UUID on success
            - Previous session (if any) is replaced with the new user's session
        
        Example:
            >>> api.login_user("john@example.com", "password123")
            {"login_status": True, "message": "User john@example.com logged in successfully."}
        
        Notes:
            - Only one user can be logged in at a time in this simulation
            - Does not create session tokens or expiration (simple state-based auth)
        """
        for user_id, user_data in self.state["users"].items():
            if user_data["email"] == email and user_data["password"] == password:
                self.state["current_user"] = user_id
                return {"login_status": True, "message": f"User {email} logged in successfully."}
        return {"login_status": False, "message": "Invalid email or password."}

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
            - Sets self.state["current_user"] to None, clearing the session
            - User's data remains intact; only the session reference is removed
        
        Example:
            >>> api.logout_user()
            {"logout_status": True, "message": "User logged out successfully."}
        """
        if not self._get_current_user_id():
            return {"logout_status": False, "message": "No user is currently logged in."}
        self.state["current_user"] = None
        return {"logout_status": True, "message": "User logged out successfully."}

    def show_profile(self) -> Dict[str, Union[bool, str, Dict]]:
        """
        Retrieves the complete profile information for the currently logged-in user,
        including all account data such as cart, orders, addresses, payment cards, and more.
        
        Returns:
            Dict[str, Union[bool, str, Dict]]: Profile result dictionary containing:
                - profile_status (bool): True if profile retrieved, False otherwise
                - message (str): Error description if applicable
                - profile (Dict): Complete user data including first_name, last_name, email,
                                  password, phone_number, balance, payment_cards, addresses,
                                  cart, wish_list, orders, prime_subscriptions, returns
        
        Error Cases:
            - Not logged in: {"profile_status": False, "message": "You must be logged in...", "profile": {}}
            - User not found: {"profile_status": False, "message": "User not found.", "profile": {}}
        
        Example:
            >>> api.show_profile()
            {"profile_status": True, "profile": {"first_name": "John", "last_name": "Doe", ...}}
        
        Notes:
            - Returns reference to actual user data, not a copy
            - Includes sensitive information like password (simulation only)
        """
        login_check = self._require_login()
        if login_check:
            return {"profile_status": False, "message": login_check["message"], "profile": {}}
        
        user_data = self._get_current_user_data()
        if user_data:
            return {"profile_status": True, "profile": user_data}
        return {"profile_status": False, "message": "User not found.", "profile": {}}

    def show_account(self) -> Dict[str, Union[bool, str, Dict]]:
        """
        Retrieves account-specific financial and contact information including balance,
        payment cards, and addresses for the currently logged-in user.
        
        Returns:
            Dict[str, Union[bool, str, Dict]]: Account result dictionary containing:
                - account_status (bool): True if account retrieved, False otherwise
                - message (str): Success message with email, or error description
                - account (Dict): Account details with:
                    - balance (float): Current account balance
                    - payment_cards (List[Dict]): List of saved payment card objects
                    - addresses (List[Dict]): List of saved address objects
        
        Error Cases:
            - Not logged in: {"account_status": False, "message": "You must be logged in..."}
            - User not found: {"account_status": False, "message": "User not found."}
        
        Example:
            >>> api.show_account()
            {"account_status": True, "message": "Account details for john@example.com",
             "account": {"balance": 150.0, "payment_cards": [...], "addresses": [...]}}
        
        Notes:
            - Returns list copies of nested dictionaries (payment_cards, addresses)
            - Does not include cart, orders, or wish list (see show_profile for complete data)
        """
        login_check = self._require_login()
        if login_check:
            return {"account_status": False, "message": login_check["message"]}
        
        user_data = self._get_current_user_data()
        if user_data:
            return {
                "account_status": True,
                "message": f"Account details for {user_data.get('email', 'N/A')}",
                "account": {
                    "balance": user_data["balance"],
                    "payment_cards": list(user_data["payment_cards"].values()),
                    "addresses": list(user_data["addresses"].values()),
                },
            }
        return {"account_status": False, "message": "User not found."}

    def delete_account(self) -> Dict[str, Union[bool, str]]:
        """
        Permanently removes the currently logged-in user's account from the system,
        deleting all associated data including orders, cart, addresses, and payment cards.
        
        Returns:
            Dict[str, Union[bool, str]]: Deletion result dictionary containing:
                - delete_status (bool): True if account deleted, False otherwise
                - message (str): Success or error message
        
        Error Cases:
            - Not logged in: {"delete_status": False, "message": "You must be logged in..."}
            - User not found: {"delete_status": False, "message": "User not found."}
        
        Side Effects:
            - Removes user record from self.state["users"]
            - Sets self.state["current_user"] to None (logs out after deletion)
            - All user data is permanently lost (cannot be recovered)
        
        Example:
            >>> api.delete_account()
            {"delete_status": True, "message": "Account deleted successfully."}
        
        Notes:
            - Does not refund balance or cancel pending orders
            - Does not remove user's reviews or questions from products
        """
        login_check = self._require_login()
        if login_check:
            return {"delete_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        if user_id in self.state["users"]:
            del self.state["users"][user_id]
            self.state["current_user"] = None
            return {"delete_status": True, "message": "Account deleted successfully."}
        return {"delete_status": False, "message": "User not found."}

    def add_payment_card(
        self,
        card_name: str,
        owner_name: str,
        card_number: int,
        expiry_year: int,
        expiry_month: int,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Adds a new payment card to the currently logged-in user's account, storing only
        the last 4 digits of the card number for security.
        
        Args:
            card_name (str): A descriptive name for the card (e.g., "Personal Visa", "Work Amex").
                           Used to identify the card in user-facing displays.
            owner_name (str): The name of the card owner as it appears on the physical card.
            card_number (int): The full card number. Only the last 4 digits will be stored.
                              Expected to be 13-19 digits typically.
            expiry_year (int): The expiration year of the card (e.g., 2025).
            expiry_month (int): The expiration month of the card (1-12).
        
        Returns:
            Dict[str, Union[bool, str, int]]: Payment card addition result containing:
                - add_card_status (bool): True if card added, False otherwise
                - message (str): Success or error message
                - card_id (str): The newly generated UUID for the card (only on success)
        
        Error Cases:
            - Not logged in: {"add_card_status": False, "message": "You must be logged in..."}
            - User not found: {"add_card_status": False, "message": "User not found."}
        
        Side Effects:
            - Adds card to user_data["payment_cards"] dictionary with UUID key
            - Stores only last 4 digits of card_number for security
            - Updates user data in-place
        
        Example:
            >>> api.add_payment_card("My Visa", "John Doe", 4111111111111111, 2025, 12)
            {"add_card_status": True, "message": "Payment card added successfully.", "card_id": "abc-123..."}
        
        Notes:
            - Does not validate card number format or expiration date
            - Multiple cards can have the same name
            - Card is stored but not automatically set as default
        """
        login_check = self._require_login()
        if login_check:
            return {"add_card_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"add_card_status": False, "message": "User not found."}

        new_card_id = str(uuid.uuid4())
        user_payment_cards = user_data.get("payment_cards", {})
        user_payment_cards[new_card_id] = {
            "card_name": card_name,
            "owner_name": owner_name,
            "card_number_last4": str(card_number)[-4:],
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
        }
        self._update_user_data(user_id, "payment_cards", user_payment_cards)
        return {"add_card_status": True, "message": "Payment card added successfully.", "card_id": new_card_id}

    def remove_payment_card(self, card_id: str) -> Dict[str, Union[bool, str]]:
        """
        Removes a payment card from the currently logged-in user's account by card ID.
        
        Args:
            card_id (str): The unique UUID identifier of the payment card to remove.
                          This ID is returned when the card is added.
        
        Returns:
            Dict[str, Union[bool, str]]: Card removal result containing:
                - remove_card_status (bool): True if card removed, False otherwise
                - message (str): Success message with card_id, or error description
        
        Error Cases:
            - Not logged in: {"remove_card_status": False, "message": "You must be logged in..."}
            - User not found: {"remove_card_status": False, "message": "User not found."}
            - Card not found: {"remove_card_status": False, "message": "Payment card not found."}
        
        Side Effects:
            - Deletes card from user_data["payment_cards"] dictionary
            - Updates user data in-place
        
        Example:
            >>> api.remove_payment_card("abc-123-def-456")
            {"remove_card_status": True, "message": "Payment card abc-123-def-456 removed successfully."}
        
        Notes:
            - Does not check if card is being used for pending orders
            - Cannot be undone; card data is permanently deleted
        """
        login_check = self._require_login()
        if login_check:
            return {"remove_card_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"remove_card_status": False, "message": "User not found."}

        user_payment_cards = user_data.get("payment_cards", {})
        if card_id in user_payment_cards:
            del user_payment_cards[card_id]
            self._update_user_data(user_id, "payment_cards", user_payment_cards)
            return {"remove_card_status": True, "message": f"Payment card {card_id} removed successfully."}
        return {"remove_card_status": False, "message": "Payment card not found."}

    def show_payment_cards(
        self, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, str, List[Dict]]]:
        """
        Retrieves a paginated list of the currently logged-in user's saved payment cards.
        
        Args:
            page_index (int, optional): The page number to retrieve (1-indexed). Default is 1.
            page_limit (int, optional): The number of cards per page. Default is 10.
        
        Returns:
            Dict[str, Union[bool, str, List[Dict]]]: Payment cards result containing:
                - cards_status (bool): True if cards retrieved (even if empty), False on error
                - message (str): Error description if applicable
                - payment_cards (List[Dict]): List of card objects, each containing:
                    - card_name (str): Descriptive name for the card
                    - owner_name (str): Card owner's name
                    - card_number_last4 (str): Last 4 digits of card number
                    - expiry_year (int): Expiration year
                    - expiry_month (int): Expiration month
        
        Error Cases:
            - Not logged in: {"cards_status": False, "message": "You must be logged in...", "payment_cards": []}
            - User not found: {"cards_status": False, "message": "User not found.", "payment_cards": []}
        
        Example:
            >>> api.show_payment_cards(page_index=1, page_limit=5)
            {"cards_status": True, "payment_cards": [{"card_name": "My Visa", "owner_name": "John Doe", ...}]}
        
        Notes:
            - Returns empty list if user has no payment cards
            - Page indices beyond available data return empty list
            - Card IDs are not included in returned data (only card details)
        """
        login_check = self._require_login()
        if login_check:
            return {"cards_status": False, "message": login_check["message"], "payment_cards": []}
        
        user_data = self._get_current_user_data()
        if not user_data:
            return {"cards_status": False, "message": "User not found.", "payment_cards": []}

        all_cards = list(user_data.get("payment_cards", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_cards = all_cards[start_index:end_index]

        return {"cards_status": True, "payment_cards": paginated_cards}

    def add_address(
        self,
        name: str,
        street_address: str,
        city: str,
        state: str,
        country: str,
        zip_code: int,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Adds a new shipping address to the currently logged-in user's account for use during checkout.
        
        Args:
            name (str): A descriptive label for the address (e.g., "Home", "Work", "Mom's House").
                       Used to identify the address in user-facing displays.
            street_address (str): The street address including house/building number and street name.
            city (str): The city name.
            state (str): The state, province, or region name.
            country (str): The country name.
            zip_code (int): The postal or ZIP code (numeric only in this simulation).
        
        Returns:
            Dict[str, Union[bool, str, int]]: Address addition result containing:
                - add_address_status (bool): True if address added, False otherwise
                - message (str): Success or error message
                - address_id (str): The newly generated UUID for the address (only on success)
        
        Error Cases:
            - Not logged in: {"add_address_status": False, "message": "You must be logged in..."}
            - User not found: {"add_address_status": False, "message": "User not found."}
        
        Side Effects:
            - Adds address to user_data["addresses"] dictionary with UUID key
            - Updates user data in-place
        
        Example:
            >>> api.add_address("Home", "123 Main St", "Springfield", "IL", "USA", 62701)
            {"add_address_status": True, "message": "Address added successfully.", "address_id": "xyz-789..."}
        
        Notes:
            - Does not validate address format or existence
            - Multiple addresses can have the same name
            - Address is not automatically set as default
        """
        login_check = self._require_login()
        if login_check:
            return {"add_address_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"add_address_status": False, "message": "User not found."}

        new_address_id = str(uuid.uuid4())
        user_addresses = user_data.get("addresses", {})
        user_addresses[new_address_id] = {
            "name": name,
            "street_address": street_address,
            "city": city,
            "state": state,
            "country": country,
            "zip_code": zip_code,
        }
        self._update_user_data(user_id, "addresses", user_addresses)
        return {"add_address_status": True, "message": "Address added successfully.", "address_id": new_address_id}

    def remove_address(self, address_id: str) -> Dict[str, Union[bool, str]]:
        """
        Removes a shipping address from the currently logged-in user's account by address ID.
        
        Args:
            address_id (str): The unique UUID identifier of the address to remove.
                             This ID is returned when the address is added.
        
        Returns:
            Dict[str, Union[bool, str]]: Address removal result containing:
                - remove_address_status (bool): True if address removed, False otherwise
                - message (str): Success message with address_id, or error description
        
        Error Cases:
            - Not logged in: {"remove_address_status": False, "message": "You must be logged in..."}
            - User not found: {"remove_address_status": False, "message": "User not found."}
            - Address not found: {"remove_address_status": False, "message": "Address not found."}
        
        Side Effects:
            - Deletes address from user_data["addresses"] dictionary
            - Updates user data in-place
        
        Example:
            >>> api.remove_address("xyz-789-abc-012")
            {"remove_address_status": True, "message": "Address xyz-789-abc-012 removed successfully."}
        
        Notes:
            - Does not check if address is being used for pending orders
            - Cannot be undone; address data is permanently deleted
        """
        login_check = self._require_login()
        if login_check:
            return {"remove_address_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"remove_address_status": False, "message": "User not found."}

        user_addresses = user_data.get("addresses", {})
        if address_id in user_addresses:
            del user_addresses[address_id]
            self._update_user_data(user_id, "addresses", user_addresses)
            return {"remove_address_status": True, "message": f"Address {address_id} removed successfully."}
        return {"remove_address_status": False, "message": "Address not found."}

    def show_addresses(
        self, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, str, List[Dict]]]:
        """
        Retrieves a paginated list of the currently logged-in user's saved shipping addresses.
        
        Args:
            page_index (int, optional): The page number to retrieve (1-indexed). Default is 1.
            page_limit (int, optional): The number of addresses per page. Default is 10.
        
        Returns:
            Dict[str, Union[bool, str, List[Dict]]]: Addresses result containing:
                - addresses_status (bool): True if addresses retrieved (even if empty), False on error
                - message (str): Error description if applicable
                - addresses (List[Dict]): List of address objects, each containing:
                    - name (str): Descriptive label for the address
                    - street_address (str): Street address
                    - city (str): City name
                    - state (str): State/province
                    - country (str): Country name
                    - zip_code (int): Postal/ZIP code
        
        Error Cases:
            - Not logged in: {"addresses_status": False, "message": "You must be logged in...", "addresses": []}
            - User not found: {"addresses_status": False, "message": "User not found.", "addresses": []}
        
        Example:
            >>> api.show_addresses(page_index=1, page_limit=5)
            {"addresses_status": True, "addresses": [{"name": "Home", "street_address": "123 Main St", ...}]}
        
        Notes:
            - Returns empty list if user has no addresses
            - Page indices beyond available data return empty list
            - Address IDs are not included in returned data (only address details)
        """
        login_check = self._require_login()
        if login_check:
            return {"addresses_status": False, "message": login_check["message"], "addresses": []}
        
        user_data = self._get_current_user_data()
        if not user_data:
            return {"addresses_status": False, "message": "User not found.", "addresses": []}

        all_addresses = list(user_data.get("addresses", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_addresses = all_addresses[start_index:end_index]

        return {"addresses_status": True, "addresses": paginated_addresses}

    def add_to_cart(self, product_id: str, quantity: int) -> Dict[str, Union[bool, str]]:
        """
        Adds a specified quantity of a product to the currently logged-in user's shopping cart,
        increasing the quantity if the product is already in the cart.
        
        Args:
            product_id (str): The unique identifier of the product to add to the cart.
            quantity (int): The number of units to add. Must be positive and not exceed available stock.
        
        Returns:
            Dict[str, Union[bool, str]]: Cart addition result containing:
                - cart_status (bool): True if product added, False otherwise
                - message (str): Success or error message
        
        Error Cases:
            - Not logged in: {"cart_status": False, "message": "You must be logged in..."}
            - User not found: {"cart_status": False, "message": "User not found."}
            - Product not found: {"cart_status": False, "message": "Product not found."}
            - Insufficient stock: {"cart_status": False, "message": "Not enough stock."}
        
        Side Effects:
            - Adds or increments product quantity in user_data["cart"][product_id]
            - Does not deduct from product stock (stock is deducted at checkout)
            - Updates user data in-place
        
        Example:
            >>> api.add_to_cart("prod-123", 2)
            {"cart_status": True, "message": "Product added to cart."}
        
        Notes:
            - If product already in cart, adds to existing quantity (not replacement)
            - Stock validation ensures requested quantity can be fulfilled
            - Does not validate if total cart quantity exceeds stock (only new addition)
        """
        login_check = self._require_login()
        if login_check:
            return {"cart_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"cart_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"cart_status": False, "message": "Product not found."}
        if self.state["products"][product_id]["stock"] < quantity:
            return {"cart_status": False, "message": "Not enough stock."}

        user_cart = user_data.get("cart", {})
        user_cart[product_id] = user_cart.get(product_id, 0) + quantity
        self._update_user_data(user_id, "cart", user_cart)
        return {"cart_status": True, "message": "Product added to cart."}

    def remove_from_cart(self, product_id: str) -> Dict[str, Union[bool, str]]:
        """
        Completely removes a product from the currently logged-in user's shopping cart,
        regardless of its quantity.
        
        Args:
            product_id (str): The unique identifier of the product to remove from the cart.
        
        Returns:
            Dict[str, Union[bool, str]]: Cart removal result containing:
                - cart_status (bool): True if product removed, False otherwise
                - message (str): Success or error message
        
        Error Cases:
            - Not logged in: {"cart_status": False, "message": "You must be logged in..."}
            - User not found: {"cart_status": False, "message": "User not found."}
            - Product not in cart: {"cart_status": False, "message": "Product not found in cart."}
        
        Side Effects:
            - Deletes product_id from user_data["cart"] dictionary
            - Removes all units of the product (does not decrement quantity)
            - Updates user data in-place
        
        Example:
            >>> api.remove_from_cart("prod-123")
            {"cart_status": True, "message": "Product removed from cart."}
        
        Notes:
            - To update quantity instead of removing completely, use update_cart_item_quantity()
            - Does not restore product stock (stock was never deducted)
        """
        login_check = self._require_login()
        if login_check:
            return {"cart_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"cart_status": False, "message": "User not found."}

        user_cart = user_data.get("cart", {})
        if product_id in user_cart:
            del user_cart[product_id]
            self._update_user_data(user_id, "cart", user_cart)
            return {"cart_status": True, "message": "Product removed from cart."}
        return {"cart_status": False, "message": "Product not found in cart."}

    def update_cart_item_quantity(self, product_id: str, quantity: int) -> Dict[str, Union[bool, str]]:
        """
        Updates the quantity of a specific product in the currently logged-in user's shopping cart
        to a new absolute value (replaces existing quantity, not incremental).
        
        Args:
            product_id (str): The unique identifier of the product in the cart to update.
            quantity (int): The new absolute quantity for the product. If <= 0, removes the product.
                           Must not exceed available stock.
        
        Returns:
            Dict[str, Union[bool, str]]: Cart update result containing:
                - cart_status (bool): True if cart updated, False otherwise
                - message (str): Success or error message
        
        Error Cases:
            - Not logged in: {"cart_status": False, "message": "You must be logged in..."}
            - User not found: {"cart_status": False, "message": "User not found."}
            - Product not in cart: {"cart_status": False, "message": "Product not in cart."}
            - Product not found: {"cart_status": False, "message": "Product not found."}
            - Insufficient stock: {"cart_status": False, "message": "Not enough stock."}
        
        Side Effects:
            - Sets user_data["cart"][product_id] to new quantity
            - If quantity <= 0, deletes product from cart entirely
            - Updates user data in-place
        
        Example:
            >>> api.update_cart_item_quantity("prod-123", 5)  # Set to exactly 5 units
            {"cart_status": True, "message": "Cart updated."}
            >>> api.update_cart_item_quantity("prod-123", 0)  # Remove product
            {"cart_status": True, "message": "Cart updated."}
        
        Notes:
            - Quantity is absolute, not incremental (use add_to_cart for incrementing)
            - Setting quantity to 0 or negative removes the product from cart
            - Stock validation ensures new quantity can be fulfilled
        """
        login_check = self._require_login()
        if login_check:
            return {"cart_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"cart_status": False, "message": "User not found."}

        user_cart = user_data.get("cart", {})
        if product_id not in user_cart:
            return {"cart_status": False, "message": "Product not in cart."}
        
        if product_id not in self.state["products"]:
            return {"cart_status": False, "message": "Product not found."}
        
        if self.state["products"][product_id]["stock"] < quantity:
            return {"cart_status": False, "message": "Not enough stock."}

        if quantity <= 0:
            del user_cart[product_id]
        else:
            user_cart[product_id] = quantity
        self._update_user_data(user_id, "cart", user_cart)
        return {"cart_status": True, "message": "Cart updated."}

    def show_cart(self) -> Dict[str, Union[bool, str, List[Dict]]]:
        """
        Retrieves the complete contents of the currently logged-in user's shopping cart
        with detailed product information and calculated totals for each item.
        
        Returns:
            Dict[str, Union[bool, str, List[Dict]]]: Cart contents result containing:
                - cart_status (bool): True if cart retrieved (even if empty), False on error
                - message (str): Error description if applicable
                - cart (List[Dict]): List of cart items, each containing:
                    - product_id (str): The product's unique identifier
                    - name (str): Product name
                    - price (float): Unit price of the product
                    - quantity (int): Number of units in cart
                    - total (float): Total price for this item (price * quantity)
        
        Error Cases:
            - Not logged in: {"cart_status": False, "message": "You must be logged in...", "cart": []}
            - User not found: {"cart_status": False, "message": "User not found.", "cart": []}
        
        Example:
            >>> api.show_cart()
            {"cart_status": True, "cart": [
                {"product_id": "prod-123", "name": "Laptop", "price": 999.99, "quantity": 1, "total": 999.99},
                {"product_id": "prod-456", "name": "Mouse", "price": 29.99, "quantity": 2, "total": 59.98}
            ]}
        
        Notes:
            - Returns empty list if cart is empty
            - Skips \"promo_code\" key if present in cart (not a product)
            - Silently omits products that no longer exist in product catalog
            - Does not include cart-wide total (calculate by summing item totals)
        """
        login_check = self._require_login()
        if login_check:
            return {"cart_status": False, "message": login_check["message"], "cart": []}
        
        user_data = self._get_current_user_data()
        if not user_data:
            return {"cart_status": False, "message": "User not found.", "cart": []}

        cart_items = []
        for product_id, quantity in user_data.get("cart", {}).items():
            if product_id == "promo_code":
                continue
            product_info = self.state["products"].get(product_id)
            if product_info:
                cart_items.append(
                    {
                        "product_id": product_id,
                        "name": product_info["name"],
                        "price": product_info["price"],
                        "quantity": quantity,
                        "total": product_info["price"] * quantity,
                    }
                )
        return {"cart_status": True, "cart": cart_items}

    def apply_promo_code_to_cart(self, promo_code: str) -> Dict[str, Union[bool, str, float]]:
        """
        Applies a promotional discount code to the currently logged-in user's shopping cart,
        validating eligibility criteria and calculating the discount amount.
        
        Args:
            promo_code (str): The promotional code string to apply (e.g., \"SAVE20\").
                             Must match an active promo code in the system.
        
        Returns:
            Dict[str, Union[bool, str, float]]: Promo code application result containing:
                - promo_status (bool): True if code applied, False otherwise
                - message (str): Success message with discount, or error description
                - discount_amount (float): Dollar amount of discount (only on success)
                - new_total (float): New cart total after discount (only on success)
        
        Error Cases:
            - Not logged in: {\"promo_status\": False, \"message\": \"You must be logged in...\"}
            - User not found: {\"promo_status\": False, \"message\": \"User not found.\"}
            - Empty cart: {\"promo_status\": False, \"message\": \"Your cart is empty.\"}
            - Code already applied: {\"promo_status\": True, \"message\": \"Promo code already applied to cart.\"}
            - Invalid code: {\"promo_status\": False, \"message\": \"Invalid promo code.\"}
            - Inactive code: {\"promo_status\": False, \"message\": \"This promo code is not currently active.\"}
            - Expired code: {\"promo_status\": False, \"message\": \"This promo code has expired.\"}
            - Minimum not met: {\"promo_status\": False, \"message\": \"A minimum purchase of $X.XX is required...\"}
        
        Side Effects:
            - Adds \"promo_code\" key to user_data[\"cart\"] with the code string
            - Does not modify product prices or cart totals (discount applied at checkout)
            - Updates user data in-place
        
        Example:
            >>> api.apply_promo_code_to_cart(\"SAVE20\")
            {\"promo_status\": True, \"message\": \"Promo code 'SAVE20' applied. Discount: $20.00\",
             \"discount_amount\": 20.0, \"new_total\": 80.0}
        
        Notes:
            - Only one promo code can be applied per cart
            - Discount percentage is retrieved from promotions dictionary
            - Expiry date is checked against current datetime
            - Minimum purchase amount must be met before discount
        """
        login_check = self._require_login()
        if login_check:
            return {"promo_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"promo_status": False, "message": "User not found."}
        
        cart_total = 0.0
        if not user_data.get("cart"):
            return {"promo_status": False, "message": "Your cart is empty."}

        if user_data.get("cart").get("promo_code"):
            return {"promo_status": True, "message": "Promo code already applied to cart."}

        for product_id, quantity in user_data.get("cart", {}).items():
            product_info = self.state["products"].get(product_id)
            if product_info:
                cart_total += product_info["price"] * quantity

        found_promo = None
        for promo_details in self.state.get("promotions", {}).values():
            if promo_details.get("code") == promo_code:
                found_promo = promo_details
                break

        if not found_promo:
            return {"promo_status": False, "message": "Invalid promo code."}

        if not found_promo.get("is_active", False):
            return {"promo_status": False, "message": "This promo code is not currently active."}

        expiry_date = datetime.strptime(found_promo["expiry_date"], "%Y-%m-%d")
        if datetime.now() > expiry_date:
            return {"promo_status": False, "message": "This promo code has expired."}

        min_purchase = found_promo.get("min_purchase_amount", 0.0)
        if cart_total < min_purchase:
            return {"promo_status": False, "message": f"A minimum purchase of ${min_purchase:.2f} is required for this code."}

        discount_percentage = found_promo.get("discount_percentage", 0) / 100.0
        
        discount_amount = cart_total * discount_percentage
        new_total = cart_total - discount_amount

        user_cart = user_data.get("cart", {})
        user_cart["promo_code"] = promo_code
        self._update_user_data(user_id, "cart", user_cart)

        return {
            "promo_status": True,
            "message": f"Promo code '{promo_code}' applied. Discount: ${discount_amount:.2f}",
            "discount_amount": discount_amount,
            "new_total": new_total,
        }

    def remove_promo_code_from_cart(self) -> Dict[str, Union[bool, str]]:
        """
        Removes any applied promotional code from the currently logged-in user's shopping cart,
        reverting to full price calculations.
        
        Returns:
            Dict[str, Union[bool, str]]: Promo code removal result containing:
                - promo_status (bool): True if code removed, False otherwise
                - message (str): Success or error message
        
        Error Cases:
            - Not logged in: {\"promo_status\": False, \"message\": \"You must be logged in...\"}
            - User not found: {\"promo_status\": False, \"message\": \"User not found.\"}
            - No code applied: {\"promo_status\": False, \"message\": \"No promo code applied to cart.\"}
        
        Side Effects:
            - Deletes \"promo_code\" key from user_data[\"cart\"] if present
            - Future cart calculations will not include discount
            - Updates user data in-place
        
        Example:
            >>> api.remove_promo_code_from_cart()
            {\"promo_status\": True, \"message\": \"Promo code removed from cart.\"}
        
        Notes:
            - Can be called multiple times without error (idempotent if no code present)
            - Does not invalidate the promo code itself (can be reapplied)
        """
        login_check = self._require_login()
        if login_check:
            return {"promo_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"promo_status": False, "message": "User not found."}

        user_cart = user_data.get("cart", {})
        if "promo_code" in user_cart:
            del user_cart["promo_code"]
            self._update_user_data(user_id, "cart", user_cart)
            return {"promo_status": True, "message": "Promo code removed from cart."}
        return {"promo_status": False, "message": "No promo code applied to cart."}

    def checkout(
        self, delivery_address_id: str, payment_card_id: str, promo_code: Union[str, None] = None
    ) -> Dict[str, Union[bool, str, Dict]]:
        """
        Processes the checkout operation for the currently logged-in user, creating an order,
        deducting inventory, processing payment, and clearing the cart.
        
        Args:
            delivery_address_id (str): The UUID of a saved address to use for delivery.
                                       Must exist in user's addresses.
            payment_card_id (str): The UUID of a saved payment card to use for payment.
                                  Must exist in user's payment cards.
            promo_code (Union[str, None], optional): Optional promotional code to apply at checkout.
                                                     If None, uses code from cart if present.
                                                     Default is None.
        
        Returns:
            Dict[str, Union[bool, str, Dict]]: Checkout result containing:
                - checkout_status (bool): True if checkout successful, False otherwise
                - message (str): Success or error message
                - order (Dict): Complete order details (only on success) including:
                    - order_date (str): Date order placed (YYYY-MM-DD format)
                    - total_amount (float): Final amount charged (after discount if applied)
                    - products (Dict): Product IDs mapped to quantities ordered
                    - delivery_address_id (str): Address ID for delivery
                    - payment_card_id (str): Payment card ID used
                    - status (str): Order status (always \"pending\" on creation)
                    - promo_code_applied (str): Promo code used, or None
                    - tracking_number (str): Generated tracking number (format: TRK<8 chars>)
        
        Error Cases:
            - Not logged in: {\"checkout_status\": False, \"message\": \"You must be logged in...\"}
            - User not found: {\"checkout_status\": False, \"message\": \"User not found.\"}
            - Empty cart: {\"checkout_status\": False, \"message\": \"Cart is empty.\"}
            - Invalid address: {\"checkout_status\": False, \"message\": \"Delivery address not found.\"}
            - Invalid payment: {\"checkout_status\": False, \"message\": \"Payment card not found.\"}
            - Insufficient stock: {\"checkout_status\": False, \"message\": \"Not enough stock for product ID X.\"}
            - Insufficient balance: {\"checkout_status\": False, \"message\": \"Insufficient balance.\"}
        
        Side Effects:
            - Deducts product stock from self.state[\"products\"][product_id][\"stock\"]
            - Deducts total_amount from user_data[\"balance\"]
            - Creates new order in user_data[\"orders\"] with UUID key
            - Clears user_data[\"cart\"] (sets to empty dict)
            - Generates unique tracking number for order
            - Updates user data in-place
        
        Example:
            >>> api.checkout(\"addr-123\", \"card-456\", \"SAVE20\")
            {\"checkout_status\": True, \"message\": \"Checkout successful. Order placed.\",
             \"order\": {\"order_date\": \"2025-12-13\", \"total_amount\": 80.0, ...}}
        
        Notes:
            - Promo code validation is performed (active, not expired, minimum met)
            - Stock is checked before charging user (atomic operation)
            - If stock check fails, no changes are made to user balance or cart
            - Balance must cover final discounted amount
            - Cart promo_code is used if no promo_code parameter provided
        """
        login_check = self._require_login()
        if login_check:
            return {"checkout_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"checkout_status": False, "message": "User not found."}

        user_cart = user_data.get("cart", {})
        if not user_cart:
            return {"checkout_status": False, "message": "Cart is empty."}

        if delivery_address_id not in user_data.get("addresses", {}):
            return {"checkout_status": False, "message": "Delivery address not found."}
        if payment_card_id not in user_data.get("payment_cards", {}):
            return {"checkout_status": False, "message": "Payment card not found."}

        total_amount = 0.0
        products_in_order = {}
        for product_id, quantity in user_cart.items():
            if product_id == "promo_code":
                continue
            product_info = self.state["products"].get(product_id)
            if not product_info or product_info["stock"] < quantity:
                return {"checkout_status": False, "message": f"Not enough stock for product ID {product_id}."}
            total_amount += product_info["price"] * quantity
            products_in_order[product_id] = quantity

        # Apply promo code if provided or if one is in the cart
        promo_code_to_use = promo_code or user_cart.get("promo_code")
        if promo_code_to_use:
            found_promo = None
            for promo_details in self.state.get("promotions", {}).values():
                if promo_details.get("code") == promo_code_to_use:
                    found_promo = promo_details
                    break
            
            if found_promo and found_promo.get("is_active", False):
                expiry_date = datetime.strptime(found_promo["expiry_date"], "%Y-%m-%d")
                if datetime.now() <= expiry_date:
                    min_purchase = found_promo.get("min_purchase_amount", 0.0)
                    if total_amount >= min_purchase:
                        discount_percentage = found_promo.get("discount_percentage", 0) / 100.0
                        total_amount = total_amount * (1 - discount_percentage)

        if user_data["balance"] < total_amount:
            return {"checkout_status": False, "message": "Insufficient balance."}

        for product_id, quantity in products_in_order.items():
            self.state["products"][product_id]["stock"] -= quantity
        user_data["balance"] -= total_amount

        new_order_id = str(uuid.uuid4())
        user_orders = user_data.get("orders", {})
        user_orders[new_order_id] = {
            "order_date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": total_amount,
            "products": products_in_order,
            "delivery_address_id": delivery_address_id,
            "payment_card_id": payment_card_id,
            "status": "pending",
            "promo_code_applied": promo_code,
            "tracking_number": f"TRK{str(uuid.uuid4())[:8].upper()}"
        }
        self._update_user_data(user_id, "orders", user_orders)
        self._update_user_data(user_id, "balance", user_data["balance"])
        self._update_user_data(user_id, "cart", {})

        return {
            "checkout_status": True,
            "message": "Checkout successful. Order placed.",
            "order": user_orders[new_order_id],
        }

    def show_orders(
        self, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, str, List[Dict]]]:
        """
        Retrieves a paginated list of the currently logged-in user's order history
        with complete order details.
        
        Args:
            page_index (int, optional): The page number to retrieve (1-indexed). Default is 1.
            page_limit (int, optional): The number of orders per page. Default is 10.
        
        Returns:
            Dict[str, Union[bool, str, List[Dict]]]: Orders result containing:
                - orders_status (bool): True if orders retrieved (even if empty), False on error
                - message (str): Error description if applicable
                - orders (List[Dict]): List of order objects, each containing:
                    - order_date (str): Date order was placed
                    - total_amount (float): Total amount paid
                    - products (Dict): Product IDs to quantities
                    - delivery_address_id (str): Address ID used
                    - payment_card_id (str): Payment card ID used
                    - status (str): Order status (e.g., \"pending\", \"shipped\", \"delivered\")
                    - promo_code_applied (str): Promo code used, or None
                    - tracking_number (str): Package tracking number
        
        Error Cases:
            - Not logged in: {\"orders_status\": False, \"message\": \"You must be logged in...\", \"orders\": []}
            - User not found: {\"orders_status\": False, \"message\": \"User not found.\", \"orders\": []}
        
        Example:
            >>> api.show_orders(page_index=1, page_limit=5)
            {\"orders_status\": True, \"orders\": [{\"order_date\": \"2025-12-13\", \"total_amount\": 99.99, ...}]}
        
        Notes:
            - Returns empty list if user has no orders
            - Page indices beyond available data return empty list
            - Order IDs are not included in returned data (only order details)
            - Orders are not sorted (returned in arbitrary dict iteration order)
        """
        login_check = self._require_login()
        if login_check:
            return {"orders_status": False, "message": login_check["message"], "orders": []}
        
        user_data = self._get_current_user_data()
        if not user_data:
            return {"orders_status": False, "message": "User not found.", "orders": []}

        all_orders = list(user_data.get("orders", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_orders = all_orders[start_index:end_index]

        return {"orders_status": True, "orders": paginated_orders}

    def add_to_wish_list(self, product_id: str) -> Dict[str, Union[bool, str]]:
        """
        Adds a product to the currently logged-in user's wish list for future reference,
        preventing duplicate entries and recording the addition date.
        
        Args:
            product_id (str): The unique identifier of the product to add to the wish list.
        
        Returns:
            Dict[str, Union[bool, str]]: Wish list addition result containing:
                - wishlist_status (bool): True if product added, False otherwise
                - message (str): Success or error message
        
        Error Cases:
            - Not logged in: {\"wishlist_status\": False, \"message\": \"You must be logged in...\"}
            - User not found: {\"wishlist_status\": False, \"message\": \"User not found.\"}
            - Product not found: {\"wishlist_status\": False, \"message\": \"Product not found.\"}
            - Already in list: {\"wishlist_status\": False, \"message\": \"Product already in wish list.\"}
        
        Side Effects:
            - Appends {\"product_id\": str, \"added_date\": str} to user_data[\"wish_list\"]
            - Records current date in YYYY-MM-DD format
            - Updates user data in-place
        
        Example:
            >>> api.add_to_wish_list(\"prod-123\")
            {\"wishlist_status\": True, \"message\": \"Product added to wish list.\"}
        
        Notes:
            - Duplicate check compares product_id only
            - Does not check if product is in cart or already ordered
            - Wish list items are stored as list (not dict) with embedded product_id
        """
        login_check = self._require_login()
        if login_check:
            return {"wishlist_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"wishlist_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"wishlist_status": False, "message": "Product not found."}

        user_wish_list = user_data.get("wish_list", [])
        # Check if already in wish list
        for item in user_wish_list:
            if item.get("product_id") == product_id:
                return {"wishlist_status": False, "message": "Product already in wish list."}

        user_wish_list.append({"product_id": product_id, "added_date": datetime.now().strftime("%Y-%m-%d")})
        self._update_user_data(user_id, "wish_list", user_wish_list)
        return {"wishlist_status": True, "message": "Product added to wish list."}

    def remove_from_wish_list(self, product_id: str) -> Dict[str, Union[bool, str]]:
        """
        Removes a product from the currently logged-in user's wish list by product ID.
        
        Args:
            product_id (str): The unique identifier of the product to remove from the wish list.
        
        Returns:
            Dict[str, Union[bool, str]]: Wish list removal result containing:
                - wishlist_status (bool): True if product removed, False otherwise
                - message (str): Success or error message
        
        Error Cases:
            - Not logged in: {\"wishlist_status\": False, \"message\": \"You must be logged in...\"}
            - User not found: {\"wishlist_status\": False, \"message\": \"User not found.\"}
            - Product not in list: {\"wishlist_status\": False, \"message\": \"Product not found in wish list.\"}
        
        Side Effects:
            - Removes matching item from user_data[\"wish_list\"] list
            - Updates user data in-place
        
        Example:
            >>> api.remove_from_wish_list(\"prod-123\")
            {\"wishlist_status\": True, \"message\": \"Product removed from wish list.\"}
        
        Notes:
            - Only removes first matching product_id (though duplicates shouldn't exist)
            - Cannot be undone; added_date is lost
        """
        login_check = self._require_login()
        if login_check:
            return {"wishlist_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"wishlist_status": False, "message": "User not found."}

        user_wish_list = user_data.get("wish_list", [])
        for i, item in enumerate(user_wish_list):
            if item.get("product_id") == product_id:
                user_wish_list.pop(i)
                self._update_user_data(user_id, "wish_list", user_wish_list)
                return {"wishlist_status": True, "message": "Product removed from wish list."}
        return {"wishlist_status": False, "message": "Product not found in wish list."}

    def show_wish_list(self) -> Dict[str, Union[bool, str, List[Dict]]]:
        """
        Retrieves the complete contents of the currently logged-in user's wish list
        with detailed product information and addition dates.
        
        Returns:
            Dict[str, Union[bool, str, List[Dict]]]: Wish list result containing:
                - wishlist_status (bool): True if wish list retrieved (even if empty), False on error
                - message (str): Error description if applicable
                - wishlist (List[Dict]): List of wish list items, each containing:
                    - product_id (str): The product's unique identifier
                    - name (str): Product name
                    - price (float): Current product price
                    - added_date (str): Date added to wish list (YYYY-MM-DD format)
        
        Error Cases:
            - Not logged in: {\"wishlist_status\": False, \"message\": \"You must be logged in...\", \"wishlist\": []}
            - User not found: {\"wishlist_status\": False, \"message\": \"User not found.\", \"wishlist\": []}
        
        Example:
            >>> api.show_wish_list()
            {\"wishlist_status\": True, \"wishlist\": [
                {\"product_id\": \"prod-123\", \"name\": \"Laptop\", \"price\": 999.99, \"added_date\": \"2025-12-01\"}
            ]}
        
        Notes:
            - Returns empty list if wish list is empty
            - Silently omits products that no longer exist in product catalog
            - Product prices are current, not from when added to wish list
        """
        login_check = self._require_login()
        if login_check:
            return {"wishlist_status": False, "message": login_check["message"], "wishlist": []}
        
        user_data = self._get_current_user_data()
        if not user_data:
            return {"wishlist_status": False, "message": "User not found.", "wishlist": []}

        wish_list_items = []
        for item in user_data.get("wish_list", []):
            product_id = item.get("product_id")
            product_info = self.state["products"].get(product_id)
            if product_info:
                wish_list_items.append(
                    {   
                        "product_id": product_id,
                        "name": product_info["name"],
                        "price": product_info["price"],
                        "added_date": item["added_date"],
                    }
                )
        return {"wishlist_status": True, "wishlist": wish_list_items}

    def search_products(
        self, query: str, category: Union[str, None] = None, min_price: float = 0.0, max_price: float = float('inf')
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Searches for products matching specified criteria including text query, category filter,
        and price range constraints.
        
        Args:
            query (str): Search text to match against product names and descriptions.
                        Case-insensitive partial matching.
            category (Union[str, None], optional): Filter by product category. If None, all categories
                                                   included. Case-insensitive exact match. Default is None.
            min_price (float, optional): Minimum price filter (inclusive). Default is 0.0.
            max_price (float, optional): Maximum price filter (inclusive). Default is infinity.
        
        Returns:
            Dict[str, Union[bool, List[Dict]]]: Search results containing:
                - search_status (bool): Always True (even if no results)
                - products (List[Dict]): List of matching product objects, each containing:
                    - product_id (str): Product's unique identifier
                    - name (str): Product name
                    - description (str): Product description
                    - price (float): Product price
                    - stock (int): Available inventory
                    - category (str): Product category
                    (Plus any other fields in product record)
        
        Example:
            >>> api.search_products("laptop", category="Electronics", min_price=500, max_price=1500)
            {"search_status": True, "products": [
                {"product_id": "prod-123", "name": "Gaming Laptop", "price": 999.99, ...}
            ]}
        
        Notes:
            - Query searches both name and description fields
            - Returns empty list if no products match
            - All filters are AND-ed together
            - Does not require user login
        """
        results = []
        for product_id, product_info in self.state["products"].items():
            if (
                query.lower() in product_info["name"].lower()
                or query.lower() in product_info["description"].lower()
            ) and (category is None or product_info["category"].lower() == category.lower()) and (
                min_price <= product_info["price"] <= max_price
            ):
                results.append({"product_id": product_id, **product_info})
        return {"search_status": True, "products": results}

    def show_product_details(self, product_id: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves detailed information about a specific product by its ID.
        
        Args:
            product_id (str): The unique identifier of the product to retrieve.
        
        Returns:
            Dict[str, Union[bool, Dict]]: Product details result containing:
                - product_status (bool): True if product found, False otherwise
                - product (Dict): Complete product information including:
                    - name (str): Product name
                    - description (str): Product description
                    - price (float): Product price
                    - stock (int): Available inventory
                    - category (str): Product category
                    (Plus any other fields in product record)
                    Returns empty dict if not found.
        
        Example:
            >>> api.show_product_details("prod-123")
            {"product_status": True, "product": {"name": "Laptop", "price": 999.99, ...}}
        
        Notes:
            - Does not require user login
            - Returns reference to actual product data, not a copy
            - product_status False with empty dict if product_id not found
        """
        product_info = self.state["products"].get(product_id)
        if product_info:
            return {"product_status": True, "product": product_info}
        return {"product_status": False, "product": {}}

    def submit_product_review(
        self, product_id: str, rating: int, comment: str
    ) -> Dict[str, Union[bool, str]]:
        """
        Submits a product review with rating and comment from the currently logged-in user,
        associating it with the product for public display.
        
        Args:
            product_id (str): The unique identifier of the product being reviewed.
            rating (int): The rating score. Typically 1-5 stars, but no validation enforced.
            comment (str): The detailed review text describing the user's experience.
        
        Returns:
            Dict[str, Union[bool, str]]: Review submission result containing:
                - submit_review_status (bool): True if review submitted, False otherwise
                - message (str): Success or error message
                - review_id (str): The newly generated UUID for the review (only on success)
        
        Error Cases:
            - Not logged in: {"submit_review_status": False, "message": "You must be logged in..."}
            - User not found: {"submit_review_status": False, "message": "User not found."}
            - Product not found: {"submit_review_status": False, "message": "Product not found."}
        
        Side Effects:
            - Appends review to self.state["product_reviews"][product_id] list
            - Creates product_reviews entry if product has no previous reviews
            - Records current date in YYYY-MM-DD format
            - Review includes user_id for attribution
        
        Example:
            >>> api.submit_product_review("prod-123", 5, "Excellent product, highly recommend!")
            {"submit_review_status": True, "message": "Review submitted successfully.", "review_id": "rev-abc..."}
        
        Notes:
            - No validation of rating range or comment length
            - User can submit multiple reviews for same product
            - Does not check if user actually purchased the product
        """
        login_check = self._require_login()
        if login_check:
            return {"submit_review_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"submit_review_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"submit_review_status": False, "message": "Product not found."}

        new_review_id = str(uuid.uuid4())
        product_reviews = self.state["product_reviews"].get(product_id, [])
        product_reviews.append(
            {
                "review_id": new_review_id,
                "user_id": user_id,
                "rating": rating,
                "comment": comment,
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
        )
        self.state["product_reviews"][product_id] = product_reviews
        return {"submit_review_status": True, "message": "Review submitted successfully.", "review_id": new_review_id}

    def show_product_reviews(
        self, product_id: str, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves a paginated list of reviews for a specific product, including reviewer information.
        
        Args:
            product_id (str): The unique identifier of the product whose reviews to retrieve.
            page_index (int, optional): The page number to retrieve (1-indexed). Default is 1.
            page_limit (int, optional): The number of reviews per page. Default is 10.
        
        Returns:
            Dict[str, Union[bool, List[Dict]]]: Product reviews result containing:
                - reviews_status (bool): Always True (even if no reviews)
                - reviews (List[Dict]): List of review objects, each containing:
                    - review_id (str): Review's unique identifier
                    - user_id (str): Reviewer's user ID
                    - user_email (str): Reviewer's email address (looked up from user_id)
                    - rating (int): Rating score given
                    - comment (str): Review text
                    - date (str): Review submission date (YYYY-MM-DD format)
        
        Example:
            >>> api.show_product_reviews("prod-123", page_index=1, page_limit=5)
            {"reviews_status": True, "reviews": [
                {"review_id": "rev-abc", "user_email": "john@example.com", "rating": 5, ...}
            ]}
        
        Notes:
            - Returns empty list if product has no reviews or page beyond available data
            - Does not require user login
            - Adds user_email to each review by looking up user_id
            - Does not validate product_id existence
        """
        reviews = self.state["product_reviews"].get(product_id, [])
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_reviews = reviews[start_index:end_index]

        display_reviews = []
        for review in paginated_reviews:
            review_copy = review.copy()
            for u_id, u_data in self.state["users"].items():
                if u_id == review_copy["user_id"]:
                    review_copy["user_email"] = u_data["email"]
                    break
            display_reviews.append(review_copy)

        return {"reviews_status": True, "reviews": display_reviews}

    def ask_product_question(
        self, product_id: str, question: str
    ) -> Dict[str, Union[bool, str]]:
        """
        Submits a question about a specific product from the currently logged-in user,
        allowing other users or sellers to provide answers.
        
        Args:
            product_id (str): The unique identifier of the product the question is about.
            question (str): The question text to submit.
        
        Returns:
            Dict[str, Union[bool, str]]: Question submission result containing:
                - ask_question_status (bool): True if question submitted, False otherwise
                - message (str): Success or error message
                - question_id (str): The newly generated UUID for the question (only on success)
        
        Error Cases:
            - Not logged in: {"ask_question_status": False, "message": "You must be logged in..."}
            - User not found: {"ask_question_status": False, "message": "User not found."}
            - Product not found: {"ask_question_status": False, "message": "Product not found."}
        
        Side Effects:
            - Creates or appends to self.state["product_questions"][product_id]["q_and_as"]
            - Initializes product_questions entry if product has no previous questions
            - Records current date in YYYY-MM-DD format
            - Answer field initialized to "..." (unanswered placeholder)
        
        Example:
            >>> api.ask_product_question("prod-123", "Is this compatible with Mac OS?")
            {"ask_question_status": True, "message": "Question submitted successfully.", "question_id": "q-xyz..."}
        
        Notes:
            - Questions start with answer="..." until someone answers
            - No validation of question text length or content
            - User can ask multiple questions about same product
        """
        login_check = self._require_login()
        if login_check:
            return {"ask_question_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"ask_question_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"ask_question_status": False, "message": "Product not found."}

        if product_id not in self.state["product_questions"]:
            self.state["product_questions"][product_id] = {"product_id": product_id, "q_and_as": []}

        qa_list = self.state["product_questions"][product_id]["q_and_as"]
        new_question_id = str(uuid.uuid4())
        qa_list.append({
            "id": new_question_id,
            "user_id": user_id,
            "question": question,
            "answer": "...",
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        return {"ask_question_status": True, "message": "Question submitted successfully.", "question_id": new_question_id}

    def answer_product_question(
            self, product_id: str, question_id: str, answer: str
        ) -> Dict[str, Union[bool, str]]:
        """
        Provides an answer to a previously asked product question from the currently logged-in user.
        
        Args:
            product_id (str): The unique identifier of the product the question is about.
            question_id (str): The unique identifier of the question to answer.
            answer (str): The answer text to provide.
        
        Returns:
            Dict[str, Union[bool, str]]: Answer submission result containing:
                - answer_question_status (bool): True if answer submitted, False otherwise
                - message (str): Success or error message
                - qa_id (str): The question_id that was answered (only on success)
        
        Error Cases:
            - Not logged in: {"answer_question_status": False, "message": "You must be logged in..."}
            - User not found: {"answer_question_status": False, "message": "User not found."}
            - Product not found: {"answer_question_status": False, "message": "Product not found."}
            - Question not found: {"answer_question_status": False, "message": "Question not found."}
        
        Side Effects:
            - Updates question's answer field in self.state["product_questions"][product_id]["q_and_as"]
            - Records answer_user_id (currently logged-in user)
            - Records answer_date in YYYY-MM-DD format
            - Replaces any existing answer (does not prevent multiple answers)
        
        Example:
            >>> api.answer_product_question("prod-123", "q-xyz", "Yes, it works with Mac OS Big Sur and later.")
            {"answer_question_status": True, "message": "Answer submitted successfully.", "qa_id": "q-xyz"}
        
        Notes:
            - Any logged-in user can answer any question (not restricted to product owner/seller)
            - Can overwrite existing answers
            - No notification system to alert question asker
        """
        login_check = self._require_login()
        if login_check:
            return {"answer_question_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"answer_question_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"answer_question_status": False, "message": "Product not found."}

        container = self.state["product_questions"].get(product_id)

        if container:
            for qa_pair in container.get("q_and_as", []):
                if qa_pair.get("id") == question_id:
                    qa_pair["answer"] = answer
                    qa_pair["answer_user_id"] = user_id
                    qa_pair["answer_date"] = datetime.now().strftime("%Y-%m-%d")

                    return {
                        "answer_question_status": True,
                        "message": "Answer submitted successfully.",
                        "qa_id": question_id
                    }
        return {"answer_question_status": False, "message": "Question not found."}

    def show_product_questions(
        self, product_id: str, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves a paginated list of questions and answers for a specific product,
        including asker and answerer information.
        
        Args:
            product_id (str): The unique identifier of the product whose Q&A to retrieve.
            page_index (int, optional): The page number to retrieve (1-indexed). Default is 1.
            page_limit (int, optional): The number of Q&A pairs per page. Default is 10.
        
        Returns:
            Dict[str, Union[bool, List[Dict]]]: Product questions result containing:
                - questions_status (bool): Always True (even if no questions)
                - questions (List[Dict]): List of Q&A objects, each containing:
                    - id (str): Question's unique identifier
                    - user_id (str): Asker's user ID
                    - user_email (str): Asker's email (looked up from user_id)
                    - question (str): Question text
                    - answer (str): Answer text ("..." if unanswered)
                    - date (str): Question submission date (YYYY-MM-DD)
                    - answer_user_id (str): Answerer's user ID (if answered)
                    - answer_user_email (str): Answerer's email (if answered, looked up)
                    - answer_date (str): Answer submission date (if answered)
        
        Example:
            >>> api.show_product_questions("prod-123", page_index=1, page_limit=5)
            {"questions_status": True, "questions": [
                {"id": "q-xyz", "user_email": "john@example.com", "question": "Compatible with Mac?",
                 "answer": "Yes!", "answer_user_email": "seller@example.com", ...}
            ]}
        
        Notes:
            - Returns empty list if product has no questions or page beyond available data
            - Does not require user login
            - Adds user_email for both asker and answerer by looking up user_ids
            - Does not validate product_id existence
            - Returns True for questions_status even if product not found
        """
        container = self.state["product_questions"].get(product_id)
        if not container:
            return {"questions_status": True, "questions": []}
        
        qa_list = container.get("q_and_as", [])
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_qa = qa_list[start_index:end_index]

        display_questions = []
        for qa in paginated_qa:
            qa_copy = qa.copy()
            # Add user email for asker
            for u_id, u_data in self.state["users"].items():
                if u_id == qa_copy.get("user_id"):
                    qa_copy["user_email"] = u_data["email"]
                    break
            # If answered, add answer user email
            if qa_copy.get("answer_user_id"):
                for u_id, u_data in self.state["users"].items():
                    if u_id == qa_copy["answer_user_id"]:
                        qa_copy["answer_user_email"] = u_data["email"]
                        break
            display_questions.append(qa_copy)

        return {"questions_status": True, "questions": display_questions}

    def subscribe_prime(
        self, duration: Literal["monthly", "yearly"]
    ) -> Dict[str, Union[bool, str, str]]:
        """
        Subscribes the currently logged-in user to an Amazon Prime membership with automatic
        expiration date calculation based on duration.
        
        Args:
            duration (Literal["monthly", "yearly"]): The subscription period. Must be either
                                                      "monthly" (30 days) or "yearly" (365 days).
        
        Returns:
            Dict[str, Union[bool, str, str]]: Prime subscription result containing:
                - subscribe_status (bool): True if subscribed, False otherwise
                - message (str): Success message with duration, or error description
                - prime_subscription_id (str): Newly generated UUID for subscription (only on success)
        
        Error Cases:
            - Not logged in: {"subscribe_status": False, "message": "You must be logged in..."}
            - User not found: {"subscribe_status": False, "message": "User not found."}
            - Active subscription: {"subscribe_status": False, "message": "You already have an active Prime subscription."}
        
        Side Effects:
            - Creates new subscription in user_data["prime_subscriptions"] with UUID key
            - Sets start_date to current date (YYYY-MM-DD format)
            - Calculates end_date: +30 days for monthly, +365 days for yearly
            - Sets status to "active"
            - Records plan_type (monthly or yearly)
        
        Example:
            >>> api.subscribe_prime("yearly")
            {"subscribe_status": True, "message": "Successfully subscribed to yearly Prime plan.",
             "prime_subscription_id": "sub-abc..."}
        
        Notes:
            - Checks for active subscriptions with end_date > current date
            - Does not charge user balance (payment not simulated)
            - Multiple expired subscriptions allowed, but only one active at a time
            - Does not auto-renew subscriptions
        """
        login_check = self._require_login()
        if login_check:
            return {"subscribe_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"subscribe_status": False, "message": "User not found."}

        for _, sub_data in user_data.get("prime_subscriptions", {}).items():
            if sub_data["status"] == "active" and datetime.strptime(sub_data["end_date"], "%Y-%m-%d") > datetime.now():
                return {"subscribe_status": False, "message": "You already have an active Prime subscription."}

        new_subscription_id = str(uuid.uuid4())
        start_date = datetime.now()
        if duration == "monthly":
            end_date = start_date + timedelta(days=30)
        else:
            end_date = start_date + timedelta(days=365)

        new_subscription = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "plan_type": duration,
            "status": "active",
        }

        user_prime_subscriptions = user_data.get("prime_subscriptions", {})
        user_prime_subscriptions[new_subscription_id] = new_subscription
        self._update_user_data(user_id, "prime_subscriptions", user_prime_subscriptions)

        return {"subscribe_status": True, "message": f"Successfully subscribed to {duration} Prime plan.", "prime_subscription_id": new_subscription_id}

    def show_prime_subscriptions(
        self, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, str, List[Dict]]]:
        """
        Retrieves a paginated list of the currently logged-in user's Amazon Prime subscription
        history, including both active and expired subscriptions.
        
        Args:
            page_index (int, optional): The page number to retrieve (1-indexed). Default is 1.
            page_limit (int, optional): The number of subscriptions per page. Default is 10.
        
        Returns:
            Dict[str, Union[bool, str, List[Dict]]]: Prime subscriptions result containing:
                - subscriptions_status (bool): True if subscriptions retrieved (even if empty), False on error
                - message (str): Error description if applicable
                - prime_subscriptions (List[Dict]): List of subscription objects, each containing:
                    - start_date (str): Subscription start date (YYYY-MM-DD)
                    - end_date (str): Subscription end date (YYYY-MM-DD)
                    - plan_type (str): \"monthly\" or \"yearly\"
                    - status (str): \"active\" or other status
        
        Error Cases:
            - Not logged in: {"subscriptions_status": False, "message": "You must be logged in...", "prime_subscriptions": []}
            - User not found: {"subscriptions_status": False, "message": "User not found.", "prime_subscriptions": []}
        
        Example:
            >>> api.show_prime_subscriptions(page_index=1, page_limit=5)
            {"subscriptions_status": True, "prime_subscriptions": [
                {"start_date": "2025-01-01", "end_date": "2026-01-01", "plan_type": "yearly", "status": "active"}
            ]}
        
        Notes:
            - Returns empty list if user has no subscriptions
            - Includes both active and expired subscriptions
            - Subscription IDs are not included in returned data
        """
        login_check = self._require_login()
        if login_check:
            return {"subscriptions_status": False, "message": login_check["message"], "prime_subscriptions": []}
        
        user_data = self._get_current_user_data()
        if not user_data:
            return {"subscriptions_status": False, "message": "User not found.", "prime_subscriptions": []}

        all_subscriptions = list(user_data.get("prime_subscriptions", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_subscriptions = all_subscriptions[start_index:end_index]

        return {"subscriptions_status": True, "prime_subscriptions": paginated_subscriptions}

    def request_return(
        self, order_id: str, product_id: str, reason: str
    ) -> Dict[str, Union[bool, str, str]]:
        """
        Initiates a return request for a specific product from a placed order,
        recording the reason and creating a pending return.
        
        Args:
            order_id (str): The unique UUID identifier of the order containing the product.
            product_id (str): The unique identifier of the product to return from that order.
            reason (str): The reason for the return request (e.g., \"defective\", \"wrong item\", \"changed mind\").
        
        Returns:
            Dict[str, Union[bool, str, str]]: Return request result containing:
                - return_status (bool): True if return initiated, False otherwise
                - message (str): Success or error message
                - return_id (str): Newly generated UUID for the return (only on success)
        
        Error Cases:
            - Not logged in: {"return_status": False, "message": "You must be logged in..."}
            - User not found: {"return_status": False, "message": "User not found."}
            - Order not found: {"return_status": False, "message": "Order not found."}
            - Product not in order: {"return_status": False, "message": "Product not found in this order."}
        
        Side Effects:
            - Creates new return in user_data["returns"] with UUID key
            - Records order_id, product_id, reason
            - Sets return_date to current date (YYYY-MM-DD format)
            - Sets status to \"pending\"
        
        Example:
            >>> api.request_return("order-123", "prod-456", "Item was damaged during shipping")
            {"return_status": True, "message": "Return request submitted.", "return_id": "ret-xyz..."}
        
        Notes:
            - Does not refund user balance (refund processing not simulated)
            - Does not restore product stock
            - Does not remove product from order
            - Multiple return requests can be created for same product
            - No validation of return eligibility or time limits
        """
        login_check = self._require_login()
        if login_check:
            return {"return_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()
        if not user_data:
            return {"return_status": False, "message": "User not found."}

        user_orders = user_data.get("orders", {})
        if order_id not in user_orders:
            return {"return_status": False, "message": "Order not found."}

        order_products = user_orders[order_id]["products"]
        if product_id not in order_products:
            return {"return_status": False, "message": "Product not found in this order."}

        new_return_id = str(uuid.uuid4())
        user_returns = user_data.get("returns", {})
        user_returns[new_return_id] = {
            "order_id": order_id,
            "product_id": product_id,
            "return_date": datetime.now().strftime("%Y-%m-%d"),
            "reason": reason,
            "status": "pending",
        }
        self._update_user_data(user_id, "returns", user_returns)
        return {"return_status": True, "message": "Return request submitted.", "return_id": new_return_id}

    def show_returns(
        self, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, str, List[Dict]]]:
        """
        Retrieves a paginated list of the currently logged-in user's return request history
        with all return details.
        
        Args:
            page_index (int, optional): The page number to retrieve (1-indexed). Default is 1.
            page_limit (int, optional): The number of returns per page. Default is 10.
        
        Returns:
            Dict[str, Union[bool, str, List[Dict]]]: Returns result containing:
                - returns_status (bool): True if returns retrieved (even if empty), False on error
                - message (str): Error description if applicable
                - returns (List[Dict]): List of return objects, each containing:
                    - order_id (str): Order ID the return is associated with
                    - product_id (str): Product ID being returned
                    - return_date (str): Date return was requested (YYYY-MM-DD)
                    - reason (str): Reason for return
                    - status (str): Return status (e.g., \"pending\", \"approved\", \"completed\")
        
        Error Cases:
            - Not logged in: {\"returns_status\": False, \"message\": \"You must be logged in...\", \"returns\": []}
            - User not found: {\"returns_status\": False, \"message\": \"User not found.\", \"returns\": []}
        
        Example:
            >>> api.show_returns(page_index=1, page_limit=5)
            {\"returns_status\": True, \"returns\": [
                {\"order_id\": \"order-123\", \"product_id\": \"prod-456\", \"return_date\": \"2025-12-13\",
                 \"reason\": \"Item was damaged\", \"status\": \"pending\"}
            ]}
        
        Notes:
            - Returns empty list if user has no return requests
            - Page indices beyond available data return empty list
            - Return IDs are not included in returned data
            - Returns are not sorted (returned in arbitrary dict iteration order)
        """
        login_check = self._require_login()
        if login_check:
            return {"returns_status": False, "message": login_check["message"], "returns": []}
        
        user_data = self._get_current_user_data()
        if not user_data:
            return {"returns_status": False, "message": "User not found.", "returns": []}

        all_returns = list(user_data.get("returns", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_returns = all_returns[start_index:end_index]

        return {"returns_status": True, "returns": paginated_returns}

    def get_seller_info(self, seller_id: int) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves detailed information about a specific seller registered in the system.
        
        Args:
            seller_id (int): The unique numeric identifier of the seller to retrieve information for.
        
        Returns:
            Dict[str, Union[bool, Dict]]: Seller information result containing:
                - seller_status (bool): True if seller found, False otherwise
                - seller_info (Dict): Complete seller information (structure depends on state data),
                                     typically including seller name, rating, contact info, etc.
                                     Returns empty dict if seller not found.
        
        Example:
            >>> api.get_seller_info(12345)
            {\"seller_status\": True, \"seller_info\": {\"name\": \"TechStore Inc\", \"rating\": 4.5, ...}}
        
        Notes:
            - Does not require user login
            - Returns reference to actual seller data, not a copy
            - seller_id is integer (unlike most other IDs which are UUID strings)
            - seller_status False with empty dict if seller_id not found
        """
        seller_info = self.state["sellers"].get(seller_id)
        if seller_info:
            return {"seller_status": True, "seller_info": seller_info}
        return {"seller_status": False, "seller_info": {}}