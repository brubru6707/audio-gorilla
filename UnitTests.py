import unittest
import time
import uuid
from SlackApis import SlackAPI
from WalmartMarketplaceApis import WalmartMarketplaceAPI
from SmartHomeApis import SmartHomeAPI, ControllerAPI, ColorControl, Lock, LockCodes, MediaPlayback, Switch, SwitchLevel, ThermostatCoolingSetpoint, ThermostatFanMode
from NetflixApis import NetflixAPI

class TestSlackAPI(unittest.TestCase):
    def setUp(self):
        self.api = SlackAPI()

    def test_chat_postMessage_and_history(self):
        channel = "C001"
        text = "Hello, Slack!"
        resp = self.api.chat_postMessage(channel, text)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["channel"], channel)
        self.assertEqual(resp["message"]["text"], text)
        # Check message in history
        history = self.api.conversations_history(channel)
        self.assertTrue(any(msg["text"] == text for msg in history["messages"]))

    def test_chat_update(self):
        channel = "C001"
        text = "Original"
        new_text = "Updated"
        resp = self.api.chat_postMessage(channel, text)
        ts = resp["ts"]
        update_resp = self.api.chat_update(channel, ts, new_text)
        self.assertTrue(update_resp["ok"])
        self.assertEqual(update_resp["message"]["text"], new_text)

    def test_chat_delete(self):
        channel = "C001"
        text = "To be deleted"
        resp = self.api.chat_postMessage(channel, text)
        ts = resp["ts"]
        del_resp = self.api.chat_delete(channel, ts)
        self.assertTrue(del_resp["ok"])
        # Should not be in history
        history = self.api.conversations_history(channel)
        self.assertFalse(any(msg["ts"] == ts for msg in history["messages"]))

    def test_conversations_create_and_rename(self):
        name = "testchannel"
        create_resp = self.api.conversations_create(name)
        self.assertTrue(create_resp["ok"])
        channel_id = create_resp["channel"]["id"]
        new_name = "renamed"
        rename_resp = self.api.conversations_rename(channel_id, new_name)
        self.assertTrue(rename_resp["ok"])
        self.assertEqual(rename_resp["channel"]["name"], new_name)

    def test_users_info_and_list(self):
        users = self.api.users_list()
        self.assertTrue(users["ok"])
        user_id = users["members"][0]["id"]
        info = self.api.users_info(user_id)
        self.assertTrue(info["ok"])
        self.assertEqual(info["user"]["id"], user_id)

    def test_reminders_add_and_complete(self):
        text = "Test reminder"
        when = int(time.time()) + 60
        add_resp = self.api.reminders_add(text, when)
        self.assertTrue(add_resp["ok"])
        reminder_id = add_resp["reminder"]["id"]
        complete_resp = self.api.reminders_complete(reminder_id)
        self.assertTrue(complete_resp["ok"])
        info = self.api.reminders_info(reminder_id)
        self.assertTrue(info["reminder"].get("completed", False))

    def test_files_upload_and_list(self):
        file_content = b"hello world"
        filename = "test.txt"
        upload_resp = self.api.files_upload(file_content, filename=filename)
        self.assertTrue(upload_resp["ok"])
        file_id = upload_resp["file"]["id"]
        files = self.api.files_list()
        self.assertTrue(any(f["id"] == file_id for f in files["files"]))

    def test_reactions_add_and_remove(self):
        channel = "C001"
        text = "React to me"
        resp = self.api.chat_postMessage(channel, text)
        ts = resp["ts"]
        add_resp = self.api.reactions_add("smile", channel, ts)
        self.assertTrue(add_resp["ok"])
        get_resp = self.api.reactions_get(channel, ts)
        self.assertTrue(get_resp["ok"])
        self.assertTrue(any(r["name"] == "smile" for r in get_resp["message"]["reactions"]))
        remove_resp = self.api.reactions_remove("smile", channel, ts)
        self.assertTrue(remove_resp["ok"])

    # Edge cases for Slack API
    def test_chat_update_nonexistent_message(self):
        """Test updating a message that doesn't exist"""
        resp = self.api.chat_update("C001", "9999999999.999999", "New text")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "message_not_found")

    def test_chat_delete_nonexistent_message(self):
        """Test deleting a message that doesn't exist"""
        resp = self.api.chat_delete("C001", "9999999999.999999")
        self.assertTrue(resp["ok"])  # Should still return ok even if message doesn't exist

    def test_users_info_nonexistent_user(self):
        """Test getting info for a user that doesn't exist"""
        resp = self.api.users_info("U999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "user_not_found")

    def test_reminders_complete_nonexistent_reminder(self):
        """Test completing a reminder that doesn't exist"""
        resp = self.api.reminders_complete("nonexistent_reminder")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "reminder_not_found")

    def test_files_info_nonexistent_file(self):
        """Test getting info for a file that doesn't exist"""
        resp = self.api.files_info("F999")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "file_not_found")

    def test_conversations_rename_nonexistent_channel(self):
        """Test renaming a channel that doesn't exist"""
        resp = self.api.conversations_rename("C999", "new_name")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "channel_not_found")

    def test_empty_message_text(self):
        """Test posting a message with empty text"""
        resp = self.api.chat_postMessage("C001", "")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["message"]["text"], "")

    def test_very_long_message_text(self):
        """Test posting a message with very long text"""
        long_text = "A" * 10000
        resp = self.api.chat_postMessage("C001", long_text)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["message"]["text"], long_text)

    def test_thread_replies(self):
        """Test thread functionality"""
        # Post parent message
        parent_resp = self.api.chat_postMessage("C001", "Parent message")
        parent_ts = parent_resp["ts"]
        
        # Post reply in thread
        reply_resp = self.api.chat_postMessage("C001", "Thread reply", thread_ts=parent_ts)
        self.assertTrue(reply_resp["ok"])
        
        # Get thread replies
        thread_resp = self.api.conversations_replies("C001", parent_ts)
        self.assertTrue(thread_resp["ok"])
        self.assertEqual(len(thread_resp["messages"]), 2)  # Parent + reply

    def test_multiple_reactions_same_message(self):
        """Test adding multiple reactions to the same message"""
        resp = self.api.chat_postMessage("C001", "Multi-reaction message")
        ts = resp["ts"]
        
        # Add multiple reactions
        self.api.reactions_add("smile", "C001", ts)
        self.api.reactions_add("thumbsup", "C001", ts)
        self.api.reactions_add("heart", "C001", ts)
        
        get_resp = self.api.reactions_get("C001", ts)
        self.assertTrue(get_resp["ok"])
        self.assertEqual(len(get_resp["message"]["reactions"]), 3)

    def test_pagination_limits(self):
        """Test pagination with various limits"""
        # Test with limit 0
        resp = self.api.conversations_list(limit=0)
        self.assertTrue(resp["ok"])
        self.assertEqual(len(resp["channels"]), 0)
        
        # Test with very large limit
        resp = self.api.conversations_list(limit=10000)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["channels"]), 10000)

