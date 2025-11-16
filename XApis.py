# Inspired by https://developers.google.com/youtube/v3/docs

from datetime import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("XApis")

class XApis:
    """
    A dummy API class for simulating X (formerly Twitter) operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the XApis instance, setting up the in-memory
        data stores and loading the default scenario.
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
        Loads a predefined scenario into the dummy backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain "users", "posts", "direct_messages".
        """
        # Create deep copy to ensure the original DEFAULT_STATE is not modified
        self.users = copy.deepcopy(scenario.get("users", {}))
        self.posts = copy.deepcopy(scenario.get("posts", {}))
        self.direct_messages = copy.deepcopy(scenario.get("direct_messages", {}))
        print("XApis: Loaded scenario with UUIDs for users, posts, and DMs.")

    def authenticate(self, access_token: str) -> Dict[str, Any]:
        """
        Authenticate with X API using an access token.

        Args:
            access_token (str): OAuth 2.0 Bearer token (format: "token_{email}")

        Returns:
            Dict[str, Any]: Authenticated user's profile data

        Raises:
            Exception: If token is invalid or user not found
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

        Raises:
            Exception: If not authenticated
        """
        if not self.access_token or not self.current_user_id:
            raise Exception("Authentication required. Call authenticate() first.")

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for dummy entities.
        """
        return str(uuid.uuid4())

    def _get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get a user's data based on their UUID."""
        return self.users.get(user_id)

    def _get_user_posts_data(self, user_id: str) -> Optional[List[str]]:
        """Helper to get a user's list of post IDs."""
        user_data = self._get_user_data(user_id)
        return user_data.get("posts") if user_data else None

    def _get_user_direct_messages_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get a user's direct messages data (conversations)."""
        # This structure needs careful handling as DMs are global, but filtered by user
        # For this dummy, we'll iterate through global DMs to find user's conversations
        return {
            conv_id: conv_data for conv_id, conv_data in self.direct_messages.items()
            if user_id in conv_data.get("participants", [])
        }

    def _update_user_data(self, user_id: str, key: str, value: Any) -> bool:
        """Helper to update a specific key in a user's data by UUID."""
        if user_id in self.users:
            self.users[user_id][key] = value
            return True
        return False
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get the profile information for the authenticated user.

        Returns:
            Dict[str, Any]: User's profile data

        Raises:
            Exception: If not authenticated
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
        Get the followers of the authenticated user with pagination.

        Args:
            limit (int): Maximum number of followers to return (default: 20)
            offset (int): Number of followers to skip (default: 0)

        Returns:
            Dict[str, Any]: Paginated list of followers with metadata

        Raises:
            Exception: If not authenticated
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
        Get the users the authenticated user is following with pagination.

        Args:
            limit (int): Maximum number of users to return (default: 20)
            offset (int): Number of users to skip (default: 0)

        Returns:
            Dict[str, Any]: Paginated list of following with metadata

        Raises:
            Exception: If not authenticated
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
        Get tweets liked by the authenticated user with pagination.

        Args:
            limit (int): Maximum number of tweets to return (default: 20)
            offset (int): Number of tweets to skip (default: 0)

        Returns:
            Dict[str, Any]: Paginated list of liked tweets

        Raises:
            Exception: If not authenticated
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
        Create a new tweet for the authenticated user.

        Args:
            text (str): The content of the tweet (max 280 characters)

        Returns:
            Dict[str, Any]: The newly created tweet data

        Raises:
            Exception: If not authenticated
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
        Delete a tweet by its ID. Only the author can delete their tweet.

        Args:
            tweet_id (str): The ID of the tweet to delete

        Raises:
            Exception: If not authenticated, tweet not found, or not authorized
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
        Get the details of a specific tweet (public endpoint, no auth required).

        Args:
            tweet_id (str): The ID of the tweet to retrieve

        Returns:
            Dict[str, Any]: The tweet data

        Raises:
            Exception: If tweet not found
        """
        post_data = self.posts.get(tweet_id)
        if not post_data:
            raise Exception("Tweet not found")
        
        return copy.deepcopy(post_data)

    def get_user_tweets(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get all tweets created by the authenticated user with pagination.

        Args:
            limit (int): Maximum number of tweets to return (default: 20)
            offset (int): Number of tweets to skip (default: 0)

        Returns:
            Dict[str, Any]: Paginated list of tweets

        Raises:
            Exception: If not authenticated
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
        Like a specific tweet.

        Args:
            tweet_id (str): The ID of the tweet to like

        Raises:
            Exception: If not authenticated, tweet not found, or already liked
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
        
        user["liked_posts"].append(tweet_id)
        
        # Update public metrics
        if "public_metrics" not in post:
            post["public_metrics"] = {"retweet_count": 0, "reply_count": 0, "like_count": 0, "quote_count": 0, "impression_count": 0}
        post["public_metrics"]["like_count"] = post["public_metrics"].get("like_count", 0) + 1
        
        print(f"Tweet liked: ID={tweet_id} by {user['username']}")

    def unlike_tweet(self, tweet_id: str) -> None:
        """
        Unlike a specific tweet.

        Args:
            tweet_id (str): The ID of the tweet to unlike

        Raises:
            Exception: If not authenticated, tweet not found, or not liked
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
        
        user["liked_posts"].remove(tweet_id)
        
        # Update public metrics
        if "public_metrics" in post:
            post["public_metrics"]["like_count"] = max(0, post["public_metrics"].get("like_count", 0) - 1)
        
        print(f"Tweet unliked: ID={tweet_id} by {user['username']}")

    def get_dm_conversations(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get all direct message conversations for the authenticated user with pagination.

        Args:
            limit (int): Maximum number of conversations to return (default: 20)
            offset (int): Number of conversations to skip (default: 0)

        Returns:
            Dict[str, Any]: Paginated list of DM conversations

        Raises:
            Exception: If not authenticated
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
                    sorted_messages = sorted(conv_data["messages"], key=lambda msg: msg.get("timestamp", ""))
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
        Get all messages within a specific DM conversation (requires participation).

        Args:
            conversation_id (str): The ID of the conversation to retrieve

        Returns:
            Dict[str, Any]: The conversation data with messages

        Raises:
            Exception: If not authenticated, conversation not found, or not a participant
        """
        self._ensure_authenticated()
        
        conv_data = self.direct_messages.get(conversation_id)
        if not conv_data:
            raise Exception("Conversation not found")
        
        # Verify user is participant
        if self.current_user_id not in conv_data.get("participants", []):
            raise Exception("Not authorized to view this conversation")
        
        # Sort messages by timestamp
        sorted_messages = sorted(conv_data.get("messages", []), key=lambda msg: msg.get("timestamp", ""))
        conversation_copy = copy.deepcopy(conv_data)
        conversation_copy["messages"] = sorted_messages
        
        return conversation_copy

    def send_dm(self, recipient_id: str, text: str) -> Dict[str, Any]:
        """
        Send a direct message to another user. Creates new conversation if needed.

        Args:
            recipient_id (str): The ID of the user to send the message to
            text (str): The content of the message

        Returns:
            Dict[str, Any]: The updated conversation data

        Raises:
            Exception: If not authenticated or recipient not found
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
        Delete a DM conversation for the authenticated user.

        Args:
            conversation_id (str): The ID of the conversation to delete

        Raises:
            Exception: If not authenticated, conversation not found, or not a participant
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
        Get current API usage statistics for the authenticated user.

        Returns:
            Dict: API usage metrics

        Raises:
            Exception: If not authenticated
        """
        self._ensure_authenticated()
        
        user_data = self._get_user_data(self.current_user_id)
        if not user_data:
            raise Exception("User data not found")
        
        return user_data.get("api_usage", {})

    def get_tweet_metrics(self, tweet_ids: List[str], metrics: Optional[List[str]] = None) -> List[Dict]:
        """
        Get public metrics for specific tweets (public endpoint, no auth required).

        Args:
            tweet_ids (List[str]): List of tweet IDs to get metrics for
            metrics (Optional[List[str]]): Specific metrics to retrieve

        Returns:
            List[Dict]: List of tweet metrics
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
        Update the authenticated user's profile.

        Args:
            bio (Optional[str]): New bio text
            name (Optional[str]): New display name

        Returns:
            Dict[str, Any]: Updated profile data

        Raises:
            Exception: If not authenticated
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
        Get comprehensive analytics for the authenticated user.

        Returns:
            Dict[str, Any]: User analytics data

        Raises:
            Exception: If not authenticated
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
        Search for users based on bio content (public endpoint, no auth required).

        Args:
            search_term (str): The term to search for in user bios
            limit (int): Maximum number of users to return (default: 20)
            offset (int): Number of users to skip (default: 0)

        Returns:
            Dict[str, Any]: Paginated list of matching users
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
        Get all verified users (public endpoint, no auth required).

        Args:
            limit (int): Maximum number of users to return (default: 20)
            offset (int): Number of users to skip (default: 0)

        Returns:
            Dict[str, Any]: Paginated list of verified users
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
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.
        """
        self._load_scenario(DEFAULT_STATE)
        self.access_token = None
        self.current_user_id = None
        print("XApis: All dummy data reset to default state.")