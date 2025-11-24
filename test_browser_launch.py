#!/usr/bin/env python3
"""
Test if Playwright browser can actually launch.
This verifies the installation is working correctly.
"""

import sys
import asyncio

print("=" * 80)
print("  Testing Playwright Browser Launch")
print("=" * 80)
print()

try:
    from playwright.async_api import async_playwright
    
    print("✅ Playwright imported successfully")
    print(f"   Browser path: Checking...")
    
    async def test_launch():
        try:
            playwright = await async_playwright().start()
            print(f"✅ Playwright started")
            
            # Get browser path
            chromium_path = playwright.chromium.executable_path
            print(f"✅ Chromium executable found at:")
            print(f"   {chromium_path}")
            
            # Try to launch browser
            print()
            print("🔄 Attempting to launch browser (headless mode)...")
            browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            print("✅ Browser launched successfully!")
            
            # Create a page
            print("🔄 Creating page...")
            page = await browser.new_page()
            print("✅ Page created successfully!")
            
            # Try to navigate
            print("🔄 Testing navigation...")
            await page.goto('https://example.com', timeout=10000)
            print("✅ Navigation successful!")
            
            # Get page title
            title = await page.title()
            print(f"✅ Page loaded: {title}")
            
            # Clean up
            await browser.close()
            await playwright.stop()
            print()
            print("=" * 80)
            print("  ✅ ALL TESTS PASSED - Browser is working correctly!")
            print("=" * 80)
            return True
            
        except Exception as e:
            print()
            print("=" * 80)
            print("  ❌ BROWSER LAUNCH FAILED")
            print("=" * 80)
            print()
            print(f"Error: {str(e)}")
            print()
            print("Error details:")
            import traceback
            traceback.print_exc()
            print()
            print("=" * 80)
            print("  Troubleshooting:")
            print("=" * 80)
            print()
            print("1. Check browser permissions:")
            print(f"   ls -la {chromium_path if 'chromium_path' in locals() else 'N/A'}")
            print()
            print("2. Check if browser is executable:")
            print(f"   test -x {chromium_path if 'chromium_path' in locals() else 'N/A'}")
            print()
            print("3. Try installing browsers again:")
            print("   python3 -m playwright install chromium")
            print()
            print("4. Check system dependencies:")
            print("   python3 check_playwright_installation.py")
            print()
            return False
    
    # Run the test
    result = asyncio.run(test_launch())
    sys.exit(0 if result else 1)
    
except ImportError as e:
    print("❌ Failed to import Playwright")
    print(f"   Error: {str(e)}")
    print()
    print("Solution: Install Playwright")
    print("   pip install playwright")
    print("   python3 -m playwright install chromium")
    sys.exit(1)
    
except Exception as e:
    print("❌ Unexpected error")
    print(f"   Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

