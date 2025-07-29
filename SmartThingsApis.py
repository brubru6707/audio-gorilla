import datetime
import copy
import uuid
import random
import json
from typing import Dict, List, Any, Optional, Union, Literal

# Current time for realistic date generation (EDT offset)
current_time_edt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=4)

_user_email_to_uuid_map = {}
# These will be populated during user creation to hold the *current user's* generated UUIDs
# for location and room names, so devices can reference them.
_current_user_location_name_to_uuid_map: Dict[str, str] = {}
_current_user_room_name_to_uuid_map: Dict[str, str] = {}

def generate_random_email(first_name, last_name):
    domains = ["example.com", "smarthome.net", "iotlife.org", "homecontrol.co", "connectedsystems.app"]
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"

def generate_random_coords():
    """Generates realistic latitude/longitude for a US-based location."""
    latitude = random.uniform(25.0, 49.0)  # Roughly US range
    longitude = random.uniform(-125.0, -65.0) # Roughly US range
    return round(latitude, 4), round(longitude, 4)

def generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365):
    """Generates a random ISO 8601 formatted datetime string (with Z for UTC) in the past relative to current_time_edt."""
    delta = datetime.timedelta(days=random.randint(days_ago_min, days_ago_max), 
                               hours=random.randint(0, 23), 
                               minutes=random.randint(0, 59), 
                               seconds=random.randint(0, 59))
    # Convert current_time_edt to UTC for consistent Z suffix
    dt = current_time_edt.astimezone(datetime.timezone.utc) - delta
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z')


def _create_user_data(email: str, first_name: str, last_name: str, smartthings_data: Dict[str, Any]):
    user_id = str(uuid.uuid4())
    _user_email_to_uuid_map[email] = user_id

    # Clear maps for the new user to avoid cross-user ID issues
    _current_user_location_name_to_uuid_map.clear()
    _current_user_room_name_to_uuid_map.clear()

    processed_smartthings_data = copy.deepcopy(smartthings_data)

    if "profile" not in processed_smartthings_data:
        processed_smartthings_data["profile"] = {}
    processed_smartthings_data["profile"]["emailAddress"] = email
    
    # Ensure account_id is set
    if "account_id" not in processed_smartthings_data["profile"]:
        processed_smartthings_data["profile"]["account_id"] = f"acc-{user_id[:8]}"
    
    # Ensure subscriptions is a list
    if "subscriptions" not in processed_smartthings_data["profile"] or not isinstance(processed_smartthings_data["profile"]["subscriptions"], list):
        processed_smartthings_data["profile"]["subscriptions"] = [random.choice(["Free Tier", "Basic Plan", "Premium Plan"])]
    
    if "locale" not in processed_smartthings_data["profile"]:
        processed_smartthings_data["profile"]["locale"] = random.choice(["en-US", "es-MX", "fr-CA", "en-GB"])
    if "country_code" not in processed_smartthings_data["profile"]:
        processed_smartthings_data["profile"]["country_code"] = random.choice(["US", "CA", "GB", "MX"])
    if "timezone" not in processed_smartthings_data["profile"]:
        processed_smartthings_data["profile"]["timezone"] = random.choice(["America/New_York", "America/Los_Angeles", "America/Chicago", "Europe/London", "Asia/Tokyo"])


    new_locations = {}
    for old_loc_name, loc_data in smartthings_data.get("locations", {}).items():
        loc_id = str(uuid.uuid4())
        _current_user_location_name_to_uuid_map[old_loc_name] = loc_id
        loc_data_copy = copy.deepcopy(loc_data) # Use copy to avoid modifying original
        loc_data_copy["id"] = loc_id
        new_locations[loc_id] = loc_data_copy
    processed_smartthings_data["locations"] = new_locations

    new_rooms = {}
    for old_room_name, room_data in smartthings_data.get("rooms", {}).items():
        room_id = str(uuid.uuid4())
        _current_user_room_name_to_uuid_map[old_room_name] = room_id
        room_data_copy = copy.deepcopy(room_data) # Use copy

        room_data_copy["id"] = room_id
        
        # Link room to location UUID
        if "location_name" in room_data_copy and room_data_copy["location_name"] in _current_user_location_name_to_uuid_map:
            room_data_copy["location_id"] = _current_user_location_name_to_uuid_map[room_data_copy["location_name"]]
            del room_data_copy["location_name"] # Remove the temporary name key
        elif "location_id" not in room_data_copy: # Fallback if location_name isn't present or mapped
            # Assign to a random existing location for the current user, or generate one if none exist
            if new_locations:
                room_data_copy["location_id"] = random.choice(list(new_locations.keys()))
            else:
                # This case shouldn't happen if locations are always generated before rooms
                # But as a failsafe:
                default_loc_id = str(uuid.uuid4())
                new_locations[default_loc_id] = {"id": default_loc_id, "name": "Default Home", "address": "N/A", "latitude": 0, "longitude": 0}
                room_data_copy["location_id"] = default_loc_id


        new_rooms[room_id] = room_data_copy
    processed_smartthings_data["rooms"] = new_rooms

    new_devices = {}
    max_activity_time = generate_random_iso_timestamp(days_ago_min=1, days_ago_max=7) # Default if no devices
    
    for old_device_id, device_data in smartthings_data.get("devices", {}).items():
        new_device_id = str(uuid.uuid4())
        device_data_copy = copy.deepcopy(device_data) # Use copy

        device_data_copy["id"] = new_device_id
        
        # Set creation and activity times
        creation_time_str = generate_random_iso_timestamp(days_ago_min=30, days_ago_max=365) # 1 month to 1 year ago
        last_activity_time_str = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=min(30, (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(creation_time_str.replace('Z', '+00:00'))).days + 1)) # Up to 30 days after creation
        
        # Ensure activity time is after creation time
        created_dt_obj = datetime.datetime.fromisoformat(creation_time_str.replace('Z', '+00:00'))
        activity_dt_obj = datetime.datetime.fromisoformat(last_activity_time_str.replace('Z', '+00:00'))
        if activity_dt_obj < created_dt_obj:
            activity_dt_obj = created_dt_obj + datetime.timedelta(minutes=random.randint(5, 60*24*7)) # At least 5 mins later, up to 7 days
            last_activity_time_str = activity_dt_obj.isoformat(timespec='seconds').replace('+00:00', 'Z')


        device_data_copy["creation_time"] = creation_time_str
        device_data_copy["last_activity_time"] = last_activity_time_str

        # Update max_activity_time for user's top-level field
        if datetime.datetime.fromisoformat(last_activity_time_str.replace('Z', '+00:00')) > datetime.datetime.fromisoformat(max_activity_time.replace('Z', '+00:00')):
            max_activity_time = last_activity_time_str

        # Link device to location UUID
        if "location" in device_data_copy and device_data_copy["location"] in _current_user_location_name_to_uuid_map:
            device_data_copy["location"] = _current_user_location_name_to_uuid_map[device_data_copy["location"]]
        elif "location" not in device_data_copy and new_locations: # If no location specified, assign to a random one
            device_data_copy["location"] = random.choice(list(new_locations.keys()))

        # Link device to room UUID
        if "room" in device_data_copy and device_data_copy["room"] in _current_user_room_name_to_uuid_map:
            device_data_copy["room"] = _current_user_room_name_to_uuid_map[device_data_copy["room"]]
        elif "room" not in device_data_copy and new_rooms: # If no room specified, assign to a random one
             device_data_copy["room"] = random.choice(list(new_rooms.keys()))

        # Add default status if missing
        if "status" not in device_data_copy:
            device_data_copy["status"] = random.choice(["online", "offline"])
        
        # Add new fields for devices
        if "powerSource" not in device_data_copy:
            device_data_copy["powerSource"] = random.choice(["battery", "mains", "solar"])
        if "healthStatus" not in device_data_copy:
            device_data_copy["healthStatus"] = random.choice(["healthy", "degraded", "error"])
        if "manufacturer" not in device_data_copy:
            device_data_copy["manufacturer"] = random.choice(["SmartCorp", "HomeLink", "EvoTech", "ZenithIoT"])
        if "model" not in device_data_copy:
            device_data_copy["model"] = f"{device_data_copy.get('type', 'Device')}-{random.randint(100,999)}"
        if "firmwareVersion" not in device_data_copy:
            device_data_copy["firmwareVersion"] = f"v{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}"
        if "label" not in device_data_copy:
            device_data_copy["label"] = device_data_copy.get("name", "Unknown Device")
        if "device_online_status_last_checked" not in device_data_copy: # New field
             device_data_copy["device_online_status_last_checked"] = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=1) # checked recently
        

        new_devices[new_device_id] = device_data_copy
    processed_smartthings_data["devices"] = new_devices

    # Consolidate global capabilities list based on all devices' capabilities
    all_capabilities = set()
    for device_data in new_devices.values():
        for cap in device_data.get("capabilities", []):
            all_capabilities.add(cap)
    
    # Transform to list of dicts with status
    processed_smartthings_data["capabilities"] = [{"id": cap_id, "version": 1, "status": "active"} for cap_id in sorted(list(all_capabilities))]

    return user_id, {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "smartthings_data": processed_smartthings_data,
        "total_locations_count": len(new_locations), # New field
        "total_rooms_count": len(new_rooms), # New field
        "total_devices_count": len(new_devices), # New field
        "last_device_activity": max_activity_time # New field: latest activity time among all devices
    }

