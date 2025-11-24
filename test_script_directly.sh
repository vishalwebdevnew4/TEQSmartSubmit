#!/bin/bash
# Test script to verify Python script can run directly

echo "Testing Python script execution..."
echo ""

# Test 1: Check if script exists
SCRIPT_PATH="/var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py"
if [ -f "$SCRIPT_PATH" ]; then
    echo "✅ Script exists at: $SCRIPT_PATH"
else
    echo "❌ Script NOT found at: $SCRIPT_PATH"
    echo "Looking for script..."
    find /var/www -name "form_discovery.py" 2>/dev/null | head -5
    exit 1
fi

echo ""
echo "Test 2: Try to run script with --help (should show usage)"
python3 "$SCRIPT_PATH" --help 2>&1 | head -20

echo ""
echo "Test 3: Check Python syntax"
python3 -m py_compile "$SCRIPT_PATH" 2>&1

echo ""
echo "Test 4: Try importing the script"
python3 -c "import sys; sys.path.insert(0, '/var/www/projects/teqsmartsubmit/teqsmartsubmit'); import automation.submission.form_discovery" 2>&1 | head -10

