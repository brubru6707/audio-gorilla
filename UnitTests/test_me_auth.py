#!/usr/bin/env python3
"""
Demo script showing the 'me' authentication feature in GmailApis.
"""

from GmailApis import GmailApis

print("=== Testing Gmail API with 'me' authentication ===\n")

# Create API instance
api = GmailApis()

# 1. Check default authenticated user
print("1. Default authenticated user:")
profile = api.get_profile('me')
print(f"   Email: {profile['emailAddress']}\n")

# 2. Authenticate as different user
print("2. Authenticating as different user...")
result = api.authenticate('kenji.tanaka32@luxury-travel.co')
print(f"   {result['message']}\n")

# 3. Get profile using 'me'
print("3. Get profile using 'me':")
profile = api.get_profile('me')
print(f"   Email: {profile['emailAddress']}\n")

# 4. List messages using 'me'
print("4. List messages using 'me':")
msgs = api.list_messages('me', max_results=3)
print(f"   Found {len(msgs['messages'])} messages\n")

# 5. Get first message using 'me'
print("5. Get first message using 'me':")
if msgs['messages']:
    msg = api.get_message('me', msgs['messages'][0]['id'], 'minimal')
    print(f"   Message ID: {msg['id']}")
    print(f"   Thread ID: {msg['threadId']}\n")

# 6. Create a label using 'me'
print("6. Create a label using 'me':")
label_result = api.create_label('me', 'Important Projects')
print(f"   Created label: {label_result['name']} (ID: {label_result['id']})\n")

# 7. Send a message using 'me'
print("7. Send a message using 'me':")
send_result = api.send_message('me', {
    'to': 'anya.sharma82@marketing-automation.solutions',
    'subject': 'Testing me authentication',
    'body': 'This message was sent using the me parameter!'
})
print(f"   Sent message ID: {send_result['id']}\n")

print("=== All 'me' operations successful! ===")
