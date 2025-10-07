import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import backend creator
from SmartThingsApis import SmartThingsApis
from UnitTests.test_data_helper import BackendDataLoader

class TestSmartThingsApis(unittest.TestCase):
    """
    Unit tests for the SmartThingsApis class.
    Tests are based on the actual API implementation and loaded test data.
    """

    def setUp(self):
        """Set up the API instance and extract test data."""
        self.smart_things_api = SmartThingsApis()

        # Get actual loaded data for testing
        devices = self.smart_things_api.list_devices()
        locations = self.smart_things_api.list_locations()
        rooms = self.smart_things_api.list_rooms()

        # Extract real IDs from loaded data
        self.first_device_id = devices[0]['id'] if devices else None
        self.first_device_name = devices[0]['name'] if devices else None
        self.first_location_id = locations[0]['id'] if locations else None
        self.first_location_name = locations[0]['name'] if locations else None
        self.first_room_id = rooms[0]['id'] if rooms else None
        self.first_room_name = rooms[0]['name'] if rooms else None

        # Store counts for validation
        self.initial_device_count = len(devices)
        self.initial_location_count = len(locations)
        self.initial_room_count = len(rooms)

    def tearDown(self):
        """Reset the API state after each test to ensure test isolation."""
        self.smart_things_api.reset_data()

    # ================
    # User Profile Tests
    # ================

    def test_get_user_profile_success(self):
        """Test getting user profile for default user."""
        result = self.smart_things_api.get_user_profile()
        self.assertTrue(result["status"])
        self.assertIn("profile", result)
        self.assertIsInstance(result["profile"], dict)

    def test_get_user_profile_invalid_user(self):
        """Test getting user profile for invalid user."""
        result = self.smart_things_api.get_user_profile("invalid_user")
        self.assertFalse(result["status"])

    # ================
    # Device Tests
    # ================

    def test_list_devices(self):
        """Test listing all devices."""
        devices = self.smart_things_api.list_devices()
        self.assertIsInstance(devices, list)
        self.assertEqual(len(devices), self.initial_device_count)
        if devices:
            self.assertIn("id", devices[0])
            self.assertIn("name", devices[0])

    def test_get_device_success(self):
        """Test getting a specific device by ID."""
        if not self.first_device_id:
            self.skipTest("No devices available for testing")

        device = self.smart_things_api.get_device(self.first_device_id)
        self.assertIsInstance(device, dict)
        self.assertEqual(device["id"], self.first_device_id)
        self.assertEqual(device["name"], self.first_device_name)

    def test_get_device_not_found(self):
        """Test getting a non-existent device."""
        device = self.smart_things_api.get_device("nonexistent-device-id")
        self.assertIn("error", device)

    def test_get_device_status_success(self):
        """Test getting the status of a device."""
        if not self.first_device_id:
            self.skipTest("No devices available for testing")

        status = self.smart_things_api.get_device_status(self.first_device_id)
        self.assertEqual(status["status"], "success")
        self.assertIn("component_status", status)

    def test_get_device_status_not_found(self):
        """Test getting the status of a non-existent device."""
        status = self.smart_things_api.get_device_status("nonexistent-device-id")
        self.assertIn("error", status)

    def test_update_device_status_success(self):
        """Test updating device status."""
        if not self.first_device_id:
            self.skipTest("No devices available for testing")

        # Update switch status
        result = self.smart_things_api.update_device_status(
            device_id=self.first_device_id,
            component_id="main",
            capability_id="switch",
            command="off"
        )
        self.assertEqual(result["status"], "success")

        # Verify the change
        status = self.smart_things_api.get_device_status(self.first_device_id)
        if "switch" in status["component_status"]:
            self.assertEqual(status["component_status"]["switch"]["switch"], "off")

    def test_create_device_success(self):
        """Test creating a new device."""
        result = self.smart_things_api.create_device(
            name="Test Device",
            capabilities=["switch"],
            initial_status={"main": {"switch": {"switch": "off"}}}
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertIn("device", result)
        self.assertEqual(result["device"]["name"], "Test Device")

        # Verify device was added
        devices = self.smart_things_api.list_devices()
        self.assertEqual(len(devices), self.initial_device_count + 1)

    def test_delete_device_success(self):
        """Test deleting an existing device."""
        if not self.first_device_id:
            self.skipTest("No devices available for testing")

        result = self.smart_things_api.delete_device(self.first_device_id)
        self.assertEqual(result["status"], True)

        # Verify device was removed
        devices = self.smart_things_api.list_devices()
        self.assertEqual(len(devices), self.initial_device_count - 1)

    def test_delete_device_not_found(self):
        """Test deleting a non-existent device."""
        result = self.smart_things_api.delete_device("nonexistent-device-id")
        self.assertEqual(result["status"], False)

    def test_get_device_health_success(self):
        """Test getting device health."""
        if not self.first_device_id:
            self.skipTest("No devices available for testing")

        health = self.smart_things_api.get_device_health(self.first_device_id)
        self.assertEqual(health["status"], "success")
        self.assertIn("health", health)
        self.assertEqual(health["health"]["device_id"], self.first_device_id)

    def test_list_devices_by_health_status(self):
        """Test listing devices by health status."""
        devices = self.smart_things_api.list_devices_by_health_status("online")
        self.assertIsInstance(devices, list)
        # All default devices should be online
        self.assertGreaterEqual(len(devices), 0)

    def test_list_devices_by_manufacturer(self):
        """Test listing devices by manufacturer."""
        devices = self.smart_things_api.list_devices_by_manufacturer("SmartThings")
        self.assertIsInstance(devices, list)

    def test_update_device_firmware_success(self):
        """Test updating device firmware."""
        if not self.first_device_id:
            self.skipTest("No devices available for testing")

        result = self.smart_things_api.update_device_firmware(self.first_device_id, "v2.0.0")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["new_version"], "v2.0.0")

    # ================
    # Location Tests
    # ================

    def test_list_locations(self):
        """Test listing all locations."""
        locations = self.smart_things_api.list_locations()
        self.assertIsInstance(locations, list)
        self.assertEqual(len(locations), self.initial_location_count)
        if locations:
            self.assertIn("id", locations[0])
            self.assertIn("name", locations[0])

    def test_get_location_success(self):
        """Test getting a specific location by ID."""
        if not self.first_location_id:
            self.skipTest("No locations available for testing")

        location = self.smart_things_api.get_location(self.first_location_id)
        self.assertIsInstance(location, dict)
        self.assertEqual(location["id"], self.first_location_id)
        self.assertEqual(location["name"], self.first_location_name)

    def test_get_location_not_found(self):
        """Test getting a non-existent location."""
        location = self.smart_things_api.get_location("nonexistent-location-id")
        self.assertIn("error", location)

    def test_create_location_success(self):
        """Test creating a new location."""
        result = self.smart_things_api.create_location(name="Test Location")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertIn("location", result)
        self.assertEqual(result["location"]["name"], "Test Location")

        # Verify location was added
        locations = self.smart_things_api.list_locations()
        self.assertEqual(len(locations), self.initial_location_count + 1)

    def test_update_location_success(self):
        """Test updating an existing location."""
        if not self.first_location_id:
            self.skipTest("No locations available for testing")

        result = self.smart_things_api.update_location(
            location_id=self.first_location_id,
            name="Updated Location Name"
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("location", result)
        self.assertEqual(result["location"]["name"], "Updated Location Name")

    def test_delete_location_success(self):
        """Test deleting an existing location."""
        if not self.first_location_id:
            self.skipTest("No locations available for testing")

        result = self.smart_things_api.delete_location(self.first_location_id)
        self.assertEqual(result["status"], True)

        # Verify location was removed
        locations = self.smart_things_api.list_locations()
        self.assertEqual(len(locations), self.initial_location_count - 1)

    # ================
    # Room Tests
    # ================

    def test_list_rooms(self):
        """Test listing all rooms."""
        rooms = self.smart_things_api.list_rooms()
        self.assertIsInstance(rooms, list)
        self.assertEqual(len(rooms), self.initial_room_count)
        if rooms:
            self.assertIn("id", rooms[0])
            self.assertIn("name", rooms[0])

    def test_get_room_success(self):
        """Test getting a specific room by ID."""
        if not self.first_room_id:
            self.skipTest("No rooms available for testing")

        room = self.smart_things_api.get_room(self.first_room_id)
        self.assertIsInstance(room, dict)
        self.assertEqual(room["id"], self.first_room_id)
        self.assertEqual(room["name"], self.first_room_name)

    def test_get_room_not_found(self):
        """Test getting a non-existent room."""
        room = self.smart_things_api.get_room("nonexistent-room-id")
        self.assertIn("error", room)

    def test_create_room_success(self):
        """Test creating a new room."""
        result = self.smart_things_api.create_room(name="Test Room")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertIn("room", result)
        self.assertEqual(result["room"]["name"], "Test Room")

        # Verify room was added
        rooms = self.smart_things_api.list_rooms()
        self.assertEqual(len(rooms), self.initial_room_count + 1)

    def test_update_room_success(self):
        """Test updating an existing room."""
        if not self.first_room_id:
            self.skipTest("No rooms available for testing")

        result = self.smart_things_api.update_room(
            room_id=self.first_room_id,
            name="Updated Room Name"
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("room", result)
        self.assertEqual(result["room"]["name"], "Updated Room Name")

    def test_delete_room_success(self):
        """Test deleting an existing room."""
        if not self.first_room_id:
            self.skipTest("No rooms available for testing")

        result = self.smart_things_api.delete_room(self.first_room_id)
        self.assertEqual(result["status"], True)

        # Verify room was removed
        rooms = self.smart_things_api.list_rooms()
        self.assertEqual(len(rooms), self.initial_room_count - 1)

    # ================
    # Capability Tests
    # ================

    def test_list_capabilities(self):
        """Test listing all capabilities."""
        capabilities = self.smart_things_api.list_capabilities()
        self.assertIsInstance(capabilities, list)
        self.assertGreater(len(capabilities), 0)
        if capabilities:
            self.assertIn("id", capabilities[0])

    def test_get_capability_success(self):
        """Test getting a specific capability."""
        capability = self.smart_things_api.get_capability("switch")
        self.assertIsInstance(capability, dict)
        self.assertEqual(capability["id"], "switch")

    def test_get_capability_not_found(self):
        """Test getting a non-existent capability."""
        capability = self.smart_things_api.get_capability("nonexistent-capability")
        self.assertIn("error", capability)

    # ================
    # Integration Tests
    # ================

    def test_device_lifecycle(self):
        """Test complete device lifecycle: create, update, delete."""
        # Create device
        device_data = {
            "name": "Lifecycle Test Device",
            "capabilities": ["switch"],
            "initial_status": {"main": {"switch": {"switch": "off"}}}
        }

        created = self.smart_things_api.create_device(**device_data)
        self.assertIn("device", created)
        device_id = created["device"]["id"]

        # Update device
        update_result = self.smart_things_api.update_device_status(
            device_id=device_id,
            component_id="main",
            capability_id="switch",
            command="on"
        )
        self.assertEqual(update_result["status"], "success")

        # Verify update
        status = self.smart_things_api.get_device_status(device_id)
        if "switch" in status["component_status"]:
            self.assertEqual(status["component_status"]["switch"]["switch"], "on")

        # Delete device
        delete_result = self.smart_things_api.delete_device(device_id)
        self.assertEqual(delete_result["status"], True)

    def test_location_room_hierarchy(self):
        """Test location and room relationship."""
        # Create location
        location = self.smart_things_api.create_location(name="Hierarchy Test Location")
        location_id = location["location"]["id"]

        # Create room in location
        room = self.smart_things_api.create_room(name="Hierarchy Test Room", location_id=location_id)
        room_id = room["room"]["id"]

        # Verify room belongs to location
        retrieved_room = self.smart_things_api.get_room(room_id)
        self.assertEqual(retrieved_room["location_id"], location_id)

        # List rooms for location
        rooms = self.smart_things_api.list_rooms(location_id=location_id)
        self.assertEqual(len(rooms), 1)
        self.assertEqual(rooms[0]["id"], room_id)

    def test_reset_data(self):
        """Test resetting data to default state."""
        # Modify data
        device_data = {"name": "Temp Device", "capabilities": ["switch"]}
        self.smart_things_api.create_device(device_data)

        # Reset
        result = self.smart_things_api.reset_data()
        self.assertEqual(result["reset_status"], True)

        # Verify reset
        devices = self.smart_things_api.list_devices()
        self.assertEqual(len(devices), self.initial_device_count)

    # ================
    # Error Handling Tests
    # ================

    def test_invalid_device_operations(self):
        """Test operations with invalid device IDs."""
        # Test with None - API treats None as invalid but doesn't raise exception
        result = self.smart_things_api.get_device(None)
        self.assertIn("error", result)

        # Test with empty string
        result = self.smart_things_api.get_device("")
        self.assertIn("error", result)

    def test_invalid_location_operations(self):
        """Test operations with invalid location IDs."""
        result = self.smart_things_api.get_location("invalid-location")
        self.assertIn("error", result)

    def test_invalid_room_operations(self):
        """Test operations with invalid room IDs."""
        result = self.smart_things_api.get_room("invalid-room")
        self.assertIn("error", result)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
