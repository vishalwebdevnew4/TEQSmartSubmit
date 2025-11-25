#!/bin/bash
# Test script to verify form_discovery.py fixes on the server
# Run this on the server: bash test_script_fix.sh

echo "🧪 Testing form_discovery.py fixes..."
echo ""

# Check if script exists
SCRIPT_PATH="/var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script not found at: $SCRIPT_PATH"
    echo "📋 Checking alternative locations..."
    find /var/www -name "form_discovery.py" 2>/dev/null | head -5
    exit 1
fi

echo "✅ Script found at: $SCRIPT_PATH"
echo ""

# Check if the fix is present (safe_write function)
echo "🔍 Checking for fix implementation..."
if grep -q "def safe_write" "$SCRIPT_PATH"; then
    echo "✅ safe_write function found"
else
    echo "❌ safe_write function NOT found - fix may not be applied"
    echo "💡 You may need to copy the updated file to the server"
fi

if grep -q "Only flush if it's a TTY" "$SCRIPT_PATH"; then
    echo "✅ TTY check found (prevents blocking on pipes)"
else
    echo "⚠️  TTY check not found"
fi

echo ""
echo "🧪 Running quick syntax check..."
python3 -m py_compile "$SCRIPT_PATH" 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Script syntax is valid"
else
    echo "❌ Script has syntax errors"
    exit 1
fi

echo ""
echo "🧪 Testing import (this may take a moment)..."
timeout 10 python3 -c "
import sys
sys.path.insert(0, '/var/www/projects/teqsmartsubmit/teqsmartsubmit')
try:
    from automation.submission import form_discovery
    print('✅ Import successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All checks passed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. The script should now work without hanging"
    echo "2. Test a real submission through the web interface"
    echo "3. Monitor the logs to see if it progresses past 'Function called'"
else
    echo ""
    echo "❌ Some checks failed - please review the errors above"
fi

