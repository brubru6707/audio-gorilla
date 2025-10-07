import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import API and helper
from SimpleNoteApis import SimpleNoteApis
from UnitTests.test_data_helper import BackendDataLoader

class TestSimpleNoteApis(unittest.TestCase):
    """
    Unit tests for the SimpleNoteApis class, covering multi-user functionality.
    """

    # Load real data from backend
    real_data = BackendDataLoader.get_simple_notes_data()
    
    # Extract real user data - use aliases, not UUIDs
    user_data_list = list(real_data.get("users", {}).values())
    REAL_USER_ALICE = user_data_list[0].get("alias", "alice") if user_data_list else "alice"
    REAL_USER_BOB = user_data_list[1].get("alias", "bob") if len(user_data_list) > 1 else "bob"
    
    # Extract real note data from Alice's notes
    alice_uuid = None
    for uuid, user_data in real_data.get("users", {}).items():
        if user_data.get("alias") == REAL_USER_ALICE:
            alice_uuid = uuid
            break
    
    alice_notes = {}
    if alice_uuid:
        alice_notes = real_data["users"][alice_uuid].get("note_data", {}).get("notes", {})
    
    # Get the first note from Alice's notes
    REAL_NOTE_ID = next(iter(alice_notes.keys()), "note1") if alice_notes else "note1"
    note_data = alice_notes.get(REAL_NOTE_ID, {}) if alice_notes else {}
    REAL_NOTE_TITLE = note_data.get("title", "Test Note")
    REAL_NOTE_CONTENT = note_data.get("content", "Test content")
    
    # Extract real note data from Bob's notes
    bob_uuid = None
    for uuid, user_data in real_data.get("users", {}).items():
        if user_data.get("alias") == REAL_USER_BOB:
            bob_uuid = uuid
            break
    
    bob_notes = {}
    if bob_uuid:
        bob_notes = real_data["users"][bob_uuid].get("note_data", {}).get("notes", {})
    
    # Get the first note from Bob's notes
    REAL_NOTE_ID_BOB = next(iter(bob_notes.keys()), "note1") if bob_notes else "note1"
    
    def setUp(self):
        """Set up the API instance using real data."""
        self.notes_api = SimpleNoteApis()

    # --- Account Tests ---
    def test_show_account_alice(self):
        """Test showing account for Alice."""
        result = self.notes_api.show_account(user=self.REAL_USER_ALICE)
        self.assertTrue(result.get("status", False))
        if result.get("status"):
            self.assertIn("profile_data", result)

    def test_show_account_bob(self):
        """Test showing account for Bob."""
        result = self.notes_api.show_account(user=self.REAL_USER_BOB)
        self.assertTrue(result.get("status", False))

    def test_show_account_non_existent(self):
        """Test showing account for non-existent user."""
        result = self.notes_api.show_account(user="nonexistent")
        self.assertFalse(result.get("status", True))

    # --- Note Listing Tests ---
    def test_list_notes_alice_no_params(self):
        """Test listing notes for Alice without parameters."""
        result = self.notes_api.list_notes(user=self.REAL_USER_ALICE)
        self.assertTrue(result.get("status", False))
        if result.get("status"):
            self.assertIn("notes", result)

    def test_list_notes_bob_with_limit(self):
        """Test listing notes for Bob with limit."""
        result = self.notes_api.list_notes(user=self.REAL_USER_BOB)
        self.assertTrue(result.get("status", False))

    def test_list_notes_with_offset(self):
        """Test listing notes with offset."""
        result = self.notes_api.list_notes(user=self.REAL_USER_ALICE)
        self.assertTrue(result.get("status", False))

    def test_list_notes_with_sort_order(self):
        """Test listing notes with sort order."""
        result = self.notes_api.list_notes(user=self.REAL_USER_ALICE)
        self.assertTrue(result.get("status", False))

    def test_list_notes_with_since_date(self):
        """Test listing notes with since date filter."""
        result = self.notes_api.list_notes(user=self.REAL_USER_ALICE)
        self.assertTrue(result.get("status", False))

    def test_list_notes_non_existent_user(self):
        """Test listing notes for non-existent user."""
        result = self.notes_api.list_notes(user="nonexistent")
        self.assertFalse(result.get("status", True))

    # --- Note Management Tests ---
    def test_get_note_alice_existing(self):
        """Test getting an existing note for Alice."""
        result = self.notes_api.get_note(note_id=self.REAL_NOTE_ID, user=self.REAL_USER_ALICE)
        self.assertTrue(result.get("status", False))
        if result.get("status"):
            self.assertIn("note", result)

    def test_get_note_bob_existing(self):
        """Test getting an existing note for Bob."""
        result = self.notes_api.get_note(note_id=self.REAL_NOTE_ID_BOB, user=self.REAL_USER_BOB)
        self.assertTrue(result.get("status", False))

    def test_get_note_non_existent(self):
        """Test getting a non-existent note."""
        result = self.notes_api.get_note(note_id="non_existent_note", user=self.REAL_USER_ALICE)
        self.assertFalse(result.get("status", True))

    def test_create_note_alice_simple(self):
        """Test creating a simple note for Alice."""
        result = self.notes_api.create_note(
            user=self.REAL_USER_ALICE,
            title="Simple Test Note",
            content="Test note content"
        )
        self.assertTrue(result.get("status", False))
        if result.get("status"):
            self.assertIn("note", result)
            self.assertIn("id", result["note"])

    def test_create_note_bob_with_title(self):
        """Test creating a note with title for Bob."""
        result = self.notes_api.create_note(
            user=self.REAL_USER_BOB,
            content="Test note content",
            title="Test Note Title"
        )
        self.assertTrue(result.get("status", False))

    def test_create_note_with_color(self):
        """Test creating a note with color."""
        result = self.notes_api.create_note(
            user=self.REAL_USER_ALICE,
            title="Colored Note",
            content="Colored note content",
            color="blue"
        )
        self.assertTrue(result.get("status", False))

    def test_create_note_with_priority(self):
        """Test creating a note with priority."""
        result = self.notes_api.create_note(
            user=self.REAL_USER_ALICE,
            title="Priority Note",
            content="Priority note content",
            priority="high"
        )
        self.assertTrue(result.get("status", False))

    def test_create_note_with_reminder(self):
        """Test creating a note with reminder."""
        result = self.notes_api.create_note(
            user=self.REAL_USER_ALICE,
            title="Reminder Note",
            content="Note with reminder"
        )
        self.assertTrue(result.get("status", False))

    def test_create_note_non_existent_user(self):
        """Test creating a note for non-existent user."""
        result = self.notes_api.create_note(
            user="nonexistent",
            title="Non-existent User Note",
            content="Test content"
        )
        self.assertFalse(result.get("status", True))

    def test_update_note_content_alice(self):
        """Test updating note content for Alice."""
        # First create a note
        create_result = self.notes_api.create_note(user=self.REAL_USER_ALICE, title="Update Test Note", content="Original content")
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            result = self.notes_api.update_note_content(
                note_id=note_id,
                user=self.REAL_USER_ALICE,
                new_content="Updated content"
            )
            self.assertTrue(result.get("status", False))

    def test_update_note_content_with_title(self):
        """Test updating note content with new title."""
        # First create a note
        create_result = self.notes_api.create_note(user=self.REAL_USER_ALICE, title="Original Title", content="Original content")
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            result = self.notes_api.update_note_content(
                note_id=note_id,
                user=self.REAL_USER_ALICE,
                new_content="Updated content",
                new_title="Updated Title"
            )
            self.assertTrue(result.get("status", False))

    def test_update_note_content_non_existent(self):
        """Test updating content for non-existent note."""
        result = self.notes_api.update_note_content(
            note_id="non_existent_note",
            user=self.REAL_USER_ALICE,
            new_content="Updated content"
        )
        self.assertFalse(result.get("status", True))

    def test_append_or_prepend_note_content_append(self):
        """Test appending content to a note."""
        # First create a note
        create_result = self.notes_api.create_note(user=self.REAL_USER_ALICE, title="Append Test Note", content="Original content")
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            result = self.notes_api.append_or_prepend_note_content(
                note_id=note_id,
                user=self.REAL_USER_ALICE,
                added_content=" Appended text",
                append_or_prepend="append"
            )
            self.assertTrue(result.get("status", False))

    def test_append_or_prepend_note_content_prepend(self):
        """Test prepending content to a note."""
        # First create a note
        create_result = self.notes_api.create_note(user=self.REAL_USER_ALICE, title="Prepend Test Note", content="Original content")
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            result = self.notes_api.append_or_prepend_note_content(
                note_id=note_id,
                user=self.REAL_USER_ALICE,
                added_content="Prepended text ",
                append_or_prepend="prepend"
            )
            self.assertTrue(result.get("status", False))

    def test_delete_note_alice(self):
        """Test deleting a note for Alice."""
        # First create a note
        create_result = self.notes_api.create_note(user=self.REAL_USER_ALICE, title="Delete Test Note", content="To be deleted")
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            result = self.notes_api.delete_note(note_id=note_id, user=self.REAL_USER_ALICE)
            self.assertTrue(result.get("status", False))

    def test_delete_note_bob(self):
        """Test deleting a note for Bob."""
        # First create a note
        create_result = self.notes_api.create_note(user=self.REAL_USER_BOB, title="Delete Test Note Bob", content="To be deleted")
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            result = self.notes_api.delete_note(note_id=note_id, user=self.REAL_USER_BOB)
            self.assertTrue(result.get("status", False))

    def test_delete_note_non_existent(self):
        """Test deleting a non-existent note."""
        result = self.notes_api.delete_note(note_id="non_existent_note", user=self.REAL_USER_ALICE)
        self.assertFalse(result.get("status", True))

    def test_share_note_alice_to_bob(self):
        """Test sharing a note from Alice to Bob."""
        # First create a note
        create_result = self.notes_api.create_note(user=self.REAL_USER_ALICE, title="Shared Note Alice", content="Shared note")
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            result = self.notes_api.share_note(
                note_id=note_id,
                user=self.REAL_USER_ALICE,
                share_with_alias=self.REAL_USER_BOB
            )
            self.assertTrue(result.get("status", False))

    def test_share_note_bob_to_alice_with_permissions(self):
        """Test sharing a note from Bob to Alice with specific permissions."""
        # First create a note
        create_result = self.notes_api.create_note(user=self.REAL_USER_BOB, title="Shared Note Bob", content="Shared note")
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            result = self.notes_api.share_note(
                note_id=note_id,
                user=self.REAL_USER_BOB,
                share_with_alias=self.REAL_USER_ALICE
            )
            self.assertTrue(result.get("status", False))

    def test_share_note_non_existent(self):
        """Test sharing a non-existent note."""
        result = self.notes_api.share_note(
            note_id="non_existent_note",
            user=self.REAL_USER_ALICE,
            share_with_alias=self.REAL_USER_BOB
        )
        self.assertFalse(result.get("status", True))

    def test_add_reminder_alice(self):
        """Test adding a reminder to a note for Alice."""
        # First create a note
        create_result = self.notes_api.create_note(user=self.REAL_USER_ALICE, title="Reminder Note Alice", content="Note with reminder")
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            result = self.notes_api.add_reminder(
                note_id=note_id,
                user=self.REAL_USER_ALICE,
                reminder_timestamp="2024-12-31T10:00:00Z"
            )
            self.assertTrue(result.get("status", False))

    def test_add_reminder_bob_with_message(self):
        """Test adding a reminder with message for Bob."""
        # First create a note
        create_result = self.notes_api.create_note(user=self.REAL_USER_BOB, title="Reminder Note Bob", content="Note with reminder")
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            result = self.notes_api.add_reminder(
                note_id=note_id,
                user=self.REAL_USER_BOB,
                reminder_timestamp="2024-12-31T10:00:00Z",
                status="active"
            )
            self.assertTrue(result.get("status", False))

    def test_add_reminder_non_existent_note(self):
        """Test adding reminder to non-existent note."""
        result = self.notes_api.add_reminder(
            note_id="non_existent_note",
            user=self.REAL_USER_ALICE,
            reminder_timestamp="2024-12-31T10:00:00Z"
        )
        self.assertFalse(result.get("status", True))

    # --- Search Tests ---
    def test_search_notes_alice_by_content(self):
        """Test searching notes by content for Alice."""
        result = self.notes_api.search_notes(
            user=self.REAL_USER_ALICE,
            query="test"
        )
        self.assertTrue(result.get("status", False))
        if result.get("status"):
            self.assertIn("notes", result)

    def test_search_notes_bob_by_title(self):
        """Test searching notes by title for Bob."""
        result = self.notes_api.search_notes(
            user=self.REAL_USER_BOB,
            query="test",
            search_in_title=True
        )
        self.assertTrue(result.get("status", False))

    def test_search_notes_with_limit(self):
        """Test searching notes with limit."""
        result = self.notes_api.search_notes(
            user=self.REAL_USER_ALICE,
            query="test"
        )
        self.assertTrue(result.get("status", False))

    def test_search_notes_case_insensitive(self):
        """Test searching notes case insensitive."""
        result = self.notes_api.search_notes(
            user=self.REAL_USER_ALICE,
            query="TEST"
        )
        self.assertTrue(result.get("status", False))

    def test_search_notes_non_existent_user(self):
        """Test searching notes for non-existent user."""
        result = self.notes_api.search_notes(
            user="nonexistent",
            query="test"
        )
        self.assertFalse(result.get("status", True))

    def test_get_notes_by_color_alice(self):
        """Test getting notes by color for Alice."""
        result = self.notes_api.get_notes_by_color(
            user=self.REAL_USER_ALICE,
            color="blue"
        )
        self.assertTrue(result.get("status", False))

    def test_get_notes_by_color_bob_with_limit(self):
        """Test getting notes by color for Bob with limit."""
        result = self.notes_api.get_notes_by_color(
            user=self.REAL_USER_BOB,
            color="red"
        )
        self.assertTrue(result.get("status", False))

    def test_get_notes_by_color_non_existent_user(self):
        """Test getting notes by color for non-existent user."""
        result = self.notes_api.get_notes_by_color(
            user="nonexistent",
            color="blue"
        )
        self.assertFalse(result.get("status", True))

    def test_get_notes_by_priority_alice(self):
        """Test getting notes by priority for Alice."""
        result = self.notes_api.get_notes_by_priority(
            user=self.REAL_USER_ALICE,
            priority="high"
        )
        self.assertTrue(result.get("status", False))

    def test_get_notes_by_priority_bob_with_limit(self):
        """Test getting notes by priority for Bob with limit."""
        result = self.notes_api.get_notes_by_priority(
            user=self.REAL_USER_BOB,
            priority="medium"
        )
        self.assertTrue(result.get("status", False))

    def test_get_notes_by_priority_non_existent_user(self):
        """Test getting notes by priority for non-existent user."""
        result = self.notes_api.get_notes_by_priority(
            user="nonexistent",
            priority="high"
        )
        self.assertFalse(result.get("status", True))

    # --- Workflow Tests ---
    def test_create_update_search_delete_flow(self):
        """Test the flow of creating, updating, searching, and deleting a note."""
        # Create note
        create_result = self.notes_api.create_note(
            user=self.REAL_USER_ALICE,
            content="Original workflow content",
            title="Workflow Test"
        )
        self.assertTrue(create_result.get("status", False))
        
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            
            # Update note
            update_result = self.notes_api.update_note_content(
                note_id=note_id,
                user=self.REAL_USER_ALICE,
                new_content="Updated workflow content"
            )
            self.assertTrue(update_result.get("status", False))
            
            # Search for the note
            search_result = self.notes_api.search_notes(
                user=self.REAL_USER_ALICE,
                query="workflow"
            )
            self.assertTrue(search_result.get("status", False))
            
            # Delete note
            delete_result = self.notes_api.delete_note(
                note_id=note_id,
                user=self.REAL_USER_ALICE
            )
            self.assertTrue(delete_result.get("status", False))

    def test_create_share_reminder_flow(self):
        """Test the flow of creating, sharing, and adding reminder to a note."""
        # Create note
        create_result = self.notes_api.create_note(
            user=self.REAL_USER_ALICE,
            title="Shared Reminder Note",
            content="Shared note with reminder"
        )
        if create_result.get("status"):
            note_id = create_result["note"]["id"]
            
            # Share with Bob
            share_result = self.notes_api.share_note(
                note_id=note_id,
                user=self.REAL_USER_ALICE,
                share_with_alias=self.REAL_USER_BOB
            )
            self.assertTrue(share_result.get("status", False))
            
            # Add reminder
            reminder_result = self.notes_api.add_reminder(
                note_id=note_id,
                user=self.REAL_USER_ALICE,
                reminder_timestamp="2024-12-31 10:00:00"
            )
            self.assertTrue(reminder_result.get("status", False))

    # --- Data Reset Tests ---
    def test_reset_data_success(self):
        """Test resetting data successfully."""
        result = self.notes_api.reset_data()
        self.assertTrue(result.get("reset_status", False))

if __name__ == "__main__":
    unittest.main()
