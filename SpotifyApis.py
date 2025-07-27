from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from copy import deepcopy

DEFAULT_STATE = {
    "username": "samantha.davis@melodify.com",
    "users": {
        "samantha.davis@melodify.com": {
            "first_name": "Samantha",
            "last_name": "Davis",
            "email": "samantha.davis@melodify.com",
            "verified": True,
            "liked_songs": [101, 103, 106],
            "liked_albums": [201, 204],
            "liked_playlists": [301, 303],
            "following_artists": [401, 404],
            "library_songs": [101, 102, 103, 106, 107],
            "library_albums": [201, 204, 205],
            "downloaded_songs": [101, 106],
            "premium": True
        },
        "liam.wilson@melodify.com": {
            "first_name": "Liam",
            "last_name": "Wilson",
            "email": "liam.wilson@melodify.com",
            "verified": True,
            "liked_songs": [102, 104, 105],
            "liked_albums": [202],
            "liked_playlists": [],
            "following_artists": [402, 403],
            "library_songs": [102, 104, 105, 108],
            "library_albums": [202, 206],
            "downloaded_songs": [],
            "premium": False
        },
        "olivia.taylor@melodify.com": {
            "first_name": "Olivia",
            "last_name": "Taylor",
            "email": "olivia.taylor@melodify.com",
            "verified": True,
            "liked_songs": [103, 108, 109],
            "liked_albums": [203, 205],
            "liked_playlists": [302, 304],
            "following_artists": [401, 405],
            "library_songs": [103, 107, 108, 109],
            "library_albums": [203, 205],
            "downloaded_songs": [103, 108],
            "premium": True
        },
        "noah.brown@melodify.com": {
            "first_name": "Noah",
            "last_name": "Brown",
            "email": "noah.brown@melodify.com",
            "verified": False,
            "liked_songs": [107],
            "liked_albums": [],
            "liked_playlists": [],
            "following_artists": [406],
            "library_songs": [106, 107],
            "library_albums": [],
            "downloaded_songs": [],
            "premium": False
        },
        "emma.jones@melodify.com": {
            "first_name": "Emma",
            "last_name": "Jones",
            "email": "emma.jones@melodify.com",
            "verified": True,
            "liked_songs": [101, 104, 109],
            "liked_albums": [201, 206],
            "liked_playlists": [305],
            "following_artists": [401, 403, 405],
            "library_songs": [101, 104, 109, 110],
            "library_albums": [201, 206],
            "downloaded_songs": [104],
            "premium": True
        }
    },
    "songs": {
        101: {"id": 101, "title": "Shape of You", "artist": "Ed Sheeran", "album": "Divide", "duration_ms": 233945, "genre": "Pop"},
        102: {"id": 102, "title": "Bohemian Rhapsody", "artist": "Queen", "album": "A Night at the Opera", "duration_ms": 354000, "genre": "Rock"},
        103: {"id": 103, "title": "Blinding Lights", "artist": "The Weeknd", "album": "After Hours", "duration_ms": 202000, "genre": "Pop"},
        104: {"id": 104, "title": "Watermelon Sugar", "artist": "Harry Styles", "album": "Fine Line", "duration_ms": 174000, "genre": "Pop"},
        105: {"id": 105, "title": "Old Town Road", "artist": "Lil Nas X", "album": "7", "duration_ms": 113000, "genre": "Country Rap"},
        106: {"id": 106, "title": "Good 4 U", "artist": "Olivia Rodrigo", "album": "SOUR", "duration_ms": 175000, "genre": "Pop Punk"},
        107: {"id": 107, "title": "Levitating", "artist": "Dua Lipa", "album": "Future Nostalgia", "duration_ms": 203000, "genre": "Pop"},
        108: {"id": 108, "title": "Save Your Tears", "artist": "The Weeknd", "album": "After Hours", "duration_ms": 215000, "genre": "Pop"},
        109: {"id": 109, "title": "Drivers License", "artist": "Olivia Rodrigo", "album": "SOUR", "duration_ms": 242000, "genre": "Pop"},
        110: {"id": 110, "title": "Happier Than Ever", "artist": "Billie Eilish", "album": "Happier Than Ever", "duration_ms": 268000, "genre": "Pop"}
    },
    "albums": {
        201: {"id": 201, "title": "Divide", "artist": "Ed Sheeran", "release_year": 2017, "genre": "Pop", "songs": [101]},
        202: {"id": 202, "title": "A Night at the Opera", "artist": "Queen", "release_year": 1975, "genre": "Rock", "songs": [102]},
        203: {"id": 203, "title": "After Hours", "artist": "The Weeknd", "release_year": 2020, "genre": "R&B", "songs": [103, 108]},
        204: {"id": 204, "title": "SOUR", "artist": "Olivia Rodrigo", "release_year": 2021, "genre": "Pop", "songs": [106, 109]},
        205: {"id": 205, "title": "Future Nostalgia", "artist": "Dua Lipa", "release_year": 2020, "genre": "Pop", "songs": [107]},
        206: {"id": 206, "title": "Happier Than Ever", "artist": "Billie Eilish", "release_year": 2021, "genre": "Pop", "songs": [110]}
    },
    "playlists": {
        301: {"id": 301, "title": "My Chill Pop Mix", "public": True, "owner": "samantha.davis@melodify.com", "songs": [101, 103, 104, 107], "created_at": "2023-01-15"},
        302: {"id": 302, "title": "Evening Drive", "public": False, "owner": "olivia.taylor@melodify.com", "songs": [103, 108, 109], "created_at": "2023-02-01"},
        303: {"id": 303, "title": "Workout Hits", "public": True, "owner": "samantha.davis@melodify.com", "songs": [106, 107], "created_at": "2023-03-10"},
        304: {"id": 304, "title": "Discover Weekly", "public": False, "owner": "olivia.taylor@melodify.com", "songs": [105, 110], "created_at": "2023-04-05"},
        305: {"id": 305, "title": "Feel Good Vibes", "public": True, "owner": "emma.jones@melodify.com", "songs": [101, 104, 106], "created_at": "2023-05-20"}
    },
    "artists": {
        401: {"id": 401, "name": "Ed Sheeran", "genre": "Pop", "followers": 15000000},
        402: {"id": 402, "name": "Queen", "genre": "Rock", "followers": 20000000},
        403: {"id": 403, "name": "The Weeknd", "genre": "R&B", "followers": 18000000},
        404: {"id": 404, "name": "Olivia Rodrigo", "genre": "Pop", "followers": 12000000},
        405: {"id": 405, "name": "Dua Lipa", "genre": "Pop", "followers": 10000000},
        406: {"id": 406, "name": "Billie Eilish", "genre": "Pop", "followers": 22000000}
    },
    "reviews": {},
    "payment_cards": {},
    "current_song": None,
    "song_queue": [],
    "volume": 75,
    "premium_subscriptions": {
        "samantha.davis@melodify.com": {"plan": "Premium Individual", "start_date": "2023-01-01", "end_date": "2024-01-01"},
        "olivia.taylor@melodify.com": {"plan": "Premium Family", "start_date": "2024-03-01", "end_date": "2025-03-01"},
        "emma.jones@melodify.com": {"plan": "Premium Individual", "start_date": "2023-08-15", "end_date": "2024-08-15"}
    },
    "id_counters": {
        "song": 111,
        "album": 207,
        "playlist": 306,
        "artist": 407,
        "review": 0,
        "payment_card": 0,
    }
}

