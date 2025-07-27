from copy import deepcopy
from typing import Dict, List, Optional, Union

DEFAULT_STATE = {
    "users": {
        "alice.smith@gmail.com": {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@gmail.com",
            "balance": 100.00,
            "friends": ["bob.johnson@yahoo.com", "charlie.brown@outlook.com"],
            "payment_cards": {
                "card_1": {"card_name": "My Debit Card", "owner_name": "Alice Smith", "card_number": "4111222233334444", "expiry_year": 2028, "expiry_month": 12, "cvv_number": "123"}
            }
        },
        "bob.johnson@yahoo.com": {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@yahoo.com",
            "balance": 50.00,
            "friends": ["alice.smith@gmail.com", "diana.prince@protonmail.com"],
            "payment_cards": {
                "card_1": {"card_name": "Bob's Visa", "owner_name": "Bob Johnson", "card_number": "4222333344445555", "expiry_year": 2026, "expiry_month": 7, "cvv_number": "456"}
            }
        },
        "charlie.brown@outlook.com": {
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "charlie.brown@outlook.com",
            "balance": 25.50,
            "friends": ["alice.smith@gmail.com"],
            "payment_cards": {}
        },
        "diana.prince@protonmail.com": {
            "first_name": "Diana",
            "last_name": "Prince",
            "email": "diana.prince@protonmail.com",
            "balance": 75.20,
            "friends": ["bob.johnson@yahoo.com"],
            "payment_cards": {
                "card_1": {"card_name": "My Credit Card", "owner_name": "Diana Prince", "card_number": "5111222233334444", "expiry_year": 2029, "expiry_month": 3, "cvv_number": "789"}
            }
        },
        "eve.davis@hotmail.com": {
            "first_name": "Eve",
            "last_name": "Davis",
            "email": "eve.davis@hotmail.com",
            "balance": 150.00,
            "friends": [],
            "payment_cards": {}
        }
    },
    "current_user": "alice.smith@gmail.com",
    "transactions": {},
    "payment_cards": {}, # This might be used for a global lookup or to store card details not directly tied to a user for some reason.
    "payment_requests": {},
    "transaction_comments": {},
    "notifications": {},
    "friends": {}, # This can be used for a global friends list if relationships are complex, otherwise redundant with user's friends list.
    "verification_codes": {},
    "password_reset_codes": {},
    "transaction_counter": 0,
    "comment_counter": 0,
    "request_counter": 0,
    "notification_counter": 0,
}

