import random
import uuid
import json
import datetime
from datetime import datetime, timedelta
from typing import Dict, Any
import copy

# Current time for realistic date generation
current_datetime = datetime.now()

DEFAULT_STATE: Dict[str, Any] = {
    "users": {},
}

_user_email_to_uuid_map = {}

def generate_random_email(first_name, last_name):
    domains = ["bizmail.co", "techcorp.io", "webmail.net", "globalinc.org", "mailhub.app"]
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"

def generate_random_datetime(min_days_ago=0, max_days_ago=365, future_days=30):
    """Generates a random ISO formatted datetime string, either in the past or future."""
    time_offset: timedelta
    if random.random() < 0.7: # 70% chance of a future event
        delta_days = random.randint(0, future_days)
        time_offset = timedelta(days=delta_days, hours=random.randint(7, 18), minutes=random.choice([0, 15, 30, 45]))
        return (current_datetime + time_offset).isoformat()
    else: # 30% chance of a past event
        # Ensure min_days_ago is less than or equal to max_days_ago
        actual_min_days_ago = min(min_days_ago, max_days_ago) # To handle cases like (730, 365) gracefully
        actual_max_days_ago = max(min_days_ago, max_days_ago)
        
        # If min_days_ago and max_days_ago are both 0, avoid error by setting a small range
        if actual_min_days_ago == actual_max_days_ago == 0:
            actual_max_days_ago = 1 # At least one day in the past

        delta_days = random.randint(actual_min_days_ago, actual_max_days_ago)
        time_offset = timedelta(days=delta_days, hours=random.randint(7, 18), minutes=random.choice([0, 15, 30, 45]))
        return (current_datetime - time_offset).isoformat()


def _create_user_data(email: str, first_name: str, last_name: str, calendar_data: Dict[str, Any]):
    user_id = str(uuid.uuid4())
    _user_email_to_uuid_map[email] = user_id

    processed_calendar_data = copy.deepcopy(calendar_data)

    _calendar_id_map = {}
    temp_new_calendars = {}
    for old_cal_id, cal_data in calendar_data.get("calendars", {}).items():
        new_cal_id = str(uuid.uuid4())
        cal_data_copy = copy.deepcopy(cal_data)
        cal_data_copy["id"] = new_cal_id
        temp_new_calendars[new_cal_id] = cal_data_copy
        _calendar_id_map[old_cal_id] = new_cal_id

    final_events_by_calendar = {new_id: {} for new_id in temp_new_calendars.keys()}

    for old_cal_id, events_dict_old in calendar_data.get("events", {}).items():
        if old_cal_id in _calendar_id_map:
            new_cal_id = _calendar_id_map[old_cal_id]
            for old_event_id, event_data in events_dict_old.items():
                new_event_id = str(uuid.uuid4())
                event_data_copy = copy.deepcopy(event_data)
                event_data_copy["id"] = new_event_id

                # Ensure attendees emails are resolved later if they are internal
                attendees = []
                for attendee in event_data_copy.get("attendees", []):
                    if "email" in attendee:
                        attendees.append({"email": attendee["email"]})
                event_data_copy["attendees"] = attendees

                # --- Handle start datetime ---
                start_dict = event_data_copy.get("start", {})
                if "dateTime" not in start_dict or not isinstance(start_dict.get("dateTime"), str):
                    start_dict["dateTime"] = generate_random_datetime()
                else:
                    try:
                        datetime.fromisoformat(start_dict["dateTime"])
                    except ValueError:
                        start_dict["dateTime"] = generate_random_datetime()
                event_data_copy["start"] = start_dict # Update the dictionary

                # --- Handle end datetime ---
                end_dict = event_data_copy.get("end", {})
                if "dateTime" not in end_dict or not isinstance(end_dict.get("dateTime"), str):
                    # Ensure start_dt is valid before calculating end_dt
                    start_dt = datetime.fromisoformat(start_dict["dateTime"])
                    end_dict["dateTime"] = (start_dt + timedelta(minutes=random.choice([30, 60, 90, 120]))).isoformat()
                else:
                    try:
                        datetime.fromisoformat(end_dict["dateTime"])
                    except ValueError:
                        start_dt = datetime.fromisoformat(start_dict["dateTime"])
                        end_dict["dateTime"] = (start_dt + timedelta(minutes=random.choice([30, 60, 90, 120]))).isoformat()
                event_data_copy["end"] = end_dict # Update the dictionary

                # Ensure timeZone is present in start/end, default to calendar timezone
                if "timeZone" not in event_data_copy["start"]:
                    event_data_copy["start"]["timeZone"] = temp_new_calendars[new_cal_id]["timeZone"]
                if "timeZone" not in event_data_copy["end"]:
                    event_data_copy["end"]["timeZone"] = temp_new_calendars[new_cal_id]["timeZone"]

                final_events_by_calendar[new_cal_id][new_event_id] = event_data_copy

    processed_calendar_data["calendars"] = temp_new_calendars
    processed_calendar_data["events"] = final_events_by_calendar

    # Derive preferred_timezone from the first calendar if available
    first_cal_timezone = "America/New_York" # Default if no calendars
    if temp_new_calendars:
        first_cal_id_key = next(iter(temp_new_calendars)) # Get the first key
        first_cal_timezone = temp_new_calendars[first_cal_id_key].get("timeZone", "America/New_York")


    return user_id, {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "calendar_data": processed_calendar_data,
        "preferred_timezone": first_cal_timezone,
        "last_calendar_sync": (current_datetime - timedelta(minutes=random.randint(5, 60 * 24))).isoformat() # New field
    }

