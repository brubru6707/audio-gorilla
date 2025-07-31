from audio_gorilla.VenmoApis import VenmoApis, DEFAULT_STATE
import unittest
from copy import deepcopy

class TestVenmoApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh VenmoApis instance for each test."""
        self.venmo_api = VenmoApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.venmo_api._load_scenario(deepcopy(DEFAULT_STATE))
        self.user1_email = "user1@example.com"
        self.user2_email = "user2@example.com"

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

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
