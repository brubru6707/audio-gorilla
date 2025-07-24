from typing import List, Dict, Any, Optional
from datetime import datetime
from copy import deepcopy

DEFAULT_STATE = {
    "devices": {
        "device1": {
            "id": "device1",
            "name": "Living Room Light",
            "location": "loc1",
            "room": "room1",
            "status": "online",
            "components": {
                "main": {
                    "switch": {"switch": "on"},
                    "level": {"level": 80}
                }
            },
            "capabilities": ["switch", "level"]
        },
        "device2": {
            "id": "device2",
            "name": "Front Door Lock",
            "location": "loc1",
            "room": "room2",
            "status": "online",
            "components": {
                "main": {
                    "lock": {"lock": "unlocked"}
                }
            },
            "capabilities": ["lock"]
        },
        "device3": {
            "id": "device3",
            "name": "Kitchen Thermostat",
            "location": "loc1",
            "room": "room3",
            "status": "online",
            "components": {
                "main": {
                    "temperatureMeasurement": {"temperature": 22},
                    "thermostatMode": {"thermostatMode": "auto"}
                }
            },
            "capabilities": ["temperatureMeasurement", "thermostatMode"]
        },
        "device4": {
            "id": "device4",
            "name": "Bedroom Fan",
            "location": "loc2",
            "room": "room4",
            "status": "offline",
            "components": {
                "main": {
                    "switch": {"switch": "off"},
                    "fanSpeed": {"fanSpeed": 0}
                }
            },
            "capabilities": ["switch", "fanSpeed"]
        },
        "device5": {
            "id": "device5",
            "name": "Backyard Camera",
            "location": "loc2",
            "room": "room5",
            "status": "online",
            "components": {
                "main": {
                    "motionSensor": {"motion": "inactive"}
                }
            },
            "capabilities": ["motionSensor"]
        }
    },
    "locations": {
        "loc1": {
            "id": "loc1",
            "name": "Home",
            "timezone": "America/New_York",
            "latitude": 34.0522,
            "longitude": -118.2437
        },
        "loc2": {
            "id": "loc2",
            "name": "Office",
            "timezone": "America/Los_Angeles",
            "latitude": 40.7128,
            "longitude": -74.0060
        },
    },
    "rooms": {
        "room1": {"id": "room1", "name": "Living Room", "locationId": "loc1"},
        "room2": {"id": "room2", "name": "Front Hallway", "locationId": "loc1"},
        "room3": {"id": "room3", "name": "Kitchen", "locationId": "loc1"},
        "room4": {"id": "room4", "name": "Main Office", "locationId": "loc2"},
        "room5": {"id": "room5", "name": "Meeting Room", "locationId": "loc2"},
    },
    "scenes": {
        "scene1": {"id": "scene1", "name": "Movie Night", "locationId": "loc1", "actions": [{"device": "device1", "command": "off"}]},
        "scene2": {"id": "scene2", "name": "Good Morning", "locationId": "loc1", "actions": [{"device": "device1", "command": "on", "level": 50}]},
        "scene3": {"id": "scene3", "name": "Leave Office", "locationId": "loc2", "actions": [{"device": "device4", "command": "off"}]},
    },
    "capabilities": [
        {"id": "switch", "version": 1, "attributes": {"switch": {"valueType": "ENUM", "values": ["on", "off"]}}},
        {"id": "temperatureMeasurement", "version": 1, "attributes": {"temperature": {"valueType": "NUMBER", "unit": "C"}}},
        {"id": "level", "version": 1, "attributes": {"level": {"valueType": "NUMBER", "range": [0, 100]}}},
        {"id": "lock", "version": 1, "attributes": {"lock": {"valueType": "ENUM", "values": ["locked", "unlocked"]}}},
        {"id": "thermostatMode", "version": 1, "attributes": {"thermostatMode": {"valueType": "ENUM", "values": ["auto", "heat", "cool", "off"]}}},
        {"id": "fanSpeed", "version": 1, "attributes": {"fanSpeed": {"valueType": "NUMBER", "range": [0, 5]}}},
        {"id": "motionSensor", "version": 1, "attributes": {"motion": {"valueType": "ENUM", "values": ["active", "inactive"]}}},
    ],
    "location_modes": {
        "loc1": [
            {"id": "mode1", "name": "Home"},
            {"id": "mode2", "name": "Away"},
            {"id": "mode3", "name": "Night"},
        ],
        "loc2": [
            {"id": "modeA", "name": "Workday"},
            {"id": "modeB", "name": "Weekend"},
        ],
    },
    "current_modes": {
        "loc1": "mode1",
        "loc2": "modeA",
    },
}

