import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import inspect
import json
from AmazonApis import AmazonApis
from VenmoApis import VenmoApis
from CommuniLinkApis import CommuniLinkApis
from GmailApis import GmailApis
from GoogleCalendarApis import GoogleCalendarApis
from GoogleDriveApis import GoogleDriveApis
from SimpleNoteApis import SimpleNoteApis
from SmartThingsApis import SmartThingsApis
from SpotifyApis import SpotifyApis
from TeslaFleetApis import TeslaFleetApis
from XApis import XApis
from YouTubeApis import YouTubeApis

def extract_api_info(api_class):
    api_name = api_class.__name__
    functions = []

    
    for name, method in inspect.getmembers(api_class, predicate=inspect.isfunction):
        if not name.startswith('_'):
            signature = inspect.signature(method)
            parameters = []

            
            for param_name, param in signature.parameters.items():
                if param_name != 'self':  
                    param_type = str(param.annotation).replace("<class '", "").replace("'>", "")
                    parameters.append({"name": param_name, "type": param_type})
            
            
            docstring = inspect.getdoc(method)

            functions.append({
                "function_name": name,
                "description": docstring,
                "parameters": parameters,
                "return": str(signature.return_annotation).replace("<class '", "").replace("'>", "")
            })
    
    return {
        "api_name": api_name,
        "functions": functions
    }

api_classes = [
    AmazonApis, 
    VenmoApis, 
    CommuniLinkApis, 
    GmailApis, 
    GoogleCalendarApis, 
    GoogleDriveApis, 
    SimpleNoteApis, 
    SmartThingsApis, 
    SpotifyApis, 
    TeslaFleetApis, 
    XApis, 
    YouTubeApis
] 

for cls in api_classes:
    print(f"Extracting API info for {cls.__name__}...")
    api_data = extract_api_info(cls)
    with open(f'all_{cls.__name__.lower()}_definitions.json', 'w') as f:
        json.dump(api_data, f, indent=4)