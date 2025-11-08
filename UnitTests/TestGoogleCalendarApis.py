import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import backend creator
from GoogleCalendarApis import GoogleCalendarApis
from UnitTests.test_data_helper import BackendDataLoader

class TestGoogleCalendarApis(unittest.TestCase):
    """
    Unit tests for the GoogleCalendarApis class, covering multi-user functionality.
    """

    # Load real data from backend
    real_data = BackendDataLoader.get_google_calendar_data()
    
    # Extract real user data
    users = real_data.get("users", {})
    user_id_key = list(users.keys())[0] if users else None
    user_data = users[user_id_key] if user_id_key else {}
    REAL_USER_ID = user_id_key
    REAL_USER_EMAIL = user_data.get("email", "real_user@gmail.com")
    
    # Extract real calendar data
    calendars = list(real_data.get("calendars", {}).values())
    calendar_data = calendars[0] if calendars else {}
    REAL_CALENDAR_NAME = calendar_data.get("name", "Real Calendar")
    
    # Extract real event data
    events = list(real_data.get("events", {}).values())
    event_data = events[0] if events else {}
    REAL_EVENT_TITLE = event_data.get("title", "Real Event")
    
    # Test constants
    TIME_ZONE = "America/New_York"
    START_TIME = "2025-12-25T10:00:00"
    END_TIME = "2025-12-25T11:00:00"
    
    def setUp(self):
        """
        Set up the API instance using real data.
        """
        self.calendar_api = GoogleCalendarApis()

    # --- User Profile Tests ---
    def test_get_user_profile_success(self):
        """Test getting user profile successfully."""
        result = self.calendar_api.get_user_profile(self.REAL_USER_ID)
        self.assertTrue(result["retrieval_status"])
        self.assertIn("profile_data", result)

    def test_get_user_profile_non_existent(self):
        """Test getting user profile for non-existent user."""
        result = self.calendar_api.get_user_profile("nonexistent@example.com")
        self.assertFalse(result["retrieval_status"])
        self.assertIn("profile_data", result)

    # --- List Calendars Tests ---
    def test_list_calendars_success(self):
        """Test listing all calendars for user."""
        result = self.calendar_api.list_calendars(self.REAL_USER_ID)
        self.assertTrue(result["retrieval_status"])
        self.assertIn("calendars", result)

    def test_list_calendars_non_existent_user(self):
        """Test listing calendars for non-existent user."""
        result = self.calendar_api.list_calendars("nonexistent@example.com")
        self.assertFalse(result["retrieval_status"])

    # --- Create Calendar Tests ---
    def test_create_calendar_success(self):
        """Test creating a calendar successfully."""
        result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        self.assertTrue(result["creation_status"])
        self.assertIn("calendar_data", result)

    def test_create_calendar_non_existent_user(self):
        """Test creating calendar for non-existent user."""
        result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, "nonexistent@example.com"
        )
        self.assertFalse(result["creation_status"])

    # --- Get Calendar Tests ---
    def test_get_calendar_success(self):
        """Test getting calendar successfully."""
        # First create a calendar
        create_result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        self.assertTrue(create_result["creation_status"])
        calendar_id = create_result["calendar_data"]["id"]
        
        # Then get it
        result = self.calendar_api.get_calendar(calendar_id, self.REAL_USER_ID)
        self.assertTrue(result["retrieval_status"])
        self.assertIn("calendar_data", result)

    def test_get_calendar_non_existent(self):
        """Test getting non-existent calendar."""
        result = self.calendar_api.get_calendar("non_existent_calendar", self.REAL_USER_ID)
        self.assertFalse(result["retrieval_status"])

    # --- Update Calendar Tests ---
    def test_update_calendar_success(self):
        """Test updating calendar successfully."""
        # First create a calendar
        create_result = self.calendar_api.create_calendar(
            "Original Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        self.assertTrue(create_result["creation_status"])
        calendar_id = create_result["calendar_data"]["id"]
        
        # Then update it
        result = self.calendar_api.update_calendar(
            calendar_id, "Updated Calendar", self.REAL_USER_ID
        )
        self.assertTrue(result["update_status"])

    def test_update_calendar_non_existent(self):
        """Test updating non-existent calendar."""
        result = self.calendar_api.update_calendar(
            "non_existent_calendar", "This should fail", self.REAL_USER_ID
        )
        self.assertFalse(result["update_status"])

    def test_update_calendar_non_existent_user(self):
        """Test updating calendar for non-existent user."""
        result = self.calendar_api.update_calendar(
            "any_calendar", "This should fail", "nonexistent@example.com"
        )
        self.assertFalse(result["update_status"])

    # --- Delete Calendar Tests ---
    def test_delete_calendar_success(self):
        """Test deleting calendar successfully."""
        # First create a calendar
        create_result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        self.assertTrue(create_result["creation_status"])
        calendar_id = create_result["calendar_data"]["id"]
        
        # Then delete it
        result = self.calendar_api.delete_calendar(calendar_id, self.REAL_USER_ID)
        self.assertTrue(result["delete_status"])

    def test_delete_calendar_non_existent(self):
        """Test deleting non-existent calendar."""
        result = self.calendar_api.delete_calendar("non_existent_calendar", self.REAL_USER_ID)
        self.assertFalse(result["delete_status"])

    # --- Create Event Tests ---
    def test_create_event_success(self):
        """Test creating event successfully."""
        # First create a calendar
        create_cal_result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        self.assertTrue(create_cal_result["creation_status"])
        calendar_id = create_cal_result["calendar_data"]["id"]
        
        # Then create an event
        result = self.calendar_api.create_event(
            calendar_id, "Test Event", self.START_TIME, self.END_TIME, 
            self.TIME_ZONE, self.REAL_USER_ID
        )
        self.assertTrue(result["creation_status"])
        self.assertIn("event_data", result)

    def test_create_event_non_existent_calendar(self):
        """Test creating event in non-existent calendar."""
        result = self.calendar_api.create_event(
            "non_existent_calendar", "Test Event", self.START_TIME, 
            self.END_TIME, self.TIME_ZONE, self.REAL_USER_ID
        )
        self.assertFalse(result["creation_status"])

    # --- Get Event Tests ---
    def test_get_event_success(self):
        """Test getting event successfully."""
        # First create a calendar and event
        create_cal_result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        calendar_id = create_cal_result["calendar_data"]["id"]
        
        create_event_result = self.calendar_api.create_event(
            calendar_id, "Test Event", self.START_TIME, self.END_TIME, 
            self.TIME_ZONE, self.REAL_USER_ID
        )
        event_id = create_event_result["event_data"]["id"]
        
        # Then get the event
        result = self.calendar_api.get_event(calendar_id, event_id, self.REAL_USER_ID)
        self.assertTrue(result["retrieval_status"])
        self.assertIn("event_data", result)

    def test_get_event_non_existent(self):
        """Test getting non-existent event."""
        # First create a calendar
        create_cal_result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        calendar_id = create_cal_result["calendar_data"]["id"]
        
        result = self.calendar_api.get_event(calendar_id, "non_existent_event", self.REAL_USER_ID)
        self.assertFalse(result["retrieval_status"])

    # --- List Events Tests ---
    def test_list_events_success(self):
        """Test listing events successfully."""
        # First create a calendar and event
        create_cal_result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        calendar_id = create_cal_result["calendar_data"]["id"]
        
        self.calendar_api.create_event(
            calendar_id, "Test Event", self.START_TIME, self.END_TIME, 
            self.TIME_ZONE, self.REAL_USER_ID
        )
        
        # Then list events
        result = self.calendar_api.list_events(calendar_id, self.REAL_USER_ID)
        self.assertTrue(result["retrieval_status"])
        self.assertIn("events", result)

    def test_list_events_non_existent_calendar(self):
        """Test listing events for non-existent calendar."""
        result = self.calendar_api.list_events("non_existent_calendar", self.REAL_USER_ID)
        self.assertFalse(result["retrieval_status"])

    # --- Delete Event Tests ---
    def test_delete_event_success(self):
        """Test deleting event successfully."""
        # First create a calendar and event
        create_cal_result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        calendar_id = create_cal_result["calendar_data"]["id"]
        
        create_event_result = self.calendar_api.create_event(
            calendar_id, "Test Event", self.START_TIME, self.END_TIME, 
            self.TIME_ZONE, self.REAL_USER_ID
        )
        event_id = create_event_result["event_data"]["id"]
        
        # Then delete the event
        result = self.calendar_api.delete_event(calendar_id, event_id, self.REAL_USER_ID)
        self.assertTrue(result["delete_status"])

    def test_delete_event_non_existent(self):
        """Test deleting non-existent event."""
        # First create a calendar
        create_cal_result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        calendar_id = create_cal_result["calendar_data"]["id"]
        
        result = self.calendar_api.delete_event(calendar_id, "non_existent_event", self.REAL_USER_ID)
        self.assertFalse(result["delete_status"])

    # --- Update Event Tests ---
    def test_update_event_success(self):
        """Test updating event successfully."""
        # First create a calendar and event
        create_cal_result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        calendar_id = create_cal_result["calendar_data"]["id"]
        
        create_event_result = self.calendar_api.create_event(
            calendar_id, "Original Event", self.START_TIME, self.END_TIME, 
            self.TIME_ZONE, self.REAL_USER_ID
        )
        event_id = create_event_result["event_data"]["id"]
        
        # Then update the event
        result = self.calendar_api.update_event(
            calendar_id, event_id, self.REAL_USER_ID, summary="Updated Event"
        )
        self.assertTrue(result["update_status"])

    def test_update_event_non_existent(self):
        """Test updating non-existent event."""
        # First create a calendar
        create_cal_result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        calendar_id = create_cal_result["calendar_data"]["id"]
        
        result = self.calendar_api.update_event(
            calendar_id, "non_existent_event", self.REAL_USER_ID, summary="This should fail"
        )
        self.assertFalse(result["update_status"])

    # --- Move Event Tests ---
    def test_move_event_success(self):
        """Test moving event successfully."""
        # First create two calendars and an event
        create_cal1_result = self.calendar_api.create_calendar(
            "Source Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        source_calendar_id = create_cal1_result["calendar_data"]["id"]
        
        create_cal2_result = self.calendar_api.create_calendar(
            "Destination Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        dest_calendar_id = create_cal2_result["calendar_data"]["id"]
        
        create_event_result = self.calendar_api.create_event(
            source_calendar_id, "Test Event", self.START_TIME, self.END_TIME, 
            self.TIME_ZONE, self.REAL_USER_ID
        )
        event_id = create_event_result["event_data"]["id"]
        
        # Then move the event
        result = self.calendar_api.move_event(
            source_calendar_id, event_id, dest_calendar_id, self.REAL_USER_ID
        )
        self.assertTrue(result["move_status"])

    def test_move_event_non_existent_source(self):
        """Test moving event from non-existent source calendar."""
        # First create destination calendar
        create_cal_result = self.calendar_api.create_calendar(
            "Destination Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        dest_calendar_id = create_cal_result["calendar_data"]["id"]
        
        result = self.calendar_api.move_event(
            "non_existent_source", "any_event", dest_calendar_id, self.REAL_USER_ID
        )
        self.assertFalse(result["move_status"])

    def test_move_event_non_existent_destination(self):
        """Test moving event to non-existent destination calendar."""
        # First create source calendar and event
        create_cal_result = self.calendar_api.create_calendar(
            "Source Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        source_calendar_id = create_cal_result["calendar_data"]["id"]
        
        create_event_result = self.calendar_api.create_event(
            source_calendar_id, "Test Event", self.START_TIME, self.END_TIME, 
            self.TIME_ZONE, self.REAL_USER_ID
        )
        event_id = create_event_result["event_data"]["id"]
        
        result = self.calendar_api.move_event(
            source_calendar_id, event_id, "non_existent_dest", self.REAL_USER_ID
        )
        self.assertFalse(result["move_status"])

    # --- Check Free/Busy Tests ---
    def test_check_free_busy_success(self):
        """Test checking free/busy status successfully."""
        # First create a calendar
        create_cal_result = self.calendar_api.create_calendar(
            "Test Calendar", self.TIME_ZONE, self.REAL_USER_ID
        )
        calendar_id = create_cal_result["calendar_data"]["id"]
        
        items = [{"id": calendar_id}]
        result = self.calendar_api.check_free_busy(
            self.START_TIME, self.END_TIME, items, self.REAL_USER_ID
        )
        self.assertTrue(result["retrieval_status"])
        self.assertIn("free_busy_data", result)

    def test_check_free_busy_non_existent_calendar(self):
        """Test checking free/busy status for non-existent calendar."""
        items = [{"id": "non_existent_calendar"}]
        result = self.calendar_api.check_free_busy(
            self.START_TIME, self.END_TIME, items, self.REAL_USER_ID
        )
        self.assertTrue(result["retrieval_status"])
        self.assertIn("error", result["free_busy_data"]["non_existent_calendar"])

    # --- Reset Data Tests ---
    def test_reset_data(self):
        """Test resetting data."""
        result = self.calendar_api.reset_data()
        self.assertTrue(result["reset_status"])

if __name__ == '__main__':
    unittest.main()
