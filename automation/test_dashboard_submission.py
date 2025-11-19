#!/usr/bin/env python3
"""
Test script to run automation with the same parameters as the dashboard.
This will show detailed logs in the terminal.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from run_submission import run_submission

# Test URL and template (matching dashboard request)
TEST_URL = "https://www.seoily.com/contact-us"
TEST_TEMPLATE = {
    "fields": [],
    "captcha": True,
    "headless": False,  # Set to False to see the browser
    "use_local_captcha_solver": True,
    "use_hybrid_captcha_solver": False,
    "captcha_service": "local",
    "use_auto_detect": True,
    "test_data": {
        "name": "TEQ QA User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "message": "This is an automated test submission from TEQSmartSubmit.",
        "subject": "Test Inquiry",
        "company": "Test Company"
    },
    "submit_selector": "button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Send'), button:has-text('Send message')",
    "post_submit_wait_ms": 30000,
    "captcha_timeout_ms": 600000,
    "wait_until": "load"
}

async def main():
    """Run the test submission."""
    print("="*80)
    print("Testing Dashboard Submission")
    print("="*80)
    print(f"URL: {TEST_URL}")
    print(f"Template: {json.dumps(TEST_TEMPLATE, indent=2)}")
    print("="*80)
    print("\n🚀 Starting automation...\n")
    print("="*80)
    
    # Create temp template file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(TEST_TEMPLATE, f, indent=2)
        template_path = Path(f.name)
    
    try:
        result = await run_submission(TEST_URL, template_path)
        
        print("\n" + "="*80)
        print("RESULT:")
        print("="*80)
        print(json.dumps(result, indent=2))
        print("="*80)
        
        if result.get("status") == "success":
            print("\n✅ SUCCESS!")
            return 0
        else:
            print(f"\n❌ FAILED: {result.get('message', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Clean up temp file
        try:
            os.unlink(template_path)
        except:
            pass

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

