# Inspired by https://developers.google.com/workspace/drive/api/reference/rest/v3

import copy
import copy
import uuid
from typing import Dict, Union, Any, Optional, List
from datetime import datetime
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("GoogleDriveApis")
if not DEFAULT_STATE:
    import json
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, 'Backends', 'diverse_googledrive_state.json')
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            DEFAULT_STATE = json.load(f)
        print(f"Successfully loaded Google Drive state from: {json_file_path}")
    except:
        DEFAULT_STATE = {}

class GoogleDriveApis:
    """
    A dummy API class for simulating Google Drive operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the GoogleDriveApis instance, setting up the in-memory
        data stores and loading the default scenario.
        """
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the Google Drive API, which provides core functionality for managing files and folders."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.
        This allows for resetting the state or initializing with specific data.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain a "users" key.
        """
        DEFAULT_STATE_COPY = copy.deepcopy(scenario)
        self.users = DEFAULT_STATE_COPY.get("users", {})
        print("GoogleDriveApis: Loaded scenario with users and their UUIDs.")

    def _generate_id(self) -> str:
        """
        Generates a unique UUID for dummy entities (files, folders).
        """
        return str(uuid.uuid4())

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """Helper to get user_id from email."""
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """Helper to get user email from user_id."""
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _get_user_drive_data(self, user_id: str) -> Optional[Dict]:
        """
        Helper to get a user's drive data.
        
        Args:
            user_id (str): The internal user ID (UUID).
        """
        return self.users.get(user_id, {}).get("drive_data")

    def _get_user_files(self, user_id: str) -> Optional[Dict]:
        """
        Helper to get a user's files.
        
        Args:
            user_id (str): The internal user ID (UUID).
        """
        drive_data = self._get_user_drive_data(user_id)
        return drive_data.get("files") if drive_data else None

    def _get_user_info(self, user_id: str) -> Optional[Dict]:
        """
        Helper to get a user's drive user info.
        
        Args:
            user_id (str): The internal user ID (UUID).
        """
        drive_data = self._get_user_drive_data(user_id)
        return drive_data.get("user_info") if drive_data else None

    def get_user_info(self, user_id: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves information about the user's Drive.

        Args:
            user_id (str): The internal user ID (UUID).

        Returns:
            Dict: A dictionary containing 'retrieval_status' (bool) and 'user_info' (Dict) if successful.
        """
        user_info = self._get_user_info(user_id)
        if user_info:
            return {"retrieval_status": True, "user_info": copy.deepcopy(user_info)}
        return {"retrieval_status": False, "user_info": {}}

    def list_files(
        self,
        user_id: str,
        query: Optional[str] = None,
        page_size: int = 10,
        page_token: Optional[str] = None,
    ) -> Dict[str, Union[bool, List[Dict], str]]:
        """
        Lists files in the user's Drive.

        Args:
            user_id (str): The internal user ID (UUID).
            query (Optional[str]): A query string to filter results (e.g., "name contains 'report'").
            page_size (int): The maximum number of files to return per page.
            page_token (Optional[str]): The token for the next page of results.

        Returns:
            Dict: A dictionary containing 'retrieval_status' (bool), 'files' (List[Dict]),
                  and 'nextPageToken' (str, optional) if successful.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"retrieval_status": False, "files": []}

        all_files = list(files.values())
        filtered_files = []

        if query:
            # Enhanced query parsing to support multiple Google Drive query formats
            if "name contains '" in query and query.endswith("'"):
                search_term = query.split("name contains '")[1][:-1].lower()
                for file_data in all_files:
                    if search_term in file_data.get("name", "").lower():
                        filtered_files.append(file_data)
            elif "trashed = true" in query.lower():
                for file_data in all_files:
                    if file_data.get("trashed", False):
                        filtered_files.append(file_data)
            elif "trashed = false" in query.lower():
                for file_data in all_files:
                    if not file_data.get("trashed", False):
                        filtered_files.append(file_data)
            elif "starred = true" in query.lower():
                for file_data in all_files:
                    if file_data.get("starred", False):
                        filtered_files.append(file_data)
            elif "shared = true" in query.lower():
                for file_data in all_files:
                    if file_data.get("shared", False):
                        filtered_files.append(file_data)
            elif "mimeType = '" in query and query.endswith("'"):
                mime_type = query.split("mimeType = '")[1][:-1]
                for file_data in all_files:
                    if file_data.get("mimeType") == mime_type:
                        filtered_files.append(file_data)
            elif "'" in query and "' in parents" in query:
                parent_id = query.split("'")[1]
                for file_data in all_files:
                    if parent_id in file_data.get("parents", []):
                        filtered_files.append(file_data)
            else:
                # If query format is not recognized, return all files
                filtered_files = all_files
        else:
            # Default: exclude trashed files unless specifically requested
            filtered_files = [f for f in all_files if not f.get("trashed", False)]

        start_index = 0
        if page_token:
            try:
                start_index = int(page_token)
            except ValueError:
                start_index = 0

        paginated_files = filtered_files[start_index : start_index + page_size]
        next_page_token = str(start_index + page_size) if start_index + page_size < len(filtered_files) else None

        return {
            "retrieval_status": True,
            "files": [copy.deepcopy(f) for f in paginated_files],
            "nextPageToken": next_page_token,
        }

    def get_file(self, fileId: str, user_id: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves a file by its ID from the user's Drive.

        Args:
            fileId (str): The ID of the file to retrieve.
            user_id (str): The internal user ID (UUID).

        Returns:
            Dict: A dictionary containing 'retrieval_status' (bool) and 'file_data' (Dict) if successful.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"retrieval_status": False, "file_data": {}}
        
        file_data = files.get(fileId)
        if file_data:
            # Update viewing metadata when file is accessed
            user_email = self._get_user_email_by_id(user_id)
            file_data["lastViewingUser"] = user_email
            file_data["viewedByMeTime"] = int(datetime.now().timestamp())
            return {"retrieval_status": True, "file_data": copy.deepcopy(file_data)}
        return {"retrieval_status": False, "file_data": {}}

    def create_file(
        self,
        name: str,
        mimeType: str,
        user_id: str,
        parents: Optional[List[str]] = None,
        content: Optional[str] = None,
    ) -> Dict[str, Union[bool, Dict]]:
        """
        Creates a new file in the user's Drive.

        Args:
            name (str): The name of the file.
            mimeType (str): The MIME type of the file.
            user_id (str): The internal user ID (UUID).
            parents (Optional[List[str]]): A list of parent folder IDs. Defaults to root.
            content (Optional[str]): The content of the file (for simplicity).

        Returns:
            Dict: A dictionary containing 'status' (bool) and 'file' (Dict) if successful.
        """
        if user_id not in self.users:
            return {"status": False, "message": "User not found."}

        user_drive_data = self.users[user_id].get("drive_data")
        if user_drive_data is None:
            user_email = self._get_user_email_by_id(user_id)
            user_drive_data = {"user_info": {"name": "", "email": user_email, "storage_quota": {"total": 0, "used": 0}}, "files": {}}
            self.users[user_id]["drive_data"] = user_drive_data
        
        files = user_drive_data.get("files")
        user_info = user_drive_data.get("user_info")
        user_email = self._get_user_email_by_id(user_id)

        new_file_id = self._generate_id()
        current_time = int(datetime.now().timestamp())
        
        new_file = {
            "id": new_file_id,
            "name": name,
            "mimeType": mimeType,
            "createdTime": current_time,
            "modifiedTime": current_time,
            "owners": [{"displayName": user_info.get("name", user_email), "emailAddress": user_email}],
            "parents": parents if parents is not None else ["root"],
            "size": len(content) if content else 0,
            "starred": False,
            "trashed": False,
            "shared": False,
            "version": 1,
            "lastViewingUser": user_email,
            "viewedByMeTime": current_time
        }
        files[new_file_id] = new_file

        user_info["storage_quota"]["used"] += new_file["size"]
        
        print(f"File '{name}' created for user {user_id} with ID: {new_file_id}")
        return {"status": True, "file": new_file}

    def update_file(
        self,
        fileId: str,
        user_id: str,
        addParents: Optional[str] = None,
        removeParents: Optional[str] = None,
        name: Optional[str] = None,
        mimeType: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a file's properties in Google Drive for a specific user.

        Args:
            fileId (str): ID of the file to update.
            user_id (str): The internal user ID (UUID).
            addParents (str, optional): Parents to add to the file. Defaults to None.
            removeParents (str, optional): Parents to remove from the file. Defaults to None.
            name (str, optional): New name for the file.
            mimeType (str, optional): New MIME type for the file.

        Returns:
            Dict: The updated file information if successful,
                  or an error message if the file or user is not found.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"error": "User data not found"}

        if fileId not in files:
            return {"error": "File not found"}

        file = files[fileId]
        user_email = self._get_user_email_by_id(user_id)
        file["modifiedTime"] = int(datetime.now().timestamp())
        file["version"] = file.get("version", 1) + 1  # Increment version on update
        file["lastViewingUser"] = user_email
        file["viewedByMeTime"] = int(datetime.now().timestamp())

        if name is not None:
            file["name"] = name
        if mimeType is not None:
            file["mimeType"] = mimeType

        # Ensure parents is always a list
        if "parents" not in file:
            file["parents"] = ["root"]
        elif not isinstance(file["parents"], list):
            file["parents"] = [file["parents"]] if file["parents"] else ["root"]

        if addParents:
            if addParents not in file["parents"]:
                file["parents"].append(addParents)

        if removeParents and "parents" in file:
            file["parents"] = [p for p in file["parents"] if p != removeParents]
            # Ensure at least one parent exists
            if not file["parents"]:
                file["parents"] = ["root"]

        print(f"File '{fileId}' updated for user {user_id}")
        return {"updated_file": copy.deepcopy(file), "status": "success"}

    def delete_file(self, fileId: str, user_id: str) -> Dict[str, Union[bool, str]]:
        """
        Deletes a file by its ID from the user's Drive.

        Args:
            fileId (str): The ID of the file to delete.
            user_id (str): The internal user ID (UUID).

        Returns:
            Dict: A dictionary indicating success or failure.
        """
        if user_id not in self.users:
            return {"delete_status": False, "message": "User not found."}
        
        user_drive_data = self.users[user_id].get("drive_data")
        if user_drive_data is None:
            return {"delete_status": False, "message": "User data not found."}

        files = user_drive_data.get("files")
        user_info = user_drive_data.get("user_info")

        if fileId in files:
            deleted_file_size = files[fileId].get("size", 0)
            del files[fileId]

            user_info["storage_quota"]["used"] -= deleted_file_size

            print(f"File '{fileId}' deleted for user {user_id}")
            return {"delete_status": True, "message": "File deleted successfully."}
        return {"delete_status": False, "message": "File not found."}

    def copy_file(
        self, fileId: str, name: str, user_id: str, parents: Optional[List[str]] = None
    ) -> Dict[str, Union[bool, Dict]]:
        """
        Copies an existing file in the user's Drive.

        Args:
            fileId (str): The ID of the file to copy.
            name (str): The name for the new copied file.
            user_id (str): The internal user ID (UUID).
            parents (Optional[List[str]]): A list of parent folder IDs for the copy. Defaults to root.

        Returns:
            Dict: A dictionary containing 'copy_status' (bool) and 'copied_file_data' (Dict) if successful.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"status": False, "message": "User data not found."}

        original_file = files.get(fileId)
        if not original_file:
            return {"status": False, "message": "Original file not found."}

        new_file_id = self._generate_id()
        current_time = int(datetime.now().timestamp())
        user_email = self._get_user_email_by_id(user_id)

        copied_file = copy.deepcopy(original_file)
        copied_file["id"] = new_file_id
        copied_file["name"] = name
        copied_file["createdTime"] = current_time
        copied_file["modifiedTime"] = current_time
        copied_file["parents"] = parents if parents is not None else ["root"]
        copied_file["version"] = 1  # Reset version for copy
        copied_file["lastViewingUser"] = user_email
        copied_file["viewedByMeTime"] = current_time
        copied_file["shared"] = False  # Reset sharing for copy

        files[new_file_id] = copied_file

        if user_id in self.users:
            user_info = self.users[user_id]["drive_data"].get("user_info")
            if user_info:
                user_info["storage_quota"]["used"] += copied_file.get("size", 0)

        print(f"File '{fileId}' copied to '{name}' with ID: {new_file_id} for user {user_id}")
        return {"status": True, "file": copied_file}

    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        self._load_scenario(DEFAULT_STATE)
        print("GoogleDriveApis: All dummy data reset to default state.")
        return {"reset_status": True}

    def star_file(self, fileId: str, user_id: str) -> Dict[str, Union[bool, str]]:
        """
        Stars or unstars a file in Google Drive.

        Args:
            fileId (str): The ID of the file to star/unstar.
            user_id (str): The internal user ID (UUID).

        Returns:
            Dict: A dictionary indicating success or failure.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"star_status": False, "message": "User data not found."}

        if fileId not in files:
            return {"star_status": False, "message": "File not found."}

        file = files[fileId]
        user_email = self._get_user_email_by_id(user_id)
        file["starred"] = not file.get("starred", False)
        file["modifiedTime"] = int(datetime.now().timestamp())
        file["lastViewingUser"] = user_email
        file["viewedByMeTime"] = int(datetime.now().timestamp())

        status = "starred" if file["starred"] else "unstarred"
        print(f"File '{fileId}' {status} for user {user_id}")
        return {"star_status": True, "message": f"File {status} successfully.", "starred": file["starred"]}

    def trash_file(self, fileId: str, user_id: str) -> Dict[str, Union[bool, str]]:
        """
        Moves a file to trash or restores it from trash.

        Args:
            fileId (str): The ID of the file to trash/restore.
            user_id (str): The internal user ID (UUID).

        Returns:
            Dict: A dictionary indicating success or failure.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"trash_status": False, "message": "User data not found."}

        if fileId not in files:
            return {"trash_status": False, "message": "File not found."}

        file = files[fileId]
        user_email = self._get_user_email_by_id(user_id)
        file["trashed"] = not file.get("trashed", False)
        file["modifiedTime"] = int(datetime.now().timestamp())
        file["lastViewingUser"] = user_email
        file["viewedByMeTime"] = int(datetime.now().timestamp())

        status = "trashed" if file["trashed"] else "restored"
        print(f"File '{fileId}' {status} for user {user_id}")
        return {"trash_status": True, "message": f"File {status} successfully.", "trashed": file["trashed"]}

    def share_file(self, fileId: str, email: str, user_id: str, role: str = "reader") -> Dict[str, Union[bool, str]]:
        """
        Shares a file with another user.

        Args:
            fileId (str): The ID of the file to share.
            email (str): Email address of the user to share with.
            user_id (str): The internal user ID (UUID) of the file owner.
            role (str): The role to grant ("reader", "writer", "owner").

        Returns:
            Dict: A dictionary indicating success or failure.
        """
        # Validate role
        valid_roles = ["reader", "writer", "owner"]
        if role not in valid_roles:
            return {"share_status": False, "message": f"Invalid role '{role}'. Valid roles are: {', '.join(valid_roles)}"}

        files = self._get_user_files(user_id)
        if files is None:
            return {"share_status": False, "message": "User data not found."}

        if fileId not in files:
            return {"share_status": False, "message": "File not found."}

        file = files[fileId]
        user_email = self._get_user_email_by_id(user_id)
        
        # Add the new owner/collaborator
        if "owners" not in file:
            file["owners"] = []
        
        # Check if already shared with this user
        existing_owner = next((owner for owner in file["owners"] if owner.get("emailAddress") == email), None)
        
        if existing_owner:
            return {"share_status": False, "message": "File already shared with this user."}

        # Find the user's display name if they exist in our system
        shared_user_name = "External User"
        for user_data in self.users.values():
            if user_data.get("email") == email:
                shared_user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                break

        file["owners"].append({
            "displayName": shared_user_name,
            "emailAddress": email,
            "role": role
        })
        
        file["shared"] = True
        file["modifiedTime"] = int(datetime.now().timestamp())
        file["lastViewingUser"] = user_email
        file["viewedByMeTime"] = int(datetime.now().timestamp())

        print(f"File '{fileId}' shared with {email} as {role} for user {user_id}")
        return {"share_status": True, "message": f"File shared with {email} successfully."}

    def get_file_revisions(self, fileId: str, user_id: str) -> Dict[str, Union[bool, List, str]]:
        """
        Gets revision history for a file (simulated).

        Args:
            fileId (str): The ID of the file.
            user_id (str): The internal user ID (UUID).

        Returns:
            Dict: A dictionary with revision history.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"retrieval_status": False, "revisions": [], "message": "User data not found."}

        if fileId not in files:
            return {"retrieval_status": False, "revisions": [], "message": "File not found."}

        file = files[fileId]
        
        # Simulate revision history based on version number
        revisions = []
        current_version = file.get("version", 1)
        created_time = file.get("createdTime", int(datetime.now().timestamp()))
        modified_time = file.get("modifiedTime", int(datetime.now().timestamp()))
        
        for v in range(1, current_version + 1):
            revision_time = created_time + (modified_time - created_time) * (v - 1) / max(1, current_version - 1)
            revisions.append({
                "id": f"{fileId}_v{v}",
                "mimeType": file.get("mimeType"),
                "modifiedTime": int(revision_time),
                "size": file.get("size", 0),
                "version": v
            })

        return {"retrieval_status": True, "revisions": revisions}

    def create_folder(self, name: str, user_id: str, parents: Optional[List[str]] = None) -> Dict[str, Union[bool, Dict]]:
        """
        Creates a new folder in the user's Drive.

        Args:
            name (str): The name of the folder.
            user_id (str): The internal user ID (UUID).
            parents (Optional[List[str]]): A list of parent folder IDs. Defaults to root.

        Returns:
            Dict: A dictionary containing 'creation_status' (bool) and 'folder_data' (Dict) if successful.
        """
        return self.create_file(
            name=name,
            mimeType="application/vnd.google-apps.folder",
            user_id=user_id,
            parents=parents,
            content=None,
        )