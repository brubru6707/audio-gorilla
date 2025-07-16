from typing import Dict, List, Any, Optional
from copy import deepcopy

DEFAULT_STATE = {
    "username": "spotify_user@example.com", # Changed to an email for consistency with login/signup
    "password": "spotify123",
    "authenticated": True, # Assume user is already logged in as per your requirement
    "users": {
        "spotify_user@example.com": {
            "first_name": "Spotify",
            "last_name": "User",
            "email": "spotify_user@example.com",
            "password": "spotify123",
            "verified": True,
            "liked_songs": [101, 103],
            "liked_albums": [201],
            "liked_playlists": [301],
            "following_artists": [401],
            "library_songs": [101, 102, 103],
            "library_albums": [201],
            "downloaded_songs": [101],
            "premium": True
        }
    },
    "songs": {
        101: {"id": 101, "title": "Shape of You", "artist": "Ed Sheeran", "album": "Divide", "duration_ms": 233945, "genre": "Pop"},
        102: {"id": 102, "title": "Bohemian Rhapsody", "artist": "Queen", "album": "A Night at the Opera", "duration_ms": 354000, "genre": "Rock"},
        103: {"id": 103, "title": "Blinding Lights", "artist": "The Weeknd", "album": "After Hours", "duration_ms": 202000, "genre": "Pop"},
        104: {"id": 104, "title": "Watermelon Sugar", "artist": "Harry Styles", "album": "Fine Line", "duration_ms": 174000, "genre": "Pop"},
        105: {"id": 105, "title": "Old Town Road", "artist": "Lil Nas X", "album": "7", "duration_ms": 113000, "genre": "Country Rap"}
    },
    "albums": {
        201: {"id": 201, "title": "Divide", "artist": "Ed Sheeran", "release_year": 2017, "genre": "Pop", "songs": [101]},
        202: {"id": 202, "title": "A Night at the Opera", "artist": "Queen", "release_year": 1975, "genre": "Rock", "songs": [102]},
        203: {"id": 203, "title": "After Hours", "artist": "The Weeknd", "release_year": 2020, "genre": "R&B", "songs": [103]}
    },
    "playlists": {
        301: {"id": 301, "title": "My Favorite Pop Hits", "public": True, "owner": "spotify_user@example.com", "songs": [101, 103, 104], "created_at": "2023-01-15"},
        302: {"id": 302, "title": "Workout Jams", "public": False, "owner": "spotify_user@example.com", "songs": [103, 105], "created_at": "2023-02-01"}
    },
    "artists": {
        401: {"id": 401, "name": "Ed Sheeran", "genre": "Pop", "followers": 15000000},
        402: {"id": 402, "name": "Queen", "genre": "Rock", "followers": 20000000},
        403: {"id": 403, "name": "The Weeknd", "genre": "R&B", "followers": 18000000}
    },
    "reviews": {}, # No dummy reviews needed for initial dummy backend
    "payment_cards": {}, # No dummy payment cards needed for audio context
    "current_song": None,
    "song_queue": [],
    "volume": 75, # Default volume set higher
    "premium_subscriptions": {
        # Dummy premium subscription for the user
        "spotify_user@example.com": {"plan": "Premium Individual", "start_date": "2023-01-01", "end_date": "2024-01-01"}
    },
    "id_counters": {
        "song": 106, # Next available ID for new songs
        "album": 204, # Next available ID for new albums
        "playlist": 303, # Next available ID for new playlists
        "artist": 404, # Next available ID for new artists
        "review": 0,
        "payment_card": 0,
    }
}

