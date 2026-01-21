"""
Interactive backend update tool that allows granular control over backend generation.

Usage:
    python updateBackends.py

Features:
    - Update specific sections of a backend (users, products, etc.)
    - Replace entire backend
    - Replace all backends
    - Merge new data with existing data
"""

import subprocess
import sys
import os
import json
from typing import Dict, List, Any, Optional

# Get the current directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Map of backend names to their script and JSON file
BACKENDS = {
    "amazon": {
        "script": "createAmazonBackend.py",
        "state_file": "diverse_amazon_state.json",
        "sections": ["users", "products", "sellers", "product_reviews", "product_questions", "promotions", "customer_service_tickets"]
    },
    "communi_link": {
        "script": "createCommuniLinkBackend.py",
        "state_file": "diverse_communi_link_state.json",
        "sections": []  # Will be detected dynamically
    },
    "gmail": {
        "script": "createGmailBackend.py",
        "state_file": "diverse_gmail_state.json",
        "sections": []
    },
    "google_calendar": {
        "script": "createGoogleCalendarBackend.py",
        "state_file": "diverse_google_calendar_state.json",
        "sections": []
    },
    "google_drive": {
        "script": "createGoogleDriveBackend.py",
        "state_file": "diverse_google_drive_state.json",
        "sections": []
    },
    "simple_notes": {
        "script": "createSimpleNotesBackend.py",
        "state_file": "diverse_simple_notes_state.json",
        "sections": []
    },
    "smart_things": {
        "script": "createSmartThingsBackend.py",
        "state_file": "diverse_smart_things_state.json",
        "sections": []
    },
    "spotify": {
        "script": "createSpotifyBackends.py",
        "state_file": "diverse_spotify_state.json",
        "sections": []
    },
    "tesla": {
        "script": "createTeslaBackend.py",
        "state_file": "diverse_teslafleet_state.json",
        "sections": []
    },
    "venmo": {
        "script": "createVenmoBackend.py",
        "state_file": "diverse_venmo_state.json",
        "sections": []
    },
    "x": {
        "script": "createXBackend.py",
        "state_file": "diverse_x_state.json",
        "sections": []
    },
    "youtube": {
        "script": "createYouTubeBackend.py",
        "state_file": "diverse_youtube_state.json",
        "sections": []
    }
}


