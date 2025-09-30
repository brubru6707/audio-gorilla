import unittest
from copy import deepcopy
from GoogleDriveApis import GoogleDriveApis, DEFAULT_STATE

class TestGoogleDriveApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh GoogleDriveApis instance for each test."""
        self.drive_api = GoogleDriveApis()
        # Ensure a deep copy of the default state for isolation between tests
        self.drive_api.state = deepcopy(DEFAULT_STATE)
        self.user_id_alice = "user1@example.com"
        self.user_id_bob = "user2@example.com"

    # --- User Info Tests ---
    def test_get_user_info_alice(self):
        """Test getting user info for Alice."""
        user_info = self.drive_api.get_user_info(user_id=self.user_id_alice)
        self.assertTrue(user_info["success"])
        self.assertIn("user_info", user_info)
        self.assertEqual(user_info["user_info"]["email"], self.user_id_alice)
        self.assertEqual(user_info["user_info"]["displayName"], "Alice Smith")

    def test_get_user_info_bob(self):
        """Test getting user info for Bob."""
        user_info = self.drive_api.get_user_info(user_id=self.user_id_bob)
        self.assertTrue(user_info["success"])
        self.assertIn("user_info", user_info)
        self.assertEqual(user_info["user_info"]["email"], self.user_id_bob)
        self.assertEqual(user_info["user_info"]["displayName"], "Bob Johnson")

    def test_get_user_info_non_existent(self):
        """Test getting user info for non-existent user."""
        user_info = self.drive_api.get_user_info(user_id="nonexistent@example.com")
        self.assertFalse(user_info["success"])
        self.assertNotIn("user_info", user_info)

    def test_get_about_alice(self):
        """Test getting 'about' information for Alice."""
        about_info = self.drive_api.get_about(user_id=self.user_id_alice)
        self.assertIsNotNone(about_info)
        self.assertIn("user", about_info)
        self.assertEqual(about_info["user"]["email"], self.user_id_alice)
        self.assertIn("storageQuota", about_info)
        self.assertEqual(about_info["storageQuota"]["total"], 1000000000)

    def test_get_about_bob(self):
        """Test getting 'about' information for Bob."""
        about_info = self.drive_api.get_about(user_id=self.user_id_bob)
        self.assertIsNotNone(about_info)
        self.assertIn("user", about_info)
        self.assertEqual(about_info["user"]["email"], self.user_id_bob)
        self.assertIn("storageQuota", about_info)
        self.assertEqual(about_info["storageQuota"]["total"], 500000000)

    def test_get_about_non_existent_user(self):
        """Test getting 'about' information for a non-existent user."""
        about_info = self.drive_api.get_about(user_id="nonexistent@example.com")
        self.assertIn("error", about_info)
        self.assertEqual(about_info["error"], "User not found")

    def test_create_file_alice(self):
        """Test creating a file for Alice."""
        initial_file_count = len(self.drive_api._get_user_files(self.user_id_alice))
        new_file = self.drive_api.create_file(user_id=self.user_id_alice)
        self.assertIsNotNone(new_file)
        self.assertIn("id", new_file)
        self.assertEqual(new_file["name"], "Untitled")
        self.assertEqual(new_file["owners"][0]["emailAddress"], self.user_id_alice)
        self.assertEqual(len(self.drive_api._get_user_files(self.user_id_alice)), initial_file_count + 1)

    def test_create_file_bob(self):
        """Test creating a file for Bob."""
        initial_file_count = len(self.drive_api._get_user_files(self.user_id_bob))
        new_file = self.drive_api.create_file(user_id=self.user_id_bob)
        self.assertIsNotNone(new_file)
        self.assertIn("id", new_file)
        self.assertEqual(new_file["name"], "Untitled")
        self.assertEqual(new_file["owners"][0]["emailAddress"], self.user_id_bob)
        self.assertEqual(len(self.drive_api._get_user_files(self.user_id_bob)), initial_file_count + 1)

    def test_get_file_alice_existing(self):
        """Test getting an existing file for Alice."""
        file_info = self.drive_api.get_file("file_1_alice", user_id=self.user_id_alice)
        self.assertIsNotNone(file_info)
        self.assertEqual(file_info["id"], "file_1_alice")
        self.assertEqual(file_info["name"], "MyDocument_Alice.txt")

    def test_get_file_bob_existing(self):
        """Test getting an existing file for Bob."""
        file_info = self.drive_api.get_file("file_1_bob", user_id=self.user_id_bob)
        self.assertIsNotNone(file_info)
        self.assertEqual(file_info["id"], "file_1_bob")
        self.assertEqual(file_info["name"], "Presentation_Bob.pptx")

    def test_get_file_non_existent(self):
        """Test getting a non-existent file."""
        file_info = self.drive_api.get_file("non_existent_file", user_id=self.user_id_alice)
        self.assertIn("error", file_info)
        self.assertEqual(file_info["error"], "File not found")

    def test_list_files_alice_no_filters(self):
        """Test listing all files for Alice without filters."""
        files_list = self.drive_api.list_files(user_id=self.user_id_alice)
        self.assertIsNotNone(files_list)
        self.assertIn("files", files_list)
        self.assertEqual(len(files_list["files"]), 2) # Alice has 2 default files

    def test_list_files_bob_no_filters(self):
        """Test listing all files for Bob without filters."""
        files_list = self.drive_api.list_files(user_id=self.user_id_bob)
        self.assertIsNotNone(files_list)
        self.assertIn("files", files_list)
        self.assertEqual(len(files_list["files"]), 1) # Bob has 1 default file

    def test_list_files_with_query(self):
        """Test listing files with a query filter."""
        # Add a new file for Alice to test query
        self.drive_api.create_file(user_id=self.user_id_alice)
        self.drive_api._get_user_files(self.user_id_alice)["file_3_alice"] = {
            "id": "file_3_alice",
            "name": "Important_Report.pdf",
            "mimeType": "application/pdf",
            "createdTime": "1679145600",
            "modifiedTime": "1679145600",
            "owners": [{"displayName": "Alice Smith", "emailAddress": "user1@example.com"}],
            "parents": ["root"]
        }

        files_list = self.drive_api.list_files(user_id=self.user_id_alice, q="report")
        self.assertIsNotNone(files_list)
        self.assertIn("files", files_list)
        self.assertEqual(len(files_list["files"]), 1)
        self.assertEqual(files_list["files"][0]["name"], "Important_Report.pdf")

    def test_list_files_with_order_by_name(self):
        """Test listing files ordered by name."""
        files_list = self.drive_api.list_files(user_id=self.user_id_alice, orderBy="name")
        self.assertIsNotNone(files_list)
        self.assertIn("files", files_list)
        self.assertEqual(files_list["files"][0]["name"], "MyDocument_Alice.txt")
        self.assertEqual(files_list["files"][1]["name"], "MySpreadsheet_Alice.xlsx")

    def test_list_files_with_order_by_modified_time_desc(self):
        """Test listing files ordered by modifiedTime descending."""
        # Modify file_1_alice to be more recent
        self.drive_api.update_file("file_1_alice", user_id=self.user_id_alice)
        files_list = self.drive_api.list_files(user_id=self.user_id_alice, orderBy="-modifiedTime")
        self.assertIsNotNone(files_list)
        self.assertIn("files", files_list)
        self.assertEqual(files_list["files"][0]["id"], "file_1_alice") # Should be first due to recent modification

    def test_list_files_with_page_size(self):
        """Test listing files with a page size limit."""
        files_list = self.drive_api.list_files(user_id=self.user_id_alice, pageSize=1)
        self.assertIsNotNone(files_list)
        self.assertIn("files", files_list)
        self.assertEqual(len(files_list["files"]), 1)

    def test_update_file_add_parent(self):
        """Test updating a file by adding a parent."""
        updated_file = self.drive_api.update_file("file_1_alice", addParents="folder_abc", user_id=self.user_id_alice)
        self.assertIsNotNone(updated_file)
        self.assertIn("folder_abc", updated_file["parents"])
        # Verify in actual state
        self.assertIn("folder_abc", self.drive_api._get_user_files(self.user_id_alice)["file_1_alice"]["parents"])

    def test_update_file_remove_parent(self):
        """Test updating a file by removing a parent."""
        # First, add a parent to ensure it exists for removal
        self.drive_api.update_file("file_1_alice", addParents="folder_to_remove", user_id=self.user_id_alice)
        updated_file = self.drive_api.update_file("file_1_alice", removeParents="folder_to_remove", user_id=self.user_id_alice)
        self.assertIsNotNone(updated_file)
        self.assertNotIn("folder_to_remove", updated_file["parents"])
        # Verify in actual state
        self.assertNotIn("folder_to_remove", self.drive_api._get_user_files(self.user_id_alice)["file_1_alice"]["parents"])

    def test_delete_file_alice(self):
        """Test deleting a file for Alice."""
        initial_file_count = len(self.drive_api._get_user_files(self.user_id_alice))
        deletion_status = self.drive_api.delete_file("file_1_alice", user_id=self.user_id_alice)
        self.assertTrue(deletion_status["deletion_status"])
        self.assertEqual(len(self.drive_api._get_user_files(self.user_id_alice)), initial_file_count - 1)
        self.assertNotIn("file_1_alice", self.drive_api._get_user_files(self.user_id_alice))

    def test_delete_file_non_existent(self):
        """Test deleting a non-existent file."""
        deletion_status = self.drive_api.delete_file("non_existent_file", user_id=self.user_id_alice)
        self.assertFalse(deletion_status["deletion_status"])
        """Test copying a file for Alice."""
        initial_file_count = len(self.drive_api._get_user_files(self.user_id_alice))
        copied_file = self.drive_api.copy_file("file_1_alice", user_id=self.user_id_alice)
        self.assertIsNotNone(copied_file)
        self.assertNotEqual(copied_file["id"], "file_1_alice")
        self.assertTrue(copied_file["name"].startswith("Copy of MyDocument_Alice.txt"))
        self.assertEqual(len(self.drive_api._get_user_files(self.user_id_alice)), initial_file_count + 1)
        self.assertIn(copied_file["id"], self.drive_api._get_user_files(self.user_id_alice))

    def test_copy_file_non_existent(self):
        """Test copying a non-existent file."""
        copied_file = self.drive_api.copy_file("non_existent_file", user_id=self.user_id_alice)
        self.assertIn("error", copied_file)
        self.assertEqual(copied_file["error"], "File not found")

    # --- Star File Tests ---
    def test_star_file_alice(self):
        """Test starring a file for Alice."""
        result = self.drive_api.star_file("file_1_alice", user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        self.assertIn("starred successfully", result["message"])
        
        # Verify the file is starred
        file_info = self.drive_api.get_file("file_1_alice", user_id=self.user_id_alice)
        self.assertTrue(file_info["starred"])

    def test_star_file_bob(self):
        """Test starring a file for Bob."""
        result = self.drive_api.star_file("file_1_bob", user_id=self.user_id_bob)
        self.assertTrue(result["success"])
        self.assertIn("starred successfully", result["message"])
        
        # Verify the file is starred
        file_info = self.drive_api.get_file("file_1_bob", user_id=self.user_id_bob)
        self.assertTrue(file_info["starred"])

    def test_star_file_non_existent(self):
        """Test starring a non-existent file."""
        result = self.drive_api.star_file("non_existent_file", user_id=self.user_id_alice)
        self.assertFalse(result["success"])
        self.assertIn("File not found", result["message"])

    def test_star_file_non_existent_user(self):
        """Test starring a file for non-existent user."""
        result = self.drive_api.star_file("file_1_alice", user_id="nonexistent@example.com")
        self.assertFalse(result["success"])
        self.assertIn("User not found", result["message"])

    # --- Trash File Tests ---
    def test_trash_file_alice(self):
        """Test trashing a file for Alice."""
        result = self.drive_api.trash_file("file_1_alice", user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        self.assertIn("trashed successfully", result["message"])
        
        # Verify the file is trashed
        file_info = self.drive_api.get_file("file_1_alice", user_id=self.user_id_alice)
        self.assertTrue(file_info["trashed"])

    def test_trash_file_bob(self):
        """Test trashing a file for Bob."""
        result = self.drive_api.trash_file("file_1_bob", user_id=self.user_id_bob)
        self.assertTrue(result["success"])
        self.assertIn("trashed successfully", result["message"])
        
        # Verify the file is trashed
        file_info = self.drive_api.get_file("file_1_bob", user_id=self.user_id_bob)
        self.assertTrue(file_info["trashed"])

    def test_trash_file_non_existent(self):
        """Test trashing a non-existent file."""
        result = self.drive_api.trash_file("non_existent_file", user_id=self.user_id_alice)
        self.assertFalse(result["success"])
        self.assertIn("File not found", result["message"])

    def test_trash_file_non_existent_user(self):
        """Test trashing a file for non-existent user."""
        result = self.drive_api.trash_file("file_1_alice", user_id="nonexistent@example.com")
        self.assertFalse(result["success"])
        self.assertIn("User not found", result["message"])

    # --- Share File Tests ---
    def test_share_file_alice_with_bob(self):
        """Test sharing a file from Alice to Bob."""
        result = self.drive_api.share_file("file_1_alice", self.user_id_bob, role="reader", user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        self.assertIn("shared successfully", result["message"])
        
        # Verify sharing in file permissions
        file_info = self.drive_api.get_file("file_1_alice", user_id=self.user_id_alice)
        self.assertIn("permissions", file_info)

    def test_share_file_bob_with_alice_editor(self):
        """Test sharing a file from Bob to Alice with editor role."""
        result = self.drive_api.share_file("file_1_bob", self.user_id_alice, role="editor", user_id=self.user_id_bob)
        self.assertTrue(result["success"])
        self.assertIn("shared successfully", result["message"])
        
        # Verify sharing in file permissions
        file_info = self.drive_api.get_file("file_1_bob", user_id=self.user_id_bob)
        self.assertIn("permissions", file_info)

    def test_share_file_non_existent(self):
        """Test sharing a non-existent file."""
        result = self.drive_api.share_file("non_existent_file", self.user_id_bob, user_id=self.user_id_alice)
        self.assertFalse(result["success"])
        self.assertIn("File not found", result["message"])

    def test_share_file_non_existent_user(self):
        """Test sharing a file for non-existent user."""
        result = self.drive_api.share_file("file_1_alice", self.user_id_bob, user_id="nonexistent@example.com")
        self.assertFalse(result["success"])
        self.assertIn("User not found", result["message"])

    def test_share_file_invalid_role(self):
        """Test sharing a file with invalid role."""
        result = self.drive_api.share_file("file_1_alice", self.user_id_bob, role="invalid_role", user_id=self.user_id_alice)
        self.assertTrue(result["success"])  # Should still succeed with default role

    # --- Get File Revisions Tests ---
    def test_get_file_revisions_alice(self):
        """Test getting file revisions for Alice."""
        result = self.drive_api.get_file_revisions("file_1_alice", user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        self.assertIn("revisions", result)
        self.assertIsInstance(result["revisions"], list)
        self.assertGreater(len(result["revisions"]), 0)

    def test_get_file_revisions_bob(self):
        """Test getting file revisions for Bob."""
        result = self.drive_api.get_file_revisions("file_1_bob", user_id=self.user_id_bob)
        self.assertTrue(result["success"])
        self.assertIn("revisions", result)
        self.assertIsInstance(result["revisions"], list)
        self.assertGreater(len(result["revisions"]), 0)

    def test_get_file_revisions_non_existent(self):
        """Test getting revisions for non-existent file."""
        result = self.drive_api.get_file_revisions("non_existent_file", user_id=self.user_id_alice)
        self.assertFalse(result["success"])
        self.assertIn("File not found", result["message"])

    def test_get_file_revisions_non_existent_user(self):
        """Test getting file revisions for non-existent user."""
        result = self.drive_api.get_file_revisions("file_1_alice", user_id="nonexistent@example.com")
        self.assertFalse(result["success"])
        self.assertIn("User not found", result["message"])

    # --- Create Folder Tests ---
    def test_create_folder_alice(self):
        """Test creating a folder for Alice."""
        initial_file_count = len(self.drive_api._get_user_files(self.user_id_alice))
        result = self.drive_api.create_folder("New Project Folder", user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        self.assertIn("folder", result)
        self.assertEqual(result["folder"]["name"], "New Project Folder")
        self.assertEqual(result["folder"]["mimeType"], "application/vnd.google-apps.folder")
        self.assertEqual(len(self.drive_api._get_user_files(self.user_id_alice)), initial_file_count + 1)

    def test_create_folder_bob_with_parent(self):
        """Test creating a folder for Bob with parent folder."""
        initial_file_count = len(self.drive_api._get_user_files(self.user_id_bob))
        result = self.drive_api.create_folder("Subfolder", parents=["parent_folder_id"], user_id=self.user_id_bob)
        self.assertTrue(result["success"])
        self.assertIn("folder", result)
        self.assertEqual(result["folder"]["name"], "Subfolder")
        self.assertIn("parent_folder_id", result["folder"]["parents"])
        self.assertEqual(len(self.drive_api._get_user_files(self.user_id_bob)), initial_file_count + 1)

    def test_create_folder_non_existent_user(self):
        """Test creating a folder for non-existent user."""
        result = self.drive_api.create_folder("Should Fail", user_id="nonexistent@example.com")
        self.assertFalse(result["success"])
        self.assertIn("User not found", result["message"])

    # Combined Functionality Tests

    def test_create_list_delete_file_flow(self):
        """Test the flow of creating, listing, and deleting a file for Alice."""
        initial_file_count = len(self.drive_api._get_user_files(self.user_id_alice))

        # 1. Create a file
        created_file = self.drive_api.create_file(user_id=self.user_id_alice)
        self.assertIsNotNone(created_file)
        self.assertEqual(len(self.drive_api._get_user_files(self.user_id_alice)), initial_file_count + 1)

        # 2. List files and find the created file
        listed_files = self.drive_api.list_files(user_id=self.user_id_alice, q=created_file["name"])
        self.assertIsNotNone(listed_files)
        self.assertIn("files", listed_files)
        self.assertEqual(len(listed_files["files"]), 1)
        self.assertEqual(listed_files["files"][0]["id"], created_file["id"])

        # 3. Delete the file
        deletion_status = self.drive_api.delete_file(created_file["id"], user_id=self.user_id_alice)
        self.assertTrue(deletion_status["deletion_status"])
        self.assertEqual(len(self.drive_api._get_user_files(self.user_id_alice)), initial_file_count)

        # 4. Verify the file is no longer found
        verified_deleted = self.drive_api.get_file(created_file["id"], user_id=self.user_id_alice)
        self.assertIn("error", verified_deleted)
        self.assertEqual(verified_deleted["error"], "File not found")

    def test_copy_update_get_file_flow(self):
        """Test the flow of copying, updating, and getting a file for Alice."""
        original_file_id = "file_1_alice"

        # 1. Copy the original file
        copied_file = self.drive_api.copy_file(original_file_id, user_id=self.user_id_alice)
        self.assertIsNotNone(copied_file)
        self.assertNotEqual(copied_file["id"], original_file_id)
        copied_file_id = copied_file["id"]

        # 2. Update the copied file (e.g., add a parent)
        updated_file = self.drive_api.update_file(copied_file_id, addParents="new_project_folder", user_id=self.user_id_alice)
        self.assertIsNotNone(updated_file)
        self.assertIn("new_project_folder", updated_file["parents"])

        # 3. Get the updated file and verify changes
        retrieved_file = self.drive_api.get_file(copied_file_id, user_id=self.user_id_alice)
        self.assertIsNotNone(retrieved_file)
        self.assertEqual(retrieved_file["id"], copied_file_id)
        self.assertIn("new_project_folder", retrieved_file["parents"])

    def test_multiple_user_file_isolation(self):
        """Test that files are isolated between different users."""
        # Create a file for Alice
        alice_file = self.drive_api.create_file(user_id=self.user_id_alice)
        self.assertIsNotNone(alice_file)

        # Try to retrieve Alice's file using Bob's user ID
        bob_attempt_to_get_alice_file = self.drive_api.get_file(alice_file["id"], user_id=self.user_id_bob)
        self.assertIn("error", bob_attempt_to_get_alice_file)
        self.assertEqual(bob_attempt_to_get_alice_file["error"], "File not found")

        # Create a file for Bob
        bob_file = self.drive_api.create_file(user_id=self.user_id_bob)
        self.assertIsNotNone(bob_file)

        # Verify Alice cannot see Bob's file
        alice_attempt_to_get_bob_file = self.drive_api.get_file(bob_file["id"], user_id=self.user_id_alice)
        self.assertIn("error", alice_attempt_to_get_bob_file)
        self.assertEqual(alice_attempt_to_get_bob_file["error"], "File not found")

        # List Alice's files and ensure Bob's file is not there
        alice_files_list = self.drive_api.list_files(user_id=self.user_id_alice)
        self.assertIsNotNone(alice_files_list)
        self.assertIn("files", alice_files_list)
        self.assertFalse(any(f["id"] == bob_file["id"] for f in alice_files_list["files"]))

        # List Bob's files and ensure Alice's file is not there
        bob_files_list = self.drive_api.list_files(user_id=self.user_id_bob)
        self.assertIsNotNone(bob_files_list)
        self.assertIn("files", bob_files_list)
        self.assertFalse(any(f["id"] == alice_file["id"] for f in bob_files_list["files"]))

    # --- Comprehensive Workflow Tests ---
    def test_comprehensive_file_management_workflow(self):
        """Test comprehensive file management workflow."""
        # 1. Create a new file
        created_file = self.drive_api.create_file(user_id=self.user_id_alice)
        self.assertIsNotNone(created_file)
        file_id = created_file["id"]
        
        # 2. Update file properties
        updated_file = self.drive_api.update_file(file_id, addParents="project_folder", user_id=self.user_id_alice)
        self.assertIsNotNone(updated_file)
        self.assertIn("project_folder", updated_file["parents"])
        
        # 3. Star the file
        result = self.drive_api.star_file(file_id, user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        
        # 4. Share the file with Bob
        result = self.drive_api.share_file(file_id, self.user_id_bob, role="editor", user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        
        # 5. Get file revisions
        result = self.drive_api.get_file_revisions(file_id, user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        self.assertIn("revisions", result)
        
        # 6. Copy the file
        copied_file = self.drive_api.copy_file(file_id, user_id=self.user_id_alice)
        self.assertIsNotNone(copied_file)
        copied_file_id = copied_file["id"]
        
        # 7. Trash the copied file
        result = self.drive_api.trash_file(copied_file_id, user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        
        # 8. Delete the original file
        result = self.drive_api.delete_file(file_id, user_id=self.user_id_alice)
        self.assertTrue(result["deletion_status"])

    def test_comprehensive_folder_and_file_workflow(self):
        """Test comprehensive folder and file management workflow."""
        # 1. Create a main project folder
        main_folder = self.drive_api.create_folder("Main Project", user_id=self.user_id_alice)
        self.assertTrue(main_folder["success"])
        main_folder_id = main_folder["folder"]["id"]
        
        # 2. Create a subfolder
        subfolder = self.drive_api.create_folder("Documents", parents=[main_folder_id], user_id=self.user_id_alice)
        self.assertTrue(subfolder["success"])
        subfolder_id = subfolder["folder"]["id"]
        
        # 3. Create a file in the subfolder
        file_in_subfolder = self.drive_api.create_file(user_id=self.user_id_alice)
        self.assertIsNotNone(file_in_subfolder)
        file_id = file_in_subfolder["id"]
        
        # 4. Move file to subfolder
        updated_file = self.drive_api.update_file(file_id, addParents=subfolder_id, user_id=self.user_id_alice)
        self.assertIsNotNone(updated_file)
        self.assertIn(subfolder_id, updated_file["parents"])
        
        # 5. List files with query to find files in subfolder
        files_list = self.drive_api.list_files(user_id=self.user_id_alice, q=f"'{subfolder_id}' in parents")
        self.assertIsNotNone(files_list)
        
        # 6. Star the main folder
        result = self.drive_api.star_file(main_folder_id, user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        
        # 7. Share the main folder with Bob
        result = self.drive_api.share_file(main_folder_id, self.user_id_bob, role="reader", user_id=self.user_id_alice)
        self.assertTrue(result["success"])

    def test_collaborative_workflow(self):
        """Test collaborative workflow between users."""
        # 1. Alice creates a document
        alice_doc = self.drive_api.create_file(user_id=self.user_id_alice)
        self.assertIsNotNone(alice_doc)
        alice_doc_id = alice_doc["id"]
        
        # 2. Alice shares document with Bob as editor
        result = self.drive_api.share_file(alice_doc_id, self.user_id_bob, role="editor", user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        
        # 3. Bob creates his own document
        bob_doc = self.drive_api.create_file(user_id=self.user_id_bob)
        self.assertIsNotNone(bob_doc)
        bob_doc_id = bob_doc["id"]
        
        # 4. Bob shares document with Alice as reader
        result = self.drive_api.share_file(bob_doc_id, self.user_id_alice, role="reader", user_id=self.user_id_bob)
        self.assertTrue(result["success"])
        
        # 5. Both users copy shared documents
        alice_copy = self.drive_api.copy_file(alice_doc_id, user_id=self.user_id_alice)
        self.assertIsNotNone(alice_copy)
        
        bob_copy = self.drive_api.copy_file(bob_doc_id, user_id=self.user_id_bob)
        self.assertIsNotNone(bob_copy)
        
        # 6. Verify isolation - Alice cannot access Bob's private files
        alice_attempt = self.drive_api.get_file(bob_doc_id, user_id=self.user_id_alice)
        self.assertIn("error", alice_attempt)

    def test_error_handling_workflow(self):
        """Test comprehensive error handling scenarios."""
        # Test operations on non-existent files
        result = self.drive_api.star_file("non_existent", user_id=self.user_id_alice)
        self.assertFalse(result["success"])
        
        result = self.drive_api.trash_file("non_existent", user_id=self.user_id_alice)
        self.assertFalse(result["success"])
        
        result = self.drive_api.share_file("non_existent", self.user_id_bob, user_id=self.user_id_alice)
        self.assertFalse(result["success"])
        
        result = self.drive_api.get_file_revisions("non_existent", user_id=self.user_id_alice)
        self.assertFalse(result["success"])
        
        # Test operations with non-existent users
        result = self.drive_api.create_folder("Test", user_id="invalid@example.com")
        self.assertFalse(result["success"])
        
        result = self.drive_api.star_file("file_1_alice", user_id="invalid@example.com")
        self.assertFalse(result["success"])
        
        # Test copying non-existent file
        copied_file = self.drive_api.copy_file("non_existent", user_id=self.user_id_alice)
        self.assertIn("error", copied_file)

    def test_file_lifecycle_workflow(self):
        """Test complete file lifecycle from creation to deletion."""
        initial_count = len(self.drive_api._get_user_files(self.user_id_alice))
        
        # 1. Create file
        created_file = self.drive_api.create_file(user_id=self.user_id_alice)
        self.assertIsNotNone(created_file)
        file_id = created_file["id"]
        self.assertEqual(len(self.drive_api._get_user_files(self.user_id_alice)), initial_count + 1)
        
        # 2. Update file properties multiple times
        updated_file = self.drive_api.update_file(file_id, addParents="folder1", user_id=self.user_id_alice)
        self.assertIn("folder1", updated_file["parents"])
        
        updated_file = self.drive_api.update_file(file_id, addParents="folder2", user_id=self.user_id_alice)
        self.assertIn("folder2", updated_file["parents"])
        
        # 3. Star and unstar operations
        result = self.drive_api.star_file(file_id, user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        
        file_info = self.drive_api.get_file(file_id, user_id=self.user_id_alice)
        self.assertTrue(file_info["starred"])
        
        # 4. Trash and verify
        result = self.drive_api.trash_file(file_id, user_id=self.user_id_alice)
        self.assertTrue(result["success"])
        
        file_info = self.drive_api.get_file(file_id, user_id=self.user_id_alice)
        self.assertTrue(file_info["trashed"])
        
        # 5. Final deletion
        result = self.drive_api.delete_file(file_id, user_id=self.user_id_alice)
        self.assertTrue(result["deletion_status"])
        self.assertEqual(len(self.drive_api._get_user_files(self.user_id_alice)), initial_count)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
