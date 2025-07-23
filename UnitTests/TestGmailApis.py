import unittest
from copy import deepcopy
from GmailApis import GmailApis, DEFAULT_STATE

class TestGmailApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh GmailApis instance for each test."""
        self.gmail_api = GmailApis()
        self.gmail_api.state = deepcopy(DEFAULT_STATE)
        self.user_id = "user1@example.com"

    def test_send_message_success(self):
        """Test sending a new message successfully."""
        initial_message_count = len(self.gmail_api._get_user_messages_data(self.user_id))
        initial_thread_count = len(self.gmail_api._get_user_threads_data(self.user_id))

        message_body = {
            "to": "recipient@example.com",
            "subject": "Test Subject",
            "body": {"raw": "Hello, this is a test message."}
        }
        sent_message = self.gmail_api.send_message(message_body, user_id=self.user_id)

        self.assertIsNotNone(sent_message)
        self.assertIn("id", sent_message)
        self.assertIn("threadId", sent_message)
        self.assertEqual(len(self.gmail_api._get_user_messages_data(self.user_id)), initial_message_count + 1)

        threads = self.gmail_api._get_user_threads_data(self.user_id)
        self.assertIn(sent_message["threadId"], threads)
        self.assertIn(sent_message, threads[sent_message["threadId"]]["messages"])

    def test_list_messages_no_filters(self):
        """Test listing messages without any filters."""
        self.gmail_api.send_message({
            "to": "test@example.com",
            "subject": "Another Test",
            "body": {"raw": "This is another message."}
        }, user_id=self.user_id)

        messages_list = self.gmail_api.list_messages(user_id=self.user_id)
        self.assertIsNotNone(messages_list)
        self.assertIn("messages", messages_list)
        self.assertGreater(len(messages_list["messages"]), 0)
        self.assertIn("resultSizeEstimate", messages_list)

    def test_list_messages_with_label_filter(self):
        """Test listing messages with a label filter."""
        label_name = "MyCustomLabel"
        created_label = self.gmail_api.create_label({"name": label_name}, user_id=self.user_id)
        self.assertIsNotNone(created_label)

        message_body = {
            "to": "labeled@example.com",
            "subject": "Message with Label",
            "body": {"raw": "This message has a specific label."},
            "labelIds": ["INBOX", created_label["id"]]
        }
        sent_message = self.gmail_api.send_message(message_body, user_id=self.user_id)
        self.assertIsNotNone(sent_message)

        messages_list = self.gmail_api.list_messages(user_id=self.user_id, label_ids=[created_label["id"]])
        self.assertIsNotNone(messages_list)
        self.assertIn("messages", messages_list)
        self.assertGreater(len(messages_list["messages"]), 0)
        self.assertTrue(any(created_label["id"] in msg.get("labelIds", []) for msg in messages_list["messages"]))

    def test_list_messages_with_query_filter(self):
        """Test listing messages with a search query filter."""
        message_body_1 = {
            "to": "query1@example.com",
            "subject": "Important Meeting",
            "body": {"raw": "Please attend the meeting tomorrow."}
        }
        self.gmail_api.send_message(message_body_1, user_id=self.user_id)

        message_body_2 = {
            "to": "query2@example.com",
            "subject": "Project Update",
            "body": {"raw": "The project is progressing well."}
        }
        self.gmail_api.send_message(message_body_2, user_id=self.user_id)

        messages_list = self.gmail_api.list_messages(user_id=self.user_id, q="meeting")
        self.assertIsNotNone(messages_list)
        self.assertIn("messages", messages_list)
        self.assertEqual(len(messages_list["messages"]), 1)
        self.assertIn("Meeting", messages_list["messages"][0]["subject"])

    def test_create_draft_success(self):
        """Test creating a new draft successfully."""
        initial_draft_count = len(self.gmail_api._get_user_drafts_data(self.user_id))
        draft_body = {
            "to": "draft_recipient@example.com",
            "subject": "Draft Subject",
            "body": "This is a draft message."
        }
        created_draft = self.gmail_api.create_draft(draft_body, user_id=self.user_id)

        self.assertIsNotNone(created_draft)
        self.assertIn("id", created_draft)
        self.assertEqual(created_draft["message"]["subject"], "Draft Subject")
        self.assertEqual(len(self.gmail_api._get_user_drafts_data(self.user_id)), initial_draft_count + 1)

    def test_get_draft_success(self):
        """Test retrieving an existing draft."""
        draft_body = {
            "to": "get_draft@example.com",
            "subject": "Draft to Get",
            "body": "Retrieve this draft."
        }
        created_draft = self.gmail_api.create_draft(draft_body, user_id=self.user_id)
        self.assertIsNotNone(created_draft)

        retrieved_draft = self.gmail_api.get_draft(created_draft["id"], user_id=self.user_id)
        self.assertIsNotNone(retrieved_draft)
        self.assertEqual(retrieved_draft["id"], created_draft["id"])
        self.assertEqual(retrieved_draft["message"]["subject"], "Draft to Get")

    def test_get_draft_not_found(self):
        """Test retrieving a non-existent draft."""
        retrieved_draft = self.gmail_api.get_draft("non_existent_draft", user_id=self.user_id)
        self.assertIsNone(retrieved_draft)

    def test_delete_draft_success(self):
        """Test deleting an existing draft."""
        draft_body = {
            "to": "delete_draft@example.com",
            "subject": "Draft to Delete",
            "body": "Delete this draft."
        }
        created_draft = self.gmail_api.create_draft(draft_body, user_id=self.user_id)
        self.assertIsNotNone(created_draft)
        initial_draft_count = len(self.gmail_api._get_user_drafts_data(self.user_id))

        self.gmail_api.delete_draft(created_draft["id"], user_id=self.user_id)
        self.assertEqual(len(self.gmail_api._get_user_drafts_data(self.user_id)), initial_draft_count - 1)
        self.assertIsNone(self.gmail_api.get_draft(created_draft["id"], user_id=self.user_id))

    def test_delete_draft_not_found(self):
        """Test deleting a non-existent draft."""
        result = self.gmail_api.delete_draft("non_existent_draft", user_id=self.user_id)
        self.assertIsNone(result)

    def test_create_label_success(self):
        """Test creating a new label successfully."""
        initial_label_count = len(self.gmail_api._get_user_labels_data(self.user_id))
        label_body = {
            "name": "NewLabel",
            "messageListVisibility": "show",
            "labelListVisibility": "show"
        }
        created_label = self.gmail_api.create_label(label_body, user_id=self.user_id)

        self.assertIsNotNone(created_label)
        self.assertIn("id", created_label)
        self.assertEqual(created_label["name"], "NewLabel")
        self.assertEqual(len(self.gmail_api._get_user_labels_data(self.user_id)), initial_label_count + 1)

    def test_list_labels_success(self):
        """Test listing all labels."""
        self.gmail_api.create_label({"name": "AnotherLabel"}, user_id=self.user_id)
        labels_list = self.gmail_api.list_labels(user_id=self.user_id)

        self.assertIsNotNone(labels_list)
        self.assertIn("labels", labels_list)
        self.assertGreater(len(labels_list["labels"]), 0)

    def test_delete_label_success(self):
        """Test deleting an existing label."""
        label_body = {
            "name": "LabelToDelete",
            "messageListVisibility": "show",
            "labelListVisibility": "show"
        }
        created_label = self.gmail_api.create_label(label_body, user_id=self.user_id)
        self.assertIsNotNone(created_label)
        initial_label_count = len(self.gmail_api._get_user_labels_data(self.user_id))

        self.gmail_api.delete_label(created_label["id"], user_id=self.user_id)
        self.assertEqual(len(self.gmail_api._get_user_labels_data(self.user_id)), initial_label_count - 1)
        self.assertIsNone(self.gmail_api.get_label(created_label["id"], user_id=self.user_id))

    def test_delete_label_not_found(self):
        """Test deleting a non-existent label."""
        result = self.gmail_api.delete_label("non_existent_label", user_id=self.user_id)
        self.assertIsNone(result)

    # Combined Functionality Tests
    def test_send_list_delete_message_flow(self):
        """Test the flow of sending a message, listing it, and then deleting it."""
        initial_message_count = len(self.gmail_api._get_user_messages_data(self.user_id))

        message_body = {
            "to": "flow_test@example.com",
            "subject": "Flow Test Message",
            "body": {"raw": "This message is part of a flow test."}
        }
        sent_message = self.gmail_api.send_message(message_body, user_id=self.user_id)
        self.assertIsNotNone(sent_message)
        self.assertEqual(len(self.gmail_api._get_user_messages_data(self.user_id)), initial_message_count + 1)

        listed_messages = self.gmail_api.list_messages(user_id=self.user_id, q="Flow Test Message")
        self.assertIsNotNone(listed_messages)
        self.assertIn("messages", listed_messages)
        self.assertEqual(len(listed_messages["messages"]), 1)
        self.assertEqual(listed_messages["messages"][0]["id"], sent_message["id"])

        self.gmail_api.batch_delete_messages([sent_message["id"]], user_id=self.user_id)
        self.assertEqual(len(self.gmail_api._get_user_messages_data(self.user_id)), initial_message_count)

        deleted_message = self.gmail_api.get_message(sent_message["id"], user_id=self.user_id)
        self.assertIsNone(deleted_message)

    def test_create_get_delete_draft_flow(self):
        """Test the flow of creating a draft, getting it, and then deleting it."""
        initial_draft_count = len(self.gmail_api._get_user_drafts_data(self.user_id))

        draft_body = {
            "to": "draft_flow@example.com",
            "subject": "Draft Flow Test",
            "body": "This draft is for a flow test."
        }
        created_draft = self.gmail_api.create_draft(draft_body, user_id=self.user_id)
        self.assertIsNotNone(created_draft)
        self.assertEqual(len(self.gmail_api._get_user_drafts_data(self.user_id)), initial_draft_count + 1)

        retrieved_draft = self.gmail_api.get_draft(created_draft["id"], user_id=self.user_id)
        self.assertIsNotNone(retrieved_draft)
        self.assertEqual(retrieved_draft["id"], created_draft["id"])
        self.assertEqual(retrieved_draft["message"]["subject"], "Draft Flow Test")

        self.gmail_api.delete_draft(created_draft["id"], user_id=self.user_id)
        self.assertEqual(len(self.gmail_api._get_user_drafts_data(self.user_id)), initial_draft_count)

        deleted_draft = self.gmail_api.get_draft(created_draft["id"], user_id=self.user_id)
        self.assertIsNone(deleted_draft)

    def test_create_list_delete_label_flow(self):
        """Test the flow of creating a label, listing it, and then deleting it."""
        initial_label_count = len(self.gmail_api._get_user_labels_data(self.user_id))

        label_body = {
            "name": "FlowTestLabel",
            "messageListVisibility": "show",
            "labelListVisibility": "show"
        }
        created_label = self.gmail_api.create_label(label_body, user_id=self.user_id)
        self.assertIsNotNone(created_label)
        self.assertEqual(len(self.gmail_api._get_user_labels_data(self.user_id)), initial_label_count + 1)

        listed_labels = self.gmail_api.list_labels(user_id=self.user_id)
        self.assertIsNotNone(listed_labels)
        self.assertIn("labels", listed_labels)
        self.assertTrue(any(label["id"] == created_label["id"] for label in listed_labels["labels"]))

        self.gmail_api.delete_label(created_label["id"], user_id=self.user_id)
        self.assertEqual(len(self.gmail_api._get_user_labels_data(self.user_id)), initial_label_count)

        deleted_label = self.gmail_api.get_label(created_label["id"], user_id=self.user_id)
        self.assertIsNone(deleted_label)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)