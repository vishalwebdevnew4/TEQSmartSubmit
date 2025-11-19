# Remote Server Deployment Guide

Complete guide to deploy and run TEQSmartSubmit automation on your remote server.

## Prerequisites

- SSH access to your remote server
- Python 3.8+ installed on the server
- Basic terminal/command line knowledge

## Step-by-Step Deployment

### Step 1: Connect to Your Remote Server

```bash
ssh username@your-server-ip
# or
ssh username@your-domain.com
```

### Step 2: Navigate to Project Directory

```bash
cd /var/www/html/TEQSmartSubmit/automation
# or wherever your project is located
```

### Step 3: Run the Automated Setup Script

This script will install everything and test it:

```bash
bash setup_and_test_remote.sh
```

**What this does:**
- ✅ Installs Playwright (no sudo needed)
- ✅ Installs Chromium browser
- ✅ Sets up environment variables
- ✅ Tests headless mode
- ✅ Verifies everything works

**Expected output:**
```
✅ Python 3.x found
✅ Playwright installed
✅ Chromium browser installed
✅ Headless mode test PASSED!
```

### Step 4: Verify Installation

After the script completes, verify everything is set up:

```bash
# Check Python
python3 --version

# Check Playwright
python3 -m playwright --version

# Check if browsers are installed
ls -la ~/.cache/ms-playwright/
```

### Step 5: Test the Automation

Test with a simple form submission:

```bash
cd /var/www/html/TEQSmartSubmit/automation

# Run a test (this will use headless mode automatically)
python3 test_headless_local.py
```

## Environment Setup

### Option A: Add to ~/.bashrc (Recommended)

The setup script should have already done this, but verify:

```bash
# Check if environment variables are set
cat ~/.bashrc | grep PLAYWRIGHT

# If not there, add them:
echo "" >> ~/.bashrc
echo "# Playwright setup" >> ~/.bashrc
echo "export PATH=\$HOME/.local/bin:\$PATH" >> ~/.bashrc
echo "export PLAYWRIGHT_BROWSERS_PATH=\$HOME/.cache/ms-playwright" >> ~/.bashrc
echo "export TEQ_PLAYWRIGHT_HEADLESS=true" >> ~/.bashrc

# Reload
source ~/.bashrc
```

### Option B: Set in Your Application

If running from Next.js or another application, set these environment variables:

```bash
export PATH=$HOME/.local/bin:$PATH
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright
export TEQ_PLAYWRIGHT_HEADLESS=true
export HEADLESS=true
```

## Running from Next.js API

The Next.js API route will automatically:
1. Detect headless mode (no display)
2. Use the correct browser path
3. Run automation in background

### Ensure Environment Variables are Set

In your Next.js application (`.env` or system environment):

```bash
# .env file or system environment
TEQ_PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_BROWSERS_PATH=/home/username/.cache/ms-playwright
PATH=/home/username/.local/bin:$PATH
```

Or let it auto-detect (recommended - it will work automatically).

## Troubleshooting

### Issue: "playwright: command not found"

**Solution:**
```bash
export PATH=$HOME/.local/bin:$PATH
# Or use: python3 -m playwright
```

### Issue: "Browser not found"

**Solution:**
```bash
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright
python3 -m playwright install chromium
```

### Issue: "ModuleNotFoundError: No module named 'playwright'"

**Solution:**
```bash
pip3 install --user playwright
export PYTHONPATH=$HOME/.local/lib/python3.*/site-packages:$PYTHONPATH
```

### Issue: "Missing shared libraries"

**Solution:**
This is common on shared hosting. Options:
1. Contact your hosting provider to install system libraries
2. Use Conda/Miniconda (see SERVER_SETUP.md)
3. Some libraries may already be installed - try running anyway

### Issue: "Permission denied"

**Solution:**
```bash
chmod +x /var/www/html/TEQSmartSubmit/automation/*.py
chmod -R u+w ~/.cache/ms-playwright
chmod -R u+w ~/.local
```

