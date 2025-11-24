#!/bin/bash
# Test automation script on server
# Run this on your server to test the full automation flow

echo "=================================================================================="
echo "  TESTING AUTOMATION ON SERVER"
echo "=================================================================================="
echo ""

# Get the script path
SCRIPT_PATH="/var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py"

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script not found at: $SCRIPT_PATH"
    echo "   Looking for script..."
    find /var/www -name "form_discovery.py" 2>/dev/null | head -3
    exit 1
fi

echo "✅ Script found at: $SCRIPT_PATH"
echo ""

# Create a test template
TEMP_DIR=$(mktemp -d)
TEMPLATE_FILE="$TEMP_DIR/template.json"

cat > "$TEMPLATE_FILE" << 'EOF'
{
  "name": "Test Template",
  "fields": [],
  "headless": false,
  "use_local_captcha_solver": true
}
EOF

echo "✅ Created test template at: $TEMPLATE_FILE"
echo ""

# Test URL
TEST_URL="https://example.com"

echo "🔄 Running automation test..."
echo "   URL: $TEST_URL"
echo "   Template: $TEMPLATE_FILE"
echo ""

# Run the automation
python3 "$SCRIPT_PATH" --url "$TEST_URL" --template "$TEMPLATE_FILE" 2>&1 | tee /tmp/automation_test.log

# Check exit code
EXIT_CODE=$?

echo ""
echo "=================================================================================="
echo "  TEST RESULTS"
echo "=================================================================================="
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Script executed successfully (exit code: $EXIT_CODE)"
else
    echo "❌ Script failed (exit code: $EXIT_CODE)"
fi

echo ""
echo "📋 Checking for key indicators in output:"
echo ""

# Check for success indicators
if grep -q "✅ Started Xvfb virtual display" /tmp/automation_test.log; then
    echo "✅ Xvfb started successfully"
else
    echo "❌ Xvfb did not start"
fi

if grep -q "DISPLAY=" /tmp/automation_test.log | grep -v "NOT SET"; then
    echo "✅ DISPLAY was set"
else
    echo "❌ DISPLAY was not set"
fi

if grep -q "✅ Browser launched" /tmp/automation_test.log; then
    echo "✅ Browser launched successfully"
else
    echo "❌ Browser did not launch"
fi

if grep -q '"status": "success"' /tmp/automation_test.log; then
    echo "✅ Automation completed successfully"
else
    echo "⚠️  Automation did not complete successfully"
fi

echo ""
echo "📄 Full log saved to: /tmp/automation_test.log"
echo "   View with: cat /tmp/automation_test.log"
echo ""

# Cleanup
rm -rf "$TEMP_DIR"

echo "=================================================================================="

