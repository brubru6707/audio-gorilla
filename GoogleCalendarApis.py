import copy
import uuid
from typing import Dict, Union, Any, Optional, List
from datetime import datetime
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("GoogleCalendarApis")

class GoogleCalendarApis:
    """
    A dummy API class for simulating Google Calendar operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initialize the Google Calendar API simulator with default state.
        """
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the Google Calendar API, which provides core functionality for managing calendars and events."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Load a scenario configuration into the API simulator.

        Args:
            scenario (Dict): Scenario configuration containing users and their data.
        """
        DEFAULT_STATE_COPY = copy.deepcopy(scenario)
        self.users = DEFAULT_STATE_COPY.get("users", {})
        print("GoogleCalendarApis: Loaded scenario with users and their UUIDs.")

    def _generate_id(self) -> str:
        """
        Generate a unique ID for calendars or events.

        Returns:
            str: A generated UUID string.
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

    def _get_user_calendar_data(self, user_id: str) -> Optional[Dict]:
        """
        Get calendar data for a specific user.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict]: User's calendar data if found, None otherwise.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return None
        return self.users.get(internal_user_id, {}).get("calendar_data")

    def _get_user_calendars(self, user_id: str) -> Optional[Dict]:
        """
        Get calendars for a specific user.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict]: User's calendars if found, None otherwise.
        """
        calendar_data = self._get_user_calendar_data(user_id)
        return calendar_data.get("calendars") if calendar_data else None

    def _get_user_events(self, user_id: str) -> Optional[Dict[str, Dict]]:
        """
        Get events for a specific user.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Optional[Dict[str, Dict]]: User's events organized by calendar if found, None otherwise.
        """
        calendar_data = self._get_user_calendar_data(user_id)
        return calendar_data.get("events") if calendar_data else None

    def get_user_profile(self, user_id: str = "me") -> Dict[str, Union[bool, Dict]]:
        """
        Get profile information for a user.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, Dict]]: Dictionary with retrieval status and profile data.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"retrieval_status": False, "profile_data": {}}
        
        user_data = self.users.get(internal_user_id)
        if user_data:
            return {"retrieval_status": True, "profile_data": {"email": user_data["email"], "first_name": user_data["first_name"], "last_name": user_data["last_name"]}}
        return {"retrieval_status": False, "profile_data": {}}

    def list_calendars(self, user_id: str = "me") -> Dict[str, Union[bool, List[Dict]]]:
        """
        List all calendars for a user.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, List[Dict]]]: Dictionary with retrieval status and list of calendars.
        """
        calendars = self._get_user_calendars(user_id)
        if calendars is None:
            return {"retrieval_status": False, "calendars": []}

        return {"retrieval_status": True, "calendars": list(calendars.values())}

    def get_calendar(
        self, calendar_id: str, user_id: str = "me"
    ) -> Dict[str, Union[bool, Dict]]:
        """
        Get details for a specific calendar.

        Args:
            calendar_id (str): ID of the calendar to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, Dict]]: Dictionary with retrieval status and calendar data.
        """
        calendars = self._get_user_calendars(user_id)
        if calendars is None:
            return {"retrieval_status": False, "calendar_data": {}}
        
        calendar = calendars.get(calendar_id)
        if calendar:
            return {"retrieval_status": True, "calendar_data": copy.deepcopy(calendar)}
        return {"retrieval_status": False, "calendar_data": {}}

    def create_calendar(
        self, summary: str, time_zone: str, user_id: str = "me"
    ) -> Dict[str, Union[bool, Dict]]:
        """
        Create a new calendar for a user.

        Args:
            summary (str): Name/description of the new calendar.
            time_zone (str): Time zone for the calendar.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, Dict]]: Dictionary with creation status and new calendar data.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"creation_status": False, "calendar_data": {}}

        user_calendar_data = self.users[internal_user_id].get("calendar_data")
        if user_calendar_data is None:
            user_calendar_data = {"calendars": {}, "events": {}}
            self.users[internal_user_id]["calendar_data"] = user_calendar_data

        calendars = user_calendar_data.get("calendars")
        events = user_calendar_data.get("events")

        new_calendar_id = self._generate_id()
        new_calendar = {
            "id": new_calendar_id,
            "summary": summary,
            "timeZone": time_zone,
        }
        calendars[new_calendar_id] = new_calendar
        events[new_calendar_id] = {}

        print(f"Calendar created: {summary} for {user_id}")
        return {"creation_status": True, "calendar_data": new_calendar}

    def update_calendar(
        self, calendar_id: str, new_summary: str, user_id: str = "me"
    ) -> Dict[str, Union[bool, str]]:
        """
        Update a calendar's summary/name.

        Args:
            calendar_id (str): ID of the calendar to update.
            new_summary (str): New name/description for the calendar.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, str]]: Dictionary with update status and message.
        """
        calendars = self._get_user_calendars(user_id)
        if calendars is None:
            return {"update_status": False, "message": "User not found or no calendar data."}
        
        if calendar_id in calendars:
            calendars[calendar_id]["summary"] = new_summary
            print(f"Calendar '{calendar_id}' updated to '{new_summary}' for {user_id}")
            return {"update_status": True, "message": "Calendar updated successfully."}
        return {"update_status": False, "message": "Calendar not found."}

    def delete_calendar(
        self, calendar_id: str, user_id: str = "me"
    ) -> Dict[str, Union[bool, str]]:
        """
        Delete a calendar and all its events.

        Args:
            calendar_id (str): ID of the calendar to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, str]]: Dictionary with deletion status and message.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"delete_status": False, "message": "User not found."}
        
        user_calendar_data = self.users[internal_user_id].get("calendar_data")
        if user_calendar_data is None:
             return {"delete_status": False, "message": "User not found or no calendar data."}

        calendars = user_calendar_data.get("calendars")
        events_data = user_calendar_data.get("events")

        if calendar_id in calendars:
            del calendars[calendar_id]
            if calendar_id in events_data:
                del events_data[calendar_id]
            print(f"Calendar '{calendar_id}' and its events deleted for {user_id}")
            return {"delete_status": True, "message": "Calendar deleted successfully."}
        return {"delete_status": False, "message": "Calendar not found."}

    def list_events(
        self,
        calendar_id: str,
        user_id: str = "me",
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 10,
        page_token: Optional[str] = None,
    ) -> Dict[str, Union[bool, List[Dict], str]]:
        """
        List events in a calendar with optional filters and pagination.

        Args:
            calendar_id (str): ID of the calendar to list events from.
            user_id (str): User's email address or 'me' for the authenticated user.
            time_min (Optional[str]): Minimum start time for events (ISO format).
            time_max (Optional[str]): Maximum end time for events (ISO format).
            max_results (int): Maximum number of events to return.
            page_token (Optional[str]): Token for pagination.

        Returns:
            Dict[str, Union[bool, List[Dict], str]]: Dictionary with retrieval status, events list, and next page token.
        """
        events_by_calendar = self._get_user_events(user_id)
        if events_by_calendar is None or calendar_id not in events_by_calendar:
            return {"retrieval_status": False, "events": []}

        all_events_in_calendar = list(events_by_calendar[calendar_id].values())
        
        filtered_events = []
        for event in all_events_in_calendar:
            match = True
            if time_min:
                if event.get("start", {}).get("dateTime") < time_min:
                    match = False
            if time_max:
                if event.get("end", {}).get("dateTime") > time_max:
                    match = False
            
            if match:
                filtered_events.append(copy.deepcopy(event))

        start_index = 0
        if page_token:
            try:
                start_index = int(page_token)
            except ValueError:
                start_index = 0

        paginated_events = filtered_events[start_index : start_index + max_results]
        next_page_token = str(start_index + max_results) if start_index + max_results < len(filtered_events) else None

        return {
            "retrieval_status": True,
            "events": paginated_events,
            "nextPageToken": next_page_token,
        }

    def get_event(
        self, calendar_id: str, event_id: str, user_id: str = "me"
    ) -> Dict[str, Union[bool, Dict]]:
        """
        Get details for a specific event.

        Args:
            calendar_id (str): ID of the calendar containing the event.
            event_id (str): ID of the event to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, Dict]]: Dictionary with retrieval status and event data.
        """
        events_by_calendar = self._get_user_events(user_id)
        if events_by_calendar is None or calendar_id not in events_by_calendar:
            return {"retrieval_status": False, "event_data": {}}

        event = events_by_calendar[calendar_id].get(event_id)
        if event:
            return {"retrieval_status": True, "event_data": copy.deepcopy(event)}
        return {"retrieval_status": False, "event_data": {}}
