# Maestro to Allure Converter - Command Line Usage

## Installation

No additional packages needed beyond standard Python libraries:
```bash
python3 --version  # Ensure Python 3.6+ is installed
```

## Basic Usage

### Simple conversion (default output directory)
```bash
python convert_maestro_to_allure.py maestro_report.json
```

This creates results in the `allure-results/` directory.

### Specify custom output directory
```bash
python convert_maestro_to_allure.py maestro_report.json -o my-custom-results
```

### Verbose output
```bash
python convert_maestro_to_allure.py maestro_report.json -o allure-results -v
```

## Command Line Arguments

| Argument | Short | Required | Description | Default |
|----------|-------|----------|-------------|---------|
| `input_file` | - | ✓ | Path to Maestro JSON report | - |
| `--output-dir` | `-o` | ✗ | Output directory for Allure results | `allure-results` |
| `--verbose` | `-v` | ✗ | Enable verbose output | `False` |
| `--help` | `-h` | ✗ | Show help message | - |

## Examples

### Example 1: Basic conversion
```bash
python convert_maestro_to_allure.py test-results.json
```

Output:
```
✓ Allure result created: allure-results/abc123-result.json

✓ Conversion successful!

To generate Allure report, run:
  allure serve allure-results
```

### Example 2: Custom output directory
```bash
python convert_maestro_to_allure.py maestro_report.json -o reports/allure
```

### Example 3: Multiple test files
```bash
# Convert multiple Maestro test results
python convert_maestro_to_allure.py test1.json -o allure-results
python convert_maestro_to_allure.py test2.json -o allure-results
python convert_maestro_to_allure.py test3.json -o allure-results

# Generate combined report
allure serve allure-results
```

### Example 4: CI/CD Pipeline
```bash
#!/bin/bash
# run_tests.sh

# Run Maestro test
maestro test flow.yaml --format json > maestro-output.json

# Convert to Allure
python convert_maestro_to_allure.py maestro-output.json -o build/allure-results

# Generate report
allure generate build/allure-results -o build/allure-report
```

## Getting Help

```bash
python convert_maestro_to_allure.py --help
```

Output:
```
usage: convert_maestro_to_allure.py [-h] [-o OUTPUT_DIR] [-v] input_file

Convert Maestro JSON report to Allure format

positional arguments:
  input_file            Path to Maestro JSON report file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory for Allure results (default: allure-results)
  -v, --verbose         Enable verbose output

Example: python convert_maestro_to_allure.py maestro_report.json -o my-results
```

## Error Handling

### File not found
```bash
$ python convert_maestro_to_allure.py missing.json
❌ Error: File 'missing.json' not found
```

### Invalid JSON
```bash
$ python convert_maestro_to_allure.py invalid.json
❌ Error: Invalid JSON in 'invalid.json'
```

## Complete Workflow

```bash
# 1. Run your Maestro test and save output
maestro test my-flow.yaml --format json > maestro_report.json

# 2. Convert to Allure format
python convert_maestro_to_allure.py maestro_report.json -o allure-results -v

# 3. Generate and view Allure report
allure serve allure-results

# OR generate static report
allure generate allure-results -o allure-report --clean
```

## Integration Examples

### GitHub Actions
```yaml
- name: Convert to Allure
  run: |
    python convert_maestro_to_allure.py maestro-output.json -o ${{ github.workspace }}/allure-results
```

### Jenkins
```groovy
sh 'python convert_maestro_to_allure.py maestro-report.json -o allure-results'
```

### GitLab CI
```yaml
script:
  - python convert_maestro_to_allure.py maestro-report.json -o allure-results
```

## Tips

1. **Batch Processing**: Process multiple test files into the same output directory to create a combined report
2. **Directory Structure**: Keep your output directory clean by using timestamped folders:
   ```bash
   python convert_maestro_to_allure.py test.json -o "results/$(date +%Y%m%d_%H%M%S)"
   ```
3. **Automation**: Create a shell script or batch file for repeated conversions
