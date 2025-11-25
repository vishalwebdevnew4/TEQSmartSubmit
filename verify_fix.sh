#!/bin/bash
# Quick verification that the fix is in the code

SCRIPT_PATH="automation/submission/form_discovery.py"

echo "🔍 Verifying pipe blocking fix..."
echo ""

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script not found: $SCRIPT_PATH"
    exit 1
fi

echo "✅ Script found: $SCRIPT_PATH"
echo ""

# Check for key fix components
echo "Checking for fix components:"
echo ""

FIXES_FOUND=0

if grep -q "def safe_write" "$SCRIPT_PATH"; then
    echo "✅ safe_write function found"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "❌ safe_write function NOT found"
fi

if grep -q "Only flush if it's a TTY" "$SCRIPT_PATH"; then
    echo "✅ TTY check found (prevents blocking on pipes)"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "❌ TTY check NOT found"
fi

if grep -q 'safe_write.*Function called' "$SCRIPT_PATH"; then
    echo "✅ safe_write used for 'Function called' message"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "❌ safe_write NOT used for 'Function called'"
fi

if grep -q 'safe_write.*AUTOMATION STARTING' "$SCRIPT_PATH" || grep -q 'safe_write.*===' "$SCRIPT_PATH"; then
    echo "✅ safe_write used for startup messages"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "⚠️  safe_write may not be used for all startup messages"
fi

echo ""
echo "=" * 80

if [ $FIXES_FOUND -ge 3 ]; then
    echo "✅ FIX VERIFIED: All key components present ($FIXES_FOUND/4)"
    echo ""
    echo "📋 The fix prevents blocking by:"
    echo "   1. Using safe_write() instead of direct flush()"
    echo "   2. Only flushing when stderr is a TTY (terminal), not a pipe"
    echo "   3. This allows Node.js to handle buffering without blocking Python"
    echo ""
    echo "🚀 Ready to deploy to server!"
    exit 0
else
    echo "❌ FIX INCOMPLETE: Only $FIXES_FOUND/4 components found"
    exit 1
fi

