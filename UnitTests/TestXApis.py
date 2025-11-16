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
    Unit tests for the XApis class using OAuth authentication.
    """

    # Load real data from backend
    real_data = BackendDataLoader.get_x_data()
    
    # Extract real user data
    users = list(real_data.get("users", {}).values())
    user_data_alice = users[0] if users else {}
    user_data_bob = users[1] if len(users) > 1 else user_data_alice
    
    REAL_EMAIL_ALICE = user_data_alice.get("email", "alice@example.com")
    REAL_EMAIL_BOB = user_data_bob.get("email", "bob@example.com")
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
        """Set up the API instance and create OAuth tokens."""
        self.x_api = XApis()
        self.alice_token = f"token_{self.REAL_EMAIL_ALICE}"
        self.bob_token = f"token_{self.REAL_EMAIL_BOB}"

    # --- Authentication Tests ---
    def test_authenticate_alice(self):
        """Test authenticating as Alice."""
        result = self.x_api.authenticate(self.alice_token)
        self.assertIn("id", result)
        self.assertIn("username", result)
        self.assertIn("email", result)
        self.assertEqual(result["email"], self.REAL_EMAIL_ALICE)

    def test_authenticate_bob(self):
        """Test authenticating as Bob."""
        result = self.x_api.authenticate(self.bob_token)
        self.assertIn("id", result)
        self.assertIn("username", result)
        self.assertEqual(result["email"], self.REAL_EMAIL_BOB)

    def test_authenticate_invalid_token(self):
        """Test authenticating with invalid token."""
        with self.assertRaises(Exception) as context:
            self.x_api.authenticate("invalid_token")
        self.assertIn("invalid", str(context.exception).lower())

    def test_ensure_authenticated_without_auth(self):
        """Test that methods requiring auth fail without authentication."""
        with self.assertRaises(Exception) as context:
            self.x_api.get_user_profile()
        self.assertIn("authentication required", str(context.exception).lower())

    # --- User Profile Tests ---
    def test_get_user_profile_alice(self):
        """Test getting authenticated user's profile."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.get_user_profile()
        self.assertIn("id", result)
        self.assertIn("username", result)
        self.assertIn("email", result)
        self.assertIn("public_metrics", result)
        self.assertEqual(result["email"], self.REAL_EMAIL_ALICE)

    def test_get_user_profile_bob(self):
        """Test getting Bob's profile."""
        self.x_api.authenticate(self.bob_token)
        result = self.x_api.get_user_profile()
        self.assertIn("username", result)
        self.assertEqual(result["email"], self.REAL_EMAIL_BOB)

    def test_update_profile_alice(self):
        """Test updating profile."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.update_profile(bio="Updated bio for testing", name="Alice Updated")
        self.assertIn("id", result)
        self.assertIn("bio", result)
        self.assertEqual(result["bio"], "Updated bio for testing")

    # --- Followers/Following Tests ---
    def test_get_followers_alice(self):
        """Test getting followers for authenticated user."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.get_followers()
        self.assertIn("data", result)
        self.assertIn("pagination", result)
        self.assertIsInstance(result["data"], list)

    def test_get_followers_with_pagination(self):
        """Test getting followers with pagination."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.get_followers(limit=2, offset=0)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["limit"], 2)

    def test_get_following_alice(self):
        """Test getting following for authenticated user."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.get_following()
        self.assertIn("data", result)
        self.assertIn("pagination", result)
        self.assertIsInstance(result["data"], list)

    def test_get_following_with_pagination(self):
        """Test getting following with pagination."""
        self.x_api.authenticate(self.bob_token)
        result = self.x_api.get_following(limit=3, offset=0)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["limit"], 3)

    # --- Tweet Management Tests ---
    def test_create_tweet(self):
        """Test creating a tweet."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.create_tweet(text="Test tweet from Alice")
        self.assertIn("id", result)
        self.assertIn("text", result)
        self.assertIn("author_id", result)
        self.assertEqual(result["text"], "Test tweet from Alice")
        self.assertEqual(result["author_id"], self.REAL_USER_ID_ALICE)

    def test_create_tweet_unauthenticated(self):
        """Test creating tweet without authentication."""
        with self.assertRaises(Exception) as context:
            self.x_api.create_tweet(text="Test")
        self.assertIn("authentication required", str(context.exception).lower())

    def test_get_tweet_public(self):
        """Test getting a tweet (public endpoint)."""
        result = self.x_api.get_tweet(self.REAL_POST_ID)
        self.assertIn("id", result)
        self.assertIn("text", result)

    def test_get_tweet_non_existent(self):
        """Test getting non-existent tweet."""
        with self.assertRaises(Exception) as context:
            self.x_api.get_tweet("nonexistent_tweet_id")
        self.assertIn("not found", str(context.exception).lower())

    def test_get_user_tweets(self):
        """Test getting authenticated user's tweets."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.get_user_tweets()
        self.assertIn("data", result)
        self.assertIn("pagination", result)
        self.assertIsInstance(result["data"], list)

    def test_get_user_tweets_with_pagination(self):
        """Test getting user tweets with pagination."""
        self.x_api.authenticate(self.bob_token)
        result = self.x_api.get_user_tweets(limit=2, offset=0)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["limit"], 2)

    def test_delete_tweet(self):
        """Test deleting a tweet."""
        self.x_api.authenticate(self.alice_token)
        # Create a tweet first
        create_result = self.x_api.create_tweet(text="Tweet to delete")
        tweet_id = create_result["id"]
        
        # Delete it
        self.x_api.delete_tweet(tweet_id)
        
        # Verify it's deleted
        with self.assertRaises(Exception):
            self.x_api.get_tweet(tweet_id)

    def test_delete_tweet_not_author(self):
        """Test deleting tweet as non-author fails."""
        # Alice creates a tweet
        self.x_api.authenticate(self.alice_token)
        create_result = self.x_api.create_tweet(text="Alice's tweet")
        tweet_id = create_result["id"]
        
        # Bob tries to delete it (should fail)
        self.x_api.authenticate(self.bob_token)
        with self.assertRaises(Exception) as context:
            self.x_api.delete_tweet(tweet_id)
        self.assertIn("not authorized", str(context.exception).lower())

    # --- Tweet Interaction Tests ---
    def test_like_tweet(self):
        """Test liking a tweet."""
        self.x_api.authenticate(self.alice_token)
        self.x_api.like_tweet(self.REAL_POST_ID)
        # Should not raise an exception

    def test_like_tweet_already_liked(self):
        """Test liking an already liked tweet."""
        self.x_api.authenticate(self.alice_token)
        # Like it once
        try:
            self.x_api.like_tweet(self.REAL_POST_ID)
        except:
            pass  # May already be liked
        
        # Try to like again (should fail)
        with self.assertRaises(Exception) as context:
            self.x_api.like_tweet(self.REAL_POST_ID)
        self.assertIn("already liked", str(context.exception).lower())

    def test_unlike_tweet(self):
        """Test unliking a tweet."""
        self.x_api.authenticate(self.alice_token)
        # Like it first
        try:
            self.x_api.like_tweet(self.REAL_POST_ID)
        except:
            pass  # May already be liked
        
        # Unlike it
        self.x_api.unlike_tweet(self.REAL_POST_ID)

    def test_unlike_tweet_not_liked(self):
        """Test unliking a tweet that wasn't liked."""
        self.x_api.authenticate(self.bob_token)
        # Make sure it's not liked
        try:
            self.x_api.unlike_tweet(self.REAL_POST_ID)
        except:
            pass
        
        # Try to unlike again (should fail)
        with self.assertRaises(Exception) as context:
            self.x_api.unlike_tweet(self.REAL_POST_ID)
        self.assertIn("not liked", str(context.exception).lower())

    def test_get_liked_tweets(self):
        """Test getting liked tweets."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.get_liked_tweets()
        self.assertIn("data", result)
        self.assertIn("pagination", result)
        self.assertIsInstance(result["data"], list)

    def test_get_liked_tweets_with_pagination(self):
        """Test getting liked tweets with pagination."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.get_liked_tweets(limit=1, offset=0)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["limit"], 1)

    # --- Direct Messages Tests ---
    def test_get_dm_conversations(self):
        """Test getting DM conversations."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.get_dm_conversations()
        self.assertIn("data", result)
        self.assertIn("pagination", result)
        self.assertIsInstance(result["data"], list)

    def test_get_dm_conversations_with_pagination(self):
        """Test getting DM conversations with pagination."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.get_dm_conversations(limit=5, offset=0)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["limit"], 5)

    def test_get_dm_conversation(self):
        """Test getting a specific DM conversation."""
        self.x_api.authenticate(self.alice_token)
        # Get all conversations first
        conversations = self.x_api.get_dm_conversations()
        if conversations["data"]:
            conv_id = conversations["data"][0]["conversation_id"]
            result = self.x_api.get_dm_conversation(conv_id)
            self.assertIn("id", result)
            self.assertIn("participants", result)
            self.assertIn("messages", result)

    def test_get_dm_conversation_not_participant(self):
        """Test getting DM conversation as non-participant."""
        # Alice gets her conversations
        self.x_api.authenticate(self.alice_token)
        conversations = self.x_api.get_dm_conversations()
        
        if conversations["data"]:
            conv_id = conversations["data"][0]["conversation_id"]
            
            # Check if Bob is a participant
            conv_details = self.x_api.get_dm_conversation(conv_id)
            if self.REAL_USER_ID_BOB not in conv_details["participants"]:
                # Bob tries to access (should fail)
                self.x_api.authenticate(self.bob_token)
                with self.assertRaises(Exception) as context:
                    self.x_api.get_dm_conversation(conv_id)
                self.assertIn("not authorized", str(context.exception).lower())

    def test_send_dm(self):
        """Test sending a direct message."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.send_dm(recipient_id=self.REAL_USER_ID_BOB, text="Test DM from Alice")
        self.assertIn("id", result)
        self.assertIn("participants", result)
        self.assertIn("messages", result)

    def test_send_dm_to_nonexistent_user(self):
        """Test sending DM to non-existent user."""
        self.x_api.authenticate(self.alice_token)
        with self.assertRaises(Exception) as context:
            self.x_api.send_dm(recipient_id="nonexistent_user", text="Test")
        self.assertIn("not found", str(context.exception).lower())

    def test_delete_dm_conversation(self):
        """Test deleting a DM conversation."""
        # Alice sends a message to Bob
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.send_dm(recipient_id=self.REAL_USER_ID_BOB, text="Message to delete")
        conv_id = result["id"]
        
        # Alice deletes the conversation
        self.x_api.delete_dm_conversation(conv_id)
        
        # Verify it's deleted
        with self.assertRaises(Exception):
            self.x_api.get_dm_conversation(conv_id)

    def test_delete_dm_conversation_not_participant(self):
        """Test deleting DM conversation as non-participant."""
        # Get a conversation that Bob is not part of
        self.x_api.authenticate(self.alice_token)
        conversations = self.x_api.get_dm_conversations()
        
        if conversations["data"]:
            # Find a conversation that Bob is not in
            for conv in conversations["data"]:
                conv_details = self.x_api.get_dm_conversation(conv["conversation_id"])
                if self.REAL_USER_ID_BOB not in conv_details["participants"]:
                    conv_id = conv["conversation_id"]
                    
                    # Bob tries to delete (should fail)
                    self.x_api.authenticate(self.bob_token)
                    with self.assertRaises(Exception) as context:
                        self.x_api.delete_dm_conversation(conv_id)
                    self.assertIn("not a participant", str(context.exception).lower())
                    break

    # --- Analytics Tests ---
    def test_get_api_usage(self):
        """Test getting API usage for authenticated user."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.get_api_usage()
        self.assertIsInstance(result, dict)

    def test_get_user_analytics(self):
        """Test getting user analytics."""
        self.x_api.authenticate(self.alice_token)
        result = self.x_api.get_user_analytics()
        self.assertIn("user_id", result)
        self.assertIn("username", result)
        self.assertIn("public_metrics", result)
        self.assertIn("total_likes_received", result)
        self.assertIn("engagement_ratio", result)

    def test_get_tweet_metrics(self):
        """Test getting tweet metrics (public endpoint)."""
        result = self.x_api.get_tweet_metrics(tweet_ids=[self.REAL_POST_ID])
        self.assertIsInstance(result, list)

    def test_get_tweet_metrics_multiple(self):
        """Test getting metrics for multiple tweets."""
        posts = list(self.real_data.get("posts", {}).keys())[:3]
        result = self.x_api.get_tweet_metrics(tweet_ids=posts)
        self.assertIsInstance(result, list)

    # --- Search Tests ---
    def test_search_users_by_bio(self):
        """Test searching users by bio (public endpoint)."""
        result = self.x_api.search_users_by_bio(search_term="developer")
        self.assertIn("data", result)
        self.assertIn("pagination", result)
        self.assertIsInstance(result["data"], list)

    def test_search_users_by_bio_with_pagination(self):
        """Test searching users with pagination."""
        result = self.x_api.search_users_by_bio(search_term="tech", limit=2, offset=0)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["limit"], 2)

    def test_get_verified_users(self):
        """Test getting verified users (public endpoint)."""
        result = self.x_api.get_verified_users()
        self.assertIn("data", result)
        self.assertIn("pagination", result)
        self.assertIsInstance(result["data"], list)

    def test_get_verified_users_with_pagination(self):
        """Test getting verified users with pagination."""
        result = self.x_api.get_verified_users(limit=5, offset=0)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["limit"], 5)

    # --- Workflow Tests ---
    def test_tweet_creation_workflow(self):
        """Test complete tweet creation and interaction workflow."""
        # Alice creates a tweet
        self.x_api.authenticate(self.alice_token)
        create_result = self.x_api.create_tweet(text="Workflow test tweet")
        tweet_id = create_result["id"]
        
        # Bob likes the tweet
        self.x_api.authenticate(self.bob_token)
        self.x_api.like_tweet(tweet_id)
        
        # Get tweet details
        tweet_details = self.x_api.get_tweet(tweet_id)
        self.assertIn("public_metrics", tweet_details)
        
        # Bob unlikes the tweet
        self.x_api.unlike_tweet(tweet_id)
        
        # Alice deletes the tweet
        self.x_api.authenticate(self.alice_token)
        self.x_api.delete_tweet(tweet_id)

    def test_dm_workflow(self):
        """Test direct message workflow."""
        # Alice sends DM to Bob
        self.x_api.authenticate(self.alice_token)
        send_result = self.x_api.send_dm(recipient_id=self.REAL_USER_ID_BOB, text="Workflow DM test")
        conv_id = send_result["id"]
        
        # Bob views the conversation
        self.x_api.authenticate(self.bob_token)
        conv_details = self.x_api.get_dm_conversation(conv_id)
        self.assertIn("messages", conv_details)
        
        # Bob replies
        reply_result = self.x_api.send_dm(recipient_id=self.REAL_USER_ID_ALICE, text="Reply to Alice")
        self.assertEqual(reply_result["id"], conv_id)  # Same conversation

    def test_user_profile_workflow(self):
        """Test user profile workflow."""
        # Get initial profile
        self.x_api.authenticate(self.alice_token)
        profile = self.x_api.get_user_profile()
        original_bio = profile.get("bio")
        
        # Update profile
        updated = self.x_api.update_profile(bio="Updated workflow bio")
        self.assertEqual(updated["bio"], "Updated workflow bio")
        
        # Get analytics
        analytics = self.x_api.get_user_analytics()
        self.assertIn("public_metrics", analytics)
        
        # Get API usage
        usage = self.x_api.get_api_usage()
        self.assertIsInstance(usage, dict)

    # --- Data Reset Tests ---
    def test_reset_data(self):
        """Test resetting data clears authentication."""
        self.x_api.authenticate(self.alice_token)
        self.assertIsNotNone(self.x_api.access_token)
        
        self.x_api.reset_data()
        
        self.assertIsNone(self.x_api.access_token)
        self.assertIsNone(self.x_api.current_user_id)

if __name__ == "__main__":
    unittest.main()
