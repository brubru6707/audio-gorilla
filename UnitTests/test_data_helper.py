import json
import os
from pathlib import Path
import sys

class BackendDataLoader:
    """Utility class to load realistic data from backend JSON files."""
    
    @staticmethod
    def get_backend_dir():
        """Get the path to the Backends directory."""
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        return parent_dir / 'Backends'
    
    @staticmethod
    def load_json_data(backend_name):
        """Load data from the specified backend JSON file.
        
        Args:
            backend_name (str): The name of the backend (e.g., 'amazon', 'gmail')
            
        Returns:
            dict: The loaded JSON data or empty dict if file not found
        """
        backend_dir = BackendDataLoader.get_backend_dir()
        json_file = backend_dir / f'diverse_{backend_name}_state.json'
        
        try:
            with open(json_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load data from {json_file}. Error: {e}")
            return {}
    
    @staticmethod
    def load_or_get_default_state(backend_module, json_name):
        """Load JSON data or fall back to DEFAULT_STATE from the backend module.
        
        Args:
            backend_module (str): The name of the backend module (e.g., 'createAmazonBackend')
            json_name (str): The name of the JSON file without 'diverse_' prefix and '.json' suffix
            
        Returns:
            dict: The loaded data or DEFAULT_STATE if available
        """
        # Try to load the JSON data first
        data = BackendDataLoader.load_json_data(json_name)
        if data:
            return data
            
        # If JSON data is empty, try to get DEFAULT_STATE from the module
        try:
            # Import the module dynamically
            sys.path.insert(0, str(BackendDataLoader.get_backend_dir().parent))
            module = __import__(f"Backends.{backend_module}", fromlist=['DEFAULT_STATE'])
            if hasattr(module, 'DEFAULT_STATE'):
                print(f"Using DEFAULT_STATE from {backend_module}")
                return module.DEFAULT_STATE
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not load DEFAULT_STATE from {backend_module}. Error: {e}")
        
        # Return empty dict if all else fails
        return {}
    
    # Update all the getter methods to use the new load_or_get_default_state method
    
    @classmethod
    def get_amazon_data(cls):
        """Get realistic data for Amazon tests."""
        return cls.load_or_get_default_state('createAmazonBackend', 'amazon')
    
    @classmethod
    def get_communi_link_data(cls):
        """Get realistic data for CommuniLink tests."""
        return cls.load_or_get_default_state('createCommuniLinkBackend', 'communi_link')
    
    @classmethod
    def get_gmail_data(cls):
        """Get realistic data for Gmail tests."""
        return cls.load_or_get_default_state('createGmailBackend', 'gmail')
    
    @classmethod
    def get_google_calendar_data(cls):
        """Get realistic data for Google Calendar tests."""
        return cls.load_or_get_default_state('createGoogleCalendarBackend', 'google_calendar')
    
    @classmethod
    def get_googledrive_data(cls):
        """Get realistic data for Google Drive tests."""
        return cls.load_or_get_default_state('createGoogleDriveBackend', 'googledrive')
    
    @classmethod
    def get_simple_notes_data(cls):
        """Get realistic data for Simple Notes tests."""
        return cls.load_or_get_default_state('createSimpleNotesBackend', 'simple_notes')
    
    @classmethod
    def get_smart_things_data(cls):
        """Get realistic data for Smart Things tests."""
        return cls.load_or_get_default_state('createSmartThingsBackend', 'smart_things')
    
    @classmethod
    def get_spotify_data(cls):
        """Get realistic data for Spotify tests."""
        return cls.load_or_get_default_state('createSpotifyBackends', 'spotify')
    
    @classmethod
    def get_teslafleet_data(cls):
        """Get realistic data for Tesla Fleet tests."""
        return cls.load_or_get_default_state('createTeslaBackend', 'teslafleet')
    
    @classmethod
    def get_venmo_data(cls):
        """Get realistic data for Venmo tests."""
        return cls.load_or_get_default_state('createVenmoBackend', 'venmo')
    
    @classmethod
    def get_x_data(cls):
        """Get realistic data for X tests."""
        return cls.load_or_get_default_state('createXBackend', 'x')
    
    @classmethod
    def get_youtube_data(cls):
        """Get realistic data for YouTube tests."""
        return cls.load_or_get_default_state('createYouTubeBackend', 'youtube')