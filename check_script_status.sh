#!/bin/bash
# Check if Python script is actually running and producing output

echo "=================================================================================="
echo "  CHECKING PYTHON SCRIPT STATUS"
echo "=================================================================================="
echo ""

# Check for heartbeat files
echo "📋 Checking for heartbeat files..."
HEARTBEAT_FILES=$(ls -t /tmp/python_script_heartbeat_*.txt 2>/dev/null | head -5)
if [ -n "$HEARTBEAT_FILES" ]; then
    echo "✅ Found heartbeat files:"
    for file in $HEARTBEAT_FILES; do
        echo ""
        echo "   File: $file"
        echo "   Content:"
        cat "$file" | sed 's/^/      /'
        echo ""
    done
else
    echo "❌ No heartbeat files found - script may not be starting"
fi

echo ""
echo "📋 Checking for error files..."
if [ -f "/tmp/python_startup_error.txt" ]; then
    echo "❌ Found startup error file:"
    cat /tmp/python_startup_error.txt | sed 's/^/   /'
elif [ -f "/tmp/python_import_error.txt" ]; then
    echo "❌ Found import error file:"
    cat /tmp/python_import_error.txt | sed 's/^/   /'
else
    echo "✅ No error files found"
fi

echo ""
echo "📋 Checking for running Python processes..."
PYTHON_PROCS=$(ps aux | grep -E "form_discovery|python3.*automation" | grep -v grep)
if [ -n "$PYTHON_PROCS" ]; then
    echo "✅ Found running Python processes:"
    echo "$PYTHON_PROCS" | sed 's/^/   /'
else
    echo "❌ No Python automation processes found"
fi

echo ""
echo "📋 Checking script file..."
SCRIPT_PATH="/var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py"
if [ -f "$SCRIPT_PATH" ]; then
    echo "✅ Script exists at: $SCRIPT_PATH"
    echo "   Size: $(stat -c%s "$SCRIPT_PATH") bytes"
    echo "   Modified: $(stat -c%y "$SCRIPT_PATH")"
    
    # Check if it has the heartbeat code
    if grep -q "python_script_heartbeat" "$SCRIPT_PATH"; then
        echo "   ✅ Contains heartbeat code (updated version)"
    else
        echo "   ⚠️  Does NOT contain heartbeat code (may be old version)"
    fi
else
    echo "❌ Script NOT found at: $SCRIPT_PATH"
fi

echo ""
echo "=================================================================================="

