import re

# Read the file
with open('YouTubeApis.py', 'r') as f:
    content = f.read()

# Replace "success": True with "status": True
content = re.sub(r'"success":\s*True', '"status": True', content)

# Replace "success": False with "status": False  
content = re.sub(r'"success":\s*False', '"status": False', content)

# Replace "status": "success" with "status": True
content = re.sub(r'"status":\s*"success"', '"status": True', content)

# Replace "status": "error" with "status": False
content = re.sub(r'"status":\s*"error"', '"status": False', content)

# Replace "error": with "message": for consistency
content = re.sub(r'"error":\s*', '"message": ', content)

# Write back
with open('YouTubeApis.py', 'w') as f:
    f.write(content)

print("Replacements done")