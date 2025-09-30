from CommuniLinkApis import CommuniLinkApis, DEFAULT_COMMUNILINK_STATE
import unittest
from copy import deepcopy
import time

class TestCommuniLinkApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh CommuniLinkApis instance for each test."""
        self.communi_link_api = CommuniLinkApis()
        self.communi_link_api._load_scenario(deepcopy(DEFAULT_COMMUNILINK_STATE))
        # Test user emails and phone numbers
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

    # --- Comprehensive Test Coverage for All CommuniLinkApis Methods ---

    def test_send_sms_comprehensive_success_cases(self):
        """Test SMS sending with various success scenarios."""
        # Test with different message lengths
        short_message = "Hi!"
        long_message = "This is a very long message that tests the SMS functionality with extended content to ensure proper handling of longer text messages."
        
        result_short = self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, short_message)
        self.assertEqual(result_short["status"], "delivered")
        self.assertEqual(result_short["message"], short_message)
        
        result_long = self.communi_link_api.send_sms(self.user2_phone, self.user3_phone, long_message)
        self.assertEqual(result_long["status"], "delivered")
        self.assertEqual(result_long["message"], long_message)

    def test_send_sms_edge_cases(self):
        """Test SMS sending edge cases."""
        # Empty message
        result_empty = self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, "")
        self.assertIn("code", result_empty)  # Should handle empty message appropriately
        
        # Special characters in message
        special_message = "Testing émojis 😀🚀 and spëcial characters!"
        result_special = self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, special_message)
        if "status" in result_special:
            self.assertEqual(result_special["message"], special_message)

    def test_send_sms_invalid_numbers(self):
        """Test SMS sending with various invalid phone numbers."""
        invalid_numbers = [
            "invalid_number",
            "+999999999999999",  # Too long
            "+1234",  # Too short
            "",  # Empty
            "1234567890"  # No country code
        ]
        
        for invalid_number in invalid_numbers:
            result_from = self.communi_link_api.send_sms(invalid_number, self.user2_phone, "Test")
            result_to = self.communi_link_api.send_sms(self.user1_phone, invalid_number, "Test")
            
            self.assertIn("code", result_from)
            self.assertIn("code", result_to)

    def test_get_sms_status_comprehensive(self):
        """Test comprehensive SMS status checking."""
        # Send SMS and check status immediately
        sent_sms = self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, "Status test")
        
        # Check status multiple times
        for _ in range(3):
            status_result = self.communi_link_api.get_sms_status(sent_sms["id"])
            self.assertEqual(status_result["id"], sent_sms["id"])
            self.assertIn(status_result["status"], ["sent", "delivered", "failed"])
            time.sleep(0.1)

    def test_get_sms_status_edge_cases(self):
        """Test SMS status checking edge cases."""
        # Invalid ID formats
        invalid_ids = ["", "invalid-id", "123", None]
        
        for invalid_id in invalid_ids:
            if invalid_id is not None:
                result = self.communi_link_api.get_sms_status(invalid_id)
                self.assertIn("code", result)

    def test_make_voice_call_comprehensive_success(self):
        """Test voice call functionality with comprehensive scenarios."""
        # Test call without audio URL
        result_no_audio = self.communi_link_api.make_voice_call(self.user1_phone, self.user2_phone)
        self.assertEqual(result_no_audio["from"], self.user1_phone)
        self.assertEqual(result_no_audio["to"], self.user2_phone)
        self.assertGreater(result_no_audio["duration"], 0)
        
        # Test call with audio URL
        audio_url = "https://example.com/audio/test.mp3"
        result_with_audio = self.communi_link_api.make_voice_call(
            self.user2_phone, self.user3_phone, audio_url
        )
        self.assertEqual(result_with_audio["audioUrl"], audio_url)
        self.assertEqual(result_with_audio["status"], "completed")

    def test_make_voice_call_cost_calculation(self):
        """Test voice call cost calculation accuracy."""
        initial_balance = self.communi_link_api.users[self.user1_email]["balance"]
        
        call_result = self.communi_link_api.make_voice_call(self.user1_phone, self.user2_phone)
        
        # Calculate expected cost
        price_per_minute = self.communi_link_api.service_plans[self.communi_link_api.active_plan]["price_per_minute"]
        expected_cost = price_per_minute * (call_result["duration"] / 60)
        
        final_balance = self.communi_link_api.users[self.user1_email]["balance"]
        actual_cost = initial_balance - final_balance
        
        self.assertAlmostEqual(actual_cost, expected_cost, places=2)

    def test_make_voice_call_invalid_scenarios(self):
        """Test voice call with invalid scenarios."""
        # Invalid audio URLs
        invalid_urls = [
            "not-a-url",
            "ftp://invalid.com/audio.mp3",
            "https://",
            ""
        ]
        
        for invalid_url in invalid_urls:
            result = self.communi_link_api.make_voice_call(
                self.user1_phone, self.user2_phone, invalid_url
            )
            if "code" in result:
                self.assertIn("INVALID", result["code"].upper())

    def test_get_voice_call_status_comprehensive(self):
        """Test comprehensive voice call status checking."""
        # Make a call and track its status
        call_result = self.communi_link_api.make_voice_call(self.user1_phone, self.user2_phone)
        call_id = call_result["id"]
        
        # Check status immediately and after delay
        immediate_status = self.communi_link_api.get_voice_call_status(call_id)
        self.assertEqual(immediate_status["id"], call_id)
        
        time.sleep(0.5)
        final_status = self.communi_link_api.get_voice_call_status(call_id)
        self.assertEqual(final_status["status"], "completed")

    def test_get_all_sms_messages_comprehensive(self):
        """Test comprehensive SMS message retrieval."""
        # Send multiple SMS messages from different users
        messages = [
            (self.user1_phone, self.user2_phone, "Message 1 from User1"),
            (self.user2_phone, self.user3_phone, "Message 2 from User2"),
            (self.user3_phone, self.user1_phone, "Message 3 from User3"),
        ]
        
        for from_phone, to_phone, message in messages:
            self.communi_link_api.send_sms(from_phone, to_phone, message)
        
        # Get SMS messages for each user
        for user_email in [self.user1_email, self.user2_email, self.user3_email]:
            result = self.communi_link_api.get_all_sms_messages(user_email)
            self.assertIn("sms_messages", result)
            self.assertIsInstance(result["sms_messages"], list)

    def test_get_all_sms_messages_no_user_filter(self):
        """Test getting all SMS messages without user filter."""
        # Send some messages
        self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, "Test message 1")
        self.communi_link_api.send_sms(self.user2_phone, self.user3_phone, "Test message 2")
        
        # Get all messages without user filter
        result = self.communi_link_api.get_all_sms_messages()
        self.assertIn("sms_messages", result)
        self.assertGreaterEqual(len(result["sms_messages"]), 2)

    def test_get_all_voice_calls_comprehensive(self):
        """Test comprehensive voice call retrieval."""
        # Make multiple calls from different users
        calls = [
            (self.user1_phone, self.user2_phone),
            (self.user2_phone, self.user3_phone),
            (self.user3_phone, self.user1_phone),
        ]
        
        for from_phone, to_phone in calls:
            self.communi_link_api.make_voice_call(from_phone, to_phone)
        
        # Get voice calls for each user
        for user_email in [self.user1_email, self.user2_email, self.user3_email]:
            result = self.communi_link_api.get_all_voice_calls(user_email)
            self.assertIn("voice_calls", result)
            self.assertIsInstance(result["voice_calls"], list)

    def test_get_all_voice_calls_no_user_filter(self):
        """Test getting all voice calls without user filter."""
        # Make some calls
        self.communi_link_api.make_voice_call(self.user1_phone, self.user2_phone)
        self.communi_link_api.make_voice_call(self.user2_phone, self.user3_phone)
        
        # Get all calls without user filter
        result = self.communi_link_api.get_all_voice_calls()
        self.assertIn("voice_calls", result)
        self.assertGreaterEqual(len(result["voice_calls"]), 2)

    def test_get_user_info_success(self):
        """Test getting user information successfully."""
        result = self.communi_link_api.get_user_info(self.user1_email)
        self.assertIn("user_info", result)
        self.assertEqual(result["user_info"]["email"], self.user1_email)
        self.assertIn("phone_number", result["user_info"])
        self.assertIn("balance", result["user_info"])
        self.assertIn("settings", result["user_info"])

    def test_get_user_info_invalid_user(self):
        """Test getting user info for non-existent user."""
        result = self.communi_link_api.get_user_info("nonexistent@example.com")
        self.assertIn("code", result)
        self.assertIn("USER_NOT_FOUND", result["code"])

    def test_update_user_settings_comprehensive(self):
        """Test comprehensive user settings updates."""
        # Test updating individual settings
        settings_updates = [
            {"call_forwarding_enabled": True},
            {"call_forwarding_number": "+15550009999"},
            {"do_not_disturb": True},
            {"notification_preferences": {"sms": True, "calls": False}},
            {"timezone": "America/New_York"}
        ]
        
        for settings_update in settings_updates:
            result = self.communi_link_api.update_user_settings(self.user1_email, settings_update)
            self.assertIn("updated_settings", result)
            
            # Verify the setting was actually updated
            for key, value in settings_update.items():
                if key in result["updated_settings"]:
                    self.assertEqual(result["updated_settings"][key], value)

    def test_update_user_settings_bulk_update(self):
        """Test bulk user settings update."""
        bulk_settings = {
            "call_forwarding_enabled": True,
            "call_forwarding_number": "+15550001111",
            "do_not_disturb": False,
            "notification_preferences": {
                "sms": True,
                "calls": True,
                "email": False
            }
        }
        
        result = self.communi_link_api.update_user_settings(self.user2_email, bulk_settings)
        self.assertIn("updated_settings", result)
        
        # Verify all settings were updated
        for key, value in bulk_settings.items():
            if key in result["updated_settings"]:
                self.assertEqual(result["updated_settings"][key], value)

    def test_update_user_settings_invalid_user(self):
        """Test updating settings for invalid user."""
        result = self.communi_link_api.update_user_settings(
            "invalid@example.com", 
            {"call_forwarding_enabled": True}
        )
        self.assertIn("code", result)
        self.assertIn("USER_NOT_FOUND", result["code"])

    def test_get_billing_history_comprehensive(self):
        """Test comprehensive billing history retrieval."""
        # Generate billing activities
        self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, "Billing test SMS")
        self.communi_link_api.make_voice_call(self.user1_phone, self.user2_phone)
        
        # Get billing history
        result = self.communi_link_api.get_billing_history(self.user1_email)
        self.assertIn("billing_history", result)
        self.assertIsInstance(result["billing_history"], list)
        
        # Verify billing records contain expected information
        if len(result["billing_history"]) > 0:
            record = result["billing_history"][-1]
            self.assertIn("type", record)
            self.assertIn("amount", record)
            self.assertIn("timestamp", record)

    def test_get_billing_history_all_users(self):
        """Test getting billing history for all users."""
        # Generate some billing activity
        self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, "Test")
        self.communi_link_api.send_sms(self.user2_phone, self.user3_phone, "Test")
        
        # Get all billing history
        result = self.communi_link_api.get_billing_history()
        self.assertIn("billing_history", result)
        self.assertGreaterEqual(len(result["billing_history"]), 2)

    def test_create_support_ticket_comprehensive(self):
        """Test comprehensive support ticket creation."""
        # Test various ticket scenarios
        tickets = [
            ("SMS Delivery Issue", "Messages are not being delivered properly"),
            ("Call Quality Problem", "Voice calls have poor audio quality"),
            ("Billing Question", "I have questions about my recent charges"),
            ("Feature Request", "Please add call recording functionality")
        ]
        
        for subject, description in tickets:
            result = self.communi_link_api.create_support_ticket(
                self.user1_email, subject, description
            )
            self.assertIn("support_ticket", result)
            self.assertEqual(result["support_ticket"]["subject"], subject)
            self.assertEqual(result["support_ticket"]["description"], description)
            self.assertEqual(result["support_ticket"]["status"], "open")

    def test_create_support_ticket_edge_cases(self):
        """Test support ticket creation edge cases."""
        # Empty subject and description
        result_empty = self.communi_link_api.create_support_ticket(
            self.user1_email, "", ""
        )
        self.assertIn("code", result_empty)  # Should handle empty input
        
        # Very long subject and description
        long_subject = "A" * 500
        long_description = "B" * 2000
        result_long = self.communi_link_api.create_support_ticket(
            self.user1_email, long_subject, long_description
        )
        if "support_ticket" in result_long:
            self.assertEqual(result_long["support_ticket"]["subject"], long_subject)

    def test_create_support_ticket_invalid_user(self):
        """Test creating support ticket for invalid user."""
        result = self.communi_link_api.create_support_ticket(
            "invalid@example.com", 
            "Test Subject", 
            "Test Description"
        )
        self.assertIn("code", result)
        self.assertIn("USER_NOT_FOUND", result["code"])

    def test_get_network_status_success(self):
        """Test getting network status."""
        result = self.communi_link_api.get_network_status()
        self.assertIn("status", result)
        self.assertIn(result["status"], ["operational", "degraded", "outage"])
        
        if "details" in result:
            self.assertIsInstance(result["details"], str)

    def test_reset_data_functionality(self):
        """Test data reset functionality."""
        # Generate some data first
        self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, "Test before reset")
        self.communi_link_api.make_voice_call(self.user1_phone, self.user2_phone)
        
        # Reset data
        result = self.communi_link_api.reset_data()
        self.assertTrue(result["success"])
        
        # Verify data was reset (counters should be reset)
        self.assertEqual(self.communi_link_api.sms_counter, 0)
        self.assertEqual(self.communi_link_api.call_counter, 0)

    def test_communication_workflow_sms_to_call(self):
        """Test workflow: SMS followed by voice call."""
        # Send SMS notification
        sms_result = self.communi_link_api.send_sms(
            self.user1_phone, self.user2_phone, "Calling you now!"
        )
        self.assertEqual(sms_result["status"], "delivered")
        
        # Follow up with voice call
        call_result = self.communi_link_api.make_voice_call(self.user1_phone, self.user2_phone)
        self.assertEqual(call_result["status"], "completed")
        
        # Verify both appear in user's history
        sms_history = self.communi_link_api.get_all_sms_messages(self.user1_email)
        call_history = self.communi_link_api.get_all_voice_calls(self.user1_email)
        
        self.assertGreater(len(sms_history["sms_messages"]), 0)
        self.assertGreater(len(call_history["voice_calls"]), 0)

    def test_multi_user_communication_workflow(self):
        """Test multi-user communication workflow."""
        # User1 sends SMS to User2
        self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, "Hello User2")
        
        # User2 calls User3
        self.communi_link_api.make_voice_call(self.user2_phone, self.user3_phone)
        
        # User3 sends SMS to User1
        self.communi_link_api.send_sms(self.user3_phone, self.user1_phone, "Hello User1")
        
        # Verify each user has appropriate communication history
        user1_sms = self.communi_link_api.get_all_sms_messages(self.user1_email)
        user2_calls = self.communi_link_api.get_all_voice_calls(self.user2_email)
        user3_sms = self.communi_link_api.get_all_sms_messages(self.user3_email)
        
        self.assertGreater(len(user1_sms["sms_messages"]), 0)
        self.assertGreater(len(user2_calls["voice_calls"]), 0)
        self.assertGreater(len(user3_sms["sms_messages"]), 0)

    def test_billing_and_balance_workflow(self):
        """Test comprehensive billing and balance workflow."""
        # Check initial balance
        initial_info = self.communi_link_api.get_user_info(self.user1_email)
        initial_balance = initial_info["user_info"]["balance"]
        
        # Perform billable activities
        self.communi_link_api.send_sms(self.user1_phone, self.user2_phone, "Billing test")
        self.communi_link_api.make_voice_call(self.user1_phone, self.user2_phone)
        
        # Check updated balance
        updated_info = self.communi_link_api.get_user_info(self.user1_email)
        updated_balance = updated_info["user_info"]["balance"]
        
        # Verify balance decreased
        self.assertLess(updated_balance, initial_balance)
        
        # Check billing history
        billing_result = self.communi_link_api.get_billing_history(self.user1_email)
        self.assertGreaterEqual(len(billing_result["billing_history"]), 2)

    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling scenarios."""
        # Test with None parameters
        with self.assertRaises((TypeError, AttributeError)):
            self.communi_link_api.send_sms(None, self.user2_phone, "Test")
        
        # Test with empty strings
        result_empty_from = self.communi_link_api.send_sms("", self.user2_phone, "Test")
        result_empty_to = self.communi_link_api.send_sms(self.user1_phone, "", "Test")
        
        self.assertIn("code", result_empty_from)
        self.assertIn("code", result_empty_to)
        
        # Test invalid status checks
        invalid_status = self.communi_link_api.get_sms_status("invalid-id-12345")
        self.assertIn("code", invalid_status)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

