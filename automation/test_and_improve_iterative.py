#!/usr/bin/env python3
"""
Test all websites iteratively, log failures, and keep improving until all succeed.
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

def log_failure(url, error_type, error_message, stderr, log_file):
    """Log failure details to file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "error_type": error_type,
        "error_message": error_message[:500],
        "stderr_preview": stderr[-1000:] if stderr else "",
    }
    log_file.write(json.dumps(log_entry) + "\n")
    log_file.flush()

async def test_site(url, template_path, failure_log):
    """Test a single site and return detailed results."""
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
            timeout=900,  # 15 minute timeout per site
            # Don't capture stderr - let it print to terminal
            stderr=subprocess.STDOUT  # Merge stderr with stdout
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
            
            if status == "success":
                print(f"✅ SUCCESS: {url}")
                return True, json_output, result.stderr, None
            else:
                error_type = "submission_error"
                if "captcha" in message.lower():
                    error_type = "captcha_error"
                elif "form" in message.lower() or "field" in message.lower():
                    error_type = "form_error"
                elif "timeout" in message.lower():
                    error_type = "timeout_error"
                
                print(f"❌ FAILED: {url} - {message[:60]}")
                log_failure(url, error_type, message, result.stderr, failure_log)
                return False, json_output, result.stderr, error_type
        else:
            # Check output for errors
            output_lower = (result.stdout + result.stderr).lower()
            
            if "syntaxerror" in output_lower or "syntax error" in output_lower:
                error_msg = "Syntax error in script"
                if result.stderr:
                    for line in result.stderr.split('\n'):
                        if "SyntaxError" in line:
                            error_msg = line.strip()[:200]
                            break
                print(f"❌ FAILED: {url} - {error_msg}")
                log_failure(url, "syntax_error", error_msg, result.stderr, failure_log)
                return False, {"status": "error", "message": error_msg}, result.stderr, "syntax_error"
            elif "success" in output_lower and "error" not in output_lower:
                print(f"✅ SUCCESS: {url} (inferred)")
                return True, {"status": "success"}, result.stderr, None
            else:
                # Try to extract meaningful error message
                error_msg = "Could not parse output"
                
                # Check stderr for errors
                if result.stderr:
                    stderr_lines = result.stderr.strip().split('\n')
                    # Look for error patterns
                    for line in reversed(stderr_lines):
                        line_lower = line.lower()
                        if any(keyword in line_lower for keyword in ["error", "failed", "exception", "traceback", "timeout"]):
                            error_msg = line.strip()[:300]
                            break
                    
                    # If no specific error found, get last few lines
                    if error_msg == "Could not parse output" and stderr_lines:
                        last_lines = "\n".join(stderr_lines[-5:])
                        error_msg = last_lines[:300] if last_lines else "Error in output"
                
                # Check stdout for errors too
                if result.stdout:
                    stdout_lines = result.stdout.strip().split('\n')
                    for line in reversed(stdout_lines):
                        line_lower = line.lower()
                        if any(keyword in line_lower for keyword in ["error", "failed", "exception"]):
                            if error_msg == "Could not parse output":
                                error_msg = line.strip()[:300]
                            break
                
                print(f"❌ FAILED: {url} - {error_msg[:80]}")
                log_failure(url, "parse_error", error_msg, result.stderr, failure_log)
                return False, {"status": "error", "message": error_msg}, result.stderr, "parse_error"
                
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {url} (exceeded 15 minutes)")
        log_failure(url, "timeout_error", "Test exceeded 15 minute timeout", "", failure_log)
        return False, {"status": "timeout"}, "", "timeout_error"
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERROR: {url} - {error_msg}")
        log_failure(url, "exception_error", error_msg, "", failure_log)
        return False, {"status": "error", "message": error_msg}, "", "exception_error"

def analyze_failures(results):
    """Analyze failure patterns."""
    error_counts = defaultdict(int)
    error_details = defaultdict(list)
    
    for url, data in results.items():
        if not data["success"]:
            error_type = data.get("error_type", "unknown")
            error_counts[error_type] += 1
            error_details[error_type].append({
                "url": url,
                "message": data["result"].get("message", "")[:100]
            })
    
    return error_counts, error_details

async def main():
    """Test all sites with iterative improvement."""
    print("\n" + "="*80)
    print("Testing All Websites - Iterative Improvement with Logging")
    print("="*80)
    print(f"Total sites: {len(TEST_SITES)}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Create template file
    template_path = Path(__file__).parent / "auto_detect_template.json"
    template_path.write_text(json.dumps(AUTO_DETECT_TEMPLATE, indent=2))
    
    # Create failure log file
    log_file_path = Path(__file__).parent / f"failure_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    failure_log = open(log_file_path, 'w')
    print(f"\n📄 Failure log: {log_file_path}")
    
    results = {}
    max_iterations = 10  # Maximum improvement iterations
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
            success, result, stderr, error_type = await test_site(url, template_path, failure_log)
            
            if url not in results:
                results[url] = {"success": False, "result": {}, "attempts": 0, "stderr": "", "error_type": None}
            
            results[url]["attempts"] = results[url].get("attempts", 0) + 1
            results[url]["result"] = result
            results[url]["stderr"] = stderr
            results[url]["error_type"] = error_type
            
            if success:
                results[url]["success"] = True
            
            await asyncio.sleep(1)
        
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
            error_counts, error_details = analyze_failures(results)
            
            for error_type, count in error_counts.items():
                print(f"   {error_type}: {count} sites")
                for detail in error_details[error_type][:3]:  # Show first 3
                    print(f"      - {detail['url']}: {detail['message'][:60]}")
            
            print(f"\n⏳ Waiting 3 seconds before next iteration...")
            await asyncio.sleep(3)
    
    # Close log file
    failure_log.close()
    
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
        error_counts, error_details = analyze_failures(results)
        for error_type, sites in error_details.items():
            print(f"\n   {error_type.upper()} ({len(sites)} sites):")
            for detail in sites:
                attempts = results[detail["url"]].get("attempts", 1)
                print(f"      ❌ {detail['url']} ({attempts} attempts)")
                print(f"         Error: {detail['message'][:80]}")
    
    print(f"\nTotal: {len(TEST_SITES)} | Passed: {len(passed)} | Failed: {len(failed)}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Failure log saved to: {log_file_path}")
    print("="*80)
    
    # Save results
    results_file = Path(__file__).parent / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "total": len(TEST_SITES),
        "passed": len(passed),
        "failed": len(failed),
        "iterations": iteration,
        "results": results,
        "error_analysis": dict(analyze_failures(results)[0])
    }, indent=2))
    print(f"\n📄 Results saved to: {results_file}")
    
    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

