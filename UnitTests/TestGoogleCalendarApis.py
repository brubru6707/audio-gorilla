import unittest
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import backend creator
from GoogleCalendarApis import GoogleCalendarApis
from UnitTests.test_data_helper import BackendDataLoader

class TestGoogleCalendarApis(unittest.TestCase):
    """
    Unit tests for the GoogleCalendarApis class, using OAuth authentication.
    """

    # Load real data from backend
    real_data = BackendDataLoader.get_google_calendar_data()
    
    # Extract real user data
    users = real_data.get("users", {})
    user_id_key = list(users.keys())[0] if users else None
    user_data = users[user_id_key] if user_id_key else {}
    user_id_key2 = list(users.keys())[1] if len(users) > 1 else None
    user_data2 = users[user_id_key2] if user_id_key2 else {}
    
    # Email constants for authentication
    EMAIL_ALICE = user_data.get("email", "alice@example.com")
    EMAIL_BOB = user_data2.get("email", "bob@example.com")
    
    # Test constants
    TIME_ZONE = "America/New_York"
    START_TIME = "2025-12-25T10:00:00"
    END_TIME = "2025-12-25T11:00:00"
    
    def setUp(self):
        """
        Set up the API instance using real data.
        """
        self.calendar_api = GoogleCalendarApis()
        # Authenticate as Alice by default
        self.calendar_api.authenticate(self.EMAIL_ALICE)

    def setUp(self):
        """
        Set up the API instance using real data.
        """
        self.calendar_api = GoogleCalendarApis()
        # Authenticate as Alice by default
        self.calendar_api.authenticate(self.EMAIL_ALICE)

    # --- Authentication Tests ---
    
    def test_authenticate_success(self):
        """Test successful authentication."""
        api = GoogleCalendarApis()
        result = api.authenticate(self.EMAIL_ALICE)
        self.assertTrue(result["success"])
        self.assertEqual(api.current_user, self.user_id_key)

    def test_authenticate_nonexistent_user(self):
        """Test authentication with non-existent user."""
        api = GoogleCalendarApis()
        result = api.authenticate("nonexistent@example.com")
        self.assertFalse(result["success"])

    # --- List Calendars Tests ---
    
    def test_list_calendar_list_success(self):
        """Test listing all calendars for user."""
        result = self.calendar_api.list_calendar_list()
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "calendar#calendarList")
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)

    def test_list_calendar_list_after_user_switch(self):
        """Test listing calendars after switching users."""
        self.calendar_api.authenticate(self.EMAIL_BOB)
        result = self.calendar_api.list_calendar_list()
        self.assertEqual(result["kind"], "calendar#calendarList")

    # --- Create Calendar Tests ---
    
    def test_insert_calendar_success(self):
        """Test creating a calendar successfully."""
        result = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        self.assertIn("id", result)
        self.assertEqual(result["summary"], "Test Calendar")
        self.assertEqual(result["kind"], "calendar#calendar")

    def test_insert_calendar_with_description(self):
        """Test creating calendar with description."""
        result = self.calendar_api.insert_calendar(
            "Test Calendar", self.TIME_ZONE, "Test description"
        )
        self.assertEqual(result["description"], "Test description")

    # --- Get Calendar Tests ---
    
    def test_get_calendar_success(self):
        """Test getting calendar successfully."""
        # First create a calendar
        created = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created["id"]
        
        # Then get it
        result = self.calendar_api.get_calendar(calendar_id)
        self.assertEqual(result["id"], calendar_id)
        self.assertEqual(result["kind"], "calendar#calendar")

    def test_get_calendar_non_existent(self):
        """Test getting non-existent calendar."""
        with self.assertRaises(Exception) as context:
            self.calendar_api.get_calendar("non_existent_calendar")
        self.assertIn("not found", str(context.exception).lower())

    # --- Update Calendar Tests ---
    
    def test_update_calendar_success(self):
        """Test updating calendar successfully."""
        # First create a calendar
        created = self.calendar_api.insert_calendar("Original Calendar", self.TIME_ZONE)
        calendar_id = created["id"]
        
        # Then update it
        updated = self.calendar_api.update_calendar(calendar_id, summary="Updated Calendar")
        self.assertEqual(updated["summary"], "Updated Calendar")

    def test_update_calendar_non_existent(self):
        """Test updating non-existent calendar."""
        with self.assertRaises(Exception) as context:
            self.calendar_api.update_calendar("non_existent_calendar", summary="This should fail")
        self.assertIn("not found", str(context.exception).lower())

    # --- Delete Calendar Tests ---
    
    def test_delete_calendar_success(self):
        """Test deleting calendar successfully."""
        # First create a calendar
        created = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created["id"]
        
        # Then delete it (should not raise exception)
        self.calendar_api.delete_calendar(calendar_id)

    def test_delete_calendar_non_existent(self):
        """Test deleting non-existent calendar."""
        with self.assertRaises(Exception) as context:
            self.calendar_api.delete_calendar("non_existent_calendar")
        self.assertIn("not found", str(context.exception).lower())

    # --- Create Event Tests ---
    
    def test_insert_event_success(self):
        """Test creating event successfully."""
        # First create a calendar
        created_cal = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        # Then create an event
        result = self.calendar_api.insert_event(
            calendar_id, "Test Event", self.START_TIME, self.END_TIME, self.TIME_ZONE
        )
        self.assertIn("id", result)
        self.assertEqual(result["summary"], "Test Event")
        self.assertEqual(result["kind"], "calendar#event")

    def test_insert_event_with_description(self):
        """Test creating event with description."""
        created_cal = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        result = self.calendar_api.insert_event(
            calendar_id, "Test Event", self.START_TIME, self.END_TIME, 
            self.TIME_ZONE, description="Test description"
        )
        self.assertEqual(result["description"], "Test description")

    def test_insert_event_non_existent_calendar(self):
        """Test creating event in non-existent calendar."""
        with self.assertRaises(Exception) as context:
            self.calendar_api.insert_event(
                "non_existent_calendar", "Test Event", self.START_TIME, 
                self.END_TIME, self.TIME_ZONE
            )
        self.assertIn("not found", str(context.exception).lower())

    # --- Get Event Tests ---
    
    def test_get_event_success(self):
        """Test getting event successfully."""
        # First create a calendar and event
        created_cal = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        created_event = self.calendar_api.insert_event(
            calendar_id, "Test Event", self.START_TIME, self.END_TIME, self.TIME_ZONE
        )
        event_id = created_event["id"]
        
        # Then get the event
        result = self.calendar_api.get_event(calendar_id, event_id)
        self.assertEqual(result["id"], event_id)
        self.assertEqual(result["kind"], "calendar#event")

    def test_get_event_non_existent(self):
        """Test getting non-existent event."""
        # First create a calendar
        created_cal = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        with self.assertRaises(Exception) as context:
            self.calendar_api.get_event(calendar_id, "non_existent_event")
        self.assertIn("not found", str(context.exception).lower())

    # --- List Events Tests ---
    
    def test_list_events_success(self):
        """Test listing events successfully."""
        # First create a calendar and event
        created_cal = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        self.calendar_api.insert_event(
            calendar_id, "Test Event", self.START_TIME, self.END_TIME, self.TIME_ZONE
        )
        
        # Then list events
        result = self.calendar_api.list_events(calendar_id)
        self.assertEqual(result["kind"], "calendar#events")
        self.assertIn("items", result)
        self.assertGreater(len(result["items"]), 0)

    def test_list_events_empty_calendar(self):
        """Test listing events for calendar with no events."""
        created_cal = self.calendar_api.insert_calendar("Empty Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        result = self.calendar_api.list_events(calendar_id)
        self.assertEqual(result["kind"], "calendar#events")
        self.assertEqual(len(result["items"]), 0)

    def test_list_events_with_query(self):
        """Test listing events with search query."""
        created_cal = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        self.calendar_api.insert_event(
            calendar_id, "Unique Event Title", self.START_TIME, self.END_TIME, self.TIME_ZONE
        )
        
        result = self.calendar_api.list_events(calendar_id, q="Unique")
        self.assertGreater(len(result["items"]), 0)

    # --- Delete Event Tests ---
    
    def test_delete_event_success(self):
        """Test deleting event successfully."""
        # First create a calendar and event
        created_cal = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        created_event = self.calendar_api.insert_event(
            calendar_id, "Test Event", self.START_TIME, self.END_TIME, self.TIME_ZONE
        )
        event_id = created_event["id"]
        
        # Then delete the event (should not raise exception)
        self.calendar_api.delete_event(calendar_id, event_id)

    def test_delete_event_non_existent(self):
        """Test deleting non-existent event."""
        # First create a calendar
        created_cal = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        with self.assertRaises(Exception) as context:
            self.calendar_api.delete_event(calendar_id, "non_existent_event")
        self.assertIn("not found", str(context.exception).lower())

    # --- Update Event Tests ---
    
    def test_update_event_success(self):
        """Test updating event successfully."""
        # First create a calendar and event
        created_cal = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        created_event = self.calendar_api.insert_event(
            calendar_id, "Original Event", self.START_TIME, self.END_TIME, self.TIME_ZONE
        )
        event_id = created_event["id"]
        
        # Then update the event
        updated = self.calendar_api.update_event(calendar_id, event_id, summary="Updated Event")
        self.assertEqual(updated["summary"], "Updated Event")

    def test_update_event_non_existent(self):
        """Test updating non-existent event."""
        # First create a calendar
        created_cal = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        with self.assertRaises(Exception) as context:
            self.calendar_api.update_event(calendar_id, "non_existent_event", summary="This should fail")
        self.assertIn("not found", str(context.exception).lower())

    # --- Move Event Tests ---
    
    def test_move_event_success(self):
        """Test moving event successfully."""
        # First create two calendars and an event
        created_cal1 = self.calendar_api.insert_calendar("Source Calendar", self.TIME_ZONE)
        source_calendar_id = created_cal1["id"]
        
        created_cal2 = self.calendar_api.insert_calendar("Destination Calendar", self.TIME_ZONE)
        dest_calendar_id = created_cal2["id"]
        
        created_event = self.calendar_api.insert_event(
            source_calendar_id, "Test Event", self.START_TIME, self.END_TIME, self.TIME_ZONE
        )
        event_id = created_event["id"]
        
        # Then move the event
        moved = self.calendar_api.move_event(source_calendar_id, event_id, dest_calendar_id)
        self.assertEqual(moved["kind"], "calendar#event")

    def test_move_event_non_existent_source(self):
        """Test moving event from non-existent source calendar."""
        # First create destination calendar
        created_cal = self.calendar_api.insert_calendar("Destination Calendar", self.TIME_ZONE)
        dest_calendar_id = created_cal["id"]
        
        with self.assertRaises(Exception) as context:
            self.calendar_api.move_event("non_existent_source", "any_event", dest_calendar_id)
        self.assertIn("not found", str(context.exception).lower())

    def test_move_event_non_existent_destination(self):
        """Test moving event to non-existent destination calendar."""
        # First create source calendar and event
        created_cal = self.calendar_api.insert_calendar("Source Calendar", self.TIME_ZONE)
        source_calendar_id = created_cal["id"]
        
        created_event = self.calendar_api.insert_event(
            source_calendar_id, "Test Event", self.START_TIME, self.END_TIME, self.TIME_ZONE
        )
        event_id = created_event["id"]
        
        with self.assertRaises(Exception) as context:
            self.calendar_api.move_event(source_calendar_id, event_id, "non_existent_dest")
        self.assertIn("not found", str(context.exception).lower())

    # --- Check Free/Busy Tests ---
    
    def test_check_free_busy_success(self):
        """Test checking free/busy status successfully."""
        # First create a calendar
        created_cal = self.calendar_api.insert_calendar("Test Calendar", self.TIME_ZONE)
        calendar_id = created_cal["id"]
        
        items = [{"id": calendar_id}]
        result = self.calendar_api.check_free_busy(self.START_TIME, self.END_TIME, items)
        self.assertEqual(result["kind"], "calendar#freeBusy")
        self.assertIn("calendars", result)

    def test_check_free_busy_non_existent_calendar(self):
        """Test checking free/busy status for non-existent calendar."""
        items = [{"id": "non_existent_calendar"}]
        result = self.calendar_api.check_free_busy(self.START_TIME, self.END_TIME, items)
        self.assertEqual(result["kind"], "calendar#freeBusy")
        # Non-existent calendars are just not included in response

    # --- Multi-user Tests ---
    
    def test_calendar_isolation_between_users(self):
        """Test that calendars are isolated between different users."""
        # Create calendar as Alice
        alice_cal = self.calendar_api.insert_calendar("Alice's Calendar", self.TIME_ZONE)
        alice_cal_id = alice_cal["id"]
        
        # Switch to Bob
        self.calendar_api.authenticate(self.EMAIL_BOB)
        
        # Bob shouldn't see Alice's calendar
        with self.assertRaises(Exception) as context:
            self.calendar_api.get_calendar(alice_cal_id)
        self.assertIn("not found", str(context.exception).lower())

    # --- Reset Data Tests ---
    
    def test_reset_data(self):
        """Test resetting data."""
        result = self.calendar_api.reset_data()
        self.assertTrue(result["reset_status"])


if __name__ == '__main__':
    unittest.main()

