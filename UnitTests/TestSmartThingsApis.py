import unittest
from copy import deepcopy
from SmartThingsApis import SmartThingsApis, DEFAULT_STATE

class TestSmartThingsApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh SmartThingsApis instance for each test."""
        self.smartthings_api = SmartThingsApis()
        self.smartthings_api._load_default_state() # Ensure a clean state for each test
        self.loc1_id = "loc1"
        self.loc2_id = "loc2"
        self.device1_id = "device1" # Living Room Light
        self.device2_id = "device2" # Front Door Lock
        self.device3_id = "device3" # Kitchen Thermostat
        self.device4_id = "device4" # Bedroom Fan
        self.device5_id = "device5" # Backyard Camera
        self.room1_id = "room1" # Living Room
        self.scene1_id = "scene1" # Movie Night

    # ================
    # Device Tests
    # ================

    def test_list_devices_no_filters(self):
        """Test listing all devices without any filters."""
        devices = self.smartthings_api.list_devices()
        self.assertIsNotNone(devices)
        self.assertIsInstance(devices, list)
        self.assertEqual(len(devices), 5) # Based on DEFAULT_STATE

    def test_list_devices_by_location(self):
        """Test listing devices filtered by location ID."""
        devices_loc1 = self.smartthings_api.list_devices(location_id=self.loc1_id)
        self.assertIsNotNone(devices_loc1)
        self.assertIsInstance(devices_loc1, list)
        self.assertEqual(len(devices_loc1), 3) # device1, device2, device3 are in loc1
        for device in devices_loc1:
            self.assertEqual(device["location"], self.loc1_id)

    def test_list_devices_by_capability(self):
        """Test listing devices filtered by capability."""
        devices_switch = self.smartthings_api.list_devices(capability="switch")
        self.assertIsNotNone(devices_switch)
        self.assertIsInstance(devices_switch, list)
        self.assertEqual(len(devices_switch), 2) # device1, device4 have 'switch' capability
        self.assertTrue(any(d["id"] == self.device1_id for d in devices_switch))
        self.assertTrue(any(d["id"] == self.device4_id for d in devices_switch))

    def test_list_devices_by_device_ids(self):
        """Test listing devices filtered by a list of device IDs."""
        devices_specific = self.smartthings_api.list_devices(device_id=[self.device1_id, self.device5_id])
        self.assertIsNotNone(devices_specific)
        self.assertIsInstance(devices_specific, list)
        self.assertEqual(len(devices_specific), 2)
        self.assertTrue(any(d["id"] == self.device1_id for d in devices_specific))
        self.assertTrue(any(d["id"] == self.device5_id for d in devices_specific))

    def test_get_device_success(self):
        """Test getting a specific device by ID."""
        device = self.smartthings_api.get_device(self.device1_id)
        self.assertIsNotNone(device)
        self.assertEqual(device["id"], self.device1_id)
        self.assertEqual(device["name"], "Living Room Light")

    def test_get_device_not_found(self):
        """Test getting a non-existent device."""
        device = self.smartthings_api.get_device("nonExistentDevice")
        self.assertIn("error", device)

    def test_get_device_status_success(self):
        """Test getting the status of a device."""
        status = self.smartthings_api.get_device_status(self.device1_id)
        self.assertIsNotNone(status)
        self.assertEqual(status["id"], self.device1_id)
        self.assertIn("components", status)
        self.assertIn("lastUpdated", status)
        self.assertEqual(status["components"]["main"]["switch"]["switch"], "on")

    def test_get_device_status_not_found(self):
        """Test getting the status of a non-existent device."""
        status = self.smartthings_api.get_device_status("nonExistentDevice")
        self.assertIn("error", status)

    def test_execute_device_command_switch_on(self):
        """Test executing a 'switch on' command on a device."""
        commands = [{"component": "main", "capability": "switch", "command": "on"}]
        result = self.smartthings_api.execute_device_command(self.device4_id, commands) # Bedroom Fan is off by default
        self.assertIsNotNone(result)
        self.assertEqual(result["deviceId"], self.device4_id)
        self.assertEqual(result["commandResults"][0]["status"], "success")
        updated_status = self.smartthings_api.get_device_status(self.device4_id)
        self.assertEqual(updated_status["components"]["main"]["switch"]["switch"], "on")

    def test_execute_device_command_set_level(self):
        """Test executing a 'setLevel' command on a device."""
        commands = [{"component": "main", "capability": "level", "command": "setLevel", "arguments": [50]}]
        result = self.smartthings_api.execute_device_command(self.device1_id, commands)
        self.assertIsNotNone(result)
        self.assertEqual(result["deviceId"], self.device1_id)
        self.assertEqual(result["commandResults"][0]["status"], "success")
        updated_status = self.smartthings_api.get_device_status(self.device1_id)
        self.assertEqual(updated_status["components"]["main"]["level"]["level"], 50)

    def test_execute_device_command_lock(self):
        """Test executing a 'lock' command on a device."""
        commands = [{"component": "main", "capability": "lock", "command": "lock"}]
        result = self.smartthings_api.execute_device_command(self.device2_id, commands)
        self.assertIsNotNone(result)
        self.assertEqual(result["deviceId"], self.device2_id)
        self.assertEqual(result["commandResults"][0]["status"], "success")
        updated_status = self.smartthings_api.get_device_status(self.device2_id)
        self.assertEqual(updated_status["components"]["main"]["lock"]["lock"], "locked")

    def test_execute_device_command_device_not_found(self):
        """Test executing commands on a non-existent device."""
        commands = [{"component": "main", "capability": "switch", "command": "on"}]
        result = self.smartthings_api.execute_device_command("nonExistentDevice", commands)
        self.assertIn("error", result)

    def test_get_device_health_success(self):
        """Test getting the health status of a device."""
        health = self.smartthings_api.get_device_health(self.device1_id)
        self.assertIsNotNone(health)
        self.assertEqual(health["id"], self.device1_id)
        self.assertEqual(health["state"], "online")
        self.assertEqual(health["healthStatus"], "GOOD")
        self.assertIn("lastUpdated", health)

    def test_get_device_health_not_found(self):
        """Test getting the health status of a non-existent device."""
        health = self.smartthings_api.get_device_health("nonExistentDevice")
        self.assertIn("error", health)

    def test_get_device_events_success(self):
        """Test getting events for a device."""
        events = self.smartthings_api.get_device_events(self.device1_id)
        self.assertIsNotNone(events)
        self.assertIsInstance(events, list)
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0]["deviceId"], self.device1_id)

    def test_get_device_events_not_found(self):
        """Test getting events for a non-existent device."""
        events = self.smartthings_api.get_device_events("nonExistentDevice")
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 1)
        self.assertIn("error", events[0])

    def test_create_device_success(self):
        """Test creating a new device."""
        initial_device_count = len(self.smartthings_api.devices)
        new_device_data = {
            "name": "New Sensor",
            "location": self.loc1_id,
            "room": self.room1_id,
            "capabilities": ["motionSensor"]
        }
        created_device = self.smartthings_api.create_device(new_device_data)
        self.assertIsNotNone(created_device)
        self.assertIn("id", created_device)
        self.assertEqual(created_device["name"], "New Sensor")
        self.assertEqual(len(self.smartthings_api.devices), initial_device_count + 1)
        self.assertIn(created_device["id"], self.smartthings_api.devices)

    def test_delete_device_success(self):
        """Test deleting an existing device."""
        initial_device_count = len(self.smartthings_api.devices)
        result = self.smartthings_api.delete_device(self.device1_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(self.smartthings_api.devices), initial_device_count - 1)
        self.assertNotIn(self.device1_id, self.smartthings_api.devices)

    def test_delete_device_not_found(self):
        """Test deleting a non-existent device."""
        result = self.smartthings_api.delete_device("nonExistentDevice")
        # Corrected assertion: check for 'error' status instead of key presence
        self.assertEqual(result["status"], "error")

    def test_get_device_component_status_success(self):
        """Test getting the status of a specific device component."""
        status = self.smartthings_api.get_device_component_status(self.device1_id, "main")
        self.assertIsNotNone(status)
        self.assertEqual(status["deviceId"], self.device1_id)
        self.assertEqual(status["componentId"], "main")
        self.assertIn("switch", status["status"])

    def test_get_device_component_status_device_not_found(self):
        """Test getting component status for a non-existent device."""
        status = self.smartthings_api.get_device_component_status("nonExistentDevice", "main")
        self.assertIn("error", status)

    def test_get_device_component_status_component_not_found(self):
        """Test getting a non-existent component's status."""
        status = self.smartthings_api.get_device_component_status(self.device1_id, "nonExistentComponent")
        self.assertIn("error", status)

    # ================
    # Location Tests
    # ================

    def test_list_locations_success(self):
        """Test listing all locations."""
        locations = self.smartthings_api.list_locations()
        self.assertIsNotNone(locations)
        self.assertIsInstance(locations, list)
        self.assertEqual(len(locations), 2) # Based on DEFAULT_STATE

    def test_get_location_success(self):
        """Test getting a specific location by ID."""
        location = self.smartthings_api.get_location(self.loc1_id)
        self.assertIsNotNone(location)
        self.assertEqual(location["id"], self.loc1_id)
        self.assertEqual(location["name"], "Home")

    def test_get_location_not_found(self):
        """Test getting a non-existent location."""
        location = self.smartthings_api.get_location("nonExistentLoc")
        self.assertIn("error", location)

    def test_create_location_success(self):
        """Test creating a new location."""
        initial_location_count = len(self.smartthings_api.locations)
        new_location_data = {
            "name": "Cabin",
            "timezone": "America/Denver",
            "latitude": 39.0,
            "longitude": -105.0
        }
        created_location = self.smartthings_api.create_location(new_location_data)
        self.assertIsNotNone(created_location)
        self.assertIn("id", created_location)
        self.assertEqual(created_location["name"], "Cabin")
        self.assertEqual(len(self.smartthings_api.locations), initial_location_count + 1)
        self.assertIn(created_location["id"], self.smartthings_api.locations)

    def test_update_location_success(self):
        """Test updating an existing location."""
        updated_data = {"name": "My Sweet Home", "timezone": "America/Chicago"}
        updated_location = self.smartthings_api.update_location(self.loc1_id, updated_data)
        self.assertIsNotNone(updated_location)
        self.assertEqual(updated_location["id"], self.loc1_id)
        self.assertEqual(updated_location["name"], "My Sweet Home")
        self.assertEqual(updated_location["timezone"], "America/Chicago")
        self.assertEqual(self.smartthings_api.locations[self.loc1_id]["name"], "My Sweet Home")

    def test_update_location_not_found(self):
        """Test updating a non-existent location."""
        updated_data = {"name": "Non Existent"}
        result = self.smartthings_api.update_location("nonExistentLoc", updated_data)
        self.assertIn("error", result)

    def test_delete_location_success(self):
        """Test deleting an existing location and its associated data."""
        initial_location_count = len(self.smartthings_api.locations)
        initial_room_count = len(self.smartthings_api.rooms)
        initial_scene_count = len(self.smartthings_api.scenes)
        initial_mode_count = len(self.smartthings_api.location_modes[self.loc1_id]) # Modes for loc1

        result = self.smartthings_api.delete_location(self.loc1_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(self.smartthings_api.locations), initial_location_count - 1)
        self.assertNotIn(self.loc1_id, self.smartthings_api.locations)

        # Verify associated rooms, scenes, and modes are deleted
        self.assertEqual(len([r for r in self.smartthings_api.rooms.values() if r.get("locationId") == self.loc1_id]), 0)
        self.assertEqual(len([s for s in self.smartthings_api.scenes.values() if s.get("locationId") == self.loc1_id]), 0)
        self.assertNotIn(self.loc1_id, self.smartthings_api.location_modes)
        self.assertNotIn(self.loc1_id, self.smartthings_api.current_modes)

    def test_delete_location_not_found(self):
        """Test deleting a non-existent location."""
        result = self.smartthings_api.delete_location("nonExistentLoc")
        # Corrected assertion: check for 'error' status instead of key presence
        self.assertEqual(result["status"], "error")

    def test_get_location_modes_success(self):
        """Test getting modes for a specific location."""
        modes = self.smartthings_api.get_location_modes(self.loc1_id)
        self.assertIsNotNone(modes)
        self.assertIsInstance(modes, list)
        self.assertEqual(len(modes), 3) # Based on DEFAULT_STATE

    def test_get_location_modes_not_found(self):
        """Test getting modes for a non-existent location."""
        modes = self.smartthings_api.get_location_modes("nonExistentLoc")
        self.assertIsInstance(modes, list)
        self.assertEqual(len(modes), 0)

    def test_set_location_mode_success(self):
        """Test setting the current mode for a location."""
        result = self.smartthings_api.set_location_mode(self.loc1_id, "mode2") # Set to Away
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.smartthings_api.current_modes[self.loc1_id], "mode2")

    def test_set_location_mode_location_not_found(self):
        """Test setting mode for a non-existent location."""
        result = self.smartthings_api.set_location_mode("nonExistentLoc", "mode1")
        self.assertIn("error", result)

    def test_set_location_mode_mode_not_found(self):
        """Test setting a non-existent mode for a location."""
        result = self.smartthings_api.set_location_mode(self.loc1_id, "nonExistentMode")
        self.assertIn("error", result)

    # ================
    # Room Tests
    # ================

    def test_list_rooms_success(self):
        """Test listing rooms in a specific location."""
        rooms = self.smartthings_api.list_rooms(self.loc1_id)
        self.assertIsNotNone(rooms)
        self.assertIsInstance(rooms, list)
        self.assertEqual(len(rooms), 3) # room1, room2, room3 are in loc1

    def test_list_rooms_location_not_found(self):
        """Test listing rooms for a non-existent location."""
        rooms = self.smartthings_api.list_rooms("nonExistentLoc")
        self.assertIsInstance(rooms, list)
        self.assertEqual(len(rooms), 0)

    def test_get_room_success(self):
        """Test getting a specific room by ID and location."""
        room = self.smartthings_api.get_room(self.loc1_id, self.room1_id)
        self.assertIsNotNone(room)
        self.assertEqual(room["id"], self.room1_id)
        self.assertEqual(room["name"], "Living Room")
        self.assertEqual(room["locationId"], self.loc1_id)

    def test_get_room_not_found(self):
        """Test getting a non-existent room."""
        room = self.smartthings_api.get_room(self.loc1_id, "nonExistentRoom")
        self.assertIn("error", room)

    def test_get_room_wrong_location(self):
        """Test getting a room that exists but belongs to a different location."""
        room = self.smartthings_api.get_room(self.loc1_id, "room4") # room4 is in loc2
        self.assertIn("error", room)

    def test_create_room_success(self):
        """Test creating a new room in a location."""
        initial_room_count = len(self.smartthings_api.rooms)
        new_room_data = {"name": "Dining Room"}
        created_room = self.smartthings_api.create_room(self.loc1_id, new_room_data)
        self.assertIsNotNone(created_room)
        self.assertIn("id", created_room)
        self.assertEqual(created_room["name"], "Dining Room")
        self.assertEqual(created_room["locationId"], self.loc1_id)
        self.assertEqual(len(self.smartthings_api.rooms), initial_room_count + 1)
        self.assertIn(created_room["id"], self.smartthings_api.rooms)

    def test_create_room_location_not_found(self):
        """Test creating a room in a non-existent location."""
        new_room_data = {"name": "Invalid Room"}
        result = self.smartthings_api.create_room("nonExistentLoc", new_room_data)
        self.assertIn("error", result)

    def test_update_room_success(self):
        """Test updating an existing room."""
        updated_data = {"name": "Main Living Area"}
        updated_room = self.smartthings_api.update_room(self.loc1_id, self.room1_id, updated_data)
        self.assertIsNotNone(updated_room)
        self.assertEqual(updated_room["id"], self.room1_id)
        self.assertEqual(updated_room["name"], "Main Living Area")
        self.assertEqual(self.smartthings_api.rooms[self.room1_id]["name"], "Main Living Area")

    def test_update_room_not_found(self):
        """Test updating a non-existent room."""
        updated_data = {"name": "Non Existent"}
        result = self.smartthings_api.update_room(self.loc1_id, "nonExistentRoom", updated_data)
        self.assertIn("error", result)

    def test_update_room_wrong_location(self):
        """Test updating a room that exists but belongs to a different location."""
        updated_data = {"name": "Wrong Location Room"}
        result = self.smartthings_api.update_room(self.loc1_id, "room4", updated_data)
        self.assertIn("error", result)

    def test_delete_room_success(self):
        """Test deleting an existing room and its associated devices."""
        initial_room_count = len(self.smartthings_api.rooms)
        initial_device_count = len(self.smartthings_api.devices)

        # Add a device to room1 specifically for this test
        self.smartthings_api.devices["temp_device"] = {
            "id": "temp_device", "name": "Temp Light", "location": self.loc1_id, "room": self.room1_id, "status": "online"
        }
        self.assertEqual(len(self.smartthings_api.devices), initial_device_count + 1)

        result = self.smartthings_api.delete_room(self.loc1_id, self.room1_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(self.smartthings_api.rooms), initial_room_count - 1)
        self.assertNotIn(self.room1_id, self.smartthings_api.rooms)

        # Verify associated devices are deleted
        self.assertNotIn("temp_device", self.smartthings_api.devices)
        self.assertFalse(any(d.get("room") == self.room1_id for d in self.smartthings_api.devices.values()))


    def test_delete_room_not_found(self):
        """Test deleting a non-existent room."""
        result = self.smartthings_api.delete_room(self.loc1_id, "nonExistentRoom")
        # Corrected assertion: check for 'error' status instead of key presence
        self.assertEqual(result["status"], "error")

    def test_delete_room_wrong_location(self):
        """Test deleting a room that exists but belongs to a different location."""
        result = self.smartthings_api.delete_room(self.loc1_id, "room4")
        # Corrected assertion: check for 'error' status instead of key presence
        self.assertEqual(result["status"], "error")

    # ================
    # Scene Tests
    # ================

    def test_list_scenes_success(self):
        """Test listing scenes in a specific location."""
        scenes = self.smartthings_api.list_scenes(self.loc1_id)
        self.assertIsNotNone(scenes)
        self.assertIsInstance(scenes, list)
        self.assertEqual(len(scenes), 2) # scene1, scene2 are in loc1

    def test_list_scenes_location_not_found(self):
        """Test listing scenes for a non-existent location."""
        scenes = self.smartthings_api.list_scenes("nonExistentLoc")
        self.assertIsInstance(scenes, list)
        self.assertEqual(len(scenes), 0)

    def test_execute_scene_success(self):
        """Test executing a scene."""
        # Ensure device1 is on before executing scene1 (which turns it off)
        self.smartthings_api.execute_device_command(self.device1_id, [{"component": "main", "capability": "switch", "command": "on"}])
        self.assertEqual(self.smartthings_api.get_device_status(self.device1_id)["components"]["main"]["switch"]["switch"], "on")

        result = self.smartthings_api.execute_scene(self.loc1_id, self.scene1_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "executed")
        self.assertEqual(result["locationId"], self.loc1_id)
        self.assertEqual(result["sceneId"], self.scene1_id)
        self.assertGreater(len(result["executedActions"]), 0)

        # Verify device state changed as per scene action
        updated_status = self.smartthings_api.get_device_status(self.device1_id)
        self.assertEqual(updated_status["components"]["main"]["switch"]["switch"], "off")

    def test_execute_scene_not_found(self):
        """Test executing a non-existent scene."""
        result = self.smartthings_api.execute_scene(self.loc1_id, "nonExistentScene")
        self.assertIn("error", result)

    def test_execute_scene_wrong_location(self):
        """Test executing a scene that exists but belongs to a different location."""
        result = self.smartthings_api.execute_scene(self.loc1_id, "scene3") # scene3 is in loc2
        self.assertIn("error", result)

    def test_get_scene_success(self):
        """Test getting a specific scene by ID and location."""
        scene = self.smartthings_api.get_scene(self.loc1_id, self.scene1_id)
        self.assertIsNotNone(scene)
        self.assertEqual(scene["id"], self.scene1_id)
        self.assertEqual(scene["name"], "Movie Night")
        self.assertEqual(scene["locationId"], self.loc1_id)

    def test_get_scene_not_found(self):
        """Test getting a non-existent scene."""
        scene = self.smartthings_api.get_scene(self.loc1_id, "nonExistentScene")
        self.assertIn("error", scene)

    def test_get_scene_wrong_location(self):
        """Test getting a scene that exists but belongs to a different location."""
        scene = self.smartthings_api.get_scene(self.loc1_id, "scene3") # scene3 is in loc2
        self.assertIn("error", scene)

    def test_create_scene_success(self):
        """Test creating a new scene in a location."""
        initial_scene_count = len(self.smartthings_api.scenes)
        new_scene_data = {
            "name": "Evening Ambiance",
            "actions": [{"device": self.device1_id, "command": "setLevel", "level": 30}]
        }
        created_scene = self.smartthings_api.create_scene(self.loc1_id, new_scene_data)
        self.assertIsNotNone(created_scene)
        self.assertIn("id", created_scene)
        self.assertEqual(created_scene["name"], "Evening Ambiance")
        self.assertEqual(created_scene["locationId"], self.loc1_id)
        self.assertEqual(len(self.smartthings_api.scenes), initial_scene_count + 1)
        self.assertIn(created_scene["id"], self.smartthings_api.scenes)

    def test_create_scene_location_not_found(self):
        """Test creating a scene in a non-existent location."""
        new_scene_data = {"name": "Invalid Scene"}
        result = self.smartthings_api.create_scene("nonExistentLoc", new_scene_data)
        self.assertIn("error", result)

    def test_update_scene_success(self):
        """Test updating an existing scene."""
        updated_data = {"name": "Late Night Chill"}
        updated_scene = self.smartthings_api.update_scene(self.loc1_id, self.scene1_id, updated_data)
        self.assertIsNotNone(updated_scene)
        self.assertEqual(updated_scene["id"], self.scene1_id)
        self.assertEqual(updated_scene["name"], "Late Night Chill")
        self.assertEqual(self.smartthings_api.scenes[self.scene1_id]["name"], "Late Night Chill")

    def test_update_scene_not_found(self):
        """Test updating a non-existent scene."""
        updated_data = {"name": "Non Existent"}
        result = self.smartthings_api.update_scene(self.loc1_id, "nonExistentScene", updated_data)
        self.assertIn("error", result)

    def test_update_scene_wrong_location(self):
        """Test updating a scene that exists but belongs to a different location."""
        updated_data = {"name": "Wrong Location Scene"}
        result = self.smartthings_api.update_scene(self.loc1_id, "scene3", updated_data)
        self.assertIn("error", result)

    def test_delete_scene_success(self):
        """Test deleting an existing scene."""
        initial_scene_count = len(self.smartthings_api.scenes)
        result = self.smartthings_api.delete_scene(self.loc1_id, self.scene1_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(self.smartthings_api.scenes), initial_scene_count - 1)
        self.assertNotIn(self.scene1_id, self.smartthings_api.scenes)

    def test_delete_scene_not_found(self):
        """Test deleting a non-existent scene."""
        result = self.smartthings_api.delete_scene(self.loc1_id, "nonExistentScene")
        # Corrected assertion: check for 'error' status instead of key presence
        self.assertEqual(result["status"], "error")

    def test_delete_scene_wrong_location(self):
        """Test deleting a scene that exists but belongs to a different location."""
        result = self.smartthings_api.delete_scene(self.loc1_id, "scene3")
        # Corrected assertion: check for 'error' status instead of key presence
        self.assertEqual(result["status"], "error")

    # ================
    # Capability Tests
    # ================

    def test_list_capabilities_success(self):
        """Test listing all capabilities."""
        capabilities = self.smartthings_api.list_capabilities()
        self.assertIsNotNone(capabilities)
        self.assertIsInstance(capabilities, list)
        self.assertGreater(len(capabilities), 0)

    def test_get_capability_success(self):
        """Test getting a specific capability."""
        capability = self.smartthings_api.get_capability("switch")
        self.assertIsNotNone(capability)
        self.assertEqual(capability["id"], "switch")
        self.assertEqual(capability["version"], 1)

    def test_get_capability_with_version_success(self):
        """Test getting a specific capability with a version."""
        capability = self.smartthings_api.get_capability("switch", version=1)
        self.assertIsNotNone(capability)
        self.assertEqual(capability["id"], "switch")
        self.assertEqual(capability["version"], 1)

    def test_get_capability_not_found(self):
        """Test getting a non-existent capability."""
        capability = self.smartthings_api.get_capability("nonExistentCapability")
        self.assertIn("error", capability)

    def test_get_capability_wrong_version(self):
        """Test getting a capability with a wrong version."""
        capability = self.smartthings_api.get_capability("switch", version=99)
        self.assertIn("error", capability)

    # ================
    # Combined Functionality Tests
    # ================

    def test_device_creation_command_and_deletion_flow(self):
        """Test the flow of creating a device, commanding it, and then deleting it."""
        initial_device_count = len(self.smartthings_api.devices)
        new_device_data = {
            "name": "Flow Test Light",
            "location": self.loc1_id,
            "room": self.room1_id,
            "capabilities": ["switch"],
            # Add default components for the switch capability to ensure it's commandable
            "components": {
                "main": {
                    "switch": {"switch": "off"} # Start off to test turning on
                }
            }
        }
        created_device = self.smartthings_api.create_device(new_device_data)
        self.assertIsNotNone(created_device)
        self.assertEqual(len(self.smartthings_api.devices), initial_device_count + 1)

        # Command the new device
        commands = [{"component": "main", "capability": "switch", "command": "on"}]
        command_result = self.smartthings_api.execute_device_command(created_device["id"], commands)
        self.assertIsNotNone(command_result)
        self.assertEqual(command_result["commandResults"][0]["status"], "success")
        updated_status = self.smartthings_api.get_device_status(created_device["id"])
        self.assertEqual(updated_status["components"]["main"]["switch"]["switch"], "on")

        # Delete the device
        delete_result = self.smartthings_api.delete_device(created_device["id"])
        self.assertIsNotNone(delete_result)
        self.assertEqual(delete_result["status"], "success")
        self.assertEqual(len(self.smartthings_api.devices), initial_device_count)
        self.assertNotIn(created_device["id"], self.smartthings_api.devices)

    def test_location_room_scene_flow(self):
        """Test the flow of creating a location, adding a room and scene, then deleting the location."""
        initial_location_count = len(self.smartthings_api.locations)
        initial_room_count = len(self.smartthings_api.rooms)
        initial_scene_count = len(self.smartthings_api.scenes)

        # Create a new location
        new_loc_data = {"name": "Vacation Home", "timezone": "Europe/Paris"}
        created_loc = self.smartthings_api.create_location(new_loc_data)
        self.assertIsNotNone(created_loc)
        self.assertEqual(len(self.smartthings_api.locations), initial_location_count + 1)

        # Create a room in the new location
        new_room_data = {"name": "Guest Bedroom"}
        created_room = self.smartthings_api.create_room(created_loc["id"], new_room_data)
        self.assertIsNotNone(created_room)
        self.assertEqual(len(self.smartthings_api.rooms), initial_room_count + 1)
        self.assertEqual(created_room["locationId"], created_loc["id"])

        # Create a scene in the new location
        new_scene_data = {"name": "Good Night", "actions": []}
        created_scene = self.smartthings_api.create_scene(created_loc["id"], new_scene_data)
        self.assertIsNotNone(created_scene)
        self.assertEqual(len(self.smartthings_api.scenes), initial_scene_count + 1)
        self.assertEqual(created_scene["locationId"], created_loc["id"])

        # Verify items exist
        self.assertIsNotNone(self.smartthings_api.get_location(created_loc["id"]))
        self.assertIsNotNone(self.smartthings_api.get_room(created_loc["id"], created_room["id"]))
        self.assertIsNotNone(self.smartthings_api.get_scene(created_loc["id"], created_scene["id"]))

        # Delete the location (should cascade delete rooms and scenes)
        delete_result = self.smartthings_api.delete_location(created_loc["id"])
        self.assertIsNotNone(delete_result)
        self.assertEqual(delete_result["status"], "success")
        self.assertEqual(len(self.smartthings_api.locations), initial_location_count)

    def test_device_status_and_health_check_flow(self):
        """Test getting device status, then health, and ensuring consistency."""
        # Get initial status
        initial_status = self.smartthings_api.get_device_status(self.device1_id)
        self.assertIsNotNone(initial_status)
        self.assertIn("components", initial_status)

        # Get health
        health = self.smartthings_api.get_device_health(self.device1_id)
        self.assertIsNotNone(health)
        self.assertEqual(health["id"], self.device1_id)
        # Removed the incorrect assertion: self.assertEqual(health["state"], initial_status["components"]["main"]["switch"]["switch"])
        self.assertEqual(health["state"], "online") # health["state"] refers to device connectivity
        self.assertEqual(health["healthStatus"], "GOOD")

        # Change device state and re-check
        self.smartthings_api.execute_device_command(self.device1_id, [{"component": "main", "capability": "switch", "command": "off"}])
        updated_status = self.smartthings_api.get_device_status(self.device1_id)
        updated_health = self.smartthings_api.get_device_health(self.device1_id)

        self.assertEqual(updated_status["components"]["main"]["switch"]["switch"], "off")
        self.assertEqual(updated_health["state"], "online") # Status remains online even if switch is off
        self.assertEqual(updated_health["healthStatus"], "GOOD")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