class SmartThingsApis:
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
        capability: Optional[str] = None, # Added capability filter
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
        if capability: # Implemented capability filtering
            devices = [d for d in devices if capability in d.get("capabilities", [])]
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
        # Return full components status if available
        if "components" in self.devices[device_id]:
            return {
                "id": device_id,
                "components": deepcopy(self.devices[device_id]["components"]),
                "lastUpdated": datetime.now().isoformat()
            }
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
        
        device = self.devices[device_id]
        results = []
        for cmd in commands:
            component = cmd.get("component", "main")
            capability = cmd.get("capability")
            command = cmd.get("command")
            arguments = cmd.get("arguments", [])

            if component in device.get("components", {}):
                if capability and command:
                    # Dummy execution: update status based on command
                    if capability == "switch" and command in ["on", "off"]:
                        device["components"][component]["switch"] = {"switch": command}
                        device["status"] = "online" # Assume device comes online if commanded
                        results.append({"command": command, "status": "success"})
                    elif capability == "level" and command == "setLevel" and arguments:
                        device["components"][component]["level"] = {"level": arguments[0]}
                        results.append({"command": command, "status": "success"})
                    elif capability == "lock" and command in ["lock", "unlock"]:
                        device["components"][component]["lock"] = {"lock": command + "ed"}
                        results.append({"command": command, "status": "success"})
                    elif capability == "thermostatMode" and command == "setThermostatMode" and arguments:
                        device["components"][component]["thermostatMode"] = {"thermostatMode": arguments[0]}
                        results.append({"command": command, "status": "success"})
                    else:
                        results.append({"command": command, "status": "unsupported_command"})
                else:
                    results.append({"command": "malformed_command", "status": "failure"})
            else:
                results.append({"command": "component_not_found", "status": "failure"})

        return {"deviceId": device_id, "commandResults": results}

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
        # Enhanced health info
        return {
            "id": device_id,
            "state": self.devices[device_id].get("status", "unknown"),
            "healthStatus": "GOOD",
            "lastUpdated": datetime.now().isoformat(),
            "batteryLevel": 85 if self.devices[device_id].get("status") == "online" else None # Example battery
        }

    def get_device_events(
        self,
        device_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get events for a device.

        Args:
            device_id (str): ID of the device.
        Returns:
            List[Dict[str, Any]]: List of device events.
        """
        if device_id not in self.devices:
            return [{"error": f"Device with ID {device_id} not found"}]
        # Dummy events
        return [
            {"deviceId": device_id, "component": "main", "capability": "switch", "attribute": "switch", "value": self.devices[device_id].get("components", {}).get("main", {}).get("switch", {}).get("switch", "off"), "unit": None, "data": {}, "eventId": "event123", "time": datetime.now().isoformat()},
            {"deviceId": device_id, "component": "main", "capability": "motionSensor", "attribute": "motion", "value": "active", "unit": None, "data": {}, "eventId": "event124", "time": datetime.now().isoformat()} if device_id == "device5" else {},
        ]

    def create_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new device.

        Args:
            device_data (Dict[str, Any]): Data for the new device.
        Returns:
            Dict[str, Any]: Details of the created device.
        """
        new_id = f"device{len(self.devices) + 1}"
        full_device_data = {"id": new_id, "status": "online", "components": {}, "capabilities": [], **device_data}
        self.devices[new_id] = full_device_data
        return deepcopy(self.devices[new_id])

    def delete_device(self, device_id: str) -> Dict[str, Any]: # Changed return type to Dict for status
        """
        Delete a device.

        Args:
            device_id (str): ID of the device to delete.
        Returns:
            Dict[str, Any]: Confirmation of deletion or error.
        """
        if device_id in self.devices:
            del self.devices[device_id]
            return {"status": "success", "message": f"Device {device_id} deleted."}
        return {"status": "error", "message": f"Device {device_id} not found."}


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
        device = self.devices.get(device_id)
        if not device:
            return {"error": f"Device with ID {device_id} not found"}
        
        component_status = device.get("components", {}).get(component_id)
        if not component_status:
            return {"error": f"Component with ID {component_id} not found for device {device_id}"}
        
        return {"deviceId": device_id, "componentId": component_id, "status": deepcopy(component_status)}

    def list_locations(self) -> List[Dict[str, Any]]:
        """
        List all locations.

        Returns:
            List[Dict[str, Any]]: List of all locations.
        """
        return list(deepcopy(self.locations).values())

    def get_location(self, location_id: str) -> Dict[str, Any]:
        """
        Get a specific location.

        Args:
            location_id (str): ID of the location.
        Returns:
            Dict[str, Any]: Details of the location.
        """
        return deepcopy(self.locations.get(location_id, {"error": f"Location with ID {location_id} not found"}))

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
        return deepcopy(self.locations[new_id])

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
        return deepcopy(self.locations[location_id])

    def delete_location(self, location_id: str) -> Dict[str, Any]: # Changed return type to Dict for status
        """
        Delete a location.

        Args:
            location_id (str): ID of the location to delete.
        Returns:
            Dict[str, Any]: Confirmation of deletion or error.
        """
        if location_id in self.locations:
            del self.locations[location_id]
            # Also delete associated rooms, scenes, and modes
            self.rooms = {rid: r_data for rid, r_data in self.rooms.items() if r_data.get("locationId") != location_id}
            self.scenes = {sid: s_data for sid, s_data in self.scenes.items() if s_data.get("locationId") != location_id}
            if location_id in self.location_modes:
                del self.location_modes[location_id]
            if location_id in self.current_modes:
                del self.current_modes[location_id]

            return {"status": "success", "message": f"Location {location_id} deleted."}
        return {"status": "error", "message": f"Location {location_id} not found."}

    def get_location_modes(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Get modes for a location.

        Args:
            location_id (str): ID of the location.
        Returns:
            List[Dict[str, Any]]: List of modes for the location.
        """
        return deepcopy(self.location_modes.get(location_id, []))

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
        return {"locationId": location_id, "currentMode": mode_id, "status": "success"}

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
        return [deepcopy(room) for room in self.rooms.values() if room.get("locationId") == location_id]

    def get_room(self
, location_id: str, room_id: str) -> Dict[str, Any]:
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
        return deepcopy(room)

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
        return deepcopy(self.rooms[new_id])

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
        return deepcopy(self.rooms[room_id])

    def delete_room(self, location_id: str, room_id: str) -> Dict[str, Any]: # Changed return type to Dict for status
        """
        Delete a room.

        Args:
            location_id (str): ID of the location.
            room_id (str): ID of the room to delete.
        Returns:
            Dict[str, Any]: Confirmation of deletion or error.
        """
        if room_id in self.rooms and self.rooms[room_id].get("locationId") == location_id:
            del self.rooms[room_id]
            # Also remove devices associated with this room
            self.devices = {did: d_data for did, d_data in self.devices.items() if d_data.get("room") != room_id}
            return {"status": "success", "message": f"Room {room_id} deleted from location {location_id}."}
        return {"status": "error", "message": f"Room {room_id} not found in location {location_id}."}

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
        return [deepcopy(scene) for scene in self.scenes.values() if scene.get("locationId") == location_id]

    def execute_scene(self, location_id: str, scene_id: str) -> Dict[str, Any]:
        """
        Execute a scene.

        Args:
            location_id (str): ID of the location.
            scene_id (str): ID of the scene to execute.
        Returns:
            Dict[str, Any]: Result of the scene execution.
        """
        scene = self.scenes.get(scene_id)
        if not scene or scene.get("locationId") != location_id:
            return {"error": f"Scene with ID {scene_id} not found in location {location_id}"}
        
        # Simulate actions within the scene execution
        executed_actions = []
        for action in scene.get("actions", []):
            device_id = action.get("device")
            command = action.get("command")
            if device_id and command:
                # This calls the existing execute_device_command method
                action_result = self.execute_device_command(device_id, [{"component": "main", "capability": "switch", "command": command}])
                executed_actions.append({"device": device_id, "command": command, "result": action_result})
            else:
                executed_actions.append({"action": action, "result": "invalid_action"})

        return {"locationId": location_id, "sceneId": scene_id, "status": "executed", "executedActions": executed_actions}

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
        return deepcopy(scene)
    
    def create_scene(self, location_id: str, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new scene.

        Args:
            location_id (str): ID of the location.
            scene_data (Dict[str, Any]): Data for the new scene.
        Returns:
            Dict[str, Any]: Details of the created scene.
        """
        if location_id not in self.locations:
            return {"error": f"Location with ID {location_id} not found"}
        new_id = f"scene{len(self.scenes) + 1}"
        self.scenes[new_id] = {"id": new_id, "locationId": location_id, **scene_data}
        return deepcopy(self.scenes[new_id])

    def update_scene(
        self,
        location_id: str,
        scene_id: str,
        scene_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a scene.

        Args:
            location_id (str): ID of the location.
            scene_id (str): ID of the scene.
            scene_data (Dict[str, Any]): New data for the scene.
        Returns:
            Dict[str, Any]: Updated details of the scene.
        """
        if scene_id not in self.scenes or self.scenes[scene_id].get("locationId") != location_id:
            return {"error": f"Scene with ID {scene_id} not found in location {location_id}"}
        self.scenes[scene_id].update(scene_data)
        return deepcopy(self.scenes[scene_id])

    def delete_scene(self, location_id: str, scene_id: str) -> Dict[str, Any]: # Changed return type to Dict for status
        """
        Delete a scene.

        Args:
            location_id (str): ID of the location.
            scene_id (str): ID of the scene to delete.
        Returns:
            Dict[str, Any]: Confirmation of deletion or error.
        """
        if scene_id in self.scenes and self.scenes[scene_id].get("locationId") == location_id:
            del self.scenes[scene_id]
            return {"status": "success", "message": f"Scene {scene_id} deleted from location {location_id}."}
        return {"status": "error", "message": f"Scene {scene_id} not found in location {location_id}."}

    # ================
    # Capabilities
    # ================

    def list_capabilities(self) -> List[Dict[str, Any]]:
        """
        List all capabilities.

        Returns:
            List[Dict[str, Any]]: List of all capabilities.
        """
        return deepcopy(self.capabilities)

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
                return deepcopy(cap)
        return {"error": f"Capability {capability_id} (version {version}) not found"}