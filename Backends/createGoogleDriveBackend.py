# Current timestamp for realistic date generation
current_timestamp_s = int(datetime.now().timestamp())

DEFAULT_STATE: Dict[str, Any] = {
    "users": {},
}

_user_email_to_uuid_map = {}

def generate_random_email(first_name, last_name):
    domains = ["cloudrive.com", "syncspace.net", "datahub.org", "filevault.co", "driveplus.app"]
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"

def generate_random_past_timestamp(max_days_ago=365):
    """Generates a Unix timestamp in the past."""
    return int((datetime.now() - timedelta(days=random.randint(1, max_days_ago), 
                                          hours=random.randint(0, 23), 
                                          minutes=random.randint(0, 59), 
                                          seconds=random.randint(0, 59))).timestamp())

def _create_user_data(email: str, first_name: str, last_name: str, drive_data: Dict[str, Any]):
    user_id = str(uuid.uuid4())
    _user_email_to_uuid_map[email] = user_id

    processed_drive_data = copy.deepcopy(drive_data)

    # Ensure user_info is correctly populated
    if "user_info" not in processed_drive_data:
        processed_drive_data["user_info"] = {}
    processed_drive_data["user_info"]["emailAddress"] = email
    processed_drive_data["user_info"]["name"] = f"{first_name} {last_name}"
    
    # Ensure storage_quota is present
    if "storage_quota" not in processed_drive_data["user_info"]:
        processed_drive_data["user_info"]["storage_quota"] = {
            "total": random.choice([50, 100, 200, 500]) * 1024 * 1024 * 1024, # 50GB to 500GB
            "used": 0 # Will be updated after files are processed
        }


    new_files = {}
    
    # Create a map for old folder IDs to new UUIDs
    _folder_id_map = {"root": "root"} # "root" is a special parent ID
    
    # First pass: Process existing folders and assign them new UUIDs
    for old_file_id, file_data in processed_drive_data.get("files", {}).items():
        if file_data.get("mimeType") == "application/vnd.google-apps.folder":
            new_folder_id = str(uuid.uuid4())
            _folder_id_map[old_file_id] = new_folder_id
            
            file_data_copy = copy.deepcopy(file_data)
            file_data_copy["id"] = new_folder_id
            new_files[new_folder_id] = file_data_copy

    # Second pass: Process other files and link them to new folder UUIDs
    for old_file_id, file_data in processed_drive_data.get("files", {}).items():
        # Skip folders already processed
        if file_data.get("mimeType") == "application/vnd.google-apps.folder":
            continue

        new_file_id = str(uuid.uuid4())
        file_data_copy = copy.deepcopy(file_data)
        file_data_copy["id"] = new_file_id

        # Update owners display name
        if "owners" in file_data_copy and isinstance(file_data_copy["owners"], list):
            for owner in file_data_copy["owners"]:
                if owner.get("emailAddress") == email:
                    owner["displayName"] = f"{first_name} {last_name}"
        
        # Adjust timestamps
        # Ensure createdTime and modifiedTime are actual timestamps (integers)
        created_time = file_data_copy.get("createdTime", current_timestamp_s - random.randint(86400 * 7, 86400 * 365)) # Default 1 week to 1 year ago
        modified_time = file_data_copy.get("modifiedTime", created_time + random.randint(60, 86400 * 30)) # Default 1 min to 1 month after creation

        if modified_time < created_time: # Ensure modified time is not before created time
            modified_time = created_time + random.randint(60, 3600 * 24) # At least 1 minute later, up to 1 day

        file_data_copy["createdTime"] = created_time
        file_data_copy["modifiedTime"] = modified_time

        # Resolve parent IDs to new UUIDs
        if "parents" in file_data_copy and isinstance(file_data_copy["parents"], list):
            resolved_parents = []
            for parent_id_old in file_data_copy["parents"]:
                resolved_parents.append(_folder_id_map.get(parent_id_old, "root")) # Default to root if not found
            file_data_copy["parents"] = list(set(resolved_parents)) # Remove duplicates

        new_files[new_file_id] = file_data_copy

    processed_drive_data["files"] = new_files
    
    # Calculate used storage
    used_storage = sum(f.get("size", 0) for f in processed_drive_data["files"].values())
    processed_drive_data["user_info"]["storage_quota"]["used"] = used_storage


    return user_id, {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "drive_data": processed_drive_data,
        "drive_last_activity": generate_random_past_timestamp(7), # New field: last activity in Drive (up to 7 days ago)
        "drive_folder_count": len([f for f in processed_drive_data["files"].values() if f.get("mimeType") == "application/vnd.google-apps.folder"]) # New field
    }

