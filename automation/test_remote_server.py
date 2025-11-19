#!/usr/bin/env python3
"""
Test script for remote server deployment.
Tests headless mode detection, CAPTCHA solving, and form submission.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from run_submission import run_submission

# Test URL - using a simple site for testing
TEST_URL = "https://www.seoily.com/contact-us"
TEST_TEMPLATE = {
    "fields": [],
    "captcha": True,
    "headless": None,  # Let auto-detection decide
    "use_local_captcha_solver": True,
    "use_hybrid_captcha_solver": False,
    "captcha_service": "local",
    "use_auto_detect": True,
    "test_data": {
        "name": "TEQ Remote Test",
        "email": "remote-test@example.com",
        "phone": "+1234567890",
        "message": "This is a remote server test submission from TEQSmartSubmit.",
        "subject": "Remote Server Test",
        "company": "Test Company"
    },
    "submit_selector": "button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Send'), button:has-text('Send message')",
    "post_submit_wait_ms": 30000,
    "captcha_timeout_ms": 600000,
    "wait_until": "load"
}

def check_environment():
    """Check the server environment."""
    print("="*80)
    print("Remote Server Environment Check")
    print("="*80)
    
    # Check display
    display = os.getenv("DISPLAY")
    has_display = display is not None and display != ""
    print(f"DISPLAY environment variable: {display or 'NOT SET'}")
    print(f"Has display: {has_display}")
    
    # Check if containerized
    is_container = os.path.exists("/.dockerenv") or os.getenv("container") is not None
    print(f"Is containerized: {is_container}")
    
    # Check headless environment variables
    force_headless = os.getenv("TEQ_FORCE_HEADLESS")
    headless_env = os.getenv("HEADLESS")
    playwright_headless = os.getenv("TEQ_PLAYWRIGHT_HEADLESS")
    
    print(f"TEQ_FORCE_HEADLESS: {force_headless or 'NOT SET'}")
    print(f"HEADLESS: {headless_env or 'NOT SET'}")
    print(f"TEQ_PLAYWRIGHT_HEADLESS: {playwright_headless or 'NOT SET'}")
    
    # Expected mode
    if has_display and not is_container:
        expected_mode = "VISIBLE BROWSER (non-headless)"
    else:
        expected_mode = "HEADLESS MODE"
    
    print(f"\nExpected browser mode: {expected_mode}")
    print("="*80)
    print()

async def test_submission():
    """Test form submission."""
    print("="*80)
    print("Testing Form Submission")
    print("="*80)
    print(f"URL: {TEST_URL}")
    print(f"Template: {json.dumps(TEST_TEMPLATE, indent=2)}")
    print("="*80)
    print("\n🚀 Starting automation...\n")
    print("="*80)
    
    # Create temp template file
    import tempfile
    
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
            print("\n✅ SUCCESS! Remote server test passed!")
            print("   The automation is working correctly on the remote server.")
            return 0
        else:
            print(f"\n❌ FAILED: {result.get('message', 'Unknown error')}")
            print("\nTroubleshooting:")
            print("1. Check if Playwright browsers are installed: playwright install chromium")
            print("2. Check if all dependencies are installed")
            print("3. Review the error message above for specific issues")
            return 1
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Ensure Playwright is installed: pip install playwright && playwright install chromium")
        print("2. Check Python dependencies: pip install -r requirements.txt")
        print("3. Verify network connectivity to the target URL")
        return 1
    finally:
        # Clean up temp file
        try:
            os.unlink(template_path)
        except:
            pass

async def main():
    """Main test function."""
    print("\n" + "="*80)
    print("TEQSmartSubmit Remote Server Test")
    print("="*80)
    print(f"Server: {os.uname().nodename}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print("="*80)
    print()
    
    # Check environment
    check_environment()
    
    # Test submission
    result = await test_submission()
    
    print("\n" + "="*80)
    print("Test Complete")
    print("="*80)
    
    return result

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

