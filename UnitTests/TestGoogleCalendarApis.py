from audio_gorilla.GoogleCalendarApis import GoogleCalendarApis, DEFAULT_STATE
import unittest
from copy import deepcopy

class TestGoogleCalendarApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh GoogleCalendar instance for each test."""
        self.calendar_api = GoogleCalendarApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.calendar_api._load_scenario(deepcopy(DEFAULT_STATE))

    def test_create_calendar_success(self):
        """Test creating a new calendar successfully."""
        initial_calendar_count = len(self.calendar_api.calendars)
        result = self.calendar_api.create_calendar(summary="New Project Calendar", time_zone="America/New_York")
        self.assertTrue(result["creation_status"])
        self.assertEqual(len(self.calendar_api.calendars), initial_calendar_count + 1)
        # Verify the new calendar exists and has correct summary
        new_cal_id = f"cal_{initial_calendar_count + 1}"
        self.assertIn(new_cal_id, self.calendar_api.calendars)
        self.assertEqual(self.calendar_api.calendars[new_cal_id]["summary"], "New Project Calendar")

    def test_create_calendar_unauthorized(self):
        """Test creating a calendar when unauthorized."""
        self.calendar_api.authorized = False
        result = self.calendar_api.create_calendar(summary="Unauthorized Calendar")
        self.assertFalse(result["creation_status"])
        self.assertEqual(len(self.calendar_api.calendars), 3) # Should not add a new calendar

    def test_get_calendar_success(self):
        """Test getting an existing calendar by ID."""
        result = self.calendar_api.get_calendar(calendar_id="cal_1")
        self.assertTrue(result["retrieval_status"])
        self.assertEqual(result["calendar_data"]["summary"], "Personal Calendar")
        self.assertEqual(result["calendar_data"]["id"], "cal_1")

    def test_get_calendar_not_found(self):
        """Test getting a non-existent calendar."""
        result = self.calendar_api.get_calendar(calendar_id="non_existent_cal")
        self.assertFalse(result["retrieval_status"])
        self.assertEqual(result["calendar_data"], {})

    def test_create_event_success(self):
        """Test creating an event in an existing calendar."""
        calendar_id = "cal_1"
        initial_event_count = len(self.calendar_api.events[calendar_id])
        event_data = {
            "summary": "Team Sync",
            "start": {"dateTime": "2025-07-25T09:00:00-04:00", "timeZone": "America/New_York"},
            "end": {"dateTime": "2025-07-25T10:00:00-04:00", "timeZone": "America/New_York"},
            "description": "Daily stand-up meeting."
        }
        result = self.calendar_api.create_event(calendar_id=calendar_id, event_data=event_data)
        self.assertTrue(result["creation_status"])
        self.assertEqual(len(self.calendar_api.events[calendar_id]), initial_event_count + 1)
        # Verify the new event exists
        new_event_id = f"event_{initial_event_count + 1}"
        self.assertIn(new_event_id, self.calendar_api.events[calendar_id])
        self.assertEqual(self.calendar_api.events[calendar_id][new_event_id]["summary"], "Team Sync")

    def test_create_event_calendar_not_found(self):
        """Test creating an event in a non-existent calendar."""
        event_data = {
            "summary": "Failed Event",
            "start": {"dateTime": "2025-07-25T09:00:00-04:00", "timeZone": "America/New_York"},
            "end": {"dateTime": "2025-07-25T10:00:00-04:00", "timeZone": "America/New_York"}
        }
        result = self.calendar_api.create_event(calendar_id="non_existent_cal", event_data=event_data)
        self.assertFalse(result["creation_status"])

    def test_list_events_success(self):
        """Test listing events from an existing calendar."""
        result = self.calendar_api.list_events(calendar_id="cal_1")
        self.assertTrue(result["retrieval_status"])
        self.assertEqual(len(result["events"]), 2)
        self.assertEqual(result["events"][0]["summary"], "Morning Run")
        self.assertEqual(result["events"][1]["summary"], "Dentist Appointment")

    def test_list_events_with_time_range(self):
        """Test listing events with a time range filter."""
        # Events in cal_1: "Morning Run" (July 19), "Dentist Appointment" (July 20)
        result = self.calendar_api.list_events(
            calendar_id="cal_1",
            time_min="2025-07-20T00:00:00-04:00",
            time_max="2025-07-20T23:59:59-04:00"
        )
        self.assertTrue(result["retrieval_status"])
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(result["events"][0]["summary"], "Dentist Appointment")

    def test_delete_event_success(self):
        """Test deleting an event from a calendar."""
        calendar_id = "cal_1"
        event_id = "event_1"
        initial_event_count = len(self.calendar_api.events[calendar_id])
        result = self.calendar_api.delete_event(calendar_id=calendar_id, event_id=event_id)
        self.assertTrue(result["deletion_status"])
        self.assertEqual(len(self.calendar_api.events[calendar_id]), initial_event_count - 1)
        self.assertNotIn(event_id, self.calendar_api.events[calendar_id])

    def test_delete_event_not_found(self):
        """Test deleting a non-existent event."""
        result = self.calendar_api.delete_event(calendar_id="cal_1", event_id="non_existent_event")
        self.assertFalse(result["deletion_status"])

    def test_move_event_success(self):
        """Test moving an event from one calendar to another."""
        source_cal_id = "cal_1"
        dest_cal_id = "cal_2"
        event_id = "event_1" # "Morning Run"

        initial_source_event_count = len(self.calendar_api.events[source_cal_id])
        initial_dest_event_count = len(self.calendar_api.events[dest_cal_id])

        print(initial_source_event_count, initial_dest_event_count)

        result = self.calendar_api.move_event(
            calendar_id=source_cal_id,
            event_id=event_id,
            destination_calendar_id=dest_cal_id
        )
    
        print("DEST AFTER TEST", len(self.calendar_api.events[dest_cal_id]))
        self.assertTrue(result["move_status"])

        # Verify event is removed from source
        self.assertEqual(len(self.calendar_api.events[source_cal_id]), initial_source_event_count - 1)
        self.assertNotIn(event_id, self.calendar_api.events[source_cal_id])

        # Verify event is added to destination
        self.assertEqual(len(self.calendar_api.events[dest_cal_id]), initial_dest_event_count + 1)
        self.assertIn(event_id, self.calendar_api.events[dest_cal_id])
        self.assertEqual(self.calendar_api.events[dest_cal_id][f"event_3"]["summary"], "Morning Run")

    def test_check_free_busy_success(self):
        """Test checking free/busy status for calendars."""
        time_min = "2025-07-19T00:00:00-04:00"
        time_max = "2025-07-20T00:00:00-04:00"
        items = [{"id": "cal_1"}, {"id": "cal_2"}] # Check personal and work calendars

        result = self.calendar_api.check_free_busy(time_min=time_min, time_max=time_max, items=items)
        self.assertTrue(result["retrieval_status"])
        self.assertIn("cal_1", result["free_busy_data"])
        self.assertIn("cal_2", result["free_busy_data"])
        self.assertEqual(result["free_busy_data"]["cal_1"]["busy"][0]["start"], time_min)
        self.assertEqual(result["free_busy_data"]["cal_2"]["busy"][0]["end"], time_max)

    # --- Combined Functionality Tests ---

    def test_create_calendar_and_add_event(self):
        """
        Scenario: Create a new calendar, then add an event to it.
        Functions: create_calendar, create_event, list_events
        """
        # 1. Create a new calendar
        create_cal_result = self.calendar_api.create_calendar(summary="New Test Calendar", time_zone="Europe/Berlin")
        self.assertTrue(create_cal_result["creation_status"])
        
        # Find the ID of the newly created calendar
        new_cal_id = None
        for cal_id, cal_data in self.calendar_api.calendars.items():
            if cal_data["summary"] == "New Test Calendar":
                new_cal_id = cal_id
                break
        self.assertIsNotNone(new_cal_id)

        # 2. Add an event to the new calendar
        event_data = {
            "summary": "Project Review",
            "location": "Online",
            "start": {"dateTime": "2025-08-01T14:00:00+02:00", "timeZone": "Europe/Berlin"},
            "end": {"dateTime": "2025-08-01T15:00:00+02:00", "timeZone": "Europe/Berlin"},
            "description": "Review Q3 project progress."
        }
        create_event_result = self.calendar_api.create_event(calendar_id=new_cal_id, event_data=event_data)
        self.assertTrue(create_event_result["creation_status"])

        # 3. List events in the new calendar to verify
        list_events_result = self.calendar_api.list_events(calendar_id=new_cal_id)
        self.assertTrue(list_events_result["retrieval_status"])
        self.assertEqual(len(list_events_result["events"]), 1)
        self.assertEqual(list_events_result["events"][0]["summary"], "Project Review")

    def test_move_event_and_verify_calendars(self):
        """
        Scenario: Move an existing event from one calendar to another, then verify its presence in both.
        Functions: move_event, get_event, list_events
        """
        source_cal_id = "cal_1"
        dest_cal_id = "cal_3"
        event_to_move_id = "event_2" # "Dentist Appointment"

        # Initial checks
        source_initial_events = self.calendar_api.list_events(calendar_id=source_cal_id)["events"]
        dest_initial_events = self.calendar_api.list_events(calendar_id=dest_cal_id)["events"]
        self.assertIn(event_to_move_id, [e["id"] for e in source_initial_events])
        self.assertNotIn(event_to_move_id, [e["id"] for e in dest_initial_events])

        # 1. Move the event
        move_result = self.calendar_api.move_event(
            calendar_id=source_cal_id,
            event_id=event_to_move_id,
            destination_calendar_id=dest_cal_id
        )
        self.assertTrue(move_result["move_status"])

        # 2. Verify event is no longer in source calendar
        source_after_move = self.calendar_api.list_events(calendar_id=source_cal_id)
        self.assertTrue(source_after_move["retrieval_status"])
        self.assertNotIn(event_to_move_id, [e["id"] for e in source_after_move["events"]])
        self.assertEqual(len(source_after_move["events"]), len(source_initial_events) - 1)

        # 3. Verify event is now in destination calendar
        dest_after_move = self.calendar_api.list_events(calendar_id=dest_cal_id)
        self.assertTrue(dest_after_move["retrieval_status"])
        self.assertIn(event_to_move_id, [e["id"] for e in dest_after_move["events"]])
        self.assertEqual(len(dest_after_move["events"]), len(dest_initial_events) + 1)
        
        # Get the event from its new location to confirm details
        moved_event_details = self.calendar_api.get_event(calendar_id=dest_cal_id, event_id=event_to_move_id)
        self.assertTrue(moved_event_details["retrieval_status"])
        self.assertEqual(moved_event_details["event_data"]["summary"], "Dentist Appointment")

    def test_check_free_busy_after_event_creation(self):
        """
        Scenario: Check free/busy, create an event, then check free/busy again to see the impact.
        Functions: check_free_busy, create_event
        """
        calendar_id = "cal_1"
        # Define a time range where cal_1 is initially free (assuming no events in this specific future slot)
        time_min_future = "2025-08-10T09:00:00-04:00"
        time_max_future = "2025-08-10T10:00:00-04:00"
        
        # 1. Initial free/busy check (should show as busy due to dummy implementation)
        initial_free_busy = self.calendar_api.check_free_busy(
            time_min=time_min_future,
            time_max=time_max_future,
            items=[{"id": calendar_id}]
        )
        self.assertTrue(initial_free_busy["retrieval_status"])
        # The dummy implementation always marks as busy for the checked period
        self.assertEqual(initial_free_busy["free_busy_data"][calendar_id]["busy"][0]["start"], time_min_future)

        # 2. Create a new event within that time slot
        event_data = {
            "summary": "New Meeting",
            "start": {"dateTime": time_min_future, "timeZone": "America/New_York"},
            "end": {"dateTime": time_max_future, "timeZone": "America/New_York"},
            "description": "Important discussion."
        }
        create_event_result = self.calendar_api.create_event(calendar_id=calendar_id, event_data=event_data)
        self.assertTrue(create_event_result["creation_status"])

        # 3. Check free/busy again (should still show busy, confirming the dummy behavior)
        final_free_busy = self.calendar_api.check_free_busy(
            time_min=time_min_future,
            time_max=time_max_future,
            items=[{"id": calendar_id}]
        )
        self.assertTrue(final_free_busy["retrieval_status"])
        self.assertEqual(final_free_busy["free_busy_data"][calendar_id]["busy"][0]["start"], time_min_future)
        # Note: In a real API, this would confirm the newly created event makes the slot busy.
        # Given the dummy free_busy, this primarily tests that the function still works after event creation.


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
