#!/usr/bin/env python3
"""
Test random websites to verify improvements work across different sites.
"""

import asyncio
import json
import random
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Add the automation directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# All test URLs
TEST_SITES = [
    "https://thefabcode.com/contact-us/",
    "https://www.seodiscovery.com/contact-us.php",
    "https://blacklisted.agency/contact/",
    "https://www.imarkinfotech.com/contact/",
    "https://www.softtrix.com/contact",
    "https://www.offsure.com/#/contact",
    "https://www.younedia.com/contact-us",
    "https://netpeak.in/contact-us/",
    "https://adroitors.com/contact-us/",
    "https://www.smart-minds.co.in/contact.php",
    "https://360digiexpertz.com/contact-us/",
    "https://www.onlinechandigarh.com/contact-us.html",
    "https://marketing-digital.in/contact/",
    "https://www.sagetitans.com/contact-us.html",
    "https://www.seoily.com/contact-us",
    "https://thehebrewscholar.com/index.php/contact",
    "https://petpointmedia.com/contact-us/",
    "https://teqtopaustralia.xcelanceweb.com/contact",
    "https://interiordesign.xcelanceweb.com/"
]

# Create a minimal template for auto-detection
AUTO_DETECT_TEMPLATE = {
    "fields": [],
    "submit_selector": "button[type='submit'], input[type='submit']",
    "post_submit_wait_ms": 30000,
    "captcha_timeout_ms": 600000,
    "captcha": True,
    "use_auto_detect": True,
    "use_local_captcha_solver": True,
    "headless": False,
    "wait_until": "load",
    "test_data": {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "message": "This is an automated test submission from TEQSmartSubmit."
    }
}

async def test_site(url, template_path):
    """Test a single site and print all output."""
    print("\n" + "="*80)
    print(f"Testing: {url}")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n📋 Watch the browser window to see the automation in action!")
    print("="*80 + "\n")
    
    script_path = Path(__file__).parent / "run_submission.py"
    
    try:
        # Run with output visible in terminal
        process = subprocess.Popen(
            [
                sys.executable, 
                str(script_path),
                "--url", url,
                "--template", str(template_path)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time
        output_lines = []
        json_output = None
        
        print("🚀 Starting automation...\n")
        
        for line in process.stdout:
            line = line.rstrip()
            print(line, flush=True)
            output_lines.append(line)
            
            # Try to parse JSON from output
            if line.strip().startswith('{'):
                try:
                    json_output = json.loads(line)
                except:
                    pass
        
        # Wait for process to complete
        return_code = process.wait(timeout=900)
        
        # Parse result
        if json_output:
            status = json_output.get("status", "unknown")
            message = json_output.get("message", "")
            
            if status == "success":
                print(f"\n✅ SUCCESS!")
                print(f"   URL: {url}")
                print(f"   Message: {message}")
                return True, json_output
            else:
                print(f"\n❌ FAILED!")
                print(f"   URL: {url}")
                print(f"   Status: {status}")
                print(f"   Message: {message}")
                return False, json_output
        else:
            # Check output for success/error
            full_output = "\n".join(output_lines)
            output_lower = full_output.lower()
            if "success" in output_lower and "error" not in output_lower:
                print(f"\n✅ SUCCESS! (inferred from output)")
                return True, {"status": "success"}
            else:
                print(f"\n❌ FAILED! (could not parse JSON output)")
                return False, {"status": "error", "message": "Could not parse output"}
                
    except subprocess.TimeoutExpired:
        print(f"\n⏰ TIMEOUT: Exceeded 15 minutes")
        process.kill()
        return False, {"status": "timeout"}
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {"status": "error", "message": str(e)}

async def main():
    """Test random sites."""
    # Get number of sites to test (default: 5 random sites)
    num_sites = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    # Randomly select sites
    selected_sites = random.sample(TEST_SITES, min(num_sites, len(TEST_SITES)))
    
    print("\n" + "="*80)
    print("Random Site Testing")
    print("="*80)
    print(f"Testing {len(selected_sites)} random site(s) out of {len(TEST_SITES)} total")
    print(f"Selected sites:")
    for i, url in enumerate(selected_sites, 1):
        print(f"  {i}. {url}")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n💡 TIP: Watch the browser windows to see what's happening!")
    print("💡 TIP: All logs will appear below in real-time")
    print("="*80)
    
    # Create template file
    template_path = Path(__file__).parent / "auto_detect_template.json"
    template_path.write_text(json.dumps(AUTO_DETECT_TEMPLATE, indent=2))
    
    results = {}
    
    # Test selected sites
    for i, url in enumerate(selected_sites, 1):
        print(f"\n\n{'#'*80}")
        print(f"# SITE {i}/{len(selected_sites)}")
        print(f"{'#'*80}\n")
        
        success, result = await test_site(url, template_path)
        results[url] = {"success": success, "result": result}
        
        # Brief pause between sites
        await asyncio.sleep(2)
    
    # Final summary
    print("\n\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    passed = [url for url, data in results.items() if data["success"]]
    failed = [url for url, data in results.items() if not data["success"]]
    
    print(f"\n✅ PASSED ({len(passed)}/{len(selected_sites)}):")
    for url in passed:
        print(f"   ✅ {url}")
    
    if failed:
        print(f"\n❌ FAILED ({len(failed)}/{len(selected_sites)}):")
        for url in failed:
            message = results[url]["result"].get("message", "Unknown error")
            print(f"   ❌ {url}")
            print(f"      Error: {message[:100]}")
    
    print(f"\nTotal: {len(selected_sites)} | Passed: {len(passed)} | Failed: {len(failed)}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

