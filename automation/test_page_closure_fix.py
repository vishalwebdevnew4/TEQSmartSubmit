#!/usr/bin/env python3
"""
Test the page closure fix with the actual failing URL.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from run_submission import run_submission


async def test_page_closure_fix():
    """Test the page closure fix with the actual failing URL."""
    print("=" * 70)
    print("Testing Page Closure Fix")
    print("=" * 70)
    print()
    
    # Test URL that was failing
    test_url = "https://www.seoily.com/contact-us"
    
    # Create a template for testing (Universal Auto-Detect Template)
    template_path = Path(__file__).parent / "test_page_closure_fix_template.json"
    template_content = {
        "reuse_browser": False,
        "use_auto_detect": True,
        "headless": True,
        "wait_until": "domcontentloaded",
        "fields": []
    }
    
    # Write template
    with open(template_path, 'w') as f:
        json.dump(template_content, f, indent=2)
    
    print(f"Testing URL: {test_url}")
    print(f"Template: {template_path}")
    print("Template config: Universal Auto-Detect Template")
    print()
    
    try:
        result = await run_submission(
            url=test_url,
            template_path=template_path
        )
        
        status = result.get('status', 'unknown')
        message = result.get('message', '')
        submission_error = result.get('submission_error', '')
        
        print()
        print("=" * 70)
        print(f"Test completed - Status: {status}")
        if message:
            print(f"Message: {message[:200]}")
        if submission_error:
            print(f"Submission Error: {submission_error[:200]}")
        print("=" * 70)
        print()
        
        # Print result summary
        print("Result summary:")
        print(f"  Status: {status}")
        print(f"  Message: {message[:100] if message else 'None'}")
        print(f"  Submission Error: {submission_error[:100] if submission_error else 'None'}")
        
        # Check if the page closure error is fixed
        if "Page was closed" in str(result) or "has been closed" in str(result):
            print()
            print("❌ Test FAILED - Page closure error still occurs!")
            print(f"Full result: {json.dumps(result, indent=2)}")
            return False
        elif status == "success":
            print()
            print("✅ Test PASSED - Form submission successful!")
            return True
        elif status == "error":
            print()
            print("⚠️  Test completed with error, but page closure issue may be fixed")
            print(f"Full result: {json.dumps(result, indent=2)}")
            # Don't fail if it's a different error (not page closure)
            return "Page was closed" not in str(result)
        else:
            print()
            print(f"⚠️  Test completed with status: {status}")
            print(f"Full result: {json.dumps(result, indent=2)}")
            return True  # Consider it a pass if no page closure error
        
    except Exception as e:
        error_str = str(e)
        print()
        print("=" * 70)
        print(f"❌ Test failed with exception: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        
        # Check if it's a page closure error
        if "Page was closed" in error_str or "has been closed" in error_str:
            print()
            print("❌ Page closure error still occurs in exception!")
            return False
        else:
            print()
            print("⚠️  Different error occurred (not page closure)")
            return False


if __name__ == "__main__":
    success = asyncio.run(test_page_closure_fix())
    sys.exit(0 if success else 1)

