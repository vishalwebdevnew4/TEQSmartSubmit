# Git Deployment Guide for form_discovery.py Fix

Since you're using git to sync files between local and server, here's the easiest way to deploy the fix:

## Quick Deployment (Recommended)

### On Your Local Machine:
1. **Commit and push the changes:**
   ```bash
   git add automation/submission/form_discovery.py
   git commit -m "Fix: Prevent stderr flush blocking on pipe buffers"
   git push origin main
   ```

### On Your Server:
1. **Pull the latest changes:**
   ```bash
   cd ~/TEQSmartSubmit  # or wherever your git repo is
   git pull origin main
   ```

2. **Verify the fix is present:**
   ```bash
   grep -q "def safe_write" automation/submission/form_discovery.py && echo "✅ Fix found" || echo "❌ Fix not found"
   ```

3. **If you need to copy to a different location:**
   ```bash
   # Only if the app uses a different path
   cp automation/submission/form_discovery.py /var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py
   ```

## Alternative: Use the Updated Deployment Script

The `deploy_and_test_fix.sh` script now auto-detects the file location:

```bash
# Run from anywhere - it will find the file
bash deploy_and_test_fix.sh
```

Or use the git-specific script:

```bash
bash deploy_with_git.sh
```

## What Changed

The fix adds a `safe_write()` function that:
- Only flushes stderr when it's a TTY (terminal), not a pipe
- Prevents blocking when Node.js isn't reading the pipe fast enough
- Uses `safe_write()` for all critical log messages in `main_async_with_ultimate_safety`

## Verification

After pulling, verify the fix:

```bash
# Check for the fix components
grep -c "def safe_write" automation/submission/form_discovery.py  # Should return 1
grep -c "Only flush if it's a TTY" automation/submission/form_discovery.py  # Should return 2
grep -c "safe_write.*Function called" automation/submission/form_discovery.py  # Should return 1
```

All should return positive numbers if the fix is present.

