from CommuniLinkApis import CommuniLinkApis, DEFAULT_COMMUNILINK_STATE
import unittest
from copy import deepcopy
import time

class TestCommuniLinkApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh CommuniLinkApis instance for each test."""
        self.communi_link_api = CommuniLinkApis()
        self.communi_link_api._load_scenario(deepcopy(DEFAULT_COMMUNILINK_STATE))
        self.user1_email = "user1@example.com"
        self.user2_email = "user2@example.com"
        self.user3_email = "user3@example.com"

        self.user1_phone = "+15551234567"
        self.user2_phone = "+15559876543"
        self.user3_phone = "+15553334444"

    # --- Unit Tests for Core Functions (most important for audio calling) ---

    def test_send_sms_success_user1(self):
        """Test sending SMS successfully for user1."""
        initial_balance = self.communi_link_api.users[self.user1_email]["balance"]
        sms_cost = self.communi_link_api.service_plans[self.communi_link_api.active_plan]["price_per_sms"]
        
        result = self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, "Hello from User1!")
        
        self.assertIn("id", result)
        self.assertEqual(result["from"], self.user1_phone)
        self.assertEqual(result["to"], self.user2_phone)
        self.assertEqual(result["message"], "Hello from User1!")
        self.assertEqual(result["status"], "delivered")
        self.assertEqual(self.communi_link_api.users[self.user1_email]["balance"], initial_balance - sms_cost)
        self.assertEqual(len(self.communi_link_api.users[self.user1_email]["sms_history"]), 1)
        self.assertEqual(self.communi_link_api.sms_counter, 1)

    def test_send_sms_insufficient_balance(self):
        """Test sending SMS with insufficient balance for user2."""
        # Set user2's balance to a very low amount
        self.communi_link_api.users[self.user2_email]["balance"] = 0.01
        
        result = self.communi_link_api.send_sms(self.user2_phone, self.user1_phone, "Urgent message!")
        
        self.assertEqual(result["code"], "INSUFFICIENT_BALANCE")
        self.assertEqual(result["message"], "Insufficient balance to send SMS.")
        self.assertEqual(self.communi_link_api.sms_counter, 0) # No SMS should be sent

    def test_send_sms_invalid_from_number(self):
        """Test sending SMS with an invalid sender number."""
        result = self.communi_link_api.send_sms("+19990001111", self.user2_phone, "Test message.")
        self.assertEqual(result["code"], "INVALID_FROM_NUMBER")
        self.assertEqual(result["message"], "Sender phone number not associated with any user.")
        self.assertEqual(self.communi_link_api.sms_counter, 0)

    def test_get_sms_status_success(self):
        """Test retrieving SMS status successfully."""
        sent_sms = self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, "Status check.")
        time.sleep(0.5) # Give time for status to update to delivered
        
        status_result = self.communi_link_api.get_sms_status(sent_sms["id"])
        
        self.assertEqual(status_result["id"], sent_sms["id"])
        self.assertEqual(status_result["status"], "delivered")

    def test_get_sms_status_not_found(self):
        """Test retrieving status for a non-existent SMS."""
        result = self.communi_link_api.get_sms_status("non-existent-sms-id")
        self.assertEqual(result["code"], "SMS_NOT_FOUND")
        self.assertEqual(result["message"], "SMS message with ID 'non-existent-sms-id' not found.")

    def test_make_voice_call_success_user2(self):
        """Test making a voice call successfully for user2."""
        initial_balance = self.communi_link_api.users[self.user2_email]["balance"]
        
        result = self.communi_link_api.make_voice_call(self.user2_phone, self.user1_phone, "http://audio.example.com/greeting.mp3")
        
        self.assertIn("id", result)
        self.assertEqual(result["from"], self.user2_phone)
        self.assertEqual(result["to"], self.user1_phone)
        self.assertEqual(result["audioUrl"], "http:// .example.com/greeting.mp3")
        self.assertEqual(result["status"], "completed")
        self.assertGreater(result["duration"], 0)
        
        # Verify balance deduction
        call_cost = self.communi_link_api.service_plans[self.communi_link_api.active_plan]["price_per_minute"] * (result["duration"] / 60)
        self.assertAlmostEqual(self.communi_link_api.users[self.user2_email]["balance"], initial_balance - call_cost, places=2)
        self.assertEqual(len(self.communi_link_api.users[self.user2_email]["call_history"]), 1)
        self.assertEqual(self.communi_link_api.call_counter, 1)

    def test_make_voice_call_insufficient_balance(self):
        """Test making a voice call with insufficient balance for user1."""
        # Set user1's balance to a very low amount
        self.communi_link_api.users[self.user1_email]["balance"] = 0.01
        
        result = self.communi_link_api.make_voice_call(self.user1_phone, self.user3_phone)
        
        self.assertEqual(result["code"], "INSUFFICIENT_BALANCE") # True
        self.assertEqual(result["message"], "Insufficient balance to make call.") # True
        self.assertEqual(self.communi_link_api.call_counter, 0) # No call should be made

    def test_make_voice_call_invalid_from_number(self):
        """Test making a voice call with an invalid caller number."""
        result = self.communi_link_api.make_voice_call("+19990001111", self.user1_phone)
        self.assertEqual(result["code"], "INVALID_FROM_NUMBER")
        self.assertEqual(result["message"], "Caller phone number not associated with any user.")
        self.assertEqual(self.communi_link_api.call_counter, 0)

    def test_get_voice_call_status_success(self):
        """Test retrieving voice call status successfully."""
        made_call = self.communi_link_api.make_voice_call(self.user3_phone, self.user1_phone)
        time.sleep(made_call["duration"] / 1000 + 0.5) # Give time for call to complete
        
        status_result = self.communi_link_api.get_voice_call_status(made_call["id"])
        
        self.assertEqual(status_result["id"], made_call["id"])
        self.assertEqual(status_result["status"], "completed")
        self.assertGreater(status_result["duration"], 0)

    def test_get_voice_call_status_not_found(self):
        """Test retrieving status for a non-existent voice call."""
        result = self.communi_link_api.get_voice_call_status("non-existent-call-id")
        self.assertEqual(result["code"], "CALL_NOT_FOUND")
        self.assertEqual(result["message"], "Voice call with ID 'non-existent-call-id' not found.")

    # --- Unit Tests Combining Multiple Functions ---

    def test_send_sms_and_check_billing_history(self):
        """Test sending SMS and verifying it appears in billing history for user1."""
        initial_billing_count = len(self.communi_link_api.billing_history)
        sms_cost = self.communi_link_api.service_plans[self.communi_link_api.active_plan]["price_per_sms"]

        self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, "Billing test SMS.")
        
        billing_history_result = self.communi_link_api.get_billing_history(self.user1_email)
        self.assertEqual(len(billing_history_result["billing_history"]), initial_billing_count + 1)
        
        last_billing_record = billing_history_result["billing_history"][-1]
        self.assertEqual(last_billing_record["type"], "sms")
        self.assertEqual(last_billing_record["user_email"], self.user1_email)
        self.assertAlmostEqual(last_billing_record["amount"], sms_cost, places=2)

    def test_make_call_and_check_billing_history(self):
        """Test making a call and verifying it appears in billing history for user3."""
        initial_billing_count = len(self.communi_link_api.billing_history)
        
        made_call = self.communi_link_api.make_voice_call(self.user3_phone, self.user1_phone)
        time.sleep(made_call["duration"] / 1000 + 0.5) # Ensure call completes and cost is applied

        billing_history_result = self.communi_link_api.get_billing_history(self.user3_email)
        self.assertEqual(len(billing_history_result["billing_history"]), initial_billing_count + 1)
        
        last_billing_record = billing_history_result["billing_history"][-1]
        self.assertEqual(last_billing_record["type"], "voice_call")
        self.assertEqual(last_billing_record["user_email"], self.user3_email)
        
        expected_cost = self.communi_link_api.service_plans[self.communi_link_api.active_plan]["price_per_minute"] * (made_call["duration"] / 60)
        self.assertAlmostEqual(last_billing_record["amount"], expected_cost, places=2)

    def test_send_sms_and_get_all_sms_messages(self):
        """Test sending SMS and then retrieving all SMS messages for user2."""
        initial_sms_count_user2 = len(self.communi_link_api.users[self.user2_email]["sms_history"])
        
        self.communi_link_api.send_sms(self.user2_phone, self.user3_phone, "Hello from User2!")
        
        all_sms_result = self.communi_link_api.get_all_sms_messages(self.user2_email)
        self.assertEqual(len(all_sms_result["sms_messages"]), initial_sms_count_user2 + 1)
        self.assertEqual(all_sms_result["sms_messages"][-1]["message"], "Hello from User2!")

    def test_make_call_and_get_all_voice_calls(self):
        """Test making a call and then retrieving all voice calls for user1."""
        initial_call_count_user1 = len(self.communi_link_api.users[self.user1_email]["call_history"])
        
        made_call = self.communi_link_api.make_voice_call(self.user1_phone, self.user2_phone)
        time.sleep(made_call["duration"] / 1000 + 0.5) # Ensure call completes
        
        all_calls_result = self.communi_link_api.get_all_voice_calls(self.user1_email)
        self.assertEqual(len(all_calls_result["voice_calls"]), initial_call_count_user1 + 1)
        self.assertEqual(all_calls_result["voice_calls"][-1]["to"], self.user2_phone)

    def test_update_settings_and_make_call(self):
        """Test updating call forwarding settings and then attempting a call (though call forwarding doesn't prevent calls in this dummy API)."""
        # User1 initially has call forwarding disabled
        initial_settings = self.communi_link_api.users[self.user1_email]["settings"]
        self.assertFalse(initial_settings["call_forwarding_enabled"])

        # Update settings for user1
        update_result = self.communi_link_api.update_user_settings(self.user1_email, {"call_forwarding_enabled": True, "call_forwarding_number": "+15550009999"})
        self.assertTrue(update_result["updated_settings"]["call_forwarding_enabled"])
        self.assertEqual(update_result["updated_settings"]["call_forwarding_number"], "+15550009999")

        # Make a call from user1 after updating settings
        initial_balance = self.communi_link_api.users[self.user1_email]["balance"]
        made_call = self.communi_link_api.make_voice_call(self.user1_phone, self.user3_phone)
        time.sleep(made_call["duration"] / 1000 + 0.5) # Ensure call completes
        
        self.assertEqual(made_call["status"], "completed")
        # Verify balance deduction still occurs
        call_cost = self.communi_link_api.service_plans[self.communi_link_api.active_plan]["price_per_minute"] * (made_call["duration"] / 60)
        self.assertAlmostEqual(self.communi_link_api.users[self.user1_email]["balance"], initial_balance - call_cost, places=2)

    def test_create_support_ticket_and_check_history(self):
        """Test creating a support ticket and verifying it exists in the support tickets list."""
        initial_ticket_count = len(self.communi_link_api.support_tickets)
        
        ticket_subject = "Issue with SMS delivery"
        ticket_description = "Some SMS messages are not being delivered to recipients."
        
        ticket_result = self.communi_link_api.create_support_ticket(self.user1_email, ticket_subject, ticket_description)
        
        self.assertIn("support_ticket", ticket_result)
        self.assertEqual(ticket_result["support_ticket"]["user_email"], self.user1_email)
        self.assertEqual(ticket_result["support_ticket"]["subject"], ticket_subject)
        self.assertEqual(ticket_result["support_ticket"]["description"], ticket_description)
        self.assertEqual(ticket_result["support_ticket"]["status"], "open")
        
        self.assertEqual(len(self.communi_link_api.support_tickets), initial_ticket_count + 1)
        self.assertEqual(self.communi_link_api.support_tickets[-1]["subject"], ticket_subject)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

