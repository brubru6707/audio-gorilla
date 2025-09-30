import unittest
from copy import deepcopy
from YouTubeApis import YouTubeApis, DEFAULT_STATE

class TestYouTubeApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh YouTubeApis instance for each test."""
        self.youtube_api = YouTubeApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.youtube_api._load_scenario(deepcopy(DEFAULT_STATE))

    # Unit Tests for Individual Audio/Caption Related Functions

    def test_youtube_captions_insert_success(self):
        """Test inserting a new caption track successfully."""
        # Ensure a video exists in the current channel for caption insertion
        self.youtube_api.current_channel = "channel1@example.com"
        video_id = "videoABC"
        initial_caption_count = len(self.youtube_api.channels[self.youtube_api.current_channel].get("captions", {}))

        result = self.youtube_api.youtube_captions_insert(
            part="snippet",
            video_id=video_id,
            language="es",
            name="Spanish Captions"
        )
        self.assertTrue(result["success"])
        self.assertIn("caption_id", result)
        self.assertEqual(result["video_id"], video_id)
        self.assertEqual(result["language"], "es")

        # Verify the caption was added to the channel's captions
        updated_captions = self.youtube_api.channels[self.youtube_api.current_channel]["captions"]
        self.assertEqual(len(updated_captions), initial_caption_count + 1)
        new_caption_id = result["caption_id"]
        self.assertIn(new_caption_id, updated_captions)
        self.assertEqual(updated_captions[new_caption_id]["language"], "es")
        self.assertEqual(updated_captions[new_caption_id]["name"], "Spanish Captions")

    def test_youtube_captions_insert_no_current_channel(self):
        """Test inserting caption without a current channel set."""
        self.youtube_api.current_channel = None
        result = self.youtube_api.youtube_captions_insert(
            part="snippet",
            video_id="videoABC",
            language="fr"
        )
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No current channel set.")

    def test_youtube_captions_insert_video_not_found(self):
        """Test inserting caption for a video that doesn't exist in the current channel."""
        self.youtube_api.current_channel = "channel1@example.com"
        result = self.youtube_api.youtube_captions_insert(
            part="snippet",
            video_id="nonExistentVideo",
            language="fr"
        )
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Video not found in current channel.")

    def test_youtube_captions_list_success(self):
        """Test listing caption tracks for a video."""
        self.youtube_api.current_channel = "channel1@example.com"
        video_id = "videoABC"
        result = self.youtube_api.youtube_captions_list(part="snippet", video_id=video_id)
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)
        self.assertGreater(len(result["items"]), 0)
        self.assertEqual(result["items"][0]["snippet"]["videoId"], video_id)
        self.assertEqual(result["items"][0]["snippet"]["language"], "en")

    def test_youtube_captions_list_no_current_channel(self):
        """Test listing captions without a current channel set."""
        self.youtube_api.current_channel = None
        result = self.youtube_api.youtube_captions_list(part="snippet", video_id="videoABC")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No current channel set.")

    def test_youtube_captions_list_no_captions_for_video(self):
        """Test listing captions for a video with no captions."""
        self.youtube_api.current_channel = "channel2@example.com" # channel2 has no captions
        result = self.youtube_api.youtube_captions_list(part="snippet", video_id="someVideo")
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 0)

    def test_youtube_captions_update_success(self):
        """Test updating an existing caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        caption_id = "caption1"
        new_name = "Updated English Captions"
        result = self.youtube_api.youtube_captions_update(
            part="snippet",
            caption_id=caption_id,
            is_draft=True,
            file_path="/new/path/to/captions1.vtt"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["caption_id"], caption_id)
        self.assertTrue(self.youtube_api.channels[self.youtube_api.current_channel]["captions"][caption_id]["is_draft"])
        self.assertEqual(self.youtube_api.channels[self.youtube_api.current_channel]["captions"][caption_id]["file_path"], "/new/path/to/captions1.vtt")

    def test_youtube_captions_update_not_found(self):
        """Test updating a non-existent caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        result = self.youtube_api.youtube_captions_update(
            part="snippet",
            caption_id="nonExistentCaption",
            is_draft=True
        )
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Caption track not found.")

    def test_youtube_captions_download_success(self):
        """Test downloading a caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        caption_id = "caption1"
        result = self.youtube_api.youtube_captions_download(id=caption_id, tfmt="srt")
        self.assertTrue(result["success"])
        self.assertEqual(result["caption_id"], caption_id)
        self.assertIn("content", result)
        self.assertIsInstance(result["content"], str)
        self.assertIn("dummy caption", result["content"])

    def test_youtube_captions_download_not_found(self):
        """Test downloading a non-existent caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        result = self.youtube_api.youtube_captions_download(id="nonExistentCaption")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Caption track not found.")

    def test_youtube_captions_delete_success(self):
        """Test deleting a caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        caption_id_to_delete = "caption1"
        initial_caption_count = len(self.youtube_api.channels[self.youtube_api.current_channel].get("captions", {}))

        result = self.youtube_api.youtube_captions_delete(id=caption_id_to_delete)
        self.assertTrue(result["success"])
        self.assertEqual(result["deleted_caption_id"], caption_id_to_delete)
        self.assertEqual(len(self.youtube_api.channels[self.youtube_api.current_channel]["captions"]), initial_caption_count - 1)
        self.assertNotIn(caption_id_to_delete, self.youtube_api.channels[self.youtube_api.current_channel]["captions"])

    def test_youtube_captions_delete_not_found(self):
        """Test deleting a non-existent caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        result = self.youtube_api.youtube_captions_delete(id="nonExistentCaption")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Caption track not found.")

    def test_youtube_videos_rate_success(self):
        """Test rating a video."""
        video_id = "videoABC"
        result = self.youtube_api.youtube_videos_rate(id=video_id, rating="like")
        self.assertTrue(result["success"])
        self.assertEqual(result["video_id"], video_id)
        self.assertEqual(result["rating"], "like")

    def test_youtube_videos_rate_invalid_rating(self):
        """Test rating a video with an invalid rating."""
        video_id = "videoABC"
        result = self.youtube_api.youtube_videos_rate(id=video_id, rating="invalid")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid rating. Must be 'like', 'dislike', or 'none'.")

    def test_youtube_videos_get_rating_success(self):
        """Test getting a video's rating."""
        video_id = "videoABC"
        result = self.youtube_api.youtube_videos_get_rating(id=video_id)
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["videoId"], video_id)
        self.assertEqual(result["items"][0]["rating"], "none") # Dummy backend always returns 'none'

    # Combined Functionality Tests

    def test_caption_workflow_insert_list_update_delete(self):
        """
        Combined test: Insert a caption, list it, update it, and then delete it.
        """
        self.youtube_api.current_channel = "channel1@example.com"
        video_id = "videoABC"
        initial_caption_count = len(self.youtube_api.channels[self.youtube_api.current_channel].get("captions", {}))

        # 1. Insert a caption
        insert_result = self.youtube_api.youtube_captions_insert(
            part="snippet",
            video_id=video_id,
            language="fr",
            name="French Captions for Workflow Test"
        )
        self.assertTrue(insert_result["success"])
        new_caption_id = insert_result["caption_id"]
        self.assertEqual(len(self.youtube_api.channels[self.youtube_api.current_channel]["captions"]), initial_caption_count + 1)

        # 2. List captions and verify the new caption is present
        list_result_after_insert = self.youtube_api.youtube_captions_list(part="snippet", video_id=video_id)
        self.assertTrue(any(item["id"] == new_caption_id for item in list_result_after_insert["items"]))

        # 3. Update the caption
        update_result = self.youtube_api.youtube_captions_update(
            part="snippet",
            caption_id=new_caption_id,
            is_draft=True
        )
        self.assertTrue(update_result["success"])
        self.assertTrue(self.youtube_api.channels[self.youtube_api.current_channel]["captions"][new_caption_id]["is_draft"])

        # 4. Delete the caption
        delete_result = self.youtube_api.youtube_captions_delete(id=new_caption_id)
        self.assertTrue(delete_result["success"])
        self.assertEqual(self.youtube_api.channels[self.youtube_api.current_channel]["captions"].get(new_caption_id), None)
        self.assertEqual(len(self.youtube_api.channels[self.youtube_api.current_channel]["captions"]), initial_caption_count)

        # 5. Verify it's no longer in the list
        list_result_after_delete = self.youtube_api.youtube_captions_list(part="snippet", video_id=video_id)
        self.assertFalse(any(item["id"] == new_caption_id for item in list_result_after_delete["items"]))

    def test_video_rating_and_retrieval(self):
        """
        Combined test: Rate a video and then retrieve its rating.
        Note: Dummy backend always returns 'none' for get_rating.
        """
        video_id = "videoDEF" # Use a different video
        
        # 1. Rate the video as 'like'
        rate_result_like = self.youtube_api.youtube_videos_rate(id=video_id, rating="like")
        self.assertTrue(rate_result_like["success"])
        self.assertEqual(rate_result_like["rating"], "like")

        # 2. Retrieve the rating (will still be 'none' due to dummy backend)
        get_rating_result_like = self.youtube_api.youtube_videos_get_rating(id=video_id)
        self.assertIn("items", get_rating_result_like)
        self.assertEqual(get_rating_result_like["items"][0]["rating"], "none")

        # 3. Rate the video as 'dislike'
        rate_result_dislike = self.youtube_api.youtube_videos_rate(id=video_id, rating="dislike")
        self.assertTrue(rate_result_dislike["success"])
        self.assertEqual(rate_result_dislike["rating"], "dislike")

        # 4. Retrieve the rating again (will still be 'none' due to dummy backend)
        get_rating_result_dislike = self.youtube_api.youtube_videos_get_rating(id=video_id)
        self.assertIn("items", get_rating_result_dislike)
        self.assertEqual(get_rating_result_dislike["items"][0]["rating"], "none")

    def test_comment_thread_creation_and_reply(self):
        """
        Combined test: Create a comment thread and then add a reply to it.
        """
        self.youtube_api.current_channel = "channel1@example.com"
        video_id = "videoABC"
        initial_thread_count = len(self.youtube_api.comment_threads)
        initial_comment_count = len(self.youtube_api.comments)

        # 1. Create a new comment thread
        thread_text = "What are your thoughts on this video?"
        create_thread_result = self.youtube_api.youtube_comment_threads_insert(
            part="snippet",
            video_id=video_id,
            text_original=thread_text
        )
        self.assertTrue(create_thread_result["success"])
        new_thread_id = create_thread_result["thread_id"]
        self.assertEqual(len(self.youtube_api.comment_threads), initial_thread_count + 1)
        self.assertEqual(self.youtube_api.comment_threads[new_thread_id]["text_original"], thread_text)

        # 2. Add a reply to the newly created thread
        reply_text = "I think it's great!"
        create_reply_result = self.youtube_api.youtube_comments_insert(
            part="snippet",
            parent_id=new_thread_id,
            text_original=reply_text
        )
        self.assertTrue(create_reply_result["success"])
        new_reply_id = create_reply_result["comment_id"]
        self.assertEqual(len(self.youtube_api.comments), initial_comment_count + 1)
        self.assertEqual(self.youtube_api.comments[new_reply_id]["text_original"], reply_text)
        self.assertIn(new_reply_id, self.youtube_api.comment_threads[new_thread_id]["replies"])

        # 3. List comment threads and verify the reply count
        list_threads_result = self.youtube_api.youtube_comment_threads_list(
            part="snippet,replies",
            video_id=video_id,
            id=new_thread_id
        )
        self.assertEqual(len(list_threads_result["items"]), 1)
        retrieved_thread = list_threads_result["items"][0]
        self.assertEqual(retrieved_thread["snippet"]["totalReplyCount"], 1)
        self.assertEqual(retrieved_thread["replies"]["comments"][0]["id"], new_reply_id)

        # 4. Delete the thread (should also delete the reply in this dummy implementation)
        delete_thread_result = self.youtube_api.youtube_comments_delete(id=new_thread_id)
        self.assertTrue(delete_thread_result["success"])
        self.assertNotIn(new_thread_id, self.youtube_api.comment_threads)
        self.assertNotIn(new_reply_id, self.youtube_api.comments) # Verify reply is also gone

    # ================ COMPREHENSIVE COVERAGE FOR MISSING METHODS ================

    def test_set_current_user_success(self):
        """Test setting current user successfully."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.youtube_api.set_current_user(user_id)
        self.assertTrue(result["success"])
        self.assertEqual(self.youtube_api.current_user, user_id)

    def test_set_current_user_not_found(self):
        """Test setting non-existent user."""
        result = self.youtube_api.set_current_user("nonexistent_user")
        self.assertFalse(result["success"])
        self.assertIn("User not found", result["message"])

    def test_set_current_channel_success(self):
        """Test setting current channel successfully."""
        channel_id = list(DEFAULT_STATE["channels"].keys())[0]
        result = self.youtube_api.set_current_channel(channel_id)
        self.assertTrue(result["success"])
        self.assertEqual(self.youtube_api.current_channel, channel_id)

    def test_get_user_profile_success(self):
        """Test getting user profile."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.youtube_api.get_user_profile(user_id)
        self.assertTrue(result["success"])
        self.assertIn("user", result)
        self.assertEqual(result["user"]["user_id"], user_id)

    def test_get_watch_history_success(self):
        """Test getting user watch history."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.youtube_api.get_watch_history(user_id)
        self.assertTrue(result["success"])
        self.assertIn("watch_history", result)

    def test_list_subscriptions_success(self):
        """Test listing user subscriptions."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.youtube_api.list_subscriptions(user_id)
        self.assertTrue(result["success"])
        self.assertIn("subscriptions", result)

    def test_youtube_subscriptions_insert_success(self):
        """Test subscribing to a channel."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        channel_id = list(DEFAULT_STATE["channels"].keys())[0]
        
        result = self.youtube_api.youtube_subscriptions_insert(channel_id, user_id)
        self.assertTrue(result["success"])
        self.assertIn("subscription_id", result)

    def test_youtube_subscriptions_delete_success(self):
        """Test unsubscribing from a channel."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        channel_id = list(DEFAULT_STATE["channels"].keys())[0]
        
        # First subscribe
        self.youtube_api.youtube_subscriptions_insert(channel_id, user_id)
        
        # Then unsubscribe
        result = self.youtube_api.youtube_subscriptions_delete(channel_id, user_id)
        self.assertTrue(result["success"])

    def test_list_channels_for_user_success(self):
        """Test listing channels for a user."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.youtube_api.list_channels_for_user(user_id)
        self.assertTrue(result["success"])
        self.assertIn("channels", result)

    def test_get_channel_details_success(self):
        """Test getting channel details."""
        channel_id = list(DEFAULT_STATE["channels"].keys())[0]
        result = self.youtube_api.get_channel_details(channel_id)
        self.assertTrue(result["success"])
        self.assertIn("channel", result)

    def test_create_channel_success(self):
        """Test creating a new channel."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        result = self.youtube_api.create_channel(
            user_id=user_id,
            title="Test Channel",
            description="A test channel"
        )
        self.assertTrue(result["success"])
        self.assertIn("channel_id", result)

    def test_youtube_channels_update_success(self):
        """Test updating channel information."""
        channel_id = list(DEFAULT_STATE["channels"].keys())[0]
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        
        updates = {"title": "Updated Channel Title", "description": "Updated description"}
        result = self.youtube_api.youtube_channels_update(channel_id, updates, user_id)
        self.assertTrue(result["success"])

    def test_youtube_channel_banners_insert_success(self):
        """Test uploading channel banner."""
        channel_id = list(DEFAULT_STATE["channels"].keys())[0]
        result = self.youtube_api.youtube_channel_banners_insert(
            image_path="/path/to/banner.jpg",
            channel_id=channel_id
        )
        self.assertTrue(result["success"])

    def test_list_videos_in_channel_success(self):
        """Test listing videos in a channel."""
        channel_id = list(DEFAULT_STATE["channels"].keys())[0]
        result = self.youtube_api.list_videos_in_channel(channel_id)
        self.assertTrue(result["success"])
        self.assertIn("videos", result)

    def test_get_video_details_success(self):
        """Test getting video details."""
        video_id = list(DEFAULT_STATE["videos"].keys())[0]
        result = self.youtube_api.get_video_details(video_id)
        self.assertTrue(result["success"])
        self.assertIn("video", result)

    def test_upload_video_success(self):
        """Test uploading a video."""
        channel_id = list(DEFAULT_STATE["channels"].keys())[0]
        result = self.youtube_api.upload_video(
            channel_id=channel_id,
            title="Test Video",
            description="A test video",
            duration_seconds=120,
            tags=["test", "video"]
        )
        self.assertTrue(result["success"])
        self.assertIn("video_id", result)

    def test_delete_video_success(self):
        """Test deleting a video."""
        # First upload a video
        channel_id = list(DEFAULT_STATE["channels"].keys())[0]
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        upload_result = self.youtube_api.upload_video(
            channel_id=channel_id,
            title="Video to Delete",
            description="Will be deleted"
        )
        video_id = upload_result["video_id"]
        
        # Then delete it
        result = self.youtube_api.delete_video(video_id, channel_id, user_id)
        self.assertTrue(result["success"])

    def test_like_unlike_video_success(self):
        """Test liking and unliking a video."""
        video_id = list(DEFAULT_STATE["videos"].keys())[0]
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        
        # Like video
        like_result = self.youtube_api.like_video(video_id, user_id)
        self.assertTrue(like_result["success"])
        
        # Unlike video
        unlike_result = self.youtube_api.unlike_video(video_id, user_id)
        self.assertTrue(unlike_result["success"])

    def test_search_videos_success(self):
        """Test searching for videos."""
        result = self.youtube_api.search_videos("test", max_results=5)
        self.assertTrue(result["success"])
        self.assertIn("videos", result)
        self.assertLessEqual(len(result["videos"]), 5)

    def test_playlist_operations_comprehensive(self):
        """Test comprehensive playlist operations."""
        channel_id = list(DEFAULT_STATE["channels"].keys())[0]
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        video_id = list(DEFAULT_STATE["videos"].keys())[0]
        
        # 1. List playlists in channel
        list_result = self.youtube_api.list_playlists_in_channel(channel_id)
        self.assertTrue(list_result["success"])
        
        # 2. Create new playlist
        create_result = self.youtube_api.create_playlist(
            channel_id=channel_id,
            title="Test Playlist",
            description="A test playlist",
            privacy_status="public"
        )
        self.assertTrue(create_result["success"])
        playlist_id = create_result["playlist_id"]
        
        # 3. Get playlist details
        details_result = self.youtube_api.get_playlist_details(playlist_id)
        self.assertTrue(details_result["success"])
        
        # 4. Add video to playlist
        add_result = self.youtube_api.add_video_to_playlist(playlist_id, video_id, user_id)
        self.assertTrue(add_result["success"])
        
        # 5. Remove video from playlist
        remove_result = self.youtube_api.remove_video_from_playlist(playlist_id, video_id, user_id)
        self.assertTrue(remove_result["success"])

    def test_comment_operations_comprehensive(self):
        """Test comprehensive comment operations."""
        video_id = list(DEFAULT_STATE["videos"].keys())[0]
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        
        # 1. Add comment to video
        add_result = self.youtube_api.add_comment_to_video(
            video_id=video_id,
            author_id=user_id,
            text="This is a test comment"
        )
        self.assertTrue(add_result["success"])
        comment_id = add_result["comment_id"]
        
        # 2. List comments for video
        list_result = self.youtube_api.list_comments_for_video(video_id)
        self.assertTrue(list_result["success"])
        self.assertIn("comments", list_result)
        
        # 3. Delete comment
        delete_result = self.youtube_api.delete_comment(comment_id, user_id)
        self.assertTrue(delete_result["success"])

    def test_watch_later_operations(self):
        """Test watch later playlist operations."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        video_id = list(DEFAULT_STATE["videos"].keys())[0]
        
        # 1. Get watch later playlist
        playlist_result = self.youtube_api.get_watch_later_playlist(user_id)
        self.assertTrue(playlist_result["success"])
        
        # 2. Add to watch later
        add_result = self.youtube_api.add_to_watch_later(user_id, video_id)
        self.assertTrue(add_result["success"])
        
        # 3. Remove from watch later
        remove_result = self.youtube_api.remove_from_watch_later(user_id, video_id)
        self.assertTrue(remove_result["success"])

    def test_user_settings_operations(self):
        """Test user settings operations."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        
        # 1. Get notification settings
        notifications_result = self.youtube_api.get_notification_settings(user_id)
        self.assertTrue(notifications_result["success"])
        
        # 2. Update notification settings
        settings = {"email_notifications": True, "push_notifications": False}
        update_result = self.youtube_api.update_notification_settings(user_id, settings)
        self.assertTrue(update_result["success"])
        
        # 3. Get language preference
        lang_result = self.youtube_api.get_user_language_preference(user_id)
        self.assertTrue(lang_result["success"])
        
        # 4. Update language preference
        lang_update_result = self.youtube_api.update_language_preference(user_id, "en")
        self.assertTrue(lang_update_result["success"])

    def test_user_analytics_and_history(self):
        """Test user analytics and history operations."""
        user_id = list(DEFAULT_STATE["users"].keys())[0]
        channel_id = list(DEFAULT_STATE["channels"].keys())[0]
        
        # 1. Get account status
        status_result = self.youtube_api.get_account_status(user_id)
        self.assertTrue(status_result["success"])
        
        # 2. Get channel history
        history_result = self.youtube_api.get_channel_history(user_id)
        self.assertTrue(history_result["success"])
        
        # 3. Add to channel history
        add_history_result = self.youtube_api.add_to_channel_history(user_id, channel_id)
        self.assertTrue(add_history_result["success"])
        
        # 4. Get user analytics
        analytics_result = self.youtube_api.get_user_analytics(user_id)
        self.assertTrue(analytics_result["success"])

    def test_user_lookup_operations(self):
        """Test user lookup operations."""
        # Get sample user data
        user_data = list(DEFAULT_STATE["users"].values())[0]
        email = user_data.get("email", "test@example.com")
        display_name = user_data.get("display_name", "TestUser")
        
        # 1. Get user by email
        email_result = self.youtube_api.get_user_by_email(email)
        self.assertTrue(email_result["success"])
        
        # 2. Get user by display name
        name_result = self.youtube_api.get_user_by_display_name(display_name)
        self.assertTrue(name_result["success"])

    def test_search_users_by_language(self):
        """Test searching users by language preference."""
        result = self.youtube_api.search_users_by_language("en")
        self.assertTrue(result["success"])
        self.assertIn("users", result)

    def test_reset_data(self):
        """Test resetting API data."""
        result = self.youtube_api.reset_data()
        self.assertTrue(result["success"])

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
