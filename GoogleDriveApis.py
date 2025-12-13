"""
Inspired by https://developers.google.com/workspace/drive/api/reference/rest/v3

-Uses a stateful approach because Google Drive API operations depend on user authentication.
-Naming conventions differ (e.g., insert_file(...)---it's just a preference thing (we believe 
insert_file is more descriptive than post_file))
"""
import copy
import uuid
from typing import Dict, Union, Any, Optional, List
from datetime import datetime
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("GoogleDriveApis")

class GoogleDriveApis:
    """
    A API class for simulating Google Drive operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the GoogleDriveApis instance with in-memory backend for development and testing.
        
        Sets up data structures for managing users, their Drive files, and authentication state.
        Automatically loads default scenario data and authenticates as the first user.
        
        Side Effects:
            - Initializes self.users as empty dictionary (populated by _load_scenario)
            - Sets self._api_description with API identification string
            - Initializes self.current_user as None (set by _load_scenario)
            - Loads DEFAULT_STATE scenario data via _load_scenario()
            - Auto-authenticates as first user if users exist
            - Prints confirmation messages about loaded scenario and authenticated user
            
        Note:
            This is a simulated API for development/testing purposes, not connected to real
            Google Drive servers. All data exists only in memory and is lost when the instance
            is destroyed. Uses stateful authentication approach where current_user tracks
            the authenticated user.
            
        Example:
            >>> api = GoogleDriveApis()
            GoogleDriveApis: Loaded scenario with users and their UUIDs.
            API auto-authenticated as: alice@example.com
            >>> # API is now ready to use with pre-loaded test data
        """
        self.users: Dict[str, Any] = {}
        self._api_description = "This tool belongs to the Google Drive API, which provides core functionality for managing files and folders."
        self.current_user: Optional[str] = None  # Currently authenticated user ID
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the backend's state for testing or reset purposes.
        
        Replaces the current user and Drive data with the provided scenario, enabling consistent
        test environments or state resets during development. Automatically authenticates as the
        first user if no user is currently authenticated.

        Args:
            scenario (Dict): Complete state dictionary to load. Expected structure:
                {
                    "users": {
                        "user-uuid-123": {
                            "first_name": str,
                            "last_name": str,
                            "email": str,
                            "drive_data": {
                                "user_info": {...},
                                "files": {
                                    "file-uuid": {...},
                                    ...
                                }
                            }
                        },
                        ...
                    }
                }
                If "users" key is missing, initializes with empty dict.
                
        Side Effects:
            - Deep copies scenario to prevent external modifications
            - Replaces self.users entirely with scenario data
            - If no current_user and users exist, sets current_user to first user
            - Prints confirmation messages with loaded user count and authenticated user email
            - All previous state is lost (existing files, permissions, etc.)
            
        Note:
            Creates deep copy of scenario to ensure the original DEFAULT_STATE
            remains unmodified for future resets. Auto-authentication provides
            convenient default behavior for testing.
            
        Example:
            >>> api = GoogleDriveApis()
            >>> custom_scenario = {"users": {...}}
            >>> api._load_scenario(custom_scenario)
            GoogleDriveApis: Loaded scenario with users and their UUIDs.
            API auto-authenticated as: alice@example.com
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
        Authenticates a user and sets them as the current active user for subsequent operations.
        
        Changes the authenticated user context, affecting all future API calls until
        authenticate is called again or the instance is reset.

        Args:
            email (str): The user's email address to authenticate as.
                Example: "alice@example.com", "bob@company.com"

        Returns:
            Dict[str, Union[bool, str]]: Authentication result dictionary:
                Success: {
                    "success": True,
                    "message": "Authenticated as {email}"
                }
                Failure: {
                    "success": False,
                    "message": "User with email {email} not found"
                }
                
        Side Effects:
            - Updates self.current_user to the user's UUID if successful
            - Prints confirmation message to console on success
            - All subsequent API calls will operate under this user's context
            
        Note:
            - User must exist in the backend (loaded from scenario)
            - Authentication is required before calling most API methods
            - Can switch between users by calling authenticate again
            - Email lookup is case-sensitive
            
        Example:
            >>> api = GoogleDriveApis()
            >>> result = api.authenticate("alice@example.com")
            GoogleDriveApis: Authenticated as alice@example.com
            >>> if result["success"]:
            ...     # Now all API calls are made as alice
            ...     files = api.list_files()
            >>> 
            >>> # Switch to different user
            >>> api.authenticate("bob@company.com")
            GoogleDriveApis: Authenticated as bob@company.com
        """
        user_id = self._get_user_id_by_email(email)
        if user_id:
            self.current_user = user_id
            print(f"GoogleDriveApis: Authenticated as {email}")
            return {"success": True, "message": f"Authenticated as {email}"}
        return {"success": False, "message": f"User with email {email} not found"}
    
    def _ensure_authenticated(self) -> str:
        """
        Verifies that a user is authenticated before performing operations.
        
        Internal helper method that guards API operations requiring authentication.
        Raises exception if no user is currently authenticated.

        Returns:
            str: The current authenticated user's UUID identifier
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        
        Raises:
            Exception: If no user is authenticated (self.current_user is None)
                Error message: "No authenticated user. Call authenticate() first."
                
        Note:
            - Called internally by most API methods as first step
            - Ensures operations always have valid user context
            - Auto-authentication in __init__ means this typically won't fail
              unless explicitly cleared
            
        Example:
            >>> api = GoogleDriveApis()
            >>> user_id = api._ensure_authenticated()  # Returns user UUID
            >>> # Use user_id for further operations
            >>> 
            >>> # If not authenticated:
            >>> api.current_user = None
            >>> api._ensure_authenticated()  # Raises Exception
            Exception: No authenticated user. Call authenticate() first.
        """
        if not self.current_user:
            raise Exception("No authenticated user. Call authenticate() first.")
        return self.current_user
    
    def _get_current_user_id(self) -> Optional[str]:
        """
        Retrieves the currently authenticated user's UUID identifier.
        
        Returns the user ID of the user currently authenticated to the API instance,
        or None if no authentication has occurred.

        Returns:
            Optional[str]: Current authenticated user's UUID if set, None otherwise.
                Example return: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
                Returns None if not authenticated.
                
        Note:
            - Does not raise exception like _ensure_authenticated()
            - Useful for checking authentication status without error
            - Returns reference to self.current_user
            
        Example:
            >>> api = GoogleDriveApis()
            >>> user_id = api._get_current_user_id()
            >>> if user_id:
            ...     print(f"Authenticated as: {user_id}")
            >>> else:
            ...     print("Not authenticated")
        """
        return self.current_user

    def _generate_id(self) -> str:
        """
        Generates a universally unique identifier (UUID) for new files and folders.
        
        Returns:
            str: A new UUID v4 string in standard format (e.g., "550e8400-e29b-41d4-a716-446655440000")
            
        Note:
            Uses Python's uuid.uuid4() which generates cryptographically strong random UUIDs.
            Collision probability is effectively zero for practical purposes.
            Used for file IDs, permission IDs, and other entity identifiers.
            
        Example:
            >>> api = GoogleDriveApis()
            >>> file_id = api._generate_id()
            >>> len(file_id)  # Standard UUID string length
            36
        """
        return str(uuid.uuid4())
    
    def _timestamp_to_rfc3339(self, timestamp: Union[int, float]) -> str:
        """
        Converts Unix timestamp to RFC3339 formatted datetime string.
        
        Google Drive API uses RFC3339 format for all timestamps. This helper converts
        Unix timestamps (seconds since epoch) to the required format.

        Args:
            timestamp (Union[int, float]): Unix timestamp (seconds since January 1, 1970).
                Example: 1702483200 (December 13, 2023)

        Returns:
            str: RFC3339 formatted datetime string with 'Z' timezone indicator.
                Format: "YYYY-MM-DDTHH:MM:SS.ffffffZ"
                Example: "2023-12-13T14:30:00.000000Z"
                
        Note:
            - Appends 'Z' to indicate UTC timezone
            - Uses datetime.fromtimestamp for conversion
            - Returns ISO 8601 format which is compatible with RFC3339
            
        Example:
            >>> api = GoogleDriveApis()
            >>> rfc_time = api._timestamp_to_rfc3339(1702483200)
            >>> print(rfc_time)  # "2023-12-13T14:00:00Z" (approximate)
        """
        return datetime.fromtimestamp(timestamp).isoformat() + 'Z'
    
    def _rfc3339_now(self) -> str:
        """
        Gets current time in RFC3339 format for timestamp fields.
        
        Convenience method that returns the current moment in the RFC3339 format
        required by Google Drive API.

        Returns:
            str: Current time in RFC3339 format with 'Z' timezone indicator.
                Format: "YYYY-MM-DDTHH:MM:SS.ffffffZ"
                Example: "2025-12-13T14:30:45.123456Z"
                
        Note:
            - Automatically appends 'Z' to indicate UTC timezone
            - Commonly used for createdTime, modifiedTime, viewedByMeTime fields
            - Each call returns current time (not cached)
            
        Example:
            >>> api = GoogleDriveApis()
            >>> now = api._rfc3339_now()
            >>> print(now)  # "2025-12-13T14:30:45.123456Z"
        """
        return datetime.now().isoformat() + 'Z'

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """
        Resolves a user email address to their internal UUID identifier.
        
        Searches all users to find the one matching the provided email address.

        Args:
            email (str): The user's email address.
                Example: "alice@example.com", "bob@company.com"

        Returns:
            Optional[str]: The user's UUID if found, None if no user has that email.
                Example return: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
                
        Note:
            Performs linear search through all users. Email must match exactly (case-sensitive).
            Used internally by authenticate() and other methods requiring email lookup.
            
        Example:
            >>> api = GoogleDriveApis()
            >>> user_id = api._get_user_id_by_email("alice@example.com")
            >>> if user_id:
            ...     print(f"Found user: {user_id}")
        """
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """
        Resolves an internal UUID identifier to user email address.
        
        Reverse lookup of _get_user_id_by_email, converting UUID to email.

        Args:
            user_id (str): The user's UUID identifier.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[str]: The user's email address if user exists, None if not found.
                Example return: "alice@example.com"
                
        Example:
            >>> api = GoogleDriveApis()
            >>> email = api._get_user_email_by_id("user-uuid-123")
            >>> print(f"User email: {email}")
        """
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _get_user_drive_data(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves a user's complete Google Drive data structure.
        
        Returns the drive_data dictionary containing user_info and files.

        Args:
            user_id (str): The user's internal UUID identifier.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[Dict]: The user's drive_data dictionary if found, None if user doesn't exist.
                Structure: {
                    "user_info": {...},  # User profile and storage quota
                    "files": {...}       # Dictionary of file_id: file_data
                }
                Returns None if user not found or has no drive_data.
                
        Note:
            Returns reference to actual data structure (not a copy), allowing direct modification.
            
        Example:
            >>> api = GoogleDriveApis()
            >>> drive_data = api._get_user_drive_data("user-uuid-123")
            >>> if drive_data:
            ...     files = drive_data.get("files", {})
            ...     print(f"User has {len(files)} files")
        """
        return self.users.get(user_id, {}).get("drive_data")

    def _get_user_files(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves a user's files dictionary directly.
        
        Convenience method that extracts just the files from drive_data.

        Args:
            user_id (str): The user's internal UUID identifier.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[Dict]: Dictionary of file_id: file_data mappings, or None if not found.
                Structure: {"file-uuid-1": {...}, "file-uuid-2": {...}, ...}
                Returns None if user not found or has no drive_data.
                
        Example:
            >>> api = GoogleDriveApis()
            >>> files = api._get_user_files("user-uuid-123")
            >>> if files:
            ...     for file_id, file_data in files.items():
            ...         print(f"{file_id}: {file_data.get('name')}")
        """
        drive_data = self._get_user_drive_data(user_id)
        return drive_data.get("files") if drive_data else None

    def _get_user_info(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves a user's Drive profile information and storage quota.
        
        Returns user_info containing display name, email, and storage quota details.

        Args:
            user_id (str): The user's internal UUID identifier.
                Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        Returns:
            Optional[Dict]: The user's user_info dictionary if found, None if not available.
                Structure: {
                    "name": str,
                    "email": str,
                    "storage_quota": {
                        "total": int,  # Total storage in bytes
                        "used": int    # Used storage in bytes
                    }
                }
                Returns None if user not found or has no drive_data.
                
        Example:
            >>> api = GoogleDriveApis()
            >>> user_info = api._get_user_info("user-uuid-123")
            >>> if user_info:
            ...     quota = user_info.get("storage_quota", {})
            ...     print(f"Storage: {quota['used']}/{quota['total']} bytes")
        """
        drive_data = self._get_user_drive_data(user_id)
        return drive_data.get("user_info") if drive_data else None

    def get_user_info(self) -> Dict[str, Any]:
        """
        Retrieves information about the authenticated user, their Drive, and system capabilities.
        
        Corresponds to the Google Drive API's "About" resource, providing user profile data
        and storage quota information.
        
        Real API endpoint: GET /drive/v3/about

        Returns:
            Dict[str, Any]: About resource containing user and Drive information:
                {
                    "kind": "drive#about",
                    "user": {
                        "kind": "drive#user",
                        "displayName": str,     # User's display name or email
                        "emailAddress": str,    # User's email address
                        "me": True              # Indicates current user
                    },
                    "storageQuota": {
                        "limit": str,           # Total storage in bytes (as string)
                        "usage": str,           # Used storage in bytes (as string)
                        "usageInDrive": str     # Drive-specific usage in bytes
                    }
                }
                
        Raises:
            Exception: If no user is authenticated (via _ensure_authenticated)
            
        Note:
            - Storage values are returned as strings per Google Drive API format
            - Default storage limit is 15GB (15000000000 bytes)
            - If user has no user_info, returns minimal structure with email only
            - me field always True for authenticated user
            
        Example:
            >>> api = GoogleDriveApis()
            >>> api.authenticate("alice@example.com")
            >>> about = api.get_user_info()
            >>> print(f"User: {about['user']['displayName']}")
            >>> quota = about['storageQuota']
            >>> used_gb = int(quota['usage']) / (1024**3)
            >>> total_gb = int(quota['limit']) / (1024**3)
            >>> print(f"Storage: {used_gb:.2f} GB / {total_gb:.2f} GB")
        """
        user_id = self._ensure_authenticated()
        user_info = self._get_user_info(user_id)
        user_email = self._get_user_email_by_id(user_id)
        
        if user_info:
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
        Lists files and folders in the authenticated user's Drive with filtering and pagination.
        
        Provides comprehensive file listing with support for query-based filtering,
        sorting, and pagination. Mimics Google Drive API list files functionality.
        
        Real API endpoint: GET /drive/v3/files

        Args:
            q (Optional[str]): Query string for filtering results using Google Drive query syntax.
                Supported query formats:
                - "name contains 'text'": Files with text in name (case-insensitive)
                - "trashed = true": Only trashed files
                - "trashed = false": Only non-trashed files (default behavior)
                - "starred = true": Only starred files
                - "shared = true" or "'me' in owners": Shared files
                - "mimeType = 'type'": Files of specific MIME type
                - "'parent-id' in parents": Files in specific folder
                Example: "name contains 'project' and trashed = false"
                Default: None (returns all non-trashed files)
            page_size (int): Maximum number of files to return per page.
                Valid range: 1-1000
                Default: 100
            page_token (Optional[str]): Token for continuing a previous list request.
                Obtained from nextPageToken in previous response.
                Value is string representation of start index.
                Default: None (start from beginning)
            order_by (Optional[str]): Comma-separated list of sort keys with optional direction.
                Valid keys:
                - "name": Sort by file name (alphabetical)
                - "createdTime": Sort by creation timestamp
                - "modifiedTime": Sort by last modified timestamp
                - "starred": Sort by starred status
                - "folder", "quotaBytesUsed", "recency", "sharedWithMeTime", "viewedByMeTime": Also supported
                Direction: Append " desc" for descending (e.g., "name desc")
                Example: "modifiedTime desc", "name"
                Default: None (no specific ordering)
            spaces (str): Comma-separated list of spaces to query.
                Supported values: "drive", "appDataFolder"
                Default: "drive"

        Returns:
            Dict[str, Any]: Files list resource with structure:
                {
                    "kind": "drive#fileList",
                    "incompleteSearch": False,
                    "files": [
                        {
                            "kind": "drive#file",
                            "id": str,
                            "name": str,
                            "mimeType": str,
                            "createdTime": str,         # RFC3339 format
                            "modifiedTime": str,        # RFC3339 format
                            "viewedByMeTime": str,      # RFC3339 format
                            "owners": List[Dict],
                            "parents": List[str],
                            "size": str,
                            "starred": bool,
                            "trashed": bool,
                            "shared": bool,
                            "capabilities": Dict,
                            # ... other file metadata
                        },
                        ...
                    ],
                    "nextPageToken": str  # Present if more results available
                }
                
        Raises:
            Exception: If no user is authenticated (via _ensure_authenticated)
            
        Note:
            - Timestamps are automatically converted to RFC3339 format
            - Default behavior excludes trashed files unless explicitly requested
            - Pagination tokens are simple string indices (not opaque tokens)
            - Files are deep copied to prevent accidental modifications
            - Query parsing supports subset of Google Drive query syntax
            - nextPageToken only present when more results available
            
        Example:
            >>> api = GoogleDriveApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # List all non-trashed files
            >>> result = api.list_files()
            >>> print(f"Found {len(result['files'])} files")
            >>> 
            >>> # Search for specific files
            >>> result = api.list_files(q="name contains 'report'")
            >>> for file in result['files']:
            ...     print(f"- {file['name']}")
            >>> 
            >>> # Get starred files, sorted by modification date
            >>> result = api.list_files(
            ...     q="starred = true",
            ...     order_by="modifiedTime desc",
            ...     page_size=50
            ... )
            >>> 
            >>> # Pagination example
            >>> page1 = api.list_files(page_size=10)
            >>> if 'nextPageToken' in page1:
            ...     page2 = api.list_files(page_size=10, page_token=page1['nextPageToken'])
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
        Retrieves complete metadata for a specific file or folder by its ID.
        
        Returns detailed file information including metadata, permissions, timestamps,
        and capabilities. Automatically updates viewing metadata when accessed.
        
        Real API endpoint: GET /drive/v3/files/{fileId}

        Args:
            fileId (str): The unique identifier of the file or folder.
                Example: "1a2b3c4d5e6f7g8h9i0j", "550e8400-e29b-41d4-a716-446655440000"
            fields (Optional[str]): Comma-separated list of fields to include in response.
                Use "*" for all fields (default).
                Example: "id,name,mimeType,createdTime"
                Note: In this simulation, fields parameter is accepted but all fields are returned.
                Default: "*"

        Returns:
            Dict[str, Any]: Complete file resource with structure:
                {
                    "kind": "drive#file",
                    "id": str,
                    "name": str,
                    "mimeType": str,
                    "createdTime": str,         # RFC3339 format
                    "modifiedTime": str,        # RFC3339 format
                    "viewedByMeTime": str,      # RFC3339 format (updated on access)
                    "lastViewingUser": str,     # Email of last viewer (updated on access)
                    "owners": List[Dict],
                    "parents": List[str],
                    "size": str,                # File size in bytes (as string)
                    "starred": bool,
                    "trashed": bool,
                    "shared": bool,
                    "description": str,         # If set
                    "capabilities": {
                        "canEdit": bool,
                        "canComment": bool,
                        "canShare": bool,
                        "canCopy": bool,
                        "canDelete": bool,
                        "canDownload": bool,
                        "canRename": bool,
                        "canTrash": bool
                    },
                    # ... other file metadata
                }
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - User data not found: "User data not found"
                - File not found: "File not found: {fileId}"
                
        Side Effects:
            - Updates file's lastViewingUser to current user's email
            - Updates file's viewedByMeTime to current timestamp
            - Changes persist for subsequent API calls
            
        Note:
            - Timestamps are automatically converted to RFC3339 format if stored as integers
            - Capabilities are auto-generated if not present (all permissions True)
            - Returns deep copy to prevent accidental modifications
            - Works for both files and folders (folders have mimeType "application/vnd.google-apps.folder")
            
        Example:
            >>> api = GoogleDriveApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Get file metadata
            >>> file = api.get_file("file-uuid-123")
            >>> print(f"Name: {file['name']}")
            >>> print(f"Type: {file['mimeType']}")
            >>> print(f"Size: {file['size']} bytes")
            >>> print(f"Last viewed: {file['viewedByMeTime']}")
            >>> 
            >>> # Check permissions
            >>> if file['capabilities']['canEdit']:
            ...     print("You can edit this file")
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
        Creates a new file or folder in Google Drive.
        
        Generates a new file with unique ID, initializes metadata, and adds it to the
        user's Drive. Automatically updates storage quota.
        
        Real API endpoint: POST /drive/v3/files

        Args:
            name (str): The name of the file or folder.
                Example: "Project Report.pdf", "My Folder"
            mimeType (str): The MIME type defining the file format.
                Common types:
                - "application/octet-stream": Generic binary file (default)
                - "application/vnd.google-apps.folder": Folder
                - "application/pdf": PDF document
                - "text/plain": Plain text file
                - "image/jpeg", "image/png": Images
                - "application/vnd.google-apps.document": Google Doc
                - "application/vnd.google-apps.spreadsheet": Google Sheet
                Default: "application/octet-stream"
            parents (Optional[List[str]]): List of parent folder IDs.
                If None or empty, file is placed in "My Drive" (parent="root").
                Example: ["folder-uuid-123"], ["root"]
                Default: None (uses ["root"])
            description (Optional[str]): Short description of the file.
                Example: "Q4 sales report for management review"
                Default: None (no description)
            starred (bool): Whether to mark the file as starred.
                Default: False

        Returns:
            Dict[str, Any]: Complete file resource with structure:
                {
                    "kind": "drive#file",
                    "id": str,                  # Generated UUID
                    "name": str,
                    "mimeType": str,
                    "createdTime": str,         # RFC3339 format (current time)
                    "modifiedTime": str,        # RFC3339 format (current time)
                    "viewedByMeTime": str,      # RFC3339 format (current time)
                    "owners": [{
                        "kind": "drive#user",
                        "displayName": str,
                        "emailAddress": str,
                        "me": True
                    }],
                    "parents": List[str],       # Parent folder IDs
                    "size": "0",                # Initial size (string)
                    "starred": bool,
                    "trashed": False,
                    "shared": False,
                    "capabilities": {           # All permissions True
                        "canEdit": True,
                        "canComment": True,
                        "canShare": True,
                        "canCopy": True,
                        "canDelete": True,
                        "canDownload": True,
                        "canRename": True,
                        "canTrash": True
                    },
                    "description": str          # If provided
                }
        
        Raises:
            Exception: If no user is authenticated (via _ensure_authenticated)
                
        Side Effects:
            - Generates new UUID for file ID
            - Adds file to user's drive_data.files dictionary
            - If user has no drive_data, initializes it with default structure
            - Updates user's storage quota (used bytes) by file size
            - Sets all timestamps to current time
            - Prints confirmation message with file name, user email, and file ID
            
        Note:
            - File ID is auto-generated and guaranteed unique
            - Initial file size is "0" (as string per Google Drive API format)
            - All timestamps (created, modified, viewed) set to same value initially
            - Owners list includes only the creating user
            - All capabilities default to True
            - If drive_data doesn't exist, creates it with 15GB default quota
            
        Example:
            >>> api = GoogleDriveApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Create a document
            >>> file = api.create_file(
            ...     name="Meeting Notes.txt",
            ...     mimeType="text/plain",
            ...     description="Notes from team meeting",
            ...     starred=True
            ... )
            File 'Meeting Notes.txt' created for alice@example.com with ID: 550e8400-...
            >>> print(f"Created file: {file['id']}")
            >>> 
            >>> # Create a folder
            >>> folder = api.create_file(
            ...     name="Project Files",
            ...     mimeType="application/vnd.google-apps.folder"
            ... )
            >>> 
            >>> # Create file in specific folder
            >>> file_in_folder = api.create_file(
            ...     name="Report.pdf",
            ...     mimeType="application/pdf",
            ...     parents=[folder['id']]
            ... )
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
        
        # Update storage quota
        if user_info and "storage_quota" in user_info:
            file_size = int(new_file.get("size", "0")) if isinstance(new_file.get("size"), str) else new_file.get("size", 0)
            user_info["storage_quota"]["used"] += file_size
        
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
        Updates a file's metadata, properties, and parent folder relationships.
        
        Allows modification of various file attributes including name, type, description,
        status flags, and parent folder hierarchy. All fields are optional.
        
        Real API endpoint: PATCH /drive/v3/files/{fileId}

        Args:
            fileId (str): The unique identifier of the file to update.
                Example: "550e8400-e29b-41d4-a716-446655440000"
            name (Optional[str]): New name for the file.
                If None, name remains unchanged.
                Example: "Updated Report.pdf"
                Default: None
            mimeType (Optional[str]): New MIME type for the file.
                If None, MIME type remains unchanged.
                Example: "application/pdf"
                Default: None
            description (Optional[str]): New description for the file.
                If None, description remains unchanged.
                Example: "Final version approved by management"
                Default: None
            starred (Optional[bool]): New starred status.
                True: Star the file
                False: Unstar the file
                None: Keep current status
                Default: None
            trashed (Optional[bool]): New trash status.
                True: Move file to trash
                False: Restore file from trash
                None: Keep current status
                Default: None
            addParents (Optional[str]): Comma-separated list of parent folder IDs to add.
                File will appear in these folders in addition to existing parents.
                Example: "folder-uuid-1,folder-uuid-2"
                Default: None
            removeParents (Optional[str]): Comma-separated list of parent folder IDs to remove.
                File will no longer appear in these folders.
                If all parents removed, file is moved to root.
                Example: "old-folder-uuid"
                Default: None

        Returns:
            Dict[str, Any]: Updated file resource with complete metadata.
                Structure same as get_file() return value.
                Includes "kind": "drive#file" and all file properties.
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - User data not found: "User data not found"
                - File not found: "File not found: {fileId}"
                
        Side Effects:
            - Modifies specified file properties in backend storage
            - Updates file's modifiedTime to current timestamp
            - Updates file's viewedByMeTime to current timestamp
            - Ensures parents list always contains at least one parent (defaults to "root")
            - Converts parents to list if stored as single string
            - Prints confirmation message with file ID and user email
            
        Note:
            - Only specified fields are updated; None values preserve existing data
            - Parent modifications use comma-separated strings, not lists
            - Adding/removing parents happens after other updates
            - File must have at least one parent (root if all others removed)
            - Returns deep copy to prevent accidental further modifications
            
        Example:
            >>> api = GoogleDriveApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Rename and star a file
            >>> updated = api.update_file(
            ...     fileId="file-uuid-123",
            ...     name="Important Report.pdf",
            ...     starred=True
            ... )
            File 'file-uuid-123' updated for alice@example.com
            >>> 
            >>> # Move file to trash
            >>> api.update_file(fileId="file-uuid-456", trashed=True)
            >>> 
            >>> # Move file to different folder
            >>> api.update_file(
            ...     fileId="file-uuid-789",
            ...     addParents="new-folder-uuid",
            ...     removeParents="old-folder-uuid"
            ... )
            >>> 
            >>> # Update description only
            >>> api.update_file(
            ...     fileId="file-uuid-abc",
            ...     description="Updated with latest data"
            ... )
        """
        user_id = self._ensure_authenticated()
        files = self._get_user_files(user_id)
        
        if files is None:
            raise Exception("User data not found")

        if fileId not in files:
            raise Exception(f"File not found: {fileId}")

        file = files[fileId]
        
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
        Permanently deletes a file without moving it to the trash.
        
        Removes the file entirely from the user's Drive and frees up storage quota.
        This operation cannot be undone.
        
        Real API endpoint: DELETE /drive/v3/files/{fileId}

        Args:
            fileId (str): The unique identifier of the file to delete.
                Example: "550e8400-e29b-41d4-a716-446655440000"

        Returns:
            None: This method doesn't return a value on success.
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - User data not found: "User data not found"
                - File not found: "File not found: {fileId}"
                
        Side Effects:
            - Permanently removes file from backend storage
            - Decreases user's storage quota (used bytes) by file size
            - All file data is lost (metadata, content references, permissions)
            - Cannot be undone or recovered
            - Prints confirmation message with file ID and user email
            
        Note:
            - This bypasses the trash; use update_file(trashed=True) to move to trash instead
            - File size is properly parsed whether stored as string or integer
            - Storage quota is only updated if user_info exists
            - Different from trashing: trashed files can be restored, deleted files cannot
            
        Example:
            >>> api = GoogleDriveApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Permanently delete a file
            >>> api.delete_file("file-uuid-123")
            File 'file-uuid-123' deleted for alice@example.com
            >>> 
            >>> # Safer alternative: move to trash first
            >>> api.update_file(fileId="file-uuid-456", trashed=True)
            >>> # Later, can restore: api.update_file(fileId="file-uuid-456", trashed=False)
            >>> # Or permanently delete from trash:
            >>> api.delete_file("file-uuid-456")
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
        Creates a copy of an existing file with optional customization.
        
        Duplicates a file, generating new ID and timestamps while preserving most metadata.
        Useful for creating templates, backups, or working copies.
        
        Real API endpoint: POST /drive/v3/files/{fileId}/copy

        Args:
            fileId (str): The unique identifier of the file to copy.
                Example: "550e8400-e29b-41d4-a716-446655440000"
            name (Optional[str]): Name for the copied file.
                If None, uses "Copy of [original name]" format.
                Example: "Report v2.pdf"
                Default: None (auto-generates name)
            parents (Optional[List[str]]): List of parent folder IDs for the copy.
                If None, uses same parents as original file.
                Example: ["folder-uuid-123"], ["root"]
                Default: None (inherits from original)
            description (Optional[str]): Description for the copied file.
                If None, preserves original file's description.
                Example: "Working copy for editing"
                Default: None (copies original description)

        Returns:
            Dict[str, Any]: Complete file resource for the copied file:
                {
                    "kind": "drive#file",
                    "id": str,                  # New UUID (different from original)
                    "name": str,                # New name or "Copy of..."
                    "mimeType": str,            # Same as original
                    "createdTime": str,         # New timestamp (current time)
                    "modifiedTime": str,        # New timestamp (current time)
                    "viewedByMeTime": str,      # New timestamp (current time)
                    "owners": [...],            # Current user as owner
                    "parents": List[str],       # New or inherited parent IDs
                    "size": str,                # Same as original
                    "starred": bool,            # Inherited from original
                    "trashed": False,
                    "shared": False,            # Reset (not shared)
                    "capabilities": {...},      # Inherited from original
                    "description": str,         # New or inherited
                    # ... other metadata from original
                }
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - User data not found: "User data not found"
                - Original file not found: "File not found: {fileId}"
                
        Side Effects:
            - Generates new UUID for copied file
            - Creates deep copy of original file's metadata
            - Adds copied file to user's files collection
            - Updates user's storage quota (used bytes) by file size
            - Sets all timestamps to current time
            - Resets sharing status (shared=False)
            - Prints confirmation message with original ID, new name, new ID, and user email
            
        Note:
            - Copied file gets new ID, creation/modification timestamps
            - Most metadata (MIME type, size, capabilities, starred status) is preserved
            - Sharing information is not copied (shared=False)
            - Storage quota increases by file size
            - Original file remains unchanged
            - Description can be overridden or inherited from original
            - If name not provided, automatically prefixes with "Copy of "
            
        Example:
            >>> api = GoogleDriveApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Simple copy with auto-generated name
            >>> copy1 = api.copy_file(fileId="file-uuid-123")
            File 'file-uuid-123' copied to 'Copy of Report.pdf' with ID: 550e8400-... for alice@example.com
            >>> print(copy1['name'])  # "Copy of Report.pdf"
            >>> 
            >>> # Copy with custom name and description
            >>> copy2 = api.copy_file(
            ...     fileId="file-uuid-123",
            ...     name="Draft Report.pdf",
            ...     description="Working draft for review"
            ... )
            >>> 
            >>> # Copy to different folder
            >>> copy3 = api.copy_file(
            ...     fileId="file-uuid-123",
            ...     name="Backup Report.pdf",
            ...     parents=["backup-folder-uuid"]
            ... )
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

        # Update storage quota with proper error checking
        user_drive_data = self.users[user_id].get("drive_data")
        if user_drive_data:
            user_info = user_drive_data.get("user_info")
            if user_info and "storage_quota" in user_info:
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
        Creates a permission for a file, granting access to users, groups, or domains.
        
        Adds sharing permissions to a file, allowing others to view, comment, or edit.
        Marks the file as shared and updates the owners/collaborators list.
        
        Real API endpoint: POST /drive/v3/files/{fileId}/permissions

        Args:
            fileId (str): The unique identifier of the file or folder to share.
                Example: "550e8400-e29b-41d4-a716-446655440000"
            role (str): The access level granted by this permission.
                Valid values:
                - "reader": Can view and download (read-only)
                - "commenter": Can view, download, and comment
                - "writer": Can view, download, comment, and edit
                - "fileOrganizer": Can organize files within shared drives
                - "organizer": Can organize content in shared drives
                - "owner": Full ownership rights (transfer ownership)
                Example: "writer", "reader"
            type (str): The category of entity being granted permission.
                Valid values:
                - "user": Individual user (requires emailAddress)
                - "group": Google Group (requires emailAddress)
                - "domain": Everyone in a domain (requires domain)
                - "anyone": Anyone on the internet (public)
                Example: "user", "anyone"
            emailAddress (Optional[str]): Email of user or group to grant permission.
                Required for type="user" or type="group".
                Example: "bob@example.com", "team@company.com"
                Default: None
            domain (Optional[str]): Domain name for domain-wide permissions.
                Required for type="domain".
                Example: "company.com"
                Default: None

        Returns:
            Dict[str, Any]: Permission resource with structure:
                {
                    "kind": "drive#permission",
                    "id": str,              # Generated UUID
                    "type": str,            # "user", "group", "domain", "anyone"
                    "role": str,            # Access level granted
                    "emailAddress": str,    # If type="user" or "group"
                    "displayName": str,     # User/group name (if found in system)
                    "domain": str           # If type="domain"
                }
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - User data not found: "User data not found"
                - File not found: "File not found: {fileId}"
                - Invalid role: "Invalid role '{role}'. Valid roles are: owner, organizer, ..."
                - Invalid type: "Invalid type '{type}'. Valid types are: user, group, domain, anyone"
                
        Side Effects:
            - Generates new UUID for permission ID
            - Adds user/group to file's owners list with role information
            - Sets file's shared flag to True
            - Updates file's modifiedTime to current timestamp
            - If emailAddress provided, attempts to resolve display name from users
            - Prints confirmation message with file ID, role, and recipient
            
        Note:
            - Display name resolution only works for users in the simulated backend
            - External users default to "External User" as display name
            - File's shared property becomes True after any permission added
            - Permission ID is newly generated (not based on email)
            - Multiple permissions can be added to same file
            
        Example:
            >>> api = GoogleDriveApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Share with specific user (edit access)
            >>> perm = api.create_permission(
            ...     fileId="file-uuid-123",
            ...     role="writer",
            ...     type="user",
            ...     emailAddress="bob@example.com"
            ... )
            Permission created for file 'file-uuid-123': writer access for bob@example.com
            >>> 
            >>> # Share with read-only access
            >>> api.create_permission(
            ...     fileId="file-uuid-456",
            ...     role="reader",
            ...     type="user",
            ...     emailAddress="charlie@example.com"
            ... )
            >>> 
            >>> # Make file public (anyone can view)
            >>> api.create_permission(
            ...     fileId="file-uuid-789",
            ...     role="reader",
            ...     type="anyone"
            ... )
            Permission created for file 'file-uuid-789': reader access for anyone
            >>> 
            >>> # Share with entire domain
            >>> api.create_permission(
            ...     fileId="file-uuid-abc",
            ...     role="commenter",
            ...     type="domain",
            ...     domain="company.com"
            ... )
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
        Lists revision history for a file.
        
        Returns available revisions of a file, showing version history. Currently
        simulates basic revision tracking with current version only.
        
        Real API endpoint: GET /drive/v3/files/{fileId}/revisions

        Args:
            fileId (str): The unique identifier of the file.
                Example: "550e8400-e29b-41d4-a716-446655440000"
            page_size (int): Maximum number of revisions to return per page.
                Valid range: 1-1000
                Default: 200

        Returns:
            Dict[str, Any]: Revisions list resource with structure:
                {
                    "kind": "drive#revisionList",
                    "revisions": [
                        {
                            "kind": "drive#revision",
                            "id": "1",              # Revision number (as string)
                            "mimeType": str,         # File's MIME type
                            "modifiedTime": str,     # RFC3339 timestamp
                            "size": str,             # File size in bytes
                            "keepForever": False,    # Retention setting
                            "published": False       # Publication status
                        }
                    ]
                }
        
        Raises:
            Exception: With descriptive message if:
                - No user is authenticated (via _ensure_authenticated)
                - User data not found: "User data not found"
                - File not found: "File not found: {fileId}"
                
        Note:
            - Current implementation returns only the current version (revision "1")
            - Real Google Drive API maintains full version history
            - modifiedTime uses file's modifiedTime or falls back to createdTime
            - keepForever and published flags always False in simulation
            - Future enhancement could track actual revision history
            
        Example:
            >>> api = GoogleDriveApis()
            >>> api.authenticate("alice@example.com")
            >>> revisions = api.list_revisions(fileId="file-uuid-123")
            >>> print(f"Found {len(revisions['revisions'])} revision(s)")
            >>> current = revisions['revisions'][0]
            >>> print(f"Current version modified: {current['modifiedTime']}")
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
        Resets all simulated data in the backend to its initial default state.
        
        Reloads the default scenario data, clearing all user modifications including created
        files, updated metadata, and permissions. This is a utility function for testing
        purposes and is not a standard Google Drive API endpoint.

        Returns:
            Dict[str, bool]: Status dictionary:
                {"reset_status": True} indicating successful reset
                
        Side Effects:
            - Reloads all backend data from DEFAULT_STATE scenario
            - Resets self.users with all Drive data
            - Re-authenticates as first user (if users exist)
            - All user modifications are lost (created/updated/deleted files, permissions)
            - Prints confirmation messages to console
            
        Note:
            - This is a test utility method not present in real Google Drive API
            - Use for resetting test environments between test runs
            - All in-memory changes are discarded (no persistence)
            - Useful for ensuring clean state in automated testing
            - Returns original users and files from loaded scenario file
            
        Example:
            >>> api = GoogleDriveApis()
            >>> # Make some changes...
            >>> api.create_file(name="Test", mimeType="text/plain")
            >>> api.delete_file(fileId="existing-file-uuid")
            >>> # ... do some testing ...
            >>> result = api.reset_data()  # Clean slate for next test
            GoogleDriveApis: All data reset to default state.
            GoogleDriveApis: Loaded scenario with users and their UUIDs.
            API auto-authenticated as: alice@example.com
            >>> # All changes reverted, back to default state
        """
        self._load_scenario(DEFAULT_STATE)
        print("GoogleDriveApis: All data reset to default state.")
        return {"reset_status": True}

    
    def create_folder(self, name: str, parents: Optional[List[str]] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a new folder in Google Drive.
        
        Convenience method that creates a file with folder MIME type. Functionally
        equivalent to create_file() with mimeType="application/vnd.google-apps.folder".
        
        Real API endpoint: POST /drive/v3/files (with mimeType='application/vnd.google-apps.folder')

        Args:
            name (str): The name of the folder.
                Example: "Project Files", "Documents", "2025 Reports"
            parents (Optional[List[str]]): List of parent folder IDs.
                If None, folder is created in "My Drive" (parent="root").
                Example: ["parent-folder-uuid"], ["root"]
                Default: None (uses ["root"])
            description (Optional[str]): Short description of the folder.
                Example: "All project-related documents"
                Default: None

        Returns:
            Dict[str, Any]: Complete folder resource (same structure as create_file).
                Key differences from files:
                - mimeType: "application/vnd.google-apps.folder"
                - size: "0" (folders don't have size)
                - Can contain other files/folders as children
                
        Raises:
            Exception: If no user is authenticated (via _ensure_authenticated)
                
        Side Effects:
            - Creates new folder using create_file() internally
            - All side effects of create_file() apply
            - Prints confirmation message with folder name and ID
            
        Note:
            - Folders are just files with special MIME type
            - Can be nested by specifying parent folder IDs
            - Folders can be shared, starred, trashed like regular files
            - Use returned ID as parent for files you want in this folder
            
        Example:
            >>> api = GoogleDriveApis()
            >>> api.authenticate("alice@example.com")
            >>> 
            >>> # Create folder in My Drive
            >>> folder = api.create_folder(name="Work Documents")
            File 'Work Documents' created for alice@example.com with ID: 550e8400-...
            >>> print(f"Created folder: {folder['id']}")
            >>> 
            >>> # Create subfolder
            >>> subfolder = api.create_folder(
            ...     name="2025 Reports",
            ...     parents=[folder['id']],
            ...     description="Annual reports for 2025"
            ... )
            >>> 
            >>> # Create file in folder
            >>> file = api.create_file(
            ...     name="Report.pdf",
            ...     mimeType="application/pdf",
            ...     parents=[subfolder['id']]
            ... )
        """
        return self.create_file(
            name=name,
            mimeType="application/vnd.google-apps.folder",
            parents=parents,
            description=description
        )