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


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)