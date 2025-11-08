import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional, Union
import sys
import os
from pathlib import Path

# Add parent directory to path to import test_data_helper
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir / 'UnitTests'))

from UnitTests.test_data_helper import BackendDataLoader

DEFAULT_STATE = BackendDataLoader.get_youtube_data()

class EmailStr(str):
    pass

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

    def _find_user_by_email(self, email: str) -> Optional[str]:
        """Helper to find a user UUID by their email address."""
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _find_user_by_display_name(self, display_name: str) -> Optional[str]:
        """Helper to find a user UUID by their display name."""
        for user_id, user_data in self.users.items():
            if user_data.get("display_name") == display_name:
                return user_id
        return None

    def _get_user_id_from_identifier(self, identifier: str) -> Optional[str]:
        """
        Helper to get user UUID from email, display name, or UUID.
        
        Args:
            identifier (str): Email, display name, or UUID
            
        Returns:
            Optional[str]: User UUID if found, None otherwise
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
        return {"data": None, "message": "User not found"}

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
        return {"data": None, "message": "User not found"}

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
        return {"data": None, "message": "User not found"}
    
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
            return {"status": False, "message": "User not found."}
        if not channel_data:
            return {"status": False, "message": "Channel not found."}
        
        if channel_id in user_data.get("subscriptions", []):
            return {"status": False, "message": "Already subscribed."}
        
        user_data["subscriptions"].append(channel_id)
        channel_data["subscribers"].append(user_id)
        channel_data["subscriber_count"] = channel_data.get("subscriber_count", 0) + 1
        
        return {"status": True, "message": f"Successfully subscribed to channel {channel_id}"}

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
            return {"status": False, "message": "User not found."}
        if not channel_data:
            return {"status": False, "message": "Channel not found."}
        
        if channel_id not in user_data.get("subscriptions", []):
            return {"status": False, "message": "Not subscribed to this channel."}
        
        user_data["subscriptions"].remove(channel_id)
        if user_id in channel_data.get("subscribers", []):
            channel_data["subscribers"].remove(user_id)
        channel_data["subscriber_count"] = max(0, channel_data.get("subscriber_count", 0) - 1)
        
        return {"status": True, "message": f"Successfully unsubscribed from channel {channel_id}"}

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
            return {"data": None, "message": "User not found"}
        
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
        return {"data": None, "message": "Channel not found"}

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
            return {"data": None, "message": "User not found"}

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
            "banner_image_path": "https://YouTube.com/default_banner.jpg"
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
            return {"status": False, "message": "Channel not found."}
        
        if channel_data.get("owner_id") != user_id:
            return {"status": False, "message": "User is not the owner of this channel."}

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
            return {"message": "Channel not found."}
        
        channel_data["banner_image_path"] = image_path
        return {"status": True, "image_path": image_path, "channel_id": channel_id}

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
            return {"data": None, "message": "Channel not found"}
        
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
        return {"data": None, "message": "Video not found"}
    
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
            return {"data": None, "message": "Channel not found"}
        
        uploader_id = channel_data["owner_id"]
        if not uploader_id or uploader_id not in self.users:
            return {"data": None, "message": "Uploader user not found for this channel."}

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
            return {"status": False, "message": "Video not found"}
        if not channel_data:
            return {"status": False, "message": "Channel not found"}
        
        if video_data.get("channel_id") != channel_id:
            return {"status": False, "message": "Video does not belong to the specified channel"}
        if channel_data.get("owner_id") != user_id:
            return {"status": False, "message": "User is not the owner of this channel and cannot delete videos"}

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

            return {"status": True, "message": "Video deleted successfully"}
        return {"status": False, "message": "Video not found or internal error"}

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
            return {"message": "Video not found.", "status": False}
        if not user_data:
            return {"message": "User not found.", "status": False}

        liked_by_list = video_data.get("liked_by", [])
        
        if rating == "like":
            if user_id not in liked_by_list:
                video_data["likes"] = video_data.get("likes", 0) + 1
                liked_by_list.append(user_id)
                if video_id not in user_data.get("liked_videos", []):
                    user_data["liked_videos"].append(video_id)
            return {"status": True, "message": f"Video {video_id} liked by {user_id}."}
        elif rating == "dislike":
            if user_id in liked_by_list:
                video_data["likes"] = max(0, video_data.get("likes", 0) - 1)
                liked_by_list.remove(user_id)
            video_data["dislikes"] = video_data.get("dislikes", 0) + 1
            if video_id in user_data.get("liked_videos", []):
                user_data["liked_videos"].remove(video_id) # Remove from liked if disliked
            return {"status": True, "message": f"Video {video_id} disliked by {user_id}."}
        else:
            return {"message": "Invalid rating. Must be 'like' or 'dislike'.", "status": False}

    def like_video(self, video_id: str, user_id: str) -> Dict[str, bool]:
        """
        Mark a video as liked by the user. This is a simplified wrapper around youtube_videos_rate.
        """
        result = self.youtube_videos_rate(video_id, "like", user_id)
        return result

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
            return {"status": False, "message": "Video or user not found."}
        
        liked_by_list = video_data.get("liked_by", [])
        if user_id in liked_by_list:
            video_data["likes"] = max(0, video_data.get("likes", 0) - 1)
            liked_by_list.remove(user_id)
            if video_id in user_data.get("liked_videos", []):
                user_data["liked_videos"].remove(video_id)
            return {"status": True, "message": "Video unliked successfully."}
        return {"status": False, "message": "Video not previously liked by this user."}

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
            return {"data": None, "message": "Channel not found"}
        
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
        return {"data": None, "message": "Playlist not found"}

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
            return {"data": None, "message": "Channel not found"}
        
        owner_id = channel_data["owner_id"]
        if not owner_id or owner_id not in self.users:
            return {"data": None, "message": "Owner user not found for this channel."}

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
            return {"status": False, "message": "Playlist not found"}
        if not video_data:
            return {"status": False, "message": "Video not found"}
        
        if playlist_data.get("owner_id") != user_id:
            return {"status": False, "message": "User is not the owner of this playlist."}

        if video_id not in playlist_data.get("video_ids", []):
            playlist_data["video_ids"].append(video_id)
            playlist_data["item_count"] = playlist_data.get("item_count", 0) + 1
            return {"status": True}
        return {"status": False, "message": "Video already in playlist"}

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
            return {"status": False, "message": "Playlist not found"}
        if not video_data: # If video doesn't exist anymore, it's implicitly not in playlist
            pass # Continue to try removing it
        
        if playlist_data.get("owner_id") != user_id:
            return {"status": False, "message": "User is not the owner of this playlist."}

        if video_id in playlist_data.get("video_ids", []):
            playlist_data["video_ids"].remove(video_id)
            playlist_data["item_count"] = max(0, playlist_data.get("item_count", 0) - 1)
            return {"status": True}
        return {"status": False, "message": "Video not found in playlist"}
    
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
        target_video_id = playlist_item_id
        
        for p_id, playlist_data in self.playlists.items():
            if playlist_data.get("owner_id") == user_id and target_video_id in playlist_data.get("video_ids", []):
                playlist_data["video_ids"].remove(target_video_id)
                playlist_data["item_count"] = max(0, playlist_data.get("item_count", 0) - 1)
                return {"status": True, "message": f"Video {target_video_id} removed from playlist {p_id}."}
        
        return {"message": "Playlist item not found or user not authorized.", "status": False}

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
            return {"data": None, "message": "Video not found"}
        if not author_data:
            return {"data": None, "message": "Author user not found"}

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
            return {"data": None, "message": "Video not found"}

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
            return {"status": False, "message": "Comment not found"}
        
        video_id = comment_data.get("video_id")
        video_data = self._get_video_data(video_id)
        
        if not video_data: # Associated video not found, perhaps already deleted
            del self.comments[comment_id] # Clean up orphaned comment
            return {"status": True, "message": "Comment found but video not, deleting orphaned comment."}

        channel_id = video_data.get("channel_id")
        channel_data = self._get_channel_data(channel_id)
        
        is_author = comment_data.get("author_id") == user_id
        is_channel_owner = channel_data and channel_data.get("owner_id") == user_id

        if not is_author and not is_channel_owner:
            return {"status": False, "message": "Not authorized to delete this comment"}

        if comment_id in self.comments:
            del self.comments[comment_id]
            if comment_id in self.videos[video_id].get("comments", []):
                self.videos[video_id]["comments"].remove(comment_id)
            return {"status": True}
        return {"status": False, "message": "Comment not found or internal error"}

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
                return {"status": True, "caption_id": id, "message": "Caption updated."}
        return {"message": "Caption track not found.", "status": False}

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
                return {"status": True, "deleted_caption_id": id}
        return {"message": "Caption track not found.", "status": False}

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """
        Get user data by email address.

        Args:
            email (str): The email address to search for.

        Returns:
            Dict: A dictionary containing the user's profile data.
        """
        user_id = self._find_user_by_email(email)
        if user_id:
            return {"data": copy.deepcopy(self.users[user_id])}
        return {"data": None, "message": "User not found"}

    def get_user_by_display_name(self, display_name: str) -> Dict[str, Any]:
        """
        Get user data by display name.

        Args:
            display_name (str): The display name to search for.

        Returns:
            Dict: A dictionary containing the user's profile data.
        """
        user_id = self._find_user_by_display_name(display_name)
        if user_id:
            return {"data": copy.deepcopy(self.users[user_id])}
        return {"data": None, "message": "User not found"}

    def get_watch_later_playlist(self, user_identifier: str) -> Dict[str, Any]:
        """
        Get the watch later playlist for a user.

        Args:
            user_identifier (str): The user ID, email, or display name.

        Returns:
            Dict: A dictionary containing the watch later playlist videos.
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
        Add a video to the user's watch later playlist.

        Args:
            user_identifier (str): The user ID, email, or display name.
            video_id (str): The ID of the video to add.

        Returns:
            Dict: A dictionary indicating success or failure.
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
        Remove a video from the user's watch later playlist.

        Args:
            user_identifier (str): The user ID, email, or display name.
            video_id (str): The ID of the video to remove.

        Returns:
            Dict: A dictionary indicating success or failure.
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
        Get notification settings for a user.

        Args:
            user_identifier (str): The user ID, email, or display name.

        Returns:
            Dict: A dictionary containing the user's notification settings.
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"data": None, "message": "User not found"}
        
        user_data = self.users[user_id]
        settings = user_data.get("notification_settings", {})
        
        return {"data": copy.deepcopy(settings)}

    def update_notification_settings(self, user_identifier: str, settings: Dict[str, bool]) -> Dict[str, Any]:
        """
        Update notification settings for a user.

        Args:
            user_identifier (str): The user ID, email, or display name.
            settings (Dict[str, bool]): New notification settings.

        Returns:
            Dict: A dictionary indicating success or failure.
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
        Get language preference for a user.

        Args:
            user_identifier (str): The user ID, email, or display name.

        Returns:
            Dict: A dictionary containing the user's language preference.
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"data": None, "message": "User not found"}
        
        user_data = self.users[user_id]
        language = user_data.get("language_preference", "en-US")
        
        return {"data": {"language_preference": language}}

    def update_language_preference(self, user_identifier: str, language: str) -> Dict[str, Any]:
        """
        Update language preference for a user.

        Args:
            user_identifier (str): The user ID, email, or display name.
            language (str): New language preference (e.g., "en-US", "es-ES").

        Returns:
            Dict: A dictionary indicating success or failure.
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"status": False, "message": "User not found"}
        
        user_data = self.users[user_id]
        user_data["language_preference"] = language
        
        return {"status": True, "message": "Language preference updated"}

    def get_account_status(self, user_identifier: str) -> Dict[str, Any]:
        """
        Get account status for a user.

        Args:
            user_identifier (str): The user ID, email, or display name.

        Returns:
            Dict: A dictionary containing the user's account status.
        """
        user_id = self._get_user_id_from_identifier(user_identifier)
        if not user_id:
            return {"data": None, "message": "User not found"}
        
        user_data = self.users[user_id]
        status = user_data.get("account_status", "active")
        
        return {"data": {"account_status": status}}

    def get_channel_history(self, user_identifier: str) -> Dict[str, Any]:
        """
        Get channel browsing history for a user.

        Args:
            user_identifier (str): The user ID, email, or display name.

        Returns:
            Dict: A dictionary containing the user's channel history.
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

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self._load_scenario(DEFAULT_STATE)
        print("YouTubeApis: All dummy data reset to default state.")
        return {"reset_status": True}
