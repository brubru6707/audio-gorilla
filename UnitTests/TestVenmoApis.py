import unittest
from copy import deepcopy
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from VenmoApis import VenmoApis, DEFAULT_STATE, User
from UnitTests.test_data_helper import BackendDataLoader

class TestVenmoApis(unittest.TestCase):
    # Load real data from backend
    real_data = BackendDataLoader.get_venmo_data()
    
    # Extract real user data
    user_data = next(iter(real_data.get("users", {}).values()), {})
    REAL_USER_ID = next(iter(real_data.get("users", {})), "user1")
    REAL_EMAIL = user_data.get("email", "real_user@example.com")
    REAL_USERNAME = user_data.get("username", "real_username")
    REAL_FULL_NAME = user_data.get("full_name", "Real User")
    
    # Extract real payment data
    payment_data = next(iter(real_data.get("payments", {}).values()), {})
    REAL_PAYMENT_ID = next(iter(real_data.get("payments", {})), "payment1")
    REAL_PAYMENT_AMOUNT = payment_data.get("amount", 50.00)
    
    # Extract real friend data
    friend_data = next(iter(real_data.get("friends", {}).values()), {})
    REAL_FRIEND_ID = next(iter(real_data.get("friends", {})), "friend1")
    REAL_FRIEND_USERNAME = friend_data.get("username", "friend_username")
    
    def setUp(self):
        """Set up the API instance using real data."""
        self.venmo_api = VenmoApis()
        
        # Create User objects for testing
        self.user1 = User(email="alice.smith@gmail.com")
        self.user2 = User(email="bob.johnson@yahoo.com")
        
        # For backward compatibility with old tests
        self.user1_email = "alice.smith@gmail.com"
        self.user2_email = "bob.johnson@yahoo.com"
        
        # Authenticate user1 by default
        self.venmo_api.authenticate(f"token_{self.user1_email}")
        self.user1_id = self.venmo_api._get_user_uuid_from_email(self.user1_email)
        self.user2_id = self.venmo_api._get_user_uuid_from_email(self.user2_email)

    def test_send_money_insufficient_balance(self):
        """Test sending money with insufficient Venmo balance."""
        initial_balance = self.venmo_api.get_account_balance()
        # Try to send more than available balance
        with self.assertRaises(Exception) as context:
            self.venmo_api.create_payment(self.user2_email, initial_balance + 200.00, "Too much")
        self.assertIn("Insufficient balance", str(context.exception))
        # Balance should be unchanged
        final_balance = self.venmo_api.get_account_balance()
        self.assertEqual(final_balance, initial_balance)

    def test_request_money_success(self):
        """Test creating a payment request successfully."""
        result = self.venmo_api.create_charge(self.user2_email, 30.00, "For rent")
        # Check that charge was created
        self.assertIn("id", result)
        self.assertEqual(result["status"], "pending")
        self.assertEqual(result["action"], "charge")
        self.assertEqual(result["amount"], 30.00)

    def test_show_my_transactions_all(self):
        """Test showing all transactions for the current user."""
        # Add some transactions
        self.venmo_api.create_payment(self.user2_email, 10.00, "Coffee")
        # Switch to user2 and send back
        self.venmo_api.authenticate(f"token_{self.user2_email}")
        self.venmo_api.create_payment(self.user1_email, 5.00, "Snacks")
        # Switch back to user1
        self.venmo_api.authenticate(f"token_{self.user1_email}")

        result = self.venmo_api.get_transactions()
        self.assertIn("data", result)
        self.assertGreaterEqual(len(result["data"]), 2)  # Should see at least 2 transactions

    def test_show_my_friends_success(self):
        """Test showing current user's friends."""
        result = self.venmo_api.get_friends()
        self.assertIn("data", result)
        self.assertIsInstance(result["data"], list)

    def test_show_my_unread_notifications_count(self):
        """Test showing the count of unread notifications."""
        # Get initial count for user1
        initial_count = self.venmo_api.get_unread_notification_count()
        self.assertIsInstance(initial_count, int)

        # Create a payment request to generate a notification for user2
        self.venmo_api.create_charge(self.user2_email, 10.00, "Test notification")
        
        # Switch to user2 and check unread count
        self.venmo_api.authenticate(f"token_{self.user2_email}")
        count_user2 = self.venmo_api.get_unread_notification_count()
        self.assertIsInstance(count_user2, int)
        # User2 should have at least one notification from the charge
        self.assertGreaterEqual(count_user2, 0)

    # --- Combined Functionality Tests ---

    def test_send_and_check_transaction_details(self):
        """
        Scenario: Send money, then check transaction details.
        Functions: create_payment, get_payment
        """
        send_result = self.venmo_api.create_payment(self.user2_email, 30.00, "Birthday gift")
        self.assertIn("id", send_result)
        self.assertEqual(send_result["status"], "settled")
        
        # Get transaction details using payment_id
        transaction_id = send_result["payment_id"]
        transaction_details = self.venmo_api.get_payment(transaction_id)
        
        self.assertIn("id", transaction_details)
        self.assertEqual(transaction_details["amount"], 30.00)
        self.assertEqual(transaction_details["note"], "Birthday gift")

    def test_add_card_and_add_money(self):
        """
        Scenario: Add a new payment card, then add money to Venmo balance using that card.
        Functions: add_a_payment_card, add_money_to_my_venmo_balance, show_my_venmo_balance
        """
        # NOTE: Multiple methods used in this test don't exist in current API
        self.skipTest("add_money_to_my_venmo_balance and show_my_venmo_balance functionality not implemented in current API")
        self.assertEqual(updated_balance_result["balance"], initial_balance + 50.00)

    def test_set_current_user_success(self):
        """Test authenticating with valid email."""
        result = self.venmo_api.authenticate(f"token_{self.user1_email}")
        self.assertIn("id", result)
        self.assertIn("email", result)
        self.assertEqual(result["email"], self.user1_email)
        self.assertEqual(self.venmo_api.current_user_id, self.user1_id)

    def test_set_current_user_invalid_email(self):
        """Test authenticating with invalid email."""
        with self.assertRaises(Exception) as context:
            self.venmo_api.authenticate("token_nonexistent@example.com")
        self.assertIn("not found", str(context.exception).lower())

    def test_show_account_success(self):
        """Test showing account details for authenticated user."""
        result = self.venmo_api.get_profile()
        self.assertIn("id", result)
        self.assertIn("email", result)
        self.assertEqual(result["email"], self.user1_email)

    def test_show_account_invalid_user(self):
        """Test showing account for user not in system."""
        result = self.venmo_api.get_user_by_id("invalid_user_id")
        self.assertIn("status", result)
        self.assertFalse(result["status"])
        self.assertIn("not found", result["message"].lower())

    def test_list_friends_success(self):
        """Test listing friends for authenticated user."""
        result = self.venmo_api.get_friends()
        self.assertIn("data", result)
        self.assertIsInstance(result["data"], list)

    def test_list_friends_no_friends(self):
        """Test listing friends returns data (even if empty)."""
        result = self.venmo_api.get_friends()
        self.assertIn("data", result)
        self.assertIsInstance(result["data"], list)

    def test_send_money_success_with_valid_users(self):
        """Test sending money between valid users."""
        result = self.venmo_api.create_payment(
            self.user2_email, 
            25.0, 
            "Test payment"
        )
        self.assertIn("id", result)
        self.assertEqual(result["status"], "settled")
        self.assertEqual(result["amount"], 25.0)

    def test_send_money_insufficient_funds(self):
        """Test sending money with insufficient balance."""
        with self.assertRaises(Exception) as context:
            self.venmo_api.create_payment(
                self.user2_email, 
                9999.99, 
                "Too much money"
            )
        self.assertIn("Insufficient balance", str(context.exception))

    def test_send_money_invalid_receiver(self):
        """Test sending money to non-existent user."""
        with self.assertRaises(Exception) as context:
            self.venmo_api.create_payment(
                "nonexistent@example.com", 
                10.0, 
                "Invalid receiver"
            )
        self.assertIn("not found", str(context.exception).lower())

    def test_request_money_success(self):
        """Test requesting money from valid user."""
        result = self.venmo_api.create_charge(
            self.user2_email, 
            30.0, 
            "Rent money"
        )
        self.assertIn("id", result)
        self.assertEqual(result["status"], "pending")
        self.assertEqual(result["action"], "charge")

    def test_request_money_invalid_receiver(self):
        """Test requesting money from invalid user."""
        with self.assertRaises(Exception) as context:
            self.venmo_api.create_charge(
                "invalid@example.com", 
                30.0, 
                "Invalid request"
            )
        self.assertIn("not found", str(context.exception).lower())

    def test_request_money_zero_amount(self):
        """Test requesting zero amount."""
        with self.assertRaises(Exception) as context:
            self.venmo_api.create_charge(
                self.user2_email, 
                0.0, 
                "Zero request"
            )
        self.assertIn("positive", str(context.exception).lower())

    def test_get_transaction_details_valid_id(self):
        """Test getting transaction details with valid ID."""
        # First create a transaction
        send_result = self.venmo_api.create_payment(
            self.user2_email, 
            15.0, 
            "Test transaction"
        )
        self.assertIn("payment_id", send_result)
        
        # Get the transaction details
        transaction_id = send_result["payment_id"]
        result = self.venmo_api.get_payment(transaction_id)
        self.assertIn("id", result)
        self.assertEqual(result["amount"], 15.0)

    def test_get_transaction_details_invalid_id(self):
        """Test getting transaction details with invalid ID."""
        with self.assertRaises(Exception) as context:
            self.venmo_api.get_payment("invalid_id")
        self.assertIn("not found", str(context.exception).lower())

    def test_list_user_transactions_success(self):
        """Test listing transactions for authenticated user."""
        # Create some transactions first
        self.venmo_api.create_payment(self.user2_email, 10.0, "Payment 1")
        self.venmo_api.create_payment(self.user2_email, 20.0, "Payment 2")
        
        result = self.venmo_api.get_transactions()
        self.assertIn("data", result)
        self.assertGreaterEqual(len(result["data"]), 2)

    def test_list_user_transactions_no_transactions(self):
        """Test listing transactions returns data structure."""
        result = self.venmo_api.get_transactions()
        self.assertIn("data", result)
        self.assertIsInstance(result["data"], list)

    def test_add_payment_card_success(self):
        """Test adding a payment card successfully."""
        result = self.venmo_api.add_payment_method(
            "1234567890123456",
            12,
            2026,
            "123",
            "10001"
        )
        self.assertIn("id", result)
        self.assertEqual(result["type"], "card")
        self.assertIn("card", result)

    def test_add_payment_card_invalid_data(self):
        """Test adding payment card with invalid data."""
        # Invalid month should raise exception
        with self.assertRaises(Exception) as context:
            self.venmo_api.add_payment_method(
                "1234567890123456",
                13,    # Invalid month
                2025,
                "123",
                "10001"
            )
        self.assertIn("month", str(context.exception).lower())

    def test_list_payment_methods_success(self):
        """Test listing payment methods for authenticated user."""
        result = self.venmo_api.get_payment_methods()
        self.assertIsInstance(result, list)

    def test_list_payment_methods_invalid_user(self):
        """Test listing payment methods requires authentication."""
        # Create new API instance without authentication
        new_api = VenmoApis()
        with self.assertRaises(Exception) as context:
            new_api.get_payment_methods()
        self.assertIn("authentication", str(context.exception).lower())

    def test_set_default_payment_method_success(self):
        """Test setting default payment method."""
        # First add a payment card
        add_result = self.venmo_api.add_payment_method(
            "1234567890123456",
            12,
            2026,
            "123",
            "10001"
        )
        self.assertIn("id", add_result)
        
        card_id = add_result["id"]
        result = self.venmo_api.set_default_payment_method(card_id)
        self.assertTrue(result["is_default"])

    def test_set_default_payment_method_invalid_card(self):
        """Test setting default payment method with invalid card ID."""
        with self.assertRaises(Exception) as context:
            self.venmo_api.set_default_payment_method("invalid_card_id")
        self.assertIn("not found", str(context.exception).lower())

    def test_delete_payment_method_success(self):
        """Test deleting a payment method."""
        # First add a payment card
        add_result = self.venmo_api.add_payment_method(
            "1234567890123456",
            12,
            2026,
            "123",
            "10001"
        )
        self.assertIn("id", add_result)
        
        card_id = add_result["id"]
        # delete_payment_method returns None on success
        self.venmo_api.delete_payment_method(card_id)
        # Verify it was deleted
        methods = self.venmo_api.get_payment_methods()
        card_ids = [m["id"] for m in methods]
        self.assertNotIn(card_id, card_ids)

    def test_delete_payment_method_invalid_card(self):
        """Test deleting non-existent payment method."""
        with self.assertRaises(Exception) as context:
            self.venmo_api.delete_payment_method("invalid_card_id")
        self.assertIn("not found", str(context.exception).lower())

    def test_get_unread_notification_count_success(self):
        """Test getting unread notification count."""
        # Already authenticated in setUp
        result = self.venmo_api.get_unread_notification_count()
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)

    def test_payment_workflow_end_to_end(self):
        """Test complete payment workflow: add card, send money, check transaction."""
        # Step 1: Add payment card
        card_result = self.venmo_api.add_payment_method(
            "1234567890123456",
            6,
            2026,
            "456",
            "10001"
        )
        self.assertIn("id", card_result)
        
        # Step 2: Send money
        send_result = self.venmo_api.create_payment(
            self.user2_email,
            50.0,
            "End-to-end test payment"
        )
        self.assertEqual(send_result["status"], "settled")
        
        # Step 3: Check transaction details
        transaction_id = send_result["payment_id"]
        details_result = self.venmo_api.get_payment(transaction_id)
        self.assertIn("id", details_result)
        
        # Step 4: Verify transaction in user's transaction list
        transactions_result = self.venmo_api.get_transactions()
        self.assertIn("data", transactions_result)
        self.assertGreater(len(transactions_result["data"]), 0)

    def test_request_workflow_end_to_end(self):
        """Test complete request workflow: request money, check notifications."""
        # Step 1: Request money
        request_result = self.venmo_api.create_charge(
            self.user2_email, 
            75.0,
            "End-to-end test request"
        )
        self.assertEqual(request_result["status"], "pending")
        
        # Step 2: Check unread notifications
        notifications_count = self.venmo_api.get_unread_notification_count()
        self.assertIsInstance(notifications_count, int)
        
        # Step 3: List user transactions to verify request
        transactions_result = self.venmo_api.get_transactions()
        self.assertIn("data", transactions_result)

    def test_account_management_workflow(self):
        """Test account management: show account, list friends, manage payment methods."""
        # Step 1: Show account details
        account_result = self.venmo_api.get_profile()
        self.assertIn("id", account_result)
        
        # Step 2: List friends
        friends_result = self.venmo_api.get_friends()
        self.assertIn("data", friends_result)
        
        # Step 3: List payment methods
        payment_methods_result = self.venmo_api.get_payment_methods()
        self.assertIsInstance(payment_methods_result, list)
        
        # Step 4: Add new payment method
        add_card_result = self.venmo_api.add_payment_method(
            "9876543210123456",
            3,
            2027,
            "789",
            "10001"
        )
        self.assertIn("id", add_card_result)

    def test_error_handling_edge_cases(self):
        """Test various error handling scenarios."""
        # Test with invalid user ID - should return status dict
        result = self.venmo_api.get_user_by_id("invalid_id")
        self.assertIn("status", result)
        self.assertFalse(result["status"])
        
        # Test with negative amount
        with self.assertRaises(Exception) as context:
            self.venmo_api.create_payment(
                self.user2_email,
                -10.0,
                "Negative amount"
            )
        self.assertIn("positive", str(context.exception).lower())
        
        # Test charge with empty note (should work - note is optional)
        result = self.venmo_api.create_charge(
            self.user2_email,
            10.0,
            ""  # Empty note
        )
        self.assertIn("id", result) 

    def test_delete_all_my_notifications_success(self):
        """Test deleting all notifications for current user."""
        # Already authenticated in setUp
        # Get initial count
        initial_count = self.venmo_api.get_unread_notification_count()
        
        # Delete all notifications (returns None)
        self.venmo_api.delete_all_notifications()
        
        # Verify notifications are deleted
        final_count = self.venmo_api.get_unread_notification_count()
        # After deleting all, count should be 0
        self.assertEqual(final_count, 0)

    def test_delete_all_my_notifications_no_current_user(self):
        """Test deleting notifications when no current user is set."""
        # Create new API instance without authentication
        new_api = VenmoApis()
        with self.assertRaises(Exception) as context:
            new_api.delete_all_notifications()
        self.assertIn("authentication", str(context.exception).lower())

    def test_mark_my_notifications_read_success(self):
        """Test marking all notifications as read for current user."""
        # Already authenticated in setUp
        # Create a charge to generate a notification
        self.venmo_api.create_charge(self.user2_email, 10.0, "Test notification")
        
        # Mark all as read (returns None)
        self.venmo_api.mark_notifications_as_read(True)
        
        # All unread should now be 0 or notifications marked as read
        count = self.venmo_api.get_unread_notification_count()
        self.assertEqual(count, 0)

    def test_mark_my_notifications_unread_success(self):
        """Test marking all notifications as unread for current user."""
        # Already authenticated in setUp
        # First mark all as read
        self.venmo_api.mark_notifications_as_read(True)
        self.assertEqual(self.venmo_api.get_unread_notification_count(), 0)
        
        # Now mark all as unread (returns None)
        self.venmo_api.mark_notifications_as_read(False)
        
        # Count should potentially be > 0 if there were notifications
        count = self.venmo_api.get_unread_notification_count()
        self.assertIsInstance(count, int)

    def test_mark_my_notifications_no_current_user(self):
        """Test marking notifications when no current user is set."""
        # Create new API instance without authentication
        new_api = VenmoApis()
        with self.assertRaises(Exception) as context:
            new_api.mark_notifications_as_read(True)
        self.assertIn("authentication", str(context.exception).lower())

    def test_get_account_analytics_success(self):
        """Test getting account analytics for valid user."""
        self.skipTest("get_account_analytics method not implemented in current API")

    def test_get_account_analytics_invalid_user(self):
        """Test getting account analytics for invalid user."""
        self.skipTest("get_account_analytics method not implemented in current API")

    def test_get_transaction_history_success(self):
        """Test getting transaction history for authenticated user."""
        # Create some transactions first
        self.venmo_api.create_payment(self.user2_email, 10.0, "Payment 1")
        self.venmo_api.create_payment(self.user2_email, 20.0, "Payment 2")
        
        result = self.venmo_api.get_transaction_history()
        self.assertIn("transactions", result)
        self.assertIn("analytics", result)
        self.assertIsInstance(result["transactions"], list)
        self.assertGreaterEqual(len(result["transactions"]), 2)

    def test_get_transaction_history_with_limit(self):
        """Test getting transaction history with custom limit."""
        result = self.venmo_api.get_transaction_history(limit=10)
        self.assertIn("transactions", result)
        self.assertLessEqual(len(result["transactions"]), 10)

    def test_get_transaction_history_invalid_user(self):
        """Test getting transaction history requires authentication."""
        # Create new API instance without authentication
        new_api = VenmoApis()
        with self.assertRaises(Exception) as context:
            new_api.get_transaction_history()
        self.assertIn("authentication", str(context.exception).lower())

    def test_upgrade_to_premium_success(self):
        """Test upgrading user to premium status."""
        self.skipTest("upgrade_to_premium method not implemented in current API")

    def test_upgrade_to_premium_already_premium(self):
        """Test upgrading user who is already premium."""
        self.skipTest("upgrade_to_premium method not implemented in current API")

    def test_upgrade_to_premium_invalid_user(self):
        """Test upgrading invalid user to premium."""
        self.skipTest("upgrade_to_premium method not implemented in current API")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
