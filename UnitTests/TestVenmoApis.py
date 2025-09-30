from audio_gorilla.VenmoApis import VenmoApis, DEFAULT_STATE, User
import unittest
from copy import deepcopy

class TestVenmoApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh VenmoApis instance for each test."""
        self.venmo_api = VenmoApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.venmo_api._load_scenario(deepcopy(DEFAULT_STATE))
        # Create test users
        self.user1 = User(email="user1@example.com")
        self.user2 = User(email="user2@example.com")
        self.test_email = "user1@example.com"

    # --- Unit Tests for Core Functions (most important for audio calling) ---

    def test_show_my_account_info_success(self):
        """Test showing account info for the current user."""
        result = self.venmo_api.show_my_account_info()
        self.assertTrue(result["account_status"])
        self.assertEqual(result["account_info"]["email"], self.user1_email)
        self.assertEqual(result["account_info"]["first_name"], "Alice")

    def test_show_my_account_info_no_current_user(self):
        """Test showing account info when no user is logged in."""
        self.venmo_api.current_user = None
        result = self.venmo_api.show_my_account_info()
        self.assertFalse(result["account_status"])
        self.assertEqual(result["account_info"], {})

    def test_send_money_success_venmo_balance(self):
        """Test sending money using Venmo balance."""
        initial_balance_sender = self.venmo_api.users[self.user1_email]["balance"]
        initial_balance_receiver = self.venmo_api.users[self.user2_email]["balance"]
        
        result = self.venmo_api.send_money(self.user2_email, 25.00, "For dinner", private=True)
        self.assertTrue(result["create_status"])
        
        self.assertEqual(self.venmo_api.users[self.user1_email]["balance"], initial_balance_sender - 25.00)
        self.assertEqual(self.venmo_api.users[self.user2_email]["balance"], initial_balance_receiver + 25.00)
        self.assertEqual(len(self.venmo_api.transactions), 1)
        self.assertEqual(self.venmo_api.transactions[0]["sender"], self.user1_email)
        self.assertEqual(self.venmo_api.transactions[0]["receiver"], self.user2_email)
        self.assertEqual(self.venmo_api.transactions[0]["amount"], 25.00)
        self.assertTrue(self.venmo_api.transactions[0]["private"])

    def test_send_money_insufficient_balance(self):
        """Test sending money with insufficient Venmo balance."""
        result = self.venmo_api.send_money(self.user2_email, 200.00, "Too much")
        self.assertFalse(result["create_status"])
        self.assertEqual(self.venmo_api.users[self.user1_email]["balance"], 100.00) # Balance should be unchanged

    def test_request_money_success(self):
        """Test creating a payment request successfully."""
        result = self.venmo_api.request_money(self.user2_email, 30.00, "For rent")
        self.assertTrue(result["create_status"])
        self.assertEqual(len(self.venmo_api.payment_requests), 1)
        self.assertEqual(self.venmo_api.payment_requests[0]["from_user"], self.user1_email)
        self.assertEqual(self.venmo_api.payment_requests[0]["to_user"], self.user2_email)
        self.assertEqual(self.venmo_api.payment_requests[0]["amount"], 30.00)
        self.assertEqual(self.venmo_api.payment_requests[0]["status"], "pending")
        self.assertEqual(len(self.venmo_api.notifications), 1) # Should create a notification for user2

    def test_approve_a_payment_request_success_balance(self):
        """Test approving a payment request using Venmo balance."""
        self.venmo_api.request_money(self.user2_email, 20.00, "Lunch") # user1 requests from user2
        self.venmo_api.current_user = self.user2_email # Switch to user2 to approve
        
        initial_balance_user2 = self.venmo_api.users[self.user2_email]["balance"]
        initial_balance_user1 = self.venmo_api.users[self.user1_email]["balance"]

        result = self.venmo_api.approve_a_payment_request(0) # Request ID is 0
        self.assertTrue(result["approve_status"])

        self.assertEqual(self.venmo_api.payment_requests[0]["status"], "approved")
        self.assertEqual(self.venmo_api.users[self.user2_email]["balance"], initial_balance_user2 - 20.00)
        self.assertEqual(self.venmo_api.users[self.user1_email]["balance"], initial_balance_user1 + 20.00)
        self.assertEqual(self.venmo_api.transaction_counter, 1) # A transaction should be created
        self.assertEqual(len(self.venmo_api.notifications), 2) # Original request notification + approval notification

    def test_deny_a_payment_request_success(self):
        """Test denying a payment request."""
        self.venmo_api.request_money(self.user2_email, 15.00, "Movie tickets") # user1 requests from user2
        self.venmo_api.current_user = self.user2_email # Switch to user2 to deny

        result = self.venmo_api.deny_a_payment_request(0)
        self.assertTrue(result["deny_status"])
        self.assertEqual(self.venmo_api.payment_requests[0]["status"], "denied")
        self.assertEqual(len(self.venmo_api.notifications), 2) # Original request notification + denial notification

    def test_show_my_transactions_all(self):
        """Test showing all transactions for the current user."""
        # Add some dummy transactions
        self.venmo_api.send_money(self.user2_email, 10.00, "Coffee")
        self.venmo_api.current_user = self.user2_email
        self.venmo_api.send_money(self.user1_email, 5.00, "Snacks")
        self.venmo_api.current_user = self.user1_email # Switch back to original user

        result = self.venmo_api.show_my_transactions()
        self.assertTrue(result["transactions_status"])
        self.assertEqual(len(result["transactions"]), 2) # Should see 2 transactions (sent and received)

    def test_show_my_friends_success(self):
        """Test showing current user's friends."""
        result = self.venmo_api.show_my_friends()
        self.assertTrue(result["friends_status"])
        self.assertEqual(len(result["friends"]), 1)
        self.assertEqual(result["friends"][0]["email"], self.user2_email)
        self.assertEqual(result["friends"][0]["first_name"], "Bob")

    def test_add_a_friend_success(self):
        """Test adding a new friend."""
        # Create a third dummy user to add as a friend
        self.venmo_api.users["user3@example.com"] = {
            "first_name": "Charlie", "last_name": "Brown", "email": "user3@example.com", "balance": 0.0, "friends": [], "payment_cards": {}
        }
        initial_friends_count = len(self.venmo_api.friends.get(self.user1_email, []))
        result = self.venmo_api.add_a_friend("user3@example.com")
        self.assertTrue(result["add_status"])
        self.assertEqual(len(self.venmo_api.friends[self.user1_email]), initial_friends_count + 1)
        self.assertIn("user3@example.com", self.venmo_api.friends[self.user1_email])

    def test_show_my_unread_notifications_count(self):
        """Test showing the count of unread notifications."""
        # Initially, there should be no unread notifications from default state
        result = self.venmo_api.show_my_unread_notifications_count()
        self.assertTrue(result["count_status"])
        self.assertEqual(result["unread_count"], 0)

        # Create a payment request to generate a notification for user2
        self.venmo_api.request_money(self.user2_email, 10.00, "Test notification")
        
        # Switch to user2 and check unread count
        self.venmo_api.current_user = self.user2_email
        result_user2 = self.venmo_api.show_my_unread_notifications_count()
        self.assertTrue(result_user2["count_status"])
        self.assertEqual(result_user2["unread_count"], 1)

    # --- Combined Functionality Tests ---

    def test_send_and_check_transaction_details(self):
        """
        Scenario: Send money, then check transaction details.
        Functions: send_money, show_a_transaction
        """
        send_result = self.venmo_api.send_money(self.user2_email, 30.00, "Birthday gift", private=False)
        self.assertTrue(send_result["create_status"])
        
        transaction_id = 0 # Assuming it's the first transaction
        transaction_details_result = self.venmo_api.show_a_transaction(transaction_id)
        
        self.assertTrue(transaction_details_result["transaction_status"])
        self.assertEqual(transaction_details_result["transaction_details"]["amount"], 30.00)
        self.assertEqual(transaction_details_result["transaction_details"]["description"], "Birthday gift")
        self.assertEqual(transaction_details_result["transaction_details"]["private"], False)

    def test_add_card_and_add_money(self):
        """
        Scenario: Add a new payment card, then add money to Venmo balance using that card.
        Functions: add_a_payment_card, add_money_to_my_venmo_balance, show_my_venmo_balance
        """
        add_card_result = self.venmo_api.add_a_payment_card("New Bank Card", "Alice Smith", 5678, 2029, 6, 456)
        self.assertTrue(add_card_result["add_status"])

        # Find the ID of the newly added card (assuming it increments from 1 in DEFAULT_STATE)
        new_card_id = 2 # Default card is 1, so new one should be 2
        self.assertIn(new_card_id, self.venmo_api.payment_cards)

        initial_balance = self.venmo_api.users[self.user1_email]["balance"]
        
        add_money_result = self.venmo_api.add_money_to_my_venmo_balance(50.00, new_card_id)
        self.assertTrue(add_money_result["add_status"])
        
        updated_balance_result = self.venmo_api.show_my_venmo_balance()
        self.assertTrue(updated_balance_result["balance_status"])
        self.assertEqual(updated_balance_result["balance"], initial_balance + 50.00)

    def test_request_deny_and_check_notifications(self):
        """
        Scenario: Request money, deny the request, then check notifications for both users.
        Functions: request_money, deny_a_payment_request, show_my_notifications
        """
        # User1 requests money from User2
        request_result = self.venmo_api.request_money(self.user2_email, 40.00, "Dinner")
        self.assertTrue(request_result["create_status"])
        request_id = 0

        # Check User2's notifications (should have a pending request)
        self.venmo_api.current_user = self.user2_email
        user2_notifications_before_deny = self.venmo_api.show_my_notifications()
        self.assertTrue(user2_notifications_before_deny["notifications_status"])
        self.assertEqual(len(user2_notifications_before_deny["notifications"]), 1)
        self.assertEqual(user2_notifications_before_deny["notifications"][0]["type"], "payment_request")
        
        # User2 denies the request
        deny_result = self.venmo_api.deny_a_payment_request(request_id)
        self.assertTrue(deny_result["deny_status"])
        self.assertEqual(self.venmo_api.payment_requests[request_id]["status"], "denied")

        # Check User1's notifications (should have a denial notification)
        self.venmo_api.current_user = self.user1_email
        user1_notifications_after_deny = self.venmo_api.show_my_notifications()
        self.assertTrue(user1_notifications_after_deny["notifications_status"])
        self.assertEqual(len(user1_notifications_after_deny["notifications"]), 1) # Only one notification for user1 (the denial)
        self.assertEqual(user1_notifications_after_deny["notifications"][0]["type"], "payment_denied")

        # Check User2's notifications again (should now have the denial and original request)
        self.venmo_api.current_user = self.user2_email
        user2_notifications_after_deny = self.venmo_api.show_my_notifications()
        self.assertTrue(user2_notifications_after_deny["notifications_status"])
        self.assertEqual(len(user2_notifications_after_deny["notifications"]), 1) 

    # --- Comprehensive Test Coverage for All VenmoApis Methods ---

    def test_set_current_user_success(self):
        """Test setting current user with valid email."""
        result = self.venmo_api.set_current_user("user2@example.com")
        self.assertTrue(result["success"])
        self.assertEqual(self.venmo_api.current_user, "user2@example.com")

    def test_set_current_user_invalid_email(self):
        """Test setting current user with invalid email."""
        result = self.venmo_api.set_current_user("nonexistent@example.com")
        self.assertFalse(result["success"])

    def test_show_account_success(self):
        """Test showing account details for valid user."""
        result = self.venmo_api.show_account(self.user1)
        self.assertTrue(result["success"])
        self.assertIn("account_details", result)
        self.assertIn("email", result["account_details"])

    def test_show_account_invalid_user(self):
        """Test showing account for user not in system."""
        invalid_user = User(email="invalid@example.com")
        result = self.venmo_api.show_account(invalid_user)
        self.assertFalse(result["success"])

    def test_list_friends_success(self):
        """Test listing friends for valid user."""
        result = self.venmo_api.list_friends(self.user1)
        self.assertTrue(result["success"])
        self.assertIn("friends", result)
        self.assertIsInstance(result["friends"], list)

    def test_list_friends_no_friends(self):
        """Test listing friends when user has no friends."""
        # Create isolated user
        isolated_user = User(email="isolated@example.com")
        result = self.venmo_api.list_friends(isolated_user)
        # Should still be successful but with empty friends list
        self.assertTrue(result["success"])
        self.assertEqual(len(result.get("friends", [])), 0)

    def test_send_money_success_with_valid_users(self):
        """Test sending money between valid users."""
        result = self.venmo_api.send_money(
            self.user1, 
            "user2@example.com", 
            25.0, 
            "Test payment"
        )
        self.assertTrue(result["success"])
        self.assertIn("transaction_id", result)

    def test_send_money_insufficient_funds(self):
        """Test sending money with insufficient balance."""
        result = self.venmo_api.send_money(
            self.user1, 
            "user2@example.com", 
            9999.99, 
            "Too much money"
        )
        self.assertFalse(result["success"])

    def test_send_money_invalid_receiver(self):
        """Test sending money to non-existent user."""
        result = self.venmo_api.send_money(
            self.user1, 
            "nonexistent@example.com", 
            10.0, 
            "Invalid receiver"
        )
        self.assertFalse(result["success"])

    def test_request_money_success(self):
        """Test requesting money from valid user."""
        result = self.venmo_api.request_money(
            self.user1, 
            "user2@example.com", 
            30.0, 
            "Rent money"
        )
        self.assertTrue(result["success"])
        self.assertIn("request_id", result)

    def test_request_money_invalid_receiver(self):
        """Test requesting money from invalid user."""
        result = self.venmo_api.request_money(
            self.user1, 
            "invalid@example.com", 
            30.0, 
            "Invalid request"
        )
        self.assertFalse(result["success"])

    def test_request_money_zero_amount(self):
        """Test requesting zero amount."""
        result = self.venmo_api.request_money(
            self.user1, 
            "user2@example.com", 
            0.0, 
            "Zero request"
        )
        self.assertFalse(result["success"])

    def test_get_transaction_details_valid_id(self):
        """Test getting transaction details with valid ID."""
        # First create a transaction
        send_result = self.venmo_api.send_money(
            self.user1, 
            "user2@example.com", 
            15.0, 
            "Test transaction"
        )
        self.assertTrue(send_result["success"])
        
        transaction_id = send_result["transaction_id"]
        result = self.venmo_api.get_transaction_details(transaction_id)
        self.assertTrue(result["success"])
        self.assertIn("transaction", result)

    def test_get_transaction_details_invalid_id(self):
        """Test getting transaction details with invalid ID."""
        result = self.venmo_api.get_transaction_details("invalid_id")
        self.assertFalse(result["success"])

    def test_list_user_transactions_success(self):
        """Test listing transactions for user."""
        # Create some transactions first
        self.venmo_api.send_money(self.user1, "user2@example.com", 10.0, "Payment 1")
        self.venmo_api.send_money(self.user1, "user2@example.com", 20.0, "Payment 2")
        
        result = self.venmo_api.list_user_transactions(self.user1)
        self.assertTrue(result["success"])
        self.assertIn("transactions", result)
        self.assertGreaterEqual(len(result["transactions"]), 2)

    def test_list_user_transactions_no_transactions(self):
        """Test listing transactions for user with no transactions."""
        # Create a new user with no transaction history
        new_user = User(email="newtestuser@example.com")
        result = self.venmo_api.list_user_transactions(new_user)
        # Should succeed but with empty list
        self.assertTrue(result["success"])
        self.assertEqual(len(result.get("transactions", [])), 0)

    def test_add_payment_card_success(self):
        """Test adding a payment card successfully."""
        result = self.venmo_api.add_payment_card(
            self.user1,
            "Test Bank Card",
            "John Doe",
            "1234567890123456",
            2025,
            12,
            "123"
        )
        self.assertTrue(result["success"])
        self.assertIn("card_id", result)

    def test_add_payment_card_invalid_data(self):
        """Test adding payment card with invalid data."""
        result = self.venmo_api.add_payment_card(
            self.user1,
            "",  # Empty name
            "John Doe",
            "invalid_card_number",
            2020,  # Past year
            13,    # Invalid month
            "12"   # Invalid CVV
        )
        self.assertFalse(result["success"])

    def test_list_payment_methods_success(self):
        """Test listing payment methods for user."""
        result = self.venmo_api.list_payment_methods(self.user1)
        self.assertTrue(result["success"])
        self.assertIn("payment_methods", result)
        self.assertIsInstance(result["payment_methods"], list)

    def test_list_payment_methods_invalid_user(self):
        """Test listing payment methods for invalid user."""
        invalid_user = User(email="invalid@example.com")
        result = self.venmo_api.list_payment_methods(invalid_user)
        self.assertFalse(result["success"])

    def test_set_default_payment_method_success(self):
        """Test setting default payment method."""
        # First add a payment card
        add_result = self.venmo_api.add_payment_card(
            self.user1,
            "Test Card",
            "John Doe", 
            "1234567890123456",
            2025,
            12,
            "123"
        )
        self.assertTrue(add_result["success"])
        
        card_id = add_result["card_id"]
        result = self.venmo_api.set_default_payment_method(self.user1, card_id)
        self.assertTrue(result["success"])

    def test_set_default_payment_method_invalid_card(self):
        """Test setting default payment method with invalid card ID."""
        result = self.venmo_api.set_default_payment_method(self.user1, "invalid_card_id")
        self.assertFalse(result["success"])

    def test_delete_payment_method_success(self):
        """Test deleting a payment method."""
        # First add a payment card
        add_result = self.venmo_api.add_payment_card(
            self.user1,
            "Card to Delete",
            "John Doe",
            "1234567890123456", 
            2025,
            12,
            "123"
        )
        self.assertTrue(add_result["success"])
        
        card_id = add_result["card_id"]
        result = self.venmo_api.delete_payment_method(self.user1, card_id)
        self.assertTrue(result["success"])

    def test_delete_payment_method_invalid_card(self):
        """Test deleting non-existent payment method."""
        result = self.venmo_api.delete_payment_method(self.user1, "invalid_card_id")
        self.assertFalse(result["success"])

    def test_get_unread_notification_count_success(self):
        """Test getting unread notification count."""
        result = self.venmo_api.get_unread_notification_count()
        self.assertTrue(result["success"])
        self.assertIn("count", result)
        self.assertIsInstance(result["count"], int)

    def test_payment_workflow_end_to_end(self):
        """Test complete payment workflow: add card, send money, check transaction."""
        # Step 1: Add payment card
        card_result = self.venmo_api.add_payment_card(
            self.user1,
            "Workflow Test Card",
            "Test User",
            "1234567890123456",
            2026,
            6,
            "456"
        )
        self.assertTrue(card_result["success"])
        
        # Step 2: Send money
        send_result = self.venmo_api.send_money(
            self.user1,
            "user2@example.com",
            50.0,
            "End-to-end test payment"
        )
        self.assertTrue(send_result["success"])
        
        # Step 3: Check transaction details
        transaction_id = send_result["transaction_id"]
        details_result = self.venmo_api.get_transaction_details(transaction_id)
        self.assertTrue(details_result["success"])
        
        # Step 4: Verify transaction in user's transaction list
        transactions_result = self.venmo_api.list_user_transactions(self.user1)
        self.assertTrue(transactions_result["success"])
        self.assertGreater(len(transactions_result["transactions"]), 0)

    def test_request_workflow_end_to_end(self):
        """Test complete request workflow: request money, check notifications."""
        # Step 1: Request money
        request_result = self.venmo_api.request_money(
            self.user1,
            "user2@example.com", 
            75.0,
            "End-to-end test request"
        )
        self.assertTrue(request_result["success"])
        
        # Step 2: Check unread notifications
        notifications_result = self.venmo_api.get_unread_notification_count()
        self.assertTrue(notifications_result["success"])
        
        # Step 3: List user transactions to verify request
        transactions_result = self.venmo_api.list_user_transactions(self.user1)
        self.assertTrue(transactions_result["success"])

    def test_account_management_workflow(self):
        """Test account management: show account, list friends, manage payment methods."""
        # Step 1: Show account details
        account_result = self.venmo_api.show_account(self.user1)
        self.assertTrue(account_result["success"])
        
        # Step 2: List friends
        friends_result = self.venmo_api.list_friends(self.user1)
        self.assertTrue(friends_result["success"])
        
        # Step 3: List payment methods
        payment_methods_result = self.venmo_api.list_payment_methods(self.user1)
        self.assertTrue(payment_methods_result["success"])
        
        # Step 4: Add new payment method
        add_card_result = self.venmo_api.add_payment_card(
            self.user1,
            "Account Management Card",
            "Test User",
            "9876543210123456",
            2027,
            3,
            "789"
        )
        self.assertTrue(add_card_result["success"])

    def test_error_handling_edge_cases(self):
        """Test various error handling scenarios."""
        # Test with None user
        with self.assertRaises((AttributeError, TypeError)):
            self.venmo_api.show_account(None)
        
        # Test with negative amount
        result = self.venmo_api.send_money(
            self.user1,
            "user2@example.com",
            -10.0,
            "Negative amount"
        )
        self.assertFalse(result["success"])
        
        # Test with empty note
        result = self.venmo_api.request_money(
            self.user1,
            "user2@example.com",
            10.0,
            ""  # Empty note
        )
        # This might be valid depending on implementation
        self.assertIn("success", result) 

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
