import json

# Load both files
with open('diverse_youtube_state.json', 'r', encoding='utf-8') as f:
    youtube_data = json.load(f)

with open('diverse_x_state.json', 'r', encoding='utf-8') as f:
    x_data = json.load(f)

# Create name-based mappings
youtube_by_name = {}
for user_id, user in youtube_data['users'].items():
    name = user.get('display_name', '')
    youtube_by_name[name] = user

x_by_name = {}
for user_id, user in x_data['users'].items():
    name = user.get('name', '')
    x_by_name[name] = user

# Find matching users
matches = []
for name in youtube_by_name.keys():
    if name in x_by_name:
        youtube_user = youtube_by_name[name]
        x_user = x_by_name[name]
        
        # Get channel info if exists
        channel_id = youtube_user.get('channels', [None])[0] if youtube_user.get('channels') else None
        
        # Count videos (need to check channels)
        video_count = 0
        if 'channels' in youtube_data and channel_id and channel_id in youtube_data['channels']:
            video_count = len(youtube_data['channels'][channel_id].get('videos', []))
        
        # Count X posts
        post_count = x_user.get('api_usage', {}).get('posts_created', 0)
        
        matches.append({
            'name': name,
            'youtube_user_id': youtube_user['user_id'],
            'youtube_email': youtube_user['email'],
            'youtube_channel_id': channel_id,
            'youtube_video_count': video_count,
            'x_user_id': x_user['id'],
            'x_email': x_user['email'],
            'x_post_count': post_count
        })
        
        if len(matches) >= 10:
            break

# Print results
for i, match in enumerate(matches, 1):
    print(f"User {i}:")
    print(f"  - YouTube: user_id={match['youtube_user_id']}, email={match['youtube_email']}, channel_id={match['youtube_channel_id']}")
    print(f"  - X: user_id={match['x_user_id']}, email={match['x_email']}")
    print(f"  - Has: {match['youtube_video_count']} videos in YouTube, {match['x_post_count']} posts in X")
    print()

print(f"Total matching users found: {len(matches)}")
