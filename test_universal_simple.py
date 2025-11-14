#!/usr/bin/env python3
"""
Simple test for universal template - tests one URL at a time.
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add automation directory to path
_script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(_script_dir))

from automation.run_submission import run_submission


async def test_universal_simple(url: str):
    """Test universal template with auto-detection on a single URL."""
    
    # Universal template with auto-detection enabled
    universal_template = {
        "fields": [],  # Empty - will trigger auto-detection
        "use_auto_detect": True,
        "use_local_captcha_solver": True,
        "use_hybrid_captcha_solver": False,  # Local only
        "captcha_service": "local",
        "headless": False,  # Show browser
        "wait_until": "load",
        "pre_actions": [],
        "submit_selector": "button[type='submit'], input[type='submit']",
        "success_indicators": ["thank", "success", "bedankt", "verzonden", "submitted"],
        "success_message": "Submission completed",
        "post_submit_wait_ms": 20000,
        "test_data": {
            "name": "TEQ QA User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": f"Universal template test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "subject": "Test Inquiry",
            "company": "Test Company"
        }
    }
    
    print("🧪 Testing Universal Template with Auto-Detection")
    print("=" * 70)
    print(f"URL: {url}")
    print(f"Template: Universal (auto-detect fields)")
    print()
    
    # Create temporary template file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(universal_template, f, indent=2)
        template_path = Path(f.name)
    
    try:
        print("Starting submission...\n")
        result = await run_submission(url, template_path)
        
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Success: {result.get('success', False)}")
        message = result.get('message', '')
        if message:
            print(f"Message: {message[:300]}")
        
        if result.get("success") or result.get("status") == "success":
            print("\n✅ SUCCESS!")
            return True
        else:
            print("\n❌ FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        template_path.unlink(missing_ok=True)


if __name__ == "__main__":
    # Test the teqtopaustralia site first (has contact form)
    test_url = "https://teqtopaustralia.xcelanceweb.com/contact"
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    try:
        success = asyncio.run(test_universal_simple(test_url))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)

