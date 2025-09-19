import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional, Union
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("GmailApis")

class GmailApis:
    """
    A dummy API class for simulating Gmail operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the Gmail API, which provides core functionality for managing emails, drafts, and labels."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Load a scenario with users and their data.
        Args:
            scenario (Dict): Scenario data to load.
        """
        DEFAULT_STATE_COPY = copy.deepcopy(DEFAULT_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        print("GmailApis: Loaded scenario with users and their UUIDs.")

    def _generate_id(self) -> str:
        """
        Generate a unique ID.

        Returns:
            str: Generated UUID.
        """
        return str(uuid.uuid4())

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
            user_id (str): User's email address.
        Returns:
            Optional[Dict]: User's Gmail data if found, None otherwise.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return None
        return self.users.get(internal_user_id, {}).get("gmail_data")

    def _get_user_threads_data(self, user_id: str) -> Optional[Dict]:
        """
        Get threads data for a user.
        Args:
            user_id (str): User's email address.
        Returns:
            Optional[Dict]: User's threads data if found, None otherwise.
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("threads") if gmail_data else None

    def _get_user_messages_data(self, user_id: str) -> Optional[Dict]:
        """
        Get messages data for a user.
        Args:
            user_id (str): User's email address.
        Returns:
            Optional[Dict]: User's messages data if found, None otherwise.
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("messages") if gmail_data else None

    def _get_user_drafts_data(self, user_id: str) -> Optional[Dict]:
        """
        Get drafts data for a user.
        Args:
            user_id (str): User's email address.
        Returns:
            Optional[Dict]: User's drafts data if found, None otherwise.
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("drafts") if gmail_data else None

    def _get_user_labels_data(self, user_id: str) -> Optional[Dict]:
        """
        Get labels data for a user.
        Args:
            user_id (str): User's email address.
        Returns:
            Optional[Dict]: User's labels data if found, None otherwise.
        """
        gmail_data = self._get_user_gmail_data(user_id)
        return gmail_data.get("labels") if gmail_data else None

    def _update_thread_snippet(self, user_id: str, thread_id: str) -> None:
        """
        Update a thread's snippet with the most recent message.
        Args:
            user_id (str): User's email address.
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
            user_id (str): User's email address.
        Returns:
            Optional[Dict[str, Any]]: User's profile data if found, None otherwise.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return None
        
        user_data = self.users.get(internal_user_id)
        return user_data.get("gmail_data", {}).get("profile") if user_data else None

    def list_messages(
        self,
        user_id: str,
        query: Optional[str] = None,
        label_ids: Optional[List[str]] = None,
        page_token: Optional[str] = None,
        max_results: int = 10,
    ) -> Dict[str, Union[List[Dict], str, int]]:
        """
        List messages matching criteria.
        Args:
            user_id (str): User's email address.
            query (Optional[str]): Search query.
            label_ids (Optional[List[str]]): Label IDs to filter by.
            page_token (Optional[str]): Pagination token.
            max_results (int): Maximum number of results to return.
        Returns:
            Dict[str, Union[List[Dict], str, int]]: Dictionary containing messages, pagination token, and result count.
        """
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return {"messages": [], "resultSizeEstimate": 0}

        filtered_messages = []
        for msg_id, msg_data in messages.items():
            match = True
            if query and query.lower() not in msg_data.get("snippet", "").lower() and \
               query.lower() not in msg_data.get("payload", {}).get("headers", [{"value":""}])[0].get("value", "").lower():
                match = False
            if label_ids:
                msg_labels = set(msg_data.get("labelIds", []))
                if not all(label in msg_labels for label in label_ids):
                    match = False
            
            if match:
                filtered_messages.append({
                    "id": msg_data["id"],
                    "threadId": msg_data["threadId"],
                    "snippet": msg_data["snippet"],
                    "labelIds": msg_data["labelIds"]
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
        self, user_id: str, msg_id: str, format: str = "full"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific message.
        Args:
            user_id (str): User's email address.
            msg_id (str): Message ID.
            format (str): Format of the message ('minimal', 'full', or 'raw').
        Returns:
            Optional[Dict[str, Any]]: Message data if found, None otherwise.
        """
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return None
        
        message = messages.get(msg_id)
        if message:
            if format == "minimal":
                return {"id": message["id"], "threadId": message["threadId"], "snippet": message["snippet"]}
            elif format == "raw":
                return {"id": message["id"], "raw": "dummy_raw_content_for_" + message["id"]}
            return copy.deepcopy(message)
        return None

    def send_message(
        self, user_id: str, to: str, subject: str, body: str, thread_id: Optional[str] = None
    ) -> Dict[str, Union[str, Dict]]:
        """
        Send a message.
        Args:
            user_id (str): Sender's email address.
            to (str): Recipient's email address.
            subject (str): Message subject.
            body (str): Message body.
            thread_id (Optional[str]): Thread ID if replying.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing message ID and thread ID, or error message.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"error": "User not found."}

        gmail_data = self.users[internal_user_id].get("gmail_data")
        if not gmail_data:
            return {"error": "Gmail data not available for user."}

        new_msg_id = self._generate_id()
        if not thread_id:
            thread_id = self._generate_id()

        new_message = {
            "id": new_msg_id,
            "threadId": thread_id,
            "snippet": body[:100] + "..." if len(body) > 100 else body,
            "payload": {
                "headers": [
                    {"name": "To", "value": to},
                    {"name": "From", "value": user_id},
                    {"name": "Subject", "value": subject}
                ],
                "body": {"data": body}
            },
            "internalDate": str(int(datetime.datetime.now().timestamp() * 1000)),
            "labelIds": ["SENT", "INBOX"]
        }
# hi
        gmail_data["messages"][new_msg_id] = new_message
        
        # Create or update thread with snippet
        if thread_id not in gmail_data["threads"]:
            gmail_data["threads"][thread_id] = {
                "id": thread_id, 
                "messages": [],
                "snippet": new_message["snippet"],
                "historyId": str(int(datetime.datetime.now().timestamp() * 1000))
            }
        else:
            # Update thread snippet with latest message
            gmail_data["threads"][thread_id]["snippet"] = new_message["snippet"]
            
        gmail_data["threads"][thread_id]["messages"].append({"id": new_msg_id})
        gmail_data["profile"]["messagesTotal"] = gmail_data["profile"].get("messagesTotal", 0) + 1
        gmail_data["profile"]["threadsTotal"] = len(gmail_data["threads"])

        recipient_user_id = self._get_user_id_by_email(to)
        if recipient_user_id and recipient_user_id != internal_user_id:
            recipient_gmail_data = self.users[recipient_user_id].get("gmail_data")
            if recipient_gmail_data:
                recipient_message = copy.deepcopy(new_message)
                recipient_message["labelIds"] = ["INBOX", "UNREAD"]
                recipient_gmail_data["messages"][new_msg_id] = recipient_message
                
                # Create or update thread for recipient with snippet
                if thread_id not in recipient_gmail_data["threads"]:
                    recipient_gmail_data["threads"][thread_id] = {
                        "id": thread_id, 
                        "messages": [],
                        "snippet": new_message["snippet"],
                        "historyId": str(int(datetime.datetime.now().timestamp() * 1000))
                    }
                else:
                    # Update thread snippet with latest message
                    recipient_gmail_data["threads"][thread_id]["snippet"] = new_message["snippet"]
                    
                recipient_gmail_data["threads"][thread_id]["messages"].append({"id": new_msg_id})
                recipient_gmail_data["profile"]["messagesTotal"] = recipient_gmail_data["profile"].get("messagesTotal", 0) + 1
                recipient_gmail_data["profile"]["threadsTotal"] = len(recipient_gmail_data["threads"])

        print(f"Dummy email sent: from {user_id} to {to}, subject '{subject}'")
        return {"id": new_msg_id, "threadId": thread_id}

    def delete_message(self, user_id: str, msg_id: str) -> Dict[str, Union[bool, str]]:
        """
        Delete a message.
        Args:
            user_id (str): User's email address.
            msg_id (str): Message ID to delete.
        Returns:
            Dict[str, Union[bool, str]]: Dictionary indicating success/failure and message.
        """
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

            internal_user_id = self._get_user_id_by_email(user_id)
            if internal_user_id:
                profile = self.users[internal_user_id].get("gmail_data", {}).get("profile")
                if profile:
                    profile["messagesTotal"] = max(0, profile.get("messagesTotal", 0) - 1)
                    profile["threadsTotal"] = len(threads) if threads else 0

            print(f"Dummy message deleted: ID={msg_id} for user {user_id}")
            return {"success": True, "message": f"Message {msg_id} deleted."}
        return {"success": False, "message": f"Message {msg_id} not found."}

    def list_drafts(
        self, user_id: str, page_token: Optional[str] = None, max_results: int = 10
    ) -> Dict[str, Union[List[Dict], str, int]]:
        """
        List drafts.
        Args:
            user_id (str): User's email address.
            page_token (Optional[str]): Pagination token.
            max_results (int): Maximum number of results to return.
        Returns:
            Dict[str, Union[List[Dict], str, int]]: Dictionary containing drafts, pagination token, and result count.
        """
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
            user_id (str): User's email address.
            draft_id (str): Draft ID.
        Returns:
            Optional[Dict[str, Any]]: Draft data if found, None otherwise.
        """
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return None
        
        draft = drafts.get(draft_id)
        if draft:
            return copy.deepcopy(draft)
        return None

    def create_draft(
        self, user_id: str, to: str, subject: str, body: str
    ) -> Dict[str, Union[str, Dict]]:
        """
        Create a draft.
        Args:
            user_id (str): User's email address.
            to (str): Recipient's email address.
            subject (str): Message subject.
            body (str): Message body.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing draft ID and message, or error message.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"error": "User not found."}

        gmail_data = self.users[internal_user_id].get("gmail_data")
        if not gmail_data:
            return {"error": "Gmail data not available for user."}

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
        print(f"Dummy draft created: ID={new_draft_id} for user {user_id}")
        return {"id": new_draft_id, "message": new_draft["message"]}

    def update_draft(
        self, user_id: str, draft_id: str, to: str, subject: str, body: str
    ) -> Dict[str, Union[str, Dict]]:
        """
        Update a draft.
        Args:
            user_id (str): User's email address.
            draft_id (str): Draft ID to update.
            to (str): New recipient's email address.
            subject (str): New message subject.
            body (str): New message body.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing draft ID and message, or error message.
        """
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return {"error": "User not found or no drafts data."}

        if draft_id in drafts:
            drafts[draft_id]["message"]["to"] = to
            drafts[draft_id]["message"]["subject"] = subject
            drafts[draft_id]["message"]["body"] = body
            print(f"Dummy draft updated: ID={draft_id} for user {user_id}")
            return {"id": draft_id, "message": drafts[draft_id]["message"]}
        return {"error": f"Draft {draft_id} not found."}

    def delete_draft(self, user_id: str, draft_id: str) -> Dict[str, Union[bool, str]]:
        """
        Delete a draft.
        Args:
            user_id (str): User's email address.
            draft_id (str): Draft ID to delete.
        Returns:
            Dict[str, Union[bool, str]]: Dictionary indicating success/failure and message.
        """
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return {"success": False, "message": "User not found or no drafts data."}
        
        if draft_id in drafts:
            del drafts[draft_id]
            print(f"Dummy draft deleted: ID={draft_id} for user {user_id}")
            return {"success": True, "message": f"Draft {draft_id} deleted."}
        return {"success": False, "message": f"Draft {draft_id} not found."}

    def send_draft(self, user_id: str, draft_id: str) -> Dict[str, Union[str, Dict]]:
        """
        Send a draft as a message.
        Args:
            user_id (str): User's email address.
            draft_id (str): Draft ID to send.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing message ID and thread ID, or error message.
        """
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return {"error": "User not found or no drafts data."}
        
        if draft_id not in drafts:
            return {"error": f"Draft {draft_id} not found."}
        
        draft = drafts[draft_id]
        draft_message = draft.get("message", {})
        
        # Extract draft details
        to = draft_message.get("to", "")
        subject = draft_message.get("subject", "")
        body = draft_message.get("body", "")
        
        if not to:
            return {"error": "Draft has no recipient specified."}
        
        # Send the draft as a regular message
        result = self.send_message(user_id, to, subject, body)
        
        # If message was sent successfully, delete the draft
        if "id" in result and "error" not in result:
            self.delete_draft(user_id, draft_id)
            print(f"Dummy draft sent and deleted: draft ID={draft_id}, message ID={result['id']}")
        
        return result

    def list_labels(self, user_id: str) -> Dict[str, Union[List[Dict], str]]:
        """
        List labels.
        Args:
            user_id (str): User's email address.
        Returns:
            Dict[str, Union[List[Dict], str]]: Dictionary containing labels.
        """
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return {"labels": []}
        
        formatted_labels = [copy.deepcopy(label) for label in labels.values()]
        return {"labels": formatted_labels}

    def get_label(self, user_id: str, label_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific label.
        Args:
            user_id (str): User's email address.
            label_id (str): Label ID.
        Returns:
            Optional[Dict[str, Any]]: Label data if found, None otherwise.
        """
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
            user_id (str): User's email address.
            label_name (str): Name for the new label.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing label ID and name, or error message.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"error": "User not found."}

        gmail_data = self.users[internal_user_id].get("gmail_data")
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
        print(f"Dummy label created: ID={new_label_id}, Name='{label_name}' for user {user_id}")
        return {"id": new_label_id, "name": label_name}

    def update_label(self, user_id: str, label_id: str, new_label_name: str) -> Dict[str, Union[str, Dict]]:
        """
        Update a label.
        Args:
            user_id (str): User's email address.
            label_id (str): Label ID to update.
            new_label_name (str): New name for the label.
        Returns:
            Dict[str, Union[str, Dict]]: Dictionary containing label ID and name, or error message.
        """
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return {"error": "User not found or no labels data."}
        
        if label_id in labels:
            labels[label_id]["name"] = new_label_name
            print(f"Dummy label updated: ID={label_id}, New Name='{new_label_name}' for user {user_id}")
            return {"id": label_id, "name": new_label_name}
        return {"error": f"Label {label_id} not found."}

    def delete_label(self, user_id: str, label_id: str) -> Dict[str, Union[bool, str]]:
        """
        Delete a label.
        Args:
            user_id (str): User's email address.
            label_id (str): Label ID to delete.
        Returns:
            Dict[str, Union[bool, str]]: Dictionary indicating success/failure and message.
        """
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return {"success": False, "message": "User not found or no labels data."}
        
        if label_id in labels:
            del labels[label_id]
            print(f"Dummy label deleted: ID={label_id} for user {user_id}")
            return {"success": True, "message": f"Label {label_id} deleted."}
        return {"success": False, "message": f"Label {label_id} not found."}

    def modify_message(
        self, user_id: str, message_id: str, modify_request: Dict[str, List[str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Modify a message (e.g., add/remove labels).
        Args:
            user_id (str): User's email address.
            message_id (str): Message ID to modify.
            modify_request (Dict[str, List[str]]): Dictionary with 'addLabelIds' and 'removeLabelIds'.
        Returns:
            Optional[Dict[str, Any]]: Modified message data if found, None otherwise.
        """
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return None
        
        message = messages.get(message_id)
        if not message:
            return None

        current_labels = set(message.get("labelIds", []))
        
        add_labels = set(modify_request.get("addLabelIds", []))
        remove_labels = set(modify_request.get("removeLabelIds", []))

        message["labelIds"] = list(current_labels.union(add_labels))
        message["labelIds"] = list(set(message["labelIds"]) - remove_labels)

        print(f"Dummy message modified: ID={message_id}, New Labels={message['labelIds']} for user {user_id}")
        return copy.deepcopy(message)

    def get_thread(
        self, user_id: str, thread_id: str, format: str = "full"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a thread with its messages.
        Args:
            user_id (str): User's email address.
            thread_id (str): Thread ID.
            format (str): Format of the messages ('minimal', 'full', or 'raw').
        Returns:
            Optional[Dict[str, Any]]: Thread data if found, None otherwise.
        """
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
                    detailed_messages.append({"id": message["id"], "raw": "dummy_raw_content_for_" + message["id"]})
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
            user_id (str): User's email address.
            thread_id (str): Thread ID to modify.
            modify_request (Dict[str, List[str]]): Dictionary with 'addLabelIds' and 'removeLabelIds'.
        Returns:
            Optional[Dict[str, Any]]: Modified thread data if found, None otherwise.
        """
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
        
        print(f"Dummy thread modified: ID={thread_id} for user {user_id}. Labels applied to contained messages.")
        return self.get_thread(user_id, thread_id, format="full")

    def reset_data(self) -> Dict[str, bool]:
        """
        Reset all data to default state.

        Returns:
            Dict[str, bool]: Dictionary indicating reset status.
        """
        self._load_scenario(DEFAULT_STATE)
        print("GmailApis: All dummy data reset to default state.")
        return {"reset_status": True}