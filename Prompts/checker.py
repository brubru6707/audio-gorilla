"""
Ground Truth Validation System for Prompt JSON Files

This script validates all ground_truth entries in JSON files located in:
- Prompts/
- Prompts/Combinations/

It checks:
1. All user IDs exist in the respective backend state files
2. All API method calls are syntactically valid
3. All referenced data (message IDs, order IDs, video IDs, etc.) exist in backends
4. API methods exist in the respective API class files
"""

import json
import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set
from collections import defaultdict

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class GroundTruthValidator:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.prompts_dir = self.base_dir / "Prompts"
        self.backends_dir = self.base_dir / "Backends"
        
        # Load all backend state files
        self.backends = {}
        self.load_backends()
        
        # Load API methods from API files
        self.api_methods = {}
        self.load_api_methods()
        
        # Validation results
        self.errors = []
        self.warnings = []
        self.stats = {
            'files_checked': 0,
            'multistep_entries': 0,
            'multiturn_entries': 0,
            'total_ground_truths': 0,
            'errors': 0,
            'warnings': 0
        }
    
    def load_backends(self):
        """Load all diverse_*_state.json files from Backends directory"""
        print("Loading backend state files...")
        backend_files = list(self.backends_dir.glob("diverse_*_state.json"))
        
        for backend_file in backend_files:
            # Extract service name (e.g., "gmail" from "diverse_gmail_state.json")
            service_name = backend_file.stem.replace("diverse_", "").replace("_state", "")
            # Normalize by removing underscores (smart_things -> smartthings)
            service_name = service_name.replace('_', '')
            
            try:
                with open(backend_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.backends[service_name] = data
                    
                    # Count users (handle both dict and list)
                    users = data.get('users', {})
                    user_count = len(users) if isinstance(users, (dict, list)) else 0
                    print(f"  [OK] Loaded {service_name}: {user_count} users")
            except Exception as e:
                print(f"  [ERROR] Loading {backend_file}: {e}")
    
    def load_api_methods(self):
        """Load all API method names from *Apis.py files"""
        print("\nLoading API methods...")
        api_files = list(self.base_dir.glob("*Apis.py"))
        
        for api_file in api_files:
            # Extract service name (e.g., "Gmail" from "GmailApis.py")
            service_name = api_file.stem.replace("Apis", "")
            
            try:
                with open(api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Find all method definitions (def method_name)
                    methods = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', content)
                    
                    # Filter out private methods and __init__
                    public_methods = [m for m in methods if not m.startswith('_')]
                    
                    self.api_methods[service_name.lower()] = set(public_methods)
                    print(f"  [OK] {service_name}: {len(public_methods)} methods")
            except Exception as e:
                print(f"  [ERROR] Loading {api_file}: {e}")
    
    def parse_function_call(self, call_str: str) -> Tuple[str, List[Any]]:
        """
        Parse a function call string and extract method name and arguments
        Returns: (method_name, arguments_list)
        """
        try:
            # Parse as Python expression
            tree = ast.parse(call_str, mode='eval')
            call = tree.body
            
            if isinstance(call, ast.Call):
                if isinstance(call.func, ast.Name):
                    method_name = call.func.id
                elif isinstance(call.func, ast.Attribute):
                    method_name = call.func.attr
                else:
                    return None, []
                
                # Extract arguments
                args = []
                for arg in call.args:
                    if isinstance(arg, ast.Constant):
                        args.append(arg.value)
                    elif isinstance(arg, ast.Dict):
                        # Handle dict arguments
                        args.append('dict')
                    elif isinstance(arg, ast.List):
                        args.append('list')
                    else:
                        args.append('unknown')
                
                return method_name, args
            
        except Exception as e:
            return None, []
        
        return None, []
    
    def validate_user_id(self, service: str, user_id: str, file_path: str, entry_index: int) -> bool:
        """Check if user_id exists in the backend for the given service"""
        backend_key = service.replace('_', '')  # Convert gmail to gmail, amazon to amazon
        
        if backend_key not in self.backends:
            self.warnings.append(
                f"{file_path} - Entry {entry_index}: No backend found for service '{service}'"
            )
            return False
        
        backend = self.backends[backend_key]
        users = backend.get('users', {})
        
        # Check if user_id exists - users can be dict or list
        if isinstance(users, dict):
            user_exists = user_id in users
        elif isinstance(users, list):
            user_exists = any(u.get('user_id') == user_id if isinstance(u, dict) else False for u in users)
        else:
            user_exists = False
        
        if not user_exists:
            self.errors.append(
                f"{file_path} - Entry {entry_index}: User ID '{user_id}' not found in {service} backend"
            )
            return False
        
        return True
    
    def validate_api_method(self, service: str, method_name: str, file_path: str, entry_index: int) -> bool:
        """Check if API method exists in the service's API file"""
        service_key = service.replace('_', '')  # Normalize service name
        
        if service_key not in self.api_methods:
            self.warnings.append(
                f"{file_path} - Entry {entry_index}: No API methods found for service '{service}'"
            )
            return False
        
        if method_name not in self.api_methods[service_key]:
            self.errors.append(
                f"{file_path} - Entry {entry_index}: Method '{method_name}' not found in {service} API"
            )
            return False
        
        return True
    
    def validate_referenced_data(self, service: str, method_name: str, args: List[Any], 
                                 file_path: str, entry_index: int) -> bool:
        """
        Validate that referenced data (message IDs, video IDs, etc.) exists in backend
        This is a heuristic-based validation
        """
        backend_key = service.replace('_', '')
        
        if backend_key not in self.backends:
            return True  # Skip if no backend
        
        backend = self.backends[backend_key]
        
        # Define patterns for different types of IDs
        # UUID pattern
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        # Gmail message ID pattern (hex)
        gmail_msg_pattern = re.compile(r'^[0-9a-f]{16}$')
        
        # Check specific methods that reference data
        if method_name in ['get_message', 'send_draft'] and len(args) >= 2:
            # Second argument is message/draft ID
            msg_id = args[1]
            if isinstance(msg_id, str) and gmail_msg_pattern.match(msg_id):
                # Find user and check if message exists
                user_id = args[0]
                users = backend.get('users', {})
                
                # Get user from dict or list
                if isinstance(users, dict):
                    user = users.get(user_id)
                elif isinstance(users, list):
                    user = next((u for u in users if isinstance(u, dict) and u.get('user_id') == user_id), None)
                else:
                    user = None
                
                if user and isinstance(user, dict):
                    gmail_data = user.get('gmail_data', {})
                    messages = gmail_data.get('messages', {})
                    drafts = gmail_data.get('drafts', {})
                    
                    # Check if message/draft exists (can be dict or list)
                    if isinstance(messages, dict):
                        msg_exists = msg_id in messages
                    else:
                        msg_exists = any(m.get('id') == msg_id if isinstance(m, dict) else False for m in messages)
                    
                    if isinstance(drafts, dict):
                        draft_exists = msg_id in drafts
                    else:
                        draft_exists = any(d.get('id') == msg_id if isinstance(d, dict) else False for d in drafts)
                    
                    if not msg_exists and not draft_exists:
                        self.warnings.append(
                            f"{file_path} - Entry {entry_index}: Message/Draft ID '{msg_id}' not found for user '{user_id}' in {service}"
                        )
                        return False
        
        elif method_name in ['remove_from_cart', 'add_to_cart'] and len(args) >= 1:
            # First argument is item/product ID
            item_id = args[0]
            if isinstance(item_id, str) and uuid_pattern.match(item_id):
                # Check if item exists in products or cart
                products = backend.get('products', {})
                
                # Handle dict or list of products
                if isinstance(products, dict):
                    item_exists = item_id in products
                elif isinstance(products, list):
                    item_exists = any(p.get('product_id') == item_id if isinstance(p, dict) else False for p in products)
                else:
                    item_exists = False
                
                if not item_exists:
                    self.warnings.append(
                        f"{file_path} - Entry {entry_index}: Product ID '{item_id}' not found in {service} backend"
                    )
                    return False
        
        elif method_name in ['track_package', 'get_order_details'] and len(args) >= 1:
            # First argument is order ID
            order_id = args[0]
            if isinstance(order_id, str) and uuid_pattern.match(order_id):
                # Find all orders across users
                users = backend.get('users', {})
                order_exists = False
                
                # Handle dict or list of users
                user_list = users.values() if isinstance(users, dict) else users
                
                for user in user_list:
                    if not isinstance(user, dict):
                        continue
                    orders = user.get('orders', [])
                    if isinstance(orders, list):
                        if any(o.get('order_id') == order_id if isinstance(o, dict) else False for o in orders):
                            order_exists = True
                            break
                
                if not order_exists:
                    self.warnings.append(
                        f"{file_path} - Entry {entry_index}: Order ID '{order_id}' not found in {service} backend"
                    )
                    return False
        
        elif method_name in ['rate_video', 'add_comment_to_video', 'add_to_watch_later'] and len(args) >= 1:
            # Check video ID (could be in different positions)
            video_id_pos = 0 if method_name != 'add_to_watch_later' else 1
            
            if len(args) > video_id_pos:
                video_id = args[video_id_pos]
                if isinstance(video_id, str) and uuid_pattern.match(video_id):
                    video_exists = False
                    
                    # Check in users' video-related arrays (watch_history, liked_videos, etc.)
                    users = backend.get('users', {})
                    user_list = users.values() if isinstance(users, dict) else users
                    
                    for user in user_list:
                        if not isinstance(user, dict):
                            continue
                        # Check in watch_history, liked_videos, watch_later_playlist
                        for field in ['watch_history', 'liked_videos', 'watch_later_playlist']:
                            video_list = user.get(field, [])
                            if isinstance(video_list, list) and video_id in video_list:
                                video_exists = True
                                break
                        if video_exists:
                            break
                    
                    # Also check in channels section (root level)
                    if not video_exists:
                        channels = backend.get('channels', {})
                        channel_list = channels.values() if isinstance(channels, dict) else channels
                        
                        for channel in channel_list:
                            if not isinstance(channel, dict):
                                continue
                            videos = channel.get('videos', [])
                            if isinstance(videos, list) and video_id in videos:
                                video_exists = True
                                break
                    
                    if not video_exists:
                        self.warnings.append(
                            f"{file_path} - Entry {entry_index}: Video ID '{video_id}' not found in {service} backend"
                        )
                        return False
        
        elif method_name == 'subscribe' and len(args) >= 1:
            # First argument is channel ID
            channel_id = args[0]
            if isinstance(channel_id, str) and uuid_pattern.match(channel_id):
                channel_exists = False
                
                # Check in users' channels array (just IDs)
                users = backend.get('users', {})
                user_list = users.values() if isinstance(users, dict) else users
                
                for user in user_list:
                    if not isinstance(user, dict):
                        continue
                    channels = user.get('channels', [])
                    if isinstance(channels, list) and channel_id in channels:
                        channel_exists = True
                        break
                    
                    # Also check subscriptions
                    subscriptions = user.get('subscriptions', [])
                    if isinstance(subscriptions, list) and channel_id in subscriptions:
                        channel_exists = True
                        break
                
                # Also check root-level channels section
                if not channel_exists:
                    channels = backend.get('channels', {})
                    if isinstance(channels, dict):
                        channel_exists = channel_id in channels
                    elif isinstance(channels, list):
                        channel_exists = any(c.get('id') == channel_id if isinstance(c, dict) else False for c in channels)
                
                if not channel_exists:
                    self.warnings.append(
                        f"{file_path} - Entry {entry_index}: Channel ID '{channel_id}' not found in {service} backend"
                    )
                    return False
        
        return True
    
    def validate_ground_truth_entry(self, ground_truth: Any, file_path: str, entry_index: int, 
                                   context: Dict = None) -> bool:
        """Validate a single ground_truth entry (can be dict or list)"""
        valid = True
        
        if isinstance(ground_truth, dict):
            # Dictionary format: service -> list of calls
            for service, calls in ground_truth.items():
                if not isinstance(calls, list):
                    continue
                
                for call_str in calls:
                    if not isinstance(call_str, str):
                        continue
                    
                    # Parse the function call
                    method_name, args = self.parse_function_call(call_str)
                    
                    if method_name is None:
                        self.errors.append(
                            f"{file_path} - Entry {entry_index}: Invalid function call syntax: '{call_str}'"
                        )
                        valid = False
                        continue
                    
                    # Validate API method exists
                    if not self.validate_api_method(service, method_name, file_path, entry_index):
                        valid = False
                    
                    # Validate user IDs if get_user_by_id
                    if method_name == 'get_user_by_id' and len(args) >= 1:
                        user_id = args[0]
                        if not self.validate_user_id(service, user_id, file_path, entry_index):
                            valid = False
                    
                    # Validate referenced data
                    if not self.validate_referenced_data(service, method_name, args, file_path, entry_index):
                        valid = False
        
        elif isinstance(ground_truth, list):
            # List format: just list of calls (need to infer service from context)
            for call_str in ground_truth:
                if not isinstance(call_str, str):
                    continue
                
                method_name, args = self.parse_function_call(call_str)
                
                if method_name is None:
                    self.errors.append(
                        f"{file_path} - Entry {entry_index}: Invalid function call syntax: '{call_str}'"
                    )
                    valid = False
        
        return valid
    
    def validate_json_file(self, json_path: Path) -> bool:
        """Validate a single JSON file"""
        print(f"\n{'='*80}")
        print(f"Validating: {json_path.relative_to(self.prompts_dir.parent)}")
        print(f"{'='*80}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.errors.append(f"{json_path}: Failed to load JSON - {e}")
            return False
        
        self.stats['files_checked'] += 1
        file_valid = True
        
        # Validate multistep entries
        if 'multistep' in data:
            for idx, entry in enumerate(data['multistep'], 1):
                self.stats['multistep_entries'] += 1
                
                # Validate context user IDs
                if 'context' in entry:
                    for service, service_data in entry['context'].items():
                        if isinstance(service_data, dict) and 'user_id' in service_data:
                            user_id = service_data['user_id']
                            if not self.validate_user_id(service, user_id, str(json_path), idx):
                                file_valid = False
                
                # Validate ground_truth
                if 'ground_truth' in entry:
                    self.stats['total_ground_truths'] += 1
                    if not self.validate_ground_truth_entry(entry['ground_truth'], str(json_path), idx, entry.get('context')):
                        file_valid = False
        
        # Validate multiturn entries
        if 'multiturn' in data:
            for idx, entry in enumerate(data['multiturn'], 1):
                self.stats['multiturn_entries'] += 1
                
                # Validate context user IDs
                if 'context' in entry:
                    # Could be user_id directly or service -> user_id dict
                    if isinstance(entry['context'], dict):
                        if 'user_id' in entry['context']:
                            # Single user_id format - need to check all relevant services
                            pass
                        else:
                            # Service-based format
                            for service, service_data in entry['context'].items():
                                if isinstance(service_data, dict) and 'user_id' in service_data:
                                    user_id = service_data['user_id']
                                    if not self.validate_user_id(service, user_id, str(json_path), idx):
                                        file_valid = False
                
                # Validate turn-level ground_truth
                if 'turns' in entry:
                    for turn_idx, turn in enumerate(entry['turns'], 1):
                        if 'ground_truth' in turn:
                            self.stats['total_ground_truths'] += 1
                            if not self.validate_ground_truth_entry(turn['ground_truth'], str(json_path), 
                                                                   f"{idx}.{turn_idx}", entry.get('context')):
                                file_valid = False
                
                # Validate entry-level ground_truth
                if 'ground_truth' in entry:
                    self.stats['total_ground_truths'] += 1
                    if not self.validate_ground_truth_entry(entry['ground_truth'], str(json_path), idx, entry.get('context')):
                        file_valid = False
        
        return file_valid
    
    def validate_all(self):
        """Validate all JSON files in Prompts and Prompts/Combinations directories"""
        print("\n" + "="*80)
        print("GROUND TRUTH VALIDATION SYSTEM")
        print("="*80)
        
        # Find all JSON files
        json_files = []
        
        # Prompts directory (non-recursive, skip Combinations)
        for json_file in self.prompts_dir.glob("*.json"):
            json_files.append(json_file)
        
        # Prompts/Combinations directory
        combinations_dir = self.prompts_dir / "Combinations"
        if combinations_dir.exists():
            for json_file in combinations_dir.glob("*.json"):
                json_files.append(json_file)
        
        print(f"\nFound {len(json_files)} JSON files to validate")
        
        # Validate each file
        all_valid = True
        for json_file in json_files:
            if not self.validate_json_file(json_file):
                all_valid = False
        
        # Print summary
        self.print_summary()
        
        return all_valid
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        
        print(f"\nFiles checked: {self.stats['files_checked']}")
        print(f"Multistep entries: {self.stats['multistep_entries']}")
        print(f"Multiturn entries: {self.stats['multiturn_entries']}")
        print(f"Total ground_truth validations: {self.stats['total_ground_truths']}")
        
        print(f"\n{'='*80}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"{'='*80}")
        
        if self.errors:
            print("\n[ERRORS]:")
            for error in self.errors[:50]:  # Limit to first 50
                print(f"  • {error}")
            if len(self.errors) > 50:
                print(f"  ... and {len(self.errors) - 50} more errors")
        
        if self.warnings:
            print("\n[WARNINGS]:")
            for warning in self.warnings[:50]:  # Limit to first 50
                print(f"  • {warning}")
            if len(self.warnings) > 50:
                print(f"  ... and {len(self.warnings) - 50} more warnings")
        
        if not self.errors and not self.warnings:
            print("\n[SUCCESS] All validations passed!")
        elif not self.errors:
            print("\n[SUCCESS] No critical errors found (only warnings)")
        else:
            print("\n[FAILED] Validation failed - please fix errors above")


def main():
    # Get the base directory (parent of Prompts)
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    
    # Create validator and run
    validator = GroundTruthValidator(str(base_dir))
    validator.validate_all()


if __name__ == "__main__":
    main()
    