# --- Initial Users Data ---
users_initial_data = [
    ("alice.smith@gmail.com", "Alice", "Smith", {
        "profile": {
            "emailAddress": "alice.smith@gmail.com", # Will be overwritten by _create_user_data
            "account_id": "acc-alice-123",
            "subscriptions": ["Premium Plan"],
            "locale": "en-US",
            "country_code": "US",
            "timezone": "America/New_York",
            "last_login_time": (current_time_edt - datetime.timedelta(hours=2)).isoformat(timespec='seconds').replace('+00:00', 'Z') # New field
        },
        "locations": {
            "Home": {"name": "Home", "address": "123 Main St, Anytown, USA", "latitude": 34.0522, "longitude": -118.2437, "status": "active"}, # New status field
            "Office": {"name": "Office", "address": "456 Business Rd, Bigcity, USA", "latitude": 34.0522, "longitude": -118.2437, "status": "active"}
        },
        "rooms": {
            "Living Room": {"name": "Living Room", "location_name": "Home"},
            "Kitchen": {"name": "Kitchen", "location_name": "Home"},
            "Bedroom": {"name": "Bedroom", "location_name": "Home"}, # Added
            "Office Room": {"name": "Office Room", "location_name": "Office"}
        },
        "devices": {
            "device1": { # This ID will be replaced by UUID
                "id": "device1",
                "name": "Living Room Lamp",
                "type": "light", # New field
                "location": "Home",
                "room": "Living Room",
                "status": "online",
                "components": {
                    "main": {
                        "switch": {"switch": "on"},
                        "level": {"level": 75},
                        "colorTemperature": {"colorTemperature": 2700} # Added
                    }
                },
                "capabilities": ["switch", "level", "colorTemperature"],
                "last_event_value": "on", # New field
                "last_event_time": (current_time_edt - datetime.timedelta(minutes=10)).isoformat(timespec='seconds').replace('+00:00', 'Z') # New field
            },
            "device2": {
                "id": "device2",
                "name": "Front Door Smart Lock",
                "type": "lock",
                "location": "Home",
                "room": "Living Room",
                "status": "online",
                "components": {
                    "main": {
                        "lock": {"lock": "locked"},
                        "battery": {"battery": 85} # Added
                    }
                },
                "capabilities": ["lock", "battery"],
                 "last_event_value": "locked",
                "last_event_time": (current_time_edt - datetime.timedelta(minutes=30)).isoformat(timespec='seconds').replace('+00:00', 'Z')
            },
            "device3": {
                "id": "device3",
                "name": "Office Thermostat",
                "type": "thermostat",
                "location": "Office",
                "room": "Office Room",
                "status": "online",
                "components": {
                    "main": {
                        "temperatureMeasurement": {"temperature": 22},
                        "thermostatMode": {"thermostatMode": "cool"},
                        "thermostatFanMode": {"thermostatFanMode": "auto"} # Added
                    }
                },
                "capabilities": ["temperatureMeasurement", "thermostatMode", "thermostatFanMode"],
                 "last_event_value": "22",
                "last_event_time": (current_time_edt - datetime.timedelta(hours=1)).isoformat(timespec='seconds').replace('+00:00', 'Z')
            },
             "device4": { # New Device: Motion Sensor
                "id": "device4",
                "name": "Hallway Motion Sensor",
                "type": "sensor",
                "location": "Home",
                "room": "Living Room",
                "status": "online",
                "components": {
                    "main": {
                        "motionSensor": {"motion": "active"},
                        "battery": {"battery": 70}
                    }
                },
                "capabilities": ["motionSensor", "battery"],
                "last_event_value": "active",
                "last_event_time": (current_time_edt - datetime.timedelta(minutes=5)).isoformat(timespec='seconds').replace('+00:00', 'Z')
            }
        },
        "capabilities": [ # This list will be dynamically rebuilt by _create_user_data based on devices
            {"id": "switch", "version": 1, "status": "active"}
        ]
    })
]

