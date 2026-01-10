import unittest
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import API and helper
from TeslaFleetApis import TeslaFleetApis, User
from UnitTests.test_data_helper import BackendDataLoader

class TestTeslaFleetApis(unittest.TestCase):
    """
    Unit tests for the TeslaFleetApis class, covering multi-user functionality.
    """

    # Load real data from backend
    real_data = BackendDataLoader.get_teslafleet_data()

    # Extract real user data properly from nested structure - pick users with vehicles
    all_users = list(real_data.get("users", {}).values())
    users_with_vehicles = [u for u in all_users if u.get("tesla_data", {}).get("vehicles")]
    user_data_alice = users_with_vehicles[0] if users_with_vehicles else all_users[0] if all_users else {}
    user_data_bob = users_with_vehicles[1] if len(users_with_vehicles) > 1 else users_with_vehicles[0] if users_with_vehicles else user_data_alice

    REAL_USER_ALICE = User(email=user_data_alice.get("email", "alice@example.com"))
    REAL_USER_BOB = User(email=user_data_bob.get("email", "bob@example.com"))

    # Extract real vehicle data from nested structure
    alice_tesla_data = user_data_alice.get("tesla_data", {})
    alice_vehicles = alice_tesla_data.get("vehicles", {})
    alice_vehicle_uuids = list(alice_vehicles.keys())
    alice_vehicle_data = alice_vehicles[alice_vehicle_uuids[0]] if alice_vehicle_uuids else {}

    bob_tesla_data = user_data_bob.get("tesla_data", {})
    bob_vehicles = bob_tesla_data.get("vehicles", {})
    bob_vehicle_uuids = list(bob_vehicles.keys())
    bob_vehicle_data = bob_vehicles[bob_vehicle_uuids[0]] if bob_vehicle_uuids else {}

    REAL_VEHICLE_TAG_ALICE = alice_vehicle_data.get("original_vehicle_tag", "genesis_cybertruck_1")
    REAL_VEHICLE_TAG_BOB = bob_vehicle_data.get("original_vehicle_tag", "olivia_roadster_1")
    REAL_VEHICLE_NAME = alice_vehicle_data.get("vehicle_tag", "Model S")

    def setUp(self):
        """Set up the API instance using real data."""
        self.tesla_api = TeslaFleetApis()
        
        # Authenticate Alice and get her vehicle ID
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        vehicles_alice = self.tesla_api.list_vehicles()
        self.alice_vehicle_id = vehicles_alice['response'][0]['id'] if vehicles_alice['response'] else None
        
        # Authenticate Bob and get his vehicle ID
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        vehicles_bob = self.tesla_api.list_vehicles()
        self.bob_vehicle_id = vehicles_bob['response'][0]['id'] if vehicles_bob['response'] else None
        
        # Set back to Alice by default
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")

    # --- User Management Tests ---
    def test_authenticate_alice(self):
        """Test authenticating as Alice."""
        result = self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        self.assertIn("response", result)
        self.assertEqual(result["response"]["email"], self.REAL_USER_ALICE.email)
        self.assertIsNone(result["error"])

    def test_authenticate_bob(self):
        """Test authenticating as Bob."""
        result = self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        self.assertIn("response", result)
        self.assertEqual(result["response"]["email"], self.REAL_USER_BOB.email)
        self.assertIsNone(result["error"])

    def test_authenticate_non_existent(self):
        """Test authenticating with non-existent email."""
        with self.assertRaises(Exception) as context:
            self.tesla_api.authenticate("token_nonexistent@example.com")
        self.assertIn("not found", str(context.exception).lower())

    # --- Vehicle Info Tests ---
    def test_list_vehicles_alice(self):
        """Test listing vehicles for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.list_vehicles()
        self.assertIn("response", result)
        self.assertIsInstance(result["response"], list)
        self.assertGreater(len(result["response"]), 0)

    def test_get_vehicle_data_alice(self):
        """Test getting vehicle data for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.get_vehicle_data(self.alice_vehicle_id)
        self.assertIn("response", result)
        self.assertIsInstance(result["response"], dict)
        self.assertIsNone(result["error"])

    def test_get_vehicle_data_invalid(self):
        """Test getting data for non-existent vehicle."""
        with self.assertRaises(Exception) as context:
            self.tesla_api.get_vehicle_data(999999999999999)
        self.assertIn("not found", str(context.exception).lower())

    # --- Vehicle Action Tests ---
    def test_honk_horn_alice(self):
        """Test honking horn for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.honk_horn(self.alice_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_honk_horn_bob(self):
        """Test honking horn for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.honk_horn(self.bob_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_honk_horn_non_existent_vehicle(self):
        """Test honking horn for non-existent vehicle."""
        with self.assertRaises(Exception) as context:
            self.tesla_api.honk_horn(999999999999999)
        self.assertIn("not found", str(context.exception).lower())

    def test_flash_lights_alice(self):
        """Test flashing lights for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.flash_lights(self.alice_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_flash_lights_bob(self):
        """Test flashing lights for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.flash_lights(self.bob_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_flash_lights_non_existent_vehicle(self):
        """Test flashing lights for non-existent vehicle."""
        with self.assertRaises(Exception) as context:
            self.tesla_api.flash_lights(999999999999999)
        self.assertIn("not found", str(context.exception).lower())

    def test_wake_up_alice(self):
        """Test waking up vehicle for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.wake_up(self.alice_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_wake_up_bob(self):
        """Test waking up vehicle for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.wake_up(self.bob_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_wake_vehicle_alice(self):
        """Test wake_vehicle method for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.wake_vehicle(self.alice_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_wake_vehicle_bob(self):
        """Test wake_vehicle method for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.wake_vehicle(self.bob_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    # --- Media Control Tests ---
    def test_media_toggle_playback_alice(self):
        """Test media toggle playback for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.media_toggle_playback(self.alice_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_media_toggle_playback_bob(self):
        """Test media toggle playback for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.media_toggle_playback(self.bob_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_adjust_volume_alice(self):
        """Test adjusting volume for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.adjust_volume(self.alice_vehicle_id, 50)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_adjust_volume_bob_max(self):
        """Test adjusting volume to max for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.adjust_volume(self.bob_vehicle_id, 100)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_adjust_volume_invalid_level(self):
        """Test adjusting to invalid volume level."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        with self.assertRaises(Exception) as context:
            self.tesla_api.adjust_volume(self.alice_vehicle_id, 150)
        self.assertIn("Volume level must be between", str(context.exception))

    def test_media_next_track_alice(self):
        """Test skipping to next track for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.media_next_track(self.alice_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_media_prev_track_bob(self):
        """Test skipping to previous track for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.media_prev_track(self.bob_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    # --- Trunk Control Tests ---
    def test_actuate_trunk_front_alice(self):
        """Test opening front trunk for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.actuate_trunk(self.alice_vehicle_id, "front")
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_actuate_trunk_rear_bob(self):
        """Test opening rear trunk for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.actuate_trunk(self.bob_vehicle_id, "rear")
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    # --- Charging Tests ---
    def test_set_charge_limit_alice(self):
        """Test setting charge limit for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.set_charge_limit(self.alice_vehicle_id, 80)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_set_charge_limit_bob_max(self):
        """Test setting charge limit to max for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.set_charge_limit(self.bob_vehicle_id, 100)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_set_charge_limit_invalid(self):
        """Test setting invalid charge limit."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        with self.assertRaises(Exception) as context:
            self.tesla_api.set_charge_limit(self.alice_vehicle_id, 150)
        self.assertIn("Charge limit must be between", str(context.exception))

    def test_charge_port_door_open_alice(self):
        """Test opening charge port for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.charge_port_door_open(self.alice_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_charge_port_door_close_bob(self):
        """Test closing charge port for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.charge_port_door_close(self.bob_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_charge_start_alice(self):
        """Test starting charge for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.charge_start(self.alice_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_charge_stop_bob(self):
        """Test stopping charge for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.charge_stop(self.bob_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    # --- Climate Control Tests ---
    def test_auto_conditioning_start_alice(self):
        """Test starting climate control for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.auto_conditioning_start(self.alice_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_auto_conditioning_stop_bob(self):
        """Test stopping climate control for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.auto_conditioning_stop(self.bob_vehicle_id)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_set_temps_alice(self):
        """Test setting climate temperatures for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.set_temps(self.alice_vehicle_id, 22.0, 20.0)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_set_temps_bob(self):
        """Test setting climate temperatures for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.set_temps(self.bob_vehicle_id, 20.0, 20.0)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_set_temps_invalid(self):
        """Test setting invalid climate temperature."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        with self.assertRaises(Exception) as context:
            self.tesla_api.set_temps(self.alice_vehicle_id, 50.0, 20.0)
        self.assertIn("must be between", str(context.exception).lower())

    def test_set_bioweapon_mode_on_alice(self):
        """Test turning bioweapon mode on for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.set_bioweapon_mode(self.alice_vehicle_id, True)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_set_bioweapon_mode_off_bob(self):
        """Test turning bioweapon mode off for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.set_bioweapon_mode(self.bob_vehicle_id, False)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_set_climate_keeper_mode_dog_alice(self):
        """Test setting climate keeper mode to dog for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.set_climate_keeper_mode(self.alice_vehicle_id, 1)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_set_climate_keeper_mode_camp_bob(self):
        """Test setting climate keeper mode to camp for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.set_climate_keeper_mode(self.bob_vehicle_id, 2)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_set_climate_keeper_mode_off(self):
        """Test turning climate keeper mode off."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.set_climate_keeper_mode(self.alice_vehicle_id, 0)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    # --- Window Control Tests ---
    def test_window_control_vent_alice(self):
        """Test venting windows for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.window_control(self.alice_vehicle_id, "vent")
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_window_control_close_bob(self):
        """Test closing windows for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.window_control(self.bob_vehicle_id, "close")
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    # --- Vehicle Status Tests ---
    def test_get_vehicle_data_location_alice(self):
        """Test getting vehicle location for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.get_vehicle_data(self.alice_vehicle_id)
        self.assertIn("response", result)
        self.assertIn("location", result["response"])
        self.assertIsNone(result["error"])

    def test_get_vehicle_data_location_bob(self):
        """Test getting vehicle location for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.get_vehicle_data(self.bob_vehicle_id)
        self.assertIn("response", result)
        self.assertIn("location", result["response"])
        self.assertIsNone(result["error"])

    def test_get_vehicle_data_non_existent(self):
        """Test getting data for non-existent vehicle."""
        with self.assertRaises(Exception) as context:
            self.tesla_api.get_vehicle_data(999999999999999)
        self.assertIn("not found", str(context.exception).lower())

    def test_get_vehicle_data_status_alice(self):
        """Test getting vehicle status for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.get_vehicle_data(self.alice_vehicle_id)
        self.assertIn("response", result)
        self.assertIn("charge", result["response"])
        self.assertIn("climate", result["response"])
        self.assertIsNone(result["error"])

    def test_get_vehicle_data_status_bob(self):
        """Test getting vehicle status for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.get_vehicle_data(self.bob_vehicle_id)
        self.assertIn("response", result)
        self.assertIsNone(result["error"])

    def test_get_vehicle_data_unauthorized(self):
        """Test getting data without proper access."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        # Try to access Bob's vehicle
        with self.assertRaises(Exception) as context:
            self.tesla_api.get_vehicle_data(self.bob_vehicle_id)
        self.assertIn("not accessible", str(context.exception).lower())

    def test_get_vehicle_data_firmware_alice(self):
        """Test getting firmware info for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.get_vehicle_data(self.alice_vehicle_id)
        self.assertIn("response", result)
        self.assertIn("firmware_version", result["response"])
        self.assertIsNone(result["error"])

    def test_get_vehicle_data_firmware_bob(self):
        """Test getting firmware info for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.get_vehicle_data(self.bob_vehicle_id)
        self.assertIn("response", result)
        self.assertIn("firmware_version", result["response"])
        self.assertIsNone(result["error"])

    def test_get_vehicle_data_firmware_invalid(self):
        """Test getting firmware info for non-existent vehicle."""
        with self.assertRaises(Exception) as context:
            self.tesla_api.get_vehicle_data(999999999999999)
        self.assertIn("not found", str(context.exception).lower())

    # --- Security Tests ---
    def test_set_sentry_mode_on_alice(self):
        """Test turning sentry mode on for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        result = self.tesla_api.set_sentry_mode(self.alice_vehicle_id, True)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    def test_set_sentry_mode_off_bob(self):
        """Test turning sentry mode off for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        result = self.tesla_api.set_sentry_mode(self.bob_vehicle_id, False)
        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(result["response"]["reason"], "")

    # --- Workflow Tests ---
    def test_vehicle_control_workflow_alice(self):
        """Test comprehensive vehicle control workflow for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        
        # Wake up vehicle
        wake_result = self.tesla_api.wake_up(self.alice_vehicle_id)
        self.assertEqual(wake_result["response"]["result"], True)
        self.assertEqual(wake_result["response"]["reason"], "")

        # Get vehicle info
        info_result = self.tesla_api.get_vehicle_data(self.alice_vehicle_id)
        self.assertIn("response", info_result)

        # Honk horn
        honk_result = self.tesla_api.honk_horn(self.alice_vehicle_id)
        self.assertEqual(honk_result["response"]["result"], True)
        self.assertEqual(honk_result["response"]["reason"], "")

        # Get status
        status_result = self.tesla_api.get_vehicle_data(self.alice_vehicle_id)
        self.assertIn("response", status_result)
        self.assertIsNone(status_result["error"])

    def test_charging_workflow_bob(self):
        """Test charging workflow for Bob."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_BOB.email}")
        
        # Open charge port
        open_result = self.tesla_api.charge_port_door_open(self.bob_vehicle_id)
        self.assertEqual(open_result["response"]["result"], True)
        self.assertEqual(open_result["response"]["reason"], "")

        # Set charge limit
        limit_result = self.tesla_api.set_charge_limit(self.bob_vehicle_id, 90)
        self.assertEqual(limit_result["response"]["result"], True)
        self.assertEqual(limit_result["response"]["reason"], "")

        # Start charging
        start_result = self.tesla_api.charge_start(self.bob_vehicle_id)
        self.assertEqual(start_result["response"]["result"], True)
        self.assertEqual(start_result["response"]["reason"], "")

    def test_climate_control_workflow_alice(self):
        """Test climate control workflow for Alice."""
        self.tesla_api.authenticate(f"token_{self.REAL_USER_ALICE.email}")
        
        # Turn climate on
        on_result = self.tesla_api.auto_conditioning_start(self.alice_vehicle_id)
        self.assertEqual(on_result["response"]["result"], True)
        self.assertEqual(on_result["response"]["reason"], "")

        # Set temperature
        temp_result = self.tesla_api.set_temps(self.alice_vehicle_id, 22.0, 22.0)
        self.assertEqual(temp_result["response"]["result"], True)
        self.assertEqual(temp_result["response"]["reason"], "")

        # Set bioweapon mode
        bio_result = self.tesla_api.set_bioweapon_mode(self.alice_vehicle_id, True)
        self.assertEqual(bio_result["response"]["result"], True)
        self.assertEqual(bio_result["response"]["reason"], "")

    # --- Data Reset Tests ---
    def test_reset_data_success(self):
        """Test resetting data successfully."""
        result = self.tesla_api.reset_data()
        self.assertTrue(result.get("reset_status", False))

if __name__ == "__main__":
    unittest.main()
