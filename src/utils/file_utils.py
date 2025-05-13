import os
import json
import glob

def load_json_file(file_path):
    """Load JSON data from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None

def save_json_file(data, file_path):
    """Save JSON data to a file"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def is_invalid_string(value):
    return not isinstance(value, str) or value.strip().lower() in ("", "null")

def is_invalid_list_of_strings(value):
    if not isinstance(value, list) or len(value) == 0:
        return True
    return all(is_invalid_string(item) for item in value)

def validate_request(request):
    return not (
        is_invalid_string(request.get("explanation")) or 
        is_invalid_string(request.get("rule"))
    )

def validate_response(response):
    return not (
        is_invalid_list_of_strings(response.get("suggestions")) or 
        is_invalid_list_of_strings(response.get("originalTexts"))
    )

def get_suggestion_pairs(request_dir="data/suggestion_requests", response_dir="data/suggestion_responses"):
    request_files = glob.glob(os.path.join(request_dir, "*.json"))
    pairs = []

    for req_file in request_files:
        uuid = os.path.splitext(os.path.basename(req_file))[0]
        resp_file = os.path.join(response_dir, f"{uuid}.json")

        if os.path.exists(resp_file):
            request = load_json_file(req_file)
            response = load_json_file(resp_file)

            if not (validate_request(request) and validate_response(response)):
                print(f"Skipping pair (ID: {uuid}): Invalid request or response data")
                continue

            pairs.append({
                "uuid": uuid,
                "request": request,
                "response": response
            })

    return pairs
