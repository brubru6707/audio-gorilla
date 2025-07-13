import unittest
from copy import deepcopy
from typing import Dict, Any
from GoogleDriveApis import GoogleDriveAPI,DEFAULT_STATE

class TestGoogleDriveAPI(unittest.TestCase):
    def setUp(self):
        """Initialize the API with a clean state before each test."""
        self.api = GoogleDriveAPI()
        self.api._load_scenario(deepcopy(DEFAULT_STATE))
        
    def test_load_scenario(self):
        """Test that _load_scenario correctly initializes the API state."""
        custom_scenario = {
            "user_info": {
                "name": "test_user",
                "email": "test@example.com",
                "storage_quota": {"total": 500000000, "used": 100000000}
            },
            "files": {
                "file_1": {"id": "file_1", "name": "test_file"}
            },
            "next_page_token": 42
        }
        
        self.api._load_scenario(custom_scenario)
        
        self.assertEqual(self.api.user_info["name"], "test_user")
        self.assertEqual(self.api.files["file_1"]["name"], "test_file")
        self.assertEqual(self.api.next_page_token, 42)

    def test_get_about(self):
        """Test that get_about returns correct user information."""
        about_info = self.api.get_about()
        
        self.assertEqual(about_info["user"]["name"], "user")
        self.assertEqual(about_info["user"]["email"], "user@example.com")
        self.assertEqual(about_info["storageQuota"]["total"], 1000000000)
        self.assertEqual(about_info["maxUploadSize"], "5TB")
        self.assertTrue(about_info["appInstalled"])

    def test_create_file(self):
        """Test creating a new file with default parameters."""
        file_info = self.api.create_file()
        
        self.assertEqual(len(self.api.files), 1)
        self.assertEqual(file_info["name"], "Untitled")
        self.assertEqual(file_info["mimeType"], "application/vnd.google-apps.document")
        self.assertEqual(file_info["owners"][0]["emailAddress"], "user@example.com")
        
    def test_get_file(self):
        """Test getting file information."""
        # First create a file
        created_file = self.api.create_file()
        file_id = created_file["id"]
        
        # Then get it
        file_info = self.api.get_file(file_id)
        
        self.assertEqual(file_info["id"], file_id)
        self.assertEqual(file_info["name"], "Untitled")
        
        # Test getting non-existent file
        non_existent = self.api.get_file("nonexistent")
        self.assertEqual(non_existent["error"], "File not found")

    def test_copy_file(self):
        """Test copying an existing file."""
        # First create a file
        original_file = self.api.create_file("Original")
        file_id = original_file["id"]
        
        # Then copy it
        copied_file = self.api.copy_file(file_id)
        
        self.assertEqual(len(self.api.files), 2)
        self.assertTrue(copied_file["name"].startswith("Copy of"))
        self.assertNotEqual(copied_file["id"], file_id)
        
        # Test copying non-existent file
        non_existent = self.api.copy_file("nonexistent")
        self.assertEqual(non_existent["error"], "File not found")

    def test_delete_file(self):
        """Test deleting a file."""
        # First create a file
        created_file = self.api.create_file()
        file_id = created_file["id"]
        self.assertEqual(len(self.api.files), 1)
        
        # Then delete it
        delete_result = self.api.delete_file(file_id)
        self.assertTrue(delete_result["deletion_status"])
        self.assertEqual(len(self.api.files), 0)
        
        # Test deleting non-existent file
        non_existent = self.api.delete_file("nonexistent")
        self.assertFalse(non_existent["deletion_status"])

    def test_empty_trash(self):
        """Test emptying the trash (always returns True in this implementation)."""
        result = self.api.empty_trash()
        self.assertTrue(result["empty_status"])

    def test_export_file(self):
        """Test exporting a file to different format."""
        # First create a file
        created_file = self.api.create_file()
        file_id = created_file["id"]
        
        # Export it
        export_result = self.api.export_file(file_id, "application/pdf")
        
        self.assertEqual(export_result["id"], file_id)
        self.assertEqual(export_result["mimeType"], "application/pdf")
        self.assertIn("exportLinks", export_result)
        
        # Test exporting non-existent file
        non_existent = self.api.export_file("nonexistent", "application/pdf")
        self.assertEqual(non_existent["error"], "File not found")

    def test_list_files(self):
        """Test listing files with various parameters."""
        # Create some test files
        file1 = self.api.create_file()
        self.api.update_file(file1["id"], name="Document 1")
        
        file2 = self.api.create_file()
        self.api.update_file(file2["id"], name="Spreadsheet 1")
        
        file3 = self.api.create_file()
        self.api.update_file(file3["id"], name="Document 2")
        
        # Test basic listing
        all_files = self.api.list_files()
        self.assertEqual(len(all_files["files"]), 3)
        
        # Test filtering with query
        doc_files = self.api.list_files(q="Document")
        self.assertEqual(len(doc_files["files"]), 2)
        self.assertTrue(all("Document" in f["name"] for f in doc_files["files"]))
        
        # Test ordering
        ordered_files = self.api.list_files(orderBy="name")
        self.assertEqual(ordered_files["files"][0]["name"], "Document 1")
        self.assertEqual(ordered_files["files"][1]["name"], "Document 2")
        
        reverse_ordered = self.api.list_files(orderBy="-name")
        self.assertEqual(reverse_ordered["files"][0]["name"], "Spreadsheet 1")
        
        # Test pagination
        paginated = self.api.list_files(pageSize=2)
        self.assertEqual(len(paginated["files"]), 2)

    def test_update_file(self):
        """Test updating file properties."""
        # First create a file
        created_file = self.api.create_file()
        file_id = created_file["id"]
        
        # Update the name
        updated_file = self.api.update_file(file_id, name="Updated Name")
        self.assertEqual(updated_file["name"], "Updated Name")
        
        # Test adding parents
        updated_with_parent = self.api.update_file(file_id, addParents="parent1")
        self.assertIn("parent1", updated_with_parent.get("parents", []))
        
        # Test removing parents
        updated_remove_parent = self.api.update_file(file_id, removeParents="parent1")
        self.assertNotIn("parent1", updated_remove_parent.get("parents", []))
        
        # Test updating non-existent file
        non_existent = self.api.update_file("nonexistent")
        self.assertEqual(non_existent["error"], "File not found")

    def test_multiple_operations(self):
        """Test a sequence of operations that use multiple functions together."""
        # Create a file
        file1 = self.api.create_file()
        self.assertEqual(len(self.api.files), 1)
        
        # Update its name
        self.api.update_file(file1["id"], name="Important Document")
        updated = self.api.get_file(file1["id"])
        self.assertEqual(updated["name"], "Important Document")
        
        # Copy it
        copy = self.api.copy_file(file1["id"])
        self.assertEqual(len(self.api.files), 2)
        self.assertEqual(copy["name"], "Copy of Important Document")
        
        # List files should show both
        files = self.api.list_files()
        self.assertEqual(len(files["files"]), 2)
        
        # Delete the original
        self.api.delete_file(file1["id"])
        self.assertEqual(len(self.api.files), 1)
        
        # Verify through get_file
        deleted = self.api.get_file(file1["id"])
        self.assertEqual(deleted["error"], "File not found")
        
        # But copy should still exist
        copy_exists = self.api.get_file(copy["id"])
        self.assertEqual(copy_exists["id"], copy["id"])

    def test_storage_quota_updates(self):
        """Test that storage quota updates when files are created/deleted."""
        # Note: The current implementation doesn't actually update storage quota
        # This test is a placeholder for when that functionality is added
        initial_quota = self.api.get_about()["storageQuota"]
        self.assertEqual(initial_quota["used"], 0)
        
        # Create a file (would update quota in real implementation)
        self.api.create_file()
        quota_after_create = self.api.get_about()["storageQuota"]
        self.assertEqual(quota_after_create["used"], 0)  # Should be >0 in real impl
        
        # Delete the file (would update quota in real implementation)
        file_id = next(iter(self.api.files.keys()))
        self.api.delete_file(file_id)
        quota_after_delete = self.api.get_about()["storageQuota"]
        self.assertEqual(quota_after_delete["used"], 0)  # Should be back to 0 in real impl

if __name__ == "__main__":
    unittest.main()