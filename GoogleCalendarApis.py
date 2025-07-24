from typing import Dict, Union, List, Any, Optional
from copy import deepcopy

DEFAULT_STATE: Dict[str, Any] = {
    "users": {
        "user1@example.com": {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "user1@example.com",
            "calendar_data": {
                "calendars": {
                    "cal_1": {
                        "summary": "Personal Calendar (Alice)",
                        "timeZone": "America/New_York",
                        "id": "cal_1"
                    },
                    "cal_2": {
                        "summary": "Work Calendar (Alice)",
                        "timeZone": "America/Los_Angeles",
                        "id": "cal_2"
                    }
                },
                "events": {
                    "cal_1": { # Events for Alice's Personal Calendar
                        "event_1": {
                            "summary": "Morning Run (Alice)",
                            "location": "Central Park",
                            "start": {"dateTime": "2025-07-19T07:00:00-04:00", "timeZone": "America/New_York"},
                            "end": {"dateTime": "2025-07-19T08:00:00-04:00", "timeZone": "America/New_York"},
                            "description": "Daily 5k run.",
                            "attendees": [{"email": "user1@example.com"}],
                            "id": "event_1"
                        },
                        "event_2": {
                            "summary": "Dentist Appointment (Alice)",
                            "location": "123 Main St, Anytown",
                            "start": {"dateTime": "2025-07-20T10:00:00-04:00", "timeZone": "America/New_York"},
                            "end": {"dateTime": "2025-07-20T11:00:00-04:00", "timeZone": "America/New_York"},
                            "description": "Annual check-up.",
                            "attendees": [{"email": "user1@example.com"}],
                            "id": "event_2"
                        }
                    },
                    "cal_2": { # Events for Alice's Work Calendar
                        "event_3": {
                            "summary": "Team Meeting (Alice)",
                            "location": "Conference Room A",
                            "start": {"dateTime": "2025-07-19T09:00:00-07:00", "timeZone": "America/Los_Angeles"},
                            "end": {"dateTime": "2025-07-19T10:00:00-07:00", "timeZone": "America/Los_Angeles"},
                            "description": "Weekly sync-up.",
                            "attendees": [{"email": "user1@example.com"}, {"email": "john.doe@work.com"}],
                            "id": "event_3"
                        }
                    }
                },
                "settings": {
                    "timezone": "America/New_York", # Default timezone for new calendars/events if not specified
                    "week_start": "Sunday",
                    "event_reminders": True
                }
            }
        },
        "user2@example.com": {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "user2@example.com",
            "calendar_data": {
                "calendars": {
                    "cal_3": {
                        "summary": "Personal Calendar (Bob)",
                        "timeZone": "Europe/London",
                        "id": "cal_3"
                    },
                    "cal_4": {
                        "summary": "Project Calendar (Bob)",
                        "timeZone": "Asia/Tokyo",
                        "id": "cal_4"
                    }
                },
                "events": {
                    "cal_3": { # Events for Bob's Personal Calendar
                        "event_4": {
                            "summary": "Gym Session (Bob)",
                            "location": "Local Gym",
                            "start": {"dateTime": "2025-07-20T18:00:00+01:00", "timeZone": "Europe/London"},
                            "end": {"dateTime": "2025-07-20T19:00:00+01:00", "timeZone": "Europe/London"},
                            "description": "Evening workout.",
                            "attendees": [{"email": "user2@example.com"}],
                            "id": "event_4"
                        }
                    },
                    "cal_4": { # Events for Bob's Project Calendar
                        "event_5": {
                            "summary": "Client Demo (Bob)",
                            "location": "Online Meeting",
                            "start": {"dateTime": "2025-07-22T10:00:00+09:00", "timeZone": "Asia/Tokyo"},
                            "end": {"dateTime": "2025-07-22T11:00:00+09:00", "timeZone": "Asia/Tokyo"},
                            "description": "Present new features.",
                            "attendees": [{"email": "user2@example.com"}, {"email": "client@example.com"}],
                            "id": "event_5"
                        }
                    }
                },
                "settings": {
                    "timezone": "Europe/London",
                    "week_start": "Monday",
                    "event_reminders": False
                }
            }
        }
    },
    "current_user": "user1@example.com",
    "calendar_counter": 4, # Global counter for unique calendar IDs
    "event_counter": 5 # Global counter for unique event IDs
}