DEFAULT_STATE: Dict[str, Any] = {
    "users": {},
}

for email, first_name, last_name, smartthings_data in users_initial_data:
    user_id, user_data = _create_user_data(email, first_name, last_name, smartthings_data)
    DEFAULT_STATE["users"][user_id] = user_data

# --- Generate 49 more diverse and realistic users ---
first_names = ["Sophia", "Liam", "Olivia", "Noah", "Ava", "Jackson", "Isabella", "Aiden", "Mia", "Lucas", "Harper", "Ethan", "Evelyn", "Mason", "Abigail", "Caleb", "Charlotte", "Logan", "Amelia", "Michael", "Ella", "Jacob", "Aria", "Daniel", "Chloe", "Samuel", "Grace", "David", "Victoria", "Joseph", "Penelope", "Matthew", "Riley", "Benjamin", "Layla", "Andrew", "Lily", "Gabriel", "Natalie", "Christopher", "Hannah", "James", "Zoe", "Ryan", "Scarlett", "Nathan", "Addison", "Christian", "Aubrey", "Joshua"]
last_names = ["Chen", "Kim", "Singh", "Lopez", "Garcia", "Nguyen", "Davis", "Jackson", "Harris", "White", "Moore", "Clark", "Lewis", "Baker", "Adams", "Hill", "Nelson", "Carter", "Mitchell", "Roberts", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders"]
email_domains = ["smart-home.com", "iotcentral.net", "connected-living.org", "automata.co", "techtopia.app"]
location_names = ["Main Home", "Summer House", "Small Apartment", "Cabin Getaway", "Urban Loft", "Vacation Rental"]
room_names = ["Living Room", "Kitchen", "Bedroom", "Bathroom", "Hallway", "Garage", "Dining Room", "Kids Room", "Guest Room", "Patio", "Office"]
device_types = ["light", "thermostat", "lock", "motionSensor", "contactSensor", "camera", "smartPlug", "speaker", "waterLeakSensor", "garageDoorOpener", "fan"]
device_capabilities_map = {
    "light": ["switch", "level", "colorTemperature", "colorControl"],
    "thermostat": ["temperatureMeasurement", "thermostatMode", "thermostatFanMode", "relativeHumidityMeasurement"],
    "lock": ["lock", "battery"],
    "motionSensor": ["motionSensor", "battery"],
    "contactSensor": ["contactSensor", "battery"],
    "camera": ["imageCapture", "motionSensor"],
    "smartPlug": ["switch", "powerMeter"],
    "speaker": ["audioVolume", "mediaPlayback"],
    "waterLeakSensor": ["waterSensor", "battery"],
    "garageDoorOpener": ["garageDoorControl", "contactSensor"],
    "fan": ["switch", "fanSpeed"]
}
device_statuses = ["online", "offline"]
health_statuses = ["healthy", "degraded", "error"]
power_sources = ["battery", "mains", "solar"]
manufacturers = ["SmartCorp", "HomeLink", "EvoTech", "ZenithIoT", "AquaSmart", "BrightFuture", "SecureHome"]
locales = ["en-US", "es-MX", "fr-CA", "en-GB", "de-DE", "ja-JP"]
country_codes = ["US", "CA", "GB", "MX", "DE", "JP"]
timezones = ["America/New_York", "America/Los_Angeles", "America/Chicago", "Europe/London", "Asia/Tokyo", "Europe/Berlin", "Australia/Sydney"]
subscription_plans = ["Free Tier", "Basic Plan", "Premium Plan", "Family Plan", "Business Tier"]


for i in range(49): # Generate 49 additional users (1 existing + 49 new = 50 total)
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = generate_random_email(first, last)
    
    # Ensure unique email
    while email in _user_email_to_uuid_map:
        email = generate_random_email(first, last)

    user_smartthings_data = {
        "profile": {
            "emailAddress": email,
            "account_id": f"acc-{uuid.uuid4().hex[:8]}",
            "subscriptions": [random.choice(subscription_plans)],
            "locale": random.choice(locales),
            "country_code": random.choice(country_codes),
            "timezone": random.choice(timezones),
            "last_login_time": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=7) # last 7 days
        },
        "locations": {},
        "rooms": {},
        "devices": {}
    }

    # Generate locations for the user
    num_locations = random.randint(1, 3)
    current_user_location_temp_ids = []
    for loc_idx in range(num_locations):
        loc_name_temp = random.choice(location_names)
        # Ensure unique location name for the current user
        while loc_name_temp in user_smartthings_data["locations"]:
             loc_name_temp = random.choice(location_names) + f" {random.randint(1,99)}"

        lat, lon = generate_random_coords()
        user_smartthings_data["locations"][loc_name_temp] = {
            "name": loc_name_temp,
            "address": f"{random.randint(100, 999)} {random.choice(['Oak', 'Maple', 'Pine'])} St, {random.choice(['Springfield', 'Rivertown'])}",
            "latitude": lat,
            "longitude": lon,
            "status": random.choice(["active", "inactive"]) # Location status
        }
        current_user_location_temp_ids.append(loc_name_temp)

    # Generate rooms for each location
    current_user_room_temp_ids = []
    for loc_name in current_user_location_temp_ids:
        num_rooms = random.randint(2, 8)
        for room_idx in range(num_rooms):
            room_name_temp = random.choice(room_names)
            # Ensure unique room name within the current user's rooms
            while room_name_temp in user_smartthings_data["rooms"]:
                 room_name_temp = random.choice(room_names) + f" {random.randint(1,99)}"

            user_smartthings_data["rooms"][room_name_temp] = {
                "name": room_name_temp,
                "location_name": loc_name # Link by name for _create_user_data to resolve
            }
            current_user_room_temp_ids.append(room_name_temp)
    
    # Generate devices for each user
    num_devices = random.randint(5, 30)
    for dev_idx in range(num_devices):
        device_type = random.choice(device_types)
        device_caps = device_capabilities_map.get(device_type, ["switch"]) # Default to switch if type not in map
        
        # Select random location and room, ensuring they exist for the user
        device_location_name = random.choice(current_user_location_temp_ids)
        
        # Filter rooms to only those belonging to the selected location
        possible_rooms_for_location = [
            r_name for r_name, r_data in user_smartthings_data["rooms"].items() 
            if r_data["location_name"] == device_location_name
        ]
        device_room_name = random.choice(possible_rooms_for_location) if possible_rooms_for_location else random.choice(current_user_room_temp_ids) # Fallback

        device_name = f"{random.choice(['Smart', 'Connected', 'Home'])} {device_type.capitalize()} {random.randint(1, 99)}"
        
        # Construct components based on capabilities
        components = {"main": {}}
        last_event_value = None
        for cap in device_caps:
            if cap == "switch":
                switch_state = random.choice(["on", "off"])
                components["main"]["switch"] = {"switch": switch_state}
                last_event_value = switch_state
            elif cap == "level":
                level_val = random.randint(0, 100)
                components["main"]["level"] = {"level": level_val}
                if last_event_value is None: last_event_value = str(level_val)
            elif cap == "colorTemperature":
                temp_val = random.choice([2700, 3000, 4000, 5000, 6500])
                components["main"]["colorTemperature"] = {"colorTemperature": temp_val}
                if last_event_value is None: last_event_value = str(temp_val)
            elif cap == "colorControl":
                color_hue = random.randint(0, 100)
                color_saturation = random.randint(0, 100)
                components["main"]["colorControl"] = {"hue": color_hue, "saturation": color_saturation}
                if last_event_value is None: last_event_value = f"H:{color_hue} S:{color_saturation}"
            elif cap == "lock":
                lock_state = random.choice(["locked", "unlocked"])
                components["main"]["lock"] = {"lock": lock_state}
                last_event_value = lock_state
            elif cap == "battery":
                batt_level = random.randint(10, 100)
                components["main"]["battery"] = {"battery": batt_level}
                if last_event_value is None: last_event_value = str(batt_level)
            elif cap == "temperatureMeasurement":
                temp_meas_val = round(random.uniform(18.0, 30.0), 1)
                components["main"]["temperatureMeasurement"] = {"temperature": temp_meas_val}
                if last_event_value is None: last_event_value = str(temp_meas_val)
            elif cap == "thermostatMode":
                mode_val = random.choice(["off", "heat", "cool", "auto"])
                components["main"]["thermostatMode"] = {"thermostatMode": mode_val}
                if last_event_value is None: last_event_value = mode_val
            elif cap == "thermostatFanMode":
                fan_mode_val = random.choice(["auto", "on"])
                components["main"]["thermostatFanMode"] = {"thermostatFanMode": fan_mode_val}
                if last_event_value is None: last_event_value = fan_mode_val
            elif cap == "motionSensor":
                motion_state = random.choice(["active", "inactive"])
                components["main"]["motionSensor"] = {"motion": motion_state}
                last_event_value = motion_state
            elif cap == "contactSensor":
                contact_state = random.choice(["open", "closed"])
                components["main"]["contactSensor"] = {"contact": contact_state}
                last_event_value = contact_state
            elif cap == "imageCapture":
                # No state to set for imageCapture directly
                pass
            elif cap == "powerMeter":
                power_val = round(random.uniform(0.1, 100.0), 2)
                components["main"]["powerMeter"] = {"power": power_val}
                if last_event_value is None: last_event_value = str(power_val)
            elif cap == "audioVolume":
                vol_val = random.randint(0, 100)
                components["main"]["audioVolume"] = {"volume": vol_val}
                if last_event_value is None: last_event_value = str(vol_val)
            elif cap == "mediaPlayback":
                playback_state = random.choice(["playing", "paused", "stopped"])
                components["main"]["mediaPlayback"] = {"playbackStatus": playback_state}
                if last_event_value is None: last_event_value = playback_state
            elif cap == "waterSensor":
                water_state = random.choice(["dry", "wet"])
                components["main"]["waterSensor"] = {"water": water_state}
                if last_event_value is None: last_event_value = water_state
            elif cap == "garageDoorControl":
                door_state = random.choice(["open", "closed"])
                components["main"]["garageDoorControl"] = {"door": door_state}
                if last_event_value is None: last_event_value = door_state
            elif cap == "fanSpeed":
                speed_val = random.choice(["low", "medium", "high", "off"])
                components["main"]["fanSpeed"] = {"fanSpeed": speed_val}
                if last_event_value is None: last_event_value = speed_val

        user_smartthings_data["devices"][f"temp_device_{dev_idx}"] = { # Temp ID for resolution by _create_user_data
            "id": f"temp_device_{dev_idx}",
            "name": device_name,
            "type": device_type,
            "location": device_location_name, # Name for resolution
            "room": device_room_name, # Name for resolution
            "status": random.choice(device_statuses),
            "components": components,
            "capabilities": device_caps,
            "powerSource": random.choice(power_sources),
            "healthStatus": random.choice(health_statuses),
            "manufacturer": random.choice(manufacturers),
            "model": f"{device_type.capitalize()}-{random.randint(100, 999)}",
            "firmwareVersion": f"v{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}",
            "label": device_name,
            "last_event_value": last_event_value,
            "last_event_time": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=3), # last 3 days
            "device_online_status_last_checked": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=1) # checked recently
        }

    user_id, user_data = _create_user_data(email, first, last, user_smartthings_data)
    DEFAULT_STATE["users"][user_id] = user_data


