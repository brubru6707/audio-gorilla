import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import API and helper
from XApis import XApis
from UnitTests.test_data_helper import BackendDataLoader

class TestXApis(unittest.TestCase):
    """
    Unit tests for the XApis class, covering multi-user functionality.
    """

    # Load real data from backend
    real_data = BackendDataLoader.get_x_data()
    
    # Extract real user data
    users = list(real_data.get("users", {}).values())
    user_data_alice = users[0] if users else {}
    user_data_bob = users[1] if len(users) > 1 else user_data_alice
    
    REAL_USER_ID_ALICE = user_data_alice.get("id", "user1")
    REAL_USER_ID_BOB = user_data_bob.get("id", "user2")
    REAL_USERNAME_ALICE = user_data_alice.get("username", "alice")
    REAL_USERNAME_BOB = user_data_bob.get("username", "bob")
    
    # Extract real post data
    posts = list(real_data.get("posts", {}).values())
    post_data = posts[0] if posts else {}
    REAL_POST_ID = next(iter(real_data.get("posts", {})), "post1")
    REAL_POST_TEXT = post_data.get("text", "Test post")
    
    # Extract real conversation data
    conversations = list(real_data.get("direct_messages", {}).values())
    conversation_data = conversations[0] if conversations else {}
    REAL_CONVERSATION_ID = next(iter(real_data.get("direct_messages", {})), "conv1")
    
    def setUp(self):
        """Set up the API instance using real data."""
        self.x_api = XApis()

    # --- User Management Tests ---
    def test_set_current_user_alice(self):
        """Test setting current user to Alice."""
        result = self.x_api.set_current_user(user_id=self.REAL_USER_ID_ALICE)
        self.assertTrue(result.get("status", False))

    def test_set_current_user_bob(self):
        """Test setting current user to Bob."""
        result = self.x_api.set_current_user(user_id=self.REAL_USER_ID_BOB)
        self.assertTrue(result.get("status", False))

    def test_set_current_user_non_existent(self):
        """Test setting current user to non-existent user."""
        result = self.x_api.set_current_user(user_id="nonexistent_user")
        self.assertFalse(result.get("status", True))

    # --- User Profile Tests ---
    def test_get_user_profile_alice(self):
        """Test getting user profile for Alice."""
        result = self.x_api.get_user_profile(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        self.assertIn("username", result["data"])

    def test_get_user_profile_bob(self):
        """Test getting user profile for Bob."""
        result = self.x_api.get_user_profile(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_get_user_profile_non_existent(self):
        """Test getting profile for non-existent user."""
        result = self.x_api.get_user_profile(user_id="nonexistent_user")
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    def test_update_user_bio_alice(self):
        """Test updating user bio for Alice."""
        result = self.x_api.update_user_bio(user_id=self.REAL_USER_ID_ALICE, new_bio="Updated bio for Alice")
        self.assertEqual(result.get("status"), "success")

    def test_update_user_bio_bob(self):
        """Test updating user bio for Bob."""
        result = self.x_api.update_user_bio(user_id=self.REAL_USER_ID_BOB, new_bio="Updated bio for Bob")
        self.assertEqual(result.get("status"), "success")

    def test_update_user_bio_non_existent(self):
        """Test updating bio for non-existent user."""
        result = self.x_api.update_user_bio(user_id="nonexistent_user", new_bio="New bio")
        self.assertEqual(result.get("status"), "error")

    # --- Followers/Following Tests ---
    def test_list_followers_alice(self):
        """Test listing followers for Alice."""
        result = self.x_api.list_followers(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        self.assertIsInstance(result["data"], list)

    def test_list_followers_bob(self):
        """Test listing followers for Bob."""
        result = self.x_api.list_followers(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_list_followers_non_existent(self):
        """Test listing followers for non-existent user."""
        result = self.x_api.list_followers(user_id="nonexistent_user")
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    def test_list_following_alice(self):
        """Test listing following for Alice."""
        result = self.x_api.list_following(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        self.assertIsInstance(result["data"], list)

    def test_list_following_bob(self):
        """Test listing following for Bob."""
        result = self.x_api.list_following(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_list_following_non_existent(self):
        """Test listing following for non-existent user."""
        result = self.x_api.list_following(user_id="nonexistent_user")
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    # --- Post Management Tests ---
    def test_create_post_alice(self):
        """Test creating a post for Alice."""
        result = self.x_api.create_post(user_id=self.REAL_USER_ID_ALICE, text="Test post from Alice")
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIn("id", result["data"])

    def test_create_post_bob(self):
        """Test creating a post for Bob."""
        result = self.x_api.create_post(user_id=self.REAL_USER_ID_BOB, text="Test post from Bob")
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_create_post_non_existent_user(self):
        """Test creating a post for non-existent user."""
        result = self.x_api.create_post(user_id="nonexistent_user", text="Test post")
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    def test_delete_post_alice(self):
        """Test deleting a post for Alice."""
        # First create a post
        create_result = self.x_api.create_post(user_id=self.REAL_USER_ID_ALICE, text="Post to delete")
        if create_result.get("data"):
            post_id = create_result["data"]["id"]
            result = self.x_api.delete_post(user_id=self.REAL_USER_ID_ALICE, post_id=post_id)
            self.assertTrue(result.get("success", False))

    def test_delete_post_bob(self):
        """Test deleting a post for Bob."""
        # First create a post
        create_result = self.x_api.create_post(user_id=self.REAL_USER_ID_BOB, text="Post to delete")
        if create_result.get("data"):
            post_id = create_result["data"]["id"]
            result = self.x_api.delete_post(user_id=self.REAL_USER_ID_BOB, post_id=post_id)
            self.assertTrue(result.get("success", False))

    def test_delete_post_non_existent(self):
        """Test deleting a non-existent post."""
        result = self.x_api.delete_post(user_id=self.REAL_USER_ID_ALICE, post_id="non_existent_post")
        self.assertFalse(result.get("success", True))

    def test_get_post_details_existing(self):
        """Test getting details for an existing post."""
        result = self.x_api.get_post_details(post_id=self.REAL_POST_ID)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIn("text", result["data"])

    def test_get_post_details_non_existent(self):
        """Test getting details for non-existent post."""
        result = self.x_api.get_post_details(post_id="non_existent_post")
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    def test_list_user_posts_alice(self):
        """Test listing posts for Alice."""
        result = self.x_api.list_user_posts(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIsInstance(result["data"], list)

    def test_list_user_posts_bob(self):
        """Test listing posts for Bob."""
        result = self.x_api.list_user_posts(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_list_user_posts_non_existent(self):
        """Test listing posts for non-existent user."""
        result = self.x_api.list_user_posts(user_id="nonexistent_user")
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    # --- Post Interaction Tests ---
    def test_like_post_alice(self):
        """Test liking a post for Alice."""
        # Check if post exists first
        post_exists = self.x_api.get_post_details(post_id=self.REAL_POST_ID)
        if post_exists.get("data"):
            result = self.x_api.like_post(user_id=self.REAL_USER_ID_ALICE, post_id=self.REAL_POST_ID)
            self.assertTrue(result.get("success", False))
        else:
            self.skipTest("REAL_POST_ID does not exist in test data")

    def test_like_post_bob(self):
        """Test liking a post for Bob."""
        # First unlike the post if it's already liked
        self.x_api.unlike_post(user_id=self.REAL_USER_ID_BOB, post_id=self.REAL_POST_ID)
        # Now try to like it
        result = self.x_api.like_post(user_id=self.REAL_USER_ID_BOB, post_id=self.REAL_POST_ID)
        self.assertTrue(result.get("success", False))

    def test_like_post_non_existent_post(self):
        """Test liking a non-existent post."""
        result = self.x_api.like_post(user_id=self.REAL_USER_ID_ALICE, post_id="non_existent_post")
        self.assertFalse(result.get("success", True))

    def test_unlike_post_alice(self):
        """Test unliking a post for Alice."""
        # First like the post
        like_result = self.x_api.like_post(user_id=self.REAL_USER_ID_ALICE, post_id=self.REAL_POST_ID)
        if like_result.get("success"):
            result = self.x_api.unlike_post(user_id=self.REAL_USER_ID_ALICE, post_id=self.REAL_POST_ID)
            self.assertTrue(result.get("success", False))

    def test_unlike_post_bob(self):
        """Test unliking a post for Bob."""
        # First like the post
        like_result = self.x_api.like_post(user_id=self.REAL_USER_ID_BOB, post_id=self.REAL_POST_ID)
        if like_result.get("success"):
            result = self.x_api.unlike_post(user_id=self.REAL_USER_ID_BOB, post_id=self.REAL_POST_ID)
            self.assertTrue(result.get("success", False))

    def test_unlike_post_non_existent(self):
        """Test unliking a non-existent post."""
        result = self.x_api.unlike_post(user_id=self.REAL_USER_ID_ALICE, post_id="non_existent_post")
        self.assertFalse(result.get("success", True))

    def test_list_liked_posts_alice(self):
        """Test listing liked posts for Alice."""
        result = self.x_api.list_liked_posts(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIsInstance(result["data"], list)

    def test_list_liked_posts_bob(self):
        """Test listing liked posts for Bob."""
        result = self.x_api.list_liked_posts(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_list_liked_posts_non_existent(self):
        """Test listing liked posts for non-existent user."""
        result = self.x_api.list_liked_posts(user_id="nonexistent_user")
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    # --- Direct Messages Tests ---
    def test_list_direct_messages_conversations_alice(self):
        """Test listing DM conversations for Alice."""
        result = self.x_api.list_direct_messages_conversations(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIsInstance(result["data"], list)

    def test_list_direct_messages_conversations_bob(self):
        """Test listing DM conversations for Bob."""
        result = self.x_api.list_direct_messages_conversations(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_list_direct_messages_conversations_non_existent(self):
        """Test listing DM conversations for non-existent user."""
        result = self.x_api.list_direct_messages_conversations(user_id="nonexistent_user")
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    def test_get_direct_messages_conversation_existing(self):
        """Test getting an existing DM conversation."""
        # Use a known existing conversation ID from the Backends test data
        existing_conversation_id = "9277335a-d071-4e0e-944f-b84d23b3ea3e"
        result = self.x_api.get_direct_messages_conversation(conversation_id=existing_conversation_id)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIn("messages", result["data"])

    def test_get_direct_messages_conversation_non_existent(self):
        """Test getting a non-existent DM conversation."""
        result = self.x_api.get_direct_messages_conversation(conversation_id="non_existent_conversation")
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    def test_send_direct_message_alice_to_bob(self):
        """Test sending a direct message from Alice to Bob."""
        result = self.x_api.send_direct_message(
            sender_id=self.REAL_USER_ID_ALICE,
            receiver_id=self.REAL_USER_ID_BOB,
            text="Hello Bob, this is Alice!"
        )
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIn("messages", result["data"])

    def test_send_direct_message_bob_to_alice(self):
        """Test sending a direct message from Bob to Alice."""
        result = self.x_api.send_direct_message(
            sender_id=self.REAL_USER_ID_BOB,
            receiver_id=self.REAL_USER_ID_ALICE,
            text="Hi Alice, this is Bob!"
        )
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_send_direct_message_non_existent_sender(self):
        """Test sending a DM with non-existent sender."""
        result = self.x_api.send_direct_message(
            sender_id="nonexistent_sender",
            receiver_id=self.REAL_USER_ID_ALICE,
            text="Test message"
        )
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    def test_send_direct_message_non_existent_receiver(self):
        """Test sending a DM with non-existent receiver."""
        result = self.x_api.send_direct_message(
            sender_id=self.REAL_USER_ID_ALICE,
            receiver_id="nonexistent_receiver",
            text="Test message"
        )
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    def test_delete_direct_message_conversation_alice(self):
        """Test deleting a DM conversation for Alice."""
        # First send a message to create a conversation
        send_result = self.x_api.send_direct_message(
            sender_id=self.REAL_USER_ID_ALICE,
            receiver_id=self.REAL_USER_ID_BOB,
            text="Message to delete conversation"
        )
        if send_result.get("data"):
            conversation_id = send_result["data"]["id"]
            result = self.x_api.delete_direct_message_conversation(
                user_id=self.REAL_USER_ID_ALICE,
                conversation_id=conversation_id
            )
            self.assertTrue(result.get("success", False))

    def test_delete_direct_message_conversation_bob(self):
        """Test deleting a DM conversation for Bob."""
        # First send a message to create a conversation
        send_result = self.x_api.send_direct_message(
            sender_id=self.REAL_USER_ID_BOB,
            receiver_id=self.REAL_USER_ID_ALICE,
            text="Message to delete conversation"
        )
        if send_result.get("data"):
            conversation_id = send_result["data"]["id"]
            result = self.x_api.delete_direct_message_conversation(
                user_id=self.REAL_USER_ID_BOB,
                conversation_id=conversation_id
            )
            self.assertTrue(result.get("success", False))

    def test_delete_direct_message_conversation_non_existent(self):
        """Test deleting a non-existent DM conversation."""
        result = self.x_api.delete_direct_message_conversation(
            user_id=self.REAL_USER_ID_ALICE,
            conversation_id="non_existent_conversation"
        )
        self.assertFalse(result.get("success", True))

    # --- Analytics Tests ---
    def test_get_api_usage_alice(self):
        """Test getting API usage for Alice."""
        result = self.x_api.get_api_usage(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIsInstance(result["data"], dict)

    def test_get_api_usage_bob(self):
        """Test getting API usage for Bob."""
        result = self.x_api.get_api_usage(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_get_api_usage_non_existent(self):
        """Test getting API usage for non-existent user."""
        result = self.x_api.get_api_usage(user_id="nonexistent_user")
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    def test_get_post_metrics_single_post(self):
        """Test getting metrics for a single post."""
        result = self.x_api.get_post_metrics(post_ids=[self.REAL_POST_ID])
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIsInstance(result["data"], list)

    def test_get_post_metrics_multiple_posts(self):
        """Test getting metrics for multiple posts."""
        result = self.x_api.get_post_metrics(post_ids=[self.REAL_POST_ID, "post2"])
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_get_post_metrics_with_specific_metrics(self):
        """Test getting specific metrics for posts."""
        result = self.x_api.get_post_metrics(
            post_ids=[self.REAL_POST_ID],
            metrics=["likes", "shares"]
        )
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_get_user_analytics_alice(self):
        """Test getting user analytics for Alice."""
        result = self.x_api.get_user_analytics(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIn("username", result["data"])

    def test_get_user_analytics_bob(self):
        """Test getting user analytics for Bob."""
        result = self.x_api.get_user_analytics(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_get_user_analytics_non_existent(self):
        """Test getting analytics for non-existent user."""
        result = self.x_api.get_user_analytics(user_id="nonexistent_user")
        self.assertIn("error", result)
        self.assertIsNone(result.get("data"))

    # --- Search Tests ---
    def test_search_users_by_bio(self):
        """Test searching users by bio."""
        result = self.x_api.search_users_by_bio(search_term="developer")
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIsInstance(result["data"], list)

    def test_search_users_by_bio_no_results(self):
        """Test searching users by bio with no results."""
        result = self.x_api.search_users_by_bio(search_term="nonexistent_term")
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))

    def test_get_verified_users(self):
        """Test getting verified users."""
        result = self.x_api.get_verified_users()
        self.assertIn("data", result)
        self.assertIsNotNone(result.get("data"))
        if result.get("data"):
            self.assertIsInstance(result["data"], list)

    # --- Workflow Tests ---
    def test_post_creation_and_interaction_workflow(self):
        """Test comprehensive post creation and interaction workflow."""
        # Create post
        create_result = self.x_api.create_post(user_id=self.REAL_USER_ID_ALICE, text="Workflow test post")
        self.assertIn("data", create_result)
        self.assertIsNotNone(create_result.get("data"))
        
        if create_result.get("data"):
            post_id = create_result["data"]["id"]
            
            # Get post details
            details_result = self.x_api.get_post_details(post_id=post_id)
            self.assertIn("data", details_result)
            self.assertIsNotNone(details_result.get("data"))
            
            # Like post from Bob
            like_result = self.x_api.like_post(user_id=self.REAL_USER_ID_BOB, post_id=post_id)
            self.assertTrue(like_result.get("success", False))
            
            # Get metrics
            metrics_result = self.x_api.get_post_metrics(post_ids=[post_id])
            self.assertIn("data", metrics_result)
            self.assertIsNotNone(metrics_result.get("data"))
            
            # Delete post
            delete_result = self.x_api.delete_post(user_id=self.REAL_USER_ID_ALICE, post_id=post_id)
            self.assertTrue(delete_result.get("success", False))

    def test_direct_message_workflow(self):
        """Test direct message workflow."""
        # Send message from Alice to Bob
        send_result = self.x_api.send_direct_message(
            sender_id=self.REAL_USER_ID_ALICE,
            receiver_id=self.REAL_USER_ID_BOB,
            text="Workflow DM test"
        )
        self.assertIn("data", send_result)
        self.assertIsNotNone(send_result.get("data"))
        
        # List conversations for Bob
        list_result = self.x_api.list_direct_messages_conversations(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", list_result)
        self.assertIsNotNone(list_result.get("data"))
        
        # Get conversation details
        if list_result.get("data") and list_result["data"]:
            conversation_id = list_result["data"][0]["conversation_id"]
            conv_result = self.x_api.get_direct_messages_conversation(conversation_id=conversation_id)
            self.assertIn("data", conv_result)
            self.assertIsNotNone(conv_result.get("data"))

    def test_user_profile_workflow(self):
        """Test user profile workflow."""
        # Get initial profile
        profile_result = self.x_api.get_user_profile(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", profile_result)
        self.assertIsNotNone(profile_result.get("data"))
        
        # Update bio
        bio_result = self.x_api.update_user_bio(user_id=self.REAL_USER_ID_ALICE, new_bio="Updated workflow bio")
        self.assertEqual(bio_result.get("status"), "success")
        
        # Get analytics
        analytics_result = self.x_api.get_user_analytics(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", analytics_result)
        self.assertIsNotNone(analytics_result.get("data"))
        
        # Get API usage
        usage_result = self.x_api.get_api_usage(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", usage_result)
        self.assertIsNotNone(usage_result.get("data"))

    # --- Data Reset Tests ---
    def test_reset_data_success(self):
        """Test resetting data successfully."""
        result = self.x_api.reset_data()
        self.assertTrue(result.get("reset_status", False))

if __name__ == "__main__":
    unittest.main()
