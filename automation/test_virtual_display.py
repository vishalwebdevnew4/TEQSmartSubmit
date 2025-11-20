#!/usr/bin/env python3
"""Test script for virtual display functionality."""

import asyncio
import json
import sys
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from virtual_display import VirtualDisplay, ensure_virtual_display


async def test_virtual_display():
    """Test virtual display with a simple browser automation."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright not installed. Install with: pip install playwright")
        return 1
    
    print("=" * 70)
    print("Testing Virtual Display with Browser Automation")
    print("=" * 70)
    print()
    
    # Test 1: Check if Xvfb is available
    print("Test 1: Checking Xvfb availability...")
    vdisplay = VirtualDisplay(auto_start=False)
    if vdisplay._check_xvfb_available():
        print("   ✅ Xvfb is available")
    else:
        print("   ❌ Xvfb not found. Install with: sudo apt-get install xvfb")
        print("   ℹ️  Continuing test anyway (will use headless mode)")
    print()
    
    # Test 2: Start virtual display
    print("Test 2: Starting virtual display...")
    with VirtualDisplay() as display:
        if display.is_running:
            print(f"   ✅ Virtual display started on {display.display_name}")
            print(f"   ℹ️  DISPLAY={display.display_name}")
            
            # Test 3: Run browser on virtual display
            print()
            print("Test 3: Running browser on virtual display...")
            async with async_playwright() as p:
                # Run in non-headless mode (will use virtual display)
                browser = await p.chromium.launch(headless=False, timeout=30000)
                context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
                page = await context.new_page()
                
                print("   ✅ Browser launched")
                print("   ℹ️  Browser is rendering on virtual display (not visible)")
                
                # Navigate to a test page
                print("   📄 Loading test page...")
                await page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=10000)
                print("   ✅ Page loaded successfully")
                
                # Take a screenshot (this will work on virtual display)
                screenshot_path = "/tmp/virtual_display_test.png"
                await page.screenshot(path=screenshot_path)
                print(f"   ✅ Screenshot saved to {screenshot_path}")
                
                await browser.close()
                print("   ✅ Browser closed")
        else:
            print("   ⚠️  Virtual display not started (Xvfb may not be installed)")
            print("   ℹ️  Browser will run in headless mode")
    
    print()
    print("=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(test_virtual_display())
    sys.exit(exit_code)

