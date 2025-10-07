from YouTubeApis import YouTubeApis
from UnitTests.test_data_helper import BackendDataLoader

api = YouTubeApis()
data = BackendDataLoader.get_youtube_data()
users = list(data.get('users', {}).values())
user_id = users[0].get('user_id', 'user1') if users else 'user1'

print('Test user ID:', repr(user_id))
print('API has user:', user_id in api.users)
print('API users keys:', list(api.users.keys())[:3])

result = api.set_current_user(user_id=user_id)
print('Result:', result)