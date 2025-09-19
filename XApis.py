import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional, Union
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("XApis")

class EmailStr(str):
    pass

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
        self.current_user: Optional[str] = None # Stores the UUID of the current user

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
        self.current_user = scenario.get("current_user") # This will already be a UUID after conversion
        print("XApis: Loaded scenario with UUIDs for users, posts, and DMs.")

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
    
    def set_current_user(self, user_id: str) -> Dict[str, Union[bool, str]]:
        """
        Sets the current authenticated user for the API session.

        Args:
            user_id (str): The ID (UUID) of the user to set as current.

        Returns:
            Dict[str, Union[bool, str]]: A dictionary with 'status' indicating success or failure and a message.
        """
        if user_id in self.users:
            self.current_user = user_id
            return {"status": True, "message": f"Current user set to {self.users[user_id]['username']} (ID: {user_id})."}
        return {"status": False, "message": f"User with ID {user_id} not found."}


    # ================
    # User Profile
    # ================

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get the profile information for a specific user.

        Args:
            user_id (str): The ID (UUID) of the user whose profile is to be retrieved.

        Returns:
            Dict: A dictionary containing the user's profile data.
        """
        user_data = self._get_user_data(user_id)
        if user_data:
            # Return enhanced profile with backend metadata
            profile = {
                "id": user_data.get("id"),
                "username": user_data.get("username"),
                "name": user_data.get("name"),
                "email": user_data.get("email"),
                "bio": user_data.get("bio"),
                "profile_picture_url": user_data.get("profile_picture_url"),
                "joined_date": user_data.get("joined_date"),
                "is_verified": user_data.get("is_verified", False),
                "follower_count": len(user_data.get("followers", [])),
                "following_count": len(user_data.get("following", [])),
                "posts_count": len(user_data.get("posts", [])),
                "liked_posts_count": len(user_data.get("liked_posts", [])),
                "api_usage": user_data.get("api_usage", {})
            }
            return {"data": profile}
        return {"data": None, "error": "User not found"}

    def list_followers(self, user_id: str) -> Dict[str, Any]:
        """
        List the followers of a specific user.

        Args:
            user_id (str): The ID (UUID) of the user whose followers are to be listed.

        Returns:
            Dict: A dictionary containing a list of follower IDs.
        """
        user_data = self._get_user_data(user_id)
        if user_data:
            follower_uuids = user_data.get("followers", [])
            followers_details = [
                {"id": self.users[f_id]["id"], "username": self.users[f_id]["username"], "name": self.users[f_id]["name"]}
                for f_id in follower_uuids if f_id in self.users
            ]
            return {"data": followers_details}
        return {"data": None, "error": "User not found"}

    def list_following(self, user_id: str) -> Dict[str, Any]:
        """
        List the users a specific user is following.

        Args:
            user_id (str): The ID (UUID) of the user whose following list is to be retrieved.

        Returns:
            Dict: A dictionary containing a list of IDs of users being followed.
        """
        user_data = self._get_user_data(user_id)
        if user_data:
            following_uuids = user_data.get("following", [])
            following_details = [
                {"id": self.users[f_id]["id"], "username": self.users[f_id]["username"], "name": self.users[f_id]["name"]}
                for f_id in following_uuids if f_id in self.users
            ]
            return {"data": following_details}
        return {"data": None, "error": "User not found"}

    def list_liked_posts(self, user_id: str) -> Dict[str, Any]:
        """
        List the posts liked by a specific user.

        Args:
            user_id (str): The ID (UUID) of the user whose liked posts are to be listed.

        Returns:
            Dict: A dictionary containing a list of liked post IDs.
        """
        user_data = self._get_user_data(user_id)
        if user_data:
            liked_post_uuids = user_data.get("liked_posts", [])
            liked_posts_details = [
                copy.deepcopy(self.posts[p_id]) for p_id in liked_post_uuids if p_id in self.posts
            ]
            return {"data": liked_posts_details}
        return {"data": None, "error": "User not found"}

    # ================
    # Posts
    # ================

    def create_post(self, user_id: str, text: str) -> Dict[str, Any]:
        """
        Create a new post for a specific user.

        Args:
            user_id (str): The ID (UUID) of the user creating the post.
            text (str): The content of the post.

        Returns:
            Dict: A dictionary containing the newly created post's data.
        """
        if user_id not in self.users:
            return {"data": None, "error": "User not found"}

        post_uuid = self._generate_unique_id()
        new_post = {
            "id": post_uuid,
            "author_id": user_id,
            "text": text,
            "created_at": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z",
            "likes": [],
            "reposts": [],
            "replies": [],
            "metrics": {"views": 0, "likes": 0, "reposts": 0, "replies": 0}
        }
        self.posts[post_uuid] = new_post
        self.users[user_id]["posts"].append(post_uuid)
        self.users[user_id]["api_usage"]["posts_created"] = self.users[user_id]["api_usage"].get("posts_created", 0) + 1
        print(f"Post created: ID={post_uuid} by {self.users[user_id]['username']}")
        return {"data": copy.deepcopy(new_post)}

    def delete_post(self, user_id: str, post_id: str) -> Dict[str, bool]:
        """
        Delete a post by its ID. Only the author can delete their post.

        Args:
            user_id (str): The ID (UUID) of the user attempting to delete the post.
            post_id (str): The ID (UUID) of the post to delete.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating the operation's outcome.
        """
        post = self.posts.get(post_id)
        if not post:
            return {"success": False, "error": "Post not found"}
        if post["author_id"] != user_id:
            return {"success": False, "error": "Not authorized to delete this post"}

        if post_id in self.posts:
            del self.posts[post_id]
            # Remove from author's list of posts
            if user_id in self.users and post_id in self.users[user_id].get("posts", []):
                self.users[user_id]["posts"].remove(post_id)
            # Remove from any user's liked_posts
            for u_data in self.users.values():
                if post_id in u_data.get("liked_posts", []):
                    u_data["liked_posts"].remove(post_id)
            return {"success": True}
        return {"success": False, "error": "Post not found or internal error"}

    def get_post_details(self, post_id: str) -> Dict[str, Any]:
        """
        Get the details of a specific post.

        Args:
            post_id (str): The ID (UUID) of the post to retrieve.

        Returns:
            Dict: A dictionary containing the post's data.
        """
        post_data = self.posts.get(post_id)
        if post_data:
            return {"data": copy.deepcopy(post_data)}
        return {"data": None, "error": "Post not found"}

    def list_user_posts(self, user_id: str) -> Dict[str, Any]:
        """
        List all posts created by a specific user.

        Args:
            user_id (str): The ID (UUID) of the user whose posts are to be listed.

        Returns:
            Dict: A dictionary containing a list of posts.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"data": None, "error": "User not found"}

        user_post_uuids = user_data.get("posts", [])
        user_posts = [
            copy.deepcopy(self.posts[p_id]) for p_id in user_post_uuids if p_id in self.posts
        ]
        # Sort by creation time, most recent first
        user_posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return {"data": user_posts}

    def like_post(self, user_id: str, post_id: str) -> Dict[str, bool]:
        """
        Like a specific post.

        Args:
            user_id (str): The ID (UUID) of the user liking the post.
            post_id (str): The ID (UUID) of the post to like.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating the operation's outcome.
        """
        user = self._get_user_data(user_id)
        post = self.posts.get(post_id)
        if not user:
            return {"success": False, "error": "User not found"}
        if not post:
            return {"success": False, "error": "Post not found"}

        if post_id not in user.get("liked_posts", []):
            user["liked_posts"].append(post_id)
            post["likes"].append(user_id)
            post["metrics"]["likes"] = post["metrics"].get("likes", 0) + 1
            return {"success": True}
        return {"success": False, "error": "Post already liked by this user"}

    def unlike_post(self, user_id: str, post_id: str) -> Dict[str, bool]:
        """
        Unlike a specific post.

        Args:
            user_id (str): The ID (UUID) of the user unliking the post.
            post_id (str): The ID (UUID) of the post to unlike.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating the operation's outcome.
        """
        user = self._get_user_data(user_id)
        post = self.posts.get(post_id)
        if not user:
            return {"success": False, "error": "User not found"}
        if not post:
            return {"success": False, "error": "Post not found"}

        if post_id in user.get("liked_posts", []):
            user["liked_posts"].remove(post_id)
            if user_id in post["likes"]:
                post["likes"].remove(user_id)
            post["metrics"]["likes"] = max(0, post["metrics"].get("likes", 0) - 1)
            return {"success": True}
        return {"success": False, "error": "Post not liked by this user"}

    # ================
    # Direct Messages
    # ================

    def list_direct_messages_conversations(self, user_id: str) -> Dict[str, Any]:
        """
        List all direct message conversations for a specific user.

        Args:
            user_id (str): The ID (UUID) of the user whose conversations are to be listed.

        Returns:
            Dict: A dictionary containing a list of conversation summaries.
        """
        if user_id not in self.users:
            return {"data": None, "error": "User not found"}

        user_conversations = []
        for conv_id, conv_data in self.direct_messages.items():
            if user_id in conv_data.get("participants", []):
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
        
        return {"data": user_conversations}

    def get_direct_messages_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get all messages within a specific direct message conversation.

        Args:
            conversation_id (str): The ID (UUID) of the conversation to retrieve.

        Returns:
            Dict: A dictionary containing the conversation data, including messages.
        """
        conv_data = self.direct_messages.get(conversation_id)
        if conv_data:
            # Sort messages by timestamp
            sorted_messages = sorted(conv_data.get("messages", []), key=lambda msg: msg.get("timestamp", ""))
            conversation_copy = copy.deepcopy(conv_data)
            conversation_copy["messages"] = sorted_messages
            return {"data": conversation_copy}
        return {"data": None, "error": "Conversation not found"}

    def send_direct_message(self, sender_id: str, receiver_id: str, text: str) -> Dict[str, Any]:
        """
        Send a direct message to another user. If no existing conversation, a new one is created.

        Args:
            sender_id (str): The ID (UUID) of the user sending the message.
            receiver_id (str): The ID (UUID) of the user receiving the message.
            text (str): The content of the message.

        Returns:
            Dict: A dictionary containing the updated conversation data or an error.
        """
        if sender_id not in self.users or receiver_id not in self.users:
            return {"data": None, "error": "Sender or receiver user not found"}

        # Find existing conversation or create a new one
        conversation_id = None
        for conv_id, conv_data in self.direct_messages.items():
            participants = set(conv_data.get("participants", []))
            if participants == {sender_id, receiver_id}:
                conversation_id = conv_id
                break

        if not conversation_id:
            conversation_id = self._generate_unique_id()
            self.direct_messages[conversation_id] = {
                "id": conversation_id,
                "participants": sorted([sender_id, receiver_id]), # Ensure consistent order
                "messages": []
            }
        
        new_message = {
            "id": self._generate_unique_id(), # Unique ID for the message
            "sender_id": sender_id,
            "text": text,
            "timestamp": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
        }
        self.direct_messages[conversation_id]["messages"].append(new_message)
        
        # Update API usage for the sender
        self.users[sender_id]["api_usage"]["dms_sent"] = self.users[sender_id]["api_usage"].get("dms_sent", 0) + 1
        
        print(f"DM sent in conversation {conversation_id}: from {self.users[sender_id]['username']} to {self.users[receiver_id]['username']}")
        return {"data": copy.deepcopy(self.direct_messages[conversation_id])}

    def delete_direct_message_conversation(self, user_id: str, conversation_id: str) -> Dict[str, bool]:
        """
        Delete a direct message conversation for a specific user.

        Args:
            user_id (str): The ID (UUID) of the user deleting the conversation.
            conversation_id (str): The ID (UUID) of the conversation to delete.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating the operation's outcome.
        """
        conv_data = self.direct_messages.get(conversation_id)
        if not conv_data:
            return {"success": False, "error": "Conversation not found"}
        
        if user_id not in conv_data.get("participants", []):
            return {"success": False, "error": "User is not a participant in this conversation"}

        # In a real scenario, this would likely "hide" the conversation for the user,
        # not delete it for everyone. For this dummy, we'll remove it entirely if a participant deletes it.
        # This implies a shared delete, or that the current user is the only one left.
        # For simplicity, we'll just delete it from global store for now.
        if conversation_id in self.direct_messages:
            del self.direct_messages[conversation_id]
            print(f"Conversation {conversation_id} deleted by user {user_id}")
            return {"success": True}
        return {"success": False, "error": "Conversation not found or internal error"}

    # ================
    # Analytics / Metrics (Dummy)
    # ================

    def get_api_usage(self, user_id: str) -> Dict:
        """
        Get current API usage statistics for a specific user.

        Parameters:
            user_id (str):
                User ID (UUID) to retrieve API usage for.

        Returns:
            Dict:
                Dictionary containing API usage metrics.
        """
        if user_id in self.users:
            return {"data": self.users[user_id].get("api_usage", {})}
        return {"data": None, "error": "User not found"}

    def get_post_metrics(self, post_ids: List[str], metrics: Optional[List[str]] = None) -> Dict:
        """
        Get metrics for specific posts.

        Parameters:
            post_ids (List[str]):
                List of post IDs (UUIDs) to get metrics for.
            metrics (Optional[List[str]]):
                Specific metrics to retrieve.

        Returns:
            Dict:
                Dictionary containing post metrics.
        """
        post_metrics = []
        for post_id in post_ids:
            if post_id in self.posts:
                post = self.posts[post_id]
                if "metrics" in post:
                    if metrics:
                        filtered_metrics = {k: v for k, v in post["metrics"].items() if k in metrics}
                        post_metrics.append({"post_id": post_id, "metrics": filtered_metrics})
                    else:
                        post_metrics.append({"post_id": post_id, "metrics": copy.deepcopy(post["metrics"])})
            else:
                post_metrics.append({"post_id": post_id, "error": "Post not found"})
        return {"data": post_metrics}

    def update_user_bio(self, user_id: str, new_bio: str) -> Dict[str, Any]:
        """
        Update a user's bio.

        Args:
            user_id (str): The ID (UUID) of the user.
            new_bio (str): The new bio text.

        Returns:
            Dict: A dictionary indicating success status.
        """
        if user_id in self.users:
            self.users[user_id]["bio"] = new_bio
            return {"status": "success", "message": "Bio updated successfully"}
        return {"status": "error", "message": "User not found"}

    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a user.

        Args:
            user_id (str): The ID (UUID) of the user.

        Returns:
            Dict: A dictionary containing user analytics.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"data": None, "error": "User not found"}

        user_posts = [p for p in self.posts.values() if p.get("author_id") == user_id]
        total_likes_received = sum(len(p.get("likes", [])) for p in user_posts)
        
        analytics = {
            "user_id": user_id,
            "username": user_data.get("username"),
            "joined_date": user_data.get("joined_date"),
            "is_verified": user_data.get("is_verified", False),
            "follower_count": len(user_data.get("followers", [])),
            "following_count": len(user_data.get("following", [])),
            "posts_count": len(user_data.get("posts", [])),
            "total_likes_received": total_likes_received,
            "liked_posts_count": len(user_data.get("liked_posts", [])),
            "api_usage": user_data.get("api_usage", {}),
            "engagement_ratio": round(total_likes_received / max(len(user_posts), 1), 2)
        }
        
        return {"data": analytics}

    def search_users_by_bio(self, search_term: str) -> Dict[str, Any]:
        """
        Search for users based on bio content.

        Args:
            search_term (str): The term to search for in user bios.

        Returns:
            Dict: A dictionary containing matching users.
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
                    "is_verified": user_data.get("is_verified", False),
                    "follower_count": len(user_data.get("followers", []))
                })
        
        return {"data": matching_users, "count": len(matching_users)}

    def get_verified_users(self) -> Dict[str, Any]:
        """
        Get all verified users.

        Returns:
            Dict: A dictionary containing all verified users.
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
                    "follower_count": len(user_data.get("followers", [])),
                    "joined_date": user_data.get("joined_date")
                })
        
        # Sort by follower count (most followed first)
        verified_users.sort(key=lambda x: x["follower_count"], reverse=True)
        
        return {"data": verified_users, "count": len(verified_users)}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self._load_scenario(DEFAULT_STATE)
        print("XApis: All dummy data reset to default state.")
        return {"reset_status": True}