#!/usr/bin/env python3
"""
Test all websites and iteratively improve until all succeed.
Analyzes failures, improves code, and retries.
"""

import asyncio
import json
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

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
    "post_submit_wait_ms": 30000,  # Increased timeout for slow sites
    "captcha_timeout_ms": 600000,  # 10 minutes for CAPTCHA solving
    "captcha": True,
    "use_auto_detect": True,
    "use_local_captcha_solver": True,
    "headless": False,  # Visible browser - open so user can watch
    "wait_until": "load",
    "test_data": {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "message": "This is an automated test submission from TEQSmartSubmit."
    }
}

async def test_site(url, template_path):
    """Test a single site."""
    print(f"\n{'='*80}")
    print(f"Testing: {url}")
    print(f"{'='*80}")
    
    script_path = Path(__file__).parent / "run_submission.py"
    
    try:
        result = subprocess.run(
            [
                sys.executable, 
                str(script_path),
                "--url", url,
                "--template", str(template_path)
            ],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        # Parse JSON output
        json_output = None
        output_lines = result.stdout.strip().split('\n')
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
            return status == "success", json_output, result.stderr
        else:
            # Check output for success indicators
            output_lower = (result.stdout + result.stderr).lower()
            # Check for syntax errors first
            if "syntaxerror" in output_lower or "syntax error" in output_lower:
                error_msg = "Syntax error in script"
                if result.stderr:
                    # Extract the actual error line
                    for line in result.stderr.split('\n'):
                        if "SyntaxError" in line or "syntax" in line.lower():
                            error_msg = line.strip()[:200]
                            break
                return False, {"status": "error", "message": error_msg}, result.stderr
            elif "success" in output_lower and "error" not in output_lower:
                return True, {"status": "success"}, result.stderr
            else:
                # Try to extract meaningful error message
                error_msg = "Could not parse output"
                if result.stderr:
                    # Get last few lines of stderr
                    stderr_lines = result.stderr.strip().split('\n')
                    if stderr_lines:
                        error_msg = stderr_lines[-1][:200] if len(stderr_lines[-1]) > 0 else stderr_lines[-2][:200] if len(stderr_lines) > 1 else "Error in output"
                return False, {"status": "error", "message": error_msg}, result.stderr
                
    except subprocess.TimeoutExpired:
        return False, {"status": "timeout"}, ""
    except Exception as e:
        return False, {"status": "error", "message": str(e)}, ""

def analyze_failures(results):
    """Analyze failure patterns to identify common issues."""
    error_patterns = defaultdict(list)
    
    for url, data in results.items():
        if not data["success"]:
            message = data["result"].get("message", "").lower()
            stderr = data.get("stderr", "").lower()
            
            # Categorize errors
            if "captcha" in message or "captcha" in stderr:
                error_patterns["captcha"].append(url)
            elif "field" in message or "not found" in message:
                error_patterns["field_not_found"].append(url)
            elif "submit" in message or "button" in message:
                error_patterns["submit_button"].append(url)
            elif "timeout" in message:
                error_patterns["timeout"].append(url)
            elif "form" in message:
                error_patterns["form_not_found"].append(url)
            else:
                error_patterns["other"].append(url)
    
    return error_patterns

async def main():
    """Test all sites with iterative improvement."""
    print("\n" + "="*80)
    print("Testing All Websites - Iterative Improvement Mode")
    print("="*80)
    print(f"Total sites: {len(TEST_SITES)}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Create template file
    template_path = Path(__file__).parent / "auto_detect_template.json"
    template_path.write_text(json.dumps(AUTO_DETECT_TEMPLATE, indent=2))
    
    results = {}
    max_iterations = 5  # Maximum improvement iterations
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'='*80}")
        print(f"ITERATION {iteration}")
        print(f"{'='*80}")
        
        # Test all sites
        for i, url in enumerate(TEST_SITES, 1):
            if url in results and results[url]["success"]:
                print(f"[{i}/{len(TEST_SITES)}] ⏭️  Skipping (already passed): {url}")
                continue
            
            print(f"[{i}/{len(TEST_SITES)}] ", end="")
            success, result, stderr = await test_site(url, template_path)
            
            if url not in results:
                results[url] = {"success": False, "result": {}, "attempts": 0, "stderr": ""}
            
            results[url]["attempts"] = results[url].get("attempts", 0) + 1
            results[url]["result"] = result
            results[url]["stderr"] = stderr
            
            if success:
                results[url]["success"] = True
                print(f"✅ SUCCESS: {url}")
            else:
                print(f"❌ FAILED: {url} - {result.get('message', 'Unknown')[:60]}")
            
            # Brief pause between tests (browser will close automatically after each test)
            await asyncio.sleep(2)
        
        # Check if all passed
        passed = sum(1 for r in results.values() if r["success"])
        failed = len(TEST_SITES) - passed
        
        print(f"\n{'='*80}")
        print(f"ITERATION {iteration} RESULTS: {passed}/{len(TEST_SITES)} passed, {failed} failed")
        print(f"{'='*80}")
        
        if failed == 0:
            print("\n🎉 ALL SITES PASSED!")
            break
        
        # Analyze failures
        if iteration < max_iterations:
            print("\n📊 Analyzing failures...")
            error_patterns = analyze_failures(results)
            
            for error_type, urls in error_patterns.items():
                if urls:
                    print(f"   {error_type}: {len(urls)} sites")
            
            # Wait before next iteration
            print(f"\n⏳ Waiting 5 seconds before next iteration...")
            await asyncio.sleep(5)
    
    # Final summary
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
    
    # Save results
    results_file = Path(__file__).parent / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "total": len(TEST_SITES),
        "passed": len(passed),
        "failed": len(failed),
        "iterations": iteration,
        "results": results
    }, indent=2))
    print(f"\n📄 Results saved to: {results_file}")
    
    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

