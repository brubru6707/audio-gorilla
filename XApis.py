import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional, Union

# Define a placeholder for EmailStr if not already defined globally
class EmailStr(str):
    pass

# Global mappings for initial data conversion from old string/int IDs to new UUIDs
_initial_user_id_map = {} # Map old_string_id to new_uuid
_initial_post_id_map = {} # Map old_string_id to new_uuid
_initial_dm_conv_id_map = {} # Map old_string_id to new_uuid

def _convert_initial_data_to_uuids(initial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Converts the initial RAW_DEFAULT_STATE data to use UUIDs for all relevant IDs and adds realism."""

    converted_data = copy.deepcopy(initial_data)

    # Reset maps for a clean conversion
    global _initial_user_id_map
    global _initial_post_id_map
    global _initial_dm_conv_id_map

    _initial_user_id_map = {}
    _initial_post_id_map = {}
    _initial_dm_conv_id_map = {}

    current_time_iso = datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"

    # Convert users and their associated lists to UUIDs
    new_users = {}
    for old_user_id, user_data in converted_data.get("users", {}).items():
        user_uuid = str(uuid.uuid4())
        _initial_user_id_map[old_user_id] = user_uuid
        user_data["id"] = user_uuid # Ensure the internal 'id' also reflects the UUID
        
        # Convert friends (followers/following) to UUIDs
        if "followers" in user_data:
            user_data["followers"] = [
                _initial_user_id_map.get(f_id, f_id) # Use get to avoid KeyError if friend not in initial map
                for f_id in user_data["followers"]
            ]
        if "following" in user_data:
            user_data["following"] = [
                _initial_user_id_map.get(f_id, f_id)
                for f_id in user_data["following"]
            ]
        
        # Clean up friends list to ensure they are valid UUIDs, remove if not mapped
        user_data["followers"] = [
            f_id for f_id in user_data["followers"] if f_id in _initial_user_id_map.values()
        ]
        user_data["following"] = [
            f_id for f_id in user_data["following"] if f_id in _initial_user_id_map.values()
        ]

        # Update joined_date to ISO 8601 if not already
        if "joined_date" in user_data and not isinstance(user_data["joined_date"], str):
            user_data["joined_date"] = user_data["joined_date"].isoformat(timespec='milliseconds') + "Z"
        
        new_users[user_uuid] = user_data
    converted_data["users"] = new_users

    # Convert posts and associated lists to UUIDs
    new_posts = {}
    for old_post_id, post_data in converted_data.get("posts", {}).items():
        post_uuid = str(uuid.uuid4())
        _initial_post_id_map[old_post_id] = post_uuid
        post_data["id"] = post_uuid # Ensure the internal 'id' also reflects the UUID

        # Convert author_id to user UUID
        if "author_id" in post_data:
            post_data["author_id"] = _initial_user_id_map.get(post_data["author_id"], post_data["author_id"])
        
        # Ensure created_at is ISO 8601
        if "created_at" in post_data and not isinstance(post_data["created_at"], str):
            post_data["created_at"] = post_data["created_at"].isoformat(timespec='milliseconds') + "Z"
        elif "created_at" not in post_data:
            post_data["created_at"] = current_time_iso

        new_posts[post_uuid] = post_data
    converted_data["posts"] = new_posts

    # Update user's liked_posts and own posts lists with new UUIDs
    for user_uuid, user_data in converted_data["users"].items():
        if "liked_posts" in user_data:
            user_data["liked_posts"] = [
                _initial_post_id_map.get(p_id, p_id)
                for p_id in user_data["liked_posts"]
            ]
            # Filter out posts that weren't successfully mapped (i.e., didn't exist in RAW_DEFAULT_STATE posts)
            user_data["liked_posts"] = [
                p_id for p_id in user_data["liked_posts"] if p_id in new_posts
            ]
        
        if "posts" in user_data:
            user_data["posts"] = [
                _initial_post_id_map.get(p_id, p_id)
                for p_id in user_data["posts"]
            ]
            # Filter out posts that weren't successfully mapped
            user_data["posts"] = [
                p_id for p_id in user_data["posts"] if p_id in new_posts
            ]

    # Convert direct messages conversations and messages within them
    new_direct_messages = {}
    for old_dm_conv_id, dm_conv_data in converted_data.get("direct_messages", {}).items():
        dm_conv_uuid = str(uuid.uuid4())
        _initial_dm_conv_id_map[old_dm_conv_id] = dm_conv_uuid
        dm_conv_data["id"] = dm_conv_uuid # Ensure the internal 'id' also reflects the UUID

        # Convert participant IDs to user UUIDs
        if "participants" in dm_conv_data:
            dm_conv_data["participants"] = [
                _initial_user_id_map.get(p_id, p_id)
                for p_id in dm_conv_data["participants"]
            ]
            # Filter participants if they were not valid users
            dm_conv_data["participants"] = [
                p_id for p_id in dm_conv_data["participants"] if p_id in new_users
            ]

        # Process individual messages within the conversation
        new_messages = []
        for message in dm_conv_data.get("messages", []):
            message_uuid = str(uuid.uuid4())
            message["id"] = message_uuid # Add a UUID for each message
            
            # Convert sender_id to user UUID
            if "sender_id" in message:
                message["sender_id"] = _initial_user_id_map.get(message["sender_id"], message["sender_id"])
            
            # Ensure timestamp is ISO 8601
            if "timestamp" not in message:
                message["timestamp"] = current_time_iso
            elif not isinstance(message["timestamp"], str):
                message["timestamp"] = message["timestamp"].isoformat(timespec='milliseconds') + "Z"

            new_messages.append(message)
        dm_conv_data["messages"] = new_messages
        
        new_direct_messages[dm_conv_uuid] = dm_conv_data
    converted_data["direct_messages"] = new_direct_messages

    return converted_data

# Define the initial raw state with string/integer IDs and emails for conversion
RAW_DEFAULT_STATE = {
    "current_user": "usr_alice_smith", # This will be converted to UUID
    "users": {
        "usr_alice_smith": {
            "id": "usr_alice_smith", # This will be replaced by a UUID
            "username": "alice_smith",
            "name": "Alice Smith",
            "email": "alice.smith@example.com",
            "joined_date": datetime.datetime(2023, 1, 15, 10, 0, 0, tzinfo=datetime.timezone.utc),
            "bio": "Tech enthusiast and amateur photographer. Sharing my thoughts on AI and the digital world.",
            "profile_picture_url": "https://example.com/profiles/alice_smith.jpg",
            "followers": ["usr_john_doe", "usr_emily_white"],
            "following": ["usr_john_doe", "usr_bob_johnson"],
            "liked_posts": ["post_002", "post_005"],
            "posts": ["post_001", "post_004", "post_006"],
            "api_usage": {"posts_created": 3, "dms_sent": 2, "profile_views": 15},
            "is_verified": True
        },
        "usr_john_doe": {
            "id": "usr_john_doe", # This will be replaced by a UUID
            "username": "john_doe",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "joined_date": datetime.datetime(2022, 11, 1, 14, 30, 0, tzinfo=datetime.timezone.utc),
            "bio": "Software developer and open-source contributor.",
            "profile_picture_url": "https://example.com/profiles/john_doe.jpg",
            "followers": ["usr_alice_smith"],
            "following": ["usr_alice_smith", "usr_emily_white"],
            "liked_posts": ["post_001", "post_003"],
            "posts": ["post_002", "post_003"],
            "api_usage": {"posts_created": 2, "dms_sent": 3, "profile_views": 10},
            "is_verified": False
        },
        "usr_emily_white": {
            "id": "usr_emily_white", # This will be replaced by a UUID
            "username": "emily_white",
            "name": "Emily White",
            "email": "emily.white@example.com",
            "joined_date": datetime.datetime(2024, 3, 20, 9, 0, 0, tzinfo=datetime.timezone.utc),
            "bio": "Digital artist exploring new creative frontiers.",
            "profile_picture_url": "https://example.com/profiles/emily_white.jpg",
            "followers": ["usr_alice_smith", "usr_john_doe"],
            "following": [],
            "liked_posts": [],
            "posts": ["post_005"],
            "api_usage": {"posts_created": 1, "dms_sent": 1, "profile_views": 8},
            "is_verified": False
        },
        "usr_bob_johnson": { # Added to ensure all referenced users exist
            "id": "usr_bob_johnson",
            "username": "bob_johnson",
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
            "joined_date": datetime.datetime(2023, 5, 1, 11, 0, 0, tzinfo=datetime.timezone.utc),
            "bio": "Musician and foodie.",
            "profile_picture_url": "https://example.com/profiles/bob_johnson.jpg",
            "followers": ["usr_alice_smith"],
            "following": [],
            "liked_posts": [],
            "posts": [],
            "api_usage": {},
            "is_verified": False
        }
    },
    "posts": {
        "post_001": {
            "id": "post_001", # This will be replaced by a UUID
            "author_id": "usr_alice_smith", # This will be replaced by a UUID
            "text": "Excited about the new AI developments! #AI #Tech",
            "created_at": datetime.datetime(2024, 7, 20, 8, 0, 0, tzinfo=datetime.timezone.utc),
            "likes": ["usr_john_doe"], # This will be replaced by a UUID
            "reposts": [],
            "replies": [],
            "metrics": {"views": 150, "likes": 1, "reposts": 0, "replies": 0}
        },
        "post_002": {
            "id": "post_002", # This will be replaced by a UUID
            "author_id": "usr_john_doe", # This will be replaced by a UUID
            "text": "Just pushed a new update to my GitHub repo. Check it out! #opensource #coding",
            "created_at": datetime.datetime(2024, 7, 21, 10, 0, 0, tzinfo=datetime.timezone.utc),
            "likes": ["usr_alice_smith"], # This will be replaced by a UUID
            "reposts": [],
            "replies": [],
            "metrics": {"views": 100, "likes": 1, "reposts": 0, "replies": 0}
        },
        "post_003": {
            "id": "post_003", # This will be replaced by a UUID
            "author_id": "usr_john_doe", # This will be replaced by a UUID
            "text": "Having a great time learning about quantum computing. Mind-blowing stuff! #QuantumComputing",
            "created_at": datetime.datetime(2024, 7, 22, 15, 30, 0, tzinfo=datetime.timezone.utc),
            "likes": ["usr_john_doe"], # Self-liked post for realism
            "reposts": [],
            "replies": [],
            "metrics": {"views": 80, "likes": 1, "reposts": 0, "replies": 0}
        },
        "post_004": {
            "id": "post_004", # This will be replaced by a UUID
            "author_id": "usr_alice_smith", # This will be replaced by a UUID
            "text": "Exploring new camera lenses. Any recommendations for landscape photography? #photography",
            "created_at": datetime.datetime(2024, 7, 23, 9, 0, 0, tzinfo=datetime.timezone.utc),
            "likes": [],
            "reposts": [],
            "replies": [],
            "metrics": {"views": 70, "likes": 0, "reposts": 0, "replies": 0}
        },
        "post_005": {
            "id": "post_005", # This will be replaced by a UUID
            "author_id": "usr_emily_white", # This will be replaced by a UUID
            "text": "New digital art piece in progress! What do you think? #digitalart",
            "created_at": datetime.datetime(2024, 7, 24, 11, 45, 0, tzinfo=datetime.timezone.utc),
            "likes": ["usr_alice_smith"], # This will be replaced by a UUID
            "reposts": [],
            "replies": [],
            "metrics": {"views": 120, "likes": 1, "reposts": 0, "replies": 0}
        },
         "post_006": {
            "id": "post_006", # This will be replaced by a UUID
            "author_id": "usr_alice_smith", # This will be replaced by a UUID
            "text": "Just finished a great book on mindful living. Highly recommend! #mindfulness #books",
            "created_at": datetime.datetime(2024, 7, 25, 14, 0, 0, tzinfo=datetime.timezone.utc),
            "likes": [],
            "reposts": [],
            "replies": [],
            "metrics": {"views": 60, "likes": 0, "reposts": 0, "replies": 0}
        }
    },
    "direct_messages": {
        "dm_conv_alice_john": {
            "id": "dm_conv_alice_john", # This will be replaced by a UUID
            "participants": ["usr_alice_smith", "usr_john_doe"], # These will be replaced by UUIDs
            "messages": [
                {"sender_id": "usr_alice_smith", "text": "Hey John, did you see the latest tech news?", "timestamp": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(timespec='milliseconds') + "Z"},
                {"sender_id": "usr_john_doe", "text": "Not yet, Alice! Anything exciting happening?", "timestamp": (datetime.datetime.now() - datetime.timedelta(days=2, minutes=5)).isoformat(timespec='milliseconds') + "Z"},
                {"sender_id": "usr_alice_smith", "text": "Just read about a breakthrough in AI ethics!", "timestamp": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(timespec='milliseconds') + "Z"}
            ]
        },
        "dm_conv_alice_emily": {
            "id": "dm_conv_alice_emily", # This will be replaced by a UUID
            "participants": ["usr_alice_smith", "usr_emily_white"], # These will be replaced by UUIDs
            "messages": [
                {"sender_id": "usr_alice_smith", "text": "Loved your new art piece, Emily! Stunning!", "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=10)).isoformat(timespec='milliseconds') + "Z"},
                {"sender_id": "usr_emily_white", "text": "Thanks, Alice! Glad you liked it.", "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=9)).isoformat(timespec='milliseconds') + "Z"}
            ]
        }
    }
}

# The actual DEFAULT_STATE used by the API will be the converted one
DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)


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
            # Return a copy to prevent external modification
            return {"data": copy.deepcopy(user_data)}
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

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        # Re-run the initial data conversion to reset maps and UUIDs
        global DEFAULT_STATE
        DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)
        self._load_scenario(DEFAULT_STATE)
        print("XApis: All dummy data reset to default state.")
        return {"reset_status": True}