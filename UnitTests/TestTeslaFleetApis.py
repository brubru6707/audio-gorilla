import unittest
from copy import deepcopy
from audio_gorilla.TeslaFleetApis import TeslaFleetApis, DEFAULT_STATE

class TestTeslaFleetApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh TeslaFleetApis instance for each test."""
        self.tesla_api = TeslaFleetApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.tesla_api._load_scenario(deepcopy(DEFAULT_STATE))
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


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)