class VenmoApis:
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.current_user: Optional[str] = None
        self.transactions: Dict[int, Dict] = {}
        self.payment_cards: Dict[int, Dict] = {}
        self.payment_requests: Dict[int, Dict] = {}
        self.transaction_comments: Dict[int, Dict] = {}
        self.notifications: Dict[int, Dict] = {}
        self.friends: Dict[str, List[str]] = {}
        self.verification_codes: Dict[str, str] = {}
        self.password_reset_codes: Dict[str, str] = {}
        self.transaction_counter: int = 0
        self.comment_counter: int = 0
        self.request_counter: int = 0
        self.notification_counter: int = 0
        self._api_description = "This tool belongs to the VenmoAPI, which provides core functionality for payments, friends, and account management on Venmo."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: dict) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.transactions = scenario.get("transactions", DEFAULT_STATE_COPY["transactions"])
        self.payment_requests = scenario.get("payment_requests", DEFAULT_STATE_COPY["payment_requests"])
        self.transaction_comments = scenario.get("transaction_comments", DEFAULT_STATE_COPY["transaction_comments"])
        self.notifications = scenario.get("notifications", DEFAULT_STATE_COPY["notifications"])
        self.friends = scenario.get("friends", DEFAULT_STATE_COPY["friends"])
        self.verification_codes = scenario.get("verification_codes", DEFAULT_STATE_COPY["verification_codes"])
        self.password_reset_codes = scenario.get("password_reset_codes", DEFAULT_STATE_COPY["password_reset_codes"])
        self.transaction_counter = scenario.get("transaction_counter", DEFAULT_STATE_COPY["transaction_counter"])
        self.comment_counter = scenario.get("comment_counter", DEFAULT_STATE_COPY["comment_counter"])
        self.request_counter = scenario.get("request_counter", DEFAULT_STATE_COPY["request_counter"])
        self.notification_counter = scenario.get("notification_counter", DEFAULT_STATE_COPY["notification_counter"])

        if self.current_user and self.current_user in self.users:
            self.payment_cards = self.users[self.current_user].get("payment_cards", {})
            self.friends[self.current_user] = self.users[self.current_user].get("friends", [])

    def show_my_account_info(self) -> Dict[str, Union[bool, Dict]]:
        """
        Show account information for the current user.

        Returns:
            Dict: A dictionary containing 'account_status' (bool) and 'account_info' (Dict) if successful.
        """
        if not self.current_user or self.current_user not in self.users:
            return {"account_status": False, "account_info": {}}
        
        return {"account_status": True, "account_info": self.users[self.current_user]}

    def update_my_account_name(self, first_name: str, last_name: str) -> Dict[str, bool]:
        """
        Update the current user's first and last name.

        Args:
            first_name (str): New first name.
            last_name (str): New last name.

        Returns:
            Dict: A dictionary containing 'update_status' (bool).
        """
        if not self.current_user or self.current_user not in self.users:
            return {"update_status": False}
        
        self.users[self.current_user]["first_name"] = first_name
        self.users[self.current_user]["last_name"] = last_name
        return {"update_status": True}

    def search_for_users(self, query: str, page_index: int = 1, page_limit: int = 10) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Search for users based on a query.

        Args:
            query (str): Search query (e.g., name, email).
            page_index (int): Page index for pagination (defaults to 1).
            page_limit (int): Number of results per page (defaults to 10).

        Returns:
            Dict: A dictionary containing 'search_status' (bool) and 'users' (List[Dict]) if successful.
        """
        # Dummy search: returns users whose name or email contains the query
        found_users = [
            {"email": email, "first_name": user["first_name"], "last_name": user["last_name"]}
            for email, user in self.users.items()
            if query.lower() in user["first_name"].lower() or
               query.lower() in user["last_name"].lower() or
               query.lower() in email.lower()
        ]
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_users = found_users[start_index:end_index]

        return {"search_status": True, "users": paginated_users}

    def show_my_friends(self, query: str = "", page_index: int = 1, page_limit: int = 10) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Show friends of the current user, optionally filtered by a query.

        Args:
            query (str): Optional search query to filter friends.
            page_index (int): Page index for pagination (defaults to 1).
            page_limit (int): Number of results per page (defaults to 10).

        Returns:
            Dict: A dictionary containing 'friends_status' (bool) and 'friends' (List[Dict]) if successful.
        """
        if not self.current_user or self.current_user not in self.users:
            return {"friends_status": False, "friends": []}

        my_friends_emails = self.friends.get(self.current_user, [])
        all_my_friends_details = [
            {"email": email, "first_name": self.users[email]["first_name"], "last_name": self.users[email]["last_name"]}
            for email in my_friends_emails if email in self.users
        ]

        filtered_friends = [
            friend for friend in all_my_friends_details
            if query.lower() in friend["first_name"].lower() or
               query.lower() in friend["last_name"].lower() or
               query.lower() in friend["email"].lower()
        ]
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_friends = filtered_friends[start_index:end_index]

        return {"friends_status": True, "friends": paginated_friends}

    def add_a_friend(self, user_email: str) -> Dict[str, bool]:
        """
        Add a user as a friend to the current user.

        Args:
            user_email (str): Email of the user to add as friend.

        Returns:
            Dict: A dictionary containing 'add_status' (bool).
        """
        if not self.current_user or user_email not in self.users:
            return {"add_status": False}
        
        if self.current_user not in self.friends:
            self.friends[self.current_user] = []
        
        if user_email in self.friends[self.current_user]:
            return {"add_status": False} # Already friends
        
        self.friends[self.current_user].append(user_email)
        return {"add_status": True}

    def remove_a_friend(self, user_email: str) -> Dict[str, bool]:
        """
        Remove a user from the current user's friends.

        Args:
            user_email (str): Email of the user to remove from friends.

        Returns:
            Dict: A dictionary containing 'remove_status' (bool).
        """
        if not self.current_user or user_email not in self.users:
            return {"remove_status": False}
        
        if self.current_user not in self.friends or user_email not in self.friends[self.current_user]:
            return {"remove_status": False} # Not friends with this user
        
        self.friends[self.current_user].remove(user_email)
        return {"remove_status": True}

    def add_money_to_my_venmo_balance(self, amount: float, payment_card_id: int) -> Dict[str, bool]:
        """
        Add money to the current user's Venmo balance from a payment card.

        Args:
            amount (float): Amount to add.
            payment_card_id (int): ID of the payment card to use.

        Returns:
            Dict: A dictionary containing 'add_status' (bool).
        """
        if not self.current_user or payment_card_id not in self.payment_cards:
            return {"add_status": False}
        
        self.users[self.current_user]["balance"] += amount
        return {"add_status": True}

    def show_my_venmo_balance(self) -> Dict[str, Union[bool, float]]:
        """
        Show the current user's Venmo balance.

        Returns:
            Dict: A dictionary containing 'balance_status' (bool) and 'balance' (float) if successful.
        """
        if not self.current_user or self.current_user not in self.users:
            return {"balance_status": False, "balance": 0.0}
        
        return {"balance_status": True, "balance": self.users[self.current_user]["balance"]}

    def withdraw_money_from_my_venmo_balance(self, amount: float, payment_card_id: int) -> Dict[str, bool]:
        """
        Withdraw money from the current user's Venmo balance to a payment card.

        Args:
            amount (float): Amount to withdraw.
            payment_card_id (int): ID of the payment card to use.

        Returns:
            Dict: A dictionary containing 'withdraw_status' (bool).
        """
        if not self.current_user or payment_card_id not in self.payment_cards:
            return {"withdraw_status": False}
        
        if self.users[self.current_user]["balance"] < amount:
            return {"withdraw_status": False} # Insufficient balance
        
        self.users[self.current_user]["balance"] -= amount
        return {"withdraw_status": True}

    def show_my_bank_transfer_history(self, transfer_type: str = "", page_index: int = 1, page_limit: int = 10) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Show history of bank transfers for the current user.

        Args:
            transfer_type (str): Optional type of transfer to filter by (e.g., 'add', 'withdraw').
            page_index (int): Page index for pagination (defaults to 1).
            page_limit (int): Number of results per page (defaults to 10).

        Returns:
            Dict: A dictionary containing 'history_status' (bool) and 'transfers' (List[Dict]) if successful.
        """
        if not self.current_user:
            return {"history_status": False, "transfers": []}
        
        # Dummy bank transfer history (since we don't have detailed transfer records)
        dummy_transfers = []
        if transfer_type == "add" or not transfer_type:
            dummy_transfers.append({"type": "add", "amount": 50.00, "date": "2023-06-01"})
        if transfer_type == "withdraw" or not transfer_type:
            dummy_transfers.append({"type": "withdraw", "amount": 20.00, "date": "2023-05-15"})

        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_transfers = dummy_transfers[start_index:end_index]
        
        return {"history_status": True, "transfers": paginated_transfers}

    def show_a_transaction(self, transaction_id: int) -> Dict[str, Union[bool, Dict]]:
        """
        Show details of a specific transaction.

        Args:
            transaction_id (int): ID of the transaction.

        Returns:
            Dict: A dictionary containing 'transaction_status' (bool) and 'transaction_details' (Dict) if successful.
        """
        if transaction_id not in self.transactions:
            return {"transaction_status": False, "transaction_details": {}}
        
        return {"transaction_status": True, "transaction_details": self.transactions[transaction_id]}

    def send_money(self, receiver_email: str, amount: float, description: str, payment_card_id: Optional[int] = None, private: bool = False) -> Dict[str, bool]:
        """
        Send money to another user.

        Args:
            receiver_email (str): Email of the receiver.
            amount (float): Amount to send.
            description (str): Description of the transaction.
            payment_card_id (int, optional): ID of the payment card to use. If not provided, uses Venmo balance.
            private (bool): Whether the transaction is private (defaults to False).

        Returns:
            Dict: A dictionary containing 'create_status' (bool).
        """
        if not self.current_user or receiver_email not in self.users:
            return {"create_status": False}

        if payment_card_id:
            if payment_card_id not in self.payment_cards:
                return {"create_status": False}
        else: # Using Venmo balance
            if self.users[self.current_user]["balance"] < amount:
                return {"create_status": False} # Insufficient balance

        transaction_id = self.transaction_counter
        self.transactions[transaction_id] = {
            "transaction_id": transaction_id,
            "sender": self.current_user,
            "receiver": receiver_email,
            "amount": amount,
            "description": description,
            "private": private,
            "timestamp": "2023-01-01",
            "likes": 0,
            "comments": []
        }
        self.transaction_counter += 1
        
        # Update balances
        if not payment_card_id: # Only deduct from balance if not using a card
            self.users[self.current_user]["balance"] -= amount
        self.users[receiver_email]["balance"] += amount
        
        return {"create_status": True}

    def update_my_transaction(self, transaction_id: int, description: Optional[str] = None, private: Optional[bool] = None) -> Dict[str, bool]:
        """
        Update a transaction's details, specifically for transactions sent by the current user.

        Args:
            transaction_id (int): ID of the transaction to update.
            description (str, optional): New description.
            private (bool, optional): New privacy setting.

        Returns:
            Dict: A dictionary containing 'update_status' (bool).
        """
        if transaction_id not in self.transactions or self.transactions[transaction_id]["sender"] != self.current_user:
            return {"update_status": False}
        
        if description is not None:
            self.transactions[transaction_id]["description"] = description
        if private is not None:
            self.transactions[transaction_id]["private"] = private
        return {"update_status": True}

    def show_my_transactions(self, query: str = "", user_email: str = "", min_created_at: str = "", max_created_at: str = "", min_like_count: int = 0, max_like_count: int = 1000, min_amount: float = 0.0, max_amount: float = float('inf'), private: Optional[bool] = None, direction: str = "", page_index: int = 1, page_limit: int = 10, sort_by: str = "timestamp") -> Dict[str, Union[bool, List[Dict]]]:
        """
        Show a list of transactions involving the current user based on filters.

        Args:
            query (str): Search query for description.
            user_email (str): Email of specific user to filter transactions with.
            min_created_at (str): Minimum creation date (YYYY-MM-DD).
            max_created_at (str): Maximum creation date (YYYY-MM-DD).
            min_like_count (int): Minimum like count.
            max_like_count (int): Maximum like count.
            min_amount (float): Minimum amount.
            max_amount (float): Maximum amount.
            private (bool, optional): Whether to include only private (True), public (False), or all (None) transactions.
            direction (str): Direction of transactions ('sent', 'received', or '').
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.
            sort_by (str): Field to sort by ('timestamp', 'amount', 'likes').

        Returns:
            Dict: A dictionary containing 'transactions_status' (bool) and 'transactions' (List[Dict]) if successful.
        """
        if not self.current_user:
            return {"transactions_status": False, "transactions": []}

        filtered_transactions = []
        for trans_id, transaction in self.transactions.items():
            # Filter by current user involvement
            if transaction["sender"] != self.current_user and transaction["receiver"] != self.current_user:
                continue

            # Filter by direction
            if direction == "sent" and transaction["sender"] != self.current_user:
                continue
            if direction == "received" and transaction["receiver"] != self.current_user:
                continue

            # Filter by specific user email
            if user_email and not (transaction["sender"] == user_email or transaction["receiver"] == user_email):
                continue

            # Filter by query in description
            if query and query.lower() not in transaction["description"].lower():
                continue

            # Filter by amount
            if not (min_amount <= transaction["amount"] <= max_amount):
                continue
            
            # Filter by private status
            if private is not None and transaction["private"] != private:
                continue

            # Dummy date and like count filtering (simplified for backend)
            # In a real backend, you'd parse dates and check ranges.
            if min_created_at and transaction["timestamp"] < min_created_at:
                continue
            if max_created_at and transaction["timestamp"] > max_created_at:
                continue
            if not (min_like_count <= transaction["likes"] <= max_like_count):
                continue


            filtered_transactions.append(transaction)

        # Sort transactions
        filtered_transactions.sort(key=lambda x: x.get(sort_by, 0), reverse=True if sort_by == "timestamp" else False) # Basic sorting

        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_transactions = filtered_transactions[start_index:end_index]

        return {"transactions_status": True, "transactions": paginated_transactions}

    def show_a_payment_card(self, card_id: int) -> Dict[str, Union[bool, Dict]]:
        """
        Show details of a specific payment card belonging to the current user.

        Args:
            card_id (int): ID of the payment card.

        Returns:
            Dict: A dictionary containing 'card_status' (bool) and 'card_details' (Dict) if successful.
        """
        if not self.current_user or card_id not in self.payment_cards:
            return {"card_status": False, "card_details": {}}
        
        return {"card_status": True, "card_details": self.payment_cards[card_id]}

    def show_my_payment_cards(self) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Show all payment cards for the current user.

        Returns:
            Dict: A dictionary containing 'cards_status' (bool) and 'payment_cards' (List[Dict]) if successful.
        """
        if not self.current_user:
            return {"cards_status": False, "payment_cards": []}
        
        return {"cards_status": True, "payment_cards": list(self.payment_cards.values())}

    def add_a_payment_card(self, card_name: str, owner_name: str, card_number: int, expiry_year: int, expiry_month: int, cvv_number: int) -> Dict[str, bool]:
        """
        Add a new payment card for the current user.

        Args:
            card_name (str): Name of the card (e.g., "Primary Debit").
            owner_name (str): Name of the card owner.
            card_number (int): Card number (last 4 digits for display).
            expiry_year (int): Expiry year.
            expiry_month (int): Expiry month.
            cvv_number (int): CVV number.

        Returns:
            Dict: A dictionary containing 'add_status' (bool).
        """
        if not self.current_user:
            return {"add_status": False}
        
        # Simple ID generation
        card_id = max(self.payment_cards.keys(), default=0) + 1
        self.payment_cards[card_id] = {
            "card_id": card_id,
            "user": self.current_user,
            "card_name": card_name,
            "owner_name": owner_name,
            "card_number": card_number, # In a real app, this would be tokenized/masked
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
            "cvv_number": cvv_number # Never store CVV in a real app
        }
        # Also update the user's payment cards in their user dictionary
        if self.current_user in self.users:
            self.users[self.current_user]["payment_cards"][card_id] = self.payment_cards[card_id]
        return {"add_status": True}

    def update_a_payment_card_name(self, card_id: int, new_card_name: str) -> Dict[str, bool]:
        """
        Update a payment card's name for the current user.

        Args:
            card_id (int): ID of the card to update.
            new_card_name (str): New name for the card.

        Returns:
            Dict: A dictionary containing 'update_status' (bool).
        """
        if not self.current_user or card_id not in self.payment_cards or self.payment_cards[card_id]["user"] != self.current_user:
            return {"update_status": False}
        
        self.payment_cards[card_id]["card_name"] = new_card_name
        # Also update the user's payment cards in their user dictionary
        if self.current_user in self.users:
            self.users[self.current_user]["payment_cards"][card_id]["card_name"] = new_card_name
        return {"update_status": True}

    def delete_a_payment_card(self, card_id: int) -> Dict[str, bool]:
        """
        Delete a payment card belonging to the current user.

        Args:
            card_id (int): ID of the card to delete.

        Returns:
            Dict: A dictionary containing 'delete_status' (bool).
        """
        if not self.current_user or card_id not in self.payment_cards or self.payment_cards[card_id]["user"] != self.current_user:
            return {"delete_status": False}
        
        del self.payment_cards[card_id]
        # Also remove from the user's payment cards in their user dictionary
        if self.current_user in self.users and card_id in self.users[self.current_user]["payment_cards"]:
            del self.users[self.current_user]["payment_cards"][card_id]
        return {"delete_status": True}

    def show_my_received_payment_requests(self, status: str = "", page_index: int = 1, page_limit: int = 10) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Show payment requests received by the current user.

        Args:
            status (str): Optional status to filter by ('pending', 'approved', 'denied').
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.

        Returns:
            Dict: A dictionary containing 'requests_status' (bool) and 'payment_requests' (List[Dict]) if successful.
        """
        if not self.current_user:
            return {"requests_status": False, "payment_requests": []}

        filtered_requests = []
        for req_id, request in self.payment_requests.items():
            if request["to_user"] == self.current_user:
                if not status or request["status"] == status:
                    filtered_requests.append(request)
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_requests = filtered_requests[start_index:end_index]
        
        return {"requests_status": True, "payment_requests": paginated_requests}

    def show_my_sent_payment_requests(self, status: str = "", page_index: int = 1, page_limit: int = 10) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Show payment requests sent by the current user.

        Args:
            status (str): Optional status to filter by ('pending', 'approved', 'denied').
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.

        Returns:
            Dict: A dictionary containing 'requests_status' (bool) and 'payment_requests' (List[Dict]) if successful.
        """
        if not self.current_user:
            return {"requests_status": False, "payment_requests": []}

        filtered_requests = []
        for req_id, request in self.payment_requests.items():
            if request["from_user"] == self.current_user:
                if not status or request["status"] == status:
                    filtered_requests.append(request)

        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_requests = filtered_requests[start_index:end_index]
        
        return {"requests_status": True, "payment_requests": paginated_requests}

    def request_money(self, user_email: str, amount: float, description: str, private: bool = False) -> Dict[str, bool]:
        """
        Create a new payment request from the current user to another user.

        Args:
            user_email (str): Email of the user to request from.
            amount (float): Amount to request.
            description (str): Description of the request.
            private (bool): Whether the request is private (defaults to False).

        Returns:
            Dict: A dictionary containing 'create_status' (bool).
        """
        if not self.current_user or user_email not in self.users:
            return {"create_status": False}
        
        request_id = self.request_counter
        self.payment_requests[request_id] = {
            "request_id": request_id,
            "from_user": self.current_user,
            "to_user": user_email,
            "amount": amount,
            "description": description,
            "private": private,
            "status": "pending",
            "timestamp": "2023-01-01"
        }
        self.request_counter += 1
        
        # Create a dummy notification for the recipient
        notification_id = self.notification_counter
        self.notifications[notification_id] = {
            "notification_id": notification_id,
            "user": user_email,
            "type": "payment_request",
            "content": f"{self.current_user} requested ${amount:.2f} from you for '{description}'.",
            "read": False,
            "timestamp": "2023-01-01"
        }
        self.notification_counter += 1
        
        return {"create_status": True}

    def approve_a_payment_request(self, request_id: int, payment_card_id: Optional[int] = None) -> Dict[str, bool]:
        """
        Approve a payment request received by the current user.

        Args:
            request_id (int): ID of the request to approve.
            payment_card_id (int, optional): ID of the payment card to use. If not provided, uses Venmo balance.

        Returns:
            Dict: A dictionary containing 'approve_status' (bool).
        """
        if (request_id not in self.payment_requests or 
            self.payment_requests[request_id]["to_user"] != self.current_user or # Must be a request *to* the current user
            self.payment_requests[request_id]["status"] != "pending"):
            return {"approve_status": False}
        
        request = self.payment_requests[request_id]
        from_user = request["from_user"] # Person who requested the money
        to_user = request["to_user"] # Current user
        amount = request["amount"]

        if payment_card_id:
            if payment_card_id not in self.payment_cards:
                return {"approve_status": False}
        else: # Using Venmo balance
            if self.users[to_user]["balance"] < amount:
                return {"approve_status": False} # Insufficient balance

        # Update balances
        if not payment_card_id: # Only deduct from balance if not using a card
            self.users[to_user]["balance"] -= amount
        self.users[from_user]["balance"] += amount
        
        # Update request status
        self.payment_requests[request_id]["status"] = "approved"
        
        # Create transaction
        transaction_id = self.transaction_counter
        self.transactions[transaction_id] = {
            "transaction_id": transaction_id,
            "sender": to_user, # Current user is sending the money
            "receiver": from_user, # Original requester is receiving
            "amount": amount,
            "description": f"Payment for: {request['description']}",
            "private": request["private"],
            "timestamp": "2023-01-01",
            "likes": 0,
            "comments": []
        }
        self.transaction_counter += 1

        # Create a dummy notification for the original requester
        notification_id = self.notification_counter
        self.notifications[notification_id] = {
            "notification_id": notification_id,
            "user": from_user,
            "type": "payment_approved",
            "content": f"{self.current_user} approved your request for ${amount:.2f}.",
            "read": False,
            "timestamp": "2023-01-01"
        }
        self.notification_counter += 1
        
        return {"approve_status": True}

    def deny_a_payment_request(self, request_id: int) -> Dict[str, bool]:
        """
        Deny a payment request received by the current user.

        Args:
            request_id (int): ID of the request to deny.

        Returns:
            Dict: A dictionary containing 'deny_status' (bool).
        """
        if (request_id not in self.payment_requests or
            self.payment_requests[request_id]["to_user"] != self.current_user or # Must be a request *to* the current user
            self.payment_requests[request_id]["status"] != "pending"):
            return {"deny_status": False}
        
        self.payment_requests[request_id]["status"] = "denied"

        # Create a dummy notification for the original requester
        request = self.payment_requests[request_id]
        notification_id = self.notification_counter
        self.notifications[notification_id] = {
            "notification_id": notification_id,
            "user": request["from_user"],
            "type": "payment_denied",
            "content": f"{self.current_user} denied your request for ${request['amount']:.2f}.",
            "read": False,
            "timestamp": "2023-01-01"
        }
        self.notification_counter += 1

        return {"deny_status": True}

    def remind_a_payment_request(self, request_id: int) -> Dict[str, bool]:
        """
        Send a reminder for a payment request sent by the current user.

        Args:
            request_id (int): ID of the request to remind.

        Returns:
            Dict: A dictionary containing 'remind_status' (bool).
        """
        if (request_id not in self.payment_requests or
            self.payment_requests[request_id]["from_user"] != self.current_user or # Must be a request *from* the current user
            self.payment_requests[request_id]["status"] != "pending"):
            return {"remind_status": False}
        
        request = self.payment_requests[request_id]
        
        # Create notification for the recipient
        notification_id = self.notification_counter
        self.notifications[notification_id] = {
            "notification_id": notification_id,
            "user": request["to_user"],
            "type": "payment_reminder",
            "content": f"Reminder: {request['from_user']} is still waiting for ${request['amount']:.2f} for '{request['description']}'.",
            "read": False,
            "timestamp": "2023-01-01"
        }
        self.notification_counter += 1
        
        return {"remind_status": True}

    def cancel_a_payment_request(self, request_id: int) -> Dict[str, bool]:
        """
        Cancel a payment request sent by the current user.

        Args:
            request_id (int): ID of the request to cancel.

        Returns:
            Dict: A dictionary containing 'cancel_status' (bool).
        """
        if (request_id not in self.payment_requests or
            self.payment_requests[request_id]["from_user"] != self.current_user or # Must be a request *from* the current user
            self.payment_requests[request_id]["status"] != "pending"):
            return {"cancel_status": False}
        
        request = self.payment_requests[request_id]
        
        del self.payment_requests[request_id]

        # Create a dummy notification for the recipient
        notification_id = self.notification_counter
        self.notifications[notification_id] = {
            "notification_id": notification_id,
            "user": request["to_user"],
            "type": "payment_request_canceled",
            "content": f"{self.current_user} canceled their request for ${request['amount']:.2f}.",
            "read": False,
            "timestamp": "2023-01-01"
        }
        self.notification_counter += 1

        return {"cancel_status": True}

    def show_my_notifications(self, page_index: int = 1, page_limit: int = 10, read: Optional[bool] = None) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Show the current user's notifications.

        Args:
            page_index (int): Page index for pagination (defaults to 1).
            page_limit (int): Number of results per page (defaults to 10).
            read (bool, optional): Whether to show only read (True), unread (False), or all (None) notifications.

        Returns:
            Dict: A dictionary containing 'notifications_status' (bool) and 'notifications' (List[Dict]) if successful.
        """
        if not self.current_user:
            return {"notifications_status": False, "notifications": []}

        filtered_notifications = []
        for notif_id, notification in self.notifications.items():
            if notification["user"] == self.current_user:
                if read is None or notification["read"] == read:
                    filtered_notifications.append(notification)
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_notifications = filtered_notifications[start_index:end_index]

        return {"notifications_status": True, "notifications": paginated_notifications}

    def show_my_unread_notifications_count(self) -> Dict[str, Union[bool, int]]:
        """
        Show count of the current user's unread notifications.

        Returns:
            Dict: A dictionary containing 'count_status' (bool) and 'unread_count' (int) if successful.
        """
        if not self.current_user:
            return {"count_status": False, "unread_count": 0}
        
        unread_count = sum(1 for notif in self.notifications.values() if notif["user"] == self.current_user and not notif["read"])
        return {"count_status": True, "unread_count": unread_count}

    def delete_all_my_notifications(self) -> Dict[str, bool]:
        """
        Delete all notifications for the current user.

        Returns:
            Dict: A dictionary containing 'delete_status' (bool).
        """
        if not self.current_user:
            return {"delete_status": False}
        
        to_delete_ids = [nid for nid, notif in self.notifications.items() if notif["user"] == self.current_user]
        for nid in to_delete_ids:
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
            return {"mark_status": False}
        
        for notif in self.notifications.values():
            if notif["user"] == self.current_user:
                notif["read"] = read_status
        
        return {"mark_status": True}
    