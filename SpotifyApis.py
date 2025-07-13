from typing import Dict, List, Any
from copy import deepcopy

DEFAULT_STATE = {
    "username": "spotify_user",
    "password": "spotify123",
    "authenticated": False,
    "users": {},
    "songs": {},
    "albums": {},
    "playlists": {},
    "artists": {},
    "reviews": {},
    "payment_cards": {},
    "current_song": None,
    "song_queue": [],
    "volume": 50,
    "premium_subscriptions": {},
    "id_counters": {
        "song": 0,
        "album": 0,
        "playlist": 0,
        "artist": 0,
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
        self.premium_subscriptions: Dict[int, Dict[str, Any]]
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

    def signup(self, first_name: str, last_name: str, email: str, password: str) -> Dict[str, bool]:
        """
        Sign up a new user with first name, last name, email and password.

        Args:
            first_name (str): First name of the user.
            last_name (str): Last name of the user.
            email (str): Email of the user.
            password (str): Password of the user.

        Returns:
            signup_status (bool): True if signup successful, False otherwise.
        """
        if email in self.users:
            return {"signup_status": False}
        
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
        return {"signup_status": True}

    def login(self, email: str, password: str) -> Dict[str, bool]:
        """
        Log in a user with email and password.

        Args:
            email (str): Email of the user.
            password (str): Password of the user.

        Returns:
            login_status (bool): True if login successful, False otherwise.
        """
        if email in self.users and self.users[email]["password"] == password:
            self.authenticated = True
            self.username = email
            return {"login_status": True}
        return {"login_status": False}

    def logout(self) -> Dict[str, bool]:
        """
        Log out the current user.

        Returns:
            logout_status (bool): True if logout successful, False otherwise.
        """
        if not self.authenticated:
            return {"logout_status": False}
        
        self.authenticated = False
        return {"logout_status": True}

    def send_verification_code(self, email: str) -> Dict[str, bool]:
        """
        Send verification code to user's email.

        Args:
            email (str): Email of the user.

        Returns:
            send_status (bool): True if code sent successfully, False otherwise.
        """
        if email not in self.users:
            return {"send_status": False}
        
        # In a real implementation, we would send an email here
        return {"send_status": True}

    def verify_account(self, email: str, verification_code: str) -> Dict[str, bool]:
        """
        Verify user account with verification code.

        Args:
            email (str): Email of the user.
            verification_code (str): Verification code sent to user's email.

        Returns:
            verification_status (bool): True if verification successful, False otherwise.
        """
        if email not in self.users:
            return {"verification_status": False}
        
        # In a real implementation, we would verify the code here
        self.users[email]["verified"] = True
        return {"verification_status": True}

    def send_password_reset_code(self, email: str) -> Dict[str, bool]:
        """
        Send password reset code to user's email.

        Args:
            email (str): Email of the user.

        Returns:
            send_status (bool): True if code sent successfully, False otherwise.
        """
        if email not in self.users:
            return {"send_status": False}
        
        # In a real implementation, we would send an email here
        return {"send_status": True}

    def reset_password(self, email: str, password_reset_code: str, new_password: str) -> Dict[str, bool]:
        """
        Reset user password with reset code.

        Args:
            email (str): Email of the user.
            password_reset_code (str): Password reset code sent to user's email.
            new_password (str): New password to set.

        Returns:
            reset_status (bool): True if password reset successful, False otherwise.
        """
        if email not in self.users:
            return {"reset_status": False}
        
        # In a real implementation, we would verify the code here
        self.users[email]["password"] = new_password
        return {"reset_status": True}

    def show_profile(self, email: str) -> Dict[str, Any]:
        """
        Show user profile information.

        Args:
            email (str): Email of the user.

        Returns:
            profile (dict): Dictionary containing user profile information.
        """
        if email not in self.users:
            return {"profile": {}}
        
        user = self.users[email]
        return {
            "profile": {
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "verified": user["verified"],
                "premium": user["premium"]
            }
        }

    def show_account(self) -> Dict[str, Any]:
        """
        Show current user account information.

        Returns:
            account (dict): Dictionary containing user account information.
        """
        if not self.authenticated or self.username not in self.users:
            return {"account": {}}
        
        user = self.users[self.username]
        return {
            "account": {
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "verified": user["verified"],
                "premium": user["premium"]
            }
        }

    def update_account_name(self, first_name: str, last_name: str) -> Dict[str, bool]:
        """
        Update user's first and last name.

        Args:
            first_name (str): New first name.
            last_name (str): New last name.

        Returns:
            update_status (bool): True if update successful, False otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"update_status": False}
        
        self.users[self.username]["first_name"] = first_name
        self.users[self.username]["last_name"] = last_name
        return {"update_status": True}

    def delete_account(self) -> Dict[str, bool]:
        """
        Delete current user account.

        Returns:
            delete_status (bool): True if deletion successful, False otherwise.
        """
        if not self.authenticated or self.username not in self.users:
            return {"delete_status": False}
        
        del self.users[self.username]
        self.authenticated = False
        return {"delete_status": True}

    def show_genres(self) -> Dict[str, List[str]]:
        """
        Show available music genres.

        Returns:
            genres (list): List of available genres.
        """
        return {"genres": ["Pop", "Rock", "Hip-Hop", "Jazz", "Classical", "Electronic", "Country", "R&B"]}

    def search_songs(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for songs.

        Args:
            query (str): Search query.

        Returns:
            songs (list): List of song dictionaries matching the query.
        """
        matching_songs = []
        for song in self.songs.values():
            if query.lower() in song["title"].lower() or query.lower() in song["artist"].lower():
                matching_songs.append(song)
        return {"songs": matching_songs}

    def show_song(self, song_id: int) -> Dict[str, Any]:
        """
        Show details of a specific song.

        Args:
            song_id (int): ID of the song.

        Returns:
            song (dict): Dictionary containing song details.
        """
        if song_id not in self.songs:
            return {"song": {}}
        return {"song": self.songs[song_id]}

    def show_song_privates(self, song_id: int) -> Dict[str, Any]:
        """
        Show private user-specific information about a song.

        Args:
            song_id (int): ID of the song.

        Returns:
            privates (dict): Dictionary containing private song information.
        """
        if not self.authenticated or song_id not in self.songs:
            return {"privates": {}}
        
        user = self.users[self.username]
        return {
            "privates": {
                "liked": song_id in user["liked_songs"],
                "in_library": song_id in user["library_songs"],
                "downloaded": song_id in user["downloaded_songs"]
            }
        }

    def like_song(self, song_id: int) -> Dict[str, bool]:
        """
        Like a song.

        Args:
            song_id (int): ID of the song to like.

        Returns:
            like_status (bool): True if like successful, False otherwise.
        """
        if not self.authenticated or song_id not in self.songs:
            return {"like_status": False}
        
        if song_id not in self.users[self.username]["liked_songs"]:
            self.users[self.username]["liked_songs"].append(song_id)
        return {"like_status": True}

    def unlike_song(self, song_id: int) -> Dict[str, bool]:
        """
        Unlike a song.

        Args:
            song_id (int): ID of the song to unlike.

        Returns:
            unlike_status (bool): True if unlike successful, False otherwise.
        """
        if not self.authenticated or song_id not in self.songs:
            return {"unlike_status": False}
        
        if song_id in self.users[self.username]["liked_songs"]:
            self.users[self.username]["liked_songs"].remove(song_id)
        return {"unlike_status": True}

    def show_liked_songs(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show all liked songs.

        Returns:
            songs (list): List of liked song dictionaries.
        """
        if not self.authenticated:
            return {"songs": []}
        
        liked_songs = []
        for song_id in self.users[self.username]["liked_songs"]:
            if song_id in self.songs:
                liked_songs.append(self.songs[song_id])
        return {"songs": liked_songs}

    def search_albums(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for albums.

        Args:
            query (str): Search query.

        Returns:
            albums (list): List of album dictionaries matching the query.
        """
        matching_albums = []
        for album in self.albums.values():
            if query.lower() in album["title"].lower() or query.lower() in album["artist"].lower():
                matching_albums.append(album)
        return {"albums": matching_albums}

    def show_album(self, album_id: int) -> Dict[str, Any]:
        """
        Show details of a specific album.

        Args:
            album_id (int): ID of the album.

        Returns:
            album (dict): Dictionary containing album details.
        """
        if album_id not in self.albums:
            return {"album": {}}
        return {"album": self.albums[album_id]}

    def show_album_privates(self, album_id: int) -> Dict[str, Any]:
        """
        Show private user-specific information about an album.

        Args:
            album_id (int): ID of the album.

        Returns:
            privates (dict): Dictionary containing private album information.
        """
        if not self.authenticated or album_id not in self.albums:
            return {"privates": {}}
        
        user = self.users[self.username]
        return {
            "privates": {
                "liked": album_id in user["liked_albums"],
                "in_library": album_id in user["library_albums"]
            }
        }

    def like_album(self, album_id: int) -> Dict[str, bool]:
        """
        Like an album.

        Args:
            album_id (int): ID of the album to like.

        Returns:
            like_status (bool): True if like successful, False otherwise.
        """
        if not self.authenticated or album_id not in self.albums:
            return {"like_status": False}
        
        if album_id not in self.users[self.username]["liked_albums"]:
            self.users[self.username]["liked_albums"].append(album_id)
        return {"like_status": True}

    def unlike_album(self, album_id: int) -> Dict[str, bool]:
        """
        Unlike an album.

        Args:
            album_id (int): ID of the album to unlike.

        Returns:
            unlike_status (bool): True if unlike successful, False otherwise.
        """
        if not self.authenticated or album_id not in self.albums:
            return {"unlike_status": False}
        
        if album_id in self.users[self.username]["liked_albums"]:
            self.users[self.username]["liked_albums"].remove(album_id)
        return {"unlike_status": True}

    def show_liked_albums(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show all liked albums.

        Returns:
            albums (list): List of liked album dictionaries.
        """
        if not self.authenticated:
            return {"albums": []}
        
        liked_albums = []
        for album_id in self.users[self.username]["liked_albums"]:
            if album_id in self.albums:
                liked_albums.append(self.albums[album_id])
        return {"albums": liked_albums}

    def show_playlist_library(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show user's playlist library.

        Returns:
            playlists (list): List of playlist dictionaries.
        """
        if not self.authenticated:
            return {"playlists": []}
        
        user_playlists = []
        for playlist_id, playlist in self.playlists.items():
            if playlist["owner"] == self.username:
                user_playlists.append(playlist)
        return {"playlists": user_playlists}

    def search_playlists(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for playlists.

        Args:
            query (str): Search query.

        Returns:
            playlists (list): List of playlist dictionaries matching the query.
        """
        matching_playlists = []
        for playlist in self.playlists.values():
            if query.lower() in playlist["title"].lower():
                matching_playlists.append(playlist)
        return {"playlists": matching_playlists}

    def show_playlist(self, playlist_id: int) -> Dict[str, Any]:
        """
        Show details of a specific playlist.

        Args:
            playlist_id (int): ID of the playlist.

        Returns:
            playlist (dict): Dictionary containing playlist details.
        """
        if playlist_id not in self.playlists:
            return {"playlist": {}}
        return {"playlist": self.playlists[playlist_id]}

    def show_playlist_privates(self, playlist_id: int) -> Dict[str, Any]:
        """
        Show private user-specific information about a playlist.

        Args:
            playlist_id (int): ID of the playlist.

        Returns:
            privates (dict): Dictionary containing private playlist information.
        """
        if not self.authenticated or playlist_id not in self.playlists:
            return {"privates": {}}
        
        user = self.users[self.username]
        return {
            "privates": {
                "liked": playlist_id in user["liked_playlists"],
                "owner": self.playlists[playlist_id]["owner"] == self.username
            }
        }

    def create_playlist(self, title: str, is_public: bool) -> Dict[str, Any]:
        """
        Create a new playlist.

        Args:
            title (str): Title of the playlist.
            is_public (bool): Whether the playlist is public.

        Returns:
            playlist (dict): Dictionary containing new playlist information.
        """
        if not self.authenticated:
            return {"playlist": {}}
        
        playlist_id = self.id_counters["playlist"]
        self.id_counters["playlist"] += 1
        
        new_playlist = {
            "id": playlist_id,
            "title": title,
            "public": is_public,
            "owner": self.username,
            "songs": [],
            "created_at": "2023-01-01"  # In a real implementation, use datetime
        }
        self.playlists[playlist_id] = new_playlist
        return {"playlist": new_playlist}

    def update_playlist(self, playlist_id: int, title: str, is_public: bool) -> Dict[str, bool]:
        """
        Update a playlist.

        Args:
            playlist_id (int): ID of the playlist to update.
            title (str): New title for the playlist.
            is_public (bool): New visibility status.

        Returns:
            update_status (bool): True if update successful, False otherwise.
        """
        if not self.authenticated or playlist_id not in self.playlists:
            return {"update_status": False}
        
        if self.playlists[playlist_id]["owner"] != self.username:
            return {"update_status": False}
        
        self.playlists[playlist_id]["title"] = title
        self.playlists[playlist_id]["public"] = is_public
        return {"update_status": True}

    def delete_playlist(self, playlist_id: int) -> Dict[str, bool]:
        """
        Delete a playlist.

        Args:
            playlist_id (int): ID of the playlist to delete.

        Returns:
            delete_status (bool): True if deletion successful, False otherwise.
        """
        if not self.authenticated or playlist_id not in self.playlists:
            return {"delete_status": False}
        
        if self.playlists[playlist_id]["owner"] != self.username:
            return {"delete_status": False}
        
        del self.playlists[playlist_id]
        return {"delete_status": True}

    def like_playlist(self, playlist_id: int) -> Dict[str, bool]:
        """
        Like a playlist.

        Args:
            playlist_id (int): ID of the playlist to like.

        Returns:
            like_status (bool): True if like successful, False otherwise.
        """
        if not self.authenticated or playlist_id not in self.playlists:
            return {"like_status": False}
        
        if playlist_id not in self.users[self.username]["liked_playlists"]:
            self.users[self.username]["liked_playlists"].append(playlist_id)
        return {"like_status": True}

    def unlike_playlist(self, playlist_id: int) -> Dict[str, bool]:
        """
        Unlike a playlist.

        Args:
            playlist_id (int): ID of the playlist to unlike.

        Returns:
            unlike_status (bool): True if unlike successful, False otherwise.
        """
        if not self.authenticated or playlist_id not in self.playlists:
            return {"unlike_status": False}
        
        if playlist_id in self.users[self.username]["liked_playlists"]:
            self.users[self.username]["liked_playlists"].remove(playlist_id)
        return {"unlike_status": True}

    def show_liked_playlists(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show all liked playlists.

        Returns:
            playlists (list): List of liked playlist dictionaries.
        """
        if not self.authenticated:
            return {"playlists": []}
        
        liked_playlists = []
        for playlist_id in self.users[self.username]["liked_playlists"]:
            if playlist_id in self.playlists:
                liked_playlists.append(self.playlists[playlist_id])
        return {"playlists": liked_playlists}

    def search_artists(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for artists.

        Args:
            query (str): Search query.

        Returns:
            artists (list): List of artist dictionaries matching the query.
        """
        matching_artists = []
        for artist in self.artists.values():
            if query.lower() in artist["name"].lower():
                matching_artists.append(artist)
        return {"artists": matching_artists}

    def show_artist(self, artist_id: int) -> Dict[str, Any]:
        """
        Show details of a specific artist.

        Args:
            artist_id (int): ID of the artist.

        Returns:
            artist (dict): Dictionary containing artist details.
        """
        if artist_id not in self.artists:
            return {"artist": {}}
        return {"artist": self.artists[artist_id]}

    def show_artist_following(self, artist_id: int) -> Dict[str, bool]:
        """
        Check if following an artist.

        Args:
            artist_id (int): ID of the artist.

        Returns:
            following_status (bool): True if following, False otherwise.
        """
        if not self.authenticated or artist_id not in self.artists:
            return {"following_status": False}
        
        return {"following_status": artist_id in self.users[self.username]["following_artists"]}

    def show_song_library(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show user's song library.

        Returns:
            songs (list): List of song dictionaries in library.
        """
        if not self.authenticated:
            return {"songs": []}
        
        library_songs = []
        for song_id in self.users[self.username]["library_songs"]:
            if song_id in self.songs:
                library_songs.append(self.songs[song_id])
        return {"songs": library_songs}

    def add_song_to_library(self, song_id: int) -> Dict[str, bool]:
        """
        Add a song to user's library.

        Args:
            song_id (int): ID of the song to add.

        Returns:
            add_status (bool): True if add successful, False otherwise.
        """
        if not self.authenticated or song_id not in self.songs:
            return {"add_status": False}
        
        if song_id not in self.users[self.username]["library_songs"]:
            self.users[self.username]["library_songs"].append(song_id)
        return {"add_status": True}

    def remove_song_from_library(self, song_id: int) -> Dict[str, bool]:
        """
        Remove a song from user's library.

        Args:
            song_id (int): ID of the song to remove.

        Returns:
            remove_status (bool): True if remove successful, False otherwise.
        """
        if not self.authenticated or song_id not in self.songs:
            return {"remove_status": False}
        
        if song_id in self.users[self.username]["library_songs"]:
            self.users[self.username]["library_songs"].remove(song_id)
        return {"remove_status": True}

    def show_album_library(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show user's album library.

        Returns:
            albums (list): List of album dictionaries in library.
        """
        if not self.authenticated:
            return {"albums": []}
        
        library_albums = []
        for album_id in self.users[self.username]["library_albums"]:
            if album_id in self.albums:
                library_albums.append(self.albums[album_id])
        return {"albums": library_albums}

    def add_album_to_library(self, album_id: int) -> Dict[str, bool]:
        """
        Add an album to user's library.

        Args:
            album_id (int): ID of the album to add.

        Returns:
            add_status (bool): True if add successful, False otherwise.
        """
        if not self.authenticated or album_id not in self.albums:
            return {"add_status": False}
        
        if album_id not in self.users[self.username]["library_albums"]:
            self.users[self.username]["library_albums"].append(album_id)
        return {"add_status": True}

    def remove_album_from_library(self, album_id: int) -> Dict[str, bool]:
        """
        Remove an album from user's library.

        Args:
            album_id (int): ID of the album to remove.

        Returns:
            remove_status (bool): True if remove successful, False otherwise.
        """
        if not self.authenticated or album_id not in self.albums:
            return {"remove_status": False}
        
        if album_id in self.users[self.username]["library_albums"]:
            self.users[self.username]["library_albums"].remove(album_id)
        return {"remove_status": True}

    def add_song_to_playlist(self, playlist_id: int, song_id: int) -> Dict[str, bool]:
        """
        Add a song to a playlist.

        Args:
            playlist_id (int): ID of the playlist.
            song_id (int): ID of the song to add.

        Returns:
            add_status (bool): True if add successful, False otherwise.
        """
        if not self.authenticated or playlist_id not in self.playlists or song_id not in self.songs:
            return {"add_status": False}
        
        if self.playlists[playlist_id]["owner"] != self.username:
            return {"add_status": False}
        
        if song_id not in self.playlists[playlist_id]["songs"]:
            self.playlists[playlist_id]["songs"].append(song_id)
        return {"add_status": True}

    def remove_song_from_playlist(self, playlist_id: int, song_id: int) -> Dict[str, bool]:
        """
        Remove a song from a playlist.

        Args:
            playlist_id (int): ID of the playlist.
            song_id (int): ID of the song to remove.

        Returns:
            remove_status (bool): True if remove successful, False otherwise.
        """
        if not self.authenticated or playlist_id not in self.playlists or song_id not in self.songs:
            return {"remove_status": False}
        
        if self.playlists[playlist_id]["owner"] != self.username:
            return {"remove_status": False}
        
        if song_id in self.playlists[playlist_id]["songs"]:
            self.playlists[playlist_id]["songs"].remove(song_id)
        return {"remove_status": True}

    def show_downloaded_songs(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show user's downloaded songs.

        Returns:
            songs (list): List of downloaded song dictionaries.
        """
        if not self.authenticated:
            return {"songs": []}
        
        downloaded_songs = []
        for song_id in self.users[self.username]["downloaded_songs"]:
            if song_id in self.songs:
                downloaded_songs.append(self.songs[song_id])
        return {"songs": downloaded_songs}

    def download_song(self, song_id: int) -> Dict[str, bool]:
        """
        Download a song.

        Args:
            song_id (int): ID of the song to download.

        Returns:
            download_status (bool): True if download successful, False otherwise.
        """
        if not self.authenticated or song_id not in self.songs:
            return {"download_status": False}
        
        if song_id not in self.users[self.username]["downloaded_songs"]:
            self.users[self.username]["downloaded_songs"].append(song_id)
        return {"download_status": True}

    def remove_downloaded_song(self, song_id: int) -> Dict[str, bool]:
        """
        Remove a downloaded song.

        Args:
            song_id (int): ID of the song to remove.

        Returns:
            remove_status (bool): True if remove successful, False otherwise.
        """
        if not self.authenticated or song_id not in self.songs:
            return {"remove_status": False}
        
        if song_id in self.users[self.username]["downloaded_songs"]:
            self.users[self.username]["downloaded_songs"].remove(song_id)
        return {"remove_status": True}

    def show_following_artists(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show artists the user is following.

        Returns:
            artists (list): List of followed artist dictionaries.
        """
        if not self.authenticated:
            return {"artists": []}
        
        following_artists = []
        for artist_id in self.users[self.username]["following_artists"]:
            if artist_id in self.artists:
                following_artists.append(self.artists[artist_id])
        return {"artists": following_artists}

    def follow_artist(self, artist_id: int) -> Dict[str, bool]:
        """
        Follow an artist.

        Args:
            artist_id (int): ID of the artist to follow.

        Returns:
            follow_status (bool): True if follow successful, False otherwise.
        """
        if not self.authenticated or artist_id not in self.artists:
            return {"follow_status": False}
        
        if artist_id not in self.users[self.username]["following_artists"]:
            self.users[self.username]["following_artists"].append(artist_id)
        return {"follow_status": True}

    def unfollow_artist(self, artist_id: int) -> Dict[str, bool]:
        """
        Unfollow an artist.

        Args:
            artist_id (int): ID of the artist to unfollow.

        Returns:
            unfollow_status (bool): True if unfollow successful, False otherwise.
        """
        if not self.authenticated or artist_id not in self.artists:
            return {"unfollow_status": False}
        
        if artist_id in self.users[self.username]["following_artists"]:
            self.users[self.username]["following_artists"].remove(artist_id)
        return {"unfollow_status": True}

    def show_song_reviews(self, song_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show reviews for a song.

        Args:
            song_id (int): ID of the song.

        Returns:
            reviews (list): List of review dictionaries for the song.
        """
        song_reviews = []
        for review in self.reviews.values():
            if review["content_type"] == "song" and review["content_id"] == song_id:
                song_reviews.append(review)
        return {"reviews": song_reviews}

    def review_song(self, song_id: int, rating: int, title: str, text: str) -> Dict[str, bool]:
        """
        Review a song.

        Args:
            song_id (int): ID of the song to review.
            rating (int): Rating for the song (1-5).
            title (str): Title of the review.
            text (str): Text content of the review.

        Returns:
            review_status (bool): True if review successful, False otherwise.
        """
        if not self.authenticated or song_id not in self.songs or rating < 1 or rating > 5:
            return {"review_status": False}
        
        review_id = self.id_counters["review"]
        self.id_counters["review"] += 1
        
        self.reviews[review_id] = {
            "id": review_id,
            "content_type": "song",
            "content_id": song_id,
            "user": self.username,
            "rating": rating,
            "title": title,
            "text": text,
            "created_at": "2023-01-01"  # In a real implementation, use datetime
        }
        return {"review_status": True}

    def update_song_review(self, review_id: int, rating: int, title: str, text: str) -> Dict[str, bool]:
        """
        Update a song review.

        Args:
            review_id (int): ID of the review to update.
            rating (int): New rating for the song (1-5).
            title (str): New title for the review.
            text (str): New text content of the review.

        Returns:
            update_status (bool): True if update successful, False otherwise.
        """
        if not self.authenticated or review_id not in self.reviews:
            return {"update_status": False}
        
        if self.reviews[review_id]["user"] != self.username:
            return {"update_status": False}
        
        if rating < 1 or rating > 5:
            return {"update_status": False}
        
        self.reviews[review_id]["rating"] = rating
        self.reviews[review_id]["title"] = title
        self.reviews[review_id]["text"] = text
        return {"update_status": True}

    def delete_song_review(self, review_id: int) -> Dict[str, bool]:
        """
        Delete a song review.

        Args:
            review_id (int): ID of the review to delete.

        Returns:
            delete_status (bool): True if deletion successful, False otherwise.
        """
        if not self.authenticated or review_id not in self.reviews:
            return {"delete_status": False}
        
        if self.reviews[review_id]["user"] != self.username:
            return {"delete_status": False}
        
        del self.reviews[review_id]
        return {"delete_status": True}

    def show_song_review(self, review_id: int) -> Dict[str, Any]:
        """
        Show details of a specific song review.

        Args:
            review_id (int): ID of the review.

        Returns:
            review (dict): Dictionary containing review details.
        """
        if review_id not in self.reviews or self.reviews[review_id]["content_type"] != "song":
            return {"review": {}}
        return {"review": self.reviews[review_id]}

    def show_album_reviews(self, album_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show reviews for an album.

        Args:
            album_id (int): ID of the album.

        Returns:
            reviews (list): List of review dictionaries for the album.
        """
        album_reviews = []
        for review in self.reviews.values():
            if review["content_type"] == "album" and review["content_id"] == album_id:
                album_reviews.append(review)
        return {"reviews": album_reviews}

    def review_album(self, album_id: int, rating: int, title: str, text: str) -> Dict[str, bool]:
        """
        Review an album.

        Args:
            album_id (int): ID of the album to review.
            rating (int): Rating for the album (1-5).
            title (str): Title of the review.
            text (str): Text content of the review.

        Returns:
            review_status (bool): True if review successful, False otherwise.
        """
        if not self.authenticated or album_id not in self.albums or rating < 1 or rating > 5:
            return {"review_status": False}
        
        review_id = self.id_counters["review"]
        self.id_counters["review"] += 1
        
        self.reviews[review_id] = {
            "id": review_id,
            "content_type": "album",
            "content_id": album_id,
            "user": self.username,
            "rating": rating,
            "title": title,
            "text": text,
            "created_at": "2023-01-01"  # In a real implementation, use datetime
        }
        return {"review_status": True}

    def update_album_review(self, review_id: int, rating: int, title: str, text: str) -> Dict[str, bool]:
        """
        Update an album review.

        Args:
            review_id (int): ID of the review to update.
            rating (int): New rating for the album (1-5).
            title (str): New title for the review.
            text (str): New text content of the review.

        Returns:
            update_status (bool): True if update successful, False otherwise.
        """
        if not self.authenticated or review_id not in self.reviews:
            return {"update_status": False}
        
        if self.reviews[review_id]["user"] != self.username:
            return {"update_status": False}
        
        if rating < 1 or rating > 5:
            return {"update_status": False}
        
        self.reviews[review_id]["rating"] = rating
        self.reviews[review_id]["title"] = title
        self.reviews[review_id]["text"] = text
        return {"update_status": True}

    def delete_album_review(self, review_id: int) -> Dict[str, bool]:
        """
        Delete an album review.

        Args:
            review_id (int): ID of the review to delete.

        Returns:
            delete_status (bool): True if deletion successful, False otherwise.
        """
        if not self.authenticated or review_id not in self.reviews:
            return {"delete_status": False}
        
        if self.reviews[review_id]["user"] != self.username:
            return {"delete_status": False}
        
        del self.reviews[review_id]
        return {"delete_status": True}

    def show_album_review(self, review_id: int) -> Dict[str, Any]:
        """
        Show details of a specific album review.

        Args:
            review_id (int): ID of the review.

        Returns:
            review (dict): Dictionary containing review details.
        """
        if review_id not in self.reviews or self.reviews[review_id]["content_type"] != "album":
            return {"review": {}}
        return {"review": self.reviews[review_id]}

    def show_playlist_reviews(self, playlist_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show reviews for a playlist.

        Args:
            playlist_id (int): ID of the playlist.

        Returns:
            reviews (list): List of review dictionaries for the playlist.
        """
        playlist_reviews = []
        for review in self.reviews.values():
            if review["content_type"] == "playlist" and review["content_id"] == playlist_id:
                playlist_reviews.append(review)
        return {"reviews": playlist_reviews}

    def review_playlist(self, playlist_id: int, rating: int, title: str, text: str) -> Dict[str, bool]:
        """
        Review a playlist.

        Args:
            playlist_id (int): ID of the playlist to review.
            rating (int): Rating for the playlist (1-5).
            title (str): Title of the review.
            text (str): Text content of the review.

        Returns:
            review_status (bool): True if review successful, False otherwise.
        """
        if not self.authenticated or playlist_id not in self.playlists or rating < 1 or rating > 5:
            return {"review_status": False}
        
        review_id = self.id_counters["review"]
        self.id_counters["review"] += 1
        
        self.reviews[review_id] = {
            "id": review_id,
            "content_type": "playlist",
            "content_id": playlist_id,
            "user": self.username,
            "rating": rating,
            "title": title,
            "text": text,
            "created_at": "2023-01-01"  # In a real implementation, use datetime
        }
        return {"review_status": True}

    def update_playlist_review(self, review_id: int, rating: int, title: str, text: str) -> Dict[str, bool]:
        """
        Update a playlist review.

        Args:
            review_id (int): ID of the review to update.
            rating (int): New rating for the playlist (1-5).
            title (str): New title for the review.
            text (str): New text content of the review.

        Returns:
            update_status (bool): True if update successful, False otherwise.
        """
        if not self.authenticated or review_id not in self.reviews:
            return {"update_status": False}
        
        if self.reviews[review_id]["user"] != self.username:
            return {"update_status": False}
        
        if rating < 1 or rating > 5:
            return {"update_status": False}
        
        self.reviews[review_id]["rating"] = rating
        self.reviews[review_id]["title"] = title
        self.reviews[review_id]["text"] = text
        return {"update_status": True}

    def delete_playlist_review(self, review_id: int) -> Dict[str, bool]:
        """
        Delete a playlist review.

        Args:
            review_id (int): ID of the review to delete.

        Returns:
            delete_status (bool): True if deletion successful, False otherwise.
        """
        if not self.authenticated or review_id not in self.reviews:
            return {"delete_status": False}
        
        if self.reviews[review_id]["user"] != self.username:
            return {"delete_status": False}
        
        del self.reviews[review_id]
        return {"delete_status": True}

    def show_playlist_review(self, review_id: int) -> Dict[str, Any]:
        """
        Show details of a specific playlist review.

        Args:
            review_id (int): ID of the review.

        Returns:
            review (dict): Dictionary containing review details.
        """
        if review_id not in self.reviews or self.reviews[review_id]["content_type"] != "playlist":
            return {"review": {}}
        return {"review": self.reviews[review_id]}

    def show_payment_cards(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show user's payment cards.

        Returns:
            cards (list): List of payment card dictionaries.
        """
        if not self.authenticated:
            return {"cards": []}
        
        user_cards = []
        for card_id, card in self.payment_cards.items():
            if card["user"] == self.username:
                user_cards.append(card)
        return {"cards": user_cards}

    def show_payment_card(self, payment_card_id: int) -> Dict[str, Any]:
        """
        Show details of a specific payment card.

        Args:
            payment_card_id (int): ID of the payment card.

        Returns:
            card (dict): Dictionary containing payment card details.
        """
        if payment_card_id not in self.payment_cards or self.payment_cards[payment_card_id]["user"] != self.username:
            return {"card": {}}
        return {"card": self.payment_cards[payment_card_id]}

    def add_payment_card(self, card_name: str, owner_name: str, card_number: str, expiry_year: int, expiry_month: int, cvv_number: int) -> Dict[str, bool]:
        """
        Add a payment card.

        Args:
            card_name (str): Name of the card.
            owner_name (str): Name of the card owner.
            card_number (str): Card number.
            expiry_year (int): Expiry year.
            expiry_month (int): Expiry month.
            cvv_number (int): CVV number.

        Returns:
            add_status (bool): True if add successful, False otherwise.
        """
        if not self.authenticated:
            return {"add_status": False}
        
        card_id = self.id_counters["payment_card"]
        self.id_counters["payment_card"] += 1
        
        self.payment_cards[card_id] = {
            "id": card_id,
            "user": self.username,
            "card_name": card_name,
            "owner_name": owner_name,
            "card_number": card_number,
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
            "cvv_number": cvv_number
        }
        return {"add_status": True}

    def update_payment_card(self, payment_card_id: int, card_name: str) -> Dict[str, bool]:
        """
        Update a payment card.

        Args:
            payment_card_id (int): ID of the card to update.
            card_name (str): New name for the card.

        Returns:
            update_status (bool): True if update successful, False otherwise.
        """
        if not self.authenticated or payment_card_id not in self.payment_cards:
            return {"update_status": False}
        
        if self.payment_cards[payment_card_id]["user"] != self.username:
            return {"update_status": False}
        
        self.payment_cards[payment_card_id]["card_name"] = card_name
        return {"update_status": True}

    def delete_payment_card(self, payment_card_id: int) -> Dict[str, bool]:
        """
        Delete a payment card.

        Args:
            payment_card_id (int): ID of the card to delete.

        Returns:
            delete_status (bool): True if deletion successful, False otherwise.
        """
        if not self.authenticated or payment_card_id not in self.payment_cards:
            return {"delete_status": False}
        
        if self.payment_cards[payment_card_id]["user"] != self.username:
            return {"delete_status": False}
        
        del self.payment_cards[payment_card_id]
        return {"delete_status": True}

    def show_current_song(self) -> Dict[str, Any]:
        """
        Show currently playing song.

        Returns:
            song (dict): Dictionary containing current song details.
        """
        if not self.current_song:
            return {"song": {}}
        
        return {"song": self.current_song}

    def play_music(self, song_id: int) -> Dict[str, bool]:
        """
        Play a song.

        Args:
            song_id (int): ID of the song to play.

        Returns:
            play_status (bool): True if play successful, False otherwise.
        """
        if song_id not in self.songs:
            return {"play_status": False}
        
        self.current_song = self.songs[song_id]
        return {"play_status": True}

    def pause_music(self) -> Dict[str, bool]:
        """
        Pause currently playing music.

        Returns:
            pause_status (bool): True if pause successful, False otherwise.
        """
        if not self.current_song:
            return {"pause_status": False}
        
        # In a real implementation, we would track pause state
        return {"pause_status": True}

    def previous_song(self) -> Dict[str, bool]:
        """
        Play previous song in queue.

        Returns:
            previous_status (bool): True if successful, False otherwise.
        """
        if not self.song_queue:
            return {"previous_status": False}
        
        # In a real implementation, we would track queue position
        return {"previous_status": True}

    def next_song(self) -> Dict[str, bool]:
        """
        Play next song in queue.

        Returns:
            next_status (bool): True if successful, False otherwise.
        """
        if not self.song_queue:
            return {"next_status": False}
        
        # In a real implementation, we would track queue position
        return {"next_status": True}

    def move_song_in_queue(self, current_position: int, new_position: int) -> Dict[str, bool]:
        """
        Move song in queue to new position.

        Args:
            current_position (int): Current position in queue.
            new_position (int): New position in queue.

        Returns:
            move_status (bool): True if move successful, False otherwise.
        """
        if current_position < 0 or current_position >= len(self.song_queue) or new_position < 0 or new_position >= len(self.song_queue):
            return {"move_status": False}
        
        song = self.song_queue.pop(current_position)
        self.song_queue.insert(new_position, song)
        return {"move_status": True}

    def seek_song(self, seek_seconds: int) -> Dict[str, bool]:
        """
        Seek to position in current song.

        Args:
            seek_seconds (int): Number of seconds to seek.

        Returns:
            seek_status (bool): True if seek successful, False otherwise.
        """
        if not self.current_song:
            return {"seek_status": False}
        
        # In a real implementation, we would track playback position
        return {"seek_status": True}

    def loop_song(self, loop: bool) -> Dict[str, bool]:
        """
        Set loop mode for current song.

        Args:
            loop (bool): Whether to loop the song.

        Returns:
            loop_status (bool): True if set successful, False otherwise.
        """
        if not self.current_song:
            return {"loop_status": False}
        
        # In a real implementation, we would track loop state
        return {"loop_status": True}

    def shuffle_song_queue(self) -> Dict[str, bool]:
        """
        Shuffle the song queue.

        Returns:
            shuffle_status (bool): True if shuffle successful, False otherwise.
        """
        if not self.song_queue:
            return {"shuffle_status": False}
        
        # In a real implementation, we would shuffle the queue
        return {"shuffle_status": True}

    def show_song_queue(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show current song queue.

        Returns:
            queue (list): List of song dictionaries in queue.
        """
        return {"queue": self.song_queue}

    def add_to_queue(self, song_id: int) -> Dict[str, bool]:
        """
        Add a song to the queue.

        Args:
            song_id (int): ID of the song to add.

        Returns:
            add_status (bool): True if add successful, False otherwise.
        """
        if song_id not in self.songs:
            return {"add_status": False}
        
        self.song_queue.append(self.songs[song_id])
        return {"add_status": True}

    def remove_song_from_queue(self, position: int) -> Dict[str, bool]:
        """
        Remove a song from the queue.

        Args:
            position (int): Position in queue to remove.

        Returns:
            remove_status (bool): True if remove successful, False otherwise.
        """
        if position < 0 or position >= len(self.song_queue):
            return {"remove_status": False}
        
        self.song_queue.pop(position)
        return {"remove_status": True}

    def clear_song_queue(self) -> Dict[str, bool]:
        """
        Clear the song queue.

        Returns:
            clear_status (bool): True if clear successful, False otherwise.
        """
        self.song_queue = []
        return {"clear_status": True}

    def show_volume(self) -> Dict[str, int]:
        """
        Show current volume level.

        Returns:
            volume (int): Current volume level (0-100).
        """
        return {"volume": self.volume}

    def set_volume(self, volume: int) -> Dict[str, bool]:
        """
        Set volume level.

        Args:
            volume (int): Volume level to set (0-100).

        Returns:
            set_status (bool): True if set successful, False otherwise.
        """
        if volume < 0 or volume > 100:
            return {"set_status": False}
        
        self.volume = volume
        return {"set_status": True}

    def show_recommendations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show song recommendations.

        Returns:
            recommendations (list): List of recommended song dictionaries.
        """
        # In a real implementation, we would have a recommendation algorithm
        return {"recommendations": []}

    def show_premium_plans(self) -> Dict[str, Any]:
        """
        Show available premium plans.

        Returns:
            plans (dict): Dictionary containing premium plan options.
        """
        return {
            "plans": {
                "individual": {
                    "price": 9.99,
                    "features": ["Ad-free music", "Download songs", "High quality audio"]
                },
                "family": {
                    "price": 14.99,
                    "features": ["Up to 6 accounts", "Ad-free music", "Download songs"]
                },
                "student": {
                    "price": 4.99,
                    "features": ["Ad-free music", "Download songs", "Student discount"]
                }
            }
        }

    def subscribe_premium(self, payment_card_id: int, duration: str) -> Dict[str, bool]:
        """
        Subscribe to premium service.

        Args:
            payment_card_id (int): ID of payment card to use.
            duration (str): Duration of subscription ('monthly' or 'yearly').

        Returns:
            subscribe_status (bool): True if subscription successful, False otherwise.
        """
        if not self.authenticated or payment_card_id not in self.payment_cards:
            return {"subscribe_status": False}
        
        if duration not in ["monthly", "yearly"]:
            return {"subscribe_status": False}
        
        subscription_id = len(self.premium_subscriptions) + 1
        self.premium_subscriptions[subscription_id] = {
            "user": self.username,
            "payment_card_id": payment_card_id,
            "duration": duration,
            "start_date": "2023-01-01",  # In a real implementation, use datetime
            "end_date": "2024-01-01" if duration == "yearly" else "2023-02-01"
        }
        self.users[self.username]["premium"] = True
        return {"subscribe_status": True}

    def show_premium_subscriptions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show user's premium subscriptions.

        Returns:
            subscriptions (list): List of subscription dictionaries.
        """
        if not self.authenticated:
            return {"subscriptions": []}
        
        user_subscriptions = []
        for sub in self.premium_subscriptions.values():
            if sub["user"] == self.username:
                user_subscriptions.append(sub)
        return {"subscriptions": user_subscriptions}

    def download_premium_subscription_receipt(self, premium_subscription_id: int) -> Dict[str, bool]:
        """
        Download premium subscription receipt.

        Args:
            premium_subscription_id (int): ID of the subscription.

        Returns:
            download_status (bool): True if download successful, False otherwise.
        """
        if not self.authenticated or premium_subscription_id not in self.premium_subscriptions:
            return {"download_status": False}
        
        if self.premium_subscriptions[premium_subscription_id]["user"] != self.username:
            return {"download_status": False}
        
        # In a real implementation, we would generate and return a receipt
        return {"download_status": True}