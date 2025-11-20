#!/usr/bin/env python3
"""Test multiple sites with single tab mode (browser reuse)."""

import asyncio
import sys
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from browser_manager import BrowserManager
from run_submission import run_submission


async def test_multiple_sites():
    """Test browser reuse with multiple real contact form URLs."""
    print("=" * 70)
    print("Testing Multiple Sites with Single Tab Mode")
    print("=" * 70)
    print()
    
    # Test URLs from user
    test_urls = [
        "https://www.seoily.com/contact-us",
        "https://www.sagetitans.com/contact-us.html",
        "https://marketing-digital.in/contact/",
        "https://www.onlinechandigarh.com/contact-us.html",
        "https://360digiexpertz.com/contact-us/",
        "https://www.smart-minds.co.in/contact.php",
        "https://adroitors.com/contact-us/",
    ]
    
    template_path = Path(__file__).parent / "test_single_tab_mode.json"
    
    # Create browser manager (visible browser, no virtual display)
    print("1. Creating browser manager...")
    browser_manager = BrowserManager(
        headless=False,           # Visible browser so you can see it
        use_virtual_display=False  # Use real display
    )
    print("   ✅ Browser manager created")
    print()
    
    results = []
    
    try:
        # Start browser once
        print("2. Starting browser (this will create a single tab)...")
        await browser_manager.start()
        print("   ✅ Browser started - you should see a browser window open!")
        print()
        
        # Process each URL
        for i, url in enumerate(test_urls, 1):
            print(f"{'=' * 70}")
            print(f"3.{i} Processing URL {i}/{len(test_urls)}: {url}")
            print(f"{'=' * 70}")
            
            try:
                result = await run_submission(
                    url=url,
                    template_path=template_path,
                    browser_manager=browser_manager
                )
                
                status = result.get('status', 'unknown')
                message = result.get('message', '')
                print(f"\n   ✅ URL {i} completed")
                print(f"      Status: {status}")
                print(f"      Message: {message[:100]}")
                
                results.append({
                    "url": url,
                    "status": status,
                    "message": message
                })
                
            except Exception as e:
                error_msg = str(e)
                print(f"\n   ❌ URL {i} failed: {error_msg[:200]}")
                results.append({
                    "url": url,
                    "status": "error",
                    "message": error_msg[:200]
                })
            
            # Small delay between URLs
            if i < len(test_urls):
                print("\n   ⏳ Waiting 3 seconds before next URL...\n")
                await asyncio.sleep(3)
        
        print()
        print("=" * 70)
        print("✅ Test completed!")
        print("=" * 70)
        print()
        print("Summary:")
        print(f"  - Browser started: Once")
        print(f"  - Tab created: Once")
        print(f"  - URLs processed: {len(test_urls)}")
        print(f"  - Tab reused: Yes (same tab, different URLs)")
        print()
        print("Results:")
        success_count = sum(1 for r in results if r.get('status') == 'success')
        error_count = sum(1 for r in results if r.get('status') == 'error')
        print(f"  - Success: {success_count}/{len(test_urls)}")
        print(f"  - Errors: {error_count}/{len(test_urls)}")
        print()
        for i, result in enumerate(results, 1):
            status_icon = "✅" if result.get('status') == 'success' else "❌"
            print(f"  {status_icon} {i}. {result.get('url')} - {result.get('status')}")
        print()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Stop browser
        print("4. Stopping browser...")
        await browser_manager.stop()
        print("   ✅ Browser stopped")
        print()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(test_multiple_sites())
    sys.exit(exit_code)