# --- Initial Users (provided in the prompt) ---
users_initial_data = [
    ("alice.smith@cloudrive.com", "Alice", "Smith", {
        "user_info": {
            "name": "Alice Smith",
            "emailAddress": "alice.smith@cloudrive.com",
            "storage_quota": {"total": 100 * 1024 * 1024 * 1024, "used": 50 * 1024 * 1024}
        },
        "files": {
            "folder_finance_reports": { # Added an initial folder
                "id": "Finance_Reports",
                "name": "Finance Reports",
                "mimeType": "application/vnd.google-apps.folder",
                "createdTime": current_timestamp_s - 86400 * 60,
                "modifiedTime": current_timestamp_s - 86400 * 10,
                "owners": [], # Owners will be populated by the script
                "parents": ["root"],
                "size": 0 # Folders have no size
            },
            "file_alice_project_plan.docx": {
                "id": "file_alice_project_plan.docx",
                "name": "Project_Plan_Q3.docx",
                "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "createdTime": 0, # Placeholder, will be generated
                "modifiedTime": 0, # Placeholder, will be generated
                "owners": [{"displayName": "Alice Smith", "emailAddress": "alice.smith@cloudrive.com"}],
                "parents": ["root"],
                "size": 5 * 1024 * 1024,
                "starred": True, # New field for initial data
                "shared": True, # New field for initial data
                "description": "Master plan for Q3 project initiatives."
            },
            "file_alice_budget_sheet.xlsx": {
                "id": "file_alice_budget_sheet.xlsx",
                "name": "Annual_Budget_2025.xlsx",
                "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "createdTime": 0,
                "modifiedTime": 0,
                "owners": [{"displayName": "Alice Smith", "emailAddress": "alice.smith@cloudrive.com"}],
                "parents": ["Finance_Reports"], # This refers to the folder_finance_reports
                "size": 2 * 1024 * 1024,
                "trashed": False
            }
        }
    }),
    ("bob.jones@cloudrive.com", "Bob", "Jones", {
        "user_info": {
            "name": "Bob Jones",
            "emailAddress": "bob.jones@cloudrive.com",
            "storage_quota": {"total": 50 * 1024 * 1024 * 1024, "used": 10 * 1024 * 1024}
        },
        "files": {
            "file_bob_presentation.pptx": {
                "id": "file_bob_presentation.pptx",
                "name": "Q2_Results_Presentation.pptx",
                "mimeType": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "createdTime": 0,
                "modifiedTime": 0,
                "owners": [{"displayName": "Bob Jones", "emailAddress": "bob.jones@cloudrive.com"}],
                "parents": ["root"],
                "size": 10 * 1024 * 1024,
                "shared": True
            },
            "file_bob_meeting_notes.txt": {
                "id": "file_bob_meeting_notes.txt",
                "name": "Meeting_Notes_ProjectX.txt",
                "mimeType": "text/plain",
                "createdTime": 0,
                "modifiedTime": 0,
                "owners": [{"displayName": "Bob Jones", "emailAddress": "bob.jones@cloudrive.com"}],
                "parents": ["root"],
                "size": 50 * 1024,
                "trashed": True,
                "description": "Notes from the Project X kick-off meeting."
            }
        }
    })
]

# Populate initial users
for email, first_name, last_name, drive_data in users_initial_data:
    user_id, user_data = _create_user_data(email, first_name, last_name, drive_data)
    DEFAULT_STATE["users"][user_id] = user_data

