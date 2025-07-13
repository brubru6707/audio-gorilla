from typing import Dict, List, Any
from copy import deepcopy

DEFAULT_STATE = {
    "vehicles": {},
    "vehicle_counter": 0,
}

class TeslaFleetApis:
    def __init__(self):
        self.vehicles: Dict[str, Dict[str, Any]]
        self.vehicle_counter: int
        self._api_description = "This tool belongs to the TeslaFleetAPI, which provides core functionality for controlling Tesla vehicles remotely."
        
    def _load_scenario(self, scenario: dict) -> None:
        """
        Load a scenario into the TeslaFleetApis instance.
        Args:
            scenario (dict): A dictionary containing vehicle data.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.vehicles = scenario.get("vehicles", DEFAULT_STATE_COPY["vehicles"])
        self.vehicle_counter = scenario.get("vehicle_counter", DEFAULT_STATE_COPY["vehicle_counter"])
    
    def _get_vehicle(self, vehicle_tag: str) -> Dict[str, Any]:
        """Helper method to get vehicle or create if not exists"""
        if vehicle_tag not in self.vehicles:
            self.vehicles[vehicle_tag] = {
                "horn": False,
                "media": {
                    "playing": False,
                    "volume": 50,
                    "current_track": 0,
                    "favorites": []
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
                    "driver_temp": 21,
                    "passenger_temp": 21,
                    "steering_wheel_heater": False,
                    "seat_heaters": {}
                },
                "doors": {
                    "locked": True
                },
                "sentry_mode": False,
                "valet_mode": False,
                "sunroof": "closed",
                "windows": "closed",
                "software_update": {
                    "scheduled": False,
                    "offset_sec": 0
                },
                "awake": True
            }
        return self.vehicles[vehicle_tag]

    def honk_horn(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Honk the horn of the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["horn"] = True
        return {"success": True}

    def media_next_fav(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Skip to the next favorite media item in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        if vehicle["media"]["favorites"]:
            current_index = vehicle["media"]["current_track"] % len(vehicle["media"]["favorites"])
            vehicle["media"]["current_track"] = (current_index + 1) % len(vehicle["media"]["favorites"])
        return {"success": True}

    def media_prev_fav(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Skip to the previous favorite media item in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        if vehicle["media"]["favorites"]:
            current_index = vehicle["media"]["current_track"] % len(vehicle["media"]["favorites"])
            vehicle["media"]["current_track"] = (current_index - 1) % len(vehicle["media"]["favorites"])
        return {"success": True}

    def media_prev_track(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Skip to the previous track in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["media"]["current_track"] -= 1
        return {"success": True}

    def media_toggle_playback(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Toggle media playback in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["media"]["playing"] = not vehicle["media"]["playing"]
        return {"success": True}

    def media_volume_down(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Decrease the media volume in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["media"]["volume"] = max(0, vehicle["media"]["volume"] - 5)
        return {"success": True}

    def remote_boombox(self, vehicle_tag: str, sound_id: int) -> Dict[str, bool]:
        """
        Activate the remote boombox feature with the specified sound.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            sound_id (int): The ID of the sound to play.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        # In a real implementation, we would play the sound with the given ID
        return {"success": True}

    def actuate_trunk(self, vehicle_tag: str, which_trunk: str) -> Dict[str, bool]:
        """
        Open or close the specified trunk.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            which_trunk (str): The trunk to actuate ("front" or "rear").

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        if which_trunk in ["front", "rear"]:
            current_state = vehicle["trunk"][which_trunk]
            vehicle["trunk"][which_trunk] = "open" if current_state == "closed" else "closed"
            return {"success": True}
        return {"success": False}

    def charge_port_door_close(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Close the charge port door of the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["charge"]["port_open"] = False
        return {"success": True}

    def charge_port_door_open(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Open the charge port door of the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["charge"]["port_open"] = True
        return {"success": True}

    def charge_max_range(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Set the charge limit to max range for the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["charge"]["limit"] = 100
        return {"success": True}

    def charge_standard(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Set the charge limit to standard for the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["charge"]["limit"] = 80
        return {"success": True}

    def charge_start(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Start charging the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["charge"]["charging"] = True
        return {"success": True}

    def charge_stop(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Stop charging the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["charge"]["charging"] = False
        return {"success": True}

    def set_charge_limit(self, vehicle_tag: str, percent: int) -> Dict[str, bool]:
        """
        Set the charge limit to a specific percentage for the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            percent (int): The charge limit percentage to set.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["charge"]["limit"] = max(0, min(100, percent))
        return {"success": True}

    def auto_conditioning_start(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Start the auto conditioning system in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["on"] = True
        return {"success": True}

    def auto_conditioning_stop(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Stop the auto conditioning system in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["on"] = False
        return {"success": True}

    def set_bioweapon_mode(self, vehicle_tag: str, on: bool, manual_override: bool) -> Dict[str, bool]:
        """
        Enable or disable bioweapon defense mode in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): True to enable, False to disable.
            manual_override (bool): True to override manual settings, False otherwise.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["bioweapon_mode"] = on
        return {"success": True}

    def set_climate_keeper_mode(self, vehicle_tag: str, climate_keeper_mode: str) -> Dict[str, bool]:
        """
        Set the climate keeper mode in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            climate_keeper_mode (str): The climate keeper mode to set.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["climate_keeper_mode"] = climate_keeper_mode
        return {"success": True}

    def set_cop_temp(self, vehicle_tag: str, cop_temp: float) -> Dict[str, bool]:
        """
        Set the cabin overheat protection temperature in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            cop_temp (float): The temperature to set for cabin overheat protection.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["cop_temp"] = cop_temp
        return {"success": True}

    def set_heated_seat(self, vehicle_tag: str, heater: str, level: int) -> Dict[str, bool]:
        """
        Set the heated seat level in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            heater (str): The seat heater to adjust.
            level (int): The heat level to set (0-3).

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["seat_heaters"][heater] = max(0, min(3, level))
        return {"success": True}

    def set_preconditioning_max(self, vehicle_tag: str, on: bool, manual_override: bool) -> Dict[str, bool]:
        """
        Enable or disable maximum preconditioning in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): True to enable, False to disable.
            manual_override (bool): True to override manual settings, False otherwise.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        # In a real implementation, we would handle the preconditioning logic
        return {"success": True}

    def set_steering_wheel_heater(self, vehicle_tag: str, on: bool) -> Dict[str, bool]:
        """
        Enable or disable the steering wheel heater in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): True to enable, False to disable.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["steering_wheel_heater"] = on
        return {"success": True}

    def set_temps(self, vehicle_tag: str, driver_temp: float, passenger_temp: float) -> Dict[str, bool]:
        """
        Set the driver and passenger temperatures in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            driver_temp (float): The temperature to set for the driver side.
            passenger_temp (float): The temperature to set for the passenger side.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["driver_temp"] = driver_temp
        vehicle["climate"]["passenger_temp"] = passenger_temp
        return {"success": True}

    def door_lock(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Lock the doors of the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["doors"]["locked"] = True
        return {"success": True}

    def door_unlock(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Unlock the doors of the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["doors"]["locked"] = False
        return {"success": True}

    def remote_start_drive(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Remotely start the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        # In a real implementation, we would start the vehicle
        return {"success": True}

    def reset_valet_pin(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Reset the valet pin for the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        # In a real implementation, we would reset the valet pin
        return {"success": True}

    def set_sentry_mode(self, vehicle_tag: str, on: bool) -> Dict[str, bool]:
        """
        Enable or disable sentry mode in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): True to enable, False to disable.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["sentry_mode"] = on
        return {"success": True}

    def set_valet_mode(self, vehicle_tag: str, on: bool, password: str) -> Dict[str, bool]:
        """
        Enable or disable valet mode in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): True to enable, False to disable.
            password (str): The password to set for valet mode.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["valet_mode"] = on
        return {"success": True}

    def adjust_volume(self, vehicle_tag: str, volume: int) -> Dict[str, bool]:
        """
        Adjust the media volume to a specific level in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            volume (int): The volume level to set.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["media"]["volume"] = max(0, min(100, volume))
        return {"success": True}

    def navigation_request(self, vehicle_tag: str, text: str, locale: str, timestamp_ms: int) -> Dict[str, bool]:
        """
        Send a navigation request to the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            text (str): The navigation destination text.
            locale (str): The locale for the navigation request.
            timestamp_ms (int): The timestamp in milliseconds.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        # In a real implementation, we would set the navigation destination
        return {"success": True}

    def share(self, vehicle_tag: str, type: str, value: str, locale: str, timestamp_ms: int) -> Dict[str, bool]:
        """
        Share content with the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            type (str): The type of content to share.
            value (str): The content value to share.
            locale (str): The locale for the shared content.
            timestamp_ms (int): The timestamp in milliseconds.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        # In a real implementation, we would handle the shared content
        return {"success": True}

    def sun_roof_control(self, vehicle_tag: str, state: str) -> Dict[str, bool]:
        """
        Control the sunroof of the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            state (str): The desired state of the sunroof.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["sunroof"] = state
        return {"success": True}

    def trigger_homelink(self, vehicle_tag: str, lat: float, lon: float, token: str) -> Dict[str, bool]:
        """
        Trigger Homelink for the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            lat (float): The latitude coordinate.
            lon (float): The longitude coordinate.
            token (str): The Homelink token.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        # In a real implementation, we would trigger Homelink
        return {"success": True}

    def wake_up(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Wake up the specified vehicle from sleep mode.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["awake"] = True
        return {"success": True}

    def window_control(self, vehicle_tag: str, command: str, lat: float, lon: float) -> Dict[str, bool]:
        """
        Control the windows of the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            command (str): The window control command.
            lat (float): The latitude coordinate.
            lon (float): The longitude coordinate.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["windows"] = command
        return {"success": True}

    def cancel_software_update(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Cancel a pending software update for the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["software_update"]["scheduled"] = False
        return {"success": True}

    def schedule_software_update(self, vehicle_tag: str, offset_sec: int) -> Dict[str, bool]:
        """
        Schedule a software update for the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            offset_sec (int): The delay in seconds before installing the update.

        Returns:
            success (bool): True if the command was successful, False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["software_update"]["scheduled"] = True
        vehicle["software_update"]["offset_sec"] = offset_sec
        return {"success": True}