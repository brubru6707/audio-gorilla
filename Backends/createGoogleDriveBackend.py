import random
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any
import copy
from fake_data import first_names, last_names, domains, first_and_last_names, user_count, file_mimetypes, file_names_base

current_timestamp_s = int(datetime.now().timestamp())

DEFAULT_STATE: Dict[str, Any] = {
    "users": {},
}

_user_email_to_uuid_map = {}

def generate_random_email(first_name, last_name):
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"

def generate_random_past_timestamp(max_days_ago=365):
    return int((datetime.now() - timedelta(days=random.randint(1, max_days_ago), 
                                          hours=random.randint(0, 23), 
                                          minutes=random.randint(0, 59), 
                                          seconds=random.randint(0, 59))).timestamp())

def _create_user_data(email: str, first_name: str, last_name: str, drive_data: Dict[str, Any]):
    user_id = str(uuid.uuid4())
    _user_email_to_uuid_map[email] = user_id

    processed_drive_data = copy.deepcopy(drive_data)

    if "user_info" not in processed_drive_data:
        processed_drive_data["user_info"] = {}
    processed_drive_data["user_info"]["emailAddress"] = email
    processed_drive_data["user_info"]["name"] = f"{first_name} {last_name}"
    
    if "storage_quota" not in processed_drive_data["user_info"]:
        processed_drive_data["user_info"]["storage_quota"] = {
            "total": random.choice([50, 100, 200, 500]) * 1024 * 1024 * 1024,
            "used": 0
        }


    new_files = {}
    
    _folder_id_map = {"root": "root"}
    
    for old_file_id, file_data in processed_drive_data.get("files", {}).items():
        if file_data.get("mimeType") == "application/vnd.google-apps.folder":
            new_folder_id = str(uuid.uuid4())
            _folder_id_map[old_file_id] = new_folder_id
            
            file_data_copy = copy.deepcopy(file_data)
            file_data_copy["id"] = new_folder_id
            new_files[new_folder_id] = file_data_copy

    for old_file_id, file_data in processed_drive_data.get("files", {}).items():
        if file_data.get("mimeType") == "application/vnd.google-apps.folder":
            continue

        new_file_id = str(uuid.uuid4())
        file_data_copy = copy.deepcopy(file_data)
        file_data_copy["id"] = new_file_id

        if "owners" in file_data_copy and isinstance(file_data_copy["owners"], list):
            for owner in file_data_copy["owners"]:
                if owner.get("emailAddress") == email:
                    owner["displayName"] = f"{first_name} {last_name}"
        
        created_time = file_data_copy.get("createdTime", current_timestamp_s - random.randint(86400 * 7, 86400 * 365))
        modified_time = file_data_copy.get("modifiedTime", created_time + random.randint(60, 86400 * 30))

        if modified_time < created_time:
            modified_time = created_time + random.randint(60, 3600 * 24)

        file_data_copy["createdTime"] = created_time
        file_data_copy["modifiedTime"] = modified_time

        if "parents" in file_data_copy and isinstance(file_data_copy["parents"], list):
            resolved_parents = []
            for parent_id_old in file_data_copy["parents"]:
                resolved_parents.append(_folder_id_map.get(parent_id_old, "root"))
            file_data_copy["parents"] = list(set(resolved_parents))

        new_files[new_file_id] = file_data_copy

    processed_drive_data["files"] = new_files
    
    used_storage = sum(f.get("size", 0) for f in processed_drive_data["files"].values())
    processed_drive_data["user_info"]["storage_quota"]["used"] = used_storage


    return user_id, {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "drive_data": processed_drive_data,
        "drive_last_activity": generate_random_past_timestamp(7),
        "drive_folder_count": len([f for f in processed_drive_data["files"].values() if f.get("mimeType") == "application/vnd.google-apps.folder"])
    }

current_user_emails = list(_user_email_to_uuid_map.keys())

