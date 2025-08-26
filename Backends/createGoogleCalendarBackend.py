import random
import uuid
import json
import datetime
from datetime import datetime, timedelta
from typing import Dict, Any
import copy
from fake_data import first_names, last_names, domains, event_descriptions, event_locations, timezones

current_datetime = datetime.now()

DEFAULT_STATE: Dict[str, Any] = {
    "users": {},
}

_user_email_to_uuid_map = {}

def generate_random_email(first_name, last_name):
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"

def generate_random_datetime(min_days_ago=0, max_days_ago=365, future_days=30):
    """Generates a random ISO formatted datetime string, either in the past or future."""
    time_offset: timedelta
    if random.random() < 0.7:
        delta_days = random.randint(0, future_days)
        time_offset = timedelta(days=delta_days,
                                hours=random.randint(7, 18),
                                minutes=random.choice([0, 15, 30, 45]))
        return (current_datetime + time_offset).isoformat()
    else:

        actual_min_days_ago = min(min_days_ago, max_days_ago)
        actual_max_days_ago = max(min_days_ago, max_days_ago)

        if actual_min_days_ago == actual_max_days_ago == 0:
            actual_max_days_ago = 1

        delta_days = random.randint(actual_min_days_ago, actual_max_days_ago)
        time_offset = timedelta(days=delta_days,
                                hours=random.randint(7, 18),
                                minutes=random.choice([0, 15, 30, 45]))
        return (current_datetime - time_offset).isoformat()


def _create_user_data(email: str, first_name: str, last_name: str,
                      calendar_data: Dict[str, Any]):
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

    final_events_by_calendar = {
        new_id: {}
        for new_id in temp_new_calendars.keys()
    }

    for old_cal_id, events_dict_old in calendar_data.get("events", {}).items():
        if old_cal_id in _calendar_id_map:
            new_cal_id = _calendar_id_map[old_cal_id]
            for _, event_data in events_dict_old.items():
                new_event_id = str(uuid.uuid4())
                event_data_copy = copy.deepcopy(event_data)
                event_data_copy["id"] = new_event_id

                attendees = []
                for attendee in event_data_copy.get("attendees", []):
                    if "email" in attendee:
                        attendees.append({"email": attendee["email"]})
                event_data_copy["attendees"] = attendees

                start_dict = event_data_copy.get("start", {})
                if "dateTime" not in start_dict or not isinstance(
                        start_dict.get("dateTime"), str):
                    start_dict["dateTime"] = generate_random_datetime()
                else:
                    try:
                        datetime.fromisoformat(start_dict["dateTime"])
                    except ValueError:
                        start_dict["dateTime"] = generate_random_datetime()
                event_data_copy["start"] = start_dict

                end_dict = event_data_copy.get("end", {})
                if "dateTime" not in end_dict or not isinstance(
                        end_dict.get("dateTime"), str):

                    start_dt = datetime.fromisoformat(start_dict["dateTime"])
                    end_dict["dateTime"] = (start_dt + timedelta(
                        minutes=random.choice([30, 60, 90, 120]))).isoformat()
                else:
                    try:
                        datetime.fromisoformat(end_dict["dateTime"])
                    except ValueError:
                        start_dt = datetime.fromisoformat(
                            start_dict["dateTime"])
                        end_dict["dateTime"] = (
                            start_dt +
                            timedelta(minutes=random.choice([30, 60, 90, 120]))
                        ).isoformat()
                event_data_copy["end"] = end_dict

                if "timeZone" not in event_data_copy["start"]:
                    event_data_copy["start"]["timeZone"] = temp_new_calendars[
                        new_cal_id]["timeZone"]
                if "timeZone" not in event_data_copy["end"]:
                    event_data_copy["end"]["timeZone"] = temp_new_calendars[
                        new_cal_id]["timeZone"]

                final_events_by_calendar[new_cal_id][
                    new_event_id] = event_data_copy

    processed_calendar_data["calendars"] = temp_new_calendars
    processed_calendar_data["events"] = final_events_by_calendar

    first_cal_timezone = "America/New_York"
    if temp_new_calendars:
        first_cal_id_key = next(iter(temp_new_calendars))
        first_cal_timezone = temp_new_calendars[first_cal_id_key].get(
            "timeZone", "America/New_York")

    return user_id, {
        "first_name":
        first_name,
        "last_name":
        last_name,
        "email":
        email,
        "calendar_data":
        processed_calendar_data,
        "preferred_timezone":
        first_cal_timezone,
        "last_calendar_sync":
        (current_datetime -
         timedelta(minutes=random.randint(5, 60 * 24))).isoformat()
    }

