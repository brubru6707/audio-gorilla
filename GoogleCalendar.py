from typing import Dict, Union, List
from copy import deepcopy

DEFAULT_STATE = {
    "username": "user@example.com",
    "password": "password123",
    "authorized": False,
    "calendars": {},
    "events": {},
    "settings": {
        "timezone": "UTC",
        "week_start": "Sunday",
        "event_reminders": True
    }
}

class GoogleCalendar:
    def __init__(self):
        self.username: str
        self.password: str
        self.authorized: bool
        self.calendars: Dict[str, Dict[str, str]]  # calendar_id -> calendar_data
        self.events: Dict[str, Dict[str, Dict[str, Union[str, dict]]]  # calendar_id -> event_id -> event_data
        self.settings: Dict[str, Union[str, bool]]
        self._api_description = "This tool belongs to the GoogleCalendarAPI, which provides core functionality for managing calendars and events in Google Calendar."
        
    def _load_scenario(self, scenario: dict) -> None:
        """
        Load a scenario into the GoogleCalendar instance.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.username = scenario.get("username", DEFAULT_STATE_COPY["username"])
        self.password = scenario.get("password", DEFAULT_STATE_COPY["password"])
        self.authorized = scenario.get("authorized", DEFAULT_STATE_COPY["authorized"])
        self.calendars = scenario.get("calendars", DEFAULT_STATE_COPY["calendars"])
        self.events = scenario.get("events", DEFAULT_STATE_COPY["events"])
        self.settings = scenario.get("settings", DEFAULT_STATE_COPY["settings"])

    def authenticate_google_calendar(self, username: str, password: str) -> Dict[str, bool]:
        """
        Authenticate a user with username and password for Google Calendar.

        Args:
            username (str): Username of the user.
            password (str): Password of the user.

        Returns:
            authentication_status (bool): True if authenticated, False otherwise.
        """
        if username == self.username and password == self.password:
            self.authorized = True
            return {"authentication_status": True}
        return {"authentication_status": False}

    def create_calendar(self, summary: str, time_zone: str = "") -> Dict[str, bool]:
        """
        Create a new calendar with summary and optional time zone.

        Args:
            summary (str): Title of the calendar.
            time_zone (str, optional): Time zone of the calendar.

        Returns:
            creation_status (bool): True if created successfully, False otherwise.
        """
        if not self.authorized:
            return {"creation_status": False}
            
        calendar_id = f"cal_{len(self.calendars) + 1}"
        self.calendars[calendar_id] = {
            "summary": summary,
            "timeZone": time_zone if time_zone else self.settings["timezone"],
            "id": calendar_id
        }
        self.events[calendar_id] = {}
        return {"creation_status": True}

    def get_calendar(self, calendar_id: str) -> Dict[str, Union[bool, dict]]:
        """
        Get a calendar by its ID.

        Args:
            calendar_id (str): ID of the calendar to retrieve.

        Returns:
            retrieval_status (bool): True if retrieved successfully, False otherwise.
            calendar_data (dict): Calendar details if successful.
        """
        if not self.authorized:
            return {"retrieval_status": False, "calendar_data": {}}
            
        if calendar_id not in self.calendars:
            return {"retrieval_status": False, "calendar_data": {}}
            
        return {"retrieval_status": True, "calendar_data": self.calendars[calendar_id]}

    def delete_calendar(self, calendar_id: str) -> Dict[str, bool]:
        """
        Delete a calendar by its ID.

        Args:
            calendar_id (str): ID of the calendar to delete.

        Returns:
            deletion_status (bool): True if deleted successfully, False otherwise.
        """
        if not self.authorized:
            return {"deletion_status": False}
            
        if calendar_id not in self.calendars:
            return {"deletion_status": False}
            
        del self.calendars[calendar_id]
        if calendar_id in self.events:
            del self.events[calendar_id]
        return {"deletion_status": True}

    def create_event(self, calendar_id: str, event_data: dict) -> Dict[str, bool]:
        """
        Create an event in the specified calendar.

        Args:
            calendar_id (str): ID of the calendar.
            event_data (dict): Details of the event to create.

        Returns:
            creation_status (bool): True if created successfully, False otherwise.
        """
        if not self.authorized:
            return {"creation_status": False}
            
        if calendar_id not in self.calendars:
            return {"creation_status": False}
            
        event_id = f"event_{len(self.events.get(calendar_id, {})) + 1}"
        self.events[calendar_id][event_id] = event_data
        return {"creation_status": True}

    def get_event(self, calendar_id: str, event_id: str) -> Dict[str, Union[bool, dict]]:
        """
        Get an event by its ID from a calendar.

        Args:
            calendar_id (str): ID of the calendar.
            event_id (str): ID of the event to retrieve.

        Returns:
            retrieval_status (bool): True if retrieved successfully, False otherwise.
            event_data (dict): Event details if successful.
        """
        if not self.authorized:
            return {"retrieval_status": False, "event_data": {}}
            
        if calendar_id not in self.events or event_id not in self.events[calendar_id]:
            return {"retrieval_status": False, "event_data": {}}
            
        return {"retrieval_status": True, "event_data": self.events[calendar_id][event_id]}

    def list_events(self, calendar_id: str, time_min: str = "", time_max: str = "") -> Dict[str, Union[bool, list]]:
        """
        List events from a calendar within an optional time range.

        Args:
            calendar_id (str): ID of the calendar.
            time_min (str, optional): Earliest time to include events.
            time_max (str, optional): Latest time to include events.

        Returns:
            retrieval_status (bool): True if retrieved successfully, False otherwise.
            events (list): List of events if successful.
        """
        if not self.authorized:
            return {"retrieval_status": False, "events": []}
            
        if calendar_id not in self.events:
            return {"retrieval_status": False, "events": []}
            
        # Simple time filtering - in a real implementation this would be more sophisticated
        events = list(self.events[calendar_id].values())
        if time_min or time_max:
            events = [
                event for event in events
                if (not time_min or event.get("start", {}).get("dateTime", "") >= time_min) and
                   (not time_max or event.get("end", {}).get("dateTime", "") <= time_max)
            ]
            
        return {"retrieval_status": True, "events": events}

    def delete_event(self, calendar_id: str, event_id: str) -> Dict[str, bool]:
        """
        Delete an event from a calendar.

        Args:
            calendar_id (str): ID of the calendar.
            event_id (str): ID of the event to delete.

        Returns:
            deletion_status (bool): True if deleted successfully, False otherwise.
        """
        if not self.authorized:
            return {"deletion_status": False}
            
        if calendar_id not in self.events or event_id not in self.events[calendar_id]:
            return {"deletion_status": False}
            
        del self.events[calendar_id][event_id]
        return {"deletion_status": True}

    def move_event(self, calendar_id: str, event_id: str, destination_calendar_id: str) -> Dict[str, bool]:
        """
        Move an event from one calendar to another.

        Args:
            calendar_id (str): ID of the source calendar.
            event_id (str): ID of the event to move.
            destination_calendar_id (str): ID of the target calendar.

        Returns:
            move_status (bool): True if moved successfully, False otherwise.
        """
        if not self.authorized:
            return {"move_status": False}
            
        if (calendar_id not in self.events or 
            event_id not in self.events[calendar_id] or 
            destination_calendar_id not in self.calendars):
            return {"move_status": False}
            
        event_data = self.events[calendar_id][event_id]
        del self.events[calendar_id][event_id]
        self.events[destination_calendar_id][event_id] = event_data
        return {"move_status": True}

    def check_free_busy(self, time_min: str, time_max: str, items: list[dict]) -> Dict[str, Union[bool, dict]]:
        """
        Check free/busy status for specified calendars.

        Args:
            time_min (str): Start time for the check.
            time_max (str): End time for the check.
            items (list[dict]): List of calendars to check.

        Returns:
            retrieval_status (bool): True if check was successful, False otherwise.
            free_busy_data (dict): Free/busy information if successful.
        """
        if not self.authorized:
            return {"retrieval_status": False, "free_busy_data": {}}
            
        free_busy_data = {}
        for item in items:
            calendar_id = item.get("id")
            if calendar_id in self.calendars:
                # Simple implementation - in reality this would check event times
                free_busy_data[calendar_id] = {
                    "busy": [
                        {"start": time_min, "end": time_max}  # Marking the whole period as busy for simplicity
                    ]
                }
                
        return {"retrieval_status": True, "free_busy_data": free_busy_data}

    def get_setting(self, setting_name: str) -> Dict[str, Union[bool, dict]]:
        """
        Get a specific setting by name.

        Args:
            setting_name (str): Name of the setting to retrieve.

        Returns:
            retrieval_status (bool): True if retrieved successfully, False otherwise.
            setting_data (dict): Setting details if successful.
        """
        if not self.authorized:
            return {"retrieval_status": False, "setting_data": {}}
            
        if setting_name not in self.settings:
            return {"retrieval_status": False, "setting_data": {}}
            
        return {"retrieval_status": True, "setting_data": {setting_name: self.settings[setting_name]}}

    def list_settings(self) -> Dict[str, Union[bool, list]]:
        """
        List all available settings.

        Returns:
            retrieval_status (bool): True if retrieved successfully, False otherwise.
            settings (list): List of settings if successful.
        """
        if not self.authorized:
            return {"retrieval_status": False, "settings": []}
            
        return {"retrieval_status": True, "settings": list(self.settings.keys())}