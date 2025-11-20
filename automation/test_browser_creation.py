#!/usr/bin/env python3
"""
Test browser creation and page initialization.
This test verifies that the browser and page are properly created when not using browser reuse.
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

async def test_browser_creation():
    """Test that browser and page are created successfully."""
    print("🧪 Testing browser creation...", file=sys.stderr)
    
    url = "https://marketing-digital.in/contact/"
    template_path = Path(__file__).parent / "test_single_tab_mode.json"
    
    if not template_path.exists():
        # Create a simple template for testing
        import json
        template = {
            "reuse_browser": False,
            "use_auto_detect": True,
            "fields": [
                {"name": "name", "value": "Test User"},
                {"name": "email", "value": "test@example.com"},
                {"name": "message", "value": "Test message"}
            ]
        }
        template_path.write_text(json.dumps(template, indent=2))
        print(f"✅ Created test template at {template_path}", file=sys.stderr)
    
    try:
        async with async_playwright() as p:
            print("📦 Playwright initialized", file=sys.stderr)
            
            # Check if we should run in headless mode
            import os
            has_display = os.getenv("DISPLAY") is not None and os.getenv("DISPLAY") != ""
            is_container = os.path.exists("/.dockerenv") or os.getenv("container") is not None
            
            if has_display and not is_container:
                headless = False
                print("🖥️  Display detected - running with visible browser", file=sys.stderr)
            else:
                headless = True
                print("🖥️  No display detected - running in HEADLESS mode", file=sys.stderr)
            
            # Launch browser
            print("🚀 Launching browser...", file=sys.stderr)
            try:
                browser = await p.chromium.launch(headless=headless, timeout=180000)
                print("✅ Browser launched successfully", file=sys.stderr)
            except Exception as e:
                print(f"❌ Failed to launch browser: {str(e)[:200]}", file=sys.stderr)
                print("   💡 Make sure Playwright browsers are installed: playwright install chromium", file=sys.stderr)
                return False
            
            # Create context
            print("📄 Creating context...", file=sys.stderr)
            try:
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    storage_state=None,
                )
                context.set_default_timeout(180000)
                print("✅ Context created successfully", file=sys.stderr)
            except Exception as e:
                print(f"❌ Failed to create context: {str(e)[:200]}", file=sys.stderr)
                await browser.close()
                return False
            
            # Create page
            print("📄 Creating page...", file=sys.stderr)
            try:
                page = await context.new_page()
                page.set_default_timeout(180000)
                print("✅ Page created successfully", file=sys.stderr)
            except Exception as e:
                print(f"❌ Failed to create page: {str(e)[:200]}", file=sys.stderr)
                await context.close()
                await browser.close()
                return False
            
            # Navigate to URL
            print(f"🌐 Navigating to {url}...", file=sys.stderr)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                print("✅ Navigation successful", file=sys.stderr)
            except Exception as e:
                print(f"❌ Failed to navigate: {str(e)[:200]}", file=sys.stderr)
                await page.close()
                await context.close()
                await browser.close()
                return False
            
            # Verify page is accessible
            print("🔍 Verifying page is accessible...", file=sys.stderr)
            try:
                title = await page.title()
                print(f"✅ Page title: {title[:50]}", file=sys.stderr)
            except Exception as e:
                print(f"❌ Failed to access page: {str(e)[:200]}", file=sys.stderr)
                await page.close()
                await context.close()
                await browser.close()
                return False
            
            # Cleanup
            print("🧹 Cleaning up...", file=sys.stderr)
            await page.close()
            await context.close()
            await browser.close()
            print("✅ Cleanup complete", file=sys.stderr)
            
            print("✅ All tests passed!", file=sys.stderr)
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)[:200]}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_browser_creation())
    sys.exit(0 if success else 1)

