import re

# Read the test file
with open('UnitTests/TestYouTubeApis.py', 'r') as f:
    content = f.read()

# Methods that return {"data": ...} format
data_methods = [
    'get_user_profile',
    'get_watch_history', 
    'list_subscriptions',
    'list_channels_for_user',
    'get_channel_details',
    'create_channel',
    'list_videos_in_channel',
    'get_video_details',
    'upload_video',
    'search_videos',
    'create_playlist',
    'get_playlist_details',
    'list_playlists_in_channel',
    'add_comment_to_video',
    'list_comments_for_video',
    'get_watch_later_playlist',
    'get_account_status',
    'get_channel_history',
    'get_notification_settings',
    'get_user_analytics',
    'get_user_language_preference',
    'search_users_by_language',
    'reset_data',
    'youtube_captions_insert',
    'youtube_captions_update',
    'youtube_captions_delete',
    'youtube_channel_banners_insert',
    'youtube_channels_update',
    'youtube_comments_insert',
    'youtube_playlistItems_insert',
    'youtube_playlistItems_delete',
    'youtube_videos_rate',
    'like_video',
    'unlike_video',
    'add_to_watch_later',
    'remove_from_watch_later',
    'update_notification_settings',
    'update_language_preference',
    'add_to_channel_history'
]

# For each data method, update the test expectations
for method in data_methods:
    # Replace status checks with data checks for success cases
    pattern = rf'(def test_{re.escape(method)}_[^\(]+)\(\):.*?(self\.assertTrue\(result\.get\("status", False\)\))'
    replacement = rf'\1():\n        """Test \1."""\n        result = self.youtube_api.\1(**test_params)\n        self.assertIn("data", result)\n        self.assertIsNotNone(result["data"])'
    
    # This is too complex. Let me do simpler replacements.
    
    # Replace self.assertTrue(result.get("status", False)) with self.assertIn("data", result); self.assertIsNotNone(result["data"])
    content = re.sub(
        rf'(def test_{re.escape(method)}_[^\(]+\(\):.*?\n.*?)self\.assertTrue\(result\.get\("status", False\)\)',
        rf'\1self.assertIn("data", result)\n        self.assertIsNotNone(result["data"])',
        content,
        flags=re.DOTALL
    )
    
    # Replace self.assertFalse(result.get("status", True)) with self.assertIn("data", result); self.assertIsNone(result["data"])
    content = re.sub(
        rf'(def test_{re.escape(method)}_[^\(]+\(\):.*?\n.*?)self\.assertFalse\(result\.get\("status", True\)\)',
        rf'\1self.assertIn("data", result)\n        self.assertIsNone(result["data"])',
        content,
        flags=re.DOTALL
    )

# Write back
with open('UnitTests/TestYouTubeApis.py', 'w') as f:
    f.write(content)

print("Test updates done")