def generate_user(first_name=None, last_name=None, email=None, balance=None):
    first = random.choice(first_names) if first_name is None else first_name
    last = random.choice(last_names) if last_name is None else last_name
    email = generate_random_email(first, last) if email is None else email

    while email in _user_email_to_uuid_map:
        email = generate_random_email(first, last)

    new_drive_data = {
        "user_info": {
            "emailAddress": email,
            "name": f"{first} {last}",
            "storage_quota": {
                "total": random.choice([50, 100, 200, 500]) * 1024 * 1024 * 1024,
                "used": 0
            }
        },
        "files": {}
    }

    num_folders = random.randint(2, 8)
    user_folder_ids = ["root"]
    
    for f_idx in range(num_folders):
        folder_id_temp = str(uuid.uuid4())
        folder_name = random.choice(["Projects", "Documents", "Photos", "Work", "Personal", "Archive", "Shared with Me", "Client Data"])
        if f_idx > 0:
             folder_name += f"_{random.randint(1,9)}"
        
        created_time_folder = generate_random_past_timestamp(max_days_ago=730)
        modified_time_folder = random.randint(created_time_folder, current_timestamp_s)

        new_drive_data["files"][folder_id_temp] = {
            "id": folder_id_temp,
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "createdTime": created_time_folder,
            "modifiedTime": modified_time_folder,
            "owners": [{"displayName": f"{first} {last}", "emailAddress": email}],
            "parents": [random.choice(user_folder_ids)],
            "size": 0,
            "starred": random.random() < 0.1,
            "description": f"Folder for {folder_name}." if random.random() < 0.5 else None
        }
        user_folder_ids.append(folder_id_temp)

    num_files = random.randint(5, 50)
    for file_idx in range(num_files):
        file_type_key = random.choice(list(file_mimetypes.keys()))
        mime_type = file_mimetypes[file_type_key]
        
        base_name = random.choice(file_names_base[file_type_key])
        file_name = f"{base_name}_{random.randint(100, 999)}.{file_type_key.split('_')[-1]}" if "_" in file_type_key else f"{base_name}_{random.randint(100, 999)}.txt"
        
        file_size = random.randint(10 * 1024, 100 * 1024 * 1024)
        
        file_id_temp = str(uuid.uuid4())
        
        created_time_file = generate_random_past_timestamp(max_days_ago=365)
        modified_time_file = random.randint(created_time_file, current_timestamp_s)
        if modified_time_file < created_time_file:
            modified_time_file = created_time_file + random.randint(60, 3600 * 24)

        owners_list = [{"displayName": f"{first} {last}", "emailAddress": email}]
        
        num_shared_owners = random.randint(0, 2)
        if num_shared_owners > 0 and current_user_emails:
            potential_shared_emails = [e for e in current_user_emails if e != email]
            if potential_shared_emails:
                for _ in range(num_shared_owners):
                    shared_email = random.choice(potential_shared_emails)
                    if shared_email in _user_email_to_uuid_map:
                        shared_user_data = next((u_data for u_data in DEFAULT_STATE["users"].values() if u_data["email"] == shared_email), None)
                        if shared_user_data:
                            owners_list.append({"displayName": f"{shared_user_data['first_name']} {shared_user_data['last_name']}", "emailAddress": shared_email})
                        else:
                            owners_list.append({"displayName": "Shared User", "emailAddress": shared_email})
                    else:
                        owners_list.append({"displayName": "External Collaborator", "emailAddress": shared_email})
        
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
            "starred": random.random() < 0.15,
            "trashed": random.random() < 0.05,
            "shared": random.random() < 0.25,
            "version": random.randint(1, 10),
            "lastViewingUser": random.choice([email] + [e["emailAddress"] for e in owners_list if e["emailAddress"] != email]) if len(owners_list) > 1 else email,
            "viewedByMeTime": int(datetime.now().timestamp() - random.randint(60, 86400 * 5))
        }
    current_user_emails.append(email)
    return _create_user_data(email, first, last, new_drive_data)


for i in range(user_count + len(first_and_last_names)):
    if user_count < i:
        first_name, _, last_name = first_and_last_names[i - user_count].partition(" ")
        user_id, user_data = generate_user(first_name=first_name, last_name=last_name)
    else:
        user_id, user_data = generate_user()
    DEFAULT_STATE["users"][user_id] = user_data    

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")

output_filename = 'diverse_google_drive_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

if DEFAULT_STATE["users"]:
    sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(0, len(DEFAULT_STATE["users"]) - 1)]
