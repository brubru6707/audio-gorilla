import unittest
import time
from SlackApis import SlackAPI

class TestSlackAPI(unittest.TestCase):
    def setUp(self):
        self.api = SlackAPI()

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - CHAT METHODS
    # ============================================================================

    def test_chat_postMessage_basic(self):
        """Test basic chat.postMessage functionality"""
        resp = self.api.chat_postMessage("C001", "Hello, world!")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["channel"], "C001")
        self.assertEqual(resp["message"]["text"], "Hello, world!")
        self.assertIn("ts", resp)

    def test_chat_postMessage_with_blocks(self):
        """Test chat.postMessage with blocks parameter"""
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Test block"}}]
        resp = self.api.chat_postMessage("C001", "Test", blocks=blocks)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["message"]["blocks"], blocks)

    def test_chat_postMessage_with_attachments(self):
        """Test chat.postMessage with attachments parameter"""
        attachments = [{"text": "Test attachment", "color": "good"}]
        resp = self.api.chat_postMessage("C001", "Test", attachments=attachments)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["message"]["attachments"], attachments)

    def test_chat_postMessage_with_thread(self):
        """Test chat.postMessage with thread_ts parameter"""
        # First post a parent message
        parent_resp = self.api.chat_postMessage("C001", "Parent message")
        parent_ts = parent_resp["ts"]
        
        # Post reply in thread
        resp = self.api.chat_postMessage("C001", "Thread reply", thread_ts=parent_ts)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["message"]["thread_ts"], parent_ts)

    def test_chat_postMessage_with_username(self):
        """Test chat.postMessage with username parameter"""
        resp = self.api.chat_postMessage("C001", "Test", username="TestBot")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["message"]["username"], "TestBot")

    def test_chat_postMessage_with_icon_url(self):
        """Test chat.postMessage with icon_url parameter"""
        resp = self.api.chat_postMessage("C001", "Test", icon_url="https://example.com/icon.png")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["message"]["icon_url"], "https://example.com/icon.png")

    def test_chat_postMessage_with_icon_emoji(self):
        """Test chat.postMessage with icon_emoji parameter"""
        resp = self.api.chat_postMessage("C001", "Test", icon_emoji=":smile:")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["message"]["icon_emoji"], ":smile:")

    def test_chat_postEphemeral_basic(self):
        """Test basic chat.postEphemeral functionality"""
        resp = self.api.chat_postEphemeral("C001", "U001", "Ephemeral message")
        self.assertTrue(resp["ok"])
        self.assertIn("message_ts", resp)

    def test_chat_postEphemeral_with_blocks(self):
        """Test chat.postEphemeral with blocks parameter"""
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Test block"}}]
        resp = self.api.chat_postEphemeral("C001", "U001", "Test", blocks=blocks)
        self.assertTrue(resp["ok"])

    def test_chat_postEphemeral_with_attachments(self):
        """Test chat.postEphemeral with attachments parameter"""
        attachments = [{"text": "Test attachment"}]
        resp = self.api.chat_postEphemeral("C001", "U001", "Test", attachments=attachments)
        self.assertTrue(resp["ok"])

    def test_chat_update_basic(self):
        """Test basic chat.update functionality"""
        # First post a message
        post_resp = self.api.chat_postMessage("C001", "Original message")
        ts = post_resp["ts"]
        
        # Update the message
        resp = self.api.chat_update("C001", ts, "Updated message")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["message"]["text"], "Updated message")

    def test_chat_update_with_blocks(self):
        """Test chat.update with blocks parameter"""
        post_resp = self.api.chat_postMessage("C001", "Original")
        ts = post_resp["ts"]
        
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Updated block"}}]
        resp = self.api.chat_update("C001", ts, "Updated", blocks=blocks)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["message"]["blocks"], blocks)

    def test_chat_update_with_attachments(self):
        """Test chat.update with attachments parameter"""
        post_resp = self.api.chat_postMessage("C001", "Original")
        ts = post_resp["ts"]
        
        attachments = [{"text": "Updated attachment"}]
        resp = self.api.chat_update("C001", ts, "Updated", attachments=attachments)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["message"]["attachments"], attachments)

    def test_chat_update_nonexistent_message(self):
        """Test chat.update with nonexistent message"""
        resp = self.api.chat_update("C001", "9999999999.999999", "New text")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "message_not_found")

    def test_chat_delete_basic(self):
        """Test basic chat.delete functionality"""
        # First post a message
        post_resp = self.api.chat_postMessage("C001", "To be deleted")
        ts = post_resp["ts"]
        
        # Delete the message
        resp = self.api.chat_delete("C001", ts)
        self.assertTrue(resp["ok"])

    def test_chat_delete_nonexistent_message(self):
        """Test chat.delete with nonexistent message"""
        resp = self.api.chat_delete("C001", "9999999999.999999")
        self.assertTrue(resp["ok"])  # Should still return ok even if message doesn't exist

    def test_chat_scheduleMessage_basic(self):
        """Test basic chat.scheduleMessage functionality"""
        post_at = int(time.time()) + 60  # 1 minute from now
        resp = self.api.chat_scheduleMessage("C001", post_at, "Scheduled message")
        self.assertTrue(resp["ok"])
        self.assertIn("scheduled_message_id", resp)
        self.assertEqual(resp["post_at"], post_at)

    def test_chat_scheduleMessage_with_blocks(self):
        """Test chat.scheduleMessage with blocks parameter"""
        post_at = int(time.time()) + 60
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Scheduled block"}}]
        resp = self.api.chat_scheduleMessage("C001", post_at, "Test", blocks=blocks)
        self.assertTrue(resp["ok"])

    def test_chat_scheduleMessage_with_attachments(self):
        """Test chat.scheduleMessage with attachments parameter"""
        post_at = int(time.time()) + 60
        attachments = [{"text": "Scheduled attachment"}]
        resp = self.api.chat_scheduleMessage("C001", post_at, "Test", attachments=attachments)
        self.assertTrue(resp["ok"])

    def test_chat_deleteScheduledMessage_basic(self):
        """Test basic chat.deleteScheduledMessage functionality"""
        # First schedule a message
        post_at = int(time.time()) + 60
        schedule_resp = self.api.chat_scheduleMessage("C001", post_at, "To be deleted")
        scheduled_id = schedule_resp["scheduled_message_id"]
        
        # Delete the scheduled message
        resp = self.api.chat_deleteScheduledMessage("C001", scheduled_id)
        self.assertTrue(resp["ok"])

    def test_chat_deleteScheduledMessage_nonexistent(self):
        """Test chat.deleteScheduledMessage with nonexistent message"""
        resp = self.api.chat_deleteScheduledMessage("C001", "nonexistent_id")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "scheduled_message_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - CONVERSATIONS METHODS
    # ============================================================================

    def test_conversations_list_basic(self):
        """Test basic conversations.list functionality"""
        resp = self.api.conversations_list()
        self.assertTrue(resp["ok"])
        self.assertIn("channels", resp)
        self.assertIn("response_metadata", resp)

    def test_conversations_list_with_types(self):
        """Test conversations.list with types parameter"""
        resp = self.api.conversations_list(types="public_channel,private_channel")
        self.assertTrue(resp["ok"])

    def test_conversations_list_with_limit(self):
        """Test conversations.list with limit parameter"""
        resp = self.api.conversations_list(limit=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["channels"]), 5)

    def test_conversations_list_with_cursor(self):
        """Test conversations.list with cursor parameter"""
        resp = self.api.conversations_list(cursor="test_cursor")
        self.assertTrue(resp["ok"])

    def test_conversations_open_basic(self):
        """Test basic conversations.open functionality"""
        resp = self.api.conversations_open("U001")
        self.assertTrue(resp["ok"])
        self.assertIn("channel", resp)

    def test_conversations_open_multiple_users(self):
        """Test conversations.open with multiple users"""
        resp = self.api.conversations_open("U001,U002")
        self.assertTrue(resp["ok"])
        self.assertTrue(resp["channel"]["is_mpim"])

    def test_conversations_open_with_return_im(self):
        """Test conversations.open with return_im parameter"""
        resp = self.api.conversations_open("U001", return_im=True)
        self.assertTrue(resp["ok"])
        self.assertIn("im", resp)

    def test_conversations_close_basic(self):
        """Test basic conversations.close functionality"""
        # First open a conversation
        open_resp = self.api.conversations_open("U001")
        channel_id = open_resp["channel"]["id"]
        
        # Close the conversation
        resp = self.api.conversations_close(channel_id)
        self.assertTrue(resp["ok"])

    def test_conversations_close_nonexistent(self):
        """Test conversations.close with nonexistent channel"""
        resp = self.api.conversations_close("D999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "channel_not_found")

    def test_conversations_join_basic(self):
        """Test basic conversations.join functionality"""
        resp = self.api.conversations_join("C001")
        self.assertTrue(resp["ok"])
        self.assertIn("channel", resp)

    def test_conversations_join_nonexistent(self):
        """Test conversations.join with nonexistent channel"""
        resp = self.api.conversations_join("C999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "channel_not_found")

    def test_conversations_leave_basic(self):
        """Test basic conversations.leave functionality"""
        resp = self.api.conversations_leave("C001")
        self.assertTrue(resp["ok"])

    def test_conversations_leave_nonexistent(self):
        """Test conversations.leave with nonexistent channel"""
        resp = self.api.conversations_leave("C999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "channel_not_found")

    def test_conversations_info_basic(self):
        """Test basic conversations.info functionality"""
        resp = self.api.conversations_info("C001")
        self.assertTrue(resp["ok"])
        self.assertIn("channel", resp)

    def test_conversations_info_with_include_num_members(self):
        """Test conversations.info with include_num_members parameter"""
        resp = self.api.conversations_info("C001", include_num_members=True)
        self.assertTrue(resp["ok"])
        self.assertIn("num_members", resp["channel"])

    def test_conversations_info_nonexistent(self):
        """Test conversations.info with nonexistent channel"""
        resp = self.api.conversations_info("C999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "channel_not_found")

    def test_conversations_history_basic(self):
        """Test basic conversations.history functionality"""
        resp = self.api.conversations_history("C001")
        self.assertTrue(resp["ok"])
        self.assertIn("messages", resp)
        self.assertIn("has_more", resp)

    def test_conversations_history_with_limit(self):
        """Test conversations.history with limit parameter"""
        resp = self.api.conversations_history("C001", limit=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["messages"]), 5)

    def test_conversations_history_with_latest(self):
        """Test conversations.history with latest parameter"""
        resp = self.api.conversations_history("C001", latest="9999999999.999999")
        self.assertTrue(resp["ok"])

    def test_conversations_history_with_oldest(self):
        """Test conversations.history with oldest parameter"""
        resp = self.api.conversations_history("C001", oldest="0")
        self.assertTrue(resp["ok"])

    def test_conversations_history_with_inclusive(self):
        """Test conversations.history with inclusive parameter"""
        resp = self.api.conversations_history("C001", inclusive=True)
        self.assertTrue(resp["ok"])

    def test_conversations_replies_basic(self):
        """Test basic conversations.replies functionality"""
        # First post a parent message
        parent_resp = self.api.chat_postMessage("C001", "Parent message")
        parent_ts = parent_resp["ts"]
        
        # Post a reply
        self.api.chat_postMessage("C001", "Reply", thread_ts=parent_ts)
        
        # Get thread replies
        resp = self.api.conversations_replies("C001", parent_ts)
        self.assertTrue(resp["ok"])
        self.assertIn("messages", resp)

    def test_conversations_replies_with_limit(self):
        """Test conversations.replies with limit parameter"""
        parent_resp = self.api.chat_postMessage("C001", "Parent")
        parent_ts = parent_resp["ts"]
        
        resp = self.api.conversations_replies("C001", parent_ts, limit=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["messages"]), 5)

    def test_conversations_replies_with_cursor(self):
        """Test conversations.replies with cursor parameter"""
        parent_resp = self.api.chat_postMessage("C001", "Parent")
        parent_ts = parent_resp["ts"]
        
        resp = self.api.conversations_replies("C001", parent_ts, cursor="test_cursor")
        self.assertTrue(resp["ok"])

    def test_conversations_setTopic_basic(self):
        """Test basic conversations.setTopic functionality"""
        resp = self.api.conversations_setTopic("C001", "New topic")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["topic"], "New topic")

    def test_conversations_setTopic_nonexistent(self):
        """Test conversations.setTopic with nonexistent channel"""
        resp = self.api.conversations_setTopic("C999", "New topic")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "channel_not_found")

    def test_conversations_setPurpose_basic(self):
        """Test basic conversations.setPurpose functionality"""
        resp = self.api.conversations_setPurpose("C001", "New purpose")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["purpose"], "New purpose")

    def test_conversations_setPurpose_nonexistent(self):
        """Test conversations.setPurpose with nonexistent channel"""
        resp = self.api.conversations_setPurpose("C999", "New purpose")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "channel_not_found")

    def test_conversations_rename_basic(self):
        """Test basic conversations.rename functionality"""
        resp = self.api.conversations_rename("C001", "new_name")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["channel"]["name"], "new_name")

    def test_conversations_rename_nonexistent(self):
        """Test conversations.rename with nonexistent channel"""
        resp = self.api.conversations_rename("C999", "new_name")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "channel_not_found")

    def test_conversations_create_basic(self):
        """Test basic conversations.create functionality"""
        resp = self.api.conversations_create("test_channel")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["channel"]["name"], "test_channel")

    def test_conversations_create_private(self):
        """Test conversations.create with is_private parameter"""
        resp = self.api.conversations_create("private_channel", is_private=True)
        self.assertTrue(resp["ok"])
        self.assertTrue(resp["channel"]["is_private"])

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - USERS METHODS
    # ============================================================================

    def test_users_list_basic(self):
        """Test basic users.list functionality"""
        resp = self.api.users_list()
        self.assertTrue(resp["ok"])
        self.assertIn("members", resp)

    def test_users_list_with_limit(self):
        """Test users.list with limit parameter"""
        resp = self.api.users_list(limit=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["members"]), 5)

    def test_users_list_with_cursor(self):
        """Test users.list with cursor parameter"""
        resp = self.api.users_list(cursor="test_cursor")
        self.assertTrue(resp["ok"])

    def test_users_info_basic(self):
        """Test basic users.info functionality"""
        resp = self.api.users_info("U001")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["user"]["id"], "U001")

    def test_users_info_nonexistent(self):
        """Test users.info with nonexistent user"""
        resp = self.api.users_info("U999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "user_not_found")

    def test_users_lookupByEmail_basic(self):
        """Test basic users.lookupByEmail functionality"""
        resp = self.api.users_lookupByEmail("alice@example.com")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["user"]["email"], "alice@example.com")

    def test_users_lookupByEmail_nonexistent(self):
        """Test users.lookupByEmail with nonexistent email"""
        resp = self.api.users_lookupByEmail("nonexistent@example.com")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "users_not_found")

    def test_users_conversations_basic(self):
        """Test basic users.conversations functionality"""
        resp = self.api.users_conversations("U001")
        self.assertTrue(resp["ok"])
        self.assertIn("channels", resp)

    def test_users_conversations_with_types(self):
        """Test users.conversations with types parameter"""
        resp = self.api.users_conversations("U001", types="public_channel,private_channel")
        self.assertTrue(resp["ok"])

    def test_users_conversations_with_limit(self):
        """Test users.conversations with limit parameter"""
        resp = self.api.users_conversations("U001", limit=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["channels"]), 5)

    def test_users_conversations_with_cursor(self):
        """Test users.conversations with cursor parameter"""
        resp = self.api.users_conversations("U001", cursor="test_cursor")
        self.assertTrue(resp["ok"])

    def test_users_getPresence_basic(self):
        """Test basic users.getPresence functionality"""
        resp = self.api.users_getPresence("U001")
        self.assertTrue(resp["ok"])
        self.assertIn("presence", resp)

    def test_users_getPresence_nonexistent(self):
        """Test users.getPresence with nonexistent user"""
        resp = self.api.users_getPresence("U999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "user_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - SEARCH METHODS
    # ============================================================================

    def test_search_messages_basic(self):
        """Test basic search.messages functionality"""
        # First post a message to search for
        self.api.chat_postMessage("C001", "Searchable message")
        
        resp = self.api.search_messages("Searchable")
        self.assertTrue(resp["ok"])
        self.assertIn("messages", resp)

    def test_search_messages_with_count(self):
        """Test search.messages with count parameter"""
        resp = self.api.search_messages("test", count=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(resp["messages"]["paging"]["count"], 5)

    def test_search_messages_with_page(self):
        """Test search.messages with page parameter"""
        resp = self.api.search_messages("test", page=2)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["messages"]["paging"]["page"], 2)

    def test_search_messages_with_sort(self):
        """Test search.messages with sort parameter"""
        resp = self.api.search_messages("test", sort="timestamp")
        self.assertTrue(resp["ok"])

    def test_search_messages_with_sort_dir(self):
        """Test search.messages with sort_dir parameter"""
        resp = self.api.search_messages("test", sort_dir="asc")
        self.assertTrue(resp["ok"])

    def test_search_files_basic(self):
        """Test basic search.files functionality"""
        # First upload a file to search for
        self.api.files_upload(b"test content", filename="searchable_file.txt")
        
        resp = self.api.search_files("searchable")
        self.assertTrue(resp["ok"])
        self.assertIn("files", resp)

    def test_search_files_with_count(self):
        """Test search.files with count parameter"""
        resp = self.api.search_files("test", count=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(resp["files"]["paging"]["count"], 5)

    def test_search_files_with_page(self):
        """Test search.files with page parameter"""
        resp = self.api.search_files("test", page=2)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["files"]["paging"]["page"], 2)

    def test_search_all_basic(self):
        """Test basic search.all functionality"""
        resp = self.api.search_all("test")
        self.assertTrue(resp["ok"])
        self.assertIn("messages", resp)
        self.assertIn("files", resp)

    def test_search_all_with_count(self):
        """Test search.all with count parameter"""
        resp = self.api.search_all("test", count=5)
        self.assertTrue(resp["ok"])

    def test_search_all_with_page(self):
        """Test search.all with page parameter"""
        resp = self.api.search_all("test", page=2)
        self.assertTrue(resp["ok"])

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - REMINDERS METHODS
    # ============================================================================

    def test_reminders_add_basic(self):
        """Test basic reminders.add functionality"""
        when = int(time.time()) + 60
        resp = self.api.reminders_add("Test reminder", when)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["reminder"]["text"], "Test reminder")
        self.assertEqual(resp["reminder"]["time"], when)

    def test_reminders_add_with_user(self):
        """Test reminders.add with user parameter"""
        when = int(time.time()) + 60
        resp = self.api.reminders_add("Test reminder", when, user="U001")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["reminder"]["user"], "U001")

    def test_reminders_list_basic(self):
        """Test basic reminders.list functionality"""
        resp = self.api.reminders_list()
        self.assertTrue(resp["ok"])
        self.assertIn("reminders", resp)

    def test_reminders_complete_basic(self):
        """Test basic reminders.complete functionality"""
        # First add a reminder
        when = int(time.time()) + 60
        add_resp = self.api.reminders_add("Test reminder", when)
        reminder_id = add_resp["reminder"]["id"]
        
        # Complete the reminder
        resp = self.api.reminders_complete(reminder_id)
        self.assertTrue(resp["ok"])

    def test_reminders_complete_nonexistent(self):
        """Test reminders.complete with nonexistent reminder"""
        resp = self.api.reminders_complete("nonexistent_reminder")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "reminder_not_found")

    def test_reminders_delete_basic(self):
        """Test basic reminders.delete functionality"""
        # First add a reminder
        when = int(time.time()) + 60
        add_resp = self.api.reminders_add("Test reminder", when)
        reminder_id = add_resp["reminder"]["id"]
        
        # Delete the reminder
        resp = self.api.reminders_delete(reminder_id)
        self.assertTrue(resp["ok"])

    def test_reminders_delete_nonexistent(self):
        """Test reminders.delete with nonexistent reminder"""
        resp = self.api.reminders_delete("nonexistent_reminder")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "reminder_not_found")

    def test_reminders_info_basic(self):
        """Test basic reminders.info functionality"""
        # First add a reminder
        when = int(time.time()) + 60
        add_resp = self.api.reminders_add("Test reminder", when)
        reminder_id = add_resp["reminder"]["id"]
        
        # Get reminder info
        resp = self.api.reminders_info(reminder_id)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["reminder"]["id"], reminder_id)

    def test_reminders_info_nonexistent(self):
        """Test reminders.info with nonexistent reminder"""
        resp = self.api.reminders_info("nonexistent_reminder")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "reminder_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - FILES METHODS
    # ============================================================================

    def test_files_upload_basic(self):
        """Test basic files.upload functionality"""
        file_content = b"test file content"
        resp = self.api.files_upload(file_content, filename="test.txt")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["file"]["name"], "test.txt")
        self.assertEqual(resp["file"]["size"], len(file_content))

    def test_files_upload_with_channels(self):
        """Test files.upload with channels parameter"""
        file_content = b"test content"
        resp = self.api.files_upload(file_content, filename="test.txt", channels="C001")
        self.assertTrue(resp["ok"])
        self.assertIn("C001", resp["file"]["channels"])

    def test_files_upload_with_initial_comment(self):
        """Test files.upload with initial_comment parameter"""
        file_content = b"test content"
        resp = self.api.files_upload(file_content, filename="test.txt", initial_comment="Test comment")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["file"]["initial_comment"], "Test comment")

    def test_files_list_basic(self):
        """Test basic files.list functionality"""
        resp = self.api.files_list()
        self.assertTrue(resp["ok"])
        self.assertIn("files", resp)

    def test_files_list_with_user(self):
        """Test files.list with user parameter"""
        resp = self.api.files_list(user="U001")
        self.assertTrue(resp["ok"])

    def test_files_list_with_types(self):
        """Test files.list with types parameter"""
        resp = self.api.files_list(types="images")
        self.assertTrue(resp["ok"])

    def test_files_list_with_page(self):
        """Test files.list with page parameter"""
        resp = self.api.files_list(page=2)
        self.assertTrue(resp["ok"])

    def test_files_list_with_count(self):
        """Test files.list with count parameter"""
        resp = self.api.files_list(count=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["files"]), 5)

    def test_files_info_basic(self):
        """Test basic files.info functionality"""
        # First upload a file
        upload_resp = self.api.files_upload(b"test content", filename="test.txt")
        file_id = upload_resp["file"]["id"]
        
        # Get file info
        resp = self.api.files_info(file_id)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["file"]["id"], file_id)

    def test_files_info_nonexistent(self):
        """Test files.info with nonexistent file"""
        resp = self.api.files_info("F999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "file_not_found")

    def test_files_delete_basic(self):
        """Test basic files.delete functionality"""
        # First upload a file
        upload_resp = self.api.files_upload(b"test content", filename="test.txt")
        file_id = upload_resp["file"]["id"]
        
        # Delete the file
        resp = self.api.files_delete(file_id)
        self.assertTrue(resp["ok"])

    def test_files_delete_nonexistent(self):
        """Test files.delete with nonexistent file"""
        resp = self.api.files_delete("F999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "file_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - REACTIONS METHODS
    # ============================================================================

    def test_reactions_add_basic(self):
        """Test basic reactions.add functionality"""
        # First post a message
        post_resp = self.api.chat_postMessage("C001", "React to me")
        ts = post_resp["ts"]
        
        # Add reaction
        resp = self.api.reactions_add("smile", "C001", ts)
        self.assertTrue(resp["ok"])

    def test_reactions_remove_basic(self):
        """Test basic reactions.remove functionality"""
        # First post a message and add reaction
        post_resp = self.api.chat_postMessage("C001", "React to me")
        ts = post_resp["ts"]
        self.api.reactions_add("smile", "C001", ts)
        
        # Remove reaction
        resp = self.api.reactions_remove("smile", "C001", ts)
        self.assertTrue(resp["ok"])

    def test_reactions_get_basic(self):
        """Test basic reactions.get functionality"""
        # First post a message and add reaction
        post_resp = self.api.chat_postMessage("C001", "React to me")
        ts = post_resp["ts"]
        self.api.reactions_add("smile", "C001", ts)
        
        # Get reactions
        resp = self.api.reactions_get("C001", ts)
        self.assertTrue(resp["ok"])
        self.assertIn("message", resp)

    def test_reactions_list_basic(self):
        """Test basic reactions.list functionality"""
        resp = self.api.reactions_list()
        self.assertTrue(resp["ok"])
        self.assertIn("items", resp)

    def test_reactions_list_with_user(self):
        """Test reactions.list with user parameter"""
        resp = self.api.reactions_list(user="U001")
        self.assertTrue(resp["ok"])

    def test_reactions_list_with_count(self):
        """Test reactions.list with count parameter"""
        resp = self.api.reactions_list(count=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["items"]), 5)

    def test_reactions_list_with_page(self):
        """Test reactions.list with page parameter"""
        resp = self.api.reactions_list(page=2)
        self.assertTrue(resp["ok"])

    def test_reactions_list_with_full(self):
        """Test reactions.list with full parameter"""
        resp = self.api.reactions_list(full=True)
        self.assertTrue(resp["ok"])

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - PINS METHODS
    # ============================================================================

    def test_pins_add_basic(self):
        """Test basic pins.add functionality"""
        # First post a message
        post_resp = self.api.chat_postMessage("C001", "Pin me")
        ts = post_resp["ts"]
        
        # Pin the message
        resp = self.api.pins_add("C001", ts)
        self.assertTrue(resp["ok"])

    def test_pins_remove_basic(self):
        """Test basic pins.remove functionality"""
        # First post a message and pin it
        post_resp = self.api.chat_postMessage("C001", "Pin me")
        ts = post_resp["ts"]
        self.api.pins_add("C001", ts)
        
        # Remove the pin
        resp = self.api.pins_remove("C001", ts)
        self.assertTrue(resp["ok"])

    def test_pins_remove_nonexistent(self):
        """Test pins.remove with nonexistent pinned item"""
        resp = self.api.pins_remove("C001", "9999999999.999999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "pinned_item_not_found")

    def test_pins_list_basic(self):
        """Test basic pins.list functionality"""
        # First post a message and pin it
        post_resp = self.api.chat_postMessage("C001", "Pin me")
        ts = post_resp["ts"]
        self.api.pins_add("C001", ts)
        
        # List pins
        resp = self.api.pins_list("C001")
        self.assertTrue(resp["ok"])
        self.assertIn("items", resp)

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - DND METHODS
    # ============================================================================

    def test_dnd_setSnooze_basic(self):
        """Test basic dnd.setSnooze functionality"""
        resp = self.api.dnd_setSnooze(30)
        self.assertTrue(resp["ok"])
        self.assertTrue(resp["snooze_enabled"])

    def test_dnd_endSnooze_basic(self):
        """Test basic dnd.endSnooze functionality"""
        resp = self.api.dnd_endSnooze()
        self.assertTrue(resp["ok"])

    def test_dnd_endDnd_basic(self):
        """Test basic dnd.endDnd functionality"""
        resp = self.api.dnd_endDnd()
        self.assertTrue(resp["ok"])

    def test_dnd_info_basic(self):
        """Test basic dnd.info functionality"""
        resp = self.api.dnd_info()
        self.assertTrue(resp["ok"])
        self.assertIn("dnd_enabled", resp)

    def test_dnd_info_with_user(self):
        """Test dnd.info with user parameter"""
        resp = self.api.dnd_info("U001")
        self.assertTrue(resp["ok"])
        self.assertIn("dnd_enabled", resp)

    def test_dnd_info_nonexistent_user(self):
        """Test dnd.info with nonexistent user"""
        resp = self.api.dnd_info("U999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "user_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - TEAM METHODS
    # ============================================================================

    def test_team_info_basic(self):
        """Test basic team.info functionality"""
        resp = self.api.team_info()
        self.assertTrue(resp["ok"])
        self.assertIn("team", resp)

if __name__ == "__main__":
    unittest.main() 