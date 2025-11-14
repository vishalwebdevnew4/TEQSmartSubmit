# Step-by-Step Commands for Remote Server Setup

## Quick Reference - All Commands

### Step 1: Connect to Server
```bash
ssh -p 3129 teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com
# Password: XFho65rfr@uj()7y8
```

### Step 2: Verify Python Installation
```bash
python3 --version
pip3 --version
which python3
```

### Step 3: Check Current Directory
```bash
pwd
cd /var/www/html/TEQSmartSubmit || cd ~/TEQSmartSubmit || cd /var/www/projects/teqsmartsubmit/teqsmartsubmit/ || echo "Current directory: $(pwd)"
```

### Step 4: Verify Python Packages (Already Installed)
```bash
pip3 list | grep -E '(playwright|pandas|reportlab|redis|SpeechRecognition|pydub|ffmpeg)'
python3 -m playwright --version
```

### Step 5: Install System Dependencies (REQUIRES SUDO)
```bash
# Option 1: Using Playwright (Recommended)
sudo python3 -m playwright install-deps chromium

# Option 2: Manual Package Installation
sudo apt-get update
sudo apt-get install -y libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 libxshmfence1 libxss1 libxtst6
```

### Step 6: Verify Installation Complete
```bash
# Check Playwright
python3 -m playwright --version

# Test Playwright import
python3 -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"

# List all installed packages
pip3 list | grep -E '(playwright|pandas|reportlab|redis|SpeechRecognition|pydub|ffmpeg)'

# Check Chromium browser
ls -la ~/.cache/ms-playwright/chromium-1194/ 2>/dev/null || echo "Checking Chromium..."
```

### Step 7: Test Python Script Execution
```bash
# Navigate to project directory
cd /var/www/html/TEQSmartSubmit || cd /var/www/projects/teqsmartsubmit/teqsmartsubmit/ || cd ~/TEQSmartSubmit

# Test if automation script can run (basic check)
python3 -c "import sys; sys.path.insert(0, './automation'); import run_submission; print('Script import OK')" 2>&1 | head -5
```

---

## Detailed Step-by-Step Instructions

### 🔵 Step 1: Connect to Remote Server
```bash
ssh -p 3129 teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com
```
When prompted, enter password: `XFho65rfr@uj()7y8`

**Expected Output:**
```
Welcome to Ubuntu 22.04.4 LTS
teqsmartsftpuser@teqtopserver:~$
```

---

### 🔵 Step 2: Verify Python is Installed
```bash
python3 --version
```

**Expected Output:**
```
Python 3.10.12
```

**If Python is not found, install it:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip
```

---

### 🔵 Step 3: Check pip Installation
```bash
pip3 --version
```

**Expected Output:**
```
pip 22.0.2 from /usr/lib/python3/dist-packages/pip (python 3.10)
```

---

### 🔵 Step 4: Navigate to Project Directory
```bash
# Try common paths
cd /var/www/html/TEQSmartSubmit 2>/dev/null || \
cd /var/www/projects/teqsmartsubmit/teqsmartsubmit/ 2>/dev/null || \
cd ~/TEQSmartSubmit 2>/dev/null || \
pwd
```

---

### 🔵 Step 5: Verify Installed Python Packages
```bash
pip3 list | grep -E '(playwright|pandas|reportlab|redis|SpeechRecognition|pydub|ffmpeg)'
```

**Expected Output:**
```
ffmpeg-python          0.2.0
playwright             1.56.0
pydub                  0.25.1
SpeechRecognition      3.14.3
pandas                 (version)
reportlab              (version)
redis                  (version)
```

---

### 🔵 Step 6: Check Playwright Installation
```bash
python3 -m playwright --version
```

**Expected Output:**
```
Version 1.56.0
```

---

### 🔵 Step 7: Check Chromium Browser Installation
```bash
ls -la ~/.cache/ms-playwright/ | head -10
```

**Expected Output:**
```
drwxrwxr-x  ... chromium-1194
drwxrwxr-x  ... chromium_headless_shell-1194
```

---

### 🔴 Step 8: Install System Dependencies (REQUIRES SUDO - THIS IS WHAT NETWORK TEAM NEEDS TO DO)

**Option A: Using Playwright Command (Recommended)**
```bash
sudo python3 -m playwright install-deps chromium
```

**Option B: Manual Installation**
```bash
sudo apt-get update
sudo apt-get install -y \
  libasound2 \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libatspi2.0-0 \
  libcups2 \
  libdbus-1-3 \
  libdrm2 \
  libgbm1 \
  libgtk-3-0 \
  libnspr4 \
  libnss3 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxkbcommon0 \
  libxrandr2 \
  libxshmfence1 \
  libxss1 \
  libxtst6