## Quick Verification Checklist

Run these commands to verify everything is set up:

```bash
# 1. Check Python
python3 --version
# Should show: Python 3.8.x or higher

# 2. Check Playwright
python3 -m playwright --version
# Should show: Version number

# 3. Check browsers
ls ~/.cache/ms-playwright/chromium-* 2>/dev/null && echo "✅ Browsers installed" || echo "❌ Browsers missing"

# 4. Test headless mode
python3 -c "
from playwright.async_api import async_playwright
import asyncio
import os
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/.cache/ms-playwright')
asyncio.run((lambda: async_playwright().__aenter__().then(lambda p: p.chromium.launch(headless=True).then(lambda b: (print('✅ Headless works!'), b.close()))))())
"
```

## Production Deployment

### 1. Set Up Process Manager (PM2)

```bash
# Install PM2
npm install -g pm2

# Start Next.js app with PM2
cd /var/www/html/TEQSmartSubmit
pm2 start npm --name "teqsmartsubmit" -- start
pm2 save
pm2 startup
```

### 2. Set Up Environment Variables

Create `/var/www/html/TEQSmartSubmit/.env.production`:

```bash
# Playwright settings
TEQ_PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_BROWSERS_PATH=/home/username/.cache/ms-playwright

# Database and other settings
DATABASE_URL=your_database_url
# ... other env vars
```

### 3. Ensure Scripts are Executable

```bash
chmod +x /var/www/html/TEQSmartSubmit/automation/*.py
```

### 4. Test the API Endpoint

```bash
# Test the automation API
curl -X POST http://localhost:3000/api/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/contact",
    "template": {
      "fields": [],
      "use_auto_detect": true,
      "use_local_captcha_solver": true,
      "headless": true
    }
  }'
```

## Common Server Configurations

### Shared Hosting (cPanel, etc.)

1. Use the no-sudo installation method
2. Install to user directory (`~/.local`)
3. Set environment variables in `.htaccess` or hosting panel
4. May need to contact support for system libraries

### VPS/Dedicated Server

1. Can use sudo installation (easier)
2. Or use no-sudo method (more secure)
3. Set up systemd service for Next.js app
4. Configure firewall if needed

### Docker Container

1. Install in Dockerfile:
```dockerfile
RUN pip3 install playwright && \
    python3 -m playwright install chromium && \
    python3 -m playwright install-deps chromium
```

2. Set environment variables in docker-compose.yml

## Testing After Deployment

### Test 1: Basic Headless Test

```bash
cd /var/www/html/TEQSmartSubmit/automation
python3 test_remote_headless.py
```

Expected: ✅ Headless mode test PASSED!

### Test 2: Form Submission Test

```bash
cd /var/www/html/TEQSmartSubmit/automation
python3 test_headless_local.py
```

Expected: Form fields fill successfully (CAPTCHA may fail, that's expected)

### Test 3: API Test

```bash
# From your local machine or server
curl -X POST http://your-server.com/api/run \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.seoily.com/contact-us", "template": {"use_auto_detect": true}}'
```

## Monitoring

### Check Logs

```bash
# Next.js logs
pm2 logs teqsmartsubmit

# Or if using systemd
journalctl -u your-service-name -f

# Automation logs (if logging to file)
tail -f /var/www/html/TEQSmartSubmit/automation/*.log
```

### Check Resource Usage

```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check if processes are running
ps aux | grep playwright
ps aux | grep node
```

## Summary

**Quick Start:**
1. SSH to server
2. `cd /var/www/html/TEQSmartSubmit/automation`
3. `bash setup_and_test_remote.sh`
4. Done! ✅

**The script handles everything:**
- ✅ Installation (no sudo needed)
- ✅ Environment setup
- ✅ Testing
- ✅ Verification

**No display needed** - headless mode works perfectly on remote servers!

