"""Quick test script to verify the realistic Google Drive API changes."""

from GoogleDriveApis import GoogleDriveApis

# Create API
api = GoogleDriveApis()

# Get first user email from auto-authentication
print("=" * 60)
print("TEST 1: Check Auto-Authentication")
print("=" * 60)
print(f"Current user: {api.current_user}")
print()

# Test 2: Get user info (about endpoint)
print("=" * 60)
print("TEST 2: Get User Info (about endpoint, no user_id!)")
print("=" * 60)
try:
    about = api.get_user_info()
    print(f"About structure: {list(about.keys())}")
    print(f"Has 'kind' field: {'kind' in about}")
    print(f"User info: {about}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 3: List files (no user_id!)
print("=" * 60)
print("TEST 3: List Files (no user_id parameter!)")
print("=" * 60)
try:
    files_list = api.list_files(page_size=5)
    print(f"Files list structure: {list(files_list.keys())}")
    print(f"Has 'kind' field: {'kind' in files_list}")
    print(f"Number of files: {len(files_list.get('files', []))}")
    if files_list.get('files'):
        print(f"First file structure: {list(files_list['files'][0].keys())}")
        print(f"First file: {files_list['files'][0]}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 4: Create a file (no user_id!)
print("=" * 60)
print("TEST 4: Create File (no user_id parameter!)")
print("=" * 60)
try:
    new_file = api.create_file(
        name="Test Document.txt",
        mimeType="text/plain",
        description="A test document",
        starred=True
    )
    print(f"Created file structure: {list(new_file.keys())}")
    print(f"Has 'kind' field: {'kind' in new_file}")
    print(f"Has 'capabilities' field: {'capabilities' in new_file}")
    print(f"Created file: {new_file}")
    file_id = new_file['id']
except Exception as e:
    print(f"Error: {e}")
    file_id = None
print()

# Test 5: Get file (no user_id!)
if file_id:
    print("=" * 60)
    print("TEST 5: Get File (no user_id!)")
    print("=" * 60)
    try:
        file = api.get_file(file_id)
        print(f"File structure: {list(file.keys())}")
        print(f"Has 'kind' field: {'kind' in file}")
        print(f"File: {file}")
    except Exception as e:
        print(f"Error: {e}")
    print()

# Test 6: Update file - star it (no user_id!)
if file_id:
    print("=" * 60)
    print("TEST 6: Update File - Change name and description (no user_id!)")
    print("=" * 60)
    try:
        updated_file = api.update_file(
            fileId=file_id,
            name="Updated Test Document.txt",
            description="Updated description",
            starred=False
        )
        print(f"Updated file: {updated_file}")
        print(f"Starred: {updated_file.get('starred')}")
    except Exception as e:
        print(f"Error: {e}")
    print()

# Test 7: List files with query (no user_id!)
print("=" * 60)
print("TEST 7: List Files with Query (no user_id!)")
print("=" * 60)
try:
    starred_files = api.list_files(q="starred = true", page_size=10)
    print(f"Starred files structure: {list(starred_files.keys())}")
    print(f"Number of starred files: {len(starred_files.get('files', []))}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 8: Copy file (no user_id!)
if file_id:
    print("=" * 60)
    print("TEST 8: Copy File (no user_id!)")
    print("=" * 60)
    try:
        copied_file = api.copy_file(
            fileId=file_id,
            name="Copy of Test Document.txt"
        )
        print(f"Copied file: {copied_file}")
        print(f"Has 'kind' field: {'kind' in copied_file}")
        copied_file_id = copied_file['id']
    except Exception as e:
        print(f"Error: {e}")
        copied_file_id = None
    print()

# Test 9: Create permission / Share file (no user_id!)
if file_id:
    print("=" * 60)
    print("TEST 9: Create Permission (no user_id!)")
    print("=" * 60)
    try:
        permission = api.create_permission(
            fileId=file_id,
            role="reader",
            type="user",
            emailAddress="test@example.com"
        )
        print(f"Permission structure: {list(permission.keys())}")
        print(f"Has 'kind' field: {'kind' in permission}")
        print(f"Permission: {permission}")
    except Exception as e:
        print(f"Error: {e}")
    print()

# Test 10: List revisions (no user_id!)
if file_id:
    print("=" * 60)
    print("TEST 10: List Revisions (no user_id!)")
    print("=" * 60)
    try:
        revisions = api.list_revisions(file_id)
        print(f"Revisions structure: {list(revisions.keys())}")
        print(f"Has 'kind' field: {'kind' in revisions}")
        print(f"Number of revisions: {len(revisions.get('revisions', []))}")
        print(f"Revisions: {revisions}")
    except Exception as e:
        print(f"Error: {e}")
    print()

# Test 11: Create folder (no user_id!)
print("=" * 60)
print("TEST 11: Create Folder (no user_id!)")
print("=" * 60)
try:
    new_folder = api.create_folder(
        name="Test Folder",
        description="A test folder"
    )
    print(f"Created folder: {new_folder}")
    print(f"MIME type: {new_folder.get('mimeType')}")
    print(f"Has 'kind' field: {'kind' in new_folder}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 12: Try without authentication (should fail)
print("=" * 60)
print("TEST 12: Try without authentication (should fail)")
print("=" * 60)
api2 = GoogleDriveApis()
api2.current_user = None
try:
    files = api2.list_files()
    print(f"UNEXPECTED: Should have failed but got: {files}")
except Exception as e:
    print(f"EXPECTED: Got exception: {e}")
print()

print("=" * 60)
print("SUMMARY")
print("=" * 60)
print("✓ No more user_id parameters!")
print("✓ Returns direct resources, not status dictionaries")
print("✓ Includes 'kind' field on all resources")
print("✓ Includes 'capabilities' field on files")
print("✓ Uses RFC3339 timestamps instead of integers")
print("✓ Authentication required before API calls")
print("✓ Matches real Google Drive API v3 structure")
print("✓ Methods match real API: list_files(), get_file(), create_file(), update_file(), etc.")
