import datetime
import copy
import json
import uuid
import random
from typing import Dict, Any
from fake_data import first_names, last_names, channel_bios, comment_texts, video_titles_general  

_initial_user_id_map = {}
_initial_channel_id_map = {}
_initial_video_id_map = {}
_initial_playlist_id_map = {}
_initial_comment_id_map = {}

def _convert_initial_data_to_uuids(initial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Converts the initial RAW_DEFAULT_STATE data to use UUIDs for all relevant IDs and adds realism."""

    converted_data = copy.deepcopy(initial_data)

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

    current_time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds') + "Z"

    new_users = {}
    for old_user_email, user_data in converted_data.get("users", {}).items():
        user_uuid = str(uuid.uuid4())
        _initial_user_id_map[old_user_email] = user_uuid
        user_data["user_id"] = user_uuid 
        user_data["email"] = f"user_{user_uuid[:8]}@oxytail.com" 
        if "joined_date" not in user_data:
            user_data["joined_date"] = current_time_iso
        elif not isinstance(user_data["joined_date"], str):
             user_data["joined_date"] = user_data["joined_date"].isoformat(timespec='milliseconds') + "Z"
        new_users[user_uuid] = user_data
    converted_data["users"] = new_users

    
    new_channels = {}
    for old_channel_id, channel_data in converted_data.get("channels", {}).items():
        channel_uuid = str(uuid.uuid4())
        _initial_channel_id_map[old_channel_id] = channel_uuid
        channel_data["id"] = channel_uuid 

        
        if "owner_id" in channel_data and channel_data["owner_id"] in _initial_user_id_map:
            channel_data["owner_id"] = _initial_user_id_map[channel_data["owner_id"]]
        else: 
            if new_users:
                channel_data["owner_id"] = random.choice(list(new_users.keys()))
            else:
                channel_data["owner_id"] = str(uuid.uuid4()) 
        
        
        if "created_at" not in channel_data:
            channel_data["created_at"] = current_time_iso
        elif not isinstance(channel_data["created_at"], str):
            channel_data["created_at"] = channel_data["created_at"].isoformat(timespec='milliseconds') + "Z"

        
        if "subscribers" in channel_data:
            channel_data["subscribers_temp"] = channel_data["subscribers"]
            channel_data["subscribers"] = [] 

        
        if "videos" in channel_data:
            channel_data["videos_temp"] = channel_data["videos"]
            channel_data["videos"] = [] 
        
        
        if "playlists" in channel_data:
            channel_data["playlists_temp"] = channel_data["playlists"]
            channel_data["playlists"] = [] 

        new_channels[channel_uuid] = channel_data
    converted_data["channels"] = new_channels

    
    new_videos = {}
    for old_video_id, video_data in converted_data.get("videos", {}).items():
        video_uuid = str(uuid.uuid4())
        _initial_video_id_map[old_video_id] = video_uuid
        video_data["id"] = video_uuid 

        
        if "channel_id" in video_data and video_data["channel_id"] in _initial_channel_id_map:
            video_data["channel_id"] = _initial_channel_id_map[video_data["channel_id"]]
        if "uploader_id" in video_data and video_data["uploader_id"] in _initial_user_id_map:
            video_data["uploader_id"] = _initial_user_id_map[video_data["uploader_id"]]

        
        if "published_at" not in video_data:
            video_data["published_at"] = current_time_iso
        elif not isinstance(video_data["published_at"], str):
            video_data["published_at"] = video_data["published_at"].isoformat(timespec='milliseconds') + "Z"
        
        
        if "liked_by" in video_data:
            video_data["liked_by_temp"] = video_data["liked_by"]
            video_data["liked_by"] = [] 

        
        if "comments" in video_data:
            video_data["comments_temp"] = video_data["comments"]
            video_data["comments"] = [] 

        new_videos[video_uuid] = video_data
    converted_data["videos"] = new_videos

    
    new_playlists = {}
    for old_playlist_id, playlist_data in converted_data.get("playlists", {}).items():
        playlist_uuid = str(uuid.uuid4())
        _initial_playlist_id_map[old_playlist_id] = playlist_uuid
        playlist_data["id"] = playlist_uuid 

        
        if "owner_id" in playlist_data and playlist_data["owner_id"] in _initial_user_id_map:
            playlist_data["owner_id"] = _initial_user_id_map[playlist_data["owner_id"]]
        if "channel_id" in playlist_data and playlist_data["channel_id"] in _initial_channel_id_map:
            playlist_data["channel_id"] = _initial_channel_id_map[playlist_data["channel_id"]]

        
        if "video_ids" in playlist_data:
            playlist_data["video_ids_temp"] = playlist_data["video_ids"]
            playlist_data["video_ids"] = [] 
        
        
        if "created_at" not in playlist_data:
            playlist_data["created_at"] = current_time_iso
        elif not isinstance(playlist_data["created_at"], str):
            playlist_data["created_at"] = playlist_data["created_at"].isoformat(timespec='milliseconds') + "Z"

        new_playlists[playlist_uuid] = playlist_data
    converted_data["playlists"] = new_playlists

    
    new_comments = {}
    for old_comment_id, comment_data in converted_data.get("comments", {}).items():
        comment_uuid = str(uuid.uuid4())
        _initial_comment_id_map[old_comment_id] = comment_uuid
        comment_data["id"] = comment_uuid 

        
        if "video_id" in comment_data and comment_data["video_id"] in _initial_video_id_map:
            comment_data["video_id"] = _initial_video_id_map[comment_data["video_id"]]
        if "author_id" in comment_data and comment_data["author_id"] in _initial_user_id_map:
            comment_data["author_id"] = _initial_user_id_map[comment_data["author_id"]]
        
        
        if "created_at" not in comment_data:
            comment_data["created_at"] = current_time_iso
        elif not isinstance(comment_data["created_at"], str):
            comment_data["created_at"] = comment_data["created_at"].isoformat(timespec='milliseconds') + "Z"

        new_comments[comment_uuid] = comment_data
    converted_data["comments"] = new_comments

    

    
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
        if "subscribers_temp" in channel_data:
            channel_data["subscribers"] = [
                _initial_user_id_map.get(u_id, u_id) for u_id in channel_data.pop("subscribers_temp")
            ]
            channel_data["subscribers"] = [
                u_id for u_id in channel_data["subscribers"] if u_id in new_users
            ]
        if "videos_temp" in channel_data:
            channel_data["videos"] = [
                _initial_video_id_map.get(v_id, v_id) for v_id in channel_data.pop("videos_temp")
            ]
            channel_data["videos"] = [
                v_id for v_id in channel_data["videos"] if v_id in new_videos
            ]
        if "playlists_temp" in channel_data:
            channel_data["playlists"] = [
                _initial_playlist_id_map.get(p_id, p_id) for p_id in channel_data.pop("playlists_temp")
            ]
            channel_data["playlists"] = [
                p_id for p_id in channel_data["playlists"] if p_id in new_playlists
            ]
    
    
    for video_uuid, video_data in new_videos.items():
        if "comments_temp" in video_data:
            video_data["comments"] = [
                _initial_comment_id_map.get(c_id, c_id) for c_id in video_data.pop("comments_temp")
            ]
            video_data["comments"] = [
                c_id for c_id in video_data["comments"] if c_id in new_comments
            ]
        if "liked_by_temp" in video_data:
            video_data["liked_by"] = [
                _initial_user_id_map.get(u_id, u_id) for u_id in video_data.pop("liked_by_temp")
            ]
            video_data["liked_by"] = [
                u_id for u_id in video_data["liked_by"] if u_id in new_users
            ]

    
    for playlist_uuid, playlist_data in new_playlists.items():
        if "video_ids_temp" in playlist_data:
            playlist_data["video_ids"] = [
                _initial_video_id_map.get(v_id, v_id) for v_id in playlist_data.pop("video_ids_temp")
            ]
            playlist_data["video_ids"] = [
                v_id for v_id in playlist_data["video_ids"] if v_id in new_videos
            ]

    return converted_data



def generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365*5):
    """Generates a random ISO 8601 timestamp within a given range of days ago."""
    delta_days = random.randint(days_ago_min, days_ago_max)
    time_offset = datetime.timedelta(days=delta_days, 
                                     hours=random.randint(0, 23), 
                                     minutes=random.randint(0, 59), 
                                     seconds=random.randint(0, 59))
    dt = datetime.datetime.now(datetime.timezone.utc) - time_offset
    return dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

channel_niches = [
    {"title_suffix": "Gaming", "description": "Gaming tutorials, let's plays, and reviews.", "tags": ["gaming", "esports", "walkthrough"]},
    {"title_suffix": "Cooking", "description": "Delicious recipes and culinary adventures.", "tags": ["food", "recipe", "cooking"]},
    {"title_suffix": "Travel", "description": "Exploring amazing destinations around the world.", "tags": ["travel", "vlog", "adventure"]},
    {"title_suffix": "Tech Reviews", "description": "In-depth reviews of the latest gadgets and software.", "tags": ["tech", "review", "gadgets"]},
    {"title_suffix": "Fitness Journey", "description": "Workout routines, healthy eating, and wellness tips.", "tags": ["fitness", "health", "workout"]},
    {"title_suffix": "DIY Crafts", "description": "Creative DIY projects and craft ideas.", "tags": ["DIY", "crafts", "handmade"]},
    {"title_suffix": "Study Tips", "description": "Effective study techniques and academic advice.", "tags": ["education", "study", "learning"]},
    {"title_suffix": "Music Covers", "description": "Covering popular songs and original music.", "tags": ["music", "covers", "songwriting"]},
    {"title_suffix": "Coding Tutorials", "description": "Learn to code with easy-to-follow tutorials.", "tags": ["programming", "coding", "tutorial"]},
    {"title_suffix": "Art Showcase", "description": "Showcasing digital and traditional artwork.", "tags": ["art", "drawing", "painting"]},
    {"title_suffix": "Personal Finance", "description": "Tips for budgeting, investing, and financial freedom.", "tags": ["finance", "money", "investing"]},
    {"title_suffix": "Nature & Wildlife", "description": "Documenting the beauty of nature and its inhabitants.", "tags": ["nature", "wildlife", "documentary"]},
    {"title_suffix": "Book Reviews", "description": "Discussing new releases and classic literature.", "tags": ["books", "reading", "literature"]},
    {"title_suffix": "Science Explained", "description": "Making complex scientific concepts easy to understand.", "tags": ["science", "education", "discovery"]},
    {"title_suffix": "Comedy Skits", "description": "Short, funny skits and relatable humor.", "tags": ["comedy", "skits", "funny"]},
    {"title_suffix": "Fashion & Style", "description": "Latest trends, fashion hauls, and styling tips.", "tags": ["fashion", "style", "beauty"]}
]


RAW_DEFAULT_STATE = {
    "users": {
        "alice.smith@oxytail.com": {
            "user_id": "user_alice", 
            "display_name": "Alice Smith",
            "email": "alice.smith@oxytail.com", 
            "joined_date": datetime.datetime(2023, 1, 15, 10, 0, 0, tzinfo=datetime.timezone.utc),
            "channels": ["UC_AliceVlogs", "UC_AliceGaming"], 
            "subscriptions": ["UC_BobTech", "UC_CharlieCooks"], 
            "watch_history": ["vid_001", "vid_003", "vid_005"], 
            "liked_videos": ["vid_001", "vid_004"], 
            "watch_later_playlist": [], 
            "notification_settings": {"comments": True, "subscriptions": True, "likes": False},
            "channel_history": [], 
            "language_preference": "en-US",
            "account_status": "active"
        },
        "bob.jones@oxytail.com": {
            "user_id": "user_bob", 
            "display_name": "Bob Jones",
            "email": "bob.jones@oxytail.com", 
            "joined_date": datetime.datetime(2022, 11, 1, 14, 30, 0, tzinfo=datetime.timezone.utc),
            "channels": ["UC_BobTech"], 
            "subscriptions": ["UC_AliceVlogs"], 
            "watch_history": ["vid_002", "vid_004"], 
            "liked_videos": ["vid_002"], 
            "watch_later_playlist": [],
            "notification_settings": {"comments": False, "subscriptions": True, "likes": True},
            "channel_history": [],
            "language_preference": "en-CA",
            "account_status": "active"
        },
        "charlie.brown@oxytail.com": {
            "user_id": "user_charlie", 
            "display_name": "Charlie Brown",
            "email": "charlie.brown@oxytail.com", 
            "joined_date": datetime.datetime(2024, 3, 20, 9, 0, 0, tzinfo=datetime.timezone.utc),
            "channels": ["UC_CharlieCooks"], 
            "subscriptions": ["UC_AliceVlogs", "UC_BobTech"], 
            "watch_history": ["vid_001", "vid_002"], 
            "liked_videos": [],
            "watch_later_playlist": [],
            "notification_settings": {"comments": True, "subscriptions": False, "likes": True},
            "channel_history": [],
            "language_preference": "en-GB",
            "account_status": "active"
        }
    },
    "channels": {
        "UC_AliceVlogs": {
            "id": "UC_AliceVlogs", 
            "title": "Alice's Daily Vlogs",
            "description": "Daily life vlogs and adventures.",
            "owner_id": "alice.smith@oxytail.com", 
            "created_at": datetime.datetime(2023, 2, 1, 12, 0, 0, tzinfo=datetime.timezone.utc),
            "subscribers": ["bob.jones@oxytail.com", "charlie.brown@oxytail.com"], 
            "videos": ["vid_001", "vid_003"], 
            "playlists": ["playlist_001"], 
            "country": "US",
            "view_count": 12000,
            "subscriber_count": 500,
            "video_count": 2,
            "banner_image_path": "https://YouTube.com/channel_banners/alice_vlogs_banner.jpg",
            "channel_type": "lifestyle",
            "is_monetized": True
        },
        "UC_BobTech": {
            "id": "UC_BobTech", 
            "title": "Bob's Tech Reviews",
            "description": "Unbiased tech reviews and tutorials.",
            "owner_id": "bob.jones@oxytail.com", 
            "created_at": datetime.datetime(2022, 12, 10, 9, 30, 0, tzinfo=datetime.timezone.utc),
            "subscribers": ["alice.smith@oxytail.com", "charlie.brown@oxytail.com"], 
            "videos": ["vid_002", "vid_004"], 
            "playlists": ["playlist_002"], 
            "country": "CA",
            "view_count": 25000,
            "subscriber_count": 1200,
            "video_count": 2,
            "banner_image_path": "https://YouTube.com/channel_banners/bob_tech_banner.jpg",
            "channel_type": "technology",
            "is_monetized": True
        },
        "UC_CharlieCooks": {
            "id": "UC_CharlieCooks", 
            "title": "Charlie's Cooking Adventures",
            "description": "Easy and delicious recipes for everyone.",
            "owner_id": "charlie.brown@oxytail.com", 
            "created_at": datetime.datetime(2024, 4, 1, 10, 0, 0, tzinfo=datetime.timezone.utc),
            "subscribers": ["alice.smith@oxytail.com"], 
            "videos": ["vid_005"], 
            "playlists": [],
            "country": "GB",
            "view_count": 8000,
            "subscriber_count": 300,
            "video_count": 1,
            "banner_image_path": "https://YouTube.com/channel_banners/charlie_cooks_banner.jpg",
            "channel_type": "cooking",
            "is_monetized": False
        },
        "UC_AliceGaming": { 
            "id": "UC_AliceGaming", 
            "title": "Alice's Gaming Zone",
            "description": "Gameplay, streams, and gaming news.",
            "owner_id": "alice.smith@oxytail.com", 
            "created_at": datetime.datetime(2023, 5, 10, 16, 0, 0, tzinfo=datetime.timezone.utc),
            "subscribers": [],
            "videos": [],
            "playlists": [],
            "country": "US",
            "view_count": 1500,
            "subscriber_count": 50,
            "video_count": 0,
            "banner_image_path": "https://YouTube.com/channel_banners/alice_gaming_banner.jpg",
            "channel_type": "gaming",
            "is_monetized": False
        }
    },
    "videos": {
        "vid_001": {
            "id": "vid_001", 
            "title": "My First Vlog: Exploring New York",
            "description": "A tour of New York City's landmarks.",
            "channel_id": "UC_AliceVlogs", 
            "uploader_id": "alice.smith@oxytail.com", 
            "published_at": datetime.datetime(2023, 2, 5, 15, 0, 0, tzinfo=datetime.timezone.utc),
            "duration_seconds": 600,
            "views": 5000,
            "likes": 250,
            "dislikes": 10,
            "comments": ["comment_001", "comment_002"], 
            "tags": ["travel", "vlog", "NYC"],
            "category": "Travel & Events",
            "privacy_status": "public",
            "age_restricted": False,
            "thumbnail_url": "https://YouTube.com/thumbnails/vid_001.jpg",
            "liked_by": [] 
        },
        "vid_002": {
            "id": "vid_002", 
            "title": "Best Budget Smartphones 2024",
            "description": "Review of affordable smartphones.",
            "channel_id": "UC_BobTech", 
            "uploader_id": "bob.jones@oxytail.com", 
            "published_at": datetime.datetime(2023, 1, 20, 11, 0, 0, tzinfo=datetime.timezone.utc),
            "duration_seconds": 900,
            "views": 10000,
            "likes": 800,
            "dislikes": 25,
            "comments": ["comment_003"], 
            "tags": ["tech", "review", "smartphone"],
            "category": "Science & Technology",
            "privacy_status": "public",
            "age_restricted": False,
            "thumbnail_url": "https://YouTube.com/thumbnails/vid_002.jpg",
            "liked_by": []
        },
        "vid_003": {
            "id": "vid_003", 
            "title": "Morning Routine & Productivity Tips",
            "description": "How I stay productive throughout the day.",
            "channel_id": "UC_AliceVlogs", 
            "uploader_id": "alice.smith@oxytail.com", 
            "published_at": datetime.datetime(2023, 3, 1, 9, 0, 0, tzinfo=datetime.timezone.utc),
            "duration_seconds": 480,
            "views": 3000,
            "likes": 150,
            "dislikes": 5,
            "comments": [],
            "tags": ["productivity", "routine", "lifestyle"],
            "category": "Howto & Style",
            "privacy_status": "public",
            "age_restricted": False,
            "thumbnail_url": "https://YouTube.com/thumbnails/vid_003.jpg",
            "liked_by": []
        },
        "vid_004": {
            "id": "vid_004", 
            "title": "Gaming PC Build Guide 2024",
            "description": "Step-by-step guide to building a gaming PC.",
            "channel_id": "UC_BobTech", 
            "uploader_id": "bob.jones@oxytail.com", 
            "published_at": datetime.datetime(2023, 4, 10, 18, 0, 0, tzinfo=datetime.timezone.utc),
            "duration_seconds": 1200,
            "views": 15000,
            "likes": 1200,
            "dislikes": 30,
            "comments": [],
            "tags": ["gaming", "PCBuild", "tutorial"],
            "category": "Gaming",
            "privacy_status": "public",
            "age_restricted": False,
            "thumbnail_url": "https://YouTube.com/thumbnails/vid_004.jpg",
            "liked_by": []
        },
        "vid_005": {
            "id": "vid_005", 
            "title": "Easy Pasta Carbonara Recipe",
            "description": "A quick and delicious carbonara recipe.",
            "channel_id": "UC_CharlieCooks", 
            "uploader_id": "charlie.brown@oxytail.com", 
            "published_at": datetime.datetime(2024, 4, 5, 14, 0, 0, tzinfo=datetime.timezone.utc),
            "duration_seconds": 360,
            "views": 7000,
            "likes": 400,
            "dislikes": 8,
            "comments": [],
            "tags": ["cooking", "recipe", "pasta"],
            "category": "Cooking",
            "privacy_status": "public",
            "age_restricted": False,
            "thumbnail_url": "https://YouTube.com/thumbnails/vid_005.jpg",
            "liked_by": []
        }
    },
    "playlists": {
        "playlist_001": {
            "id": "playlist_001", 
            "title": "My Favorite Vlogs",
            "description": "A collection of my best vlogs.",
            "owner_id": "alice.smith@oxytail.com", 
            "channel_id": "UC_AliceVlogs", 
            "video_ids": ["vid_001", "vid_003"], 
            "created_at": datetime.datetime(2023, 2, 10, 16, 0, 0, tzinfo=datetime.timezone.utc),
            "privacy_status": "public",
            "item_count": 2
        },
        "playlist_002": {
            "id": "playlist_002", 
            "title": "Tech Essentials",
            "description": "Must-watch tech videos.",
            "owner_id": "bob.jones@oxytail.com", 
            "channel_id": "UC_BobTech", 
            "video_ids": ["vid_002", "vid_004"], 
            "created_at": datetime.datetime(2023, 1, 25, 10, 0, 0, tzinfo=datetime.timezone.utc),
            "privacy_status": "public",
            "item_count": 2
        }
    },
    "comments": {
        "comment_001": {
            "id": "comment_001", 
            "video_id": "vid_001", 
            "author_id": "bob.jones@oxytail.com", 
            "text": "Great vlog, Alice! Really enjoyed the NYC tour.",
            "created_at": datetime.datetime(2023, 2, 6, 10, 0, 0, tzinfo=datetime.timezone.utc),
            "likes": 5
        },
        "comment_002": {
            "id": "comment_002", 
            "video_id": "vid_001", 
            "author_id": "charlie.brown@oxytail.com", 
            "text": "Made me want to visit NYC again!",
            "created_at": datetime.datetime(2023, 2, 6, 11, 30, 0, tzinfo=datetime.timezone.utc),
            "likes": 2
        },
        "comment_003": {
            "id": "comment_003", 
            "video_id": "vid_002", 
            "author_id": "alice.smith@oxytail.com", 
            "text": "Very informative review, Bob! Helped me decide on my next phone.",
            "created_at": datetime.datetime(2023, 1, 21, 14, 0, 0, tzinfo=datetime.timezone.utc),
            "likes": 8
        }
    }
}

DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)

num_initial_users = len(DEFAULT_STATE["users"])
num_users_to_add = 50 - num_initial_users

all_user_uuids = list(DEFAULT_STATE["users"].keys())
existing_emails = set(user_data["email"] for user_data in DEFAULT_STATE["users"].values())

for i in range(num_users_to_add):
    first = random.choice(first_names)
    last = random.choice(last_names)
    
    
    email_suffix = random.randint(1000, 99999)
    email = f"{first.lower()}.{last.lower()}{email_suffix}@{random.choice(['oxytail.com', 'mailservice.net', 'videozone.org'])}"
    while email in existing_emails:
        email_suffix = random.randint(1000, 99999)
        email = f"{first.lower()}.{last.lower()}{email_suffix}@{random.choice(['oxytail.com', 'mailservice.net', 'videozone.org'])}"
    existing_emails.add(email)

    user_id = str(uuid.uuid4())
    all_user_uuids.append(user_id) 

    new_user_data = {
        "user_id": user_id,
        "display_name": f"{first} {last}",
        "email": email,
        "joined_date": generate_random_iso_timestamp(days_ago_min=365*2, days_ago_max=365*5), 
        "channels": [],
        "subscriptions": [],
        "watch_history": [],
        "liked_videos": [],
        "watch_later_playlist": [],
        "notification_settings": {
            "comments": random.choice([True, False]),
            "subscriptions": random.choice([True, False]),
            "likes": random.choice([True, False])
        },
        "channel_history": [],
        "language_preference": random.choice(["en-US", "es-ES", "fr-FR", "de-DE", "zh-CN"]),
        "account_status": "active" if random.random() < 0.95 else "suspended" 
    }
    DEFAULT_STATE["users"][user_id] = new_user_data

all_channel_uuids = list(DEFAULT_STATE["channels"].keys())

for user_id in all_user_uuids:
    user_data = DEFAULT_STATE["users"][user_id]
    
    
    if not user_data["channels"] and random.random() < 0.8: 
        channel_id = str(uuid.uuid4())
        niche = random.choice(channel_niches)
        title = f"{user_data['display_name'].split()[0]}'s {niche['title_suffix']}"
        description = niche["description"]
        
        new_channel_data = {
            "id": channel_id,
            "title": title,
            "description": description,
            "owner_id": user_id,
            "created_at": generate_random_iso_timestamp(days_ago_min=30, days_ago_max=730), 
            "subscribers": [], 
            "videos": [], 
            "playlists": [], 
            "country": random.choice(["US", "CA", "GB", "AU", "DE", "IN", "BR", "JP", "MX"]),
            "view_count": random.randint(100, 1000000),
            "subscriber_count": random.randint(0, 50000),
            "video_count": 0, 
            "banner_image_path": f"https://YouTube.com/channel_banners/{channel_id}.jpg",
            "channel_type": niche["title_suffix"].lower().replace(' ', '_'),
            "is_monetized": random.random() < 0.3 
        }
        DEFAULT_STATE["channels"][channel_id] = new_channel_data
        user_data["channels"].append(channel_id)
        all_channel_uuids.append(channel_id)


for user_id in all_user_uuids:
    user_data = DEFAULT_STATE["users"][user_id]
    num_subscriptions = random.randint(0, min(10, len(all_channel_uuids) - 1))
    
    
    possible_subscriptions = [cid for cid in all_channel_uuids if cid not in user_data["channels"]]
    
    user_data["subscriptions"].extend(random.sample(possible_subscriptions, min(num_subscriptions, len(possible_subscriptions))))
    user_data["subscriptions"] = list(set(user_data["subscriptions"])) 

    
    for sub_channel_id in user_data["subscriptions"]:
        if sub_channel_id in DEFAULT_STATE["channels"]:
            if user_id not in DEFAULT_STATE["channels"][sub_channel_id]["subscribers"]:
                DEFAULT_STATE["channels"][sub_channel_id]["subscribers"].append(user_id)
                DEFAULT_STATE["channels"][sub_channel_id]["subscriber_count"] += 1

all_video_uuids = list(DEFAULT_STATE["videos"].keys())

for channel_id, channel_data in DEFAULT_STATE["channels"].items():
    owner_id = channel_data["owner_id"]
    num_videos_to_add = random.randint(1, 15) 

    for i in range(num_videos_to_add):
        video_uuid = str(uuid.uuid4())
        
        title_template = random.choice(video_titles_general)
        title = title_template.replace("[Topic]", random.choice(["AI ethics", "sustainable living", "future of work"])) \
                              .replace("X", random.choice(["Python", "Gardening", "Meditation"])) \
                              .replace("Y", random.choice(["Japan", "Machu Picchu", "The Great Barrier Reef"])) \
                              .replace("Z", random.choice(["new smartphone", "smartwatch", "gaming console"])) \
                              .replace("[Category]", random.choice(["Gadgets", "Travel Destinations", "Workout Gear"])) \
                              .replace("[Something]", random.choice(["Sushi", "Bread", "Vegan Curry"]))


        description_template = random.choice(channel_bios)


        num_comments_for_video = random.choices([0, 1, 2, 5], weights=[0.5, 0.2, 0.2, 0.1], k=1)[0]
        comments_for_video = []

        video_data = {
            "id": video_uuid,
            "title": title,
            "description": description_template,
            "channel_id": channel_id,
            "uploader_id": owner_id,
            "published_at": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=730), 
            "duration_seconds": random.randint(60, 1800), 
            "views": random.randint(100, 500000),
            "likes": random.randint(0, 15000),
            "dislikes": random.randint(0, 500),
            "comments": comments_for_video, 
            "tags": random.sample(channel_niches[random.randint(0, len(channel_niches)-1)]["tags"] + ["new", "viral", "challenge"], random.randint(1, 4)),
            "category": channel_data["channel_type"].replace('_', ' ').title(), 
            "privacy_status": random.choice(["public", "unlisted", "private"]),
            "age_restricted": random.random() < 0.05, 
            "thumbnail_url": f"[https://YouTube.com/thumbnails/](https://YouTube.com/thumbnails/){video_uuid}.jpg",
            "liked_by": [] 
        }
        DEFAULT_STATE["videos"][video_uuid] = video_data
        channel_data["videos"].append(video_uuid)
        channel_data["video_count"] += 1
        all_video_uuids.append(video_uuid)

        
        user_owner_data = DEFAULT_STATE["users"][owner_id]
        if random.random() < 0.3: 
            video_data["liked_by"].append(owner_id)
            if video_uuid not in user_owner_data["liked_videos"]:
                user_owner_data["liked_videos"].append(video_uuid)
        if random.random() < 0.7: 
            if video_uuid not in user_owner_data["watch_history"]:
                user_owner_data["watch_history"].append(video_uuid)


for user_id in all_user_uuids:
    user_data = DEFAULT_STATE["users"][user_id]
    
    
    num_watched = random.randint(5, min(50, len(all_video_uuids)))
    user_data["watch_history"].extend(random.sample(all_video_uuids, min(num_watched, len(all_video_uuids))))
    user_data["watch_history"] = list(set(user_data["watch_history"])) 

    
    num_liked = random.randint(0, min(20, len(all_video_uuids)))
    user_data["liked_videos"].extend(random.sample(all_video_uuids, min(num_liked, len(all_video_uuids))))
    user_data["liked_videos"] = list(set(user_data["liked_videos"])) 

    
    for liked_vid_id in user_data["liked_videos"]:
        if liked_vid_id in DEFAULT_STATE["videos"] and user_id not in DEFAULT_STATE["videos"][liked_vid_id]["liked_by"]:
            DEFAULT_STATE["videos"][liked_vid_id]["liked_by"].append(user_id)
            DEFAULT_STATE["videos"][liked_vid_id]["likes"] += 1 

    
    if random.random() < 0.5: 
        num_to_watch_later = random.randint(0, min(10, len(all_video_uuids)))
        user_data["watch_later_playlist"].extend(random.sample(all_video_uuids, min(num_to_watch_later, len(all_video_uuids))))
        user_data["watch_later_playlist"] = list(set(user_data["watch_later_playlist"]))

    
    num_channels_visited = random.randint(0, min(15, len(all_channel_uuids)))
    user_data["channel_history"].extend(random.sample(all_channel_uuids, min(num_channels_visited, len(all_channel_uuids))))
    user_data["channel_history"] = list(set(user_data["channel_history"]))

all_playlist_uuids = list(DEFAULT_STATE["playlists"].keys())

for user_id in all_user_uuids:
    user_channels = DEFAULT_STATE["users"][user_id]["channels"]
    if not user_channels: 
        continue
    
    
    num_playlists_for_user = random.randint(0, 3) 

    for _ in range(num_playlists_for_user):
        playlist_uuid = str(uuid.uuid4())
        channel_for_playlist = random.choice(user_channels) 
        
        num_videos_in_playlist = random.randint(1, min(15, len(DEFAULT_STATE["channels"][channel_for_playlist]["videos"])))
        
        
        possible_videos = DEFAULT_STATE["channels"][channel_for_playlist]["videos"]
        if not possible_videos:
            continue

        playlist_videos = random.sample(possible_videos, num_videos_in_playlist)
        
        playlist_data = {
            "id": playlist_uuid,
            "title": f"{DEFAULT_STATE['channels'][channel_for_playlist]['title']} - My Top {random.choice(['Videos', 'Picks', 'Collection'])}",
            "description": f"A curated selection from {DEFAULT_STATE['channels'][channel_for_playlist]['title']}.",
            "owner_id": user_id,
            "channel_id": channel_for_playlist,
            "video_ids": playlist_videos,
            "created_at": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365), 
            "privacy_status": random.choice(["public", "unlisted"]),
            "item_count": len(playlist_videos)
        }
        DEFAULT_STATE["playlists"][playlist_uuid] = playlist_data
        DEFAULT_STATE["channels"][channel_for_playlist]["playlists"].append(playlist_uuid)
        all_playlist_uuids.append(playlist_uuid)

all_comment_uuids = list(DEFAULT_STATE["comments"].keys())

for video_id, video_data in DEFAULT_STATE["videos"].items():
    num_comments_to_add = random.choices([0, 1, 2, 3, 5, 10], weights=[0.4, 0.2, 0.15, 0.1, 0.1, 0.05], k=1)[0]

    possible_commenters = [uid for uid in all_user_uuids if uid != video_data["uploader_id"]] 
    
    for _ in range(num_comments_to_add):
        if not possible_commenters:
            break

        comment_uuid = str(uuid.uuid4())
        author_id = random.choice(possible_commenters)
        
        comment_data = {
            "id": comment_uuid,
            "video_id": video_id,
            "author_id": author_id,
            "text": random.choice(comment_texts),
            "created_at": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=300), 
            "likes": random.randint(0, 50)
        }
        DEFAULT_STATE["comments"][comment_uuid] = comment_data
        video_data["comments"].append(comment_uuid)
        all_comment_uuids.append(comment_uuid)

output_filename = 'diverse_youtube_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Total number of users: {len(DEFAULT_STATE['users'])}")
print(f"Total number of channels: {len(DEFAULT_STATE['channels'])}")
print(f"Total number of videos: {len(DEFAULT_STATE['videos'])}")
print(f"Total number of playlists: {len(DEFAULT_STATE['playlists'])}")
print(f"Total number of comments: {len(DEFAULT_STATE['comments'])}")
print(f"Generated DEFAULT_STATE saved to '{output_filename}'")