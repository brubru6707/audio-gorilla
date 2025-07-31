import unittest
import copy
from datetime import datetime, timedelta
from GoogleCalendarApis import GoogleCalendarApis, DEFAULT_STATE

class TestGoogleCalendarApis(unittest.TestCase):
    """
    Unit tests for the GoogleCalendarApis class, covering multi-user functionality.
    """

    def setUp(self):
        """
        Set up a fresh instance of GoogleCalendarApis before each test
        to ensure test isolation and consistent state.
        """
        self.api = GoogleCalendarApis(state=copy.deepcopy(DEFAULT_STATE))
        # Define user IDs for easier access in tests
        self.user1_id = "alice.smith@bizmail.co"
        self.user2_id = "bob.johnson@globalcorp.net"

        # Pre-defined calendar and event IDs for user1
        self.user1_cal1_id = "cal_1"
        self.user1_cal2_id = "cal_2"
        self.user1_event1_id = "event_1"
        self.user1_event2_id = "event_2"
        self.user1_event3_id = "event_3"

        # Pre-defined calendar and event IDs for user2
        self.user2_cal3_id = "cal_3"
        self.user2_cal4_id = "cal_4"
        self.user2_event4_id = "event_4"
        self.user2_event5_id = "event_5"

    # --- Helper Method Tests (Indirectly tested, but good to have direct checks) ---
    def test_get_user_data(self):
        """Test retrieving user-specific data."""
        user1_data = self.api._get_user_data(self.user1_id)
        self.assertIsNotNone(user1_data)
        self.assertEqual(user1_data["email"], self.user1_id)

        user2_data = self.api._get_user_data(self.user2_id)
        self.assertIsNotNone(user2_data)
        self.assertEqual(user2_data["email"], self.user2_id)

        # Test 'me' alias for current_user
        self.api.state["current_user"] = self.user1_id
        me_data = self.api._get_user_data('me')
        self.assertEqual(me_data["email"], self.user1_id)

        # Test non-existent user
        non_existent_user = self.api._get_user_data("nonexistent@example.com")
        self.assertIsNone(non_existent_user)

    def test_get_user_calendars_helper(self):
        """Test retrieving user-specific calendars using the helper."""
        user1_calendars = self.api._get_user_calendars(self.user1_id)
        self.assertIn(self.user1_cal1_id, user1_calendars)
        self.assertIn(self.user1_cal2_id, user1_calendars)
        self.assertNotIn(self.user2_cal3_id, user1_calendars)

        user2_calendars = self.api._get_user_calendars(self.user2_id)
        self.assertIn(self.user2_cal3_id, user2_calendars)
        self.assertIn(self.user2_cal4_id, user2_calendars)
        self.assertNotIn(self.user1_cal1_id, user2_calendars)

        # Test non-existent user
        non_existent_calendars = self.api._get_user_calendars("nonexistent@example.com")
        self.assertIsNone(non_existent_calendars)

    # --- Calendar Management Tests ---
    def test_create_calendar_user1(self):
        """Test creating a calendar for user1 (default user)."""
        initial_cal_count = len(self.api._get_user_calendars(self.user1_id))
        result = self.api.create_calendar("New Personal Calendar", user_id=self.user1_id)
        self.assertTrue(result["creation_status"])
        self.assertEqual(len(self.api._get_user_calendars(self.user1_id)), initial_cal_count + 1)
        # Verify the global counter increased
        self.assertEqual(self.api.state["calendar_counter"], 5)

        # Retrieve and verify the new calendar
        new_cal_id = f"cal_{self.api.state['calendar_counter']}"
        new_cal_data = self.api._get_user_calendars(self.user1_id).get(new_cal_id)
        self.assertIsNotNone(new_cal_data)
        self.assertEqual(new_cal_data["summary"], "New Personal Calendar")
        self.assertEqual(new_cal_data["timeZone"], "America/New_York") # Should use default timezone

    def test_create_calendar_user2(self):
        """Test creating a calendar for user2."""
        initial_cal_count = len(self.api._get_user_calendars(self.user2_id))
        result = self.api.create_calendar("Bob's New Calendar", time_zone="Europe/Paris", user_id=self.user2_id)
        self.assertTrue(result["creation_status"])
        self.assertEqual(len(self.api._get_user_calendars(self.user2_id)), initial_cal_count + 1)
        # Verify the global counter increased again
        self.assertEqual(self.api.state["calendar_counter"], 5)

        # Retrieve and verify the new calendar
        new_cal_id = f"cal_{self.api.state['calendar_counter']}"
        new_cal_data = self.api._get_user_calendars(self.user2_id).get(new_cal_id)
        self.assertIsNotNone(new_cal_data)
        self.assertEqual(new_cal_data["summary"], "Bob's New Calendar")
        self.assertEqual(new_cal_data["timeZone"], "Europe/Paris")

    def test_get_calendar_user1(self):
        """Test getting an existing calendar for user1."""
        result = self.api.get_calendar(self.user1_cal1_id, user_id=self.user1_id)
        self.assertTrue(result["retrieval_status"])
        self.assertEqual(result["calendar_data"]["summary"], "Personal Calendar (Alice)")

    def test_get_calendar_user2(self):
        """Test getting an existing calendar for user2."""
        result = self.api.get_calendar(self.user2_cal3_id, user_id=self.user2_id)
        self.assertTrue(result["retrieval_status"])
        self.assertEqual(result["calendar_data"]["summary"], "Personal Calendar (Bob)")

    def test_get_non_existent_calendar(self):
        """Test getting a non-existent calendar."""
        result = self.api.get_calendar("non_existent_cal", user_id=self.user1_id)
        self.assertFalse(result["retrieval_status"])

    def test_delete_calendar_user1(self):
        """Test deleting an existing calendar for user1."""
        initial_cal_count = len(self.api._get_user_calendars(self.user1_id))
        result = self.api.delete_calendar(self.user1_cal1_id, user_id=self.user1_id)
        self.assertTrue(result["deletion_status"])
        self.assertEqual(len(self.api._get_user_calendars(self.user1_id)), initial_cal_count - 1)
        self.assertNotIn(self.user1_cal1_id, self.api._get_user_calendars(self.user1_id))
        # Ensure events associated with the deleted calendar are also gone
        self.assertNotIn(self.user1_cal1_id, self.api._get_user_events(self.user1_id))

    def test_delete_calendar_user2(self):
        """Test deleting an existing calendar for user2."""
        initial_cal_count = len(self.api._get_user_calendars(self.user2_id))
        result = self.api.delete_calendar(self.user2_cal3_id, user_id=self.user2_id)
        self.assertTrue(result["deletion_status"])
        self.assertEqual(len(self.api._get_user_calendars(self.user2_id)), initial_cal_count - 1)
        self.assertNotIn(self.user2_cal3_id, self.api._get_user_calendars(self.user2_id))
        self.assertNotIn(self.user2_cal3_id, self.api._get_user_events(self.user2_id))

    def test_delete_non_existent_calendar(self):
        """Test deleting a non-existent calendar."""
        result = self.api.delete_calendar("non_existent_cal", user_id=self.user1_id)
        self.assertFalse(result["deletion_status"])

    # --- Event Management Tests ---
    def test_create_event_user1(self):
        """Test creating an event for user1."""
        initial_event_count = len(self.api._get_user_events(self.user1_id)[self.user1_cal1_id])
        event_data = {
            "summary": "New Event Alice",
            "start": {"dateTime": "2025-08-01T09:00:00-04:00"},
            "end": {"dateTime": "2025-08-01T10:00:00-04:00"}
        }
        result = self.api.create_event(self.user1_cal1_id, event_data, user_id=self.user1_id)
        self.assertTrue(result["creation_status"])
        self.assertEqual(len(self.api._get_user_events(self.user1_id)[self.user1_cal1_id]), initial_event_count + 1)
        # Verify global event counter increased
        self.assertEqual(self.api.state["event_counter"], 6)

        # Check if the event has the correct ID assigned
        new_event_id = f"event_{self.api.state['event_counter']}"
        retrieved_event = self.api._get_user_events(self.user1_id)[self.user1_cal1_id].get(new_event_id)
        self.assertIsNotNone(retrieved_event)
        self.assertEqual(retrieved_event["id"], new_event_id)
        self.assertEqual(retrieved_event["summary"], "New Event Alice")

    def test_create_event_user2(self):
        """Test creating an event for user2."""
        initial_event_count = len(self.api._get_user_events(self.user2_id)[self.user2_cal3_id])
        event_data = {
            "summary": "New Event Bob",
            "start": {"dateTime": "2025-08-02T14:00:00+01:00"},
            "end": {"dateTime": "2025-08-02T15:00:00+01:00"}
        }
        print("event counter before", self.api.state["event_counter"])
        result = self.api.create_event(self.user2_cal3_id, event_data, user_id=self.user2_id)
        self.assertTrue(result["creation_status"])
        print("this is init_event_count", initial_event_count)
        print("event counter after", self.api.state["event_counter"])
        self.assertEqual(len(self.api._get_user_events(self.user2_id)[self.user2_cal3_id]), initial_event_count + 1)
        # Verify global event counter increased again
        self.assertEqual(self.api.state["event_counter"], 6)

    def test_create_event_non_existent_calendar(self):
        """Test creating an event in a non-existent calendar."""
        event_data = {
            "summary": "Failed Event",
            "start": {"dateTime": "2025-08-03T10:00:00-04:00"},
            "end": {"dateTime": "2025-08-03T11:00:00-04:00"}
        }
        result = self.api.create_event("non_existent_cal", event_data, user_id=self.user1_id)
        self.assertFalse(result["creation_status"])

    def test_get_event_user1(self):
        """Test getting an existing event for user1."""
        result = self.api.get_event(self.user1_cal1_id, self.user1_event1_id, user_id=self.user1_id)
        self.assertTrue(result["retrieval_status"])
        self.assertEqual(result["event_data"]["summary"], "Morning Run (Alice)")

    def test_get_event_user2(self):
        """Test getting an existing event for user2."""
        result = self.api.get_event(self.user2_cal3_id, self.user2_event4_id, user_id=self.user2_id)
        self.assertTrue(result["retrieval_status"])
        self.assertEqual(result["event_data"]["summary"], "Gym Session (Bob)")

    def test_get_non_existent_event(self):
        """Test getting a non-existent event."""
        result = self.api.get_event(self.user1_cal1_id, "non_existent_event", user_id=self.user1_id)
        self.assertFalse(result["retrieval_status"])

    def test_list_events_user1_all(self):
        """Test listing all events for user1's calendar."""
        result = self.api.list_events(self.user1_cal1_id, user_id=self.user1_id)
        self.assertTrue(result["retrieval_status"])
        self.assertEqual(len(result["events"]), 2) # event_1 and event_2

    def test_list_events_user2_all(self):
        """Test listing all events for user2's calendar."""
        result = self.api.list_events(self.user2_cal3_id, user_id=self.user2_id)
        self.assertTrue(result["retrieval_status"])
        self.assertEqual(len(result["events"]), 1) # event_4

    def test_list_events_with_time_filter_user1(self):
        """Test listing events with time filters for user1."""
        # Events for user1_cal1_id: event_1 (07:00-08:00), event_2 (10:00-11:00)
        result = self.api.list_events(
            self.user1_cal1_id,
            time_min="2025-07-20T09:00:00-04:00",
            time_max="2025-07-20T12:00:00-04:00",
            user_id=self.user1_id
        )
        self.assertTrue(result["retrieval_status"])
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(result["events"][0]["summary"], "Dentist Appointment (Alice)")

    def test_list_events_non_existent_calendar(self):
        """Test listing events from a non-existent calendar."""
        result = self.api.list_events("non_existent_cal", user_id=self.user1_id)
        self.assertFalse(result["retrieval_status"])
        self.assertEqual(len(result["events"]), 0)

    def test_delete_event_user1(self):
        """Test deleting an existing event for user1."""
        initial_event_count = len(self.api._get_user_events(self.user1_id)[self.user1_cal1_id])
        result = self.api.delete_event(self.user1_cal1_id, self.user1_event1_id, user_id=self.user1_id)
        self.assertTrue(result["deletion_status"])
        self.assertEqual(len(self.api._get_user_events(self.user1_id)[self.user1_cal1_id]), initial_event_count - 1)
        self.assertNotIn(self.user1_event1_id, self.api._get_user_events(self.user1_id)[self.user1_cal1_id])

    def test_delete_event_user2(self):
        """Test deleting an existing event for user2."""
        initial_event_count = len(self.api._get_user_events(self.user2_id)[self.user2_cal3_id])
        result = self.api.delete_event(self.user2_cal3_id, self.user2_event4_id, user_id=self.user2_id)
        self.assertTrue(result["deletion_status"])
        self.assertEqual(len(self.api._get_user_events(self.user2_id)[self.user2_cal3_id]), initial_event_count - 1)
        self.assertNotIn(self.user2_event4_id, self.api._get_user_events(self.user2_id)[self.user2_cal3_id])

    def test_delete_non_existent_event(self):
        """Test deleting a non-existent event."""
        result = self.api.delete_event(self.user1_cal1_id, "non_existent_event", user_id=self.user1_id)
        self.assertFalse(result["deletion_status"])

    def test_move_event_user1(self):
        """Test moving an event between calendars for user1."""
        # Move event_1 from cal_1 to cal_2 for user1
        initial_cal1_events = len(self.api._get_user_events(self.user1_id)[self.user1_cal1_id])
        initial_cal2_events = len(self.api._get_user_events(self.user1_id)[self.user1_cal2_id])

        result = self.api.move_event(self.user1_cal1_id, self.user1_event1_id, self.user1_cal2_id, user_id=self.user1_id)
        self.assertTrue(result["move_status"])
        self.assertIn("moved successfully", result["message"])

        # Verify event is removed from source
        self.assertEqual(len(self.api._get_user_events(self.user1_id)[self.user1_cal1_id]), initial_cal1_events - 1)
        self.assertNotIn(self.user1_event1_id, self.api._get_user_events(self.user1_id)[self.user1_cal1_id])

        # Verify event is added to destination with a new ID
        self.assertEqual(len(self.api._get_user_events(self.user1_id)[self.user1_cal2_id]), initial_cal2_events + 1)
        new_event_id = f"event_{self.api.state['event_counter']}"
        self.assertIn(new_event_id, self.api._get_user_events(self.user1_id)[self.user1_cal2_id])
        self.assertEqual(self.api._get_user_events(self.user1_id)[self.user1_cal2_id][new_event_id]["summary"], "Morning Run (Alice)")

    def test_move_event_non_existent_source_event(self):
        """Test moving a non-existent source event."""
        result = self.api.move_event(self.user1_cal1_id, "non_existent_event", self.user1_cal2_id, user_id=self.user1_id)
        self.assertFalse(result["move_status"])
        self.assertIn("Event 'non_existent_event' not found", result["message"])

    def test_move_event_non_existent_destination_calendar(self):
        """Test moving an event to a non-existent destination calendar."""
        result = self.api.move_event(self.user1_cal1_id, self.user1_event1_id, "non_existent_cal", user_id=self.user1_id)
        self.assertFalse(result["move_status"])
        self.assertIn("Destination calendar 'non_existent_cal' not found", result["message"])

    def test_check_free_busy_user1(self):
        """Test checking free/busy status for user1's calendars."""
        items = [{"id": self.user1_cal1_id}, {"id": self.user1_cal2_id}]
        time_min = "2025-07-19T00:00:00-04:00"
        time_max = "2025-07-20T23:59:59-04:00"
        result = self.api.check_free_busy(time_min, time_max, items, user_id=self.user1_id)

        self.assertTrue(result["retrieval_status"])
        self.assertIn(self.user1_cal1_id, result["free_busy_data"])
        self.assertIn(self.user1_cal2_id, result["free_busy_data"])
        self.assertEqual(len(result["free_busy_data"][self.user1_cal1_id]["busy"]), 1)
        self.assertEqual(result["free_busy_data"][self.user1_cal1_id]["busy"][0]["start"], time_min)

    def test_check_free_busy_user2(self):
        """Test checking free/busy status for user2's calendars."""
        items = [{"id": self.user2_cal3_id}]
        time_min = "2025-07-20T00:00:00+01:00"
        time_max = "2025-07-20T23:59:59+01:00"
        result = self.api.check_free_busy(time_min, time_max, items, user_id=self.user2_id)

        self.assertTrue(result["retrieval_status"])
        self.assertIn(self.user2_cal3_id, result["free_busy_data"])
        self.assertEqual(len(result["free_busy_data"][self.user2_cal3_id]["busy"]), 1)
        self.assertEqual(result["free_busy_data"][self.user2_cal3_id]["busy"][0]["start"], time_min)

    def test_check_free_busy_non_existent_calendar(self):
        """Test checking free/busy status for a non-existent calendar."""
        items = [{"id": "non_existent_cal"}]
        time_min = "2025-07-19T00:00:00-04:00"
        time_max = "2025-07-20T23:59:59-04:00"
        result = self.api.check_free_busy(time_min, time_max, items, user_id=self.user1_id)
        self.assertTrue(result["retrieval_status"]) # Still returns true, but free_busy_data will be empty
        self.assertEqual(len(result["free_busy_data"]), 0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