# --- Initial Users (provided in the prompt) ---
users_initial_data = [
    ("alice.smith@bizmail.co", "Alice", "Smith", {
        "calendars": {
            "cal_1": {
                "summary": "Personal Calendar (Alice)",
                "timeZone": "America/New_York",
                "id": "cal_1"
            },
            "cal_2": {
                "summary": "Work Calendar (Alice)",
                "timeZone": "America/Los_Angeles",
                "id": "cal_2"
            }
        },
        "events": {
            "cal_1": {
                "event_1": {
                    "id": "event_1",
                    "summary": "Morning Run",
                    "location": "Central Park",
                    "start": {"dateTime": (current_datetime + timedelta(days=1, hours=7)).isoformat(), "timeZone": "America/New_York"},
                    "end": {"dateTime": (current_datetime + timedelta(days=1, hours=8)).isoformat(), "timeZone": "America/New_York"},
                    "description": "Daily 5k run.",
                    "attendees": [{"email": "alice.smith@bizmail.co"}]
                },
                "event_2": {
                    "id": "event_2",
                    "summary": "Doctor's Appointment",
                    "location": "Medical Clinic",
                    "start": {"dateTime": (current_datetime + timedelta(days=3, hours=14)).isoformat(), "timeZone": "America/New_York"},
                    "end": {"dateTime": (current_datetime + timedelta(days=3, hours=15)).isoformat(), "timeZone": "America/New_York"},
                    "description": "Annual check-up.",
                    "attendees": [{"email": "alice.smith@bizmail.co"}]
                }
            },
            "cal_2": {
                "event_3": {
                    "id": "event_3",
                    "summary": "Team Meeting",
                    "location": "Conference Room A",
                    "start": {"dateTime": (current_datetime + timedelta(days=2, hours=10)).isoformat(), "timeZone": "America/Los_Angeles"},
                    "end": {"dateTime": (current_datetime + timedelta(days=2, hours=11)).isoformat(), "timeZone": "America/Los_Angeles"},
                    "description": "Weekly sync-up.",
                    "attendees": [{"email": "alice.smith@bizmail.co"}, {"email": "bob.jones@bizmail.co"}]
                }
            }
        }
    }),
    ("bob.jones@bizmail.co", "Bob", "Jones", {
        "calendars": {
            "cal_3": {
                "summary": "Bob's Personal Calendar",
                "timeZone": "America/Chicago",
                "id": "cal_3"
            }
        },
        "events": {
            "cal_3": {
                "event_4": {
                    "id": "event_4",
                    "summary": "Client Call",
                    "location": "Virtual",
                    "start": {"dateTime": (current_datetime + timedelta(days=4, hours=9)).isoformat(), "timeZone": "America/Chicago"},
                    "end": {"dateTime": (current_datetime + timedelta(days=4, hours=10)).isoformat(), "timeZone": "America/Chicago"},
                    "description": "Discussion with new client.",
                    "attendees": [{"email": "bob.jones@bizmail.co"}]
                }
            }
        }
    })
]

# Populate initial users
for email, first_name, last_name, calendar_data in users_initial_data:
    user_id, user_data = _create_user_data(email, first_name, last_name, calendar_data)
    DEFAULT_STATE["users"][user_id] = user_data

