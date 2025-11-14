#!/usr/bin/env python3
"""
Test script with exact form structure from the website.
Uses the actual selectors and site key.
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from automation.run_submission import run_submission


async def test_exact_form():
    """Test with exact form structure."""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("=" * 70)
    print("🧪 TEST WITH EXACT FORM STRUCTURE")
    print("=" * 70)
    print(f"\n⏰ Test Time: {current_time}")
    print(f"📋 Test ID: {timestamp}")
    print(f"🌐 URL: https://interiordesign.xcelanceweb.com/")
    print(f"🔑 Expected reCAPTCHA Site Key: 6Le-E8crAAAAADw62vcYviz51uzwfjOcI8kALbsT")
    
    # Template matching the exact form structure
    template = {
        "use_local_captcha_solver": True,  # Try local solver first
        "use_hybrid_captcha_solver": True,  # Fallback to external if local fails
        "captcha_service": "auto",  # Auto-select best available service
        "headless": False,  # Visible so you can see what happens
        "pre_actions": [
            {
                "type": "click",
                "selector": "button:has-text(\"Alles accepteren\")",
                "timeout_ms": 15000
            },
            {
                "type": "wait_for_selector",
                "selector": "form input[name='name']",
                "timeout_ms": 15000
            }
        ],
        "fields": [
            {
                "selector": "input[name='name']",
                "testValue": f"TEQ Test {timestamp}",
            },
            {
                "selector": "input[name='email']",
                "testValue": f"test_{timestamp}@example.com"
            },
            {
                "selector": "input[name='phone']",
                "testValue": "555-123-4567",
                "optional": True
            },
            {
                "selector": "textarea[name='comment']",
                "testValue": f"EXACT FORM TEST {timestamp} - Submitted at {current_time} - Testing exact form structure"
            }
        ],
        "submit_selector": "button[type='submit']:has-text(\"Bericht verzenden\")",
        "wait_until": "load",
        "post_submit_wait_ms": 30000,  # Longer wait for response
        "captcha_timeout_ms": 240000,  # 4 minutes for CAPTCHA solving
        "success_indicators": [
            "bedankt", 
            "thank", 
            "success", 
            "verzonden", 
            "uw bericht",
            "submitted",
            "successfully"
        ],
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(template, f, indent=2)
        template_path = Path(f.name)
    
    try:
        print("\n📝 Submission Details:")
        print(f"   Name: TEQ Test {timestamp}")
        print(f"   Email: test_{timestamp}@example.com")
        print(f"   Phone: 555-123-4567")
        print(f"   Message: EXACT FORM TEST {timestamp} - Submitted at {current_time}")
        print("\n⚠️  Browser will be VISIBLE")
        print("   Watch for:")
        print("   ✓ Form fields being filled")
        print("   ✓ reCAPTCHA checkbox being clicked")
        print("   ✓ CAPTCHA being solved (audio challenge if appears)")
        print("   ✓ Submit button being clicked")
        print("   ✓ Success/error message")
        print("\n" + "-" * 70)
        print("Starting in 2 seconds...")
        await asyncio.sleep(2)
        print("\n")
        
        result = await run_submission(
            "https://interiordesign.xcelanceweb.com/",
            template_path
        )
        
        print("\n" + "=" * 70)
        print("📊 SUBMISSION RESULTS")
        print("=" * 70)
        print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Status: {result.get('status', 'unknown')}")
        
        message = result.get('message', '')
        if message:
            print(f"📝 Message: {message[:400]}")
        
        if result.get('status') == 'success':
            print("\n✅ SUBMISSION REPORTED AS SUCCESS!")
            print("\n📋 Look for this in your admin panel:")
            print(f"   Name: TEQ Test {timestamp}")
            print(f"   Email: test_{timestamp}@example.com")
            print(f"   Time: {current_time}")
            print(f"   Message: EXACT FORM TEST {timestamp} - Submitted at {current_time}")
            print("\n💡 If you don't see it in admin panel:")
            print("   1. Refresh the admin panel page")
            print("   2. Check if there's a filter applied")
            print("   3. Check the browser window - did it show a success message?")
            print("   4. Wait 10-30 seconds and check again (may take time to process)")
        else:
            print(f"\n❌ SUBMISSION FAILED")
            print(f"   Error: {message[:500] if message else 'Unknown error'}")
            print("\n💡 Check the browser window to see what happened")
            print("   Common issues:")
            print("   - CAPTCHA not solved correctly")
            print("   - Form validation failed")
            print("   - Network timeout")
        
        return result.get('status') == 'success'
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        template_path.unlink(missing_ok=True)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎯 EXACT FORM TEST")
    print("=" * 70)
    print("\nThis test uses the exact form structure from your website.")
    print("It will make a visible submission you can track in admin panel.")
    print("\n" + "-" * 70)
    
    try:
        success = asyncio.run(test_exact_form())
        print("\n" + "=" * 70)
        if success:
            print("✅ TEST COMPLETED - Check your admin panel!")
        else:
            print("❌ TEST FAILED - Check the error messages above")
        print("=" * 70)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(1)