```

**Note:** You'll be prompted for sudo password. Enter the root/sudo password for the server.

---

### 🔵 Step 9: Verify System Dependencies Installed
```bash
# This should NOT show warnings anymore
python3 -m playwright --version
```

**If successful, no warnings will appear.**

---

### 🔵 Step 10: Final Verification
```bash
# Test Playwright import
python3 -c "from playwright.sync_api import sync_playwright; print('✅ Playwright import successful')"

# Test browser launch (optional - takes a few seconds)
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    print('✅ Browser launch successful')
    browser.close()
"
```

**Expected Output:**
```
✅ Playwright import successful
✅ Browser launch successful
```

---

### 🔵 Step 11: Verify All Packages
```bash
# Complete package list
pip3 list | grep -E '(playwright|pandas|reportlab|redis|SpeechRecognition|pydub|ffmpeg)'

# Python version
python3 --version

# Playwright version
python3 -m playwright --version

# Python executable path
python3 -c "import sys; print('Python path:', sys.executable)"
```

---

## Troubleshooting Commands

### If Python packages are missing:
```bash
# Install Playwright
pip3 install --user playwright
python3 -m playwright install chromium

# Install automation packages
pip3 install --user pandas reportlab redis

# Install CAPTCHA solver packages
pip3 install --user SpeechRecognition pydub ffmpeg-python
```

### If system dependencies fail:
```bash
# Check what's missing
python3 -m playwright install-deps chromium 2>&1 | grep -i "missing\|error"

# Try individual package installation
sudo apt-get update
sudo apt-get install -y libasound2
sudo apt-get install -y libgtk-3-0
# ... (install others individually if needed)
```

### Check PATH issues:
```bash
# Check Python location
which python3
python3 -c "import sys; print(sys.executable)"

# Check pip location
which pip3
pip3 --version

# Add user bin to PATH if needed (add to ~/.bashrc)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Quick Copy-Paste Script (All Commands Together)

```bash
# Copy and paste this entire block into SSH session

# Step 1: Verify Python
echo "=== Checking Python ==="
python3 --version
pip3 --version

# Step 2: Check installed packages
echo "=== Checking Packages ==="
pip3 list | grep -E '(playwright|pandas|reportlab|redis|SpeechRecognition|pydub|ffmpeg)'

# Step 3: Check Playwright
echo "=== Checking Playwright ==="
python3 -m playwright --version

# Step 4: Install system dependencies (requires sudo)
echo "=== Installing System Dependencies (REQUIRES SUDO) ==="
sudo python3 -m playwright install-deps chromium

# Step 5: Final verification
echo "=== Final Verification ==="
python3 -c "from playwright.sync_api import sync_playwright; print('✅ Playwright OK')"
python3 -m playwright --version
```

---

## Summary

✅ **Completed Automatically:**
1. Python 3.10.12 - Installed
2. Playwright 1.56.0 - Installed
3. Chromium browser - Installed
4. Python packages - All installed

⏳ **Needs Network Team:**
- Run: `sudo python3 -m playwright install-deps chromium`
- Or install system packages manually (see Step 8)

✅ **After System Deps Installed:**
- Everything should work
- Test with verification commands

---

**Total Time Required:** < 5 minutes (once you have sudo access)

