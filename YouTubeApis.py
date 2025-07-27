from copy import deepcopy
from typing import Dict, Optional, Any

DEFAULT_STATE = {
    "users": {
        "alice.smith@example.com": {
            "user_id": "user_alice",
            "display_name": "Alice Smith",
            "channels": ["UC_AliceVlogs", "UC_AliceGaming"],
            "subscriptions": ["UC_BobTech", "UC_CharlieCooks"],
            "watch_history": ["vid_001", "vid_003", "vid_005"],
            "liked_videos": ["vid_001", "vid_004"],
        },
        "bob.jones@example.com": {
            "user_id": "user_bob",
            "display_name": "Bob Jones",
            "channels": ["UC_BobTech"],
            "subscriptions": ["UC_AliceVlogs"],
            "watch_history": ["vid_002", "vid_004"],
            "liked_videos": ["vid_002"],
        },
        "charlie.brown@example.com": {
            "user_id": "user_charlie",
            "display_name": "Charlie Brown",
            "channels": ["UC_CharlieCooks"],
            "subscriptions": ["UC_AliceVlogs", "UC_BobTech"],
            "watch_history": ["vid_001", "vid_002"],
            "liked_videos": [],
        }
    },
    "channels": {
        "UC_AliceVlogs": {
            "channel_id": "UC_AliceVlogs",
            "user_id": "user_alice",
            "title": "Alice's Daily Vlogs",
            "description": "Sharing my everyday adventures and thoughts!",
            "privacy_status": "public",
            "playlists": {
                "PL_AliceTravel": {
                    "title": "Travel Adventures",
                    "description": "Journeys around the world",
                    "privacy_status": "public",
                    "video_ids": ["vid_001", "vid_003"]
                },
                "PL_AliceLife": {
                    "title": "My Life Lately",
                    "description": "Updates and reflections",
                    "privacy_status": "public",
                    "video_ids": ["vid_005"]
                }
            },
            "subscribers_count": 125000,
            "videos": ["vid_001", "vid_003", "vid_005"],
            "watermark_url": "https://example.com/watermark_alice.png",
            "channel_sections": [
                {"type": "popular_uploads", "title": "Popular Videos"},
                {"type": "single_playlist", "playlist_id": "PL_AliceTravel", "title": "My Favorite Trips"}
            ],
            "captions": {
                "cap_001_en": {
                    "video_id": "vid_001",
                    "language": "en",
                    "name": "English Auto-generated",
                    "is_draft": False,
                    "file_path": "/captions/vid_001_en.srt"
                }
            }
        },
        "UC_AliceGaming": {
            "channel_id": "UC_AliceGaming",
            "user_id": "user_alice",
            "title": "Alice Plays Games",
            "description": "Streaming my gaming sessions and walkthroughs.",
            "privacy_status": "public",
            "playlists": {},
            "subscribers_count": 50000,
            "videos": [],
            "watermark_url": None,
            "channel_sections": [],
            "captions": {}
        },
        "UC_BobTech": {
            "channel_id": "UC_BobTech",
            "user_id": "user_bob",
            "title": "Bob's Tech Reviews",
            "description": "Unboxing and reviewing the latest gadgets.",
            "privacy_status": "public",
            "playlists": {
                "PL_BobReviews": {
                    "title": "Gadget Reviews",
                    "description": "All my tech reviews",
                    "privacy_status": "public",
                    "video_ids": ["vid_002", "vid_004"]
                }
            },
            "subscribers_count": 75000,
            "videos": ["vid_002", "vid_004"],
            "watermark_url": "https://example.com/watermark_bob.png",
            "channel_sections": [],
            "captions": {}
        },
        "UC_CharlieCooks": {
            "channel_id": "UC_CharlieCooks",
            "user_id": "user_charlie",
            "title": "Charlie's Kitchen",
            "description": "Delicious recipes and cooking tips.",
            "privacy_status": "public",
            "playlists": {},
            "subscribers_count": 25000,
            "videos": [],
            "watermark_url": None,
            "channel_sections": [],
            "captions": {}
        }
    },
    "current_user_id": "user_alice",  # Represents the currently logged-in user
    "video_categories": {
        "1": "Film & Animation",
        "2": "Autos & Vehicles",
        "10": "Music",
        "15": "Pets & Animals",
        "17": "Sports",
        "19": "Travel & Events",
        "20": "Gaming",
        "22": "People & Blogs",
        "23": "Comedy",
        "24": "Entertainment",
        "25": "News & Politics",
        "26": "Howto & Style",
        "27": "Education",
        "28": "Science & Technology",
        "29": "Nonprofits & Activism"
    },
    "videos": {
        "vid_001": {
            "video_id": "vid_001",
            "channel_id": "UC_AliceVlogs",
            "title": "Exploring the Grand Canyon",
            "description": "An amazing trip to the Grand Canyon! The views were breathtaking.",
            "category_id": "19",  # Travel & Events
            "privacy_status": "public",
            "file_path": "/videos/grand_canyon_vlog.mp4",
            "thumbnail_url": "https://example.com/thumbnails/grand_canyon.jpg",
            "views": 55000,
            "likes": 4200,
            "dislikes": 150,
            "published_at": "2024-03-10T14:30:00Z"
        },
        "vid_002": {
            "video_id": "vid_002",
            "channel_id": "UC_BobTech",
            "title": "iPhone 16 Pro Max Unboxing & First Impressions",
            "description": "Getting my hands on the new iPhone 16! Here's my initial thoughts.",
            "category_id": "28",  # Science & Technology
            "privacy_status": "public",
            "file_path": "/videos/iphone16_unboxing.mp4",
            "thumbnail_url": "https://example.com/thumbnails/iphone16.jpg",
            "views": 78000,
            "likes": 6100,
            "dislikes": 200,
            "published_at": "2024-06-20T10:00:00Z"
        },
        "vid_003": {
            "video_id": "vid_003",
            "channel_id": "UC_AliceVlogs",
            "title": "Paris Food Tour - What I Ate!",
            "description": "A delicious journey through the streets of Paris, trying all the local treats.",
            "category_id": "19",  # Travel & Events
            "privacy_status": "public",
            "file_path": "/videos/paris_food_tour.mp4",
            "thumbnail_url": "https://example.com/thumbnails/paris_food.jpg",
            "views": 32000,
            "likes": 2800,
            "dislikes": 80,
            "published_at": "2024-05-01T18:00:00Z"
        },
        "vid_004": {
            "video_id": "vid_004",
            "channel_id": "UC_BobTech",
            "title": "Smart Home Automation Basics",
            "description": "Getting started with smart home devices? Here's what you need to know.",
            "category_id": "28",  # Science & Technology
            "privacy_status": "public",
            "file_path": "/videos/smart_home_basics.mp4",
            "thumbnail_url": "https://example.com/thumbnails/smart_home.jpg",
            "views": 45000,
            "likes": 3900,
            "dislikes": 100,
            "published_at": "2024-04-15T11:30:00Z"
        },
        "vid_005": {
            "video_id": "vid_005",
            "channel_id": "UC_AliceVlogs",
            "title": "My Morning Routine (Realistic!)",
            "description": "A look at my actual morning routine, no filters!",
            "category_id": "22",  # People & Blogs
            "privacy_status": "public",
            "file_path": "/videos/morning_routine.mp4",
            "thumbnail_url": "https://example.com/thumbnails/morning_routine.jpg",
            "views": 60000,
            "likes": 5000,
            "dislikes": 180,
            "published_at": "2024-06-05T09:00:00Z"
        }
    },
    "comments": {
        "comm_001": {
            "comment_id": "comm_001",
            "video_id": "vid_001",
            "channel_id": "UC_BobTech", # Bob Jones is commenting
            "user_id": "user_bob",
            "text_original": "This looks incredible, Alice! Adding the Grand Canyon to my bucket list.",
            "published_at": "2024-03-11T09:00:00Z"
        },
        "comm_002": {
            "comment_id": "comm_002",
            "video_id": "vid_002",
            "channel_id": "UC_AliceVlogs", # Alice Smith is commenting
            "user_id": "user_alice",
            "text_original": "Great review, Bob! Very helpful.",
            "published_at": "2024-06-21T14:15:00Z"
        },
        "comm_003": {
            "comment_id": "comm_003",
            "video_id": "vid_001",
            "channel_id": "UC_CharlieCooks", # Charlie Brown is commenting
            "user_id": "user_charlie",
            "text_original": "I wish I could travel more! Thanks for sharing this amazing video.",
            "published_at": "2024-03-12T10:30:00Z"
        }
    },
    "comment_threads": {
        "thread_vid_001_1": {
            "thread_id": "thread_vid_001_1",
            "video_id": "vid_001",
            "top_level_comment_id": "comm_001",
            "replies": [] # Replies to comm_001 would go here
        },
        "thread_vid_002_1": {
            "thread_id": "thread_002_1",
            "video_id": "vid_002",
            "top_level_comment_id": "comm_002",
            "replies": []
        },
        "thread_vid_001_2": {
            "thread_id": "thread_001_2",
            "video_id": "vid_001",
            "top_level_comment_id": "comm_003",
            "replies": []
        }
    }
}