def load_state_file(backend_name: str) -> Optional[Dict[str, Any]]:
    """Load existing state file for a backend."""
    state_file_path = os.path.join(current_dir, BACKENDS[backend_name]["state_file"])
    
    if not os.path.exists(state_file_path):
        print(f"Warning: State file '{state_file_path}' does not exist yet.")
        return None
    
    try:
        with open(state_file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON from '{state_file_path}': {e}")
        return None


def save_state_file(backend_name: str, state_data: Dict[str, Any]) -> bool:
    """Save state data to backend's JSON file."""
    state_file_path = os.path.join(current_dir, BACKENDS[backend_name]["state_file"])
    
    try:
        with open(state_file_path, 'w') as f:
            json.dump(state_data, f, indent=2)
        print(f"✓ Saved state to '{state_file_path}'")
        return True
    except Exception as e:
        print(f"Error: Failed to save state to '{state_file_path}': {e}")
        return False


def get_backend_sections(backend_name: str) -> List[str]:
    """Dynamically detect sections from existing state file."""
    if BACKENDS[backend_name]["sections"]:
        return BACKENDS[backend_name]["sections"]
    
    state_data = load_state_file(backend_name)
    if state_data and isinstance(state_data, dict):
        return list(state_data.keys())
    
    return []


def run_backend_script(backend_name: str, temp_file: str = None) -> Optional[Dict[str, Any]]:
    """
    Run a backend generation script and return the generated data.
    If temp_file is provided, the script should save to that file instead.
    """
    script_name = BACKENDS[backend_name]["script"]
    script_path = os.path.join(current_dir, script_name)
    
    if not os.path.exists(script_path):
        print(f"Error: Script '{script_path}' not found.")
        return None
    
    print(f"\n>>> Running {script_name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True,
            cwd=current_dir
        )
        
        if result.stdout:
            print(f"Output: {result.stdout[:200]}...")  # Show first 200 chars
        
        # Load the generated data
        return load_state_file(backend_name)
        
    except subprocess.CalledProcessError as e:
        print(f"Error: Script failed with return code {e.returncode}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return None


def merge_sections(existing_state: Dict[str, Any], new_state: Dict[str, Any], sections_to_update: List[str]) -> Dict[str, Any]:
    """
    Merge specific sections from new_state into existing_state.
    Sections not in sections_to_update are preserved from existing_state.
    """
    merged_state = existing_state.copy()
    
    for section in sections_to_update:
        if section in new_state:
            merged_state[section] = new_state[section]
            print(f"  ✓ Updated section: {section}")
        else:
            print(f"  ! Warning: Section '{section}' not found in new state")
    
    return merged_state


def remap_product_ids(data: Any, id_mapping: Dict[str, str]) -> Any:
    """
    Recursively remap product IDs in data structures (cart, wish_list, orders, etc.)
    from new UUIDs to existing UUIDs using the provided mapping.
    """
    if not id_mapping:
        return data
    
    if isinstance(data, dict):
        remapped = {}
        for key, value in data.items():
            # Check if the key itself is a product ID that needs remapping
            new_key = id_mapping.get(key, key)
            # Recursively remap values
            remapped[new_key] = remap_product_ids(value, id_mapping)
        return remapped
    elif isinstance(data, list):
        # For lists, remap each item
        return [remap_product_ids(item, id_mapping) for item in data]
    elif isinstance(data, str):
        # Check if this string is a product ID that needs remapping
        return id_mapping.get(data, data)
    else:
        # Return primitive values as-is
        return data


def merge_subsections(existing_state: Dict[str, Any], new_state: Dict[str, Any], 
                      section: str, subsections: List[str]) -> Dict[str, Any]:
    """
    Merge specific subsections within a section (e.g., update only 'cart' within all 'users').
    
    Args:
        existing_state: Current state data
        new_state: Newly generated state data
        section: The main section (e.g., 'users')
        subsections: List of subsection keys to update (e.g., ['cart', 'wish_list'])
    
    Returns:
        Updated state with subsections merged
    """
    print(f"\n[DEBUG] Starting merge_subsections for section='{section}', subsections={subsections}")
    merged_state = existing_state.copy()
    
    if section not in existing_state:
        print(f"  ! Warning: Section '{section}' not found in existing state")
        return merged_state
    
    if section not in new_state:
        print(f"  ! Warning: Section '{section}' not found in new state")
        return merged_state
    
    # Check if the section contains entities (dict of dicts)
    if not isinstance(existing_state[section], dict) or not isinstance(new_state[section], dict):
        print(f"  ! Warning: Section '{section}' is not a dictionary of entities")
        return merged_state
    
    print(f"[DEBUG] Existing state has {len(existing_state[section])} entities in '{section}'")
    print(f"[DEBUG] New state has {len(new_state[section])} entities in '{section}'")
    
    # Build ID remapping for products (new UUID -> old UUID by index)
    id_remapping = {}
    if 'products' in existing_state and 'products' in new_state:
        existing_product_ids = list(existing_state['products'].keys())
        new_product_ids = list(new_state['products'].keys())
        for i, new_id in enumerate(new_product_ids):
            if i < len(existing_product_ids):
                id_remapping[new_id] = existing_product_ids[i]
        print(f"[DEBUG] Built product ID remapping: {len(id_remapping)} mappings")
        if id_remapping:
            sample_new = list(id_remapping.keys())[0]
            sample_old = id_remapping[sample_new]
            print(f"[DEBUG] Sample mapping: {sample_new[:8]}... -> {sample_old[:8]}...")
    
    # Get lists of entity IDs
    existing_entity_ids = list(existing_state[section].keys())
    new_entity_ids = list(new_state[section].keys())
    
    print(f"[DEBUG] First existing entity ID: {existing_entity_ids[0][:16]}...")
    print(f"[DEBUG] First new entity ID: {new_entity_ids[0][:16]}...")
    print(f"[DEBUG] Entity IDs match: {existing_entity_ids[0] == new_entity_ids[0]}")
    
    # Update subsections for each entity
    merged_section = {}
    entities_updated = 0
    subsection_changes = 0
    
    # Match entities by position/index since IDs are regenerated
    for i, entity_id in enumerate(existing_entity_ids):
        entity_data = existing_state[section][entity_id]
        
        # Deep copy each entity to avoid modifying the original
        if isinstance(entity_data, dict):
            merged_section[entity_id] = entity_data.copy()
        else:
            merged_section[entity_id] = entity_data
        
        # Get the corresponding new entity by index position
        if i < len(new_entity_ids):
            new_entity_id = new_entity_ids[i]
            new_entity_data = new_state[section][new_entity_id]
            
            # Merge only the specified subsections
            for subsection in subsections:
                if subsection in new_entity_data:
                    old_value = merged_section[entity_id].get(subsection, "NOT_SET")
                    new_value = new_entity_data[subsection]
                    
                    # Remap product IDs in the subsection if needed
                    new_value = remap_product_ids(new_value, id_remapping)
                    
                    merged_section[entity_id][subsection] = new_value
                    
                    # Show first entity's change as example
                    if entities_updated == 0:
                        print(f"[DEBUG] First entity ({entity_id[:8]}...) '{subsection}' changed:")
                        print(f"        OLD: {str(old_value)[:100]}")
                        print(f"        NEW: {str(new_value)[:100]}")
                    
                    subsection_changes += 1
                else:
                    print(f"  ! Warning: Subsection '{subsection}' not found in new entity at index {i}")
            entities_updated += 1
    
    merged_state[section] = merged_section
    print(f"[DEBUG] Total subsection changes made: {subsection_changes}")
    print(f"  ✓ Updated {len(subsections)} subsection(s) in {entities_updated} entities within '{section}'")
    
    return merged_state


def display_menu():
    """Display the main menu."""
    print("\n" + "="*60)
    print("Backend Update Tool")
    print("="*60)
    print("1. Update specific sections of a backend")
    print("2. Update specific subsections within entities")
    print("3. Replace entire backend")
    print("4. Replace all backends")
    print("5. List available backends")
    print("6. View sections in a backend")
    print("7. Add new attribute to entities")
    print("0. Exit")
    print("="*60)


def select_backend() -> Optional[str]:
    """Prompt user to select a backend."""
    print("\nAvailable backends:")
    backend_list = list(BACKENDS.keys())
    
    for i, backend in enumerate(backend_list, 1):
        print(f"{i}. {backend}")
    
    try:
        choice = input("\nSelect backend number (or 0 to cancel): ").strip()
        choice_num = int(choice)
        
        if choice_num == 0:
            return None
        
        if 1 <= choice_num <= len(backend_list):
            return backend_list[choice_num - 1]
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None


def select_sections(backend_name: str) -> Optional[List[str]]:
    """Prompt user to select sections to update."""
    sections = get_backend_sections(backend_name)
    
    if not sections:
        print(f"Could not detect sections for {backend_name}. Backend may not exist yet.")
        return None
    
    print(f"\nAvailable sections in {backend_name}:")
    for i, section in enumerate(sections, 1):
        print(f"{i}. {section}")
    
    print("\nEnter section numbers separated by commas (e.g., '1,3,5')")
    print("Or enter 'all' to update all sections")
    
    choice = input("Selection: ").strip().lower()
    
    if choice == 'all':
        return sections
    
    try:
        indices = [int(x.strip()) for x in choice.split(',')]
        selected = []
        
        for idx in indices:
            if 1 <= idx <= len(sections):
                selected.append(sections[idx - 1])
            else:
                print(f"Warning: Invalid section number {idx}, skipping.")
        
        return selected if selected else None
    except ValueError:
        print("Invalid input. Please enter numbers separated by commas.")
        return None


def update_specific_sections():
    """Update specific sections of a backend."""
    backend = select_backend()
    if not backend:
        return
    
    sections = select_sections(backend)
    if not sections:
        return
    
    print(f"\n>>> Will update the following sections in {backend}:")
    for section in sections:
        print(f"    - {section}")
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Load existing state
    existing_state = load_state_file(backend)
    if existing_state is None:
        print(f"No existing state found. Will create new backend.")
        existing_state = {}
    
    # Generate new state
    new_state = run_backend_script(backend)
    if new_state is None:
        print("Failed to generate new state.")
        return
    
    # Merge sections
    merged_state = merge_sections(existing_state, new_state, sections)
    
    # Save merged state
    if save_state_file(backend, merged_state):
        print(f"\n✓ Successfully updated {len(sections)} section(s) in {backend} backend")
    else:
        print("\n✗ Failed to save updated state")


def replace_entire_backend():
    """Replace an entire backend."""
    backend = select_backend()
    if not backend:
        return
    
    print(f"\n>>> Will REPLACE the entire {backend} backend")
    confirm = input("This will overwrite all existing data. Proceed? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Generate new state (the script already saves it)
    new_state = run_backend_script(backend)
    
    if new_state:
        print(f"\n✓ Successfully replaced {backend} backend")
    else:
        print(f"\n✗ Failed to replace {backend} backend")


def replace_all_backends():
    """Replace all backends."""
    print("\n>>> Will REPLACE ALL backends")
    print("This will regenerate all backend state files.")
    
    confirm = input("Proceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    success_count = 0
    fail_count = 0
    
    for backend in BACKENDS.keys():
        print(f"\n--- Processing {backend} ---")
        new_state = run_backend_script(backend)
        
        if new_state:
            success_count += 1
            print(f"✓ {backend} completed")
        else:
            fail_count += 1
            print(f"✗ {backend} failed")
    
    print("\n" + "="*60)
    print(f"Summary: {success_count} succeeded, {fail_count} failed")
    print("="*60)


def list_backends():
    """List all available backends with their status."""
    print("\n" + "="*60)
    print("Available Backends")
    print("="*60)
    
    for backend_name, info in BACKENDS.items():
        state_file_path = os.path.join(current_dir, info["state_file"])
        exists = "✓" if os.path.exists(state_file_path) else "✗"
        
        print(f"{exists} {backend_name:20} - {info['state_file']}")
    
    print("="*60)


def view_backend_sections():
    """View sections in a backend."""
    backend = select_backend()
    if not backend:
        return
    
    sections = get_backend_sections(backend)
    
    if not sections:
        print(f"No sections found for {backend}. Backend may not exist yet.")
        return
    
    print(f"\n" + "="*60)
    print(f"Sections in {backend} backend:")
    print("="*60)
    
    state = load_state_file(backend)
    for section in sections:
        if state and section in state:
            value = state[section]
            if isinstance(value, dict):
                count = len(value)
                item_type = "items"
            elif isinstance(value, list):
                count = len(value)
                item_type = "items"
            else:
                count = 1
                item_type = "value"
            
            print(f"  - {section:30} ({count} {item_type})")
        else:
            print(f"  - {section}")
    
    print("="*60)


def get_entity_subsections(backend_name: str, section: str) -> Optional[List[str]]:
    """Get subsections available within entities of a section."""
    state = load_state_file(backend_name)
    
    if not state or section not in state:
        return None
    
    section_data = state[section]
    
    # Check if this section contains entities (dict of dicts)
    if not isinstance(section_data, dict):
        return None
    
    # Get subsections from the first entity
    for entity_id, entity_data in section_data.items():
        if isinstance(entity_data, dict):
            return list(entity_data.keys())
        break
    
    return None


def select_subsections(backend_name: str, section: str) -> Optional[List[str]]:
    """Prompt user to select subsections within a section."""
    subsections = get_entity_subsections(backend_name, section)
    
    if not subsections:
        print(f"Could not detect subsections within '{section}' for {backend_name}.")
        return None
    
    print(f"\nAvailable subsections within each entity in '{section}':")
    for i, subsection in enumerate(subsections, 1):
        print(f"{i}. {subsection}")
    
    print("\nEnter subsection numbers separated by commas (e.g., '1,3,5')")
    print("Or enter 'all' to update all subsections (equivalent to updating the entire section)")
    
    choice = input("Selection: ").strip().lower()
    
    if choice == 'all':
        return subsections
    
    try:
        indices = [int(x.strip()) for x in choice.split(',')]
        selected = []
        
        for idx in indices:
            if 1 <= idx <= len(subsections):
                selected.append(subsections[idx - 1])
            else:
                print(f"Warning: Invalid subsection number {idx}, skipping.")
        
        return selected if selected else None
    except ValueError:
        print("Invalid input. Please enter numbers separated by commas.")
        return None


def update_specific_subsections():
    """Update specific subsections within entities of a section."""
    backend = select_backend()
    if not backend:
        return
    
    # First, select the main section
    sections = get_backend_sections(backend)
    if not sections:
        print(f"Could not detect sections for {backend}. Backend may not exist yet.")
        return
    
    print(f"\nAvailable sections in {backend}:")
    for i, section in enumerate(sections, 1):
        print(f"{i}. {section}")
    
    try:
        choice = input("\nSelect section number: ").strip()
        section_idx = int(choice)
        
        if not (1 <= section_idx <= len(sections)):
            print("Invalid selection.")
            return
        
        section = sections[section_idx - 1]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Now select subsections within that section
    subsections = select_subsections(backend, section)
    if not subsections:
        return
    
    print(f"\n>>> Will update the following subsections in '{section}' for all entities in {backend}:")
    for subsection in subsections:
        print(f"    - {subsection}")
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Load existing state and save it (since running the script will overwrite it)
    print("\n[DEBUG] Loading existing state...")
    existing_state = load_state_file(backend)
    if existing_state is None:
        print(f"No existing state found. Cannot update subsections without existing data.")
        return
    
    print(f"[DEBUG] Existing state loaded. Section '{section}' has {len(existing_state.get(section, {}))} entities")
    
    # Sample the first entity's subsection value before
    first_entity_id = list(existing_state[section].keys())[0] if existing_state.get(section) else None
    if first_entity_id:
        old_subsection_value = existing_state[section][first_entity_id].get(subsections[0], "NOT_FOUND")
        print(f"[DEBUG] BEFORE: First entity ({first_entity_id[:8]}...) {subsections[0]} = {str(old_subsection_value)[:100]}")
    
    # Make a deep copy to preserve the original data before the script overwrites it
    import copy
    print("[DEBUG] Creating deep copy of existing state...")
    existing_state_backup = copy.deepcopy(existing_state)
    
    # Generate new state (this will overwrite the JSON file)
    print("[DEBUG] Running backend script (this will overwrite the JSON file)...")
    new_state = run_backend_script(backend)
    if new_state is None:
        print("Failed to generate new state.")
        # Restore the backup
        print("[DEBUG] Restoring backup...")
        save_state_file(backend, existing_state_backup)
        return
    
    print(f"[DEBUG] New state loaded. Section '{section}' has {len(new_state.get(section, {}))} entities")
    
    # Sample the first entity's subsection value in new state
    if first_entity_id and first_entity_id in new_state.get(section, {}):
        new_subsection_value = new_state[section][first_entity_id].get(subsections[0], "NOT_FOUND")
        print(f"[DEBUG] NEW STATE: First entity ({first_entity_id[:8]}...) {subsections[0]} = {str(new_subsection_value)[:100]}")
    
    # Merge subsections using the backed up existing state
    print("[DEBUG] Calling merge_subsections...")
    merged_state = merge_subsections(existing_state_backup, new_state, section, subsections)
    
    # Check the merged result
    if first_entity_id:
        merged_subsection_value = merged_state[section][first_entity_id].get(subsections[0], "NOT_FOUND")
        print(f"[DEBUG] AFTER MERGE: First entity ({first_entity_id[:8]}...) {subsections[0]} = {str(merged_subsection_value)[:100]}")
    
    # Save merged state
    print("[DEBUG] Saving merged state to file...")
    if save_state_file(backend, merged_state):
        print(f"\n✓ Successfully updated {len(subsections)} subsection(s) in '{section}' for {backend} backend")
    else:
        print("\n✗ Failed to save updated state")


def generate_attribute_value(entity_data: Dict[str, Any], attribute_name: str, generation_pattern: str) -> Any:
    """
    Generate a new attribute value based on existing entity data.
    
    Args:
        entity_data: The entity's existing data
        attribute_name: Name of the attribute to generate
        generation_pattern: Pattern for generating the value
            - "first_last_lowercase" : Concatenate first_name and last_name in lowercase
            - "email_prefix" : Extract prefix before @ from email
            - "custom:{field}" : Use value from specified field
            - "uuid" : Generate a new UUID
            - Or any literal string value
    
    Returns:
        Generated attribute value
    """
    if generation_pattern == "first_last_lowercase":
        first = entity_data.get("first_name", "")
        last = entity_data.get("last_name", "")
        return f"{first.lower()}{last.lower()}"
    
    elif generation_pattern == "email_prefix":
        email = entity_data.get("email", "")
        if "@" in email:
            return email.split("@")[0]
        return email
    
    elif generation_pattern.startswith("custom:"):
        field_name = generation_pattern.split(":", 1)[1]
        return entity_data.get(field_name, "")
    
    elif generation_pattern == "uuid":
        import uuid
        return str(uuid.uuid4())
    
    else:
        # Treat as literal value
        return generation_pattern


def add_new_attribute_to_entities():
    """Add a new attribute to all entities in a section."""
    backend = select_backend()
    if not backend:
        return
    
    # Select the section
    sections = get_backend_sections(backend)
    if not sections:
        print(f"Could not detect sections for {backend}. Backend may not exist yet.")
        return
    
    print(f"\nAvailable sections in {backend}:")
    for i, section in enumerate(sections, 1):
        print(f"{i}. {section}")
    
    try:
        choice = input("\nSelect section number: ").strip()
        section_idx = int(choice)
        
        if not (1 <= section_idx <= len(sections)):
            print("Invalid selection.")
            return
        
        section = sections[section_idx - 1]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Get attribute name
    print("\nEnter the name of the new attribute to add:")
    attribute_name = input("Attribute name: ").strip()
    
    if not attribute_name:
        print("Attribute name cannot be empty.")
        return
    
    # Get position where to insert the attribute
    print("\nWhere should the attribute be inserted?")
    print("1. After a specific existing attribute")
    print("2. At the beginning")
    print("3. At the end")
    
    position_choice = input("Choice (1-3): ").strip()
    after_attribute = None
    position = "end"
    
    if position_choice == "1":
        # Show existing attributes from first entity
        state = load_state_file(backend)
        if state and section in state:
            first_entity = next(iter(state[section].values()), None)
            if first_entity and isinstance(first_entity, dict):
                print("\nExisting attributes:")
                attrs = list(first_entity.keys())
                for i, attr in enumerate(attrs, 1):
                    print(f"{i}. {attr}")
                
                try:
                    attr_idx = int(input("\nInsert after attribute number: ").strip())
                    if 1 <= attr_idx <= len(attrs):
                        after_attribute = attrs[attr_idx - 1]
                        position = "after"
                    else:
                        print("Invalid selection. Will insert at end.")
                except ValueError:
                    print("Invalid input. Will insert at end.")
    elif position_choice == "2":
        position = "beginning"
    
    # Get generation pattern
    print("\n" + "="*60)
    print("How should the attribute value be generated?")
    print("="*60)
    print("1. first_last_lowercase - Concatenate first_name + last_name (lowercase)")
    print("2. email_prefix - Extract prefix before @ from email")
    print("3. custom:{field} - Use value from a specific field")
    print("4. uuid - Generate a new UUID for each entity")
    print("5. literal - Use a literal value for all entities")
    print("="*60)
    
    pattern_choice = input("Choice (1-5): ").strip()
    
    if pattern_choice == "1":
        generation_pattern = "first_last_lowercase"
    elif pattern_choice == "2":
        generation_pattern = "email_prefix"
    elif pattern_choice == "3":
        field_name = input("Enter field name to copy: ").strip()
        generation_pattern = f"custom:{field_name}"
    elif pattern_choice == "4":
        generation_pattern = "uuid"
    elif pattern_choice == "5":
        literal_value = input("Enter literal value: ").strip()
        generation_pattern = literal_value
    else:
        print("Invalid choice.")
        return
    
    # Show summary
    print(f"\n>>> Will add attribute '{attribute_name}' to all entities in '{section}'")
    print(f"    Generation pattern: {generation_pattern}")
    print(f"    Position: {position}" + (f" (after '{after_attribute}')" if after_attribute else ""))
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Load existing state
    state = load_state_file(backend)
    if not state or section not in state:
        print(f"Section '{section}' not found in backend.")
        return
    
    # Add attribute to all entities
    entities_updated = 0
    entities_skipped = 0
    
    for entity_id, entity_data in state[section].items():
        if not isinstance(entity_data, dict):
            entities_skipped += 1
            continue
        
        # Check if attribute already exists
        if attribute_name in entity_data:
            print(f"  ! Entity {entity_id[:8]}... already has attribute '{attribute_name}', skipping")
            entities_skipped += 1
            continue
        
        # Generate the attribute value
        attribute_value = generate_attribute_value(entity_data, attribute_name, generation_pattern)
        
        # Insert at the correct position
        if position == "beginning":
            # Create new dict with attribute at beginning
            new_entity_data = {attribute_name: attribute_value}
            new_entity_data.update(entity_data)
            state[section][entity_id] = new_entity_data
        elif position == "after" and after_attribute:
            # Create new dict inserting after specific attribute
            new_entity_data = {}
            for key, value in entity_data.items():
                new_entity_data[key] = value
                if key == after_attribute:
                    new_entity_data[attribute_name] = attribute_value
            
            # If after_attribute wasn't found, add at end
            if attribute_name not in new_entity_data:
                new_entity_data[attribute_name] = attribute_value
            
            state[section][entity_id] = new_entity_data
        else:
            # Add at end (default)
            entity_data[attribute_name] = attribute_value
        
        entities_updated += 1
        
        # Show first 3 as examples
        if entities_updated <= 3:
            print(f"  ✓ {entity_id[:8]}... : {attribute_name} = '{attribute_value}'")
    
    # Save updated state
    if save_state_file(backend, state):
        print(f"\n✓ Successfully added '{attribute_name}' to {entities_updated} entities")
        if entities_skipped > 0:
            print(f"  (Skipped {entities_skipped} entities)")
    else:
        print("\n✗ Failed to save updated state")


def main():
    """Main program loop."""
    print("Backend Update Tool - Interactive Mode")
    
    while True:
        display_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            update_specific_sections()
        elif choice == '2':
            update_specific_subsections()
        elif choice == '3':
            replace_entire_backend()
        elif choice == '4':
            replace_all_backends()
        elif choice == '5':
            list_backends()
        elif choice == '6':
            view_backend_sections()
        elif choice == '7':
            add_new_attribute_to_entities()
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
