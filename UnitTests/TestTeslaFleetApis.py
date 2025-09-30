import unittest
from copy import deepcopy
from audio_gorilla.TeslaFleetApis import TeslaFleetApis, DEFAULT_STATE, User

class TestTeslaFleetApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh TeslaFleetApis instance for each test."""
        self.tesla_api = TeslaFleetApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.tesla_api._load_scenario(deepcopy(DEFAULT_STATE))
        # Create test users and vehicle tags
        self.user1 = User(email="user1@example.com")
        self.user2 = User(email="user2@example.com")
        self.model_3_tag = "my_tesla_model_3"
        self.model_s_tag = "my_tesla_model_s"

    # --- Unit Tests for Core Functions (most important for audio calling) ---

    def test_honk_horn_success(self):
        """Test honking the horn of a vehicle."""
        result = self.tesla_api.honk_horn(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertTrue(self.tesla_api.vehicles[self.model_3_tag]["horn"])

    def test_media_toggle_playback_success(self):
        """Test toggling media playback."""
        initial_playing_status = self.tesla_api.vehicles[self.model_3_tag]["media"]["playing"]
        result = self.tesla_api.media_toggle_playback(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["media"]["playing"], not initial_playing_status)

    def test_media_volume_down_success(self):
        """Test decreasing media volume."""
        initial_volume = self.tesla_api.vehicles[self.model_3_tag]["media"]["volume"]
        result = self.tesla_api.media_volume_down(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["media"]["volume"], max(0, initial_volume - 5))

    def test_media_next_fav_success(self):
        """Test skipping to the next favorite media item."""
        # Ensure model_3 has favorites for this test
        self.tesla_api.vehicles[self.model_3_tag]["media"]["favorites"] = ["Fav1", "Fav2", "Fav3"]
        self.tesla_api.vehicles[self.model_3_tag]["media"]["current_track"] = 0 # Start at first favorite

        result = self.tesla_api.media_next_fav(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["media"]["current_track"], 1)

        result = self.tesla_api.media_next_fav(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["media"]["current_track"], 2)

        result = self.tesla_api.media_next_fav(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["media"]["current_track"], 0) # Wraps around

    def test_actuate_trunk_front_success(self):
        """Test actuating the front trunk."""
        initial_trunk_state = self.tesla_api.vehicles[self.model_3_tag]["trunk"]["front"]
        result = self.tesla_api.actuate_trunk(self.model_3_tag, "front")
        self.assertTrue(result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["trunk"]["front"], "open" if initial_trunk_state == "closed" else "closed")

    def test_charge_start_success(self):
        """Test starting vehicle charging."""
        self.tesla_api.vehicles[self.model_3_tag]["charge"]["charging"] = False # Ensure it's off
        result = self.tesla_api.charge_start(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertTrue(self.tesla_api.vehicles[self.model_3_tag]["charge"]["charging"])

    def test_charge_stop_success(self):
        """Test stopping vehicle charging."""
        self.tesla_api.vehicles[self.model_3_tag]["charge"]["charging"] = True # Ensure it's on
        result = self.tesla_api.charge_stop(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertFalse(self.tesla_api.vehicles[self.model_3_tag]["charge"]["charging"])

    def test_set_charge_limit_success(self):
        """Test setting the charge limit."""
        result = self.tesla_api.set_charge_limit(self.model_3_tag, 90)
        self.assertTrue(result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["charge"]["limit"], 90)

    def test_auto_conditioning_start_success(self):
        """Test starting auto conditioning."""
        self.tesla_api.vehicles[self.model_3_tag]["climate"]["on"] = False
        result = self.tesla_api.auto_conditioning_start(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertTrue(self.tesla_api.vehicles[self.model_3_tag]["climate"]["on"])

    def test_auto_conditioning_stop_success(self):
        """Test stopping auto conditioning."""
        self.tesla_api.vehicles[self.model_3_tag]["climate"]["on"] = True
        result = self.tesla_api.auto_conditioning_stop(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertFalse(self.tesla_api.vehicles[self.model_3_tag]["climate"]["on"])

    def test_set_temps_success(self):
        """Test setting driver and passenger temperatures."""
        result = self.tesla_api.set_temps(self.model_3_tag, 20.5, 21.0)
        self.assertTrue(result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["climate"]["driver_temp"], 20.5)
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["climate"]["passenger_temp"], 21.0)

    def test_door_lock_success(self):
        """Test locking doors."""
        self.tesla_api.vehicles[self.model_3_tag]["doors"]["locked"] = False
        result = self.tesla_api.door_lock(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertTrue(self.tesla_api.vehicles[self.model_3_tag]["doors"]["locked"])

    def test_door_unlock_success(self):
        """Test unlocking doors."""
        self.tesla_api.vehicles[self.model_3_tag]["doors"]["locked"] = True
        result = self.tesla_api.door_unlock(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertFalse(self.tesla_api.vehicles[self.model_3_tag]["doors"]["locked"])

    def test_set_sentry_mode_on(self):
        """Test enabling sentry mode."""
        self.tesla_api.vehicles[self.model_3_tag]["sentry_mode"] = False
        result = self.tesla_api.set_sentry_mode(self.model_3_tag, True)
        self.assertTrue(result["success"])
        self.assertTrue(self.tesla_api.vehicles[self.model_3_tag]["sentry_mode"])

    def test_set_sentry_mode_off(self):
        """Test disabling sentry mode."""
        self.tesla_api.vehicles[self.model_3_tag]["sentry_mode"] = True
        result = self.tesla_api.set_sentry_mode(self.model_3_tag, False)
        self.assertTrue(result["success"])
        self.assertFalse(self.tesla_api.vehicles[self.model_3_tag]["sentry_mode"])

    def test_sun_roof_control_open(self):
        """Test opening the sunroof."""
        result = self.tesla_api.sun_roof_control(self.model_3_tag, "open")
        self.assertTrue(result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["sunroof"], "open")

    def test_window_control_vent(self):
        """Test venting windows."""
        result = self.tesla_api.window_control(self.model_3_tag, "vent", 28.5, -81.0)
        self.assertTrue(result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["windows"], "vent")

    def test_wake_up_success(self):
        """Test waking up a vehicle."""
        self.tesla_api.vehicles[self.model_3_tag]["awake"] = False
        result = self.tesla_api.wake_up(self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertTrue(self.tesla_api.vehicles[self.model_3_tag]["awake"])

    # --- Combined Functionality Tests ---

    def test_climate_control_flow(self):
        """
        Scenario: Start auto conditioning, set temps, and enable bioweapon mode.
        Functions: auto_conditioning_start, set_temps, set_bioweapon_mode
        """
        # 1. Start auto conditioning
        start_climate_result = self.tesla_api.auto_conditioning_start(self.model_3_tag)
        self.assertTrue(start_climate_result["success"])
        self.assertTrue(self.tesla_api.vehicles[self.model_3_tag]["climate"]["on"])

        # 2. Set temperatures
        set_temps_result = self.tesla_api.set_temps(self.model_3_tag, 20.0, 20.0)
        self.assertTrue(set_temps_result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["climate"]["driver_temp"], 20.0)
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["climate"]["passenger_temp"], 20.0)

        # 3. Enable bioweapon mode
        set_bioweapon_result = self.tesla_api.set_bioweapon_mode(self.model_3_tag, True)
        self.assertTrue(set_bioweapon_result["success"])
        self.assertTrue(self.tesla_api.vehicles[self.model_3_tag]["climate"]["bioweapon_mode"])

    def test_charge_management_flow(self):
        """
        Scenario: Set charge limit, start charging, then stop charging.
        Functions: set_charge_limit, charge_start, charge_stop
        """
        # 1. Set charge limit
        set_limit_result = self.tesla_api.set_charge_limit(self.model_3_tag, 85)
        self.assertTrue(set_limit_result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["charge"]["limit"], 85)

        # 2. Start charging
        start_charge_result = self.tesla_api.charge_start(self.model_3_tag)
        self.assertTrue(start_charge_result["success"])
        self.assertTrue(self.tesla_api.vehicles[self.model_3_tag]["charge"]["charging"])

        # 3. Stop charging
        stop_charge_result = self.tesla_api.charge_stop(self.model_3_tag)
        self.assertTrue(stop_charge_result["success"])
        self.assertFalse(self.tesla_api.vehicles[self.model_3_tag]["charge"]["charging"])

    def test_door_and_sentry_mode_flow(self):
        """
        Scenario: Unlock doors, then enable sentry mode.
        Functions: door_unlock, set_sentry_mode
        """
        # Ensure doors are locked initially
        self.tesla_api.vehicles[self.model_3_tag]["doors"]["locked"] = True
        self.tesla_api.vehicles[self.model_3_tag]["sentry_mode"] = False

        # 1. Unlock doors
        unlock_result = self.tesla_api.door_unlock(self.model_3_tag)
        self.assertTrue(unlock_result["success"])
        self.assertFalse(self.tesla_api.vehicles[self.model_3_tag]["doors"]["locked"])

        # 2. Enable sentry mode
        sentry_result = self.tesla_api.set_sentry_mode(self.model_3_tag, True)
        self.assertTrue(sentry_result["success"])
        self.assertTrue(self.tesla_api.vehicles[self.model_3_tag]["sentry_mode"])

    def test_media_control_flow(self):
        """
        Scenario: Toggle playback, decrease volume, then skip to next favorite.
        Functions: media_toggle_playback, media_volume_down, media_next_fav
        """
        # Ensure media is off and has favorites
        self.tesla_api.vehicles[self.model_3_tag]["media"]["playing"] = False
        self.tesla_api.vehicles[self.model_3_tag]["media"]["volume"] = 60
        self.tesla_api.vehicles[self.model_3_tag]["media"]["favorites"] = ["Fav1", "Fav2", "Fav3"]
        self.tesla_api.vehicles[self.model_3_tag]["media"]["current_track"] = 0

        # 1. Toggle playback (to ON)
        toggle_result = self.tesla_api.media_toggle_playback(self.model_3_tag)
        self.assertTrue(toggle_result["success"])
        self.assertTrue(self.tesla_api.vehicles[self.model_3_tag]["media"]["playing"])

        # 2. Decrease volume
        volume_down_result = self.tesla_api.media_volume_down(self.model_3_tag)
        self.assertTrue(volume_down_result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["media"]["volume"], 55)

        # 3. Skip to next favorite
        next_fav_result = self.tesla_api.media_next_fav(self.model_3_tag)
        self.assertTrue(next_fav_result["success"])
        self.assertEqual(self.tesla_api.vehicles[self.model_3_tag]["media"]["current_track"], 1)

    # --- Comprehensive Test Coverage for All TeslaFleetApis Methods ---

    def test_set_current_user_success(self):
        """Test setting current user with valid email."""
        result = self.tesla_api.set_current_user("user1@example.com")
        self.assertTrue(result["success"])

    def test_set_current_user_invalid_email(self):
        """Test setting current user with invalid email."""
        result = self.tesla_api.set_current_user("nonexistent@example.com")
        self.assertFalse(result["success"])

    def test_show_vehicle_info_success(self):
        """Test showing vehicle information for valid user and vehicle."""
        result = self.tesla_api.show_vehicle_info(self.user1, self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertIn("vehicle_info", result)
        self.assertIn("vehicle_tag", result["vehicle_info"])

    def test_show_vehicle_info_invalid_vehicle(self):
        """Test showing vehicle info for non-existent vehicle."""
        result = self.tesla_api.show_vehicle_info(self.user1, "nonexistent_vehicle")
        self.assertFalse(result["success"])

    def test_honk_horn_success(self):
        """Test honking horn with valid user and vehicle."""
        result = self.tesla_api.honk_horn(self.user1, self.model_3_tag)
        self.assertTrue(result["success"])

    def test_honk_horn_invalid_vehicle(self):
        """Test honking horn with invalid vehicle."""
        result = self.tesla_api.honk_horn(self.user1, "invalid_vehicle")
        self.assertFalse(result["success"])

    def test_flash_lights_success(self):
        """Test flashing lights with valid user and vehicle."""
        result = self.tesla_api.flash_lights(self.user1, self.model_3_tag)
        self.assertTrue(result["success"])

    def test_flash_lights_invalid_vehicle(self):
        """Test flashing lights with invalid vehicle."""
        result = self.tesla_api.flash_lights(self.user1, "invalid_vehicle")
        self.assertFalse(result["success"])

    def test_start_stop_media_start(self):
        """Test starting media playback."""
        result = self.tesla_api.start_stop_media(self.user1, self.model_3_tag, "start")
        self.assertTrue(result["success"])

    def test_start_stop_media_stop(self):
        """Test stopping media playback."""
        result = self.tesla_api.start_stop_media(self.user1, self.model_3_tag, "stop")
        self.assertTrue(result["success"])

    def test_start_stop_media_invalid_command(self):
        """Test media control with invalid command."""
        result = self.tesla_api.start_stop_media(self.user1, self.model_3_tag, "invalid")
        self.assertFalse(result["success"])

    def test_set_volume_success(self):
        """Test setting volume to valid level."""
        result = self.tesla_api.set_volume(self.user1, self.model_3_tag, 50)
        self.assertTrue(result["success"])

    def test_set_volume_invalid_range(self):
        """Test setting volume to invalid level."""
        result = self.tesla_api.set_volume(self.user1, self.model_3_tag, 150)  # Over 100
        self.assertFalse(result["success"])
        
        result = self.tesla_api.set_volume(self.user1, self.model_3_tag, -10)  # Below 0
        self.assertFalse(result["success"])

    def test_skip_media_track_next(self):
        """Test skipping to next track."""
        result = self.tesla_api.skip_media_track(self.user1, self.model_3_tag, "next")
        self.assertTrue(result["success"])

    def test_skip_media_track_previous(self):
        """Test skipping to previous track."""
        result = self.tesla_api.skip_media_track(self.user1, self.model_3_tag, "previous")
        self.assertTrue(result["success"])

    def test_skip_media_track_invalid_direction(self):
        """Test skipping with invalid direction."""
        result = self.tesla_api.skip_media_track(self.user1, self.model_3_tag, "invalid")
        self.assertFalse(result["success"])

    def test_open_close_trunk_front_open(self):
        """Test opening front trunk."""
        result = self.tesla_api.open_close_trunk(self.user1, self.model_3_tag, "front", "open")
        self.assertTrue(result["success"])

    def test_open_close_trunk_rear_close(self):
        """Test closing rear trunk."""
        result = self.tesla_api.open_close_trunk(self.user1, self.model_3_tag, "rear", "close")
        self.assertTrue(result["success"])

    def test_open_close_trunk_invalid_part(self):
        """Test trunk control with invalid part."""
        result = self.tesla_api.open_close_trunk(self.user1, self.model_3_tag, "middle", "open")
        self.assertFalse(result["success"])

    def test_set_charge_limit_valid_range(self):
        """Test setting charge limit within valid range."""
        result = self.tesla_api.set_charge_limit(self.user1, self.model_3_tag, 80)
        self.assertTrue(result["success"])

    def test_set_charge_limit_invalid_range(self):
        """Test setting charge limit outside valid range."""
        result = self.tesla_api.set_charge_limit(self.user1, self.model_3_tag, 110)  # Over 100
        self.assertFalse(result["success"])
        
        result = self.tesla_api.set_charge_limit(self.user1, self.model_3_tag, -5)  # Below 0
        self.assertFalse(result["success"])

    def test_open_close_charge_port_open(self):
        """Test opening charge port."""
        result = self.tesla_api.open_close_charge_port(self.user1, self.model_3_tag, "open")
        self.assertTrue(result["success"])

    def test_open_close_charge_port_close(self):
        """Test closing charge port."""
        result = self.tesla_api.open_close_charge_port(self.user1, self.model_3_tag, "close")
        self.assertTrue(result["success"])

    def test_start_stop_charge_start(self):
        """Test starting charge."""
        result = self.tesla_api.start_stop_charge(self.user1, self.model_3_tag, "start")
        self.assertTrue(result["success"])

    def test_start_stop_charge_stop(self):
        """Test stopping charge."""
        result = self.tesla_api.start_stop_charge(self.user1, self.model_3_tag, "stop")
        self.assertTrue(result["success"])

    def test_start_stop_climate_on(self):
        """Test turning climate control on."""
        result = self.tesla_api.start_stop_climate(self.user1, self.model_3_tag, "on")
        self.assertTrue(result["success"])

    def test_start_stop_climate_off(self):
        """Test turning climate control off."""
        result = self.tesla_api.start_stop_climate(self.user1, self.model_3_tag, "off")
        self.assertTrue(result["success"])

    def test_set_climate_temp_valid_range(self):
        """Test setting climate temperature within valid range."""
        result = self.tesla_api.set_climate_temp(self.user1, self.model_3_tag, 22, 20)
        self.assertTrue(result["success"])

    def test_set_climate_temp_invalid_range(self):
        """Test setting climate temperature outside valid range."""
        result = self.tesla_api.set_climate_temp(self.user1, self.model_3_tag, 50, 20)  # Too hot
        self.assertFalse(result["success"])
        
        result = self.tesla_api.set_climate_temp(self.user1, self.model_3_tag, 20, -10)  # Too cold
        self.assertFalse(result["success"])

    def test_set_bioweapon_mode_on(self):
        """Test enabling bioweapon mode."""
        result = self.tesla_api.set_bioweapon_mode(self.user1, self.model_3_tag, "on")
        self.assertTrue(result["success"])

    def test_set_bioweapon_mode_off(self):
        """Test disabling bioweapon mode."""
        result = self.tesla_api.set_bioweapon_mode(self.user1, self.model_3_tag, "off")
        self.assertTrue(result["success"])

    def test_set_climate_keeper_mode_off(self):
        """Test setting climate keeper mode to off."""
        result = self.tesla_api.set_climate_keeper_mode(self.user1, self.model_3_tag, "off")
        self.assertTrue(result["success"])

    def test_set_climate_keeper_mode_dog(self):
        """Test setting climate keeper mode to dog."""
        result = self.tesla_api.set_climate_keeper_mode(self.user1, self.model_3_tag, "dog")
        self.assertTrue(result["success"])

    def test_set_climate_keeper_mode_camp(self):
        """Test setting climate keeper mode to camp."""
        result = self.tesla_api.set_climate_keeper_mode(self.user1, self.model_3_tag, "camp")
        self.assertTrue(result["success"])

    def test_wake_up_success(self):
        """Test waking up vehicle."""
        result = self.tesla_api.wake_up(self.user1, self.model_3_tag)
        self.assertTrue(result["success"])

    def test_wake_up_invalid_vehicle(self):
        """Test waking up invalid vehicle."""
        result = self.tesla_api.wake_up(self.user1, "invalid_vehicle")
        self.assertFalse(result["success"])

    def test_window_control_vent(self):
        """Test venting windows."""
        result = self.tesla_api.window_control(
            self.user1, self.model_3_tag, "vent", 37.7749, -122.4194
        )
        self.assertTrue(result["success"])

    def test_window_control_close(self):
        """Test closing windows."""
        result = self.tesla_api.window_control(
            self.user1, self.model_3_tag, "close", 37.7749, -122.4194
        )
        self.assertTrue(result["success"])

    def test_window_control_invalid_command(self):
        """Test window control with invalid command."""
        result = self.tesla_api.window_control(
            self.user1, self.model_3_tag, "invalid", 37.7749, -122.4194
        )
        self.assertFalse(result["success"])

    def test_get_vehicle_location_success(self):
        """Test getting vehicle location."""
        result = self.tesla_api.get_vehicle_location(self.user1, self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertIn("location", result)
        self.assertIn("latitude", result["location"])
        self.assertIn("longitude", result["location"])

    def test_get_vehicle_location_invalid_vehicle(self):
        """Test getting location for invalid vehicle."""
        result = self.tesla_api.get_vehicle_location(self.user1, "invalid_vehicle")
        self.assertFalse(result["success"])

    def test_get_vehicle_status_success(self):
        """Test getting vehicle status."""
        result = self.tesla_api.get_vehicle_status(self.user1, self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertIn("status", result)
        self.assertIn("battery_level", result["status"])
        self.assertIn("charge_state", result["status"])

    def test_get_vehicle_status_invalid_vehicle(self):
        """Test getting status for invalid vehicle."""
        result = self.tesla_api.get_vehicle_status(self.user1, "invalid_vehicle")
        self.assertFalse(result["success"])

    def test_manage_sentry_mode_on(self):
        """Test enabling sentry mode."""
        result = self.tesla_api.manage_sentry_mode(self.user1, self.model_3_tag, "on")
        self.assertTrue(result["success"])

    def test_manage_sentry_mode_off(self):
        """Test disabling sentry mode."""
        result = self.tesla_api.manage_sentry_mode(self.user1, self.model_3_tag, "off")
        self.assertTrue(result["success"])

    def test_manage_sentry_mode_invalid_command(self):
        """Test sentry mode with invalid command."""
        result = self.tesla_api.manage_sentry_mode(self.user1, self.model_3_tag, "invalid")
        self.assertFalse(result["success"])

    def test_get_firmware_info_success(self):
        """Test getting firmware information."""
        result = self.tesla_api.get_firmware_info(self.user1, self.model_3_tag)
        self.assertTrue(result["success"])
        self.assertIn("firmware", result)
        self.assertIn("version", result["firmware"])

    def test_get_firmware_info_invalid_vehicle(self):
        """Test getting firmware info for invalid vehicle."""
        result = self.tesla_api.get_firmware_info(self.user1, "invalid_vehicle")
        self.assertFalse(result["success"])

    def test_comprehensive_vehicle_control_workflow(self):
        """Test comprehensive vehicle control workflow."""
        # Step 1: Wake up vehicle
        wake_result = self.tesla_api.wake_up(self.user1, self.model_3_tag)
        self.assertTrue(wake_result["success"])
        
        # Step 2: Get vehicle status
        status_result = self.tesla_api.get_vehicle_status(self.user1, self.model_3_tag)
        self.assertTrue(status_result["success"])
        
        # Step 3: Start climate control
        climate_result = self.tesla_api.start_stop_climate(self.user1, self.model_3_tag, "on")
        self.assertTrue(climate_result["success"])
        
        # Step 4: Set temperature
        temp_result = self.tesla_api.set_climate_temp(self.user1, self.model_3_tag, 22, 20)
        self.assertTrue(temp_result["success"])
        
        # Step 5: Enable sentry mode
        sentry_result = self.tesla_api.manage_sentry_mode(self.user1, self.model_3_tag, "on")
        self.assertTrue(sentry_result["success"])

    def test_charging_workflow_complete(self):
        """Test complete charging workflow."""
        # Step 1: Open charge port
        open_port_result = self.tesla_api.open_close_charge_port(self.user1, self.model_3_tag, "open")
        self.assertTrue(open_port_result["success"])
        
        # Step 2: Set charge limit
        limit_result = self.tesla_api.set_charge_limit(self.user1, self.model_3_tag, 90)
        self.assertTrue(limit_result["success"])
        
        # Step 3: Start charging
        start_charge_result = self.tesla_api.start_stop_charge(self.user1, self.model_3_tag, "start")
        self.assertTrue(start_charge_result["success"])
        
        # Step 4: Check status
        status_result = self.tesla_api.get_vehicle_status(self.user1, self.model_3_tag)
        self.assertTrue(status_result["success"])
        
        # Step 5: Stop charging
        stop_charge_result = self.tesla_api.start_stop_charge(self.user1, self.model_3_tag, "stop")
        self.assertTrue(stop_charge_result["success"])

    def test_media_control_comprehensive_workflow(self):
        """Test comprehensive media control workflow."""
        # Step 1: Start media
        start_result = self.tesla_api.start_stop_media(self.user1, self.model_3_tag, "start")
        self.assertTrue(start_result["success"])
        
        # Step 2: Set volume
        volume_result = self.tesla_api.set_volume(self.user1, self.model_3_tag, 60)
        self.assertTrue(volume_result["success"])
        
        # Step 3: Skip to next track
        next_result = self.tesla_api.skip_media_track(self.user1, self.model_3_tag, "next")
        self.assertTrue(next_result["success"])
        
        # Step 4: Skip to previous track
        prev_result = self.tesla_api.skip_media_track(self.user1, self.model_3_tag, "previous")
        self.assertTrue(prev_result["success"])
        
        # Step 5: Stop media
        stop_result = self.tesla_api.start_stop_media(self.user1, self.model_3_tag, "stop")
        self.assertTrue(stop_result["success"])

    def test_error_handling_edge_cases(self):
        """Test various error handling scenarios."""
        # Test with None user
        with self.assertRaises((AttributeError, TypeError)):
            self.tesla_api.show_vehicle_info(None, self.model_3_tag)
        
        # Test with empty vehicle tag
        result = self.tesla_api.honk_horn(self.user1, "")
        self.assertFalse(result["success"])
        
        # Test invalid temperature values
        result = self.tesla_api.set_climate_temp(self.user1, self.model_3_tag, 999, 20)
        self.assertFalse(result["success"])
        
        # Test invalid coordinates
        result = self.tesla_api.window_control(
            self.user1, self.model_3_tag, "vent", 999, 999  # Invalid lat/lon
        )
        self.assertFalse(result["success"])

    def test_multi_vehicle_operations(self):
        """Test operations across multiple vehicles."""
        # Test operations on Model 3
        model3_honk = self.tesla_api.honk_horn(self.user1, self.model_3_tag)
        self.assertTrue(model3_honk["success"])
        
        # Test operations on Model S
        models_honk = self.tesla_api.honk_horn(self.user1, self.model_s_tag)
        self.assertTrue(models_honk["success"])
        
        # Test getting status for both vehicles
        model3_status = self.tesla_api.get_vehicle_status(self.user1, self.model_3_tag)
        models_status = self.tesla_api.get_vehicle_status(self.user1, self.model_s_tag)
        
        self.assertTrue(model3_status["success"])
        self.assertTrue(models_status["success"])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)