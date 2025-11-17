import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import API and helper
from GoogleDriveApis import GoogleDriveApis
from UnitTests.test_data_helper import BackendDataLoader

class TestGoogleDriveApis(unittest.TestCase):
    """
    Unit tests for the GoogleDriveApis class with OAuth authentication.
    """

    # Load real data from backend
    real_data = BackendDataLoader.get_googledrive_data()
    
    # Extract real user data
    user_ids = list(real_data.get("users", {}).keys())
    user_id_alice = user_ids[0] if user_ids else "user_001"
    user_id_bob = user_ids[1] if len(user_ids) > 1 else user_id_alice
    
    # Get user data for reference
    user_data_alice = real_data.get("users", {}).get(user_id_alice, {})
    user_data_bob = real_data.get("users", {}).get(user_id_bob, {})
    
    # Get email addresses for authentication
    EMAIL_ALICE = user_data_alice.get("email", "alice@example.com")
    EMAIL_BOB = user_data_bob.get("email", "bob@example.com")
    
    # Extract real file data
    files_alice = user_data_alice.get("drive_data", {}).get("files", {})
    REAL_FILE_ID = next(iter(files_alice), "file1")
    file_data = files_alice.get(REAL_FILE_ID, {})
    REAL_FILE_NAME = file_data.get("name", "Test File")
    
    def setUp(self):
        """Set up the API instance using real data."""
        self.drive_api = GoogleDriveApis()
        # Authenticate as Alice by default
        self.drive_api.authenticate(self.EMAIL_ALICE)

    # --- Authentication Tests ---
    
    def test_authenticate_success(self):
        """Test successful authentication."""
        api = GoogleDriveApis()
        result = api.authenticate(self.EMAIL_ALICE)
        self.assertTrue(result["success"])
        self.assertEqual(api.current_user, self.user_id_alice)

    def test_authenticate_nonexistent_user(self):
        """Test authentication with non-existent user."""
        api = GoogleDriveApis()
        result = api.authenticate("nonexistent@example.com")
        self.assertFalse(result["success"])

    def test_unauthenticated_access(self):
        """Test that methods require authentication."""
        api = GoogleDriveApis()
        api.current_user = None  # Clear auto-authentication
        with self.assertRaises(Exception) as context:
            api.get_user_info()
        self.assertIn("authenticated", str(context.exception).lower())

    # --- User Info Tests ---
    
    def test_get_user_info_alice(self):
        """Test getting user info for authenticated user."""
        result = self.drive_api.get_user_info()
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "drive#about")
        self.assertIn("user", result)
        self.assertEqual(result["user"]["emailAddress"], self.EMAIL_ALICE)

    def test_get_user_info_bob(self):
        """Test getting user info after switching users."""
        self.drive_api.authenticate(self.EMAIL_BOB)
        result = self.drive_api.get_user_info()
        self.assertEqual(result["user"]["emailAddress"], self.EMAIL_BOB)

    # --- File Creation Tests ---
    
    def test_create_file_alice(self):
        """Test creating a file."""
        result = self.drive_api.create_file(name="test_file.txt", mimeType="text/plain")
        self.assertIn("id", result)
        self.assertEqual(result["name"], "test_file.txt")
        self.assertEqual(result["mimeType"], "text/plain")
        self.assertEqual(result["kind"], "drive#file")

    def test_create_file_with_description(self):
        """Test creating a file with description."""
        result = self.drive_api.create_file(
            name="test_file.txt",
            mimeType="text/plain",
            description="Test description"
        )
        self.assertEqual(result["description"], "Test description")

    def test_create_file_starred(self):
        """Test creating a starred file."""
        result = self.drive_api.create_file(
            name="starred_file.txt",
            mimeType="text/plain",
            starred=True
        )
        self.assertTrue(result["starred"])

    # --- File Retrieval Tests ---
    
    def test_get_file_existing(self):
        """Test getting an existing file."""
        # Create a file first
        created = self.drive_api.create_file(name="get_test_file.txt", mimeType="text/plain")
        file_id = created["id"]
        
        # Get the file
        result = self.drive_api.get_file(file_id)
        self.assertEqual(result["id"], file_id)
        self.assertEqual(result["kind"], "drive#file")
        self.assertIn("capabilities", result)

    def test_get_file_not_found(self):
        """Test getting non-existent file."""
        with self.assertRaises(Exception) as context:
            self.drive_api.get_file("nonexistent_file_id")
        self.assertIn("not found", str(context.exception).lower())

    # --- File Listing Tests ---
    
    def test_list_files(self):
        """Test listing files."""
        result = self.drive_api.list_files()
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "drive#fileList")
        self.assertIn("files", result)
        self.assertIsInstance(result["files"], list)

    def test_list_files_with_page_size(self):
        """Test listing files with page size limit."""
        result = self.drive_api.list_files(page_size=1)
        self.assertLessEqual(len(result["files"]), 1)

    def test_list_files_with_order_by_name(self):
        """Test listing files ordered by name."""
        # Create some uniquely named files
        file1 = self.drive_api.create_file(name="zzz_unique_file.txt", mimeType="text/plain")
        file2 = self.drive_api.create_file(name="aaa_unique_file.txt", mimeType="text/plain")
        
        # List with ordering and search for our unique files
        result = self.drive_api.list_files(order_by="name")
        
        # Find positions of our test files in the sorted list
        names = [f["name"] for f in result["files"]]
        try:
            pos_aaa = names.index("aaa_unique_file.txt")
            pos_zzz = names.index("zzz_unique_file.txt")
            # Verify aaa comes before zzz when sorted by name
            self.assertLess(pos_aaa, pos_zzz)
        except ValueError:
            self.fail("Test files not found in list")

    def test_list_files_search_by_name(self):
        """Test searching files by name."""
        # Create a unique file
        unique_name = "unique_search_test_file.txt"
        created = self.drive_api.create_file(name=unique_name, mimeType="text/plain")
        
        # Search for it
        result = self.drive_api.list_files(q=f"name contains '{unique_name}'")
        file_names = [f["name"] for f in result["files"]]
        self.assertIn(unique_name, file_names)

    # --- File Update Tests ---
    
    def test_update_file_name(self):
        """Test updating file name."""
        # Create file
        created = self.drive_api.create_file(name="original_name.txt", mimeType="text/plain")
        file_id = created["id"]
        
        # Update name
        updated = self.drive_api.update_file(file_id, name="new_name.txt")
        self.assertEqual(updated["name"], "new_name.txt")

    def test_update_file_star(self):
        """Test starring a file via update."""
        created = self.drive_api.create_file(name="star_test.txt", mimeType="text/plain")
        file_id = created["id"]
        
        # Star the file
        updated = self.drive_api.update_file(file_id, starred=True)
        self.assertTrue(updated["starred"])

    def test_update_file_trash(self):
        """Test trashing a file via update."""
        created = self.drive_api.create_file(name="trash_test.txt", mimeType="text/plain")
        file_id = created["id"]
        
        # Trash the file
        updated = self.drive_api.update_file(file_id, trashed=True)
        self.assertTrue(updated["trashed"])

    def test_update_file_add_parent(self):
        """Test updating a file by adding a parent."""
        # Create file and folder
        file_result = self.drive_api.create_file(name="update_test_file.txt", mimeType="text/plain")
        file_id = file_result["id"]
        
        folder_result = self.drive_api.create_folder("Test Folder")
        folder_id = folder_result["id"]
        
        # Add parent
        updated = self.drive_api.update_file(file_id, addParents=folder_id)
        self.assertIn(folder_id, updated["parents"])

    # --- File Deletion Tests ---
    
    def test_delete_file(self):
        """Test deleting a file."""
        # Create file
        created = self.drive_api.create_file(name="delete_test.txt", mimeType="text/plain")
        file_id = created["id"]
        
        # Delete it (should not raise exception)
        self.drive_api.delete_file(file_id)

    def test_delete_file_not_found(self):
        """Test deleting non-existent file."""
        with self.assertRaises(Exception) as context:
            self.drive_api.delete_file("nonexistent_file")
        self.assertIn("not found", str(context.exception).lower())

    # --- File Copy Tests ---
    
    def test_copy_file(self):
        """Test copying a file."""
        # Create original
        original = self.drive_api.create_file(name="original.txt", mimeType="text/plain")
        original_id = original["id"]
        
        # Copy it
        copied = self.drive_api.copy_file(original_id, name="copied.txt")
        self.assertNotEqual(copied["id"], original_id)
        self.assertEqual(copied["name"], "copied.txt")
        self.assertEqual(copied["mimeType"], original["mimeType"])

    def test_copy_file_auto_name(self):
        """Test copying a file with auto-generated name."""
        original = self.drive_api.create_file(name="original.txt", mimeType="text/plain")
        original_id = original["id"]
        
        copied = self.drive_api.copy_file(original_id)
        self.assertTrue(copied["name"].startswith("Copy of"))

    def test_copy_file_not_found(self):
        """Test copying non-existent file."""
        with self.assertRaises(Exception) as context:
            self.drive_api.copy_file("nonexistent_file", name="copied.txt")
        self.assertIn("not found", str(context.exception).lower())

    # --- Folder Tests ---
    
    def test_create_folder(self):
        """Test creating a folder."""
        result = self.drive_api.create_folder("Test Folder")
        self.assertIn("id", result)
        self.assertEqual(result["name"], "Test Folder")
        self.assertEqual(result["mimeType"], "application/vnd.google-apps.folder")

    def test_create_folder_with_parent(self):
        """Test creating a folder with parent."""
        # Create parent folder
        parent = self.drive_api.create_folder("Parent Folder")
        parent_id = parent["id"]
        
        # Create child folder
        child = self.drive_api.create_folder("Child Folder", parents=[parent_id])
        self.assertIn(parent_id, child["parents"])

    # --- Permission/Sharing Tests ---
    
    def test_create_permission_user(self):
        """Test creating a permission for a user."""
        # Create file
        file = self.drive_api.create_file(name="share_test.txt", mimeType="text/plain")
        file_id = file["id"]
        
        # Share with Bob
        permission = self.drive_api.create_permission(
            fileId=file_id,
            role="reader",
            type="user",
            emailAddress=self.EMAIL_BOB
        )
        self.assertEqual(permission["role"], "reader")
        self.assertEqual(permission["type"], "user")
        self.assertIn("id", permission)

    def test_create_permission_writer(self):
        """Test creating a writer permission."""
        file = self.drive_api.create_file(name="share_test.txt", mimeType="text/plain")
        file_id = file["id"]
        
        permission = self.drive_api.create_permission(
            fileId=file_id,
            role="writer",
            type="user",
            emailAddress=self.EMAIL_BOB
        )
        self.assertEqual(permission["role"], "writer")

    def test_create_permission_invalid_role(self):
        """Test creating permission with invalid role."""
        file = self.drive_api.create_file(name="test.txt", mimeType="text/plain")
        file_id = file["id"]
        
        with self.assertRaises(Exception) as context:
            self.drive_api.create_permission(
                fileId=file_id,
                role="invalid_role",
                type="user",
                emailAddress=self.EMAIL_BOB
            )
        self.assertIn("invalid role", str(context.exception).lower())

    def test_create_permission_not_found(self):
        """Test creating permission for non-existent file."""
        with self.assertRaises(Exception) as context:
            self.drive_api.create_permission(
                fileId="nonexistent_file",
                role="reader",
                type="user",
                emailAddress=self.EMAIL_BOB
            )
        self.assertIn("not found", str(context.exception).lower())

    # --- Revision Tests ---
    
    def test_list_revisions(self):
        """Test listing file revisions."""
        # Create file
        file = self.drive_api.create_file(name="revisions_test.txt", mimeType="text/plain")
        file_id = file["id"]
        
        # Get revisions
        result = self.drive_api.list_revisions(file_id)
        self.assertIn("kind", result)
        self.assertEqual(result["kind"], "drive#revisionList")
        self.assertIn("revisions", result)
        self.assertGreater(len(result["revisions"]), 0)

    def test_list_revisions_not_found(self):
        """Test getting revisions for non-existent file."""
        with self.assertRaises(Exception) as context:
            self.drive_api.list_revisions("nonexistent_file")
        self.assertIn("not found", str(context.exception).lower())

    # --- Workflow Tests ---
    
    def test_create_list_delete_file_flow(self):
        """Test the flow of creating, listing, and deleting a file."""
        # Create file
        created = self.drive_api.create_file(name="flow_test.txt", mimeType="text/plain")
        file_id = created["id"]
        
        # List files to verify creation
        list_result = self.drive_api.list_files()
        file_ids = [f["id"] for f in list_result["files"]]
        self.assertIn(file_id, file_ids)
        
        # Delete file
        self.drive_api.delete_file(file_id)

    def test_copy_update_get_file_flow(self):
        """Test the flow of copying, updating, and getting a file."""
        # Create original
        original = self.drive_api.create_file(name="copy_test_original.txt", mimeType="text/plain")
        original_id = original["id"]
        
        # Copy file
        copied = self.drive_api.copy_file(original_id, name="copied_test_file.txt")
        copied_id = copied["id"]
        
        # Update copied file
        self.drive_api.update_file(copied_id, name="Updated Copy")
        
        # Get updated file
        retrieved = self.drive_api.get_file(copied_id)
        self.assertEqual(retrieved["name"], "Updated Copy")

    def test_multiple_user_file_isolation(self):
        """Test that files are isolated between different users."""
        # Create file as Alice
        alice_file = self.drive_api.create_file(name="alice_file.txt", mimeType="text/plain")
        alice_file_id = alice_file["id"]
        
        # Switch to Bob
        self.drive_api.authenticate(self.EMAIL_BOB)
        
        # Bob shouldn't see Alice's file without sharing
        bob_files = self.drive_api.list_files()
        bob_file_ids = [f["id"] for f in bob_files["files"]]
        self.assertNotIn(alice_file_id, bob_file_ids)

    # --- Reset Data Test ---
    
    def test_reset_data_success(self):
        """Test resetting data successfully."""
        result = self.drive_api.reset_data()
        self.assertTrue(result.get("reset_status", False))


if __name__ == "__main__":
    unittest.main()

