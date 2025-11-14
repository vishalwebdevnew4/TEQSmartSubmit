#!/usr/bin/env python3
"""
Iterative test script that runs automation until success.
Stops on first successful submission.
"""

import asyncio
import json
import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from automation.run_submission import run_submission


async def test_until_success(max_attempts=10):
    """Run automation tests until we get a success."""
    
    url = "https://interiordesign.xcelanceweb.com/"
    
    print("=" * 70)
    print("🧪 ITERATIVE TEST - RUNNING UNTIL SUCCESS")
    print("=" * 70)
    print(f"🌐 URL: {url}")
    print(f"🔄 Max attempts: {max_attempts}")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    template = {
        "use_local_captcha_solver": True,
        "captcha_service": "local",
        "headless": True,  # Run headless for faster testing
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
                "testValue": "TEQ Auto Test",
            },
            {
                "selector": "input[name='email']",
                "testValue": "autotest@example.com"
            },
            {
                "selector": "textarea[name='comment']",
                "testValue": f"AUTOMATED TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        ],
        "submit_selector": "button[type='submit']:has-text(\"Bericht verzenden\")",
        "wait_until": "load",
        "post_submit_wait_ms": 30000,
        "captcha_timeout_ms": 180000,  # 3 minutes for CAPTCHA
        "success_indicators": [
            "bedankt", 
            "thank", 
            "success", 
            "verzonden", 
            "uw bericht",
            "submitted"
        ],
    }
    
    for attempt in range(1, max_attempts + 1):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n{'=' * 70}")
        print(f"🔄 ATTEMPT {attempt}/{max_attempts}")
        print(f"{'=' * 70}")
        print(f"⏰ Time: {current_time}")
        print(f"📋 Test ID: {timestamp}")
        
        # Update test value with timestamp
        template["fields"][2]["testValue"] = f"AUTOMATED TEST #{attempt} - {current_time}"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(template, f, indent=2)
            template_path = Path(f.name)
        
        try:
            print(f"\n🚀 Starting automation...")
            start_time = time.time()
            
            result = await run_submission(url, template_path)
            
            elapsed = time.time() - start_time
            status = result.get('status', 'unknown')
            message = result.get('message', '')
            
            print(f"\n📊 Results (took {elapsed:.1f}s):")
            print(f"   Status: {status}")
            if message:
                print(f"   Message: {message[:200]}")
            
            if status == "success":
                print(f"\n{'=' * 70}")
                print(f"✅ SUCCESS ON ATTEMPT {attempt}!")
                print(f"{'=' * 70}")
                print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"⏱️  Total time: {elapsed:.1f} seconds")
                print(f"📋 Test ID: {timestamp}")
                print(f"\n💡 Check your admin panel for:")
                print(f"   Name: TEQ Auto Test")
                print(f"   Email: autotest@example.com")
                print(f"   Message: AUTOMATED TEST #{attempt} - {current_time}")
                return True
            else:
                print(f"\n❌ Attempt {attempt} failed")
                if attempt < max_attempts:
                    wait_time = min(5 * attempt, 15)  # Increasing wait between attempts
                    print(f"⏳ Waiting {wait_time} seconds before next attempt...")
                    await asyncio.sleep(wait_time)
        
        except Exception as e:
            print(f"\n❌ Attempt {attempt} error: {str(e)[:200]}")
            if attempt < max_attempts:
                wait_time = min(5 * attempt, 15)
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)
        
        finally:
            template_path.unlink(missing_ok=True)
    
    print(f"\n{'=' * 70}")
    print(f"❌ FAILED AFTER {max_attempts} ATTEMPTS")
    print(f"{'=' * 70}")
    return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_until_success(max_attempts=10))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)

