from typing import Dict, Union, List
from copy import deepcopy

DEFAULT_STATE = {
    "username": "user@example.com",
    "password": "password123",
    "authorized": True, # Set to True to simulate a logged-in user with data
    "calendars": {
        "cal_1": {
            "summary": "Personal Calendar",
            "timeZone": "America/New_York",
            "id": "cal_1"
        },
        "cal_2": {
            "summary": "Work Calendar",
            "timeZone": "America/Los_Angeles",
            "id": "cal_2"
        },
        "cal_3": {
            "summary": "Family Events",
            "timeZone": "Europe/London",
            "id": "cal_3"
        }
    },
    "events": {
        "cal_1": { # Events for Personal Calendar
            "event_1": {
                "summary": "Morning Run",
                "location": "Central Park",
                "start": {"dateTime": "2025-07-19T07:00:00-04:00", "timeZone": "America/New_York"},
                "end": {"dateTime": "2025-07-19T08:00:00-04:00", "timeZone": "America/New_York"},
                "description": "Daily 5k run.",
                "attendees": [{"email": "user@example.com"}],
                "id": "event_1"
            },
            "event_2": {
                "summary": "Dentist Appointment",
                "location": "123 Main St, Anytown",
                "start": {"dateTime": "2025-07-20T10:00:00-04:00", "timeZone": "America/New_York"},
                "end": {"dateTime": "2025-07-20T11:00:00-04:00", "timeZone": "America/New_York"},
                "description": "Annual check-up.",
                "attendees": [{"email": "user@example.com"}],
                "id": "event_2"
            }
        },
        "cal_2": { # Events for Work Calendar
            "event_1": {
                "summary": "Team Meeting",
                "location": "Conference Room A",
                "start": {"dateTime": "2025-07-19T09:00:00-07:00", "timeZone": "America/Los_Angeles"},
                "end": {"dateTime": "2025-07-19T10:00:00-07:00", "timeZone": "America/Los_Angeles"},
                "description": "Weekly sync-up.",
                "attendees": [{"email": "user@example.com"}, {"email": "john.doe@work.com"}],
                "id": "event_1"
            },
            "event_2": {
                "summary": "Project Deadline",
                "location": "Remote",
                "start": {"dateTime": "2025-07-22T17:00:00-07:00", "timeZone": "America/Los_Angeles"},
                "end": {"dateTime": "2025-07-22T17:00:00-07:00", "timeZone": "America/Los_Angeles"},
                "description": "Final submission for Q3 project.",
                "attendees": [{"email": "user@example.com"}],
                "id": "event_2"
            }
        },
        "cal_3": { # Events for Family Events
            "event_1": {
                "summary": "Kids' Soccer Game",
                "location": "Community Park",
                "start": {"dateTime": "2025-07-21T14:00:00+01:00", "timeZone": "Europe/London"},
                "end": {"dateTime": "2025-07-21T15:30:00+01:00", "timeZone": "Europe/London"},
                "description": "Cheer on the little ones!",
                "attendees": [{"email": "user@example.com"}, {"email": "spouse@example.com"}],
                "id": "event_1"
            }
        }
    },
    "settings": {
        "timezone": "America/New_York", # Default timezone for new calendars/events if not specified
        "week_start": "Sunday",
        "event_reminders": True
    }
}

