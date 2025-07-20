from typing import Dict, Any, Optional, List
from copy import deepcopy
import time

# Dummy backend data for Google Drive
DEFAULT_STATE = {
    "user_info": {
        "name": "user",
        "email": "user@example.com",
        "storage_quota": {"total": 1000000000, "used": 0}
    },
    "files": {
        "file_1": {
            "id": "file_1",
            "name": "MyDocument.txt",
            "mimeType": "text/plain",
            "createdTime": "1678886400", # Example timestamp
            "modifiedTime": "1678886400",
            "owners": [{
                "displayName": "user",
                "emailAddress": "user@example.com"
            }],
            "parents": ["root"]
        },
        "file_2": {
            "id": "file_2",
            "name": "MySpreadsheet.xlsx",
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "createdTime": "1678972800",
            "modifiedTime": "1678972800",
            "owners": [{
                "displayName": "user",
                "emailAddress": "user@example.com"
            }],
            "parents": ["root"]
        }
    },
    "next_page_token": 1
}

class GoogleDriveApis:
    def __init__(self):
        """
        Initializes the GoogleDriveAPI instance and loads the default scenario.
        """
        self.user_info: Dict[str, Any] = {}
        self.files: Dict[str, Dict[str, Any]] = {}
        self.next_page_token: int = 1
        self._api_description = "This tool belongs to the GoogleDriveAPI, which provides core functionality for file management in Google Drive."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: dict) -> None:
        """
        Loads a scenario into the GoogleDriveAPI instance.
        This method is used to set up the initial state of the API for testing or specific scenarios.

        Args:
            scenario (dict): A dictionary containing the initial state for user_info, files, and next_page_token.
        """
        # Create a deep copy of the default state to avoid modifying the original DEFAULT_STATE
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.user_info = scenario.get("user_info", DEFAULT_STATE_COPY["user_info"])
        self.files = scenario.get("files", DEFAULT_STATE_COPY["files"])
        self.next_page_token = scenario.get("next_page_token", DEFAULT_STATE_COPY["next_page_token"])

    def get_about(self) -> Dict[str, Any]:
        """
        Get information about the user's Google Drive.

        Returns:
        about_info (Dict[str, Any]): Information about the user's Google Drive,
                                     including user details, storage quota, max upload size,
                                     and app installation status.
        """
        return {
            "user": self.user_info,
            "storageQuota": self.user_info["storage_quota"],
            "maxUploadSize": "5TB",
            "appInstalled": True
        }

    def copy_file(self, fileId: str) -> Dict[str, Any]:
        """
        Copy a file within Google Drive.

        Args:
        fileId (str): ID of the file to copy.

        Returns:
        copied_file (Dict[str, Any]): Information about the copied file if successful,
                                      or an error message if the file is not found.
        """
        if fileId not in self.files:
            return {"error": "File not found"}

        original_file = self.files[fileId]
        # Generate a new unique file ID
        new_file_id = f"file_{len(self.files) + 1}"
        copied_file = {
            **original_file, # Copy all existing attributes
            "id": new_file_id,
            "name": f"Copy of {original_file.get('name', '')}",
            "createdTime": str(int(time.time())) # Update creation time
        }

        self.files[new_file_id] = copied_file
        return copied_file

    def create_file(self) -> Dict[str, Any]:
        """
        Create a new file in Google Drive.

        Returns:
        created_file (Dict[str, Any]): Information about the newly created file.
        """
        file_id = f"file_{len(self.files) + 1}"
        new_file = {
            "id": file_id,
            "name": "Untitled",
            "mimeType": "application/vnd.google-apps.document", # Default MIME type
            "createdTime": str(int(time.time())),
            "modifiedTime": str(int(time.time())),
            "owners": [{
                "displayName": self.user_info["name"],
                "emailAddress": self.user_info["email"]
            }]
        }

        self.files[file_id] = new_file
        return new_file

    def delete_file(self, fileId: str) -> Dict[str, bool]:
        """
        Delete a file from Google Drive.

        Args:
        fileId (str): ID of the file to delete.

        Returns:
        deletion_status (Dict[str, bool]): True if deleted successfully, False otherwise.
        """
        if fileId in self.files:
            del self.files[fileId]
            return {"deletion_status": True}
        return {"deletion_status": False}

    def empty_trash(self) -> Dict[str, bool]:
        """
        Empty the trash in Google Drive.
        In this dummy implementation, it always returns True as there's no actual trash to empty.

        Returns:
        empty_status (Dict[str, bool]): True if emptied successfully, False otherwise.
        """
        # In a real implementation, we would track trashed files separately and remove them here.
        return {"empty_status": True}

    def export_file(self, fileId: str, mimeType: str) -> Dict[str, Any]:
        """
        Export a file to a different format.

        Args:
        fileId (str): ID of the file to export.
        mimeType (str): MIME type for the exported file (e.g., "application/pdf", "text/plain").

        Returns:
        exported_file (Dict[str, Any]): Information about the exported file,
                                       including its ID, new MIME type, and a dummy export link.
                                       Returns an error if the file is not found.
        """
        if fileId not in self.files:
            return {"error": "File not found"}

        return {
            "id": fileId,
            "mimeType": mimeType,
            "exportLinks": {
                mimeType: "https://example.com" # Dummy export link
            }
        }

    def get_file(self, fileId: str) -> Dict[str, Any]:
        """
        Get information about a specific file.

        Args:
        fileId (str): ID of the file.

        Returns:
        file_info (Dict[str, Any]): Information about the file if found,
                                     or an error message if the file is not found.
        """
        if fileId in self.files:
            return self.files[fileId].copy() # Return a copy to prevent external modification
        return {"error": "File not found"}

    def list_files(self, driveId: str = "", orderBy: str = "", pageSize: int = 0, q: str = "") -> Dict[str, Any]:
        """
        List files in Google Drive based on various filters and sorting options.

        Args:
        driveId (str, optional): ID of the shared drive to filter by. Defaults to "".
        orderBy (str, optional): Order of the results (e.g., "name", "-modifiedTime"). Defaults to "".
        pageSize (int, optional): Number of files to return. Defaults to 0 (all).
        q (str, optional): Query string for filtering by file name. Defaults to "".

        Returns:
        files_list (Dict[str, Any]): A dictionary containing a list of filtered and sorted files.
        """
        files = list(self.files.values())

        # Filter by driveId (dummy implementation)
        if driveId:
            files = [f for f in files if f.get("driveId") == driveId]

        # Filter by query string (case-insensitive name search)
        if q:
            files = [f for f in files if q.lower() in f.get("name", "").lower()]

        # Sort files based on orderBy parameter
        if orderBy:
            reverse = orderBy.startswith("-") # Check for descending order
            order_field = orderBy[1:] if reverse else orderBy
            # Sort by the specified field, using an empty string as default for missing fields
            files = sorted(files, key=lambda x: x.get(order_field, ""), reverse=reverse)

        # Apply pagination (pageSize)
        if pageSize > 0:
            files = files[:pageSize]

        return {"files": files}

    def update_file(self, fileId: str, addParents: str = "", removeParents: str = "") -> Dict[str, Any]:
        """
        Update a file's properties in Google Drive.

        Args:
        fileId (str): ID of the file to update.
        addParents (str, optional): Parents to add to the file. Defaults to "".
        removeParents (str, optional): Parents to remove from the file. Defaults to "".

        Returns:
        updated_file (Dict[str, Any]): The updated file information if successful,
                                      or an error message if the file is not found.
        """
        if fileId not in self.files:
            return {"error": "File not found"}

        file = self.files[fileId]
        file["modifiedTime"] = str(int(time.time())) # Update modification time

        # Add parents
        if addParents:
            if "parents" not in file:
                file["parents"] = []
            file["parents"].append(addParents)

        # Remove parents
        if removeParents and "parents" in file:
            file["parents"] = [p for p in file["parents"] if p != removeParents]

        return file
