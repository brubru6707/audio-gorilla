import datetime
import copy
import uuid
import random
from typing import Dict, List, Any, Optional, Union, Literal

# Class definitions for type hinting, as per previous files
class EmailStr(str):
    pass

class User:
    def __init__(self, email: EmailStr):
        self.email = email

# Global mappings for initial data conversion from old string IDs/emails/tags to new UUIDs
_initial_user_email_to_uuid_map = {}
_initial_vehicle_tag_to_uuid_map = {} # Map (user_uuid, original_tag_string) to vehicle_uuid


def _convert_initial_data_to_uuids(initial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Converts the initial RAW_DEFAULT_STATE data to use UUIDs for all relevant IDs."""

    converted_data = copy.deepcopy(initial_data)

    # Reset maps for a clean conversion
    global _initial_user_email_to_uuid_map
    global _initial_vehicle_tag_to_uuid_map

    _initial_user_email_to_uuid_map = {}
    _initial_vehicle_tag_to_uuid_map = {}

    current_time_iso = datetime.datetime.now().isoformat(timespec='milliseconds') + "Z"

    # Convert users
    new_users = {}
    for email, user_data in converted_data.get("users", {}).items():
        user_id = str(uuid.uuid4())
        _initial_user_email_to_uuid_map[email] = user_id
        user_data["id"] = user_id # Add a UUID ID to the user data itself

        # Convert friends to UUIDs
        if "friends" in user_data:
            user_data["friends"] = [
                _initial_user_email_to_uuid_map.get(friend_email, friend_email) # Use get for safety if friend not in map yet
                for friend_email in user_data["friends"]
            ]
        
        new_users[user_id] = user_data
    converted_data["users"] = new_users

    # Now that user UUIDs are generated, iterate again to update friends if they weren't in initial map
    for user_id, user_data in converted_data["users"].items():
        if "friends" in user_data:
            user_data["friends"] = [
                _initial_user_email_to_uuid_map.get(friend_email, friend_email) # Re-map in case they were processed out of order
                for friend_email in user_data["friends"]
            ]
            # Clean up friends list to ensure they are valid UUIDs, remove if not mapped
            user_data["friends"] = [
                friend_id for friend_id in user_data["friends"] 
                if friend_id in converted_data["users"] or friend_id in _initial_user_email_to_uuid_map.values()
            ]


    # Convert vehicles
    for user_original_email, user_original_data in initial_data.get("users", {}).items():
        user_uuid = _initial_user_email_to_uuid_map[user_original_email]
        
        user_tesla_data = converted_data["users"][user_uuid].get("tesla_data", {})
        old_vehicles = user_tesla_data.get("vehicles", {})
        new_vehicles = {}

        for old_vehicle_tag, vehicle_data in old_vehicles.items():
            new_vehicle_id = str(uuid.uuid4())
            _initial_vehicle_tag_to_uuid_map[(user_uuid, old_vehicle_tag)] = new_vehicle_id

            vehicle_data["id"] = new_vehicle_id # Add UUID as primary ID for the vehicle
            
            # Add timestamps if not present, or convert to ISO format
            if "createdTime" not in vehicle_data:
                vehicle_data["createdTime"] = current_time_iso
            if "modifiedTime" not in vehicle_data:
                vehicle_data["modifiedTime"] = current_time_iso

            # Ensure 'vehicle_tag' field within vehicle data holds the original string for lookup
            vehicle_data["original_vehicle_tag"] = old_vehicle_tag 

            new_vehicles[new_vehicle_id] = vehicle_data
        user_tesla_data["vehicles"] = new_vehicles
        converted_data["users"][user_uuid]["tesla_data"] = user_tesla_data

    return converted_data


# Define the initial raw state with string/integer IDs and emails for conversion
RAW_DEFAULT_STATE = {
    "users": {
        "alice.smith@mail.com": {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@mail.com",
            "friends": ["bob.johnson@mail.com"],
            "tesla_data": {
                "vehicles": {
                    "alice_model_3": { # This will be the key for old_vehicle_tag mapping
                        "vehicle_tag": "5YJ3E1EA2PF330316", # This is the VIN, keep as property
                        "horn": False,
                        "media": {
                            "playing": False,
                            "volume": 50,
                            "current_track": 0,
                            "favorites": ["The Commute Playlist", "Driving Rock Anthems", "Chill Acoustic Vibes"]
                        },
                        "trunk": {
                            "front": "closed",
                            "rear": "closed"
                        },
                        "charge": {
                            "port_open": False,
                            "charging": False,
                            "limit": 80
                        },
                        "climate": {
                            "on": False,
                            "bioweapon_mode": False,
                            "climate_keeper_mode": "off",
                            "cop_temp": 30,
                            "driver_temp": 20
                        },
                        "locks": {
                            "locked": True
                        },
                        "sentry_mode": {
                            "on": False,
                            "alerts": []
                        },
                        "lights": {
                            "on": False
                        },
                        "doors": {
                            "driver_front": "closed",
                            "passenger_front": "closed",
                            "driver_rear": "closed",
                            "passenger_rear": "closed"
                        },
                        "windows": "closed",
                        "awake": True,
                        "speed": 0,
                        "location": {"latitude": 34.0522, "longitude": -118.2437}, # Los Angeles
                        "firmware_version": "2024.14.7"
                    },
                    "alice_model_y": {
                        "vehicle_tag": "5YJYGDEE3MF123456",
                        "horn": False,
                        "media": {
                            "playing": True,
                            "volume": 70,
                            "current_track": 1,
                            "favorites": ["Road Trip Mix", "Podcast Binge"]
                        },
                        "trunk": {
                            "front": "closed",
                            "rear": "closed"
                        },
                        "charge": {
                            "port_open": False,
                            "charging": True,
                            "limit": 90
                        },
                        "climate": {
                            "on": True,
                            "bioweapon_mode": False,
                            "climate_keeper_mode": "dog",
                            "cop_temp": 25,
                            "driver_temp": 22
                        },
                        "locks": {
                            "locked": False
                        },
                        "sentry_mode": {
                            "on": True,
                            "alerts": ["Motion detected near front door"]
                        },
                        "lights": {
                            "on": False
                        },
                        "doors": {
                            "driver_front": "closed",
                            "passenger_front": "closed",
                            "driver_rear": "closed",
                            "passenger_rear": "closed"
                        },
                        "windows": "closed",
                        "awake": True,
                        "speed": 65,
                        "location": {"latitude": 37.7749, "longitude": -122.4194}, # San Francisco
                        "firmware_version": "2024.14.7"
                    }
                }
            }
        },
        "bob.johnson@mail.com": {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@mail.com",
            "friends": ["alice.smith@mail.com"],
            "tesla_data": {
                "vehicles": {
                    "bob_model_s": {
                        "vehicle_tag": "5YJSA1CNXJF000001",
                        "horn": False,
                        "media": {
                            "playing": False,
                            "volume": 60,
                            "current_track": 0,
                            "favorites": ["Classical Chill", "News Briefs"]
                        },
                        "trunk": {
                            "front": "closed",
                            "rear": "closed"
                        },
                        "charge": {
                            "port_open": True,
                            "charging": False,
                            "limit": 70
                        },
                        "climate": {
                            "on": False,
                            "bioweapon_mode": False,
                            "climate_keeper_mode": "off",
                            "cop_temp": 28,
                            "driver_temp": 28
                        },
                        "locks": {
                            "locked": True
                        },
                        "sentry_mode": {
                            "on": False,
                            "alerts": []
                        },
                        "lights": {
                            "on": False
                        },
                        "doors": {
                            "driver_front": "closed",
                            "passenger_front": "closed",
                            "driver_rear": "closed",
                            "passenger_rear": "closed"
                        },
                        "windows": "closed",
                        "awake": False,
                        "speed": 0,
                        "location": {"latitude": 38.9072, "longitude": -77.0369}, # Washington D.C.
                        "firmware_version": "2024.12.3"
                    }
                }
            }
        }
    }
}

# --- Helper functions for generating diverse data ---
def generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365*5):
    """Generates a random ISO 8601 formatted datetime string (with Z for UTC) in the past."""
    delta_days = random.randint(days_ago_min, days_ago_max)
    time_offset = datetime.timedelta(days=delta_days, 
                                     hours=random.randint(0, 23), 
                                     minutes=random.randint(0, 59), 
                                     seconds=random.randint(0, 59))
    dt = datetime.datetime.now(datetime.timezone.utc) - time_offset
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

def generate_vin():
    """Generates a plausible-looking 17-character VIN."""
    # Simplified VIN generation for diversity, not real VIN logic
    prefix = random.choice(["5YJ", "7SA", "LFV", "LRW"]) # Common Tesla prefixes
    year_code = random.choice("PRSTVWXY123456789") # Year code (P=2023, R=2024, S=2025 etc.)
    plant_code = random.choice("ABCDEFGHJKLMNPRSTVWXY") # Plant code
    random_chars = ''.join(random.choices('0123456789ABCDEFGHJKLMNPRSTUVWXYZ', k=12))
    return f"{prefix}{random_chars[:5]}{year_code}{plant_code}{random_chars[7:]}"

def generate_tesla_model():
    return random.choice(["Model 3", "Model Y", "Model S", "Model X", "Cybertruck", "Roadster"])

def generate_location():
    """Generates a random latitude and longitude within a plausible range (e.g., US)"""
    lat = random.uniform(25.0, 49.0) # Approx US latitude range
    lon = random.uniform(-125.0, -66.0) # Approx US longitude range
    return {"latitude": round(lat, 4), "longitude": round(lon, 4)}

# --- Data for generating new users ---
first_names = ["Emma", "Noah", "Olivia", "Liam", "Ava", "Isabella", "Sophia", "Jackson", "Aiden", "Charlotte", "Amelia", "Harper", "Ethan", "Mason", "Logan", "Mia", "Ella", "Avery", "Lucas", "Lily", "Grace", "Chloe", "Zoe", "Riley", "Layla", "Penelope", "Nora", "Scarlett", "Hannah", "Leo", "Mila", "Sofia", "Aria", "Eleanor", "Victoria", "Aubrey", "Ellie", "Stella", "Natalie", "Luna", "Benjamin", "Samuel", "Elijah", "James", "William", "Alexander", "Michael", "Daniel", "Matthew", "David"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Sanchez"]
email_domains = ["example.com", "mail.net", "web.org", "inbox.co", "domain.app"]
favorite_playlists = [
    "Morning Commute Tunes", "Evening Drive Relax", "Weekend Adventure Mix",
    "Focus Work Beats", "Podcast Catch-up", "Family Road Trip Hits",
    "City Driving Jazz", "Country Roads Playlist", "Highway Rock Anthems",
    "Chill Acoustic Vibes", "Energy Boosters", "Rainy Day Reflections"
]
sentry_alerts = [
    "Motion detected near front door", "Object too close to rear bumper",
    "Alarm triggered by strange noise", "Recording event - vehicle approached"
]
firmware_versions = ["2024.14.7", "2024.12.3", "2024.8.9", "2023.44.30.8", "2023.38.10"]

# --- Generate additional users ---
num_initial_users = len(RAW_DEFAULT_STATE["users"])
num_users_to_add = 50 - num_initial_users # Aim for 50 total users

# Before we modify DEFAULT_STATE, convert the initial RAW_DEFAULT_STATE
# This ensures existing users and vehicles get UUIDs and are in the correct format
DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)

# Collect existing user UUIDs for friend linking
all_user_uuids = list(DEFAULT_STATE["users"].keys())

for i in range(num_users_to_add):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}{random.randint(1, 999)}@{random.choice(email_domains)}"
    
    # Ensure unique email
    # Convert existing emails in DEFAULT_STATE back to original email string for this check
    existing_emails = set([DEFAULT_STATE["users"][uid].get("email") for uid in DEFAULT_STATE["users"].keys()])
    while email in existing_emails:
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 999)}@{random.choice(email_domains)}"

    user_id = str(uuid.uuid4())
    _initial_user_email_to_uuid_map[email] = user_id # Add to map for friend linking in new users

    # Generate friends for new user (mix of existing and potentially other new users)
    num_friends = random.randint(0, min(5, len(all_user_uuids)))
    friends_list = random.sample(all_user_uuids, num_friends)
    # Add some initial email strings that will be converted to UUIDs later
    if random.random() < 0.3 and len(all_user_uuids) > 0: # 30% chance to add another random email that will become a new user
        potential_friend_email = f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}{random.randint(1000, 9999)}@{random.choice(email_domains)}"
        if potential_friend_email not in existing_emails:
            friends_list.append(potential_friend_email)


    # Generate Tesla data for new user
    num_vehicles = random.choices([0, 1, 2, 3], weights=[0.4, 0.4, 0.15, 0.05], k=1)[0] # 40% no car, 40% one, 15% two, 5% three
    user_vehicles = {}
    for v_idx in range(num_vehicles):
        vehicle_tag_base = f"{first.lower()}_{generate_tesla_model().replace(' ', '_').lower()}_{v_idx+1}"
        
        # Ensure unique vehicle_tag_base for user
        current_user_vehicle_tags = set(user_vehicles.keys())
        while vehicle_tag_base in current_user_vehicle_tags:
            vehicle_tag_base = f"{first.lower()}_{generate_tesla_model().replace(' ', '_').lower()}_{random.randint(1, 5)}"

        vehicle_id = str(uuid.uuid4()) # New UUID for the vehicle
        _initial_vehicle_tag_to_uuid_map[(user_id, vehicle_tag_base)] = vehicle_id # Map for potential future linking


        media_playing = random.random() < 0.5
        sentry_on = random.random() < 0.3
        num_alerts = random.randint(0, 2) if sentry_on else 0
        current_alerts = random.sample(sentry_alerts, num_alerts) if num_alerts > 0 else []

        user_vehicles[vehicle_id] = { # Use UUID as the key now
            "id": vehicle_id, # Add ID to the vehicle data itself
            "original_vehicle_tag": vehicle_tag_base, # Keep original tag for reference
            "vehicle_tag": generate_vin(), # Realistic VIN
            "horn": False,
            "media": {
                "playing": media_playing,
                "volume": random.randint(20, 90),
                "current_track": random.randint(0, 5) if media_playing else 0,
                "favorites": random.sample(favorite_playlists, random.randint(0, min(3, len(favorite_playlists))))
            },
            "trunk": {
                "front": random.choice(["open", "closed"]),
                "rear": random.choice(["open", "closed"])
            },
            "charge": {
                "port_open": random.random() < 0.2, # 20% chance open
                "charging": random.random() < 0.4, # 40% chance charging
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
            "awake": random.random() < 0.7, # 70% chance awake
            "speed": random.randint(0, 120) if random.random() < 0.5 else 0, # 50% chance to be moving
            "location": generate_location(),
            "firmware_version": random.choice(firmware_versions),
            "createdTime": generate_random_iso_timestamp(days_ago_min=365*2, days_ago_max=365*5), # 2 to 5 years ago
            "modifiedTime": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=60) # Last 60 days
        }
    
    # Add the new user data
    DEFAULT_STATE["users"][user_id] = {
        "id": user_id,
        "first_name": first,
        "last_name": last,
        "email": email,
        "friends": friends_list, # This will contain a mix of UUIDs and potentially emails to be converted
        "tesla_data": {
            "vehicles": user_vehicles
        }
    }
    all_user_uuids.append(user_id) # Add the new user's UUID to the list for subsequent friend linking

# Final pass to convert any remaining friend emails to UUIDs for newly added users
# This is crucial because some friends added earlier might have been emails of users
# generated *later* in the loop.
for user_id, user_data in DEFAULT_STATE["users"].items():
    if "friends" in user_data:
        updated_friends = []
        for friend_identifier in user_data["friends"]:
            if friend_identifier in _initial_user_email_to_uuid_map: # Check if it's an email that has been mapped
                updated_friends.append(_initial_user_email_to_uuid_map[friend_identifier])
            elif friend_identifier in DEFAULT_STATE["users"]: # Check if it's already a UUID
                updated_friends.append(friend_identifier)
            # If it's an email that wasn't mapped (e.g., a typo or non-existent), we'll drop it.
            # Or if it's a UUID not in DEFAULT_STATE users (shouldn't happen with current logic)
        user_data["friends"] = list(set(updated_friends)) # Use set to remove duplicates if any

import json
output_filename = 'diverse_tesla_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Total number of users: {len(DEFAULT_STATE['users'])}")
total_vehicles = sum(len(user_data.get("tesla_data", {}).get("vehicles", {})) for user_data in DEFAULT_STATE["users"].values())
print(f"Total number of vehicles: {total_vehicles}")
print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

class TeslaFleetApis:
    """
    A dummy API class for simulating Tesla Fleet operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the TeslaFleetApis instance, setting up the in-memory
        data stores and loading the default scenario.
        """
        self._api_description = "This tool simulates a Tesla Fleet management system, allowing interaction with various vehicle functionalities."
        self.users: Dict[str, Any] = {} # Keyed by user UUID
        self._current_user_uuid: Optional[str] = None # Stores the UUID of the current user

        # Internal map for efficient lookup of vehicle UUIDs by original_vehicle_tag for a user
        # {(user_uuid, original_vehicle_tag_string): vehicle_uuid}
        self._vehicle_tag_lookup_map: Dict[tuple[str, str], str] = {}

        self._load_scenario(DEFAULT_STATE)

        # Populate the vehicle tag lookup map after loading the scenario
        self._populate_vehicle_tag_lookup_map()
        
        # Set the current user to the first user in the default state, or None
        if self.users:
            self._current_user_uuid = next(iter(self.users))


    def _populate_vehicle_tag_lookup_map(self):
        """Populates the internal map for looking up vehicle UUIDs by original tag."""
        self._vehicle_tag_lookup_map = {}
        for user_uuid, user_data in self.users.items():
            vehicles = user_data.get("tesla_data", {}).get("vehicles", {})
            for vehicle_uuid, vehicle_data in vehicles.items():
                original_tag = vehicle_data.get("original_vehicle_tag")
                if original_tag:
                    self._vehicle_tag_lookup_map[(user_uuid, original_tag)] = vehicle_uuid


    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain "users" with their tesla_data.
        """
        # Create deep copy to ensure the original DEFAULT_STATE is not modified
        self.users = copy.deepcopy(scenario.get("users", {}))
        self._populate_vehicle_tag_lookup_map() # Repopulate map on load
        print("TeslaFleetApis: Loaded scenario with UUIDs for users and vehicles.")

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for dummy entities.
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

    def _get_user_tesla_data(self, user: User) -> Optional[Dict[str, Any]]:
        """Helper to get a user's Tesla data based on User object."""
        target_user_uuid = self._get_user_id_by_email(user.email)
        
        if not target_user_uuid:
            return None
        
        return self.users.get(target_user_uuid, {}).get("tesla_data")

    def _get_user_vehicles(self, user: User) -> Optional[Dict[str, Any]]:
        """Helper to get a user's vehicles based on User object."""
        tesla_data = self._get_user_tesla_data(user)
        return tesla_data.get("vehicles") if tesla_data else None

    def _get_vehicle(self, user: User, vehicle_tag: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get a specific vehicle's data for a user using its original_vehicle_tag.
        """
        user_uuid = self._get_user_id_by_email(user.email)
        if not user_uuid:
            return None # User not found

        vehicle_uuid = self._vehicle_tag_lookup_map.get((user_uuid, vehicle_tag))
        if not vehicle_uuid:
            return None # Vehicle not found for this user and tag

        vehicles = self._get_user_vehicles(user)
        return vehicles.get(vehicle_uuid) if vehicles else None


    def set_current_user(self, user_email: str) -> Dict[str, bool]:
        """
        Sets the current authenticated user for the API session.

        Args:
            user_email (str): The email address of the user to set as current.

        Returns:
            Dict[str, bool]: A dictionary with 'status' indicating success or failure.
        """
        user_id = self._get_user_id_by_email(user_email)
        if user_id:
            self._current_user_uuid = user_id
            return {"status": True, "message": f"Current user set to {user_email} (ID: {user_id})."}
        return {"status": False, "message": f"User with email {user_email} not found."}


    # ================
    # Vehicle General Operations
    # ================

    def show_vehicle_info(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive information about a specific vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier (e.g., model name or VIN) of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary containing vehicle details if successful,
                            or an error message if the vehicle or user is not found.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"error": f"Vehicle '{vehicle_tag}' not found for user {user.email}."}
        return {"vehicle_info": copy.deepcopy(vehicle)}

    def honk_horn(self, user: User, vehicle_tag: str) -> Dict[str, bool]:
        """
        Honk the horn of the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        vehicle["horn"] = True
        print(f"Vehicle {vehicle_tag}: Horn honked.")
        return {"success": True}

    def flash_lights(self, user: User, vehicle_tag: str) -> Dict[str, bool]:
        """
        Flash the lights of the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        vehicle["lights"]["on"] = True
        print(f"Vehicle {vehicle_tag}: Lights flashed.")
        return {"success": True}

    # ================
    # Media Controls
    # ================

    def start_stop_media(self, user: User, vehicle_tag: str, command: Literal["start", "stop"]) -> Dict[str, bool]:
        """
        Start or stop media playback in the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            command (Literal["start", "stop"]): The command to issue ('start' or 'stop').

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        vehicle["media"]["playing"] = (command == "start")
        print(f"Vehicle {vehicle_tag}: Media playback {command}ed.")
        return {"success": True}

    def set_volume(self, user: User, vehicle_tag: str, volume_level: int) -> Dict[str, bool]:
        """
        Set the media volume level in the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            volume_level (int): The desired volume level (0-100).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        if not (0 <= volume_level <= 100):
            return {"success": False, "message": "Volume level must be between 0 and 100."}

        vehicle["media"]["volume"] = volume_level
        print(f"Vehicle {vehicle_tag}: Volume set to {volume_level}.")
        return {"success": True}

    def skip_media_track(self, user: User, vehicle_tag: str, direction: Literal["next", "previous"]) -> Dict[str, bool]:
        """
        Skip to the next or previous media track in the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            direction (Literal["next", "previous"]): The direction to skip ('next' or 'previous').

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}
        
        # This is a dummy implementation; a real system would interact with a playlist
        current_track = vehicle["media"]["current_track"]
        if direction == "next":
            vehicle["media"]["current_track"] = current_track + 1
        else: # previous
            vehicle["media"]["current_track"] = max(0, current_track - 1)
        
        print(f"Vehicle {vehicle_tag}: Skipped to {direction} track.")
        return {"success": True}

    # ================
    # Trunk Control
    # ================

    def open_close_trunk(self, user: User, vehicle_tag: str, trunk_part: Literal["front", "rear"], command: Literal["open", "close"]) -> Dict[str, bool]:
        """
        Open or close the front or rear trunk of the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            trunk_part (Literal["front", "rear"]): Which part of the trunk to control ('front' or 'rear').
            command (Literal["open", "close"]): The command to issue ('open' or 'close').

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        vehicle["trunk"][trunk_part] = command
        print(f"Vehicle {vehicle_tag}: {trunk_part.capitalize()} trunk {command}ed.")
        return {"success": True}

    # ================
    # Charge Control
    # ================

    def set_charge_limit(self, user: User, vehicle_tag: str, limit: int) -> Dict[str, bool]:
        """
        Set the charge limit percentage for the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            limit (int): The desired charge limit percentage (0-100).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        if not (0 <= limit <= 100):
            return {"success": False, "message": "Charge limit must be between 0 and 100."}

        vehicle["charge"]["limit"] = limit
        print(f"Vehicle {vehicle_tag}: Charge limit set to {limit}%.")
        return {"success": True}

    def open_close_charge_port(self, user: User, vehicle_tag: str, command: Literal["open", "close"]) -> Dict[str, bool]:
        """
        Open or close the charge port of the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            command (Literal["open", "close"]): The command to issue ('open' or 'close').

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        vehicle["charge"]["port_open"] = (command == "open")
        print(f"Vehicle {vehicle_tag}: Charge port {command}ed.")
        return {"success": True}

    def start_stop_charge(self, user: User, vehicle_tag: str, command: Literal["start", "stop"]) -> Dict[str, bool]:
        """
        Start or stop charging for the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            command (Literal["start", "stop"]): The command to issue ('start' or 'stop').

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        vehicle["charge"]["charging"] = (command == "start")
        print(f"Vehicle {vehicle_tag}: Charging {command}ed.")
        return {"success": True}

    # ================
    # Climate Control
    # ================

    def start_stop_climate(self, user: User, vehicle_tag: str, command: Literal["on", "off"]) -> Dict[str, bool]:
        """
        Turn the climate control system of the specified vehicle on or off.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            command (Literal["on", "off"]): The command to issue ('on' or 'off').

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        vehicle["climate"]["on"] = (command == "on")
        print(f"Vehicle {vehicle_tag}: Climate control turned {command}.")
        return {"success": True}

    def set_climate_temp(self, user: User, vehicle_tag: str, driver_temp: int, cop_temp: int) -> Dict[str, bool]:
        """
        Set the driver and passenger cabin temperatures for the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            driver_temp (int): Desired temperature for the driver's side (in Celsius).
            cop_temp (int): Desired temperature for the co-pilot's side (in Celsius).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        # Assuming a reasonable range for temperatures, e.g., 15-30 Celsius
        if not (15 <= driver_temp <= 30) or not (15 <= cop_temp <= 30):
            return {"success": False, "message": "Temperatures must be between 15 and 30 Celsius."}

        vehicle["climate"]["driver_temp"] = driver_temp
        vehicle["climate"]["cop_temp"] = cop_temp
        print(f"Vehicle {vehicle_tag}: Driver temp set to {driver_temp}°C, Co-pilot temp set to {cop_temp}°C.")
        return {"success": True}

    def set_bioweapon_mode(self, user: User, vehicle_tag: str, command: Literal["on", "off"]) -> Dict[str, bool]:
        """
        Turn the Bioweapon Defense Mode of the specified vehicle on or off.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            command (Literal["on", "off"]): The command to issue ('on' or 'off').

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        vehicle["climate"]["bioweapon_mode"] = (command == "on")
        print(f"Vehicle {vehicle_tag}: Bioweapon Defense Mode turned {command}.")
        return {"success": True}

    def set_climate_keeper_mode(self, user: User, vehicle_tag: str, mode: Literal["off", "dog", "camp"]) -> Dict[str, bool]:
        """
        Set the Climate Keeper Mode of the specified vehicle (e.g., "dog", "camp", "off").

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            mode (Literal["off", "dog", "camp"]): The Climate Keeper Mode to set.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        vehicle["climate"]["climate_keeper_mode"] = mode
        print(f"Vehicle {vehicle_tag}: Climate Keeper Mode set to '{mode}'.")
        return {"success": True}
    
    # ================
    # Remote Commands
    # ================

    def wake_up(self, user: User, vehicle_tag: str) -> Dict[str, bool]:
        """
        Wake up the specified vehicle from sleep mode.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        vehicle["awake"] = True
        print(f"Vehicle {vehicle_tag}: Vehicle woken up.")
        return {"success": True}

    def window_control(self, user: User, vehicle_tag: str, command: Literal["vent", "close"], lat: float, lon: float) -> Dict[str, bool]:
        """
        Control the windows of the specified vehicle (e.g., "vent", "close").
        The latitude and longitude might be used to confirm a safe location for window operations.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            command (Literal["vent", "close"]): The window control command (e.g., "vent", "close").
            lat (float): The latitude coordinate of the vehicle.
            lon (float): The longitude coordinate of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"success": False, "message": f"Vehicle '{vehicle_tag}' not found."}

        vehicle["windows"] = command
        print(f"Vehicle {vehicle_tag}: Window command '{command}' issued at ({lat}, {lon}).")
        return {"success": True}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        # Re-run the initial data conversion to reset maps and UUIDs
        global DEFAULT_STATE
        DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)
        self._load_scenario(DEFAULT_STATE)
        print("TeslaFleetApis: All dummy data reset to default state.")
        return {"reset_status": True}