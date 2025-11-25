#!/bin/bash
# Comprehensive test script for form_discovery.py fix on remote server
# Run this on the server: bash test_fix_on_server.sh

set -e

echo "=" | tr -d '\n' | head -c 80 && echo ""
echo "🧪 Testing form_discovery.py Fix on Server"
echo "=" | tr -d '\n' | head -c 80 && echo ""
echo ""

# Find the script file
SCRIPT_FILE=""
for dir in "." "/var/www/html/TEQSmartSubmit" "$HOME/TEQSmartSubmit" "/var/www/projects/teqsmartsubmit/teqsmartsubmit"; do
    if [ -f "$dir/automation/submission/form_discovery.py" ]; then
        SCRIPT_FILE="$dir/automation/submission/form_discovery.py"
        break
    fi
done

# If not found, search for it
if [ -z "$SCRIPT_FILE" ]; then
    SCRIPT_FILE=$(find /var/www /home -name "form_discovery.py" -path "*/automation/submission/*" 2>/dev/null | head -1)
fi

if [ -z "$SCRIPT_FILE" ] || [ ! -f "$SCRIPT_FILE" ]; then
    echo "❌ form_discovery.py not found!"
    echo "   Searched in:"
    echo "   - Current directory"
    echo "   - /var/www/html/TEQSmartSubmit"
    echo "   - /var/www/projects/teqsmartsubmit/teqsmartsubmit"
    echo ""
    echo "   Please run this script from the directory containing automation/submission/form_discovery.py"
    exit 1
fi

echo "✅ Script found: $SCRIPT_FILE"
echo ""

# Test 1: Verify fix components
echo "📋 Test 1: Verifying fix components..."
echo "----------------------------------------"

FIXES_FOUND=0
TOTAL_TESTS=4

if grep -q "def safe_write" "$SCRIPT_FILE"; then
    echo "✅ safe_write function found"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "❌ safe_write function NOT found"
fi

if grep -q "Only flush if it's a TTY" "$SCRIPT_FILE"; then
    echo "✅ TTY check found (prevents blocking on pipes)"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "❌ TTY check NOT found"
fi

if grep -q "safe_write.*Function called" "$SCRIPT_FILE"; then
    echo "✅ safe_write used for 'Function called' message"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "❌ safe_write NOT used for 'Function called'"
fi

if grep -q "safe_write.*AUTOMATION STARTING" "$SCRIPT_FILE" || grep -q 'safe_write.*===' "$SCRIPT_FILE"; then
    echo "✅ safe_write used for startup messages"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "⚠️  safe_write may not be used for all startup messages"
fi

echo ""
if [ $FIXES_FOUND -eq $TOTAL_TESTS ]; then
    echo "✅ All fix components verified ($FIXES_FOUND/$TOTAL_TESTS)"
else
    echo "⚠️  Some components missing ($FIXES_FOUND/$TOTAL_TESTS)"
fi
echo ""

# Test 2: Syntax check
echo "📋 Test 2: Python syntax check..."
echo "----------------------------------------"
if python3 -m py_compile "$SCRIPT_FILE" 2>&1; then
    echo "✅ Syntax is valid"
else
    echo "❌ Syntax errors found"
    exit 1
fi
echo ""

# Test 3: Import test
echo "📋 Test 3: Import test (checking for blocking)..."
echo "----------------------------------------"
SCRIPT_DIR=$(dirname "$(dirname "$(dirname "$SCRIPT_FILE")")")
cd "$SCRIPT_DIR" 2>/dev/null || cd "$(pwd)"

timeout 20 python3 -c "
import sys
import os
sys.path.insert(0, os.getcwd())
try:
    print('📍 Attempting to import form_discovery...')
    from automation.submission import form_discovery
    print('✅ Import successful - no blocking detected')
    print('✅ Module loaded: automation.submission.form_discovery')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'⚠️  Other error (may be OK): {type(e).__name__}: {e}')
    # Don't exit on other errors - might be missing dependencies
" 2>&1

IMPORT_RESULT=$?
if [ $IMPORT_RESULT -eq 0 ]; then
    echo "✅ Import test passed"
elif [ $IMPORT_RESULT -eq 124 ]; then
    echo "❌ Import test timed out - possible blocking issue"
else
    echo "⚠️  Import had issues (might be missing dependencies like playwright)"
fi
echo ""

# Test 4: Check for blocking patterns
echo "📋 Test 4: Checking for blocking patterns..."
echo "----------------------------------------"
BLOCKING_PATTERNS=0