class GoogleCalendarApis:
    def __init__(self, state: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes the GoogleCalendarApis with a given state.
        If no state is provided, it uses a deep copy of the DEFAULT_STATE.

        Args:
            state (Optional[Dict[str, Any]]): The initial state for the simulator.
                                               Defaults to a deep copy of DEFAULT_STATE.
        """
        self.state: Dict[str, Any] = deepcopy(state if state is not None else DEFAULT_STATE)
        self._api_description = "This tool belongs to the GoogleCalendarAPI, which provides core functionality for managing calendars and events in Google Calendar."

    def _get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user-specific data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's data, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id)

    def _get_user_calendar_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user-specific calendar data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's calendar data, or None if not found.
        """
        user_data = self._get_user_data(user_id)
        return user_data.get("calendar_data") if user_data else None

    def _get_user_calendars(self, user_id: str) -> Optional[Dict[str, Dict[str, str]]]:
        """
        Helper to get user-specific calendars.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Dict[str, str]]]: A dictionary containing the user's calendars, or None if not found.
        """
        calendar_data = self._get_user_calendar_data(user_id)
        return calendar_data.get("calendars") if calendar_data else None

    def _get_user_events(self, user_id: str) -> Optional[Dict[str, Dict[str, Dict[str, Union[str, dict]]]]]:
        """
        Helper to get user-specific events.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Dict[str, Dict[str, Union[str, dict]]]]]: A dictionary containing the user's events, or None if not found.
        """
        calendar_data = self._get_user_calendar_data(user_id)
        return calendar_data.get("events") if calendar_data else None

    def _get_user_settings(self, user_id: str) -> Optional[Dict[str, Union[str, bool]]]:
        """
        Helper to get user-specific settings.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Union[str, bool]]]: A dictionary containing the user's settings, or None if not found.
        """
        calendar_data = self._get_user_calendar_data(user_id)
        return calendar_data.get("settings") if calendar_data else None

    def create_calendar(self, summary: str, time_zone: str = "", user_id: str = 'me') -> Dict[str, bool]:
        """
        Create a new calendar with summary and optional time zone for a specific user.

        Args:
            summary (str): Title of the calendar.
            time_zone (str, optional): Time zone of the calendar.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            creation_status (bool): True if created successfully, False otherwise.
        """
        calendars = self._get_user_calendars(user_id)
        settings = self._get_user_settings(user_id)
        events_data = self._get_user_events(user_id)

        if calendars is None or settings is None or events_data is None:
            return {"creation_status": False}

        self.state["calendar_counter"] += 1
        calendar_id = f"cal_{self.state['calendar_counter']}"

        calendars[calendar_id] = {
            "summary": summary,
            "timeZone": time_zone if time_zone else settings["timezone"],
            "id": calendar_id
        }
        events_data[calendar_id] = {} # Initialize an empty dictionary for events in this new calendar
        return {"creation_status": True}

    def get_calendar(self, calendar_id: str, user_id: str = 'me') -> Dict[str, Union[bool, dict]]:
        """
        Get a calendar by its ID for a specific user.

        Args:
            calendar_id (str): ID of the calendar to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            retrieval_status (bool): True if retrieved successfully, False otherwise.
            calendar_data (dict): Calendar details if successful.
        """
        calendars = self._get_user_calendars(user_id)
        if calendars is None:
            return {"retrieval_status": False, "calendar_data": {}}

        if calendar_id not in calendars:
            return {"retrieval_status": False, "calendar_data": {}}

        return {"retrieval_status": True, "calendar_data": deepcopy(calendars[calendar_id])}

    def delete_calendar(self, calendar_id: str, user_id: str = 'me') -> Dict[str, bool]:
        """
        Delete a calendar by its ID for a specific user.

        Args:
            calendar_id (str): ID of the calendar to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            deletion_status (bool): True if deleted successfully, False otherwise.
        """
        calendars = self._get_user_calendars(user_id)
        events_data = self._get_user_events(user_id)

        if calendars is None or events_data is None:
            return {"deletion_status": False}

        if calendar_id not in calendars:
            return {"deletion_status": False}

        del calendars[calendar_id]
        if calendar_id in events_data:
            del events_data[calendar_id]
        return {"deletion_status": True}

    def create_event(self, calendar_id: str, event_data: dict, user_id: str = 'me') -> Dict[str, bool]:
        """
        Create an event in the specified calendar for a specific user.

        Args:
            calendar_id (str): ID of the calendar.
            event_data (dict): Details of the event to create.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            creation_status (bool): True if created successfully, False otherwise.
        """
        calendars = self._get_user_calendars(user_id)
        events_data = self._get_user_events(user_id)

        if calendars is None or events_data is None:
            return {"creation_status": False}

        if calendar_id not in calendars:
            return {"creation_status": False}

        self.state["event_counter"] += 1
        event_id = f"event_{self.state['event_counter']}"

        event_data["id"] = event_id # Assign the generated ID to the event data
        events_data[calendar_id][event_id] = event_data
        return {"creation_status": True}

    def get_event(self, calendar_id: str, event_id: str, user_id: str = 'me') -> Dict[str, Union[bool, dict]]:
        """
        Get an event by its ID from a calendar for a specific user.

        Args:
            calendar_id (str): ID of the calendar.
            event_id (str): ID of the event to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            retrieval_status (bool): True if retrieved successfully, False otherwise.
            event_data (dict): Event details if successful.
        """
        events_data = self._get_user_events(user_id)
        if events_data is None:
            return {"retrieval_status": False, "event_data": {}}

        if calendar_id not in events_data or event_id not in events_data[calendar_id]:
            return {"retrieval_status": False, "event_data": {}}

        return {"retrieval_status": True, "event_data": deepcopy(events_data[calendar_id][event_id])}

    def list_events(self, calendar_id: str, time_min: str = "", time_max: str = "", user_id: str = 'me') -> Dict[str, Union[bool, list]]:
        """
        List events from a calendar within an optional time range for a specific user.

        Args:
            calendar_id (str): ID of the calendar.
            time_min (str, optional): Earliest time to include events.
            time_max (str, optional): Latest time to include events.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            retrieval_status (bool): True if retrieved successfully, False otherwise.
            events (list): List of events if successful.
        """
        events_data = self._get_user_events(user_id)
        if events_data is None:
            return {"retrieval_status": False, "events": []}

        if calendar_id not in events_data:
            return {"retrieval_status": False, "events": []}

        events = list(events_data[calendar_id].values())

        # Apply time filtering (simplified for this backend)
        if time_min or time_max:
            events = [
                event for event in events
                if (not time_min or event.get("start", {}).get("dateTime", "") >= time_min) and
                   (not time_max or event.get("end", {}).get("dateTime", "") <= time_max)
            ]

        return {"retrieval_status": True, "events": deepcopy(events)}

    def delete_event(self, calendar_id: str, event_id: str, user_id: str = 'me') -> Dict[str, bool]:
        """
        Delete an event from a calendar for a specific user.

        Args:
            calendar_id (str): ID of the calendar.
            event_id (str): ID of the event to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            deletion_status (bool): True if deleted successfully, False otherwise.
        """
        events_data = self._get_user_events(user_id)
        if events_data is None:
            return {"deletion_status": False}

        if calendar_id not in events_data or event_id not in events_data[calendar_id]:
            return {"deletion_status": False}

        del events_data[calendar_id][event_id]
        return {"deletion_status": True}

    def move_event(self, calendar_id: str, event_id: str, destination_calendar_id: str, user_id: str = 'me') -> Dict[str, Union[bool, str]]:
        """
        Move an event from one calendar to another for a specific user.

        Args:
            calendar_id (str): ID of the source calendar.
            event_id (str): ID of the event to move.
            destination_calendar_id (str): ID of the target calendar.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            move_status (bool): True if moved successfully, False otherwise.
            message (str): A message indicating the status of the move.
        """
        events_data = self._get_user_events(user_id)
        calendars = self._get_user_calendars(user_id)

        if events_data is None or calendars is None:
            return {"move_status": False, "message": "User data not found."}

        if (calendar_id not in events_data or
            event_id not in events_data[calendar_id]):
            return {"move_status": False, "message": f"Event '{event_id}' not found in source calendar '{calendar_id}'."}

        if destination_calendar_id not in calendars:
            return {"move_status": False, "message": f"Destination calendar '{destination_calendar_id}' not found."}

        self.state["event_counter"] += 1
        destination_event_id = f"event_{self.state['event_counter']}"

        event_data = events_data[calendar_id][event_id]
        del events_data[calendar_id][event_id]
        event_data["id"] = destination_event_id # Update event ID for the new location
        events_data[destination_calendar_id][destination_event_id] = event_data
        return {"move_status": True, "message": f"Event '{event_id}' moved successfully from '{calendar_id}' to '{destination_calendar_id}'."}

    def check_free_busy(self, time_min: str, time_max: str, items: list[dict], user_id: str = 'me') -> Dict[str, Union[bool, dict]]:
        """
        Check free/busy status for specified calendars for a specific user.

        Args:
            time_min (str): Start time for the check.
            time_max (str): End time for the check.
            items (list[dict]): List of calendars to check.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            retrieval_status (bool): True if check was successful, False otherwise.
            free_busy_data (dict): Free/busy information if successful.
        """
        calendars = self._get_user_calendars(user_id)
        if calendars is None:
            return {"retrieval_status": False, "free_busy_data": {}}

        free_busy_data = {}
        for item in items:
            calendar_id = item.get("id")
            if calendar_id in calendars:
                # Simple implementation - in reality this would check event times
                free_busy_data[calendar_id] = {
                    "busy": [
                        {"start": time_min, "end": time_max}  # Marking the whole period as busy for simplicity
                    ]
                }

        return {"retrieval_status": True, "free_busy_data": free_busy_data}