class YouTubeApis:
    def __init__(self):
        self.channels: Dict[str, Dict] = {}
        self.current_channel: Optional[str] = None
        self.video_categories: Dict[str, str] = {}
        self.comments: Dict[str, Dict] = {}
        self.comment_threads: Dict[str, Dict] = {}
        self._api_description = "This tool provides functionalities to interact with YouTube, including searching, managing playlists, subscriptions, videos, comments, and channel settings."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: dict) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.channels = scenario.get("channels", DEFAULT_STATE_COPY["channels"])
        self.current_channel = scenario.get("current_channel", DEFAULT_STATE_COPY["current_channel"])
        self.video_categories = scenario.get("video_categories", DEFAULT_STATE_COPY["video_categories"])
        self.comments = scenario.get("comments", DEFAULT_STATE_COPY["comments"])
        self.comment_threads = scenario.get("comment_threads", DEFAULT_STATE_COPY["comment_threads"])

    def Youtube(self, part: str, channel_id: Optional[str] = None, max_results: int = 5, q: Optional[str] = None, video_category_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Searches for resources that match the API request parameters.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more search resource properties that the API response will include.
            channel_id (Optional[str]): The channel_id parameter restricts the search to a particular channel.
            max_results (int): The maxResults parameter specifies the maximum number of items that should be returned in the result set.
            q (Optional[str]): The q parameter specifies the query term to search for.
            video_category_id (Optional[str]): The videoCategoryId parameter restricts the search results to videos in the specified category.

        Returns:
            Dict[str, Any]: A dictionary containing search results.
        """
        results = []
        for channel_id_str, channel_data in self.channels.items():
            if channel_id and channel_id_str != channel_id:
                continue

            for video_id, video_data in channel_data.get("videos", {}).items():
                if q and q.lower() not in video_data["title"].lower() and q.lower() not in video_data["description"].lower():
                    continue
                if video_category_id and video_data["category_id"] != video_category_id:
                    continue

                results.append({
                    "kind": "YoutubeResult",
                    "id": {"kind": "youtube#video", "videoId": video_id},
                    "snippet": {
                        "publishedAt": "2024-01-01T00:00:00Z",  # Dummy date
                        "channelId": channel_id_str,
                        "title": video_data["title"],
                        "description": video_data["description"],
                        "channelTitle": channel_data["title"],
                        "liveBroadcastContent": "none"
                    }
                })
        return {"items": results[:max_results]}

    def youtube_subscriptions_list(self, part: str, channel_id: Optional[str] = None, mine: bool = False, max_results: int = 5) -> Dict[str, Any]:
        """
        Returns subscription resources that match the API request parameters.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more subscription resource properties that the API response will include.
            channel_id (Optional[str]): The channelId parameter specifies a YouTube channel ID.
            mine (bool): The mine parameter set to true indicates that only the API requests subscriptions for the currently authenticated user.
            max_results (int): The maxResults parameter specifies the maximum number of items that should be returned in the result set.

        Returns:
            Dict[str, Any]: A dictionary containing subscription information.
        """
        if mine and not self.current_channel:
            return {"items": [], "error": "No current channel set for 'mine' parameter."}

        target_channel_id = self.current_channel if mine else channel_id
        if not target_channel_id or target_channel_id not in self.channels:
            return {"items": []}

        subscriptions = []
        for subscribed_channel_id in self.channels[target_channel_id].get("subscriptions", []):
            subscriptions.append({
                "kind": "youtube#subscription",
                "id": f"sub_{target_channel_id}_{subscribed_channel_id}",
                "snippet": {
                    "publishedAt": "2024-01-01T00:00:00Z",
                    "channelTitle": self.channels[target_channel_id]["title"],
                    "description": f"Subscription from {self.channels[target_channel_id]['title']} to {self.channels.get(subscribed_channel_id, {}).get('title', 'Unknown Channel')}",
                    "resourceId": {
                        "kind": "youtube#channel",
                        "channelId": subscribed_channel_id
                    },
                    "channelId": target_channel_id
                }
            })
        return {"items": subscriptions[:max_results]}

    def youtube_playlist_items_list(self, part: str, max_results: int = 5, playlist_id: Optional[str] = None, video_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns a collection of playlist items that match the API request parameters.
        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more playlistItem resource properties that the API response will include.
            max_results (int): The maxResults parameter specifies the maximum number of items that should be returned in the result set.
            playlist_id (Optional[str]): The playlistId parameter specifies the unique ID of the playlist for which you want to retrieve playlist items.
            video_id (Optional[str]): The videoId parameter specifies that the request should return only the playlist items that contain the specified video.

        Returns:
            Dict[str, Any]: A dictionary containing playlist items.
        """
        if not playlist_id:
            return {"items": [], "error": "playlist_id is required."}

        for channel_data in self.channels.values():
            if playlist_id in channel_data.get("playlists", {}):
                playlist = channel_data["playlists"][playlist_id]
                items = []
                for vid in playlist.get("video_ids", []):
                    if video_id and vid != video_id:
                        continue
                    items.append({
                        "kind": "youtube#playlistItem",
                        "id": f"pli_{playlist_id}_{vid}",
                        "snippet": {
                            "playlistId": playlist_id,
                            "position": playlist["video_ids"].index(vid),
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": vid
                            },
                            "title": self.channels[channel_data["title"]]["videos"].get(vid, {}).get("title", "Unknown Video"),
                            "publishedAt": "2024-01-01T00:00:00Z", # Dummy date
                            "channelId": channel_data["title"]
                        }
                    })
                return {"items": items[:max_results]}
        return {"items": [], "error": "Playlist not found."}

    def youtube_playlist_items_insert(self, part: str, playlist_id: str, video_id: str) -> Dict[str, Any]:
        """
        Adds a video to a playlist.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more playlistItem resource properties that the API response will include.
            playlist_id (str): The playlistId parameter specifies the unique ID of the playlist to which the item will be added.
            video_id (str): The videoId parameter specifies the ID of the video that is being added to the playlist.

        Returns:
            Dict[str, Any]: A dictionary containing information about the inserted playlist item.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}

        if playlist_id not in self.channels[self.current_channel].get("playlists", {}):
            return {"error": "Playlist not found in current channel."}

        if video_id not in self.channels[self.current_channel].get("videos", {}):
            return {"error": "Video not found in current channel's videos."}

        self.channels[self.current_channel]["playlists"][playlist_id].setdefault("video_ids", []).append(video_id)
        return {"success": True, "playlist_id": playlist_id, "video_id": video_id}

    def youtube_playlist_items_update(self, part: str, playlist_item_id: str, playlist_id: str, video_id: str, position: int) -> Dict[str, Any]:
        """
        Modifies a playlist item. For example, you can move an item within a playlist.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more playlistItem resource properties that the API response will include.
            playlist_item_id (str): The playlist_item_id parameter specifies the ID of the playlist item that is being updated.
            playlist_id (str): The playlistId parameter specifies the unique ID of the playlist that the item belongs to.
            video_id (str): The videoId parameter specifies the ID of the video that the playlist item refers to.
            position (int): The position parameter specifies the zero-based position where the playlist item is located in the playlist.

        Returns:
            Dict[str, Any]: A dictionary containing information about the updated playlist item.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}

        if playlist_id not in self.channels[self.current_channel].get("playlists", {}):
            return {"error": "Playlist not found in current channel."}

        playlist_videos = self.channels[self.current_channel]["playlists"][playlist_id].get("video_ids", [])
        
        # Find the video and remove it
        try:
            old_index = playlist_videos.index(video_id)
            playlist_videos.pop(old_index)
        except ValueError:
            return {"error": "Video not found in the specified playlist."}
        
        # Insert the video at the new position
        if 0 <= position <= len(playlist_videos):
            playlist_videos.insert(position, video_id)
            return {"success": True, "playlist_item_id": playlist_item_id, "new_position": position}
        else:
            return {"error": "Invalid position."}

    def youtube_playlist_items_delete(self, id: str) -> Dict[str, Any]:
        """
        Deletes a playlist item.

        Parameters:
            id (str): The id parameter specifies the YouTube playlist item ID for the resource that is being deleted.

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the deletion.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}

        # Assuming the id format is "pli_{playlist_id}_{video_id}"
        try:
            _, playlist_id, video_id_to_delete = id.split('_')
        except ValueError:
            return {"error": "Invalid playlist item ID format. Expected 'pli_{playlist_id}_{video_id}'."}

        if playlist_id not in self.channels[self.current_channel].get("playlists", {}):
            return {"error": "Playlist not found in current channel."}

        playlist_videos = self.channels[self.current_channel]["playlists"][playlist_id].get("video_ids", [])
        if video_id_to_delete in playlist_videos:
            playlist_videos.remove(video_id_to_delete)
            return {"success": True, "deleted_item_id": id}
        else:
            return {"error": "Playlist item (video) not found in the specified playlist."}

    def youtube_playlists_list(self, part: str, channel_id: Optional[str] = None, max_results: int = 5, mine: bool = False) -> Dict[str, Any]:
        """
        Returns a collection of playlists that match the API request parameters.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more playlist resource properties that the API response will include.
            channel_id (Optional[str]): The channelId parameter specifies a comma-separated list of channel IDs.
            max_results (int): The maxResults parameter specifies the maximum number of items that should be returned in the result set.
            mine (bool): The mine parameter set to true indicates that only the API requests playlists for the currently authenticated user.

        Returns:
            Dict[str, Any]: A dictionary containing playlist information.
        """
        target_channel_id = self.current_channel if mine else channel_id
        if not target_channel_id or target_channel_id not in self.channels:
            return {"items": []}

        playlists = []
        for playlist_id, playlist_data in self.channels[target_channel_id].get("playlists", {}).items():
            playlists.append({
                "kind": "youtube#playlist",
                "id": playlist_id,
                "snippet": {
                    "publishedAt": "2024-01-01T00:00:00Z", # Dummy date
                    "channelId": target_channel_id,
                    "title": playlist_data["title"],
                    "description": playlist_data["description"],
                    "channelTitle": self.channels[target_channel_id]["title"]
                },
                "status": {
                    "privacyStatus": playlist_data["privacy_status"]
                },
                "contentDetails": {
                    "itemCount": len(playlist_data.get("video_ids", []))
                }
            })
        return {"items": playlists[:max_results]}

    def youtube_playlists_insert(self, part: str, title: str, description: Optional[str] = None, privacy_status: str = "private") -> Dict[str, Any]:
        """
        Creates a playlist.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more playlist resource properties that the API response will include.
            title (str): The title of the playlist.
            description (Optional[str]): The description of the playlist.
            privacy_status (str): The privacy status of the playlist (public, private, unlisted).

        Returns:
            Dict[str, Any]: A dictionary containing information about the created playlist.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}

        new_playlist_id = f"playlist{len(self.channels[self.current_channel].get('playlists', {})) + 1}"
        self.channels[self.current_channel].setdefault("playlists", {})[new_playlist_id] = {
            "title": title,
            "description": description if description else "",
            "privacy_status": privacy_status,
            "video_ids": []
        }
        return {"success": True, "playlist_id": new_playlist_id, "title": title}

    def youtube_playlists_update(self, part: str, playlist_id: str, title: Optional[str] = None, description: Optional[str] = None, privacy_status: Optional[str] = None) -> Dict[str, Any]:
        """
        Modifies a playlist. For example, you can change a playlist's title, description, or privacy status.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more playlist resource properties that the API response will include.
            playlist_id (str): The playlistId parameter specifies the unique ID of the playlist that is being updated.
            title (Optional[str]): The title of the playlist.
            description (Optional[str]): The description of the playlist.
            privacy_status (Optional[str]): The privacy status of the playlist (public, private, unlisted).

        Returns:
            Dict[str, Any]: A dictionary containing information about the updated playlist.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}

        if playlist_id not in self.channels[self.current_channel].get("playlists", {}):
            return {"error": "Playlist not found in current channel."}

        playlist = self.channels[self.current_channel]["playlists"][playlist_id]
        if title:
            playlist["title"] = title
        if description is not None:
            playlist["description"] = description
        if privacy_status:
            playlist["privacy_status"] = privacy_status
        return {"success": True, "playlist_id": playlist_id, "updated_info": playlist}

    def youtube_playlists_delete(self, id: str) -> Dict[str, Any]:
        """
        Deletes a playlist.

        Parameters:
            id (str): The id parameter specifies the YouTube playlist ID for the resource that is being deleted.

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the deletion.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}

        if id in self.channels[self.current_channel].get("playlists", {}):
            del self.channels[self.current_channel]["playlists"][id]
            return {"success": True, "deleted_playlist_id": id}
        else:
            return {"error": "Playlist not found."}

    def youtube_subscriptions_insert(self, part: str, channel_id: str) -> Dict[str, Any]:
        """
        Adds a subscription to the API user's subscription list.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more subscription resource properties that the API response will include.
            channel_id (str): The channelId parameter specifies the YouTube channel ID of the channel that the API user is subscribing to.

        Returns:
            Dict[str, Any]: A dictionary containing information about the new subscription.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}
        if channel_id not in self.channels:
            return {"error": "Channel to subscribe to not found."}

        self.channels[self.current_channel].setdefault("subscriptions", []).append(channel_id)
        return {"success": True, "subscribed_to": channel_id}

    def youtube_subscriptions_delete(self, id: str) -> Dict[str, Any]:
        """
        Deletes a subscription from the API user's subscription list.

        Parameters:
            id (str): The id parameter specifies the YouTube subscription ID for the resource that is being deleted.

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the deletion.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}

        # Assuming 'id' is just the channel_id for simplicity in this dummy backend
        if id in self.channels[self.current_channel].get("subscriptions", []):
            self.channels[self.current_channel]["subscriptions"].remove(id)
            return {"success": True, "unsubscribed_from": id}
        else:
            return {"error": "Subscription not found."}

    def youtube_video_categories_list(self, part: str) -> Dict[str, Any]:
        """
        Returns a list of video categories that can be associated with YouTube videos.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more videoCategory resource properties that the API response will include.

        Returns:
            Dict[str, Any]: A dictionary containing video categories.
        """
        categories = []
        for cat_id, cat_name in self.video_categories.items():
            categories.append({
                "kind": "youtube#videoCategory",
                "id": cat_id,
                "snippet": {
                    "title": cat_name,
                    "assignable": True,
                    "channelId": "UCBR8-60-B28hp2BmDPdntcQ" # Dummy channel ID for categories
                }
            })
        return {"items": categories}

    def youtube_videos_list(self, part: str, id: Optional[str] = None, max_results: int = 5, video_category_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns a list of videos that match the API request parameters.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more video resource properties that the API response will include.
            id (Optional[str]): The id parameter specifies a comma-separated list of the YouTube video ID(s) for the resource(s) that are being retrieved.
            max_results (int): The maxResults parameter specifies the maximum number of items that should be returned in the result set.
            video_category_id (Optional[str]): The videoCategoryId parameter restricts the search results to videos in the specified category.

        Returns:
            Dict[str, Any]: A dictionary containing video information.
        """
        videos_list = []
        for channel_id, channel_data in self.channels.items():
            for video_id_str, video_data in channel_data.get("videos", {}).items():
                if id and video_id_str not in id.split(','):
                    continue
                if video_category_id and video_data["category_id"] != video_category_id:
                    continue
                videos_list.append({
                    "kind": "youtube#video",
                    "id": video_id_str,
                    "snippet": {
                        "publishedAt": "2024-01-01T00:00:00Z", # Dummy date
                        "channelId": channel_id,
                        "title": video_data["title"],
                        "description": video_data["description"],
                        "channelTitle": channel_data["title"],
                        "categoryId": video_data["category_id"]
                    },
                    "status": {
                        "privacyStatus": video_data["privacy_status"]
                    }
                })
        return {"items": videos_list[:max_results]}

    def youtube_videos_insert(self, part: str, file_path: str, title: str, description: Optional[str] = None, category_id: Optional[str] = None, privacy_status: str = "private") -> Dict[str, Any]:
        """
        Uploads a video to YouTube and optionally sets the video's metadata.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more video resource properties that the API response will include.
            file_path (str): The path to the video file to upload.
            title (str): The title of the video.
            description (Optional[str]): The description of the video.
            category_id (Optional[str]): The video's category ID.
            privacy_status (str): The video's privacy status (public, private, unlisted).

        Returns:
            Dict[str, Any]: A dictionary containing information about the uploaded video.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}
        new_video_id = f"video{len(self.channels[self.current_channel].get('videos', {})) + 1}"
        self.channels[self.current_channel].setdefault("videos", {})[new_video_id] = {
            "title": title,
            "description": description if description else "",
            "category_id": category_id if category_id else "22", # Default to People & Blogs
            "privacy_status": privacy_status,
            "file_path": file_path
        }
        return {"success": True, "video_id": new_video_id, "title": title}

    def youtube_videos_update(self, part: str, video_id: str, title: Optional[str] = None, description: Optional[str] = None, category_id: Optional[str] = None, privacy_status: Optional[str] = None) -> Dict[str, Any]:
        """
        Updates a video's metadata.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more video resource properties that the API response will include.
            video_id (str): The videoId parameter specifies the YouTube video ID of the video that is being updated.
            title (Optional[str]): The title of the video.
            description (Optional[str]): The description of the video.
            category_id (Optional[str]): The video's category ID.
            privacy_status (Optional[str]): The video's privacy status (public, private, unlisted).

        Returns:
            Dict[str, Any]: A dictionary containing information about the updated video.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}

        if video_id not in self.channels[self.current_channel].get("videos", {}):
            return {"error": "Video not found in current channel."}

        video = self.channels[self.current_channel]["videos"][video_id]
        if title:
            video["title"] = title
        if description is not None:
            video["description"] = description
        if category_id:
            video["category_id"] = category_id
        if privacy_status:
            video["privacy_status"] = privacy_status
        return {"success": True, "video_id": video_id, "updated_info": video}

    def youtube_videos_rate(self, id: str, rating: str) -> Dict[str, Any]:
        """
        Adds a like or dislike rating to a video or removes a rating from a video.

        Parameters:
            id (str): The id parameter specifies the YouTube video ID of the video that is being rated.
            rating (str): The rating parameter specifies the rating to apply to the video. Acceptable values are: like, dislike, none.

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the rating.
        """
        # In a dummy backend, we just acknowledge the rating
        if rating not in ["like", "dislike", "none"]:
            return {"error": "Invalid rating. Must be 'like', 'dislike', or 'none'."}
        return {"success": True, "video_id": id, "rating": rating}

    def youtube_videos_get_rating(self, id: str) -> Dict[str, Any]:
        """
        Retrieves the rating that the authorized user gave to a specified video.

        Parameters:
            id (str): The id parameter specifies a comma-separated list of the YouTube video ID(s) for the resource(s) for which you are retrieving rating information.

        Returns:
            Dict[str, Any]: A dictionary containing the video rating information.
        """
        # In a dummy backend, we'll return a placeholder rating
        return {"items": [{"videoId": id, "rating": "none"}]}

    def youtube_videos_report_abuse(self, video_id: str, reason_id: str) -> Dict[str, Any]:
        """
        Reports a video for containing abusive content.

        Parameters:
            video_id (str): The videoId parameter specifies the YouTube video ID of the video that is being reported.
            reason_id (str): The reasonId parameter identifies the primary reason for which the video is being reported.

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the report.
        """
        # In a real API, this would send a report
        return {"success": True, "video_id": video_id, "reason_id": reason_id, "message": "Video reported for abuse."}

    def youtube_captions_list(self, part: str, video_id: str, id: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns a list of caption tracks for a specified video.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more caption resource properties that the API response will include.
            video_id (str): The videoId parameter specifies the YouTube video ID of the video for which you want to retrieve caption tracks.
            id (Optional[str]): The id parameter specifies a comma-separated list of the YouTube caption track ID(s) for the resource(s) that are being retrieved.

        Returns:
            Dict[str, Any]: A dictionary containing caption track information.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}
        
        captions = []
        for cap_id, cap_data in self.channels[self.current_channel].get("captions", {}).items():
            if cap_data["video_id"] == video_id and (not id or cap_id == id):
                captions.append({
                    "kind": "youtube#caption",
                    "id": cap_id,
                    "snippet": {
                        "videoId": cap_data["video_id"],
                        "language": cap_data["language"],
                        "name": cap_data["name"],
                        "lastUpdated": "2024-01-01T00:00:00Z", # Dummy date
                        "trackKind": "standard",
                        "isDraft": cap_data["is_draft"],
                        "isAutoSynced": False,
                        "status": "serving"
                    }
                })
        return {"items": captions}

    def youtube_captions_update(self, part: str, id: str, file_path: str, draft: Optional[bool] = None) -> Dict[str, Any]:
        """
        Updates a caption track.

        Parameters:
            part (str): The part parameter specifies a comma-separated list of one or more caption resource properties that the API response will include.
            id (str): The id parameter specifies the YouTube caption track ID of the caption track that is being updated.
            file_path (str): The path to the caption track file to upload.
            draft (Optional[bool]): Indicates whether the caption track is a draft.

        Returns:
            Dict[str, Any]: A dictionary containing information about the updated caption track.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}

        if id not in self.channels[self.current_channel].get("captions", {}):
            return {"error": "Caption track not found."}

        caption = self.channels[self.current_channel]["captions"][id]
        caption["file_path"] = file_path
        if draft is not None:
            caption["is_draft"] = draft
        return {"success": True, "caption_id": id, "updated_info": caption}

    def youtube_captions_delete(self, id: str) -> Dict[str, Any]:
        """
        Deletes a caption track.

        Parameters:
            id (str): The id parameter specifies the YouTube caption track ID for the resource that is being deleted.

        Returns:
            Dict[str, Any]: A dictionary indicating the success or failure of the deletion.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}
        if id in self.channels[self.current_channel].get("captions", {}):
            del self.channels[self.current_channel]["captions"][id]
            return {"success": True, "deleted_caption_id": id}
        else:
            return {"error": "Caption track not found."}

    def youtube_channel_banners_insert(self, image_path: str) -> Dict[str, Any]:
        """
        Uploads a channel banner image to YouTube.

        Parameters:
            image_path (str): The path to the banner image file.

        Returns:
            Dict[str, Any]: A dictionary containing information about the uploaded banner.
        """
        if not self.current_channel:
            return {"error": "No current channel set."}
        
        # In a real API, this would upload the image and return a URL
        # For this dummy, we'll just acknowledge the upload and store the path
        self.channels[self.current_channel]["banner_image_path"] = image_path
        return {"success": True, "image_path": image_path, "message": "Banner uploaded successfully (dummy)."}