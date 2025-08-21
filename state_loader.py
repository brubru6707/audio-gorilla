import json
import os
import re
from typing import Dict, Any

def _camel_to_snake_case(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def load_default_state(file_name_without_extension: str) -> Dict[str, Any]:
    if file_name_without_extension.endswith("Apis"):
        camel_case_service_name = file_name_without_extension[:-4]
    else:
        print(f"Error: The provided file name '{file_name_without_extension}' does not end with 'Apis'.")

    derived_api_name_for_json = _camel_to_snake_case(camel_case_service_name)
    current_loader_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_name = f"diverse_{derived_api_name_for_json}_state.json"
    json_file_path = os.path.join(current_loader_dir, 'Backends', json_file_name)

    loaded_state: Dict[str, Any] = {}

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            loaded_state = json.load(f)
        print(f"Successfully loaded default state for {derived_api_name_for_json} from: {json_file_path}")
    except FileNotFoundError:
        print(f"Error: Default state file not found for {derived_api_name_for_json} at {json_file_path}. Using an empty state.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file_path} for {derived_api_name_for_json}. Using an empty state.")
    except Exception as e:
        print(f"An unexpected error occurred while loading state for {derived_api_name_for_json}: {e}")

    return loaded_state