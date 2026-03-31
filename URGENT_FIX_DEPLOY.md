# URGENT: Deploy Non-Blocking Fix

The script is still hanging because `sys.stderr.write()` itself can block when the pipe buffer is full.

## What Changed

1. **Enhanced `safe_write()` function** - Now uses `select()` to check if pipe is writable before writing
2. **Skips writes if pipe buffer is full** - Prevents blocking
3. **Heartbeat file updates** - Added more heartbeat updates to track progress even if stderr blocks

## Deploy Immediately

```bash
# On server:
cd ~/TEQSmartSubmit  # or wherever your git repo is
git pull origin main

# Copy to the actual script location:
cp automation/submission/form_discovery.py /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py

# Verify fix:
grep -q "select.select" /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py && echo "✅ Fix deployed" || echo "❌ Not deployed"
```

## What the Fix Does

1. **Checks if pipe is writable** using `select()` before writing
2. **Skips write if buffer is full** - prevents blocking
3. **Updates heartbeat file** - so you can track progress even if stderr blocks
4. **Continues execution** - script won't hang even if logging fails

The script will now continue past "Function called" even if stderr writes would block!

