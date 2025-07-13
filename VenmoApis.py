from copy import deepcopy
from typing import Dict, List, Optional, Union

DEFAULT_STATE = {
    "users": {},
    "current_user": None,
    "transactions": {},
    "payment_cards": {},
    "payment_requests": {},
    "transaction_comments": {},
    "notifications": {},
    "friends": {},
    "verification_codes": {},
    "password_reset_codes": {},
    "transaction_counter": 0,
    "comment_counter": 0,
    "request_counter": 0,
    "notification_counter": 0,
}

class VenmoApis:
    def __init__(self):
        self.users: Dict[str, Dict]
        self.current_user: Optional[str]
        self.transactions: Dict[int, Dict]
        self.payment_cards: Dict[int, Dict]
        self.payment_requests: Dict[int, Dict]
        self.transaction_comments: Dict[int, Dict]
        self.notifications: Dict[int, Dict]
        self.friends: Dict[str, List[str]]
        self.verification_codes: Dict[str, str]
        self.password_reset_codes: Dict[str, str]
        self.transaction_counter: int
        self.comment_counter: int
        self.request_counter: int
        self.notification_counter: int
        self._api_description = "This tool belongs to the VenmoAPI, which provides core functionality for payments, friends, and account management on Venmo."

    def _load_scenario(self, scenario: dict) -> None:
        """Load a scenario into the VenmoAPI instance."""
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.transactions = scenario.get("transactions", DEFAULT_STATE_COPY["transactions"])
        self.payment_cards = scenario.get("payment_cards", DEFAULT_STATE_COPY["payment_cards"])
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

    def signup(self, first_name: str, last_name: str, email: str, password: str) -> Dict[str, bool]:
        """
        Sign up a new user with first name, last name, email, and password.

        Args:
            first_name (str): First name of the user.
            last_name (str): Last name of the user.
            email (str): Email address of the user.
            password (str): Password of the user.

        Returns:
            signup_status (bool): True if signup was successful, False otherwise.
        """
        if email in self.users:
            return {"signup_status": False}
        
        self.users[email] = {
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "verified": False,
            "balance": 0.0
        }
        return {"signup_status": True}

    def login(self, email: str, password: str) -> Dict[str, bool]:
        """
        Log in a user with email and password.

        Args:
            email (str): Email address of the user.
            password (str): Password of the user.

        Returns:
            login_status (bool): True if login was successful, False otherwise.
        """
        if email not in self.users or self.users[email]["password"] != password:
            return {"login_status": False}
        
        self.current_user = email
        return {"login_status": True}

    def logout(self) -> Dict[str, bool]:
        """
        Log out the current user.

        Returns:
            logout_status (bool): True if logout was successful, False otherwise.
        """
        if not self.current_user:
            return {"logout_status": False}
        
        self.current_user = None
        return {"logout_status": True}

    def send_verification_code(self, email: str) -> Dict[str, bool]:
        """
        Send a verification code to the user's email.

        Args:
            email (str): Email address of the user.

        Returns:
            send_status (bool): True if code was sent successfully, False otherwise.
        """
        if email not in self.users:
            return {"send_status": False}
        
        self.verification_codes[email] = "123456"  # Simplified for example
        return {"send_status": True}

    def verify_account(self, email: str, verification_code: str) -> Dict[str, bool]:
        """
        Verify a user's account with the provided verification code.

        Args:
            email (str): Email address of the user.
            verification_code (str): Verification code sent to the user.

        Returns:
            verification_status (bool): True if verification was successful, False otherwise.
        """
        if email not in self.users or self.verification_codes.get(email) != verification_code:
            return {"verification_status": False}
        
        self.users[email]["verified"] = True
        return {"verification_status": True}

    def send_password_reset_code(self, email: str) -> Dict[str, bool]:
        """
        Send a password reset code to the user's email.

        Args:
            email (str): Email address of the user.

        Returns:
            send_status (bool): True if code was sent successfully, False otherwise.
        """
        if email not in self.users:
            return {"send_status": False}
        
        self.password_reset_codes[email] = "654321"  # Simplified for example
        return {"send_status": True}

    def reset_password(self, email: str, password_reset_code: str, new_password: str) -> Dict[str, bool]:
        """
        Reset the user's password with the provided reset code.

        Args:
            email (str): Email address of the user.
            password_reset_code (str): Reset code sent to the user.
            new_password (str): New password to set.

        Returns:
            reset_status (bool): True if password was reset successfully, False otherwise.
        """
        if email not in self.users or self.password_reset_codes.get(email) != password_reset_code:
            return {"reset_status": False}
        
        self.users[email]["password"] = new_password
        return {"reset_status": True}

    def show_profile(self, email: str) -> Dict[str, bool]:
        """
        Show profile information for a user.

        Args:
            email (str): Email address of the user.

        Returns:
            profile_status (bool): True if profile was retrieved successfully, False otherwise.
        """
        if email not in self.users:
            return {"profile_status": False}
        
        return {"profile_status": True}

    def show_account(self) -> Dict[str, bool]:
        """
        Show account information for the current user.

        Returns:
            account_status (bool): True if account was retrieved successfully, False otherwise.
        """
        if not self.current_user:
            return {"account_status": False}
        
        return {"account_status": True}

    def update_account_name(self, first_name: str, last_name: str) -> Dict[str, bool]:
        """
        Update the current user's first and last name.

        Args:
            first_name (str): New first name.
            last_name (str): New last name.

        Returns:
            update_status (bool): True if name was updated successfully, False otherwise.
        """
        if not self.current_user:
            return {"update_status": False}
        
        self.users[self.current_user]["first_name"] = first_name
        self.users[self.current_user]["last_name"] = last_name
        return {"update_status": True}

    def delete_account(self) -> Dict[str, bool]:
        """
        Delete the current user's account.

        Returns:
            delete_status (bool): True if account was deleted successfully, False otherwise.
        """
        if not self.current_user:
            return {"delete_status": False}
        
        del self.users[self.current_user]
        self.current_user = None
        return {"delete_status": True}

    def search_users(self, query: str, page_index: int, page_limit: int) -> Dict[str, bool]:
        """
        Search for users based on a query.

        Args:
            query (str): Search query.
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.

        Returns:
            search_status (bool): True if search was successful, False otherwise.
        """
        return {"search_status": True}

    def search_friends(self, query: str, user_email: str, page_index: int, page_limit: int) -> Dict[str, bool]:
        """
        Search for friends based on a query.

        Args:
            query (str): Search query.
            user_email (str): Email of the user to search friends for.
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.

        Returns:
            search_status (bool): True if search was successful, False otherwise.
        """
        return {"search_status": True}

    def add_friend(self, user_email: str) -> Dict[str, bool]:
        """
        Add a user as a friend.

        Args:
            user_email (str): Email of the user to add as friend.

        Returns:
            add_status (bool): True if friend was added successfully, False otherwise.
        """
        if not self.current_user or user_email not in self.users:
            return {"add_status": False}
        
        if self.current_user not in self.friends:
            self.friends[self.current_user] = []
        
        if user_email in self.friends[self.current_user]:
            return {"add_status": False}
        
        self.friends[self.current_user].append(user_email)
        return {"add_status": True}

    def remove_friend(self, user_email: str) -> Dict[str, bool]:
        """
        Remove a user from friends.

        Args:
            user_email (str): Email of the user to remove from friends.

        Returns:
            remove_status (bool): True if friend was removed successfully, False otherwise.
        """
        if not self.current_user or user_email not in self.users:
            return {"remove_status": False}
        
        if self.current_user not in self.friends or user_email not in self.friends[self.current_user]:
            return {"remove_status": False}
        
        self.friends[self.current_user].remove(user_email)
        return {"remove_status": True}

    def add_to_venmo_balance(self, amount: float, payment_card_id: int) -> Dict[str, bool]:
        """
        Add money to Venmo balance from a payment card.

        Args:
            amount (float): Amount to add.
            payment_card_id (int): ID of the payment card to use.

        Returns:
            add_status (bool): True if money was added successfully, False otherwise.
        """
        if not self.current_user or payment_card_id not in self.payment_cards:
            return {"add_status": False}
        
        self.users[self.current_user]["balance"] += amount
        return {"add_status": True}

    def show_venmo_balance(self) -> Dict[str, bool]:
        """
        Show the current user's Venmo balance.

        Returns:
            balance_status (bool): True if balance was retrieved successfully, False otherwise.
        """
        if not self.current_user:
            return {"balance_status": False}
        
        return {"balance_status": True}

    def withdraw_from_venmo_balance(self, amount: float, payment_card_id: int) -> Dict[str, bool]:
        """
        Withdraw money from Venmo balance to a payment card.

        Args:
            amount (float): Amount to withdraw.
            payment_card_id (int): ID of the payment card to use.

        Returns:
            withdraw_status (bool): True if money was withdrawn successfully, False otherwise.
        """
        if not self.current_user or payment_card_id not in self.payment_cards:
            return {"withdraw_status": False}
        
        if self.users[self.current_user]["balance"] < amount:
            return {"withdraw_status": False}
        
        self.users[self.current_user]["balance"] -= amount
        return {"withdraw_status": True}

    def show_bank_transfer_history(self, transfer_type: str, page_index: int, page_limit: int) -> Dict[str, bool]:
        """
        Show history of bank transfers.

        Args:
            transfer_type (str): Type of transfer to filter by.
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.

        Returns:
            history_status (bool): True if history was retrieved successfully, False otherwise.
        """
        return {"history_status": True}

    def download_bank_transfer_receipt(self, bank_transfer_id: int, file_system_access_token: str, download_to_file_path: str, overwrite: bool) -> Dict[str, bool]:
        """
        Download a bank transfer receipt.

        Args:
            bank_transfer_id (int): ID of the bank transfer.
            file_system_access_token (str): Access token for file system.
            download_to_file_path (str): Path to download the receipt to.
            overwrite (bool): Whether to overwrite existing file.

        Returns:
            download_status (bool): True if receipt was downloaded successfully, False otherwise.
        """
        return {"download_status": True}

    def show_transaction(self, transaction_id: int) -> Dict[str, bool]:
        """
        Show details of a specific transaction.

        Args:
            transaction_id (int): ID of the transaction.

        Returns:
            transaction_status (bool): True if transaction was retrieved successfully, False otherwise.
        """
        if transaction_id not in self.transactions:
            return {"transaction_status": False}
        
        return {"transaction_status": True}

    def create_transaction(self, receiver_email: str, amount: float, description: str, payment_card_id: int, private: bool) -> Dict[str, bool]:
        """
        Create a new transaction.

        Args:
            receiver_email (str): Email of the receiver.
            amount (float): Amount to send.
            description (str): Description of the transaction.
            payment_card_id (int): ID of the payment card to use.
            private (bool): Whether the transaction is private.

        Returns:
            create_status (bool): True if transaction was created successfully, False otherwise.
        """
        if not self.current_user or receiver_email not in self.users or payment_card_id not in self.payment_cards:
            return {"create_status": False}
        
        transaction_id = self.transaction_counter
        self.transactions[transaction_id] = {
            "sender": self.current_user,
            "receiver": receiver_email,
            "amount": amount,
            "description": description,
            "private": private,
            "timestamp": "2023-01-01",  # Simplified for example
            "likes": 0,
            "comments": []
        }
        self.transaction_counter += 1
        
        # Update balances
        self.users[self.current_user]["balance"] -= amount
        self.users[receiver_email]["balance"] += amount
        
        return {"create_status": True}

    def update_transaction(self, transaction_id: int, description: str, private: bool) -> Dict[str, bool]:
        """
        Update a transaction's details.

        Args:
            transaction_id (int): ID of the transaction to update.
            description (str): New description.
            private (bool): New privacy setting.

        Returns:
            update_status (bool): True if transaction was updated successfully, False otherwise.
        """
        if transaction_id not in self.transactions:
            return {"update_status": False}
        
        self.transactions[transaction_id]["description"] = description
        self.transactions[transaction_id]["private"] = private
        return {"update_status": True}

    def show_transactions(self, query: str, user_email: str, min_created_at: str, max_created_at: str, min_like_count: int, max_like_count: int, min_amount: float, max_amount: float, private: bool, direction: str, page_index: int, page_limit: int, sort_by: str) -> Dict[str, bool]:
        """
        Show a list of transactions based on filters.

        Args:
            query (str): Search query.
            user_email (str): Email of user to filter transactions by.
            min_created_at (str): Minimum creation date.
            max_created_at (str): Maximum creation date.
            min_like_count (int): Minimum like count.
            max_like_count (int): Maximum like count.
            min_amount (float): Minimum amount.
            max_amount (float): Maximum amount.
            private (bool): Whether to include private transactions.
            direction (str): Direction of transactions ('sent' or 'received').
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.
            sort_by (str): Field to sort by.

        Returns:
            transactions_status (bool): True if transactions were retrieved successfully, False otherwise.
        """
        return {"transactions_status": True}

    def download_transaction_receipt(self, transaction_id: int, file_system_access_token: str, download_to_file_path: str, overwrite: bool) -> Dict[str, bool]:
        """
        Download a transaction receipt.

        Args:
            transaction_id (int): ID of the transaction.
            file_system_access_token (str): Access token for file system.
            download_to_file_path (str): Path to download the receipt to.
            overwrite (bool): Whether to overwrite existing file.

        Returns:
            download_status (bool): True if receipt was downloaded successfully, False otherwise.
        """
        if transaction_id not in self.transactions:
            return {"download_status": False}
        
        return {"download_status": True}

    def like_transaction(self, transaction_id: int) -> Dict[str, bool]:
        """
        Like a transaction.

        Args:
            transaction_id (int): ID of the transaction to like.

        Returns:
            like_status (bool): True if transaction was liked successfully, False otherwise.
        """
        if transaction_id not in self.transactions:
            return {"like_status": False}
        
        self.transactions[transaction_id]["likes"] += 1
        return {"like_status": True}

    def unlike_transaction(self, transaction_id: int) -> Dict[str, bool]:
        """
        Unlike a transaction.

        Args:
            transaction_id (int): ID of the transaction to unlike.

        Returns:
            unlike_status (bool): True if transaction was unliked successfully, False otherwise.
        """
        if transaction_id not in self.transactions or self.transactions[transaction_id]["likes"] <= 0:
            return {"unlike_status": False}
        
        self.transactions[transaction_id]["likes"] -= 1
        return {"unlike_status": True}

    def show_transaction_comments(self, transaction_id: int, page_index: int, page_limit: int) -> Dict[str, bool]:
        """
        Show comments for a transaction.

        Args:
            transaction_id (int): ID of the transaction.
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.

        Returns:
            comments_status (bool): True if comments were retrieved successfully, False otherwise.
        """
        if transaction_id not in self.transactions:
            return {"comments_status": False}
        
        return {"comments_status": True}

    def show_transaction_comment(self, comment_id: int) -> Dict[str, bool]:
        """
        Show details of a specific transaction comment.

        Args:
            comment_id (int): ID of the comment.

        Returns:
            comment_status (bool): True if comment was retrieved successfully, False otherwise.
        """
        if comment_id not in self.transaction_comments:
            return {"comment_status": False}
        
        return {"comment_status": True}

    def create_transaction_comment(self, transaction_id: int, comment: str) -> Dict[str, bool]:
        """
        Create a comment on a transaction.

        Args:
            transaction_id (int): ID of the transaction.
            comment (str): Comment text.

        Returns:
            create_status (bool): True if comment was created successfully, False otherwise.
        """
        if not self.current_user or transaction_id not in self.transactions:
            return {"create_status": False}
        
        comment_id = self.comment_counter
        self.transaction_comments[comment_id] = {
            "transaction_id": transaction_id,
            "user": self.current_user,
            "comment": comment,
            "likes": 0,
            "timestamp": "2023-01-01"  # Simplified for example
        }
        self.comment_counter += 1
        
        # Add comment reference to transaction
        self.transactions[transaction_id]["comments"].append(comment_id)
        
        return {"create_status": True}

    def update_transaction_comment(self, comment_id: int, comment: str) -> Dict[str, bool]:
        """
        Update a transaction comment.

        Args:
            comment_id (int): ID of the comment to update.
            comment (str): New comment text.

        Returns:
            update_status (bool): True if comment was updated successfully, False otherwise.
        """
        if comment_id not in self.transaction_comments:
            return {"update_status": False}
        
        self.transaction_comments[comment_id]["comment"] = comment
        return {"update_status": True}

    def delete_transaction_comment(self, comment_id: int) -> Dict[str, bool]:
        """
        Delete a transaction comment.

        Args:
            comment_id (int): ID of the comment to delete.

        Returns:
            delete_status (bool): True if comment was deleted successfully, False otherwise.
        """
        if comment_id not in self.transaction_comments:
            return {"delete_status": False}
        
        # Remove comment reference from transaction
        transaction_id = self.transaction_comments[comment_id]["transaction_id"]
        if comment_id in self.transactions[transaction_id]["comments"]:
            self.transactions[transaction_id]["comments"].remove(comment_id)
        
        del self.transaction_comments[comment_id]
        return {"delete_status": True}

    def like_transaction_comment(self, comment_id: int) -> Dict[str, bool]:
        """
        Like a transaction comment.

        Args:
            comment_id (int): ID of the comment to like.

        Returns:
            like_status (bool): True if comment was liked successfully, False otherwise.
        """
        if comment_id not in self.transaction_comments:
            return {"like_status": False}
        
        self.transaction_comments[comment_id]["likes"] += 1
        return {"like_status": True}

    def unlike_transaction_comment(self, comment_id: int) -> Dict[str, bool]:
        """
        Unlike a transaction comment.

        Args:
            comment_id (int): ID of the comment to unlike.

        Returns:
            unlike_status (bool): True if comment was unliked successfully, False otherwise.
        """
        if comment_id not in self.transaction_comments or self.transaction_comments[comment_id]["likes"] <= 0:
            return {"unlike_status": False}
        
        self.transaction_comments[comment_id]["likes"] -= 1
        return {"unlike_status": True}

    def show_payment_card(self, payment_card_id: int) -> Dict[str, bool]:
        """
        Show details of a payment card.

        Args:
            payment_card_id (int): ID of the payment card.

        Returns:
            card_status (bool): True if card was retrieved successfully, False otherwise.
        """
        if payment_card_id not in self.payment_cards:
            return {"card_status": False}
        
        return {"card_status": True}

    def show_payment_cards(self) -> Dict[str, bool]:
        """
        Show all payment cards for the current user.

        Returns:
            cards_status (bool): True if cards were retrieved successfully, False otherwise.
        """
        if not self.current_user:
            return {"cards_status": False}
        
        return {"cards_status": True}

    def add_payment_card(self, card_name: str, owner_name: str, card_number: int, expiry_year: int, expiry_month: int, cvv_number: int) -> Dict[str, bool]:
        """
        Add a new payment card.

        Args:
            card_name (str): Name of the card.
            owner_name (str): Name of the card owner.
            card_number (int): Card number.
            expiry_year (int): Expiry year.
            expiry_month (int): Expiry month.
            cvv_number (int): CVV number.

        Returns:
            add_status (bool): True if card was added successfully, False otherwise.
        """
        if not self.current_user:
            return {"add_status": False}
        
        card_id = len(self.payment_cards) + 1
        self.payment_cards[card_id] = {
            "user": self.current_user,
            "card_name": card_name,
            "owner_name": owner_name,
            "card_number": card_number,
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
            "cvv_number": cvv_number
        }
        return {"add_status": True}

    def update_payment_card(self, payment_card_id: int, card_name: str) -> Dict[str, bool]:
        """
        Update a payment card's name.

        Args:
            payment_card_id (int): ID of the card to update.
            card_name (str): New name for the card.

        Returns:
            update_status (bool): True if card was updated successfully, False otherwise.
        """
        if payment_card_id not in self.payment_cards:
            return {"update_status": False}
        
        self.payment_cards[payment_card_id]["card_name"] = card_name
        return {"update_status": True}

    def delete_payment_card(self, payment_card_id: int) -> Dict[str, bool]:
        """
        Delete a payment card.

        Args:
            payment_card_id (int): ID of the card to delete.

        Returns:
            delete_status (bool): True if card was deleted successfully, False otherwise.
        """
        if payment_card_id not in self.payment_cards:
            return {"delete_status": False}
        
        del self.payment_cards[payment_card_id]
        return {"delete_status": True}

    def show_received_payment_requests(self, status: str, page_index: int, page_limit: int) -> Dict[str, bool]:
        """
        Show received payment requests.

        Args:
            status (str): Status to filter by ('pending', 'approved', 'denied').
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.

        Returns:
            requests_status (bool): True if requests were retrieved successfully, False otherwise.
        """
        if not self.current_user:
            return {"requests_status": False}
        
        return {"requests_status": True}

    def show_sent_payment_requests(self, status: str, page_index: int, page_limit: int) -> Dict[str, bool]:
        """
        Show sent payment requests.

        Args:
            status (str): Status to filter by ('pending', 'approved', 'denied').
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.

        Returns:
            requests_status (bool): True if requests were retrieved successfully, False otherwise.
        """
        if not self.current_user:
            return {"requests_status": False}
        
        return {"requests_status": True}

    def create_payment_request(self, user_email: str, amount: float, description: str, private: bool) -> Dict[str, bool]:
        """
        Create a new payment request.

        Args:
            user_email (str): Email of the user to request from.
            amount (float): Amount to request.
            description (str): Description of the request.
            private (bool): Whether the request is private.

        Returns:
            create_status (bool): True if request was created successfully, False otherwise.
        """
        if not self.current_user or user_email not in self.users:
            return {"create_status": False}
        
        request_id = self.request_counter
        self.payment_requests[request_id] = {
            "from_user": self.current_user,
            "to_user": user_email,
            "amount": amount,
            "description": description,
            "private": private,
            "status": "pending",
            "timestamp": "2023-01-01"  # Simplified for example
        }
        self.request_counter += 1
        
        # Create notification
        notification_id = self.notification_counter
        self.notifications[notification_id] = {
            "user": user_email,
            "type": "payment_request",
            "content": f"{self.current_user} requested ${amount}",
            "read": False,
            "timestamp": "2023-01-01"  # Simplified for example
        }
        self.notification_counter += 1
        
        return {"create_status": True}

    def update_payment_request(self, payment_request_id: int, amount: float, description: str, private: bool) -> Dict[str, bool]:
        """
        Update a payment request.

        Args:
            payment_request_id (int): ID of the request to update.
            amount (float): New amount.
            description (str): New description.
            private (bool): New privacy setting.

        Returns:
            update_status (bool): True if request was updated successfully, False otherwise.
        """
        if payment_request_id not in self.payment_requests:
            return {"update_status": False}
        
        self.payment_requests[payment_request_id]["amount"] = amount
        self.payment_requests[payment_request_id]["description"] = description
        self.payment_requests[payment_request_id]["private"] = private
        return {"update_status": True}

    def approve_payment_request(self, payment_request_id: int, payment_card_id: int) -> Dict[str, bool]:
        """
        Approve a payment request.

        Args:
            payment_request_id (int): ID of the request to approve.
            payment_card_id (int): ID of the payment card to use.

        Returns:
            approve_status (bool): True if request was approved successfully, False otherwise.
        """
        if (payment_request_id not in self.payment_requests or 
            payment_card_id not in self.payment_cards or
            self.payment_requests[payment_request_id]["status"] != "pending"):
            return {"approve_status": False}
        
        request = self.payment_requests[payment_request_id]
        from_user = request["from_user"]
        to_user = request["to_user"]
        amount = request["amount"]
        
        # Check if requester has enough balance
        if self.users[to_user]["balance"] < amount:
            return {"approve_status": False}
        
        # Update balances
        self.users[to_user]["balance"] -= amount
        self.users[from_user]["balance"] += amount
        
        # Update request status
        self.payment_requests[payment_request_id]["status"] = "approved"
        
        # Create transaction
        transaction_id = self.transaction_counter
        self.transactions[transaction_id] = {
            "sender": to_user,
            "receiver": from_user,
            "amount": amount,
            "description": request["description"],
            "private": request["private"],
            "timestamp": "2023-01-01",  # Simplified for example
            "likes": 0,
            "comments": []
        }
        self.transaction_counter += 1
        
        return {"approve_status": True}

    def deny_payment_request(self, payment_request_id: int) -> Dict[str, bool]:
        """
        Deny a payment request.

        Args:
            payment_request_id (int): ID of the request to deny.

        Returns:
            deny_status (bool): True if request was denied successfully, False otherwise.
        """
        if payment_request_id not in self.payment_requests:
            return {"deny_status": False}
        
        self.payment_requests[payment_request_id]["status"] = "denied"
        return {"deny_status": True}

    def remind_payment_request(self, payment_request_id: int) -> Dict[str, bool]:
        """
        Send a reminder for a payment request.

        Args:
            payment_request_id (int): ID of the request to remind.

        Returns:
            remind_status (bool): True if reminder was sent successfully, False otherwise.
        """
        if payment_request_id not in self.payment_requests:
            return {"remind_status": False}
        
        request = self.payment_requests[payment_request_id]
        
        # Create notification
        notification_id = self.notification_counter
        self.notifications[notification_id] = {
            "user": request["to_user"],
            "type": "payment_reminder",
            "content": f"Reminder: {request['from_user']} requested ${request['amount']}",
            "read": False,
            "timestamp": "2023-01-01"  # Simplified for example
        }
        self.notification_counter += 1
        
        return {"remind_status": True}

    def delete_payment_request(self, payment_request_id: int) -> Dict[str, bool]:
        """
        Delete a payment request.

        Args:
            payment_request_id (int): ID of the request to delete.

        Returns:
            delete_status (bool): True if request was deleted successfully, False otherwise.
        """
        if payment_request_id not in self.payment_requests:
            return {"delete_status": False}
        
        del self.payment_requests[payment_request_id]
        return {"delete_status": True}

    def show_social_feed(self, page_index: int, page_limit: int) -> Dict[str, bool]:
        """
        Show the user's social feed.

        Args:
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.

        Returns:
            feed_status (bool): True if feed was retrieved successfully, False otherwise.
        """
        if not self.current_user:
            return {"feed_status": False}
        
        return {"feed_status": True}

    def show_notifications(self, page_index: int, page_limit: int, read: bool) -> Dict[str, bool]:
        """
        Show the user's notifications.

        Args:
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.
            read (bool): Whether to show read notifications.

        Returns:
            notifications_status (bool): True if notifications were retrieved successfully, False otherwise.
        """
        if not self.current_user:
            return {"notifications_status": False}
        
        return {"notifications_status": True}

    def show_notifications_count(self, read: bool) -> Dict[str, bool]:
        """
        Show count of the user's notifications.

        Args:
            read (bool): Whether to count read notifications.

        Returns:
            count_status (bool): True if count was retrieved successfully, False otherwise.
        """
        if not self.current_user:
            return {"count_status": False}
        
        return {"count_status": True}

    def delete_notification(self, notification_id: int) -> Dict[str, bool]:
        """
        Delete a notification.

        Args:
            notification_id (int): ID of the notification to delete.

        Returns:
            delete_status (bool): True if notification was deleted successfully, False otherwise.
        """
        if notification_id not in self.notifications:
            return {"delete_status": False}
        
        del self.notifications[notification_id]
        return {"delete_status": True}

    def mark_notification(self, notification_id: int, read: bool) -> Dict[str, bool]:
        """
        Mark a notification as read or unread.

        Args:
            notification_id (int): ID of the notification.
            read (bool): Whether to mark as read (True) or unread (False).

        Returns:
            mark_status (bool): True if notification was marked successfully, False otherwise.
        """
        if notification_id not in self.notifications:
            return {"mark_status": False}
        
        self.notifications[notification_id]["read"] = read
        return {"mark_status": True}

    def delete_notifications(self) -> Dict[str, bool]:
        """
        Delete all notifications.

        Returns:
            delete_status (bool): True if notifications were deleted successfully, False otherwise.
        """
        if not self.current_user:
            return {"delete_status": False}
        
        # Delete only current user's notifications
        to_delete = [nid for nid, notif in self.notifications.items() if notif["user"] == self.current_user]
        for nid in to_delete:
            del self.notifications[nid]
        
        return {"delete_status": True}

    def mark_notifications(self, read: bool) -> Dict[str, bool]:
        """
        Mark all notifications as read or unread.

        Args:
            read (bool): Whether to mark as read (True) or unread (False).

        Returns:
            mark_status (bool): True if notifications were marked successfully, False otherwise.
        """
        if not self.current_user:
            return {"mark_status": False}
        
        # Mark only current user's notifications
        for notif in self.notifications.values():
            if notif["user"] == self.current_user:
                notif["read"] = read
        
        return {"mark_status": True}