# Inspired by https://developer.smartthings.com/docs/api/public

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
    An API class for simulating SmartThings operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the SmartThingsApis instance with in-memory data stores for simulating SmartThings smart home operations.
        
        Sets up empty user dictionary and loads the default scenario containing users with their devices,
        locations, rooms, and capabilities. This simulated backend enables testing of SmartThings workflows
        without connecting to actual SmartThings cloud services.
        
        Side Effects:
            - Creates empty users dictionary
            - Loads default state from state_loader
            - Prints confirmation message about loaded scenario
            
        Note:
            This is a simulation class for development/testing. All data is stored in memory
            and will be lost when the instance is destroyed. Each user has their own isolated
            SmartThings ecosystem (devices, locations, rooms).
        """
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the SmartThings API, which provides core functionality for managing smart home devices, locations, and rooms."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the backend's state, initializing all user data.
        
        Deep copies scenario data and populates the users dictionary. Uses performance optimization
        by caching the default scenario copy. This allows for resetting state between tests or
        initializing with specific data configurations.

        Args:
            scenario (Dict): A dictionary representing the complete state to load. Expected structure:
                {
                    "users": Dict[str, Any]  # User data keyed by user UUID, each containing:
                        # - email, first_name, last_name
                        # - smartthings_data with devices, locations, rooms, capabilities
                }
                
        Side Effects:
            - Completely replaces self.users with scenario data
            - Uses cached deep copy for DEFAULT_STATE (performance optimization)
            - Prints confirmation message to console
            - Does NOT reset any other instance state
            
        Note:
            Uses deep copy to prevent accidental modification of source scenario.
            When loading DEFAULT_STATE, uses a cached copy for better performance
            in test scenarios with frequent resets.
        """
        
        # Use cached deep copy for performance
        if scenario is DEFAULT_STATE:
            self.users = copy.deepcopy(_get_default_users_copy())
        else:
            self.users = copy.deepcopy(scenario.get("users", {}))
        print("SmartThingsApis: Loaded scenario with users, devices, locations, and rooms (all with UUIDs).")

    def _generate_id(self) -> str:
        """
        Generates a unique UUID string for creating new SmartThings entities.
        
        Uses Python's uuid.uuid4() to generate random UUIDs, ensuring global uniqueness
        across all entity types (devices, locations, rooms) in the simulated backend.
        
        Returns:
            str: A UUID string in standard format (e.g., "550e8400-e29b-41d4-a716-446655440000")
            
        Note:
            Used for creating new devices, locations, and rooms.
            Real SmartThings API uses similar UUID-based identifiers for all entities.
        """
        return str(uuid.uuid4())

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """
        Internal helper that looks up a user's UUID by their email address.
        
        Iterates through all users to find one with matching email. Enables user
        lookup by email for authentication or identification purposes.

        Args:
            email (str): The email address to search for (case-sensitive)

        Returns:
            Optional[str]: The user's UUID if found, None if no user has that email
            
        Note:
            Performs linear search through all users. For production systems,
            an email-to-UUID index would be more efficient.
        """
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """
        Internal helper that retrieves a user's email address from their UUID.
        
        Looks up user data by UUID and extracts the email field. Used for logging,
        display purposes, and building user-facing responses.

        Args:
            user_id (str): The user's UUID

        Returns:
            Optional[str]: The user's email address if user exists, None if not found
            
        Note:
            Returns None if user_id doesn't exist or if user data lacks email field.
        """
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _get_user_smartthings_data(self, user_id: str) -> Optional[Dict]:
        """
        Internal helper to retrieve the complete SmartThings data container for a user.
        
        Accesses the user's smartthings_data dictionary which contains all their SmartThings
        entities (devices, locations, rooms, capabilities, profile).

        Args:
            user_id (str): The user's UUID
            
        Returns:
            Optional[Dict]: User's smartthings_data dictionary if user exists, containing:
                - "devices": Dict of device objects keyed by device UUID
                - "locations": Dict of location objects keyed by location UUID
                - "rooms": Dict of room objects keyed by room UUID
                - "capabilities": List of capability definitions
                - "profile": User's SmartThings profile information
                Returns None if user doesn't exist.
                
        Note:
            Returns a reference to the data dict (not a copy), allowing modifications.
            All SmartThings entity operations go through this data structure.
        """
        if user_id not in self.users:
            return None
        return self.users.get(user_id, {}).get("smartthings_data")

    def _get_user_devices_data(self, user_id: str) -> Optional[Dict]:
        """
        Internal helper to retrieve a user's devices dictionary.
        
        Args:
            user_id (str): The user's UUID
            
        Returns:
            Optional[Dict]: Dictionary of device objects keyed by device UUID, or None if user not found
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("devices") if smartthings_data else None

    def _get_user_locations_data(self, user_id: str) -> Optional[Dict]:
        """
        Internal helper to retrieve a user's locations dictionary.
        
        Args:
            user_id (str): The user's UUID
            
        Returns:
            Optional[Dict]: Dictionary of location objects keyed by location UUID, or None if user not found
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("locations") if smartthings_data else None

    def _get_user_rooms_data(self, user_id: str) -> Optional[Dict]:
        """
        Internal helper to retrieve a user's rooms dictionary.
        
        Args:
            user_id (str): The user's UUID
            
        Returns:
            Optional[Dict]: Dictionary of room objects keyed by room UUID, or None if user not found
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("rooms") if smartthings_data else None

    def _get_user_capabilities_data(self, user_id: str) -> Optional[List[Dict]]:
        """
        Internal helper to retrieve a user's capabilities list.
        
        Args:
            user_id (str): The user's UUID
            
        Returns:
            Optional[List[Dict]]: List of capability definition objects, or None if user not found
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("capabilities") if smartthings_data else None

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves complete user information by user ID, including credentials.
        This method is intended for AI model context lookup during testing scenarios.
        
        Args:
            user_id (str): The unique UUID identifier of the user to retrieve.
        
        Returns:
            Dict[str, Any]: User data dictionary containing all user fields including credentials.
                Returns error dictionary if user not found with status=False and message.
        
        Notes:
            - This is a public method specifically for AI model context resolution
            - Exposes credentials intentionally for testing/simulation purposes
            - Should not be used in production environments
        """
        user_data = self.users.get(user_id)
        if not user_data:
            return {
                "status": False,
                "message": f"User with ID {user_id} not found."
            }
        
        # Return complete user data including the user_id itself
        result = {"user_id": user_id}
        result.update(user_data)
        return result


    def get_user_profile(self, user_id: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves the SmartThings profile information for a specific user.
        
        Returns the user's SmartThings profile data including account details, preferences,
        and subscription information.

        Args:
            user_id (str): The user's internal UUID identifier

        Returns:
            Dict[str, Union[bool, Dict]]: Response dictionary with structure:
                {
                    "status": bool,        # True if profile found, False otherwise
                    "profile": Dict        # Profile data if found, empty dict {} if not
                }
                Profile dictionary typically contains:
                - User account information
                - SmartThings preferences
                - Subscription details
                - Connected services
                
        Note:
            Returns {"status": False, "profile": {}} if user doesn't exist or has no profile.
            Returns a deep copy to prevent accidental modification of backend data.
            
        Example:
            >>> api = SmartThingsApis()
            >>> result = api.get_user_profile("user-uuid-123")
            >>> if result['status']:
            ...     print(f"Profile: {result['profile']}")
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        if smartthings_data and "profile" in smartthings_data:
            return {"status": True, "profile": copy.deepcopy(smartthings_data["profile"])}
        return {"status": False, "profile": {}}

    def list_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves a list of all SmartThings devices registered to a specific user.
        
        Returns complete device information for all devices in the user's SmartThings account,
        including status, capabilities, location, room assignments, and metadata.

        Args:
            user_id (str): The user's internal UUID identifier

        Returns:
            List[Dict[str, Any]]: List of device objects, each containing:
                {
                    "id": str,                      # Device UUID
                    "name": str,                    # Device display name
                    "status": str,                  # "online" or "offline"
                    "location": str,                # Location UUID (or None)
                    "room": str,                    # Room UUID (or None)
                    "components": Dict,             # Device components with capabilities
                    "capabilities": List[str],      # List of capability IDs
                    "creation_time": str,           # ISO 8601 timestamp
                    "last_activity_time": str,      # ISO 8601 timestamp
                    "powerSource": str,             # "mains", "battery", etc.
                    "healthStatus": str,            # "healthy", "degraded", "error"
                    "manufacturer": str,            # Manufacturer name
                    "model": str,                   # Model identifier
                    "firmwareVersion": str,         # Current firmware version
                    "device_online_status_last_checked": str  # ISO 8601 timestamp
                }
                Returns empty list [] if user not found or has no devices.
                
        Note:
            Returns deep copies of device objects to prevent accidental modifications.
            Devices span across all locations and rooms for the user.
            
        Example:
            >>> api = SmartThingsApis()
            >>> devices = api.list_devices("user-uuid-123")
            >>> for device in devices:
            ...     print(f"{device['name']}: {device['status']}")
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return []
        return [copy.deepcopy(d) for d in user_devices.values()]

    def get_device(self, device_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieves detailed information about a specific SmartThings device.
        
        Returns complete device data including current state, capabilities, location,
        room assignment, and metadata for a single device.

        Args:
            device_id (str): The device's UUID identifier
            user_id (str): The user's internal UUID identifier

        Returns:
            Dict[str, Any]: Device object with complete information, or error dict.
                Success response contains all device fields (see list_devices for structure).
                Error response: {"error": str} with descriptive error message.
                
        Error Cases:
            - User not found: {"error": "User with ID {user_id} not found or has no devices."}
            - Device not found: {"error": "Device {device_id} not found."}
            
        Note:
            Returns a deep copy to prevent accidental modification of backend data.
            Device must belong to the specified user.
            
        Example:
            >>> api = SmartThingsApis()
            >>> device = api.get_device("device-uuid-456", "user-uuid-123")
            >>> if "error" not in device:
            ...     print(f"Device: {device['name']}, Status: {device['status']}")
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
        Creates a new SmartThings device for a user with specified attributes.
        
        Registers a new smart home device in the user's SmartThings ecosystem. If location
        or room don't exist, they will be automatically created. Assigns capabilities and
        initial state to the device.

        Args:
            name (str): Display name for the new device.
                Example: "Living Room Light", "Front Door Lock"
            user_id (str): The user's internal UUID identifier
            location_name (Optional[str]): Name of the location for this device.
                If location doesn't exist, a new one will be created.
                Example: "Home", "Office"
                Default: None (device not assigned to location)
            room_name (Optional[str]): Name of the room for this device.
                If room doesn't exist, a new one will be created.
                Example: "Living Room", "Bedroom"
                Default: None (device not assigned to room)
            capabilities (Optional[List[str]]): List of capability IDs the device supports.
                Example: ["switch", "level"] for a dimmable light
                Example: ["lock"] for a smart lock
                Example: ["temperatureMeasurement", "thermostatMode"] for thermostat
                Default: [] (empty capabilities list)
            initial_status (Optional[Dict]): Initial state of device components and capabilities.
                Structure: {"main": {"capability_id": {"attribute": value, ...}, ...}}
                Example: {"main": {"switch": {"switch": "off"}, "level": {"level": 0}}}
                Default: {"main": {}} (empty initial state)

        Returns:
            Dict[str, Any]: Response dictionary with structure:
                {
                    "status": "success",
                    "device": {              # Complete device object
                        "id": str,           # Generated device UUID
                        "name": str,
                        "status": "online",
                        "location": str,     # Location UUID (or None)
                        "room": str,         # Room UUID (or None)
                        "components": Dict,
                        "capabilities": List[str],
                        "creation_time": str,
                        "last_activity_time": str,
                        "powerSource": "mains",
                        "healthStatus": "healthy",
                        "manufacturer": "SmartCorp",
                        "model": str,        # Generated model number
                        "firmwareVersion": "v1.0.0",
                        "device_online_status_last_checked": str
                    }
                }
                Error response: {"error": str} if user not found
                
        Side Effects:
            - Adds new device to user's devices dictionary
            - May create new location if location_name provided and doesn't exist
            - May create new room if room_name provided and doesn't exist
            - Prints confirmation messages for created locations/rooms
            - Assigns generated UUID to device
            - Sets timestamps to current time
            
        Note:
            - Auto-creates locations/rooms as needed (convenient for setup)
            - New devices start in "online" and "healthy" status
            - Default power source is "mains" (not battery)
            - Manufacturer defaults to "SmartCorp" with random model number
            
        Example:
            >>> api = SmartThingsApis()
            >>> result = api.create_device(
            ...     name="Kitchen Light",
            ...     user_id="user-uuid-123",
            ...     location_name="Home",
            ...     room_name="Kitchen",
            ...     capabilities=["switch", "level"],
            ...     initial_status={"main": {"switch": {"switch": "off"}, "level": {"level": 0}}}
            ... )
            >>> if result['status'] == 'success':
            ...     print(f"Created device: {result['device']['id']}")
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
        Updates the status of a specific device capability by sending a command.
        
        Sends control commands to device capabilities to change their state (e.g., turn lights
        on/off, lock/unlock doors, set temperature). Updates the device's last activity timestamp.

        Args:
            device_id (str): The device's UUID identifier
            component_id (str): The component ID, typically "main" for primary component
            capability_id (str): The capability ID to control. Supported capabilities:
                - "switch": On/off control
                - "level": Brightness/intensity level (0-100)
                - "lock": Lock/unlock control
                - "thermostatMode": Thermostat mode selection
                - "temperatureMeasurement": Read-only, commands not supported
            command (str): The command to send. Valid commands by capability:
                - switch: "on", "off"
                - level: "setLevel" (requires args=[level_value])
                - lock: "lock", "unlock"
                - thermostatMode: "cool", "heat", "auto", "off"
            args (Optional[List[Any]]): Arguments for the command.
                - For "setLevel": [level_value] where level_value is int or float (0-100)
                - For most other commands: None or []
                Example: [75] to set brightness to 75%
            user_id (str): The user's internal UUID identifier

        Returns:
            Dict[str, Any]: Response with updated device status or error message:
                Success: {
                    "status": "success",
                    "device_status": {      # Updated component state
                        "capability_id": {
                            "attribute": value,
                            ...
                        },
                        ...
                    }
                }
                Error: {"error": str} with descriptive error message
                
        Error Cases:
            - User not found: "User with ID {user_id} not found or has no devices."
            - Device not found: "Device {device_id} not found."
            - Invalid command: "Invalid command '{command}' for {capability_id} capability."
            - Invalid args: "Invalid command or arguments for {capability_id} capability."
            - Unsupported capability: "Capability '{capability_id}' is not supported by this handler..."
            - Component/capability not found: "Component '{component_id}' or capability '{capability_id}' not found..."
            
        Side Effects:
            - Updates device component state in memory
            - Updates device's last_activity_time to current timestamp
            - Changes persist for subsequent API calls
            
        Note:
            - temperatureMeasurement is read-only; commands will fail
            - Only capabilities listed above are implemented in this simulation
            - Real SmartThings API supports many more capabilities and commands
            - Validates command is appropriate for capability before applying
            
        Example:
            >>> api = SmartThingsApis()
            >>> # Turn on a light
            >>> result = api.update_device_status(
            ...     device_id="device-uuid",
            ...     component_id="main",
            ...     capability_id="switch",
            ...     command="on",
            ...     user_id="user-uuid"
            ... )
            >>> # Set dimmer to 75%
            >>> result = api.update_device_status(
            ...     device_id="device-uuid",
            ...     component_id="main",
            ...     capability_id="level",
            ...     command="setLevel",
            ...     args=[75],
            ...     user_id="user-uuid"
            ... )
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
                return {"error": f"Temperature measurement is read-only. Command '{command}' not supported."}

            device["last_activity_time"] = datetime.datetime.now().isoformat() + "Z"
            return {"status": "success", "device_status": copy.deepcopy(device["components"][component_id])}
        else:
            return {"error": f"Capability '{capability_id}' is not supported by this handler (only switch, level, lock, thermostatMode, temperatureMeasurement are implemented)."}
        
        return {"error": f"Component '{component_id}' or capability '{capability_id}' not found for device '{device_id}'."}

    def delete_device(self, device_id: str, user_id: str) -> Dict[str, bool]:
        """
        Deletes a SmartThings device from a user's account.
        
        Permanently removes a device from the user's SmartThings ecosystem. The device
        will no longer appear in device lists or be accessible via the API.

        Args:
            device_id (str): The device's UUID identifier to delete
            user_id (str): The user's internal UUID identifier

        Returns:
            Dict[str, bool]: Status dictionary:
                {"status": True} if device was successfully deleted
                {"status": False} if user not found or device doesn't exist
                
        Side Effects:
            - Removes device from user's devices dictionary
            - Prints confirmation message to console with device ID and user info
            - Device data is permanently lost (cannot be recovered)
            
        Note:
            - Silently returns False if device doesn't exist (idempotent operation)
            - Does NOT remove or update references in other entities (locations, rooms)
            - Real SmartThings API may have additional cleanup for automations/scenes
            
        Example:
            >>> api = SmartThingsApis()
            >>> result = api.delete_device("device-uuid-456", "user-uuid-123")
            >>> if result['status']:
            ...     print("Device deleted successfully")
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
        Retrieves the current status of a device, component, or specific capability.
        
        Queries device state without modifying it. Can retrieve status for an entire component
        or drill down to a specific capability's current state.

        Args:
            device_id (str): The device's UUID identifier
            component_id (str): The component ID to query.
                Default: "main" (primary component)
                Most devices use "main" as their primary component
            capability_id (Optional[str]): Specific capability to query.
                If None, returns all capabilities for the component.
                Example: "switch", "level", "lock", "thermostatMode"
                Default: None (return all component capabilities)
            user_id (str): The user's internal UUID identifier

        Returns:
            Dict[str, Any]: Status response or error dictionary:
                
                Success (specific capability): {
                    "status": "success",
                    "capability_status": {      # State of requested capability
                        "attribute": value,
                        ...
                    }
                }
                
                Success (entire component): {
                    "status": "success",
                    "component_status": {       # All capabilities in component
                        "capability_id_1": {...},
                        "capability_id_2": {...},
                        ...
                    }
                }
                
                Error: {"error": str} with descriptive message
                
        Error Cases:
            - User not found: "User with ID {user_id} not found or has no devices."
            - Device not found: "Device {device_id} not found."
            - Component not found: "Component '{component_id}' not found for device '{device_id}'."
            - Capability not found: "Capability '{capability_id}' not found for component..."
            
        Note:
            - Read-only operation; does not modify device state
            - Returns deep copy to prevent accidental modifications
            - Use to check device state before sending commands
            
        Example:
            >>> api = SmartThingsApis()
            >>> # Get all capabilities for main component
            >>> status = api.get_device_status(
            ...     device_id="device-uuid",
            ...     user_id="user-uuid"
            ... )
            >>> 
            >>> # Get specific capability status
            >>> switch_status = api.get_device_status(
            ...     device_id="device-uuid",
            ...     component_id="main",
            ...     capability_id="switch",
            ...     user_id="user-uuid"
            ... )
            >>> if switch_status['status'] == 'success':
            ...     print(f"Switch is {switch_status['capability_status']['switch']}")
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
        Retrieves a list of all SmartThings locations registered to a specific user.
        
        Returns all physical locations (homes, offices, etc.) where the user has SmartThings
        devices installed. Each location can contain multiple rooms and devices.

        Args:
            user_id (str): The user's internal UUID identifier

        Returns:
            List[Dict[str, Any]]: List of location objects, each containing:
                {
                    "id": str,              # Location UUID
                    "name": str,            # Location display name
                    "address": str,         # Physical address (or None)
                    "latitude": float,      # GPS latitude (or None)
                    "longitude": float      # GPS longitude (or None)
                }
                Returns empty list [] if user not found or has no locations.
                
        Note:
            Returns deep copies of location objects to prevent accidental modifications.
            Locations are independent containers for rooms and devices.
            
        Example:
            >>> api = SmartThingsApis()
            >>> locations = api.list_locations("user-uuid-123")
            >>> for location in locations:
            ...     print(f"{location['name']}: {location['address']}")
        """
        user_locations = self._get_user_locations_data(user_id)
        if user_locations is None:
            return []
        return [copy.deepcopy(loc) for loc in user_locations.values()]

    def get_location(self, location_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieves detailed information about a specific SmartThings location.
        
        Returns complete location data including name, address, and GPS coordinates
        for a single location.

        Args:
            location_id (str): The location's UUID identifier
            user_id (str): The user's internal UUID identifier

        Returns:
            Dict[str, Any]: Location object with complete information, or error dict.
                Success response contains all location fields (see list_locations for structure).
                Error response: {"error": str} with descriptive error message.
                
        Error Cases:
            - User not found: {"error": "User with ID {user_id} not found or has no locations."}
            - Location not found: {"error": "Location {location_id} not found."}
            
        Note:
            Returns a deep copy to prevent accidental modification of backend data.
            Location must belong to the specified user.
            
        Example:
            >>> api = SmartThingsApis()
            >>> location = api.get_location("location-uuid-456", "user-uuid-123")
            >>> if "error" not in location:
            ...     print(f"Location: {location['name']} at {location['address']}")
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
        Creates a new SmartThings location for a user.
        
        Registers a new physical location (home, office, etc.) in the user's SmartThings
        account. Locations serve as top-level containers for rooms and devices.

        Args:
            name (str): Display name for the new location.
                Example: "Home", "Vacation House", "Office"
                Must be unique for this user.
            user_id (str): The user's internal UUID identifier
            address (Optional[str]): Physical street address of the location.
                Example: "123 Main St, City, State 12345"
                Default: None
            latitude (Optional[float]): GPS latitude coordinate.
                Example: 37.7749
                Default: None
            longitude (Optional[float]): GPS longitude coordinate.
                Example: -122.4194
                Default: None

        Returns:
            Dict[str, Any]: Response dictionary with structure:
                Success: {
                    "status": "success",
                    "location": {         # Complete location object
                        "id": str,        # Generated location UUID
                        "name": str,
                        "address": str,   # Or None
                        "latitude": float,  # Or None
                        "longitude": float  # Or None
                    }
                }
                Error: {"error": str} with descriptive error message
                
        Error Cases:
            - User not found: {"error": "User with ID {user_id} not found or has no SmartThings data."}
            - Duplicate name: {"error": "Location with name '{name}' already exists."}
            
        Side Effects:
            - Adds new location to user's locations dictionary
            - Assigns generated UUID to location
            - Location becomes available for room and device assignment
            
        Note:
            - Location names must be unique per user
            - GPS coordinates enable location-based automations
            - Address is for display/reference only (not validated)
            
        Example:
            >>> api = SmartThingsApis()
            >>> result = api.create_location(
            ...     name="Home",
            ...     user_id="user-uuid-123",
            ...     address="123 Main St",
            ...     latitude=37.7749,
            ...     longitude=-122.4194
            ... )
            >>> if result.get('status') == 'success':
            ...     print(f"Created location: {result['location']['id']}")
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        if smartthings_data is None:
            return {"error": f"User with ID {user_id} not found or has no SmartThings data."}
        
        locations = smartthings_data.get("locations", {})
        
        
        for _, loc_data in locations.items():
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
        Updates an existing SmartThings location with new information.
        
        Modifies location properties such as name, address, or GPS coordinates. Only provided
        fields are updated; omitted fields remain unchanged.

        Args:
            location_id (str): The location's UUID identifier to update
            user_id (str): The user's internal UUID identifier
            name (Optional[str]): New display name for the location. If None, keeps existing.
                Example: "Summer Home"
            address (Optional[str]): New physical address. If None, keeps existing.
                Example: "456 Oak Ave, City, State 67890"
            latitude (Optional[float]): New GPS latitude. If None, keeps existing.
                Example: 40.7128
            longitude (Optional[float]): New GPS longitude. If None, keeps existing.
                Example: -74.0060

        Returns:
            Dict[str, Any]: Response dictionary:
                Success: {
                    "status": "success",
                    "location": Dict  # Complete updated location object
                }
                Error: {"error": str} with descriptive error message
                
        Error Cases:
            - User not found: {"error": "User with ID {user_id} not found or has no locations."}
            - Location not found: {"error": "Location {location_id} not found."}
            
        Side Effects:
            - Updates specified fields in user's locations dictionary
            - Changes persist for subsequent API calls
            - Does NOT update references in rooms or devices automatically
            
        Note:
            - Only updates fields that are explicitly provided (not None)
            - Name uniqueness is not enforced in updates (could create duplicates)
            
        Example:
            >>> api = SmartThingsApis()
            >>> result = api.update_location(
            ...     location_id="location-uuid",
            ...     user_id="user-uuid-123",
            ...     address="New Address",
            ...     latitude=40.7128
            ... )
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
        Deletes a SmartThings location and all associated rooms and devices.
        
        Permanently removes a location from the user's account. This is a cascading delete
        that also removes all rooms in the location and all devices assigned to the location.

        Args:
            location_id (str): The location's UUID identifier to delete
            user_id (str): The user's internal UUID identifier

        Returns:
            Dict[str, bool]: Status dictionary:
                {"status": True} if location was successfully deleted
                {"status": False} if user not found or location doesn't exist
                
        Side Effects:
            - Removes location from user's locations dictionary
            - Cascading delete: Removes all rooms where location_id matches
            - Cascading delete: Removes all devices where location matches
            - Prints confirmation message to console with location ID and user info
            - All related data is permanently lost (cannot be recovered)
            
        Note:
            - This is a destructive operation affecting rooms and devices
            - Silently returns False if location doesn't exist (idempotent operation)
            - Real SmartThings API may have additional cleanup for automations/scenes
            - Consider moving devices to another location before deleting
            
        Example:
            >>> api = SmartThingsApis()
            >>> result = api.delete_location("location-uuid-456", "user-uuid-123")
            >>> if result['status']:
            ...     print("Location and all contents deleted successfully")
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
        Retrieves a list of all SmartThings rooms for a user, optionally filtered by location.
        
        Returns all rooms registered in the user's SmartThings account. Rooms are logical
        groupings within locations (e.g., "Living Room", "Bedroom") where devices can be organized.

        Args:
            user_id (str): The user's internal UUID identifier
            location_id (Optional[str]): Filter to only show rooms in this specific location.
                If None, returns rooms from all locations.
                Default: None (show all rooms)

        Returns:
            List[Dict[str, Any]]: List of room objects, each containing:
                {
                    "id": str,              # Room UUID
                    "name": str,            # Room display name
                    "location_id": str      # Parent location UUID (or None)
                }
                Returns empty list [] if user not found or has no rooms.
                
        Note:
            Returns deep copies of room objects to prevent accidental modifications.
            Rooms without a location_id will be included when location_id filter is None.
            
        Example:
            >>> api = SmartThingsApis()
            >>> # Get all rooms
            >>> all_rooms = api.list_rooms("user-uuid-123")
            >>> 
            >>> # Get rooms in specific location
            >>> home_rooms = api.list_rooms("user-uuid-123", "location-uuid-456")
            >>> for room in home_rooms:
            ...     print(f"{room['name']} in location {room['location_id']}")
        """
        user_rooms = self._get_user_rooms_data(user_id)
        if user_rooms is None:
            return []
        
        filtered_rooms = []
        for _, room_data in user_rooms.items():
            if location_id is None or room_data.get("location_id") == location_id:
                filtered_rooms.append(copy.deepcopy(room_data))
        return filtered_rooms

    def get_room(self, room_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieves detailed information about a specific SmartThings room.
        
        Returns complete room data including name and location assignment for a single room.

        Args:
            room_id (str): The room's UUID identifier
            user_id (str): The user's internal UUID identifier

        Returns:
            Dict[str, Any]: Room object with complete information, or error dict.
                Success response: {
                    "id": str,
                    "name": str,
                    "location_id": str  # Or None
                }
                Error response: {"error": str} with descriptive error message.
                
        Error Cases:
            - User not found: {"error": "User with ID {user_id} not found or has no rooms."}
            - Room not found: {"error": "Room {room_id} not found."}
            
        Note:
            Returns a deep copy to prevent accidental modification of backend data.
            Room must belong to the specified user.
            
        Example:
            >>> api = SmartThingsApis()
            >>> room = api.get_room("room-uuid-789", "user-uuid-123")
            >>> if "error" not in room:
            ...     print(f"Room: {room['name']} in location {room['location_id']}")
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
        Creates a new SmartThings room for a user within a location.
        
        Registers a new room (Living Room, Bedroom, etc.) in the user's SmartThings account.
        Rooms provide logical organization for devices within a location.

        Args:
            name (str): Display name for the new room.
                Example: "Living Room", "Master Bedroom", "Kitchen"
                Must be unique within the specified location.
            user_id (str): The user's internal UUID identifier
            location_id (Optional[str]): The UUID of the location this room belongs to.
                If None, creates a room not assigned to any location.
                Default: None

        Returns:
            Dict[str, Any]: Response dictionary with structure:
                Success: {
                    "status": "success",
                    "room": {              # Complete room object
                        "id": str,         # Generated room UUID
                        "name": str,
                        "location_id": str  # Or None
                    }
                }
                Error: {"error": str} with descriptive error message
                
        Error Cases:
            - User not found: {"error": "User with ID {user_id} not found or has no SmartThings data."}
            - Duplicate name: {"error": "Room with name '{name}' already exists in this location."}
            - Invalid location: {"error": "Location with ID '{location_id}' not found."}
            
        Side Effects:
            - Adds new room to user's rooms dictionary
            - Assigns generated UUID to room
            - Room becomes available for device assignment
            
        Note:
            - Room names must be unique within each location (but can duplicate across locations)
            - location_id is validated if provided
            - Rooms can exist without a location assignment
            
        Example:
            >>> api = SmartThingsApis()
            >>> result = api.create_room(
            ...     name="Living Room",
            ...     user_id="user-uuid-123",
            ...     location_id="location-uuid-456"
            ... )
            >>> if result.get('status') == 'success':
            ...     print(f"Created room: {result['room']['id']}")
        """
        smartthings_data = self._get_user_smartthings_data(user_id)
        if smartthings_data is None:
            return {"error": f"User with ID {user_id} not found or has no SmartThings data."}
        
        rooms = smartthings_data.get("rooms", {})
        locations = smartthings_data.get("locations", {})

        
        for _, r_data in rooms.items():
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
        Updates an existing SmartThings room with new information.
        
        Modifies room properties such as name or location assignment. Only provided
        fields are updated; omitted fields remain unchanged.

        Args:
            room_id (str): The room's UUID identifier to update
            user_id (str): The user's internal UUID identifier
            name (Optional[str]): New display name for the room. If None, keeps existing.
                Example: "Master Suite"
            location_id (Optional[str]): New location UUID for the room. If None, keeps existing.
                Moving a room to a different location.

        Returns:
            Dict[str, Any]: Response dictionary:
                Success: {
                    "status": "success",
                    "room": Dict  # Complete updated room object
                }
                Error: {"error": str} with descriptive error message
                
        Error Cases:
            - User not found: {"error": "User with ID {user_id} not found or has no rooms."}
            - Room not found: {"error": "Room {room_id} not found."}
            - Invalid location: {"error": "Location with ID '{location_id}' not found."}
            
        Side Effects:
            - Updates specified fields in user's rooms dictionary
            - Changes persist for subsequent API calls
            - Devices assigned to this room are NOT automatically moved
            
        Note:
            - Only updates fields that are explicitly provided (not None)
            - location_id is validated against existing locations
            - Name uniqueness is not enforced in updates (could create duplicates)
            
        Example:
            >>> api = SmartThingsApis()
            >>> result = api.update_room(
            ...     room_id="room-uuid",
            ...     user_id="user-uuid-123",
            ...     name="Updated Room Name",
            ...     location_id="new-location-uuid"
            ... )
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
        Deletes a SmartThings room from a user's account.
        
        Permanently removes a room from the user's SmartThings ecosystem. Devices assigned
        to this room will have their room assignment cleared (set to None) but remain in the system.

        Args:
            room_id (str): The room's UUID identifier to delete
            user_id (str): The user's internal UUID identifier

        Returns:
            Dict[str, bool]: Status dictionary:
                {"status": True} if room was successfully deleted
                {"status": False} if user not found or room doesn't exist
                
        Side Effects:
            - Removes room from user's rooms dictionary
            - Clears room assignment (sets to None) for all devices in this room
            - Prints confirmation message to console with room ID and user info
            - Room data is permanently lost (cannot be recovered)
            
        Note:
            - Devices are not deleted, only their room assignment is cleared
            - Silently returns False if room doesn't exist (idempotent operation)
            - Real SmartThings API may have additional cleanup for automations/scenes
            
        Example:
            >>> api = SmartThingsApis()
            >>> result = api.delete_room("room-uuid-789", "user-uuid-123")
            >>> if result['status']:
            ...     print("Room deleted, device assignments cleared")
        """
        user_rooms = self._get_user_rooms_data(user_id)
        if user_rooms is None:
            return {"status": False}

        if room_id in user_rooms:
            
            user_devices = self._get_user_devices_data(user_id)
            if user_devices:
                for _, device_data in user_devices.items():
                    if device_data.get("room") == room_id:
                        device_data["room"] = None 
            
            del user_rooms[room_id]
            user_email = self._get_user_email_by_id(user_id)
            print(f"Room '{room_id}' deleted for user {user_id} ({user_email})")
            return {"status": True}
        return {"status": False}

    def list_capabilities(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves a list of all SmartThings capability definitions available to a user.
        
        Returns capability schemas that define what actions devices can perform and what
        attributes they expose (e.g., switch on/off, dimmer level, temperature reading).

        Args:
            user_id (str): The user's internal UUID identifier

        Returns:
            List[Dict[str, Any]]: List of capability definition objects, each containing:
                {
                    "id": str,              # Capability identifier (e.g., "switch", "level")
                    "version": int,         # Capability version number
                    "name": str,            # Human-readable name
                    "attributes": List,     # List of attribute definitions
                    "commands": List,       # List of supported commands
                    # ... other capability metadata
                }
                Returns empty list [] if user not found or has no capabilities.
                
        Note:
            Returns deep copy of capability list to prevent accidental modifications.
            Capabilities define the contract between devices and the platform.
            
        Example:
            >>> api = SmartThingsApis()
            >>> capabilities = api.list_capabilities("user-uuid-123")
            >>> for cap in capabilities:
            ...     print(f"{cap['id']} v{cap['version']}: {cap.get('name', 'N/A')}")
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
        Retrieves detailed information about a specific SmartThings capability.
        
        Returns the complete capability definition including supported commands, attributes,
        and metadata for a specific capability ID and optional version.

        Args:
            capability_id (str): The capability identifier to look up.
                Example: "switch", "level", "lock", "temperatureMeasurement"
            version (Optional[int]): Specific version of the capability.
                If None, returns any version match (typically latest).
                Default: None
            user_id (str): The user's internal UUID identifier

        Returns:
            Dict[str, Any]: Complete capability definition object, or error dict.
                Success response contains:
                {
                    "id": str,
                    "version": int,
                    "name": str,
                    "attributes": List,
                    "commands": List,
                    # ... other capability metadata
                }
                Error response: {"error": str} with descriptive error message.
                
        Error Cases:
            - User not found: {"error": "User with ID {user_id} not found or has no capabilities."}
            - Capability not found: {"error": "Capability {capability_id} not found."}
            
        Note:
            Returns a deep copy to prevent accidental modification of backend data.
            If version is None, returns first matching capability ID regardless of version.
            
        Example:
            >>> api = SmartThingsApis()
            >>> cap = api.get_capability("switch", user_id="user-uuid-123")
            >>> if "error" not in cap:
            ...     print(f"Capability: {cap['name']}")
            ...     print(f"Commands: {[cmd['name'] for cmd in cap.get('commands', [])]}")
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
        Retrieves comprehensive health status and metadata for a specific device.
        
        Returns detailed health information including online status, power source, firmware version,
        and activity timestamps. Useful for diagnostics and monitoring.

        Args:
            device_id (str): The device's UUID identifier
            user_id (str): The user's internal UUID identifier
        
        Returns:
            Dict[str, Any]: Response dictionary with structure:
                Success: {
                    "status": "success",
                    "health": {
                        "device_id": str,           # Device UUID
                        "name": str,                # Device name
                        "status": str,              # "online" or "offline"
                        "health_status": str,       # "healthy", "degraded", "error", "unknown"
                        "power_source": str,        # "mains", "battery", "unknown"
                        "manufacturer": str,
                        "model": str,
                        "firmware_version": str,
                        "last_activity_time": str,  # ISO 8601 timestamp (or None)
                        "device_online_status_last_checked": str,  # ISO 8601 timestamp (or None)
                        "creation_time": str        # ISO 8601 timestamp (or None)
                    }
                }
                Error: {"error": str} with descriptive error message
                
        Error Cases:
            - User not found: {"error": "User with ID {user_id} not found or has no devices."}
            - Device not found: {"error": "Device {device_id} not found."}
            
        Note:
            Health status indicates device reliability:
            - "healthy": Device functioning normally
            - "degraded": Device operational but with issues
            - "error": Device in error state
            - "unknown": Health status cannot be determined
            
        Example:
            >>> api = SmartThingsApis()
            >>> health = api.get_device_health("device-uuid", "user-uuid-123")
            >>> if health.get('status') == 'success':
            ...     info = health['health']
            ...     print(f"{info['name']}: {info['health_status']} ({info['status']})")
            ...     print(f"Last active: {info['last_activity_time']}")
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
        Retrieves devices filtered by their health status.
        
        Returns all devices matching a specific health status, useful for monitoring
        and identifying problematic devices.

        Args:
            health_status (str): Health status to filter by. Valid values:
                - "healthy": Devices functioning normally
                - "degraded": Devices with operational issues
                - "error": Devices in error state
                - "unknown": Devices with undetermined health
            user_id (str): The user's internal UUID identifier
        
        Returns:
            List[Dict[str, Any]]: List of device objects matching the health status.
                Each device contains complete device information (see list_devices for structure).
                Returns empty list [] if user not found or no devices match.
                
        Note:
            Returns deep copies of device objects to prevent accidental modifications.
            Health status helps prioritize maintenance and troubleshooting.
            
        Example:
            >>> api = SmartThingsApis()
            >>> # Find all devices with issues
            >>> degraded = api.list_devices_by_health_status("degraded", "user-uuid-123")
            >>> error_devices = api.list_devices_by_health_status("error", "user-uuid-123")
            >>> problematic = degraded + error_devices
            >>> print(f"Found {len(problematic)} devices needing attention")
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
        Retrieves devices filtered by manufacturer name.
        
        Returns all devices from a specific manufacturer, useful for inventory management
        and manufacturer-specific operations.

        Args:
            manufacturer (str): Manufacturer name to filter by.
                Example: "SmartCorp", "Philips", "Samsung"
                Case-sensitive exact match.
            user_id (str): The user's internal UUID identifier
        
        Returns:
            List[Dict[str, Any]]: List of device objects from the specified manufacturer.
                Each device contains complete device information (see list_devices for structure).
                Returns empty list [] if user not found or no devices match.
                
        Note:
            Returns deep copies of device objects to prevent accidental modifications.
            Manufacturer name must match exactly (case-sensitive).
            Useful for bulk operations on devices from the same manufacturer.
            
        Example:
            >>> api = SmartThingsApis()
            >>> philips_devices = api.list_devices_by_manufacturer("Philips", "user-uuid-123")
            >>> print(f"Found {len(philips_devices)} Philips devices")
            >>> for device in philips_devices:
            ...     print(f"  - {device['name']} ({device['model']})")
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
        Updates the firmware version of a device to a new version.
        
        Simulates a firmware update operation by changing the device's firmware version string
        and updating its last activity timestamp.

        Args:
            device_id (str): The device's UUID identifier
            new_version (str): New firmware version string.
                Example: "v2.1.0", "1.5.3", "2024.12.01"
            user_id (str): The user's internal UUID identifier
        
        Returns:
            Dict[str, Any]: Response dictionary with structure:
                Success: {
                    "status": "success",
                    "message": str,         # Confirmation message
                    "device_id": str,
                    "old_version": str,     # Previous firmware version
                    "new_version": str      # Updated firmware version
                }
                Error: {"error": str} with descriptive error message
                
        Error Cases:
            - User not found: {"error": "User with ID {user_id} not found or has no devices."}
            - Device not found: {"error": "Device {device_id} not found."}
            
        Side Effects:
            - Updates device's firmwareVersion field
            - Updates device's last_activity_time to current timestamp
            - Changes persist for subsequent API calls
            
        Note:
            - This is a simulation; no actual firmware is downloaded or installed
            - Real firmware updates involve complex validation, download, and installation
            - Version string format is not validated
            
        Example:
            >>> api = SmartThingsApis()
            >>> result = api.update_device_firmware(
            ...     device_id="device-uuid",
            ...     new_version="v2.0.0",
            ...     user_id="user-uuid-123"
            ... )
            >>> if result.get('status') == 'success':
            ...     print(result['message'])
            ...     print(f"Updated from {result['old_version']} to {result['new_version']}")
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
        Resets all simulated data in the backend to its initial default state.
        
        Reloads the default scenario data, clearing all user modifications including device states,
        created devices, locations, and rooms. This is a utility function for testing purposes
        and is not a standard SmartThings API endpoint.

        Returns:
            Dict[str, bool]: Status dictionary:
                {"reset_status": True} indicating successful reset
                
        Side Effects:
            - Reloads all backend data from DEFAULT_STATE scenario
            - Resets self.users with all SmartThings data (devices, locations, rooms, capabilities)
            - All user modifications are lost (device states, created entities, etc.)
            - Prints confirmation message to console
            
        Note:
            - This is a test utility method not present in real SmartThings API
            - Use for resetting test environments between test runs
            - All in-memory changes are discarded (no persistence)
            - Useful for ensuring clean state in automated testing
            
        Example:
            >>> api = SmartThingsApis()
            >>> # Make some changes...
            >>> api.create_device("Test Device", user_id="user-uuid")
            >>> # ... do some testing ...
            >>> result = api.reset_data()  # Clean slate for next test
            SmartThingsApis: All data reset to default state.
            >>> # All changes reverted, back to default state
        """
        self._load_scenario(DEFAULT_STATE)
        print("SmartThingsApis: All data reset to default state.")
        return {"reset_status": True}