from XApis import XApis
from UnitTests.test_data_helper import BackendDataLoader

# Load test data
data = BackendDataLoader.get_x_data()
users = list(data.get('users', {}).values())
user_id = users[0].get('id', 'user1') if users else 'user1'

# Test API
api = XApis()
result = api.get_user_profile(user_id)
print('get_user_profile result:', result)

result2 = api.list_followers(user_id)
print('list_followers result:', result2)

result3 = api.create_post(user_id, "Test post")
print('create_post result:', result3)