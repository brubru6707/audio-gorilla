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


def display_menu():
    """Display the main menu."""
    print("\n" + "="*60)
    print("Backend Update Tool")
    print("="*60)
    print("1. Update specific sections of a backend")
    print("2. Replace entire backend")
    print("3. Replace all backends")
    print("4. List available backends")
    print("5. View sections in a backend")
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


def main():
    """Main program loop."""
    print("Backend Update Tool - Interactive Mode")
    
    while True:
        display_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            update_specific_sections()
        elif choice == '2':
            replace_entire_backend()
        elif choice == '3':
            replace_all_backends()
        elif choice == '4':
            list_backends()
        elif choice == '5':
            view_backend_sections()
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