class TestWalmartMarketplaceAPI(unittest.TestCase):
    def setUp(self):
        self.api = WalmartMarketplaceAPI()

    def test_get_items_and_get_item(self):
        items = self.api.get_items()
        self.assertIn("items", items)
        sku = items["items"][0]["sku"]
        item = self.api.get_item(sku)
        self.assertEqual(item["sku"], sku)

    def test_update_and_retire_item(self):
        sku = "SKU001"
        update_resp = self.api.update_item(sku, {"product_name": "Updated Name", "price": 99.99})
        self.assertEqual(update_resp["status"], "success")
        item = self.api.get_item(sku)
        self.assertEqual(item["product_name"], "Updated Name")
        self.assertEqual(item["price"], 99.99)
        retire_resp = self.api.retire_item(sku)
        self.assertEqual(retire_resp["status"], "success")
        item = self.api.get_item(sku)
        self.assertEqual(item["status"], "Retired")

    def test_inventory_update_and_get(self):
        sku = "SKU001"
        resp = self.api.update_inventory(sku, 42, "FC001")
        self.assertEqual(resp["status"], "success")
        inv = self.api.get_inventory(sku)
        self.assertEqual(inv["quantity"], 42)
        self.assertEqual(inv["fulfillment_center_id"], "FC001")

    def test_order_acknowledge_and_ship(self):
        po_id = "PO001"
        ack_resp = self.api.acknowledge_order(po_id, {"ack": True})
        self.assertEqual(ack_resp["status"], "success")
        order = self.api.get_order(po_id)
        self.assertEqual(order["status"], "Acknowledged")
        ship_resp = self.api.ship_order(po_id, {"carrier": "UPS", "tracking": "123"})
        self.assertEqual(ship_resp["status"], "success")
        order = self.api.get_order(po_id)
        self.assertEqual(order["status"], "Shipped")

    def test_create_and_update_promotion(self):
        promo_payload = {"name": "Test Promo", "discount_percent": 10, "start_date": "2024-01-01", "end_date": "2024-12-31"}
        create_resp = self.api.create_promotion(promo_payload)
        self.assertEqual(create_resp["status"], "success")
        promo_id = create_resp["promo_id"]
        update_resp = self.api.update_promotion(promo_id, {"discount_percent": 20})
        self.assertEqual(update_resp["status"], "success")
        promo = self.api.get_promotion(promo_id)
        self.assertEqual(promo["discount_percent"], 20)

    def test_bulk_item_upload_and_status(self):
        file_content = b"<xml>bulk</xml>"
        resp = self.api.bulk_item_upload(file_content, "xml")
        self.assertIn("feed_id", resp)
        feed_id = resp["feed_id"]
        status = self.api.get_bulk_item_status(feed_id)
        self.assertEqual(status["status"], "Completed")

    # Edge cases for Walmart Marketplace API
    def test_update_nonexistent_item(self):
        """Test updating an item that doesn't exist"""
        resp = self.api.update_item("NONEXISTENT_SKU", {"product_name": "Test"})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_retire_nonexistent_item(self):
        """Test retiring an item that doesn't exist"""
        resp = self.api.retire_item("NONEXISTENT_SKU")
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_inventory_nonexistent_sku(self):
        """Test getting inventory for a SKU that doesn't exist"""
        resp = self.api.get_inventory("NONEXISTENT_SKU")
        self.assertIn("error", resp)
        self.assertEqual(resp["sku"], "NONEXISTENT_SKU")

    def test_update_inventory_nonexistent_sku(self):
        """Test updating inventory for a SKU that doesn't exist"""
        resp = self.api.update_inventory("NONEXISTENT_SKU", 100)
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_order_nonexistent_order(self):
        """Test getting an order that doesn't exist"""
        resp = self.api.get_order("NONEXISTENT_PO")
        self.assertIn("error", resp)
        self.assertEqual(resp["purchase_order_id"], "NONEXISTENT_PO")

    def test_acknowledge_nonexistent_order(self):
        """Test acknowledging an order that doesn't exist"""
        resp = self.api.acknowledge_order("NONEXISTENT_PO", {"ack": True})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_ship_nonexistent_order(self):
        """Test shipping an order that doesn't exist"""
        resp = self.api.ship_order("NONEXISTENT_PO", {"carrier": "UPS"})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_cancel_shipped_order(self):
        """Test cancelling an order that's already shipped"""
        po_id = "PO001"
        # First ship the order
        self.api.ship_order(po_id, {"carrier": "UPS", "tracking": "123"})
        # Try to cancel it
        resp = self.api.cancel_order(po_id, {"reason": "Customer request"})
        self.assertEqual(resp["status"], "error")
        self.assertIn("cannot be cancelled", resp["errors"][0])

    def test_refund_unshipped_order(self):
        """Test refunding an order that hasn't been shipped"""
        po_id = "PO001"
        resp = self.api.refund_order(po_id, {"amount": 50.00})
        self.assertEqual(resp["status"], "error")
        self.assertIn("cannot be refunded", resp["errors"][0])

    def test_promotion_nonexistent(self):
        """Test getting a promotion that doesn't exist"""
        resp = self.api.get_promotion("NONEXISTENT_PROMO")
        self.assertIn("error", resp)
        self.assertEqual(resp["promo_id"], "NONEXISTENT_PROMO")

    def test_update_nonexistent_promotion(self):
        """Test updating a promotion that doesn't exist"""
        resp = self.api.update_promotion("NONEXISTENT_PROMO", {"discount_percent": 25})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_bulk_status_nonexistent_feed(self):
        """Test getting status for a feed that doesn't exist"""
        resp = self.api.get_bulk_item_status("NONEXISTENT_FEED")
        self.assertIn("error", resp)
        self.assertEqual(resp["feed_id"], "NONEXISTENT_FEED")

    def test_zero_quantity_inventory(self):
        """Test setting inventory quantity to zero"""
        sku = "SKU001"
        resp = self.api.update_inventory(sku, 0)
        self.assertEqual(resp["status"], "success")
        inv = self.api.get_inventory(sku)
        self.assertEqual(inv["quantity"], 0)

    def test_negative_quantity_inventory(self):
        """Test setting negative inventory quantity"""
        sku = "SKU001"
        resp = self.api.update_inventory(sku, -10)
        self.assertEqual(resp["status"], "success")  # API allows negative quantities
        inv = self.api.get_inventory(sku)
        self.assertEqual(inv["quantity"], -10)

    def test_very_high_price(self):
        """Test setting a very high price"""
        sku = "SKU001"
        high_price = 999999.99
        resp = self.api.update_price(sku, {"price": high_price})
        self.assertEqual(resp["status"], "success")
        price_info = self.api.get_price(sku)
        self.assertEqual(price_info["price"], high_price)

    def test_zero_price(self):
        """Test setting price to zero"""
        sku = "SKU001"
        resp = self.api.update_price(sku, {"price": 0})
        self.assertEqual(resp["status"], "success")
        price_info = self.api.get_price(sku)
        self.assertEqual(price_info["price"], 0)

    def test_empty_file_upload(self):
        """Test uploading an empty file"""
        resp = self.api.bulk_item_upload(b"", "xml")
        self.assertIn("feed_id", resp)
        self.assertEqual(resp["status"], "Submitted")

    def test_large_file_upload(self):
        """Test uploading a large file"""
        large_content = b"x" * 1000000  # 1MB
        resp = self.api.bulk_item_upload(large_content, "xml")
        self.assertIn("feed_id", resp)
        self.assertEqual(resp["status"], "Submitted")