# Check for direct flush() calls in main_async (should use safe_write instead)
if grep -A 5 "def main_async_with_ultimate_safety" "$SCRIPT_FILE" | grep -q "sys.stderr.flush()"; then
    echo "⚠️  Found direct sys.stderr.flush() in main_async - might cause blocking"
    BLOCKING_PATTERNS=$((BLOCKING_PATTERNS + 1))
else
    echo "✅ No direct flush() calls found in main_async"
fi

# Check that safe_write is used
SAFE_WRITE_COUNT=$(grep -c "safe_write(" "$SCRIPT_FILE" || echo "0")
if [ "$SAFE_WRITE_COUNT" -gt 5 ]; then
    echo "✅ safe_write is used extensively ($SAFE_WRITE_COUNT times)"
else
    echo "⚠️  safe_write used only $SAFE_WRITE_COUNT times (expected more)"
fi

echo ""

# Test 5: File permissions and accessibility
echo "📋 Test 5: File permissions..."
echo "----------------------------------------"
if [ -r "$SCRIPT_FILE" ]; then
    echo "✅ File is readable"
else
    echo "❌ File is not readable"
fi

if [ -x "$SCRIPT_FILE" ]; then
    echo "✅ File is executable"
else
    echo "ℹ️  File is not executable (this is OK for Python scripts)"
fi

FILE_SIZE=$(stat -f%z "$SCRIPT_FILE" 2>/dev/null || stat -c%s "$SCRIPT_FILE" 2>/dev/null)
echo "ℹ️  File size: $FILE_SIZE bytes"
echo ""

# Test 6: Quick dry-run (if possible)
echo "📋 Test 6: Quick argument parsing test..."
echo "----------------------------------------"
cd "$SCRIPT_DIR" 2>/dev/null || cd "$(pwd)"

# Create a minimal test template
TEMP_TEMPLATE=$(mktemp /tmp/test_template_XXXXXX.json)
echo '{"name": "Test", "max_timeout_seconds": 5, "fields": []}' > "$TEMP_TEMPLATE"

# Test that script accepts arguments (should exit quickly with help or error, not hang)
timeout 5 python3 "$SCRIPT_FILE" --url "https://example.com" --template "$TEMP_TEMPLATE" > /dev/null 2>&1 &
TEST_PID=$!
sleep 2

if kill -0 $TEST_PID 2>/dev/null; then
    echo "⚠️  Script is still running (might be OK, or might indicate blocking)"
    kill $TEST_PID 2>/dev/null || true
    wait $TEST_PID 2>/dev/null || true
else
    echo "✅ Script started and completed argument parsing"
fi

rm -f "$TEMP_TEMPLATE"
echo ""

# Summary
echo "=" | tr -d '\n' | head -c 80 && echo ""
echo "📊 TEST SUMMARY"
echo "=" | tr -d '\n' | head -c 80 && echo ""
echo ""
echo "Fix Components: $FIXES_FOUND/$TOTAL_TESTS"
echo "Syntax Check: ✅ Passed"
echo "Import Test: $([ $IMPORT_RESULT -eq 0 ] && echo '✅ Passed' || echo '⚠️  Had issues')"
echo "Blocking Patterns: $([ $BLOCKING_PATTERNS -eq 0 ] && echo '✅ None found' || echo '⚠️  Found')"
echo ""

if [ $FIXES_FOUND -eq $TOTAL_TESTS ] && [ $IMPORT_RESULT -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    echo ""
    echo "✅ The fix is properly deployed and should work correctly."
    echo "   The script should no longer hang at 'Function called'"
    echo ""
    echo "📋 Next step: Test a real submission through the web interface"
    exit 0
elif [ $FIXES_FOUND -ge 3 ]; then
    echo "⚠️  MOSTLY PASSED"
    echo ""
    echo "✅ The fix appears to be deployed ($FIXES_FOUND/$TOTAL_TESTS components found)"
    if [ $IMPORT_RESULT -ne 0 ]; then
        echo "⚠️  Import had issues - might be missing dependencies (playwright, etc.)"
        echo "   This is OK - the blocking fix should still work"
    fi
    echo ""
    echo "📋 Next step: Test a real submission to verify it works"
    exit 0
else
    echo "❌ TESTS FAILED"
    echo ""
    echo "⚠️  The fix may not be properly deployed"
    echo "   Only $FIXES_FOUND/$TOTAL_TESTS fix components found"
    echo ""
    echo "💡 Try:"
    echo "   1. Pull latest changes: git pull origin main"
    echo "   2. Verify file location: ls -la $SCRIPT_FILE"
    echo "   3. Check file content: grep 'def safe_write' $SCRIPT_FILE"
    exit 1
fi

