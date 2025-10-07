import unittest
import sys
import os
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

    # --- User Management Tests ---
    def test_set_current_user_alice(self):
        """Test setting current user to Alice."""
        result = self.tesla_api.set_current_user(user_email=self.REAL_USER_ALICE.email)
        self.assertTrue(result.get("status", False))
        self.assertIn("message", result)

    def test_set_current_user_bob(self):
        """Test setting current user to Bob."""
        result = self.tesla_api.set_current_user(user_email=self.REAL_USER_BOB.email)
        self.assertTrue(result.get("status", False))
        self.assertIn("message", result)

    def test_set_current_user_non_existent(self):
        """Test setting current user to non-existent email."""
        result = self.tesla_api.set_current_user(user_email="nonexistent@example.com")
        self.assertFalse(result.get("status", True))
        self.assertIn("message", result)

    # --- Vehicle Info Tests ---
    def test_show_vehicle_info_alice(self):
        """Test showing vehicle info for Alice."""
        result = self.tesla_api.show_vehicle_info(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertIn("vehicle_info", result)
        self.assertIsInstance(result["vehicle_info"], dict)

    def test_show_vehicle_info_bob(self):
        """Test showing vehicle info for Bob."""
        result = self.tesla_api.show_vehicle_info(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertIn("vehicle_info", result)
        self.assertIsInstance(result["vehicle_info"], dict)

    def test_show_vehicle_info_non_existent_vehicle(self):
        """Test showing info for non-existent vehicle."""
        result = self.tesla_api.show_vehicle_info(user=self.REAL_USER_ALICE, vehicle_tag="non_existent_vehicle")
        self.assertIn("error", result)
        self.assertIsInstance(result["error"], str)

    # --- Vehicle Action Tests ---
    def test_honk_horn_alice(self):
        """Test honking horn for Alice."""
        result = self.tesla_api.honk_horn(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertTrue(result.get("success", False))

    def test_honk_horn_bob(self):
        """Test honking horn for Bob."""
        result = self.tesla_api.honk_horn(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertTrue(result.get("success", False))

    def test_honk_horn_non_existent_vehicle(self):
        """Test honking horn for non-existent vehicle."""
        result = self.tesla_api.honk_horn(user=self.REAL_USER_ALICE, vehicle_tag="non_existent_vehicle")
        self.assertFalse(result.get("success", True))
        self.assertIn("message", result)

    def test_flash_lights_alice(self):
        """Test flashing lights for Alice."""
        result = self.tesla_api.flash_lights(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertTrue(result.get("success", False))

    def test_flash_lights_bob(self):
        """Test flashing lights for Bob."""
        result = self.tesla_api.flash_lights(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertTrue(result.get("success", False))

    def test_flash_lights_non_existent_vehicle(self):
        """Test flashing lights for non-existent vehicle."""
        result = self.tesla_api.flash_lights(user=self.REAL_USER_ALICE, vehicle_tag="non_existent_vehicle")
        self.assertFalse(result.get("success", True))
        self.assertIn("message", result)

    def test_wake_up_alice(self):
        """Test waking up vehicle for Alice."""
        result = self.tesla_api.wake_up(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertTrue(result.get("success", False))

    def test_wake_up_bob(self):
        """Test waking up vehicle for Bob."""
        result = self.tesla_api.wake_up(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertTrue(result.get("success", False))

    def test_wake_vehicle_alice(self):
        """Test wake_vehicle method for Alice."""
        result = self.tesla_api.wake_vehicle(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertTrue(result.get("success", False))
        self.assertTrue(result.get("awake", False))

    def test_wake_vehicle_bob(self):
        """Test wake_vehicle method for Bob."""
        result = self.tesla_api.wake_vehicle(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertTrue(result.get("success", False))
        self.assertTrue(result.get("awake", False))

    # --- Media Control Tests ---
    def test_start_stop_media_start_alice(self):
        """Test starting media for Alice."""
        result = self.tesla_api.start_stop_media(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, command="start")
        self.assertTrue(result.get("success", False))

    def test_start_stop_media_stop_bob(self):
        """Test stopping media for Bob."""
        result = self.tesla_api.start_stop_media(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, command="stop")
        self.assertTrue(result.get("success", False))

    def test_set_volume_alice(self):
        """Test setting volume for Alice."""
        result = self.tesla_api.set_volume(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, volume_level=50)
        self.assertTrue(result.get("success", False))

    def test_set_volume_bob_max(self):
        """Test setting volume to max for Bob."""
        result = self.tesla_api.set_volume(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, volume_level=100)
        self.assertTrue(result.get("success", False))

    def test_set_volume_invalid_level(self):
        """Test setting invalid volume level."""
        result = self.tesla_api.set_volume(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, volume_level=150)
        self.assertFalse(result.get("success", True))
        self.assertIn("message", result)

    def test_skip_media_track_next_alice(self):
        """Test skipping to next track for Alice."""
        result = self.tesla_api.skip_media_track(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, direction="next")
        self.assertTrue(result.get("success", False))

    def test_skip_media_track_previous_bob(self):
        """Test skipping to previous track for Bob."""
        result = self.tesla_api.skip_media_track(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, direction="previous")
        self.assertTrue(result.get("success", False))

    # --- Trunk Control Tests ---
    def test_open_close_trunk_front_open_alice(self):
        """Test opening front trunk for Alice."""
        result = self.tesla_api.open_close_trunk(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, trunk_part="front", command="open")
        self.assertTrue(result.get("success", False))

    def test_open_close_trunk_rear_close_bob(self):
        """Test closing rear trunk for Bob."""
        result = self.tesla_api.open_close_trunk(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, trunk_part="rear", command="close")
        self.assertTrue(result.get("success", False))

    # --- Charging Tests ---
    def test_set_charge_limit_alice(self):
        """Test setting charge limit for Alice."""
        result = self.tesla_api.set_charge_limit(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, limit=80)
        self.assertTrue(result.get("success", False))

    def test_set_charge_limit_bob_max(self):
        """Test setting charge limit to max for Bob."""
        result = self.tesla_api.set_charge_limit(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, limit=100)
        self.assertTrue(result.get("success", False))

    def test_set_charge_limit_invalid(self):
        """Test setting invalid charge limit."""
        result = self.tesla_api.set_charge_limit(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, limit=150)
        self.assertFalse(result.get("success", True))
        self.assertIn("message", result)

    def test_open_close_charge_port_open_alice(self):
        """Test opening charge port for Alice."""
        result = self.tesla_api.open_close_charge_port(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, command="open")
        self.assertTrue(result.get("success", False))

    def test_open_close_charge_port_close_bob(self):
        """Test closing charge port for Bob."""
        result = self.tesla_api.open_close_charge_port(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, command="close")
        self.assertTrue(result.get("success", False))

    def test_start_stop_charge_start_alice(self):
        """Test starting charge for Alice."""
        result = self.tesla_api.start_stop_charge(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, command="start")
        self.assertTrue(result.get("success", False))

    def test_start_stop_charge_stop_bob(self):
        """Test stopping charge for Bob."""
        result = self.tesla_api.start_stop_charge(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, command="stop")
        self.assertTrue(result.get("success", False))

    # --- Climate Control Tests ---
    def test_start_stop_climate_on_alice(self):
        """Test turning climate on for Alice."""
        result = self.tesla_api.start_stop_climate(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, command="on")
        self.assertTrue(result.get("success", False))

    def test_start_stop_climate_off_bob(self):
        """Test turning climate off for Bob."""
        result = self.tesla_api.start_stop_climate(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, command="off")
        self.assertTrue(result.get("success", False))

    def test_set_climate_temp_alice(self):
        """Test setting climate temperature for Alice."""
        result = self.tesla_api.set_climate_temp(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, driver_temp=22, cop_temp=20)
        self.assertTrue(result.get("success", False))

    def test_set_climate_temp_bob(self):
        """Test setting climate temperature for Bob."""
        result = self.tesla_api.set_climate_temp(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, driver_temp=20, cop_temp=20)
        self.assertTrue(result.get("success", False))

    def test_set_climate_temp_invalid(self):
        """Test setting invalid climate temperature."""
        result = self.tesla_api.set_climate_temp(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, driver_temp=50, cop_temp=20)
        self.assertFalse(result.get("success", True))
        self.assertIn("message", result)

    def test_set_bioweapon_mode_on_alice(self):
        """Test turning bioweapon mode on for Alice."""
        result = self.tesla_api.set_bioweapon_mode(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, command="on")
        self.assertTrue(result.get("success", False))

    def test_set_bioweapon_mode_off_bob(self):
        """Test turning bioweapon mode off for Bob."""
        result = self.tesla_api.set_bioweapon_mode(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, command="off")
        self.assertTrue(result.get("success", False))

    def test_set_climate_keeper_mode_dog_alice(self):
        """Test setting climate keeper mode to dog for Alice."""
        result = self.tesla_api.set_climate_keeper_mode(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, mode="dog")
        self.assertTrue(result.get("success", False))

    def test_set_climate_keeper_mode_camp_bob(self):
        """Test setting climate keeper mode to camp for Bob."""
        result = self.tesla_api.set_climate_keeper_mode(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, mode="camp")
        self.assertTrue(result.get("success", False))

    def test_set_climate_keeper_mode_off(self):
        """Test turning climate keeper mode off."""
        result = self.tesla_api.set_climate_keeper_mode(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, mode="off")
        self.assertTrue(result.get("success", False))

    # --- Window Control Tests ---
    def test_window_control_vent_alice(self):
        """Test venting windows for Alice."""
        result = self.tesla_api.window_control(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, command="vent", lat=37.7749, lon=-122.4194)
        self.assertTrue(result.get("success", False))

    def test_window_control_close_bob(self):
        """Test closing windows for Bob."""
        result = self.tesla_api.window_control(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, command="close", lat=40.7128, lon=-74.0060)
        self.assertTrue(result.get("success", False))

    # --- Vehicle Status Tests ---
    def test_get_vehicle_location_alice(self):
        """Test getting vehicle location for Alice."""
        result = self.tesla_api.get_vehicle_location(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertTrue(result.get("success", False))
        self.assertIn("location", result)

    def test_get_vehicle_location_bob(self):
        """Test getting vehicle location for Bob."""
        result = self.tesla_api.get_vehicle_location(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertTrue(result.get("success", False))
        self.assertIn("location", result)

    def test_get_vehicle_location_non_existent(self):
        """Test getting location for non-existent vehicle."""
        result = self.tesla_api.get_vehicle_location(user=self.REAL_USER_ALICE, vehicle_tag="non_existent_vehicle")
        self.assertFalse(result.get("success", True))
        self.assertIn("message", result)

    def test_get_vehicle_status_alice(self):
        """Test getting vehicle status for Alice."""
        result = self.tesla_api.get_vehicle_status(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertTrue(result.get("success", False))
        self.assertIn("vehicle_info", result)
        self.assertIn("charge", result)
        self.assertIn("climate", result)

    def test_get_vehicle_status_bob(self):
        """Test getting vehicle status for Bob."""
        result = self.tesla_api.get_vehicle_status(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertTrue(result.get("success", False))
        self.assertIn("vehicle_info", result)

    def test_get_vehicle_status_non_existent(self):
        """Test getting status for non-existent vehicle."""
        result = self.tesla_api.get_vehicle_status(user=self.REAL_USER_ALICE, vehicle_tag="non_existent_vehicle")
        self.assertFalse(result.get("success", True))
        self.assertIn("message", result)

    def test_get_firmware_info_alice(self):
        """Test getting firmware info for Alice."""
        result = self.tesla_api.get_firmware_info(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertTrue(result.get("success", False))
        self.assertIn("firmware", result)

    def test_get_firmware_info_bob(self):
        """Test getting firmware info for Bob."""
        result = self.tesla_api.get_firmware_info(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertTrue(result.get("success", False))
        self.assertIn("firmware", result)

    def test_get_firmware_info_non_existent(self):
        """Test getting firmware info for non-existent vehicle."""
        result = self.tesla_api.get_firmware_info(user=self.REAL_USER_ALICE, vehicle_tag="non_existent_vehicle")
        self.assertFalse(result.get("success", True))
        self.assertIn("message", result)

    # --- Security Tests ---
    def test_manage_sentry_mode_on_alice(self):
        """Test turning sentry mode on for Alice."""
        result = self.tesla_api.manage_sentry_mode(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, command="on")
        self.assertTrue(result.get("success", False))
        self.assertIn("sentry_mode", result)

    def test_manage_sentry_mode_off_bob(self):
        """Test turning sentry mode off for Bob."""
        result = self.tesla_api.manage_sentry_mode(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, command="off")
        self.assertTrue(result.get("success", False))
        self.assertIn("sentry_mode", result)

    # --- Workflow Tests ---
    def test_vehicle_control_workflow_alice(self):
        """Test comprehensive vehicle control workflow for Alice."""
        # Wake up vehicle
        wake_result = self.tesla_api.wake_up(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertTrue(wake_result.get("success", False))

        # Get vehicle info
        info_result = self.tesla_api.show_vehicle_info(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertIn("vehicle_info", info_result)

        # Honk horn
        honk_result = self.tesla_api.honk_horn(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertTrue(honk_result.get("success", False))

        # Get status
        status_result = self.tesla_api.get_vehicle_status(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertTrue(status_result.get("success", False))

    def test_charging_workflow_bob(self):
        """Test charging workflow for Bob."""
        # Open charge port
        open_result = self.tesla_api.open_close_charge_port(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, command="open")
        self.assertTrue(open_result.get("success", False))

        # Set charge limit
        limit_result = self.tesla_api.set_charge_limit(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, limit=90)
        self.assertTrue(limit_result.get("success", False))

        # Start charging
        start_result = self.tesla_api.start_stop_charge(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, command="start")
        self.assertTrue(start_result.get("success", False))

    def test_climate_control_workflow_alice(self):
        """Test climate control workflow for Alice."""
        # Turn climate on
        on_result = self.tesla_api.start_stop_climate(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, command="on")
        self.assertTrue(on_result.get("success", False))

        # Set temperature
        temp_result = self.tesla_api.set_climate_temp(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, driver_temp=22, cop_temp=22)
        self.assertTrue(temp_result.get("success", False))

        # Set bioweapon mode
        bio_result = self.tesla_api.set_bioweapon_mode(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, command="on")
        self.assertTrue(bio_result.get("success", False))

    # --- Data Reset Tests ---
    def test_reset_data_success(self):
        """Test resetting data successfully."""
        result = self.tesla_api.reset_data()
        self.assertTrue(result.get("reset_status", False))

if __name__ == "__main__":
    unittest.main()
