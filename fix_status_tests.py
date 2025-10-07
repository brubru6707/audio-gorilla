status_methods = [
    'set_current_user',
    'set_current_channel',
    'youtube_subscriptions_insert',
    'youtube_subscriptions_delete',
    'add_to_watch_later',
    'remove_from_watch_later',
    'update_notification_settings',
    'update_language_preference',
    'add_to_channel_history',
    'youtube_videos_rate',
    'like_video',
    'unlike_video',
    'youtube_playlistItems_insert',
    'youtube_playlistItems_delete',
    'youtube_channel_banners_insert',
    'youtube_channels_update',
    'youtube_captions_insert',
    'youtube_captions_update',
    'youtube_captions_delete',
    'delete_video',
    'delete_comment',
    'reset_data'
]

# Read the test file
with open('UnitTests/TestYouTubeApis.py', 'r') as f:
    content = f.read()

# For status methods, change back to status checks
for method in status_methods:
    # Change success cases back to status
    import re
    content = re.sub(
        rf'(def test_{re.escape(method)}_[^\(]+\(\):.*?\n.*?)self\.assertIn\("data", result\);\s*self\.assertIsNotNone\(result\["data"\]\)',
        rf'\1self.assertTrue(result.get("status", False))',
        content,
        flags=re.DOTALL
    )
    
    # Change failure cases back to status
    content = re.sub(
        rf'(def test_{re.escape(method)}_[^\(]+\(\):.*?\n.*?)self\.assertIn\("data", result\);\s*self\.assertIsNone\(result\["data"\]\)',
        rf'\1self.assertFalse(result.get("status", True))',
        content,
        flags=re.DOTALL
    )

# Write back
with open('UnitTests/TestYouTubeApis.py', 'w') as f:
    f.write(content)

print("Status method test fixes done")