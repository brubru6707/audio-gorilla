import unittest
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import API and helper
from YouTubeApis import YouTubeApis
from UnitTests.test_data_helper import BackendDataLoader

class TestYouTubeApis(unittest.TestCase):
    """
    Unit tests for the YouTubeApis class using OAuth 2.0 authentication.
    Tests the YouTube Data API v3 compatible implementation.
    """

    # Load real data from backend
    real_data = BackendDataLoader.get_youtube_data()
    
    # Extract real user data
    users = list(real_data.get("users", {}).values())
    user_data_alice = users[0] if users else {}
    user_data_bob = users[1] if len(users) > 1 else user_data_alice
    
    REAL_USER_ID_ALICE = user_data_alice.get("user_id", "user1")
    REAL_USER_ID_BOB = user_data_bob.get("user_id", "user2")
    REAL_EMAIL_ALICE = user_data_alice.get("email", "alice@example.com")
    REAL_EMAIL_BOB = user_data_bob.get("email", "bob@example.com")
    
    # Extract real channel data
    channels = list(real_data.get("channels", {}).values())
    channel_data = channels[0] if channels else {}
    REAL_CHANNEL_ID = next(iter(real_data.get("channels", {})), "channel1")
    
    # Extract real video data
    videos = list(real_data.get("videos", {}).values())
    video_data = videos[0] if videos else {}
    REAL_VIDEO_ID = next(iter(real_data.get("videos", {})), "video1")
    
    # Extract real playlist data
    playlists = list(real_data.get("playlists", {}).values())
    playlist_data = playlists[0] if playlists else {}
    REAL_PLAYLIST_ID = next(iter(real_data.get("playlists", {})), "playlist1")
    
    def setUp(self):
        """Set up the API instance using real data."""
        self.youtube_api = YouTubeApis()
        # Create access tokens for test users
        self.alice_token = f"token_{self.REAL_EMAIL_ALICE}"
        self.bob_token = f"token_{self.REAL_EMAIL_BOB}"

    # --- Authentication Tests ---
    def test_authenticate_alice(self):
        """Test authenticating as Alice."""
        result = self.youtube_api.authenticate(self.alice_token)
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#channel")
        self.assertIn("id", result)

    def test_authenticate_bob(self):
        """Test authenticating as Bob."""
        result = self.youtube_api.authenticate(self.bob_token)
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#channel")

    def test_authenticate_invalid_token(self):
        """Test authenticating with invalid token."""
        with self.assertRaises(Exception) as context:
            self.youtube_api.authenticate("invalid_token")
        self.assertIn("Invalid access token", str(context.exception))

    def test_ensure_authenticated_without_auth(self):
        """Test that methods requiring auth fail without authentication."""
        with self.assertRaises(Exception) as context:
            self.youtube_api.get_my_channel()
        self.assertIn("Authentication required", str(context.exception))

    # --- Channel Tests ---
    def test_get_my_channel(self):
        """Test getting authenticated user's channel."""
        self.youtube_api.authenticate(self.alice_token)
        result = self.youtube_api.get_my_channel()
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#channel")
        self.assertIn("snippet", result)
        self.assertIn("statistics", result)

    def test_list_my_channels(self):
        """Test listing all channels owned by authenticated user."""
        self.youtube_api.authenticate(self.alice_token)
        result = self.youtube_api.list_my_channels()
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#channelListResponse")
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)

    def test_get_channel_public(self):
        """Test getting channel details (public endpoint)."""
        result = self.youtube_api.get_channel(self.REAL_CHANNEL_ID)
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#channel")
        self.assertIn("id", result)
        self.assertEqual(result["id"], self.REAL_CHANNEL_ID)

    def test_get_channel_non_existent(self):
        """Test getting non-existent channel."""
        with self.assertRaises(Exception) as context:
            self.youtube_api.get_channel("nonexistent_channel")
        self.assertIn("Channel not found", str(context.exception))

    def test_create_channel(self):
        """Test creating a new channel."""
        self.youtube_api.authenticate(self.alice_token)
        result = self.youtube_api.create_channel(
            title="Test Channel",
            description="Test Description"
        )
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#channel")
        self.assertIn("id", result)
        self.assertEqual(result["snippet"]["title"], "Test Channel")

    def test_update_channel(self):
        """Test updating a channel."""
        self.youtube_api.authenticate(self.alice_token)
        result = self.youtube_api.update_channel(
            channel_id=self.REAL_CHANNEL_ID,
            title="Updated Title",
            description="Updated Description"
        )
        self.assertIn("kind", result)
        self.assertEqual(result["snippet"]["title"], "Updated Title")

    def test_update_channel_not_owner(self):
        """Test updating channel as non-owner fails."""
        self.youtube_api.authenticate(self.bob_token)
        with self.assertRaises(Exception) as context:
            self.youtube_api.update_channel(
                channel_id=self.REAL_CHANNEL_ID,
                title="Hacked Title"
            )
        self.assertIn("only the channel owner", str(context.exception).lower())

    # --- Video Tests ---
    def test_list_channel_videos(self):
        """Test listing videos in a channel (public endpoint)."""
        result = self.youtube_api.list_channel_videos(self.REAL_CHANNEL_ID)
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#videoListResponse")
        self.assertIn("items", result)
        self.assertIn("pageInfo", result)

    def test_list_channel_videos_with_pagination(self):
        """Test listing videos with pagination."""
        result = self.youtube_api.list_channel_videos(
            self.REAL_CHANNEL_ID, 
            maxResults=5
        )
        self.assertIn("pageInfo", result)
        self.assertEqual(result["pageInfo"]["resultsPerPage"], 5)

    def test_get_video(self):
        """Test getting video details (public endpoint)."""
        result = self.youtube_api.get_video(self.REAL_VIDEO_ID)
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#video")
        self.assertIn("snippet", result)
        self.assertIn("statistics", result)
        self.assertIn("contentDetails", result)

    def test_get_video_non_existent(self):
        """Test getting non-existent video."""
        with self.assertRaises(Exception) as context:
            self.youtube_api.get_video("nonexistent_video")
        self.assertIn("Video not found", str(context.exception))

    def test_upload_video(self):
        """Test uploading a video."""
        self.youtube_api.authenticate(self.alice_token)
        result = self.youtube_api.upload_video(
            title="Test Video",
            description="Test Description",
            duration_seconds=120,
            tags=["test", "upload"]
        )
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#video")
        self.assertIn("id", result)
        self.assertEqual(result["snippet"]["title"], "Test Video")

    def test_delete_video(self):
        """Test deleting a video."""
        self.youtube_api.authenticate(self.alice_token)
        # First upload a video
        upload_result = self.youtube_api.upload_video(title="Video to Delete")
        video_id = upload_result["id"]
        
        # Delete it (should not raise exception)
        self.youtube_api.delete_video(video_id)

    def test_delete_video_not_owner(self):
        """Test deleting video as non-owner fails."""
        self.youtube_api.authenticate(self.alice_token)
        upload_result = self.youtube_api.upload_video(title="Alice's Video")
        video_id = upload_result["id"]
        
        # Try to delete as Bob
        self.youtube_api.authenticate(self.bob_token)
        with self.assertRaises(Exception) as context:
            self.youtube_api.delete_video(video_id)
        self.assertIn("only the video owner", str(context.exception).lower())

    # --- Video Rating Tests ---
    def test_rate_video_like(self):
        """Test liking a video."""
        self.youtube_api.authenticate(self.alice_token)
        # Should not raise exception
        self.youtube_api.rate_video(self.REAL_VIDEO_ID, "like")

    def test_rate_video_remove_like(self):
        """Test removing a like from a video."""
        self.youtube_api.authenticate(self.alice_token)
        self.youtube_api.rate_video(self.REAL_VIDEO_ID, "like")
        # Remove like
        self.youtube_api.rate_video(self.REAL_VIDEO_ID, "none")

    def test_rate_video_invalid_rating(self):
        """Test rating video with invalid rating."""
        self.youtube_api.authenticate(self.alice_token)
        with self.assertRaises(Exception) as context:
            self.youtube_api.rate_video(self.REAL_VIDEO_ID, "dislike")
        self.assertIn("Invalid rating", str(context.exception))

    # --- Subscription Tests ---
    def test_list_my_subscriptions(self):
        """Test listing authenticated user's subscriptions."""
        self.youtube_api.authenticate(self.alice_token)
        result = self.youtube_api.list_my_subscriptions()
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#subscriptionListResponse")
        self.assertIn("items", result)
        self.assertIn("pageInfo", result)

    def test_subscribe(self):
        """Test subscribing to a channel."""
        self.youtube_api.authenticate(self.alice_token)
        result = self.youtube_api.subscribe(self.REAL_CHANNEL_ID)
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#subscription")
        self.assertIn("snippet", result)

    def test_subscribe_non_existent_channel(self):
        """Test subscribing to non-existent channel."""
        self.youtube_api.authenticate(self.alice_token)
        with self.assertRaises(Exception) as context:
            self.youtube_api.subscribe("nonexistent_channel")
        self.assertIn("Channel not found", str(context.exception))

    def test_unsubscribe(self):
        """Test unsubscribing from a channel."""
        self.youtube_api.authenticate(self.alice_token)
        # Subscribe first
        self.youtube_api.subscribe(self.REAL_CHANNEL_ID)
        # Unsubscribe (should not raise exception)
        self.youtube_api.unsubscribe(self.REAL_CHANNEL_ID)

    def test_unsubscribe_not_subscribed(self):
        """Test unsubscribing from channel not subscribed to."""
        self.youtube_api.authenticate(self.bob_token)
        with self.assertRaises(Exception) as context:
            self.youtube_api.unsubscribe(self.REAL_CHANNEL_ID)
        self.assertIn("not subscribed", str(context.exception).lower())

    # --- Search Tests ---
    def test_search_videos(self):
        """Test searching for videos."""
        result = self.youtube_api.search_videos(query="test")
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#searchListResponse")
        self.assertIn("items", result)
        self.assertIn("pageInfo", result)

    def test_search_videos_with_max_results(self):
        """Test searching with maxResults."""
        result = self.youtube_api.search_videos(query="music", maxResults=5)
        self.assertIn("pageInfo", result)
        self.assertEqual(result["pageInfo"]["resultsPerPage"], 5)

    def test_search_videos_empty_query(self):
        """Test searching with empty query."""
        with self.assertRaises(Exception) as context:
            self.youtube_api.search_videos(query="")
        self.assertIn("Query parameter is required", str(context.exception))

    # --- Playlist Tests ---
    def test_list_playlists_in_channel(self):
        """Test listing playlists in a channel."""
        result = self.youtube_api.list_playlists_in_channel(self.REAL_CHANNEL_ID)
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#playlistListResponse")
        self.assertIn("items", result)

    def test_get_playlist_details(self):
        """Test getting playlist details."""
        result = self.youtube_api.get_playlist_details(self.REAL_PLAYLIST_ID)
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#playlist")
        self.assertIn("snippet", result)
        self.assertIn("items", result)

    def test_get_playlist_non_existent(self):
        """Test getting non-existent playlist."""
        with self.assertRaises(Exception) as context:
            self.youtube_api.get_playlist_details("nonexistent_playlist")
        self.assertIn("Playlist not found", str(context.exception))

    def test_create_playlist(self):
        """Test creating a playlist."""
        self.youtube_api.authenticate(self.alice_token)
        result = self.youtube_api.create_playlist(
            title="Test Playlist",
            description="Test Description",
            privacy_status="private"
        )
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#playlist")
        self.assertIn("id", result)
        self.assertEqual(result["snippet"]["title"], "Test Playlist")

    def test_add_video_to_playlist(self):
        """Test adding video to playlist."""
        self.youtube_api.authenticate(self.alice_token)
        # Create a playlist
        playlist_result = self.youtube_api.create_playlist(title="Test Playlist")
        playlist_id = playlist_result["id"]
        
        # Add video
        result = self.youtube_api.add_video_to_playlist(playlist_id, self.REAL_VIDEO_ID)
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#playlistItem")

    def test_add_video_to_playlist_not_owner(self):
        """Test adding video to playlist as non-owner fails."""
        # Create a playlist as Alice
        self.youtube_api.authenticate(self.alice_token)
        playlist_result = self.youtube_api.create_playlist(title="Alice's Playlist")
        alice_playlist_id = playlist_result["id"]
        
        # Try to add video as Bob (should fail)
        self.youtube_api.authenticate(self.bob_token)
        with self.assertRaises(Exception) as context:
            self.youtube_api.add_video_to_playlist(alice_playlist_id, self.REAL_VIDEO_ID)
        self.assertIn("only the playlist owner", str(context.exception).lower())

    def test_remove_video_from_playlist(self):
        """Test removing video from playlist."""
        self.youtube_api.authenticate(self.alice_token)
        # Create playlist and add video
        playlist_result = self.youtube_api.create_playlist(title="Test Playlist")
        playlist_id = playlist_result["id"]
        self.youtube_api.add_video_to_playlist(playlist_id, self.REAL_VIDEO_ID)
        
        # Remove video (should not raise exception)
        self.youtube_api.remove_video_from_playlist(playlist_id, self.REAL_VIDEO_ID)

    # --- Comment Tests ---
    def test_add_comment_to_video(self):
        """Test adding a comment to a video."""
        self.youtube_api.authenticate(self.alice_token)
        result = self.youtube_api.add_comment_to_video(
            self.REAL_VIDEO_ID,
            "Great video!"
        )
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#comment")
        self.assertIn("snippet", result)
        self.assertEqual(result["snippet"]["textDisplay"], "Great video!")

    def test_add_comment_empty_text(self):
        """Test adding comment with empty text."""
        self.youtube_api.authenticate(self.alice_token)
        with self.assertRaises(Exception) as context:
            self.youtube_api.add_comment_to_video(self.REAL_VIDEO_ID, "")
        self.assertIn("Comment text cannot be empty", str(context.exception))

    def test_list_comments_for_video(self):
        """Test listing comments for a video."""
        result = self.youtube_api.list_comments_for_video(self.REAL_VIDEO_ID)
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "youtube#commentThreadListResponse")
        self.assertIn("items", result)
        self.assertIn("pageInfo", result)

    def test_list_comments_with_pagination(self):
        """Test listing comments with pagination."""
        result = self.youtube_api.list_comments_for_video(
            self.REAL_VIDEO_ID,
            maxResults=10
        )
        self.assertIn("pageInfo", result)
        self.assertEqual(result["pageInfo"]["resultsPerPage"], 10)

    def test_delete_comment(self):
        """Test deleting a comment."""
        self.youtube_api.authenticate(self.alice_token)
        # Add a comment
        comment_result = self.youtube_api.add_comment_to_video(
            self.REAL_VIDEO_ID,
            "Comment to delete"
        )
        comment_id = comment_result["id"]
        
        # Delete it (should not raise exception)
        self.youtube_api.delete_comment(comment_id)

    # --- Helper Method Tests (Legacy endpoints) ---
    def test_get_user_by_email(self):
        """Test getting user by email (legacy helper method)."""
        result = self.youtube_api.get_user_by_email(self.REAL_EMAIL_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"])

    def test_get_user_by_display_name(self):
        """Test getting user by display name (legacy helper method)."""
        result = self.youtube_api.get_user_by_display_name("Alice")
        self.assertIn("data", result)

    def test_get_watch_later_playlist(self):
        """Test getting watch later playlist (legacy helper method)."""
        result = self.youtube_api.get_watch_later_playlist(self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)

    def test_add_to_watch_later(self):
        """Test adding to watch later (legacy helper method)."""
        result = self.youtube_api.add_to_watch_later(
            self.REAL_USER_ID_ALICE,
            self.REAL_VIDEO_ID
        )
        self.assertTrue(result.get("status", False))

    def test_get_notification_settings(self):
        """Test getting notification settings (legacy helper method)."""
        result = self.youtube_api.get_notification_settings(self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)

    def test_update_notification_settings(self):
        """Test updating notification settings (legacy helper method)."""
        settings = {"email_notifications": True}
        result = self.youtube_api.update_notification_settings(
            self.REAL_USER_ID_ALICE,
            settings
        )
        self.assertTrue(result.get("status", False))

    # --- Caption Tests ---
    def test_youtube_captions_insert(self):
        """Test inserting captions (legacy method)."""
        result = self.youtube_api.youtube_captions_insert(
            self.REAL_VIDEO_ID,
            "en",
            "Test caption content"
        )
        self.assertTrue(result.get("status", False))

    # --- Reset Data Tests ---
    def test_reset_data(self):
        """Test resetting data clears authentication."""
        self.youtube_api.authenticate(self.alice_token)
        self.assertIsNotNone(self.youtube_api.access_token)
        
        # Reset
        self.youtube_api.reset_data()
        
        # Should be cleared
        self.assertIsNone(self.youtube_api.access_token)
        self.assertIsNone(self.youtube_api.current_user_id)

    # --- Integration Workflow Tests ---
    def test_video_upload_workflow(self):
        """Test complete video upload and interaction workflow."""
        self.youtube_api.authenticate(self.alice_token)
        
        # Upload video
        upload_result = self.youtube_api.upload_video(
            title="Workflow Test Video",
            description="Testing workflow",
            tags=["test", "workflow"]
        )
        self.assertIn("id", upload_result)
        video_id = upload_result["id"]
        
        # Get video details (public)
        video = self.youtube_api.get_video(video_id)
        self.assertEqual(video["snippet"]["title"], "Workflow Test Video")
        
        # Rate video
        self.youtube_api.rate_video(video_id, "like")
        
        # Add comment
        comment = self.youtube_api.add_comment_to_video(video_id, "Great video!")
        self.assertIn("id", comment)
        
        # List comments
        comments = self.youtube_api.list_comments_for_video(video_id)
        self.assertGreater(len(comments["items"]), 0)

    def test_playlist_workflow(self):
        """Test complete playlist management workflow."""
        self.youtube_api.authenticate(self.alice_token)
        
        # Create playlist
        playlist = self.youtube_api.create_playlist(
            title="Workflow Playlist",
            description="Testing playlist workflow"
        )
        playlist_id = playlist["id"]
        
        # Add video to playlist
        item = self.youtube_api.add_video_to_playlist(playlist_id, self.REAL_VIDEO_ID)
        self.assertIn("kind", item)
        
        # Get playlist details
        details = self.youtube_api.get_playlist_details(playlist_id)
        self.assertGreater(len(details["items"]), 0)
        
        # Remove video from playlist
        self.youtube_api.remove_video_from_playlist(playlist_id, self.REAL_VIDEO_ID)

    def test_channel_subscription_workflow(self):
        """Test channel subscription workflow."""
        self.youtube_api.authenticate(self.bob_token)
        
        # Subscribe to channel
        subscription = self.youtube_api.subscribe(self.REAL_CHANNEL_ID)
        self.assertIn("kind", subscription)
        
        # List subscriptions
        subs = self.youtube_api.list_my_subscriptions()
        self.assertGreater(len(subs["items"]), 0)
        
        # Unsubscribe
        self.youtube_api.unsubscribe(self.REAL_CHANNEL_ID)

if __name__ == "__main__":
    unittest.main()
