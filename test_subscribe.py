from YouTubeApis import YouTubeApis
from UnitTests.test_data_helper import BackendDataLoader

api = YouTubeApis()
data = BackendDataLoader.get_youtube_data()
users = list(data.get('users', {}).values())
user_id = users[0].get('user_id', 'user1') if users else 'user1'
channels = list(data.get('channels', {}).values())
channel_id = channels[0].get('id', 'channel1') if channels else 'channel1'

print('user_id:', repr(user_id))
print('channel_id:', repr(channel_id))
result = api.youtube_subscriptions_insert(channel_id=channel_id, user_id=user_id)
print('Result:', result)