# --- Generate 48 more diverse and realistic users ---
first_names = ["Sophia", "Liam", "Olivia", "Noah", "Ava", "Jackson", "Isabella", "Aiden", "Mia", "Lucas", "Harper", "Ethan", "Evelyn", "Mason", "Abigail", "Caleb", "Charlotte", "Logan", "Amelia", "Michael", "Ella", "Jacob", "Aria", "Daniel", "Chloe", "Samuel", "Grace", "David", "Victoria", "Joseph", "Penelope", "Matthew", "Riley", "Benjamin", "Layla", "Andrew", "Lily", "Gabriel", "Natalie", "Christopher", "Hannah", "James", "Zoe", "Ryan", "Scarlett", "Nathan", "Addison", "Christian", "Aubrey", "Joshua"]
last_names = ["Chen", "Kim", "Singh", "Lopez", "Garcia", "Nguyen", "Davis", "Jackson", "Harris", "White", "Moore", "Clark", "Lewis", "Baker", "Adams", "Hill", "Nelson", "Carter", "Mitchell", "Roberts", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders"]
file_mimetypes = {
    "document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "presentation": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "pdf": "application/pdf",
    "image_jpeg": "image/jpeg",
    "image_png": "image/png",
    "code_py": "text/x-python",
    "code_js": "application/javascript",
    "text": "text/plain"
}
file_names_base = {
    "document": ["Report", "Minutes", "Proposal", "Contract", "Draft"],
    "spreadsheet": ["Budget", "Tracker", "Data Analysis", "Invoice", "Inventory"],
    "presentation": ["Quarterly Review", "Pitch Deck", "Training", "Strategy"],
    "pdf": ["Manual", "Ebook", "Whitepaper", "Brochure"],
    "image_jpeg": ["Photo", "Screenshot", "Design"],
    "image_png": ["Diagram", "Logo", "Icon"],
    "code_py": ["script", "model"],
    "code_js": ["frontend", "backend"],
    "text": ["Notes", "Log", "Readme"]
}
file_descriptions = [
    "Important internal document.", "Shared with client for review.",
    "Draft for feedback.", "Final version, do not modify.",
    "Contains sensitive financial data.", "Marketing collateral for new product.",
    "Team brainstorming session notes.", "Automatically generated report.",
    "Legal agreement terms and conditions.", "Personal notes on a project."
]

current_user_emails = list(_user_email_to_uuid_map.keys())

for i in range(48): # Generate 48 additional users (2 existing + 48 new = 50 total)
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = generate_random_email(first, last)
    
    # Ensure unique email
    while email in _user_email_to_uuid_map:
        email = generate_random_email(first, last)

    new_drive_data = {
        "user_info": {
            "emailAddress": email,
            "name": f"{first} {last}",
            "storage_quota": {
                "total": random.choice([50, 100, 200, 500]) * 1024 * 1024 * 1024, # 50GB to 500GB
                "used": 0 # Will be updated later
            }
        },
        "files": {}
    }

    # Generate folders for the user
    num_folders = random.randint(2, 8)
    user_folder_ids = ["root"] # Always start with root
    
    for f_idx in range(num_folders):
        folder_id_temp = str(uuid.uuid4())
        folder_name = random.choice(["Projects", "Documents", "Photos", "Work", "Personal", "Archive", "Shared with Me", "Client Data"])
        if f_idx > 0:
             folder_name += f"_{random.randint(1,9)}" # Make names unique
        
        # Ensure created/modified times are within a realistic range
        created_time_folder = generate_random_past_timestamp(max_days_ago=730)
        modified_time_folder = random.randint(created_time_folder, current_timestamp_s) # Must be >= created time

        new_drive_data["files"][folder_id_temp] = {
            "id": folder_id_temp,
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "createdTime": created_time_folder,
            "modifiedTime": modified_time_folder,
            "owners": [{"displayName": f"{first} {last}", "emailAddress": email}],
            "parents": [random.choice(user_folder_ids)], # Can be nested
            "size": 0,
            "starred": random.random() < 0.1, # 10% chance
            "description": f"Folder for {folder_name}." if random.random() < 0.5 else None
        }
        user_folder_ids.append(folder_id_temp) # Add new folder to potential parents

    # Generate files for the user
    num_files = random.randint(5, 50)
    for file_idx in range(num_files):
        file_type_key = random.choice(list(file_mimetypes.keys()))
        mime_type = file_mimetypes[file_type_key]
        
        base_name = random.choice(file_names_base[file_type_key])
        file_name = f"{base_name}_{random.randint(100, 999)}.{file_type_key.split('_')[-1]}" if "_" in file_type_key else f"{base_name}_{random.randint(100, 999)}.txt"
        
        file_size = random.randint(10 * 1024, 100 * 1024 * 1024) # 10KB to 100MB
        
        file_id_temp = str(uuid.uuid4())
        
        # Timestamps for files (more recent than folders often)
        created_time_file = generate_random_past_timestamp(max_days_ago=365)
        modified_time_file = random.randint(created_time_file, current_timestamp_s)
        if modified_time_file < created_time_file:
            modified_time_file = created_time_file + random.randint(60, 3600 * 24)

        owners_list = [{"displayName": f"{first} {last}", "emailAddress": email}]
        
        # Add shared owners randomly
        num_shared_owners = random.randint(0, 2)
        if num_shared_owners > 0 and current_user_emails:
            potential_shared_emails = [e for e in current_user_emails if e != email]
            if potential_shared_emails:
                for _ in range(num_shared_owners):
                    shared_email = random.choice(potential_shared_emails)
                    if shared_email in _user_email_to_uuid_map: # Check if it's an internal user
                        # Try to get the actual name if it's an internal user
                        shared_user_data = next((u_data for u_data in DEFAULT_STATE["users"].values() if u_data["email"] == shared_email), None)
                        if shared_user_data:
                            owners_list.append({"displayName": f"{shared_user_data['first_name']} {shared_user_data['last_name']}", "emailAddress": shared_email})
                        else: # Fallback for external or not-yet-created users
                            owners_list.append({"displayName": "Shared User", "emailAddress": shared_email})
                    else:
                        owners_list.append({"displayName": "External Collaborator", "emailAddress": shared_email})
        
        # Randomly assign parents, ensuring it's a valid folder ID or 'root'
        file_parents = [random.choice(user_folder_ids)]
        
        new_drive_data["files"][file_id_temp] = {
            "id": file_id_temp,
            "name": file_name,
            "mimeType": mime_type,
            "createdTime": created_time_file,
            "modifiedTime": modified_time_file,
            "owners": owners_list,
            "parents": file_parents,
            "size": file_size,
            "starred": random.random() < 0.15, # 15% chance
            "trashed": random.random() < 0.05, # 5% chance
            "shared": random.random() < 0.25, # 25% chance of being explicitly shared
            "description": random.choice(file_descriptions) if random.random() < 0.6 else None, # 60% chance of description
            "version": random.randint(1, 10), # New field: File version
            "lastViewingUser": random.choice([email] + [e["emailAddress"] for e in owners_list if e["emailAddress"] != email]) if len(owners_list) > 1 else email, # New field: Who last viewed
            "viewedByMeTime": int(datetime.now().timestamp() - random.randint(60, 86400 * 5)) # New field: Last time viewed by current user
        }

    user_id, user_data = _create_user_data(email, first, last, new_drive_data)
    DEFAULT_STATE["users"][user_id] = user_data
    current_user_emails.append(email) # Add new user to possible shared emails for subsequent users

# --- Output the generated DEFAULT_STATE ---
# This part is crucial: we are printing the full, static DEFAULT_STATE
# to a JSON file so you can load it consistently.
import json

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")

# Save the generated DEFAULT_STATE to a JSON file
# output_filename = 'diverse_google_drive_state.json'
# with open(output_filename, 'w') as f:
#     json.dump(DEFAULT_STATE, f, indent=2)

# print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

# Optionally, print a sample user's data for review
# if DEFAULT_STATE["users"]:
#     sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(0, len(DEFAULT_STATE["users"]) - 1)]
#     print(f"\nSample data for user {DEFAULT_STATE['users'][sample_user_id]['first_name']} {DEFAULT_STATE['users'][sample_user_id]['last_name']}:")
#     print(json.dumps(DEFAULT_STATE["users"][sample_user_id], indent=2))
