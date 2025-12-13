import datetime
import copy
import uuid
from typing import Dict, Any, Optional, List
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("SpotifyApis")
class SpotifyApis:
    """
    An API class for simulating Spotify Web API operations.
    This class provides an in-memory backend for development and testing purposes.
    Matches the real Spotify Web API structure and authentication.
    """

    def __init__(self):
        """
        Initializes the SpotifyApis instance with in-memory data stores for simulating Spotify Web API operations.
        
        Sets up empty dictionaries for users, payment cards, tracks, albums, playlists, and artists,
        then loads the default scenario data. This simulated backend allows for testing Spotify workflows
        without connecting to actual Spotify servers.
        
        Side Effects:
            - Creates empty data stores for all Spotify entities
            - Loads default state from state_loader
            - Initializes authentication state (no user authenticated)
        
        Note:
            This is a simulation class for development/testing. All data is stored in memory
            and will be lost when the instance is destroyed. Uses OAuth 2.0-style token authentication.
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
        Loads a predefined scenario into the backend's state, initializing all Spotify entities.
        
        Deep copies scenario data and populates all entity stores (users, tracks, albums, playlists,
        artists, payment cards). Handles backward compatibility by accepting both 'songs' and 'tracks' keys.

        Args:
            scenario (Dict): A dictionary containing the complete state to load. Expected keys:
                - "users" (Dict[str, Any]): User data keyed by UUID
                - "payment_cards" (Dict[str, Any]): Payment card data keyed by UUID
                - "tracks" or "songs" (Dict[str, Any]): Track data keyed by UUID (backward compatible)
                - "albums" (Dict[str, Any]): Album data keyed by UUID
                - "playlists" (Dict[str, Any]): Playlist data keyed by UUID
                - "artists" (Dict[str, Any]): Artist data keyed by UUID
                
        Side Effects:
            - Completely replaces all entity stores with scenario data
            - Prints confirmation message to console
            - Does NOT reset authentication state (access_token, current_user_id)
            
        Note:
            Uses deep copy to prevent accidental modification of source scenario.
            Backward compatible with 'songs' key (older scenarios) which maps to 'tracks'.
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
        Generates a unique UUID string for creating new entities (playlists, payment cards, etc.).
        
        Uses Python's uuid.uuid4() to generate a random UUID, ensuring global uniqueness
        across all entity types in the simulated backend.
        
        Returns:
            str: A UUID string in standard format (e.g., "550e8400-e29b-41d4-a716-446655440000")
            
        Note:
            Used for creating new playlists, payment cards, and snapshot IDs.
            Spotify IDs in real API are 22-character base62 strings, but UUIDs work for simulation.
        """
        return str(uuid.uuid4())
    
    def _generate_spotify_uri(self, resource_type: str, resource_id: str) -> str:
        """
        Generates a Spotify URI (Uniform Resource Identifier) for a resource.
        
        Spotify URIs are used to uniquely identify and link to Spotify resources. They follow
        the format: spotify:{type}:{id}
        
        Args:
            resource_type (str): Type of resource. Valid values:
                - "track": For individual songs
                - "album": For album collections
                - "playlist": For user playlists
                - "artist": For music artists
                - "user": For Spotify users
            resource_id (str): The unique ID of the resource (UUID in simulation)
            
        Returns:
            str: Spotify URI in format "spotify:{type}:{id}"
                Example: "spotify:track:550e8400-e29b-41d4-a716-446655440000"
                
        Note:
            Spotify URIs can be used to play content in Spotify apps via deep linking.
            In real Spotify, IDs are 22-character base62 strings, not UUIDs.
        """
        return f"spotify:{resource_type}:{resource_id}"
    
    def _generate_api_href(self, resource_type: str, resource_id: str) -> str:
        """
        Generates an API href URL for accessing a resource via the Spotify Web API.
        
        Creates the full REST API endpoint URL for retrieving detailed information about
        a specific resource. Used in API response objects for hypermedia navigation.
        
        Args:
            resource_type (str): Plural form of resource type for API endpoint:
                - "tracks": For track endpoints
                - "albums": For album endpoints
                - "playlists": For playlist endpoints
                - "artists": For artist endpoints
                - "users": For user endpoints
            resource_id (str): The unique ID of the resource
            
        Returns:
            str: Full API URL in format "https://api.spotify.com/v1/{type}/{id}"
                Example: "https://api.spotify.com/v1/tracks/550e8400-e29b-41d4-a716-446655440000"
                
        Note:
            These URLs match Spotify's REST API structure and can be used to fetch
            full resource details. Follows HATEOAS principles for API discoverability.
        """
        return f"https://api.spotify.com/v1/{resource_type}/{resource_id}"
    
    def _generate_external_url(self, resource_type: str, resource_id: str) -> str:
        """
        Generates an external Spotify URL for opening a resource in the Spotify web player or app.
        
        Creates user-facing URLs for the Spotify web player (open.spotify.com) that can be
        shared or opened in a browser to play content or view profiles.
        
        Args:
            resource_type (str): Singular form of resource type:
                - "track": For individual songs
                - "album": For album pages
                - "playlist": For playlist pages
                - "artist": For artist profiles
                - "user": For user profiles
            resource_id (str): The unique ID of the resource
            
        Returns:
            str: External Spotify URL in format "https://open.spotify.com/{type}/{id}"
                Example: "https://open.spotify.com/track/550e8400-e29b-41d4-a716-446655440000"
                
        Note:
            These URLs can be shared with users and will open in the Spotify web player
            or redirect to the desktop/mobile app if installed. Used in API responses
            for easy content sharing.
        """
        return f"https://open.spotify.com/{resource_type}/{resource_id}"

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """
        Internal helper that looks up a user's UUID by their email address.
        
        Iterates through all users in the backend to find one with a matching email.
        This enables user lookup by email for authentication purposes.

        Args:
            email (str): The email address to search for (case-sensitive)

        Returns:
            Optional[str]: The user's UUID if found, None if no user has that email
            
        Note:
            This performs a linear search through all users. For production systems,
            an email-to-UUID index would be more efficient.
        """
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """
        Internal helper that retrieves a user's email address from their UUID.
        
        Looks up user data by UUID and extracts the email field. Used for building
        user profile responses and display names.

        Args:
            user_id (str): The user's UUID

        Returns:
            Optional[str]: The user's email address if user exists, None if not found
            
        Note:
            Returns None if user_id doesn't exist in the users dictionary or if
            the user data doesn't contain an email field.
        """
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def authenticate(self, access_token: str) -> None:
        """
        Authenticates a user with an OAuth 2.0 access token, establishing an authenticated session.
        
        Simulates the Spotify OAuth 2.0 authentication flow. Validates the token format, extracts
        the user email from the token, locates the corresponding user in the backend, and sets up
        the authenticated session for subsequent API calls.

        Args:
            access_token (str): OAuth 2.0 Bearer access token in format "token_{user_email}".
                Example: "token_alice@example.com" for user with that email.
                In real Spotify API, tokens are long random strings obtained through OAuth flow.
        
        Raises:
            Exception: If token format is invalid (doesn't start with "token_" or is empty)
                Error message: "Invalid access token format"
            Exception: If no user exists with the email extracted from the token
                Error message: "User with email {email} not found"
                
        Side Effects:
            - Sets self.access_token to the provided token
            - Sets self.current_user_id to the authenticated user's UUID
            - All subsequent API calls will operate in context of this user
            
        Note:
            This is a simplified authentication for simulation. Real Spotify uses OAuth 2.0
            with authorization code flow, requiring client ID, secret, and user consent.
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> # Now authenticated as Alice, can access protected endpoints
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
        Internal guard method that verifies a user is authenticated before accessing protected resources.
        
        Checks that both access_token and current_user_id are set, indicating a successful
        authentication. This should be called at the start of every method that requires authentication.
        
        Raises:
            Exception: If either access_token or current_user_id is None (user not authenticated)
                Error message: "No access token provided. Authentication required."
                
        Note:
            This is an internal helper method used by all protected endpoints.
            Most Spotify API endpoints require authentication except for public catalog browsing.
        """
        if not self.access_token or not self.current_user_id:
            raise Exception("No access token provided. Authentication required.")

    def _get_current_user_data(self) -> Optional[Dict]:
        """
        Internal helper to retrieve the complete data dictionary of the currently authenticated user.
        
        Looks up the authenticated user's data from the users dictionary using current_user_id.
        Used throughout the API to access and modify user-specific data.

        Returns:
            Optional[Dict]: Current user's complete data dictionary if authenticated, containing:
                - "id": User UUID
                - "email": User email address
                - "first_name", "last_name": Name components
                - "liked_songs": List of saved track IDs
                - "liked_albums": List of saved album IDs
                - "following_artists": List of followed artist IDs
                - "liked_playlists": List of owned/saved playlist IDs
                - "country": Country code
                - "premium": Premium subscription status
                - And other user fields
                Returns None if no user is authenticated.
                
        Note:
            Returns a reference to the user data dict (not a copy), allowing modifications.
        """
        if not self.current_user_id:
            return None
        return self.users.get(self.current_user_id)

    def _get_user_payment_cards(self, user_id: str) -> Dict[str, Any]:
        """
        Internal helper to retrieve all payment cards belonging to a specific user.
        
        Filters the global payment_cards dictionary to find cards where user_id matches.
        Returns a dictionary of cards keyed by card UUID.

        Args:
            user_id (str): The user's UUID
            
        Returns:
            Dict[str, Any]: Dictionary mapping card UUIDs to card data objects:
                {
                    "card_uuid_1": {
                        "id": str,
                        "card_name": str,
                        "user_id": str,
                        "card_number": str,
                        "expiry_year": int,
                        "expiry_month": int,
                        "cvv_number": str,
                        "is_default": bool
                    },
                    # ... more cards
                }
                Returns empty dict {} if user has no payment cards.
                
        Note:
            This is a simulation feature. Real Spotify uses external payment processors
            (Stripe, PayPal, etc.) and doesn't expose card details via API.
        """
        cards = {}
        for card_id, card_data in self.payment_cards.items():
            if card_data.get("user_id") == user_id:
                cards[card_id] = card_data
        return cards

    def get_current_user_profile(self) -> Dict[str, Any]:
        """
        Retrieves detailed profile information about the currently authenticated user, including username and subscription details.
        
        Returns comprehensive user profile matching Spotify's GET /v1/me endpoint response structure.
        Includes Spotify standard fields like URIs, external URLs, and follower counts.

        Returns:
            Dict[str, Any]: Complete user profile object with structure:
                {
                    "id": str,                  # User UUID
                    "type": "user",             # Resource type constant
                    "uri": str,                 # Spotify URI (spotify:user:{id})
                    "href": str,                # API endpoint URL
                    "external_urls": {          # External web links
                        "spotify": str          # Spotify web player URL
                    },
                    "display_name": str,        # Full name or email if name unavailable
                    "email": str,               # User's email address
                    "country": str,             # ISO country code (default: "US")
                    "product": str,             # "premium" or "free"
                    "followers": {              # Follower information
                        "href": None,           # Always None (no follower endpoint)
                        "total": int            # Number of followers
                    },
                    "images": List              # Profile image URLs (array of image objects)
                }
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user_id doesn't exist in users dictionary
                Error message: "User not found"
                
        Note:
            Real Spotify API returns additional fields like explicit_content settings.
            The display_name is constructed from first_name and last_name, or falls back to email.
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> profile = api.get_current_user_profile()
            >>> print(f"{profile['display_name']} ({profile['product']} user)")
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
        Adds a new payment card to the current user's account for subscription payments.
        
        Creates a payment method record and optionally sets it as the default. If set as default,
        any existing default payment method is automatically unmarked. This is a simulation feature;
        real Spotify uses external payment processors (Stripe, PayPal, etc.).

        Args:
            card_name (str): Name as it appears on the card
                Example: "John Smith"
            card_number (str): Full card number (typically 16 digits for Visa/Mastercard)
                Example: "4111111111111111"
                Note: In production, this would be tokenized by payment processor
            expiry_year (int): Card expiration year (4-digit format)
                Example: 2025
            expiry_month (int): Card expiration month (1-12)
                Example: 12
            cvv_number (str): Card verification value (3-4 digits)
                Example: "123"
            is_default (bool): Whether to set this card as the default payment method.
                Default: False. If True, unmarks any existing default card.
                
        Returns:
            Dict[str, Any]: Payment method object with structure:
                {
                    "id": str,                  # Generated UUID for this card
                    "card_name": str,           # Name on card
                    "user_id": str,             # Owner's user UUID
                    "card_number": str,         # Card number
                    "expiry_year": int,         # Expiration year
                    "expiry_month": int,        # Expiration month
                    "cvv_number": str,          # CVV code
                    "is_default": bool          # Default status
                }
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
                
        Side Effects:
            - Adds new card to self.payment_cards dictionary
            - If is_default=True, sets all other user cards' is_default to False
            
        Note:
            This is a simulation. Real Spotify never directly handles or stores card details.
            Payment processing is delegated to PCI-compliant third-party processors.
            Card data would be tokenized and only the token stored.
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> card = api.add_payment_method(
            ...     card_name="Alice Smith",
            ...     card_number="4111111111111111",
            ...     expiry_year=2025,
            ...     expiry_month=12,
            ...     cvv_number="123",
            ...     is_default=True
            ... )
            >>> print(f"Added card: {card['id']}")
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
        Retrieves all payment methods (cards) associated with the current authenticated user.
        
        Returns a list of all saved payment cards for the user, including their details and
        default status. This is a simulation feature; real Spotify delegates payment management
        to external payment processors.

        Returns:
            List[Dict[str, Any]]: List of payment method objects, each with structure:
                [
                    {
                        "id": str,              # Card UUID
                        "card_name": str,       # Name on card
                        "user_id": str,         # Owner's user UUID
                        "card_number": str,     # Full card number
                        "expiry_year": int,     # Expiration year
                        "expiry_month": int,    # Expiration month (1-12)
                        "cvv_number": str,      # CVV security code
                        "is_default": bool      # Whether this is the default card
                    },
                    # ... more cards
                ]
                Returns empty list [] if user has no saved payment methods.
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
                
        Note:
            This is a simulation. Real Spotify uses external payment processors (Stripe, PayPal)
            and wouldn't expose full card details via API. Only masked card numbers and
            last 4 digits would be returned in production.
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> cards = api.show_payment_methods()
            >>> for card in cards:
            ...     print(f"{card['card_name']} ending in {card['card_number'][-4:]}")
            ...     if card['is_default']:
            ...         print("  (Default)")
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
        Sets a specific payment method as the default for the current user's account.
        
        Marks the specified card as default and automatically unmarks any previously default card.
        Validates that the payment method exists and belongs to the authenticated user.
        This is a simulation feature; real Spotify uses external payment processors.

        Args:
            payment_method_id (str): The UUID of the payment method to set as default.
                Must be a valid card ID that belongs to the current user.
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If payment_method_id doesn't exist in payment_cards
                Error message: "Payment method with ID {payment_method_id} not found"
            Exception: If payment method belongs to a different user
                Error message: "You do not have permission to modify this payment method"
                
        Side Effects:
            - Sets is_default=True for the specified payment method
            - Sets is_default=False for any previously default card belonging to this user
            - Changes affect future subscription billing and payment processing
            
        Note:
            This is a simulation. Real Spotify manages default payment methods through
            external payment processors' APIs with proper PCI compliance.
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> cards = api.show_payment_methods()
            >>> new_default_id = cards[1]['id']  # Select second card
            >>> api.set_default_payment_method(new_default_id)
            >>> # Second card is now the default
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
        Enriches a raw track data object with Spotify Web API standard fields and URIs.
        
        Transforms minimal track data from the backend into a complete Spotify API-compliant
        track object by adding standard fields like URIs, external URLs, popularity, preview URLs,
        and ensuring consistent field naming.

        Args:
            track_data (Dict[str, Any]): Raw track data from backend containing at minimum:
                - "id": Track UUID
                - "title" or "name": Track name
                - Other optional fields like artist, album, duration
        
        Returns:
            Dict[str, Any]: Enriched track object with Spotify standard structure:
                {
                    "id": str,                      # Track UUID
                    "type": "track",                # Resource type constant
                    "uri": str,                     # Spotify URI (spotify:track:{id})
                    "href": str,                    # API endpoint URL
                    "external_urls": {              # External web links
                        "spotify": str              # Spotify web player URL
                    },
                    "name": str,                    # Track name (renamed from title if needed)
                    "duration_ms": int,             # Duration in milliseconds
                    "explicit": bool,               # Explicit content flag (default: False)
                    "popularity": int,              # Popularity 0-100 (default: 50)
                    "track_number": int,            # Track position on album (default: 1)
                    "disc_number": int,             # Disc number for multi-disc albums (default: 1)
                    "is_local": bool,               # Local file flag (default: False)
                    "preview_url": str,             # 30-second preview MP3 URL
                    # ... plus all original track_data fields
                }
                
        Note:
            - Renames "title" field to "name" to match Spotify API conventions
            - Converts "duration" (seconds) to "duration_ms" (milliseconds) if needed
            - Adds default values for missing optional fields
            - Returns a deep copy to prevent unintended mutations
            
        Example:
            >>> raw_track = {"id": "abc-123", "title": "Song Name", "duration": 180}
            >>> enriched = api._enrich_track(raw_track)
            >>> print(enriched["uri"])  # "spotify:track:abc-123"
            >>> print(enriched["name"])  # "Song Name" (renamed from title)
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
        Enriches a raw album data object with Spotify Web API standard fields and metadata.
        
        Transforms minimal album data from the backend into a complete Spotify API-compliant
        album object by adding standard fields like URIs, external URLs, album type, release date,
        total tracks count, and ensuring consistent field naming.

        Args:
            album_data (Dict[str, Any]): Raw album data from backend containing at minimum:
                - "id": Album UUID
                - "title" or "name": Album name
                - "tracks": List of track IDs in the album (optional)
                - Other optional fields like artist, release_date
        
        Returns:
            Dict[str, Any]: Enriched album object with Spotify standard structure:
                {
                    "id": str,                      # Album UUID
                    "type": "album",                # Resource type constant
                    "uri": str,                     # Spotify URI (spotify:album:{id})
                    "href": str,                    # API endpoint URL
                    "external_urls": {              # External web links
                        "spotify": str              # Spotify web player URL
                    },
                    "name": str,                    # Album name (renamed from title if needed)
                    "album_type": str,              # "album", "single", "compilation" (default: "album")
                    "total_tracks": int,            # Number of tracks (calculated from tracks array)
                    "release_date": str,            # Release date "YYYY-MM-DD" (default: "2024-01-01")
                    "release_date_precision": str,  # "year", "month", "day" (default: "day")
                    "images": List,                 # Album cover images array (default: [])
                    "label": str,                   # Record label (default: "Independent")
                    "popularity": int,              # Popularity 0-100 (default: 50)
                    # ... plus all original album_data fields
                }
                
        Note:
            - Renames "title" field to "name" to match Spotify API conventions
            - Calculates total_tracks from tracks array length if present
            - Adds default values for missing optional fields
            - Returns a deep copy to prevent unintended mutations
            
        Example:
            >>> raw_album = {"id": "album-456", "title": "Album Name", "tracks": ["t1", "t2"]}
            >>> enriched = api._enrich_album(raw_album)
            >>> print(enriched["uri"])  # "spotify:album:album-456"
            >>> print(enriched["total_tracks"])  # 2
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
        Enriches a raw playlist data object with Spotify Web API standard fields and metadata.
        
        Transforms minimal playlist data from the backend into a complete Spotify API-compliant
        playlist object by adding standard fields like URIs, external URLs, collaborative status,
        snapshot IDs, follower counts, and converting track IDs to proper track objects structure.

        Args:
            playlist_data (Dict[str, Any]): Raw playlist data from backend containing at minimum:
                - "id": Playlist UUID
                - "name": Playlist name
                - "tracks": List of track IDs or track objects
                - "owner_id": Owner user UUID (optional)
                - Other optional fields like description, public
        
        Returns:
            Dict[str, Any]: Enriched playlist object with Spotify standard structure:
                {
                    "id": str,                      # Playlist UUID
                    "type": "playlist",             # Resource type constant
                    "uri": str,                     # Spotify URI (spotify:playlist:{id})
                    "href": str,                    # API endpoint URL
                    "external_urls": {              # External web links
                        "spotify": str              # Spotify web player URL
                    },
                    "name": str,                    # Playlist name
                    "collaborative": bool,          # Collaborative edit flag (default: False)
                    "images": List,                 # Playlist cover images array (default: [])
                    "snapshot_id": str,             # Version identifier for playlist state
                    "followers": {                  # Follower information
                        "href": None,               # Always None (no follower endpoint)
                        "total": int                # Number of followers (default: 0)
                    },
                    "tracks": {                     # Tracks container object
                        "href": str,                # Tracks endpoint URL
                        "total": int,               # Number of tracks
                        "items": []                 # Simplified - would contain track objects
                    },
                    # ... plus all original playlist_data fields
                }
                
        Note:
            - Converts simple track ID list to Spotify-standard tracks object structure
            - Generates unique snapshot_id for playlist version tracking
            - Adds default values for missing optional fields
            - Returns a deep copy to prevent unintended mutations
            - In real Spotify API, tracks.items would contain full track objects with added_at timestamps
            
        Example:
            >>> raw_playlist = {"id": "pl-789", "name": "My Playlist", "tracks": ["t1", "t2", "t3"]}
            >>> enriched = api._enrich_playlist(raw_playlist)
            >>> print(enriched["uri"])  # "spotify:playlist:pl-789"
            >>> print(enriched["tracks"]["total"])  # 3
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
        Enriches a raw artist data object with Spotify Web API standard fields and metadata.
        
        Transforms minimal artist data from the backend into a complete Spotify API-compliant
        artist object by adding standard fields like URIs, external URLs, genres, popularity,
        follower counts, and profile images.

        Args:
            artist_data (Dict[str, Any]): Raw artist data from backend containing at minimum:
                - "id": Artist UUID
                - "name": Artist name
                - Other optional fields like genres, popularity, followers_count
        
        Returns:
            Dict[str, Any]: Enriched artist object with Spotify standard structure:
                {
                    "id": str,                      # Artist UUID
                    "type": "artist",               # Resource type constant
                    "uri": str,                     # Spotify URI (spotify:artist:{id})
                    "href": str,                    # API endpoint URL
                    "external_urls": {              # External web links
                        "spotify": str              # Spotify web player URL
                    },
                    "name": str,                    # Artist name
                    "genres": List[str],            # Music genres (default: [])
                    "popularity": int,              # Popularity 0-100 (default: 50)
                    "followers": {                  # Follower information
                        "href": None,               # Always None (no follower endpoint)
                        "total": int                # Number of followers (default: 0)
                    },
                    "images": List,                 # Artist profile images array (default: [])
                    # ... plus all original artist_data fields
                }
                
        Note:
            - Adds default values for missing optional fields
            - Returns a deep copy to prevent unintended mutations
            - Real Spotify API includes additional fields like external_ids (ISNI)
            
        Example:
            >>> raw_artist = {"id": "artist-999", "name": "Artist Name"}
            >>> enriched = api._enrich_artist(raw_artist)
            >>> print(enriched["uri"])  # "spotify:artist:artist-999"
            >>> print(enriched["genres"])  # []
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
        Retrieves a paginated list of tracks saved in the current user's 'Your Music' library.
        
        Returns the user's liked/saved tracks with pagination support. Each track includes
        an added_at timestamp. Corresponds to Spotify's GET /v1/me/tracks endpoint.

        Args:
            limit (int): Maximum number of tracks to return per page.
                Valid range: 1-50. Default: 20
            offset (int): Index of the first track to return (for pagination).
                Default: 0. Use with limit for page navigation.
                Example: offset=20 with limit=20 gets the second page.
        
        Returns:
            Dict[str, Any]: Paging object with structure:
                {
                    "href": str,                    # Current request URL
                    "limit": int,                   # Page size used
                    "offset": int,                  # Starting index
                    "total": int,                   # Total saved tracks count
                    "items": [                      # Array of saved track objects
                        {
                            "added_at": str,        # ISO 8601 timestamp when track was saved
                            "track": {              # Full enriched track object
                                "id": str,
                                "name": str,
                                "uri": str,
                                "duration_ms": int,
                                # ... all track fields
                            }
                        },
                        # ... more items
                    ],
                    "previous": str | None,         # URL for previous page (None if first page)
                    "next": str | None              # URL for next page (None if last page)
                }
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
                
        Note:
            - Only returns tracks that exist in self.tracks (orphaned IDs are skipped)
            - Uses user's last_active_date as added_at fallback timestamp
            - Real Spotify API tracks actual save timestamps per track
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> page1 = api.get_saved_tracks(limit=10, offset=0)
            >>> print(f"Saved {page1['total']} tracks total")
            >>> for item in page1['items']:
            ...     print(f"- {item['track']['name']} (added {item['added_at']})")
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
        Saves one or more tracks to the current user's 'Your Music' library (liked songs).
        
        Adds tracks to the user's liked songs collection. Tracks already saved are ignored
        (no duplicates). Corresponds to Spotify's PUT /v1/me/tracks endpoint.

        Args:
            track_ids (List[str]): List of Spotify track IDs to save.
                Maximum: 50 tracks per request.
                Example: ["track-uuid-1", "track-uuid-2"]
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If more than 50 track IDs provided
                Error message: "Maximum 50 tracks can be saved at once"
            Exception: If any track_id doesn't exist in self.tracks
                Error message: "Track {track_id} not found"
                
        Side Effects:
            - Adds each track_id to user's liked_songs list (if not already present)
            - Creates liked_songs list if it doesn't exist
            - Duplicate track IDs are silently ignored (idempotent operation)
            
        Note:
            - Validates all tracks exist before adding any (atomic operation)
            - Real Spotify API is idempotent - saving an already-saved track is not an error
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> api.save_tracks(["track-id-1", "track-id-2", "track-id-3"])
            >>> # Tracks now appear in liked songs library
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
        Removes one or more tracks from the current user's 'Your Music' library (liked songs).
        
        Deletes tracks from the user's liked songs collection. Tracks not currently saved
        are silently ignored. Corresponds to Spotify's DELETE /v1/me/tracks endpoint.

        Args:
            track_ids (List[str]): List of Spotify track IDs to remove.
                Maximum: 50 tracks per request.
                Example: ["track-uuid-1", "track-uuid-2"]
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If more than 50 track IDs provided
                Error message: "Maximum 50 tracks can be removed at once"
                
        Side Effects:
            - Removes each track_id from user's liked_songs list (if present)
            - Track IDs not in liked_songs are silently ignored (idempotent operation)
            
        Note:
            - Does NOT validate whether track IDs exist in self.tracks
            - Real Spotify API is idempotent - removing an unsaved track is not an error
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> api.remove_saved_tracks(["track-id-1", "track-id-2"])
            >>> # Tracks no longer appear in liked songs library
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
        Checks if one or more tracks are already saved in the current user's 'Your Music' library.
        
        Returns a boolean array indicating save status for each requested track.
        Useful for UI to show "liked" state. Corresponds to Spotify's GET /v1/me/tracks/contains endpoint.

        Args:
            track_ids (List[str]): List of Spotify track IDs to check.
                Maximum: 50 tracks per request.
                Example: ["track-uuid-1", "track-uuid-2", "track-uuid-3"]
        
        Returns:
            List[bool]: Boolean array matching input track_ids order:
                [True, False, True] means 1st and 3rd tracks are saved, 2nd is not.
                Array length always matches track_ids length.
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If more than 50 track IDs provided
                Error message: "Maximum 50 tracks can be checked at once"
                
        Note:
            - Does NOT validate whether track IDs exist in self.tracks
            - Checks against user's liked_songs list
            - Non-existent track IDs return False (not saved)
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> api.save_tracks(["track-1", "track-3"])
            >>> status = api.check_saved_tracks(["track-1", "track-2", "track-3"])
            >>> print(status)  # [True, False, True]
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
        Retrieves a paginated list of albums saved in the current user's 'Your Music' library.
        
        Returns the user's liked/saved albums with pagination support. Each album includes
        an added_at timestamp. Corresponds to Spotify's GET /v1/me/albums endpoint.

        Args:
            limit (int): Maximum number of albums to return per page.
                Valid range: 1-50. Default: 20
            offset (int): Index of the first album to return (for pagination).
                Default: 0. Use with limit for page navigation.
                Example: offset=20 with limit=20 gets the second page.
        
        Returns:
            Dict[str, Any]: Paging object with structure:
                {
                    "href": str,                    # Current request URL
                    "limit": int,                   # Page size used
                    "offset": int,                  # Starting index
                    "total": int,                   # Total saved albums count
                    "items": [                      # Array of saved album objects
                        {
                            "added_at": str,        # ISO 8601 timestamp when album was saved
                            "album": {              # Full enriched album object
                                "id": str,
                                "name": str,
                                "uri": str,
                                "total_tracks": int,
                                # ... all album fields
                            }
                        },
                        # ... more items
                    ],
                    "previous": str | None,         # URL for previous page (None if first page)
                    "next": str | None              # URL for next page (None if last page)
                }
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
                
        Note:
            - Only returns albums that exist in self.albums (orphaned IDs are skipped)
            - Uses user's last_active_date as added_at fallback timestamp
            - Real Spotify API tracks actual save timestamps per album
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> page1 = api.get_saved_albums(limit=10, offset=0)
            >>> print(f"Saved {page1['total']} albums total")
            >>> for item in page1['items']:
            ...     print(f"- {item['album']['name']} (added {item['added_at']})")
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
        Saves one or more albums to the current user's 'Your Music' library.
        
        Adds albums to the user's saved albums collection. Albums already saved are ignored
        (no duplicates). Corresponds to Spotify's PUT /v1/me/albums endpoint.

        Args:
            album_ids (List[str]): List of Spotify album IDs to save.
                Maximum: 50 albums per request.
                Example: ["album-uuid-1", "album-uuid-2"]
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If more than 50 album IDs provided
                Error message: "Maximum 50 albums can be saved at once"
            Exception: If any album_id doesn't exist in self.albums
                Error message: "Album {album_id} not found"
                
        Side Effects:
            - Adds each album_id to user's liked_albums list (if not already present)
            - Creates liked_albums list if it doesn't exist
            - Duplicate album IDs are silently ignored (idempotent operation)
            
        Note:
            - Validates all albums exist before adding any (atomic operation)
            - Real Spotify API is idempotent - saving an already-saved album is not an error
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> api.save_albums(["album-id-1", "album-id-2"])
            >>> # Albums now appear in saved albums library
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if len(album_ids) > 50:
            raise Exception("Maximum 50 albums can be saved at once")
        
        for album_id in album_ids:
            if album_id not in self.albums:
                raise Exception(f"Album {album_id} not found")
            
            if album_id not in user_data.get("liked_albums", []):
                user_data.setdefault("liked_albums", []).append(album_id)

    def remove_saved_albums(self, album_ids: List[str]) -> None:
        """
        Removes one or more albums from the current user's 'Your Music' library.
        
        Deletes albums from the user's saved albums collection. Albums not currently saved
        are silently ignored. Corresponds to Spotify's DELETE /v1/me/albums endpoint.

        Args:
            album_ids (List[str]): List of Spotify album IDs to remove.
                Maximum: 50 albums per request.
                Example: ["album-uuid-1", "album-uuid-2"]
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If more than 50 album IDs provided
                Error message: "Maximum 50 albums can be removed at once"
                
        Side Effects:
            - Removes each album_id from user's liked_albums list (if present)
            - Album IDs not in liked_albums are silently ignored (idempotent operation)
            
        Note:
            - Does NOT validate whether album IDs exist in self.albums
            - Real Spotify API is idempotent - removing an unsaved album is not an error
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> api.remove_saved_albums(["album-id-1", "album-id-2"])
            >>> # Albums no longer appear in saved albums library
        """
        self._ensure_authenticated()
        user_data = self._get_current_user_data()
        
        if not user_data:
            raise Exception("User not found")
        
        if len(album_ids) > 50:
            raise Exception("Maximum 50 albums can be removed at once")
        
        for album_id in album_ids:
            if album_id in user_data.get("liked_albums", []):
                user_data["liked_albums"].remove(album_id)

    def follow_artists(self, artist_ids: List[str]) -> None:
        """
        Adds the current user as a follower of one or more artists.
        
        Follows artists to receive updates about new releases and concerts. Artists already
        followed are ignored (no duplicates). Corresponds to Spotify's PUT /v1/me/following endpoint.

        Args:
            artist_ids (List[str]): List of Spotify artist IDs to follow.
                Maximum: 50 artists per request.
                Example: ["artist-uuid-1", "artist-uuid-2"]
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If more than 50 artist IDs provided
                Error message: "Maximum 50 artists can be followed at once"
            Exception: If any artist_id doesn't exist in self.artists
                Error message: "Artist {artist_id} not found"
                
        Side Effects:
            - Adds each artist_id to user's following_artists list (if not already present)
            - Creates following_artists list if it doesn't exist
            - Duplicate artist IDs are silently ignored (idempotent operation)
            
        Note:
            - Validates all artists exist before adding any (atomic operation)
            - Real Spotify API is idempotent - following an already-followed artist is not an error
            - Following artists affects personalized recommendations and "Release Radar" playlist
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> api.follow_artists(["artist-id-1", "artist-id-2"])
            >>> # User now follows these artists
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
        Removes the current user as a follower of one or more artists.
        
        Unfollows artists to stop receiving updates. Artists not currently followed
        are silently ignored. Corresponds to Spotify's DELETE /v1/me/following endpoint.

        Args:
            artist_ids (List[str]): List of Spotify artist IDs to unfollow.
                Maximum: 50 artists per request.
                Example: ["artist-uuid-1", "artist-uuid-2"]
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If more than 50 artist IDs provided
                Error message: "Maximum 50 artists can be unfollowed at once"
                
        Side Effects:
            - Removes each artist_id from user's following_artists list (if present)
            - Artist IDs not in following_artists are silently ignored (idempotent operation)
            
        Note:
            - Does NOT validate whether artist IDs exist in self.artists
            - Real Spotify API is idempotent - unfollowing a non-followed artist is not an error
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> api.unfollow_artists(["artist-id-1", "artist-id-2"])
            >>> # User no longer follows these artists
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
        Retrieves the current user's followed artists with cursor-based pagination.
        
        Returns artists the user follows for receiving new release notifications.
        Uses cursor-based pagination (different from offset-based). Corresponds to
        Spotify's GET /v1/me/following endpoint with type=artist.

        Args:
            limit (int): Maximum number of artists to return.
                Valid range: 1-50. Default: 20
        
        Returns:
            Dict[str, Any]: Cursor-based paging wrapper with structure:
                {
                    "artists": {                    # Artist collection object
                        "href": str,                # Current request URL
                        "limit": int,               # Page size used
                        "total": int,               # Total followed artists count
                        "items": [                  # Array of enriched artist objects
                            {
                                "id": str,
                                "name": str,
                                "uri": str,
                                "genres": List[str],
                                "popularity": int,
                                "followers": {...},
                                # ... all artist fields
                            },
                            # ... more artists
                        ],
                        "next": str | None,         # Cursor URL for next page (simplified)
                        "previous": str | None,     # Cursor URL for previous page (simplified)
                        "cursors": {                # Cursor tokens for pagination
                            "after": str | None,    # Cursor after last item
                            "before": str | None    # Cursor before first item
                        }
                    }
                }
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
                
        Note:
            - Only returns artists that exist in self.artists (orphaned IDs are skipped)
            - Real Spotify API uses cursor-based pagination for following endpoints
            - This simplified version uses limit-only pagination (no cursor support)
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> result = api.get_followed_artists(limit=10)
            >>> print(f"Following {result['artists']['total']} artists")
            >>> for artist in result['artists']['items']:
            ...     print(f"- {artist['name']}")
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
        Creates a new empty playlist for a Spotify user.
        
        Creates a playlist owned by the authenticated user. In real Spotify API, you can only
        create playlists for yourself. Returns the enriched playlist object with all Spotify
        standard fields. Corresponds to Spotify's POST /v1/users/{user_id}/playlists endpoint.

        Args:
            user_id (str): The user's Spotify user ID (UUID). Must match authenticated user's ID.
            name (str): Name for the new playlist.
                Example: "My Workout Mix"
            description (Optional[str]): Optional description text for the playlist.
                Example: "Songs to get pumped up"
                Default: None
            public (bool): Whether the playlist is public (visible to others) or private.
                Default: True (public)
        
        Returns:
            Dict[str, Any]: Enriched playlist object with structure:
                {
                    "id": str,                      # Generated playlist UUID
                    "name": str,                    # Playlist name
                    "uri": str,                     # Spotify URI
                    "href": str,                    # API endpoint URL
                    "external_urls": {...},         # External links
                    "user_id": str,                 # Owner's user UUID
                    "description": str | None,      # Description text
                    "public": bool,                 # Public/private status
                    "tracks": {                     # Empty tracks object
                        "href": str,
                        "total": 0,
                        "items": []
                    },
                    "created_at": str,              # ISO 8601 creation timestamp
                    "updated_at": str,              # ISO 8601 update timestamp
                    "collaborative": bool,          # Collaborative flag (default False)
                    "snapshot_id": str,             # Version snapshot ID
                    # ... other Spotify standard fields
                }
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If user_id doesn't match authenticated user
                Error message: "Can only create playlists for the authenticated user"
                
        Side Effects:
            - Adds new playlist to self.playlists dictionary
            - Adds playlist_id to user's liked_playlists list
            - Sets created_at and updated_at timestamps to current time
            
        Note:
            - Playlist starts empty; use add_items_to_playlist to add tracks
            - Real Spotify API enforces that you can only create playlists for yourself
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> profile = api.get_current_user_profile()
            >>> playlist = api.create_playlist(
            ...     user_id=profile['id'],
            ...     name="Summer Hits",
            ...     description="Best songs for summer",
            ...     public=True
            ... )
            >>> print(f"Created: {playlist['name']} ({playlist['id']})")
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
        Retrieves detailed information about a specific playlist.
        
        Returns full playlist object including metadata and track list. Public playlists
        can be accessed without authentication. Private playlists require authentication
        and ownership. Corresponds to Spotify's GET /v1/playlists/{playlist_id} endpoint.

        Args:
            playlist_id (str): The Spotify playlist ID (UUID)
        
        Returns:
            Dict[str, Any]: Enriched playlist object with full details including tracks
        
        Raises:
            Exception: If playlist_id doesn't exist in self.playlists
                Error message: "Playlist {playlist_id} not found"
            Exception: If playlist is private and user is not authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If playlist is private and authenticated user is not the owner
                Error message: "Access denied to private playlist"
                
        Note:
            - Public playlists can be accessed by anyone (no authentication required)
            - Private playlists require authentication and ownership verification
            - Returns enriched playlist with Spotify standard fields
            
        Example:
            >>> api = SpotifyApis()
            >>> # Public playlist - no auth needed
            >>> public_pl = api.get_playlist("public-playlist-id")
            >>> 
            >>> # Private playlist - auth required
            >>> api.authenticate("token_alice@example.com")
            >>> private_pl = api.get_playlist("private-playlist-id")
            >>> print(f"{private_pl['name']}: {private_pl['tracks']['total']} tracks")
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
        Changes a playlist's name, description, and/or public/private state.
        
        Updates playlist metadata. Only the playlist owner can modify these details.
        Only provided fields are updated; omitted fields remain unchanged. Corresponds
        to Spotify's PUT /v1/playlists/{playlist_id} endpoint.

        Args:
            playlist_id (str): The Spotify playlist ID (UUID)
            name (Optional[str]): New name for the playlist. If None, keeps existing name.
                Example: "Updated Playlist Name"
            description (Optional[str]): New description. If None, keeps existing.
                Example: "A refreshed description"
            public (Optional[bool]): New visibility setting. If None, keeps existing.
                True = public, False = private
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If playlist_id doesn't exist in self.playlists
                Error message: "Playlist {playlist_id} not found"
            Exception: If authenticated user is not the playlist owner
                Error message: "Can only modify your own playlists"
                
        Side Effects:
            - Updates specified fields in self.playlists[playlist_id]
            - Updates updated_at timestamp to current time
            - Changes persist for subsequent API calls
            
        Note:
            - Only playlist owner can modify details
            - Real Spotify API also allows changing collaborative status
            - Snapshot ID is not changed by this operation (only track changes update snapshot)
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> api.change_playlist_details(
            ...     playlist_id="my-playlist-id",
            ...     name="New Name",
            ...     public=False  # Make private
            ... )
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
        Adds one or more tracks to a user's playlist at a specified position or at the end.
        
        Inserts tracks into the playlist. Tracks can be added at a specific position or appended
        to the end. Updates the playlist's snapshot ID to reflect the change. Corresponds to
        Spotify's POST /v1/playlists/{playlist_id}/tracks endpoint.

        Args:
            playlist_id (str): The Spotify playlist ID (UUID)
            track_uris (List[str]): List of Spotify track URIs in format "spotify:track:{id}".
                Maximum: 100 tracks per request.
                Example: ["spotify:track:abc-123", "spotify:track:def-456"]
            position (Optional[int]): Zero-based position to insert tracks.
                If None, tracks are appended to the end.
                Example: position=0 inserts at beginning, position=5 inserts after 5th track
        
        Returns:
            Dict[str, str]: Snapshot object containing:
                {
                    "snapshot_id": str  # New version identifier for the playlist
                }
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If playlist_id doesn't exist in self.playlists
                Error message: "Playlist {playlist_id} not found"
            Exception: If authenticated user is not the playlist owner
                Error message: "Can only modify your own playlists"
            Exception: If more than 100 track URIs provided
                Error message: "Maximum 100 tracks can be added at once"
            Exception: If any URI doesn't start with "spotify:track:"
                Error message: "Invalid track URI format: {uri}"
            Exception: If extracted track_id doesn't exist in self.tracks
                Error message: "Track {track_id} not found"
                
        Side Effects:
            - Adds track IDs to playlist's tracks list
            - If position provided, inserts at that index; otherwise appends
            - Updates playlist's updated_at timestamp
            - Generates and updates playlist's snapshot_id
            - Changes persist for subsequent API calls
            
        Note:
            - URIs must be in Spotify URI format: "spotify:track:{id}"
            - All track IDs are validated before any are added (atomic operation)
            - Duplicate tracks are allowed (same track can appear multiple times)
            - Snapshot ID changes with each modification for optimistic concurrency control
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> result = api.add_items_to_playlist(
            ...     playlist_id="my-playlist-id",
            ...     track_uris=["spotify:track:t1", "spotify:track:t2"],
            ...     position=0  # Add at beginning
            ... )
            >>> print(f"New snapshot: {result['snapshot_id']}")
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
        Removes one or more tracks from a user's playlist.
        
        Deletes the first occurrence of each specified track from the playlist.
        Updates the playlist's snapshot ID to reflect the change. Corresponds to
        Spotify's DELETE /v1/playlists/{playlist_id}/tracks endpoint.

        Args:
            playlist_id (str): The Spotify playlist ID (UUID)
            track_uris (List[str]): List of Spotify track URIs in format "spotify:track:{id}".
                Maximum: 100 tracks per request.
                Example: ["spotify:track:abc-123", "spotify:track:def-456"]
        
        Returns:
            Dict[str, str]: Snapshot object containing:
                {
                    "snapshot_id": str  # New version identifier for the playlist
                }
        
        Raises:
            Exception: If no user is authenticated
                Error message: "No access token provided. Authentication required."
            Exception: If authenticated user doesn't exist in users dictionary
                Error message: "User not found"
            Exception: If playlist_id doesn't exist in self.playlists
                Error message: "Playlist {playlist_id} not found"
            Exception: If authenticated user is not the playlist owner
                Error message: "Can only modify your own playlists"
            Exception: If more than 100 track URIs provided
                Error message: "Maximum 100 tracks can be removed at once"
            Exception: If any URI doesn't start with "spotify:track:"
                Error message: "Invalid track URI format: {uri}"
                
        Side Effects:
            - Removes first occurrence of each track ID from playlist's tracks list
            - Track URIs not in playlist are silently ignored (idempotent)
            - Updates playlist's updated_at timestamp
            - Generates and updates playlist's snapshot_id
            - Changes persist for subsequent API calls
            
        Note:
            - URIs must be in Spotify URI format: "spotify:track:{id}"
            - Only removes first occurrence of each track (if track appears multiple times)
            - Does NOT validate whether track IDs exist in self.tracks
            - Real Spotify API supports position-based removal for precision
            - Snapshot ID changes with each modification
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> result = api.remove_items_from_playlist(
            ...     playlist_id="my-playlist-id",
            ...     track_uris=["spotify:track:t1", "spotify:track:t2"]
            ... )
            >>> print(f"New snapshot: {result['snapshot_id']}")
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
            if track_id in current_tracks:
                current_tracks.remove(track_id)
        
        playlist["tracks"] = current_tracks
        playlist["updated_at"] = datetime.datetime.now().isoformat() + "Z"
        new_snapshot_id = self._generate_unique_id()
        playlist["snapshot_id"] = new_snapshot_id
        
        return {"snapshot_id": new_snapshot_id}

    def get_track(self, track_id: str) -> Dict[str, Any]:
        """
        Retrieves Spotify catalog information for a single track.
        
        Returns detailed track information including metadata, artists, album, duration,
        and availability. Corresponds to Spotify's GET /v1/tracks/{id} endpoint.

        Args:
            track_id (str): The Spotify track ID (UUID)
        
        Returns:
            Dict[str, Any]: Enriched track object with full Spotify standard fields
        
        Raises:
            Exception: If track_id doesn't exist in self.tracks
                Error message: "Track {track_id} not found"
                
        Note:
            - Does not require authentication (public catalog access)
            - Returns enriched track with all Spotify standard fields
            
        Example:
            >>> api = SpotifyApis()
            >>> track = api.get_track("track-id-123")
            >>> print(f"{track['name']} - {track['duration_ms']}ms")
        """
        if track_id not in self.tracks:
            raise Exception(f"Track {track_id} not found")
        
        return self._enrich_track(self.tracks[track_id])

    def get_several_tracks(self, track_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves Spotify catalog information for multiple tracks in a single request.
        
        Batch endpoint for efficiently fetching multiple tracks. Returns tracks in the same
        order as requested. Non-existent track IDs return None in the array. Corresponds
        to Spotify's GET /v1/tracks endpoint with ids parameter.

        Args:
            track_ids (List[str]): List of Spotify track IDs to retrieve.
                Maximum: 50 tracks per request.
                Example: ["track-id-1", "track-id-2", "track-id-3"]
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Object containing tracks array:
                {
                    "tracks": [         # Array matching input order
                        {...},          # Track object or None if not found
                        {...},
                        None,           # Track ID didn't exist
                        {...}
                    ]
                }
        
        Raises:
            Exception: If more than 50 track IDs provided
                Error message: "Maximum 50 tracks can be requested at once"
                
        Note:
            - Does not require authentication (public catalog access)
            - Returns None for non-existent tracks (doesn't raise exception)
            - Maintains input order in response
            - More efficient than multiple single track requests
            
        Example:
            >>> api = SpotifyApis()
            >>> result = api.get_several_tracks(["t1", "t2", "invalid-id", "t3"])
            >>> for track in result['tracks']:
            ...     if track:
            ...         print(track['name'])
            ...     else:
            ...         print("Track not found")
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
        Retrieves Spotify catalog information for a single album.
        
        Returns detailed album information including metadata, artists, release date, track list,
        and availability. Corresponds to Spotify's GET /v1/albums/{id} endpoint.

        Args:
            album_id (str): The Spotify album ID (UUID)
        
        Returns:
            Dict[str, Any]: Enriched album object with full Spotify standard fields
        
        Raises:
            Exception: If album_id doesn't exist in self.albums
                Error message: "Album {album_id} not found"
                
        Note:
            - Does not require authentication (public catalog access)
            - Returns enriched album with all Spotify standard fields
            
        Example:
            >>> api = SpotifyApis()
            >>> album = api.get_album("album-id-456")
            >>> print(f"{album['name']} by {album.get('artist', 'Unknown')}")
            >>> print(f"Released: {album['release_date']}")
        """
        if album_id not in self.albums:
            raise Exception(f"Album {album_id} not found")
        
        return self._enrich_album(self.albums[album_id])

    def get_several_albums(self, album_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves Spotify catalog information for multiple albums in a single request.
        
        Batch endpoint for efficiently fetching multiple albums. Returns albums in the same
        order as requested. Non-existent album IDs return None in the array. Corresponds
        to Spotify's GET /v1/albums endpoint with ids parameter.

        Args:
            album_ids (List[str]): List of Spotify album IDs to retrieve.
                Maximum: 20 albums per request (note: different limit than tracks).
                Example: ["album-id-1", "album-id-2", "album-id-3"]
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Object containing albums array:
                {
                    "albums": [         # Array matching input order
                        {...},          # Album object or None if not found
                        {...},
                        None,           # Album ID didn't exist
                        {...}
                    ]
                }
        
        Raises:
            Exception: If more than 20 album IDs provided
                Error message: "Maximum 20 albums can be requested at once"
                
        Note:
            - Does not require authentication (public catalog access)
            - Returns None for non-existent albums (doesn't raise exception)
            - Maintains input order in response
            - Lower limit (20) than tracks endpoint (50)
            
        Example:
            >>> api = SpotifyApis()
            >>> result = api.get_several_albums(["a1", "a2", "invalid-id"])
            >>> for album in result['albums']:
            ...     if album:
            ...         print(f"{album['name']} ({album['total_tracks']} tracks)")
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
        Retrieves Spotify catalog information for a single artist.
        
        Returns detailed artist information including name, genres, popularity, follower count,
        and profile images. Corresponds to Spotify's GET /v1/artists/{id} endpoint.

        Args:
            artist_id (str): The Spotify artist ID (UUID)
        
        Returns:
            Dict[str, Any]: Enriched artist object with full Spotify standard fields
        
        Raises:
            Exception: If artist_id doesn't exist in self.artists
                Error message: "Artist {artist_id} not found"
                
        Note:
            - Does not require authentication (public catalog access)
            - Returns enriched artist with all Spotify standard fields
            
        Example:
            >>> api = SpotifyApis()
            >>> artist = api.get_artist("artist-id-789")
            >>> print(f"{artist['name']}")
            >>> print(f"Genres: {', '.join(artist['genres'])}")
            >>> print(f"Popularity: {artist['popularity']}/100")
        """
        if artist_id not in self.artists:
            raise Exception(f"Artist {artist_id} not found")
        
        return self._enrich_artist(self.artists[artist_id])

    def get_several_artists(self, artist_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves Spotify catalog information for multiple artists in a single request.
        
        Batch endpoint for efficiently fetching multiple artists. Returns artists in the same
        order as requested. Non-existent artist IDs return None in the array. Corresponds
        to Spotify's GET /v1/artists endpoint with ids parameter.

        Args:
            artist_ids (List[str]): List of Spotify artist IDs to retrieve.
                Maximum: 50 artists per request.
                Example: ["artist-id-1", "artist-id-2", "artist-id-3"]
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Object containing artists array:
                {
                    "artists": [        # Array matching input order
                        {...},          # Artist object or None if not found
                        {...},
                        None,           # Artist ID didn't exist
                        {...}
                    ]
                }
        
        Raises:
            Exception: If more than 50 artist IDs provided
                Error message: "Maximum 50 artists can be requested at once"
                
        Note:
            - Does not require authentication (public catalog access)
            - Returns None for non-existent artists (doesn't raise exception)
            - Maintains input order in response
            
        Example:
            >>> api = SpotifyApis()
            >>> result = api.get_several_artists(["art1", "art2", "invalid"])
            >>> for artist in result['artists']:
            ...     if artist:
            ...         print(f"{artist['name']} - {artist['popularity']} popularity")
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
        Searches Spotify catalog for items matching a keyword string across multiple content types.
        
        Performs case-insensitive substring search on names/titles across specified item types.
        Returns paginated results for each requested type. Corresponds to Spotify's
        GET /v1/search endpoint.

        Args:
            q (str): Search query keywords (case-insensitive substring match).
                Example: "love" matches "Lovely", "I Love You", "beloved"
            type (List[str]): Item types to search across. Valid values:
                - "track": Search track names
                - "album": Search album names
                - "artist": Search artist names
                - "playlist": Search playlist names (public playlists only)
                Example: ["track", "album"] searches both tracks and albums
            limit (int): Maximum number of results to return per type.
                Valid range: 1-50. Default: 20
            offset (int): Index of first result to return (for pagination).
                Valid range: 0-1000. Default: 0
        
        Returns:
            Dict[str, Any]: Search results object with paging objects for each requested type:
                {
                    "tracks": {              # If "track" in type
                        "href": str,         # Search URL
                        "limit": int,
                        "offset": int,
                        "total": int,        # Total matching tracks
                        "items": [...],      # Array of enriched track objects
                        "previous": str | None,
                        "next": str | None
                    },
                    "albums": {...},         # If "album" in type
                    "artists": {...},        # If "artist" in type
                    "playlists": {...}       # If "playlist" in type
                }
                Only includes keys for requested types.
        
        Raises:
            Exception: If limit > 50
                Error message: "Maximum limit is 50"
            Exception: If offset > 1000
                Error message: "Maximum offset is 1000"
                
        Note:
            - Does not require authentication (public catalog search)
            - Performs case-insensitive substring match on name/title fields
            - Playlist search only includes public playlists
            - Real Spotify API supports advanced query syntax (field filters, operators, etc.)
            - This simplified version only searches names, not other fields like artist or album
            
        Example:
            >>> api = SpotifyApis()
            >>> results = api.search(
            ...     q="summer",
            ...     type=["track", "playlist"],
            ...     limit=10
            ... )
            >>> print(f"Found {results['tracks']['total']} tracks")
            >>> for track in results['tracks']['items']:
            ...     print(f"- {track['name']}")
            >>> print(f"Found {results['playlists']['total']} playlists")
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
        Resets all simulated data in the API backend to its initial default state.
        
        Reloads the default scenario data, clearing all user modifications including saved tracks,
        playlists, followed artists, etc. Also clears the current authentication session.
        This is a utility function for testing purposes and is not a standard Spotify API endpoint.

        Raises:
            None
                
        Side Effects:
            - Reloads all backend data from DEFAULT_STATE scenario
            - Resets self.users, self.tracks, self.albums, self.artists, self.playlists, self.payment_cards
            - Clears self.access_token (sets to None)
            - Clears self.current_user_id (sets to None)
            - All user modifications (saved tracks, playlists created, etc.) are lost
            - Prints confirmation message to console
            
        Note:
            - This is a test utility method not present in real Spotify API
            - Use for resetting test environments between test runs
            - All in-memory changes are discarded (no persistence)
            
        Example:
            >>> api = SpotifyApis()
            >>> api.authenticate("token_alice@example.com")
            >>> api.save_tracks(["track-1", "track-2"])
            >>> # ... do some testing ...
            >>> api.reset_data()  # Clean slate for next test
            SpotifyApis: All data reset to default state.
            >>> # api.access_token is now None, all saved tracks cleared
        """
        self._load_scenario(DEFAULT_STATE)
        self.access_token = None
        self.current_user_id = None
        print("SpotifyApis: All data reset to default state.")
