#!/usr/bin/env python3
"""
Test all websites and print detailed logs to terminal for debugging.
"""

import asyncio
import json
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
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Print output in real-time
        output_lines = []
        json_output = None
        
        for line in process.stdout:
            line = line.rstrip()
            print(line, flush=True)  # Print to terminal immediately
            output_lines.append(line)
            
            # Try to parse JSON from output
            if line.strip().startswith('{'):
                try:
                    json_output = json.loads(line)
                except:
                    pass
        
        # Wait for process to complete
        return_code = process.wait(timeout=900)
        
        # Combine all output
        full_output = "\n".join(output_lines)
        
        # Parse result
        if json_output:
            status = json_output.get("status", "unknown")
            message = json_output.get("message", "")
            
            if status == "success":
                print(f"\n✅ SUCCESS: {url}")
                print(f"   Message: {message}")
                return True, json_output
            else:
                print(f"\n❌ FAILED: {url}")
                print(f"   Status: {status}")
                print(f"   Message: {message}")
                return False, json_output
        else:
            # Check output for success/error
            output_lower = full_output.lower()
            if "success" in output_lower and "error" not in output_lower:
                print(f"\n✅ SUCCESS: {url} (inferred from output)")
                return True, {"status": "success"}
            else:
                print(f"\n❌ FAILED: {url} (could not parse JSON output)")
                # Show last few lines for debugging
                last_lines = "\n".join(output_lines[-10:])
                print(f"   Last output lines:\n{last_lines}")
                return False, {"status": "error", "message": "Could not parse output"}
                
    except subprocess.TimeoutExpired:
        print(f"\n⏰ TIMEOUT: {url} (exceeded 15 minutes)")
        process.kill()
        return False, {"status": "timeout"}
    except Exception as e:
        print(f"\n❌ ERROR: {url} - {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {"status": "error", "message": str(e)}

async def main():
    """Test all sites with detailed logging."""
    print("\n" + "="*80)
    print("Testing All Websites with Detailed Logs")
    print("="*80)
    print(f"Total sites: {len(TEST_SITES)}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Create template file
    template_path = Path(__file__).parent / "auto_detect_template.json"
    template_path.write_text(json.dumps(AUTO_DETECT_TEMPLATE, indent=2))
    print(f"\n📄 Using template: {template_path}")
    
    results = {}
    
    # Test all sites
    for i, url in enumerate(TEST_SITES, 1):
        print(f"\n\n{'#'*80}")
        print(f"# SITE {i}/{len(TEST_SITES)}")
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
    
    print(f"\n✅ PASSED ({len(passed)}/{len(TEST_SITES)}):")
    for url in passed:
        print(f"   ✅ {url}")
    
    if failed:
        print(f"\n❌ FAILED ({len(failed)}/{len(TEST_SITES)}):")
        for url in failed:
            message = results[url]["result"].get("message", "Unknown error")
            print(f"   ❌ {url}")
            print(f"      Error: {message[:100]}")
    
    print(f"\nTotal: {len(TEST_SITES)} | Passed: {len(passed)} | Failed: {len(failed)}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Save results
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

