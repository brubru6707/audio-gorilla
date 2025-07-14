from typing import Any, Dict, Optional, List
import time
import uuid
from datetime import datetime, timedelta


class NetflixAPI:
    """
    Slim Netflix API mock backend for voice-assistant scenarios.

    This class exposes only the Netflix methods likely to be used by a large-language-model (LLM)
    responding to spoken commands, and maintains in-memory state for all relevant Netflix objects.
    """

    def __init__(self, token: Optional[str] = None) -> None:
        """
        Create a new NetflixAPI instance with mock state.

        Args:
            token: Netflix OAuth token. Store if you need it later.
        """
        self.token = token
        # State variables
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.watchlist: Dict[str, List[Dict[str, Any]]] = {}
        self.watching_history: Dict[str, List[Dict[str, Any]]] = {}
        self.ratings: Dict[str, Dict[str, int]] = {}
        self.recommendations: Dict[str, List[Dict[str, Any]]] = {}
        self.search_results: Dict[str, List[Dict[str, Any]]] = {}
        self.continue_watching: Dict[str, List[Dict[str, Any]]] = {}
        self.trending: List[Dict[str, Any]] = []
        self.categories: Dict[str, List[Dict[str, Any]]] = {}
        self.subscription_info: Dict[str, Any] = {}
        self.devices: List[Dict[str, Any]] = []
        self.notifications: List[Dict[str, Any]] = []
        self.favorites: Dict[str, List[str]] = {}
        self.parental_controls: Dict[str, Dict[str, Any]] = {}
        self.viewing_activity: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize with sample data
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """
        Populate the mock backend with some sample profiles, content, and data.
        """
        # Sample profiles
        self.profiles = {
            "P001": {
                "id": "P001",
                "name": "Main Profile",
                "avatar": "https://netflix.com/avatar1.png",
                "maturity_level": "adult",
                "language": "en",
                "autoplay": True
            },
            "P002": {
                "id": "P002", 
                "name": "Kids",
                "avatar": "https://netflix.com/avatar2.png",
                "maturity_level": "kids",
                "language": "en",
                "autoplay": False
            }
        }
        
        # Sample content
        sample_movies = [
            {
                "id": "M001",
                "title": "The Shawshank Redemption",
                "type": "movie",
                "year": 1994,
                "rating": "R",
                "duration": 142,
                "genre": ["Drama"],
                "description": "Two imprisoned men bond over a number of years...",
                "poster": "https://netflix.com/posters/shawshank.jpg",
                "cast": ["Tim Robbins", "Morgan Freeman"],
                "director": "Frank Darabont"
            },
            {
                "id": "M002",
                "title": "The Godfather",
                "type": "movie", 
                "year": 1972,
                "rating": "R",
                "duration": 175,
                "genre": ["Crime", "Drama"],
                "description": "The aging patriarch of an organized crime dynasty...",
                "poster": "https://netflix.com/posters/godfather.jpg",
                "cast": ["Marlon Brando", "Al Pacino"],
                "director": "Francis Ford Coppola"
            }
        ]
        
        sample_shows = [
            {
                "id": "S001",
                "title": "Breaking Bad",
                "type": "series",
                "year": 2008,
                "rating": "TV-MA",
                "seasons": 5,
                "genre": ["Crime", "Drama", "Thriller"],
                "description": "A high school chemistry teacher turned methamphetamine manufacturer...",
                "poster": "https://netflix.com/posters/breaking-bad.jpg",
                "cast": ["Bryan Cranston", "Aaron Paul"],
                "creator": "Vince Gilligan"
            },
            {
                "id": "S002", 
                "title": "Stranger Things",
                "type": "series",
                "year": 2016,
                "rating": "TV-14",
                "seasons": 4,
                "genre": ["Drama", "Fantasy", "Horror"],
                "description": "When a young boy disappears, his mother must confront terrifying forces...",
                "poster": "https://netflix.com/posters/stranger-things.jpg",
                "cast": ["Millie Bobby Brown", "Finn Wolfhard"],
                "creator": "The Duffer Brothers"
            }
        ]
        
        # Initialize watchlists
        self.watchlist = {
            "P001": [sample_movies[0], sample_shows[0]],
            "P002": [sample_shows[1]]
        }
        
        # Initialize watching history
        self.watching_history = {
            "P001": [
                {
                    "content_id": "M001",
                    "title": "The Shawshank Redemption",
                    "type": "movie",
                    "watched_at": int(time.time()) - 86400,  # 1 day ago
                    "progress": 100,
                    "completed": True
                }
            ],
            "P002": []
        }
        
        # Initialize ratings
        self.ratings = {
            "P001": {"M001": 5, "S001": 4},
            "P002": {"S002": 5}
        }
        
        # Initialize recommendations
        self.recommendations = {
            "P001": sample_movies + sample_shows,
            "P002": [sample_shows[1]]
        }
        
        # Initialize continue watching
        self.continue_watching = {
            "P001": [
                {
                    "content_id": "S001",
                    "title": "Breaking Bad",
                    "type": "series",
                    "season": 1,
                    "episode": 3,
                    "progress": 25,
                    "resume_time": 1200  # 20 minutes in
                }
            ],
            "P002": []
        }
        
        # Initialize trending
        self.trending = sample_movies + sample_shows
        
        # Initialize categories
        self.categories = {
            "Drama": sample_movies + sample_shows,
            "Crime": [sample_movies[1], sample_shows[0]],
            "Fantasy": [sample_shows[1]]
        }
        
        # Initialize subscription info
        self.subscription_info = {
            "plan": "Premium",
            "billing_cycle": "monthly",
            "next_billing": int(time.time()) + 2592000,  # 30 days
            "price": 17.99,
            "currency": "USD",
            "status": "active"
        }
        
        # Initialize devices
        self.devices = [
            {
                "id": "D001",
                "name": "Living Room TV",
                "type": "smart_tv",
                "last_used": int(time.time()) - 3600,
                "location": "Living Room"
            },
            {
                "id": "D002", 
                "name": "iPhone 13",
                "type": "mobile",
                "last_used": int(time.time()) - 7200,
                "location": "Mobile"
            }
        ]
        
        # Initialize notifications
        self.notifications = [
            {
                "id": "N001",
                "type": "new_release",
                "title": "New Season Available",
                "message": "Season 4 of Stranger Things is now available",
                "content_id": "S002",
                "timestamp": int(time.time()) - 86400,
                "read": False
            }
        ]
        
        # Initialize favorites
        self.favorites = {
            "P001": ["M001", "S001"],
            "P002": ["S002"]
        }
        
        # Initialize parental controls
        self.parental_controls = {
            "P002": {
                "enabled": True,
                "max_rating": "TV-Y7",
                "pin_required": True,
                "blocked_content": ["TV-MA", "R"]
            }
        }
        
        # Initialize viewing activity
        self.viewing_activity = {
            "P001": [
                {
                    "content_id": "M001",
                    "title": "The Shawshank Redemption",
                    "type": "movie",
                    "watched_at": int(time.time()) - 86400,
                    "duration_watched": 142,
                    "device": "D001"
                }
            ],
            "P002": []
        }

    # ------------------------------------------------------------------
    # profiles.* — profile management
    # ------------------------------------------------------------------

    def profiles_list(self) -> Dict[str, Any]:
        """
        List all profiles for the account.

        Returns:
            Dict[str, Any]: {"ok": bool, "profiles": list}
        """
        return {
            "ok": True,
            "profiles": list(self.profiles.values())
        }

    def profiles_get(self, profile_id: str) -> Dict[str, Any]:
        """
        Get information about a specific profile.

        Args:
            profile_id: ID of the profile to retrieve.

        Returns:
            Dict[str, Any]: {"ok": bool, "profile": dict}
        """
        if profile_id in self.profiles:
            return {
                "ok": True,
                "profile": self.profiles[profile_id]
            }
        
        return {"ok": False, "error": "profile_not_found"}

    def profiles_create(self, name: str, *, maturity_level: str = "adult", 
                       language: str = "en", autoplay: bool = True) -> Dict[str, Any]:
        """
        Create a new profile.

        Args:
            name: Name of the profile.
            maturity_level: Maturity level (adult, kids, teen).
            language: Preferred language code.
            autoplay: Whether to enable autoplay.

        Returns:
            Dict[str, Any]: {"ok": bool, "profile": dict}
        """
        profile_id = f"P{uuid.uuid4().hex[:8]}"
        
        profile = {
            "id": profile_id,
            "name": name,
            "avatar": f"https://netflix.com/avatar_{len(self.profiles) + 1}.png",
            "maturity_level": maturity_level,
            "language": language,
            "autoplay": autoplay
        }
        
        self.profiles[profile_id] = profile
        
        # Initialize empty lists for new profile
        self.watchlist[profile_id] = []
        self.watching_history[profile_id] = []
        self.ratings[profile_id] = {}
        self.recommendations[profile_id] = []
        self.continue_watching[profile_id] = []
        self.favorites[profile_id] = []
        self.viewing_activity[profile_id] = []
        
        return {
            "ok": True,
            "profile": profile
        }

    def profiles_update(self, profile_id: str, *, name: Optional[str] = None,
                       maturity_level: Optional[str] = None, language: Optional[str] = None,
                       autoplay: Optional[bool] = None) -> Dict[str, Any]:
        """
        Update profile settings.

        Args:
            profile_id: ID of the profile to update.
            name: New profile name.
            maturity_level: New maturity level.
            language: New language preference.
            autoplay: New autoplay setting.

        Returns:
            Dict[str, Any]: {"ok": bool, "profile": dict}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        profile = self.profiles[profile_id]
        
        if name is not None:
            profile["name"] = name
        if maturity_level is not None:
            profile["maturity_level"] = maturity_level
        if language is not None:
            profile["language"] = language
        if autoplay is not None:
            profile["autoplay"] = autoplay
        
        return {
            "ok": True,
            "profile": profile
        }

    def profiles_delete(self, profile_id: str) -> Dict[str, Any]:
        """
        Delete a profile.

        Args:
            profile_id: ID of the profile to delete.

        Returns:
            Dict[str, Any]: {"ok": bool}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        del self.profiles[profile_id]
        
        # Clean up associated data
        if profile_id in self.watchlist:
            del self.watchlist[profile_id]
        if profile_id in self.watching_history:
            del self.watching_history[profile_id]
        if profile_id in self.ratings:
            del self.ratings[profile_id]
        if profile_id in self.recommendations:
            del self.recommendations[profile_id]
        if profile_id in self.continue_watching:
            del self.continue_watching[profile_id]
        if profile_id in self.favorites:
            del self.favorites[profile_id]
        if profile_id in self.viewing_activity:
            del self.viewing_activity[profile_id]
        if profile_id in self.parental_controls:
            del self.parental_controls[profile_id]
        
        return {"ok": True}

    # ------------------------------------------------------------------
    # watchlist.* — watchlist management
    # ------------------------------------------------------------------

    def watchlist_add(self, profile_id: str, content_id: str) -> Dict[str, Any]:
        """
        Add content to watchlist.

        Args:
            profile_id: ID of the profile.
            content_id: ID of the content to add.

        Returns:
            Dict[str, Any]: {"ok": bool, "watchlist": list}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        # Mock content lookup
        content = {
            "id": content_id,
            "title": f"Content {content_id}",
            "type": "movie" if content_id.startswith("M") else "series"
        }
        
        if profile_id not in self.watchlist:
            self.watchlist[profile_id] = []
        
        # Check if already in watchlist
        if not any(item["id"] == content_id for item in self.watchlist[profile_id]):
            self.watchlist[profile_id].append(content)
        
        return {
            "ok": True,
            "watchlist": self.watchlist[profile_id]
        }

    def watchlist_remove(self, profile_id: str, content_id: str) -> Dict[str, Any]:
        """
        Remove content from watchlist.

        Args:
            profile_id: ID of the profile.
            content_id: ID of the content to remove.

        Returns:
            Dict[str, Any]: {"ok": bool, "watchlist": list}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        if profile_id in self.watchlist:
            self.watchlist[profile_id] = [
                item for item in self.watchlist[profile_id] 
                if item["id"] != content_id
            ]
        
        return {
            "ok": True,
            "watchlist": self.watchlist.get(profile_id, [])
        }

    def watchlist_list(self, profile_id: str) -> Dict[str, Any]:
        """
        List watchlist for a profile.

        Args:
            profile_id: ID of the profile.

        Returns:
            Dict[str, Any]: {"ok": bool, "watchlist": list}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        return {
            "ok": True,
            "watchlist": self.watchlist.get(profile_id, [])
        }

    # ------------------------------------------------------------------
    # ratings.* — content rating
    # ------------------------------------------------------------------

    def ratings_add(self, profile_id: str, content_id: str, rating: int) -> Dict[str, Any]:
        """
        Rate content (1-5 stars).

        Args:
            profile_id: ID of the profile.
            content_id: ID of the content to rate.
            rating: Rating from 1 to 5.

        Returns:
            Dict[str, Any]: {"ok": bool, "rating": int}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        if not 1 <= rating <= 5:
            return {"ok": False, "error": "invalid_rating"}
        
        if profile_id not in self.ratings:
            self.ratings[profile_id] = {}
        
        self.ratings[profile_id][content_id] = rating
        
        return {
            "ok": True,
            "rating": rating
        }

    def ratings_remove(self, profile_id: str, content_id: str) -> Dict[str, Any]:
        """
        Remove rating for content.

        Args:
            profile_id: ID of the profile.
            content_id: ID of the content.

        Returns:
            Dict[str, Any]: {"ok": bool}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        if profile_id in self.ratings and content_id in self.ratings[profile_id]:
            del self.ratings[profile_id][content_id]
        
        return {"ok": True}

    def ratings_list(self, profile_id: str) -> Dict[str, Any]:
        """
        List all ratings for a profile.

        Args:
            profile_id: ID of the profile.

        Returns:
            Dict[str, Any]: {"ok": bool, "ratings": dict}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        return {
            "ok": True,
            "ratings": self.ratings.get(profile_id, {})
        }

    # ------------------------------------------------------------------
    # recommendations.* — content recommendations
    # ------------------------------------------------------------------

    def recommendations_get(self, profile_id: str, *, limit: int = 20) -> Dict[str, Any]:
        """
        Get personalized recommendations for a profile.

        Args:
            profile_id: ID of the profile.
            limit: Maximum number of recommendations to return.

        Returns:
            Dict[str, Any]: {"ok": bool, "recommendations": list}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        recommendations = self.recommendations.get(profile_id, [])
        
        return {
            "ok": True,
            "recommendations": recommendations[:limit]
        }

    def recommendations_because_you_watched(self, profile_id: str, content_id: str) -> Dict[str, Any]:
        """
        Get recommendations based on a specific watched content.

        Args:
            profile_id: ID of the profile.
            content_id: ID of the watched content.

        Returns:
            Dict[str, Any]: {"ok": bool, "recommendations": list}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        # Mock: return some recommendations based on content type
        if content_id.startswith("M"):
            recommendations = [item for item in self.trending if item["type"] == "movie"][:5]
        else:
            recommendations = [item for item in self.trending if item["type"] == "series"][:5]
        
        return {
            "ok": True,
            "recommendations": recommendations
        }

    # ------------------------------------------------------------------
    # search.* — content search
    # ------------------------------------------------------------------

    def search_content(self, query: str, *, profile_id: Optional[str] = None,
                      type_filter: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Search for content.

        Args:
            query: Search query.
            profile_id: ID of the profile (for personalized results).
            type_filter: Filter by content type (movie, series).
            limit: Maximum number of results.

        Returns:
            Dict[str, Any]: {"ok": bool, "results": list, "total": int}
        """
        # Mock search results
        all_content = self.trending + list(self.categories.values())[0] if self.categories else []
        
        # Filter by query
        results = [
            item for item in all_content
            if query.lower() in item["title"].lower()
        ]
        
        # Apply type filter
        if type_filter:
            results = [item for item in results if item["type"] == type_filter]
        
        # Apply limit
        limited_results = results[:limit]
        
        return {
            "ok": True,
            "results": limited_results,
            "total": len(results)
        }

    def search_suggestions(self, query: str, *, limit: int = 10) -> Dict[str, Any]:
        """
        Get search suggestions.

        Args:
            query: Partial search query.
            limit: Maximum number of suggestions.

        Returns:
            Dict[str, Any]: {"ok": bool, "suggestions": list}
        """
        # Mock suggestions based on trending content
        suggestions = [
            item["title"] for item in self.trending
            if query.lower() in item["title"].lower()
        ][:limit]
        
        return {
            "ok": True,
            "suggestions": suggestions
        }

    # ------------------------------------------------------------------
    # continue_watching.* — resume playback
    # ------------------------------------------------------------------

    def continue_watching_list(self, profile_id: str) -> Dict[str, Any]:
        """
        Get continue watching list for a profile.

        Args:
            profile_id: ID of the profile.

        Returns:
            Dict[str, Any]: {"ok": bool, "continue_watching": list}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        return {
            "ok": True,
            "continue_watching": self.continue_watching.get(profile_id, [])
        }

    def continue_watching_update(self, profile_id: str, content_id: str, 
                               progress: int, *, season: Optional[int] = None,
                               episode: Optional[int] = None) -> Dict[str, Any]:
        """
        Update continue watching progress.

        Args:
            profile_id: ID of the profile.
            content_id: ID of the content.
            progress: Progress percentage (0-100).
            season: Season number (for series).
            episode: Episode number (for series).

        Returns:
            Dict[str, Any]: {"ok": bool, "continue_watching": list}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        if profile_id not in self.continue_watching:
            self.continue_watching[profile_id] = []
        
        # Find existing entry or create new one
        existing_entry = None
        for entry in self.continue_watching[profile_id]:
            if entry["content_id"] == content_id:
                existing_entry = entry
                break
        
        if existing_entry:
            existing_entry["progress"] = progress
            if season is not None:
                existing_entry["season"] = season
            if episode is not None:
                existing_entry["episode"] = episode
        else:
            new_entry = {
                "content_id": content_id,
                "title": f"Content {content_id}",
                "type": "movie" if content_id.startswith("M") else "series",
                "progress": progress,
                "resume_time": int(time.time())
            }
            if season is not None:
                new_entry["season"] = season
            if episode is not None:
                new_entry["episode"] = episode
            
            self.continue_watching[profile_id].append(new_entry)
        
        return {
            "ok": True,
            "continue_watching": self.continue_watching[profile_id]
        }

    # ------------------------------------------------------------------
    # trending.* — trending content
    # ------------------------------------------------------------------

    def trending_get(self, *, region: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Get trending content.

        Args:
            region: Region code for localized trending.
            limit: Maximum number of results.

        Returns:
            Dict[str, Any]: {"ok": bool, "trending": list}
        """
        return {
            "ok": True,
            "trending": self.trending[:limit]
        }

    def trending_movies(self, *, limit: int = 10) -> Dict[str, Any]:
        """
        Get trending movies.

        Args:
            limit: Maximum number of results.

        Returns:
            Dict[str, Any]: {"ok": bool, "trending_movies": list}
        """
        movies = [item for item in self.trending if item["type"] == "movie"]
        
        return {
            "ok": True,
            "trending_movies": movies[:limit]
        }

    def trending_shows(self, *, limit: int = 10) -> Dict[str, Any]:
        """
        Get trending TV shows.

        Args:
            limit: Maximum number of results.

        Returns:
            Dict[str, Any]: {"ok": bool, "trending_shows": list}
        """
        shows = [item for item in self.trending if item["type"] == "series"]
        
        return {
            "ok": True,
            "trending_shows": shows[:limit]
        }

    # ------------------------------------------------------------------
    # categories.* — content categories
    # ------------------------------------------------------------------

    def categories_list(self) -> Dict[str, Any]:
        """
        List all available categories.

        Returns:
            Dict[str, Any]: {"ok": bool, "categories": list}
        """
        return {
            "ok": True,
            "categories": list(self.categories.keys())
        }

    def categories_get(self, category: str, *, limit: int = 20) -> Dict[str, Any]:
        """
        Get content in a specific category.

        Args:
            category: Category name.
            limit: Maximum number of results.

        Returns:
            Dict[str, Any]: {"ok": bool, "category": str, "content": list}
        """
        if category not in self.categories:
            return {"ok": False, "error": "category_not_found"}
        
        return {
            "ok": True,
            "category": category,
            "content": self.categories[category][:limit]
        }

    # ------------------------------------------------------------------
    # subscription.* — account management
    # ------------------------------------------------------------------

    def get_subscription_info(self) -> Dict[str, Any]:
        """
        Get subscription information.

        Returns:
            Dict[str, Any]: {"ok": bool, "subscription": dict}
        """
        return {
            "ok": True,
            "subscription": self.subscription_info
        }

    def subscription_plans(self) -> Dict[str, Any]:
        """
        Get available subscription plans.

        Returns:
            Dict[str, Any]: {"ok": bool, "plans": list}
        """
        plans = [
            {
                "name": "Basic",
                "price": 8.99,
                "currency": "USD",
                "screens": 1,
                "quality": "480p"
            },
            {
                "name": "Standard", 
                "price": 13.99,
                "currency": "USD",
                "screens": 2,
                "quality": "1080p"
            },
            {
                "name": "Premium",
                "price": 17.99,
                "currency": "USD", 
                "screens": 4,
                "quality": "4K+HDR"
            }
        ]
        
        return {
            "ok": True,
            "plans": plans
        }

    def subscription_cancel(self) -> Dict[str, Any]:
        """
        Cancel subscription.

        Returns:
            Dict[str, Any]: {"ok": bool, "cancelled_at": int}
        """
        self.subscription_info["status"] = "cancelled"
        self.subscription_info["cancelled_at"] = int(time.time())
        
        return {
            "ok": True,
            "cancelled_at": int(time.time())
        }

    # ------------------------------------------------------------------
    # devices.* — device management
    # ------------------------------------------------------------------

    def devices_list(self) -> Dict[str, Any]:
        """
        List all devices associated with the account.

        Returns:
            Dict[str, Any]: {"ok": bool, "devices": list}
        """
        return {
            "ok": True,
            "devices": self.devices
        }

    def devices_remove(self, device_id: str) -> Dict[str, Any]:
        """
        Remove a device from the account.

        Args:
            device_id: ID of the device to remove.

        Returns:
            Dict[str, Any]: {"ok": bool}
        """
        self.devices = [device for device in self.devices if device["id"] != device_id]
        
        return {"ok": True}

    def devices_logout_all(self) -> Dict[str, Any]:
        """
        Logout from all devices.

        Returns:
            Dict[str, Any]: {"ok": bool, "logged_out_devices": int}
        """
        device_count = len(self.devices)
        self.devices = []
        
        return {
            "ok": True,
            "logged_out_devices": device_count
        }

    # ------------------------------------------------------------------
    # notifications.* — notification management
    # ------------------------------------------------------------------

    def notifications_list(self, *, unread_only: bool = False) -> Dict[str, Any]:
        """
        List notifications.

        Args:
            unread_only: If True, return only unread notifications.

        Returns:
            Dict[str, Any]: {"ok": bool, "notifications": list}
        """
        notifications = self.notifications
        
        if unread_only:
            notifications = [n for n in notifications if not n.get("read", False)]
        
        return {
            "ok": True,
            "notifications": notifications
        }

    def notifications_mark_read(self, notification_id: str) -> Dict[str, Any]:
        """
        Mark a notification as read.

        Args:
            notification_id: ID of the notification.

        Returns:
            Dict[str, Any]: {"ok": bool}
        """
        for notification in self.notifications:
            if notification["id"] == notification_id:
                notification["read"] = True
                return {"ok": True}
        
        return {"ok": False, "error": "notification_not_found"}

    def notifications_mark_all_read(self) -> Dict[str, Any]:
        """
        Mark all notifications as read.

        Returns:
            Dict[str, Any]: {"ok": bool, "marked_read": int}
        """
        marked_count = 0
        for notification in self.notifications:
            if not notification.get("read", False):
                notification["read"] = True
                marked_count += 1
        
        return {
            "ok": True,
            "marked_read": marked_count
        }

    # ------------------------------------------------------------------
    # favorites.* — favorite content
    # ------------------------------------------------------------------

    def favorites_add(self, profile_id: str, content_id: str) -> Dict[str, Any]:
        """
        Add content to favorites.

        Args:
            profile_id: ID of the profile.
            content_id: ID of the content to favorite.

        Returns:
            Dict[str, Any]: {"ok": bool, "favorites": list}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        if profile_id not in self.favorites:
            self.favorites[profile_id] = []
        
        if content_id not in self.favorites[profile_id]:
            self.favorites[profile_id].append(content_id)
        
        return {
            "ok": True,
            "favorites": self.favorites[profile_id]
        }

    def favorites_remove(self, profile_id: str, content_id: str) -> Dict[str, Any]:
        """
        Remove content from favorites.

        Args:
            profile_id: ID of the profile.
            content_id: ID of the content to remove.

        Returns:
            Dict[str, Any]: {"ok": bool, "favorites": list}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        if profile_id in self.favorites and content_id in self.favorites[profile_id]:
            self.favorites[profile_id].remove(content_id)
        
        return {
            "ok": True,
            "favorites": self.favorites.get(profile_id, [])
        }

    def favorites_list(self, profile_id: str) -> Dict[str, Any]:
        """
        List favorite content for a profile.

        Args:
            profile_id: ID of the profile.

        Returns:
            Dict[str, Any]: {"ok": bool, "favorites": list}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        favorite_content = []
        for content_id in self.favorites.get(profile_id, []):
            # Mock content lookup
            content = {
                "id": content_id,
                "title": f"Content {content_id}",
                "type": "movie" if content_id.startswith("M") else "series"
            }
            favorite_content.append(content)
        
        return {
            "ok": True,
            "favorites": favorite_content
        }

    # ------------------------------------------------------------------
    # parental_controls.* — parental control settings
    # ------------------------------------------------------------------

    def parental_controls_get(self, profile_id: str) -> Dict[str, Any]:
        """
        Get parental control settings for a profile.

        Args:
            profile_id: ID of the profile.

        Returns:
            Dict[str, Any]: {"ok": bool, "parental_controls": dict}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        return {
            "ok": True,
            "parental_controls": self.parental_controls.get(profile_id, {})
        }

    def parental_controls_update(self, profile_id: str, *, enabled: Optional[bool] = None,
                               max_rating: Optional[str] = None, pin_required: Optional[bool] = None,
                               blocked_content: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Update parental control settings.

        Args:
            profile_id: ID of the profile.
            enabled: Whether parental controls are enabled.
            max_rating: Maximum allowed content rating.
            pin_required: Whether PIN is required for restricted content.
            blocked_content: List of blocked content ratings.

        Returns:
            Dict[str, Any]: {"ok": bool, "parental_controls": dict}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        if profile_id not in self.parental_controls:
            self.parental_controls[profile_id] = {}
        
        controls = self.parental_controls[profile_id]
        
        if enabled is not None:
            controls["enabled"] = enabled
        if max_rating is not None:
            controls["max_rating"] = max_rating
        if pin_required is not None:
            controls["pin_required"] = pin_required
        if blocked_content is not None:
            controls["blocked_content"] = blocked_content
        
        return {
            "ok": True,
            "parental_controls": controls
        }

    # ------------------------------------------------------------------
    # viewing_activity.* — viewing history
    # ------------------------------------------------------------------

    def viewing_activity_list(self, profile_id: str, *, limit: int = 50) -> Dict[str, Any]:
        """
        Get viewing activity for a profile.

        Args:
            profile_id: ID of the profile.
            limit: Maximum number of entries to return.

        Returns:
            Dict[str, Any]: {"ok": bool, "viewing_activity": list}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        activity = self.viewing_activity.get(profile_id, [])
        
        return {
            "ok": True,
            "viewing_activity": activity[:limit]
        }

    def viewing_activity_add(self, profile_id: str, content_id: str, 
                           duration_watched: int, *, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Add viewing activity entry.

        Args:
            profile_id: ID of the profile.
            content_id: ID of the watched content.
            duration_watched: Duration watched in minutes.
            device_id: ID of the device used.

        Returns:
            Dict[str, Any]: {"ok": bool, "activity": dict}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        if profile_id not in self.viewing_activity:
            self.viewing_activity[profile_id] = []
        
        activity_entry = {
            "content_id": content_id,
            "title": f"Content {content_id}",
            "type": "movie" if content_id.startswith("M") else "series",
            "watched_at": int(time.time()),
            "duration_watched": duration_watched,
            "device": device_id or "unknown"
        }
        
        self.viewing_activity[profile_id].append(activity_entry)
        
        return {
            "ok": True,
            "activity": activity_entry
        }

    def viewing_activity_clear(self, profile_id: str) -> Dict[str, Any]:
        """
        Clear viewing activity for a profile.

        Args:
            profile_id: ID of the profile.

        Returns:
            Dict[str, Any]: {"ok": bool, "cleared_entries": int}
        """
        if profile_id not in self.profiles:
            return {"ok": False, "error": "profile_not_found"}
        
        cleared_count = len(self.viewing_activity.get(profile_id, []))
        self.viewing_activity[profile_id] = []
        
        return {
            "ok": True,
            "cleared_entries": cleared_count
        }
