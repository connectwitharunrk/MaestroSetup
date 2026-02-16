# Converting Maestro JSON Report to Allure Report

## Question

How to convert this maestro json report to allure report?

### Maestro JSON Sample

```json
[ {
  "command" : {
    "tapOnElement" : {
      "selector" : {
        "textRegex" : "Title",
        "optional" : false
      },
      "retryIfNoChange" : false,
      "waitUntilVisible" : false,
      "longPress" : false,
      "optional" : false
    }
  },
  "metadata" : {
    "status" : "COMPLETED",
    "timestamp" : 1771239155589,
    "duration" : 3822
  }
}, {
  "command" : {
    "launchAppCommand" : {
      "appId" : "com.arunrk.newnotes",
      "clearState" : true,
      "optional" : false
    }
  },
  "metadata" : {
    "status" : "COMPLETED",
    "timestamp" : 1771239148656,
    "duration" : 2228
  }
}, {
  "command" : {
    "tapOnElement" : {
      "selector" : {
        "textRegex" : "Save",
        "optional" : false
      },
      "retryIfNoChange" : false,
      "waitUntilVisible" : false,
      "longPress" : false,
      "optional" : false
    }
  },
  "metadata" : {
    "status" : "COMPLETED",
    "timestamp" : 1771239170005,
    "duration" : 4485
  }
}, {
  "command" : {
    "inputTextCommand" : {
      "text" : "New Descriptiopn",
      "optional" : false
    }
  },
  "metadata" : {
    "status" : "COMPLETED",
    "timestamp" : 1771239165733,
    "duration" : 4269
  }
}, {
  "command" : {
    "tapOnElement" : {
      "selector" : {
        "textRegex" : "Description",
        "optional" : false
      },
      "retryIfNoChange" : false,
      "waitUntilVisible" : false,
      "longPress" : false,
      "optional" : false
    }
  },
  "metadata" : {
    "status" : "COMPLETED",
    "timestamp" : 1771239161670,
    "duration" : 4063
  }
}, {
  "command" : {
    "defineVariablesCommand" : {
      "env" : {
        "MAESTRO_FILENAME" : "launch_app"
      },
      "optional" : false
    }
  },
  "metadata" : {
    "status" : "COMPLETED",
    "timestamp" : 1771239148631,
    "duration" : 16
  }
}, {
  "command" : {
    "tapOnElement" : {
      "selector" : {
        "textRegex" : "Add Note",
        "optional" : false
      },
      "retryIfNoChange" : false,
      "waitUntilVisible" : false,
      "longPress" : false,
      "optional" : false
    }
  },
  "metadata" : {
    "status" : "COMPLETED",
    "timestamp" : 1771239150890,
    "duration" : 4697
  }
}, {
  "command" : {
    "applyConfigurationCommand" : {
      "config" : {
        "appId" : "com.arunrk.newnotes"
      },
      "optional" : false
    }
  },
  "metadata" : {
    "status" : "COMPLETED",
    "timestamp" : 1771239148652,
    "duration" : 2
  }
}, {
  "command" : {
    "inputTextCommand" : {
      "text" : "Arun",
      "optional" : false
    }
  },
  "metadata" : {
    "status" : "COMPLETED",
    "timestamp" : 1771239159412,
    "duration" : 2257
  }
} ]
```

---

## Solution

To convert Maestro JSON test results to Allure reports, you'll need to create a custom parser since Maestro doesn't have built-in Allure support. Here's how to do it:

### Solution Overview

1. **Parse the Maestro JSON** output
2. **Convert to Allure JSON format**
3. **Generate Allure report**

### Implementation

Here's a Python script to convert your Maestro results:

```python
import json
import uuid
from datetime import datetime

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
    convert_maestro_to_allure("maestro_report.json", "allure-results")
    print("\nTo generate Allure report, run:")
    print("allure serve allure-results")
```

### Steps to Use

1. **Save your Maestro JSON** to a file (e.g., `maestro_report.json`)

2. **Install Allure commandline**:
```bash
# macOS
brew install allure

# Or download from https://github.com/allure-framework/allure2/releases
```

3. **Run the conversion script**:
```bash
python convert_maestro_to_allure.py
```

4. **Generate and view the report**:
```bash
allure serve allure-results
```

### Alternative: GitHub Actions Integration

If you're using CI/CD, you can automate this:

```yaml
- name: Run Maestro Tests
  run: maestro test flow.yaml --format json > maestro-report.json

- name: Convert to Allure
  run: python convert_maestro_to_allure.py

- name: Publish Allure Report
  uses: simple-elf/allure-report-action@master
  if: always()
  with:
    allure_results: allure-results
```

This will give you a proper Allure report with your Maestro test results visualized!

---

*Conversation exported on February 16, 2026*
