#!/bin/bash
# Server Setup Diagnostic Script
# Run this on your server to check what's available

echo "=================================================================================="
echo "  SERVER SETUP DIAGNOSTIC"
echo "=================================================================================="
echo ""

echo "=== 1. DISPLAY Environment Variable ==="
if [ -z "$DISPLAY" ]; then
    echo "❌ DISPLAY: Not set"
else
    echo "✅ DISPLAY: $DISPLAY"
    # Test if display is accessible
    if command -v xdpyinfo &> /dev/null; then
        if xdpyinfo -display "$DISPLAY" &> /dev/null; then
            echo "   ✅ Display is accessible and working"
        else
            echo "   ⚠️  Display exists but may not be working"
        fi
    fi
fi
echo ""

echo "=== 2. xvfb-run Wrapper (No sudo needed if installed) ==="
if command -v xvfb-run &> /dev/null; then
    XVFB_RUN_PATH=$(which xvfb-run)
    echo "✅ xvfb-run: Found at $XVFB_RUN_PATH"
    echo "   ✅ This will be used automatically by the automation"
else
    echo "❌ xvfb-run: Not found"
    echo "   💡 Ask admin to install: sudo apt-get install xvfb"
fi
echo ""

echo "=== 3. Xvfb Binary ==="
if command -v Xvfb &> /dev/null; then
    XVFB_PATH=$(which Xvfb)
    echo "✅ Xvfb: Found at $XVFB_PATH"
else
    echo "❌ Xvfb: Not found"
    echo "   💡 Ask admin to install: sudo apt-get install xvfb"
fi
echo ""

echo "=== 4. Python Environment ==="
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "✅ Python3: $PYTHON_VERSION"
    PYTHON_PATH=$(which python3)
    echo "   Path: $PYTHON_PATH"
else
    echo "❌ Python3: Not found"
fi
echo ""

echo "=== 5. Playwright Installation ==="
if python3 -c "import playwright" 2>/dev/null; then
    PLAYWRIGHT_VERSION=$(python3 -c "import playwright; print(playwright.__version__)" 2>/dev/null || echo "unknown")
    echo "✅ Playwright: Installed (version: $PLAYWRIGHT_VERSION)"
    
    # Check browsers
    echo ""
    echo "   Browser Check:"
    if python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(p.chromium.executable_path); p.stop()" 2>/dev/null; then
        CHROMIUM_PATH=$(python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(p.chromium.executable_path); p.stop()" 2>/dev/null)
        if [ -f "$CHROMIUM_PATH" ]; then
            echo "   ✅ Chromium: Installed at $CHROMIUM_PATH"
        else
            echo "   ❌ Chromium: Not installed"
        fi
    else
        echo "   ❌ Could not check browsers"
    fi
else
    echo "❌ Playwright: Not installed"
    echo "   💡 Install with: pip install playwright && playwright install chromium"
fi
echo ""

echo "=== 6. System Dependencies (for headless browsers) ==="
MISSING_DEPS=0
for dep in libnss3 libatk1.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2; do
    if dpkg -l | grep -q "^ii.*$dep "; then
        echo "   ✅ $dep: Installed"
    else
        echo "   ❌ $dep: Missing"
        MISSING_DEPS=$((MISSING_DEPS + 1))
    fi
done
if [ $MISSING_DEPS -eq 0 ]; then
    echo "✅ All system dependencies: Installed"
else
    echo "⚠️  $MISSING_DEPS dependency(ies) missing"
    echo "   💡 Ask admin to install: sudo apt-get install libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2"
fi
echo ""

echo "=================================================================================="
echo "  SUMMARY & RECOMMENDATIONS"
echo "=================================================================================="
echo ""

# Determine what will work
if [ -n "$DISPLAY" ]; then
    echo "✅ SOLUTION: Using existing DISPLAY ($DISPLAY)"
    echo "   The automation will use your existing display session"
elif command -v xvfb-run &> /dev/null; then
    echo "✅ SOLUTION: xvfb-run is available"
    echo "   The automation will automatically use xvfb-run wrapper"
    echo "   No additional setup needed!"
elif command -v Xvfb &> /dev/null; then
    echo "✅ SOLUTION: Xvfb is installed"
    echo "   The automation will start Xvfb automatically"
else
    echo "❌ ISSUE: No display solution available"
    echo ""
    echo "   OPTIONS:"
    echo "   1. Ask server admin to install: sudo apt-get install xvfb"
    echo "   2. Use SSH with X11 forwarding: ssh -X user@server"
    echo "   3. Set up a persistent Xvfb session (requires admin help)"
fi
echo ""
echo "=================================================================================="

