# Server Setup Guide for Headless Mode

This guide covers everything you need to install on your remote server to run TEQSmartSubmit automation in headless mode.

## Prerequisites

- Linux server (Ubuntu/Debian recommended)
- Python 3.8 or higher
- Root or sudo access (for system packages)

## Step 1: Install System Dependencies

Playwright requires system libraries to run Chromium in headless mode. Install them:

### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
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
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    libu2f-udev \
    libvulkan1
```

### CentOS/RHEL:
```bash
sudo yum install -y \
    python3 \
    python3-pip \
    wget \
    alsa-lib \
    atk \
    cups-libs \
    gtk3 \
    ipa-gothic-fonts \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    xorg-x11-fonts-100dpi \
    xorg-x11-fonts-75dpi \
    xorg-x11-utils
```

## Step 2: Install Python Dependencies

Navigate to your project directory and install Python packages:

**With sudo (system-wide):**
```bash
cd /var/www/html/TEQSmartSubmit

# Install Playwright and other dependencies
pip3 install playwright

# Install additional packages for CAPTCHA solving (if needed)
pip3 install speech-recognition pydub

# Or install from requirements file if available
if [ -f automation/requirements_captcha.txt ]; then
    pip3 install -r automation/requirements_captcha.txt
fi
```

**Without sudo (user-level):**
```bash
cd /var/www/html/TEQSmartSubmit

# Install to user directory (no sudo needed)
pip3 install --user playwright

# Add to PATH (add to ~/.bashrc)
export PATH=$HOME/.local/bin:$PATH

# Install additional packages for CAPTCHA solving (if needed)
pip3 install --user speech-recognition pydub
```

## Step 3: Install Playwright Browsers

This is critical - Playwright needs to download the Chromium browser:

**With sudo (system-wide):**
```bash
# Install Chromium browser for Playwright
python3 -m playwright install chromium

# Install system dependencies (requires sudo)
python3 -m playwright install-deps chromium
```

**Without sudo (user-level):**
```bash
# Set custom browser path (add to ~/.bashrc)
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright

# Install Chromium to user directory (no sudo needed)
python3 -m playwright install chromium

# Note: install-deps requires sudo, but Chromium will work without it
# If you get library errors, see "Installation Without Sudo" section below
```

## Step 4: Verify Installation

Test that everything works:

```bash
cd /var/www/html/TEQSmartSubmit/automation

# Test headless mode
python3 -c "
from playwright.async_api import async_playwright
import asyncio

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://example.com')
        print('✅ Headless mode works!')
        await browser.close()

asyncio.run(test())
"
```

## Step 5: Set Environment Variables

Add these to your server's environment (`.env` file or system environment):

```bash
# Force headless mode (optional - will auto-detect if not set)
export TEQ_PLAYWRIGHT_HEADLESS=true
# or
export HEADLESS=true