# hi
    def create_event(
        self,
        calendar_id: str,
        summary: str,
        start_time: str,
        end_time: str,
        time_zone: str,
        description: Optional[str] = None,
        attendees: Optional[List[Dict[str, str]]] = None,
        user_id: str = "me",
    ) -> Dict[str, Union[bool, Dict]]:
        """
        Create a new event in a calendar.

        Args:
            calendar_id (str): ID of the calendar to add the event to.
            summary (str): Title/description of the event.
            start_time (str): Start time of the event (ISO format).
            end_time (str): End time of the event (ISO format).
            time_zone (str): Time zone for the event.
            description (Optional[str]): Additional description for the event.
            attendees (Optional[List[Dict[str, str]]]): List of attendees for the event.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, Dict]]: Dictionary with creation status and event data.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"creation_status": False, "message": "User not found."}
        
        user_calendar_data = self.users[internal_user_id].get("calendar_data")
        if user_calendar_data is None:
            return {"creation_status": False, "message": "User has no calendar data."}

        calendars = user_calendar_data.get("calendars")
        events_data = user_calendar_data.get("events")

        if calendar_id not in calendars:
            return {"creation_status": False, "message": "Calendar not found."}

        new_event_id = self._generate_id()
        new_event = {
            "id": new_event_id,
            "summary": summary,
            "start": {"dateTime": start_time, "timeZone": time_zone},
            "end": {"dateTime": end_time, "timeZone": time_zone},
        }
        if description:
            new_event["description"] = description
        if attendees:
            new_event["attendees"] = attendees

        events_data[calendar_id][new_event_id] = new_event

        print(f"Event '{summary}' created in calendar '{calendar_id}' for {user_id}")
        return {"creation_status": True, "event_data": new_event}

    def update_event(
        self,
        calendar_id: str,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        time_zone: Optional[str] = None,
        description: Optional[str] = None,
        attendees: Optional[List[Dict[str, str]]] = None,
        user_id: str = "me",
    ) -> Dict[str, Union[bool, str]]:
        """
        Update an existing event.

        Args:
            calendar_id (str): ID of the calendar containing the event.
            event_id (str): ID of the event to update.
            summary (Optional[str]): New title/description for the event.
            start_time (Optional[str]): New start time for the event (ISO format).
            end_time (Optional[str]): New end time for the event (ISO format).
            time_zone (Optional[str]): New time zone for the event.
            description (Optional[str]): New description for the event.
            attendees (Optional[List[Dict[str, str]]]): Updated list of attendees.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, str]]: Dictionary with update status and message.
        """
        events_by_calendar = self._get_user_events(user_id)
        if events_by_calendar is None or calendar_id not in events_by_calendar:
            return {"update_status": False, "message": "User or calendar not found."}
        
        event = events_by_calendar[calendar_id].get(event_id)
        if not event:
            return {"update_status": False, "message": "Event not found."}

        if summary:
            event["summary"] = summary
        if start_time:
            event["start"]["dateTime"] = start_time
        if end_time:
            event["end"]["dateTime"] = end_time
        if time_zone:
            event["start"]["timeZone"] = time_zone
            event["end"]["timeZone"] = time_zone
        if description is not None:
            event["description"] = description
        if attendees is not None:
            event["attendees"] = attendees

        print(f"Event '{event_id}' updated in calendar '{calendar_id}' for {user_id}")
        return {"update_status": True, "message": "Event updated successfully."}

    def delete_event(
        self, calendar_id: str, event_id: str, user_id: str = "me"
    ) -> Dict[str, Union[bool, str]]:
        """
        Delete an event from a calendar.

        Args:
            calendar_id (str): ID of the calendar containing the event.
            event_id (str): ID of the event to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, str]]: Dictionary with deletion status and message.
        """
        events_by_calendar = self._get_user_events(user_id)
        if events_by_calendar is None or calendar_id not in events_by_calendar:
            return {"delete_status": False, "message": "User or calendar not found."}
        
        if event_id in events_by_calendar[calendar_id]:
            del events_by_calendar[calendar_id][event_id]
            print(f"Event '{event_id}' deleted from calendar '{calendar_id}' for {user_id}")
            return {"delete_status": True, "message": "Event deleted successfully."}
        return {"delete_status": False, "message": "Event not found."}

    def move_event(
        self,
        calendar_id: str,
        event_id: str,
        destination_calendar_id: str,
        user_id: str = "me",
    ) -> Dict[str, Union[bool, str]]:
        """
        Move an event from one calendar to another.

        Args:
            calendar_id (str): ID of the source calendar.
            event_id (str): ID of the event to move.
            destination_calendar_id (str): ID of the destination calendar.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, str]]: Dictionary with move status and message.
        """
        events_by_calendar = self._get_user_events(user_id)
        if events_by_calendar is None:
            return {"move_status": False, "message": "User not found or no event data."}

        source_events = events_by_calendar.get(calendar_id)
        destination_events = events_by_calendar.get(destination_calendar_id)

        if not source_events or event_id not in source_events:
            return {"move_status": False, "message": "Source calendar or event not found."}
        if not destination_events:
            return {"move_status": False, "message": "Destination calendar not found."}

        event_to_move = source_events[event_id]
        
        destination_events[event_id] = copy.deepcopy(event_to_move)
        del source_events[event_id]

        print(f"Event '{event_id}' moved from '{calendar_id}' to '{destination_calendar_id}' for {user_id}")
        return {"move_status": True, "message": f"Event '{event_id}' moved successfully from '{calendar_id}' to '{destination_calendar_id}'."}

    def check_free_busy(self, time_min: str, time_max: str, items: List[Dict], user_id: str = 'me') -> Dict[str, Union[bool, Dict]]:
        """
        Check free/busy status for multiple calendars within a time range.

        Args:
            time_min (str): Start of time range to check (ISO format).
            time_max (str): End of time range to check (ISO format).
            items (List[Dict]): List of calendars to check (each with 'id' field).
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict[str, Union[bool, Dict]]: Dictionary with retrieval status and free/busy data.
        """
        calendars_data = self._get_user_calendars(user_id)
        events_data = self._get_user_events(user_id)

        if calendars_data is None or events_data is None:
            return {"retrieval_status": False, "free_busy_data": {}}

        free_busy_data = {}
        for item in items:
            calendar_id = item.get("id")
            if calendar_id in calendars_data:
                busy_intervals = []
                
                check_start = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
                check_end = datetime.fromisoformat(time_max.replace('Z', '+00:00'))

                for event_id, event in events_data.get(calendar_id, {}).items():
                    event_start_str = event.get("start", {}).get("dateTime")
                    event_end_str = event.get("end", {}).get("dateTime")

                    if event_start_str and event_end_str:
                        event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00') if event_start_str.endswith('Z') else event_start_str)
                        event_end = datetime.fromisoformat(event_end_str.replace('Z', '+00:00') if event_end_str.endswith('Z') else event_end_str)

                        if max(check_start, event_start) < min(check_end, event_end):
                            busy_intervals.append({
                                "start": event_start_str,
                                "end": event_end_str
                            })
                
                free_busy_data[calendar_id] = {"busy": busy_intervals}
            else:
                free_busy_data[calendar_id] = {"busy": [], "error": "Calendar not found."}

        return {"retrieval_status": True, "free_busy_data": free_busy_data}

    def reset_data(self) -> Dict[str, bool]:
        """
        Reset all data to default state.

        Returns:
            Dict[str, bool]: Dictionary with reset status.
        """
        self._load_scenario(DEFAULT_STATE)
        print("GoogleCalendarApis: All dummy data reset to default state.")
        return {"reset_status": True}