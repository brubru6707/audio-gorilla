import unittest
from NetflixApis import NetflixAPI

class TestNetflixAPI(unittest.TestCase):
    def setUp(self):
        self.api = NetflixAPI()

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - PROFILES METHODS
    # ============================================================================

    def test_profiles_list_basic(self):
        """Test basic profiles.list functionality"""
        resp = self.api.profiles_list()
        self.assertTrue(resp["ok"])
        self.assertIn("profiles", resp)
        self.assertIsInstance(resp["profiles"], list)

    def test_profiles_get_basic(self):
        """Test basic profiles.get functionality"""
        resp = self.api.profiles_get("P001")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["profile"]["id"], "P001")
        self.assertIn("name", resp["profile"])

    def test_profiles_get_nonexistent(self):
        """Test profiles.get with nonexistent profile"""
        resp = self.api.profiles_get("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_profiles_create_basic(self):
        """Test basic profiles.create functionality"""
        resp = self.api.profiles_create("Test Profile")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["profile"]["name"], "Test Profile")
        self.assertIn("id", resp["profile"])

    def test_profiles_create_with_maturity_level(self):
        """Test profiles.create with maturity_level parameter"""
        resp = self.api.profiles_create("Teen Profile", maturity_level="teen")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["profile"]["maturity_level"], "teen")

    def test_profiles_create_with_language(self):
        """Test profiles.create with language parameter"""
        resp = self.api.profiles_create("Spanish Profile", language="es")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["profile"]["language"], "es")

    def test_profiles_create_with_autoplay(self):
        """Test profiles.create with autoplay parameter"""
        resp = self.api.profiles_create("No Autoplay Profile", autoplay=False)
        self.assertTrue(resp["ok"])
        self.assertFalse(resp["profile"]["autoplay"])

    def test_profiles_update_basic(self):
        """Test basic profiles.update functionality"""
        # First create a profile
        create_resp = self.api.profiles_create("Original Name")
        profile_id = create_resp["profile"]["id"]
        
        # Update the profile
        resp = self.api.profiles_update(profile_id, name="Updated Name")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["profile"]["name"], "Updated Name")

    def test_profiles_update_with_language(self):
        """Test profiles.update with language parameter"""
        create_resp = self.api.profiles_create("Test Profile")
        profile_id = create_resp["profile"]["id"]
        
        resp = self.api.profiles_update(profile_id, language="fr")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["profile"]["language"], "fr")

    def test_profiles_update_nonexistent(self):
        """Test profiles.update with nonexistent profile"""
        resp = self.api.profiles_update("NONEXISTENT_PROFILE", name="New Name")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_profiles_delete_basic(self):
        """Test basic profiles.delete functionality"""
        # First create a profile
        create_resp = self.api.profiles_create("To Delete")
        profile_id = create_resp["profile"]["id"]
        
        # Delete the profile
        resp = self.api.profiles_delete(profile_id)
        self.assertTrue(resp["ok"])
        
        # Verify it's gone
        get_resp = self.api.profiles_get(profile_id)
        self.assertFalse(get_resp["ok"])
        self.assertEqual(get_resp["error"], "profile_not_found")

    def test_profiles_delete_nonexistent(self):
        """Test profiles.delete with nonexistent profile"""
        resp = self.api.profiles_delete("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - WATCHLIST METHODS
    # ============================================================================

    def test_watchlist_add_basic(self):
        """Test basic watchlist.add functionality"""
        resp = self.api.watchlist_add("P001", "M001")
        self.assertTrue(resp["ok"])
        self.assertIn("watchlist", resp)
        self.assertTrue(any(item["id"] == "M001" for item in resp["watchlist"]))

    def test_watchlist_add_nonexistent_profile(self):
        """Test watchlist.add with nonexistent profile"""
        resp = self.api.watchlist_add("NONEXISTENT_PROFILE", "M001")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_watchlist_remove_basic(self):
        """Test basic watchlist.remove functionality"""
        # First add to watchlist
        self.api.watchlist_add("P001", "M001")
        
        # Remove from watchlist
        resp = self.api.watchlist_remove("P001", "M001")
        self.assertTrue(resp["ok"])
        self.assertFalse(any(item["id"] == "M001" for item in resp["watchlist"]))

    def test_watchlist_remove_nonexistent_profile(self):
        """Test watchlist.remove with nonexistent profile"""
        resp = self.api.watchlist_remove("NONEXISTENT_PROFILE", "M001")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_watchlist_list_basic(self):
        """Test basic watchlist.list functionality"""
        resp = self.api.watchlist_list("P001")
        self.assertTrue(resp["ok"])
        self.assertIn("watchlist", resp)
        self.assertIsInstance(resp["watchlist"], list)

    def test_watchlist_list_nonexistent_profile(self):
        """Test watchlist.list with nonexistent profile"""
        resp = self.api.watchlist_list("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - RATINGS METHODS
    # ============================================================================

    def test_ratings_add_basic(self):
        """Test basic ratings.add functionality"""
        resp = self.api.ratings_add("P001", "M001", 5)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["rating"], 5)

    def test_ratings_add_invalid_rating_zero(self):
        """Test ratings.add with invalid rating (0)"""
        resp = self.api.ratings_add("P001", "M001", 0)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "invalid_rating")

    def test_ratings_add_invalid_rating_six(self):
        """Test ratings.add with invalid rating (6)"""
        resp = self.api.ratings_add("P001", "M001", 6)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "invalid_rating")

    def test_ratings_add_invalid_rating_negative(self):
        """Test ratings.add with invalid rating (negative)"""
        resp = self.api.ratings_add("P001", "M001", -1)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "invalid_rating")

    def test_ratings_add_nonexistent_profile(self):
        """Test ratings.add with nonexistent profile"""
        resp = self.api.ratings_add("NONEXISTENT_PROFILE", "M001", 5)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_ratings_remove_basic(self):
        """Test basic ratings.remove functionality"""
        # First add a rating
        self.api.ratings_add("P001", "M001", 4)
        
        # Remove the rating
        resp = self.api.ratings_remove("P001", "M001")
        self.assertTrue(resp["ok"])
        
        # Verify rating is removed
        list_resp = self.api.ratings_list("P001")
        self.assertNotIn("M001", list_resp["ratings"])

    def test_ratings_remove_nonexistent_profile(self):
        """Test ratings.remove with nonexistent profile"""
        resp = self.api.ratings_remove("NONEXISTENT_PROFILE", "M001")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_ratings_list_basic(self):
        """Test basic ratings.list functionality"""
        # First add a rating
        self.api.ratings_add("P001", "M001", 3)
        
        # List ratings
        resp = self.api.ratings_list("P001")
        self.assertTrue(resp["ok"])
        self.assertIn("ratings", resp)
        self.assertEqual(resp["ratings"]["M001"], 3)

    def test_ratings_list_nonexistent_profile(self):
        """Test ratings.list with nonexistent profile"""
        resp = self.api.ratings_list("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - RECOMMENDATIONS METHODS
    # ============================================================================

    def test_recommendations_get_basic(self):
        """Test basic recommendations.get functionality"""
        resp = self.api.recommendations_get("P001")
        self.assertTrue(resp["ok"])
        self.assertIn("recommendations", resp)
        self.assertIsInstance(resp["recommendations"], list)

    def test_recommendations_get_with_limit(self):
        """Test recommendations.get with limit parameter"""
        resp = self.api.recommendations_get("P001", limit=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["recommendations"]), 5)

    def test_recommendations_get_nonexistent_profile(self):
        """Test recommendations.get with nonexistent profile"""
        resp = self.api.recommendations_get("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_recommendations_because_you_watched_basic(self):
        """Test basic recommendations.because_you_watched functionality"""
        resp = self.api.recommendations_because_you_watched("P001", "M001")
        self.assertTrue(resp["ok"])
        self.assertIn("recommendations", resp)

    def test_recommendations_because_you_watched_nonexistent_profile(self):
        """Test recommendations.because_you_watched with nonexistent profile"""
        resp = self.api.recommendations_because_you_watched("NONEXISTENT_PROFILE", "M001")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - SEARCH METHODS
    # ============================================================================

    def test_search_content_basic(self):
        """Test basic search.content functionality"""
        resp = self.api.search_content("Shawshank")
        self.assertTrue(resp["ok"])
        self.assertIn("results", resp)
        self.assertIn("total", resp)

    def test_search_content_with_profile_id(self):
        """Test search.content with profile_id parameter"""
        resp = self.api.search_content("Breaking", profile_id="P001")
        self.assertTrue(resp["ok"])
        self.assertIn("results", resp)

    def test_search_content_with_type_filter(self):
        """Test search.content with type_filter parameter"""
        resp = self.api.search_content("Breaking", type_filter="series")
        self.assertTrue(resp["ok"])
        for result in resp["results"]:
            self.assertEqual(result["type"], "series")

    def test_search_content_with_limit(self):
        """Test search.content with limit parameter"""
        resp = self.api.search_content("Test", limit=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["results"]), 5)

    def test_search_content_empty_query(self):
        """Test search.content with empty query"""
        resp = self.api.search_content("")
        self.assertTrue(resp["ok"])
        self.assertIn("results", resp)

    def test_search_content_long_query(self):
        """Test search.content with very long query"""
        long_query = "A" * 1000
        resp = self.api.search_content(long_query)
        self.assertTrue(resp["ok"])
        self.assertIn("results", resp)

    def test_search_content_special_characters(self):
        """Test search.content with special characters"""
        special_query = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        resp = self.api.search_content(special_query)
        self.assertTrue(resp["ok"])
        self.assertIn("results", resp)

    def test_search_suggestions_basic(self):
        """Test basic search.suggestions functionality"""
        resp = self.api.search_suggestions("Stranger")
        self.assertTrue(resp["ok"])
        self.assertIn("suggestions", resp)
        self.assertIsInstance(resp["suggestions"], list)

    def test_search_suggestions_with_limit(self):
        """Test search.suggestions with limit parameter"""
        resp = self.api.search_suggestions("Test", limit=3)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["suggestions"]), 3)

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - CONTINUE WATCHING METHODS
    # ============================================================================

    def test_continue_watching_list_basic(self):
        """Test basic continue_watching.list functionality"""
        resp = self.api.continue_watching_list("P001")
        self.assertTrue(resp["ok"])
        self.assertIn("continue_watching", resp)
        self.assertIsInstance(resp["continue_watching"], list)

    def test_continue_watching_list_nonexistent_profile(self):
        """Test continue_watching.list with nonexistent profile"""
        resp = self.api.continue_watching_list("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_continue_watching_update_basic(self):
        """Test basic continue_watching.update functionality"""
        resp = self.api.continue_watching_update("P001", "S001", 50)
        self.assertTrue(resp["ok"])
        self.assertIn("continue_watching", resp)

    def test_continue_watching_update_with_season_episode(self):
        """Test continue_watching.update with season and episode parameters"""
        resp = self.api.continue_watching_update("P001", "S001", 75, season=2, episode=5)
        self.assertTrue(resp["ok"])
        entry = next(item for item in resp["continue_watching"] if item["content_id"] == "S001")
        self.assertEqual(entry["season"], 2)
        self.assertEqual(entry["episode"], 5)

    def test_continue_watching_update_nonexistent_profile(self):
        """Test continue_watching.update with nonexistent profile"""
        resp = self.api.continue_watching_update("NONEXISTENT_PROFILE", "S001", 50)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_continue_watching_update_progress_boundaries(self):
        """Test continue_watching.update with boundary progress values"""
        # Test 0% progress
        resp = self.api.continue_watching_update("P001", "M001", 0)
        self.assertTrue(resp["ok"])
        
        # Test 100% progress
        resp = self.api.continue_watching_update("P001", "M001", 100)
        self.assertTrue(resp["ok"])
        
        # Test negative progress
        resp = self.api.continue_watching_update("P001", "M001", -10)
        self.assertTrue(resp["ok"])
        
        # Test very high progress
        resp = self.api.continue_watching_update("P001", "M001", 1000)
        self.assertTrue(resp["ok"])

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - TRENDING METHODS
    # ============================================================================

    def test_trending_get_basic(self):
        """Test basic trending.get functionality"""
        resp = self.api.trending_get()
        self.assertTrue(resp["ok"])
        self.assertIn("trending", resp)
        self.assertIsInstance(resp["trending"], list)

    def test_trending_get_with_region(self):
        """Test trending.get with region parameter"""
        resp = self.api.trending_get(region="US")
        self.assertTrue(resp["ok"])
        self.assertIn("trending", resp)

    def test_trending_get_with_limit(self):
        """Test trending.get with limit parameter"""
        resp = self.api.trending_get(limit=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["trending"]), 5)

    def test_trending_movies_basic(self):
        """Test basic trending.movies functionality"""
        resp = self.api.trending_movies()
        self.assertTrue(resp["ok"])
        self.assertIn("trending_movies", resp)
        for movie in resp["trending_movies"]:
            self.assertEqual(movie["type"], "movie")

    def test_trending_movies_with_limit(self):
        """Test trending.movies with limit parameter"""
        resp = self.api.trending_movies(limit=3)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["trending_movies"]), 3)

    def test_trending_shows_basic(self):
        """Test basic trending.shows functionality"""
        resp = self.api.trending_shows()
        self.assertTrue(resp["ok"])
        self.assertIn("trending_shows", resp)
        for show in resp["trending_shows"]:
            self.assertEqual(show["type"], "series")

    def test_trending_shows_with_limit(self):
        """Test trending.shows with limit parameter"""
        resp = self.api.trending_shows(limit=3)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["trending_shows"]), 3)

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - CATEGORIES METHODS
    # ============================================================================

    def test_categories_list_basic(self):
        """Test basic categories.list functionality"""
        resp = self.api.categories_list()
        self.assertTrue(resp["ok"])
        self.assertIn("categories", resp)
        self.assertIsInstance(resp["categories"], list)

    def test_categories_get_basic(self):
        """Test basic categories.get functionality"""
        # First get categories list
        list_resp = self.api.categories_list()
        if list_resp["categories"]:
            category = list_resp["categories"][0]
            resp = self.api.categories_get(category)
            self.assertTrue(resp["ok"])
            self.assertEqual(resp["category"], category)
            self.assertIn("content", resp)

    def test_categories_get_with_limit(self):
        """Test categories.get with limit parameter"""
        list_resp = self.api.categories_list()
        if list_resp["categories"]:
            category = list_resp["categories"][0]
            resp = self.api.categories_get(category, limit=5)
            self.assertTrue(resp["ok"])
            self.assertLessEqual(len(resp["content"]), 5)

    def test_categories_get_nonexistent(self):
        """Test categories.get with nonexistent category"""
        resp = self.api.categories_get("NONEXISTENT_CATEGORY")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "category_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - SUBSCRIPTION METHODS
    # ============================================================================

    def test_get_subscription_info_basic(self):
        """Test basic get_subscription_info functionality"""
        resp = self.api.get_subscription_info()
        self.assertTrue(resp["ok"])
        self.assertIn("subscription", resp)
        self.assertIn("plan", resp["subscription"])

    def test_subscription_plans_basic(self):
        """Test basic subscription.plans functionality"""
        resp = self.api.subscription_plans()
        self.assertTrue(resp["ok"])
        self.assertIn("plans", resp)
        self.assertGreater(len(resp["plans"]), 0)

    def test_subscription_cancel_basic(self):
        """Test basic subscription.cancel functionality"""
        resp = self.api.subscription_cancel()
        self.assertTrue(resp["ok"])
        self.assertIn("cancelled_at", resp)

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - DEVICES METHODS
    # ============================================================================

    def test_devices_list_basic(self):
        """Test basic devices.list functionality"""
        resp = self.api.devices_list()
        self.assertTrue(resp["ok"])
        self.assertIn("devices", resp)
        self.assertIsInstance(resp["devices"], list)

    def test_devices_remove_basic(self):
        """Test basic devices.remove functionality"""
        # First get devices list
        list_resp = self.api.devices_list()
        if list_resp["devices"]:
            device_id = list_resp["devices"][0]["id"]
            resp = self.api.devices_remove(device_id)
            self.assertTrue(resp["ok"])
            
            # Verify device is removed
            devices_after = self.api.devices_list()
            self.assertFalse(any(d["id"] == device_id for d in devices_after["devices"]))

    def test_devices_logout_all_basic(self):
        """Test basic devices.logout_all functionality"""
        resp = self.api.devices_logout_all()
        self.assertTrue(resp["ok"])
        self.assertIn("logged_out_devices", resp)

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - NOTIFICATIONS METHODS
    # ============================================================================

    def test_notifications_list_basic(self):
        """Test basic notifications.list functionality"""
        resp = self.api.notifications_list()
        self.assertTrue(resp["ok"])
        self.assertIn("notifications", resp)
        self.assertIsInstance(resp["notifications"], list)

    def test_notifications_list_unread_only(self):
        """Test notifications.list with unread_only parameter"""
        resp = self.api.notifications_list(unread_only=True)
        self.assertTrue(resp["ok"])
        self.assertIn("notifications", resp)

    def test_notifications_mark_read_basic(self):
        """Test basic notifications.mark_read functionality"""
        # First get notifications list
        list_resp = self.api.notifications_list()
        if list_resp["notifications"]:
            notification_id = list_resp["notifications"][0]["id"]
            resp = self.api.notifications_mark_read(notification_id)
            self.assertTrue(resp["ok"])

    def test_notifications_mark_read_nonexistent(self):
        """Test notifications.mark_read with nonexistent notification"""
        resp = self.api.notifications_mark_read("NONEXISTENT_NOTIFICATION")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "notification_not_found")

    def test_notifications_mark_all_read_basic(self):
        """Test basic notifications.mark_all_read functionality"""
        resp = self.api.notifications_mark_all_read()
        self.assertTrue(resp["ok"])
        self.assertIn("marked_read", resp)

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - FAVORITES METHODS
    # ============================================================================

    def test_favorites_add_basic(self):
        """Test basic favorites.add functionality"""
        resp = self.api.favorites_add("P001", "M001")
        self.assertTrue(resp["ok"])
        self.assertIn("favorites", resp)
        self.assertIn("M001", resp["favorites"])

    def test_favorites_add_nonexistent_profile(self):
        """Test favorites.add with nonexistent profile"""
        resp = self.api.favorites_add("NONEXISTENT_PROFILE", "M001")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_favorites_remove_basic(self):
        """Test basic favorites.remove functionality"""
        # First add to favorites
        self.api.favorites_add("P001", "M001")
        
        # Remove from favorites
        resp = self.api.favorites_remove("P001", "M001")
        self.assertTrue(resp["ok"])
        self.assertNotIn("M001", resp["favorites"])

    def test_favorites_remove_nonexistent_profile(self):
        """Test favorites.remove with nonexistent profile"""
        resp = self.api.favorites_remove("NONEXISTENT_PROFILE", "M001")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_favorites_list_basic(self):
        """Test basic favorites.list functionality"""
        # First add to favorites
        self.api.favorites_add("P001", "M001")
        
        # List favorites
        resp = self.api.favorites_list("P001")
        self.assertTrue(resp["ok"])
        self.assertIn("favorites", resp)
        self.assertTrue(any(item["id"] == "M001" for item in resp["favorites"]))

    def test_favorites_list_nonexistent_profile(self):
        """Test favorites.list with nonexistent profile"""
        resp = self.api.favorites_list("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - PARENTAL CONTROLS METHODS
    # ============================================================================

    def test_parental_controls_get_basic(self):
        """Test basic parental_controls.get functionality"""
        resp = self.api.parental_controls_get("P002")
        self.assertTrue(resp["ok"])
        self.assertIn("parental_controls", resp)

    def test_parental_controls_get_nonexistent_profile(self):
        """Test parental_controls.get with nonexistent profile"""
        resp = self.api.parental_controls_get("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_parental_controls_update_basic(self):
        """Test basic parental_controls.update functionality"""
        resp = self.api.parental_controls_update("P002", enabled=True, max_rating="TV-Y7")
        self.assertTrue(resp["ok"])
        controls = resp["parental_controls"]
        self.assertTrue(controls["enabled"])
        self.assertEqual(controls["max_rating"], "TV-Y7")

    def test_parental_controls_update_with_pin(self):
        """Test parental_controls.update with pin_required parameter"""
        resp = self.api.parental_controls_update("P002", pin_required=True)
        self.assertTrue(resp["ok"])
        controls = resp["parental_controls"]
        self.assertTrue(controls["pin_required"])

    def test_parental_controls_update_with_blocked_content(self):
        """Test parental_controls.update with blocked_content parameter"""
        blocked = ["TV-MA", "R"]
        resp = self.api.parental_controls_update("P002", blocked_content=blocked)
        self.assertTrue(resp["ok"])
        controls = resp["parental_controls"]
        self.assertEqual(controls["blocked_content"], blocked)

    def test_parental_controls_update_nonexistent_profile(self):
        """Test parental_controls.update with nonexistent profile"""
        resp = self.api.parental_controls_update("NONEXISTENT_PROFILE", enabled=True)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - VIEWING ACTIVITY METHODS
    # ============================================================================

    def test_viewing_activity_add_basic(self):
        """Test basic viewing_activity.add functionality"""
        resp = self.api.viewing_activity_add("P001", "M001", 120)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["activity"]["duration_watched"], 120)
        self.assertEqual(resp["activity"]["device"], "unknown")

    def test_viewing_activity_add_with_device(self):
        """Test viewing_activity.add with device_id parameter"""
        resp = self.api.viewing_activity_add("P001", "M001", 90, device_id="D001")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["activity"]["duration_watched"], 90)
        self.assertEqual(resp["activity"]["device"], "D001")

    def test_viewing_activity_add_nonexistent_profile(self):
        """Test viewing_activity.add with nonexistent profile"""
        resp = self.api.viewing_activity_add("NONEXISTENT_PROFILE", "M001", 120)
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_viewing_activity_list_basic(self):
        """Test basic viewing_activity.list functionality"""
        # First add some activity
        self.api.viewing_activity_add("P001", "M001", 60)
        
        # List activity
        resp = self.api.viewing_activity_list("P001")
        self.assertTrue(resp["ok"])
        self.assertIn("viewing_activity", resp)
        self.assertIsInstance(resp["viewing_activity"], list)

    def test_viewing_activity_list_with_limit(self):
        """Test viewing_activity.list with limit parameter"""
        resp = self.api.viewing_activity_list("P001", limit=5)
        self.assertTrue(resp["ok"])
        self.assertLessEqual(len(resp["viewing_activity"]), 5)

    def test_viewing_activity_list_nonexistent_profile(self):
        """Test viewing_activity.list with nonexistent profile"""
        resp = self.api.viewing_activity_list("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_viewing_activity_clear_basic(self):
        """Test basic viewing_activity.clear functionality"""
        # First add some activity
        self.api.viewing_activity_add("P001", "M001", 60)
        
        # Clear activity
        resp = self.api.viewing_activity_clear("P001")
        self.assertTrue(resp["ok"])
        self.assertIn("cleared_entries", resp)

    def test_viewing_activity_clear_nonexistent_profile(self):
        """Test viewing_activity.clear with nonexistent profile"""
        resp = self.api.viewing_activity_clear("NONEXISTENT_PROFILE")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "profile_not_found")

    def test_viewing_activity_duration_boundaries(self):
        """Test viewing_activity.add with boundary duration values"""
        # Test 0 duration
        resp = self.api.viewing_activity_add("P001", "M001", 0)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["activity"]["duration_watched"], 0)
        
        # Test negative duration
        resp = self.api.viewing_activity_add("P001", "M001", -30)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["activity"]["duration_watched"], -30)
        
        # Test very high duration
        resp = self.api.viewing_activity_add("P001", "M001", 10000)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["activity"]["duration_watched"], 10000)

    # ============================================================================
    # EDGE CASE TESTS
    # ============================================================================

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