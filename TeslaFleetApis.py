import copy
import uuid
from typing import Dict, Any, Optional, Literal
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("TeslaFleetApis")

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