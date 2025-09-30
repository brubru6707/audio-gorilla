import unittest
from copy import deepcopy
from GmailApis import GmailApis, DEFAULT_STATE

class TestGmailApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh GmailApis instance for each test."""
        self.gmail_api = GmailApis()
        self.gmail_api.state = deepcopy(DEFAULT_STATE)
        self.user_id = "user1@example.com"
        self.user2_id = "user2@example.com"

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

        listed_messages = self.gmail_api.list_messages(user_id=self.user_id, q="This message is part of a flow test.")
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

    # --- Comprehensive Test Coverage for All GmailApis Methods ---

    def test_get_profile_success(self):
        """Test getting user profile successfully."""
        profile = self.gmail_api.get_profile(self.user_id)
        self.assertIsNotNone(profile)
        self.assertIn("emailAddress", profile)
        self.assertIn("messagesTotal", profile)
        self.assertIn("threadsTotal", profile)

    def test_get_profile_invalid_user(self):
        """Test getting profile for non-existent user."""
        profile = self.gmail_api.get_profile("nonexistent@example.com")
        self.assertIsNone(profile)

    def test_get_message_success(self):
        """Test getting a specific message successfully."""
        # Send a message first
        message_body = {
            "to": "get_message_test@example.com",
            "subject": "Get Message Test",
            "body": {"raw": "Testing message retrieval."}
        }
        sent_message = self.gmail_api.send_message(message_body, user_id=self.user_id)
        
        # Get the message
        retrieved_message = self.gmail_api.get_message(sent_message["id"], user_id=self.user_id)
        self.assertIsNotNone(retrieved_message)
        self.assertEqual(retrieved_message["id"], sent_message["id"])
        self.assertIn("payload", retrieved_message)

    def test_get_message_with_format(self):
        """Test getting message with specific format."""
        # Send a message first
        message_body = {
            "to": "format_test@example.com",
            "subject": "Format Test",
            "body": {"raw": "Testing message format retrieval."}
        }
        sent_message = self.gmail_api.send_message(message_body, user_id=self.user_id)
        
        # Get message with minimal format
        retrieved_message = self.gmail_api.get_message(
            sent_message["id"], 
            user_id=self.user_id, 
            format="minimal"
        )
        self.assertIsNotNone(retrieved_message)
        self.assertEqual(retrieved_message["id"], sent_message["id"])

    def test_get_message_not_found(self):
        """Test getting non-existent message."""
        retrieved_message = self.gmail_api.get_message("invalid_message_id", user_id=self.user_id)
        self.assertIsNone(retrieved_message)

    def test_delete_message_success(self):
        """Test deleting a message successfully."""
        # Send a message first
        message_body = {
            "to": "delete_test@example.com",
            "subject": "Delete Test",
            "body": {"raw": "This message will be deleted."}
        }
        sent_message = self.gmail_api.send_message(message_body, user_id=self.user_id)
        
        # Delete the message
        result = self.gmail_api.delete_message(self.user_id, sent_message["id"])
        self.assertTrue(result["success"])
        
        # Verify message is deleted
        deleted_message = self.gmail_api.get_message(sent_message["id"], user_id=self.user_id)
        self.assertIsNone(deleted_message)

    def test_delete_message_not_found(self):
        """Test deleting non-existent message."""
        result = self.gmail_api.delete_message(self.user_id, "invalid_message_id")
        self.assertFalse(result["success"])

    def test_list_drafts_success(self):
        """Test listing drafts successfully."""
        # Create some drafts
        draft1 = self.gmail_api.create_draft({
            "to": "draft1@example.com",
            "subject": "Draft 1",
            "body": "First draft"
        }, user_id=self.user_id)
        
        draft2 = self.gmail_api.create_draft({
            "to": "draft2@example.com", 
            "subject": "Draft 2",
            "body": "Second draft"
        }, user_id=self.user_id)
        
        # List drafts
        drafts_list = self.gmail_api.list_drafts(user_id=self.user_id)
        self.assertIsNotNone(drafts_list)
        self.assertIn("drafts", drafts_list)
        self.assertGreaterEqual(len(drafts_list["drafts"]), 2)

    def test_list_drafts_with_max_results(self):
        """Test listing drafts with max results limit."""
        # Create multiple drafts
        for i in range(5):
            self.gmail_api.create_draft({
                "to": f"draft{i}@example.com",
                "subject": f"Draft {i}",
                "body": f"Draft content {i}"
            }, user_id=self.user_id)
        
        # List with max results
        drafts_list = self.gmail_api.list_drafts(user_id=self.user_id, max_results=3)
        self.assertIsNotNone(drafts_list)
        self.assertIn("drafts", drafts_list)
        self.assertLessEqual(len(drafts_list["drafts"]), 3)

    def test_update_draft_success(self):
        """Test updating a draft successfully."""
        # Create a draft
        original_draft = self.gmail_api.create_draft({
            "to": "update_test@example.com",
            "subject": "Original Subject",
            "body": "Original body"
        }, user_id=self.user_id)
        
        # Update the draft
        updated_draft_body = {
            "to": "updated_test@example.com",
            "subject": "Updated Subject", 
            "body": "Updated body content"
        }
        updated_draft = self.gmail_api.update_draft(
            original_draft["id"],
            updated_draft_body,
            user_id=self.user_id
        )
        
        self.assertIsNotNone(updated_draft)
        self.assertEqual(updated_draft["id"], original_draft["id"])
        self.assertEqual(updated_draft["message"]["subject"], "Updated Subject")

    def test_update_draft_not_found(self):
        """Test updating non-existent draft."""
        updated_draft = self.gmail_api.update_draft(
            "invalid_draft_id",
            {"to": "test@example.com", "subject": "Test", "body": "Test"},
            user_id=self.user_id
        )
        self.assertIsNone(updated_draft)

    def test_send_draft_success(self):
        """Test sending a draft successfully."""
        # Create a draft
        draft = self.gmail_api.create_draft({
            "to": "send_draft_test@example.com",
            "subject": "Draft to Send",
            "body": "This draft will be sent."
        }, user_id=self.user_id)
        
        # Send the draft
        result = self.gmail_api.send_draft(self.user_id, draft["id"])
        self.assertIn("message", result)
        self.assertIn("id", result["message"])
        
        # Verify draft is no longer in drafts
        sent_draft = self.gmail_api.get_draft(draft["id"], user_id=self.user_id)
        self.assertIsNone(sent_draft)

    def test_send_draft_not_found(self):
        """Test sending non-existent draft."""
        result = self.gmail_api.send_draft(self.user_id, "invalid_draft_id")
        self.assertIn("error", result)

    def test_get_label_success(self):
        """Test getting a specific label successfully."""
        # Create a label first
        label = self.gmail_api.create_label({
            "name": "Test Get Label",
            "messageListVisibility": "show"
        }, user_id=self.user_id)
        
        # Get the label
        retrieved_label = self.gmail_api.get_label(label["id"], user_id=self.user_id)
        self.assertIsNotNone(retrieved_label)
        self.assertEqual(retrieved_label["id"], label["id"])
        self.assertEqual(retrieved_label["name"], "Test Get Label")

    def test_get_label_not_found(self):
        """Test getting non-existent label."""
        retrieved_label = self.gmail_api.get_label("invalid_label_id", user_id=self.user_id)
        self.assertIsNone(retrieved_label)

    def test_update_label_success(self):
        """Test updating a label successfully."""
        # Create a label first
        label = self.gmail_api.create_label({
            "name": "Original Label Name",
            "messageListVisibility": "show"
        }, user_id=self.user_id)
        
        # Update the label
        updated_label = self.gmail_api.update_label(
            self.user_id,
            label["id"],
            "Updated Label Name"
        )
        self.assertIn("label", updated_label)
        self.assertEqual(updated_label["label"]["name"], "Updated Label Name")

    def test_update_label_not_found(self):
        """Test updating non-existent label."""
        updated_label = self.gmail_api.update_label(
            self.user_id,
            "invalid_label_id",
            "New Name"
        )
        self.assertIn("error", updated_label)

    def test_modify_message_success(self):
        """Test modifying message labels successfully."""
        # Create a label first
        label = self.gmail_api.create_label({
            "name": "Modify Test Label"
        }, user_id=self.user_id)
        
        # Send a message
        message = self.gmail_api.send_message({
            "to": "modify_test@example.com",
            "subject": "Modify Test",
            "body": {"raw": "Message to modify"}
        }, user_id=self.user_id)
        
        # Modify message labels
        result = self.gmail_api.modify_message(
            self.user_id,
            message["id"],
            add_label_ids=[label["id"]],
            remove_label_ids=[]
        )
        self.assertIn("message", result)
        self.assertIn(label["id"], result["message"]["labelIds"])

    def test_modify_message_not_found(self):
        """Test modifying non-existent message."""
        result = self.gmail_api.modify_message(
            self.user_id,
            "invalid_message_id",
            add_label_ids=[],
            remove_label_ids=[]
        )
        self.assertIn("error", result)

    def test_get_thread_success(self):
        """Test getting a thread successfully."""
        # Send a message to create a thread
        message = self.gmail_api.send_message({
            "to": "thread_test@example.com",
            "subject": "Thread Test",
            "body": {"raw": "Initial message in thread"}
        }, user_id=self.user_id)
        
        # Get the thread
        thread = self.gmail_api.get_thread(message["threadId"], user_id=self.user_id)
        self.assertIsNotNone(thread)
        self.assertEqual(thread["id"], message["threadId"])
        self.assertIn("messages", thread)
        self.assertGreater(len(thread["messages"]), 0)

    def test_get_thread_with_format(self):
        """Test getting thread with specific format."""
        # Send a message
        message = self.gmail_api.send_message({
            "to": "thread_format_test@example.com",
            "subject": "Thread Format Test",
            "body": {"raw": "Thread format test message"}
        }, user_id=self.user_id)
        
        # Get thread with minimal format
        thread = self.gmail_api.get_thread(
            message["threadId"],
            user_id=self.user_id,
            format="minimal"
        )
        self.assertIsNotNone(thread)
        self.assertEqual(thread["id"], message["threadId"])

    def test_get_thread_not_found(self):
        """Test getting non-existent thread."""
        thread = self.gmail_api.get_thread("invalid_thread_id", user_id=self.user_id)
        self.assertIsNone(thread)

    def test_modify_thread_success(self):
        """Test modifying thread labels successfully."""
        # Create a label
        label = self.gmail_api.create_label({
            "name": "Thread Modify Label"
        }, user_id=self.user_id)
        
        # Send a message to create a thread
        message = self.gmail_api.send_message({
            "to": "thread_modify_test@example.com",
            "subject": "Thread Modify Test",
            "body": {"raw": "Thread to modify"}
        }, user_id=self.user_id)
        
        # Modify thread labels
        result = self.gmail_api.modify_thread(
            self.user_id,
            message["threadId"],
            add_label_ids=[label["id"]],
            remove_label_ids=[]
        )
        self.assertIn("thread", result)

    def test_modify_thread_not_found(self):
        """Test modifying non-existent thread."""
        result = self.gmail_api.modify_thread(
            self.user_id,
            "invalid_thread_id",
            add_label_ids=[],
            remove_label_ids=[]
        )
        self.assertIn("error", result)

    def test_reset_data_functionality(self):
        """Test data reset functionality."""
        # Create some data
        self.gmail_api.send_message({
            "to": "reset_test@example.com",
            "subject": "Reset Test",
            "body": {"raw": "Data before reset"}
        }, user_id=self.user_id)
        
        self.gmail_api.create_label({"name": "Reset Test Label"}, user_id=self.user_id)
        
        # Reset data
        result = self.gmail_api.reset_data()
        self.assertTrue(result["success"])

    def test_comprehensive_email_workflow(self):
        """Test comprehensive email workflow: compose, send, label, thread operations."""
        # Step 1: Create custom labels
        work_label = self.gmail_api.create_label({
            "name": "Work",
            "messageListVisibility": "show"
        }, user_id=self.user_id)
        
        urgent_label = self.gmail_api.create_label({
            "name": "Urgent",
            "messageListVisibility": "show"
        }, user_id=self.user_id)
        
        # Step 2: Send initial message
        initial_message = self.gmail_api.send_message({
            "to": "workflow_test@example.com",
            "subject": "Project Update - Urgent",
            "body": {"raw": "Initial project update message."},
            "labelIds": ["INBOX", work_label["id"]]
        }, user_id=self.user_id)
        
        # Step 3: Add urgent label to message
        self.gmail_api.modify_message(
            self.user_id,
            initial_message["id"],
            add_label_ids=[urgent_label["id"]],
            remove_label_ids=[]
        )
        
        # Step 4: Create and send draft response
        draft = self.gmail_api.create_draft({
            "to": "workflow_test@example.com",
            "subject": "Re: Project Update - Urgent",
            "body": "Thanks for the update. Following up...",
            "in_reply_to": initial_message["id"]
        }, user_id=self.user_id)
        
        sent_response = self.gmail_api.send_draft(self.user_id, draft["id"])
        
        # Step 5: Verify thread operations
        thread = self.gmail_api.get_thread(initial_message["threadId"], user_id=self.user_id)
        self.assertGreaterEqual(len(thread["messages"]), 2)
        
        # Step 6: Add label to entire thread
        self.gmail_api.modify_thread(
            self.user_id,
            initial_message["threadId"],
            add_label_ids=[work_label["id"]],
            remove_label_ids=[]
        )

    def test_label_management_workflow(self):
        """Test comprehensive label management workflow."""
        # Step 1: Create nested label structure
        parent_label = self.gmail_api.create_label({
            "name": "Projects",
            "messageListVisibility": "show",
            "labelListVisibility": "show"
        }, user_id=self.user_id)
        
        child_label = self.gmail_api.create_label({
            "name": "Projects/Web Development",
            "messageListVisibility": "show"
        }, user_id=self.user_id)
        
        # Step 2: List and verify labels
        labels_list = self.gmail_api.list_labels(user_id=self.user_id)
        label_names = [label["name"] for label in labels_list["labels"]]
        self.assertIn("Projects", label_names)
        self.assertIn("Projects/Web Development", label_names)
        
        # Step 3: Update label name
        self.gmail_api.update_label(
            self.user_id,
            child_label["id"],
            "Projects/Frontend Development"
        )
        
        # Step 4: Create messages with labels
        for i in range(3):
            self.gmail_api.send_message({
                "to": f"project{i}@example.com",
                "subject": f"Project Task {i+1}",
                "body": {"raw": f"Task {i+1} details"},
                "labelIds": ["INBOX", parent_label["id"], child_label["id"]]
            }, user_id=self.user_id)
        
        # Step 5: Query messages by label
        project_messages = self.gmail_api.list_messages(
            user_id=self.user_id,
            label_ids=[parent_label["id"]]
        )
        self.assertGreaterEqual(len(project_messages["messages"]), 3)

    def test_draft_management_comprehensive(self):
        """Test comprehensive draft management operations."""
        # Step 1: Create multiple drafts
        drafts = []
        for i in range(5):
            draft = self.gmail_api.create_draft({
                "to": f"draft{i}@example.com",
                "subject": f"Draft Subject {i+1}",
                "body": f"Draft content {i+1}"
            }, user_id=self.user_id)
            drafts.append(draft)
        
        # Step 2: Update some drafts
        updated_draft = self.gmail_api.update_draft(
            drafts[0]["id"],
            {
                "to": "updated_recipient@example.com",
                "subject": "Updated Draft Subject",
                "body": "Updated draft content"
            },
            user_id=self.user_id
        )
        self.assertEqual(updated_draft["message"]["subject"], "Updated Draft Subject")
        
        # Step 3: Send some drafts
        sent_draft = self.gmail_api.send_draft(self.user_id, drafts[1]["id"])
        self.assertIn("message", sent_draft)
        
        # Step 4: Delete some drafts
        delete_result = self.gmail_api.delete_draft(drafts[2]["id"], user_id=self.user_id)
        self.assertTrue(delete_result["success"])
        
        # Step 5: List remaining drafts
        remaining_drafts = self.gmail_api.list_drafts(user_id=self.user_id)
        remaining_ids = [draft["id"] for draft in remaining_drafts["drafts"]]
        self.assertNotIn(drafts[1]["id"], remaining_ids)  # Sent draft
        self.assertNotIn(drafts[2]["id"], remaining_ids)  # Deleted draft

    def test_search_and_filter_comprehensive(self):
        """Test comprehensive search and filtering operations."""
        # Step 1: Create test data with different characteristics
        test_messages = [
            {"to": "important@example.com", "subject": "Important Meeting", "body": {"raw": "Meeting scheduled for tomorrow"}},
            {"to": "project@example.com", "subject": "Project Update", "body": {"raw": "Project is on track"}},
            {"to": "urgent@example.com", "subject": "URGENT: Server Down", "body": {"raw": "Server maintenance required"}},
            {"to": "newsletter@example.com", "subject": "Weekly Newsletter", "body": {"raw": "This week's updates"}},
        ]
        
        sent_messages = []
        for msg in test_messages:
            sent_msg = self.gmail_api.send_message(msg, user_id=self.user_id)
            sent_messages.append(sent_msg)
        
        # Step 2: Test various search queries
        meeting_results = self.gmail_api.list_messages(user_id=self.user_id, q="meeting")
        self.assertGreater(len(meeting_results["messages"]), 0)
        
        urgent_results = self.gmail_api.list_messages(user_id=self.user_id, q="urgent")
        self.assertGreater(len(urgent_results["messages"]), 0)
        
        project_results = self.gmail_api.list_messages(user_id=self.user_id, q="project")
        self.assertGreater(len(project_results["messages"]), 0)

    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling scenarios."""
        # Test with None parameters
        with self.assertRaises((TypeError, AttributeError)):
            self.gmail_api.send_message(None, user_id=self.user_id)
        
        # Test with invalid user IDs
        invalid_profile = self.gmail_api.get_profile("")
        self.assertIsNone(invalid_profile)
        
        # Test with malformed message body
        result = self.gmail_api.send_message({}, user_id=self.user_id)
        self.assertIn("error", str(result).lower() if result else "")
        
        # Test with invalid label operations
        invalid_label = self.gmail_api.get_label("", user_id=self.user_id)
        self.assertIsNone(invalid_label)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)