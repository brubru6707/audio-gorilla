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
        """
        Initializes the Gmail API simulator with default state.
        
        Sets up the in-memory backend by loading default user data, messages, drafts,
        labels, and threads from the configured scenario.
        
        Side Effects:
            - Initializes users dictionary (empty initially)
            - Sets API description for tool identification
            - Sets current_user to None (requires authentication)
            - Loads DEFAULT_STATE scenario via _load_scenario
            - First user in scenario automatically set as authenticated user
            - Prints confirmation message of loaded scenario
            
        Note:
            - DEFAULT_STATE loaded from state_loader.load_default_state("GmailApis")
            - All data stored in-memory; not persisted between instances
            - Users dictionary maps internal UUID to user data
            - Each user has gmail_data containing messages, drafts, labels, threads, profile
            
        Example:
            >>> api = GmailApis()
            GmailApis: Loaded scenario with users and their UUIDs.
            >>> # First user automatically authenticated
        """
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the Gmail API, which provides core functionality for managing emails, drafts, and labels."
        self.current_user: Optional[str] = None  # Currently authenticated user ID
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a scenario with predefined users and their Gmail data.
        
        Replaces current in-memory state with scenario data including users,
        messages, drafts, labels, and threads. If no user currently authenticated,
        automatically authenticates the first user in the scenario.
        
        Args:
            scenario (Dict): Scenario data dictionary with structure:
                {
                    "users": {
                        "<user_uuid>": {
                            "email": str,
                            "gmail_data": {
                                "profile": {...},
                                "messages": {...},
                                "drafts": {...},
                                "labels": {...},
                                "threads": {...}
                            }
                        },
                        ...
                    }
                }
                
        Side Effects:
            - Replaces self.users with scenario users (or DEFAULT_STATE if missing)
            - Creates deep copy of DEFAULT_STATE to prevent mutations
            - Auto-authenticates first user if current_user is None
            - Prints confirmation message
            
        Note:
            - Falls back to DEFAULT_STATE["users"] if scenario lacks "users" key
            - Uses deep copy to preserve DEFAULT_STATE for future resets
            - First user authentication is automatic only if no user already authenticated
            - All existing data is discarded when new scenario loaded
            
        Example:
            >>> api = GmailApis()
            >>> custom_scenario = {"users": {...}}
            >>> api._load_scenario(custom_scenario)
            GmailApis: Loaded scenario with users and their UUIDs.
        """
        DEFAULT_STATE_COPY = copy.deepcopy(DEFAULT_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        # Set first user as authenticated user by default
        if self.users and not self.current_user:
            self.current_user = next(iter(self.users.keys()))
        print("GmailApis: Loaded scenario with users and their UUIDs.")

    def authenticate(self, email: str) -> Dict[str, Union[bool, str]]:
        """
        Authenticates a user and sets them as the currently active user.
        
        Looks up user by email address and sets them as current_user for subsequent
        API operations. Required before using API methods that reference "me".
        
        Args:
            email (str): The user's email address to authenticate.
                Must match an email in the users dictionary.
                Example: "alice@example.com", "bob@company.com"

        Returns:
            Dict[str, Union[bool, str]]: Authentication result with structure:
                {
                    "success": bool,  # True if authenticated, False if user not found
                    "message": str    # Confirmation or error message
                }
                
        Side Effects:
            - Sets self.current_user to the user's internal UUID on success
            - Prints confirmation message with authenticated email
            - No change to current_user if authentication fails
            
        Note:
            - Email lookup is case-sensitive
            - User must exist in self.users dictionary
            - Authentication persists until another user authenticates or reset
            - "me" keyword in other methods resolves to this authenticated user
            
        Example:
            >>> api = GmailApis()
            >>> result = api.authenticate("alice@example.com")
            GmailApis: Authenticated as alice@example.com
            >>> print(result)
            {'success': True, 'message': 'Authenticated as alice@example.com'}
            >>> 
            >>> # Failed authentication
            >>> result = api.authenticate("unknown@example.com")
            >>> print(result)
            {'success': False, 'message': 'User not found.'}
        """
        user_id = self._get_user_id_by_email(email)
        if not user_id:
            return {"success": False, "message": "User not found."}
        
        self.current_user = user_id
        print(f"GmailApis: Authenticated as {email}")
        return {"success": True, "message": f"Authenticated as {email}"}

    def _resolve_user_id(self, user_id: str) -> Optional[str]:
        """
        Resolves the special value 'me' or email address to internal user UUID.
        
        Provides flexible user identification by accepting either:
        - The special keyword "me" (resolves to current authenticated user)
        - An email address (looks up corresponding internal UUID)

        Args:
            user_id (str): User identifier to resolve.
                Valid values:
                - "me": Special value referencing current authenticated user
                - Email address: "alice@example.com", "bob@company.com"

        Returns:
            Optional[str]: Internal user UUID if found, None otherwise.
                Returns None if:
                - user_id is "me" but no user authenticated (current_user is None)
                - Email address not found in users dictionary
                Example return: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
                
        Note:
            - Used internally by most API methods to handle flexible user identification
            - "me" requires prior authentication via authenticate() method
            - Email lookup is case-sensitive
            - Returns UUID which is the key in self.users dictionary
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Resolve "me" to current user
            >>> user_uuid = api._resolve_user_id("me")
            >>> print(user_uuid)  # "user-uuid-123"
            >>> 
            >>> # Resolve email to UUID
            >>> user_uuid = api._resolve_user_id("bob@example.com")
            >>> print(user_uuid)  # "user-uuid-456"
        """
        if user_id == "me":
            return self.current_user
        
        # Must be an email address
        return self._get_user_id_by_email(user_id)

    def _generate_id(self) -> str:
        """
        Generates a unique identifier in Gmail's hexadecimal format.
        
        Creates a random 16-character hexadecimal string mimicking Gmail's
        message, draft, and label ID format.

        Returns:
            str: Generated hex ID (16 characters, lowercase).
                Format: "0123456789abcdef" (characters from 0-9 and a-f)
                Example: "a1b2c3d4e5f67890", "1234567890abcdef"
                
        Note:
            - Uses random.choices for generation (not cryptographically secure)
            - IDs are not guaranteed unique but collision probability is low
            - Used for messages, drafts, labels, and threads
            - Real Gmail IDs are longer and use different encoding
            
        Example:
            >>> api = GmailApis()
            >>> msg_id = api._generate_id()
            >>> print(len(msg_id))  # 16
            >>> print(msg_id)  # "a3f5d8c2b1e47690" (example)
        """
        import random
        return ''.join(random.choices('0123456789abcdef', k=16))
    
    def _generate_history_id(self) -> str:
        """
        Generates a history ID representing a point in the user's mailbox history.
        
        Creates a sequential-looking numeric string based on current timestamp.
        History IDs are used to track changes to the mailbox over time.

        Returns:
            str: Generated history ID as string representation of millisecond timestamp.
                Format: Numeric string (e.g., "1702465234567")
                Value increases with each call due to timestamp-based generation
                
        Note:
            - Based on current time in milliseconds since epoch
            - Not guaranteed to be strictly sequential for rapid successive calls
            - Used to track mailbox modifications and sync state
            - Real Gmail history IDs are opaque strings
            
        Example:
            >>> api = GmailApis()
            >>> history_id = api._generate_history_id()
            >>> print(history_id)  # "1702465234567" (example)
        """
        return str(int(datetime.datetime.now().timestamp() * 1000))

    def _parse_gmail_query(self, query: str, message: Dict[str, Any]) -> bool:
        """
        Parses Gmail search query operators and matches against a message.
        
        Evaluates search queries using Gmail's search syntax including operators
        like from:, to:, subject:, has:attachment, is:unread, and more.
        
        Args:
            query (str): Gmail search query string with optional operators.
                Supported operators:
                - "from:<email>": Match sender email
                - "to:<email>": Match recipient email
                - "subject:<text>": Match subject line
                - "has:attachment": Match messages with attachments
                - "is:unread": Match unread messages
                - "is:read": Match read messages
                - "is:starred": Match starred messages
                - "after:<date>": Match messages after date (not fully implemented)
                - "before:<date>": Match messages before date (not fully implemented)
                - "-<term>": Negation operator (exclude term from snippet)
                - Plain text: Searches in snippet and subject
                Example: "from:alice@example.com subject:meeting"
                Example: "has:attachment is:unread"
                Example: "project -archived"
            message (Dict[str, Any]): Message resource to match against.
                Must contain standard Gmail message structure:
                - "payload": {"headers": [{"name": str, "value": str}], "parts": [...]}
                - "snippet": str (message preview text)
                - "labelIds": List[str]

        Returns:
            bool: True if message matches all query criteria, False otherwise.
                Empty query returns True (matches all messages)
                
        Note:
            - Empty or None query matches all messages
            - Multiple operators are AND-ed together (all must match)
            - Header matching is case-insensitive
            - Attachment detection checks for payload.parts (simplified)
            - Negation (-term) only checks snippet, not all fields
            - Plain keyword search (no operators) checks snippet and subject
            - Value quotes in operators are stripped (subject:"test" becomes subject:test)
            - Partial string matching used (substring match)
            
        Example:
            >>> api = GmailApis()
            >>> message = {
            ...     "snippet": "Meeting agenda for project review",
            ...     "labelIds": ["INBOX", "UNREAD"],
            ...     "payload": {
            ...         "headers": [
            ...             {"name": "From", "value": "alice@example.com"},
            ...             {"name": "Subject", "value": "Project Meeting"}
            ...         ]
            ...     }
            ... }
            >>> 
            >>> # Simple keyword search
            >>> api._parse_gmail_query("meeting", message)  # True
            >>> 
            >>> # Operator search
            >>> api._parse_gmail_query("from:alice@example.com", message)  # True
            >>> api._parse_gmail_query("is:unread", message)  # True
            >>> 
            >>> # Combined operators
            >>> api._parse_gmail_query("from:alice subject:meeting", message)  # True
            >>> 
            >>> # Negation
            >>> api._parse_gmail_query("meeting -archived", message)  # True
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
        Decodes base64url encoded email content and extracts message fields.
        
        Parses raw email content in RFC 2822 format or JSON format, extracting
        recipient, subject, and body. Used when processing raw email data from
        send/draft operations.

        Args:
            raw_content (str): Base64url encoded email content.
                Can be:
                - Base64url encoded JSON: {"to": str, "subject": str, "body": str}
                - Base64url encoded RFC 2822 email format:
                    To: recipient@example.com
                    Subject: Email subject
                    
                    Email body content
                Example: "eyJ0byI6ICJib2JAZXhhbXBsZS5jb20iLCAic3ViamVjdCI6ICJUZXN0In0="

        Returns:
            Dict[str, str]: Decoded message fields with structure:
                {
                    "to": str,      # Recipient email address
                    "subject": str,  # Email subject line
                    "body": str      # Email body content
                }
                Returns empty strings for all fields if decoding fails:
                {"to": "", "subject": "", "body": ""}
                
        Note:
            - Attempts JSON parsing first, then falls back to RFC 2822 format
            - Base64url decoding uses urlsafe_b64decode
            - RFC 2822 parsing looks for "To:", "Subject:" headers and body after blank line
            - Returns empty dict with empty string values on any decode error
            - Body extraction in RFC format: everything after first blank line
            - Case-insensitive header matching
            - Mock implementation for testing; real Gmail uses complex MIME parsing
            
        Example:
            >>> api = GmailApis()
            >>> import base64
            >>> import json
            >>> 
            >>> # JSON format
            >>> data = {"to": "bob@example.com", "subject": "Test", "body": "Hello"}
            >>> raw = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
            >>> result = api._decode_raw_message(raw)
            >>> print(result)
            {'to': 'bob@example.com', 'subject': 'Test', 'body': 'Hello'}
            >>> 
            >>> # RFC 2822 format
            >>> email_text = "To: bob@example.com\nSubject: Test\n\nHello"
            >>> raw = base64.urlsafe_b64encode(email_text.encode()).decode()
            >>> result = api._decode_raw_message(raw)
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
        Retrieves internal user UUID by email address lookup.
        
        Searches through users dictionary to find user with matching email.

        Args:
            email (str): User's email address to look up.
                Case-sensitive match.
                Example: "alice@example.com"

        Returns:
            Optional[str]: Internal user UUID if found, None otherwise.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
                Returns None if no user has the specified email
                
        Example:
            >>> api = GmailApis()
            >>> user_id = api._get_user_id_by_email("alice@example.com")
            >>> print(user_id)  # "user-uuid-123"
        """
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """
        Retrieves user email address by internal UUID lookup.
        
        Reverse lookup of _get_user_id_by_email, converting UUID to email.

        Args:
            user_id (str): Internal user UUID.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[str]: User's email address if found, None otherwise.
                Example: "alice@example.com"
                Returns None if user_id not found in users dictionary
                
        Example:
            >>> api = GmailApis()
            >>> email = api._get_user_email_by_id("user-uuid-123")
            >>> print(email)  # "alice@example.com"
        """
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _get_user_gmail_data(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves the complete Gmail data structure for a user.
        
        Returns the gmail_data dictionary containing messages, drafts, labels,
        threads, and profile information.

        Args:
            user_id (str): The internal user UUID.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[Dict]: User's Gmail data dictionary if found, None otherwise.
                Structure: {
                    "profile": {...},
                    "messages": {...},
                    "drafts": {...},
                    "labels": {...},
                    "threads": {...}
                }
                Returns None if user not found or has no gmail_data
                
        Note:
            Returns reference to actual data (not copy), allowing direct modification
            
        Example:
            >>> api = GmailApis()
            >>> gmail_data = api._get_user_gmail_data("user-uuid-123")
            >>> if gmail_data:
            ...     print(f"User has {len(gmail_data['messages'])} messages")
        """
        return self.users.get(user_id, {}).get("gmail_data")

    def _get_user_threads_data(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves the threads data structure for a user.
        
        Returns dictionary mapping thread IDs to thread data including messages and snippets.

        Args:
            user_id (str): The internal user UUID.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[Dict]: User's threads dictionary if found, None otherwise.
                Structure: {
                    "<thread_id>": {
                        "id": str,
                        "snippet": str,
                        "historyId": str,
                        "messages": [{"id": str}, ...]
                    },
                    ...
                }
                Returns None if user not found or has no gmail_data
                
        Example:
            >>> api = GmailApis()
            >>> threads = api._get_user_threads_data("user-uuid-123")
            >>> if threads:
            ...     print(f"User has {len(threads)} threads")
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("threads") if gmail_data else None

    def _get_user_messages_data(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves the messages data structure for a user.
        
        Returns dictionary mapping message IDs to complete message resources.

        Args:
            user_id (str): The internal user UUID.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[Dict]: User's messages dictionary if found, None otherwise.
                Structure: {
                    "<message_id>": {
                        "id": str,
                        "threadId": str,
                        "labelIds": List[str],
                        "snippet": str,
                        "payload": {...},
                        "internalDate": str,
                        "historyId": str,
                        ...
                    },
                    ...
                }
                Returns None if user not found or has no gmail_data
                
        Example:
            >>> api = GmailApis()
            >>> messages = api._get_user_messages_data("user-uuid-123")
            >>> if messages:
            ...     for msg_id, msg in messages.items():
            ...         print(f"{msg_id}: {msg['snippet']}")
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("messages") if gmail_data else None

    def _get_user_drafts_data(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves the drafts data structure for a user.
        
        Returns dictionary mapping draft IDs to draft resources.

        Args:
            user_id (str): The internal user UUID.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[Dict]: User's drafts dictionary if found, None otherwise.
                Structure: {
                    "<draft_id>": {
                        "id": str,
                        "message": {
                            "to": str,
                            "subject": str,
                            "body": str
                        }
                    },
                    ...
                }
                Returns None if user not found or has no gmail_data
                
        Example:
            >>> api = GmailApis()
            >>> drafts = api._get_user_drafts_data("user-uuid-123")
            >>> if drafts:
            ...     print(f"User has {len(drafts)} drafts")
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("drafts") if gmail_data else None

    def _get_user_labels_data(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves the labels data structure for a user.
        
        Returns dictionary mapping label IDs to label resources including
        system labels (INBOX, SENT, etc.) and user-created labels.

        Args:
            user_id (str): The internal user UUID.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[Dict]: User's labels dictionary if found, None otherwise.
                Structure: {
                    "<label_id>": {
                        "id": str,
                        "name": str,
                        "type": str,  # "system" or "user"
                        "messageListVisibility": str,
                        "labelListVisibility": str
                    },
                    ...
                }
                Returns None if user not found or has no gmail_data
                
        Example:
            >>> api = GmailApis()
            >>> labels = api._get_user_labels_data("user-uuid-123")
            >>> if labels:
            ...     for label in labels.values():
            ...         print(f"{label['name']} ({label['type']})")
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("labels") if gmail_data else None

    def _update_thread_snippet(self, user_id: str, thread_id: str) -> None:
        """
        Updates a thread's snippet with the most recent message content.
        
        Finds the latest message in the thread by timestamp and updates the
        thread's snippet field to match. Used after message deletion or modification.

        Args:
            user_id (str): The internal user UUID.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
            thread_id (str): Thread ID to update.
                Example: "thread123456"
                
        Returns:
            None: This method doesn't return a value.
                
        Side Effects:
            - Updates thread's snippet field with latest message snippet
            - No change if thread not found, has no messages, or messages not found
            - Silently returns if user has no threads or messages data
            
        Note:
            - Compares messages by internalDate field (millisecond timestamp)
            - Only updates if valid message found with snippet
            - Used internally after message deletion to keep thread preview current
            - Does not modify messages, only thread metadata
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> # After deleting a message from a thread
            >>> api._update_thread_snippet("user-uuid-123", "thread-456")
            >>> # Thread snippet now reflects most recent remaining message
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
        Retrieves the Gmail profile information for a user.
        
        Returns profile data including email address, message counts, and history ID.
        Commonly used to get basic account information.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"

        Returns:
            Optional[Dict[str, Any]]: User's profile data if found, None otherwise.
                Structure: {
                    "emailAddress": str,
                    "messagesTotal": int,
                    "threadsTotal": int,
                    "historyId": str
                }
                Returns None if user not found or has no gmail_data
                
        Note:
            - "me" resolves to currently authenticated user
            - Profile contains summary statistics, not detailed message data
            - messagesTotal and threadsTotal reflect current counts
            - historyId tracks mailbox state for synchronization
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> profile = api.get_profile("me")
            >>> print(f"Email: {profile['emailAddress']}")
            >>> print(f"Messages: {profile['messagesTotal']}")
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
        Lists messages in the user's mailbox matching specified criteria.
        
        Supports filtering by search query, labels, and pagination. Returns
        minimal message data (id and threadId) for efficiency.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            q (Optional[str]): Gmail search query string.
                Supports operators: from:, to:, subject:, has:attachment, is:unread, etc.
                Examples: "from:alice@example.com", "is:unread has:attachment"
                Default: None (no query filter)
            label_ids (Optional[List[str]]): Filter by label IDs (all must match).
                Examples: ["INBOX"], ["INBOX", "UNREAD"], ["Label_123"]
                Default: None (no label filter)
            page_token (Optional[str]): Token for retrieving specific page.
                Obtained from nextPageToken in previous response.
                Value is string representation of start index.
                Default: None (start from beginning)
            max_results (int): Maximum number of messages per page.
                Range: 1-500
                Default: 100
            includeSpamTrash (bool): Whether to include SPAM and TRASH messages.
                If False, messages with SPAM or TRASH labels are excluded.
                Default: False

        Returns:
            Dict[str, Union[List[Dict], str, int]]: Results dictionary with structure:
                {
                    "messages": [
                        {
                            "id": str,        # Message ID
                            "threadId": str   # Thread ID
                        },
                        ...
                    ],
                    "nextPageToken": str,    # Present if more results available
                    "resultSizeEstimate": int  # Total matching messages count
                }
                
        Note:
            - Returns empty list if user not found or has no messages
            - Multiple label_ids are AND-ed (message must have all labels)
            - Search query parsed by _parse_gmail_query method
            - SPAM and TRASH filtered unless includeSpamTrash=True
            - nextPageToken only present when more results available
            - resultSizeEstimate is total count, not just current page
            - Messages returned in storage order (not sorted by date)
            - Use get_message() to retrieve full message details
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # List all inbox messages
            >>> result = api.list_messages("me", label_ids=["INBOX"])
            >>> print(f"Found {result['resultSizeEstimate']} messages")
            >>> for msg in result['messages']:
            ...     print(f"Message ID: {msg['id']}")
            >>> 
            >>> # Search for unread messages
            >>> result = api.list_messages("me", q="is:unread")
            >>> 
            >>> # Pagination
            >>> page1 = api.list_messages("me", max_results=10)
            >>> if 'nextPageToken' in page1:
            ...     page2 = api.list_messages("me", max_results=10, page_token=page1['nextPageToken'])
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
        Retrieves a specific message by ID with configurable detail level.
        
        Returns message data in requested format: minimal (IDs only),
        metadata (headers and labels), raw (base64 content), or full (complete resource).

        Args:
            userId (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            id (str): The message ID to retrieve.
                Format: 16-character hexadecimal string
                Example: "a1b2c3d4e5f67890"
            format (str): Response format level.
                Valid values:
                - "minimal": Returns only id and threadId
                - "metadata": Returns id, threadId, labels, snippet, and headers
                - "raw": Returns id, threadId, and raw base64url content
                - "full": Returns complete message resource with all fields
                Default: "full"

        Returns:
            Optional[Dict[str, Any]]: Message data if found, None otherwise.
                
                Minimal format structure:
                {
                    "id": str,
                    "threadId": str
                }
                
                Metadata format structure:
                {
                    "id": str,
                    "threadId": str,
                    "labelIds": List[str],
                    "snippet": str,
                    "historyId": str,
                    "internalDate": str,
                    "payload": {
                        "mimeType": str,
                        "headers": [{"name": str, "value": str}, ...]
                    },
                    "sizeEstimate": int
                }
                
                Raw format structure:
                {
                    "id": str,
                    "threadId": str,
                    "historyId": str,
                    "internalDate": str,
                    "raw": str  # Base64url encoded email content
                }
                
                Full format: Complete message resource with all fields
                Returns None if user or message not found
                
        Note:
            - Full format returns deep copy to prevent accidental modification
            - Raw format generates placeholder content ("raw_content_for_{id}")
            - Metadata format ideal for displaying message lists
            - Minimal format most efficient for ID-only operations
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Get full message
            >>> msg = api.get_message("me", "a1b2c3d4e5f67890")
            >>> print(f"Subject: {[h['value'] for h in msg['payload']['headers'] if h['name']=='Subject'][0]}")
            >>> 
            >>> # Get just headers
            >>> msg = api.get_message("me", "a1b2c3d4e5f67890", format="metadata")
            >>> print(f"Snippet: {msg['snippet']}")
            >>> 
            >>> # Get minimal data
            >>> msg = api.get_message("me", "a1b2c3d4e5f67890", format="minimal")
            >>> print(f"Thread: {msg['threadId']}")
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
        Sends an email message from the authenticated user's mailbox.
        
        Creates and sends a new email, storing it in sender's SENT folder and
        recipient's INBOX (if recipient exists in system). Supports raw RFC 2822
        format or structured message fields.

        Args:
            userId (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            message (Dict[str, Any]): Message resource to send.
                Preferred format (with raw field):
                {
                    "raw": str,  # Base64url encoded RFC 2822 email
                    "threadId": str  # Optional: add to existing thread
                }
                
                Alternative format (backward compatibility):
                {
                    "to": str,       # Recipient email
                    "subject": str,  # Email subject
                    "body": str,     # Email body text
                    "threadId": str  # Optional: add to existing thread
                }
                
                Raw field format:
                - Base64url encoded email in RFC 2822 format
                - Can contain JSON: {"to": str, "subject": str, "body": str}
                - Or RFC 2822 headers and body

        Returns:
            Dict[str, Union[str, Dict]]: Send result with structure:
                Success:
                {
                    "id": str,        # New message ID
                    "threadId": str   # Thread ID (new or existing)
                }
                Error:
                {
                    "error": str  # Error description
                }
                
        Side Effects:
            - Creates new message in sender's mailbox with SENT and INBOX labels
            - Creates or updates thread in sender's mailbox
            - If recipient exists in system:
                * Creates copy of message in recipient's mailbox with INBOX and UNREAD labels
                * Creates or updates thread in recipient's mailbox
            - Updates sender's profile message and thread counts
            - Updates recipient's profile counts (if recipient in system)
            - Generates unique message ID and history ID
            - Sets internalDate to current timestamp
            - Prints confirmation with sender, recipient, and subject
            
        Note:
            - Message ID is auto-generated (16-char hex)
            - Thread ID is auto-generated if not provided
            - If raw field present, decodes using _decode_raw_message
            - Falls back to direct to/subject/body fields if no raw content
            - Recipient delivery only if recipient email exists in users dictionary
            - Message stored in both sender and recipient mailboxes
            - Thread snippet updated to latest message
            - Size estimate calculated from body and headers
            - Supports adding message to existing thread via threadId
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Send with raw format
            >>> import base64
            >>> import json
            >>> msg_data = {"to": "bob@example.com", "subject": "Hello", "body": "Hi Bob!"}
            >>> raw_content = base64.urlsafe_b64encode(json.dumps(msg_data).encode()).decode()
            >>> result = api.send_message("me", {"raw": raw_content})
            Email sent: from alice@example.com to bob@example.com, subject 'Hello'
            >>> print(f"Sent message: {result['id']}")
            >>> 
            >>> # Send with direct fields (backward compatibility)
            >>> result = api.send_message("me", {
            ...     "to": "carol@example.com",
            ...     "subject": "Meeting",
            ...     "body": "Let's meet tomorrow"
            ... })
            >>> 
            >>> # Reply to thread
            >>> result = api.send_message("me", {
            ...     "to": "bob@example.com",
            ...     "subject": "Re: Hello",
            ...     "body": "Hi Alice!",
            ...     "threadId": "thread123456"
            ... })
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
        Permanently deletes a message from the user's mailbox.
        
        Removes message and updates thread. If message is the last in its thread,
        deletes the thread as well. Otherwise updates thread snippet.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            msg_id (str): Message ID to delete.
                Format: 16-character hexadecimal string
                Example: "a1b2c3d4e5f67890"

        Returns:
            Dict[str, Union[bool, str]]: Deletion result with structure:
                Success:
                {
                    "success": True,
                    "message": "Message {msg_id} deleted."
                }
                Failure:
                {
                    "success": False,
                    "message": "User not found." | "Message {msg_id} not found."
                }
                
        Side Effects:
            - Removes message from user's messages dictionary
            - Removes message from its thread's messages list
            - If thread becomes empty, deletes the thread
            - If thread has remaining messages, updates thread snippet to latest message
            - Decrements user profile messagesTotal count
            - Updates profile threadsTotal count if thread deleted
            - Prints confirmation with message ID and user ID
            
        Note:
            - Deletion is permanent; no trash/recovery mechanism
            - Thread automatically cleaned up when last message deleted
            - Thread snippet updated via _update_thread_snippet if messages remain
            - Profile counts kept in sync with actual message/thread counts
            - No cascade delete to recipient's copy (if exists)
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Delete a message
            >>> result = api.delete_message("me", "a1b2c3d4e5f67890")
            Message deleted: ID=a1b2c3d4e5f67890 for user user-uuid-123
            >>> print(result)
            {'success': True, 'message': 'Message a1b2c3d4e5f67890 deleted.'}
            >>> 
            >>> # Try to delete non-existent message
            >>> result = api.delete_message("me", "invalid-id")
            >>> print(result)
            {'success': False, 'message': 'Message invalid-id not found.'}
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
        Lists draft messages in the user's mailbox with pagination support.
        
        Returns summary information for drafts including IDs and message data.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            page_token (Optional[str]): Token for retrieving specific page.
                Obtained from nextPageToken in previous response.
                Value is string representation of start index.
                Default: None (start from beginning)
            max_results (int): Maximum number of drafts per page.
                Default: 10

        Returns:
            Dict[str, Union[List[Dict], str, int]]: Results dictionary with structure:
                {
                    "drafts": [
                        {
                            "id": str,
                            "message": {
                                "to": str,
                                "subject": str,
                                "body": str
                            }
                        },
                        ...
                    ],
                    "nextPageToken": str,       # Present if more results available
                    "resultSizeEstimate": int   # Total draft count
                }
                Returns empty list if user not found or has no drafts
                
        Note:
            - Returns empty list if user not found
            - nextPageToken only present when more results available
            - resultSizeEstimate is total count, not just current page
            - Drafts returned in storage order
            - Page token is simple numeric index (not opaque)
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # List all drafts
            >>> result = api.list_drafts("me")
            >>> print(f"Found {result['resultSizeEstimate']} drafts")
            >>> for draft in result['drafts']:
            ...     print(f"Draft {draft['id']}: {draft['message']['subject']}")
            >>> 
            >>> # Pagination
            >>> page1 = api.list_drafts("me", max_results=5)
            >>> if 'nextPageToken' in page1:
            ...     page2 = api.list_drafts("me", max_results=5, page_token=page1['nextPageToken'])
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
        Retrieves a specific draft by its ID.
        
        Returns complete draft resource including message content.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            draft_id (str): Draft ID to retrieve.
                Format: 16-character hexadecimal string
                Example: "a1b2c3d4e5f67890"

        Returns:
            Optional[Dict[str, Any]]: Draft resource if found, None otherwise.
                Structure:
                {
                    "id": str,
                    "message": {
                        "to": str,
                        "subject": str,
                        "body": str
                    }
                }
                Returns None if user not found or draft doesn't exist
                
        Note:
            - Returns deep copy to prevent accidental modification
            - Draft message contains to, subject, and body fields
            - No validation of message fields (can be incomplete)
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Get a draft
            >>> draft = api.get_draft("me", "a1b2c3d4e5f67890")
            >>> if draft:
            ...     print(f"To: {draft['message']['to']}")
            ...     print(f"Subject: {draft['message']['subject']}")
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
        Creates a new draft message in the user's mailbox.
        
        Stores draft with message content for later sending or editing.

        Args:
            userId (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            draft (Dict[str, Any]): Draft resource to create.
                Structure:
                {
                    "message": {
                        "to": str,       # Recipient email
                        "subject": str,  # Email subject
                        "body": str      # Email body text
                    }
                }
                
                Alternative (with raw content):
                {
                    "message": {
                        "raw": str  # Base64url encoded email
                    }
                }

        Returns:
            Dict[str, Union[str, Dict]]: Creation result with structure:
                Success:
                {
                    "id": str,
                    "message": {
                        "to": str,
                        "subject": str,
                        "body": str
                    }
                }
                Error:
                {
                    "error": str  # Error description
                }
                
        Side Effects:
            - Generates new draft ID (16-char hex)
            - Stores draft in user's drafts dictionary
            - If raw content provided, decodes using _decode_raw_message
            - Prints confirmation with draft ID and user ID
            
        Note:
            - Draft ID is auto-generated
            - Supports both structured message and raw format
            - Raw content decoded to extract to, subject, body fields
            - No validation of email addresses or content
            - Draft persists until sent or deleted
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Create draft with structured message
            >>> draft_body = {
            ...     "message": {
            ...         "to": "bob@example.com",
            ...         "subject": "Draft Email",
            ...         "body": "This is a draft"
            ...     }
            ... }
            >>> result = api.create_draft("me", draft_body)
            Draft created: ID=a1b2c3d4e5f67890 for user user-uuid-123
            >>> print(f"Draft ID: {result['id']}")
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
        Updates an existing draft with new message content.
        
        Replaces draft's message fields (to, subject, body) with new values.

        Args:
            userId (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            id (str): The draft ID to update.
                Format: 16-character hexadecimal string
                Example: "a1b2c3d4e5f67890"
            draft (Dict[str, Any]): Updated draft resource.
                Structure:
                {
                    "message": {
                        "to": str,       # New recipient email
                        "subject": str,  # New subject
                        "body": str      # New body text
                    }
                }
                
                Alternative (with raw content):
                {
                    "message": {
                        "raw": str  # Base64url encoded email
                    }
                }

        Returns:
            Dict[str, Union[str, Dict]]: Update result with structure:
                Success:
                {
                    "id": str,
                    "message": {
                        "to": str,
                        "subject": str,
                        "body": str
                    }
                }
                Error:
                {
                    "error": str  # "User not found or no drafts data." | "Draft {id} not found."
                }
                
        Side Effects:
            - Updates draft's message.to, message.subject, and message.body fields
            - If raw content provided, decodes to extract fields
            - Prints confirmation with draft ID and user ID
            
        Note:
            - Draft ID remains unchanged
            - All message fields replaced (not merged)
            - Supports both structured and raw message format
            - No validation of email addresses or content
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Update draft
            >>> updated_draft = {
            ...     "message": {
            ...         "to": "carol@example.com",
            ...         "subject": "Updated Subject",
            ...         "body": "Updated body content"
            ...     }
            ... }
            >>> result = api.update_draft("me", "a1b2c3d4e5f67890", updated_draft)
            Draft updated: ID=a1b2c3d4e5f67890 for user user-uuid-123
            >>> print(f"Updated: {result['message']['subject']}")
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
        Permanently deletes a draft from the user's mailbox.
        
        Removes draft completely. Cannot be undone.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            draft_id (str): Draft ID to delete.
                Format: 16-character hexadecimal string
                Example: "a1b2c3d4e5f67890"

        Returns:
            Dict[str, Union[bool, str]]: Deletion result with structure:
                Success:
                {
                    "success": True,
                    "message": "Draft {draft_id} deleted."
                }
                Failure:
                {
                    "success": False,
                    "message": "User not found or no drafts data." | "Draft {draft_id} not found."
                }
                
        Side Effects:
            - Removes draft from user's drafts dictionary
            - Prints confirmation with draft ID and user ID
            
        Note:
            - Deletion is permanent; no recovery mechanism
            - No cascade effects to other data
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Delete a draft
            >>> result = api.delete_draft("me", "a1b2c3d4e5f67890")
            Draft deleted: ID=a1b2c3d4e5f67890 for user user-uuid-123
            >>> print(result)
            {'success': True, 'message': 'Draft a1b2c3d4e5f67890 deleted.'}
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
        Sends a draft message as an email and deletes the draft.
        
        Converts draft to sent message, delivering to recipient if they exist
        in the system, then removes the draft.

        Args:
            userId (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            id (str): The draft ID to send.
                Format: 16-character hexadecimal string
                Example: "a1b2c3d4e5f67890"

        Returns:
            Dict[str, Union[str, Dict]]: Send result with structure:
                Success:
                {
                    "id": str,        # New message ID (generated)
                    "threadId": str   # Thread ID
                }
                Error:
                {
                    "error": str  # Error description:
                                  # - "User not found or no drafts data."
                                  # - "Draft {id} not found."
                                  # - "Draft has no recipient specified."
                }
                
        Side Effects:
            - Creates new sent message via send_message() method
            - Deletes draft via delete_draft() method on successful send
            - Message appears in sender's SENT and INBOX
            - If recipient exists, appears in their INBOX with UNREAD label
            - Updates message and thread counts for sender (and recipient if in system)
            - Prints confirmation with draft ID and message ID
            
        Note:
            - Draft deleted only after successful message send
            - Requires draft to have "to" field populated
            - Uses send_message internally, inheriting its behavior
            - New message ID generated (not same as draft ID)
            - Draft and message are separate objects
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Create and send a draft
            >>> draft_result = api.create_draft("me", {
            ...     "message": {
            ...         "to": "bob@example.com",
            ...         "subject": "Hello",
            ...         "body": "Draft message"
            ...     }
            ... })
            >>> draft_id = draft_result['id']
            >>> 
            >>> # Send the draft
            >>> result = api.send_draft("me", draft_id)
            Email sent: from alice@example.com to bob@example.com, subject 'Hello'
            Draft deleted: ID=a1b2c3d4e5f67890 for user user-uuid-123
            Draft sent and deleted: draft ID=a1b2c3d4e5f67890, message ID=f9e8d7c6b5a43210
            >>> print(f"Message sent: {result['id']}")
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
        Lists all labels in the user's mailbox including system and user labels.
        
        Returns both system labels (INBOX, SENT, etc.) and user-created labels.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"

        Returns:
            Dict[str, Union[List[Dict], str]]: Results dictionary with structure:
                {
                    "labels": [
                        {
                            "id": str,
                            "name": str,
                            "type": str,  # "system" or "user"
                            "messageListVisibility": str,
                            "labelListVisibility": str
                        },
                        ...
                    ]
                }
                Returns empty list if user not found or has no labels
                
        Note:
            - Returns deep copies to prevent accidental modification
            - System labels: INBOX, SENT, DRAFTS, TRASH, SPAM, UNREAD, STARRED, etc.
            - User labels have type="user"
            - No pagination (returns all labels)
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # List all labels
            >>> result = api.list_labels("me")
            >>> for label in result['labels']:
            ...     print(f"{label['name']} ({label['type']})")
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
        Retrieves a specific label by its ID.
        
        Returns complete label resource including visibility settings.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            label_id (str): Label ID to retrieve.
                Can be system label (e.g., "INBOX", "SENT") or user label ID
                Example: "INBOX", "a1b2c3d4e5f67890"

        Returns:
            Optional[Dict[str, Any]]: Label resource if found, None otherwise.
                Structure:
                {
                    "id": str,
                    "name": str,
                    "type": str,  # "system" or "user"
                    "messageListVisibility": str,  # "show" or "hide"
                    "labelListVisibility": str     # "show" or "hide"
                }
                Returns None if user not found or label doesn't exist
                
        Note:
            - Returns deep copy to prevent accidental modification
            - System labels have predefined IDs (INBOX, SENT, etc.)
            - User labels have generated hex IDs
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Get inbox label
            >>> label = api.get_label("me", "INBOX")
            >>> print(f"Label: {label['name']}")
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
        Creates a new user label with specified name.
        
        Generates unique label ID and creates label with default visibility settings.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            label_name (str): Name for the new label.
                Can contain spaces and special characters.
                Example: "Work Projects", "Important - 2025"

        Returns:
            Dict[str, Union[str, Dict]]: Creation result with structure:
                Success:
                {
                    "id": str,    # Generated label ID
                    "name": str   # Label name
                }
                Error:
                {
                    "error": str  # "User not found." | "Gmail data not available for user."
                }
                
        Side Effects:
            - Generates new label ID (16-char hex)
            - Creates label with type="user"
            - Sets messageListVisibility="show"
            - Sets labelListVisibility="show"
            - Initializes labels dictionary if doesn't exist
            - Prints confirmation with label ID, name, and user ID
            
        Note:
            - Label ID is auto-generated
            - No duplicate name checking
            - Cannot create system labels (INBOX, SENT, etc.)
            - Label immediately available for use
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Create a label
            >>> result = api.create_label("me", "Work Projects")
            Label created: ID=a1b2c3d4e5f67890, Name='Work Projects' for user user-uuid-123
            >>> print(f"Label ID: {result['id']}")
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
        Updates a label's name.
        
        Renames an existing user label. Cannot rename system labels.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            label_id (str): Label ID to update.
                Must be user label ID (cannot update system labels)
                Example: "a1b2c3d4e5f67890"
            new_label_name (str): New name for the label.
                Example: "Updated Project Name"

        Returns:
            Dict[str, Union[str, Dict]]: Update result with structure:
                Success:
                {
                    "id": str,    # Label ID (unchanged)
                    "name": str   # New label name
                }
                Error:
                {
                    "error": str  # "User not found or no labels data." | "Label {label_id} not found."
                }
                
        Side Effects:
            - Updates label's name field
            - Prints confirmation with label ID, new name, and user ID
            
        Note:
            - Label ID remains unchanged
            - Other label properties (visibility, type) unchanged
            - No validation on new name (can duplicate existing names)
            - System labels should not be updated but not explicitly prevented
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Update label name
            >>> result = api.update_label("me", "a1b2c3d4e5f67890", "Updated Projects")
            Label updated: ID=a1b2c3d4e5f67890, New Name='Updated Projects' for user user-uuid-123
            >>> print(f"Updated: {result['name']}")
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
        Permanently deletes a user label.
        
        Removes label from user's labels. Does not remove label from messages
        (messages with this label will retain it until modified).

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            label_id (str): Label ID to delete.
                Must be user label (should not delete system labels)
                Example: "a1b2c3d4e5f67890"

        Returns:
            Dict[str, Union[bool, str]]: Deletion result with structure:
                Success:
                {
                    "success": True,
                    "message": "Label {label_id} deleted."
                }
                Failure:
                {
                    "success": False,
                    "message": "User not found or no labels data." | "Label {label_id} not found."
                }
                
        Side Effects:
            - Removes label from user's labels dictionary
            - Does NOT remove label from messages automatically
            - Prints confirmation with label ID and user ID
            
        Note:
            - Deletion is permanent
            - System labels (INBOX, SENT, etc.) should not be deleted
            - Messages with deleted label ID will still reference it
            - Consider removing label from all messages before deletion
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Delete a label
            >>> result = api.delete_label("me", "a1b2c3d4e5f67890")
            Label deleted: ID=a1b2c3d4e5f67890 for user user-uuid-123
            >>> print(result)
            {'success': True, 'message': 'Label a1b2c3d4e5f67890 deleted.'}
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
        Modifies a message's labels by adding or removing specified labels.
        
        Supports bulk label operations on a single message without retrieving
        full message content.

        Args:
            userId (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            id (str): The message ID to modify.
                Format: 16-character hexadecimal string
                Example: "a1b2c3d4e5f67890"
            modify_request (Dict[str, List[str]]): Label modification specification.
                Structure:
                {
                    "addLabelIds": List[str],     # Labels to add
                    "removeLabelIds": List[str]   # Labels to remove
                }
                Either field can be omitted or empty list.
                Example: {"addLabelIds": ["STARRED"], "removeLabelIds": ["UNREAD"]}

        Returns:
            Optional[Dict[str, Any]]: Modified message resource if found, None otherwise.
                Returns complete message with updated labelIds field.
                Returns None if user or message not found.
                
        Side Effects:
            - Adds labels from addLabelIds to message's labelIds
            - Removes labels from removeLabelIds from message's labelIds
            - Label changes are applied atomically (add then remove)
            - Prints confirmation with message ID, new labels, and user ID
            
        Note:
            - Returns deep copy to prevent accidental modification
            - Add operation happens before remove operation
            - Duplicate labels in labelIds are automatically deduplicated
            - No validation that label IDs exist
            - System and user labels can both be modified
            - Common use: marking as read (remove UNREAD), starring (add STARRED)
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Mark message as read and starred
            >>> result = api.modify_message("me", "a1b2c3d4e5f67890", {
            ...     "addLabelIds": ["STARRED"],
            ...     "removeLabelIds": ["UNREAD"]
            ... })
            Message modified: ID=a1b2c3d4e5f67890, New Labels=['INBOX', 'STARRED'] for user user-uuid-123
            >>> 
            >>> # Add custom label
            >>> result = api.modify_message("me", "a1b2c3d4e5f67890", {
            ...     "addLabelIds": ["Label_abc123"]
            ... })
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
        Retrieves a thread with all its messages in specified format.
        
        Returns thread metadata and associated messages with configurable detail level.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            thread_id (str): Thread ID to retrieve.
                Format: 16-character hexadecimal string
                Example: "thread123456"
            format (str): Format for message details within thread.
                Valid values:
                - "minimal": Returns id, threadId, and snippet for each message
                - "full": Returns complete message resource for each message
                - "raw": Returns id and raw content for each message
                Default: "full"

        Returns:
            Optional[Dict[str, Any]]: Thread resource if found, None otherwise.
                Structure:
                {
                    "id": str,
                    "snippet": str,       # Preview from latest message
                    "historyId": str,
                    "messages": [         # Array of message objects
                        {                 # Format depends on 'format' parameter
                            # Minimal: {"id": str, "threadId": str, "snippet": str}
                            # Full: Complete message resource
                            # Raw: {"id": str, "raw": str}
                        },
                        ...
                    ]
                }
                Returns None if user not found or thread doesn't exist
                
        Note:
            - Returns deep copy to prevent accidental modification
            - Messages in thread returned in array (not guaranteed sorted)
            - Message format controlled by format parameter
            - Thread snippet reflects latest message content
            - Messages that don't exist in storage are skipped
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Get full thread with all message details
            >>> thread = api.get_thread("me", "thread123456")
            >>> print(f"Thread has {len(thread['messages'])} messages")
            >>> for msg in thread['messages']:
            ...     print(f"Message: {msg['snippet']}")
            >>> 
            >>> # Get minimal thread for efficiency
            >>> thread = api.get_thread("me", "thread123456", format="minimal")
            >>> for msg in thread['messages']:
            ...     print(f"{msg['id']}: {msg['snippet']}")
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
        Modifies labels for all messages in a thread.
        
        Applies label additions/removals to every message in the thread,
        providing bulk operations at thread level.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            thread_id (str): Thread ID to modify.
                Format: 16-character hexadecimal string
                Example: "thread123456"
            modify_request (Dict[str, List[str]]): Label modification specification.
                Structure:
                {
                    "addLabelIds": List[str],     # Labels to add to all messages
                    "removeLabelIds": List[str]   # Labels to remove from all messages
                }
                Either field can be omitted or empty list.
                Example: {"addLabelIds": ["IMPORTANT"], "removeLabelIds": ["UNREAD"]}

        Returns:
            Optional[Dict[str, Any]]: Modified thread resource with full message details, None if not found.
                Returns complete thread resource via get_thread(format="full")
                Returns None if user or thread not found
                
        Side Effects:
            - Modifies labelIds for all messages in the thread
            - Adds labels from addLabelIds to each message
            - Removes labels from removeLabelIds from each message
            - Changes applied to messages in thread's messages array
            - Prints confirmation with thread ID and user ID
            
        Note:
            - Applies same label changes to all messages in thread
            - Uses set operations to prevent duplicates
            - Add operation happens before remove operation
            - Returns full thread resource with updated messages
            - Skips messages that don't exist in storage
            - Common use: marking entire thread as read, archiving conversation
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Mark entire thread as read
            >>> thread = api.modify_thread("me", "thread123456", {
            ...     "removeLabelIds": ["UNREAD"]
            ... })
            Thread modified: ID=thread123456 for user user-uuid-123. Labels applied to contained messages.
            >>> 
            >>> # Archive and mark as important
            >>> thread = api.modify_thread("me", "thread123456", {
            ...     "addLabelIds": ["IMPORTANT"],
            ...     "removeLabelIds": ["INBOX"]
            ... })
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
        Deletes multiple messages in a single batch operation.
        
        Efficiently deletes many messages by calling delete_message for each ID.
        Continues processing even if some deletions fail.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            ids (List[str]): List of message IDs to delete.
                Format: List of 16-character hexadecimal strings
                Example: ["a1b2c3d4e5f67890", "f9e8d7c6b5a43210"]

        Returns:
            Dict[str, Union[bool, str, int]]: Batch operation result with structure:
                Success:
                {
                    "success": True,
                    "message": "Deleted {count} out of {total} messages.",
                    "deleted_count": int  # Number successfully deleted
                }
                User not found:
                {
                    "success": False,
                    "message": "User not found.",
                    "deleted_count": 0
                }
                
        Side Effects:
            - Calls delete_message for each ID in the list
            - Each successful deletion removes message and updates threads
            - Profile message/thread counts updated for each deletion
            - Prints batch summary with count and user ID
            - Individual delete confirmations printed per message
            
        Note:
            - Continues processing all IDs even if some fail
            - Returns count of successful deletions
            - Failed deletions silently skipped (success check per message)
            - Order of deletion matches order of IDs provided
            - More efficient than individual API calls for multiple deletions
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Delete multiple messages
            >>> message_ids = ["a1b2c3d4e5f67890", "f9e8d7c6b5a43210", "1234567890abcdef"]
            >>> result = api.batch_delete_messages("me", message_ids)
            Message deleted: ID=a1b2c3d4e5f67890 for user user-uuid-123
            Message deleted: ID=f9e8d7c6b5a43210 for user user-uuid-123
            Batch delete: 2/3 messages deleted for user user-uuid-123
            >>> print(result)
            {'success': True, 'message': 'Deleted 2 out of 3 messages.', 'deleted_count': 2}
        """
        resolved_user_id = self._resolve_user_id(user_id)
        if not resolved_user_id:
            return {"success": False, "message": "User not found.", "deleted_count": 0}
        
        # Get user email to pass to delete_message (which also calls _resolve_user_id)
        user_email = self._get_user_email_by_id(resolved_user_id)
        if not user_email:
            return {"success": False, "message": "User not found.", "deleted_count": 0}
        
        deleted_count = 0
        for msg_id in ids:
            result = self.delete_message(user_email, msg_id)
            if result.get("success"):
                deleted_count += 1
        
        print(f"Batch delete: {deleted_count}/{len(ids)} messages deleted for user {resolved_user_id}")
        return {
            "success": True,
            "message": f"Deleted {deleted_count} out of {len(ids)} messages.",
            "deleted_count": deleted_count
        }

    def batch_modify_messages(
        self, user_id: str, ids: List[str], modify_request: Dict[str, List[str]]
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Modifies labels for multiple messages in a single batch operation.
        
        Efficiently applies same label changes to many messages by calling
        modify_message for each ID. Continues processing even if some fail.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            ids (List[str]): List of message IDs to modify.
                Format: List of 16-character hexadecimal strings
                Example: ["a1b2c3d4e5f67890", "f9e8d7c6b5a43210"]
            modify_request (Dict[str, List[str]]): Label modification specification.
                Applied to all messages in the batch.
                Structure:
                {
                    "addLabelIds": List[str],     # Labels to add
                    "removeLabelIds": List[str]   # Labels to remove
                }
                Example: {"addLabelIds": ["STARRED"], "removeLabelIds": ["UNREAD"]}

        Returns:
            Dict[str, Union[bool, str, int]]: Batch operation result with structure:
                Success:
                {
                    "success": True,
                    "message": "Modified {count} out of {total} messages.",
                    "modified_count": int  # Number successfully modified
                }
                User not found:
                {
                    "success": False,
                    "message": "User not found.",
                    "modified_count": 0
                }
                
        Side Effects:
            - Calls modify_message for each ID in the list
            - Each successful modification updates message labels
            - Same label changes applied to all messages
            - Prints batch summary with count and user ID
            - Individual modify confirmations printed per message
            
        Note:
            - Continues processing all IDs even if some fail
            - Returns count of successful modifications
            - Failed modifications silently skipped (None check per message)
            - Order of modification matches order of IDs provided
            - More efficient than individual API calls for bulk label changes
            - Common use: bulk mark as read, bulk archive, bulk label application
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Mark multiple messages as read and starred
            >>> message_ids = ["a1b2c3d4e5f67890", "f9e8d7c6b5a43210"]
            >>> result = api.batch_modify_messages("me", message_ids, {
            ...     "addLabelIds": ["STARRED"],
            ...     "removeLabelIds": ["UNREAD"]
            ... })
            Message modified: ID=a1b2c3d4e5f67890, New Labels=[...] for user user-uuid-123
            Message modified: ID=f9e8d7c6b5a43210, New Labels=[...] for user user-uuid-123
            Batch modify: 2/2 messages modified for user user-uuid-123
            >>> print(result)
            {'success': True, 'message': 'Modified 2 out of 2 messages.', 'modified_count': 2}
        """
        resolved_user_id = self._resolve_user_id(user_id)
        if not resolved_user_id:
            return {"success": False, "message": "User not found.", "modified_count": 0}
        
        # Get user email to pass to modify_message (which also calls _resolve_user_id)
        user_email = self._get_user_email_by_id(resolved_user_id)
        if not user_email:
            return {"success": False, "message": "User not found.", "modified_count": 0}
        
        modified_count = 0
        for msg_id in ids:
            result = self.modify_message(user_email, msg_id, modify_request)
            if result is not None:
                modified_count += 1
        
        print(f"Batch modify: {modified_count}/{len(ids)} messages modified for user {resolved_user_id}")
        return {
            "success": True,
            "message": f"Modified {modified_count} out of {len(ids)} messages.",
            "modified_count": modified_count
        }

    def get_attachment(self, user_id: str, message_id: str, attachment_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves an attachment from a message.
        
        Returns attachment metadata and data for specified attachment within a message.

        Args:
            user_id (str): User identifier - email address or "me" keyword.
                Examples: "alice@example.com", "me"
            message_id (str): The message ID containing the attachment.
                Format: 16-character hexadecimal string
                Example: "a1b2c3d4e5f67890"
            attachment_id (str): The attachment ID to retrieve.
                Found in message payload parts with body.attachmentId
                Example: "attach123456"

        Returns:
            Optional[Dict[str, Any]]: Attachment resource if found, None otherwise.
                Structure:
                {
                    "attachmentId": str,
                    "size": int,         # Size in bytes
                    "data": str          # Placeholder attachment data
                }
                Returns None if user, message, or attachment not found
                
        Note:
            - Searches message payload parts for matching attachmentId
            - Returns placeholder data ("attachment_data_for_{attachment_id}")
            - Real Gmail API returns base64url encoded attachment content
            - Size comes from part.body.size field
            - Attachments stored in message.payload.parts array
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Get an attachment
            >>> attachment = api.get_attachment("me", "msg123456", "attach789")
            >>> if attachment:
            ...     print(f"Attachment size: {attachment['size']} bytes")
            ...     print(f"Data: {attachment['data']}")
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
        Resets all Gmail data to the default initial state.
        
        Reloads the default scenario, discarding all changes made during the session.
        All users, messages, drafts, labels, and threads are replaced with defaults.

        Returns:
            Dict[str, bool]: Status dictionary with structure:
                {
                    "reset_status": True  # Always True on successful reset
                }
                
        Side Effects:
            - Reloads data from DEFAULT_STATE scenario
            - All current users replaced with default users
            - All messages, drafts, labels, threads reset to default state
            - Current authentication preserved (current_user not cleared)
            - All modifications since initialization are lost
            - Prints confirmation message to console
            - Cannot be undone
            
        Note:
            - This is a testing/utility method not present in real Gmail API
            - Default state loaded from state_loader.load_default_state("GmailApis")
            - Unlike _load_scenario, does NOT auto-authenticate first user
            - Current user authentication persists if user still exists in default state
            - Useful for test cleanup or returning to known state
            - All in-memory changes are discarded
            
        Example:
            >>> api = GmailApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Make some changes
            >>> api.send_message("me", {
            ...     "to": "bob@example.com",
            ...     "subject": "Test",
            ...     "body": "Test message"
            ... })
            >>> 
            >>> # Reset to default state
            >>> result = api.reset_data()
            GmailApis: All data reset to default state.
            >>> print(result)  # {'reset_status': True}
            >>> # Test message is gone, default data restored
        """
        self._load_scenario(DEFAULT_STATE)
        print("GmailApis: All data reset to default state.")
        return {"reset_status": True}