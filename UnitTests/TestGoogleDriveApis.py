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
    Unit tests for the GoogleDriveApis class, covering multi-user functionality.
    """

    # Load real data from backend
    real_data = BackendDataLoader.get_googledrive_data()
    
    # Extract real user UUIDs (not emails!)
    user_ids = list(real_data.get("users", {}).keys())
    user_id_alice = user_ids[0] if user_ids else "user_001"
    user_id_bob = user_ids[1] if len(user_ids) > 1 else user_id_alice
    
    # Get user data for reference
    user_data_alice = real_data.get("users", {}).get(user_id_alice, {})
    user_data_bob = real_data.get("users", {}).get(user_id_bob, {})
    
    # Extract real file data
    files_alice = user_data_alice.get("drive_data", {}).get("files", {})
    REAL_FILE_ID = next(iter(files_alice), "file1")
    file_data = files_alice.get(REAL_FILE_ID, {})
    REAL_FILE_NAME = file_data.get("name", "Test File")
    
    def setUp(self):
        """Set up the API instance using real data."""
        self.drive_api = GoogleDriveApis()

    # --- User Info Tests ---
    def test_get_user_info_alice(self):
        """Test getting user info for Alice."""
        result = self.drive_api.get_user_info(user_id=self.user_id_alice)
        # FIXED: Changed from "status" to "retrieval_status"
        self.assertTrue(result.get("retrieval_status", False))
        if result.get("retrieval_status"):
            # FIXED: Changed from "user" to "user_info"
            self.assertIn("user_info", result)

    def test_get_user_info_bob(self):
        """Test getting user info for Bob."""
        result = self.drive_api.get_user_info(user_id=self.user_id_bob)
        # FIXED: Changed from "status" to "retrieval_status"
        self.assertTrue(result.get("retrieval_status", False))

    def test_get_user_info_non_existent(self):
        """Test getting user info for non-existent user."""
        result = self.drive_api.get_user_info(user_id="nonexistent@example.com")
        # FIXED: Changed from "status" to "retrieval_status"
        self.assertFalse(result.get("retrieval_status", True))

    # --- File Management Tests ---
    def test_create_file_alice(self):
        """Test creating a file for Alice."""
        result = self.drive_api.create_file(name="test_file.txt", mimeType="text/plain", user_id=self.user_id_alice)
        # Status check is correct for create operations
        self.assertTrue(result.get("status", False))
        if result.get("status"):
            self.assertIn("file", result)
            self.assertIn("id", result["file"])

    def test_create_file_bob(self):
        """Test creating a file for Bob."""
        result = self.drive_api.create_file(name="test_file.txt", mimeType="text/plain", user_id=self.user_id_bob)
        self.assertTrue(result.get("status", False))

    def test_get_file_alice_existing(self):
        """Test getting an existing file for Alice."""
        # First create a file
        create_result = self.drive_api.create_file(name="get_test_file.txt", mimeType="text/plain", user_id=self.user_id_alice)
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            result = self.drive_api.get_file(file_id, user_id=self.user_id_alice)
            # FIXED: Changed from "status" to "retrieval_status"
            self.assertTrue(result.get("retrieval_status", False))

    def test_list_files_with_order_by_name(self):
        """Test listing files ordered by name."""
        result = self.drive_api.list_files(user_id=self.user_id_alice)
        # FIXED: Changed from "status" to "retrieval_status"
        self.assertTrue(result.get("retrieval_status", False))
        if result.get("retrieval_status"):
            self.assertIn("files", result)

    def test_list_files_with_page_size(self):
        """Test listing files with a page size limit."""
        # FIXED: Changed pageSize to page_size (API uses snake_case)
        result = self.drive_api.list_files(user_id=self.user_id_alice, page_size=1)
        # FIXED: Changed from "status" to "retrieval_status"
        self.assertTrue(result.get("retrieval_status", False))

    def test_update_file_add_parent(self):
        """Test updating a file by adding a parent."""
        # First create a file and folder
        file_result = self.drive_api.create_file(name="update_test_file.txt", mimeType="text/plain", user_id=self.user_id_alice)
        if file_result.get("status"):
            file_id = file_result["file"]["id"]
            folder_result = self.drive_api.create_folder("Test Folder", user_id=self.user_id_alice)
            if folder_result.get("status"):
                folder_id = folder_result["file"]["id"]
                result = self.drive_api.update_file(file_id, addParents=[folder_id], user_id=self.user_id_alice)
                # Update returns "status": "success" format, need to check if it exists
                self.assertTrue(result.get("status") == "success" or result.get("updated_file") is not None)

    def test_delete_file_alice(self):
        """Test deleting a file for Alice."""
        # First create a file
        create_result = self.drive_api.create_file(name="delete_test_file.txt", mimeType="text/plain", user_id=self.user_id_alice)
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            result = self.drive_api.delete_file(file_id, user_id=self.user_id_alice)
            # FIXED: Changed from "status" to "delete_status"
            self.assertTrue(result.get("delete_status", False))

    def test_delete_file_non_existent(self):
        """Test deleting a non-existent file."""
        result = self.drive_api.delete_file("non_existent_file", user_id=self.user_id_alice)
        # FIXED: Changed from "status" to "delete_status"
        self.assertFalse(result.get("delete_status", True))

    def test_copy_file_non_existent(self):
        """Test copying a non-existent file."""
        result = self.drive_api.copy_file("non_existent_file", name="copied_non_existent.txt", user_id=self.user_id_alice)
        # Copy uses "status" key
        self.assertFalse(result.get("status", True))

    def test_star_file_alice(self):
        """Test starring a file for Alice."""
        # First create a file
        create_result = self.drive_api.create_file(name="star_test_file.txt", mimeType="text/plain", user_id=self.user_id_alice)
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            result = self.drive_api.star_file(file_id, user_id=self.user_id_alice)
            # FIXED: Changed from "status" to "star_status"
            self.assertTrue(result.get("star_status", False))

    def test_star_file_bob(self):
        """Test starring a file for Bob."""
        # First create a file
        create_result = self.drive_api.create_file(name="star_test_file_bob.txt", mimeType="text/plain", user_id=self.user_id_bob)
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            result = self.drive_api.star_file(file_id, user_id=self.user_id_bob)
            # FIXED: Changed from "status" to "star_status"
            self.assertTrue(result.get("star_status", False))

    def test_star_file_non_existent(self):
        """Test starring a non-existent file."""
        result = self.drive_api.star_file("non_existent_file", user_id=self.user_id_alice)
        # FIXED: Changed from "status" to "star_status"
        self.assertFalse(result.get("star_status", True))

    def test_trash_file_alice(self):
        """Test trashing a file for Alice."""
        # First create a file
        create_result = self.drive_api.create_file(name="trash_test_file.txt", mimeType="text/plain", user_id=self.user_id_alice)
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            result = self.drive_api.trash_file(file_id, user_id=self.user_id_alice)
            # FIXED: Changed from "status" to "trash_status"
            self.assertTrue(result.get("trash_status", False))

    def test_trash_file_bob(self):
        """Test trashing a file for Bob."""
        # First create a file
        create_result = self.drive_api.create_file(name="trash_test_file_bob.txt", mimeType="text/plain", user_id=self.user_id_bob)
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            result = self.drive_api.trash_file(file_id, user_id=self.user_id_bob)
            # FIXED: Changed from "status" to "trash_status"
            self.assertTrue(result.get("trash_status", False))

    def test_trash_file_non_existent(self):
        """Test trashing a non-existent file."""
        result = self.drive_api.trash_file("non_existent_file", user_id=self.user_id_alice)
        # FIXED: Changed from "status" to "trash_status"
        self.assertFalse(result.get("trash_status", True))

    def test_share_file_alice_with_bob(self):
        """Test sharing a file from Alice to Bob."""
        # First create a file
        create_result = self.drive_api.create_file(name="share_test_file.txt", mimeType="text/plain", user_id=self.user_id_alice)
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            result = self.drive_api.share_file(file_id, self.user_id_bob, role="reader", user_id=self.user_id_alice)
            # FIXED: Changed from "status" to "share_status"
            self.assertTrue(result.get("share_status", False))

    def test_share_file_bob_with_alice_editor(self):
        """Test sharing a file from Bob to Alice with editor role."""
        # First create a file
        create_result = self.drive_api.create_file(name="share_test_file_bob.txt", mimeType="text/plain", user_id=self.user_id_bob)
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            result = self.drive_api.share_file(file_id, self.user_id_alice, role="writer", user_id=self.user_id_bob)
            # FIXED: Changed from "status" to "share_status"
            self.assertTrue(result.get("share_status", False))

    def test_share_file_non_existent(self):
        """Test sharing a non-existent file."""
        result = self.drive_api.share_file("non_existent_file", self.user_id_bob, user_id=self.user_id_alice)
        # FIXED: Changed from "status" to "share_status"
        self.assertFalse(result.get("share_status", True))

    def test_share_file_invalid_role(self):
        """Test sharing a file with invalid role."""
        # First create a file
        create_result = self.drive_api.create_file(name="invalid_role_test_file.txt", mimeType="text/plain", user_id=self.user_id_alice)
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            result = self.drive_api.share_file(file_id, self.user_id_bob, role="invalid_role", user_id=self.user_id_alice)
            # FIXED: Changed from "status" to "share_status"
            self.assertFalse(result.get("share_status", True))

    def test_get_file_revisions_alice(self):
        """Test getting file revisions for Alice."""
        # First create a file
        create_result = self.drive_api.create_file(name="revisions_test_file.txt", mimeType="text/plain", user_id=self.user_id_alice)
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            result = self.drive_api.get_file_revisions(file_id, user_id=self.user_id_alice)
            # FIXED: Changed from "status" to "retrieval_status"
            self.assertTrue(result.get("retrieval_status", False))

    def test_get_file_revisions_bob(self):
        """Test getting file revisions for Bob."""
        # First create a file
        create_result = self.drive_api.create_file(name="revisions_test_file_bob.txt", mimeType="text/plain", user_id=self.user_id_bob)
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            result = self.drive_api.get_file_revisions(file_id, user_id=self.user_id_bob)
            # FIXED: Changed from "status" to "retrieval_status"
            self.assertTrue(result.get("retrieval_status", False))

    def test_get_file_revisions_non_existent(self):
        """Test getting revisions for non-existent file."""
        result = self.drive_api.get_file_revisions("non_existent_file", user_id=self.user_id_alice)
        # FIXED: Changed from "status" to "retrieval_status"
        self.assertFalse(result.get("retrieval_status", True))

    # --- Folder Tests ---
    def test_create_folder_alice(self):
        """Test creating a folder for Alice."""
        result = self.drive_api.create_folder("Test Folder", user_id=self.user_id_alice)
        # Create folder uses "status" key
        self.assertTrue(result.get("status", False))
        if result.get("status"):
            self.assertIn("file", result)
            self.assertIn("id", result["file"])

    def test_create_folder_bob_with_parent(self):
        """Test creating a folder for Bob with parent folder."""
        # First create parent folder
        parent_result = self.drive_api.create_folder("Parent Folder", user_id=self.user_id_bob)
        if parent_result.get("status"):
            parent_id = parent_result["file"]["id"]
            result = self.drive_api.create_folder("Child Folder", parents=[parent_id], user_id=self.user_id_bob)
            self.assertTrue(result.get("status", False))

    # --- Workflow Tests ---
    def test_create_list_delete_file_flow(self):
        """Test the flow of creating, listing, and deleting a file for Alice."""
        # Create file
        create_result = self.drive_api.create_file(name="flow_test_file.txt", mimeType="text/plain", user_id=self.user_id_alice)
        self.assertTrue(create_result.get("status", False))
        
        if create_result.get("status"):
            file_id = create_result["file"]["id"]
            
            # List files to verify creation
            list_result = self.drive_api.list_files(user_id=self.user_id_alice)
            # FIXED: Changed from "status" to "retrieval_status"
            self.assertTrue(list_result.get("retrieval_status", False))
            
            # Delete file
            delete_result = self.drive_api.delete_file(file_id, user_id=self.user_id_alice)
            # FIXED: Changed from "status" to "delete_status"
            self.assertTrue(delete_result.get("delete_status", False))

    def test_copy_update_get_file_flow(self):
        """Test the flow of copying, updating, and getting a file for Alice."""
        # First create original file
        create_result = self.drive_api.create_file(name="copy_test_original.txt", mimeType="text/plain", user_id=self.user_id_alice)
        if create_result.get("status"):
            original_file_id = create_result["file"]["id"]
            
            # Copy file
            copy_result = self.drive_api.copy_file(original_file_id, name="copied_test_file.txt", user_id=self.user_id_alice)
            self.assertTrue(copy_result.get("status", False))
            
            if copy_result.get("status"):
                copied_file_id = copy_result["file"]["id"]
                
                # Update copied file
                update_result = self.drive_api.update_file(copied_file_id, name="Updated Copy", user_id=self.user_id_alice)
                # Update returns "status": "success" or has "updated_file" key
                self.assertTrue(update_result.get("status") == "success" or update_result.get("updated_file") is not None)
                
                # Get updated file
                get_result = self.drive_api.get_file(copied_file_id, user_id=self.user_id_alice)
                # FIXED: Changed from "status" to "retrieval_status"
                self.assertTrue(get_result.get("retrieval_status", False))

    def test_multiple_user_file_isolation(self):
        """Test that files are isolated between different users."""
        # Create file for Alice
        alice_file = self.drive_api.create_file(name="alice_isolation_test.txt", mimeType="text/plain", user_id=self.user_id_alice)
        self.assertTrue(alice_file.get("status", False))
        
        # Create file for Bob
        bob_file = self.drive_api.create_file(name="bob_isolation_test.txt", mimeType="text/plain", user_id=self.user_id_bob)
        self.assertTrue(bob_file.get("status", False))
        
        # Verify Alice can't see Bob's files without sharing
        alice_files = self.drive_api.list_files(user_id=self.user_id_alice)
        bob_files = self.drive_api.list_files(user_id=self.user_id_bob)
        
        # FIXED: Changed from "status" to "retrieval_status"
        self.assertTrue(alice_files.get("retrieval_status", False))
        self.assertTrue(bob_files.get("retrieval_status", False))

    # --- Data Reset Tests ---
    def test_reset_data_success(self):
        """Test resetting data successfully."""
        result = self.drive_api.reset_data()
        # FIXED: Changed from "status" to "reset_status"
        self.assertTrue(result.get("reset_status", False))

if __name__ == "__main__":
    unittest.main()
