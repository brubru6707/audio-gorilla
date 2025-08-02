import time
import copy
import time
import copy
import uuid
from typing import Dict, Union, Any, Optional, List
from datetime import datetime
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("GoogleCalendarApis")

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
        """Helper to get a user's drive data."""
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return None
        return self.users.get(internal_user_id, {}).get("drive_data")

    def _get_user_files(self, user_id: str) -> Optional[Dict]:
        """Helper to get a user's files."""
        drive_data = self._get_user_drive_data(user_id)
        return drive_data.get("files") if drive_data else None

    def _get_user_info(self, user_id: str) -> Optional[Dict]:
        """Helper to get a user's drive user info."""
        drive_data = self._get_user_drive_data(user_id)
        return drive_data.get("user_info") if drive_data else None

    def get_user_info(self, user_id: str = "me") -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves information about the authenticated user's Drive.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict: A dictionary containing 'retrieval_status' (bool) and 'user_info' (Dict) if successful.
        """
        user_info = self._get_user_info(user_id)
        if user_info:
            return {"retrieval_status": True, "user_info": copy.deepcopy(user_info)}
        return {"retrieval_status": False, "user_info": {}}

    def list_files(
        self,
        user_id: str = "me",
        query: Optional[str] = None,
        page_size: int = 10,
        page_token: Optional[str] = None,
    ) -> Dict[str, Union[bool, List[Dict], str]]:
        """
        Lists files in the user's Drive.

        Args:
            user_id (str): User's email address or 'me' for the authenticated user.
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
            if "name contains '" in query and query.endswith("'"):
                search_term = query.split("name contains '")[1][:-1].lower()
                for file_data in all_files:
                    if search_term in file_data.get("name", "").lower():
                        filtered_files.append(file_data)
            else:
                filtered_files = all_files
        else:
            filtered_files = all_files

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

    def get_file(self, fileId: str, user_id: str = "me") -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves a file by its ID from the user's Drive.

        Args:
            fileId (str): The ID of the file to retrieve.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict: A dictionary containing 'retrieval_status' (bool) and 'file_data' (Dict) if successful.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"retrieval_status": False, "file_data": {}}
        
        file_data = files.get(fileId)
        if file_data:
            return {"retrieval_status": True, "file_data": copy.deepcopy(file_data)}
        return {"retrieval_status": False, "file_data": {}}

    def create_file(
        self,
        name: str,
        mimeType: str,
        parents: Optional[List[str]] = None,
        content: Optional[str] = None,
        user_id: str = "me",
    ) -> Dict[str, Union[bool, Dict]]:
        """
        Creates a new file in the user's Drive.

        Args:
            name (str): The name of the file.
            mimeType (str): The MIME type of the file.
            parents (Optional[List[str]]): A list of parent folder IDs/names. Defaults to root.
            content (Optional[str]): The content of the file (for simplicity).
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict: A dictionary containing 'creation_status' (bool) and 'file_data' (Dict) if successful.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"creation_status": False, "message": "User not found."}

        user_drive_data = self.users[internal_user_id].get("drive_data")
        if user_drive_data is None:
            user_drive_data = {"user_info": {"name": "", "email": user_id, "storage_quota": {"total": 0, "used": 0}}, "files": {}}
            self.users[internal_user_id]["drive_data"] = user_drive_data
        
        files = user_drive_data.get("files")
        user_info = user_drive_data.get("user_info")

        new_file_id = self._generate_id()
        current_time = int(datetime.now().timestamp())
        
        new_file = {
            "id": new_file_id,
            "name": name,
            "mimeType": mimeType,
            "createdTime": current_time,
            "modifiedTime": current_time,
            "owners": [{"displayName": user_info.get("name", user_id), "emailAddress": user_id}],
            "parents": parents if parents is not None else ["root"],
            "size": len(content) if content else 0
        }
        files[new_file_id] = new_file

        user_info["storage_quota"]["used"] += new_file["size"]
        
        print(f"File '{name}' created for {user_id} with ID: {new_file_id}")
        return {"creation_status": True, "file_data": new_file}

    def update_file(
        self,
        fileId: str,
        addParents: Optional[str] = None,
        removeParents: Optional[str] = None,
        user_id: str = "me",
        name: Optional[str] = None,
        mimeType: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a file's properties in Google Drive for a specific user.

        Args:
            fileId (str): ID of the file to update.
            addParents (str, optional): Parents to add to the file. Defaults to None.
            removeParents (str, optional): Parents to remove from the file. Defaults to None.
            user_id (str, optional): User's email address or 'me' for the authenticated user. Defaults to 'me'.
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
        file["modifiedTime"] = int(datetime.now().timestamp())

        if name is not None:
            file["name"] = name
        if mimeType is not None:
            file["mimeType"] = mimeType

        if addParents:
            if "parents" not in file:
                file["parents"] = []
            if addParents not in file["parents"]:
                file["parents"].append(addParents)

        if removeParents and "parents" in file:
            file["parents"] = [p for p in file["parents"] if p != removeParents]

        print(f"File '{fileId}' updated for {user_id}")
        return {"updated_file": copy.deepcopy(file), "status": "success"}

    def delete_file(self, fileId: str, user_id: str = "me") -> Dict[str, Union[bool, str]]:
        """
        Deletes a file by its ID from the user's Drive.

        Args:
            fileId (str): The ID of the file to delete.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict: A dictionary indicating success or failure.
        """
        internal_user_id = self._get_user_id_by_email(user_id)
        if not internal_user_id:
            return {"delete_status": False, "message": "User not found."}
        
        user_drive_data = self.users[internal_user_id].get("drive_data")
        if user_drive_data is None:
            return {"delete_status": False, "message": "User data not found."}

        files = user_drive_data.get("files")
        user_info = user_drive_data.get("user_info")

        if fileId in files:
            deleted_file_size = files[fileId].get("size", 0)
            del files[fileId]

            user_info["storage_quota"]["used"] -= deleted_file_size

            print(f"File '{fileId}' deleted for {user_id}")
            return {"delete_status": True, "message": "File deleted successfully."}
        return {"delete_status": False, "message": "File not found."}

    def copy_file(
        self, fileId: str, name: str, parents: Optional[List[str]] = None, user_id: str = "me"
    ) -> Dict[str, Union[bool, Dict]]:
        """
        Copies an existing file in the user's Drive.

        Args:
            fileId (str): The ID of the file to copy.
            name (str): The name for the new copied file.
            parents (Optional[List[str]]): A list of parent folder IDs/names for the copy. Defaults to root.
            user_id (str): User's email address or 'me' for the authenticated user.

        Returns:
            Dict: A dictionary containing 'copy_status' (bool) and 'copied_file_data' (Dict) if successful.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"copy_status": False, "message": "User data not found."}

        original_file = files.get(fileId)
        if not original_file:
            return {"copy_status": False, "message": "Original file not found."}

        new_file_id = self._generate_id()
        current_time = int(datetime.now().timestamp())

        copied_file = copy.deepcopy(original_file)
        copied_file["id"] = new_file_id
        copied_file["name"] = name
        copied_file["createdTime"] = current_time
        copied_file["modifiedTime"] = current_time
        copied_file["parents"] = parents if parents is not None else ["root"]

        files[new_file_id] = copied_file

        internal_user_id = self._get_user_id_by_email(user_id)
        if internal_user_id:
            user_info = self.users[internal_user_id]["drive_data"].get("user_info")
            if user_info:
                user_info["storage_quota"]["used"] += copied_file.get("size", 0)

        print(f"File '{fileId}' copied to '{name}' with ID: {new_file_id} for {user_id}")
        return {"copy_status": True, "copied_file_data": copied_file}

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