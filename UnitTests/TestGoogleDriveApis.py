from audio_gorilla.GoogleDriveApis import GoogleDriveApis, DEFAULT_STATE
import unittest
from copy import deepcopy

class TestGoogleDriveApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh GoogleDriveAPI instance for each test."""
        self.drive_api = GoogleDriveApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.drive_api._load_scenario(deepcopy(DEFAULT_STATE))

    # --- Unit Tests for Core Functions (most important for audio calling) ---

    def test_get_about_success(self):
        """Test getting information about the user's Google Drive."""
        result = self.drive_api.get_about()
        self.assertIsNotNone(result)
        self.assertIn("user", result)
        self.assertIn("storageQuota", result)
        self.assertEqual(result["user"]["email"], "user@example.com")
        self.assertEqual(result["storageQuota"]["total"], 1000000000)

    def test_list_files_success(self):
        """Test listing all files."""
        result = self.drive_api.list_files()
        self.assertIsNotNone(result)
        self.assertIn("files", result)
        self.assertEqual(len(result["files"]), 2)
        self.assertEqual(result["files"][0]["name"], "MyDocument.txt")

    def test_list_files_with_query(self):
        """Test listing files with a search query."""
        result = self.drive_api.list_files(q="spreadsheet")
        self.assertIsNotNone(result)
        self.assertIn("files", result)
        self.assertEqual(len(result["files"]), 1)
        self.assertEqual(result["files"][0]["name"], "MySpreadsheet.xlsx")

    def test_list_files_with_order_by_name(self):
        """Test listing files ordered by name."""
        result = self.drive_api.list_files(orderBy="name")
        self.assertIsNotNone(result)
        self.assertIn("files", result)
        # Files should be sorted alphabetically by name
        self.assertEqual(result["files"][0]["name"], "MyDocument.txt")
        self.assertEqual(result["files"][1]["name"], "MySpreadsheet.xlsx")

    def test_get_file_success(self):
        """Test getting information about a specific file."""
        file_id = "file_1"
        result = self.drive_api.get_file(file_id)
        self.assertIsNotNone(result)
        self.assertIn("id", result)
        self.assertEqual(result["id"], file_id)
        self.assertEqual(result["name"], "MyDocument.txt")

    def test_get_file_not_found(self):
        """Test getting information for a non-existent file."""
        file_id = "non_existent_file"
        result = self.drive_api.get_file(file_id)
        self.assertIsNotNone(result)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "File not found")

    def test_create_file_success(self):
        """Test creating a new file."""
        initial_file_count = len(self.drive_api.files)
        result = self.drive_api.create_file()
        self.assertIsNotNone(result)
        self.assertIn("id", result)
        self.assertEqual(len(self.drive_api.files), initial_file_count + 1)
        self.assertEqual(result["name"], "Untitled")
        self.assertEqual(result["mimeType"], "application/vnd.google-apps.document")

    def test_delete_file_success(self):
        """Test deleting an existing file."""
        file_id_to_delete = "file_1"
        initial_file_count = len(self.drive_api.files)
        result = self.drive_api.delete_file(file_id_to_delete)
        self.assertTrue(result["deletion_status"])
        self.assertEqual(len(self.drive_api.files), initial_file_count - 1)
        self.assertNotIn(file_id_to_delete, self.drive_api.files)

    def test_delete_file_not_found(self):
        """Test deleting a non-existent file."""
        file_id_to_delete = "non_existent_file"
        initial_file_count = len(self.drive_api.files)
        result = self.drive_api.delete_file(file_id_to_delete)
        self.assertFalse(result["deletion_status"])
        self.assertEqual(len(self.drive_api.files), initial_file_count) # Count should remain unchanged

    def test_copy_file_success(self):
        """Test copying an existing file."""
        file_id_to_copy = "file_1"
        initial_file_count = len(self.drive_api.files)
        result = self.drive_api.copy_file(file_id_to_copy)
        self.assertIsNotNone(result)
        self.assertIn("id", result)
        self.assertEqual(len(self.drive_api.files), initial_file_count + 1)
        self.assertNotEqual(result["id"], file_id_to_copy)
        self.assertEqual(result["name"], "Copy of MyDocument.txt")

    def test_copy_file_not_found(self):
        """Test copying a non-existent file."""
        file_id_to_copy = "non_existent_file"
        initial_file_count = len(self.drive_api.files)
        result = self.drive_api.copy_file(file_id_to_copy)
        self.assertIsNotNone(result)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "File not found")
        self.assertEqual(len(self.drive_api.files), initial_file_count) # Count should remain unchanged

    def test_update_file_add_parent(self):
        """Test updating a file by adding a parent."""
        file_id = "file_1"
        new_parent = "folder_abc"
        result = self.drive_api.update_file(file_id, addParents=new_parent)
        self.assertIsNotNone(result)
        self.assertIn(new_parent, result["parents"])
        self.assertGreater(int(result["modifiedTime"]), int(DEFAULT_STATE["files"]["file_1"]["modifiedTime"]))

    def test_update_file_remove_parent(self):
        """Test updating a file by removing a parent."""
        file_id = "file_1"
        parent_to_remove = "root" # 'root' is a parent in DEFAULT_STATE
        result = self.drive_api.update_file(file_id, removeParents=parent_to_remove)
        self.assertIsNotNone(result)
        self.assertNotIn(parent_to_remove, result["parents"])
        self.assertGreater(int(result["modifiedTime"]), int(DEFAULT_STATE["files"]["file_1"]["modifiedTime"]))

    # --- Combined Functionality Tests ---

    def test_create_list_and_delete_file(self):
        """
        Scenario: Create a file, list files to confirm its presence, then delete it.
        Functions: create_file, list_files, delete_file
        """
        # 1. Create a file
        create_result = self.drive_api.create_file()
        self.assertIsNotNone(create_result)
        new_file_id = create_result["id"]
        initial_file_count = len(self.drive_api.files)
        self.assertEqual(len(self.drive_api.files), initial_file_count) # Should be 3 now

        # 2. List files and confirm the new file exists
        list_result_before_delete = self.drive_api.list_files()
        self.assertIn(new_file_id, [f["id"] for f in list_result_before_delete["files"]])

        # 3. Delete the newly created file
        delete_result = self.drive_api.delete_file(new_file_id)
        self.assertTrue(delete_result["deletion_status"])
        self.assertEqual(len(self.drive_api.files), initial_file_count - 1) # Should be back to 2

        # 4. List files again to confirm deletion
        list_result_after_delete = self.drive_api.list_files()
        self.assertNotIn(new_file_id, [f["id"] for f in list_result_after_delete["files"]])

    def test_copy_and_get_file_details(self):
        """
        Scenario: Copy an existing file, then retrieve details of the copied file.
        Functions: copy_file, get_file
        """
        original_file_id = "file_1"
        
        # 1. Copy the file
        copy_result = self.drive_api.copy_file(original_file_id)
        self.assertIsNotNone(copy_result)
        copied_file_id = copy_result["id"]
        self.assertNotEqual(original_file_id, copied_file_id)
        self.assertEqual(copy_result["name"], "Copy of MyDocument.txt")

        # 2. Get details of the copied file
        get_copied_file_result = self.drive_api.get_file(copied_file_id)
        self.assertIsNotNone(get_copied_file_result)
        self.assertEqual(get_copied_file_result["id"], copied_file_id)
        self.assertEqual(get_copied_file_result["name"], "Copy of MyDocument.txt")
        self.assertEqual(get_copied_file_result["mimeType"], "text/plain") # Should retain original mimeType

    def test_update_file_and_verify_changes(self):
        """
        Scenario: Update a file's parent, then get the file to verify the update.
        Functions: update_file, get_file
        """
        file_id = "file_2"
        initial_parents = self.drive_api.files[file_id]["parents"]
        new_parent_folder = "my_new_folder_id"

        # 1. Update the file by adding a new parent
        update_result = self.drive_api.update_file(file_id, addParents=new_parent_folder)
        self.assertIsNotNone(update_result)
        self.assertIn(new_parent_folder, update_result["parents"])
        self.assertGreater(int(update_result["modifiedTime"]), int(DEFAULT_STATE["files"]["file_2"]["modifiedTime"]))

        # 2. Get the file to verify the changes persisted
        verified_file = self.drive_api.get_file(file_id)
        self.assertIsNotNone(verified_file)
        self.assertIn(new_parent_folder, verified_file["parents"])
        self.assertGreater(int(verified_file["modifiedTime"]), int(DEFAULT_STATE["files"]["file_2"]["modifiedTime"]))
        # Ensure original parents are still there unless explicitly removed
        for parent in initial_parents:
            self.assertIn(parent, verified_file["parents"])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)