current_user_emails = list(_user_email_to_uuid_map.keys())

for i in range(48):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = generate_random_email(first, last)

    while email in _user_email_to_uuid_map:
        email = generate_random_email(first, last)

    user_timezone = random.choice(timezones)

    new_calendar_data = {"calendars": {}, "events": {}}

    num_calendars = random.randint(1, 3)
    user_calendar_ids = []
    for c_idx in range(num_calendars):
        cal_id_temp = f"temp_cal_{i}_{c_idx}"
        cal_summary = f"{first}'s {random.choice(['Main', 'Work', 'Personal', 'Side Project'])} Calendar"
        if c_idx > 0:
            cal_summary += f" ({c_idx+1})"

        cal_timezone = random.choice(
            timezones) if random.random() < 0.3 else user_timezone

        new_calendar_data["calendars"][cal_id_temp] = {
            "summary": cal_summary,
            "timeZone": cal_timezone,
            "id": cal_id_temp
        }
        user_calendar_ids.append(cal_id_temp)
        new_calendar_data["events"][cal_id_temp] = {}

    for cal_id_temp in user_calendar_ids:
        num_events = random.randint(3, 25)
        for e_idx in range(num_events):
            event_id_temp = f"temp_event_{i}_{e_idx}_{cal_id_temp}"

            event_start = generate_random_datetime(min_days_ago=1,
                                                   max_days_ago=730,
                                                   future_days=365)

            start_dt = datetime.fromisoformat(event_start)
            event_end = (start_dt + timedelta(
                minutes=random.choice([30, 60, 90, 120]))).isoformat()

            attendees_list = [{"email": email}]

            num_attendees = random.randint(0, 3)
            possible_attendee_emails = list(_user_email_to_uuid_map.keys())

            for _ in range(num_attendees):
                if random.random() < 0.7 and possible_attendee_emails:
                    attendee_email = random.choice(possible_attendee_emails)
                    if attendee_email != email:
                        attendees_list.append({"email": attendee_email})
                else:
                    attendees_list.append(
                        {"email": generate_random_email("external", "guest")})

            new_calendar_data["events"][cal_id_temp][event_id_temp] = {
                "id":
                event_id_temp,
                "location":
                random.choice(event_locations),
                "start": {
                    "dateTime":
                    event_start,
                    "timeZone":
                    new_calendar_data["calendars"][cal_id_temp]["timeZone"]
                },
                "end": {
                    "dateTime":
                    event_end,
                    "timeZone":
                    new_calendar_data["calendars"][cal_id_temp]["timeZone"]
                },
                "description":
                random.choice(event_descriptions)
                if random.random() < 0.7 else None,
                "attendees":
                attendees_list,
                "status":
                random.choice(["confirmed", "tentative", "cancelled"])
            }

    user_id, user_data = _create_user_data(email, first, last,
                                           new_calendar_data)
    DEFAULT_STATE["users"][user_id] = user_data
    current_user_emails.append(email)

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")

output_filename = 'diverse_google_calendar_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

if DEFAULT_STATE["users"]:
    sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(
        0,
        len(DEFAULT_STATE["users"]) - 1)]