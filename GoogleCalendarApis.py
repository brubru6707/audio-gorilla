"""
Inspired by https://developers.google.com/workspace/calendar/api/guides/overview

-Requires the user to be authenticated before making requests, so this implementation
using a stateful approach. 
-There are some different naming conventions than in the actual code (e.g., POST /calendars
and insert_calendar(...)---it's just a prefrence thing (we belive insert_calendar is more descriptive
than post_calendar))
-Some parts of Google Calendar aren't implemented here (e.g., ACLs, colors, settings, etc.) for brevity.
The focus was on core calendar and event management functionality.
"""
import copy
import uuid
from typing import Dict, Union, Any, Optional, List
from datetime import datetime
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("GoogleCalendarApis")

class GoogleCalendarApis:
    """
    A API class for simulating Google Calendar operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initialize the Google Calendar API simulator with default state.
        """
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the Google Calendar API, which provides core functionality for managing calendars and events."
        self.current_user: Optional[str] = None  # Currently authenticated user ID
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Load a scenario configuration into the API simulator.
        Args:
            scenario (Dict): Scenario configuration containing users and their data.
        """
        self.users = copy.deepcopy(scenario).get("users", {})
        # Set first user as authenticated user by default
        if self.users and not self.current_user:
            self.current_user = next(iter(self.users.keys()))
        print("GoogleCalendarApis: Loaded scenario with users and their UUIDs.")

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
        print(f"GoogleCalendarApis: Authenticated as {email}")
        return {"success": True, "message": f"Authenticated as {email}"}

    def _resolve_calendar_id(self, calendar_id: str) -> Optional[str]:
        """
        Resolve "primary" keyword to user's primary calendar ID.
        Args:
            calendar_id (str): Calendar ID or "primary" keyword.
        Returns:
            Optional[str]: Resolved calendar ID, or None if not found.
        """
        if calendar_id == "primary":
            # Return the first calendar ID (primary calendar) for the authenticated user
            calendars = self._get_user_calendars(self.current_user) if self.current_user else None
            if calendars:
                return next(iter(calendars.keys()))
            return None
        return calendar_id

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
        return next((uid for uid, data in self.users.items() if data.get("email") == email), None)

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """
        Get user email by internal user ID.
        Args:
            user_id (str): Internal user ID.
        Returns:
            Optional[str]: User's email address if found, None otherwise.
        """
        return self.users.get(user_id, {}).get("email")

    def _get_user_calendar_data(self, user_id: str) -> Optional[Dict]:
        """
        Get calendar data for a specific user (internal method).
        Args:
            user_id (str): The internal user ID.
        Returns:
            Optional[Dict]: User's calendar data if found, None otherwise.
        """
        return self.users.get(user_id, {}).get("calendar_data")

    def _get_current_user_id(self) -> Optional[str]:
        """
        Get the current authenticated user ID.
        Returns:
            Optional[str]: Current user ID or None if not authenticated.
        """
        return self.current_user

    def _ensure_authenticated(self) -> str:
        """
        Ensure a user is authenticated and return their ID.
        Returns:
            str: Authenticated user ID.
        Raises:
            Exception: If no user is authenticated.
        """
        if not self.current_user:
            raise Exception("No authenticated user. Call authenticate() first.")
        return self.current_user

    def _get_user_calendars(self, user_id: str) -> Optional[Dict]:
        """
        Get calendars for a specific user (internal method).
        Args:
            user_id (str): The internal user ID.
        Returns:
            Optional[Dict]: User's calendars if found, None otherwise.
        """
        calendar_data = self._get_user_calendar_data(user_id)
        return calendar_data.get("calendars") if calendar_data else None

    def _get_user_events(self, user_id: str) -> Optional[Dict[str, Dict]]:
        """
        Get events for a specific user (internal method).
        Args:
            user_id (str): The internal user ID.
        Returns:
            Optional[Dict[str, Dict]]: User's events organized by calendar if found, None otherwise.
        """
        calendar_data = self._get_user_calendar_data(user_id)
        return calendar_data.get("events") if calendar_data else None

    def list_calendar_list(self) -> Dict[str, Any]:
        """
        Returns the calendars on the user's calendar list.
        Real API endpoint: GET /users/me/calendarList
        
        Returns:
            Dict[str, Any]: Calendar list with items array.
        """
        user_id = self._ensure_authenticated()
        calendars = self._get_user_calendars(user_id)
        
        if not calendars:
            return {
                "kind": "calendar#calendarList",
                "etag": self._generate_id(),
                "items": []
            }
        
        items = []
        for cal_id, cal_data in calendars.items():
            items.append({
                "kind": "calendar#calendarListEntry",
                "etag": self._generate_id(),
                "id": cal_id,
                "summary": cal_data.get("summary", ""),
                "timeZone": cal_data.get("timeZone", "UTC"),
                "colorId": cal_data.get("colorId", "1"),
                "backgroundColor": cal_data.get("backgroundColor", "#9fe1e7"),
                "foregroundColor": cal_data.get("foregroundColor", "#000000"),
                "selected": cal_data.get("selected", True),
                "accessRole": cal_data.get("accessRole", "owner"),
                "defaultReminders": cal_data.get("defaultReminders", []),
                "primary": cal_data.get("primary", False)
            })
        
        return {
            "kind": "calendar#calendarList",
            "etag": self._generate_id(),
            "items": items
        }

    def get_calendar(self, calendar_id: str) -> Dict[str, Any]:
        """
        Returns metadata for a calendar.
        Real API endpoint: GET /calendars/calendarId
        
        Args:
            calendar_id (str): Calendar identifier. To retrieve calendar IDs call the calendarList.list method.
                              If you want to access the primary calendar, use the "primary" keyword.
        Returns:
            Dict[str, Any]: Calendar resource.
        Raises:
            Exception: If calendar not found.
        """
        user_id = self._ensure_authenticated()
        calendar_id = self._resolve_calendar_id(calendar_id)
        
        calendars = self._get_user_calendars(user_id)
        if not calendars or calendar_id not in calendars:
            raise Exception(f"Calendar not found: {calendar_id}")
        
        calendar = calendars[calendar_id]
        return {
            "kind": "calendar#calendar",
            "etag": self._generate_id(),
            "id": calendar_id,
            "summary": calendar.get("summary", ""),
            "description": calendar.get("description", ""),
            "timeZone": calendar.get("timeZone", "UTC")
        }

    def insert_calendar(self, summary: str, time_zone: str = "UTC", description: str = "") -> Dict[str, Any]:
        """
        Creates a secondary calendar.
        Real API endpoint: POST /calendars
        
        Args:
            summary (str): Title of the calendar.
            time_zone (str): The time zone of the calendar. (Optional, defaults to UTC)
            description (str): Description of the calendar. (Optional)
        Returns:
            Dict[str, Any]: Created calendar resource.
        """
        user_id = self._ensure_authenticated()
        user_calendar_data = self.users[user_id].get("calendar_data")
        
        if user_calendar_data is None:
            user_calendar_data = {"calendars": {}, "events": {}}
            self.users[user_id]["calendar_data"] = user_calendar_data

        calendars = user_calendar_data.get("calendars")
        events = user_calendar_data.get("events")

        new_calendar_id = self._generate_id()
        new_calendar = {
            "kind": "calendar#calendar",
            "etag": self._generate_id(),
            "id": new_calendar_id,
            "summary": summary,
            "description": description,
            "timeZone": time_zone
        }
        calendars[new_calendar_id] = new_calendar
        events[new_calendar_id] = {}

        user_email = self._get_user_email_by_id(user_id)
        print(f"Calendar created: {summary} for {user_email}")
        return new_calendar

    def update_calendar(self, calendar_id: str, summary: Optional[str] = None, 
                       description: Optional[str] = None, time_zone: Optional[str] = None) -> Dict[str, Any]:
        """
        Updates metadata for a calendar.
        Real API endpoint: PUT /calendars/calendarId
        
        Args:
            calendar_id (str): Calendar identifier.
            summary (Optional[str]): Title of the calendar.
            description (Optional[str]): Description of the calendar.
            time_zone (Optional[str]): The time zone of the calendar.
        Returns:
            Dict[str, Any]: Updated calendar resource.
        Raises:
            Exception: If calendar not found.
        """
        user_id = self._ensure_authenticated()
        calendar_id = self._resolve_calendar_id(calendar_id)
        
        calendars = self._get_user_calendars(user_id)
        if not calendars or calendar_id not in calendars:
            raise Exception(f"Calendar not found: {calendar_id}")
        
        calendar = calendars[calendar_id]
        if summary is not None:
            calendar["summary"] = summary
        if description is not None:
            calendar["description"] = description
        if time_zone is not None:
            calendar["timeZone"] = time_zone
        
        user_email = self._get_user_email_by_id(user_id)
        print(f"Calendar '{calendar_id}' updated for {user_email}")
        
        return {
            "kind": "calendar#calendar",
            "etag": self._generate_id(),
            "id": calendar_id,
            "summary": calendar.get("summary", ""),
            "description": calendar.get("description", ""),
            "timeZone": calendar.get("timeZone", "UTC")
        }

    def delete_calendar(self, calendar_id: str) -> None:
        """
        Deletes a secondary calendar. Use calendars.clear for clearing all events on primary calendars.
        Real API endpoint: DELETE /calendars/calendarId
        
        Args:
            calendar_id (str): Calendar identifier.
        Raises:
            Exception: If calendar not found or trying to delete primary calendar.
        """
        user_id = self._ensure_authenticated()
        calendar_id = self._resolve_calendar_id(calendar_id)
        
        user_calendar_data = self.users[user_id].get("calendar_data")
        if user_calendar_data is None:
            raise Exception(f"Calendar not found: {calendar_id}")

        calendars = user_calendar_data.get("calendars")
        events_data = user_calendar_data.get("events")

        if calendar_id not in calendars:
            raise Exception(f"Calendar not found: {calendar_id}")

        del calendars[calendar_id]
        if calendar_id in events_data:
            del events_data[calendar_id]
        
        user_email = self._get_user_email_by_id(user_id)
        print(f"Calendar '{calendar_id}' deleted for {user_email}")

    def list_events(
        self,
        calendar_id: str,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 250,
        page_token: Optional[str] = None,
        q: Optional[str] = None,
        order_by: Optional[str] = None,
        single_events: bool = False,
    ) -> Dict[str, Any]:
        """
        Returns events on the specified calendar.
        Real API endpoint: GET /calendars/calendarId/events
        
        Args:
            calendar_id (str): Calendar identifier. To retrieve calendar IDs call the calendarList.list method.
                              If you want to access the primary calendar, use the "primary" keyword.
            time_min (Optional[str]): Lower bound (inclusive) for an event's end time to filter by. (ISO format)
            time_max (Optional[str]): Upper bound (exclusive) for an event's start time to filter by. (ISO format)
            max_results (int): Maximum number of events returned on one result page. (1-2500, default 250)
            page_token (Optional[str]): Token specifying which result page to return.
            q (Optional[str]): Free text search terms to find events that match these terms.
            order_by (Optional[str]): The order of the events returned in the result. "startTime" or "updated".
            single_events (bool): Whether to expand recurring events into instances.
        Returns:
            Dict[str, Any]: Events list resource.
        """
        user_id = self._ensure_authenticated()
        calendar_id = self._resolve_calendar_id(calendar_id)
        
        events_by_calendar = self._get_user_events(user_id)
        if events_by_calendar is None or calendar_id not in events_by_calendar:
            return {
                "kind": "calendar#events",
                "etag": self._generate_id(),
                "summary": "",
                "updated": datetime.now().isoformat() + "Z",
                "timeZone": "UTC",
                "accessRole": "owner",
                "items": []
            }

        all_events_in_calendar = list(events_by_calendar[calendar_id].values())
        
        filtered_events = []
        for event in all_events_in_calendar:
            match = True
            
            # Apply time filters
            if time_min:
                event_end = event.get("end", {}).get("dateTime", "")
                if event_end < time_min:
                    match = False
            if time_max:
                event_start = event.get("start", {}).get("dateTime", "")
                if event_start >= time_max:
                    match = False
            
            # Apply text search
            if q:
                summary = event.get("summary", "").lower()
                description = event.get("description", "").lower()
                if q.lower() not in summary and q.lower() not in description:
                    match = False
            
            if match:
                # Add standard event fields
                event_copy = copy.deepcopy(event)
                event_copy["kind"] = "calendar#event"
                event_copy["etag"] = self._generate_id()
                if "created" not in event_copy:
                    event_copy["created"] = datetime.now().isoformat() + "Z"
                if "updated" not in event_copy:
                    event_copy["updated"] = datetime.now().isoformat() + "Z"
                if "status" not in event_copy:
                    event_copy["status"] = "confirmed"
                
                filtered_events.append(event_copy)

        # Apply ordering
        if order_by == "startTime":
            filtered_events.sort(key=lambda e: e.get("start", {}).get("dateTime", ""))
        elif order_by == "updated":
            filtered_events.sort(key=lambda e: e.get("updated", ""))

        # Apply pagination
        start_index = 0
        if page_token:
            try:
                start_index = int(page_token)
            except ValueError:
                start_index = 0

        paginated_events = filtered_events[start_index : start_index + max_results]
        next_page_token = str(start_index + max_results) if start_index + max_results < len(filtered_events) else None

        result = {
            "kind": "calendar#events",
            "etag": self._generate_id(),
            "summary": "",
            "updated": datetime.now().isoformat() + "Z",
            "timeZone": "UTC",
            "accessRole": "owner",
            "items": paginated_events
        }
        
        if next_page_token:
            result["nextPageToken"] = next_page_token
        
        return result

    def get_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        """
        Returns an event based on its calendar ID and event ID.
        Real API endpoint: GET /calendars/calendarId/events/eventId
        
        Args:
            calendar_id (str): Calendar identifier. To retrieve calendar IDs call the calendarList.list method.
                              If you want to access the primary calendar, use the "primary" keyword.
            event_id (str): Event identifier.
        Returns:
            Dict[str, Any]: Event resource.
        Raises:
            Exception: If event not found.
        """
        user_id = self._ensure_authenticated()
        calendar_id = self._resolve_calendar_id(calendar_id)
        
        events_by_calendar = self._get_user_events(user_id)
        if not events_by_calendar or calendar_id not in events_by_calendar:
            raise Exception(f"Calendar not found: {calendar_id}")

        event = events_by_calendar[calendar_id].get(event_id)
        if not event:
            raise Exception(f"Event not found: {event_id}")
        
        event_copy = copy.deepcopy(event)
        event_copy["kind"] = "calendar#event"
        event_copy["etag"] = self._generate_id()
        if "created" not in event_copy:
            event_copy["created"] = datetime.now().isoformat() + "Z"
        if "updated" not in event_copy:
            event_copy["updated"] = datetime.now().isoformat() + "Z"
        if "status" not in event_copy:
            event_copy["status"] = "confirmed"
        
        return event_copy

    def insert_event(
        self,
        calendar_id: str,
        summary: str,
        start_time: str,
        end_time: str,
        time_zone: str = "UTC",
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Creates an event.
        Real API endpoint: POST /calendars/calendarId/events
        
        Args:
            calendar_id (str): Calendar identifier. To retrieve calendar IDs call the calendarList.list method.
                              If you want to access the primary calendar, use the "primary" keyword.
            summary (str): Title of the event.
            start_time (str): The start time of the event (ISO format).
            end_time (str): The end time of the event (ISO format).
            time_zone (str): The time zone of the event. (defaults to UTC)
            description (Optional[str]): Description of the event.
            location (Optional[str]): Geographic location of the event as free-form text.
            attendees (Optional[List[Dict[str, str]]]): The attendees of the event.
        Returns:
            Dict[str, Any]: Created event resource.
        Raises:
            Exception: If calendar not found.
        """
        user_id = self._ensure_authenticated()
        calendar_id = self._resolve_calendar_id(calendar_id)
        
        user_calendar_data = self.users[user_id].get("calendar_data")
        if user_calendar_data is None:
            raise Exception(f"Calendar not found: {calendar_id}")

        calendars = user_calendar_data.get("calendars")
        events_data = user_calendar_data.get("events")

        if calendar_id not in calendars:
            raise Exception(f"Calendar not found: {calendar_id}")

        # Ensure events dictionary exists for this calendar
        if calendar_id not in events_data:
            events_data[calendar_id] = {}

        new_event_id = self._generate_id()
        new_event = {
            "kind": "calendar#event",
            "etag": self._generate_id(),
            "id": new_event_id,
            "status": "confirmed",
            "summary": summary,
            "start": {"dateTime": start_time, "timeZone": time_zone},
            "end": {"dateTime": end_time, "timeZone": time_zone},
            "created": datetime.now().isoformat() + "Z",
            "updated": datetime.now().isoformat() + "Z",
        }
        if description:
            new_event["description"] = description
        if location:
            new_event["location"] = location
        if attendees:
            new_event["attendees"] = attendees

        events_data[calendar_id][new_event_id] = new_event

        user_email = self._get_user_email_by_id(user_id)
        print(f"Event '{summary}' created in calendar '{calendar_id}' for {user_email}")
        return new_event

    def update_event(
        self,
        calendar_id: str,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        time_zone: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Updates an event.
        Real API endpoint: PUT /calendars/calendarId/events/eventId
        
        Args:
            calendar_id (str): Calendar identifier. To retrieve calendar IDs call the calendarList.list method.
                              If you want to access the primary calendar, use the "primary" keyword.
            event_id (str): Event identifier.
            summary (Optional[str]): Title of the event.
            start_time (Optional[str]): The start time of the event (ISO format).
            end_time (Optional[str]): The end time of the event (ISO format).
            time_zone (Optional[str]): The time zone of the event.
            description (Optional[str]): Description of the event.
            location (Optional[str]): Geographic location of the event as free-form text.
            attendees (Optional[List[Dict[str, str]]]): The attendees of the event.
        Returns:
            Dict[str, Any]: Updated event resource.
        Raises:
            Exception: If event not found.
        """
        user_id = self._ensure_authenticated()
        calendar_id = self._resolve_calendar_id(calendar_id)
        
        events_by_calendar = self._get_user_events(user_id)
        if not events_by_calendar or calendar_id not in events_by_calendar:
            raise Exception(f"Calendar not found: {calendar_id}")
        
        event = events_by_calendar[calendar_id].get(event_id)
        if not event:
            raise Exception(f"Event not found: {event_id}")

        if summary is not None:
            event["summary"] = summary
        if start_time is not None:
            event["start"]["dateTime"] = start_time
        if end_time is not None:
            event["end"]["dateTime"] = end_time
        if time_zone is not None:
            event["start"]["timeZone"] = time_zone
            event["end"]["timeZone"] = time_zone
        if description is not None:
            event["description"] = description
        if location is not None:
            event["location"] = location
        if attendees is not None:
            event["attendees"] = attendees
        
        event["updated"] = datetime.now().isoformat() + "Z"
        event["etag"] = self._generate_id()

        user_email = self._get_user_email_by_id(user_id)
        print(f"Event '{event_id}' updated in calendar '{calendar_id}' for {user_email}")
        
        event_copy = copy.deepcopy(event)
        event_copy["kind"] = "calendar#event"
        if "status" not in event_copy:
            event_copy["status"] = "confirmed"
        
        return event_copy

    def delete_event(self, calendar_id: str, event_id: str) -> None:
        """
        Deletes an event.
        Real API endpoint: DELETE /calendars/calendarId/events/eventId
        
        Args:
            calendar_id (str): Calendar identifier. To retrieve calendar IDs call the calendarList.list method.
                              If you want to access the primary calendar, use the "primary" keyword.
            event_id (str): Event identifier.
        Raises:
            Exception: If event not found.
        """
        user_id = self._ensure_authenticated()
        calendar_id = self._resolve_calendar_id(calendar_id)
        
        events_by_calendar = self._get_user_events(user_id)
        if not events_by_calendar or calendar_id not in events_by_calendar:
            raise Exception(f"Calendar not found: {calendar_id}")
        
        if event_id not in events_by_calendar[calendar_id]:
            raise Exception(f"Event not found: {event_id}")
        
        del events_by_calendar[calendar_id][event_id]
        user_email = self._get_user_email_by_id(user_id)
        print(f"Event '{event_id}' deleted from calendar '{calendar_id}' for {user_email}")

    def move_event(
        self,
        calendar_id: str,
        event_id: str,
        destination: str,
    ) -> Dict[str, Any]:
        """
        Moves an event to another calendar, i.e. changes an event's organizer.
        Real API endpoint: POST /calendars/calendarId/events/eventId/move
        
        Args:
            calendar_id (str): Calendar identifier of the source calendar. To retrieve calendar IDs call 
                              the calendarList.list method. If you want to access the primary calendar, 
                              use the "primary" keyword.
            event_id (str): Event identifier.
            destination (str): Calendar identifier of the target calendar where the event is to be moved to.
        Returns:
            Dict[str, Any]: Moved event resource.
        Raises:
            Exception: If event or destination calendar not found.
        """
        user_id = self._ensure_authenticated()
        calendar_id = self._resolve_calendar_id(calendar_id)
        destination = self._resolve_calendar_id(destination)
        
        events_by_calendar = self._get_user_events(user_id)
        calendars = self._get_user_calendars(user_id)
        
        if not events_by_calendar or not calendars:
            raise Exception("User calendar data not found")

        source_events = events_by_calendar.get(calendar_id)
        if not source_events or event_id not in source_events:
            raise Exception(f"Event not found: {event_id}")

        if destination not in calendars:
            raise Exception(f"Destination calendar not found: {destination}")

        # Ensure events dictionary exists for destination calendar
        if destination not in events_by_calendar:
            events_by_calendar[destination] = {}

        event = source_events[event_id]
        del source_events[event_id]
        events_by_calendar[destination][event_id] = event
        
        event["updated"] = datetime.now().isoformat() + "Z"
        event["etag"] = self._generate_id()

        user_email = self._get_user_email_by_id(user_id)
        print(f"Event '{event_id}' moved from '{calendar_id}' to '{destination}' for {user_email}")
        
        event_copy = copy.deepcopy(event)
        event_copy["kind"] = "calendar#event"
        if "status" not in event_copy:
            event_copy["status"] = "confirmed"
        
        return event_copy

    def check_free_busy(self, time_min: str, time_max: str, items: List[Dict]) -> Dict[str, Any]:
        """
        Returns free/busy information for a set of calendars.
        Real API endpoint: POST /freeBusy
        
        Args:
            time_min (str): The start of the interval for the query formatted as per RFC3339.
            time_max (str): The end of the interval for the query formatted as per RFC3339.
            items (List[Dict]): List of calendars to query. Each item should have an 'id' field.
        Returns:
            Dict[str, Any]: Free/busy response resource.
        """
        user_id = self._ensure_authenticated()
        calendars_data = self._get_user_calendars(user_id)
        events_data = self._get_user_events(user_id)

        if not calendars_data or not events_data:
            return {
                "kind": "calendar#freeBusy",
                "timeMin": time_min,
                "timeMax": time_max,
                "calendars": {}
            }

        calendars_result = {}
        for item in items:
            calendar_id = item.get("id")
            calendar_id_resolved = self._resolve_calendar_id(calendar_id)
            
            if calendar_id_resolved in calendars_data:
                busy_intervals = []
                
                # Parse query time range, ensuring timezone awareness
                try:
                    if time_min.endswith('Z'):
                        check_start = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
                    else:
                        check_start = datetime.fromisoformat(time_min)
                    
                    if time_max.endswith('Z'):
                        check_end = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
                    else:
                        check_end = datetime.fromisoformat(time_max)
                except (ValueError, AttributeError):
                    # If parsing fails, skip this calendar
                    calendars_result[calendar_id] = {
                        "errors": [{
                            "domain": "global",
                            "reason": "invalid"
                        }],
                        "busy": []
                    }
                    continue

                for _, event in events_data.get(calendar_id_resolved, {}).items():
                    event_start_str = event.get("start", {}).get("dateTime")
                    event_end_str = event.get("end", {}).get("dateTime")

                    if event_start_str and event_end_str:
                        try:
                            # Parse event times, handling various formats
                            if event_start_str.endswith('Z'):
                                event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
                            elif '+' in event_start_str or event_start_str.count('-') > 2:
                                # Has timezone info
                                event_start = datetime.fromisoformat(event_start_str)
                            else:
                                # Naive datetime - make it aware using UTC
                                event_start = datetime.fromisoformat(event_start_str).replace(tzinfo=check_start.tzinfo)
                            
                            if event_end_str.endswith('Z'):
                                event_end = datetime.fromisoformat(event_end_str.replace('Z', '+00:00'))
                            elif '+' in event_end_str or event_end_str.count('-') > 2:
                                # Has timezone info
                                event_end = datetime.fromisoformat(event_end_str)
                            else:
                                # Naive datetime - make it aware using UTC
                                event_end = datetime.fromisoformat(event_end_str).replace(tzinfo=check_end.tzinfo)

                            # Check for overlap
                            if max(check_start, event_start) < min(check_end, event_end):
                                busy_intervals.append({
                                    "start": event_start_str,
                                    "end": event_end_str
                                })
                        except (ValueError, AttributeError):
                            # Skip events with invalid datetime formats
                            continue
                
                calendars_result[calendar_id] = {
                    "busy": busy_intervals,
                    "errors": []
                }
            else:
                calendars_result[calendar_id] = {
                    "errors": [{
                        "domain": "global",
                        "reason": "notFound"
                    }],
                    "busy": []
                }

        return {
            "kind": "calendar#freeBusy",
            "timeMin": time_min,
            "timeMax": time_max,
            "calendars": calendars_result
        }

    def reset_data(self) -> Dict[str, bool]:
        """
        Reset all data to default state.
        Returns:
            Dict[str, bool]: Dictionary with reset status.
        """
        self._load_scenario(DEFAULT_STATE)
        print("GoogleCalendarApis: All data reset to default state.")
        return {"reset_status": True}