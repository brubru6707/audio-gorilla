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
        self.current_user: Optional[str] = None  # Currently authenticated user ID
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
        # Set first user as authenticated user by default
        if self.users and not self.current_user:
            self.current_user = next(iter(self.users.keys()))
            user_email = self._get_user_email_by_id(self.current_user)
            print(f"GoogleDriveApis: Loaded scenario with users and their UUIDs.")
            print(f"API auto-authenticated as: {user_email}")
        else:
            print("GoogleDriveApis: Loaded scenario with users and their UUIDs.")
    
    def authenticate(self, email: str) -> Dict[str, Union[bool, str]]:
        """
        Authenticate a user and set them as the current user.
        
        Args:
            email (str): The user's email address.
        
        Returns:
            Dict[str, Union[bool, str]]: Authentication result.
        """
        user_id = self._get_user_id_by_email(email)
        if user_id:
            self.current_user = user_id
            print(f"GoogleDriveApis: Authenticated as {email}")
            return {"success": True, "message": f"Authenticated as {email}"}
        return {"success": False, "message": f"User with email {email} not found"}
    
    def _ensure_authenticated(self) -> str:
        """
        Ensure a user is authenticated before performing operations.
        
        Returns:
            str: The current user ID.
        
        Raises:
            Exception: If no user is authenticated.
        """
        if not self.current_user:
            raise Exception("No authenticated user. Call authenticate() first.")
        return self.current_user
    
    def _get_current_user_id(self) -> Optional[str]:
        """
        Get the current authenticated user's ID.
        
        Returns:
            Optional[str]: Current user ID if authenticated, None otherwise.
        """
        return self.current_user

    def _generate_id(self) -> str:
        """
        Generates a unique UUID for dummy entities (files, folders).
        """
        return str(uuid.uuid4())
    
    def _timestamp_to_rfc3339(self, timestamp: Union[int, float]) -> str:
        """
        Convert Unix timestamp to RFC3339 format string.
        
        Args:
            timestamp (Union[int, float]): Unix timestamp.
        
        Returns:
            str: RFC3339 formatted datetime string.
        """
        return datetime.fromtimestamp(timestamp).isoformat() + 'Z'
    
    def _rfc3339_now(self) -> str:
        """
        Get current time in RFC3339 format.
        
        Returns:
            str: Current time in RFC3339 format.
        """
        return datetime.now().isoformat() + 'Z'

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

    def get_user_info(self) -> Dict[str, Any]:
        """
        Gets information about the user, the user's Drive, and system capabilities.
        Real API endpoint: GET /drive/v3/about
        
        Returns:
            Dict[str, Any]: About resource containing user and Drive information.
        """
        user_id = self._ensure_authenticated()
        user_info = self._get_user_info(user_id)
        user_email = self._get_user_email_by_id(user_id)
        
        if user_info:
            user_data = self.users[user_id]
            return {
                "kind": "drive#about",
                "user": {
                    "kind": "drive#user",
                    "displayName": user_info.get("name", user_email),
                    "emailAddress": user_email,
                    "me": True
                },
                "storageQuota": {
                    "limit": str(user_info.get("storage_quota", {}).get("total", 15000000000)),
                    "usage": str(user_info.get("storage_quota", {}).get("used", 0)),
                    "usageInDrive": str(user_info.get("storage_quota", {}).get("used", 0))
                }
            }
        
        # Return minimal info if no user_info exists
        return {
            "kind": "drive#about",
            "user": {
                "kind": "drive#user",
                "displayName": user_email,
                "emailAddress": user_email,
                "me": True
            },
            "storageQuota": {
                "limit": "15000000000",
                "usage": "0",
                "usageInDrive": "0"
            }
        }

    def list_files(
        self,
        q: Optional[str] = None,
        page_size: int = 100,
        page_token: Optional[str] = None,
        order_by: Optional[str] = None,
        spaces: str = "drive",
    ) -> Dict[str, Any]:
        """
        Lists the user's files.
        Real API endpoint: GET /drive/v3/files
        
        Args:
            q (Optional[str]): A query for filtering the file results. 
                              See https://developers.google.com/drive/api/guides/search-files
            page_size (int): The maximum number of files to return per page. Default 100, max 1000.
            page_token (Optional[str]): The token for continuing a previous list request.
            order_by (Optional[str]): A comma-separated list of sort keys. Valid keys are 
                                     'createdTime', 'folder', 'modifiedByMeTime', 'modifiedTime',
                                     'name', 'quotaBytesUsed', 'recency', 'sharedWithMeTime', 'starred', 'viewedByMeTime'.
            spaces (str): A comma-separated list of spaces to query within. Supported values are 'drive' and 'appDataFolder'.
        
        Returns:
            Dict[str, Any]: Files list resource.
        """
        user_id = self._ensure_authenticated()
        files = self._get_user_files(user_id)
        
        if files is None:
            return {
                "kind": "drive#fileList",
                "incompleteSearch": False,
                "files": []
            }

        all_files = list(files.values())
        filtered_files = []

        if q:
            # Enhanced query parsing to support multiple Google Drive query formats
            if "name contains '" in q and q.endswith("'"):
                search_term = q.split("name contains '")[1][:-1].lower()
                for file_data in all_files:
                    if search_term in file_data.get("name", "").lower():
                        filtered_files.append(file_data)
            elif "trashed = true" in q.lower():
                for file_data in all_files:
                    if file_data.get("trashed", False):
                        filtered_files.append(file_data)
            elif "trashed = false" in q.lower():
                for file_data in all_files:
                    if not file_data.get("trashed", False):
                        filtered_files.append(file_data)
            elif "starred = true" in q.lower():
                for file_data in all_files:
                    if file_data.get("starred", False):
                        filtered_files.append(file_data)
            elif "shared = true" in q.lower() or "'me' in owners" in q.lower():
                for file_data in all_files:
                    if file_data.get("shared", False):
                        filtered_files.append(file_data)
            elif "mimeType = '" in q and q.endswith("'"):
                mime_type = q.split("mimeType = '")[1][:-1]
                for file_data in all_files:
                    if file_data.get("mimeType") == mime_type:
                        filtered_files.append(file_data)
            elif "'" in q and "' in parents" in q:
                parent_id = q.split("'")[1]
                for file_data in all_files:
                    if parent_id in file_data.get("parents", []):
                        filtered_files.append(file_data)
            else:
                # If query format is not recognized, return all files
                filtered_files = all_files
        else:
            # Default: exclude trashed files unless specifically requested
            filtered_files = [f for f in all_files if not f.get("trashed", False)]

        # Apply ordering
        if order_by:
            sort_key = order_by.split()[0]  # Handle "name desc" or just "name"
            reverse = "desc" in order_by.lower()
            
            if sort_key == "name":
                filtered_files.sort(key=lambda f: f.get("name", "").lower(), reverse=reverse)
            elif sort_key == "createdTime":
                filtered_files.sort(key=lambda f: f.get("createdTime", 0), reverse=reverse)
            elif sort_key == "modifiedTime":
                filtered_files.sort(key=lambda f: f.get("modifiedTime", 0), reverse=reverse)
            elif sort_key == "starred":
                filtered_files.sort(key=lambda f: f.get("starred", False), reverse=reverse)

        start_index = 0
        if page_token:
            try:
                start_index = int(page_token)
            except ValueError:
                start_index = 0

        paginated_files = filtered_files[start_index : start_index + page_size]
        next_page_token = str(start_index + page_size) if start_index + page_size < len(filtered_files) else None

        # Add standard fields to each file
        enriched_files = []
        for file_data in paginated_files:
            file_copy = copy.deepcopy(file_data)
            file_copy["kind"] = "drive#file"
            
            # Convert timestamps to RFC3339 if they're integers
            if isinstance(file_copy.get("createdTime"), int):
                file_copy["createdTime"] = self._timestamp_to_rfc3339(file_copy["createdTime"])
            if isinstance(file_copy.get("modifiedTime"), int):
                file_copy["modifiedTime"] = self._timestamp_to_rfc3339(file_copy["modifiedTime"])
            if isinstance(file_copy.get("viewedByMeTime"), int):
                file_copy["viewedByMeTime"] = self._timestamp_to_rfc3339(file_copy["viewedByMeTime"])
            
            enriched_files.append(file_copy)

        result = {
            "kind": "drive#fileList",
            "incompleteSearch": False,
            "files": enriched_files
        }
        
        if next_page_token:
            result["nextPageToken"] = next_page_token
        
        return result

    def get_file(self, fileId: str, fields: Optional[str] = "*") -> Dict[str, Any]:
        """
        Gets a file's metadata by ID.
        Real API endpoint: GET /drive/v3/files/{fileId}
        
        Args:
            fileId (str): The ID of the file.
            fields (Optional[str]): The paths of the fields you want included in the response.
                                   Default is "*" (all fields).
        
        Returns:
            Dict[str, Any]: File resource.
        
        Raises:
            Exception: If file not found.
        """
        user_id = self._ensure_authenticated()
        files = self._get_user_files(user_id)
        
        if files is None:
            raise Exception("User data not found")
        
        file_data = files.get(fileId)
        if not file_data:
            raise Exception(f"File not found: {fileId}")
        
        # Update viewing metadata when file is accessed
        user_email = self._get_user_email_by_id(user_id)
        file_data["lastViewingUser"] = user_email
        file_data["viewedByMeTime"] = datetime.now().timestamp()
        
        file_copy = copy.deepcopy(file_data)
        file_copy["kind"] = "drive#file"
        
        # Convert timestamps to RFC3339
        if isinstance(file_copy.get("createdTime"), (int, float)):
            file_copy["createdTime"] = self._timestamp_to_rfc3339(file_copy["createdTime"])
        if isinstance(file_copy.get("modifiedTime"), (int, float)):
            file_copy["modifiedTime"] = self._timestamp_to_rfc3339(file_copy["modifiedTime"])
        if isinstance(file_copy.get("viewedByMeTime"), (int, float)):
            file_copy["viewedByMeTime"] = self._timestamp_to_rfc3339(file_copy["viewedByMeTime"])
        
        # Add capabilities
        if "capabilities" not in file_copy:
            file_copy["capabilities"] = {
                "canEdit": True,
                "canComment": True,
                "canShare": True,
                "canCopy": True,
                "canDelete": True,
                "canDownload": True,
                "canRename": True,
                "canTrash": True
            }
        
        return file_copy

    def create_file(
        self,
        name: str,
        mimeType: str = "application/octet-stream",
        parents: Optional[List[str]] = None,
        description: Optional[str] = None,
        starred: bool = False,
    ) -> Dict[str, Any]:
        """
        Creates a new file.
        Real API endpoint: POST /drive/v3/files
        
        Args:
            name (str): The name of the file.
            mimeType (str): The MIME type of the file. Defaults to 'application/octet-stream'.
            parents (Optional[List[str]]): The IDs of the parent folders. If not specified,
                                          the file will be placed directly in the user's My Drive.
            description (Optional[str]): A short description of the file.
            starred (bool): Whether the user has starred the file.
        
        Returns:
            Dict[str, Any]: File resource.
        """
        user_id = self._ensure_authenticated()
        
        user_drive_data = self.users[user_id].get("drive_data")
        if user_drive_data is None:
            user_email = self._get_user_email_by_id(user_id)
            user_drive_data = {
                "user_info": {
                    "name": "",
                    "email": user_email,
                    "storage_quota": {"total": 15000000000, "used": 0}
                },
                "files": {}
            }
            self.users[user_id]["drive_data"] = user_drive_data
        
        files = user_drive_data.get("files")
        user_info = user_drive_data.get("user_info")
        user_email = self._get_user_email_by_id(user_id)

        new_file_id = self._generate_id()
        current_time_rfc = self._rfc3339_now()
        
        new_file = {
            "kind": "drive#file",
            "id": new_file_id,
            "name": name,
            "mimeType": mimeType,
            "createdTime": current_time_rfc,
            "modifiedTime": current_time_rfc,
            "viewedByMeTime": current_time_rfc,
            "owners": [{
                "kind": "drive#user",
                "displayName": user_info.get("name", user_email),
                "emailAddress": user_email,
                "me": True
            }],
            "parents": parents if parents is not None else ["root"],
            "size": "0",
            "starred": starred,
            "trashed": False,
            "shared": False,
            "capabilities": {
                "canEdit": True,
                "canComment": True,
                "canShare": True,
                "canCopy": True,
                "canDelete": True,
                "canDownload": True,
                "canRename": True,
                "canTrash": True
            }
        }
        
        if description:
            new_file["description"] = description
        
        files[new_file_id] = new_file
        
        user_email_display = self._get_user_email_by_id(user_id)
        print(f"File '{name}' created for {user_email_display} with ID: {new_file_id}")
        return new_file

    def update_file(
        self,
        fileId: str,
        name: Optional[str] = None,
        mimeType: Optional[str] = None,
        description: Optional[str] = None,
        starred: Optional[bool] = None,
        trashed: Optional[bool] = None,
        addParents: Optional[str] = None,
        removeParents: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Updates a file's metadata and/or content.
        Real API endpoint: PATCH /drive/v3/files/{fileId}
        
        Args:
            fileId (str): The ID of the file to update.
            name (Optional[str]): The new name for the file.
            mimeType (Optional[str]): The new MIME type for the file.
            description (Optional[str]): A short description of the file.
            starred (Optional[bool]): Whether to star or unstar the file.
            trashed (Optional[bool]): Whether to move the file to trash or restore it.
            addParents (Optional[str]): Comma-separated list of parent IDs to add.
            removeParents (Optional[str]): Comma-separated list of parent IDs to remove.
        
        Returns:
            Dict[str, Any]: Updated file resource.
        
        Raises:
            Exception: If file not found.
        """
        user_id = self._ensure_authenticated()
        files = self._get_user_files(user_id)
        
        if files is None:
            raise Exception("User data not found")

        if fileId not in files:
            raise Exception(f"File not found: {fileId}")

        file = files[fileId]
        user_email = self._get_user_email_by_id(user_id)
        
        file["modifiedTime"] = self._rfc3339_now()
        file["viewedByMeTime"] = self._rfc3339_now()

        if name is not None:
            file["name"] = name
        if mimeType is not None:
            file["mimeType"] = mimeType
        if description is not None:
            file["description"] = description
        if starred is not None:
            file["starred"] = starred
        if trashed is not None:
            file["trashed"] = trashed

        # Ensure parents is always a list
        if "parents" not in file:
            file["parents"] = ["root"]
        elif not isinstance(file["parents"], list):
            file["parents"] = [file["parents"]] if file["parents"] else ["root"]

        if addParents:
            parents_to_add = addParents.split(',')
            for parent in parents_to_add:
                if parent not in file["parents"]:
                    file["parents"].append(parent)

        if removeParents:
            parents_to_remove = removeParents.split(',')
            file["parents"] = [p for p in file["parents"] if p not in parents_to_remove]
            # Ensure at least one parent exists
            if not file["parents"]:
                file["parents"] = ["root"]

        user_email_display = self._get_user_email_by_id(user_id)
        print(f"File '{fileId}' updated for {user_email_display}")
        
        file_copy = copy.deepcopy(file)
        file_copy["kind"] = "drive#file"
        return file_copy

    def delete_file(self, fileId: str) -> None:
        """
        Permanently deletes a file owned by the user without moving it to the trash.
        Real API endpoint: DELETE /drive/v3/files/{fileId}
        
        Args:
            fileId (str): The ID of the file to delete.
        
        Raises:
            Exception: If file not found.
        """
        user_id = self._ensure_authenticated()
        
        user_drive_data = self.users[user_id].get("drive_data")
        if user_drive_data is None:
            raise Exception("User data not found")

        files = user_drive_data.get("files")
        user_info = user_drive_data.get("user_info")

        if fileId not in files:
            raise Exception(f"File not found: {fileId}")

        deleted_file_size = int(files[fileId].get("size", "0")) if isinstance(files[fileId].get("size"), str) else files[fileId].get("size", 0)
        del files[fileId]

        if user_info and "storage_quota" in user_info:
            user_info["storage_quota"]["used"] -= deleted_file_size

        user_email = self._get_user_email_by_id(user_id)
        print(f"File '{fileId}' deleted for {user_email}")

    def copy_file(
        self,
        fileId: str,
        name: Optional[str] = None,
        parents: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a copy of a file.
        Real API endpoint: POST /drive/v3/files/{fileId}/copy
        
        Args:
            fileId (str): The ID of the file to copy.
            name (Optional[str]): The name of the new file. If not provided, uses "Copy of [original name]".
            parents (Optional[List[str]]): The IDs of the parent folders containing the file.
            description (Optional[str]): A short description of the file.
        
        Returns:
            Dict[str, Any]: The copied file resource.
        
        Raises:
            Exception: If original file not found.
        """
        user_id = self._ensure_authenticated()
        files = self._get_user_files(user_id)
        
        if files is None:
            raise Exception("User data not found")

        original_file = files.get(fileId)
        if not original_file:
            raise Exception(f"File not found: {fileId}")

        new_file_id = self._generate_id()
        current_time_rfc = self._rfc3339_now()
        user_email = self._get_user_email_by_id(user_id)

        copied_file = copy.deepcopy(original_file)
        copied_file["kind"] = "drive#file"
        copied_file["id"] = new_file_id
        copied_file["name"] = name if name is not None else f"Copy of {original_file.get('name', 'Untitled')}"
        copied_file["createdTime"] = current_time_rfc
        copied_file["modifiedTime"] = current_time_rfc
        copied_file["viewedByMeTime"] = current_time_rfc
        copied_file["parents"] = parents if parents is not None else original_file.get("parents", ["root"])
        copied_file["shared"] = False  # Reset sharing for copy
        
        if description is not None:
            copied_file["description"] = description

        files[new_file_id] = copied_file

        if user_id in self.users:
            user_info = self.users[user_id]["drive_data"].get("user_info")
            if user_info:
                file_size = int(copied_file.get("size", "0")) if isinstance(copied_file.get("size"), str) else copied_file.get("size", 0)
                user_info["storage_quota"]["used"] += file_size

        print(f"File '{fileId}' copied to '{copied_file['name']}' with ID: {new_file_id} for {user_email}")
        return copied_file
    
    def create_permission(
        self,
        fileId: str,
        role: str,
        type: str,
        emailAddress: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a permission for a file or shared drive.
        Real API endpoint: POST /drive/v3/files/{fileId}/permissions
        
        Args:
            fileId (str): The ID of the file or shared drive.
            role (str): The role granted by this permission. Valid values are:
                       'owner', 'organizer', 'fileOrganizer', 'writer', 'commenter', 'reader'.
            type (str): The type of the grantee. Valid values are:
                       'user', 'group', 'domain', 'anyone'.
            emailAddress (Optional[str]): The email address of the user or group to which this permission refers.
            domain (Optional[str]): The domain to which this permission refers.
        
        Returns:
            Dict[str, Any]: Permission resource.
        
        Raises:
            Exception: If file not found or invalid parameters.
        """
        user_id = self._ensure_authenticated()
        files = self._get_user_files(user_id)
        
        if files is None:
            raise Exception("User data not found")

        if fileId not in files:
            raise Exception(f"File not found: {fileId}")

        # Validate role
        valid_roles = ["owner", "organizer", "fileOrganizer", "writer", "commenter", "reader"]
        if role not in valid_roles:
            raise Exception(f"Invalid role '{role}'. Valid roles are: {', '.join(valid_roles)}")
        
        # Validate type
        valid_types = ["user", "group", "domain", "anyone"]
        if type not in valid_types:
            raise Exception(f"Invalid type '{type}'. Valid types are: {', '.join(valid_types)}")

        file = files[fileId]
        user_email = self._get_user_email_by_id(user_id)
        
        # Create permission
        permission_id = self._generate_id()
        permission = {
            "kind": "drive#permission",
            "id": permission_id,
            "type": type,
            "role": role
        }
        
        if emailAddress:
            permission["emailAddress"] = emailAddress
            # Find the user's display name if they exist in our system
            display_name = "External User"
            for user_data in self.users.values():
                if user_data.get("email") == emailAddress:
                    display_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                    break
            permission["displayName"] = display_name
        
        if domain:
            permission["domain"] = domain
        
        # Add to file's permissions/owners list
        if "owners" not in file:
            file["owners"] = []
        
        file["owners"].append({
            "kind": "drive#user",
            "displayName": permission.get("displayName", "Unknown"),
            "emailAddress": emailAddress if emailAddress else "",
            "role": role
        })
        
        file["shared"] = True
        file["modifiedTime"] = self._rfc3339_now()

        print(f"Permission created for file '{fileId}': {role} access for {emailAddress or type}")
        return permission

    def list_revisions(self, fileId: str, page_size: int = 200) -> Dict[str, Any]:
        """
        Lists a file's revisions.
        Real API endpoint: GET /drive/v3/files/{fileId}/revisions
        
        Args:
            fileId (str): The ID of the file.
            page_size (int): The maximum number of revisions to return per page.
        
        Returns:
            Dict[str, Any]: Revisions list resource.
        
        Raises:
            Exception: If file not found.
        """
        user_id = self._ensure_authenticated()
        files = self._get_user_files(user_id)
        
        if files is None:
            raise Exception("User data not found")

        if fileId not in files:
            raise Exception(f"File not found: {fileId}")

        file = files[fileId]
        
        # Simulate revision history based on creation/modification times
        revisions = []
        created_time = file.get("createdTime")
        modified_time = file.get("modifiedTime")
        
        # Always have at least the current version
        current_revision = {
            "kind": "drive#revision",
            "id": "1",
            "mimeType": file.get("mimeType"),
            "modifiedTime": modified_time if modified_time else created_time,
            "size": file.get("size", "0"),
            "keepForever": False,
            "published": False
        }
        revisions.append(current_revision)

        return {
            "kind": "drive#revisionList",
            "revisions": revisions
        }

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

    
    def create_folder(self, name: str, parents: Optional[List[str]] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a new folder.
        Real API endpoint: POST /drive/v3/files (with mimeType='application/vnd.google-apps.folder')
        
        Args:
            name (str): The name of the folder.
            parents (Optional[List[str]]): The IDs of the parent folders. Defaults to root.
            description (Optional[str]): A short description of the folder.
        
        Returns:
            Dict[str, Any]: The created folder resource.
        """
        return self.create_file(
            name=name,
            mimeType="application/vnd.google-apps.folder",
            parents=parents,
            description=description
        )