import json
import os

# List of prompt files to update
prompt_files = [
    'Prompts/gmail_prompts.json',
    'Prompts/communilink_prompts.json',
    'Prompts/google_calendar_prompts.json',
    'Prompts/google_drive_prompts.json',
    'Prompts/simple_notes_prompts.json',
    'Prompts/smart_things_prompts.json',
    'Prompts/spotify_prompts.json',
    'Prompts/tesla_fleet_prompts.json',
    'Prompts/venmo_prompts.json',
    'Prompts/x_prompts.json',
    'Prompts/youtube_prompts.json'
]

total_updated = 0

for file_path in prompt_files:
    if not os.path.exists(file_path):
        print(f"Skipping {file_path} - file not found")
        continue
    
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    file_updates = 0
    
    # Update multistep (case-insensitive check for key)
    for key in ['multistep', 'Multistep']:
        if key in data:
            for item in data[key]:
                user_id = item.get('context', {}).get('user_id')
                if user_id and 'ground_truth' in item:
                    # Check if get_user_by_id is not already first
                    if not item['ground_truth'][0].startswith('get_user_by_id'):
                        item['ground_truth'].insert(0, f"get_user_by_id('{user_id}')")
                        file_updates += 1
    
    # Update multiturn (case-insensitive check for key)
    for key in ['multiturn', 'Multiturn']:
        if key in data:
            for item in data[key]:
                user_id = item.get('context', {}).get('user_id')
                if user_id and 'ground_truth' in item:
                    if not item['ground_truth'][0].startswith('get_user_by_id'):
                        item['ground_truth'].insert(0, f"get_user_by_id('{user_id}')")
                        file_updates += 1
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
    print(f"  Updated {file_updates} test cases in {file_path}")
    total_updated += file_updates

print(f"\n✅ Complete! Updated {total_updated} test cases across {len(prompt_files)} files")
