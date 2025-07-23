from copy import deepcopy
from typing import Dict, List, Optional

DEFAULT_STATE = {
    "posts": {
        "post1": {
            "id": "post1",
            "text": "This is the first post.",
            "author_id": "user1",
            "likes": ["user2"],
            "metrics": {"views": 100, "likes": 1},
        },
        "post2": {
            "id": "post2",
            "text": "Hello world from user2!",
            "author_id": "user2",
            "likes": ["user1"],
            "metrics": {"views": 50, "likes": 1},
        },
        "post3": {
            "id": "post3",
            "text": "A third post for testing.",
            "author_id": "user1",
            "likes": [],
            "metrics": {"views": 20, "likes": 0},
        },
    },
    "users": {
        "user1": {
            "id": "user1",
            "username": "alice_x",
            "name": "Alice X",
            "liked_posts": ["post2"],
            "posts": ["post1", "post3"]
        },
        "user2": {
            "id": "user2",
            "username": "bob_x",
            "name": "Bob X",
            "liked_posts": ["post1"],
            "posts": ["post2"]
        },
    },
    "direct_messages": {
        "dm_conv_1": {
            "id": "dm_conv_1",
            "participants": ["user1", "user2"],
            "messages": [
                {"sender_id": "user1", "text": "Hi Bob!"},
                {"sender_id": "user2", "text": "Hey Alice!"},
            ],
        }
    },
    "filtered_stream_rules": [
        {"value": "test rule", "tag": "general"},
    ],
    "community_notes": {
        "note1": {
            "id": "note1",
            "tweet_id": "post1",
            "text": "This note clarifies the first post.",
            "tags": ["clarification"],
        }
    },
    "api_usage": {
        "requests_made": 10,
        "data_transferred_mb": 2.5,
    },
}


class XApis:
    def __init__(self):
        self.posts: Dict[str, Dict] = {}
        self.users: Dict[str, Dict] = {}
        self.direct_messages: Dict[str, Dict] = {}
        self.filtered_stream_rules: List[Dict] = []
        self.community_notes: Dict[str, Dict] = {}
        self.api_usage: Dict = {}
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
        self.direct_messages = scenario.get("direct_messages", DEFAULT_STATE_COPY["direct_messages"])
        self.filtered_stream_rules = scenario.get("filtered_stream_rules", DEFAULT_STATE_COPY["filtered_stream_rules"])
        self.community_notes = scenario.get("community_notes", DEFAULT_STATE_COPY["community_notes"])
        self.api_usage = scenario.get("api_usage", DEFAULT_STATE_COPY["api_usage"])

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
        new_conv_id = f"dm_conv_{len(self.direct_messages) + 1}"
        new_conversation = {
            "id": new_conv_id,
            "participants": participant_ids,
            "messages": [{"sender_id": participant_ids[0], "text": message_text}]  # Assuming first participant sends
        }
        self.direct_messages[new_conv_id] = new_conversation
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
        # In a dummy backend, we'll find an existing conversation or create a new one.
        for conv_id, conv in self.direct_messages.items():
            if user_id in conv["participants"]:
                conv["messages"].append({"sender_id": "current_user_dummy", "text": message_text})
                return {"data": {"conversation_id": conv_id, "message_text": message_text}}

        # If no existing conversation, create a new one (assuming current_user_dummy is the sender)
        new_conv_id = f"dm_conv_{len(self.direct_messages) + 1}"
        new_conversation = {
            "id": new_conv_id,
            "participants": ["current_user_dummy", user_id],
            "messages": [{"sender_id": "current_user_dummy", "text": message_text}]
        }
        self.direct_messages[new_conv_id] = new_conversation
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
        if conversation_id in self.direct_messages:
            self.direct_messages[conversation_id]["messages"].append({"sender_id": "current_user_dummy", "text": message_text})
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
        if conversation_id in self.direct_messages:
            return {"data": self.direct_messages[conversation_id]["messages"][-max_results:]}
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
        all_dm_events = []
        for conv_id, conv in self.direct_messages.items():
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
        eligible_posts = []
        for post_id, post in self.posts.items():
            if query.lower() in post["text"].lower():
                eligible_posts.append(post)
        return {"data": eligible_posts[:max_results]}

    def search_written_community_notes(self, query: str, max_results: Optional[int] = 10) -> Dict:
        """
        Search for Community Notes written by contributors.

        Parameters:
            query (str):
                Search query.
            max_results (Optional[int]):
                Number of results to return (10-100).

        Returns:
            Dict:
                Dictionary containing Community Notes.
        """
        found_notes = []
        for note_id, note in self.community_notes.items():
            if query.lower() in note["text"].lower():
                found_notes.append(note)
        return {"data": found_notes[:max_results]}

    def create_community_note(self, post_id: str, note_text: str, tags: Optional[List[str]] = None) -> Dict:
        """
        Create a new Community Note.

        Parameters:
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
        if post_id in self.posts:
            new_note_id = f"note{len(self.community_notes) + 1}"
            new_note = {
                "id": new_note_id,
                "tweet_id": post_id,
                "text": note_text,
                "tags": tags if tags else []
            }
            self.community_notes[new_note_id] = new_note
            return {"data": new_note}
        return {"data": None, "error": "Post not found"}

    def get_api_usage(self) -> Dict:
        """
        Get current API usage statistics.

        Returns:
            Dict:
                Dictionary containing API usage metrics.
        """
        return {"data": self.api_usage}

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