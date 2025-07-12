from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# ================
# Apps
# ================

def list_apps() -> List[Dict[str, Any]]:
    """
    List all apps.

    Returns:
        List[Dict[str, Any]]: List of all apps with their details.
    """

def get_app(app_id: str) -> Dict[str, Any]:
    """
    Get a specific app.

    Args:
        app_id (str): ID of the app to retrieve.
    Returns:
        Dict[str, Any]: Details of the requested app.
    """

def create_app(app_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new app.

    Args:
        app_data (Dict[str, Any]): Data for the new app.
    Returns:
        Dict[str, Any]: Details of the created app.
    """

def update_app(app_id: str, app_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing app.

    Args:
        app_id (str): ID of the app to update.
        app_data (Dict[str, Any]): New data for the app.
    Returns:
        Dict[str, Any]: Updated details of the app.
    """

def delete_app(app_id: str) -> None:
    """
    Delete an app.

    Args:
        app_id (str): ID of the app to delete.
    """

def get_app_settings(app_id: str) -> Dict[str, Any]:
    """
    Get settings for an app.

    Args:
        app_id (str): ID of the app.
    Returns:
        Dict[str, Any]: Current settings of the app.
    """

def update_app_settings(app_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update settings for an app.

    Args:
        app_id (str): ID of the app.
        settings (Dict[str, Any]): New settings for the app.
    Returns:
        Dict[str, Any]: Updated settings of the app.
    """

def get_app_oauth(app_id: str) -> Dict[str, Any]:
    """
    Get OAuth settings for an app.

    Args:
        app_id (str): ID of the app.
    Returns:
        Dict[str, Any]: OAuth settings of the app.
    """

def update_app_oauth(app_id: str, oauth_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update OAuth settings for an app.

    Args:
        app_id (str): ID of the app.
        oauth_data (Dict[str, Any]): New OAuth settings.
    Returns:
        Dict[str, Any]: Updated OAuth settings.
    """

def get_app_oauth_metadata() -> Dict[str, Any]:
    """
    Get OAuth metadata for apps.

    Returns:
        Dict[str, Any]: OAuth metadata for all apps.
    """

# ================
# Devices
# ================

def list_devices(
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

def get_device(device_id: str) -> Dict[str, Any]:
    """
    Get a specific device.

    Args:
        device_id (str): ID of the device to retrieve.
    Returns:
        Dict[str, Any]: Details of the requested device.
    """

def get_device_status(device_id: str) -> Dict[str, Any]:
    """
    Get status of a device.

    Args:
        device_id (str): ID of the device.
    Returns:
        Dict[str, Any]: Current status of the device.
    """

def execute_device_command(
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

def get_device_health(device_id: str) -> Dict[str, Any]:
    """
    Get health status of a device.

    Args:
        device_id (str): ID of the device.
    Returns:
        Dict[str, Any]: Health status of the device.
    """

def get_device_events(
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

def create_device(device_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new device.

    Args:
        device_data (Dict[str, Any]): Data for the new device.
    Returns:
        Dict[str, Any]: Details of the created device.
    """

def delete_device(device_id: str) -> None:
    """
    Delete a device.

    Args:
        device_id (str): ID of the device to delete.
    """

def get_device_component_status(
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

# ================
# Installed Apps
# ================

def list_installed_apps() -> List[Dict[str, Any]]:
    """
    List all installed apps.

    Returns:
        List[Dict[str, Any]]: List of all installed apps.
    """

def get_installed_app(installed_app_id: str) -> Dict[str, Any]:
    """
    Get a specific installed app.

    Args:
        installed_app_id (str): ID of the installed app.
    Returns:
        Dict[str, Any]: Details of the installed app.
    """

def delete_installed_app(installed_app_id: str) -> None:
    """
    Delete an installed app.

    Args:
        installed_app_id (str): ID of the installed app to delete.
    """

def get_installed_app_config(installed_app_id: str) -> Dict[str, Any]:
    """
    Get configuration for an installed app.

    Args:
        installed_app_id (str): ID of the installed app.
    Returns:
        Dict[str, Any]: Configuration of the installed app.
    """

def update_installed_app_config(
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

# ================
# Locations
# ================

def list_locations() -> List[Dict[str, Any]]:
    """
    List all locations.

    Returns:
        List[Dict[str, Any]]: List of all locations.
    """

def get_location(location_id: str) -> Dict[str, Any]:
    """
    Get a specific location.

    Args:
        location_id (str): ID of the location.
    Returns:
        Dict[str, Any]: Details of the location.
    """

def create_location(location_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new location.

    Args:
        location_data (Dict[str, Any]): Data for the new location.
    Returns:
        Dict[str, Any]: Details of the created location.
    """

def update_location(
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

def delete_location(location_id: str) -> None:
    """
    Delete a location.

    Args:
        location_id (str): ID of the location to delete.
    """

def get_location_modes(location_id: str) -> List[Dict[str, Any]]:
    """
    Get modes for a location.

    Args:
        location_id (str): ID of the location.
    Returns:
        List[Dict[str, Any]]: List of modes for the location.
    """

def set_location_mode(location_id: str, mode_id: str) -> Dict[str, Any]:
    """
    Set the current mode for a location.

    Args:
        location_id (str): ID of the location.
        mode_id (str): ID of the mode to set.
    Returns:
        Dict[str, Any]: Updated mode information.
    """

# ================
# Rooms
# ================

def list_rooms(location_id: str) -> List[Dict[str, Any]]:
    """
    List rooms in a location.

    Args:
        location_id (str): ID of the location.
    Returns:
        List[Dict[str, Any]]: List of rooms in the location.
    """

def get_room(location_id: str, room_id: str) -> Dict[str, Any]:
    """
    Get a specific room.

    Args:
        location_id (str): ID of the location.
        room_id (str): ID of the room.
    Returns:
        Dict[str, Any]: Details of the room.
    """

def create_room(location_id: str, room_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new room.

    Args:
        location_id (str): ID of the location.
        room_data (Dict[str, Any]): Data for the new room.
    Returns:
        Dict[str, Any]: Details of the created room.
    """

def update_room(
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

def delete_room(location_id: str, room_id: str) -> None:
    """
    Delete a room.

    Args:
        location_id (str): ID of the location.
        room_id (str): ID of the room to delete.
    """

# ================
# Scenes
# ================

def list_scenes(location_id: str) -> List[Dict[str, Any]]:
    """
    List scenes in a location.

    Args:
        location_id (str): ID of the location.
    Returns:
        List[Dict[str, Any]]: List of scenes in the location.
    """

def execute_scene(location_id: str, scene_id: str) -> Dict[str, Any]:
    """
    Execute a scene.

    Args:
        location_id (str): ID of the location.
        scene_id (str): ID of the scene to execute.
    Returns:
        Dict[str, Any]: Result of the scene execution.
    """

def get_scene(location_id: str, scene_id: str) -> Dict[str, Any]:
    """
    Get a specific scene.

    Args:
        location_id (str): ID of the location.
        scene_id (str): ID of the scene.
    Returns:
        Dict[str, Any]: Details of the scene.
    """

# ================
# Subscriptions
# ================

def list_subscriptions() -> List[Dict[str, Any]]:
    """
    List all subscriptions.

    Returns:
        List[Dict[str, Any]]: List of all subscriptions.
    """

def get_subscription(subscription_id: str) -> Dict[str, Any]:
    """
    Get a specific subscription.

    Args:
        subscription_id (str): ID of the subscription.
    Returns:
        Dict[str, Any]: Details of the subscription.
    """

def create_subscription(subscription_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new subscription.

    Args:
        subscription_data (Dict[str, Any]): Data for the new subscription.
    Returns:
        Dict[str, Any]: Details of the created subscription.
    """

def delete_subscription(subscription_id: str) -> None:
    """
    Delete a subscription.

    Args:
        subscription_id (str): ID of the subscription to delete.
    """

# ================
# Schedules
# ================

def list_schedules() -> List[Dict[str, Any]]:
    """
    List all schedules.

    Returns:
        List[Dict[str, Any]]: List of all schedules.
    """

def get_schedule(schedule_id: str) -> Dict[str, Any]:
    """
    Get a specific schedule.

    Args:
        schedule_id (str): ID of the schedule.
    Returns:
        Dict[str, Any]: Details of the schedule.
    """

def create_schedule(schedule_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new schedule.

    Args:
        schedule_data (Dict[str, Any]): Data for the new schedule.
    Returns:
        Dict[str, Any]: Details of the created schedule.
    """

def delete_schedule(schedule_id: str) -> None:
    """
    Delete a schedule.

    Args:
        schedule_id (str): ID of the schedule to delete.
    """

# ================
# History
# ================

def get_device_history(
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

# ================
# Capabilities
# ================

def list_capabilities() -> List[Dict[str, Any]]:
    """
    List all capabilities.

    Returns:
        List[Dict[str, Any]]: List of all capabilities.
    """

def get_capability(
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

# ================
# Device Profiles
# ================

def list_device_profiles() -> List[Dict[str, Any]]:
    """
    List all device profiles.

    Returns:
        List[Dict[str, Any]]: List of all device profiles.
    """

def get_device_profile(profile_id: str) -> Dict[str, Any]:
    """
    Get a specific device profile.

    Args:
        profile_id (str): ID of the profile.
    Returns:
        Dict[str, Any]: Details of the profile.
    """

def create_device_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new device profile.

    Args:
        profile_data (Dict[str, Any]): Data for the new profile.
    Returns:
        Dict[str, Any]: Details of the created profile.
    """

def delete_device_profile(profile_id: str) -> None:
    """
    Delete a device profile.

    Args:
        profile_id (str): ID of the profile to delete.
    """

# ================
# Utilities
# ================

def get_schema(schema_type: str) -> Dict[str, Any]:
    """
    Get schema definition for a type.

    Args:
        schema_type (str): Type of schema to retrieve.
    Returns:
        Dict[str, Any]: Schema definition.
    """

def get_public_key(key_id: str) -> Dict[str, Any]:
    """
    Get a public key by ID.

    Args:
        key_id (str): ID of the public key.
    Returns:
        Dict[str, Any]: Public key details.
    """