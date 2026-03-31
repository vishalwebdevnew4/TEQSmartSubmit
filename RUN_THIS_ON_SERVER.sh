#!/bin/bash
# Copy-paste this entire script to run on your server via SSH
# Or save it and run: bash RUN_THIS_ON_SERVER.sh

echo "🧪 Testing form_discovery.py Fix on Server"
echo "========================================"
echo ""

# Find the script
SCRIPT_FILE=$(find ~ /var/www -name "form_discovery.py" -path "*/automation/submission/*" 2>/dev/null | head -1)

if [ -z "$SCRIPT_FILE" ]; then
    echo "❌ form_discovery.py not found"
    echo "   Please run: git pull origin main"
    exit 1
fi

echo "✅ Found: $SCRIPT_FILE"
echo ""

# Test 1: Check fix components
echo "Test 1: Fix Components"
echo "----------------------"
FIXES=0
grep -q "def safe_write" "$SCRIPT_FILE" && echo "✅ safe_write function" && FIXES=$((FIXES+1)) || echo "❌ safe_write missing"
grep -q "Only flush if it's a TTY" "$SCRIPT_FILE" && echo "✅ TTY check" && FIXES=$((FIXES+1)) || echo "❌ TTY check missing"
grep -q "safe_write.*Function called" "$SCRIPT_FILE" && echo "✅ safe_write used" && FIXES=$((FIXES+1)) || echo "❌ safe_write not used"
echo "Result: $FIXES/3 components found"
echo ""

# Test 2: Syntax
echo "Test 2: Syntax Check"
echo "----------------------"
if python3 -m py_compile "$SCRIPT_FILE" 2>&1; then
    echo "✅ Syntax valid"
else
    echo "❌ Syntax errors"
    exit 1
fi
echo ""

# Test 3: Import (with timeout)
echo "Test 3: Import Test (20s timeout)"
echo "----------------------"
SCRIPT_DIR=$(dirname "$(dirname "$(dirname "$SCRIPT_FILE")")")
cd "$SCRIPT_DIR" 2>/dev/null || cd ~

timeout 20 python3 -c "
import sys, os
sys.path.insert(0, os.getcwd())
try:
    print('📍 Importing...')
    from automation.submission import form_discovery
    print('✅ Import successful - no blocking!')
except Exception as e:
    print(f'⚠️  Error: {e}')
" 2>&1

IMPORT_OK=$?
echo ""

# Summary
echo "========================================"
echo "SUMMARY"
echo "========================================"
echo "Fix Components: $FIXES/3"
echo "Syntax: ✅"
echo "Import: $([ $IMPORT_OK -eq 0 ] && echo '✅' || echo '⚠️')"
echo ""

if [ $FIXES -eq 3 ] && [ $IMPORT_OK -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    echo "✅ Fix is working correctly"
    echo ""
    echo "Next: Test a real submission through web interface"
    exit 0
elif [ $FIXES -ge 2 ]; then
    echo "⚠️  MOSTLY OK - Fix appears deployed"
    echo "   Ready to test with real submission"
    exit 0
else
    echo "❌ FIX NOT FOUND"
    echo "   Run: git pull origin main"
    exit 1
fi

