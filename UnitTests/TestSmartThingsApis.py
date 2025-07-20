from audio_gorilla.SmartThingsApis import SmartThingsApis
import unittest

class TestSmartThingsApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh SmartThingsAPI instance for each test."""
        self.smart_api = SmartThingsApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.smart_api._load_default_state()
        self.default_location_id = "loc1"
        self.default_device_id = "device1"
        self.default_room_id = "room1"
        self.default_scene_id = "scene1"

    # --- Unit Tests for Core Functions (most important for audio calling) ---

    def test_list_devices_success(self):
        """Test listing all devices."""
        devices = self.smart_api.list_devices()
        self.assertIsInstance(devices, list)
        self.assertGreater(len(devices), 0)
        self.assertEqual(devices[0]["id"], self.default_device_id)

    def test_list_devices_by_location(self):
        """Test listing devices filtered by location ID."""
        # Add another device in a different location for testing
        self.smart_api.devices["device2"] = {"id": "device2", "name": "Kitchen Light", "location": "loc2", "status": "offline"}
        self.smart_api.locations["loc2"] = {"id": "loc2", "name": "Kitchen", "timezone": "EST"}

        devices_in_home = self.smart_api.list_devices(location_id="home")
        self.assertEqual(len(devices_in_home), 1)
        self.assertEqual(devices_in_home[0]["id"], self.default_device_id)

        devices_in_kitchen = self.smart_api.list_devices(location_id="loc2")
        self.assertEqual(len(devices_in_kitchen), 1)
        self.assertEqual(devices_in_kitchen[0]["id"], "device2")

    def test_get_device_status_success(self):
        """Test getting the status of a specific device."""
        status = self.smart_api.get_device_status(self.default_device_id)
        self.assertIn("status", status)
        self.assertEqual(status["status"], "online")
        self.assertIn("lastUpdated", status)

    def test_get_device_status_not_found(self):
        """Test getting the status of a non-existent device."""
        status = self.smart_api.get_device_status("non_existent_device")
        self.assertIn("error", status)
        self.assertEqual(status["error"], "Device with ID non_existent_device not found")

    def test_execute_device_command_success(self):
        """Test executing commands on a device."""
        commands = [{"capability": "switch", "command": "on"}]
        result = self.smart_api.execute_device_command(self.default_device_id, commands)
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["commandsExecuted"], 1)

    def test_execute_device_command_not_found(self):
        """Test executing commands on a non-existent device."""
        commands = [{"capability": "switch", "command": "on"}]
        result = self.smart_api.execute_device_command("non_existent_device", commands)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Device with ID non_existent_device not found")

    def test_list_locations_success(self):
        """Test listing all locations."""
        locations = self.smart_api.list_locations()
        self.assertIsInstance(locations, list)
        self.assertGreater(len(locations), 0)
        self.assertEqual(locations[0]["id"], self.default_location_id)

    def test_set_location_mode_success(self):
        """Test setting the current mode for a location."""
        result = self.smart_api.set_location_mode(self.default_location_id, "mode2")
        self.assertIn("currentMode", result)
        self.assertEqual(result["currentMode"], "mode2")
        self.assertEqual(self.smart_api.current_modes[self.default_location_id], "mode2")

    def test_set_location_mode_invalid_mode(self):
        """Test setting an invalid mode for a location."""
        result = self.smart_api.set_location_mode(self.default_location_id, "invalid_mode")
        self.assertIn("error", result)
        self.assertEqual(result["error"], f"Mode with ID invalid_mode not found for location {self.default_location_id}")
        # Mode should not have changed
        self.assertEqual(self.smart_api.current_modes[self.default_location_id], "mode1")

    def test_list_rooms_success(self):
        """Test listing rooms in a location."""
        rooms = self.smart_api.list_rooms(self.default_location_id)
        self.assertIsInstance(rooms, list)
        self.assertGreater(len(rooms), 0)
        self.assertEqual(rooms[0]["id"], self.default_room_id)

    def test_execute_scene_success(self):
        """Test executing a scene."""
        result = self.smart_api.execute_scene(self.default_location_id, self.default_scene_id)
        self.assertIn("status", result)
        self.assertEqual(result["status"], "executed")

    def test_execute_scene_not_found(self):
        """Test executing a non-existent scene."""
        result = self.smart_api.execute_scene(self.default_location_id, "non_existent_scene")
        self.assertIn("error", result)
        self.assertEqual(result["error"], f"Scene with ID non_existent_scene not found in location {self.default_location_id}")

    # --- Combined Functionality Tests ---

    def test_list_devices_and_get_status(self):
        """
        Scenario: List all devices, then get the status of one of them.
        Functions: list_devices, get_device_status
        """
        # 1. List all devices
        all_devices = self.smart_api.list_devices()
        self.assertIsInstance(all_devices, list)
        self.assertGreater(len(all_devices), 0)
        
        # Assume we pick the first device found
        device_to_check_id = all_devices[0]["id"]

        # 2. Get the status of that device
        status_result = self.smart_api.get_device_status(device_to_check_id)
        self.assertIn("status", status_result)
        self.assertEqual(status_result["id"], device_to_check_id)
        self.assertIn(status_result["status"], ["online", "offline", "unknown"]) # Check for valid status

    def test_create_device_and_execute_command(self):
        """
        Scenario: Create a new device, then execute a command on it.
        Functions: create_device, execute_device_command
        """
        # 1. Create a new device
        new_device_data = {"name": "New Smart Plug", "location": "home", "status": "offline"}
        create_result = self.smart_api.create_device(new_device_data)
        self.assertIn("id", create_result)
        new_device_id = create_result["id"]
        self.assertEqual(create_result["name"], "New Smart Plug")
        self.assertEqual(self.smart_api.devices[new_device_id]["status"], "offline")

        # 2. Execute a command on the new device (e.g., turn it on)
        commands = [{"capability": "switch", "command": "on"}]
        execute_result = self.smart_api.execute_device_command(new_device_id, commands)
        self.assertIn("status", execute_result)
        self.assertEqual(execute_result["status"], "success")
        self.assertEqual(execute_result["deviceId"], new_device_id)

        # In a real API, the device's status would change after command.
        # Here, we can only assert the command execution was reported as successful.
        # If the dummy backend updated status, we'd add:
        # self.assertEqual(self.smart_api.devices[new_device_id]["status"], "online")

    def test_set_location_mode_and_list_rooms(self):
        """
        Scenario: Set a location mode, then list rooms in that location.
        Functions: set_location_mode, list_rooms
        """
        # 1. Set the location mode to 'Away'
        set_mode_result = self.smart_api.set_location_mode(self.default_location_id, "mode2")
        self.assertIn("currentMode", set_mode_result)
        self.assertEqual(set_mode_result["currentMode"], "mode2")
        self.assertEqual(self.smart_api.current_modes[self.default_location_id], "mode2")

        # 2. List rooms in that location (should still be the same rooms, mode change doesn't affect list)
        rooms_in_location = self.smart_api.list_rooms(self.default_location_id)
        self.assertIsInstance(rooms_in_location, list)
        self.assertEqual(len(rooms_in_location), 1) # Still one room in default state
        self.assertEqual(rooms_in_location[0]["id"], self.default_room_id)
        self.assertEqual(rooms_in_location[0]["locationId"], self.default_location_id)

    def test_create_room_and_get_room_details(self):
        """
        Scenario: Create a new room, then get its details.
        Functions: create_room, get_room
        """
        # 1. Create a new room
        new_room_data = {"name": "Bathroom"}
        create_room_result = self.smart_api.create_room(self.default_location_id, new_room_data)
        self.assertIn("id", create_room_result)
        new_room_id = create_room_result["id"]
        self.assertEqual(create_room_result["name"], "Bathroom")
        self.assertEqual(create_room_result["locationId"], self.default_location_id)
        self.assertIn(new_room_id, self.smart_api.rooms)

        # 2. Get the details of the newly created room
        get_room_result = self.smart_api.get_room(self.default_location_id, new_room_id)
        self.assertIn("id", get_room_result)
        self.assertEqual(get_room_result["id"], new_room_id)
        self.assertEqual(get_room_result["name"], "Bathroom")
        self.assertEqual(get_room_result["locationId"], self.default_location_id)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
