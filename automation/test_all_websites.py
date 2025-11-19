#!/usr/bin/env python3
"""
Test all websites with auto-detection mode (no template required).
Tests all sites, retries failures, and reports results.
"""

import asyncio
import json
import subprocess
import sys
import time
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
    "fields": [],  # Empty - will use auto-detection
    "submit_selector": "button[type='submit'], input[type='submit']",
    "post_submit_wait_ms": 15000,
    "captcha": True,
    "use_auto_detect": True,  # Enable auto-detection
    "use_local_captcha_solver": True,
    "headless": False,  # Run with visible browser - open so user can watch
    "wait_until": "load",
    "test_data": {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "message": "This is an automated test submission from TEQSmartSubmit."
    }
}

async def test_site_with_auto_detect(url, template_path):
    """Test a single site using auto-detection."""
    print("\n" + "="*80)
    print(f"Testing: {url}")
    print("="*80)
    
    script_path = Path(__file__).parent / "run_submission.py"
    
    try:
        # Run the submission script
        result = subprocess.run(
            [
                sys.executable, 
                str(script_path),
                "--url", url,
                "--template", str(template_path)
            ],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per site
        )
        
        # Parse JSON output
        try:
            output_lines = result.stdout.strip().split('\n')
            json_output = None
            for line in output_lines:
                if line.strip().startswith('{'):
                    try:
                        json_output = json.loads(line)
                        break
                    except:
                        continue
            
            if json_output:
                status = json_output.get("status", "unknown")
                message = json_output.get("message", "")
                
                if status == "success":
                    print(f"✅ SUCCESS: {url}")
                    print(f"   Message: {message}")
                    return True, json_output
                else:
                    print(f"❌ FAILED: {url}")
                    print(f"   Message: {message}")
                    if result.stderr:
                        print(f"   Error details: {result.stderr[-500:]}")  # Last 500 chars
                    return False, json_output
            else:
                # No JSON output - check stderr
                if "success" in result.stdout.lower() or "success" in result.stderr.lower():
                    print(f"✅ SUCCESS: {url} (inferred from output)")
                    return True, {"status": "success", "message": "Inferred from output"}
                elif "error" in result.stdout.lower() or "error" in result.stderr.lower():
                    print(f"❌ FAILED: {url} (error in output)")
                    print(f"   Output: {result.stdout[-500:]}")
                    print(f"   Error: {result.stderr[-500:]}")
                    return False, {"status": "error", "message": "Error in output"}
                else:
                    print(f"⚠️  UNCLEAR: {url} (no clear status)")
                    print(f"   Output: {result.stdout[-300:]}")
                    return False, {"status": "unknown", "message": "No clear status"}
                    
        except json.JSONDecodeError:
            # Couldn't parse JSON - check output for success/error
            if "success" in result.stdout.lower():
                print(f"✅ SUCCESS: {url} (inferred)")
                return True, {"status": "success"}
            else:
                print(f"❌ FAILED: {url} (could not parse output)")
                print(f"   Output: {result.stdout[-500:]}")
                print(f"   Error: {result.stderr[-500:]}")
                return False, {"status": "error", "message": "Could not parse output"}
                
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {url} (exceeded 10 minutes)")
        return False, {"status": "timeout", "message": "Timeout exceeded"}
    except Exception as e:
        print(f"❌ ERROR testing {url}: {e}")
        return False, {"status": "error", "message": str(e)}

async def main():
    """Test all sites with retry logic."""
    print("\n" + "="*80)
    print("Testing All Websites with Auto-Detection Mode")
    print("="*80)
    print(f"Total sites: {len(TEST_SITES)}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Create template file
    template_path = Path(__file__).parent / "auto_detect_template.json"
    template_path.write_text(json.dumps(AUTO_DETECT_TEMPLATE, indent=2))
    print(f"\n📄 Created auto-detection template: {template_path}")
    
    results = {}
    failed_sites = []
    
    # First pass: Test all sites
    print("\n" + "="*80)
    print("FIRST PASS: Testing all sites")
    print("="*80)
    
    for i, url in enumerate(TEST_SITES, 1):
        print(f"\n[{i}/{len(TEST_SITES)}] ", end="")
        success, result = await test_site_with_auto_detect(url, template_path)
        results[url] = {"success": success, "result": result, "attempts": 1}
        
        if not success:
            failed_sites.append(url)
        
        # Brief pause between sites
        await asyncio.sleep(2)
    
    # Second pass: Retry failed sites
    if failed_sites:
        print("\n" + "="*80)
        print(f"SECOND PASS: Retrying {len(failed_sites)} failed sites")
        print("="*80)
        
        for i, url in enumerate(failed_sites, 1):
            print(f"\n[Retry {i}/{len(failed_sites)}] ", end="")
            success, result = await test_site_with_auto_detect(url, template_path)
            
            if success:
                results[url]["success"] = True
                results[url]["result"] = result
                failed_sites.remove(url)
            
            results[url]["attempts"] = results[url].get("attempts", 0) + 1
            
            # Brief pause between retries
            await asyncio.sleep(3)
    
    # Print final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    passed = [url for url, data in results.items() if data["success"]]
    failed = [url for url, data in results.items() if not data["success"]]
    
    print(f"\n✅ PASSED ({len(passed)}/{len(TEST_SITES)}):")
    for url in passed:
        attempts = results[url].get("attempts", 1)
        print(f"   ✅ {url} ({attempts} attempt{'s' if attempts > 1 else ''})")
    
    if failed:
        print(f"\n❌ FAILED ({len(failed)}/{len(TEST_SITES)}):")
        for url in failed:
            attempts = results[url].get("attempts", 1)
            message = results[url]["result"].get("message", "Unknown error")
            print(f"   ❌ {url} ({attempts} attempt{'s' if attempts > 1 else ''})")
            print(f"      Error: {message[:100]}")
    
    print(f"\nTotal: {len(TEST_SITES)} | Passed: {len(passed)} | Failed: {len(failed)}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Save results to file
    results_file = Path(__file__).parent / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "total": len(TEST_SITES),
        "passed": len(passed),
        "failed": len(failed),
        "results": results
    }, indent=2))
    print(f"\n📄 Results saved to: {results_file}")
    
    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

