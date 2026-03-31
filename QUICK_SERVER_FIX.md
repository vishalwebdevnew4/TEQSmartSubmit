# Quick Server Fix Guide

## Run This on Your Server

SSH into your server and run:

```bash
ssh -p 3129 teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com

# Run the fix script
bash /var/www/html/TEQSmartSubmit/fix_server_issue.sh
```

Or if the script isn't there, run these commands manually:

## Manual Fix Steps

### 1. Copy Updated File

```bash
# Copy the updated file to the correct location
cp /var/www/html/TEQSmartSubmit/automation/submission/form_discovery.py \
   /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py

# Verify it was copied
ls -lh /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py
```

### 2. Check File Has Latest Code

```bash
# Check if file has heartbeat code
grep -q "python_script_heartbeat" /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py && echo "✅ Has latest code" || echo "❌ Missing latest code"
```

### 3. Test Script Directly

```bash
# Create test template
TEMP_DIR=$(mktemp -d)
cat > "$TEMP_DIR/test.json" << 'EOF'
{"name": "Test", "fields": [], "headless": false}
EOF

# Test script
python3 /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py \
  --url "https://example.com" \
  --template "$TEMP_DIR/test.json" 2>&1 | head -30
```

### 4. Check Heartbeat Files

```bash
# Check if script is creating heartbeat files
ls -lt /tmp/python_script_heartbeat_*.txt 2>/dev/null | head -3

# If found, check content
cat /tmp/python_script_heartbeat_*.txt 2>/dev/null | head -20
```

### 5. Restart Application

```bash
pm2 restart all
```

## What to Look For

### ✅ Good Signs:
- Heartbeat files are created
- Script produces output when run directly
- File has heartbeat code

### ❌ Issues:
- No heartbeat files → Script not starting
- Syntax errors → File corruption
- Permission denied → Need to fix permissions

## After Running Fix Script

The script will:
1. ✅ Check if files are in correct locations
2. ✅ Copy updated file if needed
3. ✅ Verify Python syntax
4. ✅ Test script execution
5. ✅ Show heartbeat files

Then restart your app and test again!

