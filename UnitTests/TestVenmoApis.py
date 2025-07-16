from audio_gorilla.VenmoApis import VenmoApis, DEFAULT_STATE
import unittest
from copy import deepcopy

class TestVenmoApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh VenmoApis instance for each test."""
        self.venmo_api = VenmoApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.venmo_api._load_scenario(deepcopy(DEFAULT_STATE))

    # --- Unit Tests for Individual Realistic Functions ---

    def test_show_my_account_info_success(self):
        """Test showing account info for the current user."""
        result = self.venmo_api.show_my_account_info()
        self.assertTrue(result["account_status"])
        self.assertEqual(result["account_info"]["email"], "user1@example.com")
        self.assertEqual(result["account_info"]["first_name"], "Alice")

    def test_show_my_account_info_no_current_user(self):
        """Test showing account info when no user is logged in."""
        self.venmo_api.current_user = None
        result = self.venmo_api.show_my_account_info()
        self.assertFalse(result["account_status"])
        self.assertEqual(result["account_info"], {})

    def test_update_my_account_name_success(self):
        """Test updating the current user's name successfully."""
        result = self.venmo_api.update_my_account_name("Alicia", "Wonderland")
        self.assertTrue(result["update_status"])
        self.assertEqual(self.venmo_api.users["user1@example.com"]["first_name"], "Alicia")
        self.assertEqual(self.venmo_api.users["user1@example.com"]["last_name"], "Wonderland")

    def test_update_my_account_name_no_current_user(self):
        """Test updating name when no user is logged in."""
        self.venmo_api.current_user = None
        result = self.venmo_api.update_my_account_name("John", "Doe")
        self.assertFalse(result["update_status"])

    def test_send_money_success_venmo_balance(self):
        """Test sending money using Venmo balance."""
        initial_balance_sender = self.venmo_api.users["user1@example.com"]["balance"]
        initial_balance_receiver = self.venmo_api.users["user2@example.com"]["balance"]
        
        result = self.venmo_api.send_money("user2@example.com", 25.00, "For dinner", private=True)
        self.assertTrue(result["create_status"])
        
        self.assertEqual(self.venmo_api.users["user1@example.com"]["balance"], initial_balance_sender - 25.00)
        self.assertEqual(self.venmo_api.users["user2@example.com"]["balance"], initial_balance_receiver + 25.00)
        self.assertEqual(len(self.venmo_api.transactions), 1)
        self.assertEqual(self.venmo_api.transactions[0]["sender"], "user1@example.com")
        self.assertEqual(self.venmo_api.transactions[0]["receiver"], "user2@example.com")
        self.assertEqual(self.venmo_api.transactions[0]["amount"], 25.00)
        self.assertTrue(self.venmo_api.transactions[0]["private"])

    def test_send_money_insufficient_balance(self):
        """Test sending money with insufficient Venmo balance."""
        result = self.venmo_api.send_money("user2@example.com", 200.00, "Too much")
        self.assertFalse(result["create_status"])
        self.assertEqual(self.venmo_api.users["user1@example.com"]["balance"], 100.00) # Balance should be unchanged

    def test_send_money_invalid_receiver(self):
        """Test sending money to a non-existent user."""
        result = self.venmo_api.send_money("nonexistent@example.com", 10.00, "Test")
        self.assertFalse(result["create_status"])

    def test_show_my_transactions_all(self):
        """Test showing all transactions for the current user."""
        # Add some dummy transactions
        self.venmo_api.send_money("user2@example.com", 10.00, "Coffee")
        self.venmo_api.current_user = "user2@example.com"
        self.venmo_api.send_money("user1@example.com", 5.00, "Snacks")
        self.venmo_api.current_user = "user1@example.com" # Switch back to original user

        result = self.venmo_api.show_my_transactions()
        self.assertTrue(result["transactions_status"])
        self.assertEqual(len(result["transactions"]), 2) # Should see 2 transactions (sent and received)

    def test_show_my_transactions_filter_direction_sent(self):
        """Test filtering transactions by 'sent' direction."""
        self.venmo_api.send_money("user2@example.com", 10.00, "Coffee")
        self.venmo_api.current_user = "user2@example.com"
        self.venmo_api.send_money("user1@example.com", 5.00, "Snacks")
        self.venmo_api.current_user = "user1@example.com"

        result = self.venmo_api.show_my_transactions(direction="sent")
        self.assertTrue(result["transactions_status"])
        self.assertEqual(len(result["transactions"]), 1)
        self.assertEqual(result["transactions"][0]["sender"], "user1@example.com")

    def test_add_a_payment_card_success(self):
        """Test adding a new payment card successfully."""
        result = self.venmo_api.add_a_payment_card("New Bank Card", "Alice Smith", 5678, 2029, 6, 456)
        self.assertTrue(result["add_status"])
        self.assertEqual(len(self.venmo_api.payment_cards), 2)
        self.assertEqual(self.venmo_api.payment_cards[2]["card_name"], "New Bank Card")
        # Verify it's also in the user's data
        self.assertEqual(len(self.venmo_api.users["user1@example.com"]["payment_cards"]), 2)

    def test_add_a_payment_card_no_current_user(self):
        """Test adding a payment card when no user is logged in."""
        self.venmo_api.logout_user()
        result = self.venmo_api.add_a_payment_card("New Card", "No One", 1111, 2025, 1, 111)
        self.assertFalse(result["add_status"])

    def test_show_my_payment_cards_success(self):
        """Test showing all payment cards for the current user."""
        self.venmo_api.add_a_payment_card("New Bank Card", "Alice Smith", 5678, 2029, 6, 456)
        result = self.venmo_api.show_my_payment_cards()
        self.assertTrue(result["cards_status"])
        self.assertEqual(len(result["payment_cards"]), 2)
        self.assertEqual(result["payment_cards"][0]["card_name"], "My Debit Card")
        self.assertEqual(result["payment_cards"][1]["card_name"], "New Bank Card")

    def test_show_my_payment_cards_no_current_user(self):
        """Test showing payment cards when no user is logged in."""
        self.venmo_api.logout_user()
        result = self.venmo_api.show_my_payment_cards()
        self.assertFalse(result["cards_status"])
        self.assertEqual(result["payment_cards"], [])

    def test_request_money_success(self):
        """Test creating a payment request successfully."""
        result = self.venmo_api.request_money("user2@example.com", 30.00, "For rent")
        self.assertTrue(result["create_status"])
        self.assertEqual(len(self.venmo_api.payment_requests), 1)
        self.assertEqual(self.venmo_api.payment_requests[0]["from_user"], "user1@example.com")
        self.assertEqual(self.venmo_api.payment_requests[0]["to_user"], "user2@example.com")
        self.assertEqual(self.venmo_api.payment_requests[0]["amount"], 30.00)
        self.assertEqual(self.venmo_api.payment_requests[0]["status"], "pending")
        self.assertEqual(len(self.venmo_api.notifications), 1) # Should create a notification for user2

    def test_request_money_invalid_user(self):
        """Test requesting money from a non-existent user."""
        result = self.venmo_api.request_money("unknown@example.com", 10.00, "Test")
        self.assertFalse(result["create_status"])

    def test_approve_a_payment_request_success_balance(self):
        """Test approving a payment request using Venmo balance."""
        self.venmo_api.request_money("user2@example.com", 20.00, "Lunch") # user1 requests from user2
        self.venmo_api.current_user = "user2@example.com" # Switch to user2 to approve
        
        initial_balance_user2 = self.venmo_api.users["user2@example.com"]["balance"]
        initial_balance_user1 = self.venmo_api.users["user1@example.com"]["balance"]

        result = self.venmo_api.approve_a_payment_request(0) # Request ID is 0
        self.assertTrue(result["approve_status"])

        self.assertEqual(self.venmo_api.payment_requests[0]["status"], "approved")
        self.assertEqual(self.venmo_api.users["user2@example.com"]["balance"], initial_balance_user2 - 20.00)
        self.assertEqual(self.venmo_api.users["user1@example.com"]["balance"], initial_balance_user1 + 20.00)
        self.assertEqual(self.venmo_api.transaction_counter, 1) # A transaction should be created
        self.assertEqual(len(self.venmo_api.notifications), 2) # Original request notification + approval notification

    def test_deny_a_payment_request_success(self):
        """Test denying a payment request."""
        self.venmo_api.request_money("user2@example.com", 15.00, "Movie tickets") # user1 requests from user2
        self.venmo_api.current_user = "user2@example.com" # Switch to user2 to deny

        result = self.venmo_api.deny_a_payment_request(0)
        self.assertTrue(result["deny_status"])
        self.assertEqual(self.venmo_api.payment_requests[0]["status"], "denied")
        self.assertEqual(len(self.venmo_api.notifications), 2) # Original request notification + denial notification


    # --- Unit Tests for Combined Functionality ---

    def test_send_and_check_transaction_details(self):
        """
        Scenario: Send money, then check transaction details.
        Functions: send_money, show_a_transaction
        """
        send_result = self.venmo_api.send_money("user2@example.com", 30.00, "Birthday gift", private=False)
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
        add_card_result = self.venmo_api.add_a_payment_card("Vacation Card", "Alice Smith", 9999, 2030, 1, 789)
        self.assertTrue(add_card_result["add_status"])

        card_id = 2 # Assuming it's the second card added (1 was default)
        initial_balance = self.venmo_api.users["user1@example.com"]["balance"]
        
        add_money_result = self.venmo_api.add_money_to_my_venmo_balance(50.00, card_id)
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
        request_result = self.venmo_api.request_money("user2@example.com", 40.00, "Dinner")
        self.assertTrue(request_result["create_status"])
        request_id = 0

        # Check User2's notifications (should have a pending request)
        self.venmo_api.current_user = "user2@example.com"
        user2_notifications_before_deny = self.venmo_api.show_my_notifications()
        self.assertTrue(user2_notifications_before_deny["notifications_status"])
        self.assertEqual(len(user2_notifications_before_deny["notifications"]), 1)
        self.assertEqual(user2_notifications_before_deny["notifications"][0]["type"], "payment_request")
        
        # User2 denies the request
        deny_result = self.venmo_api.deny_a_payment_request(request_id)
        self.assertTrue(deny_result["deny_status"])
        self.assertEqual(self.venmo_api.payment_requests[request_id]["status"], "denied")

        # Check User1's notifications (should have a denial notification)
        self.venmo_api.current_user = "user1@example.com"
        user1_notifications_after_deny = self.venmo_api.show_my_notifications()
        self.assertTrue(user1_notifications_after_deny["notifications_status"])
        self.assertEqual(len(user1_notifications_after_deny["notifications"]), 1) # Only one notification for user1 (the denial)
        self.assertEqual(user1_notifications_after_deny["notifications"][0]["type"], "payment_denied")

        # Check User2's notifications again (should now have the denial and original request)
        self.venmo_api.current_user = "user2@example.com"
        user2_notifications_after_deny = self.venmo_api.show_my_notifications()
        self.assertTrue(user2_notifications_after_deny["notifications_status"])
        self.assertEqual(len(user2_notifications_after_deny["notifications"]), 2) # Original request + denial notification

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)