class TestSmartHomeAPI(unittest.TestCase):
    def setUp(self):
        self.api = SmartHomeAPI()

    def test_switch_on_off(self):
        sw = self.api.switch
        self.assertTrue(sw.on())
        self.assertEqual(sw.current_switch_state, "on")
        self.assertTrue(sw.off())
        self.assertEqual(sw.current_switch_state, "off")

    def test_switch_level(self):
        sl = self.api.switch_level
        self.assertTrue(sl.setLevel(55))
        self.assertEqual(sl.current_level, 55)

    def test_color_control(self):
        cc = self.api.color_control
        self.assertTrue(cc.setColor(120, 80))
        self.assertEqual(cc.current_color, {"hue": 120, "saturation": 80})
        self.assertTrue(cc.setHue(200))
        self.assertEqual(cc.current_color["hue"], 200)
        self.assertTrue(cc.setSaturation(60))
        self.assertEqual(cc.current_color["saturation"], 60)

    def test_lock_and_lockcodes(self):
        lock = self.api.lock
        self.assertTrue(lock.lock())
        self.assertEqual(lock.current_lock_state, "locked")
        self.assertTrue(lock.unlock())
        self.assertEqual(lock.current_lock_state, "unlocked")
        codes = self.api.lock_codes
        self.assertTrue(codes.setCode("1", "1234", "Front Door"))
        self.assertEqual(codes.requestCode("1"), {"pin": "1234", "name": "Front Door"})
        self.assertTrue(codes.deleteCode("1"))
        self.assertEqual(codes.requestCode("1"), "")

    def test_thermostat(self):
        cool = self.api.thermostat_cooling_setpoint
        self.assertTrue(cool.setCoolingSetpoint(72))
        self.assertEqual(cool.current_cooling_setpoint, 72)
        fan = self.api.thermostat_fan_mode
        self.assertTrue(fan.fanAuto())
        self.assertEqual(fan.current_fan_mode, "auto")
        self.assertTrue(fan.fanOn())
        self.assertEqual(fan.current_fan_mode, "on")
        self.assertTrue(fan.setThermostatFanMode("circulate"))
        self.assertEqual(fan.current_fan_mode, "circulate")

    def test_media_playback(self):
        mp = self.api.media_playback
        self.assertTrue(mp.fastForward())
        self.assertEqual(mp.current_media_state, "fast_forward")
        self.assertTrue(mp.pause())
        self.assertEqual(mp.current_media_state, "paused")
        self.assertTrue(mp.stop())
        self.assertEqual(mp.current_media_state, "stopped")

    # Edge cases for Smart Home API
    def test_switch_level_boundary_values(self):
        """Test switch level with boundary values"""
        sl = self.api.switch_level
        
        # Test minimum value (0)
        self.assertTrue(sl.setLevel(0))
        self.assertEqual(sl.current_level, 0)
        
        # Test maximum value (100)
        self.assertTrue(sl.setLevel(100))
        self.assertEqual(sl.current_level, 100)
        
        # Test negative value
        self.assertTrue(sl.setLevel(-10))
        self.assertEqual(sl.current_level, -10)
        
        # Test very high value
        self.assertTrue(sl.setLevel(1000))
        self.assertEqual(sl.current_level, 1000)

    def test_color_control_boundary_values(self):
        """Test color control with boundary values"""
        cc = self.api.color_control
        
        # Test minimum values
        self.assertTrue(cc.setColor(0, 0))
        self.assertEqual(cc.current_color, {"hue": 0, "saturation": 0})
        
        # Test maximum values
        self.assertTrue(cc.setColor(360, 100))
        self.assertEqual(cc.current_color, {"hue": 360, "saturation": 100})
        
        # Test negative values
        self.assertTrue(cc.setColor(-50, -25))
        self.assertEqual(cc.current_color, {"hue": -50, "saturation": -25})
        
        # Test very high values
        self.assertTrue(cc.setColor(1000, 200))
        self.assertEqual(cc.current_color, {"hue": 1000, "saturation": 200})

    def test_lock_codes_edge_cases(self):
        """Test lock codes with edge cases"""
        codes = self.api.lock_codes
        
        # Test empty code
        self.assertTrue(codes.setCode("1", "", "Empty Code"))
        self.assertEqual(codes.requestCode("1"), {"pin": "", "name": "Empty Code"})
        
        # Test very long code
        long_code = "1" * 100
        self.assertTrue(codes.setCode("2", long_code, "Long Code"))
        self.assertEqual(codes.requestCode("2"), {"pin": long_code, "name": "Long Code"})
        
        # Test special characters in code
        special_code = "!@#$%^&*()"
        self.assertTrue(codes.setCode("3", special_code, "Special Code"))
        self.assertEqual(codes.requestCode("3"), {"pin": special_code, "name": "Special Code"})
        
        # Test empty name
        self.assertTrue(codes.setCode("4", "1234", ""))
        self.assertEqual(codes.requestCode("4"), {"pin": "1234", "name": ""})
        
        # Test deleting non-existent code
        self.assertTrue(codes.deleteCode("999"))
        
        # Test requesting non-existent code
        self.assertEqual(codes.requestCode("999"), "")

    def test_thermostat_boundary_values(self):
        """Test thermostat with boundary values"""
        cool = self.api.thermostat_cooling_setpoint
        
        # Test very low temperature
        self.assertTrue(cool.setCoolingSetpoint(-50))
        self.assertEqual(cool.current_cooling_setpoint, -50)
        
        # Test very high temperature
        self.assertTrue(cool.setCoolingSetpoint(150))
        self.assertEqual(cool.current_cooling_setpoint, 150)
        
        # Test zero temperature
        self.assertTrue(cool.setCoolingSetpoint(0))
        self.assertEqual(cool.current_cooling_setpoint, 0)

    def test_thermostat_fan_mode_edge_cases(self):
        """Test thermostat fan mode with edge cases"""
        fan = self.api.thermostat_fan_mode
        
        # Test invalid fan mode
        self.assertTrue(fan.setThermostatFanMode("invalid_mode"))
        self.assertEqual(fan.current_fan_mode, "invalid_mode")
        
        # Test empty fan mode
        self.assertTrue(fan.setThermostatFanMode(""))
        self.assertEqual(fan.current_fan_mode, "")
        
        # Test very long fan mode
        long_mode = "very_long_fan_mode_name_that_exceeds_normal_length"
        self.assertTrue(fan.setThermostatFanMode(long_mode))
        self.assertEqual(fan.current_fan_mode, long_mode)

    def test_media_playback_state_transitions(self):
        """Test media playback state transitions"""
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

    def test_lock_state_transitions(self):
        """Test lock state transitions"""
        lock = self.api.lock
        
        # Test multiple lock/unlock cycles
        for i in range(5):
            self.assertTrue(lock.lock())
            self.assertEqual(lock.current_lock_state, "locked")
            self.assertTrue(lock.unlock())
            self.assertEqual(lock.current_lock_state, "unlocked")

    def test_switch_state_transitions(self):
        """Test switch state transitions"""
        sw = self.api.switch
        
        # Test multiple on/off cycles
        for i in range(5):
            self.assertTrue(sw.on())
            self.assertEqual(sw.current_switch_state, "on")
            self.assertTrue(sw.off())
            self.assertEqual(sw.current_switch_state, "off")

    def test_concurrent_operations(self):
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

