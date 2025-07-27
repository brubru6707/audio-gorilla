from copy import deepcopy
from typing import Dict, List, Optional, Any

{
    "users": {
        "usr_alice_smith": {
            "id": "usr_alice_smith",
            "username": "alice_smith",
            "name": "Alice Smith",
            "email": "alice.smith@example.com",
            "joined_date": "2023-01-15T10:00:00Z",
            "bio": "Tech enthusiast and amateur photographer. Sharing my thoughts on AI and the digital world.",
            "profile_picture_url": "https://example.com/profiles/alice_smith.jpg",
            "followers": ["usr_john_doe", "usr_emily_white"],
            "following": ["usr_john_doe", "usr_bob_johnson"],
            "liked_posts": ["post_002", "post_005"],
            "posts": ["post_001", "post_004", "post_006"],
            "direct_messages": {
                "dm_conv_alice_john": {
                    "id": "dm_conv_alice_john",
                    "participants": ["usr_alice_smith", "usr_john_doe"],
                    "messages": [
                        {"sender_id": "usr_alice_smith", "text": "Hey John, did you see the latest tech news?"},
                        {"sender_id": "usr_john_doe", "text": "Not yet, Alice! Anything exciting happening?"},
                        {"sender_id": "usr_alice_smith", "text": "Just read about a new AI breakthrough. Pretty wild!"}
                    ]
                }
            },
            "community_notes": {
                "note_alice_001": {
                    "id": "note_alice_001",
                    "tweet_id": "post_001",
                    "text": "This post refers to the recent advancements in quantum computing, not general AI.",
                    "tags": ["clarification", "tech", "quantum_computing"],
                    "created_at": "2024-06-20T14:30:00Z",
                    "upvotes": 15,
                    "downvotes": 2
                }
            },
            "api_usage": {
                "requests_made": 125,
                "data_transferred_mb": 15.3,
                "last_api_call": "2025-07-25T09:45:10Z"
            }
        },
        "usr_john_doe": {
            "id": "usr_john_doe",
            "username": "john_doe_writer",
            "name": "John Doe",
            "email": "john.doe@emailprovider.co.uk",
            "joined_date": "2022-11-01T08:30:00Z",
            "bio": "Writer and coffee enthusiast. Exploring the world one story at a time.",
            "profile_picture_url": "https://example.com/profiles/john_doe.png",
            "followers": ["usr_alice_smith", "usr_bob_johnson"],
            "following": ["usr_alice_smith"],
            "liked_posts": ["post_001"],
            "posts": ["post_002", "post_005"],
            "direct_messages": {
                "dm_conv_alice_john": {
                    "id": "dm_conv_alice_john",
                    "participants": ["usr_alice_smith", "usr_john_doe"],
                    "messages": [
                        {"sender_id": "usr_alice_smith", "text": "Hey John, did you see the latest tech news?"},
                        {"sender_id": "usr_john_doe", "text": "Not yet, Alice! Anything exciting happening?"},
                        {"sender_id": "usr_alice_smith", "text": "Just read about a new AI breakthrough. Pretty wild!"}
                    ]
                },
                "dm_conv_john_bob": {
                    "id": "dm_conv_john_bob",
                    "participants": ["usr_john_doe", "usr_bob_johnson"],
                    "messages": [
                        {"sender_id": "usr_john_doe", "text": "Bob, are you free for a call next week?"},
                        {"sender_id": "usr_bob_johnson", "text": "Yes, John! Tuesday works best for me."}
                    ]
                }
            },
            "community_notes": {},
            "api_usage": {
                "requests_made": 60,
                "data_transferred_mb": 7.8,
                "last_api_call": "2025-07-24T18:00:00Z"
            }
        },
        "usr_emily_white": {
            "id": "usr_emily_white",
            "username": "emily_travels",
            "name": "Emily White",
            "email": "emily.white@travelogue.net",
            "joined_date": "2024-03-20T14:00:00Z",
            "bio": "Wanderlust-filled adventurer sharing my journeys and photography from around the globe.",
            "profile_picture_url": "https://example.com/profiles/emily_white.jpeg",
            "followers": ["usr_alice_smith"],
            "following": ["usr_john_doe"],
            "liked_posts": ["post_004"],
            "posts": [],
            "direct_messages": {},
            "community_notes": {},
            "api_usage": {
                "requests_made": 20,
                "data_transferred_mb": 3.1,
                "last_api_call": "2025-07-23T11:00:00Z"
            }
        },
        "usr_bob_johnson": {
            "id": "usr_bob_johnson",
            "username": "bob_coder",
            "name": "Bob Johnson",
            "email": "bob.johnson@devmail.org",
            "joined_date": "2023-08-01T09:15:00Z",
            "bio": "Software developer by day, open-source contributor by night. Coffee is my fuel.",
            "profile_picture_url": "https://example.com/profiles/bob_johnson.gif",
            "followers": ["usr_john_doe"],
            "following": ["usr_alice_smith"],
            "liked_posts": ["post_006"],
            "posts": ["post_003"],
            "direct_messages": {
                "dm_conv_john_bob": {
                    "id": "dm_conv_john_bob",
                    "participants": ["usr_john_doe", "usr_bob_johnson"],
                    "messages": [
                        {"sender_id": "usr_john_doe", "text": "Bob, are you free for a call next week?"},
                        {"sender_id": "usr_bob_johnson", "text": "Yes, John! Tuesday works best for me."}
                    ]
                }
            },
            "community_notes": {},
            "api_usage": {
                "requests_made": 90,
                "data_transferred_mb": 10.5,
                "last_api_call": "2025-07-25T08:00:00Z"
            }
        }
    },
    "posts": {
        "post_001": {
            "id": "post_001",
            "text": "Just attended an amazing webinar on the future of AI in healthcare! So many exciting possibilities. #AI #Healthcare #Innovation",
            "author_id": "usr_alice_smith",
            "created_at": "2025-07-25T09:00:00Z",
            "likes": ["usr_john_doe", "usr_emily_white"],
            "comments": [
                {"comment_id": "comment_001_1", "user_id": "usr_john_doe", "text": "Sounds fascinating! Any key takeaways you can share?"}
            ],
            "metrics": {"views": 520, "likes": 25, "reposts": 8, "comments": 1},
            "tags": ["AI", "Healthcare", "Innovation"]
        },
        "post_002": {
            "id": "post_002",
            "text": "My latest short story, 'The Midnight Whisper,' is now available on my blog! Let me know what you think. Link in bio.",
            "author_id": "usr_john_doe",
            "created_at": "2025-07-24T15:30:00Z",
            "likes": ["usr_alice_smith"],
            "comments": [],
            "metrics": {"views": 310, "likes": 18, "reposts": 3, "comments": 0},
            "tags": ["Writing", "ShortStory", "Fiction"]
        },
        "post_003": {
            "id": "post_003",
            "text": "Debugging a tricky algorithm today. The joys of software development! Any tips for optimizing recursive functions?",
            "author_id": "usr_bob_johnson",
            "created_at": "2025-07-25T11:00:00Z",
            "likes": ["usr_alice_smith"],
            "comments": [
                {"comment_id": "comment_003_1", "user_id": "usr_alice_smith", "text": "Have you tried memoization or dynamic programming?"}
            ],
            "metrics": {"views": 180, "likes": 10, "reposts": 2, "comments": 1},
            "tags": ["Coding", "SoftwareDevelopment", "Debugging"]
        },
        "post_004": {
            "id": "post_004",
            "text": "Breathtaking sunset over the Grand Canyon yesterday! Nature truly is the best artist. #Travel #Photography #GrandCanyon",
            "author_id": "usr_alice_smith",
            "created_at": "2025-07-23T18:45:00Z",
            "likes": ["usr_emily_white"],
            "comments": [
                {"comment_id": "comment_004_1", "user_id": "usr_emily_white", "text": "Absolutely stunning! I was there last year, such an incredible place."}
            ],
            "metrics": {"views": 750, "likes": 40, "reposts": 15, "comments": 1},
            "tags": ["Travel", "Photography", "GrandCanyon", "Nature"]
        },
        "post_005": {
            "id": "post_005",
            "text": "Working on a new non-fiction piece about the history of cryptography. Fascinating how ancient codes still influence modern security. #History #Cryptography #Research",
            "author_id": "usr_john_doe",
            "created_at": "2025-07-22T10:00:00Z",
            "likes": [],
            "comments": [],
            "metrics": {"views": 200, "likes": 12, "reposts": 5, "comments": 0},
            "tags": ["History", "Cryptography", "Security"]
        },
        "post_006": {
            "id": "post_006",
            "text": "Just set up my new dev environment with the latest Linux distribution. Loving the workflow improvements! #Linux #DevOps #Productivity",
            "author_id": "usr_alice_smith",
            "created_at": "2025-07-25T10:30:00Z",
            "likes": ["usr_bob_johnson"],
            "comments": [],
            "metrics": {"views": 300, "likes": 20, "reposts": 7, "comments": 0},
            "tags": ["Linux", "DevOps", "Tech"]
        }
    },
    "filtered_stream_rules": [
        {"value": "AI OR Healthcare", "tag": "tech_health"},
        {"value": "Photography OR Travel", "tag": "hobbies"},
        {"value": "Writing OR Fiction", "tag": "literature"}
    ],
    "system_status": {
        "last_updated": "2025-07-25T10:19:18Z",
        "api_health": "operational",
        "database_connection": "stable"
    }
}


