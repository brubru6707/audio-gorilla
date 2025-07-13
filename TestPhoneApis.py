import unittest
from datetime import datetime
from copy import deepcopy
from PhoneApis import PhoneApis, DEFAULT_STATE

class TestPhoneApis(unittest.TestCase):
    def setUp(self):
        """Initialize a fresh PhoneApis instance before each test"""
        self.api = PhoneApis()
        self.test_user = "test_user"
        self.test_recipient = "recipient_user"
        self.test_message = "Hello, this is a test message"
        
        # Setup a basic scenario with one user and one message
        self.scenario = {
            "users": {
                self.test_user: {"password": "test123"},
                self.test_recipient: {"password": "recipient123"}
            },
            "voice_messages": {
                0: {
                    "id": 0,
                    "sender": self.test_user,
                    "recipient": self.test_recipient,
                    "message": "Initial message",
                    "timestamp": "2023-01-01T00:00:00",
                    "played": False
                }
            },
            "current_user": self.test_user,
            "password_reset_codes": {},
            "message_counter": 1
        }
        self.api._load_scenario(self.scenario)

    def tearDown(self):
        """Clean up after each test"""
        self.api = None

    # Individual function tests
    def test_load_scenario(self):
        """Test loading a scenario into the API"""
        self.assertEqual(self.api.users, self.scenario["users"])
        self.assertEqual(self.api.voice_messages, self.scenario["voice_messages"])
        self.assertEqual(self.api.current_user, self.scenario["current_user"])
        self.assertEqual(self.api.message_counter, self.scenario["message_counter"])

    def test_show_voice_message_window_success(self):
        """Test showing voice messages window successfully"""
        result = self.api.show_voice_message_window(
            phone_number=self.test_recipient,
            min_datetime="2023-01-01T00:00:00",
            max_datetime="2023-12-31T23:59:59",
            pagination_order="ascending",
            page_index=0,
            page_limit=10,
            user=self.test_user
        )
        self.assertTrue(result["messages_status"])

    def test_show_voice_message_window_no_user(self):
        """Test showing voice messages window with no current user"""
        self.api.current_user = None
        result = self.api.show_voice_message_window(
            phone_number=self.test_recipient,
            min_datetime="2023-01-01T00:00:00",
            max_datetime="2023-12-31T23:59:59",
            pagination_order="ascending",
            page_index=0,
            page_limit=10,
            user=self.test_user
        )
        self.assertFalse(result["messages_status"])

    def test_search_voice_messages_success(self):
        """Test searching voice messages successfully"""
        result = self.api.search_voice_messages(
            query="initial",
            phone_number=self.test_recipient,
            only_latest_per_contact=True,
            page_index=0,
            page_limit=10,
            sort_by="timestamp",
            user=self.test_user
        )
        self.assertTrue(result["search_status"])

    def test_search_voice_messages_no_user(self):
        """Test searching voice messages with no current user"""
        self.api.current_user = None
        result = self.api.search_voice_messages(
            query="initial",
            phone_number=self.test_recipient,
            only_latest_per_contact=True,
            page_index=0,
            page_limit=10,
            sort_by="timestamp",
            user=self.test_user
        )
        self.assertFalse(result["search_status"])

    def test_show_voice_message_success(self):
        """Test showing a specific voice message successfully"""
        result = self.api.show_voice_message(
            voice_message_id=0,
            user=self.test_user
        )
        self.assertTrue(result["message_status"])

    def test_show_voice_message_no_user(self):
        """Test showing a voice message with no current user"""
        self.api.current_user = None
        result = self.api.show_voice_message(
            voice_message_id=0,
            user=self.test_user
        )
        self.assertFalse(result["message_status"])

    def test_show_voice_message_invalid_id(self):
        """Test showing a non-existent voice message"""
        result = self.api.show_voice_message(
            voice_message_id=999,
            user=self.test_user
        )
        self.assertFalse(result["message_status"])

    def test_send_voice_message_success(self):
        """Test sending a voice message successfully"""
        initial_count = len(self.api.voice_messages)
        result = self.api.send_voice_message(
            phone_number=self.test_recipient,
            message=self.test_message,
            user=self.test_user
        )
        self.assertTrue(result["send_status"])
        self.assertEqual(len(self.api.voice_messages), initial_count + 1)

    def test_send_voice_message_no_user(self):
        """Test sending a voice message with no current user"""
        self.api.current_user = None
        initial_count = len(self.api.voice_messages)
        result = self.api.send_voice_message(
            phone_number=self.test_recipient,
            message=self.test_message,
            user=self.test_user
        )
        self.assertFalse(result["send_status"])
        self.assertEqual(len(self.api.voice_messages), initial_count)

    def test_delete_voice_message_success_as_sender(self):
        """Test deleting a voice message as the sender"""
        initial_count = len(self.api.voice_messages)
        result = self.api.delete_voice_message(
            voice_message_id=0,
            user=self.test_user
        )
        self.assertTrue(result["deletion_status"])
        self.assertEqual(len(self.api.voice_messages), initial_count - 1)

    def test_delete_voice_message_success_as_recipient(self):
        """Test deleting a voice message as the recipient"""
        self.api.current_user = self.test_recipient
        initial_count = len(self.api.voice_messages)
        result = self.api.delete_voice_message(
            voice_message_id=0,
            user=self.test_recipient
        )
        self.assertTrue(result["deletion_status"])
        self.assertEqual(len(self.api.voice_messages), initial_count - 1)

    def test_delete_voice_message_no_user(self):
        """Test deleting a voice message with no current user"""
        self.api.current_user = None
        initial_count = len(self.api.voice_messages)
        result = self.api.delete_voice_message(
            voice_message_id=0,
            user=self.test_user
        )
        self.assertFalse(result["deletion_status"])
        self.assertEqual(len(self.api.voice_messages), initial_count)

    def test_delete_voice_message_invalid_id(self):
        """Test deleting a non-existent voice message"""
        initial_count = len(self.api.voice_messages)
        result = self.api.delete_voice_message(
            voice_message_id=999,
            user=self.test_user
        )
        self.assertFalse(result["deletion_status"])
        self.assertEqual(len(self.api.voice_messages), initial_count)

    def test_delete_voice_message_unauthorized(self):
        """Test deleting a voice message by unauthorized user"""
        unauthorized_user = "unauthorized_user"
        self.api.users[unauthorized_user] = {"password": "test123"}
        self.api.current_user = unauthorized_user
        
        initial_count = len(self.api.voice_messages)
        result = self.api.delete_voice_message(
            voice_message_id=0,
            user=unauthorized_user
        )
        self.assertFalse(result["deletion_status"])
        self.assertEqual(len(self.api.voice_messages), initial_count)

    def test_get_current_date_and_time(self):
        """Test getting current date and time"""
        result = self.api.get_current_date_and_time()
        self.assertTrue(result["datetime_status"])

    # Tests that use multiple functions
    def test_send_and_show_message_flow(self):
        """Test the complete flow of sending and then showing a message"""
        # Send a new message
        send_result = self.api.send_voice_message(
            phone_number=self.test_recipient,
            message=self.test_message,
            user=self.test_user
        )
        self.assertTrue(send_result["send_status"])
        
        # Get the ID of the new message (should be 1 since we started with counter=1)
        new_message_id = self.api.message_counter - 1
        
        # Show the message we just sent
        show_result = self.api.show_voice_message(
            voice_message_id=new_message_id,
            user=self.test_user
        )
        self.assertTrue(show_result["message_status"])

    def test_send_search_and_delete_flow(self):
        """Test sending, searching, and then deleting a message"""
        # Send a new message with unique content
        unique_message = "Unique searchable content " + str(datetime.now())
        send_result = self.api.send_voice_message(
            phone_number=self.test_recipient,
            message=unique_message,
            user=self.test_user
        )
        self.assertTrue(send_result["send_status"])
        
        # Search for the message
        search_result = self.api.search_voice_messages(
            query="Unique searchable",
            phone_number=None,
            only_latest_per_contact=False,
            page_index=0,
            page_limit=10,
            sort_by=None,
            user=self.test_user
        )
        self.assertTrue(search_result["search_status"])
        
        # Get the ID of the new message
        new_message_id = self.api.message_counter - 1
        
        # Delete the message
        delete_result = self.api.delete_voice_message(
            voice_message_id=new_message_id,
            user=self.test_user
        )
        self.assertTrue(delete_result["deletion_status"])
        
        # Verify it's gone
        show_result = self.api.show_voice_message(
            voice_message_id=new_message_id,
            user=self.test_user
        )
        self.assertFalse(show_result["message_status"])

    def test_message_lifecycle(self):
        """Test complete lifecycle of a message from sending to deletion"""
        # Initial state
        initial_message_count = len(self.api.voice_messages)
        
        # Send message
        send_result = self.api.send_voice_message(
            phone_number=self.test_recipient,
            message="Lifecycle test message",
            user=self.test_user
        )
        self.assertTrue(send_result["send_status"])
        self.assertEqual(len(self.api.voice_messages), initial_message_count + 1)
        
        # Get new message ID
        new_message_id = self.api.message_counter - 1
        
        # Show message window
        window_result = self.api.show_voice_message_window(
            phone_number=self.test_recipient,
            min_datetime="2023-01-01T00:00:00",
            max_datetime=datetime.now().isoformat(),
            pagination_order="ascending",
            page_index=0,
            page_limit=10,
            user=self.test_user
        )
        self.assertTrue(window_result["messages_status"])
        
        # Show specific message
        show_result = self.api.show_voice_message(
            voice_message_id=new_message_id,
            user=self.test_user
        )
        self.assertTrue(show_result["message_status"])
        
        # Delete message
        delete_result = self.api.delete_voice_message(
            voice_message_id=new_message_id,
            user=self.test_user
        )
        self.assertTrue(delete_result["deletion_status"])
        self.assertEqual(len(self.api.voice_messages), initial_message_count)

if __name__ == '__main__':
    unittest.main()