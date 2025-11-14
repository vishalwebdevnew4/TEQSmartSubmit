#!/usr/bin/env python3
"""
Test script for CAPTCHA solving in development mode.
This will open a browser window and wait for you to solve CAPTCHA manually.
"""

import asyncio
import sys
from pathlib import Path

# Add the automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from automation.run_submission import run_submission
import json
import tempfile

async def test_with_manual_captcha():
    """Test automation with manual CAPTCHA solving."""
    
    # Create a test template
    template = {
        "headless": False,  # Visible browser for manual CAPTCHA solving
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
                "testValue": "TEQ Test User"
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
                "testValue": "Testing manual CAPTCHA solving in development mode"
            }
        ],
        "submit_selector": "button[type=\"submit\"]:has-text(\"Bericht verzenden\")",
        "wait_until": "load",
        "post_submit_wait_ms": 15000,
        "captcha_timeout_ms": 300000,  # 5 minutes for manual solving
        "success_indicators": ["bedankt", "thank", "success", "verzonden", "uw bericht"]
    }
    
    # Create temporary template file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(template, f, indent=2)
        template_path = Path(f.name)
    
    try:
        print("=" * 60)
        print("🧪 TESTING CAPTCHA SOLVING IN DEVELOPMENT MODE")
        print("=" * 60)
        print("\n📋 Test Configuration:")
        print(f"   URL: https://interiordesign.xcelanceweb.com/")
        print(f"   Mode: Manual CAPTCHA solving (headless=false)")
        print(f"   Timeout: 5 minutes for CAPTCHA solving")
        print("\n" + "=" * 60)
        print("\n⚠️  INSTRUCTIONS:")
        print("   1. A browser window will open")
        print("   2. The form will be filled automatically")
        print("   3. When CAPTCHA appears, solve it manually in the browser")
        print("   4. The script will detect when CAPTCHA is solved")
        print("   5. Form will be submitted automatically")
        print("\n" + "=" * 60 + "\n")
        
        # Run the automation
        result = await run_submission(
            "https://interiordesign.xcelanceweb.com/",
            template_path
        )
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETED")
        print("=" * 60)
        print(f"\nStatus: {result.get('status', 'unknown')}")
        print(f"Message: {result.get('message', 'N/A')}")
        print(f"URL: {result.get('url', 'N/A')}")
        print("\n" + "=" * 60)
        
        return result
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        print("\n" + "=" * 60)
        raise
    finally:
        # Clean up
        template_path.unlink(missing_ok=True)

if __name__ == "__main__":
    try:
        result = asyncio.run(test_with_manual_captcha())
        sys.exit(0 if result.get("status") == "success" else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        sys.exit(1)

