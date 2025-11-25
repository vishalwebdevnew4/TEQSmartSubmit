# Quick Server Test Instructions

## To test the fix on your server:

### Option 1: Using the deployment script (Recommended)

SSH into your server and run:

```bash
ssh -p 3129 teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com
cd /var/www/html/TEQSmartSubmit
bash deploy_and_test_fix.sh
```

This will:
1. Copy the updated file to the server location
2. Verify the fix is present
3. Run syntax and import tests

### Option 2: Manual deployment

```bash
# SSH into server
ssh -p 3129 teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com

# Copy the file
cp /var/www/html/TEQSmartSubmit/automation/submission/form_discovery.py \
   /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py

# Verify the fix
grep -n "def safe_write" /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py

# Test syntax
python3 -m py_compile /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py
```

### Option 3: Quick test without deployment

Test if the fix is already on the server:

```bash
ssh -p 3129 teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com
grep -n "safe_write" /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py
```

If you see output, the fix is already deployed. If not, use Option 1 or 2.

## What the fix does:

1. **Prevents blocking on pipe buffers**: The `safe_write()` function only flushes stderr if it's a TTY (terminal), not a pipe
2. **Non-blocking writes**: All stderr writes in `main_async_with_ultimate_safety` now use `safe_write()` instead of direct writes with `flush()`
3. **Maintains compatibility**: Still works in terminals (local testing) but won't block on servers

## Expected behavior after fix:

- Script should progress past "📍 [main_async] Function called"
- You should see subsequent log messages like:
  - "🚀 AUTOMATION STARTING"
  - "📍 [main_async] After initial log prints"
  - "📍 [main_async] About to get URL"
  - etc.

## If it still hangs:

1. Check the heartbeat file:
   ```bash
   ls -lt /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_script_heartbeat_*.txt | head -1
   cat $(ls -t /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_script_heartbeat_*.txt | head -1)
   ```

2. Check if the process is actually running:
   ```bash
   ps aux | grep form_discovery
   ```

3. Check Node.js is reading stderr:
   - Look at the submission log in the web interface
   - Check if new log messages appear