class TestNetflixAPI(unittest.TestCase):
    def setUp(self):
        self.api = NetflixAPI()

    def test_profiles_list_and_get(self):
        """Test listing profiles and getting specific profile info"""
        profiles = self.api.profiles_list()
        self.assertTrue(profiles["ok"])
        self.assertIn("profiles", profiles)
        
        profile_id = profiles["profiles"][0]["id"]
        profile = self.api.profiles_get(profile_id)
        self.assertTrue(profile["ok"])
        self.assertEqual(profile["profile"]["id"], profile_id)

    def test_profiles_create_and_update(self):
        """Test creating and updating profiles"""
        create_resp = self.api.profiles_create("Test Profile", maturity_level="teen", autoplay=False)
        self.assertTrue(create_resp["ok"])
        profile_id = create_resp["profile"]["id"]
        self.assertEqual(create_resp["profile"]["name"], "Test Profile")
        self.assertEqual(create_resp["profile"]["maturity_level"], "teen")
        self.assertFalse(create_resp["profile"]["autoplay"])
        
        # Update the profile
        update_resp = self.api.profiles_update(profile_id, name="Updated Profile", language="es")
        self.assertTrue(update_resp["ok"])
        self.assertEqual(update_resp["profile"]["name"], "Updated Profile")
        self.assertEqual(update_resp["profile"]["language"], "es")

    def test_profiles_delete(self):
        """Test deleting a profile"""
        # Create a profile first
        create_resp = self.api.profiles_create("To Delete")
        profile_id = create_resp["profile"]["id"]
        
        # Delete it
        delete_resp = self.api.profiles_delete(profile_id)
        self.assertTrue(delete_resp["ok"])
        
        # Verify it's gone
        get_resp = self.api.profiles_get(profile_id)
        self.assertFalse(get_resp["ok"])
        self.assertEqual(get_resp["error"], "profile_not_found")

    def test_watchlist_operations(self):
        """Test watchlist add, remove, and list operations"""
        profile_id = "P001"
        content_id = "M001"
        
        # Add to watchlist
        add_resp = self.api.watchlist_add(profile_id, content_id)
        self.assertTrue(add_resp["ok"])
        self.assertIn("watchlist", add_resp)
        
        # List watchlist
        list_resp = self.api.watchlist_list(profile_id)
        self.assertTrue(list_resp["ok"])
        self.assertTrue(any(item["id"] == content_id for item in list_resp["watchlist"]))
        
        # Remove from watchlist
        remove_resp = self.api.watchlist_remove(profile_id, content_id)
        self.assertTrue(remove_resp["ok"])
        self.assertFalse(any(item["id"] == content_id for item in remove_resp["watchlist"]))

    def test_ratings_operations(self):
        """Test rating content and listing ratings"""
        profile_id = "P001"
        content_id = "M001"
        
        # Add rating
        rating_resp = self.api.ratings_add(profile_id, content_id, 5)
        self.assertTrue(rating_resp["ok"])
        self.assertEqual(rating_resp["rating"], 5)
        
        # List ratings
        list_resp = self.api.ratings_list(profile_id)
        self.assertTrue(list_resp["ok"])
        self.assertEqual(list_resp["ratings"][content_id], 5)
        
        # Remove rating
        remove_resp = self.api.ratings_remove(profile_id, content_id)
        self.assertTrue(remove_resp["ok"])
        
        # Verify rating is removed
        list_resp = self.api.ratings_list(profile_id)
        self.assertNotIn(content_id, list_resp["ratings"])

    def test_recommendations(self):
        """Test getting recommendations"""
        profile_id = "P001"
        
        # Get general recommendations
        rec_resp = self.api.recommendations_get(profile_id, limit=5)
        self.assertTrue(rec_resp["ok"])
        self.assertLessEqual(len(rec_resp["recommendations"]), 5)
        
        # Get recommendations based on watched content
        content_id = "M001"
        because_resp = self.api.recommendations_because_you_watched(profile_id, content_id)
        self.assertTrue(because_resp["ok"])
        self.assertIn("recommendations", because_resp)

    def test_search_operations(self):
        """Test content search and suggestions"""
        # Search for content
        search_resp = self.api.search_content("Shawshank", limit=10)
        self.assertTrue(search_resp["ok"])
        self.assertIn("results", search_resp)
        self.assertIn("total", search_resp)
        
        # Search with type filter
        movie_search = self.api.search_content("Breaking", type_filter="series", limit=5)
        self.assertTrue(movie_search["ok"])
        for result in movie_search["results"]:
            self.assertEqual(result["type"], "series")
        
        # Get search suggestions
        suggestions_resp = self.api.search_suggestions("Stranger", limit=5)
        self.assertTrue(suggestions_resp["ok"])
        self.assertIn("suggestions", suggestions_resp)

    def test_continue_watching(self):
        """Test continue watching functionality"""
        profile_id = "P001"
        content_id = "S001"
        
        # Update continue watching progress
        update_resp = self.api.continue_watching_update(profile_id, content_id, 50, season=2, episode=5)
        self.assertTrue(update_resp["ok"])
        
        # List continue watching
        list_resp = self.api.continue_watching_list(profile_id)
        self.assertTrue(list_resp["ok"])
        self.assertTrue(any(item["content_id"] == content_id for item in list_resp["continue_watching"]))
        
        # Update progress again
        update_resp = self.api.continue_watching_update(profile_id, content_id, 75)
        self.assertTrue(update_resp["ok"])
        entry = next(item for item in update_resp["continue_watching"] if item["content_id"] == content_id)
        self.assertEqual(entry["progress"], 75)

    def test_trending_content(self):
        """Test trending content retrieval"""
        # Get general trending
        trending_resp = self.api.trending_get(limit=10)
        self.assertTrue(trending_resp["ok"])
        self.assertLessEqual(len(trending_resp["trending"]), 10)
        
        # Get trending movies
        movies_resp = self.api.trending_movies(limit=5)
        self.assertTrue(movies_resp["ok"])
        for movie in movies_resp["trending_movies"]:
            self.assertEqual(movie["type"], "movie")
        
        # Get trending shows
        shows_resp = self.api.trending_shows(limit=5)
        self.assertTrue(shows_resp["ok"])
        for show in shows_resp["trending_shows"]:
            self.assertEqual(show["type"], "series")

    def test_categories(self):
        """Test category operations"""
        # List categories
        categories_resp = self.api.categories_list()
        self.assertTrue(categories_resp["ok"])
        self.assertIn("categories", categories_resp)
        
        # Get content in specific category
        if categories_resp["categories"]:
            category = categories_resp["categories"][0]
            content_resp = self.api.categories_get(category, limit=10)
            self.assertTrue(content_resp["ok"])
            self.assertEqual(content_resp["category"], category)
            self.assertIn("content", content_resp)

    def test_subscription_operations(self):
        """Test subscription management"""
        # Get subscription info
        info_resp = self.api.get_subscription_info()
        self.assertTrue(info_resp["ok"])
        self.assertIn("subscription", info_resp)
        
        # Get available plans
        plans_resp = self.api.subscription_plans()
        self.assertTrue(plans_resp["ok"])
        self.assertIn("plans", plans_resp)
        self.assertGreater(len(plans_resp["plans"]), 0)
        
        # Cancel subscription
        cancel_resp = self.api.subscription_cancel()
        self.assertTrue(cancel_resp["ok"])
        self.assertIn("cancelled_at", cancel_resp)

    def test_device_management(self):
        """Test device management operations"""
        # List devices
        devices_resp = self.api.devices_list()
        self.assertTrue(devices_resp["ok"])
        self.assertIn("devices", devices_resp)
        
        if devices_resp["devices"]:
            device_id = devices_resp["devices"][0]["id"]
            
            # Remove device
            remove_resp = self.api.devices_remove(device_id)
            self.assertTrue(remove_resp["ok"])
            
            # Verify device is removed
            devices_after = self.api.devices_list()
            self.assertFalse(any(d["id"] == device_id for d in devices_after["devices"]))
        
        # Logout all devices
        logout_resp = self.api.devices_logout_all()
        self.assertTrue(logout_resp["ok"])
        self.assertIn("logged_out_devices", logout_resp)

    def test_notifications(self):
        """Test notification operations"""
        # List all notifications
        notifications_resp = self.api.notifications_list()
        self.assertTrue(notifications_resp["ok"])
        self.assertIn("notifications", notifications_resp)
        
        # List unread notifications
        unread_resp = self.api.notifications_list(unread_only=True)
        self.assertTrue(unread_resp["ok"])
        
        if unread_resp["notifications"]:
            notification_id = unread_resp["notifications"][0]["id"]
            
            # Mark as read
            mark_read_resp = self.api.notifications_mark_read(notification_id)
            self.assertTrue(mark_read_resp["ok"])
            
            # Verify it's marked as read
            updated_list = self.api.notifications_list(unread_only=True)
            self.assertFalse(any(n["id"] == notification_id for n in updated_list["notifications"]))
        
        # Mark all as read
        mark_all_resp = self.api.notifications_mark_all_read()
        self.assertTrue(mark_all_resp["ok"])
        self.assertIn("marked_read", mark_all_resp)

    def test_favorites_operations(self):
        """Test favorites add, remove, and list operations"""
        profile_id = "P001"
        content_id = "M001"
        
        # Add to favorites
        add_resp = self.api.favorites_add(profile_id, content_id)
        self.assertTrue(add_resp["ok"])
        self.assertIn(content_id, add_resp["favorites"])
        
        # List favorites
        list_resp = self.api.favorites_list(profile_id)
        self.assertTrue(list_resp["ok"])
        self.assertTrue(any(item["id"] == content_id for item in list_resp["favorites"]))
        
        # Remove from favorites
        remove_resp = self.api.favorites_remove(profile_id, content_id)
        self.assertTrue(remove_resp["ok"])
        self.assertNotIn(content_id, remove_resp["favorites"])

    def test_parental_controls(self):
        """Test parental control operations"""
        profile_id = "P002"  # Kids profile
        
        # Get parental controls
        get_resp = self.api.parental_controls_get(profile_id)
        self.assertTrue(get_resp["ok"])
        self.assertIn("parental_controls", get_resp)
        
        # Update parental controls
        update_resp = self.api.parental_controls_update(
            profile_id, 
            enabled=True, 
            max_rating="TV-Y7", 
            pin_required=True,
            blocked_content=["TV-MA", "R"]
        )
        self.assertTrue(update_resp["ok"])
        controls = update_resp["parental_controls"]
        self.assertTrue(controls["enabled"])
        self.assertEqual(controls["max_rating"], "TV-Y7")
        self.assertTrue(controls["pin_required"])

    def test_viewing_activity(self):
        """Test viewing activity operations"""
        profile_id = "P001"
        content_id = "M001"
        
        # Add viewing activity
        add_resp = self.api.viewing_activity_add(profile_id, content_id, 120, device_id="D001")
        self.assertTrue(add_resp["ok"])
        self.assertEqual(add_resp["activity"]["duration_watched"], 120)
        self.assertEqual(add_resp["activity"]["device"], "D001")
        
        # List viewing activity
        list_resp = self.api.viewing_activity_list(profile_id, limit=10)
        self.assertTrue(list_resp["ok"])
        self.assertIn("viewing_activity", list_resp)
        
        # Clear viewing activity
        clear_resp = self.api.viewing_activity_clear(profile_id)
        self.assertTrue(clear_resp["ok"])
        self.assertIn("cleared_entries", clear_resp)

    # Edge cases for Netflix API
    def test_profiles_get_nonexistent(self):
        """Test getting a profile that doesn't exist"""
        resp = self.api.profiles_get("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_profiles_update_nonexistent(self):
        """Test updating a profile that doesn't exist"""
        resp = self.api.profiles_update("NONEXISTENT_PROFILE", name="New Name")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_profiles_delete_nonexistent(self):
        """Test deleting a profile that doesn't exist"""
        resp = self.api.profiles_delete("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_watchlist_nonexistent_profile(self):
        """Test watchlist operations with nonexistent profile"""
        resp = self.api.watchlist_list("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")
        
        resp = self.api.watchlist_add("NONEXISTENT_PROFILE", "M001")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_ratings_invalid_rating(self):
        """Test adding invalid ratings"""
        profile_id = "P001"
        content_id = "M001"
        
        # Test rating 0 (invalid)
        resp = self.api.ratings_add(profile_id, content_id, 0)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "invalid_rating")
        
        # Test rating 6 (invalid)
        resp = self.api.ratings_add(profile_id, content_id, 6)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "invalid_rating")
        
        # Test negative rating
        resp = self.api.ratings_add(profile_id, content_id, -1)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "invalid_rating")

    def test_ratings_nonexistent_profile(self):
        """Test rating operations with nonexistent profile"""
        resp = self.api.ratings_list("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")
        
        resp = self.api.ratings_add("NONEXISTENT_PROFILE", "M001", 5)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_recommendations_nonexistent_profile(self):
        """Test recommendations with nonexistent profile"""
        resp = self.api.recommendations_get("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")
        
        resp = self.api.recommendations_because_you_watched("NONEXISTENT_PROFILE", "M001")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_continue_watching_nonexistent_profile(self):
        """Test continue watching with nonexistent profile"""
        resp = self.api.continue_watching_list("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")
        
        resp = self.api.continue_watching_update("NONEXISTENT_PROFILE", "M001", 50)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_categories_nonexistent(self):
        """Test getting content for nonexistent category"""
        resp = self.api.categories_get("NONEXISTENT_CATEGORY")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "category_not_found")

    def test_notifications_mark_read_nonexistent(self):
        """Test marking nonexistent notification as read"""
        resp = self.api.notifications_mark_read("NONEXISTENT_NOTIFICATION")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "notification_not_found")

    def test_favorites_nonexistent_profile(self):
        """Test favorites operations with nonexistent profile"""
        resp = self.api.favorites_list("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")
        
        resp = self.api.favorites_add("NONEXISTENT_PROFILE", "M001")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_parental_controls_nonexistent_profile(self):
        """Test parental controls with nonexistent profile"""
        resp = self.api.parental_controls_get("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")
        
        resp = self.api.parental_controls_update("NONEXISTENT_PROFILE", enabled=True)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_viewing_activity_nonexistent_profile(self):
        """Test viewing activity with nonexistent profile"""
        resp = self.api.viewing_activity_list("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")
        
        resp = self.api.viewing_activity_add("NONEXISTENT_PROFILE", "M001", 120)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_empty_search_query(self):
        """Test search with empty query"""
        resp = self.api.search_content("")
        self.assertTrue(resp["ok"])
        self.assertIn("results", resp)
        self.assertIn("total", resp)

    def test_very_long_search_query(self):
        """Test search with very long query"""
        long_query = "A" * 1000
        resp = self.api.search_content(long_query)
        self.assertTrue(resp["ok"])
        self.assertIn("results", resp)

    def test_search_with_special_characters(self):
        """Test search with special characters"""
        special_query = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        resp = self.api.search_content(special_query)
        self.assertTrue(resp["ok"])
        self.assertIn("results", resp)

    def test_continue_watching_progress_boundaries(self):
        """Test continue watching with boundary progress values"""
        profile_id = "P001"
        content_id = "M001"
        
        # Test 0% progress
        resp = self.api.continue_watching_update(profile_id, content_id, 0)
        self.assertTrue(resp["ok"])
        
        # Test 100% progress
        resp = self.api.continue_watching_update(profile_id, content_id, 100)
        self.assertTrue(resp["ok"])
        
        # Test negative progress
        resp = self.api.continue_watching_update(profile_id, content_id, -10)
        self.assertTrue(resp["ok"])
        
        # Test very high progress
        resp = self.api.continue_watching_update(profile_id, content_id, 1000)
        self.assertTrue(resp["ok"])

    def test_viewing_activity_duration_boundaries(self):
        """Test viewing activity with boundary duration values"""
        profile_id = "P001"
        content_id = "M001"
        
        # Test 0 duration
        resp = self.api.viewing_activity_add(profile_id, content_id, 0)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["activity"]["duration_watched"], 0)
        
        # Test negative duration
        resp = self.api.viewing_activity_add(profile_id, content_id, -30)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["activity"]["duration_watched"], -30)
        
        # Test very high duration
        resp = self.api.viewing_activity_add(profile_id, content_id, 10000)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["activity"]["duration_watched"], 10000)

    def test_profile_creation_edge_cases(self):
        """Test profile creation with edge cases"""
        # Test empty name
        resp = self.api.profiles_create("")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["profile"]["name"], "")
        
        # Test very long name
        long_name = "A" * 1000
        resp = self.api.profiles_create(long_name)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["profile"]["name"], long_name)
        
        # Test special characters in name
        special_name = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        resp = self.api.profiles_create(special_name)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["profile"]["name"], special_name)

    def test_multiple_profiles_operations(self):
        """Test operations across multiple profiles"""
        # Create multiple profiles
        profile1 = self.api.profiles_create("Profile 1")
        profile2 = self.api.profiles_create("Profile 2")
        
        profile1_id = profile1["profile"]["id"]
        profile2_id = profile2["profile"]["id"]
        
        # Add different content to each profile's watchlist
        self.api.watchlist_add(profile1_id, "M001")
        self.api.watchlist_add(profile2_id, "S001")
        
        # Verify each profile has its own watchlist
        watchlist1 = self.api.watchlist_list(profile1_id)
        watchlist2 = self.api.watchlist_list(profile2_id)
        
        self.assertTrue(any(item["id"] == "M001" for item in watchlist1["watchlist"]))
        self.assertTrue(any(item["id"] == "S001" for item in watchlist2["watchlist"]))
        self.assertFalse(any(item["id"] == "S001" for item in watchlist1["watchlist"]))
        self.assertFalse(any(item["id"] == "M001" for item in watchlist2["watchlist"]))

    def test_concurrent_operations_same_profile(self):
        """Test concurrent-like operations on the same profile"""
        profile_id = "P001"
        content_id = "M001"
        
        # Perform multiple operations on the same profile
        self.api.watchlist_add(profile_id, content_id)
        self.api.ratings_add(profile_id, content_id, 4)
        self.api.favorites_add(profile_id, content_id)
        self.api.continue_watching_update(profile_id, content_id, 25)
        
        # Verify all operations were successful
        watchlist = self.api.watchlist_list(profile_id)
        ratings = self.api.ratings_list(profile_id)
        favorites = self.api.favorites_list(profile_id)
        continue_watching = self.api.continue_watching_list(profile_id)
        
        self.assertTrue(any(item["id"] == content_id for item in watchlist["watchlist"]))
        self.assertEqual(ratings["ratings"][content_id], 4)
        self.assertTrue(any(item["id"] == content_id for item in favorites["favorites"]))
        self.assertTrue(any(item["content_id"] == content_id for item in continue_watching["continue_watching"]))

    def test_duplicate_operations(self):
        """Test duplicate operations (adding same content multiple times)"""
        profile_id = "P001"
        content_id = "M001"
        
        # Add to watchlist multiple times
        self.api.watchlist_add(profile_id, content_id)
        self.api.watchlist_add(profile_id, content_id)
        self.api.watchlist_add(profile_id, content_id)
        
        # Should only appear once
        watchlist = self.api.watchlist_list(profile_id)
        content_items = [item for item in watchlist["watchlist"] if item["id"] == content_id]
        self.assertEqual(len(content_items), 1)
        
        # Add to favorites multiple times
        self.api.favorites_add(profile_id, content_id)
        self.api.favorites_add(profile_id, content_id)
        
        # Should only appear once
        favorites = self.api.favorites_list(profile_id)
        favorite_items = [item for item in favorites["favorites"] if item["id"] == content_id]
        self.assertEqual(len(favorite_items), 1)

    def test_remove_nonexistent_items(self):
        """Test removing items that don't exist"""
        profile_id = "P001"
        nonexistent_content = "NONEXISTENT_CONTENT"
        
        # Remove from watchlist
        resp = self.api.watchlist_remove(profile_id, nonexistent_content)
        self.assertTrue(resp["ok"])
        
        # Remove from favorites
        resp = self.api.favorites_remove(profile_id, nonexistent_content)
        self.assertTrue(resp["ok"])
        
        # Remove rating
        resp = self.api.ratings_remove(profile_id, nonexistent_content)
        self.assertTrue(resp["ok"])

    def test_empty_and_none_values_netflix(self):
        """Test handling of empty and None values in Netflix API"""
        profile_id = "P001"
        
        # Test with empty content ID
        try:
            self.api.watchlist_add(profile_id, "")
        except:
            pass  # Expected to handle gracefully
        
        try:
            self.api.ratings_add(profile_id, "", 5)
        except:
            pass  # Expected to handle gracefully
        
        # Test with None values
        try:
            self.api.profiles_update(profile_id, name=None)
        except:
            pass  # Expected to handle gracefully

if __name__ == "__main__":
    unittest.main() 