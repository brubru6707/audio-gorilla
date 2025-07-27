import datetime
import copy
from typing import Dict, List, Any, Optional, Union

DEFAULT_STATE: Dict[str, Any] = {
    "users": {
        "alice.smith@example.net": {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@example.net",
            "friends": ["bob.johnson@example.com", "charlie.davis@example.org"],
            "gmail_data": {
                "profile": {
                    "emailAddress": "alice.smith@example.net",
                    "messagesTotal": 1500,
                    "threadsTotal": 500,
                    "historyId": "9876543210987"
                },
                "drafts": {
                    "draft_abc_123": {
                        "id": "draft_abc_123",
                        "message": {
                            "to": "project.team@example.com",
                            "subject": "Project Status Update",
                            "body": "Hi team, here's the latest on our project. We're on track for completion."
                        }
                    }
                },
                "labels": {
                    "label_important_client": {
                        "id": "label_important_client",
                        "name": "Important Clients",
                        "messageListVisibility": "show",
                        "labelListVisibility": "show",
                        "type": "user",
                        "messagesTotal": 85,
                        "messagesUnread": 5,
                        "threadsTotal": 30,
                        "threadsUnread": 2
                    },
                    "label_personal": {
                        "id": "label_personal",
                        "name": "Personal",
                        "messageListVisibility": "show",
                        "labelListVisibility": "show",
                        "type": "user",
                        "messagesTotal": 120,
                        "messagesUnread": 10,
                        "threadsTotal": 45,
                        "threadsUnread": 7
                    }
                },
                "messages": {
                    "msg_def_456": {
                        "id": "msg_def_456",
                        "threadId": "thread_proj_update",
                        "labelIds": ["INBOX", "label_important_client"],
                        "snippet": "Meeting confirmed for next Tuesday at 10 AM.",
                        "payload": {"headers": [], "body": {}},
                        "sizeEstimate": 2048,
                        "historyId": "1234567890123"
                    },
                    "msg_ghi_789": {
                        "id": "msg_ghi_789",
                        "threadId": "thread_family_vacation",
                        "labelIds": ["INBOX", "label_personal"],
                        "snippet": "Just booked the flights for our vacation to Hawaii!",
                        "payload": {"headers": [], "body": {}},
                        "sizeEstimate": 1500,
                        "historyId": "1234567890124"
                    }
                },
                "threads": {
                    "thread_proj_update": {
                        "id": "thread_proj_update",
                        "historyId": "1234567890123",
                        "messages": [
                            {
                                "id": "msg_def_456",
                                "threadId": "thread_proj_update",
                                "labelIds": ["INBOX", "label_important_client"],
                                "snippet": "Meeting confirmed for next Tuesday at 10 AM.",
                                "payload": {"headers": [], "body": {}},
                                "sizeEstimate": 2048,
                                "historyId": "1234567890123"
                            }
                        ],
                        "snippet": "Meeting confirmed for next Tuesday at 10 AM."
                    },
                    "thread_family_vacation": {
                        "id": "thread_family_vacation",
                        "historyId": "1234567890124",
                        "messages": [
                            {
                                "id": "msg_ghi_789",
                                "threadId": "thread_family_vacation",
                                "labelIds": ["INBOX", "label_personal"],
                                "snippet": "Just booked the flights for our vacation to Hawaii!",
                                "payload": {"headers": [], "body": {}},
                                "sizeEstimate": 1500,
                                "historyId": "1234567890124"
                            }
                        ],
                        "snippet": "Just booked the flights for our vacation to Hawaii!"
                    }
                },
                "settings": {
                    "auto_forwarding": {
                        "enabled": False,
                        "emailAddress": None,
                        "disposition": "leaveInInbox"
                    },
                    "vacation_responder": {
                        "enableAutoReply": False,
                        "responseSubject": None,
                        "responseBodyPlainText": None,
                        "responseBodyHtml": None,
                        "restrictToContacts": False,
                        "restrictToDomain": False,
                        "startTime": None,
                        "endTime": None
                    },
                    "pop_settings": {
                        "accessWindow": "allMail",
                        "disposition": "leaveInInbox"
                    },
                    "language": {
                        "displayLanguage": "en"
                    },
                    "delegates": {
                        "delegate_fin_assistant": {
                            "delegateEmail": "finance.assistant@example.net",
                            "verificationStatus": "accepted"
                        }
                    },
                    "filters": {
                        "filter_newsletter_promo": {
                            "id": "filter_newsletter_promo",
                            "criteria": {"from": "*@promotions.com", "subject": "Newsletter"},
                            "action": {"addLabelIds": ["SPAM", "TRASH"]}
                        }
                    },
                    "forwarding_addresses": {
                        "forward_backup": {
                            "forwardingEmail": "alice.backup@gmail.com",
                            "verificationStatus": "accepted"
                        }
                    },
                    "send_as_aliases": {
                        "alias_work": {
                            "sendAsEmail": "alice.work@example.net",
                            "displayName": "Alice Smith (Work)",
                            "replyToAddress": None,
                            "signature": "Best regards,\nAlice Smith",
                            "isPrimary": False,
                            "verificationStatus": "accepted"
                        }
                    }
                },
                "history": {
                    "hist_1001": {
                        "id": "hist_1001",
                        "messages": [],
                        "labelsAdded": [{"messageIds": ["msg_def_456"], "labelIds": ["STARRED"]}],
                        "historyId": "1001"
                    }
                }
            }
        },
        "bob.johnson@example.com": {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@example.com",
            "friends": ["alice.smith@example.net"],
            "gmail_data": {
                "profile": {
                    "emailAddress": "bob.johnson@example.com",
                    "messagesTotal": 750,
                    "threadsTotal": 200,
                    "historyId": "1234567890123"
                },
                "drafts": {
                    "draft_re_meeting": {
                        "id": "draft_re_meeting",
                        "message": {
                            "to": "alice.smith@example.net",
                            "subject": "Re: Meeting Reminder",
                            "body": "Thanks for the reminder! See you then."
                        }
                    }
                },
                "labels": {
                    "label_project_x": {
                        "id": "label_project_x",
                        "name": "Project X",
                        "messageListVisibility": "show",
                        "labelListVisibility": "show",
                        "type": "user",
                        "messagesTotal": 55,
                        "messagesUnread": 0,
                        "threadsTotal": 15,
                        "threadsUnread": 0
                    }
                },
                "messages": {
                    "msg_xyz_111": {
                        "id": "msg_xyz_111",
                        "threadId": "thread_client_feedback",
                        "labelIds": ["INBOX", "label_project_x"],
                        "snippet": "Feedback received on the latest design mockups.",
                        "payload": {"headers": [], "body": {}},
                        "sizeEstimate": 1800,
                        "historyId": "9876543210123"
                    }
                },
                "threads": {
                    "thread_client_feedback": {
                        "id": "thread_client_feedback",
                        "historyId": "9876543210123",
                        "messages": [
                            {
                                "id": "msg_xyz_111",
                                "threadId": "thread_client_feedback",
                                "labelIds": ["INBOX", "label_project_x"],
                                "snippet": "Feedback received on the latest design mockups.",
                                "payload": {"headers": [], "body": {}},
                                "sizeEstimate": 1800,
                                "historyId": "9876543210123"
                            }
                        ],
                        "snippet": "Feedback received on the latest design mockups."
                    }
                },
                "settings": {
                    "auto_forwarding": {
                        "enabled": True,
                        "emailAddress": "bob.alternate@outlook.com",
                        "disposition": "archive"
                    },
                    "vacation_responder": {
                        "enableAutoReply": True,
                        "responseSubject": "Out of Office - Unavailable",
                        "responseBodyPlainText": "I am currently out of the office until [Date]. I will respond to your email as soon as possible upon my return.",
                        "responseBodyHtml": "I am currently out of the office until [Date]. I will respond to your email as soon as possible upon my return.",
                        "restrictToContacts": False,
                        "restrictToDomain": False,
                        "startTime": (datetime.datetime.now() - datetime.timedelta(days=2)).timestamp() * 1000,
                        "endTime": (datetime.datetime.now() + datetime.timedelta(days=5)).timestamp() * 1000
                    },
                    "pop_settings": {
                        "accessWindow": "enabledFrom",
                        "disposition": "archive"
                    },
                    "language": {
                        "displayLanguage": "es"
                    },
                    "delegates": {},
                    "filters": {
                        "filter_spam_block": {
                            "id": "filter_spam_block",
                            "criteria": {"from": "suspicious@malware.net", "subject": "URGENT ACTION REQUIRED"},
                            "action": {"addLabelIds": ["SPAM", "TRASH"], "markAsRead": True}
                        }
                    },
                    "forwarding_addresses": {},
                    "send_as_aliases": {}
                },
                "history": {}
            }
        },
        "charlie.davis@example.org": {
            "first_name": "Charlie",
            "last_name": "Davis",
            "email": "charlie.davis@example.org",
            "friends": ["alice.smith@example.net"],
            "gmail_data": {
                "profile": {
                    "emailAddress": "charlie.davis@example.org",
                    "messagesTotal": 250,
                    "threadsTotal": 100,
                    "historyId": "2468135790246"
                },
                "drafts": {},
                "labels": {
                    "label_news": {
                        "id": "label_news",
                        "name": "Newsletters",
                        "messageListVisibility": "hide",
                        "labelListVisibility": "hide",
                        "type": "user",
                        "messagesTotal": 70,
                        "messagesUnread": 15,
                        "threadsTotal": 25,
                        "threadsUnread": 5
                    }
                },
                "messages": {},
                "threads": {},
                "settings": {
                    "auto_forwarding": {
                        "enabled": False,
                        "emailAddress": None,
                        "disposition": "leaveInInbox"
                    },
                    "vacation_responder": {
                        "enableAutoReply": False,
                        "responseSubject": None,
                        "responseBodyPlainText": None,
                        "responseBodyHtml": None,
                        "restrictToContacts": False,
                        "restrictToDomain": False,
                        "startTime": None,
                        "endTime": None
                    },
                    "pop_settings": {
                        "accessWindow": "disabled",
                        "disposition": "leaveInInbox"
                    },
                    "language": {
                        "displayLanguage": "en-GB"
                    },
                    "delegates": {},
                    "filters": {
                        "filter_social_media": {
                            "id": "filter_social_media",
                            "criteria": {"from": "*@facebookmail.com OR *@twitter.com"},
                            "action": {"addLabelIds": ["SOCIAL"], "markAsRead": True}
                        }
                    },
                    "forwarding_addresses": {},
                    "send_as_aliases": {
                        "alias_personal": {
                            "sendAsEmail": "charlie.davis.personal@gmail.com",
                            "displayName": "Charlie Davis (Personal)",
                            "replyToAddress": None,
                            "signature": "Cheers,\nCharlie",
                            "isPrimary": False,
                            "verificationStatus": "accepted"
                        }
                    }
                },
                "history": {}
            }
        },
        "diana.miller@webmail.co": {
            "first_name": "Diana",
            "last_name": "Miller",
            "email": "diana.miller@webmail.co",
            "friends": ["bob.johnson@example.com"],
            "gmail_data": {
                "profile": {
                    "emailAddress": "diana.miller@webmail.co",
                    "messagesTotal": 50,
                    "threadsTotal": 15,
                    "historyId": "3692581470369"
                },
                "drafts": {},
                "labels": {},
                "messages": {},
                "threads": {},
                "settings": {
                    "auto_forwarding": {
                        "enabled": False,
                        "emailAddress": None,
                        "disposition": "leaveInInbox"
                    },
                    "vacation_responder": {
                        "enableAutoReply": False,
                        "responseSubject": None,
                        "responseBodyPlainText": None,
                        "responseBodyHtml": None,
                        "restrictToContacts": False,
                        "restrictToDomain": False,
                        "startTime": None,
                        "endTime": None
                    },
                    "pop_settings": {
                        "accessWindow": "allMail",
                        "disposition": "leaveInInbox"
                    },
                    "language": {
                        "displayLanguage": "fr"
                    },
                    "delegates": {},
                    "filters": {},
                    "forwarding_addresses": {},
                    "send_as_aliases": {}
                },
                "history": {}
            }
        }
    },
    "current_user": "alice.smith@example.net",
    "gmail_draft_counter": 10, # Adjusted for existing drafts
    "gmail_label_counter": 10, # Adjusted for existing labels
    "gmail_message_counter": 100, # Adjusted for existing messages
    "gmail_thread_counter": 50, # Adjusted for existing threads
    "gmail_history_counter": 200, # Adjusted for existing history
    "gmail_delegate_counter": 5,
    "gmail_filter_counter": 5,
    "gmail_forwarding_address_counter": 5,
    "gmail_send_as_counter": 5
}

