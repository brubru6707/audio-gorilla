import copy
import uuid
from typing import Dict, Any, Optional, Literal
from UnitTests.test_data_helper import BackendDataLoader

DEFAULT_STATE = BackendDataLoader.get_teslafleet_data()

class EmailStr(str):
    pass

class User:
    def __init__(self, email: EmailStr):
        self.email = email

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
        self.users: Dict[str, Any] = {}
        self._current_user_uuid: Optional[str] = None

        self._vehicle_tag_lookup_map: Dict[tuple[str, str], str] = {}

        self._load_scenario(DEFAULT_STATE)

        self._populate_vehicle_tag_lookup_map()
        
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
        self.users = copy.deepcopy(scenario.get("users", {}))
        self._populate_vehicle_tag_lookup_map() 
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
            return None

        vehicle_uuid = self._vehicle_tag_lookup_map.get((user_uuid, vehicle_tag))
        if not vehicle_uuid:
            return None

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

    def honk_horn(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Honk the horn of the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["horn"] = True
        print(f"Vehicle {vehicle_tag}: Horn honked.")
        return {"reason": "", "result": True}

    def flash_lights(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Flash the lights of the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["lights"]["on"] = True
        print(f"Vehicle {vehicle_tag}: Lights flashed.")
        return {"reason": "", "result": True}

    def media_volume_up(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Turns up the volume of the media system.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        current_volume = vehicle["media"]["volume"]
        vehicle["media"]["volume"] = min(100, current_volume + 1)
        print(f"Vehicle {vehicle_tag}: Volume increased.")
        return {"reason": "", "result": True}

    def media_volume_down(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Turns down the volume of the media system.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        current_volume = vehicle["media"]["volume"]
        vehicle["media"]["volume"] = max(0, current_volume - 1)
        print(f"Vehicle {vehicle_tag}: Volume decreased.")
        return {"reason": "", "result": True}

    def door_unlock(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Unlocks the doors to the car.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["locks"] = "unlocked"
        print(f"Vehicle {vehicle_tag}: Doors unlocked.")
        return {"reason": "", "result": True}

    def door_lock(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Locks the doors to the car.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["locks"] = "locked"
        print(f"Vehicle {vehicle_tag}: Doors locked.")
        return {"reason": "", "result": True}

    def media_toggle_playback(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Toggles the media between playing and paused.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["media"]["playing"] = not vehicle["media"]["playing"]
        print(f"Vehicle {vehicle_tag}: Media playback toggled.")
        return {"reason": "", "result": True}

    def adjust_volume(self, user: User, vehicle_tag: str, volume: int) -> Dict[str, Any]:
        """
        Adjusts the volume of the media system to the desired volume.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            volume (int): The desired volume level.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        if not (0 <= volume <= 100):
            return {"reason": "Volume level must be between 0 and 100.", "result": False}

        vehicle["media"]["volume"] = volume
        print(f"Vehicle {vehicle_tag}: Volume set to {volume}.")
        return {"reason": "", "result": True}

    def media_next_track(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Skips to the next track in the current playlist.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}
        
        vehicle["media"]["current_track"] = vehicle["media"]["current_track"] + 1
        print(f"Vehicle {vehicle_tag}: Skipped to next track.")
        return {"reason": "", "result": True}

    def media_prev_track(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Skips to the previous track in the current playlist.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}
        
        vehicle["media"]["current_track"] = max(0, vehicle["media"]["current_track"] - 1)
        print(f"Vehicle {vehicle_tag}: Skipped to previous track.")
        return {"reason": "", "result": True}

    def actuate_trunk(self, user: User, vehicle_tag: str, which_trunk: Literal["front", "rear"]) -> Dict[str, Any]:
        """
        Opens either the front or rear trunk.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            which_trunk (Literal["front", "rear"]): Which trunk to actuate.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["trunk"][which_trunk] = "open"
        print(f"Vehicle {vehicle_tag}: {which_trunk.capitalize()} trunk opened.")
        return {"reason": "", "result": True}

    def set_charge_limit(self, user: User, vehicle_tag: str, limit: int) -> Dict[str, Any]:
        """
        Set the charge limit percentage for the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            limit (int): The desired charge limit percentage (0-100).

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        if not (0 <= limit <= 100):
            return {"reason": "Charge limit must be between 0 and 100.", "result": False}

        vehicle["charge"]["limit"] = limit
        print(f"Vehicle {vehicle_tag}: Charge limit set to {limit}%.")
        return {"reason": "", "result": True}

    def charge_port_door_open(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Opens the charge port or unlocks the cable.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["charge"]["port_open"] = True
        print(f"Vehicle {vehicle_tag}: Charge port opened.")
        return {"reason": "", "result": True}

    def charge_port_door_close(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Closes the charge port.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["charge"]["port_open"] = False
        print(f"Vehicle {vehicle_tag}: Charge port closed.")
        return {"reason": "", "result": True}

    def charge_start(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Start charging if the car is plugged in but not currently charging.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["charge"]["charging"] = True
        print(f"Vehicle {vehicle_tag}: Charging started.")
        return {"reason": "", "result": True}

    def charge_stop(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Stop charging if the car is currently charging.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["charge"]["charging"] = False
        print(f"Vehicle {vehicle_tag}: Charging stopped.")
        return {"reason": "", "result": True}

    def auto_conditioning_start(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Start the climate control (HVAC) system.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["climate"]["on"] = True
        print(f"Vehicle {vehicle_tag}: Climate control started.")
        return {"reason": "", "result": True}

    def auto_conditioning_stop(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Stop the climate control (HVAC) system.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["climate"]["on"] = False
        print(f"Vehicle {vehicle_tag}: Climate control stopped.")
        return {"reason": "", "result": True}

    def set_temps(self, user: User, vehicle_tag: str, driver_temp: float, passenger_temp: float) -> Dict[str, Any]:
        """
        Sets the target temperature for the climate control (HVAC) system.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            driver_temp (float): The desired temperature for the driver.
            passenger_temp (float): The desired temperature for the passenger.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        if not (15 <= driver_temp <= 30) or not (15 <= passenger_temp <= 30):
            return {"reason": "Temperatures must be between 15 and 30 Celsius.", "result": False}

        vehicle["climate"]["driver_temp"] = driver_temp
        vehicle["climate"]["cop_temp"] = passenger_temp
        print(f"Vehicle {vehicle_tag}: Driver temp set to {driver_temp}°C, Passenger temp set to {passenger_temp}°C.")
        return {"reason": "", "result": True}

    def set_bioweapon_mode(self, user: User, vehicle_tag: str, on: bool) -> Dict[str, Any]:
        """
        Enable or disable Bioweapon Defense Mode.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): Whether to enable (True) or disable (False) Bioweapon Defense Mode.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["climate"]["bioweapon_mode"] = on
        print(f"Vehicle {vehicle_tag}: Bioweapon Defense Mode turned {'on' if on else 'off'}.")
        return {"reason": "", "result": True}

    def set_climate_keeper_mode(self, user: User, vehicle_tag: str, climate_keeper_mode: int) -> Dict[str, Any]:
        """
        Set the Climate Keeper mode.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            climate_keeper_mode (int): The Climate Keeper mode (0=off, 1=dog, 2=camp).

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        mode_names = {0: "off", 1: "dog", 2: "camp"}
        if climate_keeper_mode not in mode_names:
            return {"reason": "Invalid climate keeper mode. Must be 0 (off), 1 (dog), or 2 (camp).", "result": False}

        vehicle["climate"]["climate_keeper_mode"] = mode_names[climate_keeper_mode]
        print(f"Vehicle {vehicle_tag}: Climate Keeper Mode set to '{mode_names[climate_keeper_mode]}'.")
        return {"reason": "", "result": True}
    
    def wake_up(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Wakes up the car from a sleeping state.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["awake"] = True
        print(f"Vehicle {vehicle_tag}: Vehicle woken up.")
        return {"reason": "", "result": True}

    def window_control(self, user: User, vehicle_tag: str, command: Literal["vent", "close"]) -> Dict[str, Any]:
        """
        Controls the windows. Will vent or close all windows simultaneously.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            command (Literal["vent", "close"]): The window control command.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["windows"] = command
        print(f"Vehicle {vehicle_tag}: Window command '{command}' issued.")
        return {"reason": "", "result": True}

    def get_vehicle_location(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Get the current location of the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary containing location information.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"result": False, "reason": f"Vehicle '{vehicle_tag}' not found."}

        location = vehicle.get("location", {"latitude": 0, "longitude": 0})
        return {
            "result": True,
            "reason": "",
            "location": {
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "speed": vehicle.get("speed", 0)
            }
        }

    def get_vehicle_status(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Get comprehensive status information for the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary containing detailed vehicle status.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"result": False, "reason": f"Vehicle '{vehicle_tag}' not found."}

        status = {
            "result": True,
            "reason": "",
            "vehicle_info": {
                "id": vehicle.get("id"),
                "vehicle_tag": vehicle.get("vehicle_tag"),
                "firmware_version": vehicle.get("firmware_version"),
                "awake": vehicle.get("awake", False),
                "speed": vehicle.get("speed", 0)
            },
            "location": vehicle.get("location", {}),
            "charge": vehicle.get("charge", {}),
            "climate": vehicle.get("climate", {}),
            "locks": vehicle.get("locks", {}),
            "doors": vehicle.get("doors", {}),
            "trunk": vehicle.get("trunk", {}),
            "sentry_mode": vehicle.get("sentry_mode", {}),
            "lights": vehicle.get("lights", {}),
            "media": vehicle.get("media", {}),
            "windows": vehicle.get("windows", "closed")
        }
        
        return status

    def set_sentry_mode(self, user: User, vehicle_tag: str, on: bool) -> Dict[str, Any]:
        """
        Turns sentry mode on or off.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): Whether to enable (True) or disable (False) sentry mode.

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        sentry_mode = vehicle.get("sentry_mode", {})
        sentry_mode["on"] = on
        vehicle["sentry_mode"] = sentry_mode
        
        print(f"Vehicle {vehicle_tag}: Sentry mode turned {'on' if on else 'off'}.")
        return {"reason": "", "result": True}

    def get_firmware_info(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Get firmware version and update information for the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary containing firmware information.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"result": False, "reason": f"Vehicle '{vehicle_tag}' not found."}

        return {
            "result": True,
            "reason": "",
            "firmware": {
                "current_version": vehicle.get("firmware_version", "Unknown"),
                "created_time": vehicle.get("createdTime"),
                "modified_time": vehicle.get("modifiedTime"),
                "vehicle_tag": vehicle.get("vehicle_tag")
            }
        }

    def wake_vehicle(self, user: User, vehicle_tag: str) -> Dict[str, Any]:
        """
        Wake up the specified vehicle from sleep mode.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, Any]: A dictionary indicating if the wake command was successful.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        vehicle["awake"] = True
        print(f"Vehicle {vehicle_tag}: Wake command sent successfully.")
        return {"reason": "", "result": True}

    def set_speed_limit(self, user: User, vehicle_tag: str, limit_mph: int) -> Dict[str, Any]:
        """
        Set the speed limit for the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            limit_mph (int): The speed limit in miles per hour (0-140).

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        if not (0 <= limit_mph <= 140):
            return {"reason": "Speed limit must be between 0 and 140 mph.", "result": False}

        vehicle["speed_limit"] = limit_mph
        print(f"Vehicle {vehicle_tag}: Speed limit set to {limit_mph} mph.")
        return {"reason": "", "result": True}

    def set_valet_mode(self, user: User, vehicle_tag: str, on: bool, pin: Optional[str] = None) -> Dict[str, Any]:
        """
        Enable or disable valet mode for the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): Whether to enable (True) or disable (False) valet mode.
            pin (Optional[str]): PIN code for valet mode (required when enabling).

        Returns:
            Dict[str, Any]: A dictionary with "result" indicating success and "reason" for errors.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"reason": f"Vehicle '{vehicle_tag}' not found.", "result": False}

        if on and not pin:
            return {"reason": "PIN code is required to enable valet mode.", "result": False}

        vehicle["valet_mode"] = {"on": on, "pin": pin if on else None}
        print(f"Vehicle {vehicle_tag}: Valet mode {'enabled' if on else 'disabled'}.")
        return {"reason": "", "result": True}

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the distance between two points using the Haversine formula.
        
        Args:
            lat1 (float): Latitude of first point
            lon1 (float): Longitude of first point
            lat2 (float): Latitude of second point
            lon2 (float): Longitude of second point
            
        Returns:
            float: Distance in miles
        """
        import math
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        # Earth's radius in miles
        earth_radius = 3959
        return earth_radius * c

    def get_nearby_charging_sites(self, user: User, vehicle_tag: str, lat: float, lon: float, radius: int = 50) -> Dict[str, Any]:
        """
        Get nearby charging sites (superchargers) for the specified vehicle.

        Args:
            user (User): The current user object.
            vehicle_tag (str): The unique identifier of the vehicle.
            lat (float): Latitude coordinate.
            lon (float): Longitude coordinate.
            radius (int): Search radius in miles (default 50).

        Returns:
            Dict[str, Any]: A dictionary containing nearby charging sites.
        """
        vehicle = self._get_vehicle(user, vehicle_tag)
        if vehicle is None:
            return {"result": False, "reason": f"Vehicle '{vehicle_tag}' not found."}

        # Get superchargers from the state
        all_superchargers = DEFAULT_STATE.get("superchargers", [])
        
        # Find nearby superchargers within the radius
        nearby_sites = []
        for charger in all_superchargers:
            distance = self._calculate_distance(lat, lon, charger["latitude"], charger["longitude"])
            if distance <= radius:
                # Simulate available stalls (random but realistic)
                import random
                total_stalls = charger["total_stalls"]
                available_stalls = random.randint(max(0, total_stalls - 4), total_stalls)
                
                site_data = {
                    "name": charger["name"],
                    "latitude": charger["latitude"],
                    "longitude": charger["longitude"],
                    "distance": round(distance, 1),
                    "available_stalls": available_stalls,
                    "total_stalls": total_stalls,
                    "site_type": "supercharger",
                    "address": charger.get("address", "")
                }
                nearby_sites.append(site_data)
        
        # Sort by distance
        nearby_sites.sort(key=lambda x: x["distance"])

        return {
            "result": True,
            "reason": "",
            "charging_sites": nearby_sites
        }

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self._load_scenario(DEFAULT_STATE)
        print("TeslaFleetApis: All dummy data reset to default state.")
        return {"reset_status": True}