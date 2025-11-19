# Quick Start - Remote Server Setup

## 🚀 Fastest Way to Get Started

### 1. Connect to Your Server

```bash
ssh username@your-server.com
```

### 2. Navigate to Project

```bash
cd /var/www/html/TEQSmartSubmit/automation
```

### 3. Run Setup Script

```bash
bash setup_and_test_remote.sh
```

**That's it!** The script does everything automatically.

## What Happens

The script will:
1. ✅ Check Python installation
2. ✅ Install Playwright (no sudo needed)
3. ✅ Install Chromium browser
4. ✅ Set up environment variables
5. ✅ Test headless mode
6. ✅ Show you the results

## Expected Output

You'll see messages like:
```
✅ Python 3.x found
✅ Playwright installed
✅ Chromium browser installed
✅ Headless mode test PASSED!
```

**Important:** If you see "No display detected" - that's CORRECT! ✅
- This means it detected you're on a remote server
- Headless mode is what we want
- No display is needed

## After Setup

Your automation is ready to use! The Next.js API will automatically:
- Detect headless mode
- Use the installed browsers
- Run automation in background

## Troubleshooting

**"playwright: command not found"**
```bash
export PATH=$HOME/.local/bin:$PATH
source ~/.bashrc
```

**"Browser not found"**
```bash
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright
python3 -m playwright install chromium
```

**Still having issues?**
Check the full guide: `SERVER_SETUP.md` or `REMOTE_SERVER_DEPLOYMENT.md`

