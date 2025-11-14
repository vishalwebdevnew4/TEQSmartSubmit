#!/usr/bin/env python3
"""
Diagnostic script to check why submissions might not be appearing.
This will help identify if the issue is with CAPTCHA solving, form submission, or email delivery.
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from automation.run_submission import run_submission
from automation.captcha_solver import get_captcha_solver


async def diagnose_submission_flow():
    """Diagnose the submission flow step by step."""
    
    print("=" * 70)
    print("🔍 DIAGNOSING SUBMISSION FLOW")
    print("=" * 70)
    print(f"\n⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check CAPTCHA solver configuration
    print("\n" + "=" * 70)
    print("STEP 1: Checking CAPTCHA Solver Configuration")
    print("=" * 70)
    
    solver = get_captcha_solver("local")
    if solver:
        print("   ✅ Local CAPTCHA solver is available")
    else:
        print("   ⚠️  Local CAPTCHA solver not available")
        print("   💡 Check if TEQ_USE_LOCAL_CAPTCHA_SOLVER is set")
    
    # Step 2: Test form submission with detailed logging
    print("\n" + "=" * 70)
    print("STEP 2: Testing Form Submission")
    print("=" * 70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    template = {
        "use_local_captcha_solver": True,
        "captcha_service": "local",
        "headless": False,  # Set to False to see what's happening
        "pre_actions": [
            {
                "type": "click",
                "selector": "button:has-text(\"Alles accepteren\")",
                "timeout_ms": 15000
            }
        ],
        "fields": [
            {
                "selector": "input[name='name']",
                "testValue": f"DIAGNOSTIC TEST {timestamp}",
            },
            {
                "selector": "input[name='email']",
                "testValue": f"diagnostic_{timestamp}@example.com"
            },
            {
                "selector": "textarea[name='comment']",
                "testValue": f"DIAGNOSTIC TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - This is a diagnostic test to check if submissions are working."
            }
        ],
        "submit_selector": "button[type='submit']:has-text(\"Bericht verzenden\")",
        "wait_until": "load",
        "post_submit_wait_ms": 20000,  # Longer wait to see response
        "captcha_timeout_ms": 180000,  # 3 minutes for CAPTCHA
        "success_indicators": ["bedankt", "thank", "success", "verzonden", "uw bericht"],
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(template, f, indent=2)
        template_path = Path(f.name)
    
    try:
        print("\n📝 Test Configuration:")
        print(f"   Name: DIAGNOSTIC TEST {timestamp}")
        print(f"   Email: diagnostic_{timestamp}@example.com")
        print(f"   Browser: Visible (headless=False) to see what happens")
        print("\n🚀 Starting submission...")
        print("   ⚠️  WATCH THE BROWSER WINDOW to see what happens!")
        print("   - You should see the form being filled")
        print("   - You should see CAPTCHA being solved")
        print("   - You should see the form submission")
        print("   - Check if any success/error messages appear")
        print("\n" + "-" * 70 + "\n")
        
        result = await run_submission(
            "https://interiordesign.xcelanceweb.com/",
            template_path
        )
        
        print("\n" + "=" * 70)
        print("STEP 3: Analyzing Results")
        print("=" * 70)
        
        status = result.get('status', 'unknown')
        message = result.get('message', '')
        
        print(f"\n📊 Submission Status: {status}")
        print(f"📝 Message: {message[:500]}")
        
        # Analyze the result
        if status == 'success':
            print("\n✅ Submission reported SUCCESS")
            print("\n📧 Expected submission details:")
            print(f"   Name: DIAGNOSTIC TEST {timestamp}")
            print(f"   Email: diagnostic_{timestamp}@example.com")
            print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n💡 What to check:")
            print("   1. Check your email inbox (may take a few minutes)")
            print("   2. Check spam/junk folder")
            print("   3. Check website's contact form submissions/admin panel")
            print("   4. If you saw a success message in the browser, the form was submitted")
        else:
            print("\n❌ Submission reported FAILURE")
            print("\n🔍 Common issues:")
            print("   1. CAPTCHA not solved - Check if you saw CAPTCHA being solved in browser")
            print("   2. Form validation failed - Check if all required fields were filled")
            print("   3. Network timeout - Check your internet connection")
            print("   4. Page structure changed - The form might have changed")
        
        # Check for CAPTCHA-related keywords in message
        if 'captcha' in message.lower() or 'CAPTCHA' in message:
            print("\n⚠️  CAPTCHA-related message detected:")
            captcha_lines = [line for line in message.split('\n') if 'captcha' in line.lower() or 'CAPTCHA' in line or '✅' in line or '❌' in line]
            for line in captcha_lines[:5]:
                print(f"   {line[:100]}")
        
        return status == 'success'
        
    except Exception as e:
        print(f"\n❌ DIAGNOSIS FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        template_path.unlink(missing_ok=True)


async def main():
    """Main diagnostic runner."""
    print("\n" + "=" * 70)
    print("🔍 SUBMISSION DIAGNOSTIC TOOL")
    print("=" * 70)
    print("\nThis diagnostic will:")
    print("  1. Check CAPTCHA solver configuration")
    print("  2. Run a test submission with visible browser")
    print("  3. Analyze results and provide recommendations")
    print("\n⚠️  IMPORTANT: The browser window will be VISIBLE")
    print("   Watch it carefully to see what happens during submission")
    print("\n" + "-" * 70)
    
    confirm = input("\nRun diagnostic? (y/n) [default: y]: ").strip().lower() or "y"
    
    if confirm != "y":
        print("Diagnostic cancelled.")
        return
    
    try:
        success = await diagnose_submission_flow()
        print("\n" + "=" * 70)
        if success:
            print("✅ DIAGNOSTIC COMPLETED - Check the analysis above")
        else:
            print("❌ DIAGNOSTIC FOUND ISSUES - Review the recommendations above")
        print("=" * 70)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

