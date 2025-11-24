# Finding Log Files on Server - Complete Guide

## Quick Command to Find All Logs

Run this on your server:

```bash
bash /var/www/html/TEQSmartSubmit/find_logs_on_server.sh
```

Or if the script isn't there, run these commands manually:

## Manual Commands to Find Logs

### 1. Find All Heartbeat Files

```bash
# Check /tmp directory
ls -lt /tmp/python_script_heartbeat_*.txt 2>/dev/null | head -10

# Check all temp directories
find /tmp -name "python_script_heartbeat_*.txt" -type f 2>/dev/null | head -10
find /var/tmp -name "python_script_heartbeat_*.txt" -type f 2>/dev/null | head -10

# Check home directory
find ~ -name "python_script_heartbeat_*.txt" -type f 2>/dev/null | head -10
```

### 2. Find All Error Files

```bash
# Check /tmp for error files
ls -lt /tmp/python_*error*.txt 2>/dev/null | head -10

# Find all error files
find /tmp -name "*error*.txt" -type f 2>/dev/null | head -10
```

### 3. Find the Script Location

```bash
# Check common locations
ls -lh /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py
ls -lh /var/www/html/TEQSmartSubmit/automation/submission/form_discovery.py

# Search entire system
find /var/www -name "form_discovery.py" 2>/dev/null
find /home -name "form_discovery.py" 2>/dev/null
```

### 4. Check Running Processes

```bash
# Find running Python processes
ps aux | grep form_discovery | grep -v grep

# Find all Python processes
ps aux | grep python | grep -v grep

# Check for specific PID heartbeat files
# (Replace PID with actual process ID from above)
ls -lh /tmp/python_script_heartbeat_<PID>.txt
```

### 5. Check /tmp Permissions

```bash
# Check if /tmp is writable
ls -ld /tmp
touch /tmp/test_write_$$.txt && echo "✅ Can write to /tmp" && rm /tmp/test_write_$$.txt || echo "❌ Cannot write to /tmp"

# Check current user
whoami
id
```

## If No Logs Are Found

### Possible Reasons:

1. **Script hasn't run yet**
   - Check if automation was actually triggered
   - Check application logs

2. **Script is crashing before creating logs**
   - Check for error files
   - Run script directly to see errors

3. **Files in different location**
   - Check other temp directories
   - Check if running in Docker/container

4. **Permission issues**
   - Script can't write to /tmp
   - Check user permissions

### Test Script Directly

```bash
# Find script first
SCRIPT_PATH=$(find /var/www -name "form_discovery.py" 2>/dev/null | head -1)

# Create test template
TEMP_DIR=$(mktemp -d)
cat > "$TEMP_DIR/test.json" << 'EOF'
{"name": "Test", "fields": [], "headless": false}
EOF

# Run script and watch for heartbeat file
python3 "$SCRIPT_PATH" --url "https://example.com" --template "$TEMP_DIR/test.json" 2>&1 &
SCRIPT_PID=$!

# Wait a moment
sleep 2

# Check for heartbeat
ls -lh /tmp/python_script_heartbeat_*.txt 2>/dev/null | head -3

# Check process
ps aux | grep $SCRIPT_PID | grep -v grep
```

## Check Application Logs

If script logs aren't appearing, check application logs:

```bash
# PM2 logs
pm2 logs

# Node.js application logs
tail -f /var/log/nodejs/app.log 2>/dev/null
tail -f /var/log/nginx/error.log 2>/dev/null

# System logs
journalctl -u your-app-service -f
```

## Quick Diagnostic Script

Copy this to your server and run it:

```bash
#!/bin/bash
echo "=== Finding Log Files ==="
echo ""
echo "Heartbeat files:"
ls -lt /tmp/python_script_heartbeat_*.txt 2>/dev/null | head -5
echo ""
echo "Error files:"
ls -lt /tmp/python_*error*.txt 2>/dev/null | head -5
echo ""
echo "Running processes:"
ps aux | grep form_discovery | grep -v grep
echo ""
echo "Script location:"
find /var/www -name "form_discovery.py" 2>/dev/null | head -3
```

Save as `find_logs.sh`, make executable (`chmod +x find_logs.sh`), and run it.

