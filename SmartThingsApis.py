import datetime
import copy
import uuid
import random
from typing import Dict, List, Any, Optional, Union
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("SmartThingsApis")
# Cache the deepcopied default users state for performance
_DEFAULT_USERS_COPY = None

def _get_default_users_copy():
    global _DEFAULT_USERS_COPY
    if _DEFAULT_USERS_COPY is None:
        _DEFAULT_USERS_COPY = copy.deepcopy(DEFAULT_STATE.get("users", {}))
    return _DEFAULT_USERS_COPY


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
        
        # Use cached deep copy for performance
        if scenario is DEFAULT_STATE:
            self.users = copy.deepcopy(_get_default_users_copy())
        else:
            self.users = copy.deepcopy(scenario.get("users", {}))
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
        if user_id not in self.users:
            return None
        return self.users.get(user_id, {}).get("smartthings_data")

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


    def get_user_profile(self, user_id: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves the profile information for the authenticated SmartThings user.

        Args:
            user_id (str): The internal user ID (UUID).

        Returns:
            Dict: A dictionary containing 'status' (bool) and 'profile' (Dict) if successful.
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        if smartthings_data and "profile" in smartthings_data:
            return {"status": True, "profile": copy.deepcopy(smartthings_data["profile"])}
        return {"status": False, "profile": {}}

    def list_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all devices for a user.

        Args:
            user_id (str): The internal user ID (UUID).
        Returns:
            List[Dict[str, Any]]: List of all devices.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return []
        return [copy.deepcopy(d) for d in user_devices.values()]

    def get_device(self, device_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get a specific device for a user.

        Args:
            device_id (str): ID of the device.
            user_id (str): The internal user ID (UUID).
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
        user_id: str,
        location_name: Optional[str] = None, 
        room_name: Optional[str] = None, 
        capabilities: Optional[List[str]] = None,
        initial_status: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a new device for a user.

        Args:
            name (str): The name of the new device.
            user_id (str): The internal user ID (UUID).
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
            "last_activity_time": current_time_iso,
            "powerSource": "mains",
            "healthStatus": "healthy",
            "manufacturer": "SmartCorp",
            "model": f"Device-{random.randint(100,999)}",
            "firmwareVersion": "v1.0.0",
            "device_online_status_last_checked": current_time_iso
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
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Update the status of a specific device's capability.

        Args:
            device_id (str): ID of the device to update.
            component_id (str): ID of the component (e.g., 'main').
            capability_id (str): ID of the capability (e.g., 'switch').
            command (str): Command to send (e.g., 'on', 'off', 'setLevel').
            args (Optional[List[Any]]): Arguments for the command (e.g., [75] for setLevel).
            user_id (str): The internal user ID (UUID).
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

    def delete_device(self, device_id: str, user_id: str) -> Dict[str, bool]:
        """
        Delete a device.

        Args:
            device_id (str): ID of the device to delete.
            user_id (str): The internal user ID (UUID).
        Returns:
            Dict[str, bool]: True if the device was deleted successfully, False otherwise.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"status": False}

        if device_id in user_devices:
            del user_devices[device_id]
            user_email = self._get_user_email_by_id(user_id)
            print(f"Device '{device_id}' deleted for user {user_id} ({user_email})")
            return {"status": True}
        return {"status": False}

    def get_device_status(
        self,
        device_id: str,
        component_id: str = "main",
        capability_id: Optional[str] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Get the current status of a device or a specific capability.

        Args:
            device_id (str): ID of the device.
            component_id (str): ID of the component (e.g., 'main').
            capability_id (Optional[str]): ID of the capability (e.g., 'switch', 'level'). If None, returns all component status.
            user_id (str): The internal user ID (UUID).
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

    def list_locations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all locations for a user.

        Args:
            user_id (str): The internal user ID (UUID).
        Returns:
            List[Dict[str, Any]]: List of all locations.
        """
        user_locations = self._get_user_locations_data(user_id)
        if user_locations is None:
            return []
        return [copy.deepcopy(loc) for loc in user_locations.values()]

    def get_location(self, location_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get a specific location for a user.

        Args:
            location_id (str): ID of the location.
            user_id (str): The internal user ID (UUID).
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
        user_id: str,
        address: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a new location for a user.

        Args:
            name (str): The name of the new location.
            user_id (str): The internal user ID (UUID).
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
        user_id: str,
        name: Optional[str] = None,
        address: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Update an existing location for a user.

        Args:
            location_id (str): ID of the location to update.
            user_id (str): The internal user ID (UUID).
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

    def delete_location(self, location_id: str, user_id: str) -> Dict[str, bool]:
        """
        Delete a location.

        Args:
            location_id (str): ID of the location to delete.
            user_id (str): The internal user ID (UUID).
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
            user_email = self._get_user_email_by_id(user_id)
            print(f"Location '{location_id}' deleted for user {user_id} ({user_email})")
            return {"status": True}
        return {"status": False}

    def list_rooms(self, user_id: str, location_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all rooms for a user, optionally filtered by location.

        Args:
            user_id (str): The internal user ID (UUID).
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

    def get_room(self, room_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get a specific room for a user.

        Args:
            room_id (str): ID of the room.
            user_id (str): The internal user ID (UUID).
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
        user_id: str,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new room for a user.

        Args:
            name (str): The name of the new room.
            user_id (str): The internal user ID (UUID).
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
        user_id: str,
        name: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing room for a user.

        Args:
            room_id (str): ID of the room to update.
            user_id (str): The internal user ID (UUID).
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

    def delete_room(self, room_id: str, user_id: str) -> Dict[str, bool]:
        """
        Delete a room.

        Args:
            room_id (str): ID of the room to delete.
            user_id (str): The internal user ID (UUID).
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
            user_email = self._get_user_email_by_id(user_id)
            print(f"Room '{room_id}' deleted for user {user_id} ({user_email})")
            return {"status": True}
        return {"status": False}

    def list_capabilities(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all capabilities for a user.

        Args:
            user_id (str): The internal user ID (UUID).
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
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Get a specific capability for a user.

        Args:
            capability_id (str): ID of the capability.
            version (Optional[int]): Version of the capability.
            user_id (str): The internal user ID (UUID).
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

    def get_device_health(self, device_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get health status and metadata for a specific device.

        Args:
            device_id (str): ID of the device.
            user_id (str): The internal user ID (UUID).
        
        Returns:
            Dict[str, Any]: Device health information including status, power source, etc.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"error": f"User with ID {user_id} not found or has no devices."}

        device = user_devices.get(device_id)
        if not device:
            return {"error": f"Device {device_id} not found."}

        health_info = {
            "device_id": device_id,
            "name": device.get("name", "Unknown"),
            "status": device.get("status", "unknown"),
            "health_status": device.get("healthStatus", "unknown"),
            "power_source": device.get("powerSource", "unknown"),
            "manufacturer": device.get("manufacturer", "unknown"),
            "model": device.get("model", "unknown"),
            "firmware_version": device.get("firmwareVersion", "unknown"),
            "last_activity_time": device.get("last_activity_time"),
            "device_online_status_last_checked": device.get("device_online_status_last_checked"),
            "creation_time": device.get("creation_time")
        }

        return {"status": "success", "health": health_info}

    def list_devices_by_health_status(self, health_status: str, user_id: str) -> List[Dict[str, Any]]:
        """
        List devices filtered by health status.

        Args:
            health_status (str): Health status to filter by (healthy, degraded, error).
            user_id (str): The internal user ID (UUID).
        
        Returns:
            List[Dict[str, Any]]: List of devices with the specified health status.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return []

        filtered_devices = []
        for device in user_devices.values():
            if device.get("healthStatus") == health_status:
                filtered_devices.append(copy.deepcopy(device))
        
        return filtered_devices

    def list_devices_by_manufacturer(self, manufacturer: str, user_id: str) -> List[Dict[str, Any]]:
        """
        List devices filtered by manufacturer.

        Args:
            manufacturer (str): Manufacturer name to filter by.
            user_id (str): The internal user ID (UUID).
        
        Returns:
            List[Dict[str, Any]]: List of devices from the specified manufacturer.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return []

        filtered_devices = []
        for device in user_devices.values():
            if device.get("manufacturer") == manufacturer:
                filtered_devices.append(copy.deepcopy(device))
        
        return filtered_devices

    def update_device_firmware(self, device_id: str, new_version: str, user_id: str) -> Dict[str, Any]:
        """
        Update the firmware version of a device.

        Args:
            device_id (str): ID of the device.
            new_version (str): New firmware version.
            user_id (str): The internal user ID (UUID).
        
        Returns:
            Dict[str, Any]: Result of the firmware update operation.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"error": f"User with ID {user_id} not found or has no devices."}

        device = user_devices.get(device_id)
        if not device:
            return {"error": f"Device {device_id} not found."}

        old_version = device.get("firmwareVersion", "unknown")
        device["firmwareVersion"] = new_version
        device["last_activity_time"] = datetime.datetime.now().isoformat() + "Z"
        
        return {
            "status": "success", 
            "message": f"Firmware updated from {old_version} to {new_version}",
            "device_id": device_id,
            "old_version": old_version,
            "new_version": new_version
        }

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self._load_scenario(DEFAULT_STATE)
        print("SmartThingsApis: All dummy data reset to default state.")
        return {"reset_status": True}