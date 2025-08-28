import datetime
import copy
import uuid
import json
import random
from typing import Dict, Any
from fake_data import first_names, last_names, domains, playlist_titles

_initial_user_email_to_uuid_map = {}
_initial_vehicle_tag_to_uuid_map = {}

def _convert_initial_data_to_uuids(initial_data: Dict[str, Any]) -> Dict[str, Any]:
    converted_data = copy.deepcopy(initial_data)
    global _initial_user_email_to_uuid_map
    global _initial_vehicle_tag_to_uuid_map
    _initial_user_email_to_uuid_map = {}
    _initial_vehicle_tag_to_uuid_map = {}
    current_time_iso = datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"
    new_users = {}
    for email, user_data in converted_data.get("users", {}).items():
        user_id = str(uuid.uuid4())
        _initial_user_email_to_uuid_map[email] = user_id
        user_data["id"] = user_id
        if "friends" in user_data:
            user_data["friends"] = [
                _initial_user_email_to_uuid_map.get(friend_email, friend_email)
                for friend_email in user_data["friends"]
            ]
        new_users[user_id] = user_data
    converted_data["users"] = new_users
    for user_id, user_data in converted_data["users"].items():
        if "friends" in user_data:
            user_data["friends"] = [
                _initial_user_email_to_uuid_map.get(friend_email, friend_email)
                for friend_email in user_data["friends"]
            ]
            user_data["friends"] = [
                friend_id for friend_id in user_data["friends"] 
                if friend_id in converted_data["users"] or friend_id in _initial_user_email_to_uuid_map.values()
            ]
    for user_original_email, user_original_data in initial_data.get("users", {}).items():
        user_uuid = _initial_user_email_to_uuid_map[user_original_email]
        user_tesla_data = converted_data["users"][user_uuid].get("tesla_data", {})
        old_vehicles = user_tesla_data.get("vehicles", {})
        new_vehicles = {}
        for old_vehicle_tag, vehicle_data in old_vehicles.items():
            new_vehicle_id = str(uuid.uuid4())
            _initial_vehicle_tag_to_uuid_map[(user_uuid, old_vehicle_tag)] = new_vehicle_id
            vehicle_data["id"] = new_vehicle_id
            if "createdTime" not in vehicle_data:
                vehicle_data["createdTime"] = current_time_iso
            if "modifiedTime" not in vehicle_data:
                vehicle_data["modifiedTime"] = current_time_iso
            vehicle_data["original_vehicle_tag"] = old_vehicle_tag 
            new_vehicles[new_vehicle_id] = vehicle_data
        user_tesla_data["vehicles"] = new_vehicles
        converted_data["users"][user_uuid]["tesla_data"] = user_tesla_data
    return converted_data

RAW_DEFAULT_STATE = {
    "users": {
    }
}

def generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365*5):
    delta_days = random.randint(days_ago_min, days_ago_max)
    time_offset = datetime.timedelta(days=delta_days, 
                                     hours=random.randint(0, 23), 
                                     minutes=random.randint(0, 59), 
                                     seconds=random.randint(0, 59))
    dt = datetime.datetime.now(datetime.timezone.utc) - time_offset
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

def generate_vin():
    prefix = random.choice(["5YJ", "7SA", "LFV", "LRW"])
    year_code = random.choice("PRSTVWXY123456789")
    plant_code = random.choice("ABCDEFGHJKLMNPRSTVWXY")
    random_chars = ''.join(random.choices('0123456789ABCDEFGHJKLMNPRSTUVWXYZ', k=12))
    return f"{prefix}{random_chars[:5]}{year_code}{plant_code}{random_chars[7:]}"

def generate_tesla_model():
    return random.choice(["Model 3", "Model Y", "Model S", "Model X", "Cybertruck", "Roadster"])

def generate_location():
    lat = random.uniform(25.0, 49.0)
    lon = random.uniform(-125.0, -66.0)
    return {"latitude": round(lat, 4), "longitude": round(lon, 4)}

sentry_alerts = [
    "Motion detected near front door", "Object too close to rear bumper",
    "Alarm triggered by strange noise", "Recording event - vehicle approached"
]
firmware_versions = ["2024.14.7", "2024.12.3", "2024.8.9", "2023.44.30.8", "2023.38.10"]


num_initial_users = len(RAW_DEFAULT_STATE["users"])
num_users_to_add = 50 - num_initial_users
DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)
all_user_uuids = list(DEFAULT_STATE["users"].keys())

