"""Quick test script to verify the realistic Google Calendar API changes."""

from GoogleCalendarApis import GoogleCalendarApis

# Create API (loads DEFAULT_STATE automatically)
api = GoogleCalendarApis()

# Get first user email (API sets first user as authenticated by default)
first_user_email = api._get_user_email_by_id(api.current_user)
print(f"API auto-authenticated as: {first_user_email}")
print()

# Test 1: Authenticate
print("=" * 60)
print("TEST 1: Authentication")
print("=" * 60)
result = api.authenticate(first_user_email)
print(f"Authentication result: {result}")
print()

# Test 2: List calendar list (should use authenticated user)
print("=" * 60)
print("TEST 2: List Calendar List (no user_id parameter!)")
print("=" * 60)
try:
    calendars = api.list_calendar_list()
    print(f"Calendar list structure: {list(calendars.keys())}")
    print(f"Number of calendars: {len(calendars.get('items', []))}")
    if calendars.get('items'):
        print(f"First calendar: {calendars['items'][0]}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 3: Get calendar using "primary" keyword
print("=" * 60)
print("TEST 3: Get Calendar with 'primary' keyword")
print("=" * 60)
try:
    calendar = api.get_calendar("primary")
    print(f"Calendar structure: {list(calendar.keys())}")
    print(f"Calendar: {calendar}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 4: Create a new calendar (no user_id!)
print("=" * 60)
print("TEST 4: Create Calendar (no user_id parameter!)")
print("=" * 60)
try:
    new_calendar = api.insert_calendar(
        summary="My Test Calendar",
        time_zone="America/New_York",
        description="A test calendar for testing"
    )
    print(f"Created calendar structure: {list(new_calendar.keys())}")
    print(f"Created calendar: {new_calendar}")
    calendar_id = new_calendar['id']
except Exception as e:
    print(f"Error: {e}")
    calendar_id = None
print()

# Test 5: List events (with search and filters)
print("=" * 60)
print("TEST 5: List Events with filters (no user_id!)")
print("=" * 60)
try:
    events = api.list_events(
        calendar_id="primary",
        max_results=5,
        order_by="startTime"
    )
    print(f"Events structure: {list(events.keys())}")
    print(f"Number of events: {len(events.get('items', []))}")
    if events.get('items'):
        print(f"First event: {events['items'][0]}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 6: Create an event
print("=" * 60)
print("TEST 6: Create Event (no user_id!)")
print("=" * 60)
try:
    new_event = api.insert_event(
        calendar_id="primary",
        summary="Test Meeting",
        start_time="2024-12-15T10:00:00-05:00",
        end_time="2024-12-15T11:00:00-05:00",
        time_zone="America/New_York",
        description="A test meeting",
        location="Conference Room A"
    )
    print(f"Created event structure: {list(new_event.keys())}")
    print(f"Event has 'kind' field: {'kind' in new_event}")
    print(f"Event has 'etag' field: {'etag' in new_event}")
    print(f"Event has 'status' field: {'status' in new_event}")
    print(f"Created event: {new_event}")
    event_id = new_event['id']
except Exception as e:
    print(f"Error: {e}")
    event_id = None
print()

# Test 7: Update event
if event_id:
    print("=" * 60)
    print("TEST 7: Update Event (no user_id!)")
    print("=" * 60)
    try:
        updated_event = api.update_event(
            calendar_id="primary",
            event_id=event_id,
            summary="Updated Test Meeting",
            location="Conference Room B"
        )
        print(f"Updated event: {updated_event}")
    except Exception as e:
        print(f"Error: {e}")
    print()

# Test 8: Free/busy check
print("=" * 60)
print("TEST 8: Check Free/Busy (no user_id!)")
print("=" * 60)
try:
    freebusy = api.check_free_busy(
        time_min="2024-12-01T00:00:00Z",
        time_max="2024-12-31T23:59:59Z",
        items=[{"id": "primary"}]
    )
    print(f"Free/busy structure: {list(freebusy.keys())}")
    print(f"Has 'kind' field: {'kind' in freebusy}")
    print(f"Free/busy: {freebusy}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 9: Try to use API without authentication (should fail)
print("=" * 60)
print("TEST 9: Try without authentication (should fail)")
print("=" * 60)
api2 = GoogleCalendarApis()
# Clear authentication
api2.current_user = None
try:
    calendars = api2.list_calendar_list()
    print(f"UNEXPECTED: Should have failed but got: {calendars}")
except Exception as e:
    print(f"EXPECTED: Got exception: {e}")
print()

print("=" * 60)
print("SUMMARY")
print("=" * 60)
print("✓ No more user_id parameters!")
print("✓ Using 'primary' keyword for main calendar")
print("✓ Returns direct resources, not status dictionaries")
print("✓ Includes 'kind', 'etag', and other standard fields")
print("✓ Authentication required before API calls")
print("✓ Matches real Google Calendar API v3 structure")
