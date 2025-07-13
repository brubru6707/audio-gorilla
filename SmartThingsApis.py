from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from copy import deepcopy

DEFAULT_STATE = {
    "apps": {
        "app1": {"id": "app1", "name": "Sample App", "status": "active"},
    },
    "installed_apps": {
        "installed1": {"id": "installed1", "appId": "app1", "status": "active"},
    },
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
    "subscriptions": {
        "sub1": {"id": "sub1", "type": "device", "status": "active"},
    },
    "schedules": {
        "sched1": {"id": "sched1", "name": "Morning Routine", "cron": "0 7 * * *"},
    },
    "capabilities": [
        {"id": "switch", "version": 1},
        {"id": "temperature", "version": 2},
    ],
    "device_profiles": {
        "profile1": {"id": "profile1", "name": "Smart Light", "components": ["main"]},
    },
    "app_settings": {
        "app1": {"theme": "dark", "notifications": True},
    },
    "app_oauth": {
        "app1": {"client_id": "client123", "scopes": ["read", "write"]},
    },
    "oauth_metadata": {
        "version": "1.0",
        "endpoints": {"auth": "/oauth/auth", "token": "/oauth/token"},
    },
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
        self.apps: Dict[str, Dict[str, Any]]
        self.installed_apps: Dict[str, Dict[str, Any]]
        self.devices: Dict[str, Dict[str, Any]]
        self.locations: Dict[str, Dict[str, Any]]
        self.rooms: Dict[str, Dict[str, Any]]
        self.scenes: Dict[str, Dict[str, Any]]
        self.subscriptions: Dict[str, Dict[str, Any]]
        self.schedules: Dict[str, Dict[str, Any]]
        self.capabilities: List[Dict[str, Any]]
        self.device_profiles: Dict[str, Dict[str, Any]]
        self.app_settings: Dict[str, Dict[str, Any]]
        self.app_oauth: Dict[str, Dict[str, Any]]
        self.oauth_metadata: Dict[str, Any]
        self.location_modes: Dict[str, List[Dict[str, Any]]]
        self.current_modes: Dict[str, str]
        self._api_description = "This tool belongs to the SmartThingsAPI, which provides core functionality for managing smart home devices, apps, locations, and more."
        
        self._load_default_state()
    
    def _load_default_state(self) -> None:
        """Load the default state into the API instance."""
        default_state = deepcopy(DEFAULT_STATE)
        self.apps = default_state["apps"]
        self.installed_apps = default_state["installed_apps"]
        self.devices = default_state["devices"]
        self.locations = default_state["locations"]
        self.rooms = default_state["rooms"]
        self.scenes = default_state["scenes"]
        self.subscriptions = default_state["subscriptions"]
        self.schedules = default_state["schedules"]
        self.capabilities = default_state["capabilities"]
        self.device_profiles = default_state["device_profiles"]
        self.app_settings = default_state["app_settings"]
        self.app_oauth = default_state["app_oauth"]
        self.oauth_metadata = default_state["oauth_metadata"]
        self.location_modes = default_state["location_modes"]
        self.current_modes = default_state["current_modes"]

    # ================
    # Apps
    # ================

    def list_apps(self) -> List[Dict[str, Any]]:
        """
        List all apps.

        Returns:
            List[Dict[str, Any]]: List of all apps with their details.
        """
        return list(self.apps.values())

    def get_app(self, app_id: str) -> Dict[str, Any]:
        """
        Get a specific app.

        Args:
            app_id (str): ID of the app to retrieve.
        Returns:
            Dict[str, Any]: Details of the requested app.
        """
        return self.apps.get(app_id, {"error": f"App with ID {app_id} not found"})

    def create_app(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new app.

        Args:
            app_data (Dict[str, Any]): Data for the new app.
        Returns:
            Dict[str, Any]: Details of the created app.
        """
        new_id = f"app{len(self.apps) + 1}"
        self.apps[new_id] = {"id": new_id, **app_data}
        return self.apps[new_id]

    def update_app(self, app_id: str, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing app.

        Args:
            app_id (str): ID of the app to update.
            app_data (Dict[str, Any]): New data for the app.
        Returns:
            Dict[str, Any]: Updated details of the app.
        """
        if app_id not in self.apps:
            return {"error": f"App with ID {app_id} not found"}
        self.apps[app_id].update(app_data)
        return self.apps[app_id]

    def delete_app(self, app_id: str) -> None:
        """
        Delete an app.

        Args:
            app_id (str): ID of the app to delete.
        """
        if app_id in self.apps:
            del self.apps[app_id]

    def get_app_settings(self, app_id: str) -> Dict[str, Any]:
        """
        Get settings for an app.

        Args:
            app_id (str): ID of the app.
        Returns:
            Dict[str, Any]: Current settings of the app.
        """
        return {"id": app_id, "settings": self.app_settings.get(app_id, {})}

    def update_app_settings(self, app_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update settings for an app.

        Args:
            app_id (str): ID of the app.
            settings (Dict[str, Any]): New settings for the app.
        Returns:
            Dict[str, Any]: Updated settings of the app.
        """
        self.app_settings[app_id] = settings
        return {"id": app_id, "settings": settings}

    def get_app_oauth(self, app_id: str) -> Dict[str, Any]:
        """
        Get OAuth settings for an app.

        Args:
            app_id (str): ID of the app.
        Returns:
            Dict[str, Any]: OAuth settings of the app.
        """
        return {"id": app_id, "oauth": self.app_oauth.get(app_id, {})}

    def update_app_oauth(self, app_id: str, oauth_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update OAuth settings for an app.

        Args:
            app_id (str): ID of the app.
            oauth_data (Dict[str, Any]): New OAuth settings.
        Returns:
            Dict[str, Any]: Updated OAuth settings.
        """
        self.app_oauth[app_id] = oauth_data
        return {"id": app_id, "oauth": oauth_data}

    def get_app_oauth_metadata(self) -> Dict[str, Any]:
        """
        Get OAuth metadata for apps.

        Returns:
            Dict[str, Any]: OAuth metadata for all apps.
        """
        return self.oauth_metadata

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
    # Installed Apps
    # ================

    def list_installed_apps(self) -> List[Dict[str, Any]]:
        """
        List all installed apps.

        Returns:
            List[Dict[str, Any]]: List of all installed apps.
        """
        return list(self.installed_apps.values())

    def get_installed_app(self, installed_app_id: str) -> Dict[str, Any]:
        """
        Get a specific installed app.

        Args:
            installed_app_id (str): ID of the installed app.
        Returns:
            Dict[str, Any]: Details of the installed app.
        """
        return self.installed_apps.get(installed_app_id, {"error": f"Installed app with ID {installed_app_id} not found"})

    def delete_installed_app(self, installed_app_id: str) -> None:
        """
        Delete an installed app.

        Args:
            installed_app_id (str): ID of the installed app to delete.
        """
        if installed_app_id in self.installed_apps:
            del self.installed_apps[installed_app_id]

    def get_installed_app_config(self, installed_app_id: str) -> Dict[str, Any]:
        """
        Get configuration for an installed app.

        Args:
            installed_app_id (str): ID of the installed app.
        Returns:
            Dict[str, Any]: Configuration of the installed app.
        """
        if installed_app_id not in self.installed_apps:
            return {"error": f"Installed app with ID {installed_app_id} not found"}
        return {"id": installed_app_id, "config": {"setting1": "value1"}}

    def update_installed_app_config(
        self,
        installed_app_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update configuration for an installed app.

        Args:
            installed_app_id (str): ID of the installed app.
            config (Dict[str, Any]): New configuration data.
        Returns:
            Dict[str, Any]: Updated configuration.
        """
        if installed_app_id not in self.installed_apps:
            return {"error": f"Installed app with ID {installed_app_id} not found"}
        return {"id": installed_app_id, "config": config}

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
    # Subscriptions
    # ================

    def list_subscriptions(self) -> List[Dict[str, Any]]:
        """
        List all subscriptions.

        Returns:
            List[Dict[str, Any]]: List of all subscriptions.
        """
        return list(self.subscriptions.values())

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get a specific subscription.

        Args:
            subscription_id (str): ID of the subscription.
        Returns:
            Dict[str, Any]: Details of the subscription.
        """
        return self.subscriptions.get(subscription_id, {"error": f"Subscription with ID {subscription_id} not found"})

    def create_subscription(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new subscription.

        Args:
            subscription_data (Dict[str, Any]): Data for the new subscription.
        Returns:
            Dict[str, Any]: Details of the created subscription.
        """
        new_id = f"sub{len(self.subscriptions) + 1}"
        self.subscriptions[new_id] = {"id": new_id, **subscription_data}
        return self.subscriptions[new_id]

    def delete_subscription(self, subscription_id: str) -> None:
        """
        Delete a subscription.

        Args:
            subscription_id (str): ID of the subscription to delete.
        """
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]

    # ================
    # Schedules
    # ================

    def list_schedules(self) -> List[Dict[str, Any]]:
        """
        List all schedules.

        Returns:
            List[Dict[str, Any]]: List of all schedules.
        """
        return list(self.schedules.values())

    def get_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """
        Get a specific schedule.

        Args:
            schedule_id (str): ID of the schedule.
        Returns:
            Dict[str, Any]: Details of the schedule.
        """
        return self.schedules.get(schedule_id, {"error": f"Schedule with ID {schedule_id} not found"})

    def create_schedule(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new schedule.

        Args:
            schedule_data (Dict[str, Any]): Data for the new schedule.
        Returns:
            Dict[str, Any]: Details of the created schedule.
        """
        new_id = f"sched{len(self.schedules) + 1}"
        self.schedules[new_id] = {"id": new_id, **schedule_data}
        return self.schedules[new_id]

    def delete_schedule(self, schedule_id: str) -> None:
        """
        Delete a schedule.

        Args:
            schedule_id (str): ID of the schedule to delete.
        """
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]

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
    # Device Profiles
    # ================

    def list_device_profiles(self) -> List[Dict[str, Any]]:
        """
        List all device profiles.

        Returns:
            List[Dict[str, Any]]: List of all device profiles.
        """
        return list(self.device_profiles.values())

    def get_device_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Get a specific device profile.

        Args:
            profile_id (str): ID of the profile.
        Returns:
            Dict[str, Any]: Details of the profile.
        """
        return self.device_profiles.get(profile_id, {"error": f"Device profile with ID {profile_id} not found"})

    def create_device_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new device profile.

        Args:
            profile_data (Dict[str, Any]): Data for the new profile.
        Returns:
            Dict[str, Any]: Details of the created profile.
        """
        new_id = f"profile{len(self.device_profiles) + 1}"
        self.device_profiles[new_id] = {"id": new_id, **profile_data}
        return self.device_profiles[new_id]

    def delete_device_profile(self, profile_id: str) -> None:
        """
        Delete a device profile.

        Args:
            profile_id (str): ID of the profile to delete.
        """
        if profile_id in self.device_profiles:
            del self.device_profiles[profile_id]

    # ================
    # Utilities
    # ================

    def get_schema(self, schema_type: str) -> Dict[str, Any]:
        """
        Get schema definition for a type.

        Args:
            schema_type (str): Type of schema to retrieve.
        Returns:
            Dict[str, Any]: Schema definition.
        """
        return {"type": schema_type, "properties": {"id": {"type": "string"}}}

    def get_public_key(self, key_id: str) -> Dict[str, Any]:
        """
        Get a public key by ID.

        Args:
            key_id (str): ID of the public key.
        Returns:
            Dict[str, Any]: Public key details.
        """
        return {"id": key_id, "key": "-----BEGIN PUBLIC KEY-----...", "algorithm": "RSA"}