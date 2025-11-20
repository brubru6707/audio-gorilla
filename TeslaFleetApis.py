import copy
import random
import math
import uuid
import hashlib
from typing import Dict, Any, Optional, Literal
from UnitTests.test_data_helper import BackendDataLoader

DEFAULT_STATE = BackendDataLoader.get_teslafleet_data()

class TeslaFleetApis:
    """
    An API class for simulating Tesla Fleet API operations.
    This class provides an in-memory backend for development and testing purposes.
    Matches the real Tesla Fleet API structure and authentication.
    """

    def __init__(self):
        """
        Initializes the TeslaFleetApis instance, setting up the in-memory
        data stores and loading the default scenario.
        """
        self._api_description = "This tool simulates a Tesla Fleet management system, allowing interaction with various vehicle functionalities."
        self.users: Dict[str, Any] = {}
        self.access_token: Optional[str] = None
        self.current_user_id: Optional[str] = None
        self.vehicles: Dict[str, Any] = {}  # Global vehicle registry by vehicle_id

        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the in-memory data stores, initializing
        users and vehicles. Builds global vehicle registry indexed by vehicle_id.
        """
        self.users = copy.deepcopy(scenario.get("users", {}))
        
        # Build global vehicle registry indexed by vehicle_id
        self.vehicles = {}
        for user_id, user_data in self.users.items():
            vehicles_dict = user_data.get("tesla_data", {}).get("vehicles", {})
            for vehicle_uuid, vehicle_data in vehicles_dict.items():
                # Enrich vehicle with standard Tesla fields
                enriched_vehicle = self._enrich_vehicle(vehicle_data, user_id, vehicle_uuid)
                # Use the numeric vehicle_id as the key
                vehicle_id = str(enriched_vehicle["id"])
                self.vehicles[vehicle_id] = enriched_vehicle

    def _enrich_vehicle(self, vehicle_data: Dict[str, Any], user_id: str, vehicle_uuid: str) -> Dict[str, Any]:
        """
        Enriches vehicle data with standard Tesla Fleet API fields.
        
        Args:
            vehicle_data: Raw vehicle data from backend
            user_id: Owner user ID
            vehicle_uuid: Internal vehicle UUID
            
        Returns:
            Enriched vehicle data with standard fields
        """
        # Generate numeric vehicle_id from UUID hash (simulates real Tesla vehicle IDs)
        vehicle_id_hash = int(hashlib.md5(vehicle_uuid.encode()).hexdigest()[:15], 16)
        
        # Use vehicle_tag as VIN if it looks like a VIN, otherwise generate one
        vin = vehicle_data.get("vehicle_tag", "5YJ" + vehicle_uuid[:14].replace("-", "").upper())
        
        # Create display name from original tag if available
        original_tag = vehicle_data.get("original_vehicle_tag", "")
        if original_tag:
            # Convert "hayden_cybertruck_1" to "Hayden Cybertruck 1"
            display_name = " ".join(word.capitalize() for word in original_tag.replace("_", " ").split())
        else:
            display_name = f"Vehicle {vehicle_uuid[:8]}"
        
        # Determine state based on awake field
        awake = vehicle_data.get("awake", True)
        state = "online" if awake else "asleep"
        
        # Add standard fields
        enriched = copy.deepcopy(vehicle_data)
        enriched.update({
            "id": vehicle_id_hash,  # Numeric vehicle ID
            "vehicle_id": vehicle_id_hash,  # Same as id for consistency
            "vin": vin,
            "display_name": display_name,
            "state": state,
            "in_service": False,  # Default to not in service
            "user_id": user_id,  # Track ownership
            "_uuid": vehicle_uuid,  # Keep UUID for internal tracking
        })
        
        return enriched

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for entities.
        """
        return str(uuid.uuid4())

    def authenticate(self, access_token: str) -> Dict[str, Any]:
        """
        Authenticates with Tesla Fleet API using OAuth 2.0 Bearer token.
        Simulates token validation and user identification.
        
        Args:
            access_token: OAuth 2.0 access token (format: "token_{email}")
        
        Returns:
            Response object with user information
            
        Raises:
            Exception: If token is invalid
        """
        # Validate token format
        if not access_token or not access_token.startswith("token_"):
            raise Exception("Invalid access token")
        
        # Extract user email from token
        email = access_token.replace("token_", "")
        
        # Find user by email
        user_id = None
        for uid, user_data in self.users.items():
            if user_data.get("email") == email:
                user_id = uid
                break
        
        if not user_id:
            raise Exception("Invalid access token - user not found")
        
        # Set authenticated user
        self.access_token = access_token
        self.current_user_id = user_id
        
        # Return user info (matching Tesla API structure)
        user_data = self.users[user_id]
        return {
            "response": {
                "email": user_data.get("email"),
                "full_name": user_data.get("full_name", ""),
                "profile_image_url": user_data.get("profile_image_url", "")
            },
            "error": None
        }

    def _ensure_authenticated(self) -> None:
        """
        Verifies that a user is authenticated before accessing protected resources.
        
        Raises:
            Exception: If no user is authenticated
        """
        if not self.access_token or not self.current_user_id:
            raise Exception("Authentication required - call authenticate() first")

    def _get_user_vehicles(self) -> list:
        """
        Gets all vehicles owned by the authenticated user.
        
        Returns:
            List of vehicle objects
        """
        self._ensure_authenticated()
        user_vehicles = []
        for _, vehicle_data in self.vehicles.items():
            if vehicle_data.get("user_id") == self.current_user_id:
                user_vehicles.append(vehicle_data)
        return user_vehicles

    def _get_vehicle(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Internal helper to get and validate vehicle access.
        
        Args:
            vehicle_id: Numeric vehicle ID
            
        Returns:
            Vehicle data dictionary
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        self._ensure_authenticated()
        
        vehicle_id_str = str(vehicle_id)
        vehicle = self.vehicles.get(vehicle_id_str)
        
        if not vehicle:
            raise Exception(f"Vehicle {vehicle_id} not found")
        
        if vehicle.get("user_id") != self.current_user_id:
            raise Exception(f"Vehicle {vehicle_id} not accessible")
        
        return vehicle

    def list_vehicles(self) -> Dict[str, Any]:
        """
        Gets a list of vehicles owned by the authenticated user.
        Matches GET /api/1/vehicles endpoint.
        
        Returns:
            Response object containing list of vehicles
        """
        self._ensure_authenticated()
        vehicles = self._get_user_vehicles()
        
        return {
            "response": vehicles,
            "error": None,
            "count": len(vehicles)
        }

    def get_vehicle_data(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Gets comprehensive data for a specific vehicle.
        Matches GET /api/1/vehicles/{id}/vehicle_data endpoint.
        
        Args:
            vehicle_id: Numeric vehicle ID
            
        Returns:
            Response object with vehicle data
            
        Raises:
            Exception: If vehicle not found or not owned by authenticated user
        """
        self._ensure_authenticated()
        
        vehicle_id_str = str(vehicle_id)
        vehicle = self.vehicles.get(vehicle_id_str)
        
        if not vehicle:
            raise Exception(f"Vehicle {vehicle_id} not found")
        
        if vehicle.get("user_id") != self.current_user_id:
            raise Exception(f"Vehicle {vehicle_id} not accessible")
        
        return {
            "response": copy.deepcopy(vehicle),
            "error": None
        }

    def honk_horn(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Honk the horn of the specified vehicle.
        Matches POST /api/1/vehicles/{id}/command/honk_horn endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["horn"] = True
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def flash_lights(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Flash the lights of the specified vehicle.
        Matches POST /api/1/vehicles/{id}/command/flash_lights endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["lights"]["on"] = True
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def media_volume_up(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Turns up the volume of the media system.
        Matches POST /api/1/vehicles/{id}/command/media_volume_up endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        current_volume = vehicle["media"]["volume"]
        vehicle["media"]["volume"] = min(100, current_volume + 1)
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def media_volume_down(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Turns down the volume of the media system.
        Matches POST /api/1/vehicles/{id}/command/media_volume_down endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        current_volume = vehicle["media"]["volume"]
        vehicle["media"]["volume"] = max(0, current_volume - 1)
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def door_unlock(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Unlocks the doors to the car.
        Matches POST /api/1/vehicles/{id}/command/door_unlock endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["locks"] = "unlocked"
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def door_lock(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Locks the doors to the car.
        Matches POST /api/1/vehicles/{id}/command/door_lock endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["locks"] = "locked"
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def media_toggle_playback(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Toggles the media between playing and paused.
        Matches POST /api/1/vehicles/{id}/command/media_toggle_playback endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["media"]["playing"] = not vehicle["media"]["playing"]
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def adjust_volume(self, vehicle_id: int, volume: int) -> Dict[str, Any]:
        """
        Adjusts the volume of the media system to the desired volume.
        Matches POST /api/1/vehicles/{id}/command/adjust_volume endpoint.

        Args:
            vehicle_id: Numeric vehicle ID
            volume: The desired volume level (0-100)

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible or invalid volume
        """
        vehicle = self._get_vehicle(vehicle_id)
        
        if not (0 <= volume <= 100):
            raise Exception("Volume level must be between 0 and 100")

        vehicle["media"]["volume"] = volume
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def media_next_track(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Skips to the next track in the current playlist.
        Matches POST /api/1/vehicles/{id}/command/media_next_track endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["media"]["current_track"] = vehicle["media"]["current_track"] + 1
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def media_prev_track(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Skips to the previous track in the current playlist.
        Matches POST /api/1/vehicles/{id}/command/media_prev_track endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["media"]["current_track"] = max(0, vehicle["media"]["current_track"] - 1)
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def actuate_trunk(self, vehicle_id: int, which_trunk: Literal["front", "rear"]) -> Dict[str, Any]:
        """
        Opens either the front or rear trunk.
        Matches POST /api/1/vehicles/{id}/command/actuate_trunk endpoint.

        Args:
            vehicle_id: Numeric vehicle ID
            which_trunk: Which trunk to actuate ("front" or "rear")

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["trunk"][which_trunk] = "open"
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def set_charge_limit(self, vehicle_id: int, limit: int) -> Dict[str, Any]:
        """
        Set the charge limit percentage for the specified vehicle.
        Matches POST /api/1/vehicles/{id}/command/set_charge_limit endpoint.

        Args:
            vehicle_id: Numeric vehicle ID
            limit: The desired charge limit percentage (0-100)

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible or invalid limit
        """
        vehicle = self._get_vehicle(vehicle_id)
        
        if not (0 <= limit <= 100):
            raise Exception("Charge limit must be between 0 and 100")

        vehicle["charge"]["limit"] = limit
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def charge_port_door_open(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Opens the charge port or unlocks the cable.
        Matches POST /api/1/vehicles/{id}/command/charge_port_door_open endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["charge"]["port_open"] = True
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def charge_port_door_close(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Closes the charge port.
        Matches POST /api/1/vehicles/{id}/command/charge_port_door_close endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["charge"]["port_open"] = False
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def charge_start(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Start charging if the car is plugged in but not currently charging.
        Matches POST /api/1/vehicles/{id}/command/charge_start endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["charge"]["charging"] = True
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def charge_stop(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Stop charging if the car is currently charging.
        Matches POST /api/1/vehicles/{id}/command/charge_stop endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["charge"]["charging"] = False
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def auto_conditioning_start(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Start the climate control (HVAC) system.
        Matches POST /api/1/vehicles/{id}/command/auto_conditioning_start endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["climate"]["on"] = True
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def auto_conditioning_stop(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Stop the climate control (HVAC) system.
        Matches POST /api/1/vehicles/{id}/command/auto_conditioning_stop endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["climate"]["on"] = False
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def set_temps(self, vehicle_id: int, driver_temp: float, passenger_temp: float) -> Dict[str, Any]:
        """
        Sets the target temperature for the climate control (HVAC) system.
        Matches POST /api/1/vehicles/{id}/command/set_temps endpoint.

        Args:
            vehicle_id: Numeric vehicle ID
            driver_temp: The desired temperature for the driver (Celsius)
            passenger_temp: The desired temperature for the passenger (Celsius)

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible or invalid temps
        """
        vehicle = self._get_vehicle(vehicle_id)
        
        if not (15 <= driver_temp <= 30) or not (15 <= passenger_temp <= 30):
            raise Exception("Temperatures must be between 15 and 30 Celsius")

        vehicle["climate"]["driver_temp"] = driver_temp
        vehicle["climate"]["cop_temp"] = passenger_temp
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def set_bioweapon_mode(self, vehicle_id: int, on: bool) -> Dict[str, Any]:
        """
        Enable or disable Bioweapon Defense Mode.
        Matches POST /api/1/vehicles/{id}/command/set_bioweapon_mode endpoint.

        Args:
            vehicle_id: Numeric vehicle ID
            on: Whether to enable (True) or disable (False) Bioweapon Defense Mode

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["climate"]["bioweapon_mode"] = on
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def set_climate_keeper_mode(self, vehicle_id: int, climate_keeper_mode: int) -> Dict[str, Any]:
        """
        Set the Climate Keeper mode.
        Matches POST /api/1/vehicles/{id}/command/set_climate_keeper_mode endpoint.

        Args:
            vehicle_id: Numeric vehicle ID
            climate_keeper_mode: The Climate Keeper mode (0=off, 1=dog, 2=camp)

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible or invalid mode
        """
        vehicle = self._get_vehicle(vehicle_id)
        
        mode_names = {0: "off", 1: "dog", 2: "camp"}
        if climate_keeper_mode not in mode_names:
            raise Exception("Invalid climate keeper mode. Must be 0 (off), 1 (dog), or 2 (camp)")

        vehicle["climate"]["climate_keeper_mode"] = mode_names[climate_keeper_mode]
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }
    
    def wake_up(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Wakes up the car from a sleeping state.
        Matches POST /api/1/vehicles/{id}/wake_up endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["awake"] = True
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def window_control(self, vehicle_id: int, command: Literal["vent", "close"]) -> Dict[str, Any]:
        """
        Controls the windows. Will vent or close all windows simultaneously.
        Matches POST /api/1/vehicles/{id}/command/window_control endpoint.

        Args:
            vehicle_id: Numeric vehicle ID
            command: The window control command ("vent" or "close")

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["windows"] = command
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def get_vehicle_location(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Get the current location of the specified vehicle.
        Matches GET /api/1/vehicles/{id}/data_request/drive_state endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object with location information
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        location = vehicle.get("location", {"latitude": 0, "longitude": 0})
        return {
            "response": {
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "speed": vehicle.get("speed", 0)
            },
            "error": None
        }

    def get_vehicle_status(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Get comprehensive status information for the specified vehicle.
        Matches GET /api/1/vehicles/{id}/vehicle_data endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object with detailed vehicle status
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        
        return {
            "response": {
                "id": vehicle.get("id"),
                "vehicle_id": vehicle.get("vehicle_id"),
                "vin": vehicle.get("vin"),
                "display_name": vehicle.get("display_name"),
                "state": vehicle.get("state", "online"),
                "in_service": vehicle.get("in_service", False),
                "firmware_version": vehicle.get("firmware_version"),
                "awake": vehicle.get("awake", False),
                "speed": vehicle.get("speed", 0),
                "location": vehicle.get("location", {}),
                "charge_state": vehicle.get("charge", {}),
                "climate_state": vehicle.get("climate", {}),
                "vehicle_state": {
                    "locked": vehicle.get("locks") == "locked",
                    "sentry_mode": vehicle.get("sentry_mode", {}),
                    "ft": vehicle.get("trunk", {}).get("front", "closed"),
                    "rt": vehicle.get("trunk", {}).get("rear", "closed"),
                },
                "drive_state": vehicle.get("location", {}),
            },
            "error": None
        }

    def set_sentry_mode(self, vehicle_id: int, on: bool) -> Dict[str, Any]:
        """
        Turns sentry mode on or off.
        Matches POST /api/1/vehicles/{id}/command/set_sentry_mode endpoint.

        Args:
            vehicle_id: Numeric vehicle ID
            on: Whether to enable (True) or disable (False) sentry mode

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        sentry_mode = vehicle.get("sentry_mode", {})
        sentry_mode["on"] = on
        vehicle["sentry_mode"] = sentry_mode
        
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def get_firmware_info(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Get firmware version and update information for the specified vehicle.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object with firmware information
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        
        return {
            "response": {
                "current_version": vehicle.get("firmware_version", "Unknown"),
                "created_time": vehicle.get("createdTime"),
                "modified_time": vehicle.get("modifiedTime"),
            },
            "error": None
        }

    def wake_vehicle(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Wake up the specified vehicle from sleep mode.
        Matches POST /api/1/vehicles/{id}/wake_up endpoint.

        Args:
            vehicle_id: Numeric vehicle ID

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["awake"] = True
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def set_speed_limit(self, vehicle_id: int, limit_mph: int) -> Dict[str, Any]:
        """
        Set the speed limit for the specified vehicle.
        Matches POST /api/1/vehicles/{id}/command/speed_limit_set_limit endpoint.

        Args:
            vehicle_id: Numeric vehicle ID
            limit_mph: The speed limit in miles per hour (0-140)

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible or invalid limit
        """
        vehicle = self._get_vehicle(vehicle_id)
        
        if not (0 <= limit_mph <= 140):
            raise Exception("Speed limit must be between 0 and 140 mph")

        vehicle["speed_limit"] = limit_mph
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def set_valet_mode(self, vehicle_id: int, on: bool, pin: Optional[str] = None) -> Dict[str, Any]:
        """
        Enable or disable valet mode for the specified vehicle.
        Matches POST /api/1/vehicles/{id}/command/set_valet_mode endpoint.

        Args:
            vehicle_id: Numeric vehicle ID
            on: Whether to enable (True) or disable (False) valet mode
            pin: PIN code for valet mode (required when enabling)

        Returns:
            Response object indicating success or failure
            
        Raises:
            Exception: If vehicle not found or not accessible or missing PIN
        """
        vehicle = self._get_vehicle(vehicle_id)
        
        if on and not pin:
            raise Exception("PIN code is required to enable valet mode")

        vehicle["valet_mode"] = {"on": on, "pin": pin if on else None}
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the distance between two points using the Haversine formula.
        
        Args:
            lat1 (float): Latitude of first point
            lon1 (float): Longitude of first point
            lat2 (float): Latitude of second point
            lon2 (float): Longitude of second point
            
        Returns:
            float: Distance in miles
        """
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        # Earth's radius in miles
        earth_radius = 3959
        return earth_radius * c

    def get_nearby_charging_sites(self, vehicle_id: int, radius: int = 50) -> Dict[str, Any]:
        """
        Get nearby charging sites (superchargers) for the specified vehicle.
        Uses the vehicle's current location to find nearby chargers.
        Matches GET /api/1/vehicles/{id}/nearby_charging_sites endpoint.

        Args:
            vehicle_id: Numeric vehicle ID
            radius: Search radius in miles (default 50)

        Returns:
            Response object with nearby charging sites
            
        Raises:
            Exception: If vehicle not found or not accessible
        """
        # Get the vehicle to access its location
        vehicle = self._get_vehicle(vehicle_id)
        vehicle_location = vehicle.get("location", {})
        lat = vehicle_location.get("latitude")
        lon = vehicle_location.get("longitude")
        
        if lat is None or lon is None:
            raise Exception(f"Vehicle {vehicle_id} does not have a valid location")
        
        # Get superchargers from the state
        all_superchargers = DEFAULT_STATE.get("superchargers", [])  
        # Find nearby superchargers within the radius
        nearby_sites = []
        for charger in all_superchargers:
            distance = self._calculate_distance(lat, lon, charger["latitude"], charger["longitude"])
            if distance <= radius:
                # Simulate available stalls (random but realistic)
                total_stalls = charger["total_stalls"]
                available_stalls = random.randint(max(0, total_stalls - 4), total_stalls)
                site_data = {
                    "name": charger["name"],
                    "latitude": charger["latitude"],
                    "longitude": charger["longitude"],
                    "distance": round(distance, 1),
                    "available_stalls": available_stalls,
                    "total_stalls": total_stalls,
                    "site_type": "supercharger",
                    "address": charger.get("address", "")
                }
                nearby_sites.append(site_data)
        
        # Sort by distance
        nearby_sites.sort(key=lambda x: x["distance"])

        return {
            "response": {
                "congestion_sync_time_utc_secs": 0,
                "destination_charging": [],
                "superchargers": nearby_sites,
                "timestamp": 0
            },
            "error": None
        }

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self.access_token = None
        self.current_user_id = None
        self._load_scenario(DEFAULT_STATE)
        return {"reset_status": True}
