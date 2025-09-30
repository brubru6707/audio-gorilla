import unittest
from audio_gorilla.SpotifyApis import SpotifyApis, DEFAULT_STATE

class TestSpotifyApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh SpotifyApis instance for each test."""
        self.spotify_api = SpotifyApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.spotify_api._load_default_state()
        self.test_user_email = "spotify_user@example.com"
        # No need to explicitly log in, as authentication is assumed.

    # --- Unit Tests for Core Functions (most important for audio calling) ---

    def test_show_profile_success(self):
        """Test showing the current user's profile information."""
        result = self.spotify_api.show_profile()
        self.assertIn("profile", result)
        self.assertEqual(result["profile"]["email"], self.test_user_email)
        self.assertEqual(result["profile"]["first_name"], "Spotify")
        self.assertTrue(result["profile"]["premium"])

    def test_search_songs_by_title(self):
        """Test searching for songs by title."""
        result = self.spotify_api.search_songs("Shape of You")
        self.assertIn("songs", result)
        self.assertEqual(len(result["songs"]), 1)
        self.assertEqual(result["songs"][0]["title"], "Shape of You")

    def test_search_songs_by_artist(self):
        """Test searching for songs by artist."""
        result = self.spotify_api.search_songs("Queen")
        self.assertIn("songs", result)
        self.assertEqual(len(result["songs"]), 1)
        self.assertEqual(result["songs"][0]["artist"], "Queen")

    def test_show_song_success(self):
        """Test showing details of a specific song."""
        song_id = 101 # "Shape of You"
        result = self.spotify_api.show_song(song_id)
        self.assertIn("song", result)
        self.assertEqual(result["song"]["id"], song_id)
        self.assertEqual(result["song"]["title"], "Shape of You")

    def test_show_song_not_found(self):
        """Test showing details for a non-existent song."""
        result = self.spotify_api.show_song(999)
        self.assertIn("song", result)
        self.assertEqual(result["song"], {})

    def test_play_song_success(self):
        """Test playing a song successfully."""
        song_id = 102 # "Bohemian Rhapsody"
        result = self.spotify_api.play_song(song_id)
        self.assertEqual(result["playback_status"], "playing")
        self.assertIsNotNone(self.spotify_api.current_song)
        self.assertEqual(self.spotify_api.current_song["id"], song_id)
        self.assertTrue(self.spotify_api.is_playing)

    def test_play_song_not_found(self):
        """Test playing a non-existent song."""
        result = self.spotify_api.play_song(999)
        self.assertEqual(result["playback_status"], "error")
        self.assertIsNone(self.spotify_api.current_song)
        self.assertFalse(self.spotify_api.is_playing)

    def test_pause_song_success(self):
        """Test pausing a playing song."""
        self.spotify_api.play_song(101) # Start playing a song
        result = self.spotify_api.pause_song()
        self.assertEqual(result["playback_status"], "paused")
        self.assertIsNotNone(self.spotify_api.current_song) # current_song should NOT be None after pause
        self.assertFalse(self.spotify_api.is_playing)

    def test_pause_song_no_song_playing(self):
        """Test pausing when no song is playing."""
        self.spotify_api.current_song = None
        self.spotify_api.is_playing = False
        result = self.spotify_api.pause_song()
        self.assertEqual(result["playback_status"], "error")

    def test_resume_song_success(self):
        """Test resuming a paused song."""
        self.spotify_api.play_song(101) # Play a song
        self.spotify_api.pause_song() # Pause it (sets is_playing to False, keeps current_song)

        result = self.spotify_api.resume_song()
        self.assertEqual(result["playback_status"], "playing")
        self.assertIsNotNone(self.spotify_api.current_song)
        self.assertTrue(self.spotify_api.is_playing)

    def test_resume_song_no_song_paused(self):
        """Test resuming when no song is paused."""
        self.spotify_api.current_song = None
        self.spotify_api.is_playing = False
        result = self.spotify_api.resume_song()
        self.assertEqual(result["playback_status"], "error")

    def test_skip_song_success(self):
        """Test skipping to the next song in the queue."""
        self.spotify_api.add_song_to_queue(103) # Add "Blinding Lights"
        self.spotify_api.add_song_to_queue(104) # Add "Watermelon Sugar"
        self.spotify_api.play_song(101) # Start "Shape of You"
        
        result = self.spotify_api.skip_song()
        self.assertTrue(result["skip_status"])
        self.assertEqual(self.spotify_api.current_song["id"], 103) # Should be "Blinding Lights"
        self.assertEqual(len(self.spotify_api.song_queue), 1) # One song left in queue
        self.assertTrue(self.spotify_api.is_playing)

    def test_skip_song_empty_queue(self):
        """Test skipping when the queue is empty."""
        self.spotify_api.current_song = None
        self.spotify_api.song_queue = [] # Ensure queue is empty
        result = self.spotify_api.skip_song()
        self.assertFalse(result["skip_status"])
        self.assertIsNone(self.spotify_api.current_song)
        self.assertFalse(self.spotify_api.is_playing)

    def test_set_volume_success(self):
        """Test setting the playback volume."""
        result = self.spotify_api.set_volume(50)
        self.assertTrue(result["set_status"])
        self.assertEqual(self.spotify_api.volume, 50)

    def test_set_volume_invalid_level(self):
        """Test setting an invalid volume level."""
        result = self.spotify_api.set_volume(150)
        self.assertFalse(result["set_status"])
        self.assertEqual(self.spotify_api.volume, 75) # Should remain default

    def test_get_volume_success(self):
        """Test getting the current playback volume."""
        self.spotify_api.set_volume(65)
        result = self.spotify_api.get_volume()
        self.assertEqual(result["volume"], 65)

    def test_add_song_to_queue_success(self):
        """Test adding a song to the playback queue."""
        initial_queue_len = len(self.spotify_api.song_queue)
        result = self.spotify_api.add_song_to_queue(105) # "Old Town Road"
        self.assertTrue(result["add_status"])
        self.assertEqual(len(self.spotify_api.song_queue), initial_queue_len + 1)
        self.assertEqual(self.spotify_api.song_queue[-1], 105) # Storing ID, not object

    def test_show_song_queue_success(self):
        """Test showing the current playback queue."""
        self.spotify_api.add_song_to_queue(103)
        self.spotify_api.add_song_to_queue(104)
        result = self.spotify_api.show_song_queue() 
        self.assertIn("queue", result)
        self.assertEqual(len(result["queue"]), 2)
        self.assertEqual(result["queue"][0]["id"], 103)
        self.assertEqual(result["queue"][1]["id"], 104)

    def test_create_playlist_success(self):
        """Test creating a new playlist."""
        initial_playlist_count = len(self.spotify_api.playlists)
        result = self.spotify_api.create_playlist("My New Jams", True)
        self.assertIn("playlist", result)
        self.assertTrue(result["playlist"]["public"])
        self.assertEqual(result["playlist"]["title"], "My New Jams")
        self.assertEqual(len(self.spotify_api.playlists), initial_playlist_count + 1)

    def test_like_song_success(self):
        """Test liking a song."""
        # Use a song that is NOT already liked in DEFAULT_STATE
        song_id_to_like = 102 # "Bohemian Rhapsody" is not in liked_songs by default
        initial_liked_songs = len(self.spotify_api.users[self.test_user_email]["liked_songs"])
        result = self.spotify_api.like_song(song_id_to_like)
        self.assertTrue(result["like_status"])
        self.assertEqual(len(self.spotify_api.users[self.test_user_email]["liked_songs"]), initial_liked_songs + 1)
        self.assertIn(song_id_to_like, self.spotify_api.users[self.test_user_email]["liked_songs"])

    def test_download_song_premium_required(self):
        """Test downloading a song when user is not premium."""
        # Temporarily set user to non-premium for this test
        self.spotify_api.users[self.test_user_email]["premium"] = False
        song_id = 101
        result = self.spotify_api.download_song(song_id)
        self.assertFalse(result["download_status"])
        self.assertIn("Premium subscription required", result["message"])
        # Revert premium status for other tests
        self.spotify_api.users[self.test_user_email]["premium"] = True

    def test_download_song_success(self):
        """Test downloading a song successfully (assuming premium)."""
        song_id = 105 # "Old Town Road"
        initial_downloaded_songs = len(self.spotify_api.users[self.test_user_email]["downloaded_songs"])
        result = self.spotify_api.download_song(song_id)
        self.assertTrue(result["download_status"])
        self.assertEqual(len(self.spotify_api.users[self.test_user_email]["downloaded_songs"]), initial_downloaded_songs + 1)
        self.assertIn(song_id, self.spotify_api.users[self.test_user_email]["downloaded_songs"])

    # --- Combined Functionality Tests ---

    def test_search_play(self):
        """
        Scenario: Search for a song, play it, then get current playback info.
        Functions: search_songs, play_song, get_current_playback_info
        """
        # 1. Search for a song
        search_query = "Watermelon Sugar"
        search_result = self.spotify_api.search_songs(search_query)
        self.assertIn("songs", search_result)
        self.assertEqual(len(search_result["songs"]), 1)
        song_to_play = search_result["songs"][0]
        song_to_play_id = song_to_play["id"]

        # 2. Play the found song
        play_result = self.spotify_api.play_song(song_to_play_id)
        self.assertEqual(play_result["playback_status"], "playing")
        self.assertEqual(self.spotify_api.current_song["id"], song_to_play_id)
        self.assertTrue(self.spotify_api.is_playing)

    def test_add_to_queue_skip_and_show_queue(self):
        """
        Scenario: Add songs to queue, skip a song, then show the updated queue.
        Functions: add_song_to_queue, skip_song, show_song_queue
        """
        # Ensure no song is playing initially for clean queue management
        self.spotify_api.current_song = None
        self.spotify_api.is_playing = False
        self.spotify_api.clear_song_queue() # Start with an empty queue

        # 1. Add songs to queue
        self.spotify_api.add_song_to_queue(103) # Blinding Lights
        self.spotify_api.add_song_to_queue(104) # Watermelon Sugar
        self.spotify_api.add_song_to_queue(105) # Old Town Road
        self.assertEqual(len(self.spotify_api.song_queue), 3)

        # 2. Play the first song in the queue (which happens when skip is called with no current song)
        # Or, we can explicitly play the first song to set current_song, then skip
        # Note: The skip_song function in the provided API plays the next song from the queue
        # if no song is currently playing. So, we don't need to call play_song here first.
        
        # 3. Skip to the next song (first song in queue becomes current_song)
        skip_result_1 = self.spotify_api.skip_song()
        self.assertTrue(skip_result_1["skip_status"])
        self.assertEqual(self.spotify_api.current_song["id"], 103) # Should be Blinding Lights
        self.assertEqual(len(self.spotify_api.song_queue), 2) # Queue now has 104, 105

        # 4. Skip to the next song again
        skip_result_2 = self.spotify_api.skip_song()
        self.assertTrue(skip_result_2["skip_status"])
        self.assertEqual(self.spotify_api.current_song["id"], 104) # Should be Watermelon Sugar
        self.assertEqual(len(self.spotify_api.song_queue), 1) # Queue now has 105

        # 5. Show the updated queue
        queue_info = self.spotify_api.show_song_queue()
        self.assertEqual(len(queue_info["queue"]), 1)
        self.assertEqual(queue_info["queue"][0]["id"], 105) # Only Old Town Road should remain

    def test_create_playlist_add_song_and_show_playlist(self):
        """
        Scenario: Create a new playlist, add a song to it, then show the playlist.
        Functions: create_playlist, add_song_to_playlist, show_playlist
        """
        # 1. Create a new playlist
        playlist_title = "My Workout Mix"
        create_playlist_result = self.spotify_api.create_playlist(playlist_title, False)
        self.assertIn("playlist", create_playlist_result)
        new_playlist_id = create_playlist_result["playlist"]["id"]
        self.assertEqual(create_playlist_result["playlist"]["title"], playlist_title)
        self.assertFalse(create_playlist_result["playlist"]["public"])

        # 2. Add a song to the new playlist
        song_to_add_id = 105 # "Old Town Road"
        add_song_result = self.spotify_api.add_song_to_playlist(new_playlist_id, song_to_add_id)
        self.assertTrue(add_song_result["add_status"])
        self.assertIn(song_to_add_id, self.spotify_api.playlists[new_playlist_id]["songs"])

        # 3. Show the playlist to verify the added song
        show_playlist_result = self.spotify_api.show_playlist(new_playlist_id)
        self.assertIn("playlist", show_playlist_result)
        self.assertEqual(show_playlist_result["playlist"]["id"], new_playlist_id)
        self.assertIn(song_to_add_id, show_playlist_result["playlist"]["songs"])
        self.assertEqual(len(show_playlist_result["playlist"]["songs"]), 1) # Only the one we added

    def test_check_premium_and_download_song_flow(self):
        """
        Scenario: Check premium status, if premium, download a song; if not, attempt download and expect failure.
        Functions: check_premium_status, download_song
        """
        # Test Case 1: User is premium (default state)
        premium_status_check = self.spotify_api.check_premium_status()
        self.assertTrue(premium_status_check["is_premium"])

        song_id_for_download = 102 # "Bohemian Rhapsody"
        initial_downloaded_count = len(self.spotify_api.users[self.test_user_email]["downloaded_songs"])
        download_result_premium = self.spotify_api.download_song(song_id_for_download)
        self.assertTrue(download_result_premium["download_status"])
        self.assertEqual(len(self.spotify_api.users[self.test_user_email]["downloaded_songs"]), initial_downloaded_count + 1)
        self.assertIn(song_id_for_download, self.spotify_api.users[self.test_user_email]["downloaded_songs"])

        # Test Case 2: User is NOT premium
        self.spotify_api.users[self.test_user_email]["premium"] = False
        premium_status_check_non_premium = self.spotify_api.check_premium_status()
        self.assertFalse(premium_status_check_non_premium["is_premium"])

        # Attempt to download again
        download_result_non_premium = self.spotify_api.download_song(101) # "Shape of You"
        self.assertFalse(download_result_non_premium["download_status"])
        self.assertIn("Premium subscription required", download_result_non_premium["message"])

        # Revert premium status for other tests
        self.spotify_api.users[self.test_user_email]["premium"] = True

    # ================ COMPREHENSIVE COVERAGE FOR MISSING METHODS ================

    def test_set_current_user_success(self):
        """Test setting current user successfully."""
        result = self.spotify_api.set_current_user(self.test_user_email)
        self.assertTrue(result["success"])
        self.assertEqual(self.spotify_api.current_user_email, self.test_user_email)

    def test_set_current_user_not_found(self):
        """Test setting non-existent user."""
        result = self.spotify_api.set_current_user("nonexistent@test.com")
        self.assertFalse(result["success"])

    def test_show_account_success(self):
        """Test showing account information."""
        self.spotify_api.set_current_user(self.test_user_email)
        result = self.spotify_api.show_account()
        self.assertTrue(result["success"])
        self.assertIn("account", result)
        self.assertEqual(result["account"]["email"], self.test_user_email)

    def test_show_account_no_current_user(self):
        """Test showing account with no current user set."""
        self.spotify_api.current_user_email = None
        result = self.spotify_api.show_account()
        self.assertFalse(result["success"])

    def test_add_payment_method_success(self):
        """Test adding a payment method successfully."""
        self.spotify_api.set_current_user(self.test_user_email)
        result = self.spotify_api.add_payment_method(
            card_number="4111111111111111",
            expiry_month="12",
            expiry_year="2025",
            cvv="123",
            cardholder_name="Test User",
            billing_address="123 Test St, Test City, TC 12345"
        )
        self.assertTrue(result["success"])
        self.assertIn("payment_method_id", result)

    def test_show_payment_methods_success(self):
        """Test showing payment methods."""
        self.spotify_api.set_current_user(self.test_user_email)
        result = self.spotify_api.show_payment_methods()
        self.assertTrue(result["success"])
        self.assertIn("payment_methods", result)

    def test_set_default_payment_method_success(self):
        """Test setting default payment method."""
        self.spotify_api.set_current_user(self.test_user_email)
        
        # First add a payment method
        add_result = self.spotify_api.add_payment_method(
            card_number="4111111111111111",
            expiry_month="12",
            expiry_year="2025",
            cvv="123",
            cardholder_name="Test User",
            billing_address="123 Test St"
        )
        payment_id = add_result["payment_method_id"]
        
        # Then set it as default
        result = self.spotify_api.set_default_payment_method(payment_id)
        self.assertTrue(result["success"])

    def test_get_user_liked_songs_success(self):
        """Test getting user's liked songs."""
        self.spotify_api.set_current_user(self.test_user_email)
        result = self.spotify_api.get_user_liked_songs()
        self.assertTrue(result["success"])
        self.assertIn("liked_songs", result)

    def test_like_unlike_song_operations(self):
        """Test comprehensive like/unlike song operations."""
        self.spotify_api.set_current_user(self.test_user_email)
        song_id = "test_song_123"
        
        # Like song
        like_result = self.spotify_api.like_song(song_id)
        self.assertTrue(like_result["success"])
        
        # Check it's in liked songs
        liked_songs_result = self.spotify_api.get_user_liked_songs()
        self.assertIn(song_id, liked_songs_result["liked_songs"])
        
        # Unlike song
        unlike_result = self.spotify_api.unlike_song(song_id)
        self.assertTrue(unlike_result["success"])
        
        # Check it's no longer in liked songs
        liked_songs_result_after = self.spotify_api.get_user_liked_songs()
        self.assertNotIn(song_id, liked_songs_result_after["liked_songs"])

    def test_library_song_operations(self):
        """Test comprehensive library song operations."""
        self.spotify_api.set_current_user(self.test_user_email)
        song_id = "library_song_456"
        
        # Get initial library
        initial_library = self.spotify_api.get_user_library_songs()
        self.assertTrue(initial_library["success"])
        
        # Add to library
        add_result = self.spotify_api.add_song_to_library(song_id)
        self.assertTrue(add_result["success"])
        
        # Check it's in library
        library_after_add = self.spotify_api.get_user_library_songs()
        self.assertIn(song_id, library_after_add["library_songs"])
        
        # Remove from library
        remove_result = self.spotify_api.remove_song_from_library(song_id)
        self.assertTrue(remove_result["success"])
        
        # Check it's no longer in library
        library_after_remove = self.spotify_api.get_user_library_songs()
        self.assertNotIn(song_id, library_after_remove["library_songs"])

    def test_get_user_downloaded_songs_success(self):
        """Test getting user's downloaded songs."""
        self.spotify_api.set_current_user(self.test_user_email)
        result = self.spotify_api.get_user_downloaded_songs()
        self.assertTrue(result["success"])
        self.assertIn("downloaded_songs", result)

    def test_album_operations_comprehensive(self):
        """Test comprehensive album operations."""
        self.spotify_api.set_current_user(self.test_user_email)
        album_id = "test_album_789"
        
        # Get initial liked albums
        initial_liked = self.spotify_api.get_user_liked_albums()
        self.assertTrue(initial_liked["success"])
        
        # Like album
        like_result = self.spotify_api.like_album(album_id)
        self.assertTrue(like_result["success"])
        
        # Check it's in liked albums
        liked_after = self.spotify_api.get_user_liked_albums()
        self.assertIn(album_id, liked_after["liked_albums"])
        
        # Get library albums
        library_albums = self.spotify_api.get_user_library_albums()
        self.assertTrue(library_albums["success"])
        
        # Add to library
        add_library_result = self.spotify_api.add_album_to_library(album_id)
        self.assertTrue(add_library_result["success"])
        
        # Remove from library
        remove_library_result = self.spotify_api.remove_album_from_library(album_id)
        self.assertTrue(remove_library_result["success"])
        
        # Unlike album
        unlike_result = self.spotify_api.unlike_album(album_id)
        self.assertTrue(unlike_result["success"])
        
        # Check it's no longer in liked albums
        liked_after_unlike = self.spotify_api.get_user_liked_albums()
        self.assertNotIn(album_id, liked_after_unlike["liked_albums"])

    def test_playlist_operations_comprehensive(self):
        """Test comprehensive playlist operations."""
        self.spotify_api.set_current_user(self.test_user_email)
        playlist_id = "test_playlist_101"
        
        # Get initial liked playlists
        initial_liked = self.spotify_api.get_user_liked_playlists()
        self.assertTrue(initial_liked["success"])
        
        # Like playlist
        like_result = self.spotify_api.like_playlist(playlist_id)
        self.assertTrue(like_result["success"])
        
        # Check it's in liked playlists
        liked_after = self.spotify_api.get_user_liked_playlists()
        self.assertIn(playlist_id, liked_after["liked_playlists"])
        
        # Unlike playlist
        unlike_result = self.spotify_api.unlike_playlist(playlist_id)
        self.assertTrue(unlike_result["success"])
        
        # Check it's no longer in liked playlists
        liked_after_unlike = self.spotify_api.get_user_liked_playlists()
        self.assertNotIn(playlist_id, liked_after_unlike["liked_playlists"])

    def test_artist_following_operations(self):
        """Test comprehensive artist following operations."""
        self.spotify_api.set_current_user(self.test_user_email)
        artist_id = "test_artist_202"
        
        # Get initial following artists
        initial_following = self.spotify_api.get_user_following_artists()
        self.assertTrue(initial_following["success"])
        
        # Follow artist
        follow_result = self.spotify_api.follow_artist(artist_id)
        self.assertTrue(follow_result["success"])
        
        # Check it's in following artists
        following_after = self.spotify_api.get_user_following_artists()
        self.assertIn(artist_id, following_after["following_artists"])
        
        # Unfollow artist
        unfollow_result = self.spotify_api.unfollow_artist(artist_id)
        self.assertTrue(unfollow_result["success"])
        
        # Check it's no longer in following artists
        following_after_unfollow = self.spotify_api.get_user_following_artists()
        self.assertNotIn(artist_id, following_after_unfollow["following_artists"])

    def test_like_operations_without_current_user(self):
        """Test like operations without current user set."""
        self.spotify_api.current_user_email = None
        
        # Test various operations fail without current user
        like_song_result = self.spotify_api.like_song("test_song")
        self.assertFalse(like_song_result["success"])
        
        like_album_result = self.spotify_api.like_album("test_album")
        self.assertFalse(like_album_result["success"])
        
        follow_artist_result = self.spotify_api.follow_artist("test_artist")
        self.assertFalse(follow_artist_result["success"])

    def test_payment_method_edge_cases(self):
        """Test payment method edge cases."""
        self.spotify_api.set_current_user(self.test_user_email)
        
        # Test setting non-existent payment method as default
        invalid_result = self.spotify_api.set_default_payment_method("nonexistent_id")
        self.assertFalse(invalid_result["success"])

    def test_comprehensive_user_workflow(self):
        """Test a complete user workflow with multiple operations."""
        # Set user
        self.spotify_api.set_current_user(self.test_user_email)
        
        # Show account
        account_result = self.spotify_api.show_account()
        self.assertTrue(account_result["success"])
        
        # Like some content
        song_id = "workflow_song"
        album_id = "workflow_album"
        artist_id = "workflow_artist"
        
        self.spotify_api.like_song(song_id)
        self.spotify_api.like_album(album_id)
        self.spotify_api.follow_artist(artist_id)
        
        # Add to library
        self.spotify_api.add_song_to_library(song_id)
        self.spotify_api.add_album_to_library(album_id)
        
        # Verify all operations
        liked_songs = self.spotify_api.get_user_liked_songs()
        liked_albums = self.spotify_api.get_user_liked_albums()
        following_artists = self.spotify_api.get_user_following_artists()
        library_songs = self.spotify_api.get_user_library_songs()
        library_albums = self.spotify_api.get_user_library_albums()
        
        self.assertIn(song_id, liked_songs["liked_songs"])
        self.assertIn(album_id, liked_albums["liked_albums"])
        self.assertIn(artist_id, following_artists["following_artists"])
        self.assertIn(song_id, library_songs["library_songs"])
        self.assertIn(album_id, library_albums["library_albums"])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
