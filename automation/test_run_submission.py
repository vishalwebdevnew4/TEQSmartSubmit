#!/usr/bin/env python3
"""
Test run_submission function with the failing URL.
This test verifies that run_submission works correctly.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from run_submission import run_submission


async def test_run_submission():
    """Test run_submission with the failing URL."""
    print("=" * 70)
    print("Testing run_submission")
    print("=" * 70)
    print()
    
    # Test URL that was failing
    test_url = "https://marketing-digital.in/contact/"
    
    # Create a template for testing
    template_path = Path(__file__).parent / "test_run_submission_template.json"
    template_content = {
        "reuse_browser": False,
        "use_auto_detect": True,
        "headless": True,
        "fields": [
            {"name": "name", "value": "Test User"},
            {"name": "email", "value": "test@example.com"},
            {"name": "message", "value": "Test message from automation"}
        ]
    }
    
    # Write template
    with open(template_path, 'w') as f:
        json.dump(template_content, f, indent=2)
    
    print(f"Testing URL: {test_url}")
    print(f"Template: {template_path}")
    print()
    
    try:
        result = await run_submission(
            url=test_url,
            template_path=template_path
        )
        
        status = result.get('status', 'unknown')
        message = result.get('message', '')
        
        print()
        print("=" * 70)
        print(f"Test completed - Status: {status}")
        if message:
            print(f"Message: {message[:200]}")
        print("=" * 70)
        print()
        
        # Print result summary
        print("Result summary:")
        print(f"  Status: {status}")
        print(f"  Message: {message[:100] if message else 'None'}")
        
        if status == "success":
            print("✅ Test PASSED!")
            return True
        else:
            print("❌ Test FAILED - status is not 'success'")
            print(f"Full result: {json.dumps(result, indent=2)}")
            return False
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Test failed with exception: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_run_submission())
    sys.exit(0 if success else 1)

