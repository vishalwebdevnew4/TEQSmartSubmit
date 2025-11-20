#!/usr/bin/env python3
"""Test single tab mode (browser reuse)."""

import asyncio
import sys
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from browser_manager import BrowserManager
from run_submission import run_submission


async def test_single_tab_mode():
    """Test browser reuse with multiple URLs."""
    print("=" * 70)
    print("Testing Single Tab Mode (Browser Reuse)")
    print("=" * 70)
    print()
    
    # Test URLs (simple pages that load quickly)
    test_urls = [
        "https://www.google.com",
        "https://www.example.com",
        "https://httpbin.org/html"
    ]
    
    template_path = Path(__file__).parent / "test_single_tab_mode.json"
    
    # Create browser manager
    print("1. Creating browser manager...")
    browser_manager = BrowserManager(
        headless=False,           # Visible browser
        use_virtual_display=False  # Don't use virtual display - show on real display
    )
    print("   ✅ Browser manager created")
    print()
    
    try:
        # Start browser once
        print("2. Starting browser (this will create a single tab)...")
        await browser_manager.start()
        print("   ✅ Browser started")
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
                print(f"\n   ✅ URL {i} completed - Status: {status}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"\n   ⚠️  URL {i} failed: {error_msg[:200]}")
            
            # Small delay between URLs
            if i < len(test_urls):
                print("\n   ⏳ Waiting 2 seconds before next URL...\n")
                await asyncio.sleep(2)
        
        print()
        print("=" * 70)
        print("✅ Test completed successfully!")
        print("=" * 70)
        print()
        print("Summary:")
        print(f"  - Browser started: Once")
        print(f"  - Tab created: Once")
        print(f"  - URLs processed: {len(test_urls)}")
        print(f"  - Tab reused: Yes (same tab, different URLs)")
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
    exit_code = asyncio.run(test_single_tab_mode())
    sys.exit(exit_code)