class GmailApis:
    def __init__(self, state: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes the GmailBackendSimulator with a given state.
        If no state is provided, it uses a deep copy of the DEFAULT_STATE.

        Args:
            state (Optional[Dict[str, Any]]): The initial state for the simulator.
                                               Defaults to a deep copy of DEFAULT_STATE.
        """
        self.state: Dict[str, Any] = copy.deepcopy(state if state is not None else DEFAULT_STATE)

    def _get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user-specific Gmail data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's Gmail data, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id, {}).get("gmail_data")

    def _get_user_profile_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user profile data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's profile information, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id, {}).get("gmail_data", {}).get("profile")

    def _get_user_drafts_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user drafts data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's drafts, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id, {}).get("gmail_data", {}).get("drafts")
    
    def _get_user_labels_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user labels data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's labels, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id, {}).get("gmail_data", {}).get("labels")

    def _get_user_messages_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user messages data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's messages, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id, {}).get("gmail_data", {}).get("messages")

    def _get_user_threads_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user threads data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's threads, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id, {}).get("gmail_data", {}).get("threads")

    def _get_user_settings_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user settings data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's settings, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id, {}).get("gmail_data", {}).get("settings")

    def _get_user_history_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user history data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's history, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id, {}).get("gmail_data", {}).get("history")

    def get_user_profile(self, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Gets the current user's Gmail profile from the backend state.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's profile information,
                                      or None if the profile is not found.
        """
        profile = self._get_user_profile_data(user_id)
        if profile:
            return copy.deepcopy(profile)
        return None

    def create_draft(self, message_body: Dict[str, Any], user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Creates a new draft in the backend state.

        Args:
            message_body (Dict[str, Any]): The draft message content to create.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the created draft, or None if the user data is not found.
        """
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return None

        self.state["gmail_draft_counter"] += 1
        new_draft_id = f"draft{self.state['gmail_draft_counter']}"
        new_draft = {
            "id": new_draft_id,
            "message": message_body
        }
        drafts[new_draft_id] = new_draft
        return copy.deepcopy(new_draft)

    def delete_draft(self, draft_id: str, user_id: str = 'me') -> Optional[None]:
        """
        Deletes the specified draft from the backend state.

        Args:
            draft_id (str): The ID of the draft to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[None]: None if successful, or None if the draft or user data is not found.
        """
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return None

        if draft_id in drafts:
            del drafts[draft_id]
            return None
        return None

    def get_draft(self, draft_id: str, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Gets the specified draft from the backend state.

        Args:
            draft_id (str): The ID of the draft to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the draft, or None if the draft or user data is not found.
        """
        drafts = self._get_user_drafts_data(user_id)
        if drafts is None:
            return None

        draft = drafts.get(draft_id)
        if draft:
            return copy.deepcopy(draft)
        return None

    def list_drafts(self, user_id: str = 'me', max_results: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Lists the drafts in the user's mailbox from the backend state.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.
            max_results (Optional[int]): Maximum number of drafts to return (simulated).
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing a list of drafts and result estimate,
                                      or None if the user data is not found.
        """
        drafts_data = self._get_user_drafts_data(user_id)
        if drafts_data is None:
            return None

        all_drafts = list(drafts_data.values())
        if max_results:
            all_drafts = all_drafts[:max_results]
        return {"drafts": copy.deepcopy(all_drafts), "resultSizeEstimate": len(all_drafts)}

    def create_label(self, label_body: Dict[str, Any], user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Creates a new label in the backend state.

        Args:
            label_body (Dict[str, Any]): The label to create (with name, messageListVisibility, etc.).
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: The created label, or None if the user data is not found.
        """
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return None

        self.state["gmail_label_counter"] += 1
        new_label_id = f"label{self.state['gmail_label_counter']}"
        new_label = {
            "id": new_label_id,
            "name": label_body.get("name"),
            "messageListVisibility": label_body.get("messageListVisibility", "show"),
            "labelListVisibility": label_body.get("labelListVisibility", "show"),
            "type": label_body.get("type", "user"),
            "messagesTotal": 0,
            "messagesUnread": 0,
            "threadsTotal": 0,
            "threadsUnread": 0
        }
        labels[new_label_id] = new_label
        return copy.deepcopy(new_label)

    def delete_label(self, label_id: str, user_id: str = 'me') -> Optional[None]:
        """
        Deletes the specified label from the backend state.

        Args:
            label_id (str): The ID of the label to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[None]: None if successful, or None if the label or user data is not found.
        """
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return None

        if label_id in labels:
            del labels[label_id]
            return None
        return None

    def get_label(self, label_id: str, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Gets the specified label from the backend state.

        Args:
            label_id (str): The ID of the label to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the label details, or None if the label or user data is not found.
        """
        labels = self._get_user_labels_data(user_id)
        if labels is None:
            return None

        label = labels.get(label_id)
        if label:
            return copy.deepcopy(label)
        return None

    def list_labels(self, user_id: str = 'me') -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """
        Lists all labels in the user's mailbox from the backend state.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, List[Dict[str, Any]]]]: A dictionary containing a list of labels,
                                                        or None if the user data is not found.
        """
        labels_data = self._get_user_labels_data(user_id)
        if labels_data is None:
            return None

        all_labels = list(labels_data.values())
        return {"labels": copy.deepcopy(all_labels)}

    def batch_delete_messages(self, message_ids: List[str], user_id: str = 'me') -> Optional[None]:
        """
        Deletes many messages by message ID from the backend state.

        Args:
            message_ids (List[str]): List of IDs of messages to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[None]: None if successful, or None if the user data is not found.
        """
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return None

        deleted_count = 0
        for msg_id in message_ids:
            if msg_id in messages:
                del messages[msg_id]
                deleted_count += 1
        return None

    def get_message(self, message_id: str, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Gets the specified message from the backend state.

        Args:
            message_id (str): The ID of the message to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the message, or None if the message or user data is not found.
        """
        messages = self._get_user_messages_data(user_id)
        if messages is None:
            return None

        message = messages.get(message_id)
        if message:
            return copy.deepcopy(message)
        return None

    def list_messages(self, user_id: str = 'me', label_ids: Optional[List[str]] = None, max_results: Optional[int] = None, q: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Lists the messages in the user's mailbox from the backend state.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.
            label_ids (Optional[List[str]]): Only return messages with these label IDs applied.
            max_results (Optional[int]): Maximum number of messages to return (simulated).
            q (Optional[str]): Search query in the same format as the Gmail search box (basic simulation).

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing a list of messages and result estimate,
                                      or None if the user data is not found.
        """
        messages_data = self._get_user_messages_data(user_id)
        if messages_data is None:
            return None

        filtered_messages = []
        for _, message in messages_data.items():
            match = True
            if label_ids:
                if not all(lbl in message.get("labelIds", []) for lbl in label_ids):
                    match = False
            if q:
                query_lower = q.lower()
                snippet_lower = message.get("snippet", "").lower()
                body_lower = message.get("payload", {}).get("body", {}).get("data", "").lower()
                if query_lower not in snippet_lower and query_lower not in body_lower:
                    match = False
            if match:
                filtered_messages.append(message)

        if max_results:
            filtered_messages = filtered_messages[:max_results]
        return {"messages": copy.deepcopy(filtered_messages), "resultSizeEstimate": len(filtered_messages)}

    def send_message(self, message_body: Dict[str, Any], user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Sends the specified message by adding it to the user's messages in the backend state.
        Also simulates adding it to a thread.

        Args:
            message_body (Dict[str, Any]): The message to send.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: The sent message, or None if the user data is not found.
        """
        messages = self._get_user_messages_data(user_id)
        threads = self._get_user_threads_data(user_id)
        if messages is None or threads is None:
            return None

        self.state["gmail_message_counter"] += 1
        new_msg_id = f"msg{self.state['gmail_message_counter']}"
        thread_id = message_body.get("threadId", f"thread{self.state['gmail_thread_counter']}")

        sent_message = {
            "id": new_msg_id,
            "threadId": thread_id,
            "labelIds": message_body.get("labelIds", ["SENT", "INBOX"]),
            "snippet": message_body.get("body", {}).get("raw", "")[:100],
            "payload": message_body.get("payload", {}),
            "sizeEstimate": len(message_body.get("body", {}).get("raw", "")),
            "historyId": str(self.state["gmail_history_counter"])
        }
        messages[new_msg_id] = sent_message

        if thread_id not in threads:
            self.state["gmail_thread_counter"] += 1
            threads[thread_id] = {
                "id": thread_id,
                "historyId": str(self.state["gmail_history_counter"]),
                "messages": [],
                "snippet": ""
            }
        threads[thread_id]["messages"].append(sent_message)
        threads[thread_id]["snippet"] = sent_message["snippet"]

        self.state["gmail_history_counter"] += 1
        history_id = str(self.state["gmail_history_counter"])
        if history_id not in self._get_user_history_data(user_id):
            self._get_user_history_data(user_id)[history_id] = {
                "id": history_id,
                "messages": [],
                "labelsAdded": []
            }
        self._get_user_history_data(user_id)[history_id]["messages"].append({"messageAdded": {"message": sent_message}})

        return copy.deepcopy(sent_message)

    def get_auto_forwarding(self, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Gets the auto-forwarding setting from the backend state.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing auto-forwarding settings, or None if not found.
        """
        settings = self._get_user_settings_data(user_id)
        if settings and "auto_forwarding" in settings:
            return copy.deepcopy(settings["auto_forwarding"])
        return None

    def update_vacation(self, vacation_settings: Dict[str, Any], user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Updates vacation responder settings in the backend state.

        Args:
            vacation_settings (Dict[str, Any]): The vacation responder settings to update.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: The updated vacation responder settings, or None if the user data is not found.
        """
        settings = self._get_user_settings_data(user_id)
        if settings is None:
            return None

        settings["vacation_responder"].update(vacation_settings)
        return copy.deepcopy(settings["vacation_responder"])

    def get_pop_settings(self, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Gets POP settings from the backend state.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing POP settings, or None if not found.
        """
        settings = self._get_user_settings_data(user_id)
        if settings and "pop_settings" in settings:
            return copy.deepcopy(settings["pop_settings"])
        return None

    def update_language(self, language_settings: Dict[str, str], user_id: str = 'me') -> Optional[Dict[str, str]]:
        """
        Updates language settings in the backend state.

        Args:
            language_settings (Dict[str, str]): The language settings to update.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, str]]: The updated language settings, or None if the user data is not found.
        """
        settings = self._get_user_settings_data(user_id)
        if settings is None:
            return None

        settings["language"].update(language_settings)
        return copy.deepcopy(settings["language"])

    def list_history(self, start_history_id: str, user_id: str = 'me', max_results: Optional[int] = None) -> Optional[Dict[str, Union[List[Dict[str, Any]], str]]]:
        """
        Lists the history of all changes to the user's mailbox from the backend state.

        Args:
            start_history_id (str): Required. Returns history records after the specified historyId.
            user_id (str): User's email address or 'me' for the authenticated user.
            max_results (Optional[int]): Maximum number of history records to return (simulated).
        Returns:
            Optional[Dict[str, Union[List[Dict[str, Any]], str]]]: A dictionary containing history records and the current history ID,
                                                                    or None if the user data is not found.
        """
        history_data = self._get_user_history_data(user_id)
        if history_data is None:
            return None

        all_history = sorted(list(history_data.values()), key=lambda x: int(x['id']))
        filtered_history = [h for h in all_history if int(h['id']) > int(start_history_id)]

        if max_results:
            filtered_history = filtered_history[:max_results]

        current_history_id = str(self.state["gmail_history_counter"])
        return {"history": copy.deepcopy(filtered_history), "historyId": current_history_id}

    def create_delegate(self, delegate_body: Dict[str, str], user_id: str = 'me') -> Optional[Dict[str, str]]:
        """
        Adds a delegate to the specified account in the backend state.

        Args:
            delegate_body (Dict[str, str]): The delegate to add (e.g., {"delegateEmail": "delegate@example.com"}).
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, str]]: The created delegate, or None if the user data is not found or delegate email is missing.
        """
        delegates = self._get_user_settings_data(user_id).get("delegates")
        if delegates is None:
            return None

        delegate_email = delegate_body.get("delegateEmail")
        if not delegate_email:
            return None

        if delegate_email in delegates:
            return copy.deepcopy(delegates[delegate_email])

        new_delegate = {
            "delegateEmail": delegate_email,
            "verificationStatus": "pending"
        }
        delegates[delegate_email] = new_delegate
        self.state["gmail_delegate_counter"] += 1
        return copy.deepcopy(new_delegate)

    def delete_delegate(self, delegate_email: str, user_id: str = 'me') -> Optional[None]:
        """
        Removes a delegate from the specified account in the backend state.

        Args:
            delegate_email (str): The email address of the delegate to remove.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[None]: None if successful, or None if the delegate or user data is not found.
        """
        delegates = self._get_user_settings_data(user_id).get("delegates")
        if delegates is None:
            return None

        if delegate_email in delegates:
            del delegates[delegate_email]
            return None
        return None

    def get_delegate(self, delegate_email: str, user_id: str = 'me') -> Optional[Dict[str, str]]:
        """
        Gets the specified delegate from the backend state.

        Args:
            delegate_email (str): The email address of the delegate to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, str]]: The delegate, or None if the delegate or user data is not found.
        """
        delegates = self._get_user_settings_data(user_id).get("delegates")
        if delegates is None:
            return None

        delegate = delegates.get(delegate_email)
        if delegate:
            return copy.deepcopy(delegate)
        return None

    def create_filter(self, filter_body: Dict[str, Any], user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Creates a filter in the backend state.

        Args:
            filter_body (Dict[str, Any]): The filter to create (with criteria, action, etc.).
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: The created filter, or None if the user data is not found.
        """
        filters = self._get_user_settings_data(user_id).get("filters")
        if filters is None:
            return None

        self.state["gmail_filter_counter"] += 1
        new_filter_id = f"filter{self.state['gmail_filter_counter']}"
        new_filter = {
            "id": new_filter_id,
            "criteria": filter_body.get("criteria", {}),
            "action": filter_body.get("action", {})
        }
        filters[new_filter_id] = new_filter
        return copy.deepcopy(new_filter)

    def delete_filter(self, filter_id: str, user_id: str = 'me') -> Optional[None]:
        """
        Deletes a filter from the backend state.

        Args:
            filter_id (str): The ID of the filter to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[None]: None if successful, or None if the filter or user data is not found.
        """
        filters = self._get_user_settings_data(user_id).get("filters")
        if filters is None:
            return None

        if filter_id in filters:
            del filters[filter_id]
            return None
        return None

    def list_filters(self, user_id: str = 'me') -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """
        Lists all filters for the specified account from the backend state.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, List[Dict[str, Any]]]]: A dictionary containing a list of filters,
                                                        or None if the user data is not found.
        """
        filters_data = self._get_user_settings_data(user_id).get("filters")
        if filters_data is None:
            return None

        all_filters = list(filters_data.values())
        return {"filter": copy.deepcopy(all_filters)}

    def create_forwarding_address(self, forwarding_email: str, user_id: str = 'me') -> Optional[Dict[str, str]]:
        """
        Creates a forwarding address in the backend state.

        Args:
            forwarding_email (str): The email address to forward to.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, str]]: The created forwarding address, or None if the user data is not found.
        """
        forwarding_addresses = self._get_user_settings_data(user_id).get("forwarding_addresses")
        if forwarding_addresses is None:
            return None

        if forwarding_email in forwarding_addresses:
            return copy.deepcopy(forwarding_addresses[forwarding_email])

        new_forwarding_address = {
            "forwardingEmail": forwarding_email,
            "verificationStatus": "pending"
        }
        forwarding_addresses[forwarding_email] = new_forwarding_address
        self.state["gmail_forwarding_address_counter"] += 1
        return copy.deepcopy(new_forwarding_address)

    def delete_forwarding_address(self, forwarding_email: str, user_id: str = 'me') -> Optional[None]:
        """
        Deletes a forwarding address from the backend state.

        Args:
            forwarding_email (str): The forwarding address to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[None]: None if successful, or None if the forwarding address or user data is not found.
        """
        forwarding_addresses = self._get_user_settings_data(user_id).get("forwarding_addresses")
        if forwarding_addresses is None:
            return None

        if forwarding_email in forwarding_addresses:
            del forwarding_addresses[forwarding_email]
            return None
        return None

    def get_forwarding_address(self, forwarding_email: str, user_id: str = 'me') -> Optional[Dict[str, str]]:
        """
        Gets the specified forwarding address from the backend state.

        Args:
            forwarding_email (str): The forwarding address to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, str]]: The forwarding address, or None if the address or user data is not found.
        """
        forwarding_addresses = self._get_user_settings_data(user_id).get("forwarding_addresses")
        if forwarding_addresses is None:
            return None

        address = forwarding_addresses.get(forwarding_email)
        if address:
            return copy.deepcopy(address)
        return None

    def list_forwarding_addresses(self, user_id: str = 'me') -> Optional[Dict[str, List[Dict[str, str]]]]:
        """
        Lists all forwarding addresses for the specified account from the backend state.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, List[Dict[str, str]]]]: A dictionary containing a list of forwarding addresses,
                                                        or None if the user data is not found.
        """
        forwarding_addresses_data = self._get_user_settings_data(user_id).get("forwarding_addresses")
        if forwarding_addresses_data is None:
            return None

        all_addresses = list(forwarding_addresses_data.values())
        return {"forwardingAddresses": copy.deepcopy(all_addresses)}

    def create_send_as(self, send_as_body: Dict[str, Any], user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Creates a custom "from" send-as alias in the backend state.

        Args:
            send_as_body (Dict[str, Any]): The send-as alias to create.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: The created send-as alias, or None if the user data is not found or email is missing.
        """
        send_as_aliases = self._get_user_settings_data(user_id).get("send_as_aliases")
        if send_as_aliases is None:
            return None

        send_as_email = send_as_body.get("sendAsEmail")
        if not send_as_email:
            return None

        if send_as_email in send_as_aliases:
            return copy.deepcopy(send_as_aliases[send_as_email])

        new_send_as = {
            "sendAsEmail": send_as_email,
            "displayName": send_as_body.get("displayName"),
            "replyToAddress": send_as_body.get("replyToAddress"),
            "signature": send_as_body.get("signature"),
            "isPrimary": send_as_body.get("isPrimary", False),
            "verificationStatus": "pending"
        }
        send_as_aliases[send_as_email] = new_send_as
        self.state["gmail_send_as_counter"] += 1
        return copy.deepcopy(new_send_as)

    def delete_send_as(self, send_as_email: str, user_id: str = 'me') -> Optional[None]:
        """
        Deletes a custom "from" send-as alias from the backend state.

        Args:
            send_as_email (str): The send-as alias to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[None]: None if successful, or None if the alias or user data is not found.
        """
        send_as_aliases = self._get_user_settings_data(user_id).get("send_as_aliases")
        if send_as_aliases is None:
            return None

        if send_as_email in send_as_aliases:
            del send_as_aliases[send_as_email]
            return None
        return None

    def get_send_as(self, send_as_email: str, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Gets the specified send-as alias from the backend state.

        Args:
            send_as_email (str): The send-as alias to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: The send-as alias, or None if the alias or user data is not found.
        """
        send_as_aliases = self._get_user_settings_data(user_id).get("send_as_aliases")
        if send_as_aliases is None:
            return None

        alias = send_as_aliases.get(send_as_email)
        if alias:
            return copy.deepcopy(alias)
        return None

    def delete_thread(self, thread_id: str, user_id: str = 'me') -> Optional[None]:
        """
        Deletes the specified thread and its messages from the backend state.

        Args:
            thread_id (str): The ID of the thread to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[None]: None if successful, or None if the thread or user data is not found.
        """
        threads = self._get_user_threads_data(user_id)
        messages = self._get_user_messages_data(user_id)
        if threads is None or messages is None:
            return None

        if thread_id in threads:
            # Delete messages associated with the thread
            for msg in threads[thread_id].get("messages", []):
                if msg["id"] in messages:
                    del messages[msg["id"]]
            del threads[thread_id]
            return None
        return None

    def get_thread(self, thread_id: str, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Gets the specified thread from the backend state.

        Args:
            thread_id (str): The ID of the thread to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the thread, or None if the thread or user data is not found.
        """
        threads = self._get_user_threads_data(user_id)
        if threads is None:
            return None

        thread = threads.get(thread_id)
        if thread:
            return copy.deepcopy(thread)
        return None

    def modify_thread(self, thread_id: str, modify_request: Dict[str, List[str]], user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Modifies the labels applied to the thread in the backend state.

        Args:
            thread_id (str): The ID of the thread to modify.
            modify_request (Dict[str, List[str]]): The modification request (e.g., {"addLabelIds": ["LABEL_ID"], "removeLabelIds": ["LABEL_ID"]}).
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Any]]: The modified thread, or None if the thread or user data is not found.
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

        # Apply label modifications to all messages within the thread
        for msg_data in thread.get("messages", []):
            msg_id = msg_data["id"]
            if msg_id in messages:
                current_labels = set(messages[msg_id].get("labelIds", []))
                # Add labels
                messages[msg_id]["labelIds"] = list(current_labels.union(add_labels))
                # Remove labels
                messages[msg_id]["labelIds"] = [lbl for lbl in messages[msg_id]["labelIds"] if lbl not in remove_labels]

        return copy.deepcopy(thread)