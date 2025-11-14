#!/usr/bin/env python3
"""
Test the local CAPTCHA solver with a real form.
"""

import asyncio
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from automation.run_submission import run_submission

async def test_local_solver():
    """Test local CAPTCHA solver."""
    
    template = {
        "use_local_captcha_solver": True,  # Enable local solver
        "headless": False,  # Show browser for testing
        "pre_actions": [
            {
                "type": "click",
                "selector": "button:has-text(\"Alles accepteren\")",
                "timeout_ms": 15000
            }
        ],
        "fields": [
            {
                "selector": "input[name=\"name\"]",
                "testValue": "TEQ Local Solver Test"
            },
            {
                "selector": "input[name=\"email\"]",
                "testValue": "test@example.com"
            },
            {
                "selector": "input[name=\"phone\"]",
                "testValue": "555-123-4567",
                "optional": True
            },
            {
                "selector": "textarea[name=\"comment\"]",
                "testValue": "Testing fully automated local CAPTCHA solver"
            }
        ],
        "submit_selector": "button[type=\"submit\"]:has-text(\"Bericht verzenden\")",
        "wait_until": "load",
        "post_submit_wait_ms": 20000,
        "captcha_timeout_ms": 120000,  # 2 minutes for solving
        "success_indicators": ["bedankt", "thank", "success", "verzonden", "uw bericht"]
    }
    
    # Create temporary template file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(template, f, indent=2)
        template_path = Path(f.name)
    
    try:
        print("=" * 70)
        print("🧪 TESTING LOCAL CAPTCHA SOLVER - FULLY AUTOMATED")
        print("=" * 70)
        print("\n📋 Configuration:")
        print(f"   URL: https://interiordesign.xcelanceweb.com/")
        print(f"   Solver: Local (Self-Made)")
        print(f"   Mode: Fully Automated")
        print(f"   Browser: Visible (headless=false)")
        print("\n" + "=" * 70)
        print("\n⏳ Starting automation...")
        print("   - Form will be filled automatically")
        print("   - CAPTCHA will be solved automatically")
        print("   - Form will be submitted automatically")
        print("\n" + "=" * 70 + "\n")
        
        # Run the automation
        result = await run_submission(
            "https://interiordesign.xcelanceweb.com/",
            template_path
        )
        
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS")
        print("=" * 70)
        print(f"\nStatus: {result.get('status', 'unknown')}")
        print(f"Message: {result.get('message', 'N/A')}")
        print(f"URL: {result.get('url', 'N/A')}")
        
        if result.get('status') == 'success':
            print("\n✅ SUCCESS! Local CAPTCHA solver worked!")
            print("   Form was submitted successfully with automatic CAPTCHA solving.")
        else:
            print("\n⚠️  Check the message above for details.")
        
        print("\n" + "=" * 70)
        
        return result
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ TEST FAILED")
        print("=" * 70)
        print(f"\nError: {str(e)}")
        print("\n" + "=" * 70)
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Clean up
        template_path.unlink(missing_ok=True)

if __name__ == "__main__":
    try:
        result = asyncio.run(test_local_solver())
        sys.exit(0 if result.get("status") == "success" else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        sys.exit(1)