for i in range(num_users_to_add):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}{random.randint(1, 999)}@{random.choice(domains)}"
    

    existing_emails = set([DEFAULT_STATE["users"][uid].get("email") for uid in DEFAULT_STATE["users"].keys()])
    while email in existing_emails:
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 999)}@{random.choice(domains)}"

    user_id = str(uuid.uuid4())
    _initial_user_email_to_uuid_map[email] = user_id # Add to map for friend linking in new users


    num_friends = random.randint(0, min(5, len(all_user_uuids)))
    friends_list = random.sample(all_user_uuids, num_friends)
    if random.random() < 0.3 and len(all_user_uuids) > 0:
        potential_friend_email = f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}{random.randint(1000, 9999)}@{random.choice(domains)}"
        if potential_friend_email not in existing_emails:
            friends_list.append(potential_friend_email)

    num_vehicles = random.choices([0, 1, 2, 3], weights=[0.4, 0.4, 0.15, 0.05], k=1)[0]
    user_vehicles = {}
    for v_idx in range(num_vehicles):
        vehicle_tag_base = f"{first.lower()}_{generate_tesla_model().replace(' ', '_').lower()}_{v_idx+1}"
        current_user_vehicle_tags = set(user_vehicles.keys())
        while vehicle_tag_base in current_user_vehicle_tags:
            vehicle_tag_base = f"{first.lower()}_{generate_tesla_model().replace(' ', '_').lower()}_{random.randint(1, 5)}"
        vehicle_id = str(uuid.uuid4())
        _initial_vehicle_tag_to_uuid_map[(user_id, vehicle_tag_base)] = vehicle_id
        media_playing = random.random() < 0.5
        sentry_on = random.random() < 0.3
        num_alerts = random.randint(0, 2) if sentry_on else 0
        current_alerts = random.sample(sentry_alerts, num_alerts) if num_alerts > 0 else []
        user_vehicles[vehicle_id] = {
            "id": vehicle_id,
            "original_vehicle_tag": vehicle_tag_base,
            "vehicle_tag": generate_vin(),
            "horn": False,
            "media": {
                "playing": media_playing,
                "volume": random.randint(20, 90),
                "current_track": random.randint(0, 5) if media_playing else 0,
                "favorites": random.sample(playlist_titles, random.randint(0, min(3, len(playlist_titles))))
            },
            "trunk": {
                "front": random.choice(["open", "closed"]),
                "rear": random.choice(["open", "closed"])
            },
            "charge": {
                "port_open": random.random() < 0.2,
                "charging": random.random() < 0.4,
                "limit": random.choice([70, 80, 90, 100])
            },
            "climate": {
                "on": random.random() < 0.6,
                "bioweapon_mode": random.random() < 0.05,
                "climate_keeper_mode": random.choice(["off", "dog", "camp"]),
                "cop_temp": random.randint(20, 30),
                "driver_temp": random.randint(18, 25)
            },
            "locks": {
                "locked": random.random() < 0.8
            },
            "sentry_mode": {
                "on": sentry_on,
                "alerts": current_alerts
            },
            "lights": {
                "on": random.random() < 0.1
            },
            "doors": {
                "driver_front": random.choice(["open", "closed"]),
                "passenger_front": random.choice(["open", "closed"]),
                "driver_rear": random.choice(["open", "closed"]),
                "passenger_rear": random.choice(["open", "closed"])
            },
            "windows": random.choice(["open", "closed"]),
            "awake": random.random() < 0.7,
            "speed": random.randint(0, 120) if random.random() < 0.5 else 0,
            "location": generate_location(),
            "firmware_version": random.choice(firmware_versions),
            "createdTime": generate_random_iso_timestamp(days_ago_min=365*2, days_ago_max=365*5),
            "modifiedTime": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=60)
        }
    DEFAULT_STATE["users"][user_id] = {
        "id": user_id,
        "first_name": first,
        "last_name": last,
        "email": email,
        "friends": friends_list,
        "tesla_data": {
            "vehicles": user_vehicles
        }
    }
    all_user_uuids.append(user_id)

for user_id, user_data in DEFAULT_STATE["users"].items():
    if "friends" in user_data:
        updated_friends = []
        for friend_identifier in user_data["friends"]:
            if friend_identifier in _initial_user_email_to_uuid_map:
                updated_friends.append(_initial_user_email_to_uuid_map[friend_identifier])
            elif friend_identifier in DEFAULT_STATE["users"]:
                updated_friends.append(friend_identifier)
        user_data["friends"] = list(set(updated_friends))

output_filename = 'diverse_teslafleet_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

total_vehicles = sum(len(user_data.get("tesla_data", {}).get("vehicles", {})) for user_data in DEFAULT_STATE["users"].values())
print(f"Total number of users: {len(DEFAULT_STATE['users'])}")
print(f"Total number of vehicles: {total_vehicles}")
print(f"Generated DEFAULT_STATE saved to '{output_filename}'")