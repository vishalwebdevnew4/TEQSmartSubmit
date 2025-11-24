# Server Fix Steps - Detailed Logging Added

## ✅ What Was Fixed

1. **Added heartbeat file logging** - Script writes to `/tmp/python_script_heartbeat_<PID>.txt` immediately
2. **Added detailed Playwright logging** - Now tracks every step of browser initialization
3. **Added flush calls** - Ensures output is immediately visible

## 📋 Next Steps on Server

### 1. Copy Updated File

```bash
# SSH into server
ssh -p 3129 teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com

# Copy the updated file
cp /var/www/html/TEQSmartSubmit/automation/submission/form_discovery.py \
   /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py

# Verify it was copied
ls -lh /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py
```

### 2. Restart Application

```bash
pm2 restart all
```

### 3. Test Again

Run the automation from the dashboard and watch the logs. You should now see:

```
📍 [start()] Method called
📍 [start()] Current DISPLAY: ...
📍 [start()] About to import Playwright...
📍 [start()] Playwright import result: ...
📍 [start()] Importing async_playwright...
📍 [start()] About to call async_playwright().start()...
📍 [start()] About to launch browser...
📍 [start()] Trying chromium...
```

### 4. Check Where It Hangs

The logs will show exactly where the script stops:
- If it stops at "About to import Playwright" → Playwright not installed
- If it stops at "About to call async_playwright().start()" → Playwright installation issue
- If it stops at "Trying chromium" → Browser launch issue (likely DISPLAY problem)

## 🔍 Diagnostic Commands

### Check Heartbeat Files
```bash
ls -lt /tmp/python_script_heartbeat_*.txt | head -1
cat /tmp/python_script_heartbeat_*.txt | tail -20
```

### Check Running Processes
```bash
ps aux | grep form_discovery | grep -v grep
```

### Test Script Directly
```bash
# Create test template
TEMP_DIR=$(mktemp -d)
cat > "$TEMP_DIR/test.json" << 'EOF'
{"name": "Test", "fields": [], "headless": false}
EOF

# Run script directly (will show all output)
python3 /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py \
  --url "https://example.com" \
  --template "$TEMP_DIR/test.json" 2>&1 | tee /tmp/script_output.log
```

## 🎯 Expected Behavior

After copying the file and restarting, you should see:
1. ✅ Script starts and prints startup messages
2. ✅ Template loads successfully
3. ✅ Playwright initialization begins with detailed logs
4. ✅ Browser launches (or shows specific error)

The detailed logs will show **exactly** where it's hanging, making it easy to fix the issue.

## 📝 What the Logs Will Show

The new logging will show:
- `📍 [start()] Method called` - Confirms start() was called
- `📍 [start()] Current DISPLAY: ...` - Shows display status
- `📍 [start()] About to import Playwright...` - Before import
- `📍 [start()] Playwright import result: ...` - After import
- `📍 [start()] About to call async_playwright().start()...` - Before starting
- `📍 [start()] About to launch browser...` - Before browser launch
- `📍 [start()] Trying chromium...` - Before each browser attempt

**The last log message you see will tell you exactly where it's hanging!**

