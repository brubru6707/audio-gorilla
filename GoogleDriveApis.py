from typing import Dict, Any, Optional, List
from copy import deepcopy
import time

DEFAULT_STATE = {
    "user_info": {
        "name": "user",
        "email": "user@example.com",
        "storage_quota": {"total": 1000000000, "used": 0}
    },
    "files": {},
    "next_page_token": 1
}

class GoogleDriveAPI:
    def __init__(self):
        self.user_info: Dict[str, Any]
        self.files: Dict[str, Dict[str, Any]]
        self.next_page_token: int
        self._api_description = "This tool belongs to the GoogleDriveAPI, which provides core functionality for file management in Google Drive."

    def _load_scenario(self, scenario: dict) -> None:
        """Load a scenario into the GoogleDriveAPI instance."""
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.user_info = scenario.get("user_info", DEFAULT_STATE_COPY["user_info"])
        self.files = scenario.get("files", DEFAULT_STATE_COPY["files"])
        self.next_page_token = scenario.get("next_page_token", DEFAULT_STATE_COPY["next_page_token"])

    def get_about(self) -> Dict[str, Any]:
        """  
        Get information about the user's Google Drive.  

        Returns:  
        about_info (Dict[str, Any]): Information about the user's Google Drive.  
        """  
        return {
            "user": self.user_info,
            "storageQuota": self.user_info["storage_quota"],
            "maxUploadSize": "5TB",
            "appInstalled": True
        }

    def copy_file(self, fileId: str, enforceSingleParent: bool = False, ignoreDefaultVisibility: bool = False, includeLabels: str = "", includePermissionsForView: str = "", keepRevisionForever: bool = False, ocrLanguage: str = "", supportsAllDrives: bool = False, supportsTeamDrives: bool = False) -> Dict[str, Any]:
        """  
        Copy a file.  

        Args:  
        fileId (str): ID of the file to copy.  
        enforceSingleParent (bool, optional): Whether to enforce single parent.  
        ignoreDefaultVisibility (bool, optional): Whether to ignore default visibility.  
        includeLabels (str, optional): Labels to include.  
        includePermissionsForView (str, optional): Permissions to include.  
        keepRevisionForever (bool, optional): Whether to keep revisions forever.  
        ocrLanguage (str, optional): OCR language.  
        supportsAllDrives (bool, optional): Whether to support all drives.  
        supportsTeamDrives (bool, optional): Whether to support Team Drives.  

        Returns:  
        copied_file (Dict[str, Any]): Information about the copied file.  
        """  
        if fileId not in self.files:
            return {"error": "File not found"}
            
        original_file = self.files[fileId]
        new_file_id = f"file_{len(self.files) + 1}"
        copied_file = {
            **original_file,
            "id": new_file_id,
            "name": f"Copy of {original_file.get('name', '')}",
            "createdTime": str(int(time.time()))
        }
        
        self.files[new_file_id] = copied_file
        return copied_file

    def create_file(self, enforceSingleParent: bool = False, ignoreDefaultVisibility: bool = False, includeLabels: str = "", includePermissionsForView: str = "", keepRevisionForever: bool = False, ocrLanguage: str = "", supportsAllDrives: bool = False, supportsTeamDrives: bool = False, useContentAsIndexableText: bool = False) -> Dict[str, Any]:
        """  
        Create a new file.  

        Args:  
        enforceSingleParent (bool, optional): Whether to enforce single parent.  
        ignoreDefaultVisibility (bool, optional): Whether to ignore default visibility.  
        includeLabels (str, optional): Labels to include.  
        includePermissionsForView (str, optional): Permissions to include.  
        keepRevisionForever (bool, optional): Whether to keep revisions forever.  
        ocrLanguage (str, optional): OCR language.  
        supportsAllDrives (bool, optional): Whether to support all drives.  
        supportsTeamDrives (bool, optional): Whether to support Team Drives.  
        useContentAsIndexableText (bool, optional): Whether to use content as indexable text.  

        Returns:  
        created_file (Dict[str, Any]): Information about the created file.  
        """  
        file_id = f"file_{len(self.files) + 1}"
        new_file = {
            "id": file_id,
            "name": "Untitled",
            "mimeType": "application/vnd.google-apps.document",
            "createdTime": str(int(time.time())),
            "modifiedTime": str(int(time.time())),
            "owners": [{
                "displayName": self.user_info["name"],
                "emailAddress": self.user_info["email"]
            }]
        }
        
        self.files[file_id] = new_file
        return new_file

    def delete_file(self, fileId: str, enforceSingleParent: bool = False, supportsAllDrives: bool = False, supportsTeamDrives: bool = False) -> Dict[str, bool]:
        """  
        Delete a file.  

        Args:  
        fileId (str): ID of the file to delete.  
        enforceSingleParent (bool, optional): Whether to enforce single parent.  
        supportsAllDrives (bool, optional): Whether to support all drives.  
        supportsTeamDrives (bool, optional): Whether to support Team Drives.  

        Returns:  
        deletion_status (Dict[str, bool]): True if deleted successfully, False otherwise.  
        """  
        if fileId in self.files:
            del self.files[fileId]
            return {"deletion_status": True}
        return {"deletion_status": False}

    def empty_trash(self, driveId: str = "", enforceSingleParent: bool = False) -> Dict[str, bool]:
        """  
        Empty the trash.  

        Args:  
        driveId (str, optional): ID of the shared drive.  
        enforceSingleParent (bool, optional): Whether to enforce single parent.  

        Returns:  
        empty_status (Dict[str, bool]): True if emptied successfully, False otherwise.  
        """  
        # In a real implementation, we would track trashed files separately
        return {"empty_status": True}

    def export_file(self, fileId: str, mimeType: str) -> Dict[str, Any]:
        """  
        Export a file to a different format.  

        Args:  
        fileId (str): ID of the file to export.  
        mimeType (str): MIME type for the exported file.  

        Returns:  
        exported_file (Dict[str, Any]): Information about the exported file.  
        """  
        if fileId not in self.files:
            return {"error": "File not found"}
            
        return {
            "id": fileId,
            "mimeType": mimeType,
            "exportLinks": {
                mimeType: f"https://www.googleapis.com/drive/v3/files/{fileId}/export?mimeType={mimeType}"
            }
        }

    def get_file(self, fileId: str, acknowledgeAbuse: bool = False, includeLabels: str = "", includePermissionsForView: str = "", supportsAllDrives: bool = False, supportsTeamDrives: bool = False) -> Dict[str, Any]:
        """  
        Get information about a file.  

        Args:  
        fileId (str): ID of the file.  
        acknowledgeAbuse (bool, optional): Whether to acknowledge abuse.  
        includeLabels (str, optional): Labels to include.  
        includePermissionsForView (str, optional): Permissions to include.  
        supportsAllDrives (bool, optional): Whether to support all drives.  
        supportsTeamDrives (bool, optional): Whether to support Team Drives.  

        Returns:  
        file_info (Dict[str, Any]): Information about the file.  
        """  
        if fileId in self.files:
            return self.files[fileId].copy()
        return {"error": "File not found"}

    def list_files(self, corpora: str = "", corpus: str = "", driveId: str = "", includeItemsFromAllDrives: bool = False, includeLabels: str = "", includePermissionsForView: str = "", includeTeamDriveItems: bool = False, orderBy: str = "", pageSize: int = 0, pageToken: str = "", q: str = "", spaces: str = "", supportsAllDrives: bool = False, supportsTeamDrives: bool = False, teamDriveId: str = "") -> Dict[str, Any]:
        """  
        List files in Google Drive.  

        Args:  
        corpora (str, optional): Corpora to include.  
        corpus (str, optional): Corpus to include.  
        driveId (str, optional): ID of the shared drive.  
        includeItemsFromAllDrives (bool, optional): Whether to include items from all drives.  
        includeLabels (str, optional): Labels to include.  
        includePermissionsForView (str, optional): Permissions to include.  
        includeTeamDriveItems (bool, optional): Whether to include Team Drive items.  
        orderBy (str, optional): Order of the results.  
        pageSize (int, optional): Number of files to return.  
        pageToken (str, optional): Token for pagination.  
        q (str, optional): Query string for filtering.  
        spaces (str, optional): Spaces to include.  
        supportsAllDrives (bool, optional): Whether to support all drives.  
        supportsTeamDrives (bool, optional): Whether to support Team Drives.  
        teamDriveId (str, optional): ID of the Team Drive.  

        Returns:  
        files_list (Dict[str, Any]): List of files.  
        """  
        files = list(self.files.values())
        
        if driveId:
            files = [f for f in files if f.get("driveId") == driveId]
            
        if q:
            files = [f for f in files if q.lower() in f.get("name", "").lower()]
            
        if orderBy:
            reverse = orderBy.startswith("-")
            order_field = orderBy[1:] if reverse else orderBy
            files = sorted(files, key=lambda x: x.get(order_field, ""), reverse=reverse)
            
        if pageSize > 0:
            files = files[:pageSize]
            
        return {"files": files}

    def update_file(self, fileId: str, addParents: str = "", enforceSingleParent: bool = False, includeLabels: str = "", includePermissionsForView: str = "", keepRevisionForever: bool = False, ocrLanguage: str = "", removeParents: str = "", supportsAllDrives: bool = False, supportsTeamDrives: bool = False, useContentAsIndexableText: bool = False) -> Dict[str, Any]:
        """  
        Update a file.  

        Args:  
        fileId (str): ID of the file.  
        addParents (str, optional): Parents to add.  
        enforceSingleParent (bool, optional): Whether to enforce single parent.  
        includeLabels (str, optional): Labels to include.  
        includePermissionsForView (str, optional): Permissions to include.  
        keepRevisionForever (bool, optional): Whether to keep revisions forever.  
        ocrLanguage (str, optional): OCR language.  
        removeParents (str, optional): Parents to remove.  
        supportsAllDrives (bool, optional): Whether to support all drives.  
        supportsTeamDrives (bool, optional): Whether to support Team Drives.  
        useContentAsIndexableText (bool, optional): Whether to use content as indexable text.  

        Returns:  
        updated_file (Dict[str, Any]): Updated file information.  
        """  
        if fileId not in self.files:
            return {"error": "File not found"}
            
        file = self.files[fileId]
        file["modifiedTime"] = str(int(time.time()))
        
        if addParents:
            if "parents" not in file:
                file["parents"] = []
            file["parents"].append(addParents)
            
        if removeParents and "parents" in file:
            file["parents"] = [p for p in file["parents"] if p != removeParents]
            
        return file