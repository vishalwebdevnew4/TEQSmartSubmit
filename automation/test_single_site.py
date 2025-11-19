#!/usr/bin/env python3
"""
Test a single website with full logging to terminal.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Add the automation directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Test URL - you can change this
TEST_URL = "https://petpointmedia.com/contact-us/"

# Create a minimal template for auto-detection
AUTO_DETECT_TEMPLATE = {
    "fields": [],
    "submit_selector": "button[type='submit'], input[type='submit']",
    "post_submit_wait_ms": 30000,
    "captcha_timeout_ms": 600000,
    "captcha": True,
    "use_auto_detect": True,
    "use_local_captcha_solver": True,
    "headless": False,  # Visible browser
    "wait_until": "load",
    "test_data": {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "message": "This is an automated test submission from TEQSmartSubmit."
    }
}

async def test_site(url):
    """Test a single site and print all output."""
    print("\n" + "="*80)
    print(f"Testing: {url}")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n📋 Watch the browser window to see the automation in action!")
    print("="*80 + "\n")
    
    script_path = Path(__file__).parent / "run_submission.py"
    template_path = Path(__file__).parent / "auto_detect_template.json"
    template_path.write_text(json.dumps(AUTO_DETECT_TEMPLATE, indent=2))
    
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
        
        print("🚀 Starting automation...\n")
        
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
        
        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80)
        
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
            output_lower = full_output.lower()
            if "success" in output_lower and "error" not in output_lower:
                print(f"\n✅ SUCCESS! (inferred from output)")
                return True, {"status": "success"}
            else:
                print(f"\n❌ FAILED! (could not parse JSON output)")
                # Show last few lines for debugging
                last_lines = "\n".join(output_lines[-20:])
                print(f"\n   Last output lines:\n{last_lines}")
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
    """Test single site."""
    url = sys.argv[1] if len(sys.argv) > 1 else TEST_URL
    
    print("\n" + "="*80)
    print("Single Site Test with Full Logging")
    print("="*80)
    print(f"URL: {url}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n💡 TIP: Watch the browser window to see what's happening!")
    print("💡 TIP: All logs will appear below in real-time")
    print("="*80)
    
    success, result = await test_site(url)
    
    print("\n" + "="*80)
    if success:
        print("✅ TEST PASSED!")
    else:
        print("❌ TEST FAILED!")
        print(f"   Error: {result.get('message', 'Unknown error')}")
    print("="*80)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

