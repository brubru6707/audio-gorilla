import unittest
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import backend creator
from SpotifyApis import SpotifyApis
from UnitTests.test_data_helper import BackendDataLoader

class TestSpotifyApis(unittest.TestCase):
    # Load real data from backend
    real_data = BackendDataLoader.get_spotify_data()
    
    # Extract real user data
    user_data = next(iter(real_data.get("users", {}).values()), {})
    REAL_USER_ID = next(iter(real_data.get("users", {})), "user1")
    REAL_EMAIL = user_data.get("email", "real_user@example.com")
    
    # Extract real playlist data
    playlist_data = next(iter(real_data.get("playlists", {}).values()), {})
    REAL_PLAYLIST_ID = next(iter(real_data.get("playlists", {})), "playlist1")
    
    # Extract real track/song data (handle both 'songs' and 'tracks')
    tracks_or_songs = real_data.get("tracks", real_data.get("songs", {}))
    song_data = next(iter(tracks_or_songs.values()), {})
    REAL_TRACK_ID = next(iter(tracks_or_songs), "track1")
    
    # Extract real album data
    album_data = next(iter(real_data.get("albums", {}).values()), {})
    REAL_ALBUM_ID = next(iter(real_data.get("albums", {})), "album1")
    
    # Extract real artist data
    artist_data = next(iter(real_data.get("artists", {}).values()), {})
    REAL_ARTIST_ID = next(iter(real_data.get("artists", {})), "artist1")
    
    def setUp(self):
        """Set up the API instance using real data."""
        self.spotify_api = SpotifyApis()
        # Authenticate with OAuth token
        self.access_token = f"token_{self.REAL_EMAIL}"
        self.spotify_api.authenticate(self.access_token)

    # --- Authentication Tests ---

    def test_authenticate_success(self):
        """Test successful authentication."""
        api = SpotifyApis()
        api.authenticate(f"token_{self.REAL_EMAIL}")
        self.assertEqual(api.access_token, f"token_{self.REAL_EMAIL}")
        self.assertEqual(api.current_user_id, self.REAL_USER_ID)

    def test_authenticate_invalid_token(self):
        """Test authentication with invalid token format."""
        api = SpotifyApis()
        with self.assertRaises(Exception) as context:
            api.authenticate("invalid_token")
        self.assertIn("Invalid access token", str(context.exception))

    def test_authenticate_nonexistent_user(self):
        """Test authentication with non-existent user."""
        api = SpotifyApis()
        with self.assertRaises(Exception) as context:
            api.authenticate("token_nonexistent@example.com")
        self.assertIn("not found", str(context.exception).lower())

    def test_unauthenticated_access(self):
        """Test that protected methods require authentication."""
        api = SpotifyApis()
        with self.assertRaises(Exception) as context:
            api.get_current_user_profile()
        self.assertIn("authentication required", str(context.exception).lower())

    # --- User Profile Tests ---

    def test_get_current_user_profile(self):
        """Test getting current user profile."""
        profile = self.spotify_api.get_current_user_profile()
        self.assertEqual(profile["id"], self.REAL_USER_ID)
        self.assertEqual(profile["email"], self.REAL_EMAIL)
        self.assertEqual(profile["type"], "user")
        self.assertIn("uri", profile)
        self.assertIn("href", profile)
        self.assertIn("external_urls", profile)

    # --- Payment Methods Tests ---

    def test_add_payment_method(self):
        """Test adding a payment method."""
        result = self.spotify_api.add_payment_method(
            card_name="Test Card",
            card_number="4111111111111111",
            expiry_year=2025,
            expiry_month=12,
            cvv_number="123"
        )
        self.assertIn("id", result)
        self.assertEqual(result["card_name"], "Test Card")
        self.assertEqual(result["card_number"], "4111111111111111")
        self.assertEqual(result["user_id"], self.REAL_USER_ID)

    def test_show_payment_methods(self):
        """Test showing payment methods."""
        # Add a payment method first
        self.spotify_api.add_payment_method(
            card_name="Test Card",
            card_number="4111111111111111",
            expiry_year=2025,
            expiry_month=12,
            cvv_number="123"
        )
        
        methods = self.spotify_api.show_payment_methods()
        self.assertIsInstance(methods, list)
        self.assertGreater(len(methods), 0)

    def test_set_default_payment_method(self):
        """Test setting default payment method."""
        # Add a payment method
        result = self.spotify_api.add_payment_method(
            card_name="Default Card",
            card_number="4111111111111111",
            expiry_year=2025,
            expiry_month=12,
            cvv_number="123",
            is_default=False
        )
        payment_id = result["id"]
        
        # Set as default
        self.spotify_api.set_default_payment_method(payment_id)
        
        # Verify it's default
        methods = self.spotify_api.show_payment_methods()
        default_method = next((m for m in methods if m["id"] == payment_id), None)
        self.assertTrue(default_method["is_default"])

    def test_set_default_payment_method_not_found(self):
        """Test setting non-existent payment method as default."""
        with self.assertRaises(Exception) as context:
            self.spotify_api.set_default_payment_method("nonexistent_id")
        self.assertIn("not found", str(context.exception).lower())

    # --- Track Tests ---

    def test_get_track(self):
        """Test getting a single track."""
        track = self.spotify_api.get_track(self.REAL_TRACK_ID)
        self.assertEqual(track["id"], self.REAL_TRACK_ID)
        self.assertEqual(track["type"], "track")
        self.assertIn("uri", track)
        self.assertIn("href", track)

    def test_get_track_not_found(self):
        """Test getting non-existent track."""
        with self.assertRaises(Exception) as context:
            self.spotify_api.get_track("nonexistent_track")
        self.assertIn("not found", str(context.exception).lower())

    def test_get_several_tracks(self):
        """Test getting multiple tracks."""
        result = self.spotify_api.get_several_tracks([self.REAL_TRACK_ID])
        self.assertIn("tracks", result)
        self.assertEqual(len(result["tracks"]), 1)
        self.assertEqual(result["tracks"][0]["id"], self.REAL_TRACK_ID)

    def test_get_saved_tracks(self):
        """Test getting user's saved tracks."""
        result = self.spotify_api.get_saved_tracks(limit=20, offset=0)
        self.assertIn("items", result)
        self.assertIn("total", result)
        self.assertIn("limit", result)
        self.assertIn("offset", result)

    def test_get_saved_tracks_pagination(self):
        """Test pagination for saved tracks."""
        result = self.spotify_api.get_saved_tracks(limit=5, offset=0)
        self.assertEqual(result["limit"], 5)
        self.assertEqual(result["offset"], 0)

    def test_save_tracks(self):
        """Test saving tracks to library."""
        # Should not raise exception
        self.spotify_api.save_tracks([self.REAL_TRACK_ID])

    def test_save_tracks_too_many(self):
        """Test saving too many tracks at once."""
        track_ids = [f"track_{i}" for i in range(51)]
        with self.assertRaises(Exception) as context:
            self.spotify_api.save_tracks(track_ids)
        self.assertIn("max", str(context.exception).lower())

    def test_remove_saved_tracks(self):
        """Test removing saved tracks."""
        # Save first
        self.spotify_api.save_tracks([self.REAL_TRACK_ID])
        # Remove
        self.spotify_api.remove_saved_tracks([self.REAL_TRACK_ID])

    def test_check_saved_tracks(self):
        """Test checking if tracks are saved."""
        # Save a track
        self.spotify_api.save_tracks([self.REAL_TRACK_ID])
        # Check it
        result = self.spotify_api.check_saved_tracks([self.REAL_TRACK_ID])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0])

    # --- Album Tests ---

    def test_get_album(self):
        """Test getting a single album."""
        album = self.spotify_api.get_album(self.REAL_ALBUM_ID)
        self.assertEqual(album["id"], self.REAL_ALBUM_ID)
        self.assertEqual(album["type"], "album")
        self.assertIn("uri", album)

    def test_get_album_not_found(self):
        """Test getting non-existent album."""
        with self.assertRaises(Exception) as context:
            self.spotify_api.get_album("nonexistent_album")
        self.assertIn("not found", str(context.exception).lower())

    def test_get_several_albums(self):
        """Test getting multiple albums."""
        result = self.spotify_api.get_several_albums([self.REAL_ALBUM_ID])
        self.assertIn("albums", result)
        self.assertEqual(len(result["albums"]), 1)

    def test_get_saved_albums(self):
        """Test getting user's saved albums."""
        result = self.spotify_api.get_saved_albums(limit=20, offset=0)
        self.assertIn("items", result)
        self.assertIn("total", result)

    def test_save_albums(self):
        """Test saving albums to library."""
        self.spotify_api.save_albums([self.REAL_ALBUM_ID])

    def test_save_albums_too_many(self):
        """Test saving too many albums at once."""
        # Create 51 albums to exceed the limit of 50
        album_ids = [f"album_{i}" for i in range(51)]
        with self.assertRaises(Exception) as context:
            self.spotify_api.save_albums(album_ids)
        self.assertIn("max", str(context.exception).lower())

    def test_remove_saved_albums(self):
        """Test removing saved albums."""
        self.spotify_api.save_albums([self.REAL_ALBUM_ID])
        self.spotify_api.remove_saved_albums([self.REAL_ALBUM_ID])

    # --- Artist Tests ---

    def test_get_artist(self):
        """Test getting a single artist."""
        artist = self.spotify_api.get_artist(self.REAL_ARTIST_ID)
        self.assertEqual(artist["id"], self.REAL_ARTIST_ID)
        self.assertEqual(artist["type"], "artist")

    def test_get_artist_not_found(self):
        """Test getting non-existent artist."""
        with self.assertRaises(Exception) as context:
            self.spotify_api.get_artist("nonexistent_artist")
        self.assertIn("not found", str(context.exception).lower())

    def test_get_several_artists(self):
        """Test getting multiple artists."""
        result = self.spotify_api.get_several_artists([self.REAL_ARTIST_ID])
        self.assertIn("artists", result)
        self.assertEqual(len(result["artists"]), 1)

    def test_follow_artists(self):
        """Test following artists."""
        self.spotify_api.follow_artists([self.REAL_ARTIST_ID])

    def test_follow_artists_too_many(self):
        """Test following too many artists at once."""
        artist_ids = [f"artist_{i}" for i in range(51)]
        with self.assertRaises(Exception) as context:
            self.spotify_api.follow_artists(artist_ids)
        self.assertIn("max", str(context.exception).lower())

    def test_unfollow_artists(self):
        """Test unfollowing artists."""
        self.spotify_api.follow_artists([self.REAL_ARTIST_ID])
        self.spotify_api.unfollow_artists([self.REAL_ARTIST_ID])

    def test_get_followed_artists(self):
        """Test getting followed artists."""
        result = self.spotify_api.get_followed_artists(limit=20)
        self.assertIn("artists", result)
        self.assertIn("items", result["artists"])

    # --- Playlist Tests ---

    def test_create_playlist(self):
        """Test creating a playlist."""
        playlist = self.spotify_api.create_playlist(
            user_id=self.REAL_USER_ID,
            name="My Test Playlist",
            description="Test description",
            public=True
        )
        self.assertEqual(playlist["name"], "My Test Playlist")
        self.assertEqual(playlist["description"], "Test description")
        self.assertTrue(playlist["public"])
        self.assertEqual(playlist["type"], "playlist")

    def test_create_playlist_for_other_user(self):
        """Test creating playlist for another user (should fail)."""
        with self.assertRaises(Exception) as context:
            self.spotify_api.create_playlist(
                user_id="other_user_id",
                name="Test Playlist",
                public=True
            )
        self.assertIn("authenticated user", str(context.exception).lower())

    def test_get_playlist_public(self):
        """Test getting a public playlist."""
        # Create public playlist
        created = self.spotify_api.create_playlist(
            user_id=self.REAL_USER_ID,
            name="Public Playlist",
            public=True
        )
        
        # Get it using same API instance (data is in-memory)
        playlist = self.spotify_api.get_playlist(created["id"])
        self.assertEqual(playlist["name"], "Public Playlist")

    def test_get_playlist_private_owner(self):
        """Test getting own private playlist."""
        created = self.spotify_api.create_playlist(
            user_id=self.REAL_USER_ID,
            name="Private Playlist",
            public=False
        )
        
        playlist = self.spotify_api.get_playlist(created["id"])
        self.assertEqual(playlist["name"], "Private Playlist")

    def test_get_playlist_private_not_owner(self):
        """Test getting private playlist as non-owner."""
        created = self.spotify_api.create_playlist(
            user_id=self.REAL_USER_ID,
            name="Private Playlist",
            public=False
        )
        
        # Try to access as different API instance (no shared data)
        # Private playlist will appear not found to unauthenticated users
        api = SpotifyApis()
        with self.assertRaises(Exception) as context:
            api.get_playlist(created["id"])
        # Either "not found" or "access denied" is acceptable
        self.assertTrue("not found" in str(context.exception).lower() or "access denied" in str(context.exception).lower())

    def test_get_playlist_not_found(self):
        """Test getting non-existent playlist."""
        with self.assertRaises(Exception) as context:
            self.spotify_api.get_playlist("nonexistent_playlist")
        self.assertIn("not found", str(context.exception).lower())

    def test_change_playlist_details(self):
        """Test changing playlist details."""
        created = self.spotify_api.create_playlist(
            user_id=self.REAL_USER_ID,
            name="Original Name",
            public=True
        )
        
        self.spotify_api.change_playlist_details(
            playlist_id=created["id"],
            name="Updated Name",
            description="New description",
            public=False
        )
        
        updated = self.spotify_api.get_playlist(created["id"])
        self.assertEqual(updated["name"], "Updated Name")
        self.assertEqual(updated["description"], "New description")
        self.assertFalse(updated["public"])

    def test_change_playlist_not_owner(self):
        """Test changing playlist as non-owner."""
        created = self.spotify_api.create_playlist(
            user_id=self.REAL_USER_ID,
            name="Test Playlist",
            public=True
        )
        
        # Try to modify as unauthenticated user
        api = SpotifyApis()
        with self.assertRaises(Exception):
            api.change_playlist_details(
                playlist_id=created["id"],
                name="Hacked Name"
            )

    def test_add_items_to_playlist(self):
        """Test adding tracks to playlist."""
        created = self.spotify_api.create_playlist(
            user_id=self.REAL_USER_ID,
            name="Test Playlist",
            public=True
        )
        
        track_uri = f"spotify:track:{self.REAL_TRACK_ID}"
        result = self.spotify_api.add_items_to_playlist(
            playlist_id=created["id"],
            track_uris=[track_uri]
        )
        self.assertIn("snapshot_id", result)

    def test_add_items_to_playlist_with_position(self):
        """Test adding tracks to playlist at specific position."""
        created = self.spotify_api.create_playlist(
            user_id=self.REAL_USER_ID,
            name="Test Playlist",
            public=True
        )
        
        track_uri = f"spotify:track:{self.REAL_TRACK_ID}"
        result = self.spotify_api.add_items_to_playlist(
            playlist_id=created["id"],
            track_uris=[track_uri],
            position=0
        )
        self.assertIn("snapshot_id", result)

    def test_remove_items_from_playlist(self):
        """Test removing tracks from playlist."""
        created = self.spotify_api.create_playlist(
            user_id=self.REAL_USER_ID,
            name="Test Playlist",
            public=True
        )
        
        track_uri = f"spotify:track:{self.REAL_TRACK_ID}"
        
        # Add track
        self.spotify_api.add_items_to_playlist(
            playlist_id=created["id"],
            track_uris=[track_uri]
        )
        
        # Remove track
        result = self.spotify_api.remove_items_from_playlist(
            playlist_id=created["id"],
            track_uris=[track_uri]
        )
        self.assertIn("snapshot_id", result)

    # --- Search Tests ---

    def test_search_tracks(self):
        """Test searching for tracks."""
        result = self.spotify_api.search(q="test", type=["track"], limit=10)
        self.assertIn("tracks", result)
        self.assertIn("items", result["tracks"])

    def test_search_albums(self):
        """Test searching for albums."""
        result = self.spotify_api.search(q="test", type=["album"], limit=10)
        self.assertIn("albums", result)
        self.assertIn("items", result["albums"])

    def test_search_artists(self):
        """Test searching for artists."""
        result = self.spotify_api.search(q="test", type=["artist"], limit=10)
        self.assertIn("artists", result)
        self.assertIn("items", result["artists"])

    def test_search_playlists(self):
        """Test searching for playlists."""
        result = self.spotify_api.search(q="test", type=["playlist"], limit=10)
        self.assertIn("playlists", result)
        self.assertIn("items", result["playlists"])

    def test_search_multiple_types(self):
        """Test searching for multiple content types."""
        result = self.spotify_api.search(
            q="test",
            type=["track", "album", "artist"],
            limit=5
        )
        self.assertIn("tracks", result)
        self.assertIn("albums", result)
        self.assertIn("artists", result)

    def test_search_pagination(self):
        """Test search with pagination."""
        result = self.spotify_api.search(
            q="test",
            type=["track"],
            limit=5,
            offset=10
        )
        self.assertEqual(result["tracks"]["limit"], 5)
        self.assertEqual(result["tracks"]["offset"], 10)

    # --- Workflow Tests ---

    def test_workflow_create_and_populate_playlist(self):
        """Test workflow: create playlist and add multiple tracks."""
        # Create playlist
        playlist = self.spotify_api.create_playlist(
            user_id=self.REAL_USER_ID,
            name="My Workout Mix",
            description="High energy tracks",
            public=False
        )
        
        # Add tracks
        track_uri = f"spotify:track:{self.REAL_TRACK_ID}"
        self.spotify_api.add_items_to_playlist(
            playlist_id=playlist["id"],
            track_uris=[track_uri]
        )
        
        # Verify playlist
        retrieved = self.spotify_api.get_playlist(playlist["id"])
        self.assertEqual(retrieved["name"], "My Workout Mix")
        self.assertFalse(retrieved["public"])

    def test_workflow_save_and_check_tracks(self):
        """Test workflow: save tracks and verify they're saved."""
        # Save track
        self.spotify_api.save_tracks([self.REAL_TRACK_ID])
        
        # Check it's saved using the check endpoint
        result = self.spotify_api.check_saved_tracks([self.REAL_TRACK_ID])
        self.assertTrue(result[0])

    def test_workflow_follow_and_unfollow_artist(self):
        """Test workflow: follow artist then unfollow."""
        # Follow artist
        self.spotify_api.follow_artists([self.REAL_ARTIST_ID])
        
        # Verify following
        followed = self.spotify_api.get_followed_artists()
        artist_ids = [a["id"] for a in followed["artists"]["items"]]
        self.assertIn(self.REAL_ARTIST_ID, artist_ids)
        
        # Unfollow
        self.spotify_api.unfollow_artists([self.REAL_ARTIST_ID])

    # --- Reset Data Test ---

    def test_reset_data(self):
        """Test resetting data."""
        # Make some changes
        self.spotify_api.save_tracks([self.REAL_TRACK_ID])
        
        # Reset
        self.spotify_api.reset_data()
        
        # Verify authentication cleared
        self.assertIsNone(self.spotify_api.access_token)
        self.assertIsNone(self.spotify_api.current_user_id)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
