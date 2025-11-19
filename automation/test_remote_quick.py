#!/usr/bin/env python3
"""Quick test for remote server headless mode"""
import asyncio
import os
import sys
from pathlib import Path

# Set browser path
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/.cache/ms-playwright')
os.environ['TEQ_PLAYWRIGHT_HEADLESS'] = 'true'
os.environ['HEADLESS'] = 'true'

# Add automation directory to path
_script_dir = Path(__file__).parent.absolute()
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

async def test():
    try:
        from playwright.async_api import async_playwright
        
        print("🚀 Testing headless mode on remote server...")
        print(f"   Browser path: {os.environ.get('PLAYWRIGHT_BROWSERS_PATH')}")
        print(f"   Python: {sys.version.split()[0]}")
        print("")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, timeout=60000)
            print("   ✅ Browser launched (headless)")
            
            page = await browser.new_page()
            await page.goto('https://example.com', timeout=30000)
            title = await page.title()
            print(f"   ✅ Page loaded: {title}")
            
            await browser.close()
            print("   ✅ Browser closed")
        
        print("\n✅ SUCCESS! Headless mode works perfectly!")
        print("   ✅ No display needed - everything is working!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
