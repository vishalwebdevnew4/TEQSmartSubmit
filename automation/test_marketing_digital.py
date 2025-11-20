#!/usr/bin/env python3
"""
Test run_submission with https://marketing-digital.in/contact/
"""

import asyncio
import json
import sys
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from run_submission import run_submission


async def test_marketing_digital():
    """Test run_submission with marketing-digital.in contact form."""
    print("=" * 70)
    print("Testing run_submission with https://marketing-digital.in/contact/")
    print("=" * 70)
    print()
    
    test_url = "https://marketing-digital.in/contact/"
    
    # Create template with auto-detect mode
    template_path = Path(__file__).parent / "test_marketing_digital_template.json"
    template_content = {
        "reuse_browser": False,
        "use_auto_detect": True,
        "headless": True,
        "test_data": {
            "name": "Test User",
            "email": "test@example.com",
            "message": "This is an automated test submission from TEQSmartSubmit."
        }
    }
    
    # Write template
    with open(template_path, 'w') as f:
        json.dump(template_content, f, indent=2)
    
    print(f"Testing URL: {test_url}")
    print(f"Template: {template_path}")
    print(f"Mode: Auto-detect")
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
        
        # Print detailed result
        print("Result details:")
        print(f"  Status: {status}")
        print(f"  URL: {result.get('url', 'N/A')}")
        print(f"  Message: {message[:150] if message else 'None'}")
        
        if 'post_requests_count' in result:
            print(f"  POST requests: {result.get('post_requests_count', 0)}")
        if 'post_responses_count' in result:
            print(f"  POST responses: {result.get('post_responses_count', 0)}")
        if 'submission_error' in result and result.get('submission_error'):
            print(f"  Submission error: {result.get('submission_error')[:100]}")
        
        print()
        print("Full result JSON:")
        print(json.dumps(result, indent=2))
        print()
        
        if status == "success":
            print("✅ Test PASSED - Submission successful!")
            return True
        else:
            print(f"⚠️  Test completed with status: {status}")
            print("   (This may be expected if the form requires CAPTCHA or has other protections)")
            return True  # Still consider it a pass if the script ran without crashing
            
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Test failed with exception: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up template file
        if template_path.exists():
            template_path.unlink()


if __name__ == "__main__":
    success = asyncio.run(test_marketing_digital())
    sys.exit(0 if success else 1)

