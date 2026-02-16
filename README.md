# Converting Maestro JSON to Allure Report

A complete guide on how to convert Maestro test results to Allure reports.

---

## Question 1: How to run Maestro json into allure report

### Answer

I'll help you generate Allure reports from Maestro test results. Here's how to do it:

#### Overview

Maestro doesn't natively output Allure format, so you'll need to convert Maestro's JSON test results to Allure's format.

#### Steps

**1. Run Maestro tests and generate JSON output**

```bash
maestro test --format json --output maestro-results.json your-flow.yaml
```

**2. Convert Maestro JSON to Allure format**

You'll need to create a converter script. Here's a Python example:

```python
import json
import uuid
from datetime import datetime

def convert_maestro_to_allure(maestro_json_path, allure_results_dir):
    with open(maestro_json_path, 'r') as f:
        maestro_data = json.load(f)
    
    # Create Allure result structure
    for test in maestro_data.get('tests', []):
        test_result = {
            "uuid": str(uuid.uuid4()),
            "historyId": test.get('name', 'unknown'),
            "testCaseId": test.get('name', 'unknown'),
            "name": test.get('name', 'Maestro Test'),
            "status": "passed" if test.get('status') == 'success' else "failed",
            "start": int(datetime.now().timestamp() * 1000),
            "stop": int(datetime.now().timestamp() * 1000),
            "labels": [
                {"name": "suite", "value": "Maestro Tests"}
            ]
        }
        
        # Write to allure-results directory
        result_file = f"{allure_results_dir}/{test_result['uuid']}-result.json"
        with open(result_file, 'w') as f:
            json.dump(test_result, f, indent=2)

# Usage
convert_maestro_to_allure('maestro-results.json', './allure-results')
```

**3. Generate Allure report**

```bash
# Install Allure if you haven't
npm install -g allure-commandline

# Generate report
allure generate allure-results --clean -o allure-report

# Open report
allure open allure-report
```

#### Alternative: Use existing tools

Check if there are community-built converters:
- Look for `maestro-allure-converter` packages on npm/pip
- Check Maestro's GitHub discussions for community solutions

---

## Question 2: Give me the input json for this py script

### Answer

Here's an example Maestro JSON output that the Python script would work with:

```json
{
  "flowsResult": {
    "results": [
      {
        "name": "Login Flow",
        "status": "SUCCESS",
        "duration": 15234,
        "commands": [
          {
            "command": "launchApp",
            "status": "SUCCESS",
            "duration": 2345
          },
          {
            "command": "tapOn",
            "description": "Tap on email field",
            "status": "SUCCESS",
            "duration": 234
          },
          {
            "command": "inputText",
            "description": "Enter email",
            "status": "SUCCESS",
            "duration": 345
          },
          {
            "command": "tapOn",
            "description": "Tap login button",
            "status": "SUCCESS",
            "duration": 456
          }
        ],
        "screenshots": [
          "/path/to/screenshot1.png",
          "/path/to/screenshot2.png"
        ]
      },
      {
        "name": "Add to Cart Flow",
        "status": "FAILED",
        "duration": 8234,
        "error": "Element not found: Add to Cart button",
        "commands": [
          {
            "command": "launchApp",
            "status": "SUCCESS",
            "duration": 2345
          },
          {
            "command": "tapOn",
            "description": "Tap on product",
            "status": "SUCCESS",
            "duration": 234
          },
          {
            "command": "tapOn",
            "description": "Tap add to cart",
            "status": "FAILED",
            "duration": 456,
            "error": "Element not found"
          }
        ],
        "screenshots": [
          "/path/to/screenshot3.png"
        ]
      }
    ],
    "summary": {
      "total": 2,
      "passed": 1,
      "failed": 1,
      "startTime": "2024-02-16T10:30:00Z",
      "endTime": "2024-02-16T10:30:25Z"
    }
  }
}
```

### Improved Python Script

Here's an **improved Python script** that handles this structure better:

