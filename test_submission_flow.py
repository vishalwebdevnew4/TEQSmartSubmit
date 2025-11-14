#!/usr/bin/env python3
"""
Test script to verify form submission is working correctly.
This will make an actual submission to test if the flow works.
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from automation.run_submission import run_submission


async def test_submission():
    """Test a single form submission."""
    
    print("=" * 70)
    print("🧪 TESTING FORM SUBMISSION FLOW")
    print("=" * 70)
    print(f"\n⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📋 Test Configuration:")
    print("   URL: https://interiordesign.xcelanceweb.com/")
    print("   Solver: Local CAPTCHA Solver (fully automated)")
    print("   Mode: Headless")
    
    # Create test template with unique test values
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    template = {
        "use_local_captcha_solver": True,
        "captcha_service": "local",
        "headless": True,
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
                "testValue": f"TEQ Test Submission {timestamp}",
                "note": "Primary contact name field."
            },
            {
                "selector": "input[name='email']",
                "testValue": f"test_submission_{timestamp}@example.com"
            },
            {
                "selector": "input[name='phone']",
                "testValue": "555-123-4567",
                "optional": True
            },
            {
                "selector": "textarea[name='comment']",
                "testValue": f"TEST SUBMISSION {timestamp} - Automated CAPTCHA resolver test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        ],
        "submit_selector": "button[type='submit']:has-text(\"Bericht verzenden\")",
        "wait_until": "load",
        "post_submit_wait_ms": 15000,
        "captcha_timeout_ms": 120000,
        "success_indicators": ["bedankt", "thank", "success", "verzonden", "uw bericht"],
        "success_message": "Submission completed successfully"
    }
    
    # Create temporary template file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(template, f, indent=2)
        template_path = Path(f.name)
    
    try:
        print("\n🚀 Starting submission test...")
        print(f"   Test ID: {timestamp}")
        print(f"   Test email: test_{timestamp}@example.com")
        print(f"   Test name: TEQ Test User {timestamp}")
        print("\n" + "-" * 70 + "\n")
        
        # Run the automation
        result = await run_submission(
            "https://interiordesign.xcelanceweb.com/",
            template_path
        )
        
        print("\n" + "=" * 70)
        print("📊 SUBMISSION RESULTS")
        print("=" * 70)
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nStatus: {result.get('status', 'unknown')}")
        print(f"Message: {result.get('message', 'N/A')[:300]}...")
        print(f"URL: {result.get('url', 'N/A')}")
        
        # Check if it was successful
        if result.get('status') == 'success':
            print("\n✅ SUBMISSION SUCCESSFUL!")
            print(f"\n📧 Expected submission details:")
            print(f"   Name: TEQ Test Submission {timestamp}")
            print(f"   Email: test_submission_{timestamp}@example.com")
            print(f"   Message: TEST SUBMISSION {timestamp} - Automated CAPTCHA resolver test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n💡 Check your email/contact form for this submission")
            return True
        else:
            print("\n❌ SUBMISSION FAILED")
            print(f"   Error: {result.get('message', 'Unknown error')[:500]}")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ SUBMISSION FAILED WITH EXCEPTION")
        print("=" * 70)
        print(f"\nError: {str(e)}")
        import traceback
        print("\nTraceback:")
        print(traceback.format_exc())
        return False
    finally:
        # Clean up
        template_path.unlink(missing_ok=True)
        print("\n🧹 Cleanup complete")


async def main():
    """Main test runner."""
    print("\n" + "=" * 70)
    print("🎯 FORM SUBMISSION TEST")
    print("=" * 70)
    print("\nThis test will:")
    print("  1. Navigate to the contact form")
    print("  2. Fill in test fields with unique timestamp")
    print("  3. Solve CAPTCHA automatically")
    print("  4. Submit the form")
    print("  5. Verify success")
    print("\n" + "-" * 70)
    
    confirm = input("\nProceed with test submission? (y/n) [default: y]: ").strip().lower() or "y"
    
    if confirm != "y":
        print("Test cancelled.")
        return
    
    try:
        success = await test_submission()
        if success:
            print("\n" + "=" * 70)
            print("✅ TEST COMPLETED - Check your email for the submission")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("❌ TEST FAILED - Check the error messages above")
            print("=" * 70)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

