import unittest
from copy import deepcopy
from XApis import XApis, DEFAULT_STATE

class TestXApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh XApis instance for each test."""
        self.x_api = XApis()
        self.x_api._load_scenario(deepcopy(DEFAULT_STATE))

    def test_send_dm_to_user_new_conversation(self):
        """Test sending a DM to a user, creating a new conversation if none exists."""
        user_id = "user3"
        message_text = "Hello from the test user!"
        self.x_api.users["user3"] = {"id": "user3", "username": "test_user", "name": "Test User"}
        initial_dm_count = len(self.x_api.direct_messages)
        result = self.x_api.send_dm_to_user(user_id=user_id, message_text=message_text)
        self.assertIsNotNone(result["data"])
        self.assertIn("conversation_id", result["data"])
        self.assertIn("message_text", result["data"])
        self.assertEqual(result["data"]["message_text"], message_text)
        self.assertEqual(len(self.x_api.direct_messages), initial_dm_count + 1)
        new_conv_id = result["data"]["conversation_id"]
        self.assertIn(new_conv_id, self.x_api.direct_messages)
        self.assertIn({"sender_id": "current_user_dummy", "text": message_text},
                      self.x_api.direct_messages[new_conv_id]["messages"])
        self.assertIn(user_id, self.x_api.direct_messages[new_conv_id]["participants"])

    def test_send_dm_to_user_existing_conversation(self):
        """Test sending a DM to a user with an existing conversation."""
        user_id = "user2"
        message_text = "Another message for Bob!"
        conversation_id = "dm_conv_1"
        initial_message_count = len(self.x_api.direct_messages[conversation_id]["messages"])
        result = self.x_api.send_dm_to_user(user_id=user_id, message_text=message_text)
        self.assertIsNotNone(result["data"])
        self.assertEqual(result["data"]["conversation_id"], conversation_id)
        self.assertEqual(result["data"]["message_text"], message_text)
        self.assertEqual(len(self.x_api.direct_messages[conversation_id]["messages"]), initial_message_count + 1)
        self.assertIn({"sender_id": "current_user_dummy", "text": message_text},
                      self.x_api.direct_messages[conversation_id]["messages"])

    def test_send_dm_to_conversation_success(self):
        """Test sending a DM to an existing conversation."""
        conversation_id = "dm_conv_1"
        message_text = "Hello from the test!"
        initial_message_count = len(self.x_api.direct_messages[conversation_id]["messages"])
        result = self.x_api.send_dm_to_conversation(conversation_id=conversation_id, message_text=message_text)
        self.assertIsNotNone(result["data"])
        self.assertEqual(result["data"]["conversation_id"], conversation_id)
        self.assertEqual(result["data"]["message_text"], message_text)
        self.assertEqual(len(self.x_api.direct_messages[conversation_id]["messages"]), initial_message_count + 1)
        self.assertIn({"sender_id": "current_user_dummy", "text": message_text},
                      self.x_api.direct_messages[conversation_id]["messages"])

    def test_send_dm_to_conversation_not_found(self):
        """Test sending a DM to a non-existent conversation."""
        conversation_id = "non_existent_conv"
        message_text = "This message should not be sent."
        result = self.x_api.send_dm_to_conversation(conversation_id=conversation_id, message_text=message_text)
        self.assertIsNone(result["data"])
        self.assertEqual(result["error"], "Conversation not found")

    def test_get_dm_events_success(self):
        """Test retrieving DM events for a specific conversation."""
        conversation_id = "dm_conv_1"
        result = self.x_api.get_dm_events(conversation_id=conversation_id)
        self.assertIsNotNone(result["data"])
        self.assertIsInstance(result["data"], list)
        self.assertGreater(len(result["data"]), 0)
        self.assertEqual(result["data"][0]["sender_id"], "user1")
        self.assertEqual(result["data"][1]["text"], "Hey Alice!")

    def test_get_dm_events_not_found(self):
        """Test retrieving DM events for a non-existent conversation."""
        conversation_id = "non_existent_conv"
        result = self.x_api.get_dm_events(conversation_id=conversation_id)
        self.assertIsNone(result["data"])
        self.assertEqual(result["error"], "Conversation not found")

    def test_like_post_success(self):
        """Test liking a post successfully."""
        user_id = "user1"
        post_id = "post3"
        initial_likes_post = len(self.x_api.posts[post_id]["likes"])
        initial_liked_posts_user = len(self.x_api.users[user_id].get("liked_posts", []))
        initial_metrics_likes = self.x_api.posts[post_id]["metrics"]["likes"]
        result = self.x_api.like_post(user_id=user_id, post_id=post_id)
        self.assertTrue(result["liked"])
        self.assertIn(user_id, self.x_api.posts[post_id]["likes"])
        self.assertEqual(len(self.x_api.posts[post_id]["likes"]), initial_likes_post + 1)
        self.assertEqual(self.x_api.posts[post_id]["metrics"]["likes"], initial_metrics_likes + 1)
        self.assertIn(post_id, self.x_api.users[user_id]["liked_posts"])
        self.assertEqual(len(self.x_api.users[user_id]["liked_posts"]), initial_liked_posts_user + 1)

    def test_like_post_already_liked(self):
        """Test liking a post that is already liked by the user."""
        user_id = "user1"
        post_id = "post2"
        initial_likes_post = len(self.x_api.posts[post_id]["likes"])
        initial_liked_posts_user = len(self.x_api.users[user_id].get("liked_posts", []))
        initial_metrics_likes = self.x_api.posts[post_id]["metrics"]["likes"]
        result = self.x_api.like_post(user_id=user_id, post_id=post_id)
        self.assertFalse(result["liked"])
        self.assertEqual(result["reason"], "Already liked")
        self.assertEqual(len(self.x_api.posts[post_id]["likes"]), initial_likes_post)
        self.assertEqual(self.x_api.posts[post_id]["metrics"]["likes"], initial_metrics_likes)
        self.assertEqual(len(self.x_api.users[user_id]["liked_posts"]), initial_liked_posts_user)

    def test_unlike_post_success(self):
        """Test unliking a post successfully."""
        user_id = "user1"
        post_id = "post2"
        initial_likes_post = len(self.x_api.posts[post_id]["likes"])
        initial_liked_posts_user = len(self.x_api.users[user_id].get("liked_posts", []))
        initial_metrics_likes = self.x_api.posts[post_id]["metrics"]["likes"]
        result = self.x_api.unlike_post(user_id=user_id, post_id=post_id)
        self.assertTrue(result["unliked"])
        self.assertNotIn(user_id, self.x_api.posts[post_id]["likes"])
        self.assertEqual(len(self.x_api.posts[post_id]["likes"]), initial_likes_post - 1)
        self.assertEqual(self.x_api.posts[post_id]["metrics"]["likes"], initial_metrics_likes - 1)
        self.assertNotIn(post_id, self.x_api.users[user_id]["liked_posts"])
        self.assertEqual(len(self.x_api.users[user_id]["liked_posts"]), initial_liked_posts_user - 1)

    def test_unlike_post_not_liked(self):
        """Test unliking a post that was not liked by the user."""
        user_id = "user2"
        post_id = "post3"
        initial_likes_post = len(self.x_api.posts[post_id]["likes"])
        initial_liked_posts_user = len(self.x_api.users[user_id].get("liked_posts", []))
        initial_metrics_likes = self.x_api.posts[post_id]["metrics"]["likes"]
        result = self.x_api.unlike_post(user_id=user_id, post_id=post_id)
        self.assertFalse(result["unliked"])
        self.assertEqual(result["reason"], "Not liked yet")
        self.assertEqual(len(self.x_api.posts[post_id]["likes"]), initial_likes_post)
        self.assertEqual(self.x_api.posts[post_id]["metrics"]["likes"], initial_metrics_likes)
        self.assertEqual(len(self.x_api.users[user_id]["liked_posts"]), initial_liked_posts_user)

    def test_create_community_note_success(self):
        """Test creating a community note successfully."""
        post_id = "post1"
        note_text = "This is a new community note."
        tags = ["correction", "info"]
        initial_notes_count = len(self.x_api.community_notes)
        result = self.x_api.create_community_note(post_id=post_id, note_text=note_text, tags=tags)
        self.assertIsNotNone(result["data"])
        self.assertIn("id", result["data"])
        self.assertEqual(result["data"]["tweet_id"], post_id)
        self.assertEqual(result["data"]["text"], note_text)
        self.assertEqual(result["data"]["tags"], tags)
        self.assertEqual(len(self.x_api.community_notes), initial_notes_count + 1)
        self.assertIn(result["data"]["id"], self.x_api.community_notes)

    def test_create_community_note_post_not_found(self):
        """Test creating a community note for a non-existent post."""
        post_id = "non_existent_post"
        note_text = "This note should not be created."
        result = self.x_api.create_community_note(post_id=post_id, note_text=note_text)
        self.assertIsNone(result["data"])
        self.assertEqual(result["error"], "Post not found")

    def test_dm_flow_create_send_get(self):
        """Test a complete DM flow: create, send, and retrieve messages."""
        participant_ids = ["user1", "user2"]
        initial_message = "Hello team!"
        create_result = self.x_api.create_dm_conversation(participant_ids=participant_ids, message_text=initial_message)
        self.assertIsNotNone(create_result["data"])
        new_conv_id = create_result["data"]["id"]
        self.assertIn(new_conv_id, self.x_api.direct_messages)
        second_message = "Hope you are doing well!"
        send_result = self.x_api.send_dm_to_conversation(conversation_id=new_conv_id, message_text=second_message)
        self.assertIsNotNone(send_result["data"])
        self.assertEqual(send_result["data"]["conversation_id"], new_conv_id)
        get_events_result = self.x_api.get_dm_events(conversation_id=new_conv_id)
        self.assertIsNotNone(get_events_result["data"])
        self.assertEqual(len(get_events_result["data"]), 2)
        self.assertEqual(get_events_result["data"][0]["text"], initial_message)
        self.assertEqual(get_events_result["data"][1]["text"], second_message)

    def test_post_like_unlike_metrics_flow(self):
        """Test liking, unliking a post, and verifying metrics."""
        user_id = "user2"
        post_id = "post3"
        initial_likes_post = len(self.x_api.posts[post_id]["likes"])
        initial_metrics_likes = self.x_api.posts[post_id]["metrics"]["likes"]
        self.assertEqual(initial_likes_post, 0)
        self.assertEqual(initial_metrics_likes, 0)
        like_result = self.x_api.like_post(user_id=user_id, post_id=post_id)
        self.assertTrue(like_result["liked"])
        self.assertEqual(len(self.x_api.posts[post_id]["likes"]), 1)
        self.assertEqual(self.x_api.posts[post_id]["metrics"]["likes"], 1)
        self.assertIn(post_id, self.x_api.users[user_id]["liked_posts"])
        metrics_result = self.x_api.get_post_metrics(post_ids=[post_id], metrics=["likes"])
        self.assertIsNotNone(metrics_result["data"])
        self.assertEqual(metrics_result["data"][0]["tweet_id"], post_id)
        self.assertEqual(metrics_result["data"][0]["metrics"]["likes"], 1)
        unlike_result = self.x_api.unlike_post(user_id=user_id, post_id=post_id)
        self.assertTrue(unlike_result["unliked"])
        self.assertEqual(len(self.x_api.posts[post_id]["likes"]), 0)
        self.assertEqual(self.x_api.posts[post_id]["metrics"]["likes"], 0)
        self.assertNotIn(post_id, self.x_api.users[user_id]["liked_posts"])
        metrics_result_after_unlike = self.x_api.get_post_metrics(post_ids=[post_id], metrics=["likes"])
        self.assertIsNotNone(metrics_result_after_unlike["data"])
        self.assertEqual(metrics_result_after_unlike["data"][0]["tweet_id"], post_id)
        self.assertEqual(metrics_result_after_unlike["data"][0]["metrics"]["likes"], 0)

    def test_search_and_note_creation_flow(self):
        """Test searching for eligible posts and then creating a community note."""
        query = "first post"
        note_text = "Adding a note to the first post found."
        tags = ["clarification"]
        search_result = self.x_api.search_eligible_community_notes(query=query, max_results=1)
        self.assertIsNotNone(search_result["data"])
        self.assertGreater(len(search_result["data"]), 0)
        eligible_post_id = search_result["data"][0]["id"]
        self.assertEqual(eligible_post_id, "post1")
        initial_notes_count = len(self.x_api.community_notes)
        create_note_result = self.x_api.create_community_note(post_id=eligible_post_id, note_text=note_text, tags=tags)
        self.assertIsNotNone(create_note_result["data"])
        self.assertEqual(create_note_result["data"]["tweet_id"], eligible_post_id)
        self.assertEqual(len(self.x_api.community_notes), initial_notes_count + 1)
        search_note_result = self.x_api.search_written_community_notes(query="Adding a note", max_results=1)
        self.assertIsNotNone(search_note_result["data"])
        self.assertGreater(len(search_note_result["data"]), 0)
        self.assertEqual(search_note_result["data"][0]["text"], note_text)
        self.assertEqual(search_note_result["data"][0]["tweet_id"], eligible_post_id)

    # ================ COMPREHENSIVE COVERAGE FOR MISSING METHODS ================

    def test_set_current_user_success(self):
        """Test setting current user successfully."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.x_api.set_current_user(user_id)
        self.assertTrue(result["success"])
        self.assertEqual(self.x_api.current_user, user_id)

    def test_set_current_user_not_found(self):
        """Test setting non-existent user."""
        result = self.x_api.set_current_user("nonexistent_user")
        self.assertFalse(result["success"])
        self.assertIn("User not found", result["message"])

    def test_get_user_profile_success(self):
        """Test getting user profile successfully."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.x_api.get_user_profile(user_id)
        self.assertTrue(result["success"])
        self.assertIn("user", result)
        self.assertEqual(result["user"]["id"], user_id)

    def test_get_user_profile_not_found(self):
        """Test getting profile for non-existent user."""
        result = self.x_api.get_user_profile("nonexistent_user")
        self.assertFalse(result["success"])
        self.assertIn("User not found", result["message"])

    def test_list_followers_success(self):
        """Test listing user followers."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.x_api.list_followers(user_id)
        self.assertTrue(result["success"])
        self.assertIn("followers", result)
        self.assertIsInstance(result["followers"], list)

    def test_list_following_success(self):
        """Test listing users being followed."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.x_api.list_following(user_id)
        self.assertTrue(result["success"])
        self.assertIn("following", result)
        self.assertIsInstance(result["following"], list)

    def test_list_liked_posts_success(self):
        """Test listing user's liked posts."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.x_api.list_liked_posts(user_id)
        self.assertTrue(result["success"])
        self.assertIn("liked_posts", result)
        self.assertIsInstance(result["liked_posts"], list)

    def test_create_post_success(self):
        """Test creating a post successfully."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        post_text = "This is a test post from unit tests!"
        initial_post_count = len(self.x_api.posts)
        
        result = self.x_api.create_post(user_id, post_text)
        self.assertTrue(result["success"])
        self.assertIn("post", result)
        self.assertEqual(result["post"]["text"], post_text)
        self.assertEqual(result["post"]["author_id"], user_id)
        self.assertEqual(len(self.x_api.posts), initial_post_count + 1)

    def test_delete_post_success(self):
        """Test deleting a post successfully."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        
        # First create a post
        create_result = self.x_api.create_post(user_id, "Post to be deleted")
        post_id = create_result["post"]["id"]
        initial_post_count = len(self.x_api.posts)
        
        # Then delete it
        delete_result = self.x_api.delete_post(user_id, post_id)
        self.assertTrue(delete_result["success"])
        self.assertEqual(len(self.x_api.posts), initial_post_count - 1)
        self.assertNotIn(post_id, self.x_api.posts)

    def test_delete_post_not_found(self):
        """Test deleting non-existent post."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.x_api.delete_post(user_id, "nonexistent_post")
        self.assertFalse(result["success"])
        self.assertIn("Post not found", result["message"])

    def test_get_post_details_success(self):
        """Test getting post details."""
        post_id = list(DEFAULT_STATE["posts"].keys())[0]
        result = self.x_api.get_post_details(post_id)
        self.assertTrue(result["success"])
        self.assertIn("post", result)
        self.assertEqual(result["post"]["id"], post_id)

    def test_get_post_details_not_found(self):
        """Test getting details for non-existent post."""
        result = self.x_api.get_post_details("nonexistent_post")
        self.assertFalse(result["success"])
        self.assertIn("Post not found", result["message"])

    def test_list_user_posts_success(self):
        """Test listing user's posts."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.x_api.list_user_posts(user_id)
        self.assertTrue(result["success"])
        self.assertIn("posts", result)
        self.assertIsInstance(result["posts"], list)

    def test_like_unlike_post_operations(self):
        """Test comprehensive like/unlike post operations."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        post_id = list(DEFAULT_STATE["posts"].keys())[0]
        
        # Like post
        like_result = self.x_api.like_post(user_id, post_id)
        self.assertTrue(like_result["success"])
        
        # Check if post is in liked posts
        liked_posts_result = self.x_api.list_liked_posts(user_id)
        liked_post_ids = [p["id"] for p in liked_posts_result["liked_posts"]]
        self.assertIn(post_id, liked_post_ids)
        
        # Unlike post
        unlike_result = self.x_api.unlike_post(user_id, post_id)
        self.assertTrue(unlike_result["success"])
        
        # Check if post is no longer in liked posts
        liked_posts_after = self.x_api.list_liked_posts(user_id)
        liked_post_ids_after = [p["id"] for p in liked_posts_after["liked_posts"]]
        self.assertNotIn(post_id, liked_post_ids_after)

    def test_direct_message_operations_comprehensive(self):
        """Test comprehensive direct message operations."""
        user_id1 = list(DEFAULT_STATE["users"].keys())[0]
        user_id2 = list(DEFAULT_STATE["users"].keys())[1] if len(DEFAULT_STATE["users"]) > 1 else user_id1
        
        # List conversations
        conversations_result = self.x_api.list_direct_messages_conversations(user_id1)
        self.assertTrue(conversations_result["success"])
        self.assertIn("conversations", conversations_result)
        
        # Send direct message
        message_text = "Test DM from comprehensive test"
        send_result = self.x_api.send_direct_message(user_id1, user_id2, message_text)
        self.assertTrue(send_result["success"])
        self.assertIn("message", send_result)
        
        # Get conversation details
        if send_result.get("conversation_id"):
            conversation_id = send_result["conversation_id"]
            get_conversation_result = self.x_api.get_direct_messages_conversation(conversation_id)
            self.assertTrue(get_conversation_result["success"])
            self.assertIn("conversation", get_conversation_result)

    def test_api_usage_and_metrics(self):
        """Test API usage and metrics functionality."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        
        # Get API usage
        usage_result = self.x_api.get_api_usage(user_id)
        self.assertIn("data", usage_result)
        self.assertIn("user_id", usage_result["data"])
        
        # Get post metrics
        post_ids = list(DEFAULT_STATE["posts"].keys())[:2]  # Get first 2 posts
        metrics_result = self.x_api.get_post_metrics(post_ids)
        self.assertIn("data", metrics_result)
        self.assertIsInstance(metrics_result["data"], list)

    def test_user_profile_operations(self):
        """Test user profile update operations."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        new_bio = "Updated bio from unit tests"
        
        # Update bio
        update_result = self.x_api.update_user_bio(user_id, new_bio)
        self.assertTrue(update_result["success"])
        
        # Verify bio was updated
        profile_result = self.x_api.get_user_profile(user_id)
        if "bio" in profile_result["user"]:
            self.assertEqual(profile_result["user"]["bio"], new_bio)

    def test_get_user_analytics_success(self):
        """Test getting user analytics."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.x_api.get_user_analytics(user_id)
        self.assertTrue(result["success"])
        self.assertIn("analytics", result)
        self.assertIn("total_posts", result["analytics"])
        self.assertIn("total_followers", result["analytics"])
        self.assertIn("total_following", result["analytics"])

    def test_comprehensive_user_workflow(self):
        """Test a complete user workflow."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        
        # Set current user
        self.x_api.set_current_user(user_id)
        
        # Get profile
        profile_result = self.x_api.get_user_profile(user_id)
        self.assertTrue(profile_result["success"])
        
        # Create a post
        post_text = "Workflow test post"
        create_result = self.x_api.create_post(user_id, post_text)
        self.assertTrue(create_result["success"])
        post_id = create_result["post"]["id"]
        
        # Like the post
        like_result = self.x_api.like_post(user_id, post_id)
        self.assertTrue(like_result["success"])
        
        # Get post details
        details_result = self.x_api.get_post_details(post_id)
        self.assertTrue(details_result["success"])
        
        # List user posts
        posts_result = self.x_api.list_user_posts(user_id)
        self.assertTrue(posts_result["success"])
        
        # Get analytics
        analytics_result = self.x_api.get_user_analytics(user_id)
        self.assertTrue(analytics_result["success"])
        
        # Clean up - delete the post
        delete_result = self.x_api.delete_post(user_id, post_id)
        self.assertTrue(delete_result["success"])

    def test_error_handling_edge_cases(self):
        """Test various error handling scenarios."""
        # Test operations with invalid user IDs
        invalid_user_result = self.x_api.get_user_profile("invalid_user")
        self.assertFalse(invalid_user_result["success"])
        
        # Test operations with invalid post IDs
        invalid_post_result = self.x_api.get_post_details("invalid_post")
        self.assertFalse(invalid_post_result["success"])
        
        # Test delete operations on non-existent items
        delete_invalid_post = self.x_api.delete_post("user1", "invalid_post")
        self.assertFalse(delete_invalid_post["success"])

    def test_direct_message_conversation_management(self):
        """Test direct message conversation management."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        
        # List conversations
        conversations_result = self.x_api.list_direct_messages_conversations(user_id)
        self.assertTrue(conversations_result["success"])
        
        # If there are existing conversations, test getting conversation details
        if conversations_result["conversations"]:
            conversation_id = conversations_result["conversations"][0]["id"]
            
            # Get conversation details
            conversation_result = self.x_api.get_direct_messages_conversation(conversation_id)
            self.assertTrue(conversation_result["success"])
            
            # Test deleting conversation
            delete_result = self.x_api.delete_direct_message_conversation(user_id, conversation_id)
            self.assertTrue(delete_result["success"])

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