# If you want to force headless even with display
export TEQ_FORCE_HEADLESS=true
```

## Step 6: Permissions

Ensure the web server user can execute Python scripts:

```bash
# Make scripts executable
chmod +x /var/www/html/TEQSmartSubmit/automation/*.py

# If using a specific user (e.g., www-data, nginx)
sudo chown -R www-data:www-data /var/www/html/TEQSmartSubmit
```

## Troubleshooting

### Issue: "playwright: command not found"
**Solution:** Use `python3 -m playwright` instead of just `playwright`

### Issue: "Browser not found"
**Solution:** Run `python3 -m playwright install chromium` again

### Issue: "Shared memory error"
**Solution:** Add `--disable-dev-shm-usage` flag (already in code) or increase `/dev/shm`:
```bash
sudo mount -o remount,size=2G /dev/shm
```

### Issue: "Permission denied"
**Solution:** Check file permissions and user ownership:
```bash
ls -la /var/www/html/TEQSmartSubmit/automation/
chmod +x /var/www/html/TEQSmartSubmit/automation/*.py
```

### Issue: "Missing system dependencies"
**Solution:** Run `python3 -m playwright install-deps chromium` to install missing libraries

## Quick Installation Script

Save this as `setup_server.sh` and run it:

```bash
#!/bin/bash
set -e

echo "🚀 Setting up TEQSmartSubmit server for headless mode..."

# Update system
sudo apt-get update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv wget gnupg ca-certificates \
    fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 \
    libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 \
    libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
    xdg-utils libu2f-udev libvulkan1

# Install Python packages
echo "🐍 Installing Python packages..."
pip3 install playwright

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install chromium
python3 -m playwright install-deps chromium

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x /var/www/html/TEQSmartSubmit/automation/*.py

echo "✅ Setup complete! Test with: python3 -m playwright --version"
```

## Verification Checklist

- [ ] Python 3.8+ installed: `python3 --version`
- [ ] Playwright installed: `python3 -m playwright --version`
- [ ] Chromium installed: `python3 -m playwright install chromium`
- [ ] System dependencies installed: `python3 -m playwright install-deps chromium`
- [ ] Scripts are executable: `ls -la automation/*.py`
- [ ] Headless test passes (see Step 4)

## Additional Notes

1. **Memory Requirements:** Headless Chromium needs at least 512MB RAM per instance
2. **Disk Space:** Chromium browser takes ~300MB disk space
3. **Network:** First run downloads browsers (~200MB), ensure good connection
4. **User Permissions:** If running as non-root, ensure user has access to `/tmp` and browser cache directory

## Installation Without Sudo

If you don't have sudo/root access, you can still install most dependencies at the user level:

### Step 1: Install Python Packages (User Level)

```bash
# Install Playwright to user directory
pip3 install --user playwright

# Add user Python bin to PATH (add to ~/.bashrc or ~/.profile)
export PATH=$HOME/.local/bin:$PATH
export PYTHONPATH=$HOME/.local/lib/python3.*/site-packages:$PYTHONPATH

# Reload shell configuration
source ~/.bashrc  # or source ~/.profile
```

### Step 2: Install Playwright Browsers (User Level)

```bash
# Set custom browser path (add to ~/.bashrc)
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright

# Install Chromium to user directory
python3 -m playwright install chromium

# Verify installation
python3 -m playwright --version
```

### Step 3: Handle Missing System Libraries

Without sudo, you can't install system libraries. However, Playwright will work with most missing libraries. If you encounter errors:

**Option A: Use Conda/Miniconda (Recommended for no-sudo)**
```bash
# Download and install Miniconda (no sudo needed)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
source $HOME/miniconda3/bin/activate

# Install Playwright via conda
conda install -c conda-forge playwright
playwright install chromium
```

**Option B: Use Pre-built Binaries**
Some libraries can be downloaded as binaries to user directory:
```bash
# Create local lib directory
mkdir -p $HOME/local/lib
export LD_LIBRARY_PATH=$HOME/local/lib:$LD_LIBRARY_PATH
```

**Option C: Contact Your Hosting Provider**
Ask them to install these packages (they usually do for shared hosting):
- `libnss3`, `libatk1.0-0`, `libatk-bridge2.0-0`, `libcups2`, `libdrm2`, `libgbm1`, `libxkbcommon0`, `libxcomposite1`, `libxdamage1`, `libxfixes3`, `libxrandr2`, `libasound2`

### Step 4: Test Installation (No Sudo)

```bash
cd /var/www/html/TEQSmartSubmit/automation

# Test headless mode
python3 -c "
from playwright.async_api import async_playwright
import asyncio
import os

# Set browser path
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/.cache/ms-playwright')

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://example.com')
        print('✅ Headless mode works without sudo!')
        await browser.close()