# --- Output the generated DEFAULT_STATE ---
import json

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")

# Save the generated DEFAULT_STATE to a JSON file
# output_filename = 'diverse_smartthings_state.json'
# with open(output_filename, 'w') as f:
#     json.dump(DEFAULT_STATE, f, indent=2)

# print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

# Optionally, print a sample user's data for review
# if DEFAULT_STATE["users"]:
#     sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(0, len(DEFAULT_STATE["users"]) - 1)]
#     print(f"\nSample data for user {DEFAULT_STATE['users'][sample_user_id]['first_name']} {DEFAULT_STATE['users'][sample_user_id]['last_name']}:")
#     print(json.dumps(DEFAULT_STATE["users"][sample_user_id], indent=2))

class SmartThingsApis:
    """
    A dummy API class for simulating SmartThings operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the SmartThingsApis instance, setting up the in-memory
        data stores and loading the default scenario.
        """
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the SmartThings API, which provides core functionality for managing smart home devices, locations, and rooms."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain a "users" key.
        """
        
        DEFAULT_STATE_COPY = copy.deepcopy(scenario)
        self.users = DEFAULT_STATE_COPY.get("users", {})
        print("SmartThingsApis: Loaded scenario with users, devices, locations, and rooms (all with UUIDs).")

    def _generate_id(self) -> str:
        """
        Generates a unique UUID for dummy entities (devices, locations, rooms).
        """
        return str(uuid.uuid4())

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """Helper to get user_id (UUID) from email (string)."""
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """Helper to get user email (string) from user_id (UUID)."""
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _get_user_smartthings_data(self, user_id: str) -> Optional[Dict]:
        """Helper to get a user's SmartThings data."""
        internal_user_id = self._get_user_id_by_email(user_id) if user_id != 'me' else self._get_user_id_by_email("alice.smith@gmail.com") 
        if not internal_user_id:
            return None
        return self.users.get(internal_user_id, {}).get("smartthings_data")

    def _get_user_devices_data(self, user_id: str) -> Optional[Dict]:
        """Helper to get a user's devices data."""
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("devices") if smartthings_data else None

    def _get_user_locations_data(self, user_id: str) -> Optional[Dict]:
        """Helper to get a user's locations data."""
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("locations") if smartthings_data else None

    def _get_user_rooms_data(self, user_id: str) -> Optional[Dict]:
        """Helper to get a user's rooms data."""
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("rooms") if smartthings_data else None

    def _get_user_capabilities_data(self, user_id: str) -> Optional[List[Dict]]:
        """Helper to get a user's capabilities data."""
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("capabilities") if smartthings_data else None


    def get_user_profile(self, user_id: str = 'me') -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves the profile information for the authenticated SmartThings user.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict: A dictionary containing 'status' (bool) and 'profile' (Dict) if successful.
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        if smartthings_data and "profile" in smartthings_data:
            return {"status": True, "profile": copy.deepcopy(smartthings_data["profile"])}
        return {"status": False, "profile": {}}

    def list_devices(self, user_id: str = 'me') -> List[Dict[str, Any]]:
        """
        List all devices for a user.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            List[Dict[str, Any]]: List of all devices.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return []
        return [copy.deepcopy(d) for d in user_devices.values()]

    def get_device(self, device_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Get a specific device for a user.

        Args:
            device_id (str): ID of the device.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Details of the device.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"error": f"User with ID {user_id} not found or has no devices."}
        
        device = user_devices.get(device_id)
        if device:
            return copy.deepcopy(device)
        return {"error": f"Device {device_id} not found."}

    def create_device(
        self,
        name: str,
        user_id: str = 'me',
        location_name: Optional[str] = None, 
        room_name: Optional[str] = None, 
        capabilities: Optional[List[str]] = None,
        initial_status: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a new device for a user.

        Args:
            name (str): The name of the new device.
            user_id (str): User's email address or 'me' for the authenticated user.
            location_name (Optional[str]): The name of the location for the device. If not found, a new one will be created.
            room_name (Optional[str]): The name of the room for the device. If not found, a new one will be created.
            capabilities (Optional[List[str]]): List of capabilities the device supports (e.g., ["switch", "level"]).
            initial_status (Optional[Dict]): Initial state of device components and capabilities.

        Returns:
            Dict[str, Any]: Details of the created device.
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        if smartthings_data is None:
            return {"error": f"User with ID {user_id} not found or has no SmartThings data."}

        devices = smartthings_data.get("devices", {})
        locations = smartthings_data.get("locations", {})
        rooms = smartthings_data.get("rooms", {})

        
        location_id = None
        if location_name:
            for loc_uuid, loc_data in locations.items():
                if loc_data.get("name") == location_name:
                    location_id = loc_uuid
                    break
            if not location_id:
                location_id = self._generate_id()
                locations[location_id] = {"id": location_id, "name": location_name, "address": "Unspecified"}
                print(f"Created new location: {location_name} with ID {location_id}")

        
        room_id = None
        if room_name:
            for r_uuid, r_data in rooms.items():
                if r_data.get("name") == room_name and (not location_id or r_data.get("location_id") == location_id):
                    room_id = r_uuid
                    break
            if not room_id:
                room_id = self._generate_id()
                new_room_data = {"id": room_id, "name": room_name}
                if location_id:
                    new_room_data["location_id"] = location_id
                rooms[room_id] = new_room_data
                print(f"Created new room: {room_name} with ID {room_id}")

        new_device_id = self._generate_id()
        current_time_iso = datetime.datetime.now().isoformat() + "Z"

        new_device = {
            "id": new_device_id,
            "name": name,
            "status": "online", 
            "location": location_id,
            "room": room_id,
            "components": initial_status if initial_status is not None else {"main": {}},
            "capabilities": capabilities if capabilities is not None else [],
            "creation_time": current_time_iso,
            "last_activity_time": current_time_iso
        }
        devices[new_device_id] = new_device
        
        return {"status": "success", "device": copy.deepcopy(new_device)}

    def update_device_status(
        self,
        device_id: str,
        component_id: str,
        capability_id: str,
        command: str,
        args: Optional[List[Any]] = None,
        user_id: str = 'me'
    ) -> Dict[str, Any]:
        """
        Update the status of a specific device's capability.

        Args:
            device_id (str): ID of the device to update.
            component_id (str): ID of the component (e.g., 'main').
            capability_id (str): ID of the capability (e.g., 'switch').
            command (str): Command to send (e.g., 'on', 'off', 'setLevel').
            args (Optional[List[Any]]): Arguments for the command (e.g., [75] for setLevel).
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: The updated device status or an error message.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"error": f"User with ID {user_id} not found or has no devices."}

        device = user_devices.get(device_id)
        if not device:
            return {"error": f"Device {device_id} not found."}

        
        if component_id in device["components"] and capability_id in device["components"][component_id]:
            if capability_id == "switch":
                if command == "on":
                    device["components"][component_id]["switch"]["switch"] = "on"
                elif command == "off":
                    device["components"][component_id]["switch"]["switch"] = "off"
                else:
                    return {"error": f"Invalid command '{command}' for switch capability."}
            elif capability_id == "level":
                if command == "setLevel" and args and isinstance(args[0], (int, float)):
                    device["components"][component_id]["level"]["level"] = args[0]
                else:
                    return {"error": f"Invalid command or arguments for level capability."}
            elif capability_id == "lock":
                if command == "lock":
                    device["components"][component_id]["lock"]["lock"] = "locked"
                elif command == "unlock":
                    device["components"][component_id]["lock"]["lock"] = "unlocked"
                else:
                    return {"error": f"Invalid command '{command}' for lock capability."}
            elif capability_id == "thermostatMode":
                if command in ["cool", "heat", "auto", "off"]:
                    device["components"][component_id]["thermostatMode"]["thermostatMode"] = command
                else:
                    return {"error": f"Invalid command '{command}' for thermostatMode capability."}
            elif capability_id == "temperatureMeasurement":
                
                if command == "setTemperature" and args and isinstance(args[0], (int, float)):
                     device["components"][component_id]["temperatureMeasurement"]["temperature"] = args[0]
                else:
                    return {"error": f"Temperature measurement is usually read-only. Command '{command}' not supported."}

            device["last_activity_time"] = datetime.datetime.now().isoformat() + "Z"
            return {"status": "success", "device_status": copy.deepcopy(device["components"][component_id])}
        
        return {"error": f"Component '{component_id}' or capability '{capability_id}' not found for device '{device_id}'."}

    def delete_device(self, device_id: str, user_id: str = 'me') -> Dict[str, bool]:
        """
        Delete a device.

        Args:
            device_id (str): ID of the device to delete.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, bool]: True if the device was deleted successfully, False otherwise.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"status": False}

        if device_id in user_devices:
            del user_devices[device_id]
            print(f"Device '{device_id}' deleted for {user_id}")
            return {"status": True}
        return {"status": False}

    def get_device_status(
        self,
        device_id: str,
        component_id: str = "main",
        capability_id: Optional[str] = None,
        user_id: str = 'me'
    ) -> Dict[str, Any]:
        """
        Get the current status of a device or a specific capability.

        Args:
            device_id (str): ID of the device.
            component_id (str): ID of the component (e.g., 'main').
            capability_id (Optional[str]): ID of the capability (e.g., 'switch', 'level'). If None, returns all component status.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: The status of the device/capability or an error message.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"error": f"User with ID {user_id} not found or has no devices."}

        device = user_devices.get(device_id)
        if not device:
            return {"error": f"Device {device_id} not found."}

        if component_id not in device["components"]:
            return {"error": f"Component '{component_id}' not found for device '{device_id}'."}

        component_status = device["components"][component_id]

        if capability_id:
            if capability_id in component_status:
                return {"status": "success", "capability_status": copy.deepcopy(component_status[capability_id])}
            return {"error": f"Capability '{capability_id}' not found for component '{component_id}' of device '{device_id}'."}
        
        return {"status": "success", "component_status": copy.deepcopy(component_status)}

    def list_locations(self, user_id: str = 'me') -> List[Dict[str, Any]]:
        """
        List all locations for a user.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            List[Dict[str, Any]]: List of all locations.
        """
        user_locations = self._get_user_locations_data(user_id)
        if user_locations is None:
            return []
        return [copy.deepcopy(loc) for loc in user_locations.values()]

    def get_location(self, location_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Get a specific location for a user.

        Args:
            location_id (str): ID of the location.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Details of the location.
        """
        user_locations = self._get_user_locations_data(user_id)
        if user_locations is None:
            return {"error": f"User with ID {user_id} not found or has no locations."}
        
        location = user_locations.get(location_id)
        if location:
            return copy.deepcopy(location)
        return {"error": f"Location {location_id} not found."}

    def create_location(
        self,
        name: str,
        user_id: str = 'me',
        address: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a new location for a user.

        Args:
            name (str): The name of the new location.
            user_id (str): User's email address or 'me' for the authenticated user.
            address (Optional[str]): The address of the location.
            latitude (Optional[float]): The latitude of the location.
            longitude (Optional[float]): The longitude of the location.

        Returns:
            Dict[str, Any]: Details of the created location.
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        if smartthings_data is None:
            return {"error": f"User with ID {user_id} not found or has no SmartThings data."}
        
        locations = smartthings_data.get("locations", {})
        
        
        for loc_id, loc_data in locations.items():
            if loc_data.get("name") == name:
                return {"error": f"Location with name '{name}' already exists."}

        new_location_id = self._generate_id()
        new_location = {
            "id": new_location_id,
            "name": name,
            "address": address,
            "latitude": latitude,
            "longitude": longitude
        }
        locations[new_location_id] = new_location
        return {"status": "success", "location": copy.deepcopy(new_location)}

    def update_location(
        self,
        location_id: str,
        user_id: str = 'me',
        name: Optional[str] = None,
        address: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Update an existing location for a user.

        Args:
            location_id (str): ID of the location to update.
            user_id (str): User's email address or 'me' for the authenticated user.
            name (Optional[str]): New name for the location.
            address (Optional[str]): New address for the location.
            latitude (Optional[float]): New latitude for the location.
            longitude (Optional[float]): New longitude for the location.

        Returns:
            Dict[str, Any]: Details of the updated location.
        """
        user_locations = self._get_user_locations_data(user_id)
        if user_locations is None:
            return {"error": f"User with ID {user_id} not found or has no locations."}
        
        location = user_locations.get(location_id)
        if not location:
            return {"error": f"Location {location_id} not found."}

        if name:
            location["name"] = name
        if address:
            location["address"] = address
        if latitude is not None:
            location["latitude"] = latitude
        if longitude is not None:
            location["longitude"] = longitude
        
        return {"status": "success", "location": copy.deepcopy(location)}

    def delete_location(self, location_id: str, user_id: str = 'me') -> Dict[str, bool]:
        """
        Delete a location.

        Args:
            location_id (str): ID of the location to delete.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, bool]: True if the location was deleted successfully, False otherwise.
        """
        user_locations = self._get_user_locations_data(user_id)
        if user_locations is None:
            return {"status": False}

        if location_id in user_locations:
            
            user_rooms = self._get_user_rooms_data(user_id)
            if user_rooms:
                rooms_to_delete = [room_id for room_id, room_data in user_rooms.items() if room_data.get("location_id") == location_id]
                for room_id in rooms_to_delete:
                    del user_rooms[room_id]

            user_devices = self._get_user_devices_data(user_id)
            if user_devices:
                devices_to_delete = [device_id for device_id, device_data in user_devices.items() if device_data.get("location") == location_id]
                for device_id in devices_to_delete:
                    del user_devices[device_id]

            del user_locations[location_id]
            print(f"Location '{location_id}' deleted for {user_id}")
            return {"status": True}
        return {"status": False}

    def list_rooms(self, user_id: str = 'me', location_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all rooms for a user, optionally filtered by location.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.
            location_id (Optional[str]): Filter rooms by this location ID.
        Returns:
            List[Dict[str, Any]]: List of all rooms.
        """
        user_rooms = self._get_user_rooms_data(user_id)
        if user_rooms is None:
            return []
        
        filtered_rooms = []
        for room_id, room_data in user_rooms.items():
            if location_id is None or room_data.get("location_id") == location_id:
                filtered_rooms.append(copy.deepcopy(room_data))
        return filtered_rooms

    def get_room(self, room_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Get a specific room for a user.

        Args:
            room_id (str): ID of the room.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Details of the room.
        """
        user_rooms = self._get_user_rooms_data(user_id)
        if user_rooms is None:
            return {"error": f"User with ID {user_id} not found or has no rooms."}
        
        room = user_rooms.get(room_id)
        if room:
            return copy.deepcopy(room)
        return {"error": f"Room {room_id} not found."}

    def create_room(
        self,
        name: str,
        user_id: str = 'me',
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new room for a user.

        Args:
            name (str): The name of the new room.
            user_id (str): User's email address or 'me' for the authenticated user.
            location_id (Optional[str]): The ID of the location this room belongs to.

        Returns:
            Dict[str, Any]: Details of the created room.
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        if smartthings_data is None:
            return {"error": f"User with ID {user_id} not found or has no SmartThings data."}
        
        rooms = smartthings_data.get("rooms", {})
        locations = smartthings_data.get("locations", {})

        
        for r_id, r_data in rooms.items():
            if r_data.get("name") == name and (not location_id or r_data.get("location_id") == location_id):
                return {"error": f"Room with name '{name}' already exists in this location."}

        if location_id and location_id not in locations:
            return {"error": f"Location with ID '{location_id}' not found."}

        new_room_id = self._generate_id()
        new_room = {
            "id": new_room_id,
            "name": name,
            "location_id": location_id
        }
        rooms[new_room_id] = new_room
        return {"status": "success", "room": copy.deepcopy(new_room)}

    def update_room(
        self,
        room_id: str,
        user_id: str = 'me',
        name: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing room for a user.

        Args:
            room_id (str): ID of the room to update.
            user_id (str): User's email address or 'me' for the authenticated user.
            name (Optional[str]): New name for the room.
            location_id (Optional[str]): New location ID for the room.

        Returns:
            Dict[str, Any]: Details of the updated room.
        """
        user_rooms = self._get_user_rooms_data(user_id)
        if user_rooms is None:
            return {"error": f"User with ID {user_id} not found or has no rooms."}
        
        room = user_rooms.get(room_id)
        if not room:
            return {"error": f"Room {room_id} not found."}

        if name:
            room["name"] = name
        if location_id:
            user_locations = self._get_user_locations_data(user_id)
            if user_locations and location_id in user_locations:
                room["location_id"] = location_id
            else:
                return {"error": f"Location with ID '{location_id}' not found."}
        
        return {"status": "success", "room": copy.deepcopy(room)}

    def delete_room(self, room_id: str, user_id: str = 'me') -> Dict[str, bool]:
        """
        Delete a room.

        Args:
            room_id (str): ID of the room to delete.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, bool]: True if the room was deleted successfully, False otherwise.
        """
        user_rooms = self._get_user_rooms_data(user_id)
        if user_rooms is None:
            return {"status": False}

        if room_id in user_rooms:
            
            user_devices = self._get_user_devices_data(user_id)
            if user_devices:
                for device_id, device_data in user_devices.items():
                    if device_data.get("room") == room_id:
                        device_data["room"] = None 
            
            del user_rooms[room_id]
            print(f"Room '{room_id}' deleted for {user_id}")
            return {"status": True}
        return {"status": False}

    def list_capabilities(self, user_id: str = 'me') -> List[Dict[str, Any]]:
        """
        List all capabilities for a user.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            List[Dict[str, Any]]: List of all capabilities.
        """
        user_capabilities = self._get_user_capabilities_data(user_id)
        if user_capabilities is None:
            return []
        return copy.deepcopy(user_capabilities)

    def get_capability(
        self,
        capability_id: str,
        version: Optional[int] = None,
        user_id: str = 'me'
    ) -> Dict[str, Any]:
        """
        Get a specific capability for a user.

        Args:
            capability_id (str): ID of the capability.
            version (Optional[int]): Version of the capability.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Details of the capability.
        """
        user_capabilities = self._get_user_capabilities_data(user_id)
        if user_capabilities is None:
            return {"error": f"User with ID {user_id} not found or has no capabilities."}

        for cap in user_capabilities:
            if cap["id"] == capability_id and (version is None or cap.get("version") == version):
                return copy.deepcopy(cap)
        return {"error": f"Capability {capability_id} not found."}


    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        
        global DEFAULT_STATE
        global _user_email_to_uuid_map
        global _location_name_to_uuid_map
        global _room_name_to_uuid_map

        
        _user_email_to_uuid_map = {}
        _location_name_to_uuid_map = {}
        _room_name_to_uuid_map = {}

        
        new_default_state = {"users": {}}
        for email, first_name, last_name, smartthings_data in users_initial_data:
            user_id, user_data = _create_user_data(email, first_name, last_name, smartthings_data)
            new_default_state["users"][user_id] = user_data
        DEFAULT_STATE = new_default_state

        self._load_scenario(DEFAULT_STATE)
        print("SmartThingsApis: All dummy data reset to default state.")
        return {"reset_status": True}