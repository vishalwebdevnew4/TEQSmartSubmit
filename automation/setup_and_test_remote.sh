#!/bin/bash
# TEQSmartSubmit Remote Server Setup and Test Script
# This script installs all dependencies (without sudo) and tests headless mode

set -e  # Exit on error

echo "================================================================================"
echo "TEQSmartSubmit Remote Server Setup and Test"
echo "================================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "run_submission.py" ]; then
    print_error "Please run this script from the automation directory"
    print_info "Usage: cd /var/www/html/TEQSmartSubmit/automation && bash setup_and_test_remote.sh"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AUTOMATION_DIR="$PROJECT_ROOT/automation"

echo "Project root: $PROJECT_ROOT"
echo "Automation dir: $AUTOMATION_DIR"
echo ""

# Step 1: Check Python
print_info "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Step 2: Install Python packages (user level)
print_info "Step 2: Installing Python packages (user level, no sudo)..."
pip3 install --user playwright 2>&1 | grep -v "already satisfied" || true

# Add user bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$HOME/.local/bin:$PATH"
    echo "" >> ~/.bashrc
    echo "# Playwright user installation" >> ~/.bashrc
    echo "export PATH=\$HOME/.local/bin:\$PATH" >> ~/.bashrc
    print_info "Added ~/.local/bin to PATH (added to ~/.bashrc)"
fi

# Check if playwright is accessible
if ! python3 -m playwright --version &> /dev/null; then
    print_error "Playwright installation failed or not accessible"
    print_info "Trying to add PYTHONPATH..."
    export PYTHONPATH="$HOME/.local/lib/python3.*/site-packages:$PYTHONPATH"
fi

PLAYWRIGHT_VERSION=$(python3 -m playwright --version 2>/dev/null || echo "unknown")
print_success "Playwright installed: $PLAYWRIGHT_VERSION"

# Step 3: Set browser path and install Chromium
print_info "Step 3: Setting up Playwright browsers (user level)..."
export PLAYWRIGHT_BROWSERS_PATH="$HOME/.cache/ms-playwright"

# Add to bashrc if not already there
if ! grep -q "PLAYWRIGHT_BROWSERS_PATH" ~/.bashrc 2>/dev/null; then
    echo "export PLAYWRIGHT_BROWSERS_PATH=\$HOME/.cache/ms-playwright" >> ~/.bashrc
    print_info "Added PLAYWRIGHT_BROWSERS_PATH to ~/.bashrc"
fi

# Create cache directory if it doesn't exist
mkdir -p "$HOME/.cache/ms-playwright"

print_info "Installing Chromium browser (this may take a few minutes)..."
python3 -m playwright install chromium 2>&1 | tail -5

if [ $? -eq 0 ]; then
    print_success "Chromium browser installed successfully"
else
    print_error "Chromium installation failed"
    exit 1
fi

# Step 4: Install optional CAPTCHA dependencies
print_info "Step 4: Installing optional CAPTCHA solving dependencies..."
if [ -f "requirements_captcha.txt" ]; then
    pip3 install --user -r requirements_captcha.txt 2>&1 | grep -v "already satisfied" || true
    print_success "CAPTCHA dependencies installed"
else
    print_info "requirements_captcha.txt not found, skipping CAPTCHA dependencies"
fi

# Step 5: Make scripts executable
print_info "Step 5: Setting script permissions..."
chmod +x "$AUTOMATION_DIR"/*.py 2>/dev/null || true
print_success "Scripts are executable"

# Step 6: Create test script
print_info "Step 6: Creating headless mode test script..."
cat > "$AUTOMATION_DIR/test_remote_headless.py" << 'TESTSCRIPT'
#!/usr/bin/env python3
"""
Quick test script for headless mode on remote server
"""
import asyncio
import sys
import os
from pathlib import Path

# Set browser path
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/.cache/ms-playwright')
os.environ['TEQ_PLAYWRIGHT_HEADLESS'] = 'true'
os.environ['HEADLESS'] = 'true'

# Add automation directory to path
_script_dir = Path(__file__).parent.absolute()
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

async def test_headless():
    try:
        from playwright.async_api import async_playwright
        
        print("🚀 Testing headless mode...")
        print(f"   Browser path: {os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'default')}")
        print(f"   Headless mode: True")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, timeout=60000)
            print("   ✅ Browser launched successfully")
            
            page = await browser.new_page()
            print("   ✅ Page created")
            
            await page.goto('https://example.com', timeout=30000)
            print("   ✅ Page loaded")
            
            title = await page.title()
            print(f"   ✅ Page title: {title}")
            
            await browser.close()
            print("   ✅ Browser closed")
        
        print("\n✅ Headless mode test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Headless mode test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_headless())
    sys.exit(0 if success else 1)
TESTSCRIPT

chmod +x "$AUTOMATION_DIR/test_remote_headless.py"
print_success "Test script created"

# Step 7: Run basic headless test
print_info "Step 7: Running basic headless mode test..."
echo ""
echo "================================================================================"
echo "Running Headless Mode Test"
echo "================================================================================"
echo ""

cd "$AUTOMATION_DIR"
python3 test_remote_headless.py

if [ $? -eq 0 ]; then
    print_success "Basic headless test PASSED!"
else
    print_error "Basic headless test FAILED"
    print_info "This might be due to missing system libraries. Check the error above."
fi

# Step 8: Test with actual form submission (optional)
print_info "Step 8: Testing with actual form submission..."
echo ""
echo "================================================================================"
echo "Testing Form Submission (Headless Mode)"
echo "================================================================================"
echo ""

# Check if test_headless_local.py exists
if [ -f "test_headless_local.py" ]; then
    print_info "Running full form submission test..."
    print_info "This will test: https://www.seoily.com/contact-us"
    echo ""
    
    # Set environment for headless
    export TEQ_FORCE_HEADLESS=true
    export HEADLESS=true
    export DISPLAY=""
    
    timeout 300 python3 test_headless_local.py 2>&1 | tail -50
    
    if [ $? -eq 0 ]; then
        print_success "Form submission test completed!"
    else
        print_error "Form submission test had errors (check output above)"
        print_info "This is expected if CAPTCHA solving fails - form filling should work"
    fi
else
    print_info "test_headless_local.py not found, skipping form submission test"
fi

# Step 9: Summary
echo ""
echo "================================================================================"
echo "Setup and Test Summary"
echo "================================================================================"
echo ""

print_info "Installation location:"
echo "   Python packages: $HOME/.local/lib/python3.*/site-packages"
echo "   Playwright browsers: $HOME/.cache/ms-playwright"
echo ""

print_info "Environment variables added to ~/.bashrc:"
echo "   PATH=\$HOME/.local/bin:\$PATH"
echo "   PLAYWRIGHT_BROWSERS_PATH=\$HOME/.cache/ms-playwright"
echo ""

print_info "To use in your scripts, ensure these are set:"
echo "   export PATH=\$HOME/.local/bin:\$PATH"
echo "   export PLAYWRIGHT_BROWSERS_PATH=\$HOME/.cache/ms-playwright"
echo "   export TEQ_PLAYWRIGHT_HEADLESS=true"
echo ""

print_success "Setup complete!"
print_info "To reload environment: source ~/.bashrc"
print_info "To test again: cd $AUTOMATION_DIR && python3 test_remote_headless.py"
echo ""

