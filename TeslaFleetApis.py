import copy
import random
import math
import uuid
import hashlib
from typing import Dict, Any, Optional, Literal
from UnitTests.test_data_helper import BackendDataLoader

DEFAULT_STATE = BackendDataLoader.get_teslafleet_data()

class User:
    def __init__(self, email: str):
        self.email = email

class TeslaFleetApis:
    """
    An API class for simulating Tesla Fleet API operations.
    This class provides an in-memory backend for development and testing purposes.
    Matches the real Tesla Fleet API structure and authentication.
    """

    def __init__(self):
        """
        Initializes the TeslaFleetApis instance with in-memory data stores for simulating Tesla Fleet operations.
        
        Sets up empty dictionaries for users and vehicles, then loads the default scenario data.
        This simulated backend allows for testing Tesla vehicle control workflows without connecting
        to actual Tesla servers or vehicles.
        
        Side Effects:
            - Creates empty data stores for users and vehicles (global registry)
            - Loads default state from BackendDataLoader
            - Initializes authentication state (no user authenticated)
            - Builds global vehicle registry indexed by numeric vehicle_id
        
        Note:
            This is a simulation class for development/testing. All data is stored in memory
            and will be lost when the instance is destroyed. Vehicle IDs are generated from
            UUID hashes to simulate Tesla's numeric vehicle ID format.
        """
        self._api_description = "This tool simulates a Tesla Fleet management system, allowing interaction with various vehicle functionalities."
        self.users: Dict[str, Any] = {}
        self.access_token: Optional[str] = None
        self.current_user_id: Optional[str] = None
        self.vehicles: Dict[str, Any] = {}  # Global vehicle registry by vehicle_id

        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the backend's state, initializing users and building vehicle registry.
        
        Deep copies user data from the scenario, then iterates through all users' vehicles to build
        a global vehicle registry indexed by numeric vehicle_id (Tesla's standard identifier format).
        Each vehicle is enriched with standard Tesla API fields during this process.

        Args:
            scenario (Dict): A dictionary containing the complete state to load. Expected structure:
                {
                    "users": Dict[str, Any],  # User data keyed by user UUID
                        # Each user has "tesla_data": {"vehicles": {vehicle_uuid: vehicle_data}}
                    "superchargers": List[Dict]  # Optional list of charging locations
                }
                
        Side Effects:
            - Completely replaces self.users with deep copy from scenario
            - Rebuilds self.vehicles global registry from all users' vehicles
            - Enriches each vehicle with standard Tesla fields (VIN, display_name, etc.)
            - Does NOT reset authentication state (access_token, current_user_id)
            
        Note:
            - Uses deep copy to prevent accidental modification of source scenario
            - Vehicle registry uses numeric vehicle_id as key (not UUID)
            - All vehicles across all users are accessible via self.vehicles
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
        Enriches raw vehicle data with standard Tesla Fleet API fields for consistent responses.
        
        Transforms minimal backend vehicle data into the full structure expected by the Tesla API.
        Generates numeric vehicle_id from UUID hash (simulating Tesla's ID format), creates VIN,
        generates human-readable display name, determines online/sleep state, and adds ownership tracking.
        
        Args:
            vehicle_data (Dict[str, Any]): Raw vehicle data from backend containing optional fields:
                - "vehicle_tag": Original vehicle identifier (may be used as VIN)
                - "original_vehicle_tag": Human-readable tag for display name generation
                - "awake": Boolean indicating if vehicle is awake/online
                - Plus all vehicle state data (charge, climate, media, etc.)
            user_id (str): UUID of the vehicle owner for access control
            vehicle_uuid (str): Internal UUID for vehicle (used to generate numeric ID)
            
        Returns:
            Dict[str, Any]: Enriched vehicle data with additional standard fields:
                - "id" (int): Numeric vehicle ID (Tesla standard format)
                - "vehicle_id" (int): Same as id for consistency
                - "vin" (str): Vehicle Identification Number (17 characters)
                - "display_name" (str): Human-readable vehicle name
                - "state" (str): "online" or "asleep" based on awake field
                - "in_service" (bool): Always False in simulation
                - "user_id" (str): Owner's user UUID for access control
                - "_uuid" (str): Original vehicle UUID for internal tracking
                Plus all original fields from vehicle_data
                
        Note:
            - Numeric vehicle_id is generated by MD5 hashing UUID (first 15 hex digits)
            - VIN format: "5YJ" prefix + 14 uppercase alphanumeric characters
            - Display name is Title Cased from original_vehicle_tag (underscores become spaces)
            - This is an internal helper that doesn't modify the original vehicle_data dict
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
        Generates a unique UUID string for creating new entities.
        
        Uses Python's uuid.uuid4() to generate a random UUID, ensuring global uniqueness
        across all entity types in the simulated backend.
        
        Returns:
            str: A UUID string in standard format (e.g., "550e8400-e29b-41d4-a716-446655440000")
            
        Note:
            Currently used for entity creation. Vehicle IDs are numeric (generated differently).
        """
        return str(uuid.uuid4())

    def authenticate(self, access_token: str) -> Dict[str, Any]:
        """
        Authenticates a user with the Tesla Fleet API using an OAuth 2.0 Bearer token.
        
        Simulates the Tesla OAuth 2.0 authentication flow. Validates the token format,
        extracts the user email from the token, locates the corresponding user in the
        backend, and establishes an authenticated session.
        
        Args:
            access_token (str): OAuth 2.0 Bearer access token in format "token_{email}"
                Example: "token_hayden@example.com" for user with that email
        
        Returns:
            Dict[str, Any]: Tesla API standard response wrapper:
                {
                    "response": {
                        "email": str,              # User's email address
                        "full_name": str,          # User's full name
                        "profile_image_url": str   # Profile image URL
                    },
                    "error": None                   # Always None on success
                }
            
        Raises:
            Exception: If token format is invalid (doesn't start with "token_")
                Error message: "Invalid access token"
            Exception: If no user exists with the email extracted from the token
                Error message: "Invalid access token - user not found"
            
        Side Effects:
            - Sets self.access_token to the provided token
            - Sets self.current_user_id to the authenticated user's UUID
            - Subsequent API calls will be made in context of this user
            
        Example:
            >>> api = TeslaFleetApis()
            >>> response = api.authenticate("token_hayden@example.com")
            >>> print(response["response"]["email"])  # "hayden@example.com"
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
        Internal guard method that verifies a user is authenticated before accessing protected resources.
        
        Checks that both access_token and current_user_id are set, indicating a successful
        authentication. This should be called at the start of every method that requires authentication.
        
        Raises:
            Exception: If either access_token or current_user_id is None (user not authenticated)
                Error message: "Authentication required - call authenticate() first"
                
        Note:
            This is an internal helper method used by all protected endpoints (all vehicle operations).
        """
        if not self.access_token or not self.current_user_id:
            raise Exception("Authentication required - call authenticate() first")

    def _get_user_vehicles(self) -> list:
        """
        Retrieves all vehicles owned by the currently authenticated user from the global registry.
        
        Filters the global vehicle registry (self.vehicles) to return only vehicles where
        the user_id matches the authenticated user. This is an internal helper used by
        list_vehicles() and other methods that need to operate on user's vehicle fleet.
        
        Returns:
            List[Dict[str, Any]]: List of enriched vehicle objects owned by authenticated user.
                Each vehicle contains all standard Tesla API fields (id, vin, display_name, etc.)
                Returns empty list [] if user has no vehicles.
                
        Raises:
            Exception: If not authenticated (via _ensure_authenticated() call)
                
        Note:
            - Vehicles are returned in arbitrary order (not sorted)
            - Each vehicle object is a reference to the global registry (not a copy)
            - This is an internal helper method
        """
        self._ensure_authenticated()
        user_vehicles = []
        for _, vehicle_data in self.vehicles.items():
            if vehicle_data.get("user_id") == self.current_user_id:
                user_vehicles.append(vehicle_data)
        return user_vehicles

    def _get_vehicle(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Internal helper to retrieve a vehicle and validate the authenticated user has access to it.
        
        Performs three validations: 1) user is authenticated, 2) vehicle exists in the system,
        3) vehicle belongs to the authenticated user. This is the standard access control
        mechanism used by all vehicle command methods.
        
        Args:
            vehicle_id (int): Numeric Tesla vehicle ID (not UUID)
                Example: 123456789012345 (15-digit number)
            
        Returns:
            Dict[str, Any]: Reference to the vehicle data dictionary from global registry.
                Contains all enriched vehicle fields (state, charge, climate, media, etc.)
                
        Raises:
            Exception: If not authenticated (no user logged in)
                Error message: "Authentication required - call authenticate() first"
            Exception: If vehicle_id doesn't exist in global vehicle registry
                Error message: "Vehicle {vehicle_id} not found"
            Exception: If vehicle exists but doesn't belong to authenticated user
                Error message: "Vehicle {vehicle_id} not accessible"
                
        Note:
            - Returns a reference to the vehicle object (not a copy), so modifications affect global state
            - This is the primary access control mechanism for all vehicle operations
            - vehicle_id is converted to string for dictionary lookup
        """
        self._ensure_authenticated()
        
        vehicle_id_str = str(vehicle_id)
        vehicle = self.vehicles.get(vehicle_id_str)
        
        if not vehicle:
            raise Exception(f"Vehicle {vehicle_id} not found")
        
        if vehicle.get("user_id") != self.current_user_id:
            raise Exception(f"Vehicle {vehicle_id} not accessible")
        
        return vehicle

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

    def list_vehicles(self) -> Dict[str, Any]:
        """
        Retrieves a list of all vehicles owned by the authenticated user.
        
        Matches the Tesla Fleet API GET /api/1/vehicles endpoint. Returns all vehicles
        associated with the authenticated user's account in the standard Tesla response format.
        
        Returns:
            Dict[str, Any]: Tesla API standard response wrapper:
                {
                    "response": List[Dict[str, Any]],  # List of vehicle objects, each containing:
                        # - "id": int (numeric vehicle ID)
                        # - "vehicle_id": int (same as id)
                        # - "vin": str (17-character VIN)
                        # - "display_name": str (human-readable name)
                        # - "state": str ("online" or "asleep")
                        # - "in_service": bool
                        # - Plus all vehicle state data
                    "error": None,                      # Always None on success
                    "count": int                        # Number of vehicles returned
                }
            
        Raises:
            Exception: If not authenticated (no user logged in)
                
        Example:
            >>> api.authenticate("token_hayden@example.com")
            >>> result = api.list_vehicles()
            >>> print(f"You have {result['count']} vehicle(s)")
            >>> for vehicle in result['response']:
            ...     print(f"  {vehicle['display_name']} - {vehicle['state']}")
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
        Retrieves comprehensive data for a specific vehicle including all state information.
        
        Matches the Tesla Fleet API GET /api/1/vehicles/{id}/vehicle_data endpoint.
        Returns the complete vehicle data snapshot including charge state, climate settings,
        location, media state, and all other vehicle properties.
        
        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
                Example: 123456789012345
            
        Returns:
            Dict[str, Any]: Tesla API standard response wrapper:
                {
                    "response": Dict[str, Any],  # Complete vehicle data object containing:
                        # - All fields from _enrich_vehicle() (id, vin, display_name, etc.)
                        # - "charge": Dict with battery level, charging status, limits
                        # - "climate": Dict with HVAC settings, temperatures
                        # - "media": Dict with volume, playback state, current track
                        # - "location": Dict with latitude, longitude
                        # - "locks": str ("locked" or "unlocked")
                        # - "trunk": Dict with front/rear trunk states
                        # - "windows": str ("vent" or "close")
                        # - "lights": Dict with light states
                        # - "sentry_mode": Dict with sentry mode settings
                        # - "valet_mode": Dict with valet mode settings
                        # - "speed": int (current speed)
                        # - "firmware_version": str
                        # - And many more vehicle-specific fields
                    "error": None                # Always None on success
                }
            
        Raises:
            Exception: If not authenticated
            Exception: If vehicle_id not found
                Error message: "Vehicle {vehicle_id} not found"
            Exception: If vehicle not accessible by authenticated user
                Error message: "Vehicle {vehicle_id} not accessible"
                
        Example:
            >>> api.authenticate("token_hayden@example.com")
            >>> vehicles = api.list_vehicles()
            >>> vehicle_id = vehicles['response'][0]['id']
            >>> data = api.get_vehicle_data(vehicle_id)
            >>> print(f"Battery: {data['response']['charge']['battery_level']}%")
            >>> print(f"Location: {data['response']['location']['latitude']}, {data['response']['location']['longitude']}")
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
        Honks the horn of the specified vehicle remotely.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/honk_horn endpoint.
        Useful for locating your vehicle in a parking lot or getting someone's attention.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper:
                {
                    "response": {
                        "result": True,         # Always True on success
                        "reason": ""            # Empty string on success
                    },
                    "error": None               # Always None on success
                }
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["horn"] = True in vehicle state
            - In a real vehicle, this would sound the horn once
            
        Example:
            >>> api.authenticate("token_hayden@example.com")
            >>> vehicle_id = api.list_vehicles()['response'][0]['id']
            >>> result = api.honk_horn(vehicle_id)
            >>> print("Horn honked!" if result['response']['result'] else "Failed")
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
        Flashes the exterior lights of the specified vehicle remotely.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/flash_lights endpoint.
        Useful for locating your vehicle in a parking lot, especially in low-light conditions.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper:
                {
                    "response": {
                        "result": True,         # Always True on success
                        "reason": ""            # Empty string on success
                    },
                    "error": None               # Always None on success
                }
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["lights"]["on"] = True in vehicle state
            - In a real vehicle, this would flash the headlights and taillights
            
        Example:
            >>> api.authenticate("token_hayden@example.com")
            >>> vehicle_id = api.list_vehicles()['response'][0]['id']
            >>> result = api.flash_lights(vehicle_id)
            >>> print("Lights flashed!" if result['response']['result'] else "Failed")
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
        Increases the media system volume by one increment.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/media_volume_up endpoint.
        Raises the volume by 1 unit, up to a maximum of 100.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Increments vehicle["media"]["volume"] by 1 (capped at 100)
            - If already at 100, volume remains at 100
            
        Example:
            >>> result = api.media_volume_up(vehicle_id)
            >>> # Volume increased by 1 (e.g., 45 → 46)
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
        Decreases the media system volume by one increment.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/media_volume_down endpoint.
        Lowers the volume by 1 unit, down to a minimum of 0.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Decrements vehicle["media"]["volume"] by 1 (floored at 0)
            - If already at 0, volume remains at 0 (muted)
            
        Example:
            >>> result = api.media_volume_down(vehicle_id)
            >>> # Volume decreased by 1 (e.g., 46 → 45)
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
        Unlocks all doors of the vehicle remotely.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/door_unlock endpoint.
        Unlocks all four doors simultaneously. Does not affect trunk locks.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["locks"] = "unlocked" in vehicle state
            - In a real vehicle, all doors would unlock and mirrors may unfold
            
        Note:
            For security, Tesla may require the vehicle to be within Bluetooth/GPS range
            of the authenticated account's phone. This simulation doesn't enforce that.
            
        Example:
            >>> result = api.door_unlock(vehicle_id)
            >>> # All doors are now unlocked
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
        Locks all doors of the vehicle remotely.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/door_lock endpoint.
        Locks all four doors simultaneously. Does not affect trunk locks.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["locks"] = "locked" in vehicle state
            - In a real vehicle, all doors would lock and mirrors may fold
            
        Note:
            Tesla vehicles can auto-lock when you walk away (Walk-Away Door Lock feature).
            This manual lock is useful for ensuring the vehicle is secured remotely.
            
        Example:
            >>> result = api.door_lock(vehicle_id)
            >>> # All doors are now locked
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
        Toggles the media playback between playing and paused states.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/media_toggle_playback endpoint.
        If media is currently playing, it will pause. If paused, it will resume playing.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Inverts vehicle["media"]["playing"] boolean
            - True → False (pause), False → True (play)
            
        Example:
            >>> # If currently playing
            >>> result = api.media_toggle_playback(vehicle_id)
            >>> # Now paused
            >>> result = api.media_toggle_playback(vehicle_id)
            >>> # Now playing again
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
        Sets the media system volume to a specific level (absolute volume control).
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/adjust_volume endpoint.
        Unlike media_volume_up/down which adjust incrementally, this sets the exact volume level.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
            volume (int): Desired volume level. Valid range: 0-100
                - 0: Muted/silent
                - 100: Maximum volume
                - Typical listening: 30-60

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            Exception: If volume is not in valid range (0-100)
                Error message: "Volume level must be between 0 and 100"
            
        Side Effects:
            - Sets vehicle["media"]["volume"] to the specified value
            
        Example:
            >>> # Set volume to 50%
            >>> result = api.adjust_volume(vehicle_id, 50)
            >>> # Mute
            >>> result = api.adjust_volume(vehicle_id, 0)
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
        Skips to the next track in the current media playlist or queue.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/media_next_track endpoint.
        Advances to the next song, podcast episode, or audio track.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Increments vehicle["media"]["current_track"] by 1
            - No upper bound limit (simulated backend doesn't validate playlist length)
            
        Note:
            In a real Tesla, this would skip to the next track in Spotify, TuneIn,
            Bluetooth audio, or whatever media source is active.
            
        Example:
            >>> result = api.media_next_track(vehicle_id)
            >>> # Now playing next track
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
        Skips to the previous track in the current media playlist or queue.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/media_prev_track endpoint.
        Goes back to the previous song, podcast episode, or audio track.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Decrements vehicle["media"]["current_track"] by 1 (floored at 0)
            - If already at track 0, remains at 0
            
        Note:
            In a real Tesla, pressing previous within the first few seconds goes to the
            prior track, otherwise restarts the current track. This simulation always
            goes to the previous track.
            
        Example:
            >>> result = api.media_prev_track(vehicle_id)
            >>> # Now playing previous track
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
        Opens or closes the specified trunk (frunk or rear trunk) of the vehicle.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/actuate_trunk endpoint.
        Tesla vehicles have two trunks: front trunk ("frunk") and rear trunk.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
            which_trunk (Literal["front", "rear"]): Which trunk to actuate
                - "front": Front trunk (frunk) - small storage compartment under hood
                - "rear": Rear trunk - main cargo area

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["trunk"][which_trunk] = "open" in vehicle state
            - In a real vehicle, the specified trunk would unlatch/open
            
        Note:
            - Front trunk (frunk) typically opens automatically when unlatched
            - Rear trunk may need manual closing on older models
            - Power liftgate models can close rear trunk remotely via separate command
            - This simulation only supports "open" state, not close
            
        Example:
            >>> # Open front trunk (frunk)
            >>> result = api.actuate_trunk(vehicle_id, "front")
            >>> # Open rear trunk
            >>> result = api.actuate_trunk(vehicle_id, "rear")
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
        Sets the maximum charge limit percentage for the vehicle's battery.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/set_charge_limit endpoint.
        Controls how full the battery charges when plugged in. Tesla recommends 80% for daily use
        and 100% only for long trips to maximize battery longevity.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
            limit (int): Desired charge limit percentage. Valid range: 0-100
                - 50-60%: Ideal for long-term storage
                - 80-90%: Recommended for daily use (balances range and battery health)
                - 100%: Full charge for long trips (degrades battery faster if used daily)

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            Exception: If limit is not in valid range (0-100)
                Error message: "Charge limit must be between 0 and 100"
            
        Side Effects:
            - Sets vehicle["charge"]["limit"] to the specified percentage
            - Vehicle will stop charging when battery reaches this level
            
        Note:
            Battery health: Regularly charging to 100% can degrade lithium-ion batteries faster.
            Tesla's recommendations:
            - Daily driving: 80-90%
            - Long trips: 100% (charge shortly before departure)
            - Long-term storage: 50-60%
            
        Example:
            >>> # Set to 80% for daily use
            >>> result = api.set_charge_limit(vehicle_id, 80)
            >>> # Set to 100% before a road trip
            >>> result = api.set_charge_limit(vehicle_id, 100)
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
        Opens the charge port door or unlocks the charging cable.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/charge_port_door_open endpoint.
        Opens the charge port door to allow plugging in a charging cable. If already plugged in,
        this unlocks the cable so it can be removed.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["charge"]["port_open"] = True in vehicle state
            - In a real vehicle:
              * If unplugged: Opens the charge port door (flap)
              * If plugged in: Unlocks the cable connector
            
        Note:
            The charge port is typically on the driver's side rear quarter panel (US models)
            or passenger side (EU/UK models). The port door also opens automatically when
            a Tesla Supercharger cable approaches (if enabled in settings).
            
        Example:
            >>> # Open charge port to plug in
            >>> result = api.charge_port_door_open(vehicle_id)
            >>> # Port is now open and ready for charging cable
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
        Closes the charge port door.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/charge_port_door_close endpoint.
        Closes the charge port door/flap after unplugging the charging cable. Only works when
        no cable is connected.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["charge"]["port_open"] = False in vehicle state
            - In a real vehicle, the charge port door closes
            
        Note:
            - Only works when no charging cable is connected
            - If cable is connected, first unlock/remove it with charge_port_door_open
            - The port may auto-close after unplugging on some models
            - Useful for aerodynamics or aesthetics when not charging
            
        Example:
            >>> # Close charge port after unplugging
            >>> result = api.charge_port_door_close(vehicle_id)
            >>> # Port is now closed
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
        Starts charging the vehicle if it's plugged in but not currently charging.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/charge_start endpoint.
        Initiates charging when the vehicle is connected to a charger. Useful if charging
        was manually stopped or if you want to resume after a scheduled charge pause.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["charge"]["charging"] = True in vehicle state
            - In a real vehicle, charging begins immediately (if plugged in)
            
        Note:
            - Vehicle must be plugged into a charger for this to work
            - Charging continues until the charge limit is reached
            - Real Tesla may fail if: not plugged in, charge port latch issue, or
              scheduled charging is waiting for off-peak hours
            
        Example:
            >>> # Resume charging after manual stop
            >>> result = api.charge_start(vehicle_id)
            >>> # Charging has started
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
        Stops charging the vehicle if it's currently charging.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/charge_stop endpoint.
        Pauses/stops the charging process while keeping the cable connected. Useful if you
        need to limit charge for any reason or pause during peak electricity rates.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["charge"]["charging"] = False in vehicle state
            - In a real vehicle, charging stops but cable remains connected
            
        Note:
            - Cable remains locked in the charge port after stopping
            - Can resume charging with charge_start() without unplugging
            - Useful for:
              * Pausing during peak electricity rates
              * Preventing overcharge if you realize you've set limit too high
              * Testing or maintenance purposes
            - At Superchargers, idle fees may apply if you stop charging before unplugging
            
        Example:
            >>> # Stop charging temporarily
            >>> result = api.charge_stop(vehicle_id)
            >>> # Charging has stopped (cable still connected)
            >>> # Can resume later with charge_start()
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
        Starts the climate control (HVAC) system to pre-condition the vehicle cabin.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/auto_conditioning_start endpoint.
        Activates heating or cooling to bring the cabin to the target temperature. Useful for
        pre-heating in winter or pre-cooling in summer before you get in the vehicle.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["climate"]["on"] = True in vehicle state
            - In a real vehicle:
              * HVAC system activates
              * Heats or cools cabin to target temperature
              * May activate heated seats/steering wheel if enabled
              * Draws power from battery (parked) or slightly reduces range (while driving)
            
        Note:
            - Temperature targets are set via set_temps() method
            - Climate can run for up to 30 minutes remotely (Tesla safety limit)
            - Uses significant battery power when parked (~2-5 kW)
            - Can be controlled via Tesla mobile app or this API
            - Often used before departure to have cabin comfortable
            
        Example:
            >>> # Start climate before getting in car
            >>> result = api.auto_conditioning_start(vehicle_id)
            >>> # HVAC is now running, cabin heating/cooling to target temp
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
        Stops the climate control (HVAC) system.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/auto_conditioning_stop endpoint.
        Turns off heating/cooling to conserve battery power. The cabin will gradually return
        to ambient temperature.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["climate"]["on"] = False in vehicle state
            - In a real vehicle:
              * HVAC system deactivates
              * Heated seats/steering wheel turn off
              * Cabin temperature drifts toward ambient
              * Reduces battery drain
            
        Note:
            - Useful for conserving battery when climate is no longer needed
            - Climate auto-stops after 30 minutes remotely (Tesla safety feature)
            - When driving, climate should normally stay on for comfort
            - Does NOT affect Climate Keeper mode (separate feature for parked vehicle)
            
        Example:
            >>> # Stop climate to save battery
            >>> result = api.auto_conditioning_stop(vehicle_id)
            >>> # HVAC is now off
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
        Sets the target temperatures for driver and passenger sides (dual-zone climate control).
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/set_temps endpoint.
        Tesla vehicles have dual-zone climate control allowing different temperatures for
        driver and passenger sides. Temperatures are in Celsius.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
            driver_temp (float): Desired temperature for driver side in Celsius.
                Valid range: 15°C to 30°C (59°F to 86°F)
                Common settings:
                - 18°C (64°F): Cool
                - 21°C (70°F): Moderate
                - 24°C (75°F): Warm
            passenger_temp (float): Desired temperature for passenger side in Celsius.
                Valid range: 15°C to 30°C (59°F to 86°F)
                Can be same as driver_temp or different for passenger preference

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            Exception: If either temperature is outside valid range (15-30°C)
                Error message: "Temperatures must be between 15 and 30 Celsius"
            
        Side Effects:
            - Sets vehicle["climate"]["driver_temp"] to specified value
            - Sets vehicle["climate"]["passenger_temp"] to specified value
            - In a real vehicle, HVAC adjusts to reach target temperatures
            
        Note:
            - Temperature range is 15-30°C (Tesla's operational limits)
            - Must call auto_conditioning_start() to activate HVAC
            - Setting temps doesn't automatically turn on climate
            - Can set both zones to same temp for single-zone behavior
            - Real app allows 0.5°C increments; API accepts float values
            
        Example:
            >>> # Set driver to 21°C, passenger to 23°C
            >>> result = api.set_temps(vehicle_id, 21.0, 23.0)
            >>> # Now start climate to reach these temps
            >>> api.auto_conditioning_start(vehicle_id)
        """
        vehicle = self._get_vehicle(vehicle_id)
        
        if not (15 <= driver_temp <= 30) or not (15 <= passenger_temp <= 30):
            raise Exception("Temperatures must be between 15 and 30 Celsius")

        vehicle["climate"]["driver_temp"] = driver_temp
        vehicle["climate"]["passenger_temp"] = passenger_temp
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def set_bioweapon_mode(self, vehicle_id: int, on: bool) -> Dict[str, Any]:
        """
        Enables or disables Bioweapon Defense Mode (maximum air filtration).
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/set_bioweapon_mode endpoint.
        Activates maximum positive cabin pressure using the HEPA filtration system (Model S/X/Y).
        Filters out pollution, allergens, bacteria, and viruses.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
            on (bool): Whether to enable (True) or disable (False) Bioweapon Defense Mode

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["climate"]["bioweapon_mode"] = on in vehicle state
            - In a real vehicle:
              * HEPA filter runs at maximum speed
              * Cabin pressure increases (positive pressure keeps outside air out)
              * Filters particles down to 0.01 microns (bacteria, viruses, pollen)
              * Uses more battery power than normal climate
              * May be louder than normal HVAC operation
            
        Note:
            - Only available on vehicles equipped with HEPA filter (most Model S/X/Y)
            - Model 3 Standard Range typically doesn't have HEPA filter
            - Useful in:
              * Heavy pollution areas
              * Wildfire smoke conditions
              * High pollen seasons
              * Areas with airborne contaminants
            - Can run in conjunction with regular climate control
            - Named "Bioweapon Defense Mode" as Tesla marketing humor
            
        Example:
            >>> # Enable maximum filtration in smoky conditions
            >>> result = api.set_bioweapon_mode(vehicle_id, True)
            >>> # HEPA filter now running at maximum
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
        Sets the Climate Keeper mode for maintaining cabin temperature when parked and unoccupied.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/set_climate_keeper_mode endpoint.
        Climate Keeper maintains comfortable cabin temperature when you leave the vehicle parked,
        useful for pets or camping.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
            climate_keeper_mode (int): The Climate Keeper mode to set:
                - 0: Off - Climate turns off when you leave (normal behavior)
                - 1: Dog Mode - Maintains ~20-22°C (68-72°F) for pets
                  * Displays "My owner will be back soon" on screen
                  * Shows current cabin temperature
                  * Alerts on phone if cabin temperature becomes unsafe
                - 2: Camp Mode - Maintains set temperature for camping
                  * Keeps climate, music, USB ports active
                  * Screen stays on for entertainment
                  * For sleeping in the vehicle overnight

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            Exception: If climate_keeper_mode is not 0, 1, or 2
                Error message: "Invalid climate keeper mode. Must be 0 (off), 1 (dog), or 2 (camp)"
            
        Side Effects:
            - Sets vehicle["climate"]["climate_keeper_mode"] to "off", "dog", or "camp"
            - In a real vehicle:
              * Mode 1 (Dog): Shows pet-safe message on display, monitors temperature
              * Mode 2 (Camp): Keeps all systems active for comfort
              * Both modes drain battery continuously (monitor charge level)
            
        Note:
            - Dog Mode is legally required in some jurisdictions when leaving pets
            - Both modes drain battery significantly (5-10% per hour in extreme temps)
            - Vehicle must have sufficient battery (>20% recommended)
            - Alerts sent to phone if battery drops too low or temperature unsafe
            - Camp Mode useful for car camping, tailgating, or long waits
            
        Example:
            >>> # Enable Dog Mode before leaving pet in car
            >>> result = api.set_climate_keeper_mode(vehicle_id, 1)
            >>> # Dog Mode active, cabin will stay comfortable
            >>> 
            >>> # Enable Camp Mode for overnight camping
            >>> result = api.set_climate_keeper_mode(vehicle_id, 2)
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
        Wakes up the vehicle from sleep mode to enable remote commands.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/wake_up endpoint.
        Tesla vehicles enter deep sleep after ~15-30 minutes of inactivity to conserve battery.
        Most commands require the vehicle to be awake/online.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["awake"] = True in vehicle state
            - Sets vehicle["state"] = "online"
            - In a real vehicle:
              * Vehicle computers wake up (~10-30 seconds)
              * Cellular connection established
              * Vehicle ready to accept commands
              * Slight battery drain while awake
            
        Note:
            - Required before sending most commands to a sleeping vehicle
            - May take 10-30 seconds for vehicle to fully wake
            - Vehicle returns to sleep after ~15-30 minutes of API inactivity
            - Frequent waking can cause "vampire drain" (battery drain while parked)
            - Some commands (like vehicle_data) auto-wake the vehicle
            - Check vehicle["state"] to see if wake_up is needed
            
        Example:
            >>> # Check if vehicle is asleep
            >>> vehicles = api.list_vehicles()
            >>> if vehicles['response'][0]['state'] == 'asleep':
            ...     # Wake it up
            ...     result = api.wake_up(vehicle_id)
            ...     # Wait a few seconds, then send commands
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["awake"] = True
        vehicle["state"] = "online"
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def window_control(self, vehicle_id: int, command: Literal["vent", "close"]) -> Dict[str, Any]:
        """
        Controls all windows simultaneously (vent or close all).
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/window_control endpoint.
        Opens all windows slightly for ventilation or closes all windows for security/weather protection.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
            command (Literal["vent", "close"]): The window control command:
                - "vent": Opens all windows ~2-3 inches for ventilation
                - "close": Fully closes all windows

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["windows"] = command ("vent" or "close")
            - In a real vehicle:
              * "vent": All four windows open partially (~2-3 inches)
              * "close": All four windows close completely
              * Operation takes ~5-10 seconds
            
        Note:
            - All windows move simultaneously (no individual window control via API)
            - "vent" is useful for:
              * Cooling hot cabin before entering
              * Fresh air circulation when parked
              * Preventing greenhouse effect in sun
            - "close" ensures all windows sealed for:
              * Security when leaving vehicle
              * Weather protection (rain, snow)
              * Locking vehicle properly
            - Windows also have pinch protection (stop if obstruction detected)
            - Cannot open windows fully via API (safety/security limitation)
            
        Example:
            >>> # Vent windows to cool hot cabin
            >>> result = api.window_control(vehicle_id, "vent")
            >>> # Windows now open ~2-3 inches
            >>> 
            >>> # Close all windows before leaving
            >>> result = api.window_control(vehicle_id, "close")
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
        Retrieves the current GPS location and speed of the specified vehicle.
        
        Matches the Tesla Fleet API GET /api/1/vehicles/{id}/data_request/drive_state endpoint.
        Returns real-time location data useful for tracking, navigation, or fleet management.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper:
                {
                    "response": {
                        "latitude": float,       # GPS latitude in decimal degrees (-90 to 90)
                        "longitude": float,      # GPS longitude in decimal degrees (-180 to 180)
                        "speed": int             # Current speed in mph (0 if parked)
                    },
                    "error": None                # Always None on success
                }
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Note:
            - Location accuracy typically within 5-10 meters (GPS precision)
            - Speed is in miles per hour (mph), not km/h
            - Speed is 0 when vehicle is parked/stopped
            - Location updates every few seconds while driving
            - Privacy: Only vehicle owner can access location data
            - Real endpoint includes additional fields (heading, power, shift_state, etc.)
            - Useful for:
              * Fleet management tracking
              * Finding parked vehicle
              * Geo-fencing applications
              * Trip logging
            
        Example:
            >>> result = api.get_vehicle_location(vehicle_id)
            >>> loc = result['response']
            >>> print(f"Vehicle at: {loc['latitude']}, {loc['longitude']}")
            >>> print(f"Speed: {loc['speed']} mph")
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
        Retrieves comprehensive status information for the specified vehicle.
        
        Matches the Tesla Fleet API GET /api/1/vehicles/{id}/vehicle_data endpoint.
        Returns a detailed snapshot of all vehicle systems including identification, location,
        charge state, climate state, and vehicle state.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper:
                {
                    "response": {
                        "id": int,                    # Numeric vehicle ID
                        "vehicle_id": int,            # Same as id
                        "vin": str,                   # Vehicle Identification Number
                        "display_name": str,          # User-friendly vehicle name
                        "state": str,                 # "online" or "asleep"
                        "in_service": bool,           # True if in Tesla service center
                        "firmware_version": str,      # Current software version
                        "awake": bool,                # True if vehicle is awake
                        "speed": int,                 # Current speed in mph
                        "location": {                 # GPS coordinates
                            "latitude": float,
                            "longitude": float
                        },
                        "charge_state": {             # Battery and charging info
                            "battery_level": int,     # Battery percentage
                            "charging": bool,         # True if currently charging
                            "charge_limit": int,      # Charge limit percentage
                            "port_open": bool,        # True if charge port open
                            ...
                        },
                        "climate_state": {            # HVAC and temperature info
                            "on": bool,               # True if climate running
                            "driver_temp": float,     # Driver temp setting (°C)
                            "passenger_temp": float,   # Passenger temp setting (°C)
                            ...
                        },
                        "vehicle_state": {            # Locks, doors, trunk status
                            "locked": bool,           # True if doors locked
                            "sentry_mode": dict,      # Sentry mode settings
                            "ft": str,                # Front trunk state
                            "rt": str,                # Rear trunk state
                        },
                        "drive_state": dict          # Location and driving info
                    },
                    "error": None                     # Always None on success
                }
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Note:
            - This is a comprehensive status endpoint combining multiple data categories
            - Similar to get_vehicle_data() but organized into state categories
            - Useful for dashboard displays or monitoring systems
            - All sub-states are from the vehicle object (charge, climate, location, etc.)
            - Real Tesla API has many more fields in each state category
            
        Example:
            >>> result = api.get_vehicle_status(vehicle_id)
            >>> status = result['response']
            >>> print(f"Vehicle: {status['display_name']}")
            >>> print(f"State: {status['state']}")
            >>> print(f"Battery: {status['charge_state']['battery_level']}%")
            >>> print(f"Locked: {status['vehicle_state']['locked']}")
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
        Enables or disables Sentry Mode (security monitoring system).
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/set_sentry_mode endpoint.
        Sentry Mode uses the vehicle's external cameras to monitor surroundings and record
        potential threats when parked.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
            on (bool): Whether to enable (True) or disable (False) Sentry Mode

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["sentry_mode"]["on"] = on in vehicle state
            - In a real vehicle when enabled:
              * All external cameras activate and monitor continuously
              * Screen displays "Sentry Mode Enabled" warning to deter theft
              * Motion detected: "Alert" state - saves 10-min clips to USB drive
              * Heavy impact: "Alarm" state - triggers alarm, saves footage, sends notification
              * Uses ~1% battery per hour (significant drain if used long-term)
            
        Note:
            - Requires USB drive (formatted for TeslaCam) to save footage
            - Without USB drive, Sentry Mode still monitors but doesn't record
            - Battery impact: ~0.5-1% per hour (can drain battery over days)
            - Not recommended when:
              * Battery is low (<20%)
              * Parked long-term (will drain battery)
              * In safe/secure location (unnecessary drain)
            - Recommended when:
              * Parked in public places
              * High-crime areas
              * Overnight street parking
              * Any situation where vehicle security is a concern
            - Videos saved to /TeslaCam/SentryClips/ on USB drive
            - Can exclude specific locations in vehicle settings (home, work)
            
        Example:
            >>> # Enable Sentry Mode when parking in public
            >>> result = api.set_sentry_mode(vehicle_id, True)
            >>> # Cameras now monitoring and recording
            >>> 
            >>> # Disable when returning or to save battery
            >>> result = api.set_sentry_mode(vehicle_id, False)
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
        Retrieves firmware (software) version and update information for the specified vehicle.
        
        Returns the current software version installed on the vehicle and timestamp metadata.
        Tesla regularly releases over-the-air (OTA) software updates with new features and improvements.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper:
                {
                    "response": {
                        "current_version": str,      # Current firmware version (e.g., "2024.20.7")
                        "created_time": str,         # Vehicle creation timestamp
                        "modified_time": str         # Last modification timestamp
                    },
                    "error": None                    # Always None on success
                }
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Note:
            - Firmware version format: YYYY.WW.# (year.week.revision)
              Example: "2024.20.7" = 2024, week 20, revision 7
            - Tesla releases updates every 2-4 weeks on average
            - Updates include:
              * New features (games, autopilot improvements, UI changes)
              * Bug fixes and performance improvements
              * Security patches
            - Vehicles download updates over WiFi (cellular too slow for large files)
            - User must approve installation (prompts on screen)
            - Installation takes ~30 minutes, vehicle unusable during update
            - "Unknown" returned if firmware_version not set in backend
            
        Example:
            >>> result = api.get_firmware_info(vehicle_id)
            >>> fw = result['response']
            >>> print(f"Current firmware: {fw['current_version']}")
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
        Wakes up the specified vehicle from sleep mode to enable remote commands.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/wake_up endpoint.
        This is a duplicate/alias of wake_up() method - both perform the same operation.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            
        Side Effects:
            - Sets vehicle["awake"] = True in vehicle state
            - Sets vehicle["state"] = "online"
            
        Note:
            This method is identical to wake_up(). Both exist for API compatibility.
            See wake_up() documentation for detailed information about wake behavior,
            timing, battery impact, and best practices.
            
        Example:
            >>> result = api.wake_vehicle(vehicle_id)
            >>> # Vehicle is now waking up (takes ~10-30 seconds)
        """
        vehicle = self._get_vehicle(vehicle_id)
        vehicle["awake"] = True
        vehicle["state"] = "online"
        return {
            "response": {
                "result": True,
                "reason": ""
            },
            "error": None
        }

    def set_speed_limit(self, vehicle_id: int, limit_mph: int) -> Dict[str, Any]:
        """
        Sets a maximum speed limit for the vehicle (Speed Limit Mode).
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/speed_limit_set_limit endpoint.
        When Speed Limit Mode is active, the vehicle cannot exceed this speed limit. Useful for
        parental controls, fleet management, or valet scenarios.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
            limit_mph (int): Maximum allowed speed in miles per hour (mph).
                Valid range: 0-140 mph
                Common settings:
                - 25 mph: Parking lot speed
                - 55 mph: Highway speed for teen drivers
                - 65-75 mph: General highway speeds
                - 140 mph: Maximum (essentially disables limit)

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            Exception: If limit_mph is outside valid range (0-140)
                Error message: "Speed limit must be between 0 and 140 mph"
            
        Side Effects:
            - Sets vehicle["speed_limit"] = limit_mph in vehicle state
            - In a real vehicle (when Speed Limit Mode is active):
              * Vehicle acceleration limited to prevent exceeding limit
              * Speedometer shows limit indicator
              * Audio/visual alert if approaching limit
              * Chime sounds if limit exceeded (though vehicle prevents it)
            
        Note:
            - Setting the limit alone doesn't activate Speed Limit Mode
            - Must also enable Speed Limit Mode and set PIN (separate from this API)
            - Speed Limit Mode requires 4-digit PIN to disable (security feature)
            - Common use cases:
              * Teen drivers: Parents can limit max speed
              * Valet mode: Combine with valet_mode for service parking
              * Fleet vehicles: Company speed policy enforcement
              * Driving schools: Instructor-controlled speed limits
            - Limit is in mph regardless of vehicle's display unit setting
            - 0 mph is technically valid but would make vehicle undriveable
            - 140 mph is Tesla's software maximum (most Teslas limited to ~155 mph physically)
            
        Example:
            >>> # Set 65 mph limit for teen driver
            >>> result = api.set_speed_limit(vehicle_id, 65)
            >>> # Then enable Speed Limit Mode on vehicle screen with PIN
            >>> 
            >>> # Set 25 mph limit for valet parking
            >>> result = api.set_speed_limit(vehicle_id, 25)
            >>> api.set_valet_mode(vehicle_id, True, "1234")
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
        Enables or disables Valet Mode with PIN security for the specified vehicle.
        
        Matches the Tesla Fleet API POST /api/1/vehicles/{id}/command/set_valet_mode endpoint.
        Valet Mode restricts vehicle functionality when giving keys to valet parking attendants
        or service personnel. Limits speed, power, and access to personal information.

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
            on (bool): Whether to enable (True) or disable (False) Valet Mode
            pin (Optional[str], optional): 4-digit PIN code for security.
                - Required when enabling (on=True)
                - Used to disable Valet Mode later
                - Must be 4 digits (e.g., "1234")
                - Not needed when disabling if already in Valet Mode

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper with result/reason
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            Exception: If on=True and pin is None or empty
                Error message: "PIN code is required to enable valet mode"
            
        Side Effects:
            - Sets vehicle["valet_mode"]["on"] = on
            - Sets vehicle["valet_mode"]["pin"] = pin (when enabling) or None (when disabling)
            - In a real vehicle when enabled:
              * Limits acceleration and top speed (~70 mph typical)
              * Restricts maximum power output (~25% of normal)
              * Locks glove box and frunk
              * Disables Autopilot/FSD features
              * Hides HomeLink garage door opener
              * Hides navigation history and saved locations
              * Prevents access to driver profiles
              * Disables voice commands
              * Cannot disable Valet Mode without PIN
            
        Note:
            - Designed for valet parking at restaurants, hotels, airports
            - PIN prevents valet from disabling restrictions
            - Speed limit for Valet Mode typically ~70 mph (varies by region)
            - Also useful when lending vehicle to others
            - Different from Speed Limit Mode (can be used together)
            - Valet won't be able to:
              * Access your home address or favorite locations
              * Open locked storage compartments
              * Use full vehicle performance
              * Modify vehicle settings
            - Remember your PIN! Without it, you'll need Tesla service to reset
            
        Example:
            >>> # Enable Valet Mode before giving keys to valet
            >>> result = api.set_valet_mode(vehicle_id, True, "1234")
            >>> # Vehicle now in restricted Valet Mode
            >>> 
            >>> # Disable Valet Mode when you get vehicle back
            >>> # (PIN verification happens on vehicle screen, not in API)
            >>> result = api.set_valet_mode(vehicle_id, False)
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
        Calculates the great-circle distance between two GPS coordinates using the Haversine formula.
        
        Computes the shortest distance over the Earth's surface between two points, accounting
        for the Earth's curvature. More accurate than simple Euclidean distance for geographic coordinates.
        
        Args:
            lat1 (float): Latitude of first point in decimal degrees.
                Valid range: -90 to 90 (negative = South, positive = North)
            lon1 (float): Longitude of first point in decimal degrees.
                Valid range: -180 to 180 (negative = West, positive = East)
            lat2 (float): Latitude of second point in decimal degrees.
            lon2 (float): Longitude of second point in decimal degrees.
            
        Returns:
            float: Distance between the two points in miles (statute miles, not nautical).
                Accurate to within ~0.5% for distances up to a few hundred miles.
                
        Note:
            - Uses Haversine formula: a = sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlon/2)
            - Earth's radius used: 3959 miles (mean radius)
            - Assumes spherical Earth (good approximation for most purposes)
            - For higher accuracy over very long distances, use Vincenty formula
            - Returns straight-line distance ("as the crow flies"), not driving distance
            - Does not account for:
              * Road networks or routes
              * Terrain elevation changes
              * Earth's ellipsoidal shape (minor effect <0.5%)
            
        Example:
            >>> # Distance from San Francisco to Los Angeles
            >>> dist = api._calculate_distance(37.7749, -122.4194, 34.0522, -118.2437)
            >>> print(f"{dist:.1f} miles")  # ~347 miles
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
        Finds nearby Tesla Supercharger stations within a specified radius of the vehicle's current location.
        
        Matches the Tesla Fleet API GET /api/1/vehicles/{id}/nearby_charging_sites endpoint.
        Searches for Supercharger stations using the vehicle's GPS coordinates and calculates
        distances. Includes real-time stall availability (simulated as random in backend).

        Args:
            vehicle_id (int): Numeric Tesla vehicle ID
            radius (int, optional): Search radius in miles. Defaults to 50.
                Typical values:
                - 10-25 miles: Urban/city driving
                - 50 miles: Default, good for most scenarios  
                - 100 miles: Long-distance travel planning
                - 200+ miles: Emergency low-battery situations

        Returns:
            Dict[str, Any]: Tesla API standard response wrapper:
                {
                    "response": {
                        "congestion_sync_time_utc_secs": int,  # Timestamp (0 in simulation)
                        "destination_charging": [],             # Destination chargers (empty in simulation)
                        "superchargers": [                      # List of nearby Superchargers
                            {
                                "name": str,                    # Site name (e.g., "Fremont, CA - Supercharger")
                                "latitude": float,              # GPS latitude
                                "longitude": float,             # GPS longitude
                                "distance": float,              # Distance from vehicle in miles (1 decimal)
                                "available_stalls": int,        # Currently available charging stalls
                                "total_stalls": int,            # Total stalls at this site
                                "site_type": "supercharger",   # Always "supercharger"
                                "address": str                  # Street address (if available)
                            },
                            ...
                        ],
                        "timestamp": int                        # Unix timestamp (0 in simulation)
                    },
                    "error": None                               # Always None on success
                }
                Superchargers are sorted by distance (nearest first).
            
        Raises:
            Exception: If not authenticated, vehicle not found, or not accessible
            Exception: If vehicle doesn't have valid location data
                Error message: "Vehicle {vehicle_id} does not have a valid location"
            
        Note:
            - Uses vehicle's current GPS location (must have valid latitude/longitude)
            - Distance calculated using Haversine formula (great-circle distance)
            - Simulated availability: random value between (total_stalls - 4) and total_stalls
            - Real Tesla API provides:
              * Real-time stall availability from Supercharger network
              * Charging speeds (V2: 150kW, V3: 250kW, V4: 350kW+)
              * Pricing information
              * Amenities (restrooms, food, WiFi)
              * Peak hours and congestion predictions
            - Supercharger types:
              * V2: 150 kW max, shared power between stall pairs
              * V3: 250 kW max, dedicated power per stall (preferred)
              * V4: 350 kW+ max (newest, limited deployment)
            - Typical charging times at Supercharger:
              * 20-80%: 20-30 minutes (optimal range)
              * 0-100%: 45-60 minutes (slower above 80%)
            - Trip planning: Tesla navigation automatically routes via Superchargers
            
        Example:
            >>> # Find Superchargers within 50 miles
            >>> result = api.get_nearby_charging_sites(vehicle_id, radius=50)
            >>> chargers = result['response']['superchargers']
            >>> for sc in chargers[:3]:  # Show 3 nearest
            ...     avail = sc['available_stalls']
            ...     total = sc['total_stalls']
            ...     print(f"{sc['name']}: {sc['distance']} mi - {avail}/{total} stalls available")
            >>> 
            >>> # Find all Superchargers within 100 miles for road trip
            >>> result = api.get_nearby_charging_sites(vehicle_id, radius=100)
            >>> print(f"Found {len(result['response']['superchargers'])} Superchargers")
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
        Resets the entire simulated backend to its default state for testing purposes.
        
        This is a utility function for development and testing, not a standard Tesla API endpoint.
        Reloads the default scenario data and clears authentication state, effectively resetting
        the simulation to a clean starting point. All vehicles return to their initial state.

        Returns:
            Dict[str, bool]: Status indicator:
                {
                    "reset_status": True  # Always True (reset successful)
                }
            
        Side Effects:
            - Clears authentication: access_token set to None
            - Clears current user: current_user_id set to None
            - Reloads all data (users, vehicles) from DEFAULT_STATE via _load_scenario()
            - Rebuilds global vehicle registry with fresh data
            - All vehicle state changes are lost:
              * Charge levels reset to default
              * Climate settings reset
              * Lock states reset
              * Location changes reset
              * Media state reset
              * Any commands issued are undone
            
        Warning:
            This is destructive! All changes made during the session (horn honks,
            door locks, charge starts, climate changes, etc.) will be lost.
            Use with caution, primarily for testing.
            
        Note:
            - This method does NOT require authentication (can reset from any state)
            - After reset, you must call authenticate() again before using vehicle commands
            - Useful for:
              * Resetting state between test cases
              * Recovering from error states
              * Starting fresh without restarting the application
            - Vehicle IDs remain the same (generated from same UUIDs)
            - Supercharger locations unchanged (loaded from same scenario)
            
        Example:
            >>> api = TeslaFleetApis()
            >>> api.authenticate("token_hayden@example.com")
            >>> vehicle_id = api.list_vehicles()['response'][0]['id']
            >>> api.honk_horn(vehicle_id)
            >>> api.door_unlock(vehicle_id)
            >>> 
            >>> # Reset everything
            >>> result = api.reset_data()
            >>> print(result)  # {"reset_status": True}
            >>> 
            >>> # Must authenticate again
            >>> api.authenticate("token_hayden@example.com")
            >>> # Vehicle state is back to original (doors locked, horn not honked)
        """
        self.access_token = None
        self.current_user_id = None
        self._load_scenario(DEFAULT_STATE)
        return {"reset_status": True}
