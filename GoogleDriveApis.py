import time
import copy
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

DEFAULT_STATE: Dict[str, Any] = {
    "users": {
        "alice.smith@cloudrive.com": {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@cloudrive.com",
            "drive_data": {
                "user_info": {
                    "name": "Alice Smith",
                    "email": "alice.smith@cloudrive.com",
                    "storage_quota": {"total": 100 * 1024 * 1024 * 1024, "used": 50 * 1024 * 1024} # 100 GB total, 50 MB used
                },
                "files": {
                    "file_alice_project_plan.docx": {
                        "id": "file_alice_project_plan.docx",
                        "name": "Project_Plan_Q3.docx",
                        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "createdTime": int((datetime.now() - timedelta(days=15, hours=3)).timestamp()),
                        "modifiedTime": int((datetime.now() - timedelta(days=10, hours=1)).timestamp()),
                        "owners": [{"displayName": "Alice Smith", "emailAddress": "alice.smith@cloudrive.com"}],
                        "parents": ["root"],
                        "size": 152000 # in bytes
                    },
                    "file_alice_budget_2025.xlsx": {
                        "id": "file_alice_budget_2025.xlsx",
                        "name": "Annual_Budget_2025.xlsx",
                        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "createdTime": int((datetime.now() - timedelta(days=30)).timestamp()),
                        "modifiedTime": int((datetime.now() - timedelta(days=25, minutes=30)).timestamp()),
                        "owners": [{"displayName": "Alice Smith", "emailAddress": "alice.smith@cloudrive.com"}],
                        "parents": ["root"],
                        "size": 230000
                    },
                    "file_alice_family_vacation.jpg": {
                        "id": "file_alice_family_vacation.jpg",
                        "name": "Family_Vacation_2024.jpg",
                        "mimeType": "image/jpeg",
                        "createdTime": int((datetime.now() - timedelta(days=60)).timestamp()),
                        "modifiedTime": int((datetime.now() - timedelta(days=60)).timestamp()),
                        "owners": [{"displayName": "Alice Smith", "emailAddress": "alice.smith@cloudrive.com"}],
                        "parents": ["root"],
                        "size": 5120000 # 5 MB
                    },
                    "folder_alice_presentations": {
                        "id": "folder_alice_presentations",
                        "name": "Presentations",
                        "mimeType": "application/vnd.google-apps.folder",
                        "createdTime": int((datetime.now() - timedelta(days=20)).timestamp()),
                        "modifiedTime": int((datetime.now() - timedelta(days=5)).timestamp()),
                        "owners": [{"displayName": "Alice Smith", "emailAddress": "alice.smith@cloudrive.com"}],
                        "parents": ["root"],
                        "size": 0
                    },
                    "file_alice_marketing_deck.pptx": {
                        "id": "file_alice_marketing_deck.pptx",
                        "name": "Marketing_Strategy_Deck.pptx",
                        "mimeType": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        "createdTime": int((datetime.now() - timedelta(days=18)).timestamp()),
                        "modifiedTime": int((datetime.now() - timedelta(days=5)).timestamp()),
                        "owners": [{"displayName": "Alice Smith", "emailAddress": "alice.smith@cloudrive.com"}],
                        "parents": ["folder_alice_presentations"],
                        "size": 8900000 # 8.9 MB
                    }
                },
                "next_file_id_counter": 5 # Counter for this user's files (based on unique names for simplicity)
            }
        },
        "bob.johnson@cloudrive.com": {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@cloudrive.com",
            "drive_data": {
                "user_info": {
                    "name": "Bob Johnson",
                    "email": "bob.johnson@cloudrive.com",
                    "storage_quota": {"total": 50 * 1024 * 1024 * 1024, "used": 10 * 1024 * 1024} # 50 GB total, 10 MB used
                },
                "files": {
                    "file_bob_team_meeting_notes.txt": {
                        "id": "file_bob_team_meeting_notes.txt",
                        "name": "Team_Meeting_Notes_07-2025.txt",
                        "mimeType": "text/plain",
                        "createdTime": int((datetime.now() - timedelta(days=7)).timestamp()),
                        "modifiedTime": int((datetime.now() - timedelta(days=1, hours=2)).timestamp()),
                        "owners": [{"displayName": "Bob Johnson", "emailAddress": "bob.johnson@cloudrive.com"}],
                        "parents": ["root"],
                        "size": 50000
                    },
                    "file_bob_client_proposal.pdf": {
                        "id": "file_bob_client_proposal.pdf",
                        "name": "Client_Proposal_Acme_Corp.pdf",
                        "mimeType": "application/pdf",
                        "createdTime": int((datetime.now() - timedelta(days=10)).timestamp()),
                        "modifiedTime": int((datetime.now() - timedelta(days=3)).timestamp()),
                        "owners": [{"displayName": "Bob Johnson", "emailAddress": "bob.johnson@cloudrive.com"}],
                        "parents": ["root"],
                        "size": 3500000 # 3.5 MB
                    }
                },
                "next_file_id_counter": 2
            }
        },
        "charlie.davis@cloudrive.com": {
            "first_name": "Charlie",
            "last_name": "Davis",
            "email": "charlie.davis@cloudrive.com",
            "drive_data": {
                "user_info": {
                    "name": "Charlie Davis",
                    "email": "charlie.davis@cloudrive.com",
                    "storage_quota": {"total": 25 * 1024 * 1024 * 1024, "used": 2 * 1024 * 1024} # 25 GB total, 2 MB used
                },
                "files": {
                    "file_charlie_research_paper.pdf": {
                        "id": "file_charlie_research_paper.pdf",
                        "name": "Quantum_Physics_Research.pdf",
                        "mimeType": "application/pdf",
                        "createdTime": int((datetime.now() - timedelta(days=40)).timestamp()),
                        "modifiedTime": int((datetime.now() - timedelta(days=20)).timestamp()),
                        "owners": [{"displayName": "Charlie Davis", "emailAddress": "charlie.davis@cloudrive.com"}],
                        "parents": ["root"],
                        "size": 2000000
                    }
                },
                "next_file_id_counter": 1
            }
        },
        "diana.perez@cloudrive.com": {
            "first_name": "Diana",
            "last_name": "Perez",
            "email": "diana.perez@cloudrive.com",
            "drive_data": {
                "user_info": {
                    "name": "Diana Perez",
                    "email": "diana.perez@cloudrive.com",
                    "storage_quota": {"total": 100 * 1024 * 1024 * 1024, "used": 0} # 100 GB total, 0 used
                },
                "files": {},
                "next_file_id_counter": 0
            }
        },
        "eve.wang@cloudrive.com": {
            "first_name": "Eve",
            "last_name": "Wang",
            "email": "eve.wang@cloudrive.com",
            "drive_data": {
                "user_info": {
                    "name": "Eve Wang",
                    "email": "eve.wang@cloudrive.com",
                    "storage_quota": {"total": 200 * 1024 * 1024 * 1024, "used": 15 * 1024 * 1024 * 1024} # 200 GB total, 15 GB used
                },
                "files": {
                    "file_eve_video_project_part1.mp4": {
                        "id": "file_eve_video_project_part1.mp4",
                        "name": "Travel_Vlog_Project_Part1.mp4",
                        "mimeType": "video/mp4",
                        "createdTime": int((datetime.now() - timedelta(days=90)).timestamp()),
                        "modifiedTime": int((datetime.now() - timedelta(days=1)).timestamp()),
                        "owners": [{"displayName": "Eve Wang", "emailAddress": "eve.wang@cloudrive.com"}],
                        "parents": ["root"],
                        "size": 10 * 1024 * 1024 * 1024 # 10 GB
                    },
                    "file_eve_presentation_notes.txt": {
                        "id": "file_eve_presentation_notes.txt",
                        "name": "Presentation_Notes.txt",
                        "mimeType": "text/plain",
                        "createdTime": int((datetime.now() - timedelta(days=5)).timestamp()),
                        "modifiedTime": int((datetime.now() - timedelta(days=2, hours=4)).timestamp()),
                        "owners": [{"displayName": "Eve Wang", "emailAddress": "eve.wang@cloudrive.com"}],
                        "parents": ["root"],
                        "size": 10000
                    }
                },
                "next_file_id_counter": 2
            }
        }
    },
    "current_user": "alice.smith@cloudrive.com",
}

