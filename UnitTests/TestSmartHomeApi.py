import unittest
from SmartHomeApis import SmartHomeAPI, ControllerAPI, ColorControl, Lock, LockCodes, MediaPlayback, Switch, SwitchLevel, ThermostatCoolingSetpoint, ThermostatFanMode

class TestSmartHomeAPI(unittest.TestCase):
    def setUp(self):
        self.api = SmartHomeAPI()

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - SWITCH METHODS
    # ============================================================================

    def test_switch_on_basic(self):
        """Test basic switch.on functionality"""
        sw = self.api.switch
        resp = sw.on()
        self.assertTrue(resp)
        self.assertEqual(sw.current_switch_state, "on")

    def test_switch_off_basic(self):
        """Test basic switch.off functionality"""
        sw = self.api.switch
        # First turn on
        sw.on()
        # Then turn off
        resp = sw.off()
        self.assertTrue(resp)
        self.assertEqual(sw.current_switch_state, "off")

    def test_switch_on_off_cycle(self):
        """Test switch on/off cycle"""
        sw = self.api.switch
        # Test multiple cycles
        for i in range(3):
            self.assertTrue(sw.on())
            self.assertEqual(sw.current_switch_state, "on")
            self.assertTrue(sw.off())
            self.assertEqual(sw.current_switch_state, "off")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - SWITCH LEVEL METHODS
    # ============================================================================

    def test_switch_level_setLevel_basic(self):
        """Test basic switch_level.setLevel functionality"""
        sl = self.api.switch_level
        resp = sl.setLevel(50)
        self.assertTrue(resp)
        self.assertEqual(sl.current_level, 50)

    def test_switch_level_setLevel_minimum(self):
        """Test switch_level.setLevel with minimum value"""
        sl = self.api.switch_level
        resp = sl.setLevel(0)
        self.assertTrue(resp)
        self.assertEqual(sl.current_level, 0)

    def test_switch_level_setLevel_maximum(self):
        """Test switch_level.setLevel with maximum value"""
        sl = self.api.switch_level
        resp = sl.setLevel(100)
        self.assertTrue(resp)
        self.assertEqual(sl.current_level, 100)

    def test_switch_level_setLevel_negative(self):
        """Test switch_level.setLevel with negative value"""
        sl = self.api.switch_level
        resp = sl.setLevel(-10)
        self.assertTrue(resp)
        self.assertEqual(sl.current_level, -10)

    def test_switch_level_setLevel_high(self):
        """Test switch_level.setLevel with very high value"""
        sl = self.api.switch_level
        resp = sl.setLevel(1000)
        self.assertTrue(resp)
        self.assertEqual(sl.current_level, 1000)

    def test_switch_level_multiple_levels(self):
        """Test switch_level.setLevel with multiple different levels"""
        sl = self.api.switch_level
        levels = [0, 25, 50, 75, 100, 0]
        for level in levels:
            self.assertTrue(sl.setLevel(level))
            self.assertEqual(sl.current_level, level)

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - COLOR CONTROL METHODS
    # ============================================================================

    def test_color_control_setColor_basic(self):
        """Test basic color_control.setColor functionality"""
        cc = self.api.color_control
        resp = cc.setColor(120, 80)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color, {"hue": 120, "saturation": 80})

    def test_color_control_setColor_minimum_values(self):
        """Test color_control.setColor with minimum values"""
        cc = self.api.color_control
        resp = cc.setColor(0, 0)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color, {"hue": 0, "saturation": 0})

    def test_color_control_setColor_maximum_values(self):
        """Test color_control.setColor with maximum values"""
        cc = self.api.color_control
        resp = cc.setColor(360, 100)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color, {"hue": 360, "saturation": 100})

    def test_color_control_setColor_negative_values(self):
        """Test color_control.setColor with negative values"""
        cc = self.api.color_control
        resp = cc.setColor(-50, -25)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color, {"hue": -50, "saturation": -25})

    def test_color_control_setColor_high_values(self):
        """Test color_control.setColor with very high values"""
        cc = self.api.color_control
        resp = cc.setColor(1000, 200)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color, {"hue": 1000, "saturation": 200})

    def test_color_control_setHue_basic(self):
        """Test basic color_control.setHue functionality"""
        cc = self.api.color_control
        resp = cc.setHue(200)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color["hue"], 200)

    def test_color_control_setHue_minimum(self):
        """Test color_control.setHue with minimum value"""
        cc = self.api.color_control
        resp = cc.setHue(0)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color["hue"], 0)

    def test_color_control_setHue_maximum(self):
        """Test color_control.setHue with maximum value"""
        cc = self.api.color_control
        resp = cc.setHue(360)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color["hue"], 360)

    def test_color_control_setHue_negative(self):
        """Test color_control.setHue with negative value"""
        cc = self.api.color_control
        resp = cc.setHue(-100)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color["hue"], -100)

    def test_color_control_setHue_high(self):
        """Test color_control.setHue with very high value"""
        cc = self.api.color_control
        resp = cc.setHue(1000)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color["hue"], 1000)

    def test_color_control_setSaturation_basic(self):
        """Test basic color_control.setSaturation functionality"""
        cc = self.api.color_control
        resp = cc.setSaturation(60)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color["saturation"], 60)

    def test_color_control_setSaturation_minimum(self):
        """Test color_control.setSaturation with minimum value"""
        cc = self.api.color_control
        resp = cc.setSaturation(0)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color["saturation"], 0)

    def test_color_control_setSaturation_maximum(self):
        """Test color_control.setSaturation with maximum value"""
        cc = self.api.color_control
        resp = cc.setSaturation(100)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color["saturation"], 100)

    def test_color_control_setSaturation_negative(self):
        """Test color_control.setSaturation with negative value"""
        cc = self.api.color_control
        resp = cc.setSaturation(-50)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color["saturation"], -50)

    def test_color_control_setSaturation_high(self):
        """Test color_control.setSaturation with very high value"""
        cc = self.api.color_control
        resp = cc.setSaturation(200)
        self.assertTrue(resp)
        self.assertEqual(cc.current_color["saturation"], 200)

    def test_color_control_multiple_operations(self):
        """Test color_control with multiple operations"""
        cc = self.api.color_control
        # Test setColor
        self.assertTrue(cc.setColor(180, 50))
        self.assertEqual(cc.current_color, {"hue": 180, "saturation": 50})
        
        # Test setHue
        self.assertTrue(cc.setHue(90))
        self.assertEqual(cc.current_color, {"hue": 90, "saturation": 50})
        
        # Test setSaturation
        self.assertTrue(cc.setSaturation(75))
        self.assertEqual(cc.current_color, {"hue": 90, "saturation": 75})

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - LOCK METHODS
    # ============================================================================

    def test_lock_lock_basic(self):
        """Test basic lock.lock functionality"""
        lock = self.api.lock
        resp = lock.lock()
        self.assertTrue(resp)
        self.assertEqual(lock.current_lock_state, "locked")

    def test_lock_unlock_basic(self):
        """Test basic lock.unlock functionality"""
        lock = self.api.lock
        # First lock
        lock.lock()
        # Then unlock
        resp = lock.unlock()
        self.assertTrue(resp)
        self.assertEqual(lock.current_lock_state, "unlocked")

    def test_lock_lock_unlock_cycle(self):
        """Test lock lock/unlock cycle"""
        lock = self.api.lock
        # Test multiple cycles
        for i in range(3):
            self.assertTrue(lock.lock())
            self.assertEqual(lock.current_lock_state, "locked")
            self.assertTrue(lock.unlock())
            self.assertEqual(lock.current_lock_state, "unlocked")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - LOCK CODES METHODS
    # ============================================================================

    def test_lock_codes_setCode_basic(self):
        """Test basic lock_codes.setCode functionality"""
        codes = self.api.lock_codes
        resp = codes.setCode("1", "1234", "Front Door")
        self.assertTrue(resp)
        code_info = codes.requestCode("1")
        self.assertEqual(code_info, {"pin": "1234", "name": "Front Door"})

    def test_lock_codes_setCode_empty_pin(self):
        """Test lock_codes.setCode with empty PIN"""
        codes = self.api.lock_codes
        resp = codes.setCode("2", "", "Empty Code")
        self.assertTrue(resp)
        code_info = codes.requestCode("2")
        self.assertEqual(code_info, {"pin": "", "name": "Empty Code"})

    def test_lock_codes_setCode_long_pin(self):
        """Test lock_codes.setCode with very long PIN"""
        codes = self.api.lock_codes
        long_pin = "1" * 100
        resp = codes.setCode("3", long_pin, "Long Code")
        self.assertTrue(resp)
        code_info = codes.requestCode("3")
        self.assertEqual(code_info, {"pin": long_pin, "name": "Long Code"})

    def test_lock_codes_setCode_special_characters(self):
        """Test lock_codes.setCode with special characters"""
        codes = self.api.lock_codes
        special_pin = "!@#$%^&*()"
        resp = codes.setCode("4", special_pin, "Special Code")
        self.assertTrue(resp)
        code_info = codes.requestCode("4")
        self.assertEqual(code_info, {"pin": special_pin, "name": "Special Code"})

    def test_lock_codes_setCode_empty_name(self):
        """Test lock_codes.setCode with empty name"""
        codes = self.api.lock_codes
        resp = codes.setCode("5", "5678", "")
        self.assertTrue(resp)
        code_info = codes.requestCode("5")
        self.assertEqual(code_info, {"pin": "5678", "name": ""})

    def test_lock_codes_requestCode_basic(self):
        """Test basic lock_codes.requestCode functionality"""
        codes = self.api.lock_codes
        codes.setCode("6", "9999", "Test Code")
        code_info = codes.requestCode("6")
        self.assertEqual(code_info, {"pin": "9999", "name": "Test Code"})

    def test_lock_codes_requestCode_nonexistent(self):
        """Test lock_codes.requestCode with nonexistent code"""
        codes = self.api.lock_codes
        code_info = codes.requestCode("999")
        self.assertEqual(code_info, "")

    def test_lock_codes_deleteCode_basic(self):
        """Test basic lock_codes.deleteCode functionality"""
        codes = self.api.lock_codes
        codes.setCode("7", "7777", "To Delete")
        # Verify code exists
        self.assertEqual(codes.requestCode("7"), {"pin": "7777", "name": "To Delete"})
        # Delete the code
        resp = codes.deleteCode("7")
        self.assertTrue(resp)
        # Verify code is deleted
        self.assertEqual(codes.requestCode("7"), "")

    def test_lock_codes_deleteCode_nonexistent(self):
        """Test lock_codes.deleteCode with nonexistent code"""
        codes = self.api.lock_codes
        resp = codes.deleteCode("999")
        self.assertTrue(resp)  # Should not fail

    def test_lock_codes_reloadAllCodes_basic(self):
        """Test basic lock_codes.reloadAllCodes functionality"""
        codes = self.api.lock_codes
        resp = codes.reloadAllCodes()
        self.assertTrue(resp)

    def test_lock_codes_setCodeLength_basic(self):
        """Test basic lock_codes.setCodeLength functionality"""
        codes = self.api.lock_codes
        resp = codes.setCodeLength(6)
        self.assertTrue(resp)

    def test_lock_codes_updateCodes_basic(self):
        """Test basic lock_codes.updateCodes functionality"""
        codes = self.api.lock_codes
        new_codes = {
            "8": {"pin": "8888", "name": "Code 8"},
            "9": {"pin": "9999", "name": "Code 9"}
        }
        resp = codes.updateCodes(new_codes)
        self.assertTrue(resp)
        # Verify codes were updated
        self.assertEqual(codes.requestCode("8"), {"pin": "8888", "name": "Code 8"})
        self.assertEqual(codes.requestCode("9"), {"pin": "9999", "name": "Code 9"})

    def test_lock_codes_multiple_operations(self):
        """Test lock_codes with multiple operations"""
        codes = self.api.lock_codes
        # Set multiple codes
        self.assertTrue(codes.setCode("10", "1010", "Code 10"))
        self.assertTrue(codes.setCode("11", "1111", "Code 11"))
        
        # Request codes
        self.assertEqual(codes.requestCode("10"), {"pin": "1010", "name": "Code 10"})
        self.assertEqual(codes.requestCode("11"), {"pin": "1111", "name": "Code 11"})
        
        # Delete one code
        self.assertTrue(codes.deleteCode("10"))
        self.assertEqual(codes.requestCode("10"), "")
        self.assertEqual(codes.requestCode("11"), {"pin": "1111", "name": "Code 11"})

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - THERMOSTAT COOLING SETPOINT METHODS
    # ============================================================================

    def test_thermostat_cooling_setpoint_setCoolingSetpoint_basic(self):
        """Test basic thermostat_cooling_setpoint.setCoolingSetpoint functionality"""
        cool = self.api.thermostat_cooling_setpoint
        resp = cool.setCoolingSetpoint(72)
        self.assertTrue(resp)
        self.assertEqual(cool.current_cooling_setpoint, 72)

    def test_thermostat_cooling_setpoint_setCoolingSetpoint_minimum(self):
        """Test thermostat_cooling_setpoint.setCoolingSetpoint with minimum value"""
        cool = self.api.thermostat_cooling_setpoint
        resp = cool.setCoolingSetpoint(-50)
        self.assertTrue(resp)
        self.assertEqual(cool.current_cooling_setpoint, -50)

    def test_thermostat_cooling_setpoint_setCoolingSetpoint_maximum(self):
        """Test thermostat_cooling_setpoint.setCoolingSetpoint with maximum value"""
        cool = self.api.thermostat_cooling_setpoint
        resp = cool.setCoolingSetpoint(150)
        self.assertTrue(resp)
        self.assertEqual(cool.current_cooling_setpoint, 150)

    def test_thermostat_cooling_setpoint_setCoolingSetpoint_zero(self):
        """Test thermostat_cooling_setpoint.setCoolingSetpoint with zero"""
        cool = self.api.thermostat_cooling_setpoint
        resp = cool.setCoolingSetpoint(0)
        self.assertTrue(resp)
        self.assertEqual(cool.current_cooling_setpoint, 0)

    def test_thermostat_cooling_setpoint_multiple_values(self):
        """Test thermostat_cooling_setpoint.setCoolingSetpoint with multiple values"""
        cool = self.api.thermostat_cooling_setpoint
        temperatures = [65, 70, 75, 80, 65]
        for temp in temperatures:
            self.assertTrue(cool.setCoolingSetpoint(temp))
            self.assertEqual(cool.current_cooling_setpoint, temp)

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - THERMOSTAT FAN MODE METHODS
    # ============================================================================

    def test_thermostat_fan_mode_fanAuto_basic(self):
        """Test basic thermostat_fan_mode.fanAuto functionality"""
        fan = self.api.thermostat_fan_mode
        resp = fan.fanAuto()
        self.assertTrue(resp)
        self.assertEqual(fan.current_fan_mode, "auto")

    def test_thermostat_fan_mode_fanOn_basic(self):
        """Test basic thermostat_fan_mode.fanOn functionality"""
        fan = self.api.thermostat_fan_mode
        resp = fan.fanOn()
        self.assertTrue(resp)
        self.assertEqual(fan.current_fan_mode, "on")

    def test_thermostat_fan_mode_setThermostatFanMode_basic(self):
        """Test basic thermostat_fan_mode.setThermostatFanMode functionality"""
        fan = self.api.thermostat_fan_mode
        resp = fan.setThermostatFanMode("circulate")
        self.assertTrue(resp)
        self.assertEqual(fan.current_fan_mode, "circulate")

    def test_thermostat_fan_mode_setThermostatFanMode_invalid(self):
        """Test thermostat_fan_mode.setThermostatFanMode with invalid mode"""
        fan = self.api.thermostat_fan_mode
        resp = fan.setThermostatFanMode("invalid_mode")
        self.assertTrue(resp)
        self.assertEqual(fan.current_fan_mode, "invalid_mode")

    def test_thermostat_fan_mode_setThermostatFanMode_empty(self):
        """Test thermostat_fan_mode.setThermostatFanMode with empty mode"""
        fan = self.api.thermostat_fan_mode
        resp = fan.setThermostatFanMode("")
        self.assertTrue(resp)
        self.assertEqual(fan.current_fan_mode, "")

    def test_thermostat_fan_mode_setThermostatFanMode_long(self):
        """Test thermostat_fan_mode.setThermostatFanMode with very long mode"""
        fan = self.api.thermostat_fan_mode
        long_mode = "very_long_fan_mode_name_that_exceeds_normal_length"
        resp = fan.setThermostatFanMode(long_mode)
        self.assertTrue(resp)
        self.assertEqual(fan.current_fan_mode, long_mode)

    def test_thermostat_fan_mode_multiple_operations(self):
        """Test thermostat_fan_mode with multiple operations"""
        fan = self.api.thermostat_fan_mode
        # Test different modes
        self.assertTrue(fan.fanAuto())
        self.assertEqual(fan.current_fan_mode, "auto")
        
        self.assertTrue(fan.fanOn())
        self.assertEqual(fan.current_fan_mode, "on")
        
        self.assertTrue(fan.setThermostatFanMode("circulate"))
        self.assertEqual(fan.current_fan_mode, "circulate")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - MEDIA PLAYBACK METHODS
    # ============================================================================

    def test_media_playback_fastForward_basic(self):
        """Test basic media_playback.fastForward functionality"""
        mp = self.api.media_playback
        resp = mp.fastForward()
        self.assertTrue(resp)
        self.assertEqual(mp.current_media_state, "fast_forward")

    def test_media_playback_pause_basic(self):
        """Test basic media_playback.pause functionality"""
        mp = self.api.media_playback
        resp = mp.pause()
        self.assertTrue(resp)
        self.assertEqual(mp.current_media_state, "paused")

    def test_media_playback_stop_basic(self):
        """Test basic media_playback.stop functionality"""
        mp = self.api.media_playback
        resp = mp.stop()
        self.assertTrue(resp)
        self.assertEqual(mp.current_media_state, "stopped")

    def test_media_playback_state_transitions(self):
        """Test media_playback state transitions"""
        mp = self.api.media_playback
        # Test multiple state changes
        self.assertTrue(mp.fastForward())
        self.assertEqual(mp.current_media_state, "fast_forward")
        
        self.assertTrue(mp.pause())
        self.assertEqual(mp.current_media_state, "paused")
        
        self.assertTrue(mp.stop())
        self.assertEqual(mp.current_media_state, "stopped")
        
        # Test calling same state multiple times
        self.assertTrue(mp.stop())
        self.assertEqual(mp.current_media_state, "stopped")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - CONTROLLER API METHODS
    # ============================================================================

    def test_controller_api_getClient_basic(self):
        """Test basic controller_api.getClient functionality"""
        controller = self.api.controller_api
        client = controller.getClient("test_context")
        self.assertIsNotNone(client)

    def test_controller_api_getDevice_basic(self):
        """Test basic controller_api.getDevice functionality"""
        controller = self.api.controller_api
        device = controller.getDevice("test_device_id")
        # Should return None for nonexistent device
        self.assertIsNone(device)

    def test_controller_api_readCapability_basic(self):
        """Test basic controller_api.readCapability functionality"""
        controller = self.api.controller_api
        capability = controller.readCapability("test_capability")
        self.assertIsInstance(capability, dict)

    # ============================================================================
    # CONCURRENT OPERATIONS TESTS
    # ============================================================================

    def test_concurrent_operations_different_components(self):
        """Test concurrent-like operations on different components"""
        # Test operations on multiple components simultaneously
        sw = self.api.switch
        sl = self.api.switch_level
        cc = self.api.color_control
        lock = self.api.lock
        
        # Perform operations on all components
        self.assertTrue(sw.on())
        self.assertTrue(sl.setLevel(75))
        self.assertTrue(cc.setColor(180, 50))
        self.assertTrue(lock.lock())
        
        # Verify all states are correct
        self.assertEqual(sw.current_switch_state, "on")
        self.assertEqual(sl.current_level, 75)
        self.assertEqual(cc.current_color, {"hue": 180, "saturation": 50})
        self.assertEqual(lock.current_lock_state, "locked")

    def test_concurrent_operations_same_component(self):
        """Test concurrent-like operations on the same component"""
        sl = self.api.switch_level
        # Perform multiple operations on the same component
        self.assertTrue(sl.setLevel(25))
        self.assertTrue(sl.setLevel(50))
        self.assertTrue(sl.setLevel(75))
        self.assertTrue(sl.setLevel(100))
        
        # Verify final state
        self.assertEqual(sl.current_level, 100)

    # ============================================================================
    # EDGE CASE TESTS
    # ============================================================================

    def test_empty_and_none_values(self):
        """Test handling of empty and None values"""
        codes = self.api.lock_codes
        cc = self.api.color_control
        
        # Test with None values (should handle gracefully)
        try:
            codes.setCode(None, "1234", "Test")
        except:
            pass  # Expected to fail, but shouldn't crash
        
        try:
            cc.setColor(None, None)
        except:
            pass  # Expected to fail, but shouldn't crash

    def test_boundary_values_all_components(self):
        """Test boundary values for all components"""
        # Switch level boundary values
        sl = self.api.switch_level
        self.assertTrue(sl.setLevel(0))
        self.assertEqual(sl.current_level, 0)
        self.assertTrue(sl.setLevel(100))
        self.assertEqual(sl.current_level, 100)
        self.assertTrue(sl.setLevel(-10))
        self.assertEqual(sl.current_level, -10)
        self.assertTrue(sl.setLevel(1000))
        self.assertEqual(sl.current_level, 1000)
        
        # Color control boundary values
        cc = self.api.color_control
        self.assertTrue(cc.setColor(0, 0))
        self.assertEqual(cc.current_color, {"hue": 0, "saturation": 0})
        self.assertTrue(cc.setColor(360, 100))
        self.assertEqual(cc.current_color, {"hue": 360, "saturation": 100})
        self.assertTrue(cc.setColor(-50, -25))
        self.assertEqual(cc.current_color, {"hue": -50, "saturation": -25})
        self.assertTrue(cc.setColor(1000, 200))
        self.assertEqual(cc.current_color, {"hue": 1000, "saturation": 200})
        
        # Thermostat boundary values
        cool = self.api.thermostat_cooling_setpoint
        self.assertTrue(cool.setCoolingSetpoint(-50))
        self.assertEqual(cool.current_cooling_setpoint, -50)
        self.assertTrue(cool.setCoolingSetpoint(150))
        self.assertEqual(cool.current_cooling_setpoint, 150)
        self.assertTrue(cool.setCoolingSetpoint(0))
        self.assertEqual(cool.current_cooling_setpoint, 0)

    def test_state_transitions_all_components(self):
        """Test state transitions for all components"""
        # Switch state transitions
        sw = self.api.switch
        for i in range(5):
            self.assertTrue(sw.on())
            self.assertEqual(sw.current_switch_state, "on")
            self.assertTrue(sw.off())
            self.assertEqual(sw.current_switch_state, "off")
        
        # Lock state transitions
        lock = self.api.lock
        for i in range(5):
            self.assertTrue(lock.lock())
            self.assertEqual(lock.current_lock_state, "locked")
            self.assertTrue(lock.unlock())
            self.assertEqual(lock.current_lock_state, "unlocked")
        
        # Media playback state transitions
        mp = self.api.media_playback
        states = ["fast_forward", "paused", "stopped"]
        for state in states:
            if state == "fast_forward":
                self.assertTrue(mp.fastForward())
            elif state == "paused":
                self.assertTrue(mp.pause())
            elif state == "stopped":
                self.assertTrue(mp.stop())
            self.assertEqual(mp.current_media_state, state)

if __name__ == "__main__":
    unittest.main() 