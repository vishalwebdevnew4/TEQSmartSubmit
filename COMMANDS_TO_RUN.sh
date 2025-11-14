#!/bin/bash
# Step-by-step commands to run on remote server
# Copy and paste each section or run entire script

set -e

echo "=========================================="
echo "TEQSmartSubmit - Installation Commands"
echo "=========================================="
echo ""

# Step 1: Verify Python
echo "STEP 1: Verifying Python Installation"
echo "--------------------------------------"
python3 --version
pip3 --version
which python3
echo ""

# Step 2: Check installed packages
echo "STEP 2: Checking Installed Python Packages"
echo "-------------------------------------------"
pip3 list | grep -E '(playwright|pandas|reportlab|redis|SpeechRecognition|pydub|ffmpeg)' || echo "Some packages may be missing"
echo ""

# Step 3: Check Playwright
echo "STEP 3: Checking Playwright"
echo "----------------------------"
python3 -m playwright --version || echo "Playwright check..."
echo ""

# Step 4: Check Chromium browser
echo "STEP 4: Checking Chromium Browser"
echo "----------------------------------"
ls -la ~/.cache/ms-playwright/ 2>/dev/null | head -5 || echo "Checking Chromium installation..."
echo ""

# Step 5: System dependencies (REQUIRES SUDO)
echo "STEP 5: Installing System Dependencies (REQUIRES SUDO)"
echo "------------------------------------------------------"
echo "⚠️  This step requires sudo/root access"
echo "Run this command:"
echo "  sudo python3 -m playwright install-deps chromium"
echo ""
read -p "Do you have sudo access? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo python3 -m playwright install-deps chromium
else
    echo "Skipping system dependencies installation."
    echo "Please contact network team to run: sudo python3 -m playwright install-deps chromium"
fi
echo ""

# Step 6: Final verification
echo "STEP 6: Final Verification"
echo "--------------------------"
python3 -m playwright --version
echo ""

python3 -c "from playwright.sync_api import sync_playwright; print('✅ Playwright import successful')" 2>/dev/null || echo "⚠️  Playwright import test - may need system deps"

echo ""
echo "=========================================="
echo "Installation Check Complete!"
echo "=========================================="
echo ""
echo "If system dependencies are installed, test browser launch:"
echo "  python3 -c \"from playwright.sync_api import sync_playwright; p = sync_playwright(); b = p.start().chromium.launch(headless=True); print('✅ Browser OK'); b.close(); p.stop()\""

