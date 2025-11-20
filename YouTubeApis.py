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
        self.access_token: Optional[str] = None
        self.current_user_id: Optional[str] = None

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
        self.comments = {}
        print("YouTubeApis: Loaded scenario with UUIDs for users, channels, videos, playlists, and comments.")

    def authenticate(self, access_token: str) -> Dict[str, Any]:
        """
        Authenticate with YouTube Data API using an OAuth 2.0 access token.

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
            "email": user_data.get("email"),
            "displayName": user_data.get("display_name"),
            "kind": "youtube#channel"
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

    def get_my_channel(self) -> Dict[str, Any]:
        """
        Get the authenticated user's YouTube channel (primary channel).

        Returns:
            Dict[str, Any]: Channel data with YouTube API v3 structure

        Raises:
            Exception: If not authenticated or no channel found
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
        List channels the authenticated user is subscribed to.

        Args:
            maxResults (int): Maximum number of results to return (default: 25)
            pageToken (Optional[str]): Token for pagination

        Returns:
            Dict[str, Any]: Subscriptions with YouTube API v3 pagination

        Raises:
            Exception: If not authenticated
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
        Subscribe the authenticated user to a channel.

        Args:
            channel_id (str): The ID of the channel to subscribe to

        Returns:
            Dict[str, Any]: Subscription resource

        Raises:
            Exception: If not authenticated, channel not found, or already subscribed
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
        Unsubscribe the authenticated user from a channel.

        Args:
            channel_id (str): The ID of the channel to unsubscribe from

        Raises:
            Exception: If not authenticated, channel not found, or not subscribed
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

        Returns:
            Dict[str, Any]: Channel list with YouTube API v3 structure

        Raises:
            Exception: If not authenticated
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
        Get the details of a specific channel (public endpoint, no auth required).

        Args:
            channel_id (str): The ID of the channel to retrieve

        Returns:
            Dict[str, Any]: Channel data with YouTube API v3 structure

        Raises:
            Exception: If channel not found
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
        Create a new channel for the authenticated user.

        Args:
            title (str): The title of the new channel
            description (str, optional): The description of the new channel

        Returns:
            Dict[str, Any]: Newly created channel with YouTube API v3 structure

        Raises:
            Exception: If not authenticated
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
        Update a channel's properties (must be owner).

        Args:
            channel_id (str): The ID of the channel to update
            title (Optional[str]): New title
            description (Optional[str]): New description

        Returns:
            Dict[str, Any]: Updated channel with YouTube API v3 structure

        Raises:
            Exception: If not authenticated, channel not found, or not owner
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
        List all videos in a specific channel (public endpoint).

        Args:
            channel_id (str): The ID of the channel
            maxResults (int): Maximum number of results to return
            pageToken (Optional[str]): Token for pagination

        Returns:
            Dict[str, Any]: Video list with YouTube API v3 pagination

        Raises:
            Exception: If channel not found
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
        Get the details of a specific video (public endpoint, no auth required).

        Args:
            video_id (str): The ID of the video to retrieve

        Returns:
            Dict[str, Any]: Video data with YouTube API v3 structure

        Raises:
            Exception: If video not found
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

        Args:
            title (str): The title of the video
            description (str, optional): The description of the video
            duration_seconds (int, optional): The duration of the video in seconds
            tags (Optional[List[str]], optional): A list of tags for the video

        Returns:
            Dict[str, Any]: Newly created video with YouTube API v3 structure

        Raises:
            Exception: If not authenticated or no channel found
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
        Delete a video (must be the channel owner).

        Args:
            video_id (str): The ID of the video to delete

        Raises:
            Exception: If not authenticated, video not found, or not owner
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
        Rate a video (like or none).

        Args:
            video_id (str): The ID of the video to rate
            rating (str): The rating to apply ("like" or "none")

        Raises:
            Exception: If not authenticated, video not found, or invalid rating
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
                    user_data["liked_videos"].append(video_id)
                print(f"Video {video_id} liked by user {self.current_user_id}")
        elif rating == "none":
            # Remove like
            if self.current_user_id in liked_by_list:
                video_data["likes"] = max(0, video_data.get("likes", 0) - 1)
                liked_by_list.remove(self.current_user_id)
                if video_id in user_data.get("liked_videos", []):
                    user_data["liked_videos"].remove(video_id)
                print(f"Like removed from video {video_id}")
        else:
            raise Exception("Invalid rating. Must be 'like' or 'none'")

    def search_videos(self, query: str, maxResults: int = 10, pageToken: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for videos based on a query string.
        Public endpoint - no authentication required.

        Args:
            query (str): The search query
            maxResults (int): Maximum number of results to return (default 10)
            pageToken (str): Token for pagination

        Returns:
            Dict: YouTube searchListResponse structure

        Raises:
            Exception: If query is empty
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

    def list_playlists_in_channel(self, channel_id: str, maxResults: int = 25, pageToken: Optional[str] = None) -> Dict[str, Any]:
        """
        List all playlists in a channel.
        Public endpoint - no authentication required.

        Args:
            channel_id (str): The channel ID
            maxResults (int): Maximum results per page
            pageToken (str): Pagination token

        Returns:
            Dict: YouTube playlistListResponse structure

        Raises:
            Exception: If channel not found
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
        Get playlist details including videos.
        Public endpoint - no authentication required.

        Args:
            playlist_id (str): The playlist ID

        Returns:
            Dict: YouTube playlist resource with videos

        Raises:
            Exception: If playlist not found
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
        Create a new playlist for the authenticated user's channel.

        Args:
            title (str): Playlist title
            description (str): Playlist description
            privacy_status (str): "public", "unlisted", or "private"

        Returns:
            Dict: YouTube playlist resource

        Raises:
            Exception: If not authenticated, channel not found, or invalid privacy status
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
        Add a video to a playlist.
        Only the playlist owner can add videos.

        Args:
            playlist_id (str): The playlist ID
            video_id (str): The video ID

        Returns:
            Dict: YouTube playlistItem resource

        Raises:
            Exception: If not authenticated, not owner, or video/playlist not found
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
        Remove a video from a playlist.
        Only the playlist owner can remove videos.

        Args:
            playlist_id (str): The playlist ID
            video_id (str): The video ID

        Raises:
            Exception: If not authenticated, not owner, or video/playlist not found
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

        Args:
            video_id (str): The video ID
            text (str): Comment text

        Returns:
            Dict: YouTube comment resource

        Raises:
            Exception: If not authenticated, video not found, or comment text empty
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
        List comments for a video.
        Public endpoint - no authentication required.

        Args:
            video_id (str): The video ID
            maxResults (int): Maximum results per page
            pageToken (str): Pagination token

        Returns:
            Dict: YouTube commentThreadListResponse structure

        Raises:
            Exception: If video not found
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
        Delete a comment.
        Only the comment author can delete it.

        Args:
            comment_id (str): The comment ID

        Raises:
            Exception: If not authenticated, comment not found, or not the author
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
        for _, channel_data in self.channels.items():
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

    def reset_data(self) -> None:
        """
        Reset all data to default state.
        Clears authentication and reloads default scenario.
        """
        self.access_token = None
        self.current_user_id = None
        self._load_scenario(DEFAULT_STATE)
        print("YouTubeApis: All data reset to default state.")
