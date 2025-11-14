#!/usr/bin/env python3
"""
Test universal template until success.
Retries with improved form selection and better error handling.
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


async def test_until_success(url: str, max_attempts: int = 5):
    """Test universal template with auto-detection until success."""
    
    # Universal template with auto-detection enabled
    universal_template = {
        "fields": [],  # Empty - will trigger auto-detection
        "use_auto_detect": True,
        "use_local_captcha_solver": True,
        "use_hybrid_captcha_solver": False,  # Local only
        "captcha_service": "local",
        "headless": False,  # Show browser for testing
        "wait_until": "load",
        "pre_actions": [],
        "submit_selector": "button[type='submit'], input[type='submit']",
        "success_indicators": ["thank", "success", "bedankt", "verzonden", "submitted"],
        "success_message": "Submission completed",
        "post_submit_wait_ms": 20000,  # Longer wait
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
    print(f"Max attempts: {max_attempts}")
    print(f"Auto-detect: Enabled")
    print()
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n{'='*70}")
        print(f"Attempt {attempt}/{max_attempts}")
        print(f"{'='*70}\n")
        
        # Create temporary template file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(universal_template, f, indent=2)
            template_path = Path(f.name)
        
        try:
            result = await run_submission(url, template_path)
            
            if result.get("success") or result.get("status") == "success":
                print(f"\n✅ SUCCESS on attempt {attempt}!")
                print(f"   Message: {result.get('message', 'Success')[:200]}")
                template_path.unlink()
                return True
            else:
                error_msg = result.get("message", "Unknown error")
                print(f"\n❌ Attempt {attempt} failed")
                print(f"   Error: {error_msg[:200]}")
                
                if attempt < max_attempts:
                    wait_time = min(attempt * 2, 10)  # Wait 2, 4, 6, 8, 10 seconds
                    print(f"   Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ Attempt {attempt} error: {error_msg[:200]}")
            
            if attempt < max_attempts:
                wait_time = min(attempt * 2, 10)
                print(f"   Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)
        finally:
            template_path.unlink(missing_ok=True)
    
    print(f"\n❌ All {max_attempts} attempts failed")
    return False


async def main():
    """Test multiple URLs until success."""
    test_urls = [
        "https://teqtopaustralia.xcelanceweb.com/contact",
        "https://interiordesign.xcelanceweb.com/",
    ]
    
    results = []
    
    for url in test_urls:
        print(f"\n{'#'*70}")
        print(f"Testing: {url}")
        print(f"{'#'*70}\n")
        
        success = await test_until_success(url, max_attempts=3)
        results.append({"url": url, "success": success})
        
        if success:
            print(f"\n✅ {url} - SUCCESS!")
        else:
            print(f"\n❌ {url} - FAILED after all attempts")
    
    # Summary
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    for result in results:
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"{status}: {result['url']}")
    
    all_success = all(r["success"] for r in results)
    return all_success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Test script error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

