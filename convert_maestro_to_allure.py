import json
import uuid
import argparse

def convert_maestro_to_allure(maestro_json_path, output_dir="allure-results"):
    """Convert Maestro JSON report to Allure format"""
    
    # Read Maestro JSON
    with open(maestro_json_path, 'r') as f:
        maestro_data = json.load(f)
    
    # Create Allure result structure
    allure_result = {
        "uuid": str(uuid.uuid4()),
        "historyId": str(uuid.uuid4()),
        "fullName": "Maestro Test Flow",
        "labels": [
            {"name": "suite", "value": "Maestro Mobile Tests"},
            {"name": "framework", "value": "maestro"},
            {"name": "language", "value": "yaml"}
        ],
        "links": [],
        "name": maestro_data[0].get("command", {}).get("defineVariablesCommand", {}).get("env", {}).get("MAESTRO_FILENAME", "maestro_test"),
        "status": "passed",
        "statusDetails": {},
        "stage": "finished",
        "steps": [],
        "attachments": [],
        "parameters": [],
        "start": min(cmd["metadata"]["timestamp"] for cmd in maestro_data),
        "stop": max(cmd["metadata"]["timestamp"] + cmd["metadata"]["duration"] for cmd in maestro_data)
    }
    
    # Convert each command to a step
    for idx, command_data in enumerate(maestro_data):
        command = command_data.get("command", {})
        metadata = command_data.get("metadata", {})
        
        # Determine command type and name
        command_type = list(command.keys())[0] if command else "unknown"
        step_name = get_step_name(command, command_type)
        
        step = {
            "name": step_name,
            "status": "passed" if metadata.get("status") == "COMPLETED" else "failed",
            "stage": "finished",
            "steps": [],
            "attachments": [],
            "parameters": get_step_parameters(command, command_type),
            "start": metadata.get("timestamp", 0),
            "stop": metadata.get("timestamp", 0) + metadata.get("duration", 0)
        }
        
        allure_result["steps"].append(step)
    
    # Check if any step failed
    if any(step["status"] == "failed" for step in allure_result["steps"]):
        allure_result["status"] = "failed"
    
    # Write Allure result file
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    result_filename = f"{allure_result['uuid']}-result.json"
    result_path = os.path.join(output_dir, result_filename)
    
    with open(result_path, 'w') as f:
        json.dump(allure_result, f, indent=2)
    
    print(f"✓ Allure result created: {result_path}")
    return result_path

def get_step_name(command, command_type):
    """Generate readable step name from command"""
    if command_type == "tapOnElement":
        text = command[command_type].get("selector", {}).get("textRegex", "element")
        return f"Tap on '{text}'"
    elif command_type == "inputTextCommand":
        text = command[command_type].get("text", "")
        return f"Input text: '{text}'"
    elif command_type == "launchAppCommand":
        app_id = command[command_type].get("appId", "app")
        return f"Launch app: {app_id}"
    elif command_type == "defineVariablesCommand":
        return "Define variables"
    elif command_type == "applyConfigurationCommand":
        return "Apply configuration"
    else:
        return command_type

def get_step_parameters(command, command_type):
    """Extract parameters from command"""
    params = []
    
    if command_type == "tapOnElement":
        selector = command[command_type].get("selector", {})
        if "textRegex" in selector:
            params.append({"name": "selector", "value": selector["textRegex"]})
    elif command_type == "inputTextCommand":
        params.append({"name": "text", "value": command[command_type].get("text", "")})
    elif command_type == "launchAppCommand":
        params.append({"name": "appId", "value": command[command_type].get("appId", "")})
        params.append({"name": "clearState", "value": str(command[command_type].get("clearState", False))})
    
    return params

# Usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert Maestro JSON report to Allure format',
        epilog='Example: python convert_maestro_to_allure.py maestro_report.json -o my-results'
    )
    
    parser.add_argument('input_file', 
                        help='Path to Maestro JSON report file')
    
    parser.add_argument('-o', '--output-dir', 
                        default='allure-results', 
                        help='Output directory for Allure results (default: allure-results)')
    
    parser.add_argument('-v', '--verbose', 
                        action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Input file: {args.input_file}")
        print(f"Output directory: {args.output_dir}")
    
    try:
        convert_maestro_to_allure(args.input_file, args.output_dir)
        print(f"\n✓ Conversion successful!")
        print(f"\nTo generate Allure report, run:")
        print(f"  allure serve {args.output_dir}")
    except FileNotFoundError:
        print(f"❌ Error: File '{args.input_file}' not found")
        exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in '{args.input_file}'")
        exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        exit(1)
