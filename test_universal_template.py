#!/usr/bin/env python3
"""
Test script for universal template with auto-detection.
This tests the auto-detection feature that works without manual field mapping.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add automation directory to path
_script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(_script_dir))

from automation.run_submission import run_submission


async def test_universal_template():
    """Test universal template with auto-detection on multiple sites."""
    
    # Test URLs
    test_urls = [
        "https://interiordesign.xcelanceweb.com/",
        "https://teqtopaustralia.xcelanceweb.com/contact",
    ]
    
    # Universal template with auto-detection enabled
    # No fields specified - will auto-detect
    universal_template = {
        "fields": [],  # Empty - will trigger auto-detection
        "use_auto_detect": True,
        "use_local_captcha_solver": True,
        "use_hybrid_captcha_solver": False,
        "captcha_service": "local",
        "headless": False,  # Show browser for testing
        "wait_until": "load",
        "pre_actions": [],
        "submit_selector": "button[type='submit'], input[type='submit']",
        "success_indicators": ["thank", "success", "bedankt", "verzonden"],
        "success_message": "Submission completed",
        "post_submit_wait_ms": 15000,
        "test_data": {
            "name": "TEQ QA User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": "This is an automated test submission using universal template with auto-detection.",
            "subject": "Test Inquiry",
            "company": "Test Company"
        }
    }
    
    # Create temporary template file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(universal_template, f, indent=2)
        template_path = Path(f.name)
    
    print("🧪 Testing Universal Template with Auto-Detection")
    print("=" * 60)
    print(f"Template: Universal (no field mappings)")
    print(f"Auto-detect: Enabled")
    print(f"Test URLs: {len(test_urls)}")
    print()
    
    results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{len(test_urls)}: {url}")
        print(f"{'='*60}\n")
        
        try:
            result = await run_submission(url, template_path)
            results.append({
                "url": url,
                "success": result.get("success", False),
                "message": result.get("message", "Unknown"),
                "status": result.get("status", "unknown")
            })
            
            if result.get("success"):
                print(f"\n✅ SUCCESS: {url}")
            else:
                print(f"\n❌ FAILED: {url}")
                print(f"   Message: {result.get('message', 'No message')}")
                
        except Exception as e:
            print(f"\n❌ ERROR: {url}")
            print(f"   Error: {str(e)}")
            results.append({
                "url": url,
                "success": False,
                "message": str(e),
                "status": "error"
            })
    
    # Cleanup
    template_path.unlink()
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    success_count = sum(1 for r in results if r["success"])
    print(f"Total tests: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    print()
    
    for result in results:
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {result['url']}")
        if not result["success"]:
            print(f"   {result['message'][:100]}")
    
    return results


if __name__ == "__main__":
    try:
        results = asyncio.run(test_universal_template())
        # Exit with error code if any test failed
        if any(not r["success"] for r in results):
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Test script error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

