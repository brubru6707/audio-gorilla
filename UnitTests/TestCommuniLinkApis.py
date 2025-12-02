import unittest
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import backend creator
from CommuniLinkApis import CommuniLinkApis
from UnitTests.test_data_helper import BackendDataLoader

class TestCommuniLinkApis(unittest.TestCase):
    # Load real data from backend
    real_data = BackendDataLoader.get_communi_link_data()
    
    # Extract real user data from first user
    users = real_data.get("users", {})
    first_user_id = next(iter(users), "user1")
    first_user_data = users.get(first_user_id, {})
    
    REAL_USER_ID = first_user_id
    REAL_EMAIL = first_user_data.get("email", "user1@example.com")
    REAL_PHONE = first_user_data.get("phone_number", "+15551234567")
    REAL_NAME = first_user_data.get("name", "Test User")
    TEST_EMAIL = REAL_EMAIL
    TEST_PASSWORD = "testpassword123"  # Will be set during registration if needed
    
    # Get second user for testing interactions
    user_list = list(users.items())
    if len(user_list) > 1:
        second_user_id, second_user_data = user_list[1]
        SECOND_USER_EMAIL = second_user_data.get("email", "user2@example.com")
        SECOND_USER_PHONE = second_user_data.get("phone_number", "+15559876543")
    else:
        SECOND_USER_EMAIL = "user2@example.com"
        SECOND_USER_PHONE = "+15559876543"
    
    def setUp(self):
        """Set up the API instance using default state."""
        self.communilink_api = CommuniLinkApis()
    
    def _login_as_real_user(self):
        """Helper to login as the real test user, registering if needed."""
        # Try to login first
        login_result = self.communilink_api.login_user(self.TEST_EMAIL, self.TEST_PASSWORD)
        
        if not login_result.get("login_status"):
            # User doesn't exist or wrong password, try to register
            register_result = self.communilink_api.register_user(
                first_name="Test",
                last_name="User",
                email=self.TEST_EMAIL,
                password=self.TEST_PASSWORD,
                phone_number=self.REAL_PHONE
            )
            
            if register_result.get("register_status"):
                # Registration successful, now login
                login_result = self.communilink_api.login_user(self.TEST_EMAIL, self.TEST_PASSWORD)
                self.assertTrue(login_result.get("login_status"))
        
        return login_result
    
    # --- SMS Communication Tests ---

    def test_send_sms_success(self):
        """Test sending SMS successfully."""
        self._login_as_real_user()
        result = self.communilink_api.send_sms(
            to_number=self.SECOND_USER_PHONE,
            message="Test message"
        )
        self.assertIn("id", result)
        self.assertEqual(result["to"], self.SECOND_USER_PHONE)
        self.assertEqual(result["message"], "Test message")
        self.assertEqual(result["status"], "delivered")

    def test_send_sms_missing_params(self):
        """Test sending SMS with missing parameters."""
        self._login_as_real_user()
        result = self.communilink_api.send_sms("", "Test")
        self.assertEqual(result["code"], "MISSING_PARAMS")
        self.assertIn("message", result)

    def test_send_sms_invalid_from_number(self):
        """Test sending SMS without being logged in."""
        # Ensure no one is logged in
        self.communilink_api.current_user_id = None
        result = self.communilink_api.send_sms(self.SECOND_USER_PHONE, "Test message")
        self.assertEqual(result["code"], "NOT_AUTHENTICATED")
        self.assertIn("message", result)

    def test_get_sms_status_success(self):
        """Test retrieving SMS status successfully."""
        self._login_as_real_user()
        sent_sms = self.communilink_api.send_sms(self.SECOND_USER_PHONE, "Status check")
        # time.sleep(0.5)  # Allow status to update
        
        status_result = self.communilink_api.get_sms_status(sent_sms["id"])
        self.assertEqual(status_result["id"], sent_sms["id"])
        self.assertEqual(status_result["status"], "delivered")

    def test_get_sms_status_not_found(self):
        """Test retrieving status for non-existent SMS."""
        result = self.communilink_api.get_sms_status("non-existent-sms-id")
        self.assertEqual(result["code"], "SMS_NOT_FOUND")
        self.assertIn("message", result)

    # --- Voice Call Tests ---

    def test_make_voice_call_success(self):
        """Test making a voice call successfully."""
        self._login_as_real_user()
        result = self.communilink_api.make_voice_call(
            to_number=self.SECOND_USER_PHONE
        )
        self.assertIn("call_id", result)
        self.assertEqual(result["to"], self.SECOND_USER_PHONE)
        self.assertEqual(result["status"], "completed")

    def test_get_voice_call_status_success(self):
        """Test retrieving voice call status."""
        self._login_as_real_user()
        call_result = self.communilink_api.make_voice_call(self.SECOND_USER_PHONE)
        
        status_result = self.communilink_api.get_voice_call_status(call_result["call_id"])
        self.assertEqual(status_result["call_id"], call_result["call_id"])
        self.assertEqual(status_result["status"], "completed")

    def test_get_voice_call_status_not_found(self):
        """Test retrieving status for non-existent call."""
        result = self.communilink_api.get_voice_call_status("non-existent-call-id")
        self.assertEqual(result["code"], "CALL_NOT_FOUND")
        self.assertIn("message", result)

    # --- Message and Call History Tests ---

    def test_get_all_sms_messages_success(self):
        """Test retrieving all SMS messages."""
        self._login_as_real_user()
        result = self.communilink_api.get_all_sms_messages()
        self.assertIn("sms_messages", result)
        self.assertIsInstance(result["sms_messages"], list)

    def test_get_all_voice_calls_success(self):
        """Test retrieving all voice calls."""
        self._login_as_real_user()
        result = self.communilink_api.get_all_voice_calls()
        self.assertIn("voice_calls", result)
        self.assertIsInstance(result["voice_calls"], list)

    # --- User Information Tests ---

    def test_get_user_info_success(self):
        """Test retrieving user information."""
        self._login_as_real_user()
        result = self.communilink_api.get_user_info()
        self.assertIn("user", result)
        self.assertIsInstance(result["user"], dict)

    def test_get_user_info_not_found(self):
        """Test retrieving info without being logged in."""
        # Ensure no one is logged in
        self.communilink_api.current_user_id = None
        result = self.communilink_api.get_user_info()
        self.assertEqual(result["code"], "NOT_AUTHENTICATED")

    def test_update_user_settings_success(self):
        """Test updating user settings."""
        self._login_as_real_user()
        settings = {"sms_notifications": True, "call_notifications": False}
        result = self.communilink_api.update_user_settings(settings)
        self.assertIn("updated_settings", result)

    # --- Billing and Support Tests ---

    def test_get_billing_history_success(self):
        """Test retrieving billing history."""
        self._login_as_real_user()
        result = self.communilink_api.get_billing_history()
        self.assertIn("billing_history", result)
        self.assertIsInstance(result["billing_history"], list)

    def test_create_support_ticket_success(self):
        """Test creating a support ticket."""
        self._login_as_real_user()
        result = self.communilink_api.create_support_ticket(
            subject="Test Issue",
            description="This is a test support ticket"
        )
        self.assertIn("ticket", result)
        self.assertIn("ticket_id", result["ticket"])

    # --- System Status Tests ---

    def test_get_network_status_success(self):
        """Test retrieving network status."""
        result = self.communilink_api.get_network_status()
        self.assertIn("status", result)
        self.assertIn("message", result)

    def test_reset_data_success(self):
        """Test resetting data."""
        result = self.communilink_api.reset_data()
        self.assertIn("success", result)
        self.assertTrue(result["status"])

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


