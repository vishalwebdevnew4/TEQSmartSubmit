# Run Server Test

## Quick Test Command

On your server, run:

```bash
cd /var/www/html/TEQSmartSubmit
bash test_automation_on_server.sh
```

Or if the file isn't in that location, run this directly:

```bash
# Create test template
TEMP_DIR=$(mktemp -d)
cat > "$TEMP_DIR/template.json" << 'EOF'
{
  "name": "Test Template",
  "fields": [],
  "headless": false,
  "use_local_captcha_solver": true
}
EOF

# Run test
python3 /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py \
  --url "https://example.com" \
  --template "$TEMP_DIR/template.json"
```

## What to Look For

The test should show:
- ✅ "Started Xvfb virtual display: :XX"
- ✅ "DISPLAY=:XX (browser will run in visible mode)"
- ✅ "Browser launched: chromium"
- ✅ "Navigation successful"

If you see:
- ❌ "DISPLAY: NOT SET" → Xvfb setup failed
- ❌ "Missing X server" → DISPLAY not set before browser launch
- ❌ "Browser launch failed" → Check the specific error message

## After Test

1. Check the output for Xvfb setup messages
2. Verify DISPLAY is set correctly
3. Confirm browser launches
4. Share the results if there are issues

