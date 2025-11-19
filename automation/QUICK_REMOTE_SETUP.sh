#!/bin/bash
# Quick one-liner setup script for remote server
# Usage: curl -sSL https://your-server.com/setup.sh | bash
# Or: wget -qO- https://your-server.com/setup.sh | bash

set -e

echo "🚀 Quick Setup for TEQSmartSubmit (No Sudo Required)"
echo ""

# Install Playwright
pip3 install --user playwright

# Set paths
export PATH="$HOME/.local/bin:$PATH"
export PLAYWRIGHT_BROWSERS_PATH="$HOME/.cache/ms-playwright"

# Add to bashrc
if ! grep -q "PLAYWRIGHT_BROWSERS_PATH" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# Playwright" >> ~/.bashrc
    echo "export PATH=\$HOME/.local/bin:\$PATH" >> ~/.bashrc
    echo "export PLAYWRIGHT_BROWSERS_PATH=\$HOME/.cache/ms-playwright" >> ~/.bashrc
fi

# Install browser
python3 -m playwright install chromium

# Test
python3 -c "
import asyncio
from playwright.async_api import async_playwright
import os
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/.cache/ms-playwright')

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://example.com')
        print('✅ Headless mode works!')
        await browser.close()

asyncio.run(test())
"

echo ""
echo "✅ Setup complete! Run: source ~/.bashrc"

