# Remote Server Testing Guide

## Quick Test on Remote Server

### 1. Connect to Remote Server

```bash
ssh -p 3129 teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com
```

### 2. Navigate to Project Directory

```bash
cd /var/www/html/TEQSmartSubmit
```

### 3. Run the Test Script

```bash
cd automation
chmod +x test_remote_server.py
python3 test_remote_server.py
```

## What the Test Checks

1. **Environment Detection**
   - Checks if DISPLAY is available
   - Detects containerized environments
   - Shows expected browser mode (headless vs visible)

2. **Form Submission**
   - Tests form field auto-detection
   - Tests CAPTCHA detection and solving
   - Tests form submission
   - Verifies success/failure

## Expected Results

### On Remote Server (No Display)
- Should detect: `No display detected`
- Should use: `HEADLESS MODE`
- Should still work for form submission
- CAPTCHA solving may be less reliable in headless mode

### If Xvfb is Set Up
- Should detect: `Display detected`
- Should use: `VISIBLE BROWSER (non-headless)`
- Better CAPTCHA solving reliability

## Troubleshooting

### If Playwright is Not Installed

```bash
# Install Playwright
pip3 install playwright

# Install Chromium browser
playwright install chromium
```

### If Dependencies are Missing

```bash
# Install Python dependencies
pip3 install playwright requests asyncio
```

### If Test Fails

1. Check the error message in the output
2. Verify network connectivity: `curl -I https://www.seoily.com/contact-us`
3. Check if the site is accessible from the server
4. Review logs for specific error details

## Setting Up Xvfb (Optional - for Better CAPTCHA Solving)

If you want better CAPTCHA solving on the remote server:

```bash
# Install Xvfb
sudo apt-get update
sudo apt-get install -y xvfb

# Start Xvfb
Xvfb :99 -screen 0 1920x1080x24 &

# Set DISPLAY
export DISPLAY=:99

# Now run the test
python3 test_remote_server.py
```

## Environment Variables

You can override behavior with environment variables:

```bash
# Force headless mode
export TEQ_FORCE_HEADLESS=true

# Or use visible browser (if display available)
export TEQ_FORCE_HEADLESS=false
```

## Next Steps After Testing

1. If test passes: Deploy the application
2. If test fails: Review error messages and fix issues
3. For production: Consider setting up Xvfb for better CAPTCHA solving

