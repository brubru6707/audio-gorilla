from typing import List, Dict, Any, Optional
from datetime import datetime
from copy import deepcopy

DEFAULT_STATE: Dict[str, Any] = {
    "users": {
        "alice.smith@gmail.com": {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@gmail.com",
            "smartthings_data": {
                "devices": {
                    "device1": {
                        "id": "device1",
                        "name": "Living Room Lamp",
                        "location": "loc1_user1",
                        "room": "room1_user1",
                        "status": "online",
                        "components": {
                            "main": {
                                "switch": {"switch": "on"},
                                "level": {"level": 75}
                            }
                        },
                        "capabilities": ["switch", "level"]
                    },
                    "device2": {
                        "id": "device2",
                        "name": "Front Door Smart Lock",
                        "location": "loc1_user1",
                        "room": "room2_user1",
                        "status": "online",
                        "components": {
                            "main": {
                                "lock": {"lock": "locked"}
                            }
                        },
                        "capabilities": ["lock"]
                    },
                    "device3": {
                        "id": "device3",
                        "name": "Hallway Motion Sensor",
                        "location": "loc1_user1",
                        "room": "room2_user1",
                        "status": "online",
                        "components": {
                            "main": {
                                "motionSensor": {"motion": "inactive"}
                            }
                        },
                        "capabilities": ["motionSensor"]
                    },
                    "device6": {
                        "id": "device6",
                        "name": "Bedroom Blinds",
                        "location": "loc1_user1",
                        "room": "room4_user1",
                        "status": "online",
                        "components": {
                            "main": {
                                "windowShadeLevel": {"level": 0} # 0 is closed, 100 is open
                            }
                        },
                        "capabilities": ["windowShadeLevel"]
                    }
                },
                "locations": {
                    "loc1_user1": {
                        "id": "loc1_user1",
                        "name": "Alice's Primary Residence",
                        "timezone": "America/New_York",
                        "latitude": 34.0522,
                        "longitude": -118.2437
                    },
                },
                "rooms": {
                    "room1_user1": {"id": "room1_user1", "name": "Living Room", "locationId": "loc1_user1"},
                    "room2_user1": {"id": "room2_user1", "name": "Entryway", "locationId": "loc1_user1"},
                    "room3_user1": {"id": "room3_user1", "name": "Kitchen", "locationId": "loc1_user1"},
                    "room4_user1": {"id": "room4_user1", "name": "Master Bedroom", "locationId": "loc1_user1"},

                },
                "scenes": {
                    "scene1_user1": {"id": "scene1_user1", "name": "Good Night", "locationId": "loc1_user1", "actions": [{"device": "device1", "command": "off"}, {"device": "device2", "command": "locked"}, {"device": "device6", "command": "set_level", "level": 0}]},
                    "scene2_user1": {"id": "scene2_user1", "name": "Morning Coffee", "locationId": "loc1_user1", "actions": [{"device": "device1", "command": "on", "level": 40}, {"device": "device6", "command": "set_level", "level": 100}]},
                },
                "capabilities": [
                    {"id": "switch", "version": 1, "attributes": {"switch": {"valueType": "ENUM", "values": ["on", "off"]}}},
                    {"id": "temperatureMeasurement", "version": 1, "attributes": {"temperature": {"valueType": "NUMBER", "unit": "C"}}},
                    {"id": "level", "version": 1, "attributes": {"level": {"valueType": "NUMBER", "range": [0, 100]}}},
                    {"id": "lock", "version": 1, "attributes": {"lock": {"valueType": "ENUM", "values": ["locked", "unlocked"]}}},
                    {"id": "thermostatMode", "version": 1, "attributes": {"thermostatMode": {"valueType": "ENUM", "values": ["auto", "heat", "cool", "off"]}}},
                    {"id": "fanSpeed", "version": 1, "attributes": {"fanSpeed": {"valueType": "NUMBER", "range": [0, 5]}}},
                    {"id": "motionSensor", "version": 1, "attributes": {"motion": {"valueType": "ENUM", "values": ["active", "inactive"]}}},
                    {"id": "windowShadeLevel", "version": 1, "attributes": {"level": {"valueType": "NUMBER", "range": [0, 100]}}},
                    {"id": "waterSensor", "version": 1, "attributes": {"water": {"valueType": "ENUM", "values": ["wet", "dry"]}}},
                ],
                "location_modes": {
                    "loc1_user1": [
                        {"id": "mode1", "name": "Home"},
                        {"id": "mode2", "name": "Away"},
                        {"id": "mode3", "name": "Night"},
                    ],
                },
                "current_modes": {
                    "loc1_user1": "mode1",
                },
            }
        },
        "bob.johnson@outlook.com": {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@outlook.com",
            "smartthings_data": {
                "devices": {
                    "device4": {
                        "id": "device4",
                        "name": "Office Thermostat",
                        "location": "loc2_user2",
                        "room": "room5_user2",
                        "status": "online",
                        "components": {
                            "main": {
                                "temperatureMeasurement": {"temperature": 20},
                                "thermostatMode": {"thermostatMode": "cool"}
                            }
                        },
                        "capabilities": ["temperatureMeasurement", "thermostatMode"]
                    },
                    "device5": {
                        "id": "device5",
                        "name": "Conference Room Light",
                        "location": "loc2_user2",
                        "room": "room6_user2",
                        "status": "online",
                        "components": {
                            "main": {
                                "switch": {"switch": "off"},
                                "level": {"level": 0}
                            }
                        },
                        "capabilities": ["switch", "level"]
                    },
                    "device7": {
                        "id": "device7",
                        "name": "Server Room Water Sensor",
                        "location": "loc2_user2",
                        "room": "room7_user2",
                        "status": "online",
                        "components": {
                            "main": {
                                "waterSensor": {"water": "dry"}
                            }
                        },
                        "capabilities": ["waterSensor"]
                    }
                },
                "locations": {
                    "loc2_user2": {
                        "id": "loc2_user2",
                        "name": "Bob's Business Office",
                        "timezone": "America/Los_Angeles",
                        "latitude": 34.0522,
                        "longitude": -118.2437
                    },
                },
                "rooms": {
                    "room5_user2": {"id": "room5_user2", "name": "Main Office", "locationId": "loc2_user2"},
                    "room6_user2": {"id": "room6_user2", "name": "Conference Room", "locationId": "loc2_user2"},
                    "room7_user2": {"id": "room7_user2", "name": "Server Room", "locationId": "loc2_user2"},
                },
                "scenes": {
                    "scene3_user2": {"id": "scene3_user2", "name": "End of Day", "locationId": "loc2_user2", "actions": [{"device": "device4", "command": "setThermostatMode", "thermostatMode": "off"}, {"device": "device5", "command": "off"}]},
                },
                "capabilities": [
                    {"id": "switch", "version": 1, "attributes": {"switch": {"valueType": "ENUM", "values": ["on", "off"]}}},
                    {"id": "temperatureMeasurement", "version": 1, "attributes": {"temperature": {"valueType": "NUMBER", "unit": "C"}}},
                    {"id": "level", "version": 1, "attributes": {"level": {"valueType": "NUMBER", "range": [0, 100]}}},
                    {"id": "lock", "version": 1, "attributes": {"lock": {"valueType": "ENUM", "values": ["locked", "unlocked"]}}},
                    {"id": "thermostatMode", "version": 1, "attributes": {"thermostatMode": {"valueType": "ENUM", "values": ["auto", "heat", "cool", "off"]}}},
                    {"id": "fanSpeed", "version": 1, "attributes": {"fanSpeed": {"valueType": "NUMBER", "range": [0, 5]}}},
                    {"id": "motionSensor", "version": 1, "attributes": {"motion": {"valueType": "ENUM", "values": ["active", "inactive"]}}},
                    {"id": "windowShadeLevel", "version": 1, "attributes": {"level": {"valueType": "NUMBER", "range": [0, 100]}}},
                    {"id": "waterSensor", "version": 1, "attributes": {"water": {"valueType": "ENUM", "values": ["wet", "dry"]}}},
                ],
                "location_modes": {
                    "loc2_user2": [
                        {"id": "modeA", "name": "Office Hours"},
                        {"id": "modeB", "name": "After Hours"},
                    ],
                },
                "current_modes": {
                    "loc2_user2": "modeA",
                },
            }
        },
        "charlie.davis@yahoo.com": {
            "first_name": "Charlie",
            "last_name": "Davis",
            "email": "charlie.davis@yahoo.com",
            "smartthings_data": {
                "devices": {
                    "device8": {
                        "id": "device8",
                        "name": "Garage Door Opener",
                        "location": "loc3_user3",
                        "room": "room8_user3",
                        "status": "online",
                        "components": {
                            "main": {
                                "garageDoorControl": {"door": "closed"}
                            }
                        },
                        "capabilities": ["garageDoorControl"]
                    },
                    "device9": {
                        "id": "device9",
                        "name": "Kids Room Light",
                        "location": "loc3_user3",
                        "room": "room9_user3",
                        "status": "online",
                        "components": {
                            "main": {
                                "switch": {"switch": "on"},
                                "level": {"level": 60}
                            }
                        },
                        "capabilities": ["switch", "level"]
                    },
                },
                "locations": {
                    "loc3_user3": {
                        "id": "loc3_user3",
                        "name": "Charlie's Lake House",
                        "timezone": "America/Chicago",
                        "latitude": 30.2672,
                        "longitude": -97.7431
                    },
                },
                "rooms": {
                    "room8_user3": {"id": "room8_user3", "name": "Garage", "locationId": "loc3_user3"},
                    "room9_user3": {"id": "room9_user3", "name": "Kids Bedroom", "locationId": "loc3_user3"},
                },
                "scenes": {
                    "scene4_user3": {"id": "scene4_user3", "name": "Arrive Home", "locationId": "loc3_user3", "actions": [{"device": "device8", "command": "open"}]},
                    "scene5_user3": {"id": "scene5_user3", "name": "Bedtime", "locationId": "loc3_user3", "actions": [{"device": "device9", "command": "off"}]},
                },
                "capabilities": [
                    {"id": "switch", "version": 1, "attributes": {"switch": {"valueType": "ENUM", "values": ["on", "off"]}}},
                    {"id": "temperatureMeasurement", "version": 1, "attributes": {"temperature": {"valueType": "NUMBER", "unit": "C"}}},
                    {"id": "level", "version": 1, "attributes": {"level": {"valueType": "NUMBER", "range": [0, 100]}}},
                    {"id": "lock", "version": 1, "attributes": {"lock": {"valueType": "ENUM", "values": ["locked", "unlocked"]}}},
                    {"id": "thermostatMode", "version": 1, "attributes": {"thermostatMode": {"valueType": "ENUM", "values": ["auto", "heat", "cool", "off"]}}},
                    {"id": "fanSpeed", "version": 1, "attributes": {"fanSpeed": {"valueType": "NUMBER", "range": [0, 5]}}},
                    {"id": "motionSensor", "version": 1, "attributes": {"motion": {"valueType": "ENUM", "values": ["active", "inactive"]}}},
                    {"id": "windowShadeLevel", "version": 1, "attributes": {"level": {"valueType": "NUMBER", "range": [0, 100]}}},
                    {"id": "waterSensor", "version": 1, "attributes": {"water": {"valueType": "ENUM", "values": ["wet", "dry"]}}},
                    {"id": "garageDoorControl", "version": 1, "attributes": {"door": {"valueType": "ENUM", "values": ["open", "closed", "opening", "closing", "unknown"]}}},
                ],
                "location_modes": {
                    "loc3_user3": [
                        {"id": "modeX", "name": "Present"},
                        {"id": "modeY", "name": "Vacation"},
                    ],
                },
                "current_modes": {
                    "loc3_user3": "modeX",
                },
            }
        }
    },
    "current_user": "alice.smith@gmail.com",
    "smartthings_device_counter": 9,
    "smartthings_location_counter": 3,
    "smartthings_room_counter": 9,
    "smartthings_scene_counter": 5,
}

