# Inspired by https://developers.google.com/youtube/v3/docs

from datetime import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("XApis")

class XApis:
    """
    An API class for simulating X (formerly Twitter) operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the XApis instance, setting up the in-memory data stores and loading the default scenario.
        
        This constructor creates empty dictionaries for users, posts (tweets), and direct messages,
        all keyed by UUID. It also initializes authentication state (access_token and current_user_id) to None.
        Finally, it loads the default scenario data to populate the backend with initial test data.
        
        The instance maintains several data structures:
        - users: Maps user UUIDs to user profile data including username, bio, followers, following, posts, etc.
        - posts: Maps post/tweet UUIDs to tweet data including text, author, metrics, timestamps, etc.
        - direct_messages: Maps conversation UUIDs to DM conversation data including participants and messages
        - access_token: Stores the current OAuth 2.0 access token (None when not authenticated)
        - current_user_id: Stores the UUID of the currently authenticated user (None when not authenticated)
        """
        self._api_description = "This tool simulates X (formerly Twitter) social media functionalities."
        self.users: Dict[str, Any] = {} # Keyed by user UUID
        self.posts: Dict[str, Any] = {} # Keyed by post UUID
        self.direct_messages: Dict[str, Any] = {} # Keyed by DM conversation UUID
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
                - "users" (Dict[str, Dict]): User data keyed by UUID, containing profile info, followers, posts, etc.
                - "posts" (Dict[str, Dict]): Tweet/post data keyed by UUID, containing text, metrics, timestamps, etc.
                - "direct_messages" (Dict[str, Dict]): DM conversation data keyed by UUID, with participants and messages
                If any key is missing, an empty dictionary is used as the default.
        
        Returns:
            None: This method modifies the instance state in-place and returns nothing.
        
        Side Effects:
            - Replaces all existing users, posts, and direct_messages data
            - Prints a confirmation message to stdout
            - Does not affect authentication state (access_token, current_user_id)
        """
        # Create deep copy to ensure the original DEFAULT_STATE is not modified
        self.users = copy.deepcopy(scenario.get("users", {}))
        self.posts = copy.deepcopy(scenario.get("posts", {}))
        self.direct_messages = copy.deepcopy(scenario.get("direct_messages", {}))
        print("XApis: Loaded scenario with UUIDs for users, posts, and DMs.")

    def authenticate(self, access_token: str) -> Dict[str, Any]:
        """
        Authenticate with X (Twitter) API using an OAuth 2.0 access token, establishing a user session.
        
        This method validates the access token format, extracts the email address from it, looks up the
        corresponding user in the backend, and sets the authentication state for subsequent API calls.
        Once authenticated, all methods that require authentication will use this authenticated user's identity.

        Args:
            access_token (str): OAuth 2.0 Bearer token in the format "token_{email}", where {email} is
                the email address of the user to authenticate. For example, "token_user@example.com".
                The token must start with "token_" prefix and contain a valid email address that exists
                in the backend's user database.

        Returns:
            Dict[str, Any]: A dictionary containing the authenticated user's profile data with the following structure:
                {
                    "id": str,              # The user's unique UUID
                    "username": str,        # The user's X handle (without @ symbol)
                    "name": str,            # The user's display name
                    "email": str            # The user's email address
                }

        Raises:
            Exception: If the access token format is invalid (doesn't start with "token_" or is empty)
            Exception: If no user is found in the backend with the email address extracted from the token
        
        Side Effects:
            - Sets self.access_token to the provided token
            - Sets self.current_user_id to the UUID of the authenticated user
            - All subsequent method calls will use this authentication context
        
        Example:
            >>> api = XApis()
            >>> profile = api.authenticate("token_john@example.com")
            >>> print(profile["username"])
            'johndoe'
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
            "username": user_data.get("username"),
            "name": user_data.get("name"),
            "email": user_data.get("email")
        }
    
    def _ensure_authenticated(self) -> None:
        """
        Ensures that the user is authenticated before accessing protected resources.
        
        This internal helper method checks whether authenticate() has been called successfully
        by verifying that both access_token and current_user_id are set. It should be called
        at the beginning of any method that requires authentication to access protected resources.
        This prevents unauthorized access to user-specific operations.

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
        identifier for users, posts, DM conversations, and other entities in the backend.
        UUID v4 uses random generation and provides sufficient uniqueness for this simulation.
        
        Returns:
            str: A string representation of a UUID v4, formatted as a 36-character string with hyphens
                (e.g., "550e8400-e29b-41d4-a716-446655440000"). Each call produces a different UUID
                with extremely high probability of uniqueness.
        """
        return str(uuid.uuid4())

    def _get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to retrieve a user's complete data dictionary based on their UUID.
        
        Args:
            user_id (str): The UUID of the user to retrieve.
        
        Returns:
            Optional[Dict[str, Any]]: The user's data dictionary if found, containing keys such as
                "id", "username", "name", "email", "bio", "followers", "following", "posts",
                "liked_posts", "is_verified", etc. Returns None if the user_id is not found.
        """
        return self.users.get(user_id)

    def _get_user_posts_data(self, user_id: str) -> Optional[List[str]]:
        """
        Helper method to retrieve a user's list of post/tweet IDs.
        
        Args:
            user_id (str): The UUID of the user whose posts to retrieve.
        
        Returns:
            Optional[List[str]]: A list of post UUIDs if the user exists, or None if the user is not found.
        """
        user_data = self._get_user_data(user_id)
        return user_data.get("posts") if user_data else None

    def _get_user_direct_messages_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to retrieve all DM conversations that include a specific user.
        
        This method filters the global direct_messages dictionary to find all conversations where
        the specified user is a participant.
        
        Args:
            user_id (str): The UUID of the user whose DM conversations to retrieve.
        
        Returns:
            Dict[str, Any]: A dictionary mapping conversation UUIDs to conversation data for all
                conversations where the user is a participant. Returns an empty dict if the user
                has no conversations.
        """
        # This structure needs careful handling as DMs are global, but filtered by user
        # For this, we'll iterate through global DMs to find user's conversations
        return {
            conv_id: conv_data for conv_id, conv_data in self.direct_messages.items()
            if user_id in conv_data.get("participants", [])
        }

    def _update_user_data(self, user_id: str, key: str, value: Any) -> bool:
        """
        Helper method to update a specific key-value pair in a user's data dictionary.
        
        Args:
            user_id (str): The UUID of the user whose data should be updated.
            key (str): The dictionary key to update (e.g., "name", "bio", "followers").
            value (Any): The new value to assign to the specified key. Can be any type.
        
        Returns:
            bool: True if the user was found and the update was successful, False if the user_id
                does not exist in the backend.
        """
        if user_id in self.users:
            self.users[user_id][key] = value
            return True
        return False
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive profile information for the authenticated user.
        
        This method returns detailed profile data including basic information, verification status,
        and public engagement metrics. The metrics are calculated in real-time from the backend state,
        providing current follower counts, tweet counts, and engagement statistics.

        Returns:
            Dict[str, Any]: A dictionary containing the user's complete profile in X API v2 format:
                {
                    "id": str,                      # User UUID
                    "username": str,                # X handle (without @ symbol)
                    "name": str,                    # Display name
                    "email": str,                   # Email address
                    "bio": str,                     # User biography/description
                    "profile_picture_url": str,    # URL to profile image
                    "created_at": str,              # Account creation timestamp (ISO 8601)
                    "verified": bool,               # Whether the account is verified
                    "public_metrics": {
                        "followers_count": int,     # Number of followers
                        "following_count": int,     # Number of accounts following
                        "tweet_count": int,         # Number of tweets posted
                        "like_count": int           # Number of tweets liked
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> profile = api.get_user_profile()
            >>> print(f"{profile['name']} (@{profile['username']})")
            >>> print(f"Followers: {profile['public_metrics']['followers_count']}")
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        # Return enhanced profile with backend metadata
        return {
            "id": user_data.get("id"),
            "username": user_data.get("username"),
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "bio": user_data.get("bio"),
            "profile_picture_url": user_data.get("profile_picture_url"),
            "created_at": user_data.get("joined_date"),
            "verified": user_data.get("is_verified", False),
            "public_metrics": {
                "followers_count": len(user_data.get("followers", [])),
                "following_count": len(user_data.get("following", [])),
                "tweet_count": len(user_data.get("posts", [])),
                "like_count": len(user_data.get("liked_posts", []))
            }
        }

    def get_followers(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve a paginated list of users who follow the authenticated user.
        
        This method returns basic profile information for each follower, including their username,
        display name, and verification status. Results are paginated using limit and offset parameters
        for efficient handling of large follower lists.

        Args:
            limit (int, optional): Maximum number of followers to return in a single response.
                Defaults to 20. Controls the page size for pagination. Typical values are 10-100.
            offset (int, optional): Number of followers to skip before starting to return results.
                Defaults to 0 (start from the beginning). Use this to retrieve subsequent pages.
                For example, offset=20 with limit=20 retrieves the second page of results.

        Returns:
            Dict[str, Any]: A dictionary containing paginated follower data:
                {
                    "data": [                       # List of follower profiles
                        {
                            "id": str,              # Follower's UUID
                            "username": str,        # Follower's X handle
                            "name": str,            # Follower's display name
                            "verified": bool        # Whether follower is verified
                        },
                        # ... more followers
                    ],
                    "pagination": {
                        "limit": int,               # Number of results per page
                        "offset": int,              # Starting position in the list
                        "total": int                # Total number of followers
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> # Get first page of followers
            >>> page1 = api.get_followers(limit=10, offset=0)
            >>> print(f"Total followers: {page1['pagination']['total']}")
            >>> # Get next page
            >>> page2 = api.get_followers(limit=10, offset=10)
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        follower_uuids = user_data.get("followers", [])
        paginated_followers = follower_uuids[offset:offset + limit]
        
        followers_details = [
            {
                "id": self.users[f_id]["id"],
                "username": self.users[f_id]["username"],
                "name": self.users[f_id]["name"],
                "verified": self.users[f_id].get("is_verified", False)
            }
            for f_id in paginated_followers if f_id in self.users
        ]
        
        return {
            "data": followers_details,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(follower_uuids)
            }
        }

    def get_following(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve a paginated list of users that the authenticated user is following.
        
        This method returns basic profile information for each account the user follows, including
        username, display name, and verification status. Results are paginated using limit and offset
        parameters for efficient handling of large following lists.

        Args:
            limit (int, optional): Maximum number of users to return in a single response.
                Defaults to 20. Controls the page size for pagination. Typical values are 10-100.
            offset (int, optional): Number of users to skip before starting to return results.
                Defaults to 0 (start from the beginning). Use this to retrieve subsequent pages.
                For example, offset=20 with limit=20 retrieves the second page of results.

        Returns:
            Dict[str, Any]: A dictionary containing paginated following data:
                {
                    "data": [                       # List of followed user profiles
                        {
                            "id": str,              # User's UUID
                            "username": str,        # User's X handle
                            "name": str,            # User's display name
                            "verified": bool        # Whether user is verified
                        },
                        # ... more users
                    ],
                    "pagination": {
                        "limit": int,               # Number of results per page
                        "offset": int,              # Starting position in the list
                        "total": int                # Total number of accounts following
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> following = api.get_following(limit=50)
            >>> print(f"Following {following['pagination']['total']} accounts")
            >>> for user in following['data']:
            ...     print(f"@{user['username']}")
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        following_uuids = user_data.get("following", [])
        paginated_following = following_uuids[offset:offset + limit]
        
        following_details = [
            {
                "id": self.users[f_id]["id"],
                "username": self.users[f_id]["username"],
                "name": self.users[f_id]["name"],
                "verified": self.users[f_id].get("is_verified", False)
            }
            for f_id in paginated_following if f_id in self.users
        ]
        
        return {
            "data": following_details,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(following_uuids)
            }
        }

    def get_liked_tweets(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve a paginated list of tweets that the authenticated user has liked.
        
        This method returns complete tweet data for each liked tweet, including the tweet text,
        author information, timestamps, and public metrics. Liked tweets are returned with pagination
        support to handle users with many likes efficiently.

        Args:
            limit (int, optional): Maximum number of tweets to return in a single response.
                Defaults to 20. Controls the page size for pagination. Typical values are 10-100.
            offset (int, optional): Number of tweets to skip before starting to return results.
                Defaults to 0 (start from the beginning). Use this to retrieve subsequent pages.
                For example, offset=20 with limit=20 retrieves the second page of liked tweets.

        Returns:
            Dict[str, Any]: A dictionary containing paginated liked tweet data:
                {
                    "data": [                       # List of complete tweet objects
                        {
                            "id": str,              # Tweet UUID
                            "author_id": str,       # Author's user UUID
                            "text": str,            # Tweet text content
                            "created_at": str,      # Tweet creation timestamp (ISO 8601)
                            "lang": str,            # Language code (e.g., "en")
                            "public_metrics": {     # Engagement metrics
                                "retweet_count": int,
                                "reply_count": int,
                                "like_count": int,
                                "quote_count": int,
                                "impression_count": int
                            },
                            # ... other tweet fields
                        },
                        # ... more tweets
                    ],
                    "pagination": {
                        "limit": int,               # Number of results per page
                        "offset": int,              # Starting position in the list
                        "total": int                # Total number of liked tweets
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
        
        Note:
            - Returns deep copies of tweet data to prevent external modifications
            - Tweets that have been deleted are automatically skipped
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> likes = api.get_liked_tweets(limit=10)
            >>> print(f"Total likes: {likes['pagination']['total']}")
            >>> for tweet in likes['data']:
            ...     print(f"Liked: {tweet['text'][:50]}...")
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        liked_post_uuids = user_data.get("liked_posts", [])
        paginated_likes = liked_post_uuids[offset:offset + limit]
        
        liked_posts_details = [
            copy.deepcopy(self.posts[p_id]) for p_id in paginated_likes if p_id in self.posts
        ]
        
        return {
            "data": liked_posts_details,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(liked_post_uuids)
            }
        }

    def create_tweet(self, text: str) -> Dict[str, Any]:
        """
        Create and publish a new tweet for the authenticated user.
        
        This method creates a new tweet with the provided text content and associates it with the
        authenticated user's account. The tweet is initialized with zero engagement metrics and a
        current timestamp. The user's tweet count and API usage statistics are automatically updated.

        Args:
            text (str): The content of the tweet. While X (Twitter) typically limits tweets to 280
                characters, this simulation does not enforce a character limit. The text should
                contain the message you want to post.

        Returns:
            Dict[str, Any]: A deep copy of the newly created tweet data in X API v2 format:
                {
                    "id": str,                      # Newly generated tweet UUID
                    "author_id": str,               # UUID of the authenticated user
                    "text": str,                    # The tweet text content
                    "created_at": str,              # Current timestamp (ISO 8601 with milliseconds)
                    "lang": str,                    # Language code (default: "en")
                    "possibly_sensitive": bool,     # Content warning flag (default: False)
                    "edit_history_tweet_ids": [str], # List containing this tweet's ID
                    "public_metrics": {             # Engagement metrics (all initialized to 0)
                        "retweet_count": 0,
                        "reply_count": 0,
                        "like_count": 0,
                        "quote_count": 0,
                        "impression_count": 0
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
        
        Side Effects:
            - Creates a new tweet entry in self.posts dictionary
            - Appends the new tweet UUID to the user's "posts" list
            - Increments the user's "api_usage.posts_created" counter
            - Prints a confirmation message to stdout with tweet ID and username
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> tweet = api.create_tweet("Hello, World! This is my first tweet.")
            >>> print(f"Tweet posted with ID: {tweet['id']}")
            >>> print(f"Tweet text: {tweet['text']}")
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")

        post_uuid = self._generate_unique_id()
        new_post = {
            "id": post_uuid,
            "author_id": self.current_user_id,
            "text": text,
            "created_at": datetime.now().isoformat(timespec='milliseconds') + "Z",
            "lang": "en",
            "possibly_sensitive": False,
            "edit_history_tweet_ids": [post_uuid],
            "public_metrics": {
                "retweet_count": 0,
                "reply_count": 0,
                "like_count": 0,
                "quote_count": 0,
                "impression_count": 0
            }
        }
        self.posts[post_uuid] = new_post
        user_data["posts"].append(post_uuid)
        user_data["api_usage"]["posts_created"] = user_data["api_usage"].get("posts_created", 0) + 1
        
        print(f"Tweet created: ID={post_uuid} by {user_data['username']}")
        return copy.deepcopy(new_post)

    def delete_tweet(self, tweet_id: str) -> None:
        """
        Permanently delete a tweet. Only the tweet's author can delete their own tweets.
        
        This method removes a tweet from the backend and performs cascading cleanup by removing
        all references to the tweet from the author's post list and from all users' liked tweets
        lists. This simulates X's behavior of completely removing a tweet and its associations.

        Args:
            tweet_id (str): The UUID of the tweet to delete. Must be a valid tweet ID that exists
                in the backend and is owned by the authenticated user.

        Returns:
            None: This method returns nothing on success.

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If the specified tweet_id does not exist in the backend
            Exception: If the authenticated user is not the author of the tweet (authorization failure)
        
        Side Effects:
            - Removes the tweet entry from self.posts dictionary
            - Removes tweet_id from the author's "posts" list
            - Removes tweet_id from all users' "liked_posts" lists
            - Prints a confirmation message to stdout
        
        Note:
            This is a destructive operation that cannot be undone. All engagement metrics
            (likes, retweets, replies) are permanently lost.
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> tweet = api.create_tweet("Test tweet")
            >>> api.delete_tweet(tweet["id"])
            # Prints: Tweet deleted: ID={tweet_id}
        """
        self._ensure_authenticated()
        
        post = self.posts.get(tweet_id)
        if not post:
            raise Exception("Tweet not found")
        
        if post["author_id"] != self.current_user_id:
            raise Exception("Not authorized to delete this tweet")

        if tweet_id in self.posts:
            del self.posts[tweet_id]
            # Remove from author's list of posts
            if self.current_user_id in self.users and tweet_id in self.users[self.current_user_id].get("posts", []):
                self.users[self.current_user_id]["posts"].remove(tweet_id)
            # Remove from any user's liked_posts
            for u_data in self.users.values():
                if tweet_id in u_data.get("liked_posts", []):
                    u_data["liked_posts"].remove(tweet_id)
            
            print(f"Tweet deleted: ID={tweet_id}")
        else:
            raise Exception("Tweet not found or internal error")

    def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific tweet by its ID. This is a public endpoint.
        
        This method returns comprehensive tweet data including text content, author information,
        timestamps, and engagement metrics. No authentication is required as this simulates X's
        public tweet viewing capability.

        Args:
            tweet_id (str): The UUID of the tweet to retrieve. Must be a valid tweet ID that exists
                in the backend.

        Returns:
            Dict[str, Any]: A deep copy of the tweet's data in X API v2 format:
                {
                    "id": str,                      # Tweet UUID
                    "author_id": str,               # Author's user UUID
                    "text": str,                    # Tweet text content
                    "created_at": str,              # Tweet creation timestamp (ISO 8601)
                    "lang": str,                    # Language code (e.g., "en")
                    "possibly_sensitive": bool,     # Content warning flag
                    "edit_history_tweet_ids": [str], # Edit history (list of IDs)
                    "public_metrics": {             # Current engagement metrics
                        "retweet_count": int,
                        "reply_count": int,
                        "like_count": int,
                        "quote_count": int,
                        "impression_count": int
                    }
                }

        Raises:
            Exception: If the specified tweet_id does not exist in the backend
        
        Note:
            - This method does NOT require authentication
            - Returns a deep copy to prevent external modifications to backend state
        
        Example:
            >>> api = XApis()
            >>> tweet = api.get_tweet("some-tweet-uuid")
            >>> print(f"{tweet['text']}")
            >>> print(f"Likes: {tweet['public_metrics']['like_count']}")
        """
        post_data = self.posts.get(tweet_id)
        if not post_data:
            raise Exception("Tweet not found")
        
        return copy.deepcopy(post_data)

    def get_user_tweets(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve all tweets created by the authenticated user with pagination and sorting.
        
        This method returns the authenticated user's complete tweet history, sorted by creation time
        with the most recent tweets first (reverse chronological order). Results are paginated to
        efficiently handle users with many tweets.

        Args:
            limit (int, optional): Maximum number of tweets to return in a single response.
                Defaults to 20. Controls the page size for pagination. Typical values are 10-100.
            offset (int, optional): Number of tweets to skip before starting to return results.
                Defaults to 0 (start from the most recent). Use this to retrieve older tweets.
                For example, offset=20 with limit=20 retrieves the second page of tweets.

        Returns:
            Dict[str, Any]: A dictionary containing paginated tweet data:
                {
                    "data": [                       # List of complete tweet objects (sorted newest first)
                        {
                            "id": str,              # Tweet UUID
                            "author_id": str,       # Authenticated user's UUID
                            "text": str,            # Tweet text content
                            "created_at": str,      # Tweet creation timestamp (ISO 8601)
                            "public_metrics": {     # Engagement metrics
                                "retweet_count": int,
                                "reply_count": int,
                                "like_count": int,
                                "quote_count": int,
                                "impression_count": int
                            },
                            # ... other tweet fields
                        },
                        # ... more tweets
                    ],
                    "pagination": {
                        "limit": int,               # Number of results per page
                        "offset": int,              # Starting position in the sorted list
                        "total": int                # Total number of tweets by this user
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
        
        Note:
            - Tweets are sorted by created_at in reverse chronological order (newest first)
            - Deleted tweets are automatically skipped
            - Returns deep copies of tweet data
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> tweets = api.get_user_tweets(limit=5)
            >>> print(f"Your {tweets['pagination']['total']} tweets:")
            >>> for tweet in tweets['data']:
            ...     print(f"- {tweet['text']}")
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")

        user_post_uuids = user_data.get("posts", [])
        user_posts = [
            copy.deepcopy(self.posts[p_id]) for p_id in user_post_uuids if p_id in self.posts
        ]
        # Sort by creation time, most recent first
        user_posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        paginated_posts = user_posts[offset:offset + limit]
        
        return {
            "data": paginated_posts,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(user_posts)
            }
        }

    def like_tweet(self, tweet_id: str) -> None:
        """
        Like a specific tweet, adding it to the user's liked tweets and incrementing the like count.
        
        This method adds the tweet to the authenticated user's list of liked tweets and increments
        the tweet's like_count metric. If the user has already liked the tweet, an exception is raised
        to prevent duplicate likes.

        Args:
            tweet_id (str): The UUID of the tweet to like. Must be a valid tweet ID that exists
                in the backend.

        Returns:
            None: This method returns nothing on success.

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
            Exception: If the specified tweet_id does not exist in the backend
            Exception: If the user has already liked this tweet (duplicate like prevention)
        
        Side Effects:
            - Appends tweet_id to the user's "liked_posts" list
            - Increments the tweet's "public_metrics.like_count" by 1
            - Initializes public_metrics dict if it doesn't exist on the tweet
            - Prints a confirmation message to stdout with tweet ID and username
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> api.like_tweet("some-tweet-uuid")
            # Prints: Tweet liked: ID=some-tweet-uuid by username
        """
        self._ensure_authenticated()
        
        user = self._get_user_data(self.current_user_id)
        post = self.posts.get(tweet_id)
        
        if not user:
            raise Exception("User data not found")
        if not post:
            raise Exception("Tweet not found")

        if tweet_id in user.get("liked_posts", []):
            raise Exception("Tweet already liked by this user")
        
        user.setdefault("liked_posts", []).append(tweet_id)
        
        # Update public metrics
        if "public_metrics" not in post:
            post["public_metrics"] = {"retweet_count": 0, "reply_count": 0, "like_count": 0, "quote_count": 0, "impression_count": 0}
        post["public_metrics"]["like_count"] = post["public_metrics"].get("like_count", 0) + 1
        
        print(f"Tweet liked: ID={tweet_id} by {user['username']}")

    def unlike_tweet(self, tweet_id: str) -> None:
        """
        Remove a like from a specific tweet that was previously liked.
        
        This method removes the tweet from the authenticated user's list of liked tweets and decrements
        the tweet's like_count metric. The user must have previously liked the tweet, otherwise an
        exception is raised.

        Args:
            tweet_id (str): The UUID of the tweet to unlike. Must be a valid tweet ID that exists
                in the backend and is currently liked by the user.

        Returns:
            None: This method returns nothing on success.

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
            Exception: If the specified tweet_id does not exist in the backend
            Exception: If the user has not liked this tweet (cannot unlike what wasn't liked)
        
        Side Effects:
            - Removes tweet_id from the user's "liked_posts" list
            - Decrements the tweet's "public_metrics.like_count" by 1 (minimum 0)
            - Prints a confirmation message to stdout with tweet ID and username
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> api.like_tweet("some-tweet-uuid")  # Like it first
            >>> api.unlike_tweet("some-tweet-uuid")  # Then unlike it
            # Prints: Tweet unliked: ID=some-tweet-uuid by username
        """
        self._ensure_authenticated()
        
        user = self._get_user_data(self.current_user_id)
        post = self.posts.get(tweet_id)
        
        if not user:
            raise Exception("User data not found")
        if not post:
            raise Exception("Tweet not found")

        if tweet_id not in user.get("liked_posts", []):
            raise Exception("Tweet not liked by this user")
        
        user.setdefault("liked_posts", []).remove(tweet_id)
        
        # Update public metrics
        if "public_metrics" in post:
            post["public_metrics"]["like_count"] = max(0, post["public_metrics"].get("like_count", 0) - 1)
        
        print(f"Tweet unliked: ID={tweet_id} by {user['username']}")

    def get_dm_conversations(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve all direct message conversations for the authenticated user with pagination.
        
        This method returns a list of all DM conversations where the authenticated user is a participant.
        Each conversation entry includes the conversation ID, participant usernames, and a snippet of
        the last message. Results are paginated to handle users with many conversations.

        Args:
            limit (int, optional): Maximum number of conversations to return in a single response.
                Defaults to 20. Controls the page size for pagination. Typical values are 10-50.
            offset (int, optional): Number of conversations to skip before starting to return results.
                Defaults to 0 (start from the beginning). Use this to retrieve subsequent pages.
                For example, offset=20 with limit=20 retrieves the second page of conversations.

        Returns:
            Dict[str, Any]: A dictionary containing paginated conversation data:
                {
                    "data": [                           # List of conversation summaries
                        {
                            "conversation_id": str,     # Conversation UUID
                            "participants": [str],      # List of participant usernames
                            "last_message_snippet": str # Text of the most recent message or None
                        },
                        # ... more conversations
                    ],
                    "pagination": {
                        "limit": int,                   # Number of results per page
                        "offset": int,                  # Starting position in the list
                        "total": int                    # Total number of conversations
                    }
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If the authenticated user is not found in the backend
        
        Note:
            - Only returns conversations where the user is a participant
            - Messages within each conversation are sorted by timestamp to find the last message
            - Participant usernames are resolved from user IDs
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> conversations = api.get_dm_conversations(limit=10)
            >>> print(f"You have {conversations['pagination']['total']} conversations")
            >>> for conv in conversations['data']:
            ...     print(f"With: {', '.join(conv['participants'])}")
            ...     print(f"Last: {conv['last_message_snippet']}")
        """
        self._ensure_authenticated()
        
        if self.current_user_id not in self.users:
            raise Exception("User not found")

        user_conversations = []
        for conv_id, conv_data in self.direct_messages.items():
            if self.current_user_id in conv_data.get("participants", []):
                # Get participant details (usernames)
                participant_usernames = []
                for p_uuid in conv_data["participants"]:
                    p_data = self.users.get(p_uuid)
                    if p_data:
                        participant_usernames.append(p_data["username"])
                
                # Get the last message
                last_message = None
                if conv_data["messages"]:
                    # Ensure messages are sorted by timestamp for correct "last message"
                    sorted_messages = sorted(conv_data["messages"], key=lambda msg: msg.get("created_at", ""))
                    last_message = sorted_messages[-1].get("text", "")

                user_conversations.append({
                    "conversation_id": conv_id,
                    "participants": participant_usernames,
                    "last_message_snippet": last_message
                })
        
        # Pagination
        paginated_conversations = user_conversations[offset:offset + limit]
        
        return {
            "data": paginated_conversations,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(user_conversations)
            }
        }

    def get_dm_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Retrieve all messages within a specific DM conversation. Requires user to be a participant.
        
        This method returns the complete conversation data including all messages in chronological order.
        The authenticated user must be a participant in the conversation to access it, ensuring privacy.

        Args:
            conversation_id (str): The UUID of the conversation to retrieve. Must be a valid conversation
                ID that exists in the backend and includes the authenticated user as a participant.

        Returns:
            Dict[str, Any]: A deep copy of the conversation data with sorted messages:
                {
                    "id": str,                      # Conversation UUID
                    "participants": [str],          # List of participant user UUIDs
                    "messages": [                   # List of messages (sorted by created_at)
                        {
                            "id": str,              # Message UUID
                            "sender_id": str,       # Sender's user UUID
                            "text": str,            # Message text content
                            "created_at": str       # Message timestamp (ISO 8601)
                        },
                        # ... more messages in chronological order
                    ]
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If the specified conversation_id does not exist in the backend
            Exception: If the authenticated user is not a participant in this conversation (authorization failure)
        
        Note:
            - Messages are sorted by created_at timestamp in ascending order (oldest first)
            - Returns a deep copy to prevent external modifications to backend state
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> conversation = api.get_dm_conversation("conversation-uuid")
            >>> print(f"Conversation with {len(conversation['participants'])} participants")
            >>> for msg in conversation['messages']:
            ...     print(f"{msg['sender_id']}: {msg['text']}")
        """
        self._ensure_authenticated()
        
        conv_data = self.direct_messages.get(conversation_id)
        if not conv_data:
            raise Exception("Conversation not found")
        
        # Verify user is participant
        if self.current_user_id not in conv_data.get("participants", []):
            raise Exception("Not authorized to view this conversation")
        
        # Sort messages by timestamp
        sorted_messages = sorted(conv_data.get("messages", []), key=lambda msg: msg.get("created_at", ""))
        conversation_copy = copy.deepcopy(conv_data)
        conversation_copy["messages"] = sorted_messages
        
        return conversation_copy

    def send_dm(self, recipient_id: str, text: str) -> Dict[str, Any]:
        """
        Send a direct message to another user. Creates a new conversation if one doesn't exist.
        
        This method sends a DM to the specified recipient. If no existing conversation exists between
        the authenticated user and the recipient, a new conversation is automatically created. If a
        conversation already exists, the message is added to it. The sender's API usage statistics
        are updated.

        Args:
            recipient_id (str): The UUID of the user to send the message to. Must be a valid user ID
                that exists in the backend. Can be the same as the sender for self-messaging.
            text (str): The content of the direct message. Can be any length in this simulation
                (real X has DM length limits).

        Returns:
            Dict[str, Any]: A deep copy of the updated conversation data:
                {
                    "id": str,                      # Conversation UUID (existing or newly created)
                    "participants": [str],          # Sorted list of participant user UUIDs
                    "messages": [                   # All messages in the conversation
                        {
                            "id": str,              # Message UUID
                            "sender_id": str,       # Sender's user UUID
                            "text": str,            # Message text content
                            "created_at": str       # Message timestamp (ISO 8601)
                        },
                        # ... including the newly sent message
                    ]
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If the specified recipient_id does not exist in the backend
        
        Side Effects:
            - Creates a new conversation in self.direct_messages if none exists between the users
            - Appends the new message to the conversation's "messages" list
            - Increments the sender's "api_usage.dms_sent" counter
            - Prints a confirmation message to stdout with conversation ID and usernames
        
        Note:
            - Participants list is sorted consistently to ensure the same conversation is found/created
              regardless of who initiates it
            - Each message gets a unique UUID
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> conversation = api.send_dm("recipient-uuid", "Hello, how are you?")
            >>> print(f"Conversation ID: {conversation['id']}")
            >>> print(f"Total messages: {len(conversation['messages'])}")
        """
        self._ensure_authenticated()
        
        if recipient_id not in self.users:
            raise Exception("Recipient user not found")

        # Find existing conversation or create a new one
        conversation_id = None
        for conv_id, conv_data in self.direct_messages.items():
            participants = set(conv_data.get("participants", []))
            if participants == {self.current_user_id, recipient_id}:
                conversation_id = conv_id
                break

        if not conversation_id:
            conversation_id = self._generate_unique_id()
            self.direct_messages[conversation_id] = {
                "id": conversation_id,
                "participants": sorted([self.current_user_id, recipient_id]), # Ensure consistent order
                "messages": []
            }
        
        new_message = {
            "id": self._generate_unique_id(), # Unique ID for the message
            "sender_id": self.current_user_id,
            "text": text,
            "created_at": datetime.now().isoformat(timespec='milliseconds') + "Z"
        }
        self.direct_messages[conversation_id]["messages"].append(new_message)
        
        # Update API usage for the sender
        sender_data = self.users[self.current_user_id]
        sender_data["api_usage"]["dms_sent"] = sender_data["api_usage"].get("dms_sent", 0) + 1
        
        print(f"DM sent in conversation {conversation_id}: from {sender_data['username']} to {self.users[recipient_id]['username']}")
        return copy.deepcopy(self.direct_messages[conversation_id])

    def delete_dm_conversation(self, conversation_id: str) -> None:
        """
        Permanently delete a DM conversation for the authenticated user.
        
        This method removes the entire conversation from the backend, including all messages.
        The authenticated user must be a participant in the conversation to delete it. This is
        a destructive operation that affects all participants.

        Args:
            conversation_id (str): The UUID of the conversation to delete. Must be a valid conversation
                ID that exists in the backend and includes the authenticated user as a participant.

        Returns:
            None: This method returns nothing on success.

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If the specified conversation_id does not exist in the backend
            Exception: If the authenticated user is not a participant in this conversation (authorization failure)
        
        Side Effects:
            - Removes the conversation entry from self.direct_messages dictionary
            - All messages in the conversation are permanently deleted
            - Prints a confirmation message to stdout with conversation ID and user ID
        
        Note:
            - This is a destructive operation that cannot be undone
            - In this simulation, deletion affects all participants (real X allows per-user deletion)
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> api.delete_dm_conversation("conversation-uuid")
            # Prints: Conversation conversation-uuid deleted by user {user_id}
        """
        self._ensure_authenticated()
        
        conv_data = self.direct_messages.get(conversation_id)
        if not conv_data:
            raise Exception("Conversation not found")
        
        if self.current_user_id not in conv_data.get("participants", []):
            raise Exception("User is not a participant in this conversation")

        # Delete from global store
        if conversation_id in self.direct_messages:
            del self.direct_messages[conversation_id]
            print(f"Conversation {conversation_id} deleted by user {self.current_user_id}")

    def get_api_usage(self) -> Dict:
        """
        Retrieve current API usage statistics for the authenticated user.
        
        This method returns metrics tracking how many API operations the user has performed,
        such as posts created and DMs sent. Useful for monitoring activity and enforcing
        rate limits in more advanced implementations.

        Returns:
            Dict: API usage metrics dictionary containing counters such as:
                {
                    "posts_created": int,       # Number of tweets created
                    "dms_sent": int,            # Number of direct messages sent
                    # ... potentially other usage metrics
                }
                Returns an empty dict if no usage data has been recorded.

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> usage = api.get_api_usage()
            >>> print(f"Tweets created: {usage.get('posts_created', 0)}")
            >>> print(f"DMs sent: {usage.get('dms_sent', 0)}")
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        return user_data.get("api_usage", {})

    def get_tweet_metrics(self, tweet_ids: List[str], metrics: Optional[List[str]] = None) -> List[Dict]:
        """
        Retrieve public engagement metrics for specific tweets. This is a public endpoint.
        
        This method returns engagement statistics for one or more tweets, optionally filtered to
        specific metrics. Useful for analytics, monitoring tweet performance, or comparing engagement
        across multiple tweets. No authentication is required.

        Args:
            tweet_ids (List[str]): A list of tweet UUIDs to retrieve metrics for. Can contain one or
                more tweet IDs. Tweets that don't exist will be returned with an error message.
            metrics (Optional[List[str]], optional): A list of specific metric names to retrieve.
                If None, all available metrics are returned. Valid metric names include:
                - "retweet_count": Number of retweets
                - "reply_count": Number of replies
                - "like_count": Number of likes
                - "quote_count": Number of quote tweets
                - "impression_count": Number of impressions/views
                Defaults to None (return all metrics).

        Returns:
            List[Dict]: A list of metric dictionaries, one per tweet ID:
                Successful case:
                [
                    {
                        "tweet_id": str,            # Tweet UUID
                        "public_metrics": {         # Filtered or complete metrics
                            "retweet_count": int,
                            "reply_count": int,
                            "like_count": int,
                            "quote_count": int,
                            "impression_count": int
                        }
                    },
                    # ... more tweet metrics
                ]
                
                Error case (tweet not found):
                [
                    {
                        "tweet_id": str,            # Tweet UUID that wasn't found
                        "error": "Tweet not found"
                    }
                ]

        Note:
            - This method does NOT require authentication
            - Returns metrics only if the tweet has a "public_metrics" field
            - Missing tweets are included in results with an error message
        
        Example:
            >>> api = XApis()
            >>> tweet_ids = ["tweet1-uuid", "tweet2-uuid"]
            >>> # Get all metrics
            >>> all_metrics = api.get_tweet_metrics(tweet_ids)
            >>> # Get only like and retweet counts
            >>> filtered = api.get_tweet_metrics(tweet_ids, ["like_count", "retweet_count"])
            >>> for result in filtered:
            ...     if "error" not in result:
            ...         print(f"Tweet {result['tweet_id']}: {result['public_metrics']}")
        """
        tweet_metrics = []
        for tweet_id in tweet_ids:
            if tweet_id in self.posts:
                post = self.posts[tweet_id]
                if "public_metrics" in post:
                    if metrics:
                        filtered_metrics = {k: v for k, v in post["public_metrics"].items() if k in metrics}
                        tweet_metrics.append({"tweet_id": tweet_id, "public_metrics": filtered_metrics})
                    else:
                        tweet_metrics.append({"tweet_id": tweet_id, "public_metrics": copy.deepcopy(post["public_metrics"])})
            else:
                tweet_metrics.append({"tweet_id": tweet_id, "error": "Tweet not found"})
        return tweet_metrics

    def update_profile(self, bio: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Update the authenticated user's profile information.
        
        This method allows the user to modify their display name and/or bio (biography/description).
        Fields that are not provided (None) remain unchanged, allowing partial updates. The username
        (handle) cannot be changed through this method.

        Args:
            bio (Optional[str], optional): New biography/description text to display on the user's
                profile. Can be any length in this simulation (real X has length limits). If None,
                the bio remains unchanged. Defaults to None.
            name (Optional[str], optional): New display name for the user. This is the name shown
                prominently on the profile and in tweets (not the @username handle). If None, the
                name remains unchanged. Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing the updated profile information:
                {
                    "id": str,              # User UUID (unchanged)
                    "username": str,        # X handle (unchanged)
                    "name": str,            # Display name (updated or existing)
                    "bio": str              # Biography (updated or existing)
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
        
        Side Effects:
            - Updates the user's "bio" field in self.users (if bio is provided)
            - Updates the user's "name" field in self.users (if name is provided)
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> # Update only bio
            >>> profile = api.update_profile(bio="Software developer and tech enthusiast")
            >>> # Update both name and bio
            >>> profile = api.update_profile(
            ...     name="John Smith",
            ...     bio="Developer | Writer | Coffee lover"
            ... )
            >>> print(f"Updated profile: {profile['name']}")
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        if bio is not None:
            user_data["bio"] = bio
        if name is not None:
            user_data["name"] = name
        
        return {
            "id": user_data.get("id"),
            "username": user_data.get("username"),
            "name": user_data.get("name"),
            "bio": user_data.get("bio")
        }

    def get_user_analytics(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive analytics and statistics about the authenticated user's X activity.
        
        This method aggregates various metrics about the user's account, including follower counts,
        tweet statistics, engagement metrics, and calculated ratios. Provides a high-level overview
        of the user's presence and performance on the platform.

        Returns:
            Dict[str, Any]: A dictionary containing comprehensive user analytics:
                {
                    "user_id": str,                 # User UUID
                    "username": str,                # X handle
                    "created_at": str,              # Account creation date (ISO 8601)
                    "verified": bool,               # Verification status
                    "public_metrics": {             # Current public engagement metrics
                        "followers_count": int,     # Number of followers
                        "following_count": int,     # Number of accounts following
                        "tweet_count": int,         # Number of tweets posted
                        "like_count": int           # Number of tweets liked
                    },
                    "total_likes_received": int,    # Sum of likes across all user's tweets
                    "engagement_ratio": float       # Likes per tweet (likes_received / tweet_count)
                }

        Raises:
            Exception: If not authenticated (authenticate() has not been called successfully)
            Exception: If user data cannot be found in the backend
        
        Note:
            - total_likes_received is calculated by summing like_count from all tweets by this user
            - engagement_ratio is rounded to 2 decimal places
            - engagement_ratio uses max(tweet_count, 1) to avoid division by zero
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> analytics = api.get_user_analytics()
            >>> print(f"Username: @{analytics['username']}")
            >>> print(f"Followers: {analytics['public_metrics']['followers_count']}")
            >>> print(f"Tweets: {analytics['public_metrics']['tweet_count']}")
            >>> print(f"Total likes received: {analytics['total_likes_received']}")
            >>> print(f"Engagement ratio: {analytics['engagement_ratio']} likes per tweet")
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")

        user_posts = [p for p in self.posts.values() if p.get("author_id") == self.current_user_id]
        total_likes_received = sum(p.get("public_metrics", {}).get("like_count", 0) for p in user_posts)
        
        return {
            "user_id": self.current_user_id,
            "username": user_data.get("username"),
            "created_at": user_data.get("joined_date"),
            "verified": user_data.get("is_verified", False),
            "public_metrics": {
                "followers_count": len(user_data.get("followers", [])),
                "following_count": len(user_data.get("following", [])),
                "tweet_count": len(user_data.get("posts", [])),
                "like_count": len(user_data.get("liked_posts", []))
            },
            "total_likes_received": total_likes_received,
            "engagement_ratio": round(total_likes_received / max(len(user_posts), 1), 2)
        }

    def search_users_by_bio(self, search_term: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Search for users based on bio content. This is a public endpoint requiring no authentication.
        
        This method searches through all users in the backend to find those whose bio (biography/description)
        contains the specified search term. The search is case-insensitive and uses substring matching.
        Results are paginated and include basic profile information and follower counts.

        Args:
            search_term (str): The term to search for in user bios. Search is case-insensitive and
                matches any bio containing this substring. For example, "developer" would match bios
                containing "Developer", "web developer", "DEVELOPER", etc.
            limit (int, optional): Maximum number of users to return in a single response.
                Defaults to 20. Controls the page size for pagination. Typical values are 10-50.
            offset (int, optional): Number of users to skip before starting to return results.
                Defaults to 0 (start from the beginning). Use this to retrieve subsequent pages.

        Returns:
            Dict[str, Any]: A dictionary containing paginated search results:
                {
                    "data": [                       # List of matching user profiles
                        {
                            "id": str,              # User UUID
                            "username": str,        # X handle
                            "name": str,            # Display name
                            "bio": str,             # Biography containing the search term
                            "verified": bool,       # Verification status
                            "public_metrics": {
                                "followers_count": int  # Number of followers
                            }
                        },
                        # ... more matching users
                    ],
                    "pagination": {
                        "limit": int,               # Number of results per page
                        "offset": int,              # Starting position in results
                        "total": int                # Total number of matching users
                    }
                }

        Note:
            - This method does NOT require authentication
            - Search is case-insensitive
            - Uses substring matching (not exact word matching)
            - Users with empty bios will not match any search term
        
        Example:
            >>> api = XApis()
            >>> # Search for developers
            >>> results = api.search_users_by_bio("developer", limit=10)
            >>> print(f"Found {results['pagination']['total']} developers")
            >>> for user in results['data']:
            ...     print(f"@{user['username']}: {user['bio']}")
        """
        matching_users = []
        search_term_lower = search_term.lower()
        
        for user_id, user_data in self.users.items():
            bio = user_data.get("bio", "").lower()
            if search_term_lower in bio:
                matching_users.append({
                    "id": user_id,
                    "username": user_data.get("username"),
                    "name": user_data.get("name"),
                    "bio": user_data.get("bio"),
                    "verified": user_data.get("is_verified", False),
                    "public_metrics": {
                        "followers_count": len(user_data.get("followers", []))
                    }
                })
        
        paginated_users = matching_users[offset:offset + limit]
        
        return {
            "data": paginated_users,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(matching_users)
            }
        }

    def get_verified_users(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve all verified users sorted by follower count. This is a public endpoint.
        
        This method returns a list of all users who have verified status (the checkmark badge),
        sorted by follower count in descending order (most followed first). Results are paginated
        and include complete profile information. Useful for discovering influential or notable accounts.

        Args:
            limit (int, optional): Maximum number of users to return in a single response.
                Defaults to 20. Controls the page size for pagination. Typical values are 10-50.
            offset (int, optional): Number of users to skip before starting to return results.
                Defaults to 0 (start from the most followed). Use this to retrieve subsequent pages.
                The offset applies after sorting by follower count.

        Returns:
            Dict[str, Any]: A dictionary containing paginated verified user data:
                {
                    "data": [                       # List of verified users (sorted by followers, desc)
                        {
                            "id": str,              # User UUID
                            "username": str,        # X handle
                            "name": str,            # Display name
                            "bio": str,             # Biography
                            "profile_picture_url": str,  # Profile image URL
                            "created_at": str,      # Account creation date (ISO 8601)
                            "verified": True,       # Always True for this endpoint
                            "public_metrics": {
                                "followers_count": int  # Number of followers (used for sorting)
                            }
                        },
                        # ... more verified users
                    ],
                    "pagination": {
                        "limit": int,               # Number of results per page
                        "offset": int,              # Starting position in sorted list
                        "total": int                # Total number of verified users
                    }
                }

        Note:
            - This method does NOT require authentication
            - Results are sorted by follower count (highest first)
            - Only users with is_verified=True are included
            - Returns empty list if no verified users exist
        
        Example:
            >>> api = XApis()
            >>> # Get top 10 most followed verified users
            >>> verified = api.get_verified_users(limit=10)
            >>> print(f"Found {verified['pagination']['total']} verified users")
            >>> for user in verified['data']:
            ...     followers = user['public_metrics']['followers_count']
            ...     print(f"@{user['username']}: {followers:,} followers")
        """
        verified_users = []
        
        for user_id, user_data in self.users.items():
            if user_data.get("is_verified", False):
                verified_users.append({
                    "id": user_id,
                    "username": user_data.get("username"),
                    "name": user_data.get("name"),
                    "bio": user_data.get("bio"),
                    "profile_picture_url": user_data.get("profile_picture_url"),
                    "created_at": user_data.get("joined_date"),
                    "verified": True,
                    "public_metrics": {
                        "followers_count": len(user_data.get("followers", []))
                    }
                })
        
        # Sort by follower count (most followed first)
        verified_users.sort(key=lambda x: x["public_metrics"]["followers_count"], reverse=True)
        
        paginated_users = verified_users[offset:offset + limit]
        
        return {
            "data": paginated_users,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(verified_users)
            }
        }

    def reset_data(self) -> None:
        """
        Reset all simulated data in the backend to its default state.
        
        This utility function reloads the DEFAULT_STATE scenario, effectively erasing all changes
        made during the current session and returning the backend to its initial configuration.
        This also clears any authentication state. Primarily useful for testing and development
        to ensure a clean slate between test runs.

        Returns:
            None: This method returns nothing.
        
        Side Effects:
            - Reloads all data from DEFAULT_STATE (users, posts, direct_messages)
            - Sets access_token to None (clears authentication)
            - Sets current_user_id to None (clears authenticated user)
            - Prints a confirmation message to stdout
        
        Note:
            - This is a utility function for testing, not a standard X API endpoint
            - All user-generated data (tweets, DMs, likes, etc.) is lost
            - Cannot be undone - use with caution
        
        Example:
            >>> api = XApis()
            >>> api.authenticate("token_user@example.com")
            >>> api.create_tweet("Test tweet")
            >>> # Reset everything
            >>> api.reset_data()
            # Prints: XApis: All data reset to default state.
            >>> # Now need to authenticate again
        """
        self._load_scenario(DEFAULT_STATE)
        self.access_token = None
        self.current_user_id = None
        print("XApis: All data reset to default state.")