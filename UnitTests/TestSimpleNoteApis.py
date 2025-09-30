from SimpleNoteApis import SimpleNoteApis, DEFAULT_STATE
import unittest
from copy import deepcopy

class TestSimpleNoteApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh SimpleNoteApis instance for each test."""
        self.note_api = SimpleNoteApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.note_api._load_scenario(deepcopy(DEFAULT_STATE))
        self.user1 = "user123"
        self.user2 = "user456"

    # --- User Account Tests ---
    def test_show_account_user1(self):
        """Test showing account information for user1."""
        result = self.note_api.show_account(self.user1)
        self.assertTrue(result["success"])
        self.assertIn("account", result)
        self.assertEqual(result["account"]["user_alias"], self.user1)
        self.assertEqual(result["account"]["display_name"], "John Doe")

    def test_show_account_user2(self):
        """Test showing account information for user2."""
        result = self.note_api.show_account(self.user2)
        self.assertTrue(result["success"])
        self.assertIn("account", result)
        self.assertEqual(result["account"]["user_alias"], self.user2)
        self.assertEqual(result["account"]["display_name"], "Jane Smith")

    def test_show_account_non_existent_user(self):
        """Test showing account for non-existent user."""
        result = self.note_api.show_account("nonexistent_user")
        self.assertFalse(result["success"])
        self.assertNotIn("account", result)

    # --- List Notes Tests ---
    def test_list_notes_user1(self):
        """Test listing all notes for user1."""
        result = self.note_api.list_notes(user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("notes", result)
        self.assertEqual(len(result["notes"]), 3)  # user1 has 3 notes in default state

    def test_list_notes_user2(self):
        """Test listing all notes for user2."""
        result = self.note_api.list_notes(user=self.user2)
        self.assertTrue(result["success"])
        self.assertIn("notes", result)
        self.assertEqual(len(result["notes"]), 1)  # user2 has 1 note in default state

    def test_list_notes_with_limit(self):
        """Test listing notes with limit for user1."""
        result = self.note_api.list_notes(limit=2, user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("notes", result)
        self.assertEqual(len(result["notes"]), 2)

    def test_list_notes_with_offset(self):
        """Test listing notes with offset for user1."""
        result = self.note_api.list_notes(offset=1, user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("notes", result)
        self.assertEqual(len(result["notes"]), 2)  # 3 total - 1 offset = 2

    def test_list_notes_with_tag_filter(self):
        """Test listing notes filtered by tag."""
        result = self.note_api.list_notes(tags=["personal"], user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("notes", result)
        self.assertEqual(len(result["notes"]), 1)  # Only one note with "personal" tag

    def test_list_notes_non_existent_user(self):
        """Test listing notes for non-existent user."""
        result = self.note_api.list_notes(user="nonexistent_user")
        self.assertFalse(result["success"])
        self.assertEqual(len(result["notes"]), 0)

    # --- Get Note Tests ---
    def test_get_note_user1(self):
        """Test getting a specific note for user1."""
        result = self.note_api.get_note("0", user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("note", result)
        self.assertEqual(result["note"]["title"], "My First Note")
        self.assertEqual(result["note"]["user"], self.user1)

    def test_get_note_user2(self):
        """Test getting a specific note for user2."""
        result = self.note_api.get_note("3", user=self.user2)
        self.assertTrue(result["success"])
        self.assertIn("note", result)
        self.assertEqual(result["note"]["title"], "Meeting Minutes")
        self.assertEqual(result["note"]["user"], self.user2)

    def test_get_note_non_existent(self):
        """Test getting a non-existent note."""
        result = self.note_api.get_note("999", user=self.user1)
        self.assertFalse(result["success"])
        self.assertNotIn("note", result)

    def test_get_note_wrong_user(self):
        """Test getting a note that belongs to different user."""
        result = self.note_api.get_note("3", user=self.user1)  # user1 trying to access user2's note
        self.assertFalse(result["success"])
        self.assertNotIn("note", result)

    # --- Update Note Content Tests ---
    def test_update_note_content_user1(self):
        """Test updating note content for user1."""
        new_content = "This is updated content."
        result = self.note_api.update_note_content("0", new_content, user=self.user1)
        self.assertTrue(result["success"])
        
        # Verify update
        updated_note = self.note_api.get_note("0", user=self.user1)
        self.assertEqual(updated_note["note"]["content"], new_content)

    def test_update_note_content_user2(self):
        """Test updating note content for user2."""
        new_content = "Updated meeting minutes content."
        result = self.note_api.update_note_content("3", new_content, user=self.user2)
        self.assertTrue(result["success"])
        
        # Verify update
        updated_note = self.note_api.get_note("3", user=self.user2)
        self.assertEqual(updated_note["note"]["content"], new_content)

    def test_update_note_content_non_existent(self):
        """Test updating content of non-existent note."""
        result = self.note_api.update_note_content("999", "Should fail", user=self.user1)
        self.assertFalse(result["success"])

    def test_update_note_content_wrong_user(self):
        """Test updating note content for wrong user."""
        result = self.note_api.update_note_content("3", "Should fail", user=self.user1)
        self.assertFalse(result["success"])

    # --- Append/Prepend Note Content Tests ---
    def test_append_note_content(self):
        """Test appending content to a note."""
        original_content = self.note_api.notes[0]["content"]
        append_text = "This is appended text."
        result = self.note_api.append_or_prepend_note_content("0", "append", append_text, user=self.user1)
        self.assertTrue(result["success"])
        
        # Verify append
        updated_note = self.note_api.get_note("0", user=self.user1)
        expected_content = f"{original_content}\n{append_text}"
        self.assertEqual(updated_note["note"]["content"], expected_content)

    def test_prepend_note_content(self):
        """Test prepending content to a note."""
        original_content = self.note_api.notes[1]["content"]
        prepend_text = "This is prepended text."
        result = self.note_api.append_or_prepend_note_content("1", "prepend", prepend_text, user=self.user1)
        self.assertTrue(result["success"])
        
        # Verify prepend
        updated_note = self.note_api.get_note("1", user=self.user1)
        expected_content = f"{prepend_text}\n{original_content}"
        self.assertEqual(updated_note["note"]["content"], expected_content)

    def test_append_prepend_invalid_operation(self):
        """Test append/prepend with invalid operation."""
        result = self.note_api.append_or_prepend_note_content("0", "invalid", "text", user=self.user1)
        self.assertFalse(result["success"])

    def test_append_prepend_non_existent_note(self):
        """Test append/prepend on non-existent note."""
        result = self.note_api.append_or_prepend_note_content("999", "append", "text", user=self.user1)
        self.assertFalse(result["success"])

    # --- Share Note Tests ---
    def test_share_note_with_user(self):
        """Test sharing a note with another user."""
        result = self.note_api.share_note("0", self.user2, "read", user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("shared successfully", result["message"])

    def test_share_note_with_email(self):
        """Test sharing a note via email."""
        result = self.note_api.share_note("1", "friend@example.com", "read", user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("shared successfully", result["message"])

    def test_share_note_with_edit_permission(self):
        """Test sharing a note with edit permission."""
        result = self.note_api.share_note("2", self.user2, "edit", user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("shared successfully", result["message"])

    def test_share_note_non_existent(self):
        """Test sharing a non-existent note."""
        result = self.note_api.share_note("999", self.user2, "read", user=self.user1)
        self.assertFalse(result["success"])

    def test_share_note_wrong_user(self):
        """Test sharing a note that doesn't belong to user."""
        result = self.note_api.share_note("3", self.user1, "read", user=self.user1)  # user1 sharing user2's note
        self.assertFalse(result["success"])

    # --- Add Reminder Tests ---
    def test_add_reminder_to_note(self):
        """Test adding a reminder to a note."""
        reminder_date = "2025-12-31T23:59:59"
        result = self.note_api.add_reminder("0", reminder_date, user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("reminder added", result["message"])

    def test_add_reminder_with_message(self):
        """Test adding a reminder with custom message."""
        reminder_date = "2025-12-25T12:00:00"
        reminder_message = "Don't forget Christmas!"
        result = self.note_api.add_reminder("1", reminder_date, reminder_message, user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("reminder added", result["message"])

    def test_add_reminder_non_existent_note(self):
        """Test adding reminder to non-existent note."""
        result = self.note_api.add_reminder("999", "2025-12-31T23:59:59", user=self.user1)
        self.assertFalse(result["success"])

    def test_add_reminder_wrong_user(self):
        """Test adding reminder to note of wrong user."""
        result = self.note_api.add_reminder("3", "2025-12-31T23:59:59", user=self.user1)
        self.assertFalse(result["success"])

    def test_add_reminder_invalid_date(self):
        """Test adding reminder with invalid date format."""
        result = self.note_api.add_reminder("0", "invalid-date", user=self.user1)
        self.assertFalse(result["success"])

    # --- Get Notes by Color Tests ---
    def test_get_notes_by_color_yellow(self):
        """Test getting notes by yellow color."""
        result = self.note_api.get_notes_by_color("yellow", user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("notes", result)
        # Check that returned notes have yellow color
        for note in result["notes"]:
            self.assertEqual(note["color"], "yellow")

    def test_get_notes_by_color_blue(self):
        """Test getting notes by blue color."""
        result = self.note_api.get_notes_by_color("blue", user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("notes", result)

    def test_get_notes_by_color_non_existent_user(self):
        """Test getting notes by color for non-existent user."""
        result = self.note_api.get_notes_by_color("yellow", user="nonexistent")
        self.assertFalse(result["success"])

    def test_get_notes_by_color_invalid_color(self):
        """Test getting notes by invalid color."""
        result = self.note_api.get_notes_by_color("invalid_color", user=self.user1)
        self.assertTrue(result["success"])  # Should succeed but return empty list
        self.assertEqual(len(result["notes"]), 0)

    # --- Get Notes by Priority Tests ---
    def test_get_notes_by_priority_high(self):
        """Test getting notes by high priority."""
        result = self.note_api.get_notes_by_priority("high", user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("notes", result)
        # Check that returned notes have high priority
        for note in result["notes"]:
            self.assertEqual(note["priority"], "high")

    def test_get_notes_by_priority_medium(self):
        """Test getting notes by medium priority."""
        result = self.note_api.get_notes_by_priority("medium", user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("notes", result)

    def test_get_notes_by_priority_low(self):
        """Test getting notes by low priority."""
        result = self.note_api.get_notes_by_priority("low", user=self.user1)
        self.assertTrue(result["success"])
        self.assertIn("notes", result)

    def test_get_notes_by_priority_non_existent_user(self):
        """Test getting notes by priority for non-existent user."""
        result = self.note_api.get_notes_by_priority("high", user="nonexistent")
        self.assertFalse(result["success"])

    def test_get_notes_by_priority_invalid_priority(self):
        """Test getting notes by invalid priority."""
        result = self.note_api.get_notes_by_priority("invalid_priority", user=self.user1)
        self.assertTrue(result["success"])  # Should succeed but return empty list
        self.assertEqual(len(result["notes"]), 0)

    # --- Reset Data Tests ---
    def test_reset_data(self):
        """Test resetting all data."""
        # First modify some data
        self.note_api.create_note("Test Note", "Test Content", user=self.user1)
        initial_notes_count = len(self.note_api.notes)
        
        # Reset data
        result = self.note_api.reset_data()
        self.assertTrue(result["success"])
        
        # Verify data is reset to default state
        # The reset should reload DEFAULT_STATE
        self.assertLessEqual(len(self.note_api.notes), initial_notes_count)

    # --- Unit Tests for Core Functions (most important for audio calling) ---

    def test_create_note_success(self):
        """Test creating a new note successfully."""
        initial_note_count = len(self.note_api.notes)
        result = self.note_api.create_note("New Test Note", "This is a test content.", user=self.user1)
        self.assertTrue(result["status"])
        self.assertEqual(len(self.note_api.notes), initial_note_count + 1)
        new_note_id = result["id"]
        self.assertIn(new_note_id, self.note_api.notes)
        self.assertEqual(self.note_api.notes[new_note_id]["title"], "New Test Note")
        self.assertEqual(self.note_api.notes[new_note_id]["user"], self.user1)

    def test_show_note_success(self):
        """Test showing details of an existing note."""
        note_id = 0 # "My First Note" belongs to user123
        result = self.note_api.show_note(note_id, user=self.user1)
        self.assertTrue(result["status"])
        self.assertEqual(result["title"], "My First Note")
        self.assertEqual(result["content"], "This is the content of my first note. It's about getting started.")
        self.assertTrue(result["pinned"])

    def test_show_note_not_found(self):
        """Test showing a non-existent note."""
        result = self.note_api.show_note(999, user=self.user1)
        self.assertFalse(result["status"])
        self.assertNotIn("title", result)

    def test_show_note_wrong_user(self):
        """Test showing a note that belongs to a different user."""
        note_id = 3 # "Meeting Minutes" belongs to user456
        result = self.note_api.show_note(note_id, user=self.user1) # user123 trying to access user456's note
        self.assertFalse(result["status"])

    def test_search_notes_by_query(self):
        """Test searching notes by a query string."""
        result = self.note_api.search_notes("grocery", user=self.user1)
        self.assertTrue(result["status"])
        self.assertEqual(len(result["notes"]), 1)
        self.assertEqual(result["notes"][0]["title"], "Grocery List")

    def test_search_notes_by_tag(self):
        """Test searching notes by a specific tag."""
        result = self.note_api.search_notes("note", tags=["personal"], user=self.user1)
        self.assertTrue(result["status"])
        self.assertEqual(len(result["notes"]), 1)
        self.assertEqual(result["notes"][0]["title"], "My First Note")

    def test_search_notes_by_pinned_status(self):
        """Test searching notes by pinned status."""
        # Corrected: Changed query to empty string to only filter by pinned status and user
        result = self.note_api.search_notes(query="", pinned=True, user=self.user1)
        self.assertTrue(result["status"])
        self.assertEqual(len(result["notes"]), 2) # "My First Note", "Project Ideas"
        self.assertTrue(all(n["pinned"] for n in result["notes"]))

    def test_update_note_title(self):
        """Test updating a note's title."""
        note_id = 0
        new_title = "Updated First Note"
        result = self.note_api.update_note(note_id, title=new_title, user=self.user1)
        self.assertTrue(result["status"])
        self.assertEqual(self.note_api.notes[note_id]["title"], new_title)

    def test_update_note_content(self):
        """Test updating a note's content."""
        note_id = 1
        new_content = "Updated content for grocery list."
        result = self.note_api.update_note(note_id, content=new_content, user=self.user1)
        self.assertTrue(result["status"])
        self.assertEqual(self.note_api.notes[note_id]["content"], new_content)

    def test_add_content_to_note_append(self):
        """Test appending content to a note."""
        note_id = 0
        initial_content = self.note_api.notes[note_id]["content"]
        added_content = "New line appended."
        result = self.note_api.add_content_to_note(note_id, "append", added_content, user=self.user1)
        self.assertTrue(result["status"])
        self.assertEqual(self.note_api.notes[note_id]["content"], f"{initial_content}\n{added_content}")

    def test_add_content_to_note_prepend(self):
        """Test prepending content to a note."""
        note_id = 1
        initial_content = self.note_api.notes[note_id]["content"]
        # Corrected: Removed trailing newline from prepended_text, as the function adds one.
        added_content = "Important: " 
        result = self.note_api.add_content_to_note(note_id, "prepend", added_content, user=self.user1)
        self.assertTrue(result["status"])
        # Expected content now reflects the single newline added by the function
        self.assertEqual(self.note_api.notes[note_id]["content"], f"{added_content}\n{initial_content}")

    def test_delete_note_success(self):
        """Test deleting an existing note."""
        note_id_to_delete = 2 # "Project Ideas"
        initial_note_count = len(self.note_api.notes)
        result = self.note_api.delete_note(note_id_to_delete, user=self.user1)
        self.assertTrue(result["status"])
        self.assertEqual(len(self.note_api.notes), initial_note_count - 1)
        self.assertNotIn(note_id_to_delete, self.note_api.notes)

    def test_delete_note_not_found(self):
        """Test deleting a non-existent note."""
        result = self.note_api.delete_note(999, user=self.user1)
        self.assertFalse(result["status"])

    def test_delete_note_wrong_user(self):
        """Test deleting a note that belongs to a different user."""
        note_id = 3 # "Meeting Minutes" belongs to user456
        result = self.note_api.delete_note(note_id, user=self.user1) # user123 trying to delete user456's note
        self.assertFalse(result["status"])
        self.assertIn(note_id, self.note_api.notes) # Note should still exist

    # --- Combined Functionality Tests ---

    def test_create_search_and_update_note(self):
        """
        Scenario: Create a note, search for it, then update its content.
        Functions: create_note, search_notes, update_note
        """
        # 1. Create a note
        new_title = "My Combined Test Note"
        new_content = "Initial content for combined test."
        create_result = self.note_api.create_note(new_title, new_content, tags=["test"], user=self.user1)
        self.assertTrue(create_result["status"])
        new_note_id = create_result["id"]

        # 2. Search for the newly created note
        search_result = self.note_api.search_notes(new_title, user=self.user1)
        self.assertTrue(search_result["status"])
        self.assertEqual(len(search_result["notes"]), 1)
        self.assertEqual(search_result["notes"][0]["id"], new_note_id)
        self.assertEqual(search_result["notes"][0]["content"], new_content)

        # 3. Update the content of the note
        updated_content = "Updated content after searching."
        update_result = self.note_api.update_note(new_note_id, content=updated_content, user=self.user1)
        self.assertTrue(update_result["status"])

        # 4. Verify the update by showing the note
        show_result = self.note_api.show_note(new_note_id, user=self.user1)
        self.assertTrue(show_result["status"])
        self.assertEqual(show_result["content"], updated_content)

    def test_create_add_content_and_show_note(self):
        """
        Scenario: Create a note, add more content to it, then show the note to verify.
        Functions: create_note, add_content_to_note, show_note
        """
        # 1. Create a note
        title = "Dynamic Content Note"
        initial_content = "This is the first part."
        create_result = self.note_api.create_note(title, initial_content, user=self.user1)
        self.assertTrue(create_result["status"])
        note_id = create_result["id"]

        # 2. Append content
        appended_text = "And this is the appended part."
        append_result = self.note_api.add_content_to_note(note_id, "append", appended_text, user=self.user1)
        self.assertTrue(append_result["status"])

        # 3. Prepend content
        # Corrected: Removed trailing newline from prepended_text to avoid double newlines
        prepended_text = "This is the prepended part." 
        prepend_result = self.note_api.add_content_to_note(note_id, "prepend", prepended_text, user=self.user1)
        self.assertTrue(prepend_result["status"])

        # 4. Show the note and verify all content
        show_result = self.note_api.show_note(note_id, user=self.user1)
        self.assertTrue(show_result["status"])
        # Expected content now matches the function's behavior (single newline after prepended text)
        expected_content = f"{prepended_text}\n{initial_content}\n{appended_text}"
        self.assertEqual(show_result["content"], expected_content)

    def test_create_pin_and_search_pinned_notes(self):
        """
        Scenario: Create a note, pin it, then search for pinned notes.
        Functions: create_note, update_note, search_notes
        """
        # 1. Create a note (initially unpinned)
        title = "Note to Pin"
        content = "This note will be pinned."
        create_result = self.note_api.create_note(title, content, pinned=False, user=self.user1)
        self.assertTrue(create_result["status"])
        note_id = create_result["id"]

        # 2. Update the note to be pinned
        update_result = self.note_api.update_note(note_id, pinned=True, user=self.user1)
        self.assertTrue(update_result["status"])

        # 3. Search for pinned notes
        # Corrected: Changed query to empty string to only filter by pinned status and user
        search_pinned_result = self.note_api.search_notes(query="", pinned=True, user=self.user1)
        self.assertTrue(search_pinned_result["status"])
        # Check that our newly pinned note is in the results, along with any other default pinned notes
        found = False
        for note in search_pinned_result["notes"]:
            if note["id"] == note_id and note["pinned"]:
                found = True
                break
        self.assertTrue(found)
        # Ensure the count is correct (default pinned notes + our new one)
        # Default state has 2 pinned notes for user123 (id 0 and 2)
        self.assertEqual(len(search_pinned_result["notes"]), 3)

    # --- Comprehensive Workflow Tests ---
    def test_comprehensive_note_management_workflow(self):
        """Test comprehensive note management workflow."""
        # 1. Create a new note
        result = self.note_api.create_note("Workflow Note", "Initial content", user=self.user1)
        self.assertTrue(result["status"])
        note_id = result["id"]
        
        # 2. Update note content using update_note_content
        result = self.note_api.update_note_content(note_id, "Updated content", user=self.user1)
        self.assertTrue(result["success"])
        
        # 3. Append more content
        result = self.note_api.append_or_prepend_note_content(note_id, "append", "Appended text", user=self.user1)
        self.assertTrue(result["success"])
        
        # 4. Share the note
        result = self.note_api.share_note(note_id, self.user2, "read", user=self.user1)
        self.assertTrue(result["success"])
        
        # 5. Add a reminder
        result = self.note_api.add_reminder(note_id, "2025-12-31T23:59:59", user=self.user1)
        self.assertTrue(result["success"])
        
        # 6. Verify final state
        final_note = self.note_api.get_note(note_id, user=self.user1)
        self.assertTrue(final_note["success"])
        expected_content = "Updated content\nAppended text"
        self.assertEqual(final_note["note"]["content"], expected_content)

    def test_comprehensive_search_and_filter_workflow(self):
        """Test comprehensive search and filtering workflow."""
        # 1. Create notes with different properties
        note1_result = self.note_api.create_note("High Priority Task", "Important work", tags=["work"], user=self.user1)
        self.assertTrue(note1_result["status"])
        note1_id = note1_result["id"]
        
        note2_result = self.note_api.create_note("Personal Reminder", "Buy groceries", tags=["personal"], user=self.user1)
        self.assertTrue(note2_result["status"])
        note2_id = note2_result["id"]
        
        # 2. Search by different criteria
        search_work = self.note_api.search_notes("work", user=self.user1)
        self.assertTrue(search_work["status"])
        
        search_personal = self.note_api.search_notes("personal", tags=["personal"], user=self.user1)
        self.assertTrue(search_personal["status"])
        
        # 3. Get notes by color (if any)
        color_result = self.note_api.get_notes_by_color("yellow", user=self.user1)
        self.assertTrue(color_result["success"])
        
        # 4. Get notes by priority
        priority_result = self.note_api.get_notes_by_priority("high", user=self.user1)
        self.assertTrue(priority_result["success"])
        
        # 5. List all notes with limit
        limited_list = self.note_api.list_notes(limit=3, user=self.user1)
        self.assertTrue(limited_list["success"])
        self.assertLessEqual(len(limited_list["notes"]), 3)

    def test_multi_user_collaboration_workflow(self):
        """Test multi-user collaboration workflow."""
        # 1. User1 creates a note
        note_result = self.note_api.create_note("Shared Project", "Project details", user=self.user1)
        self.assertTrue(note_result["status"])
        note_id = note_result["id"]
        
        # 2. User1 shares note with User2
        share_result = self.note_api.share_note(note_id, self.user2, "edit", user=self.user1)
        self.assertTrue(share_result["success"])
        
        # 3. User2 creates their own note
        user2_note = self.note_api.create_note("User2 Note", "User2 content", user=self.user2)
        self.assertTrue(user2_note["status"])
        user2_note_id = user2_note["id"]
        
        # 4. Verify user isolation - User1 cannot access User2's private note
        user1_access_attempt = self.note_api.get_note(user2_note_id, user=self.user1)
        self.assertFalse(user1_access_attempt["success"])
        
        # 5. User2 adds reminder to their own note
        reminder_result = self.note_api.add_reminder(user2_note_id, "2025-12-25T12:00:00", user=self.user2)
        self.assertTrue(reminder_result["success"])
        
        # 6. Both users list their notes
        user1_notes = self.note_api.list_notes(user=self.user1)
        user2_notes = self.note_api.list_notes(user=self.user2)
        self.assertTrue(user1_notes["success"])
        self.assertTrue(user2_notes["success"])

    def test_content_manipulation_workflow(self):
        """Test comprehensive content manipulation workflow."""
        # 1. Create a note
        result = self.note_api.create_note("Content Test", "Original content", user=self.user1)
        self.assertTrue(result["status"])
        note_id = result["id"]
        
        # 2. Prepend content
        prepend_result = self.note_api.append_or_prepend_note_content(note_id, "prepend", "Prepended text", user=self.user1)
        self.assertTrue(prepend_result["success"])
        
        # 3. Append content
        append_result = self.note_api.append_or_prepend_note_content(note_id, "append", "Appended text", user=self.user1)
        self.assertTrue(append_result["success"])
        
        # 4. Verify final content structure
        final_note = self.note_api.get_note(note_id, user=self.user1)
        self.assertTrue(final_note["success"])
        expected_content = "Prepended text\nOriginal content\nAppended text"
        self.assertEqual(final_note["note"]["content"], expected_content)
        
        # 5. Update entire content
        update_result = self.note_api.update_note_content(note_id, "Completely new content", user=self.user1)
        self.assertTrue(update_result["success"])
        
        # 6. Verify update
        updated_note = self.note_api.get_note(note_id, user=self.user1)
        self.assertEqual(updated_note["note"]["content"], "Completely new content")

    def test_error_handling_workflow(self):
        """Test comprehensive error handling scenarios."""
        # Test operations with non-existent notes
        result = self.note_api.get_note("999", user=self.user1)
        self.assertFalse(result["success"])
        
        result = self.note_api.update_note_content("999", "content", user=self.user1)
        self.assertFalse(result["success"])
        
        result = self.note_api.share_note("999", self.user2, "read", user=self.user1)
        self.assertFalse(result["success"])
        
        result = self.note_api.add_reminder("999", "2025-12-31T23:59:59", user=self.user1)
        self.assertFalse(result["success"])
        
        # Test operations with non-existent users
        result = self.note_api.show_account("nonexistent")
        self.assertFalse(result["success"])
        
        result = self.note_api.list_notes(user="nonexistent")
        self.assertFalse(result["success"])
        
        result = self.note_api.get_notes_by_color("yellow", user="nonexistent")
        self.assertFalse(result["success"])
        
        # Test cross-user access violations
        user2_note = self.note_api.create_note("User2 Private", "Private content", user=self.user2)
        user2_note_id = user2_note["id"]
        
        # User1 trying to access User2's note
        result = self.note_api.get_note(user2_note_id, user=self.user1)
        self.assertFalse(result["success"])
        
        result = self.note_api.update_note_content(user2_note_id, "hack attempt", user=self.user1)
        self.assertFalse(result["success"])

    def test_account_and_preferences_workflow(self):
        """Test account management and preferences workflow."""
        # 1. Check account information for both users
        user1_account = self.note_api.show_account(self.user1)
        self.assertTrue(user1_account["success"])
        self.assertEqual(user1_account["account"]["user_alias"], self.user1)
        
        user2_account = self.note_api.show_account(self.user2)
        self.assertTrue(user2_account["success"])
        self.assertEqual(user2_account["account"]["user_alias"], self.user2)
        
        # 2. Create notes with different colors and priorities
        high_priority_note = self.note_api.create_note("Urgent Task", "High priority content", user=self.user1)
        self.assertTrue(high_priority_note["status"])
        
        # 3. Filter by different attributes
        high_priority_notes = self.note_api.get_notes_by_priority("high", user=self.user1)
        self.assertTrue(high_priority_notes["success"])
        
        yellow_notes = self.note_api.get_notes_by_color("yellow", user=self.user1)
        self.assertTrue(yellow_notes["success"])
        
        # 4. Test data reset functionality
        initial_notes_count = len(self.note_api.notes)
        reset_result = self.note_api.reset_data()
        self.assertTrue(reset_result["success"])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)