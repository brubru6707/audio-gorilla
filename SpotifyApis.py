import datetime
import copy
import uuid
from typing import Dict, Any, Optional, Literal, List
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("SpotifyApis")
class SpotifyApis:
    """
    A dummy API class for simulating Spotify Web API operations.
    This class provides an in-memory backend for development and testing purposes.
    Matches the real Spotify Web API structure and authentication.
    """

    def __init__(self):
        """
        Initializes the SpotifyApis instance, setting up the in-memory
        data stores and loading the default scenario.
        """
        self._api_description = "This tool belongs to the Spotify API, which provides core functionality for managing music, playlists, and user profiles."
        self.users: Dict[str, Any] = {}
        self.payment_cards: Dict[str, Any] = {}
        self.tracks: Dict[str, Any] = {}  # Changed from songs to tracks
        self.albums: Dict[str, Any] = {}
        self.playlists: Dict[str, Any] = {}
        self.artists: Dict[str, Any] = {}
        self.access_token: Optional[str] = None  # OAuth token instead of username
        self.current_user_id: Optional[str] = None  # User ID for authenticated user

        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain "users", "payment_cards", "tracks", etc.
        """
        scenario_copy = copy.deepcopy(scenario)
        self.users = scenario_copy.get("users", {})
        self.payment_cards = scenario_copy.get("payment_cards", {})
        # Handle both 'songs' and 'tracks' for backward compatibility
        self.tracks = scenario_copy.get("tracks", scenario_copy.get("songs", {}))
        self.albums = scenario_copy.get("albums", {})
        self.playlists = scenario_copy.get("playlists", {})
        self.artists = scenario_copy.get("artists", {})
        print("SpotifyApis: Loaded scenario with UUIDs for all entities.")

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for dummy entities.
        """
        return str(uuid.uuid4())
    
    def _generate_spotify_uri(self, resource_type: str, resource_id: str) -> str:
        """
        Generates a Spotify URI for a resource.
        
        Args:
            resource_type (str): Type of resource (track, album, playlist, artist, user).
            resource_id (str): ID of the resource.
        Returns:
            str: Spotify URI (e.g., spotify:track:xxxxx).
        """
        return f"spotify:{resource_type}:{resource_id}"
    
    def _generate_api_href(self, resource_type: str, resource_id: str) -> str:
        """
        Generates an API href URL for a resource.
        
        Args:
            resource_type (str): Type of resource (tracks, albums, playlists, artists, users).
            resource_id (str): ID of the resource.
        Returns:
            str: API href URL.
        """
        return f"https://api.spotify.com/v1/{resource_type}/{resource_id}"
    
    def _generate_external_url(self, resource_type: str, resource_id: str) -> str:
        """
        Generates an external Spotify URL for a resource.
        
        Args:
            resource_type (str): Type of resource (track, album, playlist, artist, user).
            resource_id (str): ID of the resource.
        Returns:
            str: External Spotify URL.
        """
        return f"https://open.spotify.com/{resource_type}/{resource_id}"

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

    def authenticate(self, access_token: str) -> None:
        """
        Authenticates a user with an OAuth access token.
        In a real implementation, this would validate the token with Spotify's servers.
        For this simulation, the token format is: "token_{user_email}".

        Args:
            access_token (str): OAuth 2.0 access token (format: "token_{user_email}").
        
        Raises:
            Exception: If the token is invalid or user not found.
        """
        if not access_token or not access_token.startswith("token_"):
            raise Exception("Invalid access token format")
        
        # Extract email from token (simulation)
        email = access_token.replace("token_", "")
        user_id = self._get_user_id_by_email(email)
        
        if not user_id:
            raise Exception(f"User with email {email} not found")
        
        self.access_token = access_token
        self.current_user_id = user_id

    def _ensure_authenticated(self) -> None:
        """
        Ensures that a user is authenticated before performing operations.
        
        Raises:
            Exception: If no user is authenticated.
        """
        if not self.access_token or not self.current_user_id:
            raise Exception("No access token provided. Authentication required.")

    def _get_current_user_data(self) -> Optional[Dict]:
        """
        Helper to get the data of the currently authenticated user.

        Returns:
            Optional[Dict]: Current user's data if authenticated, None otherwise.
        """
        if not self.current_user_id:
            return None
        return self.users.get(self.current_user_id)

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

    def get_current_user_profile(self) -> Dict[str, Any]:
        """
        Get detailed profile information about the current user (including the current user's username).
        Endpoint: GET https://api.spotify.com/v1/me
        
        Returns:
            Dict[str, Any]: User profile object with Spotify standard fields.
        
        Raises:
            Exception: If not authenticated.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        user_id = user_data["id"]
        email = self._get_user_email_by_id(user_id)
        
        profile = {
            "id": user_id,
            "type": "user",
            "uri": self._generate_spotify_uri("user", user_id),
            "href": self._generate_api_href("users", user_id),
            "external_urls": {
                "spotify": self._generate_external_url("user", user_id)
            },
            "display_name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip() or email,
            "email": email,
            "country": user_data.get("country", "US"),
            "product": "premium" if user_data.get("premium", False) else "free",
            "followers": {
                "href": None,
                "total": user_data.get("followers_count", 0)
            },
            "images": user_data.get("images", [])
        }
        
        return profile

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
        Note: This is a simulation - real Spotify uses external payment processors.

        Args:
            card_name (str): Name on the card.
            card_number (str): Card number.
            expiry_year (int): Expiration year.
            expiry_month (int): Expiration month.
            cvv_number (str): CVV security code.
            is_default (bool): Whether to set as default payment method.
        Returns:
            Dict[str, Any]: Payment method object.
        
        Raises:
            Exception: If not authenticated.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")

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
        return copy.deepcopy(new_card)

    def show_payment_methods(self) -> List[Dict[str, Any]]:
        """
        Shows all payment methods associated with the current user.
        Note: This is a simulation - real Spotify uses external payment processors.

        Returns:
            List[Dict[str, Any]]: List of payment method objects.
        
        Raises:
            Exception: If not authenticated.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")

        user_id = user_data["id"]
        payment_methods = [
            copy.deepcopy(card_info)
            for card_id, card_info in self.payment_cards.items()
            if card_info.get("user_id") == user_id
        ]
        return payment_methods

    def set_default_payment_method(self, payment_method_id: str) -> None:
        """
        Set a specific payment method as the default for the current user.
        Note: This is a simulation - real Spotify uses external payment processors.

        Args:
            payment_method_id (str): The ID of the payment method to set as default.
        
        Raises:
            Exception: If not authenticated or payment method not found.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")

        if payment_method_id not in self.payment_cards:
            raise Exception(f"Payment method with ID {payment_method_id} not found")

        if self.payment_cards[payment_method_id]["user_id"] != user_data["id"]:
            raise Exception("You do not have permission to modify this payment method")

        for card_id, card_info in self.payment_cards.items():
            if card_info["user_id"] == user_data["id"] and card_info["is_default"]:
                self.payment_cards[card_id]["is_default"] = False
                break

        self.payment_cards[payment_method_id]["is_default"] = True

    def _enrich_track(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches a track object with Spotify standard fields.
        
        Args:
            track_data (Dict[str, Any]): Raw track data.
        Returns:
            Dict[str, Any]: Enriched track object with standard Spotify fields.
        """
        track_id = track_data["id"]
        enriched = copy.deepcopy(track_data)
        
        # Add Spotify standard fields
        enriched["type"] = "track"
        enriched["uri"] = self._generate_spotify_uri("track", track_id)
        enriched["href"] = self._generate_api_href("tracks", track_id)
        enriched["external_urls"] = {
            "spotify": self._generate_external_url("track", track_id)
        }
        
        # Ensure duration_ms exists
        if "duration_ms" not in enriched:
            enriched["duration_ms"] = enriched.get("duration", 0) * 1000 if "duration" in enriched else 180000
        
        # Add track-specific fields
        enriched.setdefault("explicit", False)
        enriched.setdefault("popularity", 50)
        enriched.setdefault("track_number", 1)
        enriched.setdefault("disc_number", 1)
        enriched.setdefault("is_local", False)
        enriched.setdefault("preview_url", f"https://p.scdn.co/mp3-preview/{track_id}")
        
        # Rename 'title' to 'name' if needed
        if "title" in enriched and "name" not in enriched:
            enriched["name"] = enriched["title"]
        
        return enriched
    
    def _enrich_album(self, album_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches an album object with Spotify standard fields.
        
        Args:
            album_data (Dict[str, Any]): Raw album data.
        Returns:
            Dict[str, Any]: Enriched album object with standard Spotify fields.
        """
        album_id = album_data["id"]
        enriched = copy.deepcopy(album_data)
        
        enriched["type"] = "album"
        enriched["uri"] = self._generate_spotify_uri("album", album_id)
        enriched["href"] = self._generate_api_href("albums", album_id)
        enriched["external_urls"] = {
            "spotify": self._generate_external_url("album", album_id)
        }
        
        enriched.setdefault("album_type", "album")
        enriched.setdefault("total_tracks", len(enriched.get("tracks", [])))
        enriched.setdefault("release_date", "2024-01-01")
        enriched.setdefault("release_date_precision", "day")
        enriched.setdefault("images", [])
        enriched.setdefault("label", "Independent")
        enriched.setdefault("popularity", 50)
        
        # Rename 'title' to 'name' if needed
        if "title" in enriched and "name" not in enriched:
            enriched["name"] = enriched["title"]
        
        return enriched
    
    def _enrich_playlist(self, playlist_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches a playlist object with Spotify standard fields.
        
        Args:
            playlist_data (Dict[str, Any]): Raw playlist data.
        Returns:
            Dict[str, Any]: Enriched playlist object with standard Spotify fields.
        """
        playlist_id = playlist_data["id"]
        enriched = copy.deepcopy(playlist_data)
        
        enriched["type"] = "playlist"
        enriched["uri"] = self._generate_spotify_uri("playlist", playlist_id)
        enriched["href"] = self._generate_api_href("playlists", playlist_id)
        enriched["external_urls"] = {
            "spotify": self._generate_external_url("playlist", playlist_id)
        }
        
        enriched.setdefault("collaborative", False)
        enriched.setdefault("images", [])
        enriched.setdefault("snapshot_id", self._generate_unique_id())
        enriched.setdefault("followers", {"href": None, "total": 0})
        
        # Handle tracks field
        track_ids = enriched.get("tracks", [])
        if isinstance(track_ids, list) and track_ids and isinstance(track_ids[0], str):
            # Convert track IDs to track objects
            enriched["tracks"] = {
                "href": f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                "total": len(track_ids),
                "items": []  # Simplified - would contain track objects in real API
            }
        
        return enriched
    
    def _enrich_artist(self, artist_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches an artist object with Spotify standard fields.
        
        Args:
            artist_data (Dict[str, Any]): Raw artist data.
        Returns:
            Dict[str, Any]: Enriched artist object with standard Spotify fields.
        """
        artist_id = artist_data["id"]
        enriched = copy.deepcopy(artist_data)
        
        enriched["type"] = "artist"
        enriched["uri"] = self._generate_spotify_uri("artist", artist_id)
        enriched["href"] = self._generate_api_href("artists", artist_id)
        enriched["external_urls"] = {
            "spotify": self._generate_external_url("artist", artist_id)
        }
        
        enriched.setdefault("genres", [])
        enriched.setdefault("popularity", 50)
        enriched.setdefault("followers", {"href": None, "total": 0})
        enriched.setdefault("images", [])
        
        return enriched

    def get_saved_tracks(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get a list of the tracks saved in the current user's 'Your Music' library.
        Endpoint: GET https://api.spotify.com/v1/me/tracks
        
        Args:
            limit (int): Maximum number of items to return (default 20, max 50).
            offset (int): Index of the first item to return (default 0).
        
        Returns:
            Dict[str, Any]: Paging object containing saved track objects.
        
        Raises:
            Exception: If not authenticated.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        saved_track_ids = user_data.get("liked_songs", [])
        total = len(saved_track_ids)
        
        # Apply pagination
        paginated_ids = saved_track_ids[offset:offset + limit]
        
        items = []
        for track_id in paginated_ids:
            if track_id in self.tracks:
                track_data = self._enrich_track(self.tracks[track_id])
                items.append({
                    "added_at": user_data.get("last_active_date", datetime.datetime.now().isoformat() + "Z"),
                    "track": track_data
                })
        
        # Build paging object
        paging = {
            "href": f"https://api.spotify.com/v1/me/tracks?offset={offset}&limit={limit}",
            "limit": limit,
            "offset": offset,
            "total": total,
            "items": items,
            "previous": f"https://api.spotify.com/v1/me/tracks?offset={max(0, offset - limit)}&limit={limit}" if offset > 0 else None,
            "next": f"https://api.spotify.com/v1/me/tracks?offset={offset + limit}&limit={limit}" if offset + limit < total else None
        }
        
        return paging

    def save_tracks(self, track_ids: List[str]) -> None:
        """
        Save one or more tracks to the current user's 'Your Music' library.
        Endpoint: PUT https://api.spotify.com/v1/me/tracks
        
        Args:
            track_ids (List[str]): List of Spotify track IDs (max 50).
        
        Raises:
            Exception: If not authenticated or track not found.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if len(track_ids) > 50:
            raise Exception("Maximum 50 tracks can be saved at once")
        
        for track_id in track_ids:
            if track_id not in self.tracks:
                raise Exception(f"Track {track_id} not found")
            
            if track_id not in user_data.get("liked_songs", []):
                user_data.setdefault("liked_songs", []).append(track_id)

    def remove_saved_tracks(self, track_ids: List[str]) -> None:
        """
        Remove one or more tracks from the current user's 'Your Music' library.
        Endpoint: DELETE https://api.spotify.com/v1/me/tracks
        
        Args:
            track_ids (List[str]): List of Spotify track IDs (max 50).
        
        Raises:
            Exception: If not authenticated.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if len(track_ids) > 50:
            raise Exception("Maximum 50 tracks can be removed at once")
        
        for track_id in track_ids:
            if track_id in user_data.get("liked_songs", []):
                user_data["liked_songs"].remove(track_id)

    def check_saved_tracks(self, track_ids: List[str]) -> List[bool]:
        """
        Check if one or more tracks is already saved in the current user's 'Your Music' library.
        Endpoint: GET https://api.spotify.com/v1/me/tracks/contains
        
        Args:
            track_ids (List[str]): List of Spotify track IDs (max 50).
        
        Returns:
            List[bool]: List of boolean values indicating if each track is saved.
        
        Raises:
            Exception: If not authenticated.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if len(track_ids) > 50:
            raise Exception("Maximum 50 tracks can be checked at once")
        
        saved_track_ids = user_data.get("liked_songs", [])
        return [track_id in saved_track_ids for track_id in track_ids]

    def get_saved_albums(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get a list of the albums saved in the current user's 'Your Music' library.
        Endpoint: GET https://api.spotify.com/v1/me/albums
        
        Args:
            limit (int): Maximum number of items to return (default 20, max 50).
            offset (int): Index of the first item to return (default 0).
        
        Returns:
            Dict[str, Any]: Paging object containing saved album objects.
        
        Raises:
            Exception: If not authenticated.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        saved_album_ids = user_data.get("liked_albums", [])
        total = len(saved_album_ids)
        
        # Apply pagination
        paginated_ids = saved_album_ids[offset:offset + limit]
        
        items = []
        for album_id in paginated_ids:
            if album_id in self.albums:
                album_data = self._enrich_album(self.albums[album_id])
                items.append({
                    "added_at": user_data.get("last_active_date", datetime.datetime.now().isoformat() + "Z"),
                    "album": album_data
                })
        
        # Build paging object
        paging = {
            "href": f"https://api.spotify.com/v1/me/albums?offset={offset}&limit={limit}",
            "limit": limit,
            "offset": offset,
            "total": total,
            "items": items,
            "previous": f"https://api.spotify.com/v1/me/albums?offset={max(0, offset - limit)}&limit={limit}" if offset > 0 else None,
            "next": f"https://api.spotify.com/v1/me/albums?offset={offset + limit}&limit={limit}" if offset + limit < total else None
        }
        
        return paging

    def save_albums(self, album_ids: List[str]) -> None:
        """
        Save one or more albums to the current user's 'Your Music' library.
        Endpoint: PUT https://api.spotify.com/v1/me/albums
        
        Args:
            album_ids (List[str]): List of Spotify album IDs (max 50).
        
        Raises:
            Exception: If not authenticated or album not found.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if len(album_ids) > 20:
            raise Exception("Maximum 20 albums can be saved at once")
        
        for album_id in album_ids:
            if album_id not in self.albums:
                raise Exception(f"Album {album_id} not found")
            
            if album_id not in user_data.get("liked_albums", []):
                user_data.setdefault("liked_albums", []).append(album_id)

    def remove_saved_albums(self, album_ids: List[str]) -> None:
        """
        Remove one or more albums from the current user's 'Your Music' library.
        Endpoint: DELETE https://api.spotify.com/v1/me/albums
        
        Args:
            album_ids (List[str]): List of Spotify album IDs (max 50).
        
        Raises:
            Exception: If not authenticated.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if len(album_ids) > 20:
            raise Exception("Maximum 20 albums can be removed at once")
        
        for album_id in album_ids:
            if album_id in user_data.get("liked_albums", []):
                user_data["liked_albums"].remove(album_id)

    def follow_artists(self, artist_ids: List[str]) -> None:
        """
        Add the current user as a follower of one or more artists.
        Endpoint: PUT https://api.spotify.com/v1/me/following
        
        Args:
            artist_ids (List[str]): List of Spotify artist IDs (max 50).
        
        Raises:
            Exception: If not authenticated or artist not found.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if len(artist_ids) > 50:
            raise Exception("Maximum 50 artists can be followed at once")
        
        for artist_id in artist_ids:
            if artist_id not in self.artists:
                raise Exception(f"Artist {artist_id} not found")
            
            if artist_id not in user_data.get("following_artists", []):
                user_data.setdefault("following_artists", []).append(artist_id)

    def unfollow_artists(self, artist_ids: List[str]) -> None:
        """
        Remove the current user as a follower of one or more artists.
        Endpoint: DELETE https://api.spotify.com/v1/me/following
        
        Args:
            artist_ids (List[str]): List of Spotify artist IDs (max 50).
        
        Raises:
            Exception: If not authenticated.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if len(artist_ids) > 50:
            raise Exception("Maximum 50 artists can be unfollowed at once")
        
        for artist_id in artist_ids:
            if artist_id in user_data.get("following_artists", []):
                user_data["following_artists"].remove(artist_id)

    def get_followed_artists(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get the current user's followed artists.
        Endpoint: GET https://api.spotify.com/v1/me/following
        
        Args:
            limit (int): Maximum number of items to return (default 20, max 50).
        
        Returns:
            Dict[str, Any]: Cursor-based paging object containing artist objects.
        
        Raises:
            Exception: If not authenticated.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        following_artist_ids = user_data.get("following_artists", [])
        total = len(following_artist_ids)
        
        # Apply limit
        paginated_ids = following_artist_ids[:limit]
        
        items = []
        for artist_id in paginated_ids:
            if artist_id in self.artists:
                artist_data = self._enrich_artist(self.artists[artist_id])
                items.append(artist_data)
        
        # Build cursor-based paging object (simplified)
        result = {
            "artists": {
                "href": f"https://api.spotify.com/v1/me/following?type=artist&limit={limit}",
                "limit": limit,
                "total": total,
                "items": items,
                "cursors": {
                    "after": None,
                    "before": None
                },
                "next": None
            }
        }
        
        return result

    def create_playlist(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        public: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a playlist for a Spotify user.
        Endpoint: POST https://api.spotify.com/v1/users/{user_id}/playlists
        
        Args:
            user_id (str): The user's Spotify user ID.
            name (str): Name of the playlist.
            description (Optional[str]): Description of the playlist.
            public (bool): Whether the playlist is public (default True).
        
        Returns:
            Dict[str, Any]: Playlist object.
        
        Raises:
            Exception: If not authenticated or user not found.
        """
        self._ensure_authenticated()
        current_user_data = self._get_current_user_data()
        
        if not current_user_data:
            raise Exception("User not found")
        
        # In real Spotify API, you can only create playlists for yourself
        if user_id != current_user_data["id"]:
            raise Exception("Can only create playlists for the authenticated user")

        new_playlist_id = self._generate_unique_id()
        current_time_iso = datetime.datetime.now().isoformat() + "Z"

        new_playlist = {
            "id": new_playlist_id,
            "name": name,
            "user_id": current_user_data["id"],
            "description": description,
            "public": public,
            "tracks": [],
            "created_at": current_time_iso,
            "updated_at": current_time_iso,
        }
        self.playlists[new_playlist_id] = new_playlist
        
        current_user_data.setdefault("liked_playlists", []).append(new_playlist_id)

        return self._enrich_playlist(new_playlist)

    def get_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """
        Get a playlist.
        Endpoint: GET https://api.spotify.com/v1/playlists/{playlist_id}
        
        Args:
            playlist_id (str): The Spotify ID for the playlist.
        
        Returns:
            Dict[str, Any]: Playlist object.
        
        Raises:
            Exception: If playlist not found or access denied.
        """
        if playlist_id not in self.playlists:
            raise Exception(f"Playlist {playlist_id} not found")
        
        playlist = self.playlists[playlist_id]
        
        # Check if user has access (public or owned by current user)
        if not playlist.get("public"):
            self._ensure_authenticated()
            user_data = self._get_current_user_data()
            if not user_data or playlist.get("user_id") != user_data["id"]:
                raise Exception("Access denied to private playlist")
        
        return self._enrich_playlist(playlist)

    def change_playlist_details(
        self,
        playlist_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        public: Optional[bool] = None,
    ) -> None:
        """
        Change a playlist's name and public/private state.
        Endpoint: PUT https://api.spotify.com/v1/playlists/{playlist_id}
        
        Args:
            playlist_id (str): The Spotify ID for the playlist.
            name (Optional[str]): New name for the playlist.
            description (Optional[str]): New description for the playlist.
            public (Optional[bool]): New visibility setting for the playlist.
        
        Raises:
            Exception: If not authenticated or not owner of playlist.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if playlist_id not in self.playlists:
            raise Exception(f"Playlist {playlist_id} not found")
        
        if self.playlists[playlist_id]["user_id"] != user_data["id"]:
            raise Exception("Can only modify your own playlists")

        playlist = self.playlists[playlist_id]
        if name is not None:
            playlist["name"] = name
        if description is not None:
            playlist["description"] = description
        if public is not None:
            playlist["public"] = public
        
        playlist["updated_at"] = datetime.datetime.now().isoformat() + "Z"

    def add_items_to_playlist(self, playlist_id: str, track_uris: List[str], position: Optional[int] = None) -> Dict[str, str]:
        """
        Add one or more items to a user's playlist.
        Endpoint: POST https://api.spotify.com/v1/playlists/{playlist_id}/tracks
        
        Args:
            playlist_id (str): The Spotify ID for the playlist.
            track_uris (List[str]): List of Spotify track URIs (max 100).
            position (Optional[int]): Position to insert tracks.
        
        Returns:
            Dict[str, str]: Snapshot object with snapshot_id.
        
        Raises:
            Exception: If not authenticated or not owner of playlist.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if playlist_id not in self.playlists:
            raise Exception(f"Playlist {playlist_id} not found")
        
        if self.playlists[playlist_id]["user_id"] != user_data["id"]:
            raise Exception("Can only modify your own playlists")
        
        if len(track_uris) > 100:
            raise Exception("Maximum 100 tracks can be added at once")

        playlist = self.playlists[playlist_id]
        
        # Extract track IDs from URIs (format: spotify:track:xxxxx)
        track_ids = []
        for uri in track_uris:
            if uri.startswith("spotify:track:"):
                track_id = uri.replace("spotify:track:", "")
                if track_id not in self.tracks:
                    raise Exception(f"Track {track_id} not found")
                track_ids.append(track_id)
            else:
                raise Exception(f"Invalid track URI format: {uri}")
        
        # Add tracks
        current_tracks = playlist.get("tracks", [])
        if position is not None:
            for i, track_id in enumerate(track_ids):
                current_tracks.insert(position + i, track_id)
        else:
            current_tracks.extend(track_ids)
        
        playlist["tracks"] = current_tracks
        playlist["updated_at"] = datetime.datetime.now().isoformat() + "Z"
        new_snapshot_id = self._generate_unique_id()
        playlist["snapshot_id"] = new_snapshot_id
        
        return {"snapshot_id": new_snapshot_id}

    def remove_items_from_playlist(self, playlist_id: str, track_uris: List[str]) -> Dict[str, str]:
        """
        Remove one or more items from a user's playlist.
        Endpoint: DELETE https://api.spotify.com/v1/playlists/{playlist_id}/tracks
        
        Args:
            playlist_id (str): The Spotify ID for the playlist.
            track_uris (List[str]): List of Spotify track URIs to remove (max 100).
        
        Returns:
            Dict[str, str]: Snapshot object with snapshot_id.
        
        Raises:
            Exception: If not authenticated or not owner of playlist.
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if playlist_id not in self.playlists:
            raise Exception(f"Playlist {playlist_id} not found")
        
        if self.playlists[playlist_id]["user_id"] != user_data["id"]:
            raise Exception("Can only modify your own playlists")
        
        if len(track_uris) > 100:
            raise Exception("Maximum 100 tracks can be removed at once")

        playlist = self.playlists[playlist_id]
        
        # Extract track IDs from URIs
        track_ids = []
        for uri in track_uris:
            if uri.startswith("spotify:track:"):
                track_id = uri.replace("spotify:track:", "")
                track_ids.append(track_id)
            else:
                raise Exception(f"Invalid track URI format: {uri}")
        
        # Remove tracks
        current_tracks = playlist.get("tracks", [])
        for track_id in track_ids:
            while track_id in current_tracks:
                current_tracks.remove(track_id)
        
        playlist["tracks"] = current_tracks
        playlist["updated_at"] = datetime.datetime.now().isoformat() + "Z"
        new_snapshot_id = self._generate_unique_id()
        playlist["snapshot_id"] = new_snapshot_id
        
        return {"snapshot_id": new_snapshot_id}

    def get_track(self, track_id: str) -> Dict[str, Any]:
        """
        Get Spotify catalog information for a single track.
        Endpoint: GET https://api.spotify.com/v1/tracks/{id}
        
        Args:
            track_id (str): The Spotify ID for the track.
        
        Returns:
            Dict[str, Any]: Track object.
        
        Raises:
            Exception: If track not found.
        """
        if track_id not in self.tracks:
            raise Exception(f"Track {track_id} not found")
        
        return self._enrich_track(self.tracks[track_id])

    def get_several_tracks(self, track_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get Spotify catalog information for multiple tracks.
        Endpoint: GET https://api.spotify.com/v1/tracks
        
        Args:
            track_ids (List[str]): List of Spotify track IDs (max 50).
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Object containing array of track objects.
        
        Raises:
            Exception: If more than 50 IDs provided.
        """
        if len(track_ids) > 50:
            raise Exception("Maximum 50 tracks can be requested at once")
        
        tracks = []
        for track_id in track_ids:
            if track_id in self.tracks:
                tracks.append(self._enrich_track(self.tracks[track_id]))
            else:
                tracks.append(None)
        
        return {"tracks": tracks}

    def get_album(self, album_id: str) -> Dict[str, Any]:
        """
        Get Spotify catalog information for a single album.
        Endpoint: GET https://api.spotify.com/v1/albums/{id}
        
        Args:
            album_id (str): The Spotify ID for the album.
        
        Returns:
            Dict[str, Any]: Album object.
        
        Raises:
            Exception: If album not found.
        """
        if album_id not in self.albums:
            raise Exception(f"Album {album_id} not found")
        
        return self._enrich_album(self.albums[album_id])

    def get_several_albums(self, album_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get Spotify catalog information for multiple albums.
        Endpoint: GET https://api.spotify.com/v1/albums
        
        Args:
            album_ids (List[str]): List of Spotify album IDs (max 20).
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Object containing array of album objects.
        
        Raises:
            Exception: If more than 20 IDs provided.
        """
        if len(album_ids) > 20:
            raise Exception("Maximum 20 albums can be requested at once")
        
        albums = []
        for album_id in album_ids:
            if album_id in self.albums:
                albums.append(self._enrich_album(self.albums[album_id]))
            else:
                albums.append(None)
        
        return {"albums": albums}

    def get_artist(self, artist_id: str) -> Dict[str, Any]:
        """
        Get Spotify catalog information for a single artist.
        Endpoint: GET https://api.spotify.com/v1/artists/{id}
        
        Args:
            artist_id (str): The Spotify ID for the artist.
        
        Returns:
            Dict[str, Any]: Artist object.
        
        Raises:
            Exception: If artist not found.
        """
        if artist_id not in self.artists:
            raise Exception(f"Artist {artist_id} not found")
        
        return self._enrich_artist(self.artists[artist_id])

    def get_several_artists(self, artist_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get Spotify catalog information for several artists.
        Endpoint: GET https://api.spotify.com/v1/artists
        
        Args:
            artist_ids (List[str]): List of Spotify artist IDs (max 50).
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Object containing array of artist objects.
        
        Raises:
            Exception: If more than 50 IDs provided.
        """
        if len(artist_ids) > 50:
            raise Exception("Maximum 50 artists can be requested at once")
        
        artists = []
        for artist_id in artist_ids:
            if artist_id in self.artists:
                artists.append(self._enrich_artist(self.artists[artist_id]))
            else:
                artists.append(None)
        
        return {"artists": artists}

    def search(self, q: str, type: List[str], limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get Spotify catalog information about albums, artists, playlists, tracks that match a keyword string.
        Endpoint: GET https://api.spotify.com/v1/search
        
        Args:
            q (str): Search query keywords.
            type (List[str]): List of item types to search across (album, artist, playlist, track).
            limit (int): Maximum number of results to return per type (default 20, max 50).
            offset (int): Index of the first result to return (default 0, max 1000).
        
        Returns:
            Dict[str, Any]: Search response object with paging objects for each type.
        
        Raises:
            Exception: If invalid parameters.
        """
        if limit > 50:
            raise Exception("Maximum limit is 50")
        if offset > 1000:
            raise Exception("Maximum offset is 1000")
        
        results = {}

        if "track" in type:
            matched_tracks = []
            for track in self.tracks.values():
                track_name = track.get("name", track.get("title", ""))
                if q.lower() in track_name.lower():
                    matched_tracks.append(self._enrich_track(track))
            
            total = len(matched_tracks)
            paginated = matched_tracks[offset:offset + limit]
            
            results["tracks"] = {
                "href": f"https://api.spotify.com/v1/search?q={q}&type=track&offset={offset}&limit={limit}",
                "limit": limit,
                "offset": offset,
                "total": total,
                "items": paginated,
                "previous": f"https://api.spotify.com/v1/search?q={q}&type=track&offset={max(0, offset - limit)}&limit={limit}" if offset > 0 else None,
                "next": f"https://api.spotify.com/v1/search?q={q}&type=track&offset={offset + limit}&limit={limit}" if offset + limit < total else None
            }
        
        if "album" in type:
            matched_albums = []
            for album in self.albums.values():
                album_name = album.get("name", album.get("title", ""))
                if q.lower() in album_name.lower():
                    matched_albums.append(self._enrich_album(album))
            
            total = len(matched_albums)
            paginated = matched_albums[offset:offset + limit]
            
            results["albums"] = {
                "href": f"https://api.spotify.com/v1/search?q={q}&type=album&offset={offset}&limit={limit}",
                "limit": limit,
                "offset": offset,
                "total": total,
                "items": paginated,
                "previous": f"https://api.spotify.com/v1/search?q={q}&type=album&offset={max(0, offset - limit)}&limit={limit}" if offset > 0 else None,
                "next": f"https://api.spotify.com/v1/search?q={q}&type=album&offset={offset + limit}&limit={limit}" if offset + limit < total else None
            }
        
        if "artist" in type:
            matched_artists = []
            for artist in self.artists.values():
                if q.lower() in artist.get("name", "").lower():
                    matched_artists.append(self._enrich_artist(artist))
            
            total = len(matched_artists)
            paginated = matched_artists[offset:offset + limit]
            
            results["artists"] = {
                "href": f"https://api.spotify.com/v1/search?q={q}&type=artist&offset={offset}&limit={limit}",
                "limit": limit,
                "offset": offset,
                "total": total,
                "items": paginated,
                "previous": f"https://api.spotify.com/v1/search?q={q}&type=artist&offset={max(0, offset - limit)}&limit={limit}" if offset > 0 else None,
                "next": f"https://api.spotify.com/v1/search?q={q}&type=artist&offset={offset + limit}&limit={limit}" if offset + limit < total else None
            }
        
        if "playlist" in type:
            matched_playlists = []
            for playlist in self.playlists.values():
                if q.lower() in playlist.get("name", "").lower():
                    # Only include public playlists in search or user's own playlists
                    if playlist.get("public"):
                        matched_playlists.append(self._enrich_playlist(playlist))
            
            total = len(matched_playlists)
            paginated = matched_playlists[offset:offset + limit]
            
            results["playlists"] = {
                "href": f"https://api.spotify.com/v1/search?q={q}&type=playlist&offset={offset}&limit={limit}",
                "limit": limit,
                "offset": offset,
                "total": total,
                "items": paginated,
                "previous": f"https://api.spotify.com/v1/search?q={q}&type=playlist&offset={max(0, offset - limit)}&limit={limit}" if offset > 0 else None,
                "next": f"https://api.spotify.com/v1/search?q={q}&type=playlist&offset={offset + limit}&limit={limit}" if offset + limit < total else None
            }

        return results

    def reset_data(self) -> None:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.
        """
        self._load_scenario(DEFAULT_STATE)
        self.access_token = None
        self.current_user_id = None
        print("SpotifyApis: All dummy data reset to default state.")
