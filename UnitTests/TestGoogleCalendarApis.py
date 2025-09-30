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

    # --- User Profile Tests ---
    def test_get_user_profile_user1(self):
        """Test getting user profile for user1."""
        result = self.api.get_user_profile(self.user1_id)
        self.assertTrue(result["success"])
        self.assertIn("profile", result)
        self.assertEqual(result["profile"]["email"], self.user1_id)
        self.assertEqual(result["profile"]["name"], "Alice Smith")

    def test_get_user_profile_user2(self):
        """Test getting user profile for user2."""
        result = self.api.get_user_profile(self.user2_id)
        self.assertTrue(result["success"])
        self.assertIn("profile", result)
        self.assertEqual(result["profile"]["email"], self.user2_id)
        self.assertEqual(result["profile"]["name"], "Bob Johnson")

    def test_get_user_profile_non_existent(self):
        """Test getting user profile for non-existent user."""
        result = self.api.get_user_profile("nonexistent@example.com")
        self.assertFalse(result["success"])
        self.assertNotIn("profile", result)

    # --- List Calendars Tests ---
    def test_list_calendars_user1(self):
        """Test listing all calendars for user1."""
        result = self.api.list_calendars(self.user1_id)
        self.assertTrue(result["success"])
        self.assertIn("calendars", result)
        self.assertEqual(len(result["calendars"]), 2)
        calendar_ids = [cal["id"] for cal in result["calendars"]]
        self.assertIn(self.user1_cal1_id, calendar_ids)
        self.assertIn(self.user1_cal2_id, calendar_ids)

    def test_list_calendars_user2(self):
        """Test listing all calendars for user2."""
        result = self.api.list_calendars(self.user2_id)
        self.assertTrue(result["success"])
        self.assertIn("calendars", result)
        self.assertEqual(len(result["calendars"]), 2)
        calendar_ids = [cal["id"] for cal in result["calendars"]]
        self.assertIn(self.user2_cal3_id, calendar_ids)
        self.assertIn(self.user2_cal4_id, calendar_ids)

    def test_list_calendars_non_existent_user(self):
        """Test listing calendars for non-existent user."""
        result = self.api.list_calendars("nonexistent@example.com")
        self.assertFalse(result["success"])
        self.assertEqual(len(result["calendars"]), 0)

    # --- Update Calendar Tests ---
    def test_update_calendar_user1(self):
        """Test updating calendar for user1."""
        result = self.api.update_calendar(
            self.user1_cal1_id,
            summary="Updated Personal Calendar",
            description="Updated description",
            time_zone="Pacific/Honolulu",
            user_id=self.user1_id
        )
        self.assertTrue(result["update_status"])
        
        # Verify the update
        updated_cal = self.api._get_user_calendars(self.user1_id)[self.user1_cal1_id]
        self.assertEqual(updated_cal["summary"], "Updated Personal Calendar")
        self.assertEqual(updated_cal["description"], "Updated description")
        self.assertEqual(updated_cal["timeZone"], "Pacific/Honolulu")

    def test_update_calendar_user2(self):
        """Test updating calendar for user2."""
        result = self.api.update_calendar(
            self.user2_cal3_id,
            summary="Bob's Updated Calendar",
            user_id=self.user2_id
        )
        self.assertTrue(result["update_status"])
        
        # Verify the update
        updated_cal = self.api._get_user_calendars(self.user2_id)[self.user2_cal3_id]
        self.assertEqual(updated_cal["summary"], "Bob's Updated Calendar")

    def test_update_calendar_non_existent(self):
        """Test updating non-existent calendar."""
        result = self.api.update_calendar(
            "non_existent_cal",
            summary="Should Fail",
            user_id=self.user1_id
        )
        self.assertFalse(result["update_status"])

    def test_update_calendar_non_existent_user(self):
        """Test updating calendar for non-existent user."""
        result = self.api.update_calendar(
            self.user1_cal1_id,
            summary="Should Fail",
            user_id="nonexistent@example.com"
        )
        self.assertFalse(result["update_status"])

    # --- Update Event Tests ---
    def test_update_event_user1(self):
        """Test updating event for user1."""
        updated_event_data = {
            "summary": "Updated Morning Run",
            "description": "Updated description for morning run",
            "start": {"dateTime": "2025-07-20T08:00:00-04:00"},
            "end": {"dateTime": "2025-07-20T09:00:00-04:00"}
        }
        result = self.api.update_event(
            self.user1_cal1_id,
            self.user1_event1_id,
            updated_event_data,
            user_id=self.user1_id
        )
        self.assertTrue(result["update_status"])
        
        # Verify the update
        updated_event = self.api._get_user_events(self.user1_id)[self.user1_cal1_id][self.user1_event1_id]
        self.assertEqual(updated_event["summary"], "Updated Morning Run")
        self.assertEqual(updated_event["description"], "Updated description for morning run")
        self.assertEqual(updated_event["start"]["dateTime"], "2025-07-20T08:00:00-04:00")

    def test_update_event_user2(self):
        """Test updating event for user2."""
        updated_event_data = {
            "summary": "Updated Gym Session",
            "location": "New Gym Location"
        }
        result = self.api.update_event(
            self.user2_cal3_id,
            self.user2_event4_id,
            updated_event_data,
            user_id=self.user2_id
        )
        self.assertTrue(result["update_status"])
        
        # Verify the update
        updated_event = self.api._get_user_events(self.user2_id)[self.user2_cal3_id][self.user2_event4_id]
        self.assertEqual(updated_event["summary"], "Updated Gym Session")
        self.assertEqual(updated_event["location"], "New Gym Location")

    def test_update_event_non_existent_calendar(self):
        """Test updating event in non-existent calendar."""
        updated_event_data = {"summary": "Should Fail"}
        result = self.api.update_event(
            "non_existent_cal",
            self.user1_event1_id,
            updated_event_data,
            user_id=self.user1_id
        )
        self.assertFalse(result["update_status"])

    def test_update_event_non_existent_event(self):
        """Test updating non-existent event."""
        updated_event_data = {"summary": "Should Fail"}
        result = self.api.update_event(
            self.user1_cal1_id,
            "non_existent_event",
            updated_event_data,
            user_id=self.user1_id
        )
        self.assertFalse(result["update_status"])

    def test_update_event_non_existent_user(self):
        """Test updating event for non-existent user."""
        updated_event_data = {"summary": "Should Fail"}
        result = self.api.update_event(
            self.user1_cal1_id,
            self.user1_event1_id,
            updated_event_data,
            user_id="nonexistent@example.com"
        )
        self.assertFalse(result["update_status"])

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

    # --- Comprehensive Workflow Tests ---
    def test_comprehensive_calendar_workflow(self):
        """Test comprehensive calendar management workflow."""
        # 1. Create a new calendar
        result = self.api.create_calendar("Workflow Test Calendar", user_id=self.user1_id)
        self.assertTrue(result["creation_status"])
        new_cal_id = f"cal_{self.api.state['calendar_counter']}"
        
        # 2. Update the calendar
        result = self.api.update_calendar(
            new_cal_id,
            summary="Updated Workflow Calendar",
            description="Calendar for testing workflow",
            user_id=self.user1_id
        )
        self.assertTrue(result["update_status"])
        
        # 3. Create an event in the calendar
        event_data = {
            "summary": "Workflow Event",
            "start": {"dateTime": "2025-08-01T10:00:00-04:00"},
            "end": {"dateTime": "2025-08-01T11:00:00-04:00"}
        }
        result = self.api.create_event(new_cal_id, event_data, user_id=self.user1_id)
        self.assertTrue(result["creation_status"])
        new_event_id = f"event_{self.api.state['event_counter']}"
        
        # 4. Update the event
        updated_event_data = {"summary": "Updated Workflow Event"}
        result = self.api.update_event(new_cal_id, new_event_id, updated_event_data, user_id=self.user1_id)
        self.assertTrue(result["update_status"])
        
        # 5. List events to verify
        result = self.api.list_events(new_cal_id, user_id=self.user1_id)
        self.assertTrue(result["retrieval_status"])
        self.assertEqual(len(result["events"]), 1)
        
        # 6. Delete the event
        result = self.api.delete_event(new_cal_id, new_event_id, user_id=self.user1_id)
        self.assertTrue(result["deletion_status"])
        
        # 7. Delete the calendar
        result = self.api.delete_calendar(new_cal_id, user_id=self.user1_id)
        self.assertTrue(result["deletion_status"])

    def test_comprehensive_event_management_workflow(self):
        """Test comprehensive event management workflow."""
        # 1. Create multiple events in different calendars
        event1_data = {
            "summary": "Event 1",
            "start": {"dateTime": "2025-08-01T09:00:00-04:00"},
            "end": {"dateTime": "2025-08-01T10:00:00-04:00"}
        }
        result1 = self.api.create_event(self.user1_cal1_id, event1_data, user_id=self.user1_id)
        self.assertTrue(result1["creation_status"])
        event1_id = f"event_{self.api.state['event_counter']}"
        
        event2_data = {
            "summary": "Event 2",
            "start": {"dateTime": "2025-08-01T11:00:00-04:00"},
            "end": {"dateTime": "2025-08-01T12:00:00-04:00"}
        }
        result2 = self.api.create_event(self.user1_cal2_id, event2_data, user_id=self.user1_id)
        self.assertTrue(result2["creation_status"])
        event2_id = f"event_{self.api.state['event_counter']}"
        
        # 2. Move event from one calendar to another
        result = self.api.move_event(self.user1_cal1_id, event1_id, self.user1_cal2_id, user_id=self.user1_id)
        self.assertTrue(result["move_status"])
        
        # 3. Check free/busy across both calendars
        items = [{"id": self.user1_cal1_id}, {"id": self.user1_cal2_id}]
        result = self.api.check_free_busy(
            "2025-08-01T08:00:00-04:00",
            "2025-08-01T13:00:00-04:00",
            items,
            user_id=self.user1_id
        )
        self.assertTrue(result["retrieval_status"])

    def test_multi_user_calendar_interaction(self):
        """Test multi-user calendar interactions."""
        # 1. Both users create calendars
        result1 = self.api.create_calendar("User1 Shared Calendar", user_id=self.user1_id)
        self.assertTrue(result1["creation_status"])
        user1_shared_cal = f"cal_{self.api.state['calendar_counter']}"
        
        result2 = self.api.create_calendar("User2 Shared Calendar", user_id=self.user2_id)
        self.assertTrue(result2["creation_status"])
        user2_shared_cal = f"cal_{self.api.state['calendar_counter']}"
        
        # 2. Create events in respective calendars
        event_data1 = {
            "summary": "User1 Event",
            "start": {"dateTime": "2025-08-01T14:00:00-04:00"},
            "end": {"dateTime": "2025-08-01T15:00:00-04:00"}
        }
        result = self.api.create_event(user1_shared_cal, event_data1, user_id=self.user1_id)
        self.assertTrue(result["creation_status"])
        
        event_data2 = {
            "summary": "User2 Event",
            "start": {"dateTime": "2025-08-01T14:00:00+01:00"},
            "end": {"dateTime": "2025-08-01T15:00:00+01:00"}
        }
        result = self.api.create_event(user2_shared_cal, event_data2, user_id=self.user2_id)
        self.assertTrue(result["creation_status"])
        
        # 3. Verify each user can only access their own calendars
        result1 = self.api.list_calendars(self.user1_id)
        calendar_ids1 = [cal["id"] for cal in result1["calendars"]]
        self.assertIn(user1_shared_cal, calendar_ids1)
        self.assertNotIn(user2_shared_cal, calendar_ids1)
        
        result2 = self.api.list_calendars(self.user2_id)
        calendar_ids2 = [cal["id"] for cal in result2["calendars"]]
        self.assertIn(user2_shared_cal, calendar_ids2)
        self.assertNotIn(user1_shared_cal, calendar_ids2)

    def test_calendar_error_handling_workflow(self):
        """Test comprehensive error handling scenarios."""
        # Test creating calendar with invalid user
        result = self.api.create_calendar("Invalid User Calendar", user_id="invalid@example.com")
        self.assertFalse(result["creation_status"])
        
        # Test updating non-existent calendar
        result = self.api.update_calendar("invalid_cal", summary="Should Fail", user_id=self.user1_id)
        self.assertFalse(result["update_status"])
        
        # Test creating event in non-existent calendar
        event_data = {
            "summary": "Invalid Event",
            "start": {"dateTime": "2025-08-01T10:00:00-04:00"},
            "end": {"dateTime": "2025-08-01T11:00:00-04:00"}
        }
        result = self.api.create_event("invalid_cal", event_data, user_id=self.user1_id)
        self.assertFalse(result["creation_status"])
        
        # Test moving event to non-existent calendar
        result = self.api.move_event(self.user1_cal1_id, self.user1_event2_id, "invalid_cal", user_id=self.user1_id)
        self.assertFalse(result["move_status"])
        
        # Test free/busy with invalid calendar
        items = [{"id": "invalid_cal"}]
        result = self.api.check_free_busy(
            "2025-08-01T08:00:00-04:00",
            "2025-08-01T13:00:00-04:00",
            items,
            user_id=self.user1_id
        )
        self.assertTrue(result["retrieval_status"])  # Still succeeds but returns empty data
        self.assertEqual(len(result["free_busy_data"]), 0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