class SpotifyApis:
    def __init__(self):
        self.username: str
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
        self.premium_subscriptions: Dict[str, Dict[str, Any]] 
        self.id_counters: Dict[str, int]
        self.is_playing: bool = False 
        self._load_default_state()

    def _load_default_state(self) -> None:
        """Load the default state into the SpotifyAPI instance."""
        default_state_copy = deepcopy(DEFAULT_STATE)
        self.username = default_state_copy["username"]
        # self.password = default_state_copy["password"] # Removed
        # self.authenticated = default_state_copy["authenticated"] # Removed
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
        self.is_playing = False # Ensure initial state is not playing

    def show_profile(self) -> Dict[str, Any]:
        """
        Show the current user's profile information.
        Returns:
            Dict[str, Any]: Dictionary containing user profile information.
        """
        # No authentication check needed, user is assumed logged in
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
            Dict[str, bool]: {"update_status": True} if update successful.
        """
        # No authentication check needed
        self.users[self.username]["first_name"] = first_name
        self.users[self.username]["last_name"] = last_name
        return {"update_status": True, "message": "Account name updated successfully."}

    def delete_account(self) -> Dict[str, bool]:
        """
        Delete the current user account.
        Returns:
            Dict[str, bool]: {"delete_status": True} if deletion successful, {"delete_status": False} otherwise.
        """
        # In a real system, you might set a placeholder user or re-initialize.
        # For this context, we'll revert to the default assumed user.
        if self.username in self.users:
            del self.users[self.username]
        self._load_default_state() # Revert to default user
        return {"delete_status": True, "message": "Account deleted successfully. Default user re-established."}

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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
            Dict[str, Any]: {"playlist": {...}} Dictionary containing new playlist information.
        """
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
        liked_playlists = []
        for playlist_id in self.users[self.username]["liked_playlists"]:
            if playlist_id in self.playlists:
                liked_playlists.append(self.playlists[playlist_id])
        return {"playlists": liked_playlists, "message": "Liked playlists retrieved."}

    def add_song_to_playlist(self, playlist_id: int, song_id: int) -> Dict[str, bool]:
        """
        Add a song to a playlist owned by the current user.
        Args:
            playlist_id (int): ID of the playlist.
            song_id (int): ID of the song to add.
        Returns:
            Dict[str, bool]: {"add_status": True} if add successful, {"add_status": False} otherwise.
        """
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed, but premium check remains
        if not self.users[self.username]["premium"]:
            return {"download_status": False, "message": "Premium subscription required to download songs."}
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
        # No authentication check needed
        if song_id not in self.songs:
            return {"remove_status": False, "message": f"Song with ID {song_id} not found."}

        if song_id in self.users[self.username]["downloaded_songs"]:
            self.users[self.username]["downloaded_songs"].remove(song_id)
            return {"remove_status": True, "message": f"Song ID {song_id} removed from downloads."}
        return {"remove_status": False, "message": f"Song ID {song_id} is not downloaded."}

    # --- Playback Control ---
    def play_song(self, song_id: int) -> Dict[str, Any]:
        """
        Start playing a song.
        Args:
            song_id (int): ID of the song to play.
        Returns:
            Dict[str, Any]: {"playback_status": "playing", "song": {...}} if successful, {"playback_status": "error"} otherwise.
        """
        # No authentication check needed
        if song_id not in self.songs:
            return {"playback_status": "error", "message": f"Song with ID {song_id} not found."}
        
        self.current_song = self.songs[song_id]
        self.is_playing = True
        return {"playback_status": "playing", "song": self.current_song, "message": f"Now playing: {self.current_song['title']}."}

    def pause_song(self) -> Dict[str, str]:
        """
        Pause the currently playing song.
        Returns:
            Dict[str, str]: {"playback_status": "paused"} if successful, {"playback_status": "error"} otherwise.
        """
        # No authentication check needed
        if self.current_song and self.is_playing:
            self.is_playing = False
            return {"playback_status": "paused", "message": f"Song paused: {self.current_song['title']}."}
        return {"playback_status": "error", "message": "No song is currently playing to pause."}

    def resume_song(self) -> Dict[str, str]:
        """
        Resume the currently paused song.
        Returns:
            Dict[str, str]: {"playback_status": "playing"} if successful, {"playback_status": "error"} otherwise.
        """
        # No authentication check needed
        if self.current_song and not self.is_playing:
            self.is_playing = True
            return {"playback_status": "playing", "message": f"Song resumed: {self.current_song['title']}."}
        # Only resume from queue if no song is currently paused
        elif not self.current_song and self.song_queue: 
            next_song_id = self.song_queue.pop(0)
            self.current_song = self.songs.get(next_song_id)
            if self.current_song:
                self.is_playing = True
                return {"playback_status": "playing", "message": f"Resuming playback with: {self.current_song['title']}."}
            else:
                return {"playback_status": "error", "message": "Next song in queue not found for resume."}
        
        return {"playback_status": "error", "message": "No song to resume."}

    def skip_song(self) -> Dict[str, bool]:
        """
        Skip to the next song in the queue.
        Returns:
            Dict[str, bool]: {"skip_status": True} if skipped, {"skip_status": False} otherwise.
        """
        # No authentication check needed
        if not self.song_queue:
            return {"skip_status": False, "message": "No more songs in the queue to skip to."}

        self.current_song = self.songs.get(self.song_queue.pop(0)) # Get song object from ID
        if self.current_song:
            self.is_playing = True # Ensure it continues playing after skip
            return {"skip_status": True, "message": f"Skipped to next song: {self.current_song['title']}."}
        else:
            return {"skip_status": False, "message": "Next song in queue not found."}


    def previous_song(self) -> Dict[str, bool]:
        """
        Go back to the previous song (dummy implementation - will just stop current).
        Returns:
            Dict[str, bool]: {"previous_status": True} if successful, {"previous_status": False} otherwise.
        """
        # No authentication check needed
        if not self.current_song:
            return {"previous_status": False, "message": "No song currently playing or previous song available."}

        # In a real player, you'd manage a history stack. For dummy, just "stop"
        self.current_song = None
        self.is_playing = False # Stop playing
        return {"previous_status": True, "message": "Went back to previous song (simulated stop)."}

    def set_volume(self, volume_level: int) -> Dict[str, bool]:
        """
        Set the playback volume.
        Args:
            volume_level (int): Volume level from 0 to 100.
        Returns:
            Dict[str, bool]: {"set_status": True} if set, {"set_status": False} otherwise.
        """
        # No authentication check needed
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
        # No authentication check needed
        return {"volume": self.volume, "message": f"Current volume is {self.volume}."}

    def show_current_song(self) -> Dict[str, Any]:
        """
        Show details of the currently playing song.
        Returns:
            Dict[str, Any]: {"current_song": {...}} Dictionary containing song details, or empty if nothing is playing.
        """
        # No authentication check needed
        if not self.current_song or not self.is_playing: # Check is_playing as well
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
        # No authentication check needed
        if song_id not in self.songs:
            return {"add_status": False, "message": f"Song with ID {song_id} not found."}

        self.song_queue.append(song_id) # Store ID, not full song object
        return {"add_status": True, "message": f"Song '{self.songs[song_id]['title']}' added to queue."}

    def show_song_queue(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Show the current playback queue.
        Returns:
            Dict[str, List[Dict[str, Any]]]: {"queue": [...]} List of song dictionaries in the queue.
        """
        # No authentication check needed
        queue_songs_details = [self.songs[song_id] for song_id in self.song_queue if song_id in self.songs]
        return {"queue": queue_songs_details, "message": "Playback queue retrieved."}

    def clear_song_queue(self) -> Dict[str, bool]:
        """
        Clear the current playback queue.
        Returns:
            Dict[str, bool]: {"clear_status": True}
        """
        # No authentication check needed
        self.song_queue = []
        return {"clear_status": True, "message": "Playback queue cleared."}

    # --- Premium Features ---
    def upgrade_to_premium(self) -> Dict[str, bool]:
        """
        Upgrade the current user's account to premium.
        Returns:
            Dict[str, bool]: {"upgrade_status": True} if successful, {"upgrade_status": False} otherwise.
        """
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
        # No authentication check needed
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