```python
import json
import uuid
import os
from datetime import datetime

def convert_maestro_to_allure(maestro_json_path, allure_results_dir):
    # Create allure-results directory if it doesn't exist
    os.makedirs(allure_results_dir, exist_ok=True)
    
    with open(maestro_json_path, 'r') as f:
        maestro_data = json.load(f)
    
    # Get test results
    results = maestro_data.get('flowsResult', {}).get('results', [])
    
    for test in results:
        test_uuid = str(uuid.uuid4())
        
        # Convert status
        status_map = {
            'SUCCESS': 'passed',
            'FAILED': 'failed',
            'SKIPPED': 'skipped'
        }
        status = status_map.get(test.get('status', 'FAILED'), 'broken')
        
        # Calculate timestamps
        duration = test.get('duration', 0)
        stop_time = int(datetime.now().timestamp() * 1000)
        start_time = stop_time - duration
        
        # Build steps from commands
        steps = []
        for idx, cmd in enumerate(test.get('commands', [])):
            step = {
                "name": cmd.get('description', cmd.get('command', 'Step')),
                "status": status_map.get(cmd.get('status', 'SUCCESS'), 'passed'),
                "start": start_time + sum(c.get('duration', 0) for c in test.get('commands', [])[:idx]),
                "stop": start_time + sum(c.get('duration', 0) for c in test.get('commands', [])[:idx+1])
            }
            if cmd.get('error'):
                step['statusDetails'] = {
                    "message": cmd.get('error')
                }
            steps.append(step)
        
        # Create Allure result
        test_result = {
            "uuid": test_uuid,
            "historyId": test.get('name', 'unknown'),
            "testCaseId": test.get('name', 'unknown'),
            "name": test.get('name', 'Maestro Test'),
            "status": status,
            "start": start_time,
            "stop": stop_time,
            "labels": [
                {"name": "suite", "value": "Maestro Tests"},
                {"name": "framework", "value": "maestro"}
            ],
            "steps": steps
        }
        
        # Add error details if failed
        if test.get('error'):
            test_result['statusDetails'] = {
                "message": test.get('error'),
                "trace": test.get('error')
            }
        
        # Add attachments for screenshots
        attachments = []
        for screenshot in test.get('screenshots', []):
            if os.path.exists(screenshot):
                attachment_uuid = str(uuid.uuid4())
                attachments.append({
                    "name": os.path.basename(screenshot),
                    "source": attachment_uuid + "-attachment.png",
                    "type": "image/png"
                })
        
        if attachments:
            test_result['attachments'] = attachments
        
        # Write result file
        result_file = f"{allure_results_dir}/{test_uuid}-result.json"
        with open(result_file, 'w') as f:
            json.dump(test_result, f, indent=2)
        
        print(f"Created: {result_file}")

# Usage
if __name__ == "__main__":
    convert_maestro_to_allure('maestro-results.json', './allure-results')
    print("\nConversion complete! Run: allure generate allure-results --clean -o allure-report")
```

Save your Maestro output as `maestro-results.json` and run the script to convert it to Allure format.

---

## Question 3: How to run this script

### Answer

Here's how to run the Python script:

#### Step 1: Save the script

Save the Python code to a file named `convert_maestro_to_allure.py`

#### Step 2: Prepare your Maestro JSON file

Make sure you have your Maestro test results saved as `maestro-results.json` in the same directory, or adjust the path in the script.

#### Step 3: Run the script

**Option A: Simple execution**

```bash
python convert_maestro_to_allure.py
```

or if you have Python 3:

```bash
python3 convert_maestro_to_allure.py
```

**Option B: Pass custom paths as arguments**

First, modify the script to accept command-line arguments:

```python
import json
import uuid
import os
import sys
from datetime import datetime

def convert_maestro_to_allure(maestro_json_path, allure_results_dir):
    # ... (same code as before)

if __name__ == "__main__":
    # Get paths from command line or use defaults
    maestro_json = sys.argv[1] if len(sys.argv) > 1 else 'maestro-results.json'
    allure_dir = sys.argv[2] if len(sys.argv) > 2 else './allure-results'
    
    convert_maestro_to_allure(maestro_json, allure_dir)
    print(f"\nConversion complete! Run: allure generate {allure_dir} --clean -o allure-report")
```

Then run with custom paths:

```bash
python3 convert_maestro_to_allure.py /path/to/your/maestro-results.json ./output-dir
```

#### Step 4: Generate Allure report

After running the conversion script:

```bash
# Install Allure (if not already installed)
npm install -g allure-commandline

# Generate the report
allure generate allure-results --clean -o allure-report

# Open the report in your browser
allure open allure-report
```

#### Complete Example

```bash
# 1. Navigate to your project directory
cd /path/to/your/project

# 2. Run Maestro tests and save JSON output
maestro test --format json --output maestro-results.json your-flow.yaml

# 3. Run the conversion script
python3 convert_maestro_to_allure.py

# 4. Generate Allure report
allure generate allure-results --clean -o allure-report

# 5. Open report
allure open allure-report
```

#### Troubleshooting

**If you get "python: command not found":**
- Try `python3` instead
- Or install Python from python.org

**If you get module errors:**
- The script only uses built-in Python modules, so no pip install needed

**If the script runs but creates no files:**
- Check that your `maestro-results.json` file exists and has the correct format
- Check the console output for error messages

---

## Summary

This guide covered:
1. ✅ Converting Maestro JSON test results to Allure format
2. ✅ Example Maestro JSON structure
3. ✅ Complete Python conversion script
4. ✅ Step-by-step execution instructions
5. ✅ Generating and viewing Allure reports

---

**Note:** This conversion script uses only Python built-in modules, so no additional dependencies are required.
