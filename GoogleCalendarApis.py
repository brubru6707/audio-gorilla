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
        Initializes the GoogleCalendarApis instance with in-memory backend for development and testing.
        
        Sets up data structures for managing users, their calendars, events, and authentication state.
        Automatically loads default scenario data and authenticates as the first user.
        
        Side Effects:
            - Initializes self.users as empty dictionary (populated by _load_scenario)
            - Sets self._api_description with API identification string
            - Initializes self.current_user as None (set by _load_scenario)
            - Loads DEFAULT_STATE scenario data via _load_scenario()
            - Auto-authenticates as first user if users exist
            - Prints confirmation message about loaded scenario
            
        Note:
            This is a simulated API for development/testing purposes, not connected to real
            Google Calendar servers. All data exists only in memory and is lost when the
            instance is destroyed. Uses stateful authentication approach where current_user
            tracks the authenticated user.
            
        Example:
            >>> api = GoogleCalendarApis()
            GoogleCalendarApis: Loaded scenario with users and their UUIDs.
            >>> # API is now ready to use with pre-loaded test data
        """
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the Google Calendar API, which provides core functionality for managing calendars and events."
        self.current_user: Optional[str] = None  # Currently authenticated user ID
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the backend's state for testing or reset purposes.
        
        Replaces the current user, calendar, and event data with the provided scenario,
        enabling consistent test environments or state resets. Automatically authenticates
        as the first user if no user is currently authenticated.

        Args:
            scenario (Dict): Complete state dictionary to load. Expected structure:
                {
                    "users": {
                        "user-uuid-123": {
                            "email": str,
                            "first_name": str,
                            "last_name": str,
                            "calendar_data": {
                                "calendars": {
                                    "calendar-uuid": {...},
                                    ...
                                },
                                "events": {
                                    "calendar-uuid": {
                                        "event-uuid": {...},
                                        ...
                                    }
                                }
                            }
                        },
                        ...
                    }
                }
                If "users" key is missing, initializes with empty dict.
                
        Side Effects:
            - Deep copies scenario to prevent external modifications
            - Replaces self.users entirely with scenario data
            - If no current_user and users exist, sets current_user to first user
            - Prints confirmation message with loaded user count
            - All previous state is lost (existing calendars, events, etc.)
            
        Note:
            Creates deep copy of scenario to ensure the original DEFAULT_STATE
            remains unmodified for future resets. Auto-authentication provides
            convenient default behavior for testing.
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> custom_scenario = {"users": {...}}
            >>> api._load_scenario(custom_scenario)
            GoogleCalendarApis: Loaded scenario with users and their UUIDs.
        """
        self.users = copy.deepcopy(scenario).get("users", {})
        # Set first user as authenticated user by default
        if self.users and not self.current_user:
            self.current_user = next(iter(self.users.keys()))
        print("GoogleCalendarApis: Loaded scenario with users and their UUIDs.")

    def authenticate(self, email: str) -> Dict[str, Union[bool, str]]:
        """
        Authenticates a user and sets them as the current active user for subsequent operations.
        
        Changes the authenticated user context, affecting all future API calls until
        authenticate is called again or the instance is reset.

        Args:
            email (str): The user's email address to authenticate as.
                Example: "alice@example.com", "bob@company.com"

        Returns:
            Dict[str, Union[bool, str]]: Authentication result dictionary:
                Success: {
                    "success": True,
                    "message": "Authenticated as {email}"
                }
                Failure: {
                    "success": False,
                    "message": "User not found."
                }
                
        Side Effects:
            - Updates self.current_user to the user's UUID if successful
            - Prints confirmation message to console on success
            - All subsequent API calls will operate under this user's context
            
        Note:
            - User must exist in the backend (loaded from scenario)
            - Authentication is required before calling most API methods
            - Can switch between users by calling authenticate again
            - Email lookup is case-sensitive
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> result = api.authenticate("alice@example.com")
            GoogleCalendarApis: Authenticated as alice@example.com
            >>> if result["success"]:
            ...     # Now all API calls are made as alice
            ...     calendars = api.list_calendar_list()
            >>> 
            >>> # Switch to different user
            >>> api.authenticate("bob@company.com")
            GoogleCalendarApis: Authenticated as bob@company.com
        """
        user_id = self._get_user_id_by_email(email)
        if not user_id:
            return {"success": False, "message": "User not found."}
        
        self.current_user = user_id
        print(f"GoogleCalendarApis: Authenticated as {email}")
        return {"success": True, "message": f"Authenticated as {email}"}

    def _resolve_calendar_id(self, calendar_id: str) -> Optional[str]:
        """
        Resolves the special "primary" keyword to the user's actual primary calendar ID.
        
        Provides convenience functionality to access a user's primary calendar without
        needing to know its UUID. If a specific calendar ID is provided, returns it unchanged.

        Args:
            calendar_id (str): Calendar identifier to resolve.
                Special value: "primary" - resolves to user's primary calendar
                Regular value: Any UUID - returned unchanged
                Example: "primary", "calendar-uuid-123"

        Returns:
            Optional[str]: Resolved calendar UUID, or None if not found.
                Returns actual calendar UUID when "primary" is provided.
                Returns input unchanged when UUID is provided.
                Returns None if "primary" requested but user has no calendars.
                
        Note:
            - Primary calendar is the first calendar in user's calendars dictionary
            - Most Google Calendar API methods accept "primary" as calendar_id
            - Returns None instead of raising exception to allow caller to handle
            - Does not verify that non-"primary" IDs actually exist
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> # Resolve "primary" to actual UUID
            >>> resolved = api._resolve_calendar_id("primary")
            >>> print(resolved)  # "550e8400-e29b-41d4-a716-446655440000"
            >>> 
            >>> # Pass through regular UUID
            >>> resolved = api._resolve_calendar_id("calendar-uuid-123")
            >>> print(resolved)  # "calendar-uuid-123"
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
        Generates a universally unique identifier (UUID) for new calendars and events.
        
        Returns:
            str: A new UUID v4 string in standard format (e.g., "550e8400-e29b-41d4-a716-446655440000")
            
        Note:
            Uses Python's uuid.uuid4() which generates cryptographically strong random UUIDs.
            Collision probability is effectively zero for practical purposes.
            Used for calendar IDs, event IDs, and etag values.
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> cal_id = api._generate_id()
            >>> len(cal_id)  # Standard UUID string length
            36
        """
        return str(uuid.uuid4())

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """
        Resolves a user email address to their internal UUID identifier.
        
        Searches all users to find the one matching the provided email address.

        Args:
            email (str): The user's email address.
                Example: "alice@example.com", "bob@company.com"

        Returns:
            Optional[str]: The user's UUID if found, None if no user has that email.
                Example return: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
                
        Note:
            Uses generator expression with next() for efficient single-pass search.
            Email must match exactly (case-sensitive).
            Used internally by authenticate() and other methods requiring email lookup.
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> user_id = api._get_user_id_by_email("alice@example.com")
            >>> if user_id:
            ...     print(f"Found user: {user_id}")
        """
        return next((uid for uid, data in self.users.items() if data.get("email") == email), None)

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """
        Resolves an internal UUID identifier to user email address.
        
        Reverse lookup of _get_user_id_by_email, converting UUID to email.

        Args:
            user_id (str): The user's UUID identifier.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[str]: The user's email address if user exists, None if not found.
                Example return: "alice@example.com"
                
        Example:
            >>> api = GoogleCalendarApis()
            >>> email = api._get_user_email_by_id("user-uuid-123")
            >>> print(f"User email: {email}")
        """
        return self.users.get(user_id, {}).get("email")

    def _get_user_calendar_data(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves a user's complete calendar data structure.
        
        Returns the calendar_data dictionary containing calendars and events.

        Args:
            user_id (str): The user's internal UUID identifier.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[Dict]: The user's calendar_data dictionary if found, None if user doesn't exist.
                Structure: {
                    "calendars": {...},  # Dictionary of calendar_id: calendar_data
                    "events": {...}      # Dictionary of calendar_id: {event_id: event_data}
                }
                Returns None if user not found or has no calendar_data.
                
        Note:
            Returns reference to actual data structure (not a copy), allowing direct modification.
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> cal_data = api._get_user_calendar_data("user-uuid-123")
            >>> if cal_data:
            ...     calendars = cal_data.get("calendars", {})
            ...     print(f"User has {len(calendars)} calendars")
        """
        return self.users.get(user_id, {}).get("calendar_data")

    def _get_current_user_id(self) -> Optional[str]:
        """
        Retrieves the currently authenticated user's UUID identifier.
        
        Returns the user ID of the user currently authenticated to the API instance,
        or None if no authentication has occurred.

        Returns:
            Optional[str]: Current authenticated user's UUID if set, None otherwise.
                Example return: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
                Returns None if not authenticated.
                
        Note:
            - Does not raise exception like _ensure_authenticated()
            - Useful for checking authentication status without error
            - Returns reference to self.current_user
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> user_id = api._get_current_user_id()
            >>> if user_id:
            ...     print(f"Authenticated as: {user_id}")
            >>> else:
            ...     print("Not authenticated")
        """
        return self.current_user

    def _ensure_authenticated(self) -> str:
        """
        Verifies that a user is authenticated before performing operations.
        
        Internal helper method that guards API operations requiring authentication.
        Raises exception if no user is currently authenticated.

        Returns:
            str: The current authenticated user's UUID identifier
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        
        Raises:
            Exception: If no user is authenticated (self.current_user is None)
                Error message: "No authenticated user. Call authenticate() first."
                
        Note:
            - Called internally by most API methods as first step
            - Ensures operations always have valid user context
            - Auto-authentication in __init__ means this typically won't fail
              unless explicitly cleared
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> user_id = api._ensure_authenticated()  # Returns user UUID
            >>> # Use user_id for further operations
            >>> 
            >>> # If not authenticated:
            >>> api.current_user = None
            >>> api._ensure_authenticated()  # Raises Exception
            Exception: No authenticated user. Call authenticate() first.
        """
        if not self.current_user:
            raise Exception("No authenticated user. Call authenticate() first.")
        return self.current_user

    def _get_user_calendars(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves a user's calendars dictionary directly.
        
        Convenience method that extracts just the calendars from calendar_data.

        Args:
            user_id (str): The user's internal UUID identifier.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[Dict]: Dictionary of calendar_id: calendar_data mappings, or None if not found.
                Structure: {"calendar-uuid-1": {...}, "calendar-uuid-2": {...}, ...}
                Returns None if user not found or has no calendar_data.
                
        Example:
            >>> api = GoogleCalendarApis()
            >>> calendars = api._get_user_calendars("user-uuid-123")
            >>> if calendars:
            ...     for cal_id, cal_data in calendars.items():
            ...         print(f"{cal_id}: {cal_data.get('summary')}")
        """
        calendar_data = self._get_user_calendar_data(user_id)
        return calendar_data.get("calendars") if calendar_data else None

    def _get_user_events(self, user_id: str) -> Optional[Dict[str, Dict]]:
        """
        Retrieves a user's events organized by calendar.
        
        Returns nested dictionary structure where events are grouped by their calendar ID.

        Args:
            user_id (str): The user's internal UUID identifier.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[Dict[str, Dict]]: Nested dictionary of calendar_id: {event_id: event_data}, or None.
                Structure: {
                    "calendar-uuid-1": {
                        "event-uuid-1": {...},
                        "event-uuid-2": {...}
                    },
                    "calendar-uuid-2": {...}
                }
                Returns None if user not found or has no calendar_data.
                
        Note:
            Events are organized by calendar to maintain proper separation and associations.
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> events = api._get_user_events("user-uuid-123")
            >>> if events:
            ...     for cal_id, cal_events in events.items():
            ...         print(f"Calendar {cal_id} has {len(cal_events)} events")
        """
        calendar_data = self._get_user_calendar_data(user_id)
        return calendar_data.get("events") if calendar_data else None

    def list_calendar_list(self) -> Dict[str, Any]:
        """
        Retrieves all calendars in the authenticated user's calendar list.
        
        Returns complete calendar list with metadata including display settings,
        access roles, and default reminders for each calendar.
        
        Real API endpoint: GET /users/me/calendarList

        Returns:
            Dict[str, Any]: Calendar list resource with structure:
                {
                    "kind": "calendar#calendarList",
                    "etag": str,              # Entity tag for versioning
                    "items": [
                        {
                            "kind": "calendar#calendarListEntry",
                            "etag": str,
                            "id": str,                    # Calendar UUID
                            "summary": str,               # Calendar title
                            "timeZone": str,              # IANA timezone (e.g., "UTC", "America/New_York")
                            "colorId": str,               # Color scheme ID ("1"-"24")
                            "backgroundColor": str,       # Hex color code (e.g., "#9fe1e7")
                            "foregroundColor": str,       # Hex color code (e.g., "#000000")
                            "selected": bool,             # Visibility in calendar list
                            "accessRole": str,            # "owner", "writer", "reader", "freeBusyReader"
                            "defaultReminders": List,     # Default reminder settings
                            "primary": bool               # True for user's primary calendar
                        },
                        ...
                    ]
                }
                Returns empty items array [] if user has no calendars.
                
        Raises:
            Exception: If no user is authenticated (via _ensure_authenticated)
            
        Note:
            - Each calendar gets a new etag value per request
            - Primary calendar has primary=True flag
            - Empty calendar list is valid (new users may have no calendars)
            - Access role determines permissions for calendar operations
            - selected flag controls UI visibility, not API access
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> result = api.list_calendar_list()
            >>> print(f"Found {len(result['items'])} calendars")
            >>> for calendar in result['items']:
            ...     print(f"- {calendar['summary']} ({calendar['accessRole']})")
            ...     if calendar.get('primary'):
            ...         print("  [PRIMARY CALENDAR]")
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
        Retrieves metadata for a specific calendar by its ID.
        
        Returns detailed calendar information including title, description, and timezone.
        Supports "primary" keyword for accessing user's main calendar.
        
        Real API endpoint: GET /calendars/calendarId

        Args:
            calendar_id (str): Calendar identifier or "primary" keyword.
                Special value: "primary" - user's primary calendar
                Regular value: Calendar UUID
                Example: "primary", "calendar-uuid-123"

        Returns:
            Dict[str, Any]: Calendar resource with structure:
                {
                    "kind": "calendar#calendar",
                    "etag": str,              # Entity tag for versioning
                    "id": str,                # Calendar UUID (resolved from "primary" if applicable)
                    "summary": str,           # Calendar title
                    "description": str,       # Calendar description (may be empty)
                    "timeZone": str          # IANA timezone (e.g., "UTC", "America/New_York")
                }
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - Calendar not found: "Calendar not found: {calendar_id}"
                
        Note:
            - "primary" keyword is automatically resolved to actual calendar UUID
            - Returns new etag value per request
            - Description field may be empty string if not set
            - TimeZone affects how event times are interpreted
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Get primary calendar
            >>> primary = api.get_calendar("primary")
            >>> print(f"Primary calendar: {primary['summary']}")
            >>> print(f"Timezone: {primary['timeZone']}")
            >>> 
            >>> # Get specific calendar by ID
            >>> calendar = api.get_calendar("calendar-uuid-123")
            >>> print(f"Calendar: {calendar['summary']}")
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
        Creates a new secondary calendar for the authenticated user.
        
        Generates a new calendar with unique ID and initializes empty events collection.
        Cannot create primary calendars (users have one by default).
        
        Real API endpoint: POST /calendars

        Args:
            summary (str): Title/name of the calendar.
                Example: "Work Calendar", "Team Events", "Personal"
            time_zone (str): IANA timezone identifier for the calendar.
                Affects how event times are displayed and interpreted.
                Example: "UTC", "America/New_York", "Europe/London"
                Default: "UTC"
            description (str): Optional description of the calendar's purpose.
                Example: "Calendar for tracking team meetings and deadlines"
                Default: "" (empty string)

        Returns:
            Dict[str, Any]: Created calendar resource with structure:
                {
                    "kind": "calendar#calendar",
                    "etag": str,              # Generated entity tag
                    "id": str,                # Generated UUID
                    "summary": str,           # Provided title
                    "description": str,       # Provided description
                    "timeZone": str          # Provided timezone
                }
        
        Raises:
            Exception: If no user is authenticated (via _ensure_authenticated)
                
        Side Effects:
            - Generates new UUID for calendar ID
            - Adds calendar to user's calendars dictionary
            - Initializes empty events dictionary for this calendar
            - If user has no calendar_data, initializes it with default structure
            - Prints confirmation message with calendar name and user email
            
        Note:
            - Calendar ID is auto-generated and guaranteed unique
            - Creates secondary calendar (not primary)
            - Events collection initialized empty
            - If calendar_data doesn't exist, creates it
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Create basic calendar
            >>> cal = api.insert_calendar("Work Projects")
            Calendar created: Work Projects for alice@example.com
            >>> print(f"Created calendar: {cal['id']}")
            >>> 
            >>> # Create calendar with timezone and description
            >>> cal = api.insert_calendar(
            ...     summary="Team Events",
            ...     time_zone="America/New_York",
            ...     description="Shared calendar for team meetings"
            ... )
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
        Updates metadata for an existing calendar.
        
        Allows modification of calendar title, description, and timezone. All fields
        are optional - only provided fields will be updated.
        
        Real API endpoint: PUT /calendars/calendarId

        Args:
            calendar_id (str): Calendar identifier or "primary" keyword.
                Example: "primary", "calendar-uuid-123"
            summary (Optional[str]): New title for the calendar.
                If None, title remains unchanged.
                Example: "Updated Work Calendar"
                Default: None
            description (Optional[str]): New description for the calendar.
                If None, description remains unchanged.
                Example: "Updated to include project deadlines"
                Default: None
            time_zone (Optional[str]): New IANA timezone for the calendar.
                If None, timezone remains unchanged.
                Example: "America/Los_Angeles"
                Default: None

        Returns:
            Dict[str, Any]: Updated calendar resource with complete metadata.
                Structure same as get_calendar() return value.
                Includes new etag value.
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - Calendar not found: "Calendar not found: {calendar_id}"
                
        Side Effects:
            - Modifies specified calendar properties in backend storage
            - Generates new etag value
            - Unchanged fields retain their original values
            - Prints confirmation message with calendar ID and user email
            
        Note:
            - Only specified fields are updated; None values preserve existing data
            - "primary" keyword is automatically resolved to actual calendar UUID
            - Timezone changes affect how existing and future events are displayed
            - etag is regenerated even if no actual changes made
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Update calendar title only
            >>> updated = api.update_calendar(
            ...     calendar_id="primary",
            ...     summary="My Primary Calendar"
            ... )
            Calendar 'calendar-uuid-123' updated for alice@example.com
            >>> 
            >>> # Update multiple properties
            >>> updated = api.update_calendar(
            ...     calendar_id="calendar-uuid-456",
            ...     summary="Team Calendar",
            ...     description="Updated team schedule",
            ...     time_zone="America/New_York"
            ... )
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
        Permanently deletes a secondary calendar and all its events.
        
        Removes the calendar and all associated events from the user's account.
        Cannot be used to delete primary calendars - use calendars.clear instead.
        This operation cannot be undone.
        
        Real API endpoint: DELETE /calendars/calendarId

        Args:
            calendar_id (str): Calendar identifier or "primary" keyword.
                Note: Attempting to delete "primary" will resolve to primary calendar ID.
                Example: "calendar-uuid-123"

        Returns:
            None: This method doesn't return a value on success.
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - Calendar not found: "Calendar not found: {calendar_id}"
                
        Side Effects:
            - Permanently removes calendar from backend storage
            - Permanently removes all events associated with this calendar
            - All calendar and event data is lost
            - Cannot be undone or recovered
            - Prints confirmation message with calendar ID and user email
            
        Note:
            - This bypasses any trash mechanism; deletion is immediate and permanent
            - Use calendars.clear to remove events while keeping the calendar
            - "primary" keyword is resolved but deleting primary calendar may not be desired
            - All events in calendar are deleted without individual notifications
            - Real Google Calendar API prevents primary calendar deletion
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Delete a secondary calendar
            >>> api.delete_calendar("calendar-uuid-123")
            Calendar 'calendar-uuid-123' deleted for alice@example.com
            >>> 
            >>> # WARNING: This would delete primary calendar (not typical)
            >>> # api.delete_calendar("primary")  # Not recommended!
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
        Retrieves events from a specified calendar with filtering and pagination support.
        
        Returns list of events matching specified criteria including time range, text search,
        and ordering preferences. Supports pagination for large result sets.
        
        Real API endpoint: GET /calendars/calendarId/events

        Args:
            calendar_id (str): Calendar identifier or "primary" keyword.
                Example: "primary", "calendar-uuid-123"
            time_min (Optional[str]): Lower bound (inclusive) for event's end time to filter by.
                Events ending at or after this time are included.
                Format: ISO 8601 (e.g., "2025-01-01T00:00:00Z")
                Default: None (no lower bound)
            time_max (Optional[str]): Upper bound (exclusive) for event's start time to filter by.
                Events starting before this time are included.
                Format: ISO 8601 (e.g., "2025-12-31T23:59:59Z")
                Default: None (no upper bound)
            max_results (int): Maximum number of events to return per page.
                Valid range: 1-2500
                Default: 250
            page_token (Optional[str]): Token for continuing a previous list request.
                Obtained from nextPageToken in previous response.
                Value is string representation of start index.
                Default: None (start from beginning)
            q (Optional[str]): Free text search terms to find matching events.
                Searches in both event summary and description fields.
                Case-insensitive search.
                Example: "meeting", "project review"
                Default: None (no text filtering)
            order_by (Optional[str]): Sort order for returned events.
                Valid values:
                - "startTime": Sort by event start time (ascending)
                - "updated": Sort by last update time (ascending)
                - None: No specific ordering
                Default: None
            single_events (bool): Whether to expand recurring events into instances.
                Currently not implemented - included for API compatibility.
                Default: False

        Returns:
            Dict[str, Any]: Events list resource with structure:
                {
                    "kind": "calendar#events",
                    "etag": str,              # Generated entity tag
                    "summary": str,           # Calendar summary (empty if not set)
                    "updated": str,           # ISO 8601 timestamp
                    "timeZone": str,          # Calendar timezone ("UTC")
                    "accessRole": str,        # User's access level ("owner")
                    "items": [
                        {
                            "kind": "calendar#event",
                            "etag": str,
                            "id": str,
                            "status": str,            # "confirmed", "tentative", "cancelled"
                            "summary": str,           # Event title
                            "description": str,       # Event description (if set)
                            "location": str,          # Event location (if set)
                            "start": {                # Start time
                                "dateTime": str,      # ISO 8601 format
                                "timeZone": str
                            },
                            "end": {                  # End time
                                "dateTime": str,
                                "timeZone": str
                            },
                            "created": str,           # ISO 8601 timestamp
                            "updated": str,           # ISO 8601 timestamp
                            "attendees": List,        # If set
                            # ... other event fields
                        },
                        ...
                    ],
                    "nextPageToken": str      # Present if more results available
                }
        
        Raises:
            Exception: If no user is authenticated (via _ensure_authenticated)
            
        Note:
            - Returns empty items array if calendar not found (graceful handling)
            - Time filters use event end/start times (not both)
            - Text search is case-insensitive and searches summary and description
            - Pagination tokens are simple string indices (not opaque tokens)
            - Events are deep copied to prevent accidental modifications
            - Standard event fields (created, updated, status) auto-added if missing
            - nextPageToken only present when more results available
            - single_events parameter accepted but not implemented
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # List all events in primary calendar
            >>> result = api.list_events("primary")
            >>> print(f"Found {len(result['items'])} events")
            >>> 
            >>> # List events in date range
            >>> result = api.list_events(
            ...     calendar_id="primary",
            ...     time_min="2025-01-01T00:00:00Z",
            ...     time_max="2025-12-31T23:59:59Z"
            ... )
            >>> 
            >>> # Search for specific events
            >>> result = api.list_events(
            ...     calendar_id="primary",
            ...     q="meeting",
            ...     order_by="startTime"
            ... )
            >>> for event in result['items']:
            ...     print(f"- {event['summary']} at {event['start']['dateTime']}")
            >>> 
            >>> # Pagination example
            >>> page1 = api.list_events("primary", max_results=10)
            >>> if 'nextPageToken' in page1:
            ...     page2 = api.list_events("primary", max_results=10, page_token=page1['nextPageToken'])
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
        Retrieves a single event by its unique identifier.
        
        Returns the complete event resource with all fields including organizer,
        attendees, reminders, and metadata.
        
        Real API endpoint: GET /calendars/calendarId/events/eventId

        Args:
            calendar_id (str): Calendar identifier or "primary" keyword.
                To retrieve calendar IDs use calendarList.list method.
                Use "primary" for user's primary calendar.
                Example: "primary", "calendar-uuid-123"
            event_id (str): Unique event identifier.
                Format: UUID string
                Example: "event-uuid-456"

        Returns:
            Dict[str, Any]: Complete event resource with structure:
                {
                    "kind": "calendar#event",
                    "etag": str,                    # Generated entity tag
                    "id": str,                      # Event identifier
                    "status": str,                  # "confirmed", "tentative", "cancelled"
                    "created": str,                 # ISO 8601 creation timestamp
                    "updated": str,                 # ISO 8601 last update timestamp
                    "summary": str,                 # Event title/name (if set)
                    "description": str,             # Event description (if set)
                    "location": str,                # Event location (if set)
                    "start": {                      # Start date/time
                        "dateTime": str,            # ISO 8601 format
                        "timeZone": str
                    },
                    "end": {                        # End date/time
                        "dateTime": str,
                        "timeZone": str
                    },
                    "attendees": [                  # If event has attendees
                        {
                            "email": str,
                            # ... other attendee fields
                        },
                        ...
                    ],
                    # ... other event fields
                }
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - Calendar not found: "Calendar not found: {calendar_id}"
                - Event not found: "Event not found: {event_id}"
                
        Note:
            - Returns deep copy to prevent accidental modifications
            - Standard fields (created, updated, status) added if missing
            - kind and etag fields automatically added
            - Event data retrieved from backend storage
            - Auto-sets "confirmed" status if not already set
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Get event from primary calendar
            >>> event = api.get_event("primary", "event-uuid-456")
            >>> print(f"Event: {event['summary']}")
            >>> print(f"When: {event['start']['dateTime']}")
            >>> print(f"Where: {event.get('location', 'No location')}")
            >>> 
            >>> # Check attendees
            >>> if 'attendees' in event:
            ...     for attendee in event['attendees']:
            ...         print(f"- {attendee['email']}")
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
        Creates a new event in the specified calendar.
        
        Adds a new event with specified details including time, location, attendees,
        and description. Auto-generates event ID and metadata fields.
        
        Real API endpoint: POST /calendars/calendarId/events

        Args:
            calendar_id (str): Calendar identifier or "primary" keyword.
                To retrieve calendar IDs use calendarList.list method.
                Use "primary" for user's primary calendar.
                Example: "primary", "calendar-uuid-123"
            summary (str): Title/name of the event.
                Example: "Team Meeting", "Project Review"
            start_time (str): Event start time in ISO 8601 format.
                Format: "YYYY-MM-DDTHH:MM:SSZ" or "YYYY-MM-DDTHH:MM:SS-HH:MM"
                Example: "2025-06-15T10:00:00Z", "2025-06-15T10:00:00-04:00"
            end_time (str): Event end time in ISO 8601 format.
                Must be after start_time.
                Format: Same as start_time
                Example: "2025-06-15T11:00:00Z"
            time_zone (str): IANA timezone identifier for the event.
                Used for displaying times in user's local timezone.
                Example: "UTC", "America/New_York", "Europe/London"
                Default: "UTC"
            description (Optional[str]): Detailed event description.
                Can be plain text or contain formatting.
                Example: "Quarterly review meeting with stakeholders"
                Default: None (not included in event)
            location (Optional[str]): Event location as free-form text.
                Can be address, room name, or any location identifier.
                Example: "Conference Room A", "123 Main St, City"
                Default: None (not included in event)
            attendees (Optional[List[Dict[str, str]]]): List of event attendees.
                Each attendee is a dictionary with email and optional fields.
                Attendee dict structure:
                    {
                        "email": str,           # Required: attendee email
                        "displayName": str,     # Optional: attendee name
                        "optional": bool,       # Optional: is attendance optional
                        "responseStatus": str,  # Optional: response status
                        # ... other fields
                    }
                Example: [{"email": "bob@example.com"}, {"email": "carol@example.com"}]
                Default: None (no attendees)

        Returns:
            Dict[str, Any]: Created event resource with structure:
                {
                    "kind": "calendar#event",
                    "etag": str,              # Generated entity tag
                    "id": str,                # Generated UUID
                    "status": "confirmed",
                    "summary": str,           # Provided title
                    "description": str,       # If provided
                    "location": str,          # If provided
                    "start": {
                        "dateTime": str,      # Provided start_time
                        "timeZone": str       # Provided time_zone
                    },
                    "end": {
                        "dateTime": str,      # Provided end_time
                        "timeZone": str       # Provided time_zone
                    },
                    "created": str,           # ISO 8601 timestamp (now)
                    "updated": str,           # ISO 8601 timestamp (now)
                    "attendees": List,        # If provided
                }
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - Calendar not found: "Calendar not found: {calendar_id}"
                
        Side Effects:
            - Creates new event in backend storage
            - Generates unique event ID (UUID)
            - Sets creation and update timestamps to current time
            - Initializes events dictionary for calendar if doesn't exist
            - Event persists in calendar until deleted
            - Prints confirmation message with event summary, calendar ID, and user email
            
        Note:
            - Event ID is auto-generated; cannot specify custom ID
            - Status automatically set to "confirmed"
            - Start time should be before end time (not validated)
            - Attendee emails should be valid (not validated)
            - Optional fields only included in result if provided
            - Event immediately available for retrieval
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Create simple event
            >>> event = api.insert_event(
            ...     calendar_id="primary",
            ...     summary="Team Meeting",
            ...     start_time="2025-06-15T10:00:00Z",
            ...     end_time="2025-06-15T11:00:00Z"
            ... )
            Event 'Team Meeting' created in calendar 'primary' for alice@example.com
            >>> print(f"Created event: {event['id']}")
            >>> 
            >>> # Create event with all details
            >>> meeting = api.insert_event(
            ...     calendar_id="primary",
            ...     summary="Project Review",
            ...     start_time="2025-06-20T14:00:00-04:00",
            ...     end_time="2025-06-20T15:30:00-04:00",
            ...     time_zone="America/New_York",
            ...     description="Q1 project status review",
            ...     location="Conference Room A",
            ...     attendees=[
            ...         {"email": "bob@example.com"},
            ...         {"email": "carol@example.com"}
            ...     ]
            ... )
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
        Updates an existing event with new details.
        
        Modifies specific fields of an event while preserving unspecified fields.
        Only fields provided as arguments will be updated.
        
        Real API endpoint: PUT /calendars/calendarId/events/eventId

        Args:
            calendar_id (str): Calendar identifier or "primary" keyword.
                To retrieve calendar IDs use calendarList.list method.
                Use "primary" for user's primary calendar.
                Example: "primary", "calendar-uuid-123"
            event_id (str): Unique event identifier to update.
                Format: UUID string
                Example: "event-uuid-456"
            summary (Optional[str]): New event title/name.
                If None, existing summary is preserved.
                Example: "Updated Team Meeting"
                Default: None (no change)
            start_time (Optional[str]): New event start time in ISO 8601 format.
                If None, existing start time is preserved.
                Format: "YYYY-MM-DDTHH:MM:SSZ" or "YYYY-MM-DDTHH:MM:SS-HH:MM"
                Example: "2025-06-15T10:00:00Z"
                Default: None (no change)
            end_time (Optional[str]): New event end time in ISO 8601 format.
                If None, existing end time is preserved.
                Should be after start_time if both are provided.
                Format: Same as start_time
                Example: "2025-06-15T11:30:00Z"
                Default: None (no change)
            time_zone (Optional[str]): New IANA timezone identifier.
                If None, existing timezone is preserved.
                Applied to both start and end times.
                Example: "America/New_York", "Europe/London"
                Default: None (no change)
            description (Optional[str]): New event description.
                If None, existing description is preserved.
                Example: "Updated meeting agenda"
                Default: None (no change)
            location (Optional[str]): New event location.
                If None, existing location is preserved.
                Example: "Conference Room B"
                Default: None (no change)
            attendees (Optional[List[Dict[str, str]]]): New attendees list.
                If None, existing attendees are preserved.
                Replaces entire attendees list (not merged).
                Each attendee dict structure:
                    {"email": str, "displayName": str, ...}
                Example: [{"email": "newperson@example.com"}]
                Default: None (no change)

        Returns:
            Dict[str, Any]: Updated event resource with structure:
                {
                    "kind": "calendar#event",
                    "etag": str,              # Newly generated
                    "id": str,                # Same as input event_id
                    "status": str,            # "confirmed" (default if missing)
                    "summary": str,           # Updated or existing
                    "description": str,       # Updated or existing (if set)
                    "location": str,          # Updated or existing (if set)
                    "start": {
                        "dateTime": str,      # Updated or existing
                        "timeZone": str       # Updated or existing
                    },
                    "end": {
                        "dateTime": str,      # Updated or existing
                        "timeZone": str       # Updated or existing
                    },
                    "created": str,           # Original creation timestamp
                    "updated": str,           # Current timestamp (now)
                    "attendees": List,        # Updated or existing (if set)
                }
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - Calendar not found: "Calendar not found: {calendar_id}"
                - Event not found: "Event not found: {event_id}"
                
        Side Effects:
            - Modifies event in backend storage
            - Updates "updated" timestamp to current time
            - Preserves all fields not specified in arguments
            - Event modifications are immediate and persistent
            - Prints confirmation message with event summary, calendar ID, and user email
            
        Note:
            - Only specified fields are updated; others remain unchanged
            - Partial updates supported (can update just one field)
            - Attendees list is replaced entirely, not merged
            - If start_time or end_time updated, time_zone should also be provided
            - Updated timestamp automatically set to current time
            - Returns deep copy to prevent accidental further modifications
            - Standard fields (created, updated, status) added if missing
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Update only the summary
            >>> updated = api.update_event(
            ...     calendar_id="primary",
            ...     event_id="event-uuid-456",
            ...     summary="Updated Team Meeting"
            ... )
            Event 'event-uuid-456' updated in calendar 'primary' for alice@example.com
            >>> 
            >>> # Update time and location
            >>> updated = api.update_event(
            ...     calendar_id="primary",
            ...     event_id="event-uuid-456",
            ...     start_time="2025-06-15T14:00:00Z",
            ...     end_time="2025-06-15T15:00:00Z",
            ...     location="Conference Room B"
            ... )
            >>> 
            >>> # Update all fields
            >>> updated = api.update_event(
            ...     calendar_id="primary",
            ...     event_id="event-uuid-456",
            ...     summary="Project Review - Updated",
            ...     start_time="2025-06-20T15:00:00-04:00",
            ...     end_time="2025-06-20T16:00:00-04:00",
            ...     time_zone="America/New_York",
            ...     description="Updated meeting details",
            ...     location="Virtual",
            ...     attendees=[{"email": "newperson@example.com"}]
            ... )
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
        Permanently deletes an event from a calendar.
        
        Removes the event completely. This operation cannot be undone.
        Consider updating event status to "cancelled" instead if you need
        to preserve event history.
        
        Real API endpoint: DELETE /calendars/calendarId/events/eventId

        Args:
            calendar_id (str): Calendar identifier or "primary" keyword.
                To retrieve calendar IDs use calendarList.list method.
                Use "primary" for user's primary calendar.
                Example: "primary", "calendar-uuid-123"
            event_id (str): Unique identifier of the event to delete.
                Format: UUID string
                Example: "event-uuid-456"

        Returns:
            None: This method doesn't return a value on success.
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - Calendar not found: "Calendar not found: {calendar_id}"
                - Event not found: "Event not found: {event_id}"
                
        Side Effects:
            - Permanently removes event from backend storage
            - Event data is lost and cannot be recovered
            - Cannot be undone
            - Prints confirmation message with event ID, calendar ID, and user email
            
        Note:
            - Deletion is immediate and permanent
            - No trash/recycle bin mechanism
            - Consider using update_event with status="cancelled" for soft delete
            - All event data including attendees and reminders is lost
            - No notification sent to attendees (simulated API)
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Delete an event
            >>> api.delete_event("primary", "event-uuid-456")
            Event 'event-uuid-456' deleted from calendar 'primary' for alice@example.com
            >>> 
            >>> # Alternative: soft delete (preserves history)
            >>> # api.update_event("primary", "event-uuid-456", status="cancelled")
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
        Moves an event from one calendar to another, effectively changing the event's organizer.
        
        Transfers an event between calendars, removing it from source and adding to destination.
        Useful for transferring event ownership or reorganizing events.
        
        Real API endpoint: POST /calendars/calendarId/events/eventId/move

        Args:
            calendar_id (str): Source calendar identifier or "primary" keyword.
                To retrieve calendar IDs use calendarList.list method.
                This is the calendar currently containing the event.
                Example: "primary", "calendar-uuid-123"
            event_id (str): Unique identifier of the event to move.
                Format: UUID string
                Example: "event-uuid-456"
            destination (str): Destination calendar identifier or "primary" keyword.
                This is the target calendar where event will be moved to.
                Must be a different calendar than the source.
                Example: "calendar-uuid-789", "primary"

        Returns:
            Dict[str, Any]: Moved event resource with structure:
                {
                    "kind": "calendar#event",
                    "etag": str,              # Newly generated
                    "id": str,                # Same event ID
                    "status": str,            # Preserved from original
                    "summary": str,           # Preserved from original
                    "description": str,       # Preserved from original (if set)
                    "location": str,          # Preserved from original (if set)
                    "start": {...},           # Preserved from original
                    "end": {...},             # Preserved from original
                    "created": str,           # Preserved from original
                    "updated": str,           # Current timestamp (now)
                    "attendees": [...],       # Preserved from original (if set)
                    # ... all other original event fields
                }
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - Source calendar not found: "Calendar not found: {calendar_id}"
                - Event not found: "Event not found: {event_id}"
                - Destination calendar not found: "Destination calendar not found: {destination}"
                
        Side Effects:
            - Removes event from source calendar
            - Adds event to destination calendar (same ID)
            - Updates event's "updated" timestamp to current time
            - Generates new etag for the moved event
            - Initializes events dictionary for destination calendar if doesn't exist
            - Event is atomically transferred (not duplicated)
            - Prints confirmation message with event ID, source, destination, and user email
            
        Note:
            - Event keeps the same ID after moving
            - All event data (attendees, reminders, etc.) is preserved
            - Source and destination calendars must be different
            - "primary" keyword resolved for both source and destination
            - Moving doesn't change event times or content
            - Updated timestamp reflects the move operation
            - In real Google Calendar API, this changes the event organizer
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Move event from primary to another calendar
            >>> moved = api.move_event(
            ...     calendar_id="primary",
            ...     event_id="event-uuid-456",
            ...     destination="calendar-uuid-789"
            ... )
            Event 'event-uuid-456' moved from 'primary' to 'calendar-uuid-789' for alice@example.com
            >>> print(f"Event now in: {moved['id']}")
            >>> 
            >>> # Move event to primary calendar
            >>> moved = api.move_event(
            ...     calendar_id="calendar-uuid-789",
            ...     event_id="event-uuid-456",
            ...     destination="primary"
            ... )
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
        Returns free/busy information for a set of calendars within a specified time range.
        
        Queries multiple calendars to determine when they have scheduled events (busy)
        and when they are available (free). Useful for finding meeting times or
        checking availability across multiple calendars.
        
        Real API endpoint: POST /freeBusy

        Args:
            time_min (str): Start of the query interval.
                Format: RFC3339/ISO 8601 format ("YYYY-MM-DDTHH:MM:SSZ" or with timezone offset)
                Example: "2025-06-15T00:00:00Z", "2025-06-15T00:00:00-04:00"
            time_max (str): End of the query interval.
                Format: RFC3339/ISO 8601 format (must be after time_min)
                Example: "2025-06-15T23:59:59Z"
            items (List[Dict]): List of calendars to query for availability.
                Each dict should contain:
                    {"id": str}  # Calendar identifier or "primary" keyword
                Example: [{"id": "primary"}, {"id": "calendar-uuid-123"}]

        Returns:
            Dict[str, Any]: Free/busy response resource with structure:
                {
                    "kind": "calendar#freeBusy",
                    "timeMin": str,           # Echo of input time_min
                    "timeMax": str,           # Echo of input time_max
                    "calendars": {
                        "<calendar_id>": {      # For each queried calendar
                            "busy": [           # List of busy time periods
                                {
                                    "start": str,  # ISO 8601 start time
                                    "end": str     # ISO 8601 end time
                                },
                                ...
                            ],
                            "errors": [        # Any errors for this calendar
                                {
                                    "domain": str,     # "global"
                                    "reason": str      # "notFound", "invalid", etc.
                                },
                                ...
                            ]
                        },
                        ...
                    }
                }
        
        Raises:
            Exception: If no user is authenticated (via _ensure_authenticated)
                
        Note:
            - Returns empty calendars dict if user has no calendar data
            - "primary" keyword is resolved to user's primary calendar ID
            - Busy intervals include only events that overlap with query range
            - Events checked for overlap: max(query_start, event_start) < min(query_end, event_end)
            - Invalid calendar IDs result in "notFound" error for that calendar
            - Invalid time formats result in "invalid" error for that calendar
            - Handles various timezone formats (Z suffix, explicit offset, naive)
            - Naive datetimes are made timezone-aware using query time's timezone
            - Events with invalid datetime formats are silently skipped
            - Free time is implicit (any time not listed as busy)
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Check free/busy for primary calendar
            >>> result = api.check_free_busy(
            ...     time_min="2025-06-15T00:00:00Z",
            ...     time_max="2025-06-15T23:59:59Z",
            ...     items=[{"id": "primary"}]
            ... )
            >>> 
            >>> # Check calendar's availability
            >>> calendar_info = result["calendars"]["primary"]
            >>> if calendar_info["errors"]:
            ...     print("Error checking calendar")
            >>> else:
            ...     print(f"Busy periods: {len(calendar_info['busy'])}")
            ...     for busy in calendar_info["busy"]:
            ...         print(f"  Busy from {busy['start']} to {busy['end']}")
            >>> 
            >>> # Check multiple calendars
            >>> result = api.check_free_busy(
            ...     time_min="2025-06-20T09:00:00-04:00",
            ...     time_max="2025-06-20T17:00:00-04:00",
            ...     items=[
            ...         {"id": "primary"},
            ...         {"id": "calendar-uuid-123"},
            ...         {"id": "calendar-uuid-456"}
            ...     ]
            ... )
            >>> # Find common free time by examining all calendars' busy periods
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
        Resets all calendar data to the default initial state.
        
        Reloads the default scenario, discarding all changes made during the session.
        All users, calendars, and events are replaced with the default state.
        Useful for testing or restoring to a known state.

        Returns:
            Dict[str, bool]: Status dictionary with structure:
                {
                    "reset_status": True  # Always True on successful reset
                }
                
        Side Effects:
            - Reloads data from DEFAULT_STATE scenario
            - All current users are replaced with default users
            - All calendars and events reset to default state
            - Current authentication is cleared (current_user_id reset)
            - All modifications since initialization are lost
            - Prints confirmation message to console
            - Cannot be undone
            
        Note:
            - This is a testing/utility method not present in real Google Calendar API
            - Default state loaded from state_loader.load_state(DEFAULT_STATE)
            - Authentication will need to be re-established after reset
            - Useful for test cleanup or returning to known state
            - All in-memory changes are discarded
            
        Example:
            >>> api = GoogleCalendarApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Make some changes
            >>> api.insert_event(
            ...     calendar_id="primary",
            ...     summary="Test Event",
            ...     start_time="2025-06-15T10:00:00Z",
            ...     end_time="2025-06-15T11:00:00Z"
            ... )
            >>> 
            >>> # Reset to default state
            >>> result = api.reset_data()
            GoogleCalendarApis: All data reset to default state.
            >>> print(result)  # {'reset_status': True}
            >>> 
            >>> # Need to re-authenticate
            >>> api.authenticate("alice@example.com")
        """
        self._load_scenario(DEFAULT_STATE)
        print("GoogleCalendarApis: All data reset to default state.")
        return {"reset_status": True}