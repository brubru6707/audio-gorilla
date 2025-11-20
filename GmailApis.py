# Inspired by https://developers.google.com/workspace/gmail/api/guides

import datetime
import copy
import base64
from typing import Dict, List, Any, Optional, Union
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("GmailApis")

class GmailApis:
    """
    An API class for simulating Gmail operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the Gmail API, which provides core functionality for managing emails, drafts, and labels."
        self.current_user: Optional[str] = None  # Currently authenticated user ID
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Load a scenario with users and their data.
        Args:
            scenario (Dict): Scenario data to load.
        """
        DEFAULT_STATE_COPY = copy.deepcopy(DEFAULT_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        # Set first user as authenticated user by default
        if self.users and not self.current_user:
            self.current_user = next(iter(self.users.keys()))
        print("GmailApis: Loaded scenario with users and their UUIDs.")

    def authenticate(self, email: str) -> Dict[str, Union[bool, str]]:
        """
        Authenticate a user and set them as the current user.
        Args:
            email (str): The user's email address to authenticate.
        Returns:
            Dict[str, Union[bool, str]]: Dictionary indicating success/failure and message.
        """
        user_id = self._get_user_id_by_email(email)
        if not user_id:
            return {"success": False, "message": "User not found."}
        
        self.current_user = user_id
        print(f"GmailApis: Authenticated as {email}")
        return {"success": True, "message": f"Authenticated as {email}"}

    def _resolve_user_id(self, user_id: str) -> Optional[str]:
        """
        Resolve 'me' to current authenticated user, or email to internal user ID.
        Args:
            user_id (str): User's email address or the special value 'me'.
        Returns:
            Optional[str]: Resolved internal user ID, or None if not found.
        """
        if user_id == "me":
            return self.current_user
        
        # Must be an email address
        return self._get_user_id_by_email(user_id)

    def _generate_id(self) -> str:
        """
        Generate a unique ID in Gmail format (hex string).

        Returns:
            str: Generated hex ID (16 characters).
        """
        import random
        return ''.join(random.choices('0123456789abcdef', k=16))
    
    def _generate_history_id(self) -> str:
        """
        Generate a history ID (sequential-looking number).

        Returns:
            str: Generated history ID.
        """
        return str(int(datetime.datetime.now().timestamp() * 1000))

    def _parse_gmail_query(self, query: str, message: Dict[str, Any]) -> bool:
        """
        Parse Gmail search query operators and match against message.
        Supports: from:, to:, subject:, after:, before:, has:attachment, is:unread, etc.

        Args:
            query (str): Gmail search query string.
            message (Dict[str, Any]): Message to match against.

        Returns:
            bool: True if message matches query, False otherwise.
        """
        if not query:
            return True
        
        query_lower = query.lower()
        
        # Extract headers for searching
        headers = {h["name"].lower(): h["value"].lower() for h in message.get("payload", {}).get("headers", [])}
        snippet = message.get("snippet", "").lower()
        label_ids = [lid.lower() for lid in message.get("labelIds", [])]
        
        # Simple keyword search (no operators)
        if ':' not in query_lower and not query_lower.startswith('-'):
            return query_lower in snippet or query_lower in headers.get("subject", "")
        
        # Parse operators
        tokens = query_lower.split()
        for token in tokens:
            if ':' in token:
                operator, value = token.split(':', 1)
                value = value.strip('"')
                
                if operator == 'from':
                    if value not in headers.get("from", ""):
                        return False
                elif operator == 'to':
                    if value not in headers.get("to", ""):
                        return False
                elif operator == 'subject':
                    if value not in headers.get("subject", ""):
                        return False
                elif operator == 'has' and value == 'attachment':
                    # Check if message has attachment (simplified)
                    if not message.get("payload", {}).get("parts"):
                        return False
                elif operator == 'is':
                    if value == 'unread' and 'unread' not in label_ids:
                        return False
                    elif value == 'read' and 'unread' in label_ids:
                        return False
                    elif value == 'starred' and 'starred' not in label_ids:
                        return False
            elif token.startswith('-'):
                # Negation operator
                neg_term = token[1:]
                if neg_term in snippet:
                    return False
        
        return True

    def _decode_raw_message(self, raw_content: str) -> Dict[str, str]:
        """
        Decode base64url encoded email content and extract fields.
        For mock purposes, we'll simulate decoding by assuming the raw content
        contains JSON-like structure or simple text format.

        Args:
            raw_content (str): Base64url encoded email content.

        Returns:
            Dict[str, str]: Dictionary with 'to', 'subject', 'body' fields.
        """
        try:
            # Try to decode as base64url
            decoded_bytes = base64.urlsafe_b64decode(raw_content)
            decoded_text = decoded_bytes.decode('utf-8')

            # For mock purposes, try to parse as simple JSON first
            import json
            try:
                parsed = json.loads(decoded_text)
                return {
                    "to": parsed.get("to", ""),
                    "subject": parsed.get("subject", ""),
                    "body": parsed.get("body", "")
                }
            except json.JSONDecodeError:
                # If not JSON, try to extract from RFC 2822-like format
                lines = decoded_text.split('\n')
                to = ""
                subject = ""
                body = ""

                for line in lines:
                    if line.lower().startswith('to:'):
                        to = line[3:].strip()
                    elif line.lower().startswith('subject:'):
                        subject = line[8:].strip()
                    elif line.strip() == "" and not body:
                        # Empty line marks start of body
                        continue
                    elif body or line.strip():
                        if not body:
                            body = line
                        else:
                            body += '\n' + line

                return {"to": to, "subject": subject, "body": body.strip()}

        except Exception:
            # If decoding fails, return empty dict - caller should handle
            return {"to": "", "subject": "", "body": ""}

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """
        Get internal user ID by email address.
        Args:
            email (str): User's email address.
        Returns:
            Optional[str]: Internal user ID if found, None otherwise.
        """
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """
        Get user email by internal user ID.
        Args:
            user_id (str): Internal user ID.
        Returns:
            Optional[str]: User's email address if found, None otherwise.
        """
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _get_user_gmail_data(self, user_id: str) -> Optional[Dict]:
        """
        Get Gmail data for a user.
        Args:
            user_id (str): The internal user ID (UUID).
        Returns:
            Optional[Dict]: User's Gmail data if found, None otherwise.
        """
        return self.users.get(user_id, {}).get("gmail_data")

    def _get_user_threads_data(self, user_id: str) -> Optional[Dict]:
        """
        Get threads data for a user.
        Args:
            user_id (str): The internal user ID (UUID).
        Returns:
            Optional[Dict]: User's threads data if found, None otherwise.
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("threads") if gmail_data else None

    def _get_user_messages_data(self, user_id: str) -> Optional[Dict]:
        """
        Get messages data for a user.
        Args:
            user_id (str): The internal user ID (UUID).
        Returns:
            Optional[Dict]: User's messages data if found, None otherwise.
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("messages") if gmail_data else None

    def _get_user_drafts_data(self, user_id: str) -> Optional[Dict]:
        """
        Get drafts data for a user.
        Args:
            user_id (str): The internal user ID (UUID).
        Returns:
            Optional[Dict]: User's drafts data if found, None otherwise.
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("drafts") if gmail_data else None

    def _get_user_labels_data(self, user_id: str) -> Optional[Dict]:
        """
        Get labels data for a user.
        Args:
            user_id (str): The internal user ID (UUID).
        Returns:
            Optional[Dict]: User's labels data if found, None otherwise.
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("labels") if gmail_data else None

    def _update_thread_snippet(self, user_id: str, thread_id: str) -> None:
        """
        Update a thread's snippet with the most recent message.
        Args:
            user_id (str): The internal user ID (UUID).
            thread_id (str): Thread ID to update.
        """
        threads = self._get_user_threads_data(user_id)
        messages = self._get_user_messages_data(user_id)
        
        if not threads or not messages or thread_id not in threads:
            return
            
        thread = threads[thread_id]
        thread_msg_ids = [m["id"] for m in thread.get("messages", [])]
        
        if not thread_msg_ids:
            return
            
        # Find the most recent message by timestamp
        latest_msg = None
        latest_timestamp = 0
        for msg_id in thread_msg_ids:
            if msg_id in messages:
                msg_timestamp = int(messages[msg_id].get("internalDate", "0"))
                if msg_timestamp > latest_timestamp:
                    latest_timestamp = msg_timestamp
                    latest_msg = messages[msg_id]
        
        if latest_msg:
            thread["snippet"] = latest_msg.get("snippet", "")

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the Gmail profile for a user.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
        Returns:
            Optional[Dict[str, Any]]: User's profile data if found, None otherwise.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id or user_id not in self.users:
            return None
        
        user_data = self.users.get(user_id)
        return user_data.get("gmail_data", {}).get("profile") if user_data else None

    def list_messages(
        self,
        user_id: str,
        q: Optional[str] = None,
        label_ids: Optional[List[str]] = None,
        page_token: Optional[str] = None,
        max_results: int = 100,
        includeSpamTrash: bool = False,
    ) -> Dict[str, Union[List[Dict], str, int]]:
        """
        List messages matching criteria.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            q (Optional[str]): Only return messages matching the specified query. Supports the same query format as the Gmail search box.
            label_ids (Optional[List[str]]): Only return messages with labels that match all of the specified label IDs.
            page_token (Optional[str]): Page token to retrieve a specific page of results in the list.
            max_results (int): Maximum number of messages to return. This field defaults to 100. The maximum allowed value for this field is 500.
            includeSpamTrash (bool): Include messages from SPAM and TRASH in the results.
        Returns:
            Dict[str, Union[List[Dict], str, int]]: Dictionary containing messages, pagination token, and result count.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return {"messages": [], "resultSizeEstimate": 0}
        
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return {"messages": [], "resultSizeEstimate": 0}

        filtered_messages = []
        for _, msg_data in messages.items():
            match = True
            
            # Filter by query using Gmail query parser
            if q:
                if not self._parse_gmail_query(q, msg_data):
                    match = False
                
            # Filter by label IDs
            if label_ids:
                msg_labels = set(msg_data.get("labelIds", []))
                if not all(label in msg_labels for label in label_ids):
                    match = False
            
            # Filter out SPAM and TRASH unless includeSpamTrash is True
            if not includeSpamTrash:
                msg_labels = set(msg_data.get("labelIds", []))
                if "SPAM" in msg_labels or "TRASH" in msg_labels:
                    match = False
            
            if match:
                filtered_messages.append({
                    "id": msg_data["id"],
                    "threadId": msg_data["threadId"]
                })

        start_index = 0
        if page_token:
            try:
                start_index = int(page_token)
            except ValueError:
                start_index = 0

        paginated_messages = filtered_messages[start_index : start_index + max_results]
        next_page_token = str(start_index + max_results) if start_index + max_results < len(filtered_messages) else None

        return {
            "messages": paginated_messages,
            "nextPageToken": next_page_token,
            "resultSizeEstimate": len(filtered_messages)
        }

    def get_message(
        self, userId: str, id: str, format: str = "full"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific message.
        Args:
            userId (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            id (str): The ID of the message to retrieve.
            format (str): The format to return the message in.
        Returns:
            Optional[Dict[str, Any]]: Message data if found, None otherwise.
        """
        userId = self._resolve_user_id(userId)
        if not userId:
            return None
        messages = self._get_user_messages_data(userId)
        if messages is None:
            return None
        message = messages.get(id)
        if message:
            if format == "minimal":
                return {
                    "id": message["id"], 
                    "threadId": message["threadId"]
                }
            elif format == "metadata":
                return {
                    "id": message["id"],
                    "threadId": message["threadId"],
                    "labelIds": message.get("labelIds", []),
                    "snippet": message.get("snippet", ""),
                    "historyId": message.get("historyId", ""),
                    "internalDate": message.get("internalDate", ""),
                    "payload": {
                        "mimeType": message.get("payload", {}).get("mimeType", "text/plain"),
                        "headers": message.get("payload", {}).get("headers", [])
                    },
                    "sizeEstimate": message.get("sizeEstimate", 0)
                }
            elif format == "raw":
                return {
                    "id": message["id"],
                    "threadId": message["threadId"],
                    "historyId": message.get("historyId", ""),
                    "internalDate": message.get("internalDate", ""),
                    "raw": "raw_content_for_" + message["id"]
                }
            # Full format
            return copy.deepcopy(message)
        return None

    def send_message(
        self, userId: str, message: Dict[str, Any]
    ) -> Dict[str, Union[str, Dict]]:
        """
        Send a message.
        Args:
            userId (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            message (Dict[str, Any]): The message to send. Must contain 'raw' field with base64url encoded email.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing message ID and thread ID, or error message.
        """
        userId = self._resolve_user_id(userId)
        if not userId or userId not in self.users:
            return {"error": "User not found."}

        gmail_data = self.users[userId].get("gmail_data")
        if not gmail_data:
            return {"error": "Gmail data not available for user."}

        # For mock purposes, we'll decode the raw message or use provided fields
        raw_content = message.get("raw", "")
        thread_id = message.get("threadId")
        
        # If no raw content, construct from message parts for backward compatibility
        if not raw_content:
            to = message.get("to", "")
            subject = message.get("subject", "")
            body = message.get("body", "")
            if not thread_id:
                thread_id = message.get("threadId")
        else:
            # Decode the raw email content
            decoded_fields = self._decode_raw_message(raw_content)
            to = decoded_fields.get("to", "")
            subject = decoded_fields.get("subject", "")
            body = decoded_fields.get("body", "")
            if not thread_id:
                thread_id = self._generate_id()

        user_email = self._get_user_email_by_id(userId)
        new_msg_id = self._generate_id()
        if not thread_id:
            thread_id = self._generate_id()
        
        history_id = self._generate_history_id()
        internal_date = str(int(datetime.datetime.now().timestamp() * 1000))
        
        # Calculate size estimate (rough approximation)
        body_size = len(body)
        headers_size = len(to) + len(subject) + len(user_email or "") + 100
        size_estimate = body_size + headers_size

        new_message = {
            "id": new_msg_id,
            "threadId": thread_id,
            "snippet": body[:100] if len(body) > 100 else body,
            "historyId": history_id,
            "internalDate": internal_date,
            "sizeEstimate": size_estimate,
            "payload": {
                "mimeType": "text/plain",
                "headers": [
                    {"name": "To", "value": to},
                    {"name": "From", "value": user_email},
                    {"name": "Subject", "value": subject},
                    {"name": "Date", "value": datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")},
                    {"name": "Message-ID", "value": f"<{new_msg_id}@mail.gmail.com>"}
                ],
                "body": {
                    "size": body_size,
                    "data": base64.urlsafe_b64encode(body.encode('utf-8')).decode('utf-8') if body else ""
                }
            },
            "labelIds": ["SENT", "INBOX"]
        }
        gmail_data["messages"][new_msg_id] = new_message
        
        # Create or update thread with snippet and historyId
        if thread_id not in gmail_data["threads"]:
            gmail_data["threads"][thread_id] = {
                "id": thread_id, 
                "messages": [],
                "snippet": new_message["snippet"],
                "historyId": history_id
            }
        else:
            # Update thread snippet and historyId with latest message
            gmail_data["threads"][thread_id]["snippet"] = new_message["snippet"]
            gmail_data["threads"][thread_id]["historyId"] = history_id
            
        gmail_data["threads"][thread_id]["messages"].append({"id": new_msg_id})
        gmail_data["profile"]["messagesTotal"] = gmail_data["profile"].get("messagesTotal", 0) + 1
        gmail_data["profile"]["threadsTotal"] = len(gmail_data["threads"])

        recipient_user_id = self._get_user_id_by_email(to)
        if recipient_user_id and recipient_user_id != userId:
            recipient_gmail_data = self.users[recipient_user_id].get("gmail_data")
            if recipient_gmail_data:
                recipient_message = copy.deepcopy(new_message)
                recipient_message["labelIds"] = ["INBOX", "UNREAD"]
                recipient_gmail_data["messages"][new_msg_id] = recipient_message
                
                # Create or update thread for recipient with snippet and historyId
                if thread_id not in recipient_gmail_data["threads"]:
                    recipient_gmail_data["threads"][thread_id] = {
                        "id": thread_id, 
                        "messages": [],
                        "snippet": new_message["snippet"],
                        "historyId": history_id
                    }
                else:
                    # Update thread snippet and historyId with latest message
                    recipient_gmail_data["threads"][thread_id]["snippet"] = new_message["snippet"]
                    recipient_gmail_data["threads"][thread_id]["historyId"] = history_id
                    
                recipient_gmail_data["threads"][thread_id]["messages"].append({"id": new_msg_id})
                recipient_gmail_data["profile"]["messagesTotal"] = recipient_gmail_data["profile"].get("messagesTotal", 0) + 1
                recipient_gmail_data["profile"]["threadsTotal"] = len(recipient_gmail_data["threads"])

        print(f"Email sent: from {user_email} to {to}, subject '{subject}'")
        return {"id": new_msg_id, "threadId": thread_id}

    def delete_message(self, user_id: str, msg_id: str) -> Dict[str, Union[bool, str]]:
        """
        Delete a message.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            msg_id (str): Message ID to delete.
        Returns:
            Dict[str, Union[bool, str]]: Dictionary indicating success/failure and message.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return {"success": False, "message": "User not found."}
        
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return {"success": False, "message": "User not found or no messages data."}
        
        if msg_id in messages:
            thread_id = messages[msg_id]["threadId"]
            del messages[msg_id]
            
            threads = self._get_user_threads_data(user_id)
            if threads and thread_id in threads:
                threads[thread_id]["messages"] = [m for m in threads[thread_id]["messages"] if m["id"] != msg_id]
                
                # If no messages left in thread, delete the thread
                if not threads[thread_id]["messages"]:
                    del threads[thread_id]
                else:
                    # Update thread snippet with the most recent remaining message
                    self._update_thread_snippet(user_id, thread_id)

            if user_id in self.users:
                profile = self.users[user_id].get("gmail_data", {}).get("profile")
                if profile:
                    profile["messagesTotal"] = max(0, profile.get("messagesTotal", 0) - 1)
                    profile["threadsTotal"] = len(threads) if threads else 0

            print(f"Message deleted: ID={msg_id} for user {user_id}")
            return {"success": True, "message": f"Message {msg_id} deleted."}
        return {"success": False, "message": f"Message {msg_id} not found."}

    def list_drafts(
        self, user_id: str, page_token: Optional[str] = None, max_results: int = 10
    ) -> Dict[str, Union[List[Dict], str, int]]:
        """
        List drafts.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            page_token (Optional[str]): Pagination token.
            max_results (int): Maximum number of results to return.
        Returns:
            Dict[str, Union[List[Dict], str, int]]: Dictionary containing drafts, pagination token, and result count.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return {"drafts": [], "resultSizeEstimate": 0}
        
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return {"drafts": [], "resultSizeEstimate": 0}

        all_drafts = list(drafts.values())
        
        start_index = 0
        if page_token:
            try:
                start_index = int(page_token)
            except ValueError:
                start_index = 0

        paginated_drafts = all_drafts[start_index : start_index + max_results]
        next_page_token = str(start_index + max_results) if start_index + max_results < len(all_drafts) else None

        formatted_drafts = [{"id": d["id"], "message": d["message"]} for d in paginated_drafts]

        return {
            "drafts": formatted_drafts,
            "nextPageToken": next_page_token,
            "resultSizeEstimate": len(all_drafts)
        }

    def get_draft(self, user_id: str, draft_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific draft.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            draft_id (str): Draft ID.
        Returns:
            Optional[Dict[str, Any]]: Draft data if found, None otherwise.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return None
        
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return None
        
        draft = drafts.get(draft_id)
        if draft:
            return copy.deepcopy(draft)
        return None

    def create_draft(
        self, userId: str, draft: Dict[str, Any]
    ) -> Dict[str, Union[str, Dict]]:
        """
        Create a draft.
        Args:
            userId (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            draft (Dict[str, Any]): The draft to create. Must contain 'message' field with Message object.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing draft ID and message, or error message.
        """
        userId = self._resolve_user_id(userId)
        if not userId or userId not in self.users:
            return {"error": "User not found."}

        gmail_data = self.users[userId].get("gmail_data")
        if not gmail_data:
            return {"error": "Gmail data not available for user."}

        message = draft.get("message", {})
        
        # Extract message details for backward compatibility
        to = message.get("to", "")
        subject = message.get("subject", "")
        body = message.get("body", "")
        
        # If message doesn't have individual fields, use the raw content
        if not to and not subject and not body:
            raw_content = message.get("raw", "")
            if raw_content:
                decoded_fields = self._decode_raw_message(raw_content)
                to = decoded_fields.get("to", "")
                subject = decoded_fields.get("subject", "")
                body = decoded_fields.get("body", "")

        new_draft_id = self._generate_id()
        new_draft = {
            "id": new_draft_id,
            "message": {
                "to": to,
                "subject": subject,
                "body": body
            }
        }
        gmail_data["drafts"][new_draft_id] = new_draft
        print(f"Draft created: ID={new_draft_id} for user {userId}")
        return {"id": new_draft_id, "message": new_draft["message"]}

    def update_draft(
        self, userId: str, id: str, draft: Dict[str, Any]
    ) -> Dict[str, Union[str, Dict]]:
        """
        Update a draft.
        Args:
            userId (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            id (str): The ID of the draft to update.
            draft (Dict[str, Any]): The draft to update. Must contain 'message' field with Message object.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing draft ID and message, or error message.
        """
        userId = self._resolve_user_id(userId)
        if not userId:
            return {"error": "User not found or no drafts data."}
        
        drafts = self._get_user_drafts_data(userId)
        if drafts is None:
            return {"error": "User not found or no drafts data."}

        if id in drafts:
            message = draft.get("message", {})
            
            # Extract message details for backward compatibility
            to = message.get("to", "")
            subject = message.get("subject", "")
            body = message.get("body", "")
            
            # If message doesn't have individual fields, use the raw content
            if not to and not subject and not body:
                raw_content = message.get("raw", "")
                if raw_content:
                    decoded_fields = self._decode_raw_message(raw_content)
                    to = decoded_fields.get("to", "")
                    subject = decoded_fields.get("subject", "")
                    body = decoded_fields.get("body", "")
            
            drafts[id]["message"]["to"] = to
            drafts[id]["message"]["subject"] = subject
            drafts[id]["message"]["body"] = body
            print(f"Draft updated: ID={id} for user {userId}")
            return {"id": id, "message": drafts[id]["message"]}
        return {"error": f"Draft {id} not found."}

    def delete_draft(self, user_id: str, draft_id: str) -> Dict[str, Union[bool, str]]:
        """
        Delete a draft.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            draft_id (str): Draft ID to delete.
        Returns:
            Dict[str, Union[bool, str]]: Dictionary indicating success/failure and message.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return {"success": False, "message": "User not found or no drafts data."}
        
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return {"success": False, "message": "User not found or no drafts data."}
        
        if draft_id in drafts:
            del drafts[draft_id]
            print(f"Draft deleted: ID={draft_id} for user {user_id}")
            return {"success": True, "message": f"Draft {draft_id} deleted."}
        return {"success": False, "message": f"Draft {draft_id} not found."}

    def send_draft(self, userId: str, id: str) -> Dict[str, Union[str, Dict]]:
        """
        Send a draft as a message.
        Args:
            userId (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            id (str): The ID of the draft to send.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing message ID and thread ID, or error message.
        """
        userId = self._resolve_user_id(userId)
        if not userId:
            return {"error": "User not found or no drafts data."}
        
        drafts = self._get_user_drafts_data(userId)
        if drafts is None:
            return {"error": "User not found or no drafts data."}
        
        if id not in drafts:
            return {"error": f"Draft {id} not found."}
        
        draft = drafts[id]
        draft_message = draft.get("message", {})
        
        # Extract draft details
        to = draft_message.get("to", "")
        subject = draft_message.get("subject", "")
        body = draft_message.get("body", "")
        
        if not to:
            return {"error": "Draft has no recipient specified."}
        
        # Send the draft as a regular message
        # Use internal method directly since we already have the resolved userId
        user_email = self._get_user_email_by_id(userId)
        if not user_email:
            return {"error": "User not found."}
            
        message = {
            "to": to,
            "subject": subject,
            "body": body
        }
        result = self.send_message(user_email, message)
        
        # If message was sent successfully, delete the draft
        if "id" in result and "error" not in result:
            self.delete_draft(user_email, id)
            print(f"Draft sent and deleted: draft ID={id}, message ID={result['id']}")
        
        return result

    def list_labels(self, user_id: str) -> Dict[str, Union[List[Dict], str]]:
        """
        List labels.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
        Returns:
            Dict[str, Union[List[Dict], str]]: Dictionary containing labels.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return {"labels": []}
        
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return {"labels": []}
        
        formatted_labels = [copy.deepcopy(label) for label in labels.values()]
        return {"labels": formatted_labels}

    def get_label(self, user_id: str, label_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific label.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            label_id (str): Label ID.
        Returns:
            Optional[Dict[str, Any]]: Label data if found, None otherwise.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return None
        
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return None
        
        label = labels.get(label_id)
        if label:
            return copy.deepcopy(label)
        return None

    def create_label(self, user_id: str, label_name: str) -> Dict[str, Union[str, Dict]]:
        """
        Create a label.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            label_name (str): Name for the new label.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing label ID and name, or error message.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id or user_id not in self.users:
            return {"error": "User not found."}

        gmail_data = self.users[user_id].get("gmail_data")
        if not gmail_data:
            return {"error": "Gmail data not available for user."}
        
        labels = gmail_data.get("labels")
        if labels is None:
            gmail_data["labels"] = {}
            labels = gmail_data["labels"]

        new_label_id = self._generate_id()
        new_label = {
            "id": new_label_id,
            "name": label_name,
            "messageListVisibility": "show",
            "labelListVisibility": "show",
            "type": "user"
        }
        labels[new_label_id] = new_label
        print(f"Label created: ID={new_label_id}, Name='{label_name}' for user {user_id}")
        return {"id": new_label_id, "name": label_name}

    def update_label(self, user_id: str, label_id: str, new_label_name: str) -> Dict[str, Union[str, Dict]]:
        """
        Update a label.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            label_id (str): Label ID to update.
            new_label_name (str): New name for the label.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing label ID and name, or error message.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return {"error": "User not found or no labels data."}
        
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return {"error": "User not found or no labels data."}
        
        if label_id in labels:
            labels[label_id]["name"] = new_label_name
            print(f"Label updated: ID={label_id}, New Name='{new_label_name}' for user {user_id}")
            return {"id": label_id, "name": new_label_name}
        return {"error": f"Label {label_id} not found."}

    def delete_label(self, user_id: str, label_id: str) -> Dict[str, Union[bool, str]]:
        """
        Delete a label.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            label_id (str): Label ID to delete.
        Returns:
            Dict[str, Union[bool, str]]: Dictionary indicating success/failure and message.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return {"success": False, "message": "User not found or no labels data."}
        
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return {"success": False, "message": "User not found or no labels data."}
        
        if label_id in labels:
            del labels[label_id]
            print(f"Label deleted: ID={label_id} for user {user_id}")
            return {"success": True, "message": f"Label {label_id} deleted."}
        return {"success": False, "message": f"Label {label_id} not found."}

    def modify_message(
        self, userId: str, id: str, modify_request: Dict[str, List[str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Modify a message (e.g., add/remove labels).
        Args:
            userId (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            id (str): The ID of the message to modify.
            modify_request (Dict[str, List[str]]): Dictionary with 'addLabelIds' and 'removeLabelIds'.
        Returns:
            Optional[Dict[str, Any]]: Modified message data if found, None otherwise.
        """
        userId = self._resolve_user_id(userId)
        if not userId:
            return None
        
        messages = self._get_user_messages_data(userId)
        if messages is None:
            return None
        
        message = messages.get(id)
        if not message:
            return None

        current_labels = set(message.get("labelIds", []))
        
        add_labels = set(modify_request.get("addLabelIds", []))
        remove_labels = set(modify_request.get("removeLabelIds", []))

        message["labelIds"] = list(current_labels.union(add_labels))
        message["labelIds"] = list(set(message["labelIds"]) - remove_labels)

        print(f"Message modified: ID={id}, New Labels={message['labelIds']} for user {userId}")
        return copy.deepcopy(message)

    def get_thread(
        self, user_id: str, thread_id: str, format: str = "full"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a thread with its messages.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            thread_id (str): Thread ID.
            format (str): Format of the messages ('minimal', 'full', or 'raw').
        Returns:
            Optional[Dict[str, Any]]: Thread data if found, None otherwise.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return None
        
        threads = self._get_user_threads_data(user_id)
        messages_data = self._get_user_messages_data(user_id)
        if threads is None or messages_data is None:
            return None
        
        thread = threads.get(thread_id)
        if not thread:
            return None

        thread_copy = copy.deepcopy(thread)
        detailed_messages = []
        for msg_summary in thread_copy.get("messages", []):
            msg_id = msg_summary.get("id")
            if msg_id and msg_id in messages_data:
                message = messages_data[msg_id]
                if format == "minimal":
                    detailed_messages.append({"id": message["id"], "threadId": message["threadId"], "snippet": message["snippet"]})
                elif format == "raw":
                    detailed_messages.append({"id": message["id"], "raw": "raw_content_for_" + message["id"]})
                else:
                    detailed_messages.append(copy.deepcopy(message))
        thread_copy["messages"] = detailed_messages

        return thread_copy

    def modify_thread(
        self, user_id: str, thread_id: str, modify_request: Dict[str, List[str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Modify a thread (e.g., add/remove labels to all messages in thread).
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            thread_id (str): Thread ID to modify.
            modify_request (Dict[str, List[str]]): Dictionary with 'addLabelIds' and 'removeLabelIds'.
        Returns:
            Optional[Dict[str, Any]]: Modified thread data if found, None otherwise.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return None
        
        threads = self._get_user_threads_data(user_id)
        messages = self._get_user_messages_data(user_id)
        if threads is None or messages is None:
            return None

        thread = threads.get(thread_id)
        if not thread:
            return None

        add_labels = set(modify_request.get("addLabelIds", []))
        remove_labels = set(modify_request.get("removeLabelIds", []))

        for msg_data_summary in thread.get("messages", []):
            msg_id = msg_data_summary["id"]
            if msg_id in messages:
                current_labels = set(messages[msg_id].get("labelIds", []))
                messages[msg_id]["labelIds"] = list(current_labels.union(add_labels))
                messages[msg_id]["labelIds"] = list(set(messages[msg_id]["labelIds"]) - remove_labels)
        
        print(f"Thread modified: ID={thread_id} for user {user_id}. Labels applied to contained messages.")
        
        # Get user email to call get_thread (which expects email or 'me')
        user_email = self._get_user_email_by_id(user_id)
        return self.get_thread(user_email, thread_id, format="full") if user_email else None

    def batch_delete_messages(self, user_id: str, ids: List[str]) -> Dict[str, Union[bool, str, int]]:
        """
        Delete multiple messages in a single batch operation.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            ids (List[str]): List of message IDs to delete.
        Returns:
            Dict[str, Union[bool, str, int]]: Dictionary with success status and count of deleted messages.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return {"success": False, "message": "User not found.", "deleted_count": 0}
        
        deleted_count = 0
        for msg_id in ids:
            result = self.delete_message(user_id, msg_id)
            if result.get("success"):
                deleted_count += 1
        
        print(f"Batch delete: {deleted_count}/{len(ids)} messages deleted for user {user_id}")
        return {
            "success": True,
            "message": f"Deleted {deleted_count} out of {len(ids)} messages.",
            "deleted_count": deleted_count
        }

    def batch_modify_messages(
        self, user_id: str, ids: List[str], modify_request: Dict[str, List[str]]
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Modify multiple messages in a single batch operation.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            ids (List[str]): List of message IDs to modify.
            modify_request (Dict[str, List[str]]): Dictionary with 'addLabelIds' and 'removeLabelIds'.
        Returns:
            Dict[str, Union[bool, str, int]]: Dictionary with success status and count of modified messages.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return {"success": False, "message": "User not found.", "modified_count": 0}
        
        modified_count = 0
        for msg_id in ids:
            result = self.modify_message(user_id, msg_id, modify_request)
            if result is not None:
                modified_count += 1
        
        print(f"Batch modify: {modified_count}/{len(ids)} messages modified for user {user_id}")
        return {
            "success": True,
            "message": f"Modified {modified_count} out of {len(ids)} messages.",
            "modified_count": modified_count
        }

    def get_attachment(self, user_id: str, message_id: str, attachment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a message attachment.
        Args:
            user_id (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
            message_id (str): The message ID containing the attachment.
            attachment_id (str): The attachment ID.
        Returns:
            Optional[Dict[str, Any]]: Attachment data if found, None otherwise.
        """
        user_id = self._resolve_user_id(user_id)
        if not user_id:
            return None
        
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return None
        
        message = messages.get(message_id)
        if not message:
            return None
        
        # Look for attachment in message parts
        parts = message.get("payload", {}).get("parts", [])
        for part in parts:
            if part.get("body", {}).get("attachmentId") == attachment_id:
                return {
                    "attachmentId": attachment_id,
                    "size": part.get("body", {}).get("size", 0),
                    "data": f"attachment_data_for_{attachment_id}"
                }
        
        return None

    def reset_data(self) -> Dict[str, bool]:
        """
        Reset all data to default state.

        Returns:
            Dict[str, bool]: Dictionary indicating reset status.
        """
        self._load_scenario(DEFAULT_STATE)
        print("GmailApis: All data reset to default state.")
        return {"reset_status": True}