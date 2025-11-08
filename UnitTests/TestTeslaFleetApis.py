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
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_honk_horn_bob(self):
        """Test honking horn for Bob."""
        result = self.tesla_api.honk_horn(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_honk_horn_non_existent_vehicle(self):
        """Test honking horn for non-existent vehicle."""
        result = self.tesla_api.honk_horn(user=self.REAL_USER_ALICE, vehicle_tag="non_existent_vehicle")
        self.assertEqual(result["result"], False)
        self.assertIn("not found", result["reason"])

    def test_flash_lights_alice(self):
        """Test flashing lights for Alice."""
        result = self.tesla_api.flash_lights(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_flash_lights_bob(self):
        """Test flashing lights for Bob."""
        result = self.tesla_api.flash_lights(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_flash_lights_non_existent_vehicle(self):
        """Test flashing lights for non-existent vehicle."""
        result = self.tesla_api.flash_lights(user=self.REAL_USER_ALICE, vehicle_tag="non_existent_vehicle")
        self.assertEqual(result["result"], False)
        self.assertIn("not found", result["reason"])

    def test_wake_up_alice(self):
        """Test waking up vehicle for Alice."""
        result = self.tesla_api.wake_up(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_wake_up_bob(self):
        """Test waking up vehicle for Bob."""
        result = self.tesla_api.wake_up(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_wake_vehicle_alice(self):
        """Test wake_vehicle method for Alice."""
        result = self.tesla_api.wake_vehicle(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_wake_vehicle_bob(self):
        """Test wake_vehicle method for Bob."""
        result = self.tesla_api.wake_vehicle(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    # --- Media Control Tests ---
    def test_media_toggle_playback_alice(self):
        """Test media toggle playback for Alice."""
        result = self.tesla_api.media_toggle_playback(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_media_toggle_playback_bob(self):
        """Test media toggle playback for Bob."""
        result = self.tesla_api.media_toggle_playback(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_adjust_volume_alice(self):
        """Test adjusting volume for Alice."""
        result = self.tesla_api.adjust_volume(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, volume=50)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_adjust_volume_bob_max(self):
        """Test adjusting volume to max for Bob."""
        result = self.tesla_api.adjust_volume(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, volume=100)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_adjust_volume_invalid_level(self):
        """Test adjusting to invalid volume level."""
        result = self.tesla_api.adjust_volume(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, volume=150)
        self.assertEqual(result["result"], False)
        self.assertIn("Volume level must be between 0 and 100", result["reason"])

    def test_media_next_track_alice(self):
        """Test skipping to next track for Alice."""
        result = self.tesla_api.media_next_track(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_media_prev_track_bob(self):
        """Test skipping to previous track for Bob."""
        result = self.tesla_api.media_prev_track(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    # --- Trunk Control Tests ---
    def test_actuate_trunk_front_alice(self):
        """Test opening front trunk for Alice."""
        result = self.tesla_api.actuate_trunk(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, which_trunk="front")
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_actuate_trunk_rear_bob(self):
        """Test opening rear trunk for Bob."""
        result = self.tesla_api.actuate_trunk(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, which_trunk="rear")
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    # --- Charging Tests ---
    def test_set_charge_limit_alice(self):
        """Test setting charge limit for Alice."""
        result = self.tesla_api.set_charge_limit(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, limit=80)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_set_charge_limit_bob_max(self):
        """Test setting charge limit to max for Bob."""
        result = self.tesla_api.set_charge_limit(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, limit=100)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_set_charge_limit_invalid(self):
        """Test setting invalid charge limit."""
        result = self.tesla_api.set_charge_limit(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, limit=150)
        self.assertEqual(result["result"], False)
        self.assertIn("Charge limit must be between 0 and 100", result["reason"])

    def test_charge_port_door_open_alice(self):
        """Test opening charge port for Alice."""
        result = self.tesla_api.charge_port_door_open(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_charge_port_door_close_bob(self):
        """Test closing charge port for Bob."""
        result = self.tesla_api.charge_port_door_close(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_charge_start_alice(self):
        """Test starting charge for Alice."""
        result = self.tesla_api.charge_start(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_charge_stop_bob(self):
        """Test stopping charge for Bob."""
        result = self.tesla_api.charge_stop(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    # --- Climate Control Tests ---
    def test_auto_conditioning_start_alice(self):
        """Test starting climate control for Alice."""
        result = self.tesla_api.auto_conditioning_start(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_auto_conditioning_stop_bob(self):
        """Test stopping climate control for Bob."""
        result = self.tesla_api.auto_conditioning_stop(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_set_temps_alice(self):
        """Test setting climate temperatures for Alice."""
        result = self.tesla_api.set_temps(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, driver_temp=22.0, passenger_temp=20.0)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_set_temps_bob(self):
        """Test setting climate temperatures for Bob."""
        result = self.tesla_api.set_temps(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, driver_temp=20.0, passenger_temp=20.0)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_set_temps_invalid(self):
        """Test setting invalid climate temperature."""
        result = self.tesla_api.set_temps(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, driver_temp=50.0, passenger_temp=20.0)
        self.assertEqual(result["result"], False)
        self.assertIn("Temperatures must be between 15 and 30", result["reason"])

    def test_set_bioweapon_mode_on_alice(self):
        """Test turning bioweapon mode on for Alice."""
        result = self.tesla_api.set_bioweapon_mode(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, on=True)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_set_bioweapon_mode_off_bob(self):
        """Test turning bioweapon mode off for Bob."""
        result = self.tesla_api.set_bioweapon_mode(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, on=False)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_set_climate_keeper_mode_dog_alice(self):
        """Test setting climate keeper mode to dog for Alice."""
        result = self.tesla_api.set_climate_keeper_mode(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, climate_keeper_mode=1)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_set_climate_keeper_mode_camp_bob(self):
        """Test setting climate keeper mode to camp for Bob."""
        result = self.tesla_api.set_climate_keeper_mode(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, climate_keeper_mode=2)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_set_climate_keeper_mode_off(self):
        """Test turning climate keeper mode off."""
        result = self.tesla_api.set_climate_keeper_mode(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, climate_keeper_mode=0)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    # --- Window Control Tests ---
    def test_window_control_vent_alice(self):
        """Test venting windows for Alice."""
        result = self.tesla_api.window_control(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, command="vent")
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_window_control_close_bob(self):
        """Test closing windows for Bob."""
        result = self.tesla_api.window_control(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, command="close")
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    # --- Vehicle Status Tests ---
    def test_get_vehicle_location_alice(self):
        """Test getting vehicle location for Alice."""
        result = self.tesla_api.get_vehicle_location(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")
        self.assertIn("location", result)

    def test_get_vehicle_location_bob(self):
        """Test getting vehicle location for Bob."""
        result = self.tesla_api.get_vehicle_location(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")
        self.assertIn("location", result)

    def test_get_vehicle_location_non_existent(self):
        """Test getting location for non-existent vehicle."""
        result = self.tesla_api.get_vehicle_location(user=self.REAL_USER_ALICE, vehicle_tag="non_existent_vehicle")
        self.assertEqual(result["result"], False)
        self.assertIn("not found", result["reason"])

    def test_get_vehicle_status_alice(self):
        """Test getting vehicle status for Alice."""
        result = self.tesla_api.get_vehicle_status(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")
        self.assertIn("vehicle_info", result)
        self.assertIn("charge", result)
        self.assertIn("climate", result)

    def test_get_vehicle_status_bob(self):
        """Test getting vehicle status for Bob."""
        result = self.tesla_api.get_vehicle_status(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")
        self.assertIn("vehicle_info", result)

    def test_get_vehicle_status_non_existent(self):
        """Test getting status for non-existent vehicle."""
        result = self.tesla_api.get_vehicle_status(user=self.REAL_USER_ALICE, vehicle_tag="non_existent_vehicle")
        self.assertEqual(result["result"], False)
        self.assertIn("not found", result["reason"])

    def test_get_firmware_info_alice(self):
        """Test getting firmware info for Alice."""
        result = self.tesla_api.get_firmware_info(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")
        self.assertIn("firmware", result)

    def test_get_firmware_info_bob(self):
        """Test getting firmware info for Bob."""
        result = self.tesla_api.get_firmware_info(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")
        self.assertIn("firmware", result)

    def test_get_firmware_info_non_existent(self):
        """Test getting firmware info for non-existent vehicle."""
        result = self.tesla_api.get_firmware_info(user=self.REAL_USER_ALICE, vehicle_tag="non_existent_vehicle")
        self.assertEqual(result["result"], False)
        self.assertIn("not found", result["reason"])

    # --- Security Tests ---
    def test_set_sentry_mode_on_alice(self):
        """Test turning sentry mode on for Alice."""
        result = self.tesla_api.set_sentry_mode(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, on=True)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    def test_set_sentry_mode_off_bob(self):
        """Test turning sentry mode off for Bob."""
        result = self.tesla_api.set_sentry_mode(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, on=False)
        self.assertEqual(result["result"], True)
        self.assertEqual(result["reason"], "")

    # --- Workflow Tests ---
    def test_vehicle_control_workflow_alice(self):
        """Test comprehensive vehicle control workflow for Alice."""
        # Wake up vehicle
        wake_result = self.tesla_api.wake_up(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(wake_result["result"], True)
        self.assertEqual(wake_result["reason"], "")

        # Get vehicle info
        info_result = self.tesla_api.show_vehicle_info(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertIn("vehicle_info", info_result)

        # Honk horn
        honk_result = self.tesla_api.honk_horn(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(honk_result["result"], True)
        self.assertEqual(honk_result["reason"], "")

        # Get status
        status_result = self.tesla_api.get_vehicle_status(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(status_result["result"], True)
        self.assertEqual(status_result["reason"], "")
        self.assertIn("vehicle_info", status_result)

    def test_charging_workflow_bob(self):
        """Test charging workflow for Bob."""
        # Open charge port
        open_result = self.tesla_api.charge_port_door_open(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(open_result["result"], True)
        self.assertEqual(open_result["reason"], "")

        # Set charge limit
        limit_result = self.tesla_api.set_charge_limit(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB, limit=90)
        self.assertEqual(limit_result["result"], True)
        self.assertEqual(limit_result["reason"], "")

        # Start charging
        start_result = self.tesla_api.charge_start(user=self.REAL_USER_BOB, vehicle_tag=self.REAL_VEHICLE_TAG_BOB)
        self.assertEqual(start_result["result"], True)
        self.assertEqual(start_result["reason"], "")

    def test_climate_control_workflow_alice(self):
        """Test climate control workflow for Alice."""
        # Turn climate on
        on_result = self.tesla_api.auto_conditioning_start(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE)
        self.assertEqual(on_result["result"], True)
        self.assertEqual(on_result["reason"], "")

        # Set temperature
        temp_result = self.tesla_api.set_temps(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, driver_temp=22.0, passenger_temp=22.0)
        self.assertEqual(temp_result["result"], True)
        self.assertEqual(temp_result["reason"], "")

        # Set bioweapon mode
        bio_result = self.tesla_api.set_bioweapon_mode(user=self.REAL_USER_ALICE, vehicle_tag=self.REAL_VEHICLE_TAG_ALICE, on=True)
        self.assertEqual(bio_result["result"], True)
        self.assertEqual(bio_result["reason"], "")

    # --- Data Reset Tests ---
    def test_reset_data_success(self):
        """Test resetting data successfully."""
        result = self.tesla_api.reset_data()
        self.assertTrue(result.get("reset_status", False))

if __name__ == "__main__":
    unittest.main()
