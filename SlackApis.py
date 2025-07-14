from typing import Any, Dict, Optional, List
import time
import uuid


class SlackAPI:
    """
    Slim Slack Web API mock backend for voice-assistant scenarios.

    This class exposes only the Slack methods likely to be used by a large-language-model (LLM)
    responding to spoken commands, and maintains in-memory state for all relevant Slack objects.
    """

    def __init__(self, token: Optional[str] = None) -> None:
        """
        Create a new SlackVoiceAPI instance with mock state.

        Args:
            token: Slack OAuth token (bot or user). Store if you need it later.
        """
        self.token = token
        # State variables
        self.channels: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.messages: List[Dict[str, Any]] = []
        self.threads: Dict[str, List[Dict[str, Any]]] = {}
        self.reminders: Dict[str, Dict[str, Any]] = {}
        self.files: Dict[str, Dict[str, Any]] = {}
        self.reactions: Dict[str, List[Dict[str, Any]]] = {}
        self.pins: Dict[str, List[str]] = {}
        self.dnd: Dict[str, Dict[str, Any]] = {}
        self.emoji: Dict[str, str] = {}
        self.team_info: Dict[str, Any] = {"id": "T123", "name": "Mock Team"}
        self.scheduled_messages: Dict[str, Dict[str, Any]] = {}
        # Initialize with sample data
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """
        Populate the mock backend with some sample users, channels, and messages.
        """
        self.users = {
            "U001": {"id": "U001", "name": "alice", "real_name": "Alice Example", "email": "alice@example.com"},
            "U002": {"id": "U002", "name": "bob", "real_name": "Bob Example", "email": "bob@example.com"},
        }
        self.channels = {
            "C001": {"id": "C001", "name": "general", "is_channel": True, "topic": "General discussion", "purpose": "General workspace discussion"},
            "C002": {"id": "C002", "name": "random", "is_channel": True, "topic": "Random stuff", "purpose": "Random conversations"},
        }
        self.messages = []
        self.threads = {}
        self.reminders = {}
        self.files = {}
        self.reactions = {}
        self.pins = {"C001": [], "C002": []}
        self.dnd = {"U001": {"dnd_enabled": False}, "U002": {"dnd_enabled": False}}
        self.emoji = {":smile:": "https://emoji.url/smile.png", ":thumbsup:": "https://emoji.url/thumbsup.png"}
        self.team_info = {"id": "T123", "name": "Mock Team", "domain": "mockteam"}
        self.scheduled_messages = {}

    # ------------------------------------------------------------------
    # chat.* — basic messaging actions
    # ------------------------------------------------------------------

    def chat_postMessage(self, channel: str, text: str, *, blocks: Optional[list] = None,
                         attachments: Optional[list] = None, thread_ts: Optional[str] = None,
                         username: Optional[str] = None, icon_url: Optional[str] = None,
                         icon_emoji: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to a channel or user.

        Args:
            channel: ID of the channel, DM, or IM to post to.
            text: Plain-text body of the message.
            blocks: Optional rich-layout *blocks* structure.
            attachments: Optional legacy attachments.
            thread_ts: If provided, posts the message as a thread reply.
            username: Override the bot/user display name.
            icon_url: Override the bot/user avatar URL.
            icon_emoji: Override the bot/user avatar with an emoji.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "channel": str, "ts": str, "message": dict}``
        """
        ts = str(time.time())
        message = {
            "type": "message",
            "user": "U001",  # Mock user
            "text": text,
            "ts": ts,
            "channel": channel,
            "blocks": blocks,
            "attachments": attachments,
            "thread_ts": thread_ts,
            "username": username,
            "icon_url": icon_url,
            "icon_emoji": icon_emoji
        }
        
        self.messages.append(message)
        
        if thread_ts:
            if thread_ts not in self.threads:
                self.threads[thread_ts] = []
            self.threads[thread_ts].append(message)
        
        return {
            "ok": True,
            "channel": channel,
            "ts": ts,
            "message": message
        }

    def chat_postEphemeral(self, channel: str, user: str, text: str, *,
                           blocks: Optional[list] = None, attachments: Optional[list] = None) -> Dict[str, Any]:
        """
        Send an ephemeral message visible only to a specific user.

        Args:
            channel: Channel in which to post the ephemeral message.
            user: Recipient user ID.
            text: Fallback text of the message.
            blocks: Optional Block Kit layout.
            attachments: Optional legacy attachments.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "message_ts": str}``
        """
        ts = str(time.time())
        message = {
            "type": "ephemeral",
            "user": user,
            "text": text,
            "ts": ts,
            "channel": channel,
            "blocks": blocks,
            "attachments": attachments
        }
        
        self.messages.append(message)
        
        return {
            "ok": True,
            "message_ts": ts
        }

    def chat_update(self, channel: str, ts: str, text: str, *, blocks: Optional[list] = None,
                    attachments: Optional[list] = None) -> Dict[str, Any]:
        """
        Update an existing message.

        Args:
            channel: Channel containing the message.
            ts: Timestamp of the message to update.
            text: New text.
            blocks: Optional new blocks.
            attachments: Optional new attachments.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "ts": str, "channel": str, "message": dict}``
        """
        # Find and update the message
        for message in self.messages:
            if message.get("ts") == ts and message.get("channel") == channel:
                message["text"] = text
                if blocks is not None:
                    message["blocks"] = blocks
                if attachments is not None:
                    message["attachments"] = attachments
                return {
                    "ok": True,
                    "ts": ts,
                    "channel": channel,
                    "message": message
                }
        
        return {"ok": False, "error": "message_not_found"}

    def chat_delete(self, channel: str, ts: str) -> Dict[str, Any]:
        """
        Delete a message.

        Args:
            channel: Channel containing the message.
            ts: Timestamp of the message to delete.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "channel": str, "ts": str}``
        """
        # Remove message from messages list
        self.messages = [msg for msg in self.messages if not (msg.get("ts") == ts and msg.get("channel") == channel)]
        
        # Remove from threads if it's a thread message
        for thread_ts in self.threads:
            self.threads[thread_ts] = [msg for msg in self.threads[thread_ts] if not (msg.get("ts") == ts and msg.get("channel") == channel)]
        
        return {
            "ok": True,
            "channel": channel,
            "ts": ts
        }

    def chat_scheduleMessage(self, channel: str, post_at: int, text: str, *,
                             blocks: Optional[list] = None, attachments: Optional[list] = None) -> Dict[str, Any]:
        """
        Schedule a message to post at a specific Unix timestamp.

        Args:
            channel: Destination channel.
            post_at: Future Unix timestamp at which to post.
            text: Fallback text.
            blocks: Optional blocks.
            attachments: Optional attachments.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "scheduled_message_id": str, "post_at": int}``
        """
        scheduled_message_id = f"scheduled_{uuid.uuid4().hex[:8]}"
        
        self.scheduled_messages[scheduled_message_id] = {
            "id": scheduled_message_id,
            "channel": channel,
            "post_at": post_at,
            "text": text,
            "blocks": blocks,
            "attachments": attachments,
            "user": "U001"  # Mock user
        }
        
        return {
            "ok": True,
            "scheduled_message_id": scheduled_message_id,
            "post_at": post_at
        }

    def chat_deleteScheduledMessage(self, channel: str, scheduled_message_id: str) -> Dict[str, Any]:
        """
        Cancel a scheduled message.

        Args:
            channel: Channel where the message would be sent.
            scheduled_message_id: ID returned by :py:meth:`chat_scheduleMessage`.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        if scheduled_message_id in self.scheduled_messages:
            del self.scheduled_messages[scheduled_message_id]
            return {"ok": True}
        
        return {"ok": False, "error": "scheduled_message_not_found"}

    def chat_scheduledMessages_list(self, channel: str, *, limit: int = 100) -> Dict[str, Any]:
        """
        List scheduled messages for a channel.

        Args:
            channel: Channel to check.
            limit: Maximum number of entries to return.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "scheduled_messages": list}``
        """
        channel_messages = [
            msg for msg in self.scheduled_messages.values()
            if msg["channel"] == channel
        ][:limit]
        
        return {
            "ok": True,
            "scheduled_messages": channel_messages
        }

    def chat_getPermalink(self, channel: str, message_ts: str) -> Dict[str, Any]:
        """
        Retrieve a permalink for a message.

        Args:
            channel: Channel containing the message.
            message_ts: Timestamp of the message.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "permalink": str}``
        """
        # Check if message exists
        message_exists = any(
            msg.get("ts") == message_ts and msg.get("channel") == channel
            for msg in self.messages
        )
        
        if message_exists:
            permalink = f"https://mockteam.slack.com/archives/{channel}/p{message_ts.replace('.', '')}"
            return {
                "ok": True,
                "permalink": permalink
            }
        
        return {"ok": False, "error": "message_not_found"}

    # ------------------------------------------------------------------
    # conversations.* — channel & DM management / retrieval
    # ------------------------------------------------------------------

    def conversations_list(self, *, types: str = "public_channel,private_channel,im,mpim", limit: int = 100, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Lists visible conversations.

        Args:
            types: Comma-separated list of conversation types to include.
            limit: Maximum number of items to return.
            cursor: Pagination cursor from a previous call.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "channels": list, "response_metadata": dict}``
        """
        channels_list = list(self.channels.values())[:limit]
        
        return {
            "ok": True,
            "channels": channels_list,
            "response_metadata": {
                "next_cursor": None if len(channels_list) < limit else "next_page_token"
            }
        }

    def conversations_open(self, users: str, *, return_im: bool = False) -> Dict[str, Any]:
        """
        Open a DM or MPDM with the specified users.

        Args:
            users: Comma-separated user IDs to include.
            return_im: If True, also return the IM object for 1-on-1 DMs.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "channel": dict}``
        """
        user_list = users.split(",")
        channel_id = f"D{uuid.uuid4().hex[:8]}"
        
        channel = {
            "id": channel_id,
            "is_im": len(user_list) == 1,
            "is_mpim": len(user_list) > 1,
            "user": user_list[0] if len(user_list) == 1 else None,
            "users": user_list
        }
        
        self.channels[channel_id] = channel
        
        result = {"ok": True, "channel": channel}
        if return_im and len(user_list) == 1:
            result["im"] = channel
        
        return result

    def conversations_close(self, channel: str) -> Dict[str, Any]:
        """
        Close a DM or MPDM.

        Args:
            channel: Conversation ID to close.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        if channel in self.channels:
            del self.channels[channel]
            return {"ok": True}
        
        return {"ok": False, "error": "channel_not_found"}

    def conversations_join(self, channel: str) -> Dict[str, Any]:
        """
        Join a channel.

        Args:
            channel: Channel ID.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "channel": dict}``
        """
        if channel in self.channels:
            self.channels[channel]["is_member"] = True
            return {
                "ok": True,
                "channel": self.channels[channel]
            }
        
        return {"ok": False, "error": "channel_not_found"}

    def conversations_leave(self, channel: str) -> Dict[str, Any]:
        """
        Leave a channel.

        Args:
            channel: Channel ID.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        if channel in self.channels:
            self.channels[channel]["is_member"] = False
            return {"ok": True}
        
        return {"ok": False, "error": "channel_not_found"}

    def conversations_info(self, channel: str, *, include_num_members: bool = False) -> Dict[str, Any]:
        """
        Retrieve channel metadata.

        Args:
            channel: Channel ID.
            include_num_members: Whether to include the member count.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "channel": dict}``
        """
        if channel in self.channels:
            channel_info = self.channels[channel].copy()
            if include_num_members:
                channel_info["num_members"] = 2  # Mock member count
            return {
                "ok": True,
                "channel": channel_info
            }
        
        return {"ok": False, "error": "channel_not_found"}

    def conversations_history(self, channel: str, *, limit: int = 100, latest: Optional[str] = None, oldest: Optional[str] = None, inclusive: bool = False) -> Dict[str, Any]:
        """
        Fetch message history for a conversation.

        Args:
            channel: Conversation ID.
            limit: Max messages to return.
            latest: Only messages before this ts.
            oldest: Only messages after this ts.
            inclusive: Include messages with latest/oldest timestamp.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "messages": list, "has_more": bool}``
        """
        channel_messages = [
            msg for msg in self.messages
            if msg.get("channel") == channel
        ]
        
        # Apply timestamp filtering
        if latest:
            channel_messages = [msg for msg in channel_messages if float(msg.get("ts", 0)) < float(latest)]
        if oldest:
            channel_messages = [msg for msg in channel_messages if float(msg.get("ts", 0)) > float(oldest)]
        
        # Sort by timestamp (newest first)
        channel_messages.sort(key=lambda x: float(x.get("ts", 0)), reverse=True)
        
        # Apply limit
        result_messages = channel_messages[:limit]
        
        return {
            "ok": True,
            "messages": result_messages,
            "has_more": len(channel_messages) > limit
        }

    def conversations_replies(self, channel: str, ts: str, *, limit: int = 100, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve messages in a thread.

        Args:
            channel: Channel ID containing the parent message.
            ts: Timestamp of the parent message.
            limit: Messages per page.
            cursor: Pagination cursor.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "messages": list}``
        """
        thread_messages = self.threads.get(ts, [])
        
        # Add parent message to the beginning
        parent_message = next((msg for msg in self.messages if msg.get("ts") == ts), None)
        if parent_message:
            thread_messages = [parent_message] + thread_messages
        
        return {
            "ok": True,
            "messages": thread_messages[:limit]
        }

    def conversations_setTopic(self, channel: str, topic: str) -> Dict[str, Any]:
        """
        Set a channel topic.

        Args:
            channel: Channel ID.
            topic: New topic.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "topic": str}``
        """
        if channel in self.channels:
            self.channels[channel]["topic"] = topic
            return {
                "ok": True,
                "topic": topic
            }
        
        return {"ok": False, "error": "channel_not_found"}

    def conversations_setPurpose(self, channel: str, purpose: str) -> Dict[str, Any]:
        """
        Set a channel purpose.

        Args:
            channel: Channel ID.
            purpose: New purpose text.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "purpose": str}``
        """
        if channel in self.channels:
            self.channels[channel]["purpose"] = purpose
            return {
                "ok": True,
                "purpose": purpose
            }
        
        return {"ok": False, "error": "channel_not_found"}

    def conversations_rename(self, channel: str, name: str) -> Dict[str, Any]:
        """
        Rename a channel.

        Args:
            channel: Channel ID.
            name: New channel name.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "channel": dict}``
        """
        if channel in self.channels:
            self.channels[channel]["name"] = name
            return {
                "ok": True,
                "channel": self.channels[channel]
            }
        
        return {"ok": False, "error": "channel_not_found"}

    def conversations_create(self, name: str, *, is_private: bool = False) -> Dict[str, Any]:
        """
        Create a new channel.

        Args:
            name: Name of the channel to create.
            is_private: If True, create as a private channel.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "channel": dict}``
        """
        channel_id = f"C{uuid.uuid4().hex[:8]}"
        
        channel = {
            "id": channel_id,
            "name": name,
            "is_channel": True,
            "is_private": is_private,
            "is_member": True,
            "topic": "",
            "purpose": ""
        }
        
        self.channels[channel_id] = channel
        
        return {
            "ok": True,
            "channel": channel
        }

    # ------------------------------------------------------------------
    # users.* — user discovery & presence
    # ------------------------------------------------------------------

    def users_list(self, *, limit: int = 200, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        List workspace members.

        Args:
            limit: Max users to return.
            cursor: Pagination cursor.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "members": list}``
        """
        members_list = list(self.users.values())[:limit]
        
        return {
            "ok": True,
            "members": members_list
        }

    def users_info(self, user: str) -> Dict[str, Any]:
        """
        Retrieve a user's profile.

        Args:
            user: User ID.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "user": dict}``
        """
        if user in self.users:
            return {
                "ok": True,
                "user": self.users[user]
            }
        
        return {"ok": False, "error": "user_not_found"}

    def users_lookupByEmail(self, email: str) -> Dict[str, Any]:
        """
        Find a user by email address.

        Args:
            email: Email address.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "user": dict}``
        """
        for user in self.users.values():
            if user.get("email") == email:
                return {
                    "ok": True,
                    "user": user
                }
        
        return {"ok": False, "error": "users_not_found"}

    def users_conversations(self, user: str, *, types: str = "public_channel,private_channel,im,mpim", limit: int = 100, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        List conversations a user is a member of.

        Args:
            user: User ID.
            types: Conversation types to include.
            limit: Max results.
            cursor: Pagination cursor.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "channels": list}``
        """
        # Mock: return channels where user is a member
        user_channels = [
            channel for channel in self.channels.values()
            if channel.get("is_member", False)
        ][:limit]
        
        return {
            "ok": True,
            "channels": user_channels
        }

    def users_getPresence(self, user: str) -> Dict[str, Any]:
        """
        Retrieve a user's presence status.

        Args:
            user: User ID.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "presence": str}``
        """
        if user in self.users:
            return {
                "ok": True,
                "presence": "active"  # Mock presence
            }
        
        return {"ok": False, "error": "user_not_found"}

    # ------------------------------------------------------------------
    # search.* — searching messages & files
    # ------------------------------------------------------------------

    def search_messages(self, query: str, *, count: int = 20, page: int = 1, sort: str = "score", sort_dir: str = "desc") -> Dict[str, Any]:
        """
        Search messages.

        Args:
            query: Search query.
            count: Results per page.
            page: Page number.
            sort: Field to sort by.
            sort_dir: asc or desc.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "messages": dict}``
        """
        # Simple text search in messages
        matching_messages = [
            msg for msg in self.messages
            if query.lower() in msg.get("text", "").lower()
        ]
        
        # Apply pagination
        start_idx = (page - 1) * count
        end_idx = start_idx + count
        paginated_messages = matching_messages[start_idx:end_idx]
        
        return {
            "ok": True,
            "messages": {
                "total": len(matching_messages),
                "paging": {
                    "count": count,
                    "total": len(matching_messages),
                    "page": page,
                    "pages": (len(matching_messages) + count - 1) // count
                },
                "matches": paginated_messages
            }
        }

    def search_files(self, query: str, *, count: int = 20, page: int = 1) -> Dict[str, Any]:
        """
        Search files.

        Args:
            query: Search query.
            count: Results per page.
            page: Page number.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "files": dict}``
        """
        # Simple text search in file names
        matching_files = [
            file for file in self.files.values()
            if query.lower() in file.get("name", "").lower()
        ]
        
        # Apply pagination
        start_idx = (page - 1) * count
        end_idx = start_idx + count
        paginated_files = matching_files[start_idx:end_idx]
        
        return {
            "ok": True,
            "files": {
                "total": len(matching_files),
                "paging": {
                    "count": count,
                    "total": len(matching_files),
                    "page": page,
                    "pages": (len(matching_files) + count - 1) // count
                },
                "matches": paginated_files
            }
        }

    def search_all(self, query: str, *, count: int = 20, page: int = 1) -> Dict[str, Any]:
        """
        Perform a combined search across messages and files.

        Args:
            query: Search query.
            count: Results per page.
            page: Page number.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "messages": dict, "files": dict}``
        """
        messages_result = self.search_messages(query, count=count, page=page)
        files_result = self.search_files(query, count=count, page=page)
        
        return {
            "ok": True,
            "messages": messages_result["messages"],
            "files": files_result["files"]
        }

    # ------------------------------------------------------------------
    # reminders.* — personal reminders
    # ------------------------------------------------------------------

    def reminders_add(self, text: str, remind_time: str | int, *, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a reminder.

        Args:
            text: Reminder text.
            remind_time: When to remind (unix ts or natural text).
            user: User ID to set reminder for (defaults to caller).

        Returns:
            Dict[str, Any]: ``{"ok": bool, "reminder": dict}``
        """
        reminder_id = f"reminder_{uuid.uuid4().hex[:8]}"
        user_id = user or "U001"  # Default to mock user
        
        reminder = {
            "id": reminder_id,
            "text": text,
            "time": remind_time,
            "user": user_id,
            "created": int(time.time())
        }
        
        self.reminders[reminder_id] = reminder
        
        return {
            "ok": True,
            "reminder": reminder
        }

    def reminders_list(self) -> Dict[str, Any]:
        """
        List reminders.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "reminders": list}``
        """
        return {
            "ok": True,
            "reminders": list(self.reminders.values())
        }

    def reminders_complete(self, reminder: str) -> Dict[str, Any]:
        """
        Mark a reminder as complete.

        Args:
            reminder: Reminder ID.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        if reminder in self.reminders:
            self.reminders[reminder]["completed"] = True
            return {"ok": True}
        
        return {"ok": False, "error": "reminder_not_found"}

    def reminders_delete(self, reminder: str) -> Dict[str, Any]:
        """
        Delete a reminder.

        Args:
            reminder: Reminder ID.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        if reminder in self.reminders:
            del self.reminders[reminder]
            return {"ok": True}
        
        return {"ok": False, "error": "reminder_not_found"}

    def reminders_info(self, reminder: str) -> Dict[str, Any]:
        """
        Get information about a reminder.

        Args:
            reminder: Reminder ID.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "reminder": dict}``
        """
        if reminder in self.reminders:
            return {
                "ok": True,
                "reminder": self.reminders[reminder]
            }
        
        return {"ok": False, "error": "reminder_not_found"}

    # ------------------------------------------------------------------
    # files.* — file uploads & metadata
    # ------------------------------------------------------------------

    def files_upload(self, file: bytes, *, filename: str, channels: Optional[str] = None, initial_comment: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file.

        Args:
            file: Binary content.
            filename: Display filename.
            channels: Comma list of channel IDs.
            initial_comment: Optional comment to add.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "file": dict}``
        """
        file_id = f"F{uuid.uuid4().hex[:8]}"
        
        file_info = {
            "id": file_id,
            "name": filename,
            "size": len(file),
            "channels": channels.split(",") if channels else [],
            "initial_comment": initial_comment,
            "created": int(time.time()),
            "user": "U001"  # Mock user
        }
        
        self.files[file_id] = file_info
        
        return {
            "ok": True,
            "file": file_info
        }

    def files_list(self, *, user: Optional[str] = None, types: Optional[str] = None, page: int = 1, count: int = 100) -> Dict[str, Any]:
        """
        List files.

        Args:
            user: Filter by user ID.
            types: Filter by file types.
            page: Page number.
            count: Results per page.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "files": list}``
        """
        files_list = list(self.files.values())
        
        # Apply user filter
        if user:
            files_list = [f for f in files_list if f.get("user") == user]
        
        # Apply pagination
        start_idx = (page - 1) * count
        end_idx = start_idx + count
        paginated_files = files_list[start_idx:end_idx]
        
        return {
            "ok": True,
            "files": paginated_files
        }

    def files_info(self, file: str) -> Dict[str, Any]:
        """
        Get information about a file.

        Args:
            file: File ID.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "file": dict}``
        """
        if file in self.files:
            return {
                "ok": True,
                "file": self.files[file]
            }
        
        return {"ok": False, "error": "file_not_found"}

    def files_delete(self, file: str) -> Dict[str, Any]:
        """
        Delete a file.

        Args:
            file: File ID.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        if file in self.files:
            del self.files[file]
            return {"ok": True}
        
        return {"ok": False, "error": "file_not_found"}

    # ------------------------------------------------------------------
    # reactions.* — add/remove emoji reactions
    # ------------------------------------------------------------------

    def reactions_add(self, name: str, channel: str, timestamp: str) -> Dict[str, Any]:
        """
        Add a reaction to a message or file.

        Args:
            name: Emoji name (without colons).
            channel: Channel ID.
            timestamp: Item timestamp.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        reaction_key = f"{channel}:{timestamp}"
        
        if reaction_key not in self.reactions:
            self.reactions[reaction_key] = []
        
        # Check if reaction already exists
        existing_reaction = next(
            (r for r in self.reactions[reaction_key] if r["name"] == name),
            None
        )
        
        if not existing_reaction:
            reaction = {
                "name": name,
                "count": 1,
                "users": ["U001"]  # Mock user
            }
            self.reactions[reaction_key].append(reaction)
        else:
            existing_reaction["count"] += 1
            if "U001" not in existing_reaction["users"]:
                existing_reaction["users"].append("U001")
        
        return {"ok": True}

    def reactions_get(self, channel: str, timestamp: str, *, full: bool = False) -> Dict[str, Any]:
        """
        Get reactions for an item.

        Args:
            channel: Channel ID.
            timestamp: Item timestamp.
            full: If True, include list of reacting users.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "message": dict}``
        """
        reaction_key = f"{channel}:{timestamp}"
        reactions = self.reactions.get(reaction_key, [])
        
        # Find the message
        message = next(
            (msg for msg in self.messages if msg.get("ts") == timestamp and msg.get("channel") == channel),
            None
        )
        
        if message:
            message_copy = message.copy()
            message_copy["reactions"] = reactions
            return {
                "ok": True,
                "message": message_copy
            }
        
        return {"ok": False, "error": "message_not_found"}

    def reactions_list(self, *, user: Optional[str] = None, count: int = 100, page: int = 1) -> Dict[str, Any]:
        """
        List reactions made by a user.

        Args:
            user: Filter by user ID (default caller).
            count: Results per page.
            page: Page number.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "items": list}``
        """
        user_id = user or "U001"
        
        # Find all reactions by this user
        user_reactions = []
        for reaction_key, reactions in self.reactions.items():
            channel, timestamp = reaction_key.split(":", 1)
            for reaction in reactions:
                if user_id in reaction.get("users", []):
                    user_reactions.append({
                        "type": "message",
                        "channel": channel,
                        "timestamp": timestamp,
                        "reaction": reaction
                    })
        
        # Apply pagination
        start_idx = (page - 1) * count
        end_idx = start_idx + count
        paginated_reactions = user_reactions[start_idx:end_idx]
        
        return {
            "ok": True,
            "items": paginated_reactions
        }

    def reactions_remove(self, name: str, channel: str, timestamp: str) -> Dict[str, Any]:
        """
        Remove a reaction from a message or file.

        Args:
            name: Emoji name.
            channel: Channel ID.
            timestamp: Item timestamp.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        reaction_key = f"{channel}:{timestamp}"
        
        if reaction_key in self.reactions:
            reactions = self.reactions[reaction_key]
            for reaction in reactions:
                if reaction["name"] == name:
                    if "U001" in reaction["users"]:
                        reaction["users"].remove("U001")
                        reaction["count"] -= 1
                        if reaction["count"] == 0:
                            reactions.remove(reaction)
                        return {"ok": True}
        
        return {"ok": False, "error": "reaction_not_found"}

    # ------------------------------------------------------------------
    # pins.* — channel pin management
    # ------------------------------------------------------------------

    def pins_add(self, channel: str, timestamp: str) -> Dict[str, Any]:
        """
        Pin an item in a channel.

        Args:
            channel: Channel ID.
            timestamp: Message timestamp to pin.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        if channel not in self.pins:
            self.pins[channel] = []
        
        if timestamp not in self.pins[channel]:
            self.pins[channel].append(timestamp)
        
        return {"ok": True}

    def pins_remove(self, channel: str, timestamp: str) -> Dict[str, Any]:
        """
        Unpin an item in a channel.

        Args:
            channel: Channel ID.
            timestamp: Timestamp of the pinned item.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        if channel in self.pins and timestamp in self.pins[channel]:
            self.pins[channel].remove(timestamp)
            return {"ok": True}
        
        return {"ok": False, "error": "pinned_item_not_found"}

    def pins_list(self, channel: str) -> Dict[str, Any]:
        """
        List pinned items in a channel.

        Args:
            channel: Channel ID.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "items": list}``
        """
        pinned_timestamps = self.pins.get(channel, [])
        pinned_items = []
        
        for ts in pinned_timestamps:
            message = next(
                (msg for msg in self.messages if msg.get("ts") == ts and msg.get("channel") == channel),
                None
            )
            if message:
                pinned_items.append(message)
        
        return {
            "ok": True,
            "items": pinned_items
        }

    # ------------------------------------------------------------------
    # dnd.* — Do Not Disturb controls
    # ------------------------------------------------------------------

    def dnd_setSnooze(self, num_minutes: int) -> Dict[str, Any]:
        """
        Set Do Not Disturb snooze.

        Args:
            num_minutes: Duration in minutes.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "snooze_enabled": bool}``
        """
        user_id = "U001"  # Mock user
        if user_id not in self.dnd:
            self.dnd[user_id] = {}
        
        self.dnd[user_id]["snooze_enabled"] = True
        self.dnd[user_id]["snooze_endtime"] = int(time.time()) + (num_minutes * 60)
        
        return {
            "ok": True,
            "snooze_enabled": True
        }

    def dnd_endSnooze(self) -> Dict[str, Any]:
        """
        End Do Not Disturb snooze.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        user_id = "U001"  # Mock user
        if user_id in self.dnd:
            self.dnd[user_id]["snooze_enabled"] = False
            if "snooze_endtime" in self.dnd[user_id]:
                del self.dnd[user_id]["snooze_endtime"]
        
        return {"ok": True}

    def dnd_endDnd(self) -> Dict[str, Any]:
        """
        End the current Do Not Disturb session.

        Returns:
            Dict[str, Any]: ``{"ok": bool}``
        """
        user_id = "U001"  # Mock user
        if user_id in self.dnd:
            self.dnd[user_id]["dnd_enabled"] = False
        
        return {"ok": True}

    def dnd_info(self, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Do Not Disturb status.

        Args:
            user: User ID (defaults to caller).

        Returns:
            Dict[str, Any]: ``{"ok": bool, "dnd_enabled": bool}``
        """
        user_id = user or "U001"
        
        if user_id in self.dnd:
            return {
                "ok": True,
                "dnd_enabled": self.dnd[user_id].get("dnd_enabled", False)
            }
        
        return {"ok": False, "error": "user_not_found"}

    # ------------------------------------------------------------------
    # team.info — workspace metadata
    # ------------------------------------------------------------------

    def team_info(self) -> Dict[str, Any]:
        """
        Retrieve workspace information.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "team": dict}``
        """
        return {
            "ok": True,
            "team": self.team_info
        }

    # ------------------------------------------------------------------
    # emoji.list — fun extras (often requested via voice: "what emojis do we have?")
    # ------------------------------------------------------------------

    def emoji_list(self) -> Dict[str, Any]:
        """
        List custom emoji in the workspace.

        Returns:
            Dict[str, Any]: ``{"ok": bool, "emoji": dict}``
        """
        return {
            "ok": True,
            "emoji": self.emoji
        } 