class SpotifyApis:
    def __init__(self):
        self.username: str
        self.password: str
        self.authenticated: bool
        self.users: Dict[str, Dict[str, Any]]
        self.songs: Dict[int, Dict[str, Any]]
        self.albums: Dict[int, Dict[str, Any]]
        self.playlists: Dict[int, Dict[str, Any]]
        self.artists: Dict[int, Dict[str, Any]]
        self.reviews: Dict[int, Dict[str, Any]]
        self.payment_cards: Dict[int, Dict[str, Any]]
        self.current_song: Optional[Dict[str, Any]]
        self.song_queue: List[Dict[str, Any]]
        self.volume: int
        self.premium_subscriptions: Dict[str, Dict[str, Any]] # Changed type hint to str for email key
        self.id_counters: Dict[str, int]
        self._load_default_state()

    def _load_default_state(self) -> None:
        """Load the default state into the SpotifyAPI instance."""
        default_state_copy = deepcopy(DEFAULT_STATE)
        self.username = default_state_copy["username"]
        self.password = default_state_copy["password"]
        self.authenticated = default_state_copy["authenticated"]
        self.users = default_state_copy["users"]
        self.songs = default_state_copy["songs"]
        self.albums = default_state_copy["albums"]
        self.playlists = default_state_copy["playlists"]
        self.artists = default_state_copy["artists"]
        self.reviews = default_state_copy["reviews"]
        self.payment_cards = default_state_copy["payment_cards"]
        self.current_song = default_state_copy["current_song"]
        self.song_queue = default_state_copy["song_queue"]
        self.volume = default_state_copy["volume"]
        self.premium_subscriptions = default_state_copy["premium_subscriptions"]
        self.id_counters = default_state_copy["id_counters"]

    # --- Account Management ---
    def signup(self, first_name: str, last_name: str, email: str, password: str) -> Dict[str, bool]:
        """
        Sign up a new user with first name, last name, email and password.
        Args:
            first_name (str): First name of the user.
            last_name (str): Last name of the user.
            email (str): Email of the user.
            password (str): Password of the user.
        Returns:
            Dict[str, bool]: {"signup_status": True} if signup successful, {"signup_status": False} otherwise.
        """
        if email in self.users:
            return {"signup_status": False, "message": "Email already exists."}

        # In a real system, you'd add more robust password handling (hashing)
        self.users[email] = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "verified": False,
            "liked_songs": [],
            "liked_albums": [],
            "liked_playlists": [],
            "following_artists": [],
            "library_songs": [],
            "library_albums": [],
            "downloaded_songs": [],
            "premium": False
        }
        return {"signup_status": True, "message": "Signup successful."}

    def login(self, email: str, password: str) -> Dict[str, bool]:
        """
        Log in a user with email and password.
        Args:
            email (str): Email of the user.
            password (str): Password of the user.
        Returns:
            Dict[str, bool]: {"login_status": True} if login successful, {"login_status": False} otherwise.
        """
        if email in self.users and self.users[email]["password"] == password:
            self.authenticated = True
            self.username = email
            return {"login_status": True, "message": "Login successful."}
        return {"login_status": False, "message": "Invalid email or password."}

    def logout(self) -> Dict[str, bool]:
        """
        Log out the current user.
        Returns:
            Dict[str, bool]: {"logout_status": True} if logout successful, {"logout_status": False} otherwise.
        """
        if not self.authenticated:
            return {"logout_status": False, "message": "No user is currently logged in."}

        self.authenticated = False
        self.username = ""  # Clear the username on logout
        return {"logout_status": True, "message": "Logout successful."}

    def send_verification_code(self, email: str) -> Dict[str, bool]:
        """
        Send a verification code to the user's email.
        Args:
            email (str): Email of the user.
        Returns:
            Dict[str, bool]: {"send_status": True} if code sent successfully, {"send_status": False} otherwise.
        """
        if email not in self.users:
            return {"send_status": False, "message": "User with this email does not exist."}

        # In a real implementation, a verification code would be generated and sent
        return {"send_status": True, "message": f"Verification code sent to {email}."}

    def verify_account(self, email: str, verification_code: str) -> Dict[str, bool]:
        """
        Verify user account with a verification code.
        Args:
            email (str): Email of the user.
            verification_code (str): Verification code sent to user's email.
        Returns:
            Dict[str, bool]: {"verification_status": True} if verification successful, {"verification_status": False} otherwise.
        """
        if email not in self.users:
            return {"verification_status": False, "message": "User with this email does not exist."}

        # Dummy verification: always assume code is "123456" for testing
        if verification_code == "123456":
            self.users[email]["verified"] = True
            return {"verification_status": True, "message": "Account verified successfully."}
        return {"verification_status": False, "message": "Invalid verification code."}

    def send_password_reset_code(self, email: str) -> Dict[str, bool]:
        """
        Send a password reset code to the user's email.
        Args:
            email (str): Email of the user.
        Returns:
            Dict[str, bool]: {"send_status": True} if code sent successfully, {"send_status": False} otherwise.
        """
        if email not in self.users:
            return {"send_status": False, "message": "User with this email does not exist."}

        # In a real implementation, a password reset code would be generated and sent
        return {"send_status": True, "message": f"Password reset code sent to {email}."}

    def reset_password(self, email: str, password_reset_code: str, new_password: str) -> Dict[str, bool]:
        """
        Reset user password with a reset code.
        Args:
            email (str): Email of the user.
            password_reset_code (str): Password reset code sent to user's email.
            new_password (str): New password to set.
        Returns:
            Dict[str, bool]: {"reset_status": True} if password reset successful, {"reset_status": False} otherwise.
        """
        if email not in self.users:
            return {"reset_status": False, "message": "User with this email does not exist."}

        # Dummy verification: always assume code is "654321" for testing
        if password_reset_code == "654321":
            self.users[email]["password"] = new_password
            return {"reset_status": True, "message": "Password reset successfully."}
        return {"reset_status": False, "message": "Invalid password reset code."}

    def show_profile(self) -> Dict[str, Any]:
        """
        Show the current user's profile information.
        Returns:
            Dict[str, Any]: Dictionary containing user profile information, or empty if not authenticated.
        """
        if not self.authenticated or self.username not in self.users:
            return {"profile": {}, "message": "Not authenticated."}

        user = self.users[self.username]
        return {
            "profile": {
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "verified": user["verified"],
                "premium": user["premium"]
            },
            "message": "User profile retrieved."
        }

    def update_account_name(self, first_name: str, last_name: str) -> Dict[str, bool]:
        """
        Update the current user's first and last name.
        Args:
            first_name (str): New first name.
            last_name (str): New last name.
        Returns:
            Dict[str, bool]: {"update_status": True} if update successful, {"update_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"update_status": False, "message": "Not authenticated."}

        self.users[self.username]["first_name"] = first_name
        self.users[self.username]["last_name"] = last_name
        return {"update_status": True, "message": "Account name updated successfully."}

    def delete_account(self) -> Dict[str, bool]:
        """
        Delete the current user account.
        Returns:
            Dict[str, bool]: {"delete_status": True} if deletion successful, {"delete_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"delete_status": False, "message": "Not authenticated."}

        del self.users[self.username]
        self.authenticated = False
        self.username = ""  # Clear the username on account deletion
        return {"delete_status": True, "message": "Account deleted successfully."}

    # --- Music Browse & Discovery ---
    def show_genres(self) -> Dict[str, List[str]]:
        """
        Show available music genres.
        Returns:
            Dict[str, List[str]]: {"genres": ["Pop", "Rock", ...]}
        """
        return {"genres": ["Pop", "Rock", "Hip-Hop", "Jazz", "Classical", "Electronic", "Country", "R&B"],
                "message": "Available genres retrieved."}

    def search_songs(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for songs by title or artist.
        Args:
            query (str): Search query.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"songs": [...]} List of song dictionaries matching the query.
        """
        matching_songs = []
        for song in self.songs.values():
            if query.lower() in song["title"].lower() or query.lower() in song["artist"].lower():
                matching_songs.append(song)
        return {"songs": matching_songs, "message": f"Songs matching '{query}' retrieved."}

    def show_song(self, song_id: int) -> Dict[str, Any]:
        """
        Show details of a specific song.
        Args:
            song_id (int): ID of the song.
        Returns:
            Dict[str, Any]: {"song": {...}} Dictionary containing song details, or empty if not found.
        """
        if song_id not in self.songs:
            return {"song": {}, "message": f"Song with ID {song_id} not found."}
        return {"song": self.songs[song_id], "message": f"Details for song ID {song_id} retrieved."}

    def show_song_privates(self, song_id: int) -> Dict[str, Any]:
        """
        Show private user-specific information about a song (liked, in library, downloaded).
        Args:
            song_id (int): ID of the song.
        Returns:
            Dict[str, Any]: {"privates": {...}} Dictionary containing private song information.
        """
        if not self.authenticated or self.username not in self.users:
            return {"privates": {}, "message": "Not authenticated."}

        if song_id not in self.songs:
            return {"privates": {}, "message": f"Song with ID {song_id} not found."}

        user = self.users[self.username]
        return {
            "privates": {
                "liked": song_id in user["liked_songs"],
                "in_library": song_id in user["library_songs"],
                "downloaded": song_id in user["downloaded_songs"]
            },
            "message": f"Private details for song ID {song_id} retrieved."
        }

    def like_song(self, song_id: int) -> Dict[str, bool]:
        """
        Like a song.
        Args:
            song_id (int): ID of the song to like.
        Returns:
            Dict[str, bool]: {"like_status": True} if like successful, {"like_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"like_status": False, "message": "Not authenticated."}
        if song_id not in self.songs:
            return {"like_status": False, "message": f"Song with ID {song_id} not found."}

        if song_id not in self.users[self.username]["liked_songs"]:
            self.users[self.username]["liked_songs"].append(song_id)
            return {"like_status": True, "message": f"Song ID {song_id} liked."}
        return {"like_status": False, "message": f"Song ID {song_id} is already liked."}

    def unlike_song(self, song_id: int) -> Dict[str, bool]:
        """
        Unlike a song.
        Args:
            song_id (int): ID of the song to unlike.
        Returns:
            Dict[str, bool]: {"unlike_status": True} if unlike successful, {"unlike_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"unlike_status": False, "message": "Not authenticated."}
        if song_id not in self.songs:
            return {"unlike_status": False, "message": f"Song with ID {song_id} not found."}

        if song_id in self.users[self.username]["liked_songs"]:
            self.users[self.username]["liked_songs"].remove(song_id)
            return {"unlike_status": True, "message": f"Song ID {song_id} unliked."}
        return {"unlike_status": False, "message": f"Song ID {song_id} is not liked."}

    def show_liked_songs(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show all liked songs for the current user.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"songs": [...]} List of liked song dictionaries.
        """
        if not self.authenticated or self.username not in self.users:
            return {"songs": [], "message": "Not authenticated."}

        liked_songs = []
        for song_id in self.users[self.username]["liked_songs"]:
            if song_id in self.songs:
                liked_songs.append(self.songs[song_id])
        return {"songs": liked_songs, "message": "Liked songs retrieved."}

    def search_albums(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for albums by title or artist.
        Args:
            query (str): Search query.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"albums": [...]} List of album dictionaries matching the query.
        """
        matching_albums = []
        for album in self.albums.values():
            if query.lower() in album["title"].lower() or query.lower() in album["artist"].lower():
                matching_albums.append(album)
        return {"albums": matching_albums, "message": f"Albums matching '{query}' retrieved."}

    def show_album(self, album_id: int) -> Dict[str, Any]:
        """
        Show details of a specific album.
        Args:
            album_id (int): ID of the album.
        Returns:
            Dict[str, Any]: {"album": {...}} Dictionary containing album details, or empty if not found.
        """
        if album_id not in self.albums:
            return {"album": {}, "message": f"Album with ID {album_id} not found."}
        return {"album": self.albums[album_id], "message": f"Details for album ID {album_id} retrieved."}

    def show_album_privates(self, album_id: int) -> Dict[str, Any]:
        """
        Show private user-specific information about an album (liked, in library).
        Args:
            album_id (int): ID of the album.
        Returns:
            Dict[str, Any]: {"privates": {...}} Dictionary containing private album information.
        """
        if not self.authenticated or self.username not in self.users:
            return {"privates": {}, "message": "Not authenticated."}

        if album_id not in self.albums:
            return {"privates": {}, "message": f"Album with ID {album_id} not found."}

        user = self.users[self.username]
        return {
            "privates": {
                "liked": album_id in user["liked_albums"],
                "in_library": album_id in user["library_albums"]
            },
            "message": f"Private details for album ID {album_id} retrieved."
        }

    def like_album(self, album_id: int) -> Dict[str, bool]:
        """
        Like an album.
        Args:
            album_id (int): ID of the album to like.
        Returns:
            Dict[str, bool]: {"like_status": True} if like successful, {"like_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"like_status": False, "message": "Not authenticated."}
        if album_id not in self.albums:
            return {"like_status": False, "message": f"Album with ID {album_id} not found."}

        if album_id not in self.users[self.username]["liked_albums"]:
            self.users[self.username]["liked_albums"].append(album_id)
            return {"like_status": True, "message": f"Album ID {album_id} liked."}
        return {"like_status": False, "message": f"Album ID {album_id} is already liked."}

    def unlike_album(self, album_id: int) -> Dict[str, bool]:
        """
        Unlike an album.
        Args:
            album_id (int): ID of the album to unlike.
        Returns:
            Dict[str, bool]: {"unlike_status": True} if unlike successful, {"unlike_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"unlike_status": False, "message": "Not authenticated."}
        if album_id not in self.albums:
            return {"unlike_status": False, "message": f"Album with ID {album_id} not found."}

        if album_id in self.users[self.username]["liked_albums"]:
            self.users[self.username]["liked_albums"].remove(album_id)
            return {"unlike_status": True, "message": f"Album ID {album_id} unliked."}
        return {"unlike_status": False, "message": f"Album ID {album_id} is not liked."}

    def show_liked_albums(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show all liked albums for the current user.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"albums": [...]} List of liked album dictionaries.
        """
        if not self.authenticated or self.username not in self.users:
            return {"albums": [], "message": "Not authenticated."}

        liked_albums = []
        for album_id in self.users[self.username]["liked_albums"]:
            if album_id in self.albums:
                liked_albums.append(self.albums[album_id])
        return {"albums": liked_albums, "message": "Liked albums retrieved."}

    def show_playlist_library(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show the current user's playlist library (playlists they own).
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"playlists": [...]} List of playlist dictionaries.
        """
        if not self.authenticated or self.username not in self.users:
            return {"playlists": [], "message": "Not authenticated."}

        user_playlists = []
        for playlist_id, playlist in self.playlists.items():
            if playlist["owner"] == self.username:
                user_playlists.append(playlist)
        return {"playlists": user_playlists, "message": "User's playlists retrieved."}

    def search_playlists(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for playlists by title.
        Args:
            query (str): Search query.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"playlists": [...]} List of playlist dictionaries matching the query.
        """
        matching_playlists = []
        for playlist in self.playlists.values():
            if query.lower() in playlist["title"].lower():
                matching_playlists.append(playlist)
        return {"playlists": matching_playlists, "message": f"Playlists matching '{query}' retrieved."}

    def show_playlist(self, playlist_id: int) -> Dict[str, Any]:
        """
        Show details of a specific playlist.
        Args:
            playlist_id (int): ID of the playlist.
        Returns:
            Dict[str, Any]: {"playlist": {...}} Dictionary containing playlist details, or empty if not found.
        """
        if playlist_id not in self.playlists:
            return {"playlist": {}, "message": f"Playlist with ID {playlist_id} not found."}
        return {"playlist": self.playlists[playlist_id], "message": f"Details for playlist ID {playlist_id} retrieved."}

    def show_playlist_privates(self, playlist_id: int) -> Dict[str, Any]:
        """
        Show private user-specific information about a playlist (liked, owner status).
        Args:
            playlist_id (int): ID of the playlist.
        Returns:
            Dict[str, Any]: {"privates": {...}} Dictionary containing private playlist information.
        """
        if not self.authenticated or self.username not in self.users:
            return {"privates": {}, "message": "Not authenticated."}

        if playlist_id not in self.playlists:
            return {"privates": {}, "message": f"Playlist with ID {playlist_id} not found."}

        user = self.users[self.username]
        return {
            "privates": {
                "liked": playlist_id in user["liked_playlists"],
                "owner": self.playlists[playlist_id]["owner"] == self.username
            },
            "message": f"Private details for playlist ID {playlist_id} retrieved."
        }

    def create_playlist(self, title: str, is_public: bool) -> Dict[str, Any]:
        """
        Create a new playlist for the current user.
        Args:
            title (str): Title of the playlist.
            is_public (bool): Whether the playlist is public.
        Returns:
            Dict[str, Any]: {"playlist": {...}} Dictionary containing new playlist information, or empty if not authenticated.
        """
        if not self.authenticated or self.username not in self.users:
            return {"playlist": {}, "message": "Not authenticated."}

        playlist_id = self.id_counters["playlist"]
        self.id_counters["playlist"] += 1

        new_playlist = {
            "id": playlist_id,
            "title": title,
            "public": is_public,
            "owner": self.username,
            "songs": [],
            "created_at": "2023-01-01"  # Dummy date
        }
        self.playlists[playlist_id] = new_playlist
        return {"playlist": new_playlist, "message": f"Playlist '{title}' created with ID {playlist_id}."}

    def update_playlist_visibility(self, playlist_id: int, is_public: bool) -> Dict[str, bool]:
        """
        Update the visibility of a playlist (public or private).
        Args:
            playlist_id (int): ID of the playlist to update.
            is_public (bool): New visibility status (True for public, False for private).
        Returns:
            Dict[str, bool]: {"update_status": True} if update successful, {"update_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"update_status": False, "message": "Not authenticated."}
        if playlist_id not in self.playlists:
            return {"update_status": False, "message": f"Playlist with ID {playlist_id} not found."}
        if self.playlists[playlist_id]["owner"] != self.username:
            return {"update_status": False, "message": "You are not the owner of this playlist."}

        self.playlists[playlist_id]["public"] = is_public
        return {"update_status": True, "message": f"Playlist ID {playlist_id} visibility updated."}

    def rename_playlist(self, playlist_id: int, new_title: str) -> Dict[str, bool]:
        """
        Rename a playlist.
        Args:
            playlist_id (int): ID of the playlist to rename.
            new_title (str): New title for the playlist.
        Returns:
            Dict[str, bool]: {"update_status": True} if rename successful, {"update_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"update_status": False, "message": "Not authenticated."}
        if playlist_id not in self.playlists:
            return {"update_status": False, "message": f"Playlist with ID {playlist_id} not found."}
        if self.playlists[playlist_id]["owner"] != self.username:
            return {"update_status": False, "message": "You are not the owner of this playlist."}

        self.playlists[playlist_id]["title"] = new_title
        return {"update_status": True, "message": f"Playlist ID {playlist_id} renamed to '{new_title}'."}

    def delete_playlist(self, playlist_id: int) -> Dict[str, bool]:
        """
        Delete a playlist.
        Args:
            playlist_id (int): ID of the playlist to delete.
        Returns:
            Dict[str, bool]: {"delete_status": True} if deletion successful, {"delete_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"delete_status": False, "message": "Not authenticated."}
        if playlist_id not in self.playlists:
            return {"delete_status": False, "message": f"Playlist with ID {playlist_id} not found."}
        if self.playlists[playlist_id]["owner"] != self.username:
            return {"delete_status": False, "message": "You are not the owner of this playlist."}

        del self.playlists[playlist_id]
        return {"delete_status": True, "message": f"Playlist ID {playlist_id} deleted."}

    def like_playlist(self, playlist_id: int) -> Dict[str, bool]:
        """
        Like a playlist.
        Args:
            playlist_id (int): ID of the playlist to like.
        Returns:
            Dict[str, bool]: {"like_status": True} if like successful, {"like_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"like_status": False, "message": "Not authenticated."}
        if playlist_id not in self.playlists:
            return {"like_status": False, "message": f"Playlist with ID {playlist_id} not found."}

        if playlist_id not in self.users[self.username]["liked_playlists"]:
            self.users[self.username]["liked_playlists"].append(playlist_id)
            return {"like_status": True, "message": f"Playlist ID {playlist_id} liked."}
        return {"like_status": False, "message": f"Playlist ID {playlist_id} is already liked."}

    def unlike_playlist(self, playlist_id: int) -> Dict[str, bool]:
        """
        Unlike a playlist.
        Args:
            playlist_id (int): ID of the playlist to unlike.
        Returns:
            Dict[str, bool]: {"unlike_status": True} if unlike successful, {"unlike_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"unlike_status": False, "message": "Not authenticated."}
        if playlist_id not in self.playlists:
            return {"unlike_status": False, "message": f"Playlist with ID {playlist_id} not found."}

        if playlist_id in self.users[self.username]["liked_playlists"]:
            self.users[self.username]["liked_playlists"].remove(playlist_id)
            return {"unlike_status": True, "message": f"Playlist ID {playlist_id} unliked."}
        return {"unlike_status": False, "message": f"Playlist ID {playlist_id} is not liked."}

    def show_liked_playlists(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show all liked playlists for the current user.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"playlists": [...]} List of liked playlist dictionaries.
        """
        if not self.authenticated or self.username not in self.users:
            return {"playlists": [], "message": "Not authenticated."}

        liked_playlists = []
        for playlist_id in self.users[self.username]["liked_playlists"]:
            if playlist_id in self.playlists:
                liked_playlists.append(self.playlists[playlist_id])
        return {"playlists": liked_playlists, "message": "Liked playlists retrieved."}

    def search_artists(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for artists by name.
        Args:
            query (str): Search query.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"artists": [...]} List of artist dictionaries matching the query.
        """
        matching_artists = []
        for artist in self.artists.values():
            if query.lower() in artist["name"].lower():
                matching_artists.append(artist)
        return {"artists": matching_artists, "message": f"Artists matching '{query}' retrieved."}

    def show_artist(self, artist_id: int) -> Dict[str, Any]:
        """
        Show details of a specific artist.
        Args:
            artist_id (int): ID of the artist.
        Returns:
            Dict[str, Any]: {"artist": {...}} Dictionary containing artist details, or empty if not found.
        """
        if artist_id not in self.artists:
            return {"artist": {}, "message": f"Artist with ID {artist_id} not found."}
        return {"artist": self.artists[artist_id], "message": f"Details for artist ID {artist_id} retrieved."}

    def show_artist_following(self, artist_id: int) -> Dict[str, bool]:
        """
        Check if the current user is following an artist.
        Args:
            artist_id (int): ID of the artist.
        Returns:
            Dict[str, bool]: {"following_status": True} if following, {"following_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"following_status": False, "message": "Not authenticated."}
        if artist_id not in self.artists:
            return {"following_status": False, "message": f"Artist with ID {artist_id} not found."}

        return {"following_status": artist_id in self.users[self.username]["following_artists"],
                "message": f"Following status for artist ID {artist_id} retrieved."}

    def show_following_artists(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show artists the current user is following.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"artists": [...]} List of followed artist dictionaries.
        """
        if not self.authenticated or self.username not in self.users:
            return {"artists": [], "message": "Not authenticated."}

        following_artists = []
        for artist_id in self.users[self.username]["following_artists"]:
            if artist_id in self.artists:
                following_artists.append(self.artists[artist_id])
        return {"artists": following_artists, "message": "Following artists retrieved."}

    def follow_artist(self, artist_id: int) -> Dict[str, bool]:
        """
        Follow an artist.
        Args:
            artist_id (int): ID of the artist to follow.
        Returns:
            Dict[str, bool]: {"follow_status": True} if follow successful, {"follow_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"follow_status": False, "message": "Not authenticated."}
        if artist_id not in self.artists:
            return {"follow_status": False, "message": f"Artist with ID {artist_id} not found."}

        if artist_id not in self.users[self.username]["following_artists"]:
            self.users[self.username]["following_artists"].append(artist_id)
            return {"follow_status": True, "message": f"Artist ID {artist_id} followed."}
        return {"follow_status": False, "message": f"Artist ID {artist_id} is already followed."}

    def unfollow_artist(self, artist_id: int) -> Dict[str, bool]:
        """
        Unfollow an artist.
        Args:
            artist_id (int): ID of the artist to unfollow.
        Returns:
            Dict[str, bool]: {"unfollow_status": True} if unfollow successful, {"unfollow_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"unfollow_status": False, "message": "Not authenticated."}
        if artist_id not in self.artists:
            return {"unfollow_status": False, "message": f"Artist with ID {artist_id} not found."}

        if artist_id in self.users[self.username]["following_artists"]:
            self.users[self.username]["following_artists"].remove(artist_id)
            return {"unfollow_status": True, "message": f"Artist ID {artist_id} unfollowed."}
        return {"unfollow_status": False, "message": f"Artist ID {artist_id} is not followed."}

    # --- Library Management ---
    def show_song_library(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show the current user's song library.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"songs": [...]} List of song dictionaries in library.
        """
        if not self.authenticated or self.username not in self.users:
            return {"songs": [], "message": "Not authenticated."}

        library_songs = []
        for song_id in self.users[self.username]["library_songs"]:
            if song_id in self.songs:
                library_songs.append(self.songs[song_id])
        return {"songs": library_songs, "message": "Song library retrieved."}

    def add_song_to_library(self, song_id: int) -> Dict[str, bool]:
        """
        Add a song to the current user's library.
        Args:
            song_id (int): ID of the song to add.
        Returns:
            Dict[str, bool]: {"add_status": True} if add successful, {"add_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"add_status": False, "message": "Not authenticated."}
        if song_id not in self.songs:
            return {"add_status": False, "message": f"Song with ID {song_id} not found."}

        if song_id not in self.users[self.username]["library_songs"]:
            self.users[self.username]["library_songs"].append(song_id)
            return {"add_status": True, "message": f"Song ID {song_id} added to library."}
        return {"add_status": False, "message": f"Song ID {song_id} is already in library."}

    def remove_song_from_library(self, song_id: int) -> Dict[str, bool]:
        """
        Remove a song from the current user's library.
        Args:
            song_id (int): ID of the song to remove.
        Returns:
            Dict[str, bool]: {"remove_status": True} if remove successful, {"remove_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"remove_status": False, "message": "Not authenticated."}
        if song_id not in self.songs:
            return {"remove_status": False, "message": f"Song with ID {song_id} not found."}

        if song_id in self.users[self.username]["library_songs"]:
            self.users[self.username]["library_songs"].remove(song_id)
            return {"remove_status": True, "message": f"Song ID {song_id} removed from library."}
        return {"remove_status": False, "message": f"Song ID {song_id} is not in library."}

    def show_album_library(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show the current user's album library.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"albums": [...]} List of album dictionaries in library.
        """
        if not self.authenticated or self.username not in self.users:
            return {"albums": [], "message": "Not authenticated."}

        library_albums = []
        for album_id in self.users[self.username]["library_albums"]:
            if album_id in self.albums:
                library_albums.append(self.albums[album_id])
        return {"albums": library_albums, "message": "Album library retrieved."}

    def add_album_to_library(self, album_id: int) -> Dict[str, bool]:
        """
        Add an album to the current user's library.
        Args:
            album_id (int): ID of the album to add.
        Returns:
            Dict[str, bool]: {"add_status": True} if add successful, {"add_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"add_status": False, "message": "Not authenticated."}
        if album_id not in self.albums:
            return {"add_status": False, "message": f"Album with ID {album_id} not found."}

        if album_id not in self.users[self.username]["library_albums"]:
            self.users[self.username]["library_albums"].append(album_id)
            return {"add_status": True, "message": f"Album ID {album_id} added to library."}
        return {"add_status": False, "message": f"Album ID {album_id} is already in library."}

    def remove_album_from_library(self, album_id: int) -> Dict[str, bool]:
        """
        Remove an album from the current user's library.
        Args:
            album_id (int): ID of the album to remove.
        Returns:
            Dict[str, bool]: {"remove_status": True} if remove successful, {"remove_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"remove_status": False, "message": "Not authenticated."}
        if album_id not in self.albums:
            return {"remove_status": False, "message": f"Album with ID {album_id} not found."}

        if album_id in self.users[self.username]["library_albums"]:
            self.users[self.username]["library_albums"].remove(album_id)
            return {"remove_status": True, "message": f"Album ID {album_id} removed from library."}
        return {"remove_status": False, "message": f"Album ID {album_id} is not in library."}

    def add_song_to_playlist(self, playlist_id: int, song_id: int) -> Dict[str, bool]:
        """
        Add a song to a playlist owned by the current user.
        Args:
            playlist_id (int): ID of the playlist.
            song_id (int): ID of the song to add.
        Returns:
            Dict[str, bool]: {"add_status": True} if add successful, {"add_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"add_status": False, "message": "Not authenticated."}
        if playlist_id not in self.playlists:
            return {"add_status": False, "message": f"Playlist with ID {playlist_id} not found."}
        if song_id not in self.songs:
            return {"add_status": False, "message": f"Song with ID {song_id} not found."}
        if self.playlists[playlist_id]["owner"] != self.username:
            return {"add_status": False, "message": "You are not the owner of this playlist."}

        if song_id not in self.playlists[playlist_id]["songs"]:
            self.playlists[playlist_id]["songs"].append(song_id)
            return {"add_status": True, "message": f"Song ID {song_id} added to playlist ID {playlist_id}."}
        return {"add_status": False, "message": f"Song ID {song_id} is already in playlist ID {playlist_id}."}

    def remove_song_from_playlist(self, playlist_id: int, song_id: int) -> Dict[str, bool]:
        """
        Remove a song from a playlist owned by the current user.
        Args:
            playlist_id (int): ID of the playlist.
            song_id (int): ID of the song to remove.
        Returns:
            Dict[str, bool]: {"remove_status": True} if remove successful, {"remove_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"remove_status": False, "message": "Not authenticated."}
        if playlist_id not in self.playlists:
            return {"remove_status": False, "message": f"Playlist with ID {playlist_id} not found."}
        if song_id not in self.songs:
            return {"remove_status": False, "message": f"Song with ID {song_id} not found."}
        if self.playlists[playlist_id]["owner"] != self.username:
            return {"remove_status": False, "message": "You are not the owner of this playlist."}

        if song_id in self.playlists[playlist_id]["songs"]:
            self.playlists[playlist_id]["songs"].remove(song_id)
            return {"remove_status": True, "message": f"Song ID {song_id} removed from playlist ID {playlist_id}."}
        return {"remove_status": False, "message": f"Song ID {song_id} is not in playlist ID {playlist_id}."}

    def show_downloaded_songs(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show the current user's downloaded songs.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"songs": [...]} List of downloaded song dictionaries.
        """
        if not self.authenticated or self.username not in self.users:
            return {"songs": [], "message": "Not authenticated."}

        downloaded_songs = []
        for song_id in self.users[self.username]["downloaded_songs"]:
            if song_id in self.songs:
                downloaded_songs.append(self.songs[song_id])
        return {"songs": downloaded_songs, "message": "Downloaded songs retrieved."}

    def download_song(self, song_id: int) -> Dict[str, bool]:
        """
        Download a song for the current user.
        Args:
            song_id (int): ID of the song to download.
        Returns:
            Dict[str, bool]: {"download_status": True} if download successful, {"download_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"download_status": False, "message": "Not authenticated."}
        if song_id not in self.songs:
            return {"download_status": False, "message": f"Song with ID {song_id} not found."}

        if song_id not in self.users[self.username]["downloaded_songs"]:
            self.users[self.username]["downloaded_songs"].append(song_id)
            return {"download_status": True, "message": f"Song ID {song_id} downloaded."}
        return {"download_status": False, "message": f"Song ID {song_id} is already downloaded."}
    
    def remove_downloaded_song(self, song_id: int) -> Dict[str, bool]:
        """
        Remove a downloaded song for the current user.
        Args:
            song_id (int): ID of the song to remove.
        Returns:
            Dict[str, bool]: {"remove_status": True} if remove successful, {"remove_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"remove_status": False, "message": "Not authenticated."}
        if song_id not in self.songs:
            return {"remove_status": False, "message": f"Song with ID {song_id} not found."}

        if song_id in self.users[self.username]["downloaded_songs"]:
            self.users[self.username]["downloaded_songs"].remove(song_id)
            return {"remove_status": True, "message": f"Song ID {song_id} removed from downloads."}
        return {"remove_status": False, "message": f"Song ID {song_id} is not downloaded."}

    # --- Playback Control ---
    def play_song(self, song_id: int) -> Dict[str, bool]:
        """
        Start playing a song.
        Args:
            song_id (int): ID of the song to play.
        Returns:
            Dict[str, bool]: {"play_status": True} if song starts playing, {"play_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"play_status": False, "message": "Not authenticated."}
        if song_id not in self.songs:
            return {"play_status": False, "message": f"Song with ID {song_id} not found."}

        self.current_song = self.songs[song_id]
        self.song_queue = [] # Clear queue when new song is played directly
        return {"play_status": True, "message": f"Now playing: {self.current_song['title']} by {self.current_song['artist']}."}

    def pause_song(self) -> Dict[str, bool]:
        """
        Pause the currently playing song.
        Returns:
            Dict[str, bool]: {"pause_status": True} if paused, {"pause_status": False} otherwise.
        """
        if not self.authenticated or not self.current_song:
            return {"pause_status": False, "message": "No song is currently playing."}

        # In a real system, this would interact with an audio player
        self.current_song = None # Simulating pause by clearing current song for simplicity
        return {"pause_status": True, "message": "Song paused."}

    def resume_song(self) -> Dict[str, bool]:
        """
        Resume the last paused song or the current song if available.
        Returns:
            Dict[str, bool]: {"resume_status": True} if resumed, {"resume_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"resume_status": False, "message": "Not authenticated."}
        if not self.current_song and self.song_queue:
            # If nothing is currently playing but there's a queue, play the next in queue
            self.current_song = self.song_queue.pop(0)
            return {"resume_status": True, "message": f"Resuming playback with: {self.current_song['title']}."}
        elif self.current_song:
            return {"resume_status": True, "message": f"Resuming playback of: {self.current_song['title']}."}
        return {"resume_status": False, "message": "No song to resume."}

    def skip_song(self) -> Dict[str, bool]:
        """
        Skip to the next song in the queue.
        Returns:
            Dict[str, bool]: {"skip_status": True} if skipped, {"skip_status": False} otherwise.
        """
        if not self.authenticated or not self.song_queue:
            return {"skip_status": False, "message": "No more songs in the queue to skip to."}

        self.current_song = self.song_queue.pop(0)
        return {"skip_status": True, "message": f"Skipped to next song: {self.current_song['title']}."}

    def previous_song(self) -> Dict[str, bool]:
        """
        Go back to the previous song (dummy implementation - will just stop current).
        Returns:
            Dict[str, bool]: {"previous_status": True} if successful, {"previous_status": False} otherwise.
        """
        if not self.authenticated or not self.current_song:
            return {"previous_status": False, "message": "No song currently playing or previous song available."}

        # In a real player, you'd manage a history stack. For dummy, just "stop"
        self.current_song = None
        return {"previous_status": True, "message": "Went back to previous song (simulated stop)."}

    def set_volume(self, volume_level: int) -> Dict[str, bool]:
        """
        Set the playback volume.
        Args:
            volume_level (int): Volume level from 0 to 100.
        Returns:
            Dict[str, bool]: {"set_status": True} if set, {"set_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"set_status": False, "message": "Not authenticated."}

        if 0 <= volume_level <= 100:
            self.volume = volume_level
            return {"set_status": True, "message": f"Volume set to {volume_level}."}
        return {"set_status": False, "message": "Volume level must be between 0 and 100."}

    def get_volume(self) -> Dict[str, int]:
        """
        Get the current playback volume.
        Returns:
            Dict[str, int]: {"volume": current_volume_level}
        """
        if not self.authenticated or self.username not in self.users:
            return {"volume": -1, "message": "Not authenticated."} # -1 indicates error

        return {"volume": self.volume, "message": f"Current volume is {self.volume}."}

    def show_current_song(self) -> Dict[str, Any]:
        """
        Show details of the currently playing song.
        Returns:
            Dict[str, Any]: {"current_song": {...}} Dictionary containing song details, or empty if nothing is playing.
        """
        if not self.authenticated or self.username not in self.users:
            return {"current_song": {}, "message": "Not authenticated."}
        if not self.current_song:
            return {"current_song": {}, "message": "No song is currently playing."}

        return {"current_song": self.current_song, "message": "Current song details retrieved."}

    def add_song_to_queue(self, song_id: int) -> Dict[str, bool]:
        """
        Add a song to the playback queue.
        Args:
            song_id (int): ID of the song to add to the queue.
        Returns:
            Dict[str, bool]: {"add_status": True} if added, {"add_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"add_status": False, "message": "Not authenticated."}
        if song_id not in self.songs:
            return {"add_status": False, "message": f"Song with ID {song_id} not found."}

        self.song_queue.append(self.songs[song_id])
        return {"add_status": True, "message": f"Song '{self.songs[song_id]['title']}' added to queue."}

    def show_song_queue(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show the current playback queue.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"queue": [...]} List of song dictionaries in the queue.
        """
        if not self.authenticated or self.username not in self.users:
            return {"queue": [], "message": "Not authenticated."}

        return {"queue": self.song_queue, "message": "Playback queue retrieved."}

    def clear_song_queue(self) -> Dict[str, bool]:
        """
        Clear the current playback queue.
        Returns:
            Dict[str, bool]: {"clear_status": True} if cleared, {"clear_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"clear_status": False, "message": "Not authenticated."}

        self.song_queue = []
        return {"clear_status": True, "message": "Playback queue cleared."}

    # --- Premium Features ---
    def upgrade_to_premium(self) -> Dict[str, bool]:
        """
        Upgrade the current user's account to premium.
        Returns:
            Dict[str, bool]: {"upgrade_status": True} if successful, {"upgrade_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"upgrade_status": False, "message": "Not authenticated."}
        if self.users[self.username]["premium"]:
            return {"upgrade_status": False, "message": "User is already premium."}

        self.users[self.username]["premium"] = True
        # In a real system, you'd handle payment processing
        self.premium_subscriptions[self.username] = {"plan": "Premium Individual", "start_date": "2023-07-15", "end_date": "2024-07-15"}
        return {"upgrade_status": True, "message": "Account upgraded to premium."}

    def cancel_premium(self) -> Dict[str, bool]:
        """
        Cancel the current user's premium subscription.
        Returns:
            Dict[str, bool]: {"cancel_status": True} if successful, {"cancel_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"cancel_status": False, "message": "Not authenticated."}
        if not self.users[self.username]["premium"]:
            return {"cancel_status": False, "message": "User is not a premium subscriber."}

        self.users[self.username]["premium"] = False
        if self.username in self.premium_subscriptions:
            del self.premium_subscriptions[self.username]
        return {"cancel_status": True, "message": "Premium subscription cancelled."}

    def check_premium_status(self) -> Dict[str, bool]:
        """
        Check if the current user has a premium subscription.
        Returns:
            Dict[str, bool]: {"is_premium": True} if premium, {"is_premium": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"is_premium": False, "message": "Not authenticated."}

        return {"is_premium": self.users[self.username]["premium"], "message": "Premium status retrieved."}

    def add_payment_method(self, card_type: str, last_four_digits: str) -> Dict[str, bool]:
        """
        Add a new payment method, represented by its type and last four digits.
        This simulates a user providing minimal, safe information via voice.
        A real backend would require secure tokenization or redirection for full card details.
        Args:
            card_type (str): Type of the card (e.g., "Visa", "Mastercard", "Amex").
            last_four_digits (str): Last four digits of the card number.
        Returns:
            Dict[str, bool]: {"add_status": True} if successful, {"add_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"add_status": False, "message": "Not authenticated."}

        payment_card_id = self.id_counters["payment_card"]
        self.id_counters["payment_card"] += 1

        # In a real scenario, this would involve a secure payment gateway
        self.payment_cards[payment_card_id] = {
            "id": payment_card_id,
            "user_email": self.username,
            "card_type": card_type,
            "last_four_digits": last_four_digits,
            "is_default": False # Assume not default initially
        }
        return {"add_status": True, "message": f"Payment method ending in {last_four_digits} ({card_type}) added."}

    def remove_payment_method(self, payment_method_id: int) -> Dict[str, bool]:
        """
        Remove a stored payment method by its ID.
        Args:
            payment_method_id (int): The ID of the payment method to remove.
        Returns:
            Dict[str, bool]: {"remove_status": True} if successful, {"remove_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"remove_status": False, "message": "Not authenticated."}

        if payment_method_id not in self.payment_cards:
            return {"remove_status": False, "message": f"Payment method with ID {payment_method_id} not found."}

        if self.payment_cards[payment_method_id]["user_email"] != self.username:
            return {"remove_status": False, "message": "You do not have permission to remove this payment method."}

        del self.payment_cards[payment_method_id]
        return {"remove_status": True, "message": f"Payment method ID {payment_method_id} removed."}

    def show_payment_methods(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show the payment methods associated with the current user's account.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"payment_methods": [...]} List of payment method dictionaries.
        """
        if not self.authenticated or self.username not in self.users:
            return {"payment_methods": [], "message": "Not authenticated."}

        user_payment_methods = []
        for card_id, card_info in self.payment_cards.items():
            if card_info["user_email"] == self.username:
                user_payment_methods.append({
                    "id": card_info["id"],
                    "card_type": card_info["card_type"],
                    "last_four_digits": card_info["last_four_digits"],
                    "is_default": card_info["is_default"]
                })
        return {"payment_methods": user_payment_methods, "message": "Payment methods retrieved."}

    def set_default_payment_method(self, payment_method_id: int) -> Dict[str, bool]:
        """
        Set a specific payment method as the default for the current user.
        Args:
            payment_method_id (int): The ID of the payment method to set as default.
        Returns:
            Dict[str, bool]: {"set_default_status": True} if successful, {"set_default_status": False} otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"set_default_status": False, "message": "Not authenticated."}

        if payment_method_id not in self.payment_cards:
            return {"set_default_status": False, "message": f"Payment method with ID {payment_method_id} not found."}

        if self.payment_cards[payment_method_id]["user_email"] != self.username:
            return {"set_default_status": False, "message": "You do not have permission to set this as default."}

        # Clear any existing default for this user
        for card_id, card_info in self.payment_cards.items():
            if card_info["user_email"] == self.username and card_info["is_default"]:
                self.payment_cards[card_id]["is_default"] = False
                break

        self.payment_cards[payment_method_id]["is_default"] = True
        return {"set_default_status": True, "message": f"Payment method ID {payment_method_id} set as default."}

