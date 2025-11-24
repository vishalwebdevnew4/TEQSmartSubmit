# Log Location Fixed ✅

## What Was Changed

The script now writes all log files to:
```
/var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/
```

Instead of `/tmp/`

## Files That Will Be Created

1. **Heartbeat files** (one per process):
   ```
   /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_script_heartbeat_<PID>.txt
   ```

2. **Error files**:
   ```
   /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_startup_error.txt
   /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_import_error.txt
   ```

## Setup Steps on Server

### 1. Ensure Directory Exists

```bash
# Run the setup script
bash /var/www/html/TEQSmartSubmit/update_logs_location.sh
```

Or manually:
```bash
mkdir -p /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp
chmod 755 /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp
```

### 2. Copy Updated Script

```bash
cp /var/www/html/TEQSmartSubmit/automation/submission/form_discovery.py \
   /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py
```

### 3. Restart Application

```bash
pm2 restart all
```

### 4. Check Logs

```bash
# List all heartbeat files
ls -lt /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_script_heartbeat_*.txt

# View latest heartbeat
ls -t /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_script_heartbeat_*.txt | head -1 | xargs cat

# Check for errors
ls -lt /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_*error*.txt
```

## Fallback Behavior

If the custom tmp directory doesn't exist or isn't writable, the script will:
1. Try to create it
2. If that fails, fall back to `/tmp/`

This ensures the script always works, even if the directory setup isn't perfect.

## Quick Test

```bash
# Test that directory is writable
touch /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/test.txt && \
  echo "✅ Directory is writable" && \
  rm /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/test.txt || \
  echo "❌ Directory is NOT writable"
```

