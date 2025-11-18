import unittest
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import API and helper
from GmailApis import GmailApis
from UnitTests.test_data_helper import BackendDataLoader

class TestGmailApis(unittest.TestCase):
    """
    Unit tests for the GmailApis class, covering multi-user functionality.
    """

    # Load real data from backend
    real_data = BackendDataLoader.get_gmail_data()
    
    # Extract real user data
    users = list(real_data.get("users", {}).values())
    user_data = users[0] if users else {}
    REAL_USER_EMAIL = user_data.get("email", "real_user@gmail.com")
    REAL_USER_ID = next(iter(real_data.get("users", {})), "user1")
    
    # Extract gmail data
    gmail_data = user_data.get("gmail_data", {})
    
    # Extract real message data
    messages = list(gmail_data.get("messages", {}).values())
    message_data = messages[0] if messages else {}
    REAL_MESSAGE_ID = message_data.get("id", "msg1")
    REAL_SUBJECT = message_data.get("payload", {}).get("headers", [{}]*3)[2].get("value", "Real Email Subject")
    REAL_SENDER = user_data.get("email", "sender@example.com")
    REAL_RECIPIENT = "recipient@example.com"
    
    # Extract real label data
    labels_keys = list(gmail_data.get("labels", {}).keys())
    label_data = gmail_data.get("labels", {}).get(labels_keys[0], {}) if labels_keys else {}
    REAL_LABEL_ID = labels_keys[0] if labels_keys else "label1"
    REAL_LABEL_NAME = label_data.get("name", "Real Label")
    
    # Extract real draft data
    drafts_keys = list(gmail_data.get("drafts", {}).keys())
    draft_data = gmail_data.get("drafts", {}).get(drafts_keys[0], {}) if drafts_keys else {}
    REAL_DRAFT_ID = drafts_keys[0] if drafts_keys else "draft1"
    
    # Extract real thread data
    threads_keys = list(gmail_data.get("threads", {}).keys())
    REAL_THREAD_ID = threads_keys[0] if threads_keys else "thread1"
    
    def setUp(self):
        """Set up the API instance using real data."""
        self.gmail_api = GmailApis()

    # --- Profile Tests ---
    def test_get_profile_success(self):
        """Test getting user profile successfully."""
        result = self.gmail_api.get_profile(self.REAL_USER_EMAIL)
        self.assertIsNotNone(result)
        if result:
            self.assertIn("emailAddress", result)

    def test_get_profile_user_not_found(self):
        """Test getting profile for non-existent user."""
        result = self.gmail_api.get_profile("nonexistent@example.com")
        self.assertIsNone(result)

    # --- Message Tests ---
    def test_list_messages_success(self):
        """Test listing messages successfully."""
        result = self.gmail_api.list_messages(self.REAL_USER_EMAIL)
        self.assertIn("messages", result)
        self.assertIsInstance(result["messages"], list)

    def test_list_messages_with_query(self):
        """Test listing messages with query."""
        result = self.gmail_api.list_messages(self.REAL_USER_EMAIL, q="subject:test")
        self.assertIn("messages", result)
        self.assertIsInstance(result["messages"], list)

    def test_list_messages_with_label_ids(self):
        """Test listing messages with label IDs."""
        result = self.gmail_api.list_messages(self.REAL_USER_EMAIL, label_ids=["INBOX"])
        self.assertIn("messages", result)
        self.assertIsInstance(result["messages"], list)

    def test_get_message_success(self):
        """Test getting message successfully."""
        result = self.gmail_api.get_message(self.REAL_USER_EMAIL, self.REAL_MESSAGE_ID)
        self.assertIsNotNone(result)
        if result:
            self.assertIn("id", result)
            self.assertIn("threadId", result)

    def test_get_message_not_found(self):
        """Test getting non-existent message."""
        result = self.gmail_api.get_message(self.REAL_USER_EMAIL, "nonexistent_msg")
        self.assertIsNone(result)

    def test_send_message_success(self):
        """Test sending message successfully."""
        message = {
            "to": self.REAL_RECIPIENT,
            "subject": "Test Subject", 
            "body": "Test message body"
        }
        result = self.gmail_api.send_message(self.REAL_USER_EMAIL, message)
        self.assertIn("id", result)
        self.assertNotIn("error", result)

    def test_send_message_with_thread_id(self):
        """Test sending message with thread ID."""
        message = {
            "to": self.REAL_RECIPIENT,
            "subject": "Re: Test Subject",
            "body": "Reply message body",
            "threadId": "test_thread_id"
        }
        result = self.gmail_api.send_message(self.REAL_USER_EMAIL, message)
        self.assertIn("id", result)
        self.assertNotIn("error", result)

    def test_send_message_user_not_found(self):
        """Test sending message for non-existent user."""
        message = {
            "to": self.REAL_RECIPIENT,
            "subject": "Test Subject",
            "body": "Test message body"
        }
        result = self.gmail_api.send_message("nonexistent@example.com", message)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "User not found.")

    def test_delete_message_success(self):
        """Test deleting message successfully."""
        # First send a message to delete
        message = {
            "to": self.REAL_RECIPIENT,
            "subject": "Test Delete Subject",
            "body": "Test delete body"
        }
        send_result = self.gmail_api.send_message(self.REAL_USER_EMAIL, message)
        message_id = send_result.get("id")
        
        if message_id:
            result = self.gmail_api.delete_message(self.REAL_USER_EMAIL, message_id)
            self.assertTrue(result.get("success", False))

    def test_delete_message_not_found(self):
        """Test deleting non-existent message."""
        result = self.gmail_api.delete_message(self.REAL_USER_EMAIL, "nonexistent_msg")
        self.assertIn("success", result)
        self.assertFalse(result["success"])

    # --- Draft Tests ---
    def test_list_drafts_success(self):
        """Test listing drafts successfully."""
        result = self.gmail_api.list_drafts(self.REAL_USER_EMAIL)
        self.assertIn("drafts", result)
        self.assertIsInstance(result["drafts"], list)

    def test_get_draft_success(self):
        """Test getting draft successfully."""
        if not self.drafts_keys:
            self.skipTest("No drafts available in test data")
        result = self.gmail_api.get_draft(self.REAL_USER_EMAIL, self.REAL_DRAFT_ID)
        self.assertIsNotNone(result)
        if result:
            self.assertIn("id", result)

    def test_get_draft_not_found(self):
        """Test getting non-existent draft."""
        result = self.gmail_api.get_draft(self.REAL_USER_EMAIL, "nonexistent_draft")
        self.assertIsNone(result)

    def test_create_draft_success(self):
        """Test creating draft successfully."""
        draft = {
            "message": {
                "to": self.REAL_RECIPIENT,
                "subject": "Draft Subject",
                "body": "Draft message body"
            }
        }
        result = self.gmail_api.create_draft(self.REAL_USER_EMAIL, draft)
        self.assertIn("id", result)
        self.assertNotIn("error", result)

    def test_update_draft_success(self):
        """Test updating draft successfully."""
        # First create a draft
        draft = {
            "message": {
                "to": self.REAL_RECIPIENT,
                "subject": "Original Draft Subject",
                "body": "Original draft body"
            }
        }
        create_result = self.gmail_api.create_draft(self.REAL_USER_EMAIL, draft)
        draft_id = create_result.get("id")
        
        if draft_id:
            updated_draft = {
                "message": {
                    "to": self.REAL_RECIPIENT,
                    "subject": "Updated Draft Subject",
                    "body": "Updated draft body"
                }
            }
            result = self.gmail_api.update_draft(self.REAL_USER_EMAIL, draft_id, updated_draft)
            self.assertIn("id", result)
            self.assertNotIn("error", result)

    def test_delete_draft_success(self):
        """Test deleting draft successfully."""
        # First create a draft
        draft = {
            "message": {
                "to": self.REAL_RECIPIENT,
                "subject": "Delete Draft Subject",
                "body": "Delete draft body"
            }
        }
        create_result = self.gmail_api.create_draft(self.REAL_USER_EMAIL, draft)
        draft_id = create_result.get("id")
        
        if draft_id:
            result = self.gmail_api.delete_draft(self.REAL_USER_EMAIL, draft_id)
            self.assertTrue(result.get("success", False))

    def test_send_draft_success(self):
        """Test sending draft successfully."""
        # First create a draft
        draft = {
            "message": {
                "to": self.REAL_RECIPIENT,
                "subject": "Send Draft Subject",
                "body": "Send draft body"
            }
        }
        create_result = self.gmail_api.create_draft(self.REAL_USER_EMAIL, draft)
        draft_id = create_result.get("id")
        
        if draft_id:
            result = self.gmail_api.send_draft(self.REAL_USER_EMAIL, draft_id)
            self.assertIn("id", result)
            self.assertNotIn("error", result)

    # --- Label Tests ---
    def test_list_labels_success(self):
        """Test listing labels successfully."""
        result = self.gmail_api.list_labels(self.REAL_USER_EMAIL)
        self.assertIn("labels", result)
        self.assertIsInstance(result["labels"], list)

    def test_get_label_success(self):
        """Test getting label successfully."""
        result = self.gmail_api.get_label(self.REAL_USER_EMAIL, self.REAL_LABEL_ID)
        self.assertIsNotNone(result)
        if result:
            self.assertIn("id", result)
            self.assertIn("name", result)

    def test_get_label_not_found(self):
        """Test getting non-existent label."""
        result = self.gmail_api.get_label(self.REAL_USER_EMAIL, "nonexistent_label")
        self.assertIsNone(result)

    def test_create_label_success(self):
        """Test creating label successfully."""
        result = self.gmail_api.create_label(self.REAL_USER_EMAIL, "Test Label")
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "Test Label")

    def test_update_label_success(self):
        """Test updating label successfully."""
        # First create a label
        create_result = self.gmail_api.create_label(self.REAL_USER_EMAIL, "Original Label")
        label_id = create_result.get("id")
        
        if label_id:
            result = self.gmail_api.update_label(self.REAL_USER_EMAIL, label_id, "Updated Label")
            self.assertIn("id", result)
            self.assertIn("name", result)
            self.assertEqual(result["name"], "Updated Label")

    def test_delete_label_success(self):
        """Test deleting label successfully."""
        # First create a label
        create_result = self.gmail_api.create_label(self.REAL_USER_EMAIL, "Delete Label")
        label_id = create_result.get("id")
        
        if label_id:
            result = self.gmail_api.delete_label(self.REAL_USER_EMAIL, label_id)
            self.assertTrue(result.get("success", False))

    # --- Message Modification Tests ---
    def test_modify_message_success(self):
        """Test modifying message successfully."""
        result = self.gmail_api.modify_message(
            self.REAL_USER_EMAIL,
            self.REAL_MESSAGE_ID,
            {"addLabelIds": ["IMPORTANT"], "removeLabelIds": ["UNREAD"]}
        )
        self.assertIn("id", result)
        self.assertNotIn("error", result)

    # --- Thread Tests ---
    def test_get_thread_success(self):
        """Test getting thread successfully."""
        result = self.gmail_api.get_thread(self.REAL_USER_EMAIL, self.REAL_THREAD_ID)
        self.assertIsNotNone(result)
        if result:
            self.assertIn("id", result)
            self.assertIn("messages", result)

    def test_modify_thread_success(self):
        """Test modifying thread successfully."""
        result = self.gmail_api.modify_thread(
            self.REAL_USER_EMAIL,
            self.REAL_THREAD_ID,
            {"addLabelIds": ["IMPORTANT"], "removeLabelIds": ["UNREAD"]}
        )
        self.assertIn("id", result)
        self.assertNotIn("error", result)

    # --- Error Handling Tests ---
    def test_user_not_found_errors(self):
        """Test various operations with non-existent user."""
        nonexistent_user = "nonexistent@example.com"
        
        # Test send message
        message = {
            "to": "to@example.com",
            "subject": "Subject",
            "body": "Body"
        }
        result = self.gmail_api.send_message(nonexistent_user, message)
        self.assertIn("error", result)
        
        # Test create label
        result = self.gmail_api.create_label(nonexistent_user, "Test Label")
        self.assertIn("error", result)
        
        # Test list labels
        result = self.gmail_api.list_labels(nonexistent_user)
        self.assertIn("labels", result)
        self.assertEqual(result["labels"], [])

    # --- Data Reset Tests ---
    def test_reset_data_success(self):
        """Test resetting data successfully."""
        result = self.gmail_api.reset_data()
        self.assertTrue(result.get("reset_status", False))

if __name__ == "__main__":
    unittest.main()

