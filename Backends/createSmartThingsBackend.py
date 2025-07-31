
import datetime
import copy
import uuid
import random
import json
from typing import Dict, List, Any, Optional, Union, Literal

current_time_edt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=4)

_user_email_to_uuid_map = {}
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

output_filename = 'diverse_smartthings_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

# Optionally, print a sample user's data for review
# if DEFAULT_STATE["users"]:
#     sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(0, len(DEFAULT_STATE["users"]) - 1)]
#     print(f"\nSample data for user {DEFAULT_STATE['users'][sample_user_id]['first_name']} {DEFAULT_STATE['users'][sample_user_id]['last_name']}:")
#     print(json.dumps(DEFAULT_STATE["users"][sample_user_id], indent=2))