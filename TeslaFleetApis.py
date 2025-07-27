import datetime
import copy
from typing import Dict, List, Any, Optional, Union

DEFAULT_STATE: Dict[str, Any] = {
    "users": {
        "alice.smith@mail.com": {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@mail.com",
            "friends": ["bob.johnson@mail.com"],
            "tesla_data": {
                "vehicles": {
                    "alice_model_3": {
                        "vehicle_tag": "5YJ3E1EA2PF330316",
                        "horn": False,
                        "media": {
                            "playing": False,
                            "volume": 50,
                            "current_track": 0,
                            "favorites": ["The Commute Playlist", "Driving Rock Anthems", "Chill Acoustic Vibes"]
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
                            "seat_heaters": {"driver_front": 0, "passenger_front": 0}
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
                    },
                    "alice_model_s": {
                        "vehicle_tag": "5YJ3E1EH4PF000316",
                        "horn": False,
                        "media": {
                            "playing": True,
                            "volume": 75,
                            "current_track": 1,
                            "favorites": ["Tech News Daily", "True Crime Stories", "Morning Motivation"]
                        },
                        "trunk": {
                            "front": "closed",
                            "rear": "open"
                        },
                        "charge": {
                            "port_open": True,
                            "charging": True,
                            "limit": 90
                        },
                        "climate": {
                            "on": True,
                            "bioweapon_mode": False,
                            "climate_keeper_mode": "dog_mode",
                            "cop_temp": 35,
                            "driver_temp": 22,
                            "passenger_temp": 22,
                            "steering_wheel_heater": True,
                            "seat_heaters": {"driver_front": 2, "passenger_front": 1}
                        },
                        "doors": {
                            "locked": False
                        },
                        "sentry_mode": True,
                        "valet_mode": False,
                        "sunroof": "vent",
                        "windows": "open",
                        "software_update": {
                            "scheduled": True,
                            "offset_sec": 3600
                        },
                        "awake": True
                    }
                },
                "vehicle_counter": 2,
                "notes": {
                    "note_1": "Alice's primary vehicle is the Model 3 for daily commuting.",
                    "note_2": "Model S is primarily used for family trips and long-distance travel."
                }
            }
        },
        "bob.johnson@mail.com": {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@mail.com",
            "friends": ["alice.smith@mail.com", "charlie.brown@mail.com"],
            "tesla_data": {
                "vehicles": {
                    "bob_cybertruck": {
                        "vehicle_tag": "5YJSA1HC0RF005789",
                        "horn": False,
                        "media": {
                            "playing": False,
                            "volume": 60,
                            "current_track": 0,
                            "favorites": ["Heavy Metal Mix", "Off-Roading Anthems"]
                        },
                        "trunk": {
                            "front": "closed",
                            "rear": "closed" # Cybertruck has a vault, not a typical trunk
                        },
                        "charge": {
                            "port_open": False,
                            "charging": False,
                            "limit": 85
                        },
                        "climate": {
                            "on": True,
                            "bioweapon_mode": True,
                            "climate_keeper_mode": "camp_mode",
                            "cop_temp": 25,
                            "driver_temp": 23,
                            "passenger_temp": 23,
                            "steering_wheel_heater": True,
                            "seat_heaters": {"driver_front": 1, "passenger_front": 1}
                        },
                        "doors": {
                            "locked": True
                        },
                        "sentry_mode": True,
                        "valet_mode": False,
                        "sunroof": "closed", # Cybertruck has a glass roof, not a sunroof
                        "windows": "closed",
                        "software_update": {
                            "scheduled": False,
                            "offset_sec": 0
                        },
                        "awake": True
                    }
                },
                "vehicle_counter": 1,
                "notes": {
                    "note_3": "Bob just took delivery of his Cybertruck. He's excited to test its off-road capabilities.",
                    "note_4": "Considering adding a roof tent for camping trips."
                }
            }
        },
        "charlie.brown@mail.com": {
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "charlie.brown@mail.com",
            "friends": ["bob.johnson@mail.com"],
            "tesla_data": {
                "vehicles": {
                    "charlie_model_y": {
                        "vehicle_tag": "5YJXCBE25NF001234",
                        "horn": False,
                        "media": {
                            "playing": True,
                            "volume": 40,
                            "current_track": 2,
                            "favorites": ["Kids' Story Time", "Classical Relaxation"]
                        },
                        "trunk": {
                            "front": "closed",
                            "rear": "closed"
                        },
                        "charge": {
                            "port_open": False,
                            "charging": False,
                            "limit": 70
                        },
                        "climate": {
                            "on": False,
                            "bioweapon_mode": False,
                            "climate_keeper_mode": "off",
                            "cop_temp": 28,
                            "driver_temp": 20,
                            "passenger_temp": 20,
                            "steering_wheel_heater": False,
                            "seat_heaters": {"driver_front": 0, "passenger_front": 0}
                        },
                        "doors": {
                            "locked": True
                        },
                        "sentry_mode": False,
                        "valet_mode": False,
                        "sunroof": "closed", # Model Y has a glass roof, not a sunroof
                        "windows": "closed",
                        "software_update": {
                            "scheduled": True,
                            "offset_sec": 7200
                        },
                        "awake": True
                    }
                },
                "vehicle_counter": 1,
                "notes": {
                    "note_5": "Charlie uses his Model Y for family errands and school runs.",
                    "note_6": "Scheduled a software update for 2 hours from now."
                }
            }
        },
        "diana.prince@mail.com": {
            "first_name": "Diana",
            "last_name": "Prince",
            "email": "diana.prince@mail.com",
            "friends": [],
            "tesla_data": {
                "vehicles": {},
                "vehicle_counter": 0,
                "notes": {
                    "note_7": "Diana is currently saving up for a Tesla Roadster."
                }
            }
        }
    },
    "current_user": "alice.smith@mail.com",
    "tesla_note_counter": 7 # Counter for unique note IDs
}

class TeslaFleetApis:
    def __init__(self, state: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes the TeslaFleetApis instance and loads the default scenario.
        """
        self.state: Dict[str, Any] = copy.deepcopy(state if state is not None else DEFAULT_STATE)
        self._api_description = "This tool belongs to the TeslaFleetAPI, which provides core functionality for controlling Tesla vehicles remotely."

    def _get_user_data(self, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Helper to get user-specific Tesla data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's Tesla data, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id, {}).get("tesla_data")

    def _get_user_vehicles_data(self, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Helper to get user's vehicles data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's vehicles, or None if not found.
        """
        tesla_data = self._get_user_data(user_id)
        if tesla_data:
            return tesla_data.get("vehicles")
        return None

    def _get_user_vehicle_counter(self, user_id: str = 'me') -> Optional[int]:
        """
        Helper to get user's vehicle counter.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[int]: The user's vehicle counter, or None if not found.
        """
        tesla_data = self._get_user_data(user_id)
        if tesla_data:
            return tesla_data.get("vehicle_counter")
        return None

    def _set_user_vehicle_counter(self, count: int, user_id: str = 'me') -> None:
        """
        Helper to set user's vehicle counter.

        Args:
            count (int): The new count for the vehicle counter.
            user_id (str): The ID of the user or 'me' for the current user.
        """
        tesla_data = self._get_user_data(user_id)
        if tesla_data:
            tesla_data["vehicle_counter"] = count

    def _get_vehicle(self, vehicle_tag: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Helper method to get vehicle data by its tag for a specific user.
        If the vehicle does not exist, it creates a new dummy vehicle with default settings and adds it to the
        `self.vehicles` dictionary for the current user. This simulates a new vehicle being registered.

        Args:
            vehicle_tag (str): The unique identifier (tag) of the vehicle.
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Dict[str, Any]: A dictionary containing the vehicle's data.
        """
        vehicles = self._get_user_vehicles_data(user_id)
        if vehicles is None:
            # This should ideally not happen if user data is set up correctly
            raise ValueError(f"Could not retrieve vehicles data for user {user_id}")

        if vehicle_tag not in vehicles:
            # If vehicle doesn't exist, create a new one with default properties for the current user
            current_vehicle_counter = self._get_user_vehicle_counter(user_id)
            if current_vehicle_counter is None:
                current_vehicle_counter = 0 # Default if not found
            self._set_user_vehicle_counter(current_vehicle_counter + 1, user_id)

            vehicles[vehicle_tag] = {
                "vehicle_tag": vehicle_tag, # Ensure the tag is saved with the vehicle
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
        return vehicles[vehicle_tag]

    def _load_scenario(self, scenario: Dict[str, Any]) -> None:
        """
        Load a scenario into the TeslaFleetApis instance.
        This method initializes the instance variables with data from the provided scenario dictionary,
        falling back to DEFAULT_STATE values if a key is not present in the scenario.

        Args:
            scenario (dict): A dictionary containing user and vehicle data to load into the API.
        """
        # Create a deep copy of the default state to ensure tests or scenarios
        # don't modify the original DEFAULT_STATE object.
        DEFAULT_STATE_COPY = copy.deepcopy(DEFAULT_STATE)

        # Populate instance variables using data from the scenario or default values
        self.state["users"] = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.state["current_user"] = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.state["tesla_note_counter"] = scenario.get("tesla_note_counter", DEFAULT_STATE_COPY["tesla_note_counter"])

    def honk_horn(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Honk the horn of the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["horn"] = True # Simulate horn being honked
        return {"success": True}

    def media_next_fav(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Skip to the next favorite media item in the specified vehicle's media playlist.
        If there are no favorites, no action is taken.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        if vehicle["media"]["favorites"]:
            current_index = vehicle["media"]["current_track"]
            # Cycle to the next favorite, wrapping around if at the end
            vehicle["media"]["current_track"] = (current_index + 1) % len(vehicle["media"]["favorites"])
        return {"success": True}

    def media_prev_fav(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Skip to the previous favorite media item in the specified vehicle's media playlist.
        If there are no favorites, no action is taken.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        if vehicle["media"]["favorites"]:
            current_index = vehicle["media"]["current_track"]
            # Cycle to the previous favorite, wrapping around if at the beginning
            vehicle["media"]["current_track"] = (current_index - 1 + len(vehicle["media"]["favorites"])) % len(vehicle["media"]["favorites"])
        return {"success": True}

    def media_prev_track(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Skip to the previous track in the specified vehicle's media playback.
        This is a simplified simulation and does not manage a full track list,
        only decrements a 'current_track' counter.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["media"]["current_track"] -= 1 # Simulate moving to previous track
        return {"success": True}

    def media_toggle_playback(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Toggle media playback (play/pause) in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["media"]["playing"] = not vehicle["media"]["playing"]
        return {"success": True}

    def media_volume_down(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Decrease the media volume in the specified vehicle by a fixed amount (e.g., 5 units).
        The volume will not go below 0.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["media"]["volume"] = max(0, vehicle["media"]["volume"] - 5)
        return {"success": True}

    def remote_boombox(self, vehicle_tag: str, sound_id: int) -> Dict[str, bool]:
        """
        Activate the remote boombox feature with the specified sound ID.
        In this dummy implementation, it only acknowledges the command.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            sound_id (int): The ID of the sound to play (e.g., 1 for a specific sound).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        # In a real implementation, this would trigger playing a specific sound
        print(f"Vehicle {vehicle_tag}: Playing boombox sound ID {sound_id}")
        return {"success": True}

    def actuate_trunk(self, vehicle_tag: str, which_trunk: str) -> Dict[str, bool]:
        """
        Open or close the specified trunk (front or rear) of the vehicle.
        If the trunk is closed, it opens; if open, it closes.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            which_trunk (str): The trunk to actuate ("front" or "rear").

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True if trunk type is valid),
                             False otherwise.
        """
        vehicle = self._get_vehicle(vehicle_tag)
        if which_trunk in ["front", "rear"]:
            current_state = vehicle["trunk"][which_trunk]
            vehicle["trunk"][which_trunk] = "open" if current_state == "closed" else "closed"
            return {"success": True}
        return {"success": False} # Invalid trunk type

    def charge_port_door_close(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Close the charge port door of the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
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
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["charge"]["port_open"] = True
        return {"success": True}

    def charge_max_range(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Set the charge limit to the maximum range (100%) for the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["charge"]["limit"] = 100
        return {"success": True}

    def charge_standard(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Set the charge limit to a standard level (80%) for the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
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
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
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
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["charge"]["charging"] = False
        return {"success": True}

    def set_charge_limit(self, vehicle_tag: str, percent: int) -> Dict[str, bool]:
        """
        Set the charge limit to a specific percentage for the specified vehicle.
        The percentage will be clamped between 0 and 100.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            percent (int): The charge limit percentage to set (0-100).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
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
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
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
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["on"] = False
        return {"success": True}

    def set_bioweapon_mode(self, vehicle_tag: str, on: bool) -> Dict[str, bool]:
        """
        Enable or disable bioweapon defense mode in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): True to enable, False to disable bioweapon mode.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["bioweapon_mode"] = on
        return {"success": True}

    def set_climate_keeper_mode(self, vehicle_tag: str, climate_keeper_mode: str) -> Dict[str, bool]:
        """
        Set the climate keeper mode in the specified vehicle.
        (e.g., "off", "dog_mode", "camp_mode").

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            climate_keeper_mode (str): The climate keeper mode to set.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["climate_keeper_mode"] = climate_keeper_mode
        return {"success": True}

    def set_cop_temp(self, vehicle_tag: str, cop_temp: float) -> Dict[str, bool]:
        """
        Set the cabin overheat protection (COP) temperature in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            cop_temp (float): The temperature to set for cabin overheat protection (e.g., in Celsius or Fahrenheit).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["cop_temp"] = cop_temp
        return {"success": True}

    def set_heated_seat(self, vehicle_tag: str, heater: str, level: int) -> Dict[str, bool]:
        """
        Set the heated seat level in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            heater (str): The specific seat heater to adjust (e.g., "driver_front", "passenger_front").
            level (int): The heating level (0-3).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        if heater in vehicle["climate"]["seat_heaters"]:
            vehicle["climate"]["seat_heaters"][heater] = max(0, min(3, level))
            return {"success": True}
        return {"success": False} # Invalid heater

    def set_preconditioning_enabled(self, vehicle_tag: str, enabled: bool) -> Dict[str, bool]:
        """
        Enable or disable preconditioning (preparing the cabin temperature) in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            enabled (bool): True to enable, False to disable preconditioning.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        # In a real implementation, this would trigger preconditioning
        print(f"Vehicle {vehicle_tag}: Preconditioning set to {enabled}")
        return {"success": True}

    def set_temp(self, vehicle_tag: str, driver_temp: float, passenger_temp: Optional[float] = None) -> Dict[str, bool]:
        """
        Set the desired temperature for the driver and optionally passenger in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            driver_temp (float): The desired temperature for the driver.
            passenger_temp (Optional[float]): The desired temperature for the passenger (if dual zone climate).

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["driver_temp"] = driver_temp
        if passenger_temp is not None:
            vehicle["climate"]["passenger_temp"] = passenger_temp
        return {"success": True}

    def set_steering_wheel_heater(self, vehicle_tag: str, on: bool) -> Dict[str, bool]:
        """
        Turn the steering wheel heater on or off in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): True to turn on, False to turn off the steering wheel heater.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["climate"]["steering_wheel_heater"] = on
        return {"success": True}

    def door_lock(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Lock the doors of the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
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
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["doors"]["locked"] = False
        return {"success": True}

    def set_sentry_mode(self, vehicle_tag: str, on: bool) -> Dict[str, bool]:
        """
        Enable or disable Sentry Mode in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): True to enable, False to disable Sentry Mode.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["sentry_mode"] = on
        return {"success": True}

    def set_valet_mode(self, vehicle_tag: str, on: bool) -> Dict[str, bool]:
        """
        Enable or disable Valet Mode in the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            on (bool): True to enable, False to disable Valet Mode.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["valet_mode"] = on
        return {"success": True}

    def sunroof_control(self, vehicle_tag: str, command: str) -> Dict[str, bool]:
        """
        Control the sunroof of the specified vehicle (e.g., "open", "close", "vent").

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            command (str): The sunroof control command (e.g., "open", "close", "vent").

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["sunroof"] = command
        return {"success": True}

    def schedule_software_update(self, vehicle_tag: str, offset_sec: int) -> Dict[str, bool]:
        """
        Schedule a software update for the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            offset_sec (int): The offset in seconds from now to schedule the update.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["software_update"]["scheduled"] = True
        vehicle["software_update"]["offset_sec"] = offset_sec
        return {"success": True}

    def cancel_software_update(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Cancel a scheduled software update for the specified vehicle.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["software_update"]["scheduled"] = False
        vehicle["software_update"]["offset_sec"] = 0
        return {"success": True}

    def wake_up(self, vehicle_tag: str) -> Dict[str, bool]:
        """
        Wake up the specified vehicle from sleep mode.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["awake"] = True
        return {"success": True}

    def window_control(self, vehicle_tag: str, command: str, lat: float, lon: float) -> Dict[str, bool]:
        """
        Control the windows of the specified vehicle (e.g., "vent", "close").
        The latitude and longitude might be used to confirm a safe location for window operations.

        Args:
            vehicle_tag (str): The unique identifier of the vehicle.
            command (str): The window control command (e.g., "vent", "close").
            lat (float): The latitude coordinate of the vehicle.
            lon (float): The longitude coordinate of the vehicle.

        Returns:
            Dict[str, bool]: A dictionary with a "success" key indicating
                             if the command was successful (True).
        """
        vehicle = self._get_vehicle(vehicle_tag)
        vehicle["windows"] = command
        print(f"Vehicle {vehicle_tag}: Window command '{command}' issued at ({lat}, {lon}).")
        return {"success": True}