asyncio.run(test())
"
```

### Step 5: Update Environment Variables

Add to your `~/.bashrc` or project `.env`:
```bash
# User-level Playwright setup
export PATH=$HOME/.local/bin:$PATH
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright
export PYTHONPATH=$HOME/.local/lib/python3.*/site-packages:$PYTHONPATH

# Force headless mode
export TEQ_PLAYWRIGHT_HEADLESS=true
```

### Troubleshooting (No Sudo)

**Issue: "ModuleNotFoundError: No module named 'playwright'"**
```bash
# Solution: Add user site-packages to Python path
export PYTHONPATH=$HOME/.local/lib/python3.*/site-packages:$PYTHONPATH
# Or use: python3 -m pip install --user playwright
```

**Issue: "Browser not found"**
```bash
# Solution: Set custom browser path
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright
python3 -m playwright install chromium
```

**Issue: "Missing shared libraries"**
```bash
# Check which libraries are missing
ldd ~/.cache/ms-playwright/chromium-*/chrome | grep "not found"

# If many are missing, contact hosting provider or use Conda
```

**Issue: "Permission denied"**
```bash
# Ensure you own the directories
chmod -R u+w $HOME/.cache/ms-playwright
chmod -R u+w $HOME/.local
```

### Quick No-Sudo Installation Script

```bash
#!/bin/bash
set -e

echo "🚀 Setting up TEQSmartSubmit WITHOUT sudo..."

# Install Python packages to user directory
echo "📦 Installing Python packages..."
pip3 install --user playwright

# Set environment variables
export PATH=$HOME/.local/bin:$PATH
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright

# Add to bashrc
if ! grep -q "PLAYWRIGHT_BROWSERS_PATH" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Playwright user installation" >> ~/.bashrc
    echo "export PATH=\$HOME/.local/bin:\$PATH" >> ~/.bashrc
    echo "export PLAYWRIGHT_BROWSERS_PATH=\$HOME/.cache/ms-playwright" >> ~/.bashrc
fi

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install chromium

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x /var/www/html/TEQSmartSubmit/automation/*.py

echo "✅ Setup complete (no sudo required)!"
echo "⚠️  Note: Some system libraries may be missing. If you get errors, contact your hosting provider."
```

## Automated Setup Script

We've created an automated setup and test script that does everything for you:

### Full Setup and Test Script

```bash
cd /var/www/html/TEQSmartSubmit/automation
bash setup_and_test_remote.sh
```

This script will:
1. ✅ Check Python installation
2. ✅ Install Playwright (user level, no sudo)
3. ✅ Install Chromium browser
4. ✅ Set up environment variables
5. ✅ Install optional CAPTCHA dependencies
6. ✅ Run headless mode test
7. ✅ Test form submission (optional)

### Quick One-Liner Setup

For a minimal setup, use the quick script:

```bash
cd /var/www/html/TEQSmartSubmit/automation
bash QUICK_REMOTE_SETUP.sh
```

Or copy-paste this one-liner:
```bash
pip3 install --user playwright && export PATH="$HOME/.local/bin:$PATH" && export PLAYWRIGHT_BROWSERS_PATH="$HOME/.cache/ms-playwright" && python3 -m playwright install chromium && echo "export PATH=\$HOME/.local/bin:\$PATH" >> ~/.bashrc && echo "export PLAYWRIGHT_BROWSERS_PATH=\$HOME/.cache/ms-playwright" >> ~/.bashrc && echo "✅ Setup complete! Run: source ~/.bashrc"
```

## Production Recommendations

1. **Use a process manager** (PM2, systemd) to manage the Next.js app
2. **Set up logging** to monitor automation runs
3. **Configure resource limits** to prevent memory issues
4. **Use a reverse proxy** (Nginx) for the Next.js app
5. **Monitor disk space** - browser cache can grow over time
6. **For no-sudo setups:** Consider using Conda/Miniconda for better library management
7. **Use the automated setup script** (`setup_and_test_remote.sh`) for easy installation