class XApis:
    def __init__(self):
        self.posts: Dict[str, Dict] = {}
        self.users: Dict[str, Dict] = {}
        self.filtered_stream_rules: List[Dict] = []
        # direct_messages, community_notes, api_usage will now be nested under users
        self._api_description = "This tool belongs to the XApis, which provides functionality for searching posts, managing direct messages, and interacting with community notes."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: dict) -> None:
        """
        Loads the internal state of the API with a given scenario.

        Parameters:
            scenario (dict):
                The dictionary containing the state to load.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.posts = scenario.get("posts", DEFAULT_STATE_COPY["posts"])
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.filtered_stream_rules = scenario.get("filtered_stream_rules", DEFAULT_STATE_COPY["filtered_stream_rules"])
        # No longer loading direct_messages, community_notes, api_usage directly here as they are nested

    def _get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user-specific data.
        """
        return self.users.get(user_id)

    def search_posts_full_archive(self, query: str, max_results: Optional[int] = 10) -> Dict:
        """
        Search across the complete history of public posts matching a query.

        Parameters:
            query (str):
                Search query (up to 1024 characters).
            max_results (Optional[int]):
                Number of results to return (10-500).

        Returns:
            Dict:
                Dictionary containing posts matching the query and pagination info.
        """
        results = []
        for post_id, post in self.posts.items():
            if query.lower() in post["text"].lower():
                results.append(post)
        return {"data": results[:max_results], "meta": {"result_count": len(results)}}

    def search_posts_recent(self, query: str, max_results: Optional[int] = 10) -> Dict:
        """
        Search recent posts (last 7 days) matching a query.

        Parameters:
            query (str):
                Search query (up to 512 characters).
            max_results (Optional[int]):
                Number of results to return (10-100).

        Returns:
            Dict:
                Dictionary containing recent posts matching the query and pagination info.
        """
        results = []
        for post_id, post in self.posts.items():
            if query.lower() in post["text"].lower():
                results.append(post)
        return {"data": results[:max_results], "meta": {"result_count": len(results)}}

    def get_full_archive_search_counts(self, query: str, start_time: Optional[str] = None,
                                       end_time: Optional[str] = None) -> Dict:
        """
        Get count of posts matching query across complete history.

        Parameters:
            query (str):
                Search query (up to 1024 characters).
            start_time (Optional[str]):
                Oldest UTC timestamp (YYYY-MM-DDTHH:mm:ssZ).
            end_time (Optional[str]):
                Newest UTC timestamp (YYYY-MM-DDTHH:mm:ssZ).

        Returns:
            Dict:
                Dictionary containing counts of posts matching the query.
        """
        count = 0
        for post_id, post in self.posts.items():
            if query.lower() in post["text"].lower():
                count += 1
        return {"data": [{"count": count, "start": start_time, "end": end_time}]}

    def get_recent_search_counts(self, query: str, start_time: Optional[str] = None,
                                 end_time: Optional[str] = None) -> Dict:
        """
        Get count of recent posts (last 7 days) matching query.

        Parameters:
            query (str):
                Search query (up to 512 characters).
            start_time (Optional[str]):
                Oldest UTC timestamp (YYYY-MM-DDTHH:mm:ssZ).
            end_time (Optional[str]):
                Newest UTC timestamp (YYYY-MM-DDTHH:mm:ssZ).

        Returns:
            Dict:
                Dictionary containing counts of recent posts matching the query.
        """
        count = 0
        for post_id, post in self.posts.items():
            if query.lower() in post["text"].lower():
                count += 1
        return {"data": [{"count": count, "start": start_time, "end": end_time}]}

    def create_post(self, user_id: str, text: str, reply_settings: Optional[str] = None) -> Dict:
        """
        Create a new post on behalf of a user.

        Parameters:
            user_id (str): User ID creating the post
            text (str): Text content of the post
            reply_settings (Optional[str]): Who can reply to the post

        Returns:
            Dict: Dictionary containing the created post details
        """
        if user_id not in self.users:
            return {"data": None, "error": "User not found"}
        
        new_post_id = f"post{len(self.posts) + 1}"
        new_post = {
            "id": new_post_id,
            "text": text,
            "author_id": user_id,
            "likes": [],
            "metrics": {"views": 0, "likes": 0},
            "reply_settings": reply_settings or "everyone"
        }
        self.posts[new_post_id] = new_post
        self.users[user_id].setdefault("posts", []).append(new_post_id)
        return {"data": new_post}

    def delete_post(self, user_id: str, post_id: str) -> Dict:
        """
        Delete a post on behalf of a user.

        Parameters:
            user_id (str): User ID deleting the post
            post_id (str): Post ID to delete

        Returns:
            Dict: Dictionary containing deletion status
        """
        if post_id not in self.posts:
            return {"deleted": False, "error": "Post not found"}
        
        if self.posts[post_id]["author_id"] != user_id:
            return {"deleted": False, "error": "User not authorized"}
        
        # Remove from user's posts
        author_id = self.posts[post_id]["author_id"]
        if post_id in self.users[author_id].get("posts", []):
            self.users[author_id]["posts"].remove(post_id)
        
        # Remove from likes
        for user in self.users.values():
            if post_id in user.get("liked_posts", []):
                user["liked_posts"].remove(post_id)
        
        # Remove from community notes if exists (now specific to users)
        for user_id_iter, user_data in self.users.items():
            notes_to_delete = [nid for nid, note in user_data.get("community_notes", {}).items() if note["tweet_id"] == post_id]
            for nid in notes_to_delete:
                del user_data["community_notes"][nid]
        
        del self.posts[post_id]
        return {"deleted": True}

    def get_posts_by_ids(self, post_ids: List[str]) -> Dict:
        """
        Get multiple posts by their IDs.

        Parameters:
            post_ids (List[str]):
                List of post IDs (up to 100).

        Returns:
            Dict:
                Dictionary containing requested posts and related data.
        """
        found_posts = []
        for post_id in post_ids:
            if post_id in self.posts:
                found_posts.append(self.posts[post_id])
        return {"data": found_posts}

    def get_post_by_id(self, post_id: str) -> Dict:
        """
        Get a single post by its ID.

        Parameters:
            post_id (str):
                Post ID.

        Returns:
            Dict:
                Dictionary containing the requested post and related data.
        """
        if post_id in self.posts:
            return {"data": self.posts[post_id]}
        return {"data": None}

    def get_user_posts_timeline(self, user_id: str, max_results: Optional[int] = 10) -> Dict:
        """
        Get the timeline of posts for a specific user.

        Parameters:
            user_id (str):
                User ID whose timeline to retrieve.
            max_results (Optional[int]):
                Number of results to return (10-100).

        Returns:
            Dict:
                Dictionary containing the user's posts timeline.
        """
        user_posts = []
        if user_id in self.users:
            for post_id in self.users[user_id].get("posts", []):
                if post_id in self.posts:
                    user_posts.append(self.posts[post_id])
        return {"data": user_posts[:max_results]}

    def get_user_mentions_timeline(self, user_id: str, max_results: Optional[int] = 10) -> Dict:
        """
        Get the timeline of mentions for a specific user.

        Parameters:
            user_id (str):
                User ID whose mentions to retrieve.
            max_results (Optional[int]):
                Number of results to return (10-100).

        Returns:
            Dict:
                Dictionary containing the user's mentions timeline.
        """
        mentions = []
        for post_id, post in self.posts.items():
            if f"@{self.users.get(user_id, {}).get('username', '')}" in post["text"]:
                mentions.append(post)
        return {"data": mentions[:max_results]}

    def get_user_home_timeline(self, user_id: str, max_results: Optional[int] = 10) -> Dict:
        """
        Get the home timeline for a specific user.

        Parameters:
            user_id (str):
                User ID whose home timeline to retrieve.
            max_results (Optional[int]):
                Number of results to return (10-100).

        Returns:
            Dict:
                Dictionary containing the user's home timeline.
        """
        # In a dummy backend, we'll return all posts as a simplified "home timeline"
        # A real implementation would involve following/follower logic.
        all_posts = list(self.posts.values())
        return {"data": all_posts[:max_results]}

    def create_dm_conversation(self, participant_ids: List[str], message_text: str) -> Dict:
        """
        Create a new DM conversation.

        Parameters:
            participant_ids (List[str]):
                List of user IDs to include in the conversation.
            message_text (str):
                Text of the initial message.

        Returns:
            Dict:
                Dictionary containing the new conversation details.
        """
        # Assuming the first participant is the initiator and their direct_messages will store it.
        if not participant_ids or participant_ids[0] not in self.users:
            return {"data": None, "error": "Initiating user not found"}

        user_dms = self.users[participant_ids[0]].setdefault("direct_messages", {})
        new_conv_id = f"dm_conv_{len(user_dms) + 1}"
        new_conversation = {
            "id": new_conv_id,
            "participants": participant_ids,
            "messages": [{"sender_id": participant_ids[0], "text": message_text}]
        }
        user_dms[new_conv_id] = new_conversation
        return {"data": new_conversation}

    def send_dm_to_user(self, user_id: str, message_text: str) -> Dict:
        """
        Send a direct message to a specific user.

        Parameters:
            user_id (str):
                User ID to send the message to.
            message_text (str):
                Text of the message.

        Returns:
            Dict:
                Dictionary containing the sent message details.
        """
        # This function assumes a "current_user_dummy" for simplicity.
        # In a real scenario, this would be the authenticated user.
        current_user_id = "user1" # Arbitrarily picking user1 as the sender for this dummy function
        if current_user_id not in self.users or user_id not in self.users:
            return {"data": None, "error": "One or both users not found"}

        user_dms = self.users[current_user_id].setdefault("direct_messages", {})

        # Try to find an existing conversation
        found_conv_id = None
        for conv_id, conv in user_dms.items():
            if user_id in conv["participants"] and current_user_id in conv["participants"]:
                found_conv_id = conv_id
                break

        if found_conv_id:
            user_dms[found_conv_id]["messages"].append({"sender_id": current_user_id, "text": message_text})
            return {"data": {"conversation_id": found_conv_id, "message_text": message_text}}
        else:
            # If no existing conversation, create a new one
            new_conv_id = f"dm_conv_{len(user_dms) + 1}"
            new_conversation = {
                "id": new_conv_id,
                "participants": [current_user_id, user_id],
                "messages": [{"sender_id": current_user_id, "text": message_text}]
            }
            user_dms[new_conv_id] = new_conversation
            return {"data": {"conversation_id": new_conv_id, "message_text": message_text}}

    def send_dm_to_conversation(self, conversation_id: str, message_text: str) -> Dict:
        """
        Send a direct message to an existing conversation.

        Parameters:
            conversation_id (str):
                Conversation ID to send the message to.
            message_text (str):
                Text of the message.

        Returns:
            Dict:
                Dictionary containing the sent message details.
        """
        # This function assumes a "current_user_dummy" for simplicity.
        # In a real scenario, this would be the authenticated user.
        current_user_id = "user1" # Arbitrarily picking user1 as the sender for this dummy function
        if current_user_id not in self.users:
            return {"data": None, "error": "User not found"}

        user_dms = self.users[current_user_id].setdefault("direct_messages", {})

        if conversation_id in user_dms:
            user_dms[conversation_id]["messages"].append({"sender_id": current_user_id, "text": message_text})
            return {"data": {"conversation_id": conversation_id, "message_text": message_text}}
        return {"data": None, "error": "Conversation not found"}

    def get_dm_events(self, conversation_id: str, max_results: Optional[int] = 50) -> Dict:
        """
        Get DM events for a specific conversation.

        Parameters:
            conversation_id (str):
                Conversation ID to retrieve messages from.
            max_results (Optional[int]):
                Number of results to return (1-50).

        Returns:
            Dict:
                Dictionary containing DM events for the conversation.
        """
        # This function assumes a "current_user_dummy" for simplicity.
        current_user_id = "user1" # Arbitrarily picking user1 as the sender for this dummy function
        if current_user_id not in self.users:
            return {"data": None, "error": "User not found"}

        user_dms = self.users[current_user_id].setdefault("direct_messages", {})

        if conversation_id in user_dms:
            return {"data": user_dms[conversation_id]["messages"][-max_results:]}
        return {"data": None, "error": "Conversation not found"}

    def get_recent_dm_events(self, max_results: Optional[int] = 50) -> Dict:
        """
        Get recent DM events across all conversations.

        Parameters:
            max_results (Optional[int]):
                Number of results to return (1-50).

        Returns:
            Dict:
                Dictionary containing recent DM events.
        """
        # This function assumes a "current_user_dummy" for simplicity.
        current_user_id = "user1" # Arbitrarily picking user1 as the sender for this dummy function
        if current_user_id not in self.users:
            return {"data": None, "error": "User not found"}

        user_dms = self.users[current_user_id].setdefault("direct_messages", {})

        all_dm_events = []
        for conv_id, conv in user_dms.items():
            all_dm_events.extend(conv["messages"])
        return {"data": all_dm_events[-max_results:]}

    def get_liked_posts(self, user_id: str, max_results: Optional[int] = 10) -> Dict:
        """
        Get posts liked by a specific user.

        Parameters:
            user_id (str):
                User ID whose likes to retrieve.
            max_results (Optional[int]):
                Number of results to return (10-100).

        Returns:
            Dict:
                Dictionary containing posts liked by the user.
        """
        liked_posts = []
        if user_id in self.users:
            for post_id in self.users[user_id].get("liked_posts", []):
                if post_id in self.posts:
                    liked_posts.append(self.posts[post_id])
        return {"data": liked_posts[:max_results]}

    def get_post_likes(self, post_id: str, max_results: Optional[int] = 10) -> Dict:
        """
        Get users who liked a specific post.

        Parameters:
            post_id (str):
                Post ID to retrieve likers for.
            max_results (Optional[int]):
                Number of results to return (10-100).

        Returns:
            Dict:
                Dictionary containing users who liked the post.
        """
        liking_users = []
        if post_id in self.posts:
            for user_id in self.posts[post_id].get("likes", []):
                if user_id in self.users:
                    liking_users.append(self.users[user_id])
        return {"data": liking_users[:max_results]}

    def like_post(self, user_id: str, post_id: str) -> Dict:
        """
        Like a post on behalf of a user.

        Parameters:
            user_id (str):
                User ID who is liking the post.
            post_id (str):
                Post ID to like.

        Returns:
            Dict:
                Dictionary containing the like status.
        """
        if user_id in self.users and post_id in self.posts:
            if user_id not in self.posts[post_id]["likes"]:
                self.posts[post_id]["likes"].append(user_id)
                self.posts[post_id]["metrics"]["likes"] += 1
                self.users[user_id].setdefault("liked_posts", []).append(post_id)
                return {"liked": True}
            return {"liked": False, "reason": "Already liked"}
        return {"liked": False, "reason": "User or post not found"}

    def unlike_post(self, user_id: str, post_id: str) -> Dict:
        """
        Remove a like from a post on behalf of a user.

        Parameters:
            user_id (str):
                User ID who is unliking the post.
            post_id (str):
                Post ID to unlike.

        Returns:
            Dict:
                Dictionary containing the unlike status.
        """
        if user_id in self.users and post_id in self.posts:
            if user_id in self.posts[post_id]["likes"]:
                self.posts[post_id]["likes"].remove(user_id)
                self.posts[post_id]["metrics"]["likes"] -= 1
                if post_id in self.users[user_id].get("liked_posts", []):
                    self.users[user_id]["liked_posts"].remove(post_id)
                return {"unliked": True}
            return {"unliked": False, "reason": "Not liked yet"}
        return {"unliked": False, "reason": "User or post not found"}

    def search_eligible_community_notes(self, query: str, max_results: Optional[int] = 10) -> Dict:
        """
        Search for posts eligible for Community Notes.

        Parameters:
            query (str):
                Search query.
            max_results (Optional[int]):
                Number of results to return (10-100).

        Returns:
            Dict:
                Dictionary containing eligible posts.
        """
        # This function now returns all posts matching the query, as eligibility
        # for community notes isn't explicitly defined in this dummy backend beyond text content.
        eligible_posts = []
        for post_id, post in self.posts.items():
            if query.lower() in post["text"].lower():
                eligible_posts.append(post)
        return {"data": eligible_posts[:max_results]}

    def search_written_community_notes(self, user_id: str, query: str, max_results: Optional[int] = 10) -> Dict:
        """
        Search for Community Notes written by contributors.

        Parameters:
            user_id (str):
                User ID whose community notes to search.
            query (str):
                Search query.
            max_results (Optional[int]):
                Number of results to return (10-100).

        Returns:
            Dict:
                Dictionary containing Community Notes.
        """
        if user_id not in self.users:
            return {"data": None, "error": "User not found"}
        
        user_notes = self.users[user_id].get("community_notes", {})
        found_notes = []
        for note_id, note in user_notes.items():
            if query.lower() in note["text"].lower():
                found_notes.append(note)
        return {"data": found_notes[:max_results]}

    def create_community_note(self, user_id: str, post_id: str, note_text: str, tags: Optional[List[str]] = None) -> Dict:
        """
        Create a new Community Note.

        Parameters:
            user_id (str):
                User ID creating the note.
            post_id (str):
                Post ID to attach the note to.
            note_text (str):
                Text of the note.
            tags (Optional[List[str]]):
                Optional tags for the note.

        Returns:
            Dict:
                Dictionary containing created note details.
        """
        if user_id not in self.users:
            return {"data": None, "error": "User not found"}
        
        if post_id not in self.posts:
            return {"data": None, "error": "Post not found"}
        
        user_notes = self.users[user_id].setdefault("community_notes", {})
        new_note_id = f"note{len(user_notes) + 1}"
        new_note = {
            "id": new_note_id,
            "tweet_id": post_id,
            "text": note_text,
            "tags": tags if tags else []
        }
        user_notes[new_note_id] = new_note
        return {"data": new_note}

    def get_api_usage(self, user_id: str) -> Dict:
        """
        Get current API usage statistics for a specific user.

        Parameters:
            user_id (str):
                User ID to retrieve API usage for.

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
                List of post IDs to get metrics for.
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
                        post_metrics.append({"tweet_id": post_id, "metrics": filtered_metrics})
                    else:
                        post_metrics.append({"tweet_id": post_id, "metrics": post["metrics"]})
        return {"data": post_metrics}