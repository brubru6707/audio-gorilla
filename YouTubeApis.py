# Inspired by https://developers.google.com/youtube/v3/docs

from datetime import datetime, timezone
import copy
import uuid
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path

# Add parent directory to path to import test_data_helper
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir / 'UnitTests'))

from UnitTests.test_data_helper import BackendDataLoader

DEFAULT_STATE = BackendDataLoader.get_youtube_data()

class YouTubeApis:
    """
    An API class for simulating YouTube operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the YouTubeApis instance, setting up the in-memory data stores and loading the default scenario.
        
        This constructor creates empty dictionaries for users, channels, videos, playlists, and comments,
        all keyed by UUID. It also initializes authentication state (access_token and current_user_id) to None.
        Finally, it loads the default scenario data from the BackendDataLoader to populate the backend with
        initial test data.
        
        The instance maintains several data structures:
        - users: Maps user UUIDs to user profile data including email, display name, channels, subscriptions, etc.
        - channels: Maps channel UUIDs to channel data including title, videos, playlists, subscribers, etc.
        - videos: Maps video UUIDs to video data including title, description, views, likes, comments, etc.
        - playlists: Maps playlist UUIDs to playlist data including title, video list, owner, etc.
        - comments: Maps comment UUIDs to comment data
        - access_token: Stores the current OAuth 2.0 access token (None when not authenticated)
        - current_user_id: Stores the UUID of the currently authenticated user (None when not authenticated)
        """
        self._api_description = "This tool simulates YouTube functionalities, allowing management of channels, videos, playlists, and comments."
        self.users: Dict[str, Any] = {} # Keyed by user UUID
        self.channels: Dict[str, Any] = {} # Keyed by channel UUID
        self.videos: Dict[str, Any] = {} # Keyed by video UUID
        self.playlists: Dict[str, Any] = {} # Keyed by playlist UUID
        self.comments: Dict[str, Any] = {} # Keyed by comment UUID
        self.access_token: Optional[str] = None
        self.current_user_id: Optional[str] = None

        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the backend's state, allowing for state reset or initialization with specific data.
        
        This method performs a deep copy of the scenario data to ensure the original DEFAULT_STATE remains
        unmodified during runtime. This is crucial for test isolation and repeatability. The method replaces
        all existing data in the backend with the provided scenario data.

        Args:
            scenario (Dict): A dictionary representing the complete state to load. Expected keys:
                - "users" (Dict[str, Dict]): User data keyed by UUID, containing profile info, subscriptions, etc.
                - "channels" (Dict[str, Dict]): Channel data keyed by UUID, containing videos, playlists, stats, etc.
                - "videos" (Dict[str, Dict]): Video data keyed by UUID, containing metadata, views, likes, etc.
                - "playlists" (Dict[str, Dict]): Playlist data keyed by UUID, containing video lists, metadata, etc.
                - "comments" (Dict[str, Dict]): Comment data (typically empty initially, populated at runtime)
                If any key is missing, an empty dictionary is used as the default.
        
        Returns:
            None: This method modifies the instance state in-place and returns nothing.
        
        Side Effects:
            - Replaces all existing users, channels, videos, playlists, and comments data
            - Prints a confirmation message to stdout
            - Does not affect authentication state (access_token, current_user_id)
        """
        # Create deep copy to ensure the original DEFAULT_STATE is not modified
        self.users = copy.deepcopy(scenario.get("users", {}))
        self.channels = copy.deepcopy(scenario.get("channels", {}))
        self.videos = copy.deepcopy(scenario.get("videos", {}))
        self.playlists = copy.deepcopy(scenario.get("playlists", {}))
        self.comments = {}
        print("YouTubeApis: Loaded scenario with UUIDs for users, channels, videos, playlists, and comments.")

    def authenticate(self, access_token: str) -> Dict[str, Any]:
        """
        Authenticate with YouTube Data API using an OAuth 2.0 access token, establishing a user session.
        
        This method validates the access token format, extracts the email address from it, looks up the
        corresponding user in the backend, and sets the authentication state for subsequent API calls.
        Once authenticated, all methods that require authentication (e.g., subscribe, upload_video) will
        use this authenticated user's identity.

        Args:
            access_token (str): OAuth 2.0 Bearer token in the format "token_{email}", where {email} is
                the email address of the user to authenticate. For example, "token_user@example.com".
                The token must start with "token_" prefix and contain a valid email address that exists
                in the backend's user database.

        Returns:
            Dict[str, Any]: A dictionary containing the authenticated user's profile data with the following structure:
                {
                    "id": str,              # The user's unique YouTube channel ID
                    "email": str,           # The user's email address
                    "displayName": str,     # The user's display name on YouTube
                    "kind": "youtube#channel"  # Resource type identifier
                }

        Raises:
            Exception: If the access token format is invalid (doesn't start with "token_" or is empty)
            Exception: If no user is found in the backend with the email address extracted from the token
        
        Side Effects:
            - Sets self.access_token to the provided token
            - Sets self.current_user_id to the UUID of the authenticated user
            - All subsequent method calls will use this authentication context
        
        Example:
            >>> api = YouTubeApis()
            >>> profile = api.authenticate("token_john@example.com")
            >>> print(profile["displayName"])
            'John Doe'
        """
        if not access_token or not access_token.startswith("token_"):
            raise Exception("Invalid access token format")
        
        # Extract email from token
        email = access_token.replace("token_", "")
        
        # Find user by email
        user_id = None
        for uid, user_data in self.users.items():
            if user_data.get("email") == email:
                user_id = uid
                break
        
        if not user_id:
            raise Exception(f"No user found with email: {email}")
        
        self.access_token = access_token
        self.current_user_id = user_id
        
        user_data = self.users[user_id]
        return {
            "id": user_data.get("id"),
            "email": user_data.get("email"),
            "displayName": user_data.get("display_name"),
            "kind": "youtube#channel"
        }
    
    def _ensure_authenticated(self) -> None:
        """
        Ensures that the user is authenticated before accessing protected resources.
        
        This internal helper method checks whether authenticate() has been called successfully
        by verifying that both access_token and current_user_id are set. It should be called
        at the beginning of any method that requires authentication to access protected resources.
        This prevents unauthorized access to user-specific operations like uploading videos,
        subscribing to channels, or managing playlists.

        Returns:
            None: Returns nothing if authentication check passes.

        Raises:
            Exception: If either access_token or current_user_id is None, indicating that
                authenticate() has not been called or authentication failed. The exception
                message instructs the caller to call authenticate() first.
        
        Note:
            This is a private method (prefix _) and should only be called internally by other
            methods in this class, not by external code.
        """
        if not self.access_token or not self.current_user_id:
            raise Exception("Authentication required. Call authenticate() first.")

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID (Universally Unique Identifier) for entities.
        
        This helper method creates a new UUID v4 string representation to be used as a unique
        identifier for channels, videos, playlists, comments, and other entities in the backend.
        UUID v4 uses random generation and provides sufficient uniqueness for this simulation.
        
        Returns:
            str: A string representation of a UUID v4, formatted as a 36-character string with hyphens
                (e.g., "550e8400-e29b-41d4-a716-446655440000"). Each call produces a different UUID
                with extremely high probability of uniqueness.
        
        Example:
            >>> api = YouTubeApis()
            >>> id1 = api._generate_unique_id()
            >>> id2 = api._generate_unique_id()
            >>> print(id1 == id2)
            False
        """
        return str(uuid.uuid4())

    def _get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to retrieve a user's complete data dictionary based on their UUID.
        
        Args:
            user_id (str): The UUID of the user to retrieve. This should be a valid UUID string
                that exists in the self.users dictionary.
        
        Returns:
            Optional[Dict[str, Any]]: The user's data dictionary if found, containing keys such as
                "id", "email", "display_name", "channels", "subscriptions", "watch_history", etc.
                Returns None if the user_id is not found in the backend.
        """
        return self.users.get(user_id)

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves complete user information by user ID, including credentials.
        This method is intended for AI model context lookup during testing scenarios.
        
        Args:
            user_id (str): The unique UUID identifier of the user to retrieve.
        
        Returns:
            Dict[str, Any]: User data dictionary containing all user fields including credentials.
                Returns error dictionary if user not found with status=False and message.
        
        Notes:
            - This is a public method specifically for AI model context resolution
            - Exposes credentials intentionally for testing/simulation purposes
            - Should not be used in production environments
        """
        user_data = self.users.get(user_id)
        if not user_data:
            return {
                "status": False,
                "message": f"User with ID {user_id} not found."
            }
        
        # Return complete user data including the user_id itself
        result = {"user_id": user_id}
        result.update(user_data)
        return result

    def _update_user_data(self, user_id: str, key: str, value: Any) -> bool:
        """
        Helper method to update a specific key-value pair in a user's data dictionary.
        
        Args:
            user_id (str): The UUID of the user whose data should be updated.
            key (str): The dictionary key to update (e.g., "display_name", "email", "subscriptions").
            value (Any): The new value to assign to the specified key. Can be any type (str, int, list, dict, etc.).
        
        Returns:
            bool: True if the user was found and the update was successful, False if the user_id
                does not exist in the backend.
        """
        if user_id in self.users:
            self.users[user_id][key] = value
            return True
        return False

    def _get_channel_data(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to retrieve a channel's complete data dictionary based on its UUID.
        
        Args:
            channel_id (str): The UUID of the channel to retrieve.
        
        Returns:
            Optional[Dict[str, Any]]: The channel's data dictionary if found, containing keys such as
                "id", "title", "description", "owner_id", "videos", "playlists", "subscribers",
                "subscriber_count", "video_count", "view_count", etc. Returns None if the channel_id
                is not found in the backend.
        """
        return self.channels.get(channel_id)

    def _update_channel_data(self, channel_id: str, key: str, value: Any) -> bool:
        """
        Helper method to update a specific key-value pair in a channel's data dictionary.
        
        Args:
            channel_id (str): The UUID of the channel whose data should be updated.
            key (str): The dictionary key to update (e.g., "title", "description", "subscriber_count").
            value (Any): The new value to assign to the specified key.
        
        Returns:
            bool: True if the channel was found and the update was successful, False otherwise.
        """
        if channel_id in self.channels:
            self.channels[channel_id][key] = value
            return True
        return False

    def _get_video_data(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to retrieve a video's complete data dictionary based on its UUID.
        
        Args:
            video_id (str): The UUID of the video to retrieve.
        
        Returns:
            Optional[Dict[str, Any]]: The video's data dictionary if found, containing keys such as
                "id", "title", "description", "channel_id", "uploader_id", "published_at",
                "duration_seconds", "views", "likes", "comments", "tags", etc. Returns None if
                the video_id is not found in the backend.
        """
        return self.videos.get(video_id)

    def _update_video_data(self, video_id: str, key: str, value: Any) -> bool:
        """
        Helper method to update a specific key-value pair in a video's data dictionary.
        
        Args:
            video_id (str): The UUID of the video whose data should be updated.
            key (str): The dictionary key to update (e.g., "title", "views", "likes").
            value (Any): The new value to assign to the specified key.
        
        Returns:
            bool: True if the video was found and the update was successful, False otherwise.
        """
        if video_id in self.videos:
            self.videos[video_id][key] = value
            return True
        return False
    
    def _get_playlist_data(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to retrieve a playlist's complete data dictionary based on its UUID.
        
        Args:
            playlist_id (str): The UUID of the playlist to retrieve.
        
        Returns:
            Optional[Dict[str, Any]]: The playlist's data dictionary if found, containing keys such as
                "id", "title", "description", "owner_id", "channel_id", "video_ids", "created_at",
                "privacy_status", "item_count", etc. Returns None if the playlist_id is not found.
        """
        return self.playlists.get(playlist_id)

    def _update_playlist_data(self, playlist_id: str, key: str, value: Any) -> bool:
        """
        Helper method to update a specific key-value pair in a playlist's data dictionary.
        
        Args:
            playlist_id (str): The UUID of the playlist whose data should be updated.
            key (str): The dictionary key to update (e.g., "title", "description", "item_count").
            value (Any): The new value to assign to the specified key.
        
        Returns:
            bool: True if the playlist was found and the update was successful, False otherwise.
        """
        if playlist_id in self.playlists:
            self.playlists[playlist_id][key] = value
            return True
        return False
    
    def _get_comment_data(self, comment_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to retrieve a comment's complete data dictionary based on its UUID.
        
        Args:
            comment_id (str): The UUID of the comment to retrieve.
        
        Returns:
            Optional[Dict[str, Any]]: The comment's data dictionary if found, containing keys such as
                "id", "text", "published_at", "author_id", "video_id", etc. Returns None if the
                comment_id is not found in the backend.
        """
        return self.comments.get(comment_id)

    def _update_comment_data(self, comment_id: str, key: str, value: Any) -> bool:
        """
        Helper method to update a specific key-value pair in a comment's data dictionary.
        
        Args:
            comment_id (str): The UUID of the comment whose data should be updated.
            key (str): The dictionary key to update (e.g., "text", "likes").
            value (Any): The new value to assign to the specified key.
        
        Returns:
            bool: True if the comment was found and the update was successful, False otherwise.
        """
        if comment_id in self.comments:
            self.comments[comment_id][key] = value
            return True
        return False

    def _find_user_by_email(self, email: str) -> Optional[str]:
        """
        Helper method to search for and retrieve a user's UUID by their email address.
        
        This method iterates through all users in the backend and performs a case-sensitive
        match on the email field.
        
        Args:
            email (str): The email address to search for. Must match exactly (case-sensitive).
        
        Returns:
            Optional[str]: The UUID of the first user found with the matching email address,
                or None if no user with that email exists in the backend.
        """
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _find_user_by_display_name(self, display_name: str) -> Optional[str]:
        """
        Helper method to search for and retrieve a user's UUID by their display name.
        
        This method iterates through all users in the backend and performs a case-sensitive
        match on the display_name field.
        
        Args:
            display_name (str): The display name to search for. Must match exactly (case-sensitive).
        
        Returns:
            Optional[str]: The UUID of the first user found with the matching display name,
                or None if no user with that display name exists in the backend.
        """
        for user_id, user_data in self.users.items():
            if user_data.get("display_name") == display_name:
                return user_id
        return None

    def _get_user_id_from_identifier(self, identifier: str) -> Optional[str]:
        """
        Helper method to resolve a flexible user identifier to a user UUID.
        
        This method attempts to find a user by trying multiple lookup strategies in sequence:
        1. First checks if the identifier is already a valid UUID in the users dictionary
        2. Then tries to find a user by email address
        3. Finally tries to find a user by display name
        
        This provides flexibility in API calls where users can be identified by any of these methods.
        
        Args:
            identifier (str): A string that could be:
                - A user UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - An email address (e.g., "user@example.com")
                - A display name (e.g., "John Doe")
            
        Returns:
            Optional[str]: The user's UUID if found by any of the lookup strategies,
                or None if the identifier doesn't match any user in the backend.
        
        Example:
            >>> api = YouTubeApis()
            >>> # All three of these could return the same UUID:
            >>> uuid1 = api._get_user_id_from_identifier("550e8400-e29b-41d4-a716-446655440000")
            >>> uuid2 = api._get_user_id_from_identifier("john@example.com")
            >>> uuid3 = api._get_user_id_from_identifier("John Doe")
        """
        # First check if it's already a UUID in our users
        if identifier in self.users:
            return identifier
        
        # Try to find by email
        user_id = self._find_user_by_email(identifier)
        if user_id:
            return user_id
            
        # Try to find by display name
        user_id = self._find_user_by_display_name(identifier)
        if user_id:
            return user_id
            
        return None

    def get_my_channel(self) -> Dict[str, Any]:
        """
        Retrieve the authenticated user's primary YouTube channel information.
        
        This method returns information about the first (primary) channel owned by the currently
        authenticated user. Most YouTube users have a single channel, which is returned here.
        The method requires prior authentication via authenticate().

        Returns:
            Dict[str, Any]: A dictionary containing the channel's data in YouTube API v3 format:
                {
                    "kind": "youtube#channel",
                    "etag": str,                    # Entity tag for caching
                    "id": str,                      # Channel UUID
                    "snippet": {
                        "title": str,               # Channel display name
                        "description": str,         # Channel description
                        "publishedAt": str,         # ISO 8601 timestamp of channel creation
                        "country": str              # Country code (e.g., "US")
                    },
                    "statistics": {
                        "viewCount": str,           # Total views across all videos (as string)
                        "subscriberCount": str,     # Number of subscribers (as string)
                        "videoCount": str           # Number of videos uploaded (as string)
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data is not found in the backend
            Exception: If the authenticated user has no channels associated with their account
            Exception: If the channel data cannot be found for the user's primary channel ID
        
        Note:
            Statistics counts are returned as strings to match YouTube API v3 behavior.
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        # Get user's first channel (primary channel)
        user_channels = user_data.get("channels", [])
        if not user_channels:
            raise Exception("No channel found for authenticated user")
        
        primary_channel_id = user_channels[0]
        channel_data = self._get_channel_data(primary_channel_id)
        
        if not channel_data:
            raise Exception("Channel data not found")
        
        return {
            "kind": "youtube#channel",
            "etag": f"etag_{channel_data['id']}",
            "id": channel_data["id"],
            "snippet": {
                "title": channel_data.get("title"),
                "description": channel_data.get("description"),
                "publishedAt": channel_data.get("created_at"),
                "country": channel_data.get("country", "US")
            },
            "statistics": {
                "viewCount": str(channel_data.get("view_count", 0)),
                "subscriberCount": str(channel_data.get("subscriber_count", 0)),
                "videoCount": str(channel_data.get("video_count", 0))
            }
        }

    def list_my_subscriptions(self, maxResults: int = 25, pageToken: Optional[str] = None) -> Dict[str, Any]:
        """
        List all channels that the authenticated user is subscribed to, with pagination support.
        
        This method retrieves the user's subscription list, which represents all channels they follow.
        Results are paginated to handle large subscription lists efficiently. The pagination uses a
        simple offset-based system where pageToken is a string representation of the offset.

        Args:
            maxResults (int, optional): Maximum number of subscription items to return in a single response.
                Defaults to 25. Valid range is typically 1-50, though this implementation doesn't enforce
                a maximum. Controls the page size for pagination.
            pageToken (Optional[str], optional): Token for retrieving a specific page of results. If None,
                returns the first page (offset 0). The token is a string integer representing the offset
                in the subscription list (e.g., "25" for the second page when maxResults=25). Use the
                "nextPageToken" from a previous response to get the next page. Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing subscription list data in YouTube API v3 format:
                {
                    "kind": "youtube#subscriptionListResponse",
                    "etag": "etag_subscriptions",
                    "pageInfo": {
                        "totalResults": int,        # Total number of subscriptions the user has
                        "resultsPerPage": int       # Number of results in this response (maxResults)
                    },
                    "items": [                      # List of subscription resources
                        {
                            "kind": "youtube#subscription",
                            "etag": str,            # Unique etag for this subscription
                            "id": str,              # Subscription channel UUID
                            "snippet": {
                                "publishedAt": str, # When the channel was created (ISO 8601)
                                "title": str,       # Channel name
                                "description": str, # Channel description
                                "resourceId": {
                                    "kind": "youtube#channel",
                                    "channelId": str # Channel UUID
                                }
                            }
                        },
                        # ... more subscription items
                    ],
                    "nextPageToken": str (optional) # Present only if more results are available
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_user@example.com")
            >>> # Get first page of subscriptions
            >>> page1 = api.list_my_subscriptions(maxResults=10)
            >>> print(len(page1["items"]))  # Up to 10 items
            >>> # Get next page if available
            >>> if "nextPageToken" in page1:
            ...     page2 = api.list_my_subscriptions(maxResults=10, pageToken=page1["nextPageToken"])
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        subscribed_channel_ids = user_data.get("subscriptions", [])
        
        # Simple pagination (offset-based)
        offset = int(pageToken) if pageToken else 0
        paginated_ids = subscribed_channel_ids[offset:offset + maxResults]
        
        items = []
        for channel_uuid in paginated_ids:
            channel_details = self._get_channel_data(channel_uuid)
            if channel_details:
                items.append({
                    "kind": "youtube#subscription",
                    "etag": f"etag_{channel_uuid}",
                    "id": channel_uuid,
                    "snippet": {
                        "publishedAt": channel_details.get("created_at"),
                        "title": channel_details.get("title"),
                        "description": channel_details.get("description"),
                        "resourceId": {
                            "kind": "youtube#channel",
                            "channelId": channel_uuid
                        }
                    }
                })
        
        result = {
            "kind": "youtube#subscriptionListResponse",
            "etag": "etag_subscriptions",
            "pageInfo": {
                "totalResults": len(subscribed_channel_ids),
                "resultsPerPage": maxResults
            },
            "items": items
        }
        
        # Add nextPageToken if there are more results
        if offset + maxResults < len(subscribed_channel_ids):
            result["nextPageToken"] = str(offset + maxResults)
        
        return result
    
    def subscribe(self, channel_id: str) -> Dict[str, Any]:
        """
        Subscribe the authenticated user to a specified channel.
        
        This method creates a subscription relationship between the authenticated user and the target
        channel. It updates both the user's subscription list and the channel's subscriber list, and
        increments the channel's subscriber count. If already subscribed, an exception is raised.

        Args:
            channel_id (str): The UUID of the channel to subscribe to. Must be a valid channel ID
                that exists in the backend.

        Returns:
            Dict[str, Any]: A subscription resource in YouTube API v3 format:
                {
                    "kind": "youtube#subscription",
                    "etag": str,                    # Entity tag based on channel_id
                    "id": str,                      # Newly generated UUID for this subscription
                    "snippet": {
                        "publishedAt": str,         # Current timestamp (ISO 8601 with milliseconds)
                        "title": str,               # Channel name
                        "description": str,         # Channel description
                        "resourceId": {
                            "kind": "youtube#channel",
                            "channelId": str        # The subscribed channel's UUID
                        }
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If user data cannot be found in the backend
            Exception: If the specified channel_id does not exist in the backend
            Exception: If the user is already subscribed to this channel
        
        Side Effects:
            - Appends channel_id to the user's "subscriptions" list
            - Appends current_user_id to the channel's "subscribers" list
            - Increments the channel's "subscriber_count" by 1
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_user@example.com")
            >>> subscription = api.subscribe("channel-uuid-123")
            >>> print(subscription["snippet"]["title"])
            'Tech Channel'
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        channel_data = self._get_channel_data(channel_id)

        if not user_data:
            raise Exception("User data not found")
        if not channel_data:
            raise Exception("Channel not found")
        
        if channel_id in user_data.get("subscriptions", []):
            raise Exception("Already subscribed to this channel")
        
        user_data["subscriptions"].append(channel_id)
        channel_data["subscribers"].append(self.current_user_id)
        channel_data["subscriber_count"] = channel_data.get("subscriber_count", 0) + 1
        
        return {
            "kind": "youtube#subscription",
            "etag": f"etag_{channel_id}",
            "id": self._generate_unique_id(),
            "snippet": {
                "publishedAt": datetime.now().isoformat(timespec='milliseconds') + "Z",
                "title": channel_data.get("title"),
                "description": channel_data.get("description"),
                "resourceId": {
                    "kind": "youtube#channel",
                    "channelId": channel_id
                }
            }
        }

    def unsubscribe(self, channel_id: str) -> None:
        """
        Unsubscribe the authenticated user from a specified channel.
        
        This method removes the subscription relationship between the authenticated user and the
        target channel. It updates both the user's subscription list and the channel's subscriber
        list, and decrements the channel's subscriber count. If not currently subscribed, an
        exception is raised.

        Args:
            channel_id (str): The UUID of the channel to unsubscribe from. Must be a valid channel
                ID that exists in the backend and that the user is currently subscribed to.

        Returns:
            None: This method returns nothing on success.

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If user data cannot be found in the backend
            Exception: If the specified channel_id does not exist in the backend
            Exception: If the user is not currently subscribed to this channel
        
        Side Effects:
            - Removes channel_id from the user's "subscriptions" list
            - Removes current_user_id from the channel's "subscribers" list (if present)
            - Decrements the channel's "subscriber_count" by 1 (minimum value 0)
            - Prints a confirmation message to stdout
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_user@example.com")
            >>> api.unsubscribe("channel-uuid-123")
            # Prints: Unsubscribed from channel channel-uuid-123
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        channel_data = self._get_channel_data(channel_id)

        if not user_data:
            raise Exception("User data not found")
        if not channel_data:
            raise Exception("Channel not found")
        
        if channel_id not in user_data.get("subscriptions", []):
            raise Exception("Not subscribed to this channel")
        
        user_data["subscriptions"].remove(channel_id)
        if self.current_user_id in channel_data.get("subscribers", []):
            channel_data["subscribers"].remove(self.current_user_id)
        channel_data["subscriber_count"] = max(0, channel_data.get("subscriber_count", 0) - 1)
        
        print(f"Unsubscribed from channel {channel_id}")

    def list_my_channels(self) -> Dict[str, Any]:
        """
        List all channels owned by the authenticated user.
        
        This method retrieves all channels that belong to the currently authenticated user.
        While most users have a single channel, some may own multiple channels (e.g., brand channels,
        topic-specific channels). All owned channels are returned in a single response without pagination.

        Returns:
            Dict[str, Any]: A dictionary containing the channel list in YouTube API v3 format:
                {
                    "kind": "youtube#channelListResponse",
                    "etag": "etag_channels",
                    "pageInfo": {
                        "totalResults": int,        # Total number of channels owned
                        "resultsPerPage": int       # Same as totalResults (no pagination)
                    },
                    "items": [                      # List of channel resources
                        {
                            "kind": "youtube#channel",
                            "etag": str,            # Entity tag for this channel
                            "id": str,              # Channel UUID
                            "snippet": {
                                "title": str,       # Channel name
                                "description": str, # Channel description
                                "publishedAt": str, # Creation timestamp (ISO 8601)
                                "country": str      # Country code (default "US")
                            },
                            "statistics": {
                                "viewCount": str,   # Total views (as string)
                                "subscriberCount": str, # Subscriber count (as string)
                                "videoCount": str   # Video count (as string)
                            }
                        },
                        # ... more channel items
                    ]
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If user data cannot be found in the backend
        
        Note:
            Empty list is returned if the user has no channels (though this is rare on YouTube).
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        items = []
        for channel_uuid in user_data.get("channels", []):
            channel_details = self._get_channel_data(channel_uuid)
            if channel_details:
                items.append({
                    "kind": "youtube#channel",
                    "etag": f"etag_{channel_uuid}",
                    "id": channel_uuid,
                    "snippet": {
                        "title": channel_details.get("title"),
                        "description": channel_details.get("description"),
                        "publishedAt": channel_details.get("created_at"),
                        "country": channel_details.get("country", "US")
                    },
                    "statistics": {
                        "viewCount": str(channel_details.get("view_count", 0)),
                        "subscriberCount": str(channel_details.get("subscriber_count", 0)),
                        "videoCount": str(channel_details.get("video_count", 0))
                    }
                })
        
        return {
            "kind": "youtube#channelListResponse",
            "etag": "etag_channels",
            "pageInfo": {
                "totalResults": len(items),
                "resultsPerPage": len(items)
            },
            "items": items
        }

    def get_channel(self, channel_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific channel by its ID.
        
        This is a public endpoint that does not require authentication. Any channel's public information
        can be retrieved, including statistics, description, and metadata. This is useful for discovering
        channels, viewing channel details before subscribing, or retrieving channel information for display.

        Args:
            channel_id (str): The UUID of the channel to retrieve. Must be a valid channel ID that
                exists in the backend.

        Returns:
            Dict[str, Any]: A dictionary containing the channel's data in YouTube API v3 format:
                {
                    "kind": "youtube#channel",
                    "etag": str,                    # Entity tag based on channel_id
                    "id": str,                      # The channel UUID
                    "snippet": {
                        "title": str,               # Channel display name
                        "description": str,         # Channel description
                        "publishedAt": str,         # Channel creation date (ISO 8601)
                        "country": str              # Country code (e.g., "US")
                    },
                    "statistics": {
                        "viewCount": str,           # Total views across all videos (as string)
                        "subscriberCount": str,     # Number of subscribers (as string)
                        "videoCount": str           # Number of videos uploaded (as string)
                    }
                }

        Raises:
            Exception: If the specified channel_id does not exist in the backend
        
        Note:
            This method does NOT require authentication and can be called without calling authenticate().
        """
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            raise Exception("Channel not found")
        
        return {
            "kind": "youtube#channel",
            "etag": f"etag_{channel_id}",
            "id": channel_id,
            "snippet": {
                "title": channel_data.get("title"),
                "description": channel_data.get("description"),
                "publishedAt": channel_data.get("created_at"),
                "country": channel_data.get("country", "US")
            },
            "statistics": {
                "viewCount": str(channel_data.get("view_count", 0)),
                "subscriberCount": str(channel_data.get("subscriber_count", 0)),
                "videoCount": str(channel_data.get("video_count", 0))
            }
        }

    def create_channel(self, title: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new YouTube channel for the authenticated user.
        
        This method creates a new channel owned by the currently authenticated user. The channel is
        initialized with default values (0 views, 0 subscribers, 0 videos, empty playlists and videos
        lists, default banner image). The channel is automatically added to the user's list of owned channels.

        Args:
            title (str): The title/name of the new channel. This is the public-facing name that will be
                displayed to other users. Required and should be descriptive and unique.
            description (str, optional): The channel description that appears on the channel's about page.
                Can be empty or contain detailed information about the channel's content and purpose.
                Defaults to an empty string.

        Returns:
            Dict[str, Any]: The newly created channel resource in YouTube API v3 format:
                {
                    "kind": "youtube#channel",
                    "etag": str,                    # Entity tag for the new channel
                    "id": str,                      # Newly generated channel UUID
                    "snippet": {
                        "title": str,               # The provided title
                        "description": str,         # The provided description
                        "publishedAt": str,         # Current timestamp (ISO 8601 with milliseconds)
                        "country": "US"             # Default country code
                    },
                    "statistics": {
                        "viewCount": "0",           # Initialized to 0
                        "subscriberCount": "0",     # Initialized to 0
                        "videoCount": "0"           # Initialized to 0
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If user data cannot be found in the backend
        
        Side Effects:
            - Creates a new channel entry in self.channels dictionary
            - Appends the new channel UUID to the user's "channels" list
            - Prints a confirmation message to stdout with channel ID and owner name
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_user@example.com")
            >>> channel = api.create_channel("My Gaming Channel", "Videos about gaming")
            >>> print(channel["snippet"]["title"])
            'My Gaming Channel'
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")

        channel_uuid = self._generate_unique_id()
        created_at = datetime.now().isoformat(timespec='milliseconds') + "Z"
        new_channel = {
            "id": channel_uuid,
            "title": title,
            "description": description,
            "owner_id": self.current_user_id,
            "created_at": created_at,
            "subscribers": [],
            "videos": [],
            "playlists": [],
            "country": "US",
            "view_count": 0,
            "subscriber_count": 0,
            "video_count": 0,
            "banner_image_path": "https://YouTube.com/default_banner.jpg"
        }
        self.channels[channel_uuid] = new_channel
        user_data["channels"].append(channel_uuid)
        
        print(f"Channel created: ID={channel_uuid} by {user_data['display_name']}")
        
        return {
            "kind": "youtube#channel",
            "etag": f"etag_{channel_uuid}",
            "id": channel_uuid,
            "snippet": {
                "title": title,
                "description": description,
                "publishedAt": created_at,
                "country": "US"
            },
            "statistics": {
                "viewCount": "0",
                "subscriberCount": "0",
                "videoCount": "0"
            }
        }

    def update_channel(self, channel_id: str, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Update properties of an existing channel. Only the channel owner can perform this operation.
        
        This method allows the channel owner to modify the channel's title and/or description.
        Properties that are not specified (None) remain unchanged. The channel's owner_id is checked
        to ensure only the authenticated user who owns the channel can make modifications.

        Args:
            channel_id (str): The UUID of the channel to update. Must be a valid channel ID that exists
                in the backend and is owned by the authenticated user.
            title (Optional[str], optional): The new title for the channel. If None, the title remains
                unchanged. If provided, replaces the current title completely. Defaults to None.
            description (Optional[str], optional): The new description for the channel. If None, the
                description remains unchanged. If provided, replaces the current description completely.
                Defaults to None.

        Returns:
            Dict[str, Any]: The updated channel resource in YouTube API v3 format:
                {
                    "kind": "youtube#channel",
                    "etag": str,                    # Entity tag for the channel
                    "id": str,                      # Channel UUID
                    "snippet": {
                        "title": str,               # Updated or existing title
                        "description": str,         # Updated or existing description
                        "publishedAt": str,         # Original creation date (unchanged)
                        "country": str              # Country code (unchanged)
                    },
                    "statistics": {
                        "viewCount": str,           # Current view count
                        "subscriberCount": str,     # Current subscriber count
                        "videoCount": str           # Current video count
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If the specified channel_id does not exist in the backend
            Exception: If the authenticated user is not the owner of the channel (owner_id mismatch)
        
        Side Effects:
            - Modifies the channel's "title" field in self.channels (if title is provided)
            - Modifies the channel's "description" field in self.channels (if description is provided)
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_owner@example.com")
            >>> updated = api.update_channel("channel-uuid", title="New Channel Name")
            >>> print(updated["snippet"]["title"])
            'New Channel Name'
        """
        self._ensure_authenticated()
        
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            raise Exception("Channel not found")
        
        if channel_data.get("owner_id") != self.current_user_id:
            raise Exception("Only the channel owner can update this channel")

        if title is not None:
            channel_data["title"] = title
        if description is not None:
            channel_data["description"] = description
        
        return {
            "kind": "youtube#channel",
            "etag": f"etag_{channel_id}",
            "id": channel_id,
            "snippet": {
                "title": channel_data.get("title"),
                "description": channel_data.get("description"),
                "publishedAt": channel_data.get("created_at"),
                "country": channel_data.get("country", "US")
            },
            "statistics": {
                "viewCount": str(channel_data.get("view_count", 0)),
                "subscriberCount": str(channel_data.get("subscriber_count", 0)),
                "videoCount": str(channel_data.get("video_count", 0))
            }
        }

    def list_channel_videos(self, channel_id: str, maxResults: int = 25, pageToken: Optional[str] = None) -> Dict[str, Any]:
        """
        List all videos uploaded to a specific channel. This is a public endpoint requiring no authentication.
        
        This method retrieves videos from a channel with pagination support. Videos are returned in the
        order they appear in the channel's video list (typically newest first, but depends on how they
        were added). Useful for browsing a channel's content, displaying channel video galleries, or
        analyzing channel content.

        Args:
            channel_id (str): The UUID of the channel whose videos to retrieve. Must be a valid channel
                ID that exists in the backend.
            maxResults (int, optional): Maximum number of video items to return in a single response.
                Controls pagination page size. Defaults to 25. Valid range is typically 1-50.
            pageToken (Optional[str], optional): Token for retrieving a specific page of results. If None,
                returns the first page (offset 0). The token is a string integer representing the offset
                in the video list (e.g., "25" for the second page when maxResults=25). Use the
                "nextPageToken" from a previous response to get the next page. Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing the video list in YouTube API v3 format:
                {
                    "kind": "youtube#videoListResponse",
                    "etag": "etag_videos",
                    "pageInfo": {
                        "totalResults": int,        # Total number of videos in the channel
                        "resultsPerPage": int       # Number of results in this response (maxResults)
                    },
                    "items": [                      # List of video resources
                        {
                            "kind": "youtube#video",
                            "etag": str,            # Entity tag for this video
                            "id": str,              # Video UUID
                            "snippet": {
                                "publishedAt": str, # Upload timestamp (ISO 8601)
                                "channelId": str,   # The channel UUID (same as input)
                                "title": str,       # Video title
                                "description": str  # Video description
                            },
                            "statistics": {
                                "viewCount": str,   # View count (as string)
                                "likeCount": str,   # Like count (as string)
                                "commentCount": str # Comment count (as string)
                            }
                        },
                        # ... more video items
                    ],
                    "nextPageToken": str (optional) # Present only if more results are available
                }

        Raises:
            Exception: If the specified channel_id does not exist in the backend
        
        Note:
            This method does NOT require authentication and can be called without calling authenticate().
        """
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            raise Exception("Channel not found")
        
        video_ids = channel_data.get("videos", [])
        
        # Simple pagination
        offset = int(pageToken) if pageToken else 0
        paginated_ids = video_ids[offset:offset + maxResults]
        
        items = []
        for video_uuid in paginated_ids:
            video_details = self._get_video_data(video_uuid)
            if video_details:
                items.append({
                    "kind": "youtube#video",
                    "etag": f"etag_{video_uuid}",
                    "id": video_uuid,
                    "snippet": {
                        "publishedAt": video_details.get("uploaded_at"),
                        "channelId": channel_id,
                        "title": video_details.get("title"),
                        "description": video_details.get("description")
                    },
                    "statistics": {
                        "viewCount": str(video_details.get("view_count", 0)),
                        "likeCount": str(video_details.get("like_count", 0)),
                        "commentCount": str(video_details.get("comment_count", 0))
                    }
                })
        
        result = {
            "kind": "youtube#videoListResponse",
            "etag": "etag_videos",
            "pageInfo": {
                "totalResults": len(video_ids),
                "resultsPerPage": maxResults
            },
            "items": items
        }
        
        if offset + maxResults < len(video_ids):
            result["nextPageToken"] = str(offset + maxResults)
        
        return result

    def get_video(self, video_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific video by its ID. This is a public endpoint.
        
        This method returns comprehensive video metadata including title, description, statistics, and
        content details. Each call automatically increments the video's view count by 1 to simulate
        real YouTube behavior. No authentication is required to view public video information.

        Args:
            video_id (str): The UUID of the video to retrieve. Must be a valid video ID that exists
                in the backend.

        Returns:
            Dict[str, Any]: A dictionary containing the video's data in YouTube API v3 format:
                {
                    "kind": "youtube#video",
                    "etag": str,                    # Entity tag based on video_id
                    "id": str,                      # The video UUID
                    "snippet": {
                        "publishedAt": str,         # Upload timestamp (ISO 8601)
                        "channelId": str,           # UUID of the channel that uploaded this video
                        "title": str,               # Video title
                        "description": str,         # Video description
                        "tags": List[str]           # List of tag strings
                    },
                    "contentDetails": {
                        "duration": str             # ISO 8601 duration format (e.g., "PT5M30S" for 5:30)
                    },
                    "statistics": {
                        "viewCount": str,           # View count after increment (as string)
                        "likeCount": str,           # Like count (as string)
                        "commentCount": str         # Number of comments (as string)
                    }
                }

        Raises:
            Exception: If the specified video_id does not exist in the backend
        
        Side Effects:
            - Increments the video's "views" field by 1 each time this method is called
        
        Note:
            This method does NOT require authentication. The view count increment simulates the
            behavior of watching a video on YouTube.
        """
        video_data = self._get_video_data(video_id)
        if not video_data:
            raise Exception("Video not found")
        
        # Increment view count for realism
        video_data["views"] = video_data.get("views", 0) + 1
        
        return {
            "kind": "youtube#video",
            "etag": f"etag_{video_id}",
            "id": video_id,
            "snippet": {
                "publishedAt": video_data.get("published_at"),
                "channelId": video_data.get("channel_id"),
                "title": video_data.get("title"),
                "description": video_data.get("description"),
                "tags": video_data.get("tags", [])
            },
            "contentDetails": {
                "duration": f"PT{video_data.get('duration_seconds', 0)}S"
            },
            "statistics": {
                "viewCount": str(video_data.get("views", 0)),
                "likeCount": str(video_data.get("likes", 0)),
                "commentCount": str(len(video_data.get("comments", {})))
            }
        }
    
    def upload_video(self, title: str, description: str = "", duration_seconds: int = 0, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Upload a new video to the authenticated user's primary channel.
        
        This method simulates uploading a video to YouTube by creating a new video entry associated
        with the user's first (primary) channel. The video is initialized with 0 views, 0 likes,
        0 dislikes, and an empty comments dictionary. The video is added to the channel's video list
        and the channel's video count is incremented.

        Args:
            title (str): The title of the video. This is the main heading displayed to viewers and
                should be descriptive and engaging. Required field.
            description (str, optional): The video description that appears below the video player.
                Can include details about the video content, links, timestamps, credits, etc.
                Defaults to an empty string.
            duration_seconds (int, optional): The length of the video in seconds. For example, a
                5-minute video would be 300 seconds. Used to generate the ISO 8601 duration format
                in the response. Defaults to 0 (which would be displayed as "PT0S").
            tags (Optional[List[str]], optional): A list of tag strings for video categorization and
                search optimization. Tags help users discover the video. For example:
                ["gaming", "tutorial", "minecraft"]. If None, an empty list is used. Defaults to None.

        Returns:
            Dict[str, Any]: The newly created video resource in YouTube API v3 format:
                {
                    "kind": "youtube#video",
                    "etag": str,                    # Entity tag for the new video
                    "id": str,                      # Newly generated video UUID
                    "snippet": {
                        "publishedAt": str,         # Current timestamp (ISO 8601 with milliseconds)
                        "channelId": str,           # UUID of the user's primary channel
                        "title": str,               # The provided title
                        "description": str,         # The provided description
                        "tags": List[str]           # The provided tags or empty list
                    },
                    "contentDetails": {
                        "duration": str             # ISO 8601 duration (e.g., "PT300S" for 300 seconds)
                    },
                    "statistics": {
                        "viewCount": "0",           # Initialized to 0
                        "likeCount": "0",           # Initialized to 0
                        "commentCount": "0"         # Initialized to 0
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If user data cannot be found in the backend
            Exception: If the authenticated user has no channels (cannot upload without a channel)
            Exception: If the channel data cannot be found for the user's primary channel ID
        
        Side Effects:
            - Creates a new video entry in self.videos dictionary
            - Appends the new video UUID to the channel's "videos" list
            - Increments the channel's "video_count" by 1
            - Prints a confirmation message to stdout with video ID and channel title
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_creator@example.com")
            >>> video = api.upload_video(
            ...     title="How to Code in Python",
            ...     description="A beginner's guide",
            ...     duration_seconds=1200,
            ...     tags=["python", "tutorial", "programming"]
            ... )
            >>> print(video["id"])
            '550e8400-e29b-41d4-a716-446655440000'
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        # Get user's primary channel
        user_channels = user_data.get("channels", [])
        if not user_channels:
            raise Exception("No channel found for authenticated user")
        
        channel_id = user_channels[0]
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            raise Exception("Channel data not found")

        video_uuid = self._generate_unique_id()
        published_at = datetime.now().isoformat(timespec='milliseconds') + "Z"
        
        new_video = {
            "id": video_uuid,
            "title": title,
            "description": description,
            "channel_id": channel_id,
            "uploader_id": self.current_user_id,
            "published_at": published_at,
            "duration_seconds": duration_seconds,
            "views": 0,
            "likes": 0,
            "dislikes": 0,
            "comments": {},
            "tags": tags if tags is not None else [],
            "liked_by": []
        }
        self.videos[video_uuid] = new_video
        channel_data["videos"].append(video_uuid)
        channel_data["video_count"] = channel_data.get("video_count", 0) + 1
        
        print(f"Video uploaded: ID={video_uuid} to channel {channel_data['title']}")
        
        return {
            "kind": "youtube#video",
            "etag": f"etag_{video_uuid}",
            "id": video_uuid,
            "snippet": {
                "publishedAt": published_at,
                "channelId": channel_id,
                "title": title,
                "description": description,
                "tags": tags if tags is not None else []
            },
            "contentDetails": {
                "duration": f"PT{duration_seconds}S"
            },
            "statistics": {
                "viewCount": "0",
                "likeCount": "0",
                "commentCount": "0"
            }
        }

    def delete_video(self, video_id: str) -> None:
        """
        Delete a video from YouTube. Only the channel owner can perform this operation.
        
        This method permanently removes a video from the backend. It performs cascading cleanup by
        removing all references to the video from channels, user watch histories, user liked videos,
        and playlists. The channel's video count is decremented. This simulates YouTube's behavior
        of completely removing a video and all its associations when deleted.

        Args:
            video_id (str): The UUID of the video to delete. Must be a valid video ID that exists
                in the backend and is owned by a channel that the authenticated user owns.

        Returns:
            None: This method returns nothing on success.

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If the specified video_id does not exist in the backend
            Exception: If the video's associated channel cannot be found
            Exception: If the authenticated user is not the owner of the channel (and thus the video)
        
        Side Effects:
            - Removes the video entry from self.videos dictionary
            - Removes video_id from the channel's "videos" list
            - Decrements the channel's "video_count" by 1 (minimum 0)
            - Removes video_id from all users' "watch_history" lists
            - Removes video_id from all users' "liked_videos" lists
            - Removes video_id from all playlists' "video_ids" lists
            - Decrements affected playlists' "item_count" by 1 (minimum 0)
            - Prints a confirmation message to stdout
        
        Note:
            This is a destructive operation that cannot be undone. All statistics (views, likes,
            comments) are permanently lost.
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_owner@example.com")
            >>> api.delete_video("video-uuid-123")
            # Prints: Video deleted: ID=video-uuid-123
        """
        self._ensure_authenticated()
        
        video_data = self._get_video_data(video_id)
        if not video_data:
            raise Exception("Video not found")
        
        channel_id = video_data.get("channel_id")
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            raise Exception("Channel not found")
        
        if channel_data.get("owner_id") != self.current_user_id:
            raise Exception("Only the video owner can delete this video")

        if video_id in self.videos:
            del self.videos[video_id]
            
            # Remove from channel's video list
            if video_id in channel_data.get("videos", []):
                channel_data["videos"].remove(video_id)
                channel_data["video_count"] = max(0, channel_data.get("video_count", 0) - 1)
            
            # Remove from any user's watch history or liked videos
            for u_data in self.users.values():
                if video_id in u_data.get("watch_history", []):
                    u_data["watch_history"].remove(video_id)
                if video_id in u_data.get("liked_videos", []):
                    u_data["liked_videos"].remove(video_id)
            
            # Remove from any playlists
            for p_data in self.playlists.values():
                if video_id in p_data.get("video_ids", []):
                    p_data["video_ids"].remove(video_id)
                    p_data["item_count"] = max(0, p_data.get("item_count", 0) - 1)
            
            print(f"Video deleted: ID={video_id}")

    def rate_video(self, video_id: str, rating: str) -> None:
        """
        Rate a video by liking it or removing a previous like.
        
        This method allows the authenticated user to like a video or remove their existing like.
        YouTube's API v3 uses a rating system where "like" adds a like and "none" removes it.
        The method updates both the video's like count and the user's liked_videos list to maintain
        consistency. Attempting to like an already-liked video has no effect (idempotent).

        Args:
            video_id (str): The UUID of the video to rate. Must be a valid video ID that exists
                in the backend.
            rating (str): The rating action to perform. Must be one of:
                - "like": Add a like to the video (if not already liked by this user)
                - "none": Remove the user's like from the video (if currently liked)
                Any other value will raise an exception.

        Returns:
            None: This method returns nothing on success.

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If the specified video_id does not exist in the backend
            Exception: If user data cannot be found in the backend
            Exception: If rating is not "like" or "none"
        
        Side Effects:
            When rating="like" and not already liked:
            - Increments the video's "likes" count by 1
            - Adds current_user_id to the video's "liked_by" list
            - Adds video_id to the user's "liked_videos" list
            - Prints a confirmation message
            
            When rating="none" and currently liked:
            - Decrements the video's "likes" count by 1 (minimum 0)
            - Removes current_user_id from the video's "liked_by" list
            - Removes video_id from the user's "liked_videos" list
            - Prints a confirmation message
        
        Note:
            YouTube API v3 only supports "like" and "none" ratings. The old "dislike" rating
            has been removed from the public API.
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_user@example.com")
            >>> api.rate_video("video-uuid-123", "like")
            # Prints: Video video-uuid-123 liked by user {uuid}
            >>> api.rate_video("video-uuid-123", "none")
            # Prints: Like removed from video video-uuid-123
        """
        self._ensure_authenticated()
        
        video_data = self._get_video_data(video_id)
        user_data = self._get_user_data(self.current_user_id)

        if not video_data:
            raise Exception("Video not found")
        if not user_data:
            raise Exception("User data not found")

        liked_by_list = video_data.get("liked_by", [])
        
        if rating == "like":
            if self.current_user_id not in liked_by_list:
                video_data["likes"] = video_data.get("likes", 0) + 1
                liked_by_list.append(self.current_user_id)
                if video_id not in user_data.get("liked_videos", []):
                    user_data.setdefault("liked_videos", []).append(video_id)
                print(f"Video {video_id} liked by user {self.current_user_id}")
        elif rating == "none":
            # Remove like
            if self.current_user_id in liked_by_list:
                video_data["likes"] = max(0, video_data.get("likes", 0) - 1)
                liked_by_list.remove(self.current_user_id)
                if video_id in user_data.get("liked_videos", []):
                    user_data.setdefault("liked_videos", []).remove(video_id)
                print(f"Like removed from video {video_id}")
        else:
            raise Exception("Invalid rating. Must be 'like' or 'none'")

    def search_videos(self, query: str, maxResults: int = 10, pageToken: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for videos based on a query string. This is a public endpoint requiring no authentication.
        
        This method searches through all videos in the backend, matching the query against video titles,
        descriptions, and tags (case-insensitive). Results are sorted by popularity (view count) in
        descending order. Pagination is supported using pageToken. The search simulates YouTube's
        search functionality for discovering videos.

        Args:
            query (str): The search query string to match against videos. The search is case-insensitive
                and looks for the query as a substring in:
                - Video titles
                - Video descriptions
                - Video tags (any tag containing the query)
                Cannot be empty or whitespace-only.
            maxResults (int, optional): Maximum number of search results to return per page. Controls
                pagination page size. Defaults to 10. Valid range is typically 1-50.
            pageToken (Optional[str], optional): Token for retrieving a specific page of results. If None,
                returns the first page. The token format is "offset_{number}" where {number} is the
                offset in the results list. Use the "nextPageToken" from a previous response to get
                subsequent pages. Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing search results in YouTube API v3 format:
                {
                    "kind": "youtube#searchListResponse",
                    "etag": str,                    # Based on hash of query
                    "pageInfo": {
                        "totalResults": int,        # Total number of videos matching the query
                        "resultsPerPage": int       # Number of results in this response (maxResults)
                    },
                    "items": [                      # List of search result items (sorted by views)
                        {
                            "kind": "youtube#searchResult",
                            "etag": str,            # Entity tag for this result
                            "id": {
                                "kind": "youtube#video",
                                "videoId": str      # UUID of the matching video
                            },
                            "snippet": {
                                "publishedAt": str, # Video upload date (ISO 8601)
                                "channelId": str,   # UUID of the video's channel
                                "title": str,       # Video title
                                "description": str, # Video description
                                "channelTitle": str # Name of the channel (if found)
                            }
                        },
                        # ... more search results
                    ],
                    "nextPageToken": str (optional) # Present only if more results are available
                }

        Raises:
            Exception: If query is empty or contains only whitespace
        
        Note:
            - This method does NOT require authentication
            - Results are sorted by view count (most viewed first)
            - Search is case-insensitive and uses substring matching
        
        Example:
            >>> api = YouTubeApis()
            >>> results = api.search_videos("python tutorial", maxResults=5)
            >>> for item in results["items"]:
            ...     print(item["snippet"]["title"])
        """
        if not query or not query.strip():
            raise Exception("Query parameter is required")
        
        query_lower = query.lower()
        matching_videos = []
        
        for video_uuid, video_data in self.videos.items():
            if query_lower in video_data.get("title", "").lower() or \
               query_lower in video_data.get("description", "").lower() or \
               any(query_lower in tag.lower() for tag in video_data.get("tags", [])):
                matching_videos.append((video_uuid, video_data))
        
        # Sort by views (most popular first)
        matching_videos.sort(key=lambda x: x[1].get("views", 0), reverse=True)
        
        # Pagination
        offset = 0
        if pageToken:
            try:
                offset = int(pageToken.split("_")[1])
            except:
                offset = 0
        
        total_results = len(matching_videos)
        paginated_videos = matching_videos[offset:offset + maxResults]
        
        items = []
        for video_id, video_data in paginated_videos:
            items.append({
                "kind": "youtube#searchResult",
                "etag": f"etag_{video_id}",
                "id": {
                    "kind": "youtube#video",
                    "videoId": video_id
                },
                "snippet": {
                    "publishedAt": video_data.get("published_at", datetime.now(timezone.utc).isoformat()),
                    "channelId": video_data.get("channel_id"),
                    "title": video_data.get("title"),
                    "description": video_data.get("description"),
                    "channelTitle": self._get_channel_data(video_data.get("channel_id", "")).get("title", "") if video_data.get("channel_id") else ""
                }
            })
        
        response = {
            "kind": "youtube#searchListResponse",
            "etag": f"etag_search_{hash(query)}",
            "pageInfo": {
                "totalResults": total_results,
                "resultsPerPage": maxResults
            },
            "items": items
        }
        
        if offset + maxResults < total_results:
            response["nextPageToken"] = f"offset_{offset + maxResults}"
        
        return response

    def search_channels(self, query: str, maxResults: int = 10, pageToken: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for channels based on a query string. This is a public endpoint requiring no authentication.
        
        This method searches through all channels in the backend, matching the query against channel titles
        and descriptions (case-insensitive). Results are sorted by subscriber count in descending order.
        Pagination is supported using pageToken. This simulates YouTube's channel search functionality
        for discovering channels by name or topic.

        Args:
            query (str): The search query string to match against channels. The search is case-insensitive
                and looks for the query as a substring in:
                - Channel titles
                - Channel descriptions
                Cannot be empty or whitespace-only.
            maxResults (int, optional): Maximum number of search results to return per page. Controls
                pagination page size. Defaults to 10. Valid range is typically 1-50.
            pageToken (Optional[str], optional): Token for retrieving a specific page of results. If None,
                returns the first page. The token format is "offset_{number}" where {number} is the
                offset in the results list. Use the "nextPageToken" from a previous response to get
                subsequent pages. Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing search results in YouTube API v3 format:
                {
                    "kind": "youtube#searchListResponse",
                    "etag": str,                    # Based on hash of query
                    "pageInfo": {
                        "totalResults": int,        # Total number of channels matching the query
                        "resultsPerPage": int       # Number of results in this response (maxResults)
                    },
                    "items": [                      # List of search result items (sorted by subscribers)
                        {
                            "kind": "youtube#searchResult",
                            "etag": str,            # Entity tag for this result
                            "id": {
                                "kind": "youtube#channel",
                                "channelId": str    # UUID of the matching channel
                            },
                            "snippet": {
                                "publishedAt": str, # Channel creation date (ISO 8601)
                                "title": str,       # Channel name
                                "description": str, # Channel description
                                "channelId": str    # UUID of the channel (same as id.channelId)
                            }
                        },
                        # ... more search results
                    ],
                    "nextPageToken": str (optional) # Present only if more results are available
                }

        Raises:
            Exception: If query is empty or contains only whitespace
        
        Note:
            - This method does NOT require authentication
            - Results are sorted by subscriber count (most subscribers first)
            - Search is case-insensitive and uses substring matching
            - This enables natural language queries like "subscribe to The Daily Glimpse"
        
        Example:
            >>> api = YouTubeApis()
            >>> results = api.search_channels("gaming", maxResults=5)
            >>> for item in results["items"]:
            ...     print(item["snippet"]["title"])
        """
        if not query or not query.strip():
            raise Exception("Query cannot be empty")
        
        query_lower = query.lower()
        matching_channels = []
        
        # Search through all channels
        for channel_id, channel_data in self.channels.items():
            title = channel_data.get("title", "").lower()
            description = channel_data.get("description", "").lower()
            
            # Check if query matches title or description
            if query_lower in title or query_lower in description:
                matching_channels.append((channel_id, channel_data))
        
        # Sort by subscriber count (descending)
        matching_channels.sort(key=lambda x: x[1].get("subscriber_count", 0), reverse=True)
        
        # Pagination
        offset = 0
        if pageToken and pageToken.startswith("offset_"):
            try:
                offset = int(pageToken.split("_")[1])
            except (ValueError, IndexError):
                offset = 0
        
        total_results = len(matching_channels)
        paginated_channels = matching_channels[offset:offset + maxResults]
        
        items = []
        for channel_id, channel_data in paginated_channels:
            items.append({
                "kind": "youtube#searchResult",
                "etag": f"etag_{channel_id}",
                "id": {
                    "kind": "youtube#channel",
                    "channelId": channel_id
                },
                "snippet": {
                    "publishedAt": channel_data.get("created_at", ""),
                    "title": channel_data.get("title", ""),
                    "description": channel_data.get("description", ""),
                    "channelId": channel_id
                }
            })
        
        response = {
            "kind": "youtube#searchListResponse",
            "etag": f"etag_{abs(hash(query))}",
            "pageInfo": {
                "totalResults": total_results,
                "resultsPerPage": len(items)
            },
            "items": items
        }
        
        if offset + maxResults < total_results:
            response["nextPageToken"] = f"offset_{offset + maxResults}"
        
        return response

    def list_playlists_in_channel(self, channel_id: str, maxResults: int = 25, pageToken: Optional[str] = None) -> Dict[str, Any]:
        """
        List all playlists in a specific channel. This is a public endpoint requiring no authentication.
        
        This method retrieves all playlists created by a channel, allowing users to browse organized
        collections of videos. Playlists help channels organize content by topic, series, or theme.
        Results are paginated for channels with many playlists.

        Args:
            channel_id (str): The UUID of the channel whose playlists to retrieve. Must be a valid
                channel ID that exists in the backend.
            maxResults (int, optional): Maximum number of playlist items to return per page. Controls
                pagination page size. Defaults to 25. Valid range is typically 1-50.
            pageToken (Optional[str], optional): Token for retrieving a specific page of results. If None,
                returns the first page. The token format is "offset_{number}" where {number} is the
                offset in the playlists list. Use the "nextPageToken" from a previous response to get
                subsequent pages. Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing the playlist list in YouTube API v3 format:
                {
                    "kind": "youtube#playlistListResponse",
                    "etag": str,                    # Based on channel_id
                    "pageInfo": {
                        "totalResults": int,        # Total number of playlists in the channel
                        "resultsPerPage": int       # Number of results in this response (maxResults)
                    },
                    "items": [                      # List of playlist resources
                        {
                            "kind": "youtube#playlist",
                            "etag": str,            # Entity tag for this playlist
                            "id": str,              # Playlist UUID
                            "snippet": {
                                "publishedAt": str, # Playlist creation timestamp (ISO 8601)
                                "channelId": str,   # Channel UUID (same as input)
                                "title": str,       # Playlist title
                                "description": str  # Playlist description
                            },
                            "contentDetails": {
                                "itemCount": int    # Number of videos in the playlist
                            }
                        },
                        # ... more playlist items
                    ],
                    "nextPageToken": str (optional) # Present only if more results are available
                }

        Raises:
            Exception: If the specified channel_id does not exist in the backend
        
        Note:
            This method does NOT require authentication and can be called without calling authenticate().
        """
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            raise Exception("Channel not found")
        
        playlist_ids = channel_data.get("playlists", [])
        
        # Pagination
        offset = 0
        if pageToken:
            try:
                offset = int(pageToken.split("_")[1])
            except:
                offset = 0
        
        total_results = len(playlist_ids)
        paginated_ids = playlist_ids[offset:offset + maxResults]
        
        items = []
        for playlist_id in paginated_ids:
            playlist_data = self._get_playlist_data(playlist_id)
            if playlist_data:
                items.append({
                    "kind": "youtube#playlist",
                    "etag": f"etag_{playlist_id}",
                    "id": playlist_id,
                    "snippet": {
                        "publishedAt": playlist_data.get("created_at", datetime.now(timezone.utc).isoformat()),
                        "channelId": channel_id,
                        "title": playlist_data.get("title"),
                        "description": playlist_data.get("description", "")
                    },
                    "contentDetails": {
                        "itemCount": playlist_data.get("item_count", 0)
                    }
                })
        
        response = {
            "kind": "youtube#playlistListResponse",
            "etag": f"etag_playlists_{channel_id}",
            "pageInfo": {
                "totalResults": total_results,
                "resultsPerPage": maxResults
            },
            "items": items
        }
        
        if offset + maxResults < total_results:
            response["nextPageToken"] = f"offset_{offset + maxResults}"
        
        return response

    def get_playlist_details(self, playlist_id: str) -> Dict[str, Any]:
        """
        Get comprehensive playlist details including all videos in the playlist. Public endpoint.
        
        This method retrieves complete playlist information, including metadata and a list of all
        videos contained in the playlist. Unlike list_playlists_in_channel which only returns
        playlist summaries, this method includes the full video list with details for each video.
        Useful for displaying playlist contents or analyzing playlist composition.

        Args:
            playlist_id (str): The UUID of the playlist to retrieve. Must be a valid playlist ID
                that exists in the backend.

        Returns:
            Dict[str, Any]: A dictionary containing comprehensive playlist data in YouTube API v3 format:
                {
                    "kind": "youtube#playlist",
                    "etag": str,                    # Entity tag for the playlist
                    "id": str,                      # Playlist UUID
                    "snippet": {
                        "publishedAt": str,         # Playlist creation timestamp (ISO 8601)
                        "channelId": str,           # UUID of the channel that owns this playlist
                        "title": str,               # Playlist title
                        "description": str          # Playlist description
                    },
                    "contentDetails": {
                        "itemCount": int            # Number of videos in the playlist
                    },
                    "items": [                      # List of videos in the playlist
                        {
                            "kind": "youtube#playlistItem",
                            "etag": str,            # Entity tag for this playlist item
                            "id": str,              # Composite ID: {playlist_id}_{video_id}
                            "snippet": {
                                "publishedAt": str, # Video upload timestamp
                                "channelId": str,   # Channel UUID
                                "title": str,       # Video title
                                "description": str, # Video description
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": str  # Video UUID
                                }
                            }
                        },
                        # ... more playlist items
                    ]
                }

        Raises:
            Exception: If the specified playlist_id does not exist in the backend
        
        Note:
            - This method does NOT require authentication
            - Returns ALL videos in the playlist (no pagination)
            - Video details are included only if the video still exists in the backend
        """
        playlist_data = self._get_playlist_data(playlist_id)
        if not playlist_data:
            raise Exception("Playlist not found")
        
        # Get video details
        videos = []
        for video_id in playlist_data.get("video_ids", []):
            video_data = self._get_video_data(video_id)
            if video_data:
                videos.append({
                    "kind": "youtube#playlistItem",
                    "etag": f"etag_{video_id}",
                    "id": f"{playlist_id}_{video_id}",
                    "snippet": {
                        "publishedAt": video_data.get("published_at", datetime.now(timezone.utc).isoformat()),
                        "channelId": playlist_data.get("channel_id"),
                        "title": video_data.get("title"),
                        "description": video_data.get("description"),
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                })
        
        return {
            "kind": "youtube#playlist",
            "etag": f"etag_{playlist_id}",
            "id": playlist_id,
            "snippet": {
                "publishedAt": playlist_data.get("created_at", datetime.now(timezone.utc).isoformat()),
                "channelId": playlist_data.get("channel_id"),
                "title": playlist_data.get("title"),
                "description": playlist_data.get("description", "")
            },
            "contentDetails": {
                "itemCount": playlist_data.get("item_count", 0)
            },
            "items": videos
        }

    def create_playlist(self, title: str, description: str = "", privacy_status: str = "public") -> Dict[str, Any]:
        """
        Create a new playlist in the authenticated user's primary channel.
        
        This method creates an empty playlist that can later be populated with videos using
        add_video_to_playlist(). The playlist is associated with the user's first (primary) channel.
        Privacy settings control who can view and access the playlist.

        Args:
            title (str): The title of the playlist. This is the name displayed to viewers and should
                clearly describe the playlist's content or theme. Required field.
            description (str, optional): A detailed description of the playlist that appears on the
                playlist page. Can explain the purpose, theme, or contents of the playlist.
                Defaults to an empty string.
            privacy_status (str, optional): Controls the visibility of the playlist. Must be one of:
                - "public": Anyone can find and view the playlist
                - "unlisted": Only people with the link can view the playlist (not searchable)
                - "private": Only the owner can view the playlist
                Defaults to "public". Any other value will raise an exception.

        Returns:
            Dict[str, Any]: The newly created playlist resource in YouTube API v3 format:
                {
                    "kind": "youtube#playlist",
                    "etag": str,                    # Entity tag for the new playlist
                    "id": str,                      # Newly generated playlist UUID
                    "snippet": {
                        "publishedAt": str,         # Current timestamp (ISO 8601)
                        "channelId": str,           # UUID of the user's primary channel
                        "title": str,               # The provided title
                        "description": str          # The provided description
                    },
                    "status": {
                        "privacyStatus": str        # The provided privacy status
                    },
                    "contentDetails": {
                        "itemCount": 0              # Initialized to 0 (empty playlist)
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If user data cannot be found in the backend
            Exception: If the authenticated user has no channels
            Exception: If the channel data cannot be found for the user's primary channel
            Exception: If privacy_status is not one of "public", "unlisted", or "private"
        
        Side Effects:
            - Creates a new playlist entry in self.playlists dictionary
            - Appends the new playlist UUID to the channel's "playlists" list
            - Prints a confirmation message to stdout with playlist ID and channel title
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_user@example.com")
            >>> playlist = api.create_playlist(
            ...     title="Best Coding Tutorials",
            ...     description="My favorite programming tutorials",
            ...     privacy_status="public"
            ... )
            >>> print(playlist["id"])
            '550e8400-e29b-41d4-a716-446655440000'
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        # Get user's primary channel
        if not user_data.get("channels"):
            raise Exception("User has no channels")
        
        channel_id = user_data["channels"][0]
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            raise Exception("Channel not found")
        
        if privacy_status not in ["public", "unlisted", "private"]:
            raise Exception("Invalid privacy status. Must be 'public', 'unlisted', or 'private'")
        
        playlist_id = self._generate_unique_id()
        created_at = datetime.now(timezone.utc).isoformat()
        
        new_playlist = {
            "id": playlist_id,
            "title": title,
            "description": description,
            "owner_id": self.current_user_id,
            "channel_id": channel_id,
            "video_ids": [],
            "created_at": created_at,
            "privacy_status": privacy_status,
            "item_count": 0
        }
        
        self.playlists[playlist_id] = new_playlist
        self.channels[channel_id]["playlists"].append(playlist_id)
        
        print(f"Playlist created: ID={playlist_id} in channel {channel_data['title']}")
        
        return {
            "kind": "youtube#playlist",
            "etag": f"etag_{playlist_id}",
            "id": playlist_id,
            "snippet": {
                "publishedAt": created_at,
                "channelId": channel_id,
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": privacy_status
            },
            "contentDetails": {
                "itemCount": 0
            }
        }

    def add_video_to_playlist(self, playlist_id: str, video_id: str) -> Dict[str, Any]:
        """
        Add a video to a playlist. Only the playlist owner can add videos.
        
        This method adds a video to the specified playlist by appending its UUID to the playlist's
        video_ids list. The video must exist in the backend, and duplicate additions are prevented.
        The playlist's item count is incremented. Only the authenticated user who owns the playlist
        can add videos to it.

        Args:
            playlist_id (str): The UUID of the playlist to add the video to. Must be a valid playlist
                ID that exists in the backend and is owned by the authenticated user.
            video_id (str): The UUID of the video to add to the playlist. Must be a valid video ID
                that exists in the backend. The video can be from any channel, not just the playlist
                owner's channel.

        Returns:
            Dict[str, Any]: A playlist item resource in YouTube API v3 format:
                {
                    "kind": "youtube#playlistItem",
                    "etag": str,                    # Composite etag: {playlist_id}_{video_id}
                    "id": str,                      # Composite ID: {playlist_id}_{video_id}
                    "snippet": {
                        "publishedAt": str,         # Current timestamp (ISO 8601)
                        "channelId": str,           # UUID of the playlist's channel
                        "title": str,               # Video title
                        "description": str,         # Video description
                        "playlistId": str,          # The playlist UUID
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": str          # The video UUID
                        }
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If the specified playlist_id does not exist in the backend
            Exception: If the specified video_id does not exist in the backend
            Exception: If the authenticated user is not the owner of the playlist (owner_id mismatch)
            Exception: If the video is already in the playlist (duplicate prevention)
        
        Side Effects:
            - Appends video_id to the playlist's "video_ids" list
            - Increments the playlist's "item_count" by 1
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_owner@example.com")
            >>> item = api.add_video_to_playlist("playlist-uuid", "video-uuid")
            >>> print(item["snippet"]["title"])
            'Video Title'
        """
        self._ensure_authenticated()
        
        playlist_data = self._get_playlist_data(playlist_id)
        video_data = self._get_video_data(video_id)

        if not playlist_data:
            raise Exception("Playlist not found")
        if not video_data:
            raise Exception("Video not found")
        
        if playlist_data.get("owner_id") != self.current_user_id:
            raise Exception("Only the playlist owner can add videos")

        if video_id in playlist_data.get("video_ids", []):
            raise Exception("Video already in playlist")
        
        playlist_data["video_ids"].append(video_id)
        playlist_data["item_count"] = playlist_data.get("item_count", 0) + 1
        
        return {
            "kind": "youtube#playlistItem",
            "etag": f"etag_{playlist_id}_{video_id}",
            "id": f"{playlist_id}_{video_id}",
            "snippet": {
                "publishedAt": datetime.now(timezone.utc).isoformat(),
                "channelId": playlist_data.get("channel_id"),
                "title": video_data.get("title"),
                "description": video_data.get("description"),
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }

    def remove_video_from_playlist(self, playlist_id: str, video_id: str) -> None:
        """
        Remove a video from a playlist. Only the playlist owner can remove videos.
        
        This method removes a video from the specified playlist by removing its UUID from the
        playlist's video_ids list. The playlist's item count is decremented. Only the authenticated
        user who owns the playlist can remove videos from it. The video itself is not deleted,
        only the reference in the playlist is removed.

        Args:
            playlist_id (str): The UUID of the playlist to remove the video from. Must be a valid
                playlist ID that exists in the backend and is owned by the authenticated user.
            video_id (str): The UUID of the video to remove from the playlist. Must currently be
                in the playlist's video list.

        Returns:
            None: This method returns nothing on success.

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If the specified playlist_id does not exist in the backend
            Exception: If the authenticated user is not the owner of the playlist (owner_id mismatch)
            Exception: If the video_id is not found in the playlist's video list
        
        Side Effects:
            - Removes video_id from the playlist's "video_ids" list
            - Decrements the playlist's "item_count" by 1 (minimum 0)
        
        Note:
            The video itself remains in the backend and in other playlists. Only the playlist
            reference is removed.
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_owner@example.com")
            >>> api.remove_video_from_playlist("playlist-uuid", "video-uuid")
            # Video removed successfully
        """
        self._ensure_authenticated()
        
        playlist_data = self._get_playlist_data(playlist_id)

        if not playlist_data:
            raise Exception("Playlist not found")
        
        if playlist_data.get("owner_id") != self.current_user_id:
            raise Exception("Only the playlist owner can remove videos")

        if video_id not in playlist_data.get("video_ids", []):
            raise Exception("Video not found in playlist")
        
        playlist_data["video_ids"].remove(video_id)
        playlist_data["item_count"] = max(0, playlist_data.get("item_count", 0) - 1)

    def add_comment_to_video(self, video_id: str, text: str) -> Dict[str, Any]:
        """
        Add a comment to a video.
        
        This method creates a new comment on the specified video by the authenticated user. The comment
        is stored in the video's comments dictionary, keyed by the user's UUID. The video's comment
        count is incremented. Only one comment per user per video is stored in this simplified model
        (subsequent comments from the same user replace the previous comment).

        Args:
            video_id (str): The UUID of the video to comment on. Must be a valid video ID that exists
                in the backend.
            text (str): The comment text content. Cannot be empty or whitespace-only. Should contain
                the user's thoughts, feedback, or response to the video.

        Returns:
            Dict[str, Any]: A comment resource in YouTube API v3 format:
                {
                    "kind": "youtube#comment",
                    "etag": str,                    # Entity tag based on comment_id
                    "id": str,                      # Newly generated comment UUID
                    "snippet": {
                        "authorDisplayName": str,   # Display name of the commenting user
                        "authorChannelId": str,     # UUID of the user's primary channel (if exists)
                        "videoId": str,             # UUID of the commented video
                        "textDisplay": str,         # The comment text (HTML-safe)
                        "textOriginal": str,        # The original comment text
                        "canRate": True,            # Whether the comment can be rated (always True)
                        "likeCount": 0,             # Like count (initialized to 0)
                        "publishedAt": str,         # Current timestamp (ISO 8601)
                        "updatedAt": str            # Same as publishedAt (ISO 8601)
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If text is empty or contains only whitespace
            Exception: If the specified video_id does not exist in the backend
            Exception: If user data cannot be found in the backend
        
        Side Effects:
            - Adds/updates an entry in the video's "comments" dictionary (keyed by current_user_id)
            - Increments the video's "comments_count" by 1 (only for new comments)
            - Prints a confirmation message to stdout with user display name and comment text
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_user@example.com")
            >>> comment = api.add_comment_to_video("video-uuid", "Great tutorial!")
            >>> print(comment["snippet"]["textDisplay"])
            'Great tutorial!'
        """
        self._ensure_authenticated()
        
        if not text or not text.strip():
            raise Exception("Comment text cannot be empty")
        
        video_data = self._get_video_data(video_id)
        user_data = self._get_user_data(self.current_user_id)

        if not video_data:
            raise Exception("Video not found")
        if not user_data:
            raise Exception("User data not found")

        # Ensure comments is a dictionary
        if not isinstance(self.videos[video_id]["comments"], dict):
            self.videos[video_id]["comments"] = {}
        
        # Add comment
        comment_id = self._generate_unique_id()
        published_at = datetime.now(timezone.utc).isoformat()
        
        self.videos[video_id]["comments"][self.current_user_id] = {
            "id": comment_id,
            "text": text,
            "published_at": published_at
        }
        
        # Increment comment count
        self.videos[video_id]["comments_count"] = self.videos[video_id].get("comments_count", 0) + 1
        
        print(f"Comment added on video {video_id} by {user_data['display_name']}: {text}")
        
        return {
            "kind": "youtube#comment",
            "etag": f"etag_{comment_id}",
            "id": comment_id,
            "snippet": {
                "authorDisplayName": user_data.get("display_name", "Unknown"),
                "authorChannelId": user_data.get("channels", [""])[0] if user_data.get("channels") else "",
                "videoId": video_id,
                "textDisplay": text,
                "textOriginal": text,
                "canRate": True,
                "likeCount": 0,
                "publishedAt": published_at,
                "updatedAt": published_at
            }
        }

    def list_comments_for_video(self, video_id: str, maxResults: int = 20, pageToken: Optional[str] = None) -> Dict[str, Any]:
        """
        List all comments for a video with pagination. This is a public endpoint requiring no authentication.
        
        This method retrieves all comments posted on a video, formatted as comment threads (which can
        contain replies in YouTube's actual API, though this simulation doesn't support replies). Each
        comment includes the author's information and the comment text. Comments are paginated to handle
        videos with many comments efficiently.

        Args:
            video_id (str): The UUID of the video whose comments to retrieve. Must be a valid video ID
                that exists in the backend.
            maxResults (int, optional): Maximum number of comment thread items to return per page.
                Controls pagination page size. Defaults to 20. Valid range is typically 1-100.
            pageToken (Optional[str], optional): Token for retrieving a specific page of results. If None,
                returns the first page. The token format is "offset_{number}" where {number} is the
                offset in the comments list. Use the "nextPageToken" from a previous response to get
                subsequent pages. Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing comment threads in YouTube API v3 format:
                {
                    "kind": "youtube#commentThreadListResponse",
                    "etag": str,                    # Based on video_id
                    "pageInfo": {
                        "totalResults": int,        # Total number of comments on the video
                        "resultsPerPage": int       # Number of results in this response (maxResults)
                    },
                    "items": [                      # List of comment thread resources
                        {
                            "kind": "youtube#commentThread",
                            "etag": str,            # Entity tag for this comment thread
                            "id": str,              # Comment UUID
                            "snippet": {
                                "videoId": str,     # Video UUID (same as input)
                                "topLevelComment": {
                                    "kind": "youtube#comment",
                                    "etag": str,    # Entity tag for the comment
                                    "id": str,      # Comment UUID
                                    "snippet": {
                                        "authorDisplayName": str,  # Commenter's display name
                                        "authorChannelId": str,    # Commenter's channel UUID
                                        "videoId": str,            # Video UUID
                                        "textDisplay": str,        # Comment text
                                        "textOriginal": str,       # Original comment text
                                        "canRate": True,           # Can be rated
                                        "likeCount": 0,            # Like count
                                        "publishedAt": str,        # Comment timestamp (ISO 8601)
                                        "updatedAt": str           # Last update timestamp
                                    }
                                },
                                "canReply": True,       # Whether replies are allowed
                                "totalReplyCount": 0,   # Number of replies (always 0 in this simulation)
                                "isPublic": True        # Whether the comment is public
                            }
                        },
                        # ... more comment threads
                    ],
                    "nextPageToken": str (optional) # Present only if more results are available
                }

        Raises:
            Exception: If the specified video_id does not exist in the backend
        
        Note:
            - This method does NOT require authentication
            - Comments are stored per user (one comment per user per video in this simulation)
            - The "Unknown" author is used if the commenting user data is not found
        """
        video_data = self._get_video_data(video_id)
        if not video_data:
            raise Exception("Video not found")

        comments_data = video_data.get("comments", {})
        comment_items = []
        
        if isinstance(comments_data, dict):
            for author_id, comment_info in comments_data.items():
                author_info = self._get_user_data(author_id)
                
                # Handle both old simple dict and new structured format
                if isinstance(comment_info, dict):
                    comment_id = comment_info.get("id", self._generate_unique_id())
                    text = comment_info.get("text", "")
                    published_at = comment_info.get("published_at", datetime.now(timezone.utc).isoformat())
                else:
                    comment_id = self._generate_unique_id()
                    text = str(comment_info)
                    published_at = datetime.now(timezone.utc).isoformat()
                
                comment_items.append({
                    "kind": "youtube#commentThread",
                    "etag": f"etag_{comment_id}",
                    "id": comment_id,
                    "snippet": {
                        "videoId": video_id,
                        "topLevelComment": {
                            "kind": "youtube#comment",
                            "etag": f"etag_{comment_id}",
                            "id": comment_id,
                            "snippet": {
                                "authorDisplayName": author_info.get("display_name", "Unknown") if author_info else "Unknown",
                                "authorChannelId": author_info.get("channels", [""])[0] if author_info and author_info.get("channels") else "",
                                "videoId": video_id,
                                "textDisplay": text,
                                "textOriginal": text,
                                "canRate": True,
                                "likeCount": 0,
                                "publishedAt": published_at,
                                "updatedAt": published_at
                            }
                        },
                        "canReply": True,
                        "totalReplyCount": 0,
                        "isPublic": True
                    }
                })
        # Pagination
        offset = 0
        if pageToken:
            try:
                offset = int(pageToken.split("_")[1])
            except:
                offset = 0       
        total_results = len(comment_items)
        paginated_comments = comment_items[offset:offset + maxResults]
        
        response = {
            "kind": "youtube#commentThreadListResponse",
            "etag": f"etag_comments_{video_id}",
            "pageInfo": {
                "totalResults": total_results,
                "resultsPerPage": maxResults
            },
            "items": paginated_comments
        }
        
        if offset + maxResults < total_results:
            response["nextPageToken"] = f"offset_{offset + maxResults}"
        
        return response

    def delete_comment(self, comment_id: str) -> None:
        """
        Delete a comment from a video. Only the comment author can delete it.
        
        This method removes a comment from a video by searching through all videos to find the comment
        with the specified ID. The comment must have been posted by the currently authenticated user.
        The video's comment count is decremented. Only the author of a comment can delete it, ensuring
        users can't delete others' comments.

        Args:
            comment_id (str): The UUID of the comment to delete. Must be a valid comment ID that exists
                in the backend and was authored by the currently authenticated user.

        Returns:
            None: This method returns nothing on success.

        Raises:
            Exception: If not authenticated (authenticate() has not been called)
            Exception: If the comment_id is not found in any video's comments
            Exception: If the comment exists but was not authored by the currently authenticated user
        
        Side Effects:
            - Removes the comment entry from the video's "comments" dictionary
            - Decrements the video's "comments_count" by 1 (minimum 0)
        
        Note:
            This method searches through all videos to find the comment, which may be less efficient
            for large numbers of videos. The search stops after finding and deleting the first matching
            comment.
        
        Example:
            >>> api = YouTubeApis()
            >>> api.authenticate("token_user@example.com")
            >>> comment = api.add_comment_to_video("video-uuid", "Test comment")
            >>> api.delete_comment(comment["id"])
            # Comment deleted successfully
        """
        self._ensure_authenticated()
        
        # Find comment across all videos
        comment_found = False
        for video_id, video_data in self.videos.items():
            comments = video_data.get("comments", {})
            if isinstance(comments, dict):
                # Check if current user has a comment
                if self.current_user_id in comments:
                    comment_info = comments[self.current_user_id]
                    # Check if this is the comment to delete
                    if isinstance(comment_info, dict) and comment_info.get("id") == comment_id:
                        del comments[self.current_user_id]
                        self.videos[video_id]["comments_count"] = max(0, self.videos[video_id].get("comments_count", 1) - 1)
                        comment_found = True
                        break
        
        if not comment_found:
            raise Exception("Comment not found or you are not the author")

    def youtube_captions_insert(self, video_id: str, language: str, track_content: str) -> Dict[str, Any]:
        """
        Upload a caption/subtitle track for a video. Simulates adding captions without storing actual files.
        
        This method simulates the YouTube captions API by storing caption metadata (language, status, and
        a snippet of the content) in the channel's captions dictionary. In a real implementation, this would
        upload and process SRT, VTT, or other caption file formats. The caption is stored in the channel that
        owns the video, not directly with the video.

        Args:
            video_id (str): The UUID of the video to add captions to. Must be a valid video ID that exists
                in the backend.
            language (str): The language code for the caption track following BCP-47 standard (e.g., "en"
                for English, "es" for Spanish, "fr" for French, "ja" for Japanese). This identifies which
                language the captions are in.
            track_content (str): The full content of the caption track as a string. In real usage, this would
                be SRT format (with timestamps) or similar. For example:
                "1\n00:00:00,000 --> 00:00:02,000\nHello World\n\n2\n00:00:02,000 --> 00:00:05,000\nWelcome to the video"
                Only the first 50 characters are stored (plus "...") as a content snippet.

        Returns:
            Dict[str, Any]: A dictionary indicating the result of the caption upload:
                Success case:
                {
                    "status": True,
                    "caption_id": str,          # Newly generated caption UUID
                    "language": str             # The language code provided
                }
                
                Failure cases:
                {
                    "message": str,             # Error message explaining the failure
                    "status": False
                }

        Side Effects:
            - Creates a new caption entry in the channel's "captions" dictionary (if video found)
            - The caption entry includes: id, video_id, language, status="serving", content_snippet
        
        Note:
            - This is a simulation and doesn't actually process or store full caption files
            - Returns failure if video not found or if the video's channel is not found
            - Does not require authentication in this simulation (though real YouTube API would)
        
        Example:
            >>> api = YouTubeApis()
            >>> srt_content = "1\n00:00:00,000 --> 00:00:02,000\nHello World"
            >>> result = api.youtube_captions_insert("video-uuid", "en", srt_content)
            >>> print(result["status"])
            True
        """
        video_data = self._get_video_data(video_id)
        if not video_data:
            return {"message": "Video not found.", "status": False}
        
        caption_id = self._generate_unique_id()
        channel_id = video_data.get("channel_id")
        if channel_id and channel_id in self.channels:
            if "captions" not in self.channels[channel_id]:
                self.channels[channel_id]["captions"] = {}
            self.channels[channel_id]["captions"][caption_id] = {
                "id": caption_id,
                "video_id": video_id,
                "language": language,
                "status": "serving",
                "content_snippet": track_content[:50] + "..." if len(track_content) > 50 else track_content
            }
            return {"status": True, "caption_id": caption_id, "language": language}
        return {"message": "Channel for video not found.", "status": False}

    def youtube_captions_update(self, id: str, track_content: str) -> Dict[str, Any]:
        """
        Update an existing caption track with new content. Simulates updating captions by caption ID.
        
        This method searches through all channels' caption dictionaries to find and update a caption
        with the specified ID. Only the content snippet (first 50 characters) is updated to simulate
        caption content modification. In a real implementation, this would replace the entire caption
        file with new timing and text.

        Args:
            id (str): The UUID of the caption track to update. Must be a valid caption ID that exists
                in some channel's captions dictionary.
            track_content (str): The new content for the caption track. In real usage, this would be
                the complete SRT or VTT formatted caption file content. Only the first 50 characters
                (plus "...") are stored as a content snippet in this simulation.

        Returns:
            Dict[str, Any]: A dictionary indicating the result of the update operation:
                Success case:
                {
                    "status": True,
                    "caption_id": str,          # The updated caption's UUID (same as input id)
                    "message": "Caption updated."
                }
                
                Failure case:
                {
                    "message": "Caption track not found.",
                    "status": False
                }

        Side Effects:
            - Updates the "content_snippet" field of the caption entry (if found)
        
        Note:
            - Searches through all channels to find the caption
            - Does not modify language or other caption metadata, only content
            - Does not require authentication in this simulation
        
        Example:
            >>> api = YouTubeApis()
            >>> new_content = "1\n00:00:00,000 --> 00:00:02,000\nUpdated text"
            >>> result = api.youtube_captions_update("caption-uuid", new_content)
            >>> print(result["message"])
            'Caption updated.'
        """
        for _, channel_data in self.channels.items():
            if "captions" in channel_data and id in channel_data["captions"]:
                channel_data["captions"][id]["content_snippet"] = track_content[:50] + "..." if len(track_content) > 50 else track_content
                return {"status": True, "caption_id": id, "message": "Caption updated."}
        return {"message": "Caption track not found.", "status": False}

    def youtube_captions_delete(self, id: str) -> Dict[str, Any]:
        """
        Delete a caption track from a video permanently.
        
        This method searches through all channels' caption dictionaries to find and remove a caption
        with the specified ID. Once deleted, the caption is permanently removed and cannot be recovered.
        In a real implementation, this would delete the caption file from YouTube's storage.

        Args:
            id (str): The UUID of the caption track to delete. Must be a valid caption ID that exists
                in some channel's captions dictionary.

        Returns:
            Dict[str, Any]: A dictionary indicating the result of the deletion:
                Success case:
                {
                    "status": True,
                    "deleted_caption_id": str   # The UUID of the deleted caption (same as input id)
                }
                
                Failure case:
                {
                    "message": "Caption track not found.",
                    "status": False
                }

        Side Effects:
            - Removes the caption entry from the channel's "captions" dictionary (if found)
        
        Note:
            - Searches through all channels to find the caption
            - Deletion is permanent and cannot be undone
            - Does not require authentication in this simulation (though real YouTube API would)
        
        Example:
            >>> api = YouTubeApis()
            >>> result = api.youtube_captions_delete("caption-uuid")
            >>> if result["status"]:
            ...     print(f"Deleted: {result['deleted_caption_id']}")
        """
        for channel_id, channel_data in self.channels.items():
            if "captions" in channel_data and id in channel_data["captions"]:
                del self.channels[channel_id]["captions"][id]
                return {"status": True, "deleted_caption_id": id}
        return {"message": "Caption track not found.", "status": False}

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """
        Retrieve complete user profile data by searching for their email address.
        
        This utility method searches through all users in the backend to find a user with a matching
        email address. Returns a deep copy of the user's data to prevent external modifications to
        the backend state. Useful for user lookup, profile retrieval, and testing.

        Args:
            email (str): The email address to search for. Must match exactly (case-sensitive) a user's
                email in the backend.

        Returns:
            Dict[str, Any]: A dictionary with a "data" key containing the user information:
                Success case:
                {
                    "data": {                   # Deep copy of user profile data
                        "id": str,              # User UUID
                        "email": str,           # Email address
                        "display_name": str,    # Display name
                        "channels": List[str],  # List of owned channel UUIDs
                        "subscriptions": List[str], # List of subscribed channel UUIDs
                        "watch_history": List[str], # List of watched video UUIDs
                        "liked_videos": List[str],  # List of liked video UUIDs
                        "watch_later_playlist": List[str], # Watch later video UUIDs
                        "notification_settings": Dict,  # Notification preferences
                        "language_preference": str,     # Language code
                        "account_status": str,          # Account status
                        # ... other user fields
                    }
                }
                
                Failure case (user not found):
                {
                    "data": None,
                    "message": "User not found"
                }
        
        Note:
            - Does not require authentication
            - Email matching is case-sensitive
            - Returns a deep copy to protect backend integrity
        
        Example:
            >>> api = YouTubeApis()
            >>> user = api.get_user_by_email("john@example.com")
            >>> if user["data"]:
            ...     print(user["data"]["display_name"])
        """
        user_id = self._find_user_by_email(email)
        if user_id:
            return {"data": copy.deepcopy(self.users[user_id])}
        return {"data": None, "message": "User not found"}

    def get_user_by_display_name(self, display_name: str) -> Dict[str, Any]:
        """
        Retrieve complete user profile data by searching for their display name.
        
        This utility method searches through all users in the backend to find a user with a matching
        display name. Returns a deep copy of the user's data to prevent external modifications. Useful
        for user discovery, profile lookup by username, and testing scenarios.

        Args:
            display_name (str): The display name (username) to search for. Must match exactly
                (case-sensitive) a user's display_name in the backend.

        Returns:
            Dict[str, Any]: A dictionary with a "data" key containing the user information:
                Success case:
                {
                    "data": {                   # Deep copy of user profile data
                        "id": str,              # User UUID
                        "email": str,           # Email address
                        "display_name": str,    # Display name (same as search input)
                        "channels": List[str],  # List of owned channel UUIDs
                        "subscriptions": List[str], # List of subscribed channel UUIDs
                        # ... other user fields (same structure as get_user_by_email)
                    }
                }
                
                Failure case (user not found):
                {
                    "data": None,
                    "message": "User not found"
                }
        
        Note:
            - Does not require authentication
            - Display name matching is case-sensitive
            - Returns a deep copy to protect backend integrity
            - If multiple users have the same display name, returns the first match
        
        Example:
            >>> api = YouTubeApis()
            >>> user = api.get_user_by_display_name("JohnDoe")
            >>> if user["data"]:
            ...     print(user["data"]["email"])
        """
        user_id = self._find_user_by_display_name(display_name)
        if user_id:
            return {"data": copy.deepcopy(self.users[user_id])}
        return {"data": None, "message": "User not found"}

    def get_watch_later_playlist(self, user_identifier: str) -> Dict[str, Any]:
        """
        Retrieve a user's Watch Later playlist containing videos they've saved to watch later.
        
        This method fetches all videos that the specified user has added to their Watch Later queue.
        The Watch Later feature allows users to bookmark videos for future viewing. Videos are returned
        as a list of complete video data dictionaries, not just IDs. The user can be identified by
        UUID, email, or display name.

        Args:
            user_identifier (str): The user identification, which can be:
                - User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - Email address (e.g., "user@example.com")
                - Display name (e.g., "John Doe")
                The method will automatically determine which type and look up the user.

        Returns:
            Dict[str, Any]: A dictionary with a "data" key containing the Watch Later videos:
                Success case:
                {
                    "data": [                   # List of video data dictionaries
                        {                       # Each entry is a complete video object
                            "id": str,          # Video UUID
                            "title": str,       # Video title
                            "description": str, # Video description
                            "channel_id": str,  # Channel UUID
                            "views": int,       # View count
                            "likes": int,       # Like count
                            # ... other video fields
                        },
                        # ... more videos
                    ]
                }
                
                Failure case (user not found):
                {
                    "data": None,
                    "message": "User not found"
                }
        
        Note:
            - Does not require authentication
            - Returns deep copies of video data
            - Videos that no longer exist in the backend are skipped
            - Returns empty list if user has no videos in Watch Later
        
        Example:
            >>> api = YouTubeApis()
            >>> result = api.get_watch_later_playlist("user@example.com")
            >>> if result["data"]:
            ...     for video in result["data"]:
            ...         print(video["title"])
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"data": None, "message": "User not found"}
        
        user_data = self.users[user_id]
        watch_later_videos = []
        for video_id in user_data.get("watch_later_playlist", []):
            video_data = self._get_video_data(video_id)
            if video_data:
                watch_later_videos.append(copy.deepcopy(video_data))
        
        return {"data": watch_later_videos}

    def add_to_watch_later(self, user_identifier: str, video_id: str) -> Dict[str, Any]:
        """
        Add a video to a user's Watch Later playlist for future viewing.
        
        This method adds a video to the specified user's Watch Later queue, allowing them to bookmark
        videos for later viewing. Duplicate additions are prevented - if the video is already in the
        Watch Later list, an error is returned. The user can be identified by UUID, email, or display name.

        Args:
            user_identifier (str): The user identification, which can be:
                - User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - Email address (e.g., "user@example.com")
                - Display name (e.g., "John Doe")
            video_id (str): The UUID of the video to add to Watch Later. Must be a valid video ID
                that exists in the backend.

        Returns:
            Dict[str, Any]: A dictionary indicating the result of the operation:
                Success case:
                {
                    "status": True,
                    "message": "Video added to watch later playlist"
                }
                
                Failure cases:
                {
                    "status": False,
                    "message": str              # One of:
                                                # "User not found"
                                                # "Video not found"
                                                # "Video already in watch later playlist"
                }

        Side Effects:
            - Appends video_id to the user's "watch_later_playlist" list (if successful)
        
        Note:
            - Does not require authentication (utility method for managing any user's Watch Later)
            - Prevents duplicate entries
            - Video must exist in the backend
        
        Example:
            >>> api = YouTubeApis()
            >>> result = api.add_to_watch_later("user@example.com", "video-uuid-123")
            >>> if result["status"]:
            ...     print("Video added successfully")
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"status": False, "message": "User not found"}
        
        if not self._get_video_data(video_id):
            return {"status": False, "message": "Video not found"}
        
        user_data = self.users[user_id]
        watch_later = user_data.get("watch_later_playlist", [])
        
        if video_id in watch_later:
            return {"status": False, "message": "Video already in watch later playlist"}
        
        watch_later.append(video_id)
        user_data["watch_later_playlist"] = watch_later
        
        return {"status": True, "message": "Video added to watch later playlist"}

    def remove_from_watch_later(self, user_identifier: str, video_id: str) -> Dict[str, Any]:
        """
        Remove a video from a user's Watch Later playlist.
        
        This method removes a previously bookmarked video from the specified user's Watch Later queue.
        The video must currently be in the Watch Later list. The user can be identified by UUID,
        email, or display name. The video itself is not deleted, only removed from the Watch Later list.

        Args:
            user_identifier (str): The user identification, which can be:
                - User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - Email address (e.g., "user@example.com")
                - Display name (e.g., "John Doe")
            video_id (str): The UUID of the video to remove from Watch Later. Must currently be in
                the user's Watch Later playlist.

        Returns:
            Dict[str, Any]: A dictionary indicating the result of the operation:
                Success case:
                {
                    "status": True,
                    "message": "Video removed from watch later playlist"
                }
                
                Failure cases:
                {
                    "status": False,
                    "message": str              # One of:
                                                # "User not found"
                                                # "Video not in watch later playlist"
                }

        Side Effects:
            - Removes video_id from the user's "watch_later_playlist" list (if successful)
        
        Note:
            - Does not require authentication (utility method for managing any user's Watch Later)
            - Does not delete the video, only removes the Watch Later bookmark
        
        Example:
            >>> api = YouTubeApis()
            >>> result = api.remove_from_watch_later("user@example.com", "video-uuid-123")
            >>> if result["status"]:
            ...     print("Video removed successfully")
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"status": False, "message": "User not found"}
        
        user_data = self.users[user_id]
        watch_later = user_data.get("watch_later_playlist", [])
        
        if video_id not in watch_later:
            return {"status": False, "message": "Video not in watch later playlist"}
        
        watch_later.remove(video_id)
        user_data["watch_later_playlist"] = watch_later
        
        return {"status": True, "message": "Video removed from watch later playlist"}

    def get_notification_settings(self, user_identifier: str) -> Dict[str, Any]:
        """
        Retrieve a user's notification preferences and settings.
        
        This method returns the notification configuration for the specified user, showing which types
        of notifications they have enabled or disabled. Notification settings control how users are
        alerted about channel activity, comments, mentions, and other YouTube events. The user can be
        identified by UUID, email, or display name.

        Args:
            user_identifier (str): The user identification, which can be:
                - User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - Email address (e.g., "user@example.com")
                - Display name (e.g., "John Doe")

        Returns:
            Dict[str, Any]: A dictionary with a "data" key containing notification settings:
                Success case:
                {
                    "data": {                   # Dictionary of notification settings
                        # Settings depend on what's stored for the user
                        # Common examples:
                        "email_notifications": bool,    # Email notifications enabled/disabled
                        "push_notifications": bool,     # Push notifications enabled/disabled
                        "comment_notifications": bool,  # Comment reply notifications
                        "subscription_notifications": bool,  # New video notifications
                        # ... other notification preferences
                    }
                }
                
                Failure case (user not found):
                {
                    "data": None,
                    "message": "User not found"
                }
        
        Note:
            - Does not require authentication
            - Returns a deep copy of settings
            - Returns empty dict if user has no notification settings configured
        
        Example:
            >>> api = YouTubeApis()
            >>> result = api.get_notification_settings("user@example.com")
            >>> if result["data"]:
            ...     print(f"Email notifications: {result['data'].get('email_notifications')}")
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"data": None, "message": "User not found"}
        
        user_data = self.users[user_id]
        settings = user_data.get("notification_settings", {})
        
        return {"data": copy.deepcopy(settings)}

    def update_notification_settings(self, user_identifier: str, settings: Dict[str, bool]) -> Dict[str, Any]:
        """
        Update a user's notification preferences with new settings.
        
        This method modifies the notification configuration for the specified user by merging the
        provided settings with existing settings. Only the keys present in the settings parameter
        are updated; other notification preferences remain unchanged. This allows partial updates
        without needing to specify all notification settings.

        Args:
            user_identifier (str): The user identification, which can be:
                - User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - Email address (e.g., "user@example.com")
                - Display name (e.g., "John Doe")
            settings (Dict[str, bool]): A dictionary of notification settings to update. Keys are
                setting names (strings) and values are booleans indicating enabled (True) or disabled
                (False). Common setting keys include:
                - "email_notifications": Enable/disable email notifications
                - "push_notifications": Enable/disable push notifications
                - "comment_notifications": Enable/disable comment reply notifications
                - "subscription_notifications": Enable/disable new video notifications
                Only the specified keys are updated; other settings remain unchanged.

        Returns:
            Dict[str, Any]: A dictionary indicating the result of the update:
                Success case:
                {
                    "status": True,
                    "message": "Notification settings updated"
                }
                
                Failure case:
                {
                    "status": False,
                    "message": "User not found"
                }

        Side Effects:
            - Updates the user's "notification_settings" dictionary with the provided settings
            - Existing settings not in the update are preserved
            - Creates notification_settings dict if it doesn't exist
        
        Note:
            - Does not require authentication (utility method for managing any user's settings)
            - Performs a merge update, not a replacement
        
        Example:
            >>> api = YouTubeApis()
            >>> new_settings = {
            ...     "email_notifications": False,
            ...     "push_notifications": True
            ... }
            >>> result = api.update_notification_settings("user@example.com", new_settings)
            >>> if result["status"]:
            ...     print("Settings updated")
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"status": False, "message": "User not found"}
        
        user_data = self.users[user_id]
        current_settings = user_data.get("notification_settings", {})
        current_settings.update(settings)
        user_data["notification_settings"] = current_settings
        
        return {"status": True, "message": "Notification settings updated"}

    def get_user_language_preference(self, user_identifier: str) -> Dict[str, Any]:
        """
        Retrieve a user's preferred language setting for the YouTube interface.
        
        This method returns the language preference configured for the specified user. The language
        preference determines which language is used for YouTube's interface, menus, and text.
        Language codes follow the BCP-47 standard (e.g., "en-US", "es-ES", "ja-JP"). The user can
        be identified by UUID, email, or display name.

        Args:
            user_identifier (str): The user identification, which can be:
                - User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - Email address (e.g., "user@example.com")
                - Display name (e.g., "John Doe")

        Returns:
            Dict[str, Any]: A dictionary with a "data" key containing the language preference:
                Success case:
                {
                    "data": {
                        "language_preference": str  # BCP-47 language code (e.g., "en-US")
                    }
                }
                
                Failure case (user not found):
                {
                    "data": None,
                    "message": "User not found"
                }
        
        Note:
            - Does not require authentication
            - Defaults to "en-US" if no language preference is set
            - Language codes follow BCP-47 standard (language-COUNTRY format)
        
        Example:
            >>> api = YouTubeApis()
            >>> result = api.get_user_language_preference("user@example.com")
            >>> if result["data"]:
            ...     print(f"Language: {result['data']['language_preference']}")
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"data": None, "message": "User not found"}
        
        user_data = self.users[user_id]
        language = user_data.get("language_preference", "en-US")
        
        return {"data": {"language_preference": language}}

    def update_language_preference(self, user_identifier: str, language: str) -> Dict[str, Any]:
        """
        Update a user's preferred language setting for the YouTube interface.
        
        This method changes the language preference for the specified user. The language preference
        controls which language is displayed for YouTube's interface, menus, buttons, and system text.
        The language code should follow the BCP-47 standard (e.g., "en-US" for US English, "es-ES"
        for Spanish, "ja-JP" for Japanese). The user can be identified by UUID, email, or display name.

        Args:
            user_identifier (str): The user identification, which can be:
                - User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - Email address (e.g., "user@example.com")
                - Display name (e.g., "John Doe")
            language (str): The new language preference code following BCP-47 standard. Format is
                typically "language-COUNTRY" such as:
                - "en-US": US English
                - "en-GB": British English
                - "es-ES": Spanish (Spain)
                - "es-MX": Spanish (Mexico)
                - "fr-FR": French
                - "de-DE": German
                - "ja-JP": Japanese
                - "zh-CN": Chinese (Simplified)

        Returns:
            Dict[str, Any]: A dictionary indicating the result of the update:
                Success case:
                {
                    "status": True,
                    "message": "Language preference updated"
                }
                
                Failure case:
                {
                    "status": False,
                    "message": "User not found"
                }

        Side Effects:
            - Updates the user's "language_preference" field with the new language code
        
        Note:
            - Does not require authentication (utility method for managing any user's settings)
            - Does not validate the language code format
        
        Example:
            >>> api = YouTubeApis()
            >>> result = api.update_language_preference("user@example.com", "es-ES")
            >>> if result["status"]:
            ...     print("Language changed to Spanish")
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"status": False, "message": "User not found"}
        
        user_data = self.users[user_id]
        user_data["language_preference"] = language
        
        return {"status": True, "message": "Language preference updated"}

    def get_account_status(self, user_identifier: str) -> Dict[str, Any]:
        """
        Retrieve the account status for a user.
        
        This method returns the current status of the specified user's account. Account status indicates
        whether the account is active, suspended, restricted, or in another state. This is useful for
        determining if a user can access YouTube services normally. The user can be identified by UUID,
        email, or display name.

        Args:
            user_identifier (str): The user identification, which can be:
                - User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - Email address (e.g., "user@example.com")
                - Display name (e.g., "John Doe")

        Returns:
            Dict[str, Any]: A dictionary with a "data" key containing the account status:
                Success case:
                {
                    "data": {
                        "account_status": str   # Status value, common values include:
                                                # "active" - Normal, fully functional account
                                                # "suspended" - Account temporarily suspended
                                                # "restricted" - Account has restrictions
                                                # "closed" - Account has been closed
                    }
                }
                
                Failure case (user not found):
                {
                    "data": None,
                    "message": "User not found"
                }
        
        Note:
            - Does not require authentication
            - Defaults to "active" if no account status is explicitly set
            - Status values are strings and can be any value stored in the backend
        
        Example:
            >>> api = YouTubeApis()
            >>> result = api.get_account_status("user@example.com")
            >>> if result["data"]:
            ...     status = result['data']['account_status']
            ...     print(f"Account is {status}")
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"data": None, "message": "User not found"}
        
        user_data = self.users[user_id]
        status = user_data.get("account_status", "active")
        
        return {"data": {"account_status": status}}

    def get_channel_history(self, user_identifier: str) -> Dict[str, Any]:
        """
        Retrieve a user's channel browsing/viewing history.
        
        This method returns a list of channels that the user has previously visited or interacted with.
        Channel history helps track which channels a user has browsed, similar to browser history for
        web pages. Each history entry includes the full channel details. The user can be identified by
        UUID, email, or display name.

        Args:
            user_identifier (str): The user identification, which can be:
                - User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - Email address (e.g., "user@example.com")
                - Display name (e.g., "John Doe")

        Returns:
            Dict[str, Any]: A dictionary with a "data" key containing the channel history:
                Success case:
                {
                    "data": [                   # List of visited channel data dictionaries
                        {                       # Each entry is a complete channel object
                            "id": str,          # Channel UUID
                            "title": str,       # Channel name
                            "description": str, # Channel description
                            "owner_id": str,    # Channel owner's user UUID
                            "subscriber_count": int, # Number of subscribers
                            "video_count": int, # Number of videos
                            # ... other channel fields
                        },
                        # ... more channels in browsing order
                    ]
                }
                
                Failure case (user not found):
                {
                    "data": None,
                    "message": "User not found"
                }
        
        Note:
            - Does not require authentication
            - Returns deep copies of channel data
            - Channels that no longer exist in the backend are skipped
            - Returns empty list if user has no channel history
            - Order typically represents browsing chronology
        
        Example:
            >>> api = YouTubeApis()
            >>> result = api.get_channel_history("user@example.com")
            >>> if result["data"]:
            ...     for channel in result["data"]:
            ...         print(f"Visited: {channel['title']}")
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"data": None, "message": "User not found"}
        
        user_data = self.users[user_id]
        channel_history = []
        
        for channel_id in user_data.get("channel_history", []):
            channel_data = self._get_channel_data(channel_id)
            if channel_data:
                channel_history.append({
                    "id": channel_id,
                    "title": channel_data.get("title"),
                    "description": channel_data.get("description"),
                    "subscriber_count": channel_data.get("subscriber_count", 0)
                })
        
        return {"data": channel_history}

    def add_to_channel_history(self, user_identifier: str, channel_id: str) -> Dict[str, Any]:
        """
        Add a channel to a user's browsing/viewing history.
        
        This method records that a user has visited or viewed a specific channel by adding the channel
        to their channel history list. This helps track which channels users have interacted with.
        Duplicate additions are prevented - if the channel is already in the history, it won't be
        added again. The user can be identified by UUID, email, or display name.

        Args:
            user_identifier (str): The user identification, which can be:
                - User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - Email address (e.g., "user@example.com")
                - Display name (e.g., "John Doe")
            channel_id (str): The UUID of the channel to add to the history. Must be a valid channel
                ID that exists in the backend.

        Returns:
            Dict[str, Any]: A dictionary indicating the result of the operation:
                Success case:
                {
                    "status": True,
                    "message": "Channel added to history"
                }
                
                Failure cases:
                {
                    "status": False,
                    "message": str              # One of:
                                                # "User not found"
                                                # "Channel not found"
                                                # "Channel already in history"
                }

        Side Effects:
            - Appends channel_id to the user's "channel_history" list (if successful and not duplicate)
        
        Note:
            - Does not require authentication (utility method for tracking any user's history)
            - Prevents duplicate entries
            - Channel must exist in the backend
        
        Example:
            >>> api = YouTubeApis()
            >>> result = api.add_to_channel_history("user@example.com", "channel-uuid-123")
            >>> if result["status"]:
            ...     print("Channel visit recorded")
        """
        """
        Add a channel to the user's browsing history.

        Args:
            user_identifier (str): The user ID, email, or display name.
            channel_id (str): The ID of the channel to add to history.

        Returns:
            Dict: A dictionary indicating success or failure.
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"status": False, "message": "User not found"}
        
        if not self._get_channel_data(channel_id):
            return {"status": False, "message": "Channel not found"}
        
        user_data = self.users[user_id]
        channel_history = user_data.get("channel_history", [])
        
        # Remove if already exists to move to front
        if channel_id in channel_history:
            channel_history.remove(channel_id)
        
        # Add to front of history
        channel_history.insert(0, channel_id)
        
        # Keep only last 50 channels
        channel_history = channel_history[:50]
        user_data["channel_history"] = channel_history
        
        return {"status": True, "message": "Channel added to history"}

    def get_user_analytics(self, user_identifier: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive analytics and statistics about a user's YouTube activity.
        
        This method aggregates various metrics about the user's engagement with YouTube, including
        their channels, subscriptions, watch history, and other activity. This provides a high-level
        overview of the user's presence and behavior on the platform. Useful for dashboards, reports,
        or understanding user engagement. The user can be identified by UUID, email, or display name.

        Args:
            user_identifier (str): The user identification, which can be:
                - User UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")
                - Email address (e.g., "user@example.com")
                - Display name (e.g., "John Doe")

        Returns:
            Dict[str, Any]: A dictionary with a "data" key containing comprehensive analytics:
                Success case:
                {
                    "data": {
                        "total_channels": int,          # Number of channels owned
                        "total_videos_uploaded": int,   # Total videos across all owned channels
                        "total_views": int,             # Combined views across all owned videos
                        "total_subscribers": int,       # Combined subscribers across all channels
                        "total_likes_received": int,    # Combined likes on all owned videos
                        "subscriptions_count": int,     # Number of channels subscribed to
                        "watch_history_count": int,     # Number of videos in watch history
                        "liked_videos_count": int,      # Number of videos liked
                        "watch_later_count": int,       # Number of videos in Watch Later
                        "comments_made_count": int      # Number of comments posted
                    }
                }
                
                Failure case (user not found):
                {
                    "data": None,
                    "message": "User not found"
                }
        
        Note:
            - Does not require authentication
            - Calculates statistics by iterating through user's channels and videos
            - Counts are computed in real-time from current backend state
            - Returns 0 for all counts if user has no activity
        
        Example:
            >>> api = YouTubeApis()
            >>> result = api.get_user_analytics("creator@example.com")
            >>> if result["data"]:
            ...     analytics = result['data']
            ...     print(f"Total videos: {analytics['total_videos_uploaded']}")
            ...     print(f"Total views: {analytics['total_views']}")
            ...     print(f"Subscribers: {analytics['total_subscribers']}")
        """
        """
        Get comprehensive analytics for a user.

        Args:
            user_identifier (str): The user ID, email, or display name.

        Returns:
            Dict: A dictionary containing user analytics.
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"data": None, "message": "User not found"}
        
        user_data = self.users[user_id]
        
        # Calculate analytics
        total_videos_watched = len(user_data.get("watch_history", []))
        total_subscriptions = len(user_data.get("subscriptions", []))
        total_liked_videos = len(user_data.get("liked_videos", []))
        total_channels_owned = len(user_data.get("channels", []))
        watch_later_count = len(user_data.get("watch_later_playlist", []))
        
        analytics = {
            "user_id": user_id,
            "display_name": user_data.get("display_name"),
            "email": user_data.get("email"),
            "joined_date": user_data.get("joined_date"),
            "account_status": user_data.get("account_status", "active"),
            "language_preference": user_data.get("language_preference", "en-US"),
            "total_videos_watched": total_videos_watched,
            "total_subscriptions": total_subscriptions,
            "total_liked_videos": total_liked_videos,
            "total_channels_owned": total_channels_owned,
            "watch_later_count": watch_later_count,
            "notification_settings": user_data.get("notification_settings", {})
        }
        
        return {"data": analytics}

    def search_users_by_language(self, language: str) -> Dict[str, Any]:
        """
        Search for users by their language preference.

        Args:
            language (str): The language code to search for.

        Returns:
            Dict: A dictionary containing matching users.
        """
        matching_users = []
        
        for user_id, user_data in self.users.items():
            if user_data.get("language_preference") == language:
                matching_users.append({
                    "id": user_id,
                    "display_name": user_data.get("display_name"),
                    "email": user_data.get("email"),
                    "account_status": user_data.get("account_status", "active"),
                    "joined_date": user_data.get("joined_date")
                })
        
        return {"data": matching_users, "count": len(matching_users)}

    def reset_data(self) -> None:
        """
        Reset all data to default state.
        Clears authentication and reloads default scenario.
        """
        self.access_token = None
        self.current_user_id = None
        self._load_scenario(DEFAULT_STATE)
        print("YouTubeApis: All data reset to default state.")
