import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import API and helper
from YouTubeApis import YouTubeApis
from UnitTests.test_data_helper import BackendDataLoader

class TestYouTubeApis(unittest.TestCase):
    """
    Unit tests for the YouTubeApis class, covering multi-user functionality.
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
    REAL_DISPLAY_NAME_ALICE = user_data_alice.get("display_name", "Alice")
    REAL_DISPLAY_NAME_BOB = user_data_bob.get("display_name", "Bob")
    
    # Extract real channel data
    channels = list(real_data.get("channels", {}).values())
    channel_data = channels[0] if channels else {}
    REAL_CHANNEL_ID = next(iter(real_data.get("channels", {})), "channel1")
    REAL_CHANNEL_TITLE = channel_data.get("title", "Test Channel")
    
    # Extract real video data
    videos = list(real_data.get("videos", {}).values())
    video_data = videos[0] if videos else {}
    REAL_VIDEO_ID = next(iter(real_data.get("videos", {})), "video1")
    REAL_VIDEO_TITLE = video_data.get("title", "Test Video")
    
    # Extract real playlist data
    playlists = list(real_data.get("playlists", {}).values())
    playlist_data = playlists[0] if playlists else {}
    REAL_PLAYLIST_ID = next(iter(real_data.get("playlists", {})), "playlist1")
    REAL_PLAYLIST_TITLE = playlist_data.get("title", "Test Playlist")
    
    # Extract real comment data
    comments = list(real_data.get("comments", {}).values())
    comment_data = comments[0] if comments else {}
    REAL_COMMENT_ID = next(iter(real_data.get("comments", {})), "comment1")
    
    def setUp(self):
        """Set up the API instance using real data."""
        self.youtube_api = YouTubeApis()

    # --- User Management Tests ---
    def test_set_current_user_alice(self):
        """Test setting current user to Alice."""
        result = self.youtube_api.set_current_user(user_id=self.REAL_USER_ID_ALICE)
        self.assertTrue(result.get("status", False))

    def test_set_current_user_bob(self):
        """Test setting current user to Bob."""
        result = self.youtube_api.set_current_user(user_id=self.REAL_USER_ID_BOB)
        self.assertTrue(result.get("status", False))

    def test_set_current_user_non_existent(self):
        """Test setting current user to non-existent user."""
        result = self.youtube_api.set_current_user(user_id="nonexistent_user")
        self.assertFalse(result.get("status", True))

    def test_set_current_channel_existing(self):
        """Test setting current channel to existing channel."""
        # First set current user to Alice (owner of the channel)
        self.youtube_api.set_current_user(user_id=self.REAL_USER_ID_ALICE)
        result = self.youtube_api.set_current_channel(channel_id=self.REAL_CHANNEL_ID)
        self.assertTrue(result.get("status", False))

    def test_set_current_channel_non_existent(self):
        """Test setting current channel to non-existent channel."""
        result = self.youtube_api.set_current_channel(channel_id="nonexistent_channel")
        self.assertFalse(result.get("status", True))

    # --- User Profile Tests ---
    def test_get_user_profile_alice(self):
        """Test getting user profile for Alice."""
        result = self.youtube_api.get_user_profile(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"])

    def test_get_user_profile_bob(self):
        """Test getting user profile for Bob."""
        result = self.youtube_api.get_user_profile(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"])

    def test_get_user_profile_non_existent(self):
        """Test getting profile for non-existent user."""
        result = self.youtube_api.get_user_profile(user_id="nonexistent_user")
        self.assertIn("data", result)
        self.assertIsNone(result["data"])
        self.assertIn("message", result)

    def test_get_user_by_email_alice(self):
        """Test getting user by email for Alice."""
        result = self.youtube_api.get_user_by_email(email=self.REAL_EMAIL_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"])

    def test_get_user_by_email_bob(self):
        """Test getting user by email for Bob."""
        result = self.youtube_api.get_user_by_email(email=self.REAL_EMAIL_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"])

    def test_get_user_by_email_non_existent(self):
        """Test getting user by non-existent email."""
        result = self.youtube_api.get_user_by_email(email="nonexistent@example.com")
        self.assertIn("data", result)
        self.assertIsNone(result["data"])
        self.assertIn("message", result)

    def test_get_user_by_display_name_alice(self):
        """Test getting user by display name for Alice."""
        result = self.youtube_api.get_user_by_display_name(display_name=self.REAL_DISPLAY_NAME_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"])

    def test_get_user_by_display_name_bob(self):
        """Test getting user by display name for Bob."""
        result = self.youtube_api.get_user_by_display_name(display_name=self.REAL_DISPLAY_NAME_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"])

    def test_get_user_by_display_name_non_existent(self):
        """Test getting user by non-existent display name."""
        result = self.youtube_api.get_user_by_display_name(display_name="NonExistent")
        self.assertIn("data", result)
        self.assertIsNone(result["data"])
        self.assertIn("message", result)

    # --- Watch History Tests ---
    def test_get_watch_history_alice(self):
        """Test getting watch history for Alice."""
        result = self.youtube_api.get_watch_history(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"])

    def test_get_watch_history_bob(self):
        """Test getting watch history for Bob."""
        result = self.youtube_api.get_watch_history(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"])

    def test_get_watch_history_non_existent(self):
        """Test getting watch history for non-existent user."""
        result = self.youtube_api.get_watch_history(user_id="nonexistent_user")
        self.assertIn("data", result)
        self.assertIsNone(result["data"])
        self.assertIn("message", result)

    # --- Subscription Tests ---
    def test_list_subscriptions_alice(self):
        """Test listing subscriptions for Alice."""
        result = self.youtube_api.list_subscriptions(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"])

    def test_list_subscriptions_bob(self):
        """Test listing subscriptions for Bob."""
        result = self.youtube_api.list_subscriptions(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"])

    def test_list_subscriptions_non_existent(self):
        """Test listing subscriptions for non-existent user."""
        result = self.youtube_api.list_subscriptions(user_id="nonexistent_user")
        self.assertIn("data", result)
        self.assertIsNone(result["data"])
        self.assertIn("message", result)

    def test_youtube_subscriptions_insert_alice(self):
        """Test inserting subscription for Alice."""
        result = self.youtube_api.youtube_subscriptions_insert(channel_id=self.REAL_CHANNEL_ID, user_id=self.REAL_USER_ID_ALICE)
        self.assertTrue(result.get("status", False))

    def test_youtube_subscriptions_insert_bob(self):
        """Test inserting subscription for Bob."""
        result = self.youtube_api.youtube_subscriptions_insert(channel_id=self.REAL_CHANNEL_ID, user_id=self.REAL_USER_ID_BOB)
        self.assertTrue(result.get("status", False))

    def test_youtube_subscriptions_insert_non_existent_channel(self):
        """Test inserting subscription to non-existent channel."""
        result = self.youtube_api.youtube_subscriptions_insert(channel_id="nonexistent_channel", user_id=self.REAL_USER_ID_ALICE)
        self.assertFalse(result.get("status", True)); self.assertIn("message", result)

    def test_youtube_subscriptions_delete_alice(self):
        """Test deleting subscription for Alice."""
        # First subscribe
        subscribe_result = self.youtube_api.youtube_subscriptions_insert(channel_id=self.REAL_CHANNEL_ID, user_id=self.REAL_USER_ID_ALICE)
        if subscribe_result.get("status"):
            result = self.youtube_api.youtube_subscriptions_delete(channel_id=self.REAL_CHANNEL_ID, user_id=self.REAL_USER_ID_ALICE)
            self.assertTrue(result.get("status", False))

    def test_youtube_subscriptions_delete_bob(self):
        """Test deleting subscription for Bob."""
        # First subscribe
        subscribe_result = self.youtube_api.youtube_subscriptions_insert(channel_id=self.REAL_CHANNEL_ID, user_id=self.REAL_USER_ID_BOB)
        if subscribe_result.get("status"):
            result = self.youtube_api.youtube_subscriptions_delete(channel_id=self.REAL_CHANNEL_ID, user_id=self.REAL_USER_ID_BOB)
            self.assertTrue(result.get("status", False))

    # --- Channel Management Tests ---
    def test_list_channels_for_user_alice(self):
        """Test listing channels for Alice."""
        result = self.youtube_api.list_channels_for_user(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("channels", result)

    def test_list_channels_for_user_bob(self):
        """Test listing channels for Bob."""
        result = self.youtube_api.list_channels_for_user(user_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_list_channels_for_user_non_existent(self):
        """Test listing channels for non-existent user."""
        result = self.youtube_api.list_channels_for_user(user_id="nonexistent_user")
        self.assertIn("data", result); self.assertIsNone(result["data"])

    def test_get_channel_details_existing(self):
        """Test getting details for existing channel."""
        result = self.youtube_api.get_channel_details(channel_id=self.REAL_CHANNEL_ID)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("channel", result)

    def test_get_channel_details_non_existent(self):
        """Test getting details for non-existent channel."""
        result = self.youtube_api.get_channel_details(channel_id="nonexistent_channel")
        self.assertIn("data", result); self.assertIsNone(result["data"])

    def test_create_channel_alice(self):
        """Test creating a channel for Alice."""
        result = self.youtube_api.create_channel(user_id=self.REAL_USER_ID_ALICE, title="Alice's Test Channel", description="Test channel description")
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("channel", result)

    def test_create_channel_bob_simple(self):
        """Test creating a simple channel for Bob."""
        result = self.youtube_api.create_channel(user_id=self.REAL_USER_ID_BOB, title="Bob's Channel")
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_create_channel_non_existent_user(self):
        """Test creating channel for non-existent user."""
        result = self.youtube_api.create_channel(user_id="nonexistent_user", title="Test Channel")
        self.assertIn("data", result); self.assertIsNone(result["data"])

    def test_youtube_channels_update_alice(self):
        """Test updating channel for Alice."""
        updates = {"title": "Updated Alice Channel", "description": "Updated description"}
        result = self.youtube_api.youtube_channels_update(channel_id=self.REAL_CHANNEL_ID, updates=updates, user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_youtube_channels_update_bob(self):
        """Test updating channel for Bob."""
        updates = {"description": "Updated Bob's channel description"}
        result = self.youtube_api.youtube_channels_update(channel_id=self.REAL_CHANNEL_ID, updates=updates, user_id=self.REAL_USER_ID_BOB)
        self.assertFalse(result.get("status", True)); self.assertIn("message", result)

    def test_youtube_channel_banners_insert(self):
        """Test inserting channel banner."""
        result = self.youtube_api.youtube_channel_banners_insert(image_path="/fake/path/banner.jpg", channel_id=self.REAL_CHANNEL_ID)
        self.assertTrue(result.get("status", False))

    # --- Video Management Tests ---
    def test_list_videos_in_channel_existing(self):
        """Test listing videos in existing channel."""
        result = self.youtube_api.list_videos_in_channel(channel_id=self.REAL_CHANNEL_ID)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("videos", result)

    def test_list_videos_in_channel_non_existent(self):
        """Test listing videos in non-existent channel."""
        result = self.youtube_api.list_videos_in_channel(channel_id="nonexistent_channel")
        self.assertIn("data", result); self.assertIsNone(result["data"])

    def test_get_video_details_existing(self):
        """Test getting details for existing video."""
        result = self.youtube_api.get_video_details(video_id=self.REAL_VIDEO_ID)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("video", result)

    def test_get_video_details_non_existent(self):
        """Test getting details for non-existent video."""
        result = self.youtube_api.get_video_details(video_id="nonexistent_video")
        self.assertIn("data", result); self.assertIsNone(result["data"])

    def test_upload_video_alice_simple(self):
        """Test uploading a simple video for Alice."""
        result = self.youtube_api.upload_video(channel_id=self.REAL_CHANNEL_ID, title="Alice's Test Video")
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("video", result)

    def test_upload_video_bob_with_details(self):
        """Test uploading video with full details for Bob."""
        result = self.youtube_api.upload_video(
            channel_id=self.REAL_CHANNEL_ID,
            title="Bob's Detailed Video",
            description="Detailed video description",
            duration_seconds=300,
            tags=["test", "bob", "video"]
        )
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_upload_video_non_existent_channel(self):
        """Test uploading video to non-existent channel."""
        result = self.youtube_api.upload_video(channel_id="nonexistent_channel", title="Test Video")
        self.assertIn("data", result); self.assertIsNone(result["data"])

    def test_delete_video_alice(self):
        """Test deleting video for Alice."""
        # First upload a video
        upload_result = self.youtube_api.upload_video(channel_id=self.REAL_CHANNEL_ID, title="Video to Delete")
        if upload_result.get("status"):
            video_id = upload_result["video"]["id"]
            result = self.youtube_api.delete_video(video_id=video_id, channel_id=self.REAL_CHANNEL_ID, user_id=self.REAL_USER_ID_ALICE)
            self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_delete_video_bob(self):
        """Test deleting video for Bob."""
        # First upload a video
        upload_result = self.youtube_api.upload_video(channel_id=self.REAL_CHANNEL_ID, title="Bob's Video to Delete")
        if upload_result.get("status"):
            video_id = upload_result["video"]["id"]
            result = self.youtube_api.delete_video(video_id=video_id, channel_id=self.REAL_CHANNEL_ID, user_id=self.REAL_USER_ID_BOB)
            self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_delete_video_non_existent(self):
        """Test deleting non-existent video."""
        result = self.youtube_api.delete_video(video_id="nonexistent_video", channel_id=self.REAL_CHANNEL_ID, user_id=self.REAL_USER_ID_ALICE)
        self.assertFalse(result.get("status", True)); self.assertIn("message", result)

    # --- Video Rating Tests ---
    def test_youtube_videos_rate_like_alice(self):
        """Test rating video like for Alice."""
        result = self.youtube_api.youtube_videos_rate(video_id=self.REAL_VIDEO_ID, rating="like", user_id=self.REAL_USER_ID_ALICE)
        self.assertTrue(result.get("status", False))

    def test_youtube_videos_rate_dislike_bob(self):
        """Test rating video dislike for Bob."""
        result = self.youtube_api.youtube_videos_rate(video_id=self.REAL_VIDEO_ID, rating="dislike", user_id=self.REAL_USER_ID_BOB)
        self.assertTrue(result.get("status", False))

    def test_youtube_videos_rate_none(self):
        """Test rating video none."""
        result = self.youtube_api.youtube_videos_rate(video_id=self.REAL_VIDEO_ID, rating="none", user_id=self.REAL_USER_ID_ALICE)
        self.assertFalse(result.get("status", True)); self.assertIn("message", result)

    def test_like_video_alice(self):
        """Test liking video for Alice."""
        result = self.youtube_api.like_video(video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_ALICE)
        self.assertTrue(result.get("status", False))

    def test_like_video_bob(self):
        """Test liking video for Bob."""
        result = self.youtube_api.like_video(video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_BOB)
        self.assertTrue(result.get("status", False))

    def test_unlike_video_alice(self):
        """Test unliking video for Alice."""
        # First like the video
        like_result = self.youtube_api.like_video(video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_ALICE)
        if like_result.get("status"):
            result = self.youtube_api.unlike_video(video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_ALICE)
            self.assertTrue(result.get("status", False))

    def test_unlike_video_bob(self):
        """Test unliking video for Bob."""
        # First like the video
        like_result = self.youtube_api.like_video(video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_BOB)
        if like_result.get("status"):
            result = self.youtube_api.unlike_video(video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_BOB)
            self.assertTrue(result.get("status", False))

    # --- Search Tests ---
    def test_search_videos_simple(self):
        """Test searching videos with simple query."""
        result = self.youtube_api.search_videos(query="test")
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("videos", result)

    def test_search_videos_with_max_results(self):
        """Test searching videos with max results limit."""
        result = self.youtube_api.search_videos(query="music", max_results=5)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_search_videos_no_results(self):
        """Test searching videos with query that returns no results."""
        result = self.youtube_api.search_videos(query="nonexistent_unique_term_12345")
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    # --- Playlist Management Tests ---
    def test_list_playlists_in_channel_existing(self):
        """Test listing playlists in existing channel."""
        result = self.youtube_api.list_playlists_in_channel(channel_id=self.REAL_CHANNEL_ID)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("playlists", result)

    def test_list_playlists_in_channel_non_existent(self):
        """Test listing playlists in non-existent channel."""
        result = self.youtube_api.list_playlists_in_channel(channel_id="nonexistent_channel")
        self.assertIn("data", result); self.assertIsNone(result["data"])

    def test_get_playlist_details_existing(self):
        """Test getting details for existing playlist."""
        result = self.youtube_api.get_playlist_details(playlist_id=self.REAL_PLAYLIST_ID)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("playlist", result)

    def test_get_playlist_details_non_existent(self):
        """Test getting details for non-existent playlist."""
        result = self.youtube_api.get_playlist_details(playlist_id="nonexistent_playlist")
        self.assertIn("data", result); self.assertIsNone(result["data"])

    def test_create_playlist_alice_simple(self):
        """Test creating a simple playlist for Alice."""
        result = self.youtube_api.create_playlist(channel_id=self.REAL_CHANNEL_ID, title="Alice's Test Playlist")
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("playlist", result)

    def test_create_playlist_bob_detailed(self):
        """Test creating detailed playlist for Bob."""
        result = self.youtube_api.create_playlist(
            channel_id=self.REAL_CHANNEL_ID,
            title="Bob's Detailed Playlist",
            description="Playlist with description",
            privacy_status="private"
        )
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_create_playlist_non_existent_channel(self):
        """Test creating playlist for non-existent channel."""
        result = self.youtube_api.create_playlist(channel_id="nonexistent_channel", title="Test Playlist")
        self.assertIn("data", result); self.assertIsNone(result["data"])

    def test_add_video_to_playlist_alice(self):
        """Test adding video to playlist for Alice."""
        result = self.youtube_api.add_video_to_playlist(playlist_id=self.REAL_PLAYLIST_ID, video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_ALICE)
        self.assertTrue(result.get("status", False))

    def test_add_video_to_playlist_bob(self):
        """Test adding video to playlist for Bob."""
        result = self.youtube_api.add_video_to_playlist(playlist_id=self.REAL_PLAYLIST_ID, video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_BOB)
        self.assertFalse(result.get("status", True))  # Bob should not be able to modify Alice's playlist

    def test_add_video_to_playlist_non_existent_playlist(self):
        """Test adding video to non-existent playlist."""
        result = self.youtube_api.add_video_to_playlist(playlist_id="nonexistent_playlist", video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_ALICE)
        self.assertFalse(result.get("status", True)); self.assertIn("message", result)

    def test_remove_video_from_playlist_alice(self):
        """Test removing video from playlist for Alice."""
        # First add video to playlist
        add_result = self.youtube_api.add_video_to_playlist(playlist_id=self.REAL_PLAYLIST_ID, video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_ALICE)
        if add_result.get("status"):
            result = self.youtube_api.remove_video_from_playlist(playlist_id=self.REAL_PLAYLIST_ID, video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_ALICE)
            self.assertTrue(result.get("status", False))

    def test_remove_video_from_playlist_bob(self):
        """Test removing video from playlist for Bob."""
        # First add video to playlist
        add_result = self.youtube_api.add_video_to_playlist(playlist_id=self.REAL_PLAYLIST_ID, video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_BOB)
        if add_result.get("status"):
            result = self.youtube_api.remove_video_from_playlist(playlist_id=self.REAL_PLAYLIST_ID, video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_BOB)
            self.assertTrue(result.get("status", False))

    def test_youtube_playlistItems_insert_alice(self):
        """Test inserting playlist item for Alice."""
        result = self.youtube_api.youtube_playlistItems_insert(playlist_id=self.REAL_PLAYLIST_ID, video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_ALICE)
        self.assertTrue(result.get("status", False))

    def test_youtube_playlistItems_insert_bob(self):
        """Test inserting playlist item for Bob."""
        result = self.youtube_api.youtube_playlistItems_insert(playlist_id=self.REAL_PLAYLIST_ID, video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_BOB)
        self.assertFalse(result.get("status", True)); self.assertIn("message", result)

    def test_youtube_playlistItems_delete_alice(self):
        """Test deleting playlist item for Alice."""
        result = self.youtube_api.youtube_playlistItems_delete(playlist_item_id="playlist_item_1", user_id=self.REAL_USER_ID_ALICE)
        self.assertFalse(result.get("status", True)); self.assertIn("message", result)

    def test_youtube_playlistItems_delete_bob(self):
        """Test deleting playlist item for Bob."""
        result = self.youtube_api.youtube_playlistItems_delete(playlist_item_id="playlist_item_2", user_id=self.REAL_USER_ID_BOB)
        self.assertFalse(result.get("status", True)); self.assertIn("message", result)

    # --- Comment Tests ---
    def test_add_comment_to_video_alice(self):
        """Test adding comment to video for Alice."""
        result = self.youtube_api.add_comment_to_video(video_id=self.REAL_VIDEO_ID, author_id=self.REAL_USER_ID_ALICE, text="Great video!")
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("comment", result)

    def test_add_comment_to_video_bob(self):
        """Test adding comment to video for Bob."""
        result = self.youtube_api.add_comment_to_video(video_id=self.REAL_VIDEO_ID, author_id=self.REAL_USER_ID_BOB, text="Nice work!")
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_add_comment_to_video_non_existent_video(self):
        """Test adding comment to non-existent video."""
        result = self.youtube_api.add_comment_to_video(video_id="nonexistent_video", author_id=self.REAL_USER_ID_ALICE, text="Test comment")
        self.assertIn("data", result); self.assertIsNone(result["data"])

    def test_list_comments_for_video_existing(self):
        """Test listing comments for existing video."""
        result = self.youtube_api.list_comments_for_video(video_id=self.REAL_VIDEO_ID)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])
        if result.get("status"):
            self.assertIn("comments", result)

    def test_list_comments_for_video_non_existent(self):
        """Test listing comments for non-existent video."""
        result = self.youtube_api.list_comments_for_video(video_id="nonexistent_video")
        self.assertIn("data", result); self.assertIsNone(result["data"])

    def test_delete_comment_alice(self):
        """Test deleting comment for Alice."""
        # First add a comment
        comment_result = self.youtube_api.add_comment_to_video(video_id=self.REAL_VIDEO_ID, author_id=self.REAL_USER_ID_ALICE, text="Comment to delete")
        if comment_result.get("status"):
            comment_id = comment_result["comment"]["id"]
            result = self.youtube_api.delete_comment(comment_id=comment_id, user_id=self.REAL_USER_ID_ALICE)
            self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_delete_comment_bob(self):
        """Test deleting comment for Bob."""
        # First add a comment
        comment_result = self.youtube_api.add_comment_to_video(video_id=self.REAL_VIDEO_ID, author_id=self.REAL_USER_ID_BOB, text="Bob's comment to delete")
        if comment_result.get("status"):
            comment_id = comment_result["comment"]["id"]
            result = self.youtube_api.delete_comment(comment_id=comment_id, user_id=self.REAL_USER_ID_BOB)
            self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_delete_comment_non_existent(self):
        """Test deleting non-existent comment."""
        result = self.youtube_api.delete_comment(comment_id="nonexistent_comment", user_id=self.REAL_USER_ID_ALICE)
        self.assertFalse(result.get("status", True)); self.assertIn("message", result)

    def test_youtube_comments_insert_alice(self):
        """Test inserting comment for Alice."""
        result = self.youtube_api.youtube_comments_insert(video_id=self.REAL_VIDEO_ID, text="Alice's comment", author_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_youtube_comments_insert_bob(self):
        """Test inserting comment for Bob."""
        result = self.youtube_api.youtube_comments_insert(video_id=self.REAL_VIDEO_ID, text="Bob's comment", author_id=self.REAL_USER_ID_BOB)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    # --- Caption Tests ---
    def test_youtube_captions_insert(self):
        """Test inserting captions for video."""
        result = self.youtube_api.youtube_captions_insert(video_id=self.REAL_VIDEO_ID, language="en", track_content="Test caption content")
        self.assertTrue(result.get("status", False))

    def test_youtube_captions_update(self):
        """Test updating captions."""
        result = self.youtube_api.youtube_captions_update(id="caption_1", track_content="Updated caption content")
        self.assertFalse(result.get("status", True)); self.assertIn("message", result)

    def test_youtube_captions_delete(self):
        """Test deleting captions."""
        result = self.youtube_api.youtube_captions_delete(id="caption_1")
        self.assertFalse(result.get("status", True)); self.assertIn("message", result)

    # --- Watch Later Tests ---
    def test_get_watch_later_playlist_alice(self):
        """Test getting watch later playlist for Alice."""
        result = self.youtube_api.get_watch_later_playlist(user_identifier=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_get_watch_later_playlist_bob_by_email(self):
        """Test getting watch later playlist for Bob by email."""
        result = self.youtube_api.get_watch_later_playlist(user_identifier=self.REAL_EMAIL_BOB)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_add_to_watch_later_alice(self):
        """Test adding video to watch later for Alice."""
        result = self.youtube_api.add_to_watch_later(user_identifier=self.REAL_USER_ID_ALICE, video_id=self.REAL_VIDEO_ID)
        self.assertTrue(result.get("status", False))

    def test_add_to_watch_later_bob_by_display_name(self):
        """Test adding video to watch later for Bob by display name."""
        result = self.youtube_api.add_to_watch_later(user_identifier=self.REAL_DISPLAY_NAME_BOB, video_id=self.REAL_VIDEO_ID)
        self.assertTrue(result.get("status", False))

    def test_remove_from_watch_later_alice(self):
        """Test removing video from watch later for Alice."""
        # First add to watch later
        add_result = self.youtube_api.add_to_watch_later(user_identifier=self.REAL_USER_ID_ALICE, video_id=self.REAL_VIDEO_ID)
        if add_result.get("status"):
            result = self.youtube_api.remove_from_watch_later(user_identifier=self.REAL_USER_ID_ALICE, video_id=self.REAL_VIDEO_ID)
            self.assertTrue(result.get("status", False))

    def test_remove_from_watch_later_bob(self):
        """Test removing video from watch later for Bob."""
        # First add to watch later
        add_result = self.youtube_api.add_to_watch_later(user_identifier=self.REAL_USER_ID_BOB, video_id=self.REAL_VIDEO_ID)
        if add_result.get("status"):
            result = self.youtube_api.remove_from_watch_later(user_identifier=self.REAL_USER_ID_BOB, video_id=self.REAL_VIDEO_ID)
            self.assertTrue(result.get("status", False))

    # --- User Settings Tests ---
    def test_get_notification_settings_alice(self):
        """Test getting notification settings for Alice."""
        result = self.youtube_api.get_notification_settings(user_identifier=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_get_notification_settings_bob(self):
        """Test getting notification settings for Bob."""
        result = self.youtube_api.get_notification_settings(user_identifier=self.REAL_USER_ID_BOB)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_update_notification_settings_alice(self):
        """Test updating notification settings for Alice."""
        settings = {"email_notifications": True, "push_notifications": False}
        result = self.youtube_api.update_notification_settings(user_identifier=self.REAL_USER_ID_ALICE, settings=settings)
        self.assertTrue(result.get("status", False))

    def test_update_notification_settings_bob(self):
        """Test updating notification settings for Bob."""
        settings = {"email_notifications": False, "push_notifications": True}
        result = self.youtube_api.update_notification_settings(user_identifier=self.REAL_USER_ID_BOB, settings=settings)
        self.assertTrue(result.get("status", False))

    def test_get_user_language_preference_alice(self):
        """Test getting language preference for Alice."""
        result = self.youtube_api.get_user_language_preference(user_identifier=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_get_user_language_preference_bob(self):
        """Test getting language preference for Bob."""
        result = self.youtube_api.get_user_language_preference(user_identifier=self.REAL_USER_ID_BOB)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_update_language_preference_alice(self):
        """Test updating language preference for Alice."""
        result = self.youtube_api.update_language_preference(user_identifier=self.REAL_USER_ID_ALICE, language="es")
        self.assertTrue(result.get("status", False))

    def test_update_language_preference_bob(self):
        """Test updating language preference for Bob."""
        result = self.youtube_api.update_language_preference(user_identifier=self.REAL_USER_ID_BOB, language="fr")
        self.assertTrue(result.get("status", False))

    # --- Analytics Tests ---
    def test_get_account_status_alice(self):
        """Test getting account status for Alice."""
        result = self.youtube_api.get_account_status(user_identifier=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_get_account_status_bob(self):
        """Test getting account status for Bob."""
        result = self.youtube_api.get_account_status(user_identifier=self.REAL_USER_ID_BOB)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_get_channel_history_alice(self):
        """Test getting channel history for Alice."""
        result = self.youtube_api.get_channel_history(user_identifier=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_get_channel_history_bob(self):
        """Test getting channel history for Bob."""
        result = self.youtube_api.get_channel_history(user_identifier=self.REAL_USER_ID_BOB)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_add_to_channel_history_alice(self):
        """Test adding to channel history for Alice."""
        result = self.youtube_api.add_to_channel_history(user_identifier=self.REAL_USER_ID_ALICE, channel_id=self.REAL_CHANNEL_ID)
        self.assertTrue(result.get("status", False))

    def test_add_to_channel_history_bob(self):
        """Test adding to channel history for Bob."""
        result = self.youtube_api.add_to_channel_history(user_identifier=self.REAL_USER_ID_BOB, channel_id=self.REAL_CHANNEL_ID)
        self.assertTrue(result.get("status", False))

    def test_get_user_analytics_alice(self):
        """Test getting user analytics for Alice."""
        result = self.youtube_api.get_user_analytics(user_identifier=self.REAL_USER_ID_ALICE)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_get_user_analytics_bob(self):
        """Test getting user analytics for Bob."""
        result = self.youtube_api.get_user_analytics(user_identifier=self.REAL_USER_ID_BOB)
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    def test_search_users_by_language(self):
        """Test searching users by language."""
        result = self.youtube_api.search_users_by_language(language="en")
        self.assertIn("data", result); self.assertIsNotNone(result["data"])

    # --- Workflow Tests ---
    def test_video_upload_and_interaction_workflow(self):
        """Test comprehensive video upload and interaction workflow."""
        # Upload video
        upload_result = self.youtube_api.upload_video(channel_id=self.REAL_CHANNEL_ID, title="Workflow Test Video")
        self.assertIn("data", upload_result)
        
        if "data" in upload_result:
            video_id = upload_result["data"]["id"]
            
            # Get video details
            details_result = self.youtube_api.get_video_details(video_id=video_id)
            self.assertIn("data", details_result)
            
            # Like video
            like_result = self.youtube_api.like_video(video_id=video_id, user_id=self.REAL_USER_ID_ALICE)
            self.assertTrue(like_result.get("status", False))
            
            # Add comment
            comment_result = self.youtube_api.add_comment_to_video(video_id=video_id, author_id=self.REAL_USER_ID_BOB, text="Great workflow video!")
            self.assertIn("data", comment_result)
            
            # Add to watch later
            watch_later_result = self.youtube_api.add_to_watch_later(user_identifier=self.REAL_USER_ID_ALICE, video_id=video_id)
            self.assertTrue(watch_later_result.get("status", False))

    def test_playlist_management_workflow(self):
        """Test playlist management workflow."""
        # Create playlist
        playlist_result = self.youtube_api.create_playlist(channel_id=self.REAL_CHANNEL_ID, title="Workflow Playlist")
        self.assertIn("data", playlist_result)
        
        if "data" in playlist_result:
            playlist_id = playlist_result["data"]["id"]
            
            # Add video to playlist
            add_result = self.youtube_api.add_video_to_playlist(playlist_id=playlist_id, video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_ALICE)
            self.assertTrue(add_result.get("status", False))
            
            # Get playlist details
            details_result = self.youtube_api.get_playlist_details(playlist_id=playlist_id)
            self.assertIn("data", details_result)
            
            # Remove video from playlist
            remove_result = self.youtube_api.remove_video_from_playlist(playlist_id=playlist_id, video_id=self.REAL_VIDEO_ID, user_id=self.REAL_USER_ID_ALICE)
            self.assertTrue(remove_result.get("status", False))

    def test_channel_subscription_workflow(self):
        """Test channel subscription workflow."""
        # Subscribe to channel
        subscribe_result = self.youtube_api.youtube_subscriptions_insert(channel_id=self.REAL_CHANNEL_ID, user_id=self.REAL_USER_ID_ALICE)
        self.assertTrue(subscribe_result.get("status", False))
        
        # List subscriptions
        list_result = self.youtube_api.list_subscriptions(user_id=self.REAL_USER_ID_ALICE)
        self.assertIn("data", list_result)
        
        # Get channel details
        channel_result = self.youtube_api.get_channel_details(channel_id=self.REAL_CHANNEL_ID)
        self.assertIn("data", channel_result)
        
        # Unsubscribe
        unsubscribe_result = self.youtube_api.youtube_subscriptions_delete(channel_id=self.REAL_CHANNEL_ID, user_id=self.REAL_USER_ID_ALICE)
        self.assertTrue(unsubscribe_result.get("status", False))

    # --- Data Reset Tests ---
    def test_reset_data_success(self):
        """Test resetting data successfully."""
        result = self.youtube_api.reset_data()
        self.assertTrue(result.get("reset_status", False))

if __name__ == "__main__":
    unittest.main()
