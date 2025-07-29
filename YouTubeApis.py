import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional, Union

# Define a placeholder for EmailStr if not already defined globally
class EmailStr(str):
    pass

# Global mappings for initial data conversion from old string IDs to new UUIDs
_initial_user_id_map = {}
_initial_channel_id_map = {}
_initial_video_id_map = {}
_initial_playlist_id_map = {}
_initial_comment_id_map = {}

def _convert_initial_data_to_uuids(initial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Converts the initial RAW_DEFAULT_STATE data to use UUIDs for all relevant IDs and adds realism."""

    converted_data = copy.deepcopy(initial_data)

    # Reset maps for a clean conversion
    global _initial_user_id_map
    global _initial_channel_id_map
    global _initial_video_id_map
    global _initial_playlist_id_map
    global _initial_comment_id_map

    _initial_user_id_map = {}
    _initial_channel_id_map = {}
    _initial_video_id_map = {}
    _initial_playlist_id_map = {}
    _initial_comment_id_map = {}

    current_time_iso = datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"

    # --- Convert Users ---
    new_users = {}
    for old_user_email, user_data in converted_data.get("users", {}).items():
        user_uuid = str(uuid.uuid4())
        _initial_user_id_map[old_user_email] = user_uuid
        user_data["user_id"] = user_uuid # Ensure the internal 'user_id' also reflects the UUID
        user_data["email"] = f"user_{user_uuid[:8]}@example.com" # Make email more realistic/dummy
        if "joined_date" not in user_data:
            user_data["joined_date"] = current_time_iso
        elif not isinstance(user_data["joined_date"], str):
             user_data["joined_date"] = user_data["joined_date"].isoformat(timespec='milliseconds') + "Z"
        new_users[user_uuid] = user_data
    converted_data["users"] = new_users

    # --- Convert Channels ---
    new_channels = {}
    for old_channel_id, channel_data in converted_data.get("channels", {}).items():
        channel_uuid = str(uuid.uuid4())
        _initial_channel_id_map[old_channel_id] = channel_uuid
        channel_data["id"] = channel_uuid # Ensure the internal 'id' also reflects the UUID

        # Convert owner_id to user UUID
        if "owner_id" in channel_data and channel_data["owner_id"] in _initial_user_id_map:
            channel_data["owner_id"] = _initial_user_id_map[channel_data["owner_id"]]
        else: # Assign to a default user if owner_id is missing or invalid
            first_user_uuid = next(iter(new_users.keys()), None)
            if first_user_uuid:
                channel_data["owner_id"] = first_user_uuid
            else:
                channel_data["owner_id"] = str(uuid.uuid4()) # Fallback for no users
        
        # Convert created_at to ISO 8601
        if "created_at" not in channel_data:
            channel_data["created_at"] = current_time_iso
        elif not isinstance(channel_data["created_at"], str):
            channel_data["created_at"] = channel_data["created_at"].isoformat(timespec='milliseconds') + "Z"

        new_channels[channel_uuid] = channel_data
    converted_data["channels"] = new_channels

    # --- Convert Videos ---
    new_videos = {}
    for old_video_id, video_data in converted_data.get("videos", {}).items():
        video_uuid = str(uuid.uuid4())
        _initial_video_id_map[old_video_id] = video_uuid
        video_data["id"] = video_uuid # Ensure the internal 'id' also reflects the UUID

        # Convert channel_id and uploader_id to UUIDs
        if "channel_id" in video_data and video_data["channel_id"] in _initial_channel_id_map:
            video_data["channel_id"] = _initial_channel_id_map[video_data["channel_id"]]
        if "uploader_id" in video_data and video_data["uploader_id"] in _initial_user_id_map:
            video_data["uploader_id"] = _initial_user_id_map[video_data["uploader_id"]]

        # Convert published_at to ISO 8601
        if "published_at" not in video_data:
            video_data["published_at"] = current_time_iso
        elif not isinstance(video_data["published_at"], str):
            video_data["published_at"] = video_data["published_at"].isoformat(timespec='milliseconds') + "Z"
        
        # Convert 'liked_by' list to user UUIDs
        if "liked_by" in video_data:
            video_data["liked_by"] = [
                _initial_user_id_map.get(u_id, u_id) for u_id in video_data["liked_by"]
            ]
            video_data["liked_by"] = [
                u_id for u_id in video_data["liked_by"] if u_id in new_users
            ]

        new_videos[video_uuid] = video_data
    converted_data["videos"] = new_videos

    # --- Convert Playlists ---
    new_playlists = {}
    for old_playlist_id, playlist_data in converted_data.get("playlists", {}).items():
        playlist_uuid = str(uuid.uuid4())
        _initial_playlist_id_map[old_playlist_id] = playlist_uuid
        playlist_data["id"] = playlist_uuid # Ensure the internal 'id' also reflects the UUID

        # Convert owner_id (user UUID) and channel_id (channel UUID)
        if "owner_id" in playlist_data and playlist_data["owner_id"] in _initial_user_id_map:
            playlist_data["owner_id"] = _initial_user_id_map[playlist_data["owner_id"]]
        if "channel_id" in playlist_data and playlist_data["channel_id"] in _initial_channel_id_map:
            playlist_data["channel_id"] = _initial_channel_id_map[playlist_data["channel_id"]]

        # Convert video_ids to video UUIDs
        if "video_ids" in playlist_data:
            playlist_data["video_ids"] = [
                _initial_video_id_map.get(v_id, v_id) for v_id in playlist_data["video_ids"]
            ]
            playlist_data["video_ids"] = [
                v_id for v_id in playlist_data["video_ids"] if v_id in new_videos
            ]
        
        # Convert created_at to ISO 8601
        if "created_at" not in playlist_data:
            playlist_data["created_at"] = current_time_iso
        elif not isinstance(playlist_data["created_at"], str):
            playlist_data["created_at"] = playlist_data["created_at"].isoformat(timespec='milliseconds') + "Z"

        new_playlists[playlist_uuid] = playlist_data
    converted_data["playlists"] = new_playlists

    # --- Convert Comments ---
    new_comments = {}
    for old_comment_id, comment_data in converted_data.get("comments", {}).items():
        comment_uuid = str(uuid.uuid4())
        _initial_comment_id_map[old_comment_id] = comment_uuid
        comment_data["id"] = comment_uuid # Ensure the internal 'id' also reflects the UUID

        # Convert video_id (video UUID) and author_id (user UUID)
        if "video_id" in comment_data and comment_data["video_id"] in _initial_video_id_map:
            comment_data["video_id"] = _initial_video_id_map[comment_data["video_id"]]
        if "author_id" in comment_data and comment_data["author_id"] in _initial_user_id_map:
            comment_data["author_id"] = _initial_user_id_map[comment_data["author_id"]]
        
        # Convert created_at to ISO 8601
        if "created_at" not in comment_data:
            comment_data["created_at"] = current_time_iso
        elif not isinstance(comment_data["created_at"], str):
            comment_data["created_at"] = comment_data["created_at"].isoformat(timespec='milliseconds') + "Z"

        new_comments[comment_uuid] = comment_data
    converted_data["comments"] = new_comments

    # --- Update References in Users, Channels, Videos with new UUIDs ---
    for user_uuid, user_data in new_users.items():
        if "channels" in user_data:
            user_data["channels"] = [
                _initial_channel_id_map.get(c_id, c_id) for c_id in user_data["channels"]
            ]
            user_data["channels"] = [
                c_id for c_id in user_data["channels"] if c_id in new_channels
            ]
        if "subscriptions" in user_data:
            user_data["subscriptions"] = [
                _initial_channel_id_map.get(s_id, s_id) for s_id in user_data["subscriptions"]
            ]
            user_data["subscriptions"] = [
                s_id for s_id in user_data["subscriptions"] if s_id in new_channels
            ]
        if "watch_history" in user_data:
            user_data["watch_history"] = [
                _initial_video_id_map.get(v_id, v_id) for v_id in user_data["watch_history"]
            ]
            user_data["watch_history"] = [
                v_id for v_id in user_data["watch_history"] if v_id in new_videos
            ]
        if "liked_videos" in user_data:
            user_data["liked_videos"] = [
                _initial_video_id_map.get(v_id, v_id) for v_id in user_data["liked_videos"]
            ]
            user_data["liked_videos"] = [
                v_id for v_id in user_data["liked_videos"] if v_id in new_videos
            ]

    for channel_uuid, channel_data in new_channels.items():
        if "subscribers" in channel_data:
            channel_data["subscribers"] = [
                _initial_user_id_map.get(u_id, u_id) for u_id in channel_data["subscribers"]
            ]
            channel_data["subscribers"] = [
                u_id for u_id in channel_data["subscribers"] if u_id in new_users
            ]
        if "videos" in channel_data:
            channel_data["videos"] = [
                _initial_video_id_map.get(v_id, v_id) for v_id in channel_data["videos"]
            ]
            channel_data["videos"] = [
                v_id for v_id in channel_data["videos"] if v_id in new_videos
            ]
    
    for video_uuid, video_data in new_videos.items():
        if "comments" in video_data:
            video_data["comments"] = [
                _initial_comment_id_map.get(c_id, c_id) for c_id in video_data["comments"]
            ]
            video_data["comments"] = [
                c_id for c_id in video_data["comments"] if c_id in new_comments
            ]
        
    # Set current_user and current_channel to their new UUIDs
    if converted_data.get("current_user") in _initial_user_id_map:
        converted_data["current_user"] = _initial_user_id_map[converted_data["current_user"]]
    elif new_users: # Default to first user if specified current_user wasn't mapped
        converted_data["current_user"] = next(iter(new_users.keys()))
    else:
        converted_data["current_user"] = None

    if converted_data.get("current_channel") in _initial_channel_id_map:
        converted_data["current_channel"] = _initial_channel_id_map[converted_data["current_channel"]]
    elif new_channels: # Default to first channel if specified current_channel wasn't mapped
        converted_data["current_channel"] = next(iter(new_channels.keys()))
    else:
        converted_data["current_channel"] = None

    return converted_data

# Define the initial raw state with string IDs for conversion
RAW_DEFAULT_STATE = {
    "current_user": "alice.smith@example.com", # Will be converted to UUID
    "current_channel": "UC_AliceVlogs", # Will be converted to UUID
    "users": {
        "alice.smith@example.com": {
            "user_id": "user_alice", # Will be converted to UUID
            "display_name": "Alice Smith",
            "email": "alice.smith@example.com", # Will be updated to dummy email based on UUID
            "joined_date": datetime.datetime(2023, 1, 15, 10, 0, 0, tzinfo=datetime.timezone.utc),
            "channels": ["UC_AliceVlogs", "UC_AliceGaming"], # Will be converted to UUIDs
            "subscriptions": ["UC_BobTech", "UC_CharlieCooks"], # Will be converted to UUIDs
            "watch_history": ["vid_001", "vid_003", "vid_005"], # Will be converted to UUIDs
            "liked_videos": ["vid_001", "vid_004"], # Will be converted to UUIDs
        },
        "bob.jones@example.com": {
            "user_id": "user_bob", # Will be converted to UUID
            "display_name": "Bob Jones",
            "email": "bob.jones@example.com", # Will be updated to dummy email based on UUID
            "joined_date": datetime.datetime(2022, 11, 1, 14, 30, 0, tzinfo=datetime.timezone.utc),
            "channels": ["UC_BobTech"], # Will be converted to UUIDs
            "subscriptions": ["UC_AliceVlogs"], # Will be converted to UUIDs
            "watch_history": ["vid_002", "vid_004"], # Will be converted to UUIDs
            "liked_videos": ["vid_002"], # Will be converted to UUIDs
        },
        "charlie.brown@example.com": {
            "user_id": "user_charlie", # Will be converted to UUID
            "display_name": "Charlie Brown",
            "email": "charlie.brown@example.com", # Will be updated to dummy email based on UUID
            "joined_date": datetime.datetime(2024, 3, 20, 9, 0, 0, tzinfo=datetime.timezone.utc),
            "channels": ["UC_CharlieCooks"], # Will be converted to UUIDs
            "subscriptions": ["UC_AliceVlogs", "UC_BobTech"], # Will be converted to UUIDs
            "watch_history": ["vid_001", "vid_002"], # Will be converted to UUIDs
            "liked_videos": [],
        }
    },
    "channels": {
        "UC_AliceVlogs": {
            "id": "UC_AliceVlogs", # Will be converted to UUID
            "title": "Alice's Daily Vlogs",
            "description": "Daily life vlogs and adventures.",
            "owner_id": "alice.smith@example.com", # Will be converted to UUID
            "created_at": datetime.datetime(2023, 2, 1, 12, 0, 0, tzinfo=datetime.timezone.utc),
            "subscribers": ["bob.jones@example.com", "charlie.brown@example.com"], # Will be converted to UUIDs
            "videos": ["vid_001", "vid_003"], # Will be converted to UUIDs
            "playlists": ["playlist_001"], # Will be converted to UUIDs
            "country": "US",
            "view_count": 12000,
            "subscriber_count": 500,
            "video_count": 2,
            "banner_image_path": "https://example.com/channel_banners/alice_vlogs_banner.jpg"
        },
        "UC_BobTech": {
            "id": "UC_BobTech", # Will be converted to UUID
            "title": "Bob's Tech Reviews",
            "description": "Unbiased tech reviews and tutorials.",
            "owner_id": "bob.jones@example.com", # Will be converted to UUID
            "created_at": datetime.datetime(2022, 12, 10, 9, 30, 0, tzinfo=datetime.timezone.utc),
            "subscribers": ["alice.smith@example.com", "charlie.brown@example.com"], # Will be converted to UUIDs
            "videos": ["vid_002", "vid_004"], # Will be converted to UUIDs
            "playlists": ["playlist_002"], # Will be converted to UUIDs
            "country": "CA",
            "view_count": 25000,
            "subscriber_count": 1200,
            "video_count": 2,
            "banner_image_path": "https://example.com/channel_banners/bob_tech_banner.jpg"
        },
        "UC_CharlieCooks": {
            "id": "UC_CharlieCooks", # Will be converted to UUID
            "title": "Charlie's Cooking Adventures",
            "description": "Easy and delicious recipes for everyone.",
            "owner_id": "charlie.brown@example.com", # Will be converted to UUID
            "created_at": datetime.datetime(2024, 4, 1, 10, 0, 0, tzinfo=datetime.timezone.utc),
            "subscribers": ["alice.smith@example.com"], # Will be converted to UUIDs
            "videos": ["vid_005"], # Will be converted to UUIDs
            "playlists": [],
            "country": "GB",
            "view_count": 8000,
            "subscriber_count": 300,
            "video_count": 1,
            "banner_image_path": "https://example.com/channel_banners/charlie_cooks_banner.jpg"
        },
        "UC_AliceGaming": { # Another channel for Alice
            "id": "UC_AliceGaming", # Will be converted to UUID
            "title": "Alice's Gaming Zone",
            "description": "Gameplay, streams, and gaming news.",
            "owner_id": "alice.smith@example.com", # Will be converted to UUID
            "created_at": datetime.datetime(2023, 5, 10, 16, 0, 0, tzinfo=datetime.timezone.utc),
            "subscribers": [],
            "videos": [],
            "playlists": [],
            "country": "US",
            "view_count": 1500,
            "subscriber_count": 50,
            "video_count": 0,
            "banner_image_path": "https://example.com/channel_banners/alice_gaming_banner.jpg"
        }
    },
    "videos": {
        "vid_001": {
            "id": "vid_001", # Will be converted to UUID
            "title": "My First Vlog: Exploring New York",
            "description": "A tour of New York City's landmarks.",
            "channel_id": "UC_AliceVlogs", # Will be converted to UUID
            "uploader_id": "alice.smith@example.com", # Will be converted to UUID
            "published_at": datetime.datetime(2023, 2, 5, 15, 0, 0, tzinfo=datetime.timezone.utc),
            "duration_seconds": 600,
            "views": 5000,
            "likes": 250,
            "dislikes": 10,
            "comments": ["comment_001", "comment_002"], # Will be converted to UUIDs
            "tags": ["travel", "vlog", "NYC"]
        },
        "vid_002": {
            "id": "vid_002", # Will be converted to UUID
            "title": "Best Budget Smartphones 2024",
            "description": "Review of affordable smartphones.",
            "channel_id": "UC_BobTech", # Will be converted to UUID
            "uploader_id": "bob.jones@example.com", # Will be converted to UUID
            "published_at": datetime.datetime(2023, 1, 20, 11, 0, 0, tzinfo=datetime.timezone.utc),
            "duration_seconds": 900,
            "views": 10000,
            "likes": 800,
            "dislikes": 25,
            "comments": ["comment_003"], # Will be converted to UUIDs
            "tags": ["tech", "review", "smartphone"]
        },
        "vid_003": {
            "id": "vid_003", # Will be converted to UUID
            "title": "Morning Routine & Productivity Tips",
            "description": "How I stay productive throughout the day.",
            "channel_id": "UC_AliceVlogs", # Will be converted to UUID
            "uploader_id": "alice.smith@example.com", # Will be converted to UUID
            "published_at": datetime.datetime(2023, 3, 1, 9, 0, 0, tzinfo=datetime.timezone.utc),
            "duration_seconds": 480,
            "views": 3000,
            "likes": 150,
            "dislikes": 5,
            "comments": [],
            "tags": ["productivity", "routine", "lifestyle"]
        },
        "vid_004": {
            "id": "vid_004", # Will be converted to UUID
            "title": "Gaming PC Build Guide 2024",
            "description": "Step-by-step guide to building a gaming PC.",
            "channel_id": "UC_BobTech", # Will be converted to UUID
            "uploader_id": "bob.jones@example.com", # Will be converted to UUID
            "published_at": datetime.datetime(2023, 4, 10, 18, 0, 0, tzinfo=datetime.timezone.utc),
            "duration_seconds": 1200,
            "views": 15000,
            "likes": 1200,
            "dislikes": 30,
            "comments": [],
            "tags": ["gaming", "PCBuild", "tutorial"]
        },
        "vid_005": {
            "id": "vid_005", # Will be converted to UUID
            "title": "Easy Pasta Carbonara Recipe",
            "description": "A quick and delicious carbonara recipe.",
            "channel_id": "UC_CharlieCooks", # Will be converted to UUID
            "uploader_id": "charlie.brown@example.com", # Will be converted to UUID
            "published_at": datetime.datetime(2024, 4, 5, 14, 0, 0, tzinfo=datetime.timezone.utc),
            "duration_seconds": 360,
            "views": 7000,
            "likes": 400,
            "dislikes": 8,
            "comments": [],
            "tags": ["cooking", "recipe", "pasta"]
        }
    },
    "playlists": {
        "playlist_001": {
            "id": "playlist_001", # Will be converted to UUID
            "title": "My Favorite Vlogs",
            "description": "A collection of my best vlogs.",
            "owner_id": "alice.smith@example.com", # Will be converted to UUID
            "channel_id": "UC_AliceVlogs", # Will be converted to UUID
            "video_ids": ["vid_001", "vid_003"], # Will be converted to UUIDs
            "created_at": datetime.datetime(2023, 2, 10, 16, 0, 0, tzinfo=datetime.timezone.utc),
            "privacy_status": "public",
            "item_count": 2
        },
        "playlist_002": {
            "id": "playlist_002", # Will be converted to UUID
            "title": "Tech Essentials",
            "description": "Must-watch tech videos.",
            "owner_id": "bob.jones@example.com", # Will be converted to UUID
            "channel_id": "UC_BobTech", # Will be converted to UUID
            "video_ids": ["vid_002", "vid_004"], # Will be converted to UUIDs
            "created_at": datetime.datetime(2023, 1, 25, 10, 0, 0, tzinfo=datetime.timezone.utc),
            "privacy_status": "public",
            "item_count": 2
        }
    },
    "comments": {
        "comment_001": {
            "id": "comment_001", # Will be converted to UUID
            "video_id": "vid_001", # Will be converted to UUID
            "author_id": "bob.jones@example.com", # Will be converted to UUID
            "text": "Great vlog, Alice! Really enjoyed the NYC tour.",
            "created_at": datetime.datetime(2023, 2, 6, 10, 0, 0, tzinfo=datetime.timezone.utc),
            "likes": 5
        },
        "comment_002": {
            "id": "comment_002", # Will be converted to UUID
            "video_id": "vid_001", # Will be converted to UUID
            "author_id": "charlie.brown@example.com", # Will be converted to UUID
            "text": "Made me want to visit NYC again!",
            "created_at": datetime.datetime(2023, 2, 6, 11, 30, 0, tzinfo=datetime.timezone.utc),
            "likes": 2
        },
        "comment_003": {
            "id": "comment_003", # Will be converted to UUID
            "video_id": "vid_002", # Will be converted to UUID
            "author_id": "alice.smith@example.com", # Will be converted to UUID
            "text": "Very informative review, Bob! Helped me decide on my next phone.",
            "created_at": datetime.datetime(2023, 1, 21, 14, 0, 0, tzinfo=datetime.timezone.utc),
            "likes": 8
        }
    }
}

# The actual DEFAULT_STATE used by the API will be the converted one
DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)


class YouTubeApis:
    """
    A dummy API class for simulating YouTube operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the YouTubeApis instance, setting up the in-memory
        data stores and loading the default scenario.
        """
        self._api_description = "This tool simulates YouTube functionalities, allowing management of channels, videos, playlists, and comments."
        self.users: Dict[str, Any] = {} # Keyed by user UUID
        self.channels: Dict[str, Any] = {} # Keyed by channel UUID
        self.videos: Dict[str, Any] = {} # Keyed by video UUID
        self.playlists: Dict[str, Any] = {} # Keyed by playlist UUID
        self.comments: Dict[str, Any] = {} # Keyed by comment UUID
        self.current_user: Optional[str] = None # Stores the UUID of the current user
        self.current_channel: Optional[str] = None # Stores the UUID of the current channel

        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain "users", "channels", "videos", "playlists", "comments".
        """
        # Create deep copy to ensure the original DEFAULT_STATE is not modified
        self.users = copy.deepcopy(scenario.get("users", {}))
        self.channels = copy.deepcopy(scenario.get("channels", {}))
        self.videos = copy.deepcopy(scenario.get("videos", {}))
        self.playlists = copy.deepcopy(scenario.get("playlists", {}))
        self.comments = copy.deepcopy(scenario.get("comments", {}))
        self.current_user = scenario.get("current_user") # This will already be a UUID after conversion
        self.current_channel = scenario.get("current_channel") # This will already be a UUID after conversion
        print("YouTubeApis: Loaded scenario with UUIDs for users, channels, videos, playlists, and comments.")

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for dummy entities.
        """
        return str(uuid.uuid4())

    # --- Helper functions for data access ---
    def _get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get a user's data based on their UUID."""
        return self.users.get(user_id)

    def _update_user_data(self, user_id: str, key: str, value: Any) -> bool:
        """Helper to update a specific key in a user's data by UUID."""
        if user_id in self.users:
            self.users[user_id][key] = value
            return True
        return False

    def _get_channel_data(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get a channel's data based on its UUID."""
        return self.channels.get(channel_id)

    def _update_channel_data(self, channel_id: str, key: str, value: Any) -> bool:
        """Helper to update a specific key in a channel's data by UUID."""
        if channel_id in self.channels:
            self.channels[channel_id][key] = value
            return True
        return False

    def _get_video_data(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get a video's data based on its UUID."""
        return self.videos.get(video_id)

    def _update_video_data(self, video_id: str, key: str, value: Any) -> bool:
        """Helper to update a specific key in a video's data by UUID."""
        if video_id in self.videos:
            self.videos[video_id][key] = value
            return True
        return False
    
    def _get_playlist_data(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get a playlist's data based on its UUID."""
        return self.playlists.get(playlist_id)

    def _update_playlist_data(self, playlist_id: str, key: str, value: Any) -> bool:
        """Helper to update a specific key in a playlist's data by UUID."""
        if playlist_id in self.playlists:
            self.playlists[playlist_id][key] = value
            return True
        return False
    
    def _get_comment_data(self, comment_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get a comment's data based on its UUID."""
        return self.comments.get(comment_id)

    def _update_comment_data(self, comment_id: str, key: str, value: Any) -> bool:
        """Helper to update a specific key in a comment's data by UUID."""
        if comment_id in self.comments:
            self.comments[comment_id][key] = value
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
            return {"status": True, "message": f"Current user set to {self.users[user_id]['display_name']} (ID: {user_id})."}
        return {"status": False, "message": f"User with ID {user_id} not found."}

    def set_current_channel(self, channel_id: str) -> Dict[str, Union[bool, str]]:
        """
        Sets the current active channel for the API session.
        The current user must own this channel.

        Args:
            channel_id (str): The ID (UUID) of the channel to set as current.

        Returns:
            Dict[str, Union[bool, str]]: A dictionary with 'status' indicating success or failure and a message.
        """
        if not self.current_user:
            return {"status": False, "message": "No current user set. Please set a current user first."}
        
        channel_data = self._get_channel_data(channel_id)
        if channel_data:
            if channel_data.get("owner_id") == self.current_user:
                self.current_channel = channel_id
                return {"status": True, "message": f"Current channel set to {channel_data['title']} (ID: {channel_id})."}
            return {"status": False, "message": "You do not own this channel."}
        return {"status": False, "message": f"Channel with ID {channel_id} not found."}

    # ====================
    # User Operations
    # ====================

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
            return {"data": copy.deepcopy(user_data)}
        return {"data": None, "error": "User not found"}

    def get_watch_history(self, user_id: str) -> Dict[str, Any]:
        """
        Get the watch history for a specific user.

        Args:
            user_id (str): The ID (UUID) of the user whose watch history is to be retrieved.

        Returns:
            Dict: A dictionary containing a list of video IDs in the watch history.
        """
        user_data = self._get_user_data(user_id)
        if user_data:
            watched_videos = []
            for video_uuid in user_data.get("watch_history", []):
                video_details = self._get_video_data(video_uuid)
                if video_details:
                    watched_videos.append(copy.deepcopy(video_details))
            return {"data": watched_videos}
        return {"data": None, "error": "User not found"}

    def list_subscriptions(self, user_id: str) -> Dict[str, Any]:
        """
        List the channels a specific user is subscribed to.

        Args:
            user_id (str): The ID (UUID) of the user whose subscriptions are to be listed.

        Returns:
            Dict: A dictionary containing a list of subscribed channel IDs.
        """
        user_data = self._get_user_data(user_id)
        if user_data:
            subscribed_channels = []
            for channel_uuid in user_data.get("subscriptions", []):
                channel_details = self._get_channel_data(channel_uuid)
                if channel_details:
                    subscribed_channels.append(copy.deepcopy(channel_details))
            return {"data": subscribed_channels}
        return {"data": None, "error": "User not found"}
    
    def youtube_subscriptions_insert(self, channel_id: str, user_id: str) -> Dict[str, Any]:
        """
        Subscribes a user to a channel.

        Parameters:
            channel_id (str): The ID (UUID) of the channel to subscribe to.
            user_id (str): The ID (UUID) of the user subscribing.

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the subscription.
        """
        user_data = self._get_user_data(user_id)
        channel_data = self._get_channel_data(channel_id)

        if not user_data:
            return {"error": "User not found.", "success": False}
        if not channel_data:
            return {"error": "Channel not found.", "success": False}
        
        if channel_id in user_data.get("subscriptions", []):
            return {"error": "Already subscribed.", "success": False}
        
        user_data["subscriptions"].append(channel_id)
        channel_data["subscribers"].append(user_id)
        channel_data["subscriber_count"] = channel_data.get("subscriber_count", 0) + 1
        
        return {"success": True, "channel_id": channel_id, "user_id": user_id}

    def youtube_subscriptions_delete(self, channel_id: str, user_id: str) -> Dict[str, Any]:
        """
        Unsubscribes a user from a channel.

        Parameters:
            channel_id (str): The ID (UUID) of the channel to unsubscribe from.
            user_id (str): The ID (UUID) of the user unsubscribing.

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the unsubscription.
        """
        user_data = self._get_user_data(user_id)
        channel_data = self._get_channel_data(channel_id)

        if not user_data:
            return {"error": "User not found.", "success": False}
        if not channel_data:
            return {"error": "Channel not found.", "success": False}
        
        if channel_id not in user_data.get("subscriptions", []):
            return {"error": "Not subscribed to this channel.", "success": False}
        
        user_data["subscriptions"].remove(channel_id)
        if user_id in channel_data.get("subscribers", []):
            channel_data["subscribers"].remove(user_id)
        channel_data["subscriber_count"] = max(0, channel_data.get("subscriber_count", 0) - 1)
        
        return {"success": True, "channel_id": channel_id, "user_id": user_id}


    # ====================
    # Channel Operations
    # ====================

    def list_channels_for_user(self, user_id: str) -> Dict[str, Any]:
        """
        List all channels owned by a specific user.

        Args:
            user_id (str): The ID (UUID) of the user whose channels are to be listed.

        Returns:
            Dict: A dictionary containing a list of channels.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"data": None, "error": "User not found"}
        
        user_channels = []
        for channel_uuid in user_data.get("channels", []):
            channel_details = self._get_channel_data(channel_uuid)
            if channel_details:
                user_channels.append(copy.deepcopy(channel_details))
        return {"data": user_channels}

    def get_channel_details(self, channel_id: str) -> Dict[str, Any]:
        """
        Get the details of a specific channel.

        Args:
            channel_id (str): The ID (UUID) of the channel to retrieve.

        Returns:
            Dict: A dictionary containing the channel's data.
        """
        channel_data = self._get_channel_data(channel_id)
        if channel_data:
            return {"data": copy.deepcopy(channel_data)}
        return {"data": None, "error": "Channel not found"}

    def create_channel(self, user_id: str, title: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new channel for a specific user.

        Args:
            user_id (str): The ID (UUID) of the user creating the channel.
            title (str): The title of the new channel.
            description (str, optional): The description of the new channel. Defaults to "".

        Returns:
            Dict: A dictionary containing the newly created channel's data.
        """
        if user_id not in self.users:
            return {"data": None, "error": "User not found"}

        channel_uuid = self._generate_unique_id()
        new_channel = {
            "id": channel_uuid,
            "title": title,
            "description": description,
            "owner_id": user_id,
            "created_at": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z",
            "subscribers": [],
            "videos": [],
            "playlists": [],
            "country": "US", # Default country
            "view_count": 0,
            "subscriber_count": 0,
            "video_count": 0,
            "banner_image_path": "https://example.com/default_banner.jpg"
        }
        self.channels[channel_uuid] = new_channel
        self.users[user_id]["channels"].append(channel_uuid)
        print(f"Channel created: ID={channel_uuid} by {self.users[user_id]['display_name']}")
        return {"data": copy.deepcopy(new_channel)}

    def youtube_channels_update(self, channel_id: str, updates: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Updates a channel's properties.

        Parameters:
            channel_id (str): The ID (UUID) of the channel to update.
            updates (Dict[str, Any]): A dictionary containing the fields to update (e.g., {"title": "New Title", "description": "New Description"}).
            user_id (str): The ID (UUID) of the user requesting the update. Must be the channel owner.

        Returns:
            Dict[str, Any]: The updated channel information.
        """
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            return {"error": "Channel not found."}
        
        if channel_data.get("owner_id") != user_id:
            return {"error": "User is not the owner of this channel."}

        for key, value in updates.items():
            if key in channel_data: # Only allow updating existing fields for simplicity
                channel_data[key] = value
        
        return {"data": copy.deepcopy(channel_data)}

    def youtube_channel_banners_insert(self, image_path: str, channel_id: str) -> Dict[str, Any]:
        """
        Uploads a channel banner image to YouTube for a specific channel.

        Parameters:
            image_path (str): The path to the banner image file.
            channel_id (str): The ID (UUID) of the channel to upload the banner for.

        Returns:
            Dict[str, Any]: A dictionary containing information about the uploaded banner.
        """
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            return {"error": "Channel not found."}
        
        # In a real API, this would upload the image and return a URL
        # For this dummy, we'll just acknowledge the upload and store the path
        channel_data["banner_image_path"] = image_path
        return {"success": True, "image_path": image_path, "channel_id": channel_id}


    # ====================
    # Video Operations
    # ====================

    def list_videos_in_channel(self, channel_id: str) -> Dict[str, Any]:
        """
        List all videos belonging to a specific channel.

        Args:
            channel_id (str): The ID (UUID) of the channel whose videos are to be listed.

        Returns:
            Dict: A dictionary containing a list of videos.
        """
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            return {"data": None, "error": "Channel not found"}
        
        channel_videos = []
        for video_uuid in channel_data.get("videos", []):
            video_details = self._get_video_data(video_uuid)
            if video_details:
                channel_videos.append(copy.deepcopy(video_details))
        return {"data": channel_videos}

    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Get the details of a specific video.

        Args:
            video_id (str): The ID (UUID) of the video to retrieve.

        Returns:
            Dict: A dictionary containing the video's data.
        """
        video_data = self._get_video_data(video_id)
        if video_data:
            # Increment view count for realism
            video_data["views"] = video_data.get("views", 0) + 1 
            return {"data": copy.deepcopy(video_data)}
        return {"data": None, "error": "Video not found"}
    
    def upload_video(self, channel_id: str, title: str, description: str = "", duration_seconds: int = 0, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Upload a new video to a specified channel.

        Args:
            channel_id (str): The ID (UUID) of the channel to upload the video to.
            title (str): The title of the video.
            description (str, optional): The description of the video. Defaults to "".
            duration_seconds (int, optional): The duration of the video in seconds. Defaults to 0.
            tags (Optional[List[str]], optional): A list of tags for the video. Defaults to None.

        Returns:
            Dict: A dictionary containing the newly created video's data.
        """
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            return {"data": None, "error": "Channel not found"}
        
        uploader_id = channel_data["owner_id"]
        if not uploader_id or uploader_id not in self.users:
            return {"data": None, "error": "Uploader user not found for this channel."}

        video_uuid = self._generate_unique_id()
        new_video = {
            "id": video_uuid,
            "title": title,
            "description": description,
            "channel_id": channel_id,
            "uploader_id": uploader_id,
            "published_at": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z",
            "duration_seconds": duration_seconds,
            "views": 0,
            "likes": 0,
            "dislikes": 0,
            "comments": [],
            "tags": tags if tags is not None else [],
            "liked_by": [] # Keep track of users who liked this video
        }
        self.videos[video_uuid] = new_video
        self.channels[channel_id]["videos"].append(video_uuid)
        self.channels[channel_id]["video_count"] = self.channels[channel_id].get("video_count", 0) + 1
        print(f"Video uploaded: ID={video_uuid} to channel {channel_data['title']}")
        return {"data": copy.deepcopy(new_video)}

    def delete_video(self, video_id: str, channel_id: str, user_id: str) -> Dict[str, bool]:
        """
        Delete a video. Only the uploader (channel owner) can delete their video.

        Args:
            video_id (str): The ID (UUID) of the video to delete.
            channel_id (str): The ID (UUID) of the channel the video belongs to.
            user_id (str): The ID (UUID) of the user attempting to delete (must be channel owner).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating the operation's outcome.
        """
        video_data = self._get_video_data(video_id)
        channel_data = self._get_channel_data(channel_id)

        if not video_data:
            return {"success": False, "error": "Video not found"}
        if not channel_data:
            return {"success": False, "error": "Channel not found"}
        
        if video_data.get("channel_id") != channel_id:
            return {"success": False, "error": "Video does not belong to the specified channel"}
        if channel_data.get("owner_id") != user_id:
            return {"success": False, "error": "User is not the owner of this channel and cannot delete videos"}

        if video_id in self.videos:
            del self.videos[video_id]
            # Remove from channel's video list
            if video_id in self.channels[channel_id].get("videos", []):
                self.channels[channel_id]["videos"].remove(video_id)
                self.channels[channel_id]["video_count"] = max(0, self.channels[channel_id].get("video_count", 0) - 1)
            
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
            
            # Delete associated comments
            comments_to_delete = [cid for cid, cdata in self.comments.items() if cdata.get("video_id") == video_id]
            for cid in comments_to_delete:
                del self.comments[cid]

            return {"success": True}
        return {"success": False, "error": "Video not found or internal error"}

    def youtube_videos_rate(self, video_id: str, rating: str, user_id: str) -> Dict[str, Any]:
        """
        Rates a video (like or dislike).

        Parameters:
            video_id (str): The ID (UUID) of the video to rate.
            rating (str): The rating to apply ("like" or "dislike").
            user_id (str): The ID (UUID) of the user rating the video.

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the rating.
        """
        video_data = self._get_video_data(video_id)
        user_data = self._get_user_data(user_id)

        if not video_data:
            return {"error": "Video not found.", "success": False}
        if not user_data:
            return {"error": "User not found.", "success": False}

        liked_by_list = video_data.get("liked_by", [])
        
        if rating == "like":
            if user_id not in liked_by_list:
                video_data["likes"] = video_data.get("likes", 0) + 1
                liked_by_list.append(user_id)
                if video_id not in user_data.get("liked_videos", []):
                    user_data["liked_videos"].append(video_id)
            return {"success": True, "message": f"Video {video_id} liked by {user_id}."}
        elif rating == "dislike":
            if user_id in liked_by_list:
                video_data["likes"] = max(0, video_data.get("likes", 0) - 1)
                liked_by_list.remove(user_id)
            video_data["dislikes"] = video_data.get("dislikes", 0) + 1
            if video_id in user_data.get("liked_videos", []):
                user_data["liked_videos"].remove(video_id) # Remove from liked if disliked
            return {"success": True, "message": f"Video {video_id} disliked by {user_id}."}
        else:
            return {"error": "Invalid rating. Must be 'like' or 'dislike'.", "success": False}

    def like_video(self, video_id: str, user_id: str) -> Dict[str, bool]:
        """
        Mark a video as liked by the user. This is a simplified wrapper around youtube_videos_rate.
        """
        result = self.youtube_videos_rate(video_id, "like", user_id)
        return {"success": result.get("success", False)}

    def unlike_video(self, video_id: str, user_id: str) -> Dict[str, bool]:
        """
        Mark a video as unliked by the user (effectively a dislike in this dummy, or just removal of like).
        """
        # For simplicity, if unliking means removing the like without adding a dislike, adjust logic.
        # Current youtube_videos_rate("dislike") increments dislike.
        # Let's adjust this to specifically "unlike" without necessarily "disliking" for this wrapper.
        video_data = self._get_video_data(video_id)
        user_data = self._get_user_data(user_id)
        if not video_data or not user_data:
            return {"success": False, "error": "Video or user not found."}
        
        liked_by_list = video_data.get("liked_by", [])
        if user_id in liked_by_list:
            video_data["likes"] = max(0, video_data.get("likes", 0) - 1)
            liked_by_list.remove(user_id)
            if video_id in user_data.get("liked_videos", []):
                user_data["liked_videos"].remove(video_id)
            return {"success": True}
        return {"success": False, "error": "Video not previously liked by this user."}

    def search_videos(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for videos based on a query string in titles or descriptions.

        Args:
            query (str): The search query.
            max_results (int): The maximum number of results to return.

        Returns:
            Dict: A dictionary containing a list of matching video data.
        """
        query_lower = query.lower()
        matching_videos = []
        for video_uuid, video_data in self.videos.items():
            if query_lower in video_data.get("title", "").lower() or \
               query_lower in video_data.get("description", "").lower() or \
               any(query_lower in tag.lower() for tag in video_data.get("tags", [])):
                matching_videos.append(copy.deepcopy(video_data))
        
        # Sort by views (most popular first) for a more realistic search result
        matching_videos.sort(key=lambda x: x.get("views", 0), reverse=True)
        return {"data": matching_videos[:max_results]}

    # ====================
    # Playlist Operations
    # ====================

    def list_playlists_in_channel(self, channel_id: str) -> Dict[str, Any]:
        """
        List all playlists belonging to a specific channel.

        Args:
            channel_id (str): The ID (UUID) of the channel whose playlists are to be listed.

        Returns:
            Dict: A dictionary containing a list of playlists.
        """
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            return {"data": None, "error": "Channel not found"}
        
        channel_playlists = []
        for playlist_uuid in channel_data.get("playlists", []):
            playlist_details = self._get_playlist_data(playlist_uuid)
            if playlist_details:
                channel_playlists.append(copy.deepcopy(playlist_details))
        return {"data": channel_playlists}

    def get_playlist_details(self, playlist_id: str) -> Dict[str, Any]:
        """
        Get the details of a specific playlist, including its videos.

        Args:
            playlist_id (str): The ID (UUID) of the playlist to retrieve.

        Returns:
            Dict: A dictionary containing the playlist's data.
        """
        playlist_data = self._get_playlist_data(playlist_id)
        if playlist_data:
            playlist_copy = copy.deepcopy(playlist_data)
            # Replace video_ids with full video details
            playlist_copy["videos"] = []
            for video_uuid in playlist_data.get("video_ids", []):
                video_details = self._get_video_data(video_uuid)
                if video_details:
                    playlist_copy["videos"].append(video_details)
            return {"data": playlist_copy}
        return {"data": None, "error": "Playlist not found"}

    def create_playlist(self, channel_id: str, title: str, description: str = "", privacy_status: str = "public") -> Dict[str, Any]:
        """
        Create a new playlist for a specified channel.

        Args:
            channel_id (str): The ID (UUID) of the channel creating the playlist.
            title (str): The title of the new playlist.
            description (str, optional): The description of the new playlist. Defaults to "".
            privacy_status (str, optional): The privacy status of the playlist ("public", "unlisted", "private"). Defaults to "public".

        Returns:
            Dict: A dictionary containing the newly created playlist's data.
        """
        channel_data = self._get_channel_data(channel_id)
        if not channel_data:
            return {"data": None, "error": "Channel not found"}
        
        owner_id = channel_data["owner_id"]
        if not owner_id or owner_id not in self.users:
            return {"data": None, "error": "Owner user not found for this channel."}

        playlist_uuid = self._generate_unique_id()
        new_playlist = {
            "id": playlist_uuid,
            "title": title,
            "description": description,
            "owner_id": owner_id,
            "channel_id": channel_id,
            "video_ids": [],
            "created_at": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z",
            "privacy_status": privacy_status,
            "item_count": 0
        }
        self.playlists[playlist_uuid] = new_playlist
        self.channels[channel_id]["playlists"].append(playlist_uuid)
        print(f"Playlist created: ID={playlist_uuid} in channel {channel_data['title']}")
        return {"data": copy.deepcopy(new_playlist)}

    def add_video_to_playlist(self, playlist_id: str, video_id: str, user_id: str) -> Dict[str, bool]:
        """
        Add a video to a specific playlist. Only the playlist owner can modify it.

        Args:
            playlist_id (str): The ID (UUID) of the playlist to add the video to.
            video_id (str): The ID (UUID) of the video to add.
            user_id (str): The ID (UUID) of the user performing the action (must be playlist owner).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating the operation's outcome.
        """
        playlist_data = self._get_playlist_data(playlist_id)
        video_data = self._get_video_data(video_id)

        if not playlist_data:
            return {"success": False, "error": "Playlist not found"}
        if not video_data:
            return {"success": False, "error": "Video not found"}
        
        if playlist_data.get("owner_id") != user_id:
            return {"success": False, "error": "User is not the owner of this playlist."}

        if video_id not in playlist_data.get("video_ids", []):
            playlist_data["video_ids"].append(video_id)
            playlist_data["item_count"] = playlist_data.get("item_count", 0) + 1
            return {"success": True}
        return {"success": False, "error": "Video already in playlist"}

    def remove_video_from_playlist(self, playlist_id: str, video_id: str, user_id: str) -> Dict[str, bool]:
        """
        Remove a video from a specific playlist. Only the playlist owner can modify it.

        Args:
            playlist_id (str): The ID (UUID) of the playlist to remove the video from.
            video_id (str): The ID (UUID) of the video to remove.
            user_id (str): The ID (UUID) of the user performing the action (must be playlist owner).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating the operation's outcome.
        """
        playlist_data = self._get_playlist_data(playlist_id)
        video_data = self._get_video_data(video_id) # Just to check if video exists, not strictly needed but good practice

        if not playlist_data:
            return {"success": False, "error": "Playlist not found"}
        if not video_data: # If video doesn't exist anymore, it's implicitly not in playlist
            pass # Continue to try removing it
        
        if playlist_data.get("owner_id") != user_id:
            return {"success": False, "error": "User is not the owner of this playlist."}

        if video_id in playlist_data.get("video_ids", []):
            playlist_data["video_ids"].remove(video_id)
            playlist_data["item_count"] = max(0, playlist_data.get("item_count", 0) - 1)
            return {"success": True}
        return {"success": False, "error": "Video not found in playlist"}
    
    def youtube_playlistItems_insert(self, playlist_id: str, video_id: str, user_id: str) -> Dict[str, Any]:
        """
        Adds a video to a playlist. This is a wrapper for add_video_to_playlist.

        Parameters:
            playlist_id (str): The ID (UUID) of the playlist to add the video to.
            video_id (str): The ID (UUID) of the video to add.
            user_id (str): The ID (UUID) of the user requesting the action (must be playlist owner).

        Returns:
            Dict[str, Any]: Result of the operation.
        """
        return self.add_video_to_playlist(playlist_id, video_id, user_id)

    def youtube_playlistItems_delete(self, playlist_item_id: str, user_id: str) -> Dict[str, Any]:
        """
        Deletes a playlist item. Note: Dummy API treats playlist_item_id as video_id for simplicity.

        Parameters:
            playlist_item_id (str): The ID (UUID) of the video (which acts as the playlist item ID in this dummy).
            user_id (str): The ID (UUID) of the user requesting the action (must be playlist owner of relevant playlist).

        Returns:
            Dict[str, Any]: Result of the operation.
        """
        # In a real API, playlist_item_id is distinct from video_id.
        # For simplicity, this dummy will assume playlist_item_id IS the video_id,
        # and it will try to find any playlist where this user is owner and this video exists.
        
        target_video_id = playlist_item_id
        
        for p_id, playlist_data in self.playlists.items():
            if playlist_data.get("owner_id") == user_id and target_video_id in playlist_data.get("video_ids", []):
                playlist_data["video_ids"].remove(target_video_id)
                playlist_data["item_count"] = max(0, playlist_data.get("item_count", 0) - 1)
                return {"success": True, "message": f"Video {target_video_id} removed from playlist {p_id}."}
        
        return {"error": "Playlist item not found or user not authorized.", "success": False}


    # ====================
    # Comment Operations
    # ====================

    def add_comment_to_video(self, video_id: str, author_id: str, text: str) -> Dict[str, Any]:
        """
        Add a new comment to a specific video.

        Args:
            video_id (str): The ID (UUID) of the video to comment on.
            author_id (str): The ID (UUID) of the user posting the comment.
            text (str): The content of the comment.

        Returns:
            Dict: A dictionary containing the newly created comment's data.
        """
        video_data = self._get_video_data(video_id)
        author_data = self._get_user_data(author_id)

        if not video_data:
            return {"data": None, "error": "Video not found"}
        if not author_data:
            return {"data": None, "error": "Author user not found"}

        comment_uuid = self._generate_unique_id()
        new_comment = {
            "id": comment_uuid,
            "video_id": video_id,
            "author_id": author_id,
            "text": text,
            "created_at": datetime.datetime.now().isoformat(timespec='milliseconds') + "Z",
            "likes": 0
        }
        self.comments[comment_uuid] = new_comment
        self.videos[video_id]["comments"].append(comment_uuid)
        print(f"Comment added: ID={comment_uuid} on video {video_id} by {author_data['display_name']}")
        return {"data": copy.deepcopy(new_comment)}

    def list_comments_for_video(self, video_id: str) -> Dict[str, Any]:
        """
        List all comments for a specific video.

        Args:
            video_id (str): The ID (UUID) of the video whose comments are to be listed.

        Returns:
            Dict: A dictionary containing a list of comments.
        """
        video_data = self._get_video_data(video_id)
        if not video_data:
            return {"data": None, "error": "Video not found"}

        video_comments = []
        for comment_uuid in video_data.get("comments", []):
            comment_details = self._get_comment_data(comment_uuid)
            if comment_details:
                # Add author's display name for convenience
                author_info = self._get_user_data(comment_details.get("author_id"))
                comment_copy = copy.deepcopy(comment_details)
                comment_copy["author_display_name"] = author_info["display_name"] if author_info else "Unknown User"
                video_comments.append(comment_copy)
        
        # Sort comments by creation time, oldest first
        video_comments.sort(key=lambda x: x.get("created_at", ""))
        return {"data": video_comments}

    def delete_comment(self, comment_id: str, user_id: str) -> Dict[str, bool]:
        """
        Delete a comment. Only the author of the comment or the channel owner can delete it.

        Args:
            comment_id (str): The ID (UUID) of the comment to delete.
            user_id (str): The ID (UUID) of the user attempting to delete (must be author or channel owner).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating the operation's outcome.
        """
        comment_data = self._get_comment_data(comment_id)
        if not comment_data:
            return {"success": False, "error": "Comment not found"}
        
        video_id = comment_data.get("video_id")
        video_data = self._get_video_data(video_id)
        
        if not video_data: # Associated video not found, perhaps already deleted
            del self.comments[comment_id] # Clean up orphaned comment
            return {"success": True, "message": "Comment found but video not, deleting orphaned comment."}

        channel_id = video_data.get("channel_id")
        channel_data = self._get_channel_data(channel_id)
        
        is_author = comment_data.get("author_id") == user_id
        is_channel_owner = channel_data and channel_data.get("owner_id") == user_id

        if not is_author and not is_channel_owner:
            return {"success": False, "error": "Not authorized to delete this comment"}

        if comment_id in self.comments:
            del self.comments[comment_id]
            if comment_id in self.videos[video_id].get("comments", []):
                self.videos[video_id]["comments"].remove(comment_id)
            return {"success": True}
        return {"success": False, "error": "Comment not found or internal error"}

    def youtube_comments_insert(self, video_id: str, text: str, author_id: str) -> Dict[str, Any]:
        """
        Adds a comment to a video. This is a wrapper for add_comment_to_video.

        Parameters:
            video_id (str): The ID (UUID) of the video to comment on.
            text (str): The content of the comment.
            author_id (str): The ID (UUID) of the user posting the comment.

        Returns:
            Dict[str, Any]: Result of the operation.
        """
        return self.add_comment_to_video(video_id, author_id, text)

    # ====================
    # Caption Operations (Dummy)
    # ====================

    def youtube_captions_insert(self, video_id: str, language: str, track_content: str) -> Dict[str, Any]:
        """
        Uploads a caption track for a video.
        In this dummy, it simulates adding a caption, but doesn't store actual files.

        Parameters:
            video_id (str): The ID (UUID) of the video the caption is for.
            language (str): The language of the caption track (e.g., "en", "es").
            track_content (str): The content of the caption track (e.g., SRT format string).

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the upload, with a dummy ID.
        """
        video_data = self._get_video_data(video_id)
        if not video_data:
            return {"error": "Video not found.", "success": False}
        
        # Simulating storing captions within the channel's data for the video
        caption_id = self._generate_unique_id()
        channel_id = video_data.get("channel_id")
        if channel_id and channel_id in self.channels:
            if "captions" not in self.channels[channel_id]:
                self.channels[channel_id]["captions"] = {}
            self.channels[channel_id]["captions"][caption_id] = {
                "id": caption_id,
                "video_id": video_id,
                "language": language,
                "status": "serving", # Dummy status
                "content_snippet": track_content[:50] + "..." if len(track_content) > 50 else track_content
            }
            return {"success": True, "caption_id": caption_id, "language": language}
        return {"error": "Channel for video not found.", "success": False}

    def youtube_captions_update(self, id: str, track_content: str) -> Dict[str, Any]:
        """
        Updates a caption track.
        In this dummy, it simulates updating a caption by its dummy ID.

        Parameters:
            id (str): The ID (UUID) of the caption track to update.
            track_content (str): The new content of the caption track.

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the update.
        """
        for channel_id, channel_data in self.channels.items():
            if "captions" in channel_data and id in channel_data["captions"]:
                channel_data["captions"][id]["content_snippet"] = track_content[:50] + "..." if len(track_content) > 50 else track_content
                return {"success": True, "caption_id": id, "message": "Caption updated."}
        return {"error": "Caption track not found.", "success": False}

    def youtube_captions_delete(self, id: str) -> Dict[str, Any]:
        """
        Deletes a caption track.

        Parameters:
            id (str): The ID (UUID) of the caption track to delete.

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the deletion.
        """
        for channel_id, channel_data in self.channels.items():
            if "captions" in channel_data and id in channel_data["captions"]:
                del self.channels[channel_id]["captions"][id]
                return {"success": True, "deleted_caption_id": id}
        return {"error": "Caption track not found.", "success": False}

    # ====================
    # Reset Data
    # ====================
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
        print("YouTubeApis: All dummy data reset to default state.")
        return {"reset_status": True}