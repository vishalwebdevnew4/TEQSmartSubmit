#!/usr/bin/env python3
"""
Quick test submission with visible browser to verify it works.
This will make a submission you can track in your admin panel.
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from automation.run_submission import run_submission


async def quick_test():
    """Run a quick test submission."""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("=" * 70)
    print("🚀 QUICK TEST SUBMISSION")
    print("=" * 70)
    print(f"\n⏰ Test Time: {current_time}")
    print(f"📋 Test ID: {timestamp}")
    
    template = {
        "use_local_captcha_solver": True,
        "captcha_service": "local",
        "headless": False,  # Visible browser so you can see what happens
        "pre_actions": [
            {
                "type": "click",
                "selector": "button:has-text(\"Alles accepteren\")",
                "timeout_ms": 15000
            },
            {
                "type": "wait_for_selector",
                "selector": "form button[type='submit']:has-text(\"Bericht verzenden\")",
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
                "selector": "textarea[name='comment']",
                "testValue": f"QUICK TEST {timestamp} - Submitted at {current_time} - Local CAPTCHA solver test"
            }
        ],
        "submit_selector": "button[type='submit']:has-text(\"Bericht verzenden\")",
        "wait_until": "load",
        "post_submit_wait_ms": 20000,
        "captcha_timeout_ms": 180000,
        "success_indicators": ["bedankt", "thank", "success", "verzonden", "uw bericht"],
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(template, f, indent=2)
        template_path = Path(f.name)
    
    try:
        print("\n📝 Submission Details:")
        print(f"   Name: TEQ Test {timestamp}")
        print(f"   Email: test_{timestamp}@example.com")
        print(f"   Message: QUICK TEST {timestamp} - Submitted at {current_time}")
        print("\n⚠️  Browser will be VISIBLE - watch what happens!")
        print("   - You'll see the form being filled")
        print("   - You'll see CAPTCHA being solved")
        print("   - You'll see the submission")
        print("\n" + "-" * 70)
        print("Starting in 3 seconds...")
        await asyncio.sleep(3)
        print("\n")
        
        result = await run_submission(
            "https://interiordesign.xcelanceweb.com/",
            template_path
        )
        
        print("\n" + "=" * 70)
        print("📊 RESULTS")
        print("=" * 70)
        print(f"\nStatus: {result.get('status', 'unknown')}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if result.get('status') == 'success':
            print("\n✅ SUBMISSION SUCCESSFUL!")
            print("\n📋 Check your admin panel for:")
            print(f"   Name: TEQ Test {timestamp}")
            print(f"   Email: test_{timestamp}@example.com")
            print(f"   Time: ~{current_time}")
            print("\n💡 The submission should appear in your admin panel now.")
            print("   If you don't see it, check:")
            print("   1. Wait a few seconds and refresh the admin panel")
            print("   2. Check if there are any filters applied")
            print("   3. Check the browser window for any error messages")
        else:
            print(f"\n❌ SUBMISSION FAILED")
            print(f"   Error: {result.get('message', 'Unknown error')[:300]}")
            print("\n💡 Check the browser window to see what happened")
        
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
    print("🎯 QUICK TEST - Will submit to your admin panel")
    print("=" * 70)
    
    try:
        success = asyncio.run(quick_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(1)

