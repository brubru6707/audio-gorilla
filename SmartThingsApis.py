from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from copy import deepcopy

DEFAULT_STATE = {
    "devices": {
        "device1": {"id": "device1", "name": "Smart Light", "location": "home", "status": "online"},
    },
    "locations": {
        "loc1": {"id": "loc1", "name": "Home", "timezone": "UTC"},
    },
    "rooms": {
        "room1": {"id": "room1", "name": "Living Room", "locationId": "loc1"},
    },
    "scenes": {
        "scene1": {"id": "scene1", "name": "Movie Night", "locationId": "loc1"},
    },
    "capabilities": [
        {"id": "switch", "version": 1},
        {"id": "temperature", "version": 2},
    ],
    "location_modes": {
        "loc1": [
            {"id": "mode1", "name": "Home"},
            {"id": "mode2", "name": "Away"},
        ],
    },
    "current_modes": {
        "loc1": "mode1",
    },
}

class SmartThingsAPI:
    def __init__(self):
        self.devices: Dict[str, Dict[str, Any]]
        self.locations: Dict[str, Dict[str, Any]]
        self.rooms: Dict[str, Dict[str, Any]]
        self.scenes: Dict[str, Dict[str, Any]]
        self.capabilities: List[Dict[str, Any]]
        self.location_modes: Dict[str, List[Dict[str, Any]]]
        self.current_modes: Dict[str, str]
        self._api_description = "This tool belongs to the SmartThingsAPI, which provides core functionality for managing smart home devices, locations, and scenes."
        
        self._load_default_state()
    
    def _load_default_state(self) -> None:
        """Load the default state into the API instance."""
        default_state = deepcopy(DEFAULT_STATE)
        self.devices = default_state["devices"]
        self.locations = default_state["locations"]
        self.rooms = default_state["rooms"]
        self.scenes = default_state["scenes"]
        self.capabilities = default_state["capabilities"]
        self.location_modes = default_state["location_modes"]
        self.current_modes = default_state["current_modes"]

    # ================
    # Devices
    # ================

    def list_devices(
        self,
        location_id: Optional[str] = None,
        capability: Optional[str] = None,
        device_id: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List devices with optional filters.

        Args:
            location_id (Optional[str]): Filter by location ID.
            capability (Optional[str]): Filter by capability.
            device_id (Optional[List[str]]): Filter by device IDs.
        Returns:
            List[Dict[str, Any]]: List of devices matching the filters.
        """
        devices = list(self.devices.values())
        
        if location_id:
            devices = [d for d in devices if d.get("location") == location_id]
        if device_id:
            devices = [d for d in devices if d["id"] in device_id]
        # Capability filtering would require device profiles to be implemented
        return devices

    def get_device(self, device_id: str) -> Dict[str, Any]:
        """
        Get a specific device.

        Args:
            device_id (str): ID of the device to retrieve.
        Returns:
            Dict[str, Any]: Details of the requested device.
        """
        return self.devices.get(device_id, {"error": f"Device with ID {device_id} not found"})

    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get status of a device.

        Args:
            device_id (str): ID of the device.
        Returns:
            Dict[str, Any]: Current status of the device.
        """
        if device_id not in self.devices:
            return {"error": f"Device with ID {device_id} not found"}
        return {
            "id": device_id,
            "status": self.devices[device_id].get("status", "unknown"),
            "lastUpdated": datetime.now().isoformat()
        }

    def execute_device_command(
        self,
        device_id: str,
        commands: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute commands on a device.

        Args:
            device_id (str): ID of the device.
            commands (List[Dict[str, Any]]): Commands to execute.
        Returns:
            Dict[str, Any]: Result of the command execution.
        """
        if device_id not in self.devices:
            return {"error": f"Device with ID {device_id} not found"}
        return {"deviceId": device_id, "status": "success", "commandsExecuted": len(commands)}

    def get_device_health(self, device_id: str) -> Dict[str, Any]:
        """
        Get health status of a device.

        Args:
            device_id (str): ID of the device.
        Returns:
            Dict[str, Any]: Health status of the device.
        """
        if device_id not in self.devices:
            return {"error": f"Device with ID {device_id} not found"}
        return {"id": device_id, "health": "good", "battery": 85}

    def get_device_events(
        self,
        device_id: str,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get events for a device.

        Args:
            device_id (str): ID of the device.
            limit (Optional[int]): Maximum number of events to return.
            since (Optional[datetime]): Start time for events.
            until (Optional[datetime]): End time for events.
        Returns:
            List[Dict[str, Any]]: List of device events.
        """
        if device_id not in self.devices:
            return [{"error": f"Device with ID {device_id} not found"}]
        return [{"deviceId": device_id, "event": "motion", "time": datetime.now().isoformat()}]

    def create_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new device.

        Args:
            device_data (Dict[str, Any]): Data for the new device.
        Returns:
            Dict[str, Any]: Details of the created device.
        """
        new_id = f"device{len(self.devices) + 1}"
        self.devices[new_id] = {"id": new_id, **device_data}
        return self.devices[new_id]

    def delete_device(self, device_id: str) -> None:
        """
        Delete a device.

        Args:
            device_id (str): ID of the device to delete.
        """
        if device_id in self.devices:
            del self.devices[device_id]

    def get_device_component_status(
        self,
        device_id: str,
        component_id: str
    ) -> Dict[str, Any]:
        """
        Get status of a device component.

        Args:
            device_id (str): ID of the device.
            component_id (str): ID of the component.
        Returns:
            Dict[str, Any]: Status of the component.
        """
        if device_id not in self.devices:
            return {"error": f"Device with ID {device_id} not found"}
        return {"deviceId": device_id, "componentId": component_id, "status": "active"}

    # ================
    # Locations
    # ================

    def list_locations(self) -> List[Dict[str, Any]]:
        """
        List all locations.

        Returns:
            List[Dict[str, Any]]: List of all locations.
        """
        return list(self.locations.values())

    def get_location(self, location_id: str) -> Dict[str, Any]:
        """
        Get a specific location.

        Args:
            location_id (str): ID of the location.
        Returns:
            Dict[str, Any]: Details of the location.
        """
        return self.locations.get(location_id, {"error": f"Location with ID {location_id} not found"})

    def create_location(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new location.

        Args:
            location_data (Dict[str, Any]): Data for the new location.
        Returns:
            Dict[str, Any]: Details of the created location.
        """
        new_id = f"loc{len(self.locations) + 1}"
        self.locations[new_id] = {"id": new_id, **location_data}
        return self.locations[new_id]

    def update_location(
        self,
        location_id: str,
        location_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a location.

        Args:
            location_id (str): ID of the location.
            location_data (Dict[str, Any]): New data for the location.
        Returns:
            Dict[str, Any]: Updated details of the location.
        """
        if location_id not in self.locations:
            return {"error": f"Location with ID {location_id} not found"}
        self.locations[location_id].update(location_data)
        return self.locations[location_id]

    def delete_location(self, location_id: str) -> None:
        """
        Delete a location.

        Args:
            location_id (str): ID of the location to delete.
        """
        if location_id in self.locations:
            del self.locations[location_id]

    def get_location_modes(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Get modes for a location.

        Args:
            location_id (str): ID of the location.
        Returns:
            List[Dict[str, Any]]: List of modes for the location.
        """
        return self.location_modes.get(location_id, [])

    def set_location_mode(self, location_id: str, mode_id: str) -> Dict[str, Any]:
        """
        Set the current mode for a location.

        Args:
            location_id (str): ID of the location.
            mode_id (str): ID of the mode to set.
        Returns:
            Dict[str, Any]: Updated mode information.
        """
        if location_id not in self.locations:
            return {"error": f"Location with ID {location_id} not found"}
        valid_modes = [m["id"] for m in self.location_modes.get(location_id, [])]
        if mode_id not in valid_modes:
            return {"error": f"Mode with ID {mode_id} not found for location {location_id}"}
        self.current_modes[location_id] = mode_id
        return {"locationId": location_id, "currentMode": mode_id}

    # ================
    # Rooms
    # ================

    def list_rooms(self, location_id: str) -> List[Dict[str, Any]]:
        """
        List rooms in a location.

        Args:
            location_id (str): ID of the location.
        Returns:
            List[Dict[str, Any]]: List of rooms in the location.
        """
        return [room for room in self.rooms.values() if room.get("locationId") == location_id]

    def get_room(self, location_id: str, room_id: str) -> Dict[str, Any]:
        """
        Get a specific room.

        Args:
            location_id (str): ID of the location.
            room_id (str): ID of the room.
        Returns:
            Dict[str, Any]: Details of the room.
        """
        room = self.rooms.get(room_id)
        if not room or room.get("locationId") != location_id:
            return {"error": f"Room with ID {room_id} not found in location {location_id}"}
        return room

    def create_room(self, location_id: str, room_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new room.

        Args:
            location_id (str): ID of the location.
            room_data (Dict[str, Any]): Data for the new room.
        Returns:
            Dict[str, Any]: Details of the created room.
        """
        if location_id not in self.locations:
            return {"error": f"Location with ID {location_id} not found"}
        new_id = f"room{len(self.rooms) + 1}"
        self.rooms[new_id] = {"id": new_id, "locationId": location_id, **room_data}
        return self.rooms[new_id]

    def update_room(
        self,
        location_id: str,
        room_id: str,
        room_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a room.

        Args:
            location_id (str): ID of the location.
            room_id (str): ID of the room.
            room_data (Dict[str, Any]): New data for the room.
        Returns:
            Dict[str, Any]: Updated details of the room.
        """
        if room_id not in self.rooms or self.rooms[room_id].get("locationId") != location_id:
            return {"error": f"Room with ID {room_id} not found in location {location_id}"}
        self.rooms[room_id].update(room_data)
        return self.rooms[room_id]

    def delete_room(self, location_id: str, room_id: str) -> None:
        """
        Delete a room.

        Args:
            location_id (str): ID of the location.
            room_id (str): ID of the room to delete.
        """
        if room_id in self.rooms and self.rooms[room_id].get("locationId") == location_id:
            del self.rooms[room_id]

    # ================
    # Scenes
    # ================

    def list_scenes(self, location_id: str) -> List[Dict[str, Any]]:
        """
        List scenes in a location.

        Args:
            location_id (str): ID of the location.
        Returns:
            List[Dict[str, Any]]: List of scenes in the location.
        """
        return [scene for scene in self.scenes.values() if scene.get("locationId") == location_id]

    def execute_scene(self, location_id: str, scene_id: str) -> Dict[str, Any]:
        """
        Execute a scene.

        Args:
            location_id (str): ID of the location.
            scene_id (str): ID of the scene to execute.
        Returns:
            Dict[str, Any]: Result of the scene execution.
        """
        if scene_id not in self.scenes or self.scenes[scene_id].get("locationId") != location_id:
            return {"error": f"Scene with ID {scene_id} not found in location {location_id}"}
        return {"locationId": location_id, "sceneId": scene_id, "status": "executed"}

    def get_scene(self, location_id: str, scene_id: str) -> Dict[str, Any]:
        """
        Get a specific scene.

        Args:
            location_id (str): ID of the location.
            scene_id (str): ID of the scene.
        Returns:
            Dict[str, Any]: Details of the scene.
        """
        scene = self.scenes.get(scene_id)
        if not scene or scene.get("locationId") != location_id:
            return {"error": f"Scene with ID {scene_id} not found in location {location_id}"}
        return scene

    # ================
    # Capabilities
    # ================

    def list_capabilities(self) -> List[Dict[str, Any]]:
        """
        List all capabilities.

        Returns:
            List[Dict[str, Any]]: List of all capabilities.
        """
        return self.capabilities

    def get_capability(
        self,
        capability_id: str,
        version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get a specific capability.

        Args:
            capability_id (str): ID of the capability.
            version (Optional[int]): Version of the capability.
        Returns:
            Dict[str, Any]: Details of the capability.
        """
        for cap in self.capabilities:
            if cap["id"] == capability_id and (version is None or cap.get("version") == version):
                return cap
        return {"error": f"Capability {capability_id} (version {version}) not found"}

    # ================
    # History
    # ================

    def get_device_history(
        self,
        device_id: str,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get history for a device.

        Args:
            device_id (str): ID of the device.
            limit (Optional[int]): Maximum number of history entries to return.
            since (Optional[datetime]): Start time for history.
            until (Optional[datetime]): End time for history.
        Returns:
            List[Dict[str, Any]]: List of history entries for the device.
        """
        if device_id not in self.devices:
            return [{"error": f"Device with ID {device_id} not found"}]
        return [{"deviceId": device_id, "event": "on", "time": datetime.now().isoformat()}]