#!/bin/bash
# Quick test script to verify remote installation

echo "================================================================================"
echo "Testing Remote Server Installation"
echo "================================================================================"
echo ""

# Set environment
export PLAYWRIGHT_BROWSERS_PATH="$HOME/.cache/ms-playwright"
export TEQ_PLAYWRIGHT_HEADLESS=true
export HEADLESS=true

echo "Environment:"
echo "  Python: $(python3 --version)"
echo "  Playwright: $(python3 -m playwright --version 2>/dev/null || echo 'Not found')"
echo "  Browser path: $PLAYWRIGHT_BROWSERS_PATH"
echo "  Browsers installed: $(ls -d $PLAYWRIGHT_BROWSERS_PATH/chromium-* 2>/dev/null | wc -l)"
echo ""

# Test headless mode
echo "Testing headless mode..."
python3 -c "
import asyncio
import os
import sys
from playwright.async_api import async_playwright

os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/.cache/ms-playwright')

async def test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, timeout=60000)
            page = await browser.new_page()
            await page.goto('https://example.com', timeout=30000)
            title = await page.title()
            print(f'✅ SUCCESS! Page loaded: {title}')
            await browser.close()
            return True
    except Exception as e:
        print(f'❌ ERROR: {e}')
        return False

success = asyncio.run(test())
sys.exit(0 if success else 1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation verified! Everything works!"
    echo "✅ Your automation is ready to use!"
else
    echo ""
    echo "❌ Test failed. Check the error above."
fi

