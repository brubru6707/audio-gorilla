import datetime
import copy
import uuid
from typing import Dict, Any, Optional, Literal
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("SpotifyApis")
class SpotifyApis:
    """
    A dummy API class for simulating Spotify operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the SpotifyApis instance, setting up the in-memory
        data stores and loading the default scenario.
        """
        self._api_description = "This tool belongs to the Spotify API, which provides core functionality for managing music, playlists, and user profiles."
        self.users: Dict[str, Any] = {}
        self.payment_cards: Dict[str, Any] = {}
        self.songs: Dict[str, Any] = {}
        self.albums: Dict[str, Any] = {}
        self.playlists: Dict[str, Any] = {}
        self.artists: Dict[str, Any] = {}
        self.username: Optional[str] = None

        self._load_scenario(DEFAULT_STATE)
        if DEFAULT_STATE.get("username"):
            self.username = DEFAULT_STATE["username"]

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain "users", "payment_cards", "songs", etc.
        """
        scenario_copy = copy.deepcopy(scenario)
        self.users = scenario_copy.get("users", {})
        self.payment_cards = scenario_copy.get("payment_cards", {})
        self.songs = scenario_copy.get("songs", {})
        self.albums = scenario_copy.get("albums", {})
        self.playlists = scenario_copy.get("playlists", {})
        self.artists = scenario_copy.get("artists", {})
        self.username = scenario_copy.get("username")
        print("SpotifyApis: Loaded scenario with UUIDs for all entities.")

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for dummy entities.
        """
        return str(uuid.uuid4())

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """
        Helper to get user_id (UUID) from email (string).

        Args:
            email (str): User's email address.
        Returns:
            Optional[str]: User ID if found, None otherwise.
        """
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """
        Helper to get user email (string) from user_id (UUID).

        Args:
            user_id (str): User's ID.
        Returns:
            Optional[str]: User email if found, None otherwise.
        """
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _get_current_user_data(self) -> Optional[Dict]:
        """
        Helper to get the data of the currently logged-in user (identified by self.username UUID).

        Returns:
            Optional[Dict]: Current user's data if authenticated, None otherwise.
        """
        if not self.username:
            # Auto-login the first user if no user is authenticated
            if self.users:
                self.username = next(iter(self.users.keys()))
        
        return self.users.get(self.username) if self.username else None

    def _get_user_payment_cards(self, user_id: str) -> Dict[str, Any]:
        """
        Helper to get a user's payment cards, keyed by UUID.

        Args:
            user_id (str): User's ID.
        Returns:
            Dict[str, Any]: Dictionary of payment cards belonging to the user.
        """
        cards = {}
        for card_id, card_data in self.payment_cards.items():
            if card_data.get("user_id") == user_id:
                cards[card_id] = card_data
        return cards

    def set_current_user(self, user_email: str) -> Dict[str, bool]:
        """
        Sets the current authenticated user for the API session.

        Args:
            user_email (str): The email address of the user to set as current.
        Returns:
            Dict[str, bool]: A dictionary with 'status' indicating success or failure.
        """
        user_id = self._get_user_id_by_email(user_email)
        if user_id:
            self.username = user_id
            return {"status": True, "message": f"User set to {user_email} (ID: {user_id})."}
        return {"status": False, "message": f"User with email {user_email} not found."}

    def show_account(self) -> Dict[str, Any]:
        """
        Shows the account information for the current user.

        Returns:
            Dict[str, Any]: Dictionary containing user profile information or error message.
        """
        user_data = self._get_current_user_data()
        if user_data:
            profile = {k: v for k, v in user_data.items() if k not in ["id"]}
            profile["email"] = self._get_user_email_by_id(self.username)
            return {"status": "success", "profile": profile}
        return {"status": "error", "message": "User not authenticated or not found."}

    def add_payment_method(
        self,
        card_name: str,
        card_number: str,
        expiry_year: int,
        expiry_month: int,
        cvv_number: str,
        is_default: bool = False,
    ) -> Dict[str, Any]:
        """
        Adds a new payment method for the current user.

        Args:
            card_name (str): Name on the card.
            card_number (str): Card number.
            expiry_year (int): Expiration year.
            expiry_month (int): Expiration month.
            cvv_number (str): CVV security code.
            is_default (bool): Whether to set as default payment method.
        Returns:
            Dict[str, Any]: Dictionary containing new payment method details or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}

        new_card_id = self._generate_unique_id()
        user_id = user_data["id"]

        if is_default:
            for card_id, card_info in self.payment_cards.items():
                if card_info.get("user_id") == user_id and card_info.get("is_default"):
                    self.payment_cards[card_id]["is_default"] = False
                    break

        new_card = {
            "id": new_card_id,
            "card_name": card_name,
            "user_id": user_id,
            "card_number": card_number,
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
            "cvv_number": cvv_number,
            "is_default": is_default,
        }
        self.payment_cards[new_card_id] = new_card
        return {"status": "success", "payment_method": copy.deepcopy(new_card)}

    def show_payment_methods(self) -> Dict[str, Any]:
        """
        Shows all payment methods associated with the current user.

        Returns:
            Dict[str, Any]: Dictionary containing list of payment methods or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}

        user_id = user_data["id"]
        payment_methods = [
            copy.deepcopy(card_info)
            for card_id, card_info in self.payment_cards.items()
            if card_info.get("user_id") == user_id
        ]
        return {"status": "success", "payment_methods": payment_methods}

    def set_default_payment_method(self, payment_method_id: str) -> Dict[str, bool]:
        """
        Set a specific payment method as the default for the current user.

        Args:
            payment_method_id (str): The ID (UUID) of the payment method to set as default.
        Returns:
            Dict[str, bool]: {"set_default_status": True} if successful, {"set_default_status": False} otherwise.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"set_default_status": False, "message": "User not authenticated."}

        if payment_method_id not in self.payment_cards:
            return {"set_default_status": False, "message": f"Payment method with ID {payment_method_id} not found."}

        if self.payment_cards[payment_method_id]["user_id"] != user_data["id"]:
            return {"set_default_status": False, "message": "You do not have permission to set this as default."}

        for card_id, card_info in self.payment_cards.items():
            if card_info["user_id"] == user_data["id"] and card_info["is_default"]:
                self.payment_cards[card_id]["is_default"] = False
                break

        self.payment_cards[payment_method_id]["is_default"] = True
        return {"set_default_status": True, "message": f"Payment method {payment_method_id} set as default."}

    def get_user_liked_songs(self) -> Dict[str, Any]:
        """
        Retrieves the list of songs liked by the current user.

        Returns:
            Dict[str, Any]: Dictionary containing list of liked songs or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        liked_songs_ids = user_data.get("liked_songs", [])
        liked_songs_details = [copy.deepcopy(self.songs[s_id]) for s_id in liked_songs_ids if s_id in self.songs]
        return {"status": "success", "liked_songs": liked_songs_details}

    def like_song(self, song_id: str) -> Dict[str, bool]:
        """
        Adds a song to the current user's liked songs.

        Args:
            song_id (str): ID of the song to like.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song with ID {song_id} not found."}

        if song_id not in user_data.get("liked_songs", []):
            user_data.setdefault("liked_songs", []).append(song_id)
            return {"status": True, "message": f"Song {song_id} liked."}
        return {"status": False, "message": f"Song {song_id} already liked."}

    def unlike_song(self, song_id: str) -> Dict[str, bool]:
        """
        Removes a song from the current user's liked songs.

        Args:
            song_id (str): ID of the song to unlike.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song with ID {song_id} not found."}

        if song_id in user_data.get("liked_songs", []):
            user_data["liked_songs"].remove(song_id)
            return {"status": True, "message": f"Song {song_id} unliked."}
        return {"status": False, "message": f"Song {song_id} not in liked songs."}

    def get_user_library_songs(self) -> Dict[str, Any]:
        """
        Retrieves the list of songs in the current user's library.

        Returns:
            Dict[str, Any]: Dictionary containing list of library songs or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        library_songs_ids = user_data.get("library_songs", [])
        library_songs_details = [copy.deepcopy(self.songs[s_id]) for s_id in library_songs_ids if s_id in self.songs]
        return {"status": "success", "library_songs": library_songs_details}

    def add_song_to_library(self, song_id: str) -> Dict[str, bool]:
        """
        Adds a song to the current user's library.

        Args:
            song_id (str): ID of the song to add.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song with ID {song_id} not found."}

        if song_id not in user_data.get("library_songs", []):
            user_data.setdefault("library_songs", []).append(song_id)
            return {"status": True, "message": f"Song {song_id} added to library."}
        return {"status": False, "message": f"Song {song_id} already in library."}

    def remove_song_from_library(self, song_id: str) -> Dict[str, bool]:
        """
        Removes a song from the current user's library.

        Args:
            song_id (str): ID of the song to remove.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song with ID {song_id} not found."}

        if song_id in user_data.get("library_songs", []):
            user_data["library_songs"].remove(song_id)
            return {"status": True, "message": f"Song {song_id} removed from library."}
        return {"status": False, "message": f"Song {song_id} not in library."}

    def get_user_downloaded_songs(self) -> Dict[str, Any]:
        """
        Retrieves the list of songs downloaded by the current user.

        Returns:
            Dict[str, Any]: Dictionary containing list of downloaded songs or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        downloaded_songs_ids = user_data.get("downloaded_songs", [])
        downloaded_songs_details = [copy.deepcopy(self.songs[s_id]) for s_id in downloaded_songs_ids if s_id in self.songs]
        return {"status": "success", "downloaded_songs": downloaded_songs_details}

    def get_user_liked_albums(self) -> Dict[str, Any]:
        """
        Retrieves the list of albums liked by the current user.

        Returns:
            Dict[str, Any]: Dictionary containing list of liked albums or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        liked_albums_ids = user_data.get("liked_albums", [])
        liked_albums_details = [copy.deepcopy(self.albums[a_id]) for a_id in liked_albums_ids if a_id in self.albums]
        return {"status": "success", "liked_albums": liked_albums_details}

    def like_album(self, album_id: str) -> Dict[str, bool]:
        """
        Adds an album to the current user's liked albums.

        Args:
            album_id (str): ID of the album to like.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if album_id not in self.albums:
            return {"status": False, "message": f"Album with ID {album_id} not found."}

        if album_id not in user_data.get("liked_albums", []):
            user_data.setdefault("liked_albums", []).append(album_id)
            return {"status": True, "message": f"Album {album_id} liked."}
        return {"status": False, "message": f"Album {album_id} already liked."}

    def unlike_album(self, album_id: str) -> Dict[str, bool]:
        """
        Removes an album from the current user's liked albums.

        Args:
            album_id (str): ID of the album to unlike.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if album_id not in self.albums:
            return {"status": False, "message": f"Album with ID {album_id} not found."}

        if album_id in user_data.get("liked_albums", []):
            user_data["liked_albums"].remove(album_id)
            return {"status": True, "message": f"Album {album_id} unliked."}
        return {"status": False, "message": f"Album {album_id} not in liked albums."}

    def get_user_library_albums(self) -> Dict[str, Any]:
        """
        Retrieves the list of albums in the current user's library.

        Returns:
            Dict[str, Any]: Dictionary containing list of library albums or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        library_albums_ids = user_data.get("library_albums", [])
        library_albums_details = [copy.deepcopy(self.albums[a_id]) for a_id in library_albums_ids if a_id in self.albums]
        return {"status": "success", "library_albums": library_albums_details}

    def add_album_to_library(self, album_id: str) -> Dict[str, bool]:
        """
        Adds an album to the current user's library.

        Args:
            album_id (str): ID of the album to add.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if album_id not in self.albums:
            return {"status": False, "message": f"Album with ID {album_id} not found."}

        if album_id not in user_data.get("library_albums", []):
            user_data.setdefault("library_albums", []).append(album_id)
            return {"status": True, "message": f"Album {album_id} added to library."}
        return {"status": False, "message": f"Album {album_id} already in library."}

    def remove_album_from_library(self, album_id: str) -> Dict[str, bool]:
        """
        Removes an album from the current user's library.

        Args:
            album_id (str): ID of the album to remove.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if album_id not in self.albums:
            return {"status": False, "message": f"Album with ID {album_id} not found."}

        if album_id in user_data.get("library_albums", []):
            user_data["library_albums"].remove(album_id)
            return {"status": True, "message": f"Album {album_id} removed from library."}
        return {"status": False, "message": f"Album {album_id} not in library."}

    def get_user_liked_playlists(self) -> Dict[str, Any]:
        """
        Retrieves the list of playlists liked by the current user.

        Returns:
            Dict[str, Any]: Dictionary containing list of liked playlists or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        liked_playlists_ids = user_data.get("liked_playlists", [])
        liked_playlists_details = [copy.deepcopy(self.playlists[p_id]) for p_id in liked_playlists_ids if p_id in self.playlists]
        return {"status": "success", "liked_playlists": liked_playlists_details}

    def like_playlist(self, playlist_id: str) -> Dict[str, bool]:
        """
        Adds a playlist to the current user's liked playlists.

        Args:
            playlist_id (str): ID of the playlist to like.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if playlist_id not in self.playlists:
            return {"status": False, "message": f"Playlist with ID {playlist_id} not found."}

        if playlist_id not in user_data.get("liked_playlists", []):
            user_data.setdefault("liked_playlists", []).append(playlist_id)
            return {"status": True, "message": f"Playlist {playlist_id} liked."}
        return {"status": False, "message": f"Playlist {playlist_id} already liked."}

    def unlike_playlist(self, playlist_id: str) -> Dict[str, bool]:
        """
        Removes a playlist from the current user's liked playlists.

        Args:
            playlist_id (str): ID of the playlist to unlike.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if playlist_id not in self.playlists:
            return {"status": False, "message": f"Playlist with ID {playlist_id} not found."}

        if playlist_id in user_data.get("liked_playlists", []):
            user_data["liked_playlists"].remove(playlist_id)
            return {"status": True, "message": f"Playlist {playlist_id} unliked."}
        return {"status": False, "message": f"Playlist {playlist_id} not in liked playlists."}

    def get_user_following_artists(self) -> Dict[str, Any]:
        """
        Retrieves the list of artists followed by the current user.

        Returns:
            Dict[str, Any]: Dictionary containing list of followed artists or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        following_artists_ids = user_data.get("following_artists", [])
        following_artists_details = [copy.deepcopy(self.artists[a_id]) for a_id in following_artists_ids if a_id in self.artists]
        return {"status": "success", "following_artists": following_artists_details}

    def follow_artist(self, artist_id: str) -> Dict[str, bool]:
        """
        Adds an artist to the current user's followed artists.

        Args:
            artist_id (str): ID of the artist to follow.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if artist_id not in self.artists:
            return {"status": False, "message": f"Artist with ID {artist_id} not found."}

        if artist_id not in user_data.get("following_artists", []):
            user_data.setdefault("following_artists", []).append(artist_id)
            return {"status": True, "message": f"Artist {artist_id} followed."}
        return {"status": False, "message": f"Artist {artist_id} already followed."}

    def unfollow_artist(self, artist_id: str) -> Dict[str, bool]:
        """
        Removes an artist from the current user's followed artists.

        Args:
            artist_id (str): ID of the artist to unfollow.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if artist_id not in self.artists:
            return {"status": False, "message": f"Artist with ID {artist_id} not found."}

        if artist_id in user_data.get("following_artists", []):
            user_data["following_artists"].remove(artist_id)
            return {"status": True, "message": f"Artist {artist_id} unfollowed."}
        return {"status": False, "message": f"Artist {artist_id} not followed."}

    def create_playlist(
        self,
        name: str,
        description: Optional[str] = None,
        public: bool = True,
    ) -> Dict[str, Any]:
        """
        Creates a new playlist for the current user.

        Args:
            name (str): Name of the playlist.
            description (Optional[str]): Description of the playlist.
            public (bool): Whether the playlist is public.
        Returns:
            Dict[str, Any]: Dictionary containing new playlist details or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}

        new_playlist_id = self._generate_unique_id()
        current_time_iso = datetime.datetime.now().isoformat() + "Z"

        new_playlist = {
            "id": new_playlist_id,
            "name": name,
            "user_id": user_data["id"],
            "description": description,
            "public": public,
            "tracks": [],
            "created_at": current_time_iso,
            "updated_at": current_time_iso,
        }
        self.playlists[new_playlist_id] = new_playlist
        
        user_data.setdefault("liked_playlists", []).append(new_playlist_id)

        return {"status": "success", "playlist": copy.deepcopy(new_playlist)}

    def delete_playlist(self, playlist_id: str) -> Dict[str, bool]:
        """
        Deletes a playlist owned by the current user.

        Args:
            playlist_id (str): ID of the playlist to delete.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        
        if playlist_id in self.playlists and self.playlists[playlist_id]["user_id"] == user_data["id"]:
            if playlist_id in user_data.get("liked_playlists", []):
                user_data["liked_playlists"].remove(playlist_id)
            del self.playlists[playlist_id]
            return {"status": True, "message": f"Playlist {playlist_id} deleted."}
        return {"status": False, "message": f"Playlist {playlist_id} not found or not owned by user."}

    def add_song_to_playlist(self, playlist_id: str, song_id: str) -> Dict[str, bool]:
        """
        Adds a song to a specific playlist owned by the current user.

        Args:
            playlist_id (str): ID of the playlist.
            song_id (str): ID of the song to add.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        
        if playlist_id not in self.playlists:
            return {"status": False, "message": f"Playlist {playlist_id} not found."}
        if self.playlists[playlist_id]["user_id"] != user_data["id"]:
            return {"status": False, "message": "You do not own this playlist."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song {song_id} not found."}

        playlist = self.playlists[playlist_id]
        if song_id not in playlist["tracks"]:
            playlist["tracks"].append(song_id)
            playlist["updated_at"] = datetime.datetime.now().isoformat() + "Z"
            return {"status": True, "message": f"Song {song_id} added to playlist {playlist_id}."}
        return {"status": False, "message": f"Song {song_id} already in playlist {playlist_id}."}

    def remove_song_from_playlist(self, playlist_id: str, song_id: str) -> Dict[str, bool]:
        """
        Removes a song from a specific playlist owned by the current user.

        Args:
            playlist_id (str): ID of the playlist.
            song_id (str): ID of the song to remove.
        Returns:
            Dict[str, bool]: Dictionary indicating success status and message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        
        if playlist_id not in self.playlists:
            return {"status": False, "message": f"Playlist {playlist_id} not found."}
        if self.playlists[playlist_id]["user_id"] != user_data["id"]:
            return {"status": False, "message": "You do not own this playlist."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song {song_id} not found."}

        playlist = self.playlists[playlist_id]
        if song_id in playlist["tracks"]:
            playlist["tracks"].remove(song_id)
            playlist["updated_at"] = datetime.datetime.now().isoformat() + "Z"
            return {"status": True, "message": f"Song {song_id} removed from playlist {playlist_id}."}
        return {"status": False, "message": f"Song {song_id} not in playlist {playlist_id}."}

    def update_playlist_details(
        self,
        playlist_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        public: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Updates details of a playlist owned by the current user.

        Args:
            playlist_id (str): ID of the playlist to update.
            name (Optional[str]): New name for the playlist.
            description (Optional[str]): New description for the playlist.
            public (Optional[bool]): New visibility setting for the playlist.
        Returns:
            Dict[str, Any]: Dictionary containing updated playlist details or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        if playlist_id not in self.playlists:
            return {"status": "error", "message": f"Playlist {playlist_id} not found."}
        if self.playlists[playlist_id]["user_id"] != user_data["id"]:
            return {"status": "error", "message": "You do not own this playlist."}

        playlist = self.playlists[playlist_id]
        if name is not None:
            playlist["name"] = name
        if description is not None:
            playlist["description"] = description
        if public is not None:
            playlist["public"] = public
        
        playlist["updated_at"] = datetime.datetime.now().isoformat() + "Z"
        return {"status": "success", "playlist": copy.deepcopy(playlist)}

    def get_all_songs(self) -> Dict[str, Any]:
        """
        Retrieves a list of all songs available on the platform.

        Returns:
            Dict[str, Any]: Dictionary containing list of all songs.
        """
        return {"status": "success", "songs": [copy.deepcopy(s) for s in self.songs.values()]}

    def get_song_details(self, song_id: str) -> Dict[str, Any]:
        """
        Retrieves details for a specific song.

        Args:
            song_id (str): ID of the song to retrieve.
        Returns:
            Dict[str, Any]: Dictionary containing song details or error message.
        """
        song = self.songs.get(song_id)
        if song:
            return {"status": "success", "song": copy.deepcopy(song)}
        return {"status": "error", "message": f"Song {song_id} not found."}

    def get_all_albums(self) -> Dict[str, Any]:
        """
        Retrieves a list of all albums available on the platform.

        Returns:
            Dict[str, Any]: Dictionary containing list of all albums.
        """
        return {"status": "success", "albums": [copy.deepcopy(a) for a in self.albums.values()]}

    def get_album_details(self, album_id: str) -> Dict[str, Any]:
        """
        Retrieves details for a specific album.

        Args:
            album_id (str): ID of the album to retrieve.
        Returns:
            Dict[str, Any]: Dictionary containing album details or error message.
        """
        album = self.albums.get(album_id)
        if album:
            return {"status": "success", "album": copy.deepcopy(album)}
        return {"status": "error", "message": f"Album {album_id} not found."}

    def get_all_playlists(self) -> Dict[str, Any]:
        """
        Retrieves a list of all public playlists available on the platform.

        Returns:
            Dict[str, Any]: Dictionary containing list of public playlists.
        """
        public_playlists = [copy.deepcopy(p) for p in self.playlists.values() if p.get("public")]
        return {"status": "success", "playlists": public_playlists}

    def get_playlist_details(self, playlist_id: str) -> Dict[str, Any]:
        """
        Retrieves details for a specific playlist.

        Args:
            playlist_id (str): ID of the playlist to retrieve.
        Returns:
            Dict[str, Any]: Dictionary containing playlist details or error message.
        """
        playlist = self.playlists.get(playlist_id)
        user_data = self._get_current_user_data()

        if playlist:
            if playlist.get("public") or (user_data and playlist.get("user_id") == user_data["id"]):
                return {"status": "success", "playlist": copy.deepcopy(playlist)}
            return {"status": "error", "message": "Access denied to private playlist."}
        return {"status": "error", "message": f"Playlist {playlist_id} not found."}

    def get_all_artists(self) -> Dict[str, Any]:
        """
        Retrieves a list of all artists available on the platform.

        Returns:
            Dict[str, Any]: Dictionary containing list of all artists.
        """
        return {"status": "success", "artists": [copy.deepcopy(a) for a in self.artists.values()]}

    def get_artist_details(self, artist_id: str) -> Dict[str, Any]:
        """
        Retrieves details for a specific artist.

        Args:
            artist_id (str): ID of the artist to retrieve.
        Returns:
            Dict[str, Any]: Dictionary containing artist details or error message.
        """
        artist = self.artists.get(artist_id)
        if artist:
            return {"status": "success", "artist": copy.deepcopy(artist)}
        return {"status": "error", "message": f"Artist {artist_id} not found."}

    def search_content(self, query: str, content_type: Literal["song", "album", "playlist", "artist", "all"] = "all") -> Dict[str, Any]:
        """
        Searches for content (songs, albums, playlists, artists) by a given query.

        Args:
            query (str): Search query string.
            content_type (Literal): Type of content to search for ("song", "album", "playlist", "artist", "all").
        Returns:
            Dict[str, Any]: Dictionary containing search results.
        """
        results = {}

        if content_type in ["song", "all"]:
            matched_songs = [copy.deepcopy(s) for s in self.songs.values() if query.lower() in s["title"].lower()]
            results["songs"] = matched_songs
        
        if content_type in ["album", "all"]:
            matched_albums = [copy.deepcopy(a) for a in self.albums.values() if query.lower() in a["title"].lower()]
            results["albums"] = matched_albums

        if content_type in ["playlist", "all"]:
            user_data = self._get_current_user_data()
            matched_playlists = []
            for p in self.playlists.values():
                if query.lower() in p["name"].lower():
                    if p.get("public") or (user_data and p.get("user_id") == user_data["id"]):
                        matched_playlists.append(copy.deepcopy(p))
            results["playlists"] = matched_playlists

        if content_type in ["artist", "all"]:
            matched_artists = [copy.deepcopy(ar) for ar in self.artists.values() if query.lower() in ar["name"].lower()]
            results["artists"] = matched_artists

        return {"status": "success", "results": results}

    def play_content(self, content_type: Literal["song", "album", "playlist"], content_id: str) -> Dict[str, Any]:
        """
        Simulates playing a song, album, or playlist.

        Args:
            content_type (Literal): Type of content to play ("song", "album", "playlist").
            content_id (str): ID of the content to play.
        Returns:
            Dict[str, Any]: Dictionary containing play status or error message.
        """
        content = None
        if content_type == "song":
            content = self.songs.get(content_id)
        elif content_type == "album":
            content = self.albums.get(content_id)
        elif content_type == "playlist":
            content = self.playlists.get(content_id)
            user_data = self._get_current_user_data()
            if content and not content.get("public") and (not user_data or content.get("user_id") != user_data["id"]):
                return {"status": "error", "message": "Access denied to private playlist."}

        if content:
            return {"status": "success", "message": f"Now playing {content_type}: {content.get('title') or content.get('name')} (ID: {content_id})."}
        return {"status": "error", "message": f"{content_type.capitalize()} with ID {content_id} not found."}

    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Retrieves statistics and metadata for the current user.

        Returns:
            Dict[str, Any]: Dictionary containing user statistics or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        stats = {
            "user_id": user_data["id"],
            "email": user_data.get("email"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "registration_date": user_data.get("registration_date"),
            "last_active_date": user_data.get("last_active_date"),
            "preferred_genre": user_data.get("preferred_genre"),
            "total_play_time_ms": user_data.get("total_play_time_ms", 0),
            "country": user_data.get("country"),
            "device_type": user_data.get("device_type"),
            "premium": user_data.get("premium", False),
            "total_liked_songs": len(user_data.get("liked_songs", [])),
            "total_liked_albums": len(user_data.get("liked_albums", [])),
            "total_liked_playlists": len(user_data.get("liked_playlists", [])),
            "total_following_artists": len(user_data.get("following_artists", [])),
            "total_library_songs": len(user_data.get("library_songs", [])),
            "total_downloaded_songs": len(user_data.get("downloaded_songs", []))
        }
        
        return {"status": "success", "statistics": stats}

    def update_user_preferences(
        self,
        preferred_genre: Optional[str] = None,
        country: Optional[str] = None,
        device_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Updates user preferences.

        Args:
            preferred_genre (Optional[str]): New preferred genre.
            country (Optional[str]): New country setting.
            device_type (Optional[str]): New device type.

        Returns:
            Dict[str, Any]: Dictionary indicating success status and updated fields.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        updated_fields = []
        
        if preferred_genre is not None:
            user_data["preferred_genre"] = preferred_genre
            updated_fields.append("preferred_genre")
        
        if country is not None:
            user_data["country"] = country
            updated_fields.append("country")
        
        if device_type is not None:
            user_data["device_type"] = device_type
            updated_fields.append("device_type")
        
        user_data["last_active_date"] = datetime.datetime.now().isoformat() + "Z"
        
        return {
            "status": "success", 
            "message": f"Updated fields: {', '.join(updated_fields) if updated_fields else 'none'}",
            "updated_fields": updated_fields
        }

    def get_listening_history(self, limit: int = 50) -> Dict[str, Any]:
        """
        Retrieves user's listening history based on liked songs and library.

        Args:
            limit (int): Maximum number of items to return.

        Returns:
            Dict[str, Any]: Dictionary containing listening history or error message.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        # Combine liked songs and library songs as "history"
        all_song_ids = list(set(
            user_data.get("liked_songs", []) + 
            user_data.get("library_songs", [])
        ))
        
        history = []
        for song_id in all_song_ids[:limit]:
            if song_id in self.songs:
                song_data = copy.deepcopy(self.songs[song_id])
                song_data["played_at"] = user_data.get("last_active_date", datetime.datetime.now().isoformat() + "Z")
                history.append(song_data)
        
        return {"status": "success", "history": history, "total_items": len(history)}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self._load_scenario(DEFAULT_STATE)
        print("SpotifyApis: All dummy data reset to default state.")
        return {"reset_status": True}