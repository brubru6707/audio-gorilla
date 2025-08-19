import anthropic
import json
import os
import sys
import random
from dotenv import load_dotenv

import os

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def get_random_api_name():
    api_names = [
        "Amazon",
        "Venmo",
        "CommuniLink",
        "Gmail",
        "GoogleCalendar",
        "GoogleDrive",
        "SimpleNote",
        "SmartThings",
        "Spotify",
        "TeslaFleet",
        "X",
        "YouTube"
    ]
    return random.choice(api_names)

# def get_api_definition(api_name):
#     api_name = api_name.lower()
#     api_definitions = load_all_api_definitions()
#     return api_definitions.get(api_name, None)

def get_other_context_info(api_name):
    api_name = api_name.lower()
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Backends', f"diverse_{api_name}_state.json"))
    
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    context_info = {}
    
    excluded_keys = [
        'comments', 
        'direct_messages', 
        'notifications', 
        'transactions', 
        'service_plans', 
        'promotions'
    ]
    
    for key in data.keys():
        if key not in excluded_keys and isinstance(data[key], (dict, list)):
            samples = []
            if isinstance(data[key], dict):
                sample_keys = random.sample(list(data[key].keys()), min(3, len(data[key])))
                samples = [data[key][k] for k in sample_keys]
            elif isinstance(data[key], list):
                samples = random.sample(data[key], min(3, len(data[key])))
            context_info[key] = samples
            
    return context_info

def load_all_api_definitions():
    api_definitions = {}
    prompts_dir = os.path.abspath(os.path.dirname(__file__))
    for filename in os.listdir(prompts_dir):
        if filename.startswith('all_') and filename.endswith('_definitions.json'):
            with open(filename, 'r') as f:
                data = json.load(f)
                api_definitions[data['api_name']] = data
    return api_definitions

def generate_training_data():
    client = anthropic.Anthropic(
        api_key = os.getenv("ANTHROPIC_API_KEY")
    )
    
    api_definitions = load_all_api_definitions()
    api_names = list(api_definitions.keys())
    random_api_name = random.choice(api_names)
    random_api_definition = api_definitions[random_api_name]

    type_mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "dict": "object",
        "NoneType": "null"
    }

    all_tools = []
    for func in random_api_definition['functions']:
        tool_schema = {
            "name": f"{random_api_name}.{func['function_name']}",
            "description": func['description'],
            "input_schema": {
                "type": "object",
                "properties": {
                    param['name']: {
                        "type": type_mapping.get(param['type'], "string")
                    } for param in func['parameters']
                },
                "required": [param['name'] for param in func['parameters']]
            }
        }
        all_tools.append(tool_schema)
            
    system_prompt = (
        "You are a helpful assistant whose sole purpose is to generate high-quality training data for a function-calling model. "
        "You will be provided with a list of available tools and will perform the following steps: "
        "1. Invent a user prompt that is a realistic and natural request for a human and take inpsiration from the context information."
        "2. Based on the user's prompt, generate a structured ground truth that uses the available tools to fulfill the request. "
        "3. Ensure the ground truth includes valid parameter values, which you can invent based on the context of the prompt. "
        "4. Output the complete training data entry as a single JSON object. "
        "The final JSON object must contain 'prompt', 'tools', 'context', and 'ground_truth' fields as shown in the example. "
        "Your response MUST start with the JSON object and contain no other text before or after it."
    )

    example_output = {
        "prompt": "Order a new 1080P HD with Android TV from Amazon",
        "tools": ["AmazonApis"],
        "context": {
            "amazon_current_user": "15ca4c07-750a-476f-92c3-bd882642fb06"
        },
        "ground_truth": {
            "Amazon": [
                "search_products(query: '1080P HD with Android TV')", 
                "order_product(user: '15ca4c07-750a-40f6-a750-b9d18ab50b63', productId: '4ee8cb6d-aa52-40f6-a750-b9d18ab50b63', quantity: 1)"
            ]
        }
    }

    user_message = (
        "Generate one complete training data entry. The final output must be a single JSON object. "
        "Here are the available tools: "
        f"{json.dumps(all_tools, indent=2)}\n\n"
        "Here is an example of the desired output format:\n"
        f"{json.dumps(example_output, indent=2)}"
    )

    extra_context = get_other_context_info(random_api_name)

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        raw_output = response.content[0].text
        
        try:
            generated_data = json.loads(raw_output)
            
            for tool_name, calls in generated_data.get('ground_truth', {}).items():
                backend_file_name = f"diverse_{tool_name.lower().replace('apis', '')}_state.json"
                backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Backends', backend_file_name))
                user_id = "23423432" #get_random_user_id(backend_path)
                
                if user_id:
                    generated_data['context'][f"{tool_name.lower().replace('apis', '')}_current_user"] = user_id
                    
                    new_calls = []
                    for call_dict in calls:
                        if isinstance(call_dict, dict) and 'user' in call_dict.get('args', {}):
                             call_dict['args']['user'] = user_id
                        new_calls.append(call_dict)
                    generated_data['ground_truth'][tool_name] = new_calls

            return generated_data
        
        except json.JSONDecodeError:
            print(f"Error: AI response was not a valid JSON object. Raw response:\n{raw_output}")
            return None

    except anthropic.APIError as e:
        print(f"An API error occurred: {e}")
        return None

if __name__ == '__main__':
    training_data_entry = generate_training_data()
    if training_data_entry:
        print(json.dumps(training_data_entry, indent=4))
    else:
        print("Failed to generate training data.")