class SmartThingsApis:
    def __init__(self, state: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes the SmartThingsApis with a given state.
        If no state is provided, it uses a deep copy of the DEFAULT_STATE.
        """
        self.state: Dict[str, Any] = deepcopy(state if state is not None else DEFAULT_STATE)
        self._api_description = "This tool belongs to the SmartThingsAPI, which provides core functionality for managing smart home devices, locations, and scenes."
    
    def _get_user_smartthings_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user-specific SmartThings data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's SmartThings data, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id, {}).get("smartthings_data")

    def _get_user_devices_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get user's devices data."""
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("devices") if smartthings_data else None

    def _get_user_locations_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get user's locations data."""
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("locations") if smartthings_data else None

    def _get_user_rooms_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get user's rooms data."""
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("rooms") if smartthings_data else None

    def _get_user_scenes_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get user's scenes data."""
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("scenes") if smartthings_data else None

    def _get_user_capabilities_data(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Helper to get user's capabilities data."""
        smartthings_data = self._get_user_smartthings_data(user_id)
        # Capabilities are global in this simulation but stored per user for consistency with Gmail example
        return smartthings_data.get("capabilities") if smartthings_data else None

    def _get_user_location_modes_data(self, user_id: str) -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """Helper to get user's location modes data."""
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("location_modes") if smartthings_data else None

    def _get_user_current_modes_data(self, user_id: str) -> Optional[Dict[str, str]]:
        """Helper to get user's current modes data."""
        smartthings_data = self._get_user_smartthings_data(user_id)
        return smartthings_data.get("current_modes") if smartthings_data else None

    # ================
    # Devices
    # ================

    def list_devices(
        self,
        user_id: str = 'me',
        location_id: Optional[str] = None,
        capability: Optional[str] = None,
        device_id: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List devices with optional filters for a specific user.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.
            location_id (Optional[str]): Filter by location ID.
            capability (Optional[str]): Filter by capability.
            device_id (Optional[List[str]]): Filter by device IDs.
        Returns:
            List[Dict[str, Any]]: List of devices matching the filters.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return []
        
        devices = list(user_devices.values())
        
        if location_id:
            devices = [d for d in devices if d.get("location") == location_id]
        if device_id:
            devices = [d for d in devices if d["id"] in device_id]
        if capability:
            devices = [d for d in devices if capability in d.get("capabilities", [])]
        return deepcopy(devices)

    def get_device(self, device_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Get a specific device for a user.

        Args:
            device_id (str): ID of the device to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Details of the requested device.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"error": f"User with ID {user_id} not found or has no devices."}
        return deepcopy(user_devices.get(device_id, {"error": f"Device with ID {device_id} not found"}))

    def get_device_status(self, device_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Get status of a device for a user.

        Args:
            device_id (str): ID of the device.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Current status of the device.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"error": f"User with ID {user_id} not found or has no devices."}

        if device_id not in user_devices:
            return {"error": f"Device with ID {device_id} not found"}
        
        if "components" in user_devices[device_id]:
            return {
                "id": device_id,
                "components": deepcopy(user_devices[device_id]["components"]),
                "lastUpdated": datetime.now().isoformat()
            }
        return {
            "id": device_id,
            "status": user_devices[device_id].get("status", "unknown"),
            "lastUpdated": datetime.now().isoformat()
        }

    def execute_device_command(
        self,
        device_id: str,
        commands: List[Dict[str, Any]],
        user_id: str = 'me'
    ) -> Dict[str, Any]:
        """
        Execute commands on a device for a user.

        Args:
            device_id (str): ID of the device.
            commands (List[Dict[str, Any]]): Commands to execute.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Result of the command execution.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"error": f"User with ID {user_id} not found or has no devices."}

        if device_id not in user_devices:
            return {"error": f"Device with ID {device_id} not found"}
        
        device = user_devices[device_id]
        results = []
        for cmd in commands:
            component = cmd.get("component", "main")
            capability = cmd.get("capability")
            command = cmd.get("command")
            arguments = cmd.get("arguments", [])

            if component in device.get("components", {}):
                if capability and command:
                    if capability == "switch" and command in ["on", "off"]:
                        device["components"][component]["switch"] = {"switch": command}
                        device["status"] = "online"
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

    def get_device_health(self, device_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Get health status of a device for a user.

        Args:
            device_id (str): ID of the device.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Health status of the device.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"error": f"User with ID {user_id} not found or has no devices."}

        if device_id not in user_devices:
            return {"error": f"Device with ID {device_id} not found"}
        
        return {
            "id": device_id,
            "state": user_devices[device_id].get("status", "unknown"),
            "healthStatus": "GOOD",
            "lastUpdated": datetime.now().isoformat(),
            "batteryLevel": 85 if user_devices[device_id].get("status") == "online" else None
        }

    def get_device_events(
        self,
        device_id: str,
        user_id: str = 'me'
    ) -> List[Dict[str, Any]]:
        """
        Get events for a device for a user.

        Args:
            device_id (str): ID of the device.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            List[Dict[str, Any]]: List of device events.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return [{"error": f"User with ID {user_id} not found or has no devices."}]

        if device_id not in user_devices:
            return [{"error": f"Device with ID {device_id} not found"}]
        
        return [
            {"deviceId": device_id, "component": "main", "capability": "switch", "attribute": "switch", "value": user_devices[device_id].get("components", {}).get("main", {}).get("switch", {}).get("switch", "off"), "unit": None, "data": {}, "eventId": "event123", "time": datetime.now().isoformat()},
            {"deviceId": device_id, "component": "main", "capability": "motionSensor", "attribute": "motion", "value": "active", "unit": None, "data": {}, "eventId": "event124", "time": datetime.now().isoformat()} if device_id == "device5" else {},
        ]

    def create_device(self, device_data: Dict[str, Any], user_id: str = 'me') -> Dict[str, Any]:
        """
        Create a new device for a user.

        Args:
            device_data (Dict[str, Any]): Data for the new device.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Details of the created device.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"error": f"User with ID {user_id} not found or has no devices."}

        self.state["smartthings_device_counter"] += 1
        new_id = f"device{self.state['smartthings_device_counter']}"
        full_device_data = {"id": new_id, "status": "online", "components": {}, "capabilities": [], **device_data}
        user_devices[new_id] = full_device_data
        return deepcopy(user_devices[new_id])

    def delete_device(self, device_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Delete a device for a user.

        Args:
            device_id (str): ID of the device to delete.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Confirmation of deletion or error.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"status": "error", "message": f"User with ID {user_id} not found or has no devices."}

        if device_id in user_devices:
            del user_devices[device_id]
            return {"status": "success", "message": f"Device {device_id} deleted."}
        return {"status": "error", "message": f"Device {device_id} not found."}


    def get_device_component_status(
        self,
        device_id: str,
        component_id: str,
        user_id: str = 'me'
    ) -> Dict[str, Any]:
        """
        Get status of a device component for a user.

        Args:
            device_id (str): ID of the device.
            component_id (str): ID of the component.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Status of the component.
        """
        user_devices = self._get_user_devices_data(user_id)
        if user_devices is None:
            return {"error": f"User with ID {user_id} not found or has no devices."}

        device = user_devices.get(device_id)
        if not device:
            return {"error": f"Device with ID {device_id} not found"}
        
        component_status = device.get("components", {}).get(component_id)
        if not component_status:
            return {"error": f"Component with ID {component_id} not found for device {device_id}"}
        
        return {"deviceId": device_id, "componentId": component_id, "status": deepcopy(component_status)}

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
        return list(deepcopy(user_locations).values())

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
        return deepcopy(user_locations.get(location_id, {"error": f"Location with ID {location_id} not found"}))

    def create_location(self, location_data: Dict[str, Any], user_id: str = 'me') -> Dict[str, Any]:
        """
        Create a new location for a user.

        Args:
            location_data (Dict[str, Any]): Data for the new location.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Details of the created location.
        """
        user_locations = self._get_user_locations_data(user_id)
        if user_locations is None:
            return {"error": f"User with ID {user_id} not found or has no locations."}
        
        self.state["smartthings_location_counter"] += 1
        new_id = f"loc{self.state['smartthings_location_counter']}_{user_id.split('@')[0]}"
        user_locations[new_id] = {"id": new_id, **location_data}
        return deepcopy(user_locations[new_id])

    def update_location(
        self,
        location_id: str,
        location_data: Dict[str, Any],
        user_id: str = 'me'
    ) -> Dict[str, Any]:
        """
        Update a location for a user.

        Args:
            location_id (str): ID of the location.
            location_data (Dict[str, Any]): New data for the location.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Updated details of the location.
        """
        user_locations = self._get_user_locations_data(user_id)
        if user_locations is None:
            return {"error": f"User with ID {user_id} not found or has no locations."}

        if location_id not in user_locations:
            return {"error": f"Location with ID {location_id} not found"}
        user_locations[location_id].update(location_data)
        return deepcopy(user_locations[location_id])

    def delete_location(self, location_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Delete a location for a user.

        Args:
            location_id (str): ID of the location to delete.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Confirmation of deletion or error.
        """
        user_locations = self._get_user_locations_data(user_id)
        user_rooms = self._get_user_rooms_data(user_id)
        user_scenes = self._get_user_scenes_data(user_id)
        user_location_modes = self._get_user_location_modes_data(user_id)
        user_current_modes = self._get_user_current_modes_data(user_id)

        if user_locations is None:
            return {"status": "error", "message": f"User with ID {user_id} not found or has no locations."}

        if location_id in user_locations:
            del user_locations[location_id]
            
            if user_rooms:
                user_rooms = {rid: r_data for rid, r_data in user_rooms.items() if r_data.get("locationId") != location_id}
            if user_scenes:
                user_scenes = {sid: s_data for sid, s_data in user_scenes.items() if s_data.get("locationId") != location_id}
            if user_location_modes and location_id in user_location_modes:
                del user_location_modes[location_id]
            if user_current_modes and location_id in user_current_modes:
                del user_current_modes[location_id]

            # Update the state after filtering
            if self._get_user_smartthings_data(user_id):
                if user_rooms is not None:
                    self._get_user_smartthings_data(user_id)["rooms"] = user_rooms
                if user_scenes is not None:
                    self._get_user_smartthings_data(user_id)["scenes"] = user_scenes
                if user_location_modes is not None:
                    self._get_user_smartthings_data(user_id)["location_modes"] = user_location_modes
                if user_current_modes is not None:
                    self._get_user_smartthings_data(user_id)["current_modes"] = user_current_modes

            return {"status": "success", "message": f"Location {location_id} deleted."}
        return {"status": "error", "message": f"Location {location_id} not found."}

    def get_location_modes(self, location_id: str, user_id: str = 'me') -> List[Dict[str, Any]]:
        """
        Get modes for a location for a user.

        Args:
            location_id (str): ID of the location.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            List[Dict[str, Any]]: List of modes for the location.
        """
        user_location_modes = self._get_user_location_modes_data(user_id)
        if user_location_modes is None:
            return []
        return deepcopy(user_location_modes.get(location_id, []))

    def set_location_mode(self, location_id: str, mode_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Set the current mode for a location for a user.

        Args:
            location_id (str): ID of the location.
            mode_id (str): ID of the mode to set.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Updated mode information.
        """
        user_locations = self._get_user_locations_data(user_id)
        user_location_modes = self._get_user_location_modes_data(user_id)
        user_current_modes = self._get_user_current_modes_data(user_id)

        if user_locations is None or user_location_modes is None or user_current_modes is None:
            return {"error": f"User with ID {user_id} not found or missing data."}

        if location_id not in user_locations:
            return {"error": f"Location with ID {location_id} not found"}
        valid_modes = [m["id"] for m in user_location_modes.get(location_id, [])]
        if mode_id not in valid_modes:
            return {"error": f"Mode with ID {mode_id} not found for location {location_id}"}
        user_current_modes[location_id] = mode_id
        return {"locationId": location_id, "currentMode": mode_id, "status": "success"}

    # ================
    # Rooms
    # ================

    def list_rooms(self, location_id: str, user_id: str = 'me') -> List[Dict[str, Any]]:
        """
        List rooms in a location for a user.

        Args:
            location_id (str): ID of the location.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            List[Dict[str, Any]]: List of rooms in the location.
        """
        user_rooms = self._get_user_rooms_data(user_id)
        if user_rooms is None:
            return []
        return [deepcopy(room) for room in user_rooms.values() if room.get("locationId") == location_id]

    def get_room(self, location_id: str, room_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Get a specific room for a user.

        Args:
            location_id (str): ID of the location.
            room_id (str): ID of the room.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Details of the room.
        """
        user_rooms = self._get_user_rooms_data(user_id)
        if user_rooms is None:
            return {"error": f"User with ID {user_id} not found or has no rooms."}

        room = user_rooms.get(room_id)
        if not room or room.get("locationId") != location_id:
            return {"error": f"Room with ID {room_id} not found in location {location_id}"}
        return deepcopy(room)

    def create_room(self, location_id: str, room_data: Dict[str, Any], user_id: str = 'me') -> Dict[str, Any]:
        """
        Create a new room for a user.

        Args:
            location_id (str): ID of the location.
            room_data (Dict[str, Any]): Data for the new room.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Details of the created room.
        """
        user_locations = self._get_user_locations_data(user_id)
        user_rooms = self._get_user_rooms_data(user_id)
        if user_locations is None or user_rooms is None:
            return {"error": f"User with ID {user_id} not found or missing data."}

        if location_id not in user_locations:
            return {"error": f"Location with ID {location_id} not found"}
        
        self.state["smartthings_room_counter"] += 1
        new_id = f"room{self.state['smartthings_room_counter']}_{user_id.split('@')[0]}"
        user_rooms[new_id] = {"id": new_id, "locationId": location_id, **room_data}
        return deepcopy(user_rooms[new_id])

    def update_room(
        self,
        location_id: str,
        room_id: str,
        room_data: Dict[str, Any],
        user_id: str = 'me'
    ) -> Dict[str, Any]:
        """
        Update a room for a user.

        Args:
            location_id (str): ID of the location.
            room_id (str): ID of the room.
            room_data (Dict[str, Any]): New data for the room.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Updated details of the room.
        """
        user_rooms = self._get_user_rooms_data(user_id)
        if user_rooms is None:
            return {"error": f"User with ID {user_id} not found or has no rooms."}

        if room_id not in user_rooms or user_rooms[room_id].get("locationId") != location_id:
            return {"error": f"Room with ID {room_id} not found in location {location_id}"}
        user_rooms[room_id].update(room_data)
        return deepcopy(user_rooms[room_id])

    def delete_room(self, location_id: str, room_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Delete a room for a user.

        Args:
            location_id (str): ID of the location.
            room_id (str): ID of the room to delete.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Confirmation of deletion or error.
        """
        user_rooms = self._get_user_rooms_data(user_id)
        user_devices = self._get_user_devices_data(user_id)

        if user_rooms is None:
            return {"status": "error", "message": f"User with ID {user_id} not found or has no rooms."}

        if room_id in user_rooms and user_rooms[room_id].get("locationId") == location_id:
            del user_rooms[room_id]
            # Also remove devices associated with this room
            if user_devices:
                self._get_user_smartthings_data(user_id)["devices"] = {did: d_data for did, d_data in user_devices.items() if d_data.get("room") != room_id}
            return {"status": "success", "message": f"Room {room_id} deleted from location {location_id}."}
        return {"status": "error", "message": f"Room {room_id} not found in location {location_id}."}

    # ================
    # Scenes
    # ================

    def list_scenes(self, location_id: str, user_id: str = 'me') -> List[Dict[str, Any]]:
        """
        List scenes in a location for a user.

        Args:
            location_id (str): ID of the location.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            List[Dict[str, Any]]: List of scenes in the location.
        """
        user_scenes = self._get_user_scenes_data(user_id)
        if user_scenes is None:
            return []
        return [deepcopy(scene) for scene in user_scenes.values() if scene.get("locationId") == location_id]

    def execute_scene(self, location_id: str, scene_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Execute a scene for a user.

        Args:
            location_id (str): ID of the location.
            scene_id (str): ID of the scene to execute.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Result of the scene execution.
        """
        user_scenes = self._get_user_scenes_data(user_id)
        if user_scenes is None:
            return {"error": f"User with ID {user_id} not found or has no scenes."}

        scene = user_scenes.get(scene_id)
        if not scene or scene.get("locationId") != location_id:
            return {"error": f"Scene with ID {scene_id} not found in location {location_id}"}
        
        executed_actions = []
        for action in scene.get("actions", []):
            device_id = action.get("device")
            command = action.get("command")
            if device_id and command:
                action_result = self.execute_device_command(device_id, [{"component": "main", "capability": "switch", "command": command}], user_id=user_id)
                executed_actions.append({"device": device_id, "command": command, "result": action_result})
            else:
                executed_actions.append({"action": action, "result": "invalid_action"})

        return {"locationId": location_id, "sceneId": scene_id, "status": "executed", "executedActions": executed_actions}

    def get_scene(self, location_id: str, scene_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Get a specific scene for a user.

        Args:
            location_id (str): ID of the location.
            scene_id (str): ID of the scene.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Details of the scene.
        """
        user_scenes = self._get_user_scenes_data(user_id)
        if user_scenes is None:
            return {"error": f"User with ID {user_id} not found or has no scenes."}

        scene = user_scenes.get(scene_id)
        if not scene or scene.get("locationId") != location_id:
            return {"error": f"Scene with ID {scene_id} not found in location {location_id}"}
        return deepcopy(scene)
    
    def create_scene(self, location_id: str, scene_data: Dict[str, Any], user_id: str = 'me') -> Dict[str, Any]:
        """
        Create a new scene for a user.

        Args:
            location_id (str): ID of the location.
            scene_data (Dict[str, Any]): Data for the new scene.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Details of the created scene.
        """
        user_locations = self._get_user_locations_data(user_id)
        user_scenes = self._get_user_scenes_data(user_id)
        if user_locations is None or user_scenes is None:
            return {"error": f"User with ID {user_id} not found or missing data."}

        if location_id not in user_locations:
            return {"error": f"Location with ID {location_id} not found"}
        
        self.state["smartthings_scene_counter"] += 1
        new_id = f"scene{self.state['smartthings_scene_counter']}_{user_id.split('@')[0]}"
        user_scenes[new_id] = {"id": new_id, "locationId": location_id, **scene_data}
        return deepcopy(user_scenes[new_id])

    def update_scene(
        self,
        location_id: str,
        scene_id: str,
        scene_data: Dict[str, Any],
        user_id: str = 'me'
    ) -> Dict[str, Any]:
        """
        Update a scene for a user.

        Args:
            location_id (str): ID of the location.
            scene_id (str): ID of the scene.
            scene_data (Dict[str, Any]): New data for the scene.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Updated details of the scene.
        """
        user_scenes = self._get_user_scenes_data(user_id)
        if user_scenes is None:
            return {"error": f"User with ID {user_id} not found or has no scenes."}

        if scene_id not in user_scenes or user_scenes[scene_id].get("locationId") != location_id:
            return {"error": f"Scene with ID {scene_id} not found in location {location_id}"}
        user_scenes[scene_id].update(scene_data)
        return deepcopy(user_scenes[scene_id])

    def delete_scene(self, location_id: str, scene_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Delete a scene for a user.

        Args:
            location_id (str): ID of the location.
            scene_id (str): ID of the scene to delete.
            user_id (str): User's email address or 'me' for the authenticated user.
        Returns:
            Dict[str, Any]: Confirmation of deletion or error.
        """
        user_scenes = self._get_user_scenes_data(user_id)
        if user_scenes is None:
            return {"status": "error", "message": f"User with ID {user_id} not found or has no scenes."}

        if scene_id in user_scenes and user_scenes[scene_id].get("locationId") == location_id:
            del user_scenes[scene_id]
            return {"status": "success", "message": f"Scene {scene_id} deleted from location {location_id}."}
        return {"status": "error", "message": f"Scene {scene_id} not found in location {location_id}."}

    # ================
    # Capabilities
    # ================

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
        return deepcopy(user_capabilities)

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
                return deepcopy(cap)
        return {"error": f"Capability {capability_id} (version {version}) not found"}