# --- Generate 48 more diverse and realistic users ---
first_names = ["Sophia", "Liam", "Olivia", "Noah", "Ava", "Jackson", "Isabella", "Aiden", "Mia", "Lucas", "Harper", "Ethan", "Evelyn", "Mason", "Abigail", "Caleb", "Charlotte", "Logan", "Amelia", "Michael", "Ella", "Jacob", "Aria", "Daniel", "Chloe", "Samuel", "Grace", "David", "Victoria", "Joseph", "Penelope", "Matthew", "Riley", "Benjamin", "Layla", "Andrew", "Lily", "Gabriel", "Natalie", "Christopher", "Hannah", "James", "Zoe", "Ryan", "Scarlett", "Nathan", "Addison", "Christian", "Aubrey", "Joshua"]
last_names = ["Chen", "Kim", "Singh", "Lopez", "Garcia", "Nguyen", "Davis", "Jackson", "Harris", "White", "Moore", "Clark", "Lewis", "Baker", "Adams", "Hill", "Nelson", "Carter", "Mitchell", "Roberts", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders"]
timezones = ["America/New_York", "America/Los_Angeles", "America/Chicago", "America/Denver", "Europe/London", "Europe/Paris", "Asia/Tokyo", "Asia/Shanghai", "Australia/Sydney"]
event_summaries = ["Daily Standup", "Project Brainstorm", "Client Demo", "One-on-One Meeting", "Team Lunch", "Training Session", "Code Review", "Strategic Planning", "Vendor Call", "Product Launch Sync", "Workout Session", "Dentist Appointment", "Grocery Shopping", "Book Club Meeting", "Family Dinner"]
event_locations = ["Conference Room A", "Zoom Call", "Office 3B", "Cafe Central", "Virtual", "Gym", "Home", "Library", "Client Site"]
event_descriptions = ["Discuss daily progress.", "Generate new ideas for Q3.", "Showcase latest features.", "Catch up on goals.", "Casual team get-together.", "Learn new software.", "Review pull requests.", "Outline next year's strategy.", "Negotiate new contract.", "Coordinate launch activities.", "Stay fit.", "Routine check-up.", "Weekly supplies run.", "Discuss current reading.", "Enjoy time with family."]

current_user_emails = list(_user_email_to_uuid_map.keys())

for i in range(48): # Generate 48 additional users (2 existing + 48 new = 50 total)
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = generate_random_email(first, last)
    
    # Ensure unique email
    while email in _user_email_to_uuid_map:
        email = generate_random_email(first, last)

    user_timezone = random.choice(timezones)
    
    new_calendar_data = {
        "calendars": {},
        "events": {}
    }

    # Generate 1 to 3 calendars for each user
    num_calendars = random.randint(1, 3)
    user_calendar_ids = []
    for c_idx in range(num_calendars):
        cal_id_temp = f"temp_cal_{i}_{c_idx}" # Temporary ID for creation process
        cal_summary = f"{first}'s {random.choice(['Main', 'Work', 'Personal', 'Side Project'])} Calendar"
        if c_idx > 0: # Ensure distinct summaries for multiple calendars
            cal_summary += f" ({c_idx+1})"
        
        cal_timezone = random.choice(timezones) if random.random() < 0.3 else user_timezone # 30% chance of different timezone
        
        new_calendar_data["calendars"][cal_id_temp] = {
            "summary": cal_summary,
            "timeZone": cal_timezone,
            "id": cal_id_temp # This will be replaced by UUID by _create_user_data
        }
        user_calendar_ids.append(cal_id_temp)
        new_calendar_data["events"][cal_id_temp] = {} # Initialize events dict for this temp calendar

    # Generate events for each calendar
    for cal_id_temp in user_calendar_ids:
        num_events = random.randint(3, 25)
        for e_idx in range(num_events):
            event_id_temp = f"temp_event_{i}_{e_idx}_{cal_id_temp}" # Temporary ID
            
            # Fix for ValueError: empty range in randrange(730, 366)
            # Use min_days_ago=1 and max_days_ago=730 to get events between 1 day and 2 years ago
            event_start = generate_random_datetime(min_days_ago=1, max_days_ago=730, future_days=365)
            
            start_dt = datetime.fromisoformat(event_start)
            event_end = (start_dt + timedelta(minutes=random.choice([30, 60, 90, 120]))).isoformat()
            
            attendees_list = [{"email": email}] # Current user is always an attendee
            
            # Add other attendees (random existing users or external emails)
            num_attendees = random.randint(0, 3)
            possible_attendee_emails = list(_user_email_to_uuid_map.keys())
            
            for _ in range(num_attendees):
                if random.random() < 0.7 and possible_attendee_emails: # 70% chance of internal attendee
                    attendee_email = random.choice(possible_attendee_emails)
                    if attendee_email != email: # Don't add self twice
                        attendees_list.append({"email": attendee_email})
                else: # 30% chance of external attendee
                    attendees_list.append({"email": generate_random_email("external", "guest")})

            new_calendar_data["events"][cal_id_temp][event_id_temp] = {
                "id": event_id_temp, # This will be replaced by UUID
                "summary": random.choice(event_summaries),
                "location": random.choice(event_locations),
                "start": {"dateTime": event_start, "timeZone": new_calendar_data["calendars"][cal_id_temp]["timeZone"]},
                "end": {"dateTime": event_end, "timeZone": new_calendar_data["calendars"][cal_id_temp]["timeZone"]},
                "description": random.choice(event_descriptions) if random.random() < 0.7 else None, # 70% chance of description
                "attendees": attendees_list,
                "status": random.choice(["confirmed", "tentative", "cancelled"]) # New field: Event status
            }

    user_id, user_data = _create_user_data(email, first, last, new_calendar_data)
    DEFAULT_STATE["users"][user_id] = user_data
    current_user_emails.append(email) # Add new user to possible attendees for subsequent users

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")

output_filename = 'diverse_google_calendar_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

if DEFAULT_STATE["users"]:
    sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(0, len(DEFAULT_STATE["users"]) - 1)]
    print(f"\nSample data for user {DEFAULT_STATE['users'][sample_user_id]['first_name']} {DEFAULT_STATE['users'][sample_user_id]['last_name']}:")
    print(json.dumps(DEFAULT_STATE["users"][sample_user_id], indent=2))
