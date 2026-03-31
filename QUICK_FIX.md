# Quick Fix for Remote Server

Based on your diagnostic output, **Chromium IS installed** ✅, but there might be a path or permission issue.

## Step 1: Test Browser Launch

Run this test to verify the browser can actually launch:

```bash
cd /var/www/html/TEQSmartSubmit
python3 test_browser_launch.py
```

This will:
- ✅ Verify Playwright can import
- ✅ Check if browser executable exists
- ✅ Try to launch the browser
- ✅ Test navigation
- ❌ Show specific errors if something fails

## Step 2: Check Browser Permissions

If the test fails, check permissions:

```bash
# Check if browser is executable
ls -la /var/www/projects/teqsmartsubmit/teqsmartsubmit/.cache/ms-playwright/chromium-1194/chrome-linux/chrome

# Make sure it's executable
chmod +x /var/www/projects/teqsmartsubmit/teqsmartsubmit/.cache/ms-playwright/chromium-1194/chrome-linux/chrome
```

## Step 3: Verify Python Environment

The automation might be using a different Python environment. Check:

```bash
# Check which Python the automation uses
which python3

# Check if Playwright is in the same environment
python3 -c "import playwright; print(playwright.__file__)"
```

## Step 4: Reinstall Browsers (if needed)

If the browser path is wrong or inaccessible, reinstall:

```bash
# Install to default location (user's home directory)
python3 -m playwright install chromium

# Or install to system location
PLAYWRIGHT_BROWSERS_PATH=/var/www/projects/teqsmartsubmit/teqsmartsubmit/.cache/ms-playwright python3 -m playwright install chromium
```

## Common Issues

### Issue: "Executable doesn't exist"
**Solution:** Browser might be in a different location. Reinstall:
```bash
python3 -m playwright install chromium
```

### Issue: Permission denied
**Solution:** Make browser executable:
```bash
chmod +x /var/www/projects/teqsmartsubmit/teqsmartsubmit/.cache/ms-playwright/chromium-1194/chrome-linux/chrome
```

### Issue: Different Python environment
**Solution:** Make sure the automation uses the same Python that has Playwright:
```bash
# Find where Playwright is installed
python3 -c "import playwright; print(playwright.__file__)"

# Use that Python for automation
```

## After Testing

Once `test_browser_launch.py` passes, your automation should work. If it still fails, the error message will tell you exactly what's wrong.