class GoogleCalendarApis:
    def __init__(self):
        # Declare all instance variables that will hold the backend state
        self.username: str
        self.password: str
        self.authorized: bool
        self.calendars: Dict[str, Dict[str, str]]  # calendar_id -> calendar_data
        self.events: Dict[str, Dict[str, Dict[str, Union[str, dict]]]]  # calendar_id -> event_id -> event_data
        self.settings: Dict[str, Union[str, bool]]
        self._api_description = "This tool belongs to the GoogleCalendarAPI, which provides core functionality for managing calendars and events in Google Calendar."
        
        # Load the default scenario to set up the initial backend state
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: dict) -> None:
        """
        Load a scenario into the GoogleCalendar instance. This method initializes
        the instance variables with data from the provided scenario dictionary,
        falling back to DEFAULT_STATE values if a key is not present in the scenario.
        
        Args:
            scenario (dict): A dictionary containing Google Calendar data.
        """
        # Create a deep copy of the default state to ensure tests or scenarios
        # don't modify the original DEFAULT_STATE object.
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        
        # Populate instance variables using data from the scenario or default values
        self.username = scenario.get("username", DEFAULT_STATE_COPY["username"])
        self.password = scenario.get("password", DEFAULT_STATE_COPY["password"])
        self.authorized = scenario.get("authorized", DEFAULT_STATE_COPY["authorized"])
        self.calendars = scenario.get("calendars", DEFAULT_STATE_COPY["calendars"])
        self.events = scenario.get("events", DEFAULT_STATE_COPY["events"])
        self.settings = scenario.get("settings", DEFAULT_STATE_COPY["settings"])

    def create_calendar(self, summary: str, time_zone: str = "") -> Dict[str, bool]:
        """
        Create a new calendar with summary and optional time zone.

        Args:
            summary (str): Title of the calendar.
            time_zone (str, optional): Time zone of the calendar.

        Returns:
            creation_status (bool): True if created successfully, False otherwise.
        """
        # Check if the user is authorized before performing the action
        if not self.authorized:
            return {"creation_status": False}
            
        # Generate a unique ID for the new calendar
        calendar_id = f"cal_{len(self.calendars) + 1}"
        
        # Store the new calendar in the self.calendars dictionary
        self.calendars[calendar_id] = {
            "summary": summary,
            "timeZone": time_zone if time_zone else self.settings["timezone"], # Use provided timezone or default setting
            "id": calendar_id
        }
        # Initialize an empty dictionary for events in this new calendar
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
        # Check if the user is authorized
        if not self.authorized:
            return {"retrieval_status": False, "calendar_data": {}}
            
        # Check if the calendar exists in self.calendars
        if calendar_id not in self.calendars:
            return {"retrieval_status": False, "calendar_data": {}}
            
        # Return the calendar data
        return {"retrieval_status": True, "calendar_data": self.calendars[calendar_id]}

    def delete_calendar(self, calendar_id: str) -> Dict[str, bool]:
        """
        Delete a calendar by its ID.

        Args:
            calendar_id (str): ID of the calendar to delete.

        Returns:
            deletion_status (bool): True if deleted successfully, False otherwise.
        """
        # Check if the user is authorized
        if not self.authorized:
            return {"deletion_status": False}
            
        # Check if the calendar exists
        if calendar_id not in self.calendars:
            return {"deletion_status": False}
            
        # Delete the calendar and its associated events
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
        # Check if the user is authorized
        if not self.authorized:
            return {"creation_status": False}
            
        # Check if the target calendar exists
        if calendar_id not in self.calendars:
            return {"creation_status": False}
            
        # Generate a unique ID for the new event within the calendar
        event_id = f"event_{len(self.events.get(calendar_id, {})) + 1}"
        
        # Add the event to the specified calendar's events
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
        # Check if the user is authorized
        if not self.authorized:
            return {"retrieval_status": False, "event_data": {}}
            
        # Check if the calendar and event exist
        if calendar_id not in self.events or event_id not in self.events[calendar_id]:
            return {"retrieval_status": False, "event_data": {}}
            
        # Return the event data
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
        # Check if the user is authorized
        if not self.authorized:
            return {"retrieval_status": False, "events": []}
            
        # Check if the calendar exists
        if calendar_id not in self.events:
            return {"retrieval_status": False, "events": []}
            
        # Retrieve all events for the specified calendar
        events = list(self.events[calendar_id].values())
        
        # Apply time filtering (simplified for this backend)
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
        # Check if the user is authorized
        if not self.authorized:
            return {"deletion_status": False}
            
        # Check if the calendar and event exist
        if calendar_id not in self.events or event_id not in self.events[calendar_id]:
            return {"deletion_status": False}
            
        # Delete the event
        del self.events[calendar_id][event_id]
        return {"deletion_status": True}

    def move_event(self, calendar_id: str, event_id: str, destination_calendar_id: str) -> Dict[str, Union[bool, str]]:
        """
        Move an event from one calendar to another.

        Args:
            calendar_id (str): ID of the source calendar.
            event_id (str): ID of the event to move.
            destination_calendar_id (str): ID of the target calendar.

        Returns:
            move_status (bool): True if moved successfully, False otherwise.
            message (str): A message indicating the status of the move.
        """
        if not self.authorized:
            return {"move_status": False, "message": "Unauthorized."}
            
        if (calendar_id not in self.events or 
            event_id not in self.events[calendar_id]):
            return {"move_status": False, "message": f"Event '{event_id}' not found in source calendar '{calendar_id}'."}
        
        if destination_calendar_id not in self.calendars:
            return {"move_status": False, "message": f"Destination calendar '{destination_calendar_id}' not found."}

        destination_event_id = f"event_{len(self.events.get(destination_calendar_id, {})) + 1}"

        event_data = self.events[calendar_id][event_id]
        del self.events[calendar_id][event_id]
        self.events[destination_calendar_id][destination_event_id] = event_data
        return {"move_status": True, "message": f"Event '{event_id}' moved successfully from '{calendar_id}' to '{destination_calendar_id}'."}
    
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