class GoogleDriveApis:
    def __init__(self, state: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes the GoogleDriveAPI instance with a given state.
        If no state is provided, it uses a deep copy of the DEFAULT_STATE.
        """
        self.state: Dict[str, Any] = copy.deepcopy(state if state is not None else DEFAULT_STATE)
        self._api_description = "This tool belongs to the GoogleDriveAPI, which provides core functionality for file management in Google Drive."

    def _get_user_drive_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user-specific Google Drive data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's Google Drive data, or None if not found.
        """
        if user_id == 'me':
            user_id = self.state["current_user"]
        return self.state["users"].get(user_id, {}).get("drive_data")

    def _get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user profile information.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's profile information, or None if not found.
        """
        drive_data = self._get_user_drive_data(user_id)
        return drive_data.get("user_info") if drive_data else None

    def _get_user_files(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Helper to get user's files data.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the user's files, or None if not found.
        """
        drive_data = self._get_user_drive_data(user_id)
        return drive_data.get("files") if drive_data else None

    def _get_next_file_id_counter(self, user_id: str) -> Optional[int]:
        """
        Helper to get the next file ID counter for a user.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.

        Returns:
            Optional[int]: The next file ID counter, or None if user data is not found.
        """
        drive_data = self._get_user_drive_data(user_id)
        return drive_data.get("next_file_id_counter") if drive_data else None

    def _increment_next_file_id_counter(self, user_id: str) -> None:
        """
        Helper to increment the next file ID counter for a user.

        Args:
            user_id (str): The ID of the user or 'me' for the current user.
        """
        drive_data = self._get_user_drive_data(user_id)
        if drive_data:
            drive_data["next_file_id_counter"] = drive_data.get("next_file_id_counter", 0) + 1

    def get_about(self, user_id: str = 'me') -> Dict[str, Any]:
        """
        Get information about the user's Google Drive.

        Args:
            user_id (str, optional): User's email address or 'me' for the authenticated user. Defaults to 'me'.

        Returns:
            about_info (Dict[str, Any]): Information about the user's Google Drive,
                                         including user details, storage quota, max upload size,
                                         and app installation status. Returns an error if the user is not found.
        """
        user_info = self._get_user_info(user_id)
        if user_info:
            return {
                "user": copy.deepcopy(user_info),
                "storageQuota": copy.deepcopy(user_info["storage_quota"]),
                "maxUploadSize": "5TB",
                "appInstalled": True
            }
        return {"error": "User not found"}

    def copy_file(self, fileId: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Copy a file within Google Drive for a specific user.

        Args:
            fileId (str): ID of the file to copy.
            user_id (str, optional): User's email address or 'me' for the authenticated user. Defaults to 'me'.

        Returns:
            copied_file (Dict[str, Any]): Information about the copied file if successful,
                                          or an error message if the file or user is not found.
        """
        files = self._get_user_files(user_id)
        user_info = self._get_user_info(user_id)
        if files is None or user_info is None:
            return {"error": "User data not found"}

        if fileId not in files:
            return {"error": "File not found"}

        original_file = files[fileId]
        next_id_counter = self._get_next_file_id_counter(user_id)
        if next_id_counter is None:
             next_id_counter = 1

        # Generate a new unique file ID for the specific user
        new_file_id = f"file_{next_id_counter}_{user_id.split('@')[0]}"
        self._increment_next_file_id_counter(user_id)

        copied_file = {
            **original_file, # Copy all existing attributes
            "id": new_file_id,
            "name": f"Copy of {original_file.get('name', '')}",
            "createdTime": str(int(time.time())), # Update creation time
            "owners": [{
                "displayName": user_info["name"],
                "emailAddress": user_info["email"]
            }]
        }

        files[new_file_id] = copied_file
        return copy.deepcopy(copied_file)

    def create_file(self, user_id: str = 'me') -> Dict[str, Any]:
        """
        Create a new file in Google Drive for a specific user.

        Returns:
            created_file (Dict[str, Any]): Information about the newly created file.
                                          Returns an error if the user is not found.
        """
        files = self._get_user_files(user_id)
        user_info = self._get_user_info(user_id)
        if files is None or user_info is None:
            return {"error": "User data not found"}

        next_id_counter = self._get_next_file_id_counter(user_id)
        if next_id_counter is None:
             next_id_counter = 1

        file_id = f"file_{next_id_counter}_{user_id.split('@')[0]}" # Unique ID per user
        self._increment_next_file_id_counter(user_id)

        new_file = {
            "id": file_id,
            "name": "Untitled",
            "mimeType": "application/vnd.google-apps.document", # Default MIME type
            "createdTime": str(int(time.time())),
            "modifiedTime": str(int(time.time())),
            "owners": [{
                "displayName": user_info["name"],
                "emailAddress": user_info["email"]
            }]
        }

        files[file_id] = new_file
        return copy.deepcopy(new_file)

    def delete_file(self, fileId: str, user_id: str = 'me') -> Dict[str, bool]:
        """
        Delete a file from Google Drive for a specific user.

        Args:
            fileId (str): ID of the file to delete.
            user_id (str, optional): User's email address or 'me' for the authenticated user. Defaults to 'me'.

        Returns:
            deletion_status (Dict[str, bool]): True if deleted successfully, False otherwise.
                                              Returns False if the file or user is not found.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"deletion_status": False, "error": "User data not found"}

        if fileId in files:
            del files[fileId]
            return {"deletion_status": True}
        return {"deletion_status": False}

    def empty_trash(self, user_id: str = 'me') -> Dict[str, bool]:
        """
        Empty the trash in Google Drive for a specific user.
        In this dummy implementation, it always returns True as there's no actual trash to empty.

        Args:
            user_id (str, optional): User's email address or 'me' for the authenticated user. Defaults to 'me'.

        Returns:
            empty_status (Dict[str, bool]): True if emptied successfully, False otherwise.
                                            Returns False if the user is not found.
        """
        # In a real implementation, we would track trashed files separately and remove them here.
        # For now, just check if the user exists.
        if self._get_user_drive_data(user_id) is None:
            return {"empty_status": False, "error": "User data not found"}
        return {"empty_status": True}

    def export_file(self, fileId: str, mimeType: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Export a file to a different format for a specific user.

        Args:
            fileId (str): ID of the file to export.
            mimeType (str): MIME type for the exported file (e.g., "application/pdf", "text/plain").
            user_id (str, optional): User's email address or 'me' for the authenticated user. Defaults to 'me'.

        Returns:
            exported_file (Dict[str, Any]): Information about the exported file,
                                           including its ID, new MIME type, and a dummy export link.
                                           Returns an error if the file or user is not found.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"error": "User data not found"}

        if fileId not in files:
            return {"error": "File not found"}

        return {
            "id": fileId,
            "mimeType": mimeType,
            "exportLinks": {
                mimeType: "https://example.com" # Dummy export link
            }
        }

    def get_file(self, fileId: str, user_id: str = 'me') -> Dict[str, Any]:
        """
        Get information about a specific file for a specific user.

        Args:
            fileId (str): ID of the file.
            user_id (str, optional): User's email address or 'me' for the authenticated user. Defaults to 'me'.

        Returns:
            file_info (Dict[str, Any]): Information about the file if found,
                                         or an error message if the file or user is not found.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"error": "User data not found"}

        if fileId in files:
            return copy.deepcopy(files[fileId]) # Return a copy to prevent external modification
        return {"error": "File not found"}

    def list_files(self, user_id: str = 'me', driveId: str = "", orderBy: str = "", pageSize: int = 0, q: str = "") -> Dict[str, Any]:
        """
        List files in Google Drive for a specific user based on various filters and sorting options.

        Args:
            user_id (str, optional): User's email address or 'me' for the authenticated user. Defaults to 'me'.
            driveId (str, optional): ID of the shared drive to filter by. Defaults to "".
            orderBy (str, optional): Order of the results (e.g., "name", "-modifiedTime"). Defaults to "".
            pageSize (int, optional): Number of files to return. Defaults to 0 (all).
            q (str, optional): Query string for filtering by file name. Defaults to "".

        Returns:
            files_list (Dict[str, Any]): A dictionary containing a list of filtered and sorted files.
                                         Returns an error if the user is not found.
        """
        files_data = self._get_user_files(user_id)
        if files_data is None:
            return {"error": "User data not found"}

        files = list(files_data.values())

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

        return {"files": copy.deepcopy(files)}

    def update_file(self, fileId: str, addParents: str = "", removeParents: str = "", user_id: str = 'me') -> Dict[str, Any]:
        """
        Update a file's properties in Google Drive for a specific user.

        Args:
            fileId (str): ID of the file to update.
            addParents (str, optional): Parents to add to the file. Defaults to "".
            removeParents (str, optional): Parents to remove from the file. Defaults to "".
            user_id (str, optional): User's email address or 'me' for the authenticated user. Defaults to 'me'.

        Returns:
            updated_file (Dict[str, Any]): The updated file information if successful,
                                          or an error message if the file or user is not found.
        """
        files = self._get_user_files(user_id)
        if files is None:
            return {"error": "User data not found"}

        if fileId not in files:
            return {"error": "File not found"}

        file = files[fileId]
        file["modifiedTime"] = str(int(time.time())) # Update modification time

        if addParents:
            if "parents" not in file:
                file["parents"] = []
            if addParents not in file["parents"]: # Avoid duplicate parents
                file["parents"].append(addParents)

        # Remove parents
        if removeParents and "parents" in file:
            file["parents"] = [p for p in file["parents"] if p != removeParents]

        return copy.deepcopy(file)