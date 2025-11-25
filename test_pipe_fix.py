#!/usr/bin/env python3
"""
Test script to verify the pipe blocking fix works correctly.
This simulates the server environment where stderr is a pipe.
"""

import sys
import subprocess
import time
import os
from pathlib import Path

def test_script_non_blocking():
    """Test that the script doesn't block when writing to a pipe."""
    
    script_path = Path(__file__).parent / "automation" / "submission" / "form_discovery.py"
    
    if not script_path.exists():
        print(f"❌ Script not found at: {script_path}")
        return False
    
    print(f"✅ Script found: {script_path}")
    print("🧪 Testing non-blocking behavior...")
    print("")
    
    # Create a test template
    test_template = {
        "name": "Test Template",
        "max_timeout_seconds": 10,
        "fields": []
    }
    
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_template, f)
        template_path = f.name
    
    try:
        # Run the script with a pipe (simulating server environment)
        # Use a short timeout to detect if it hangs
        print("📍 Starting script with pipe (simulating server)...")
        print("   (This should complete quickly, not hang)")
        print("")
        
        start_time = time.time()
        
        process = subprocess.Popen(
            [sys.executable, str(script_path), "--url", "https://example.com", "--template", template_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,  # Unbuffered
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )
        
        # Read stderr in real-time to prevent buffer from filling
        stderr_lines = []
        stdout_lines = []
        
        # Set a timeout
        timeout = 15  # seconds
        elapsed = 0
        
        while process.poll() is None and elapsed < timeout:
            # Read available data
            if process.stderr:
                try:
                    line = process.stderr.readline()
                    if line:
                        stderr_lines.append(line)
                        print(f"   [stderr] {line.rstrip()}")
                        # Check if we got past the problematic point
                        if "📍 [main_async] Function called" in line:
                            print("   ✅ Got past 'Function called' - checking for more output...")
                            # Wait a bit more to see if it continues
                            time.sleep(2)
                            # Try to read more
                            while True:
                                try:
                                    more_line = process.stderr.readline()
                                    if more_line:
                                        stderr_lines.append(more_line)
                                        print(f"   [stderr] {more_line.rstrip()}")
                                    else:
                                        break
                                except:
                                    break
                except:
                    pass
            
            if process.stdout:
                try:
                    line = process.stdout.readline()
                    if line:
                        stdout_lines.append(line)
                except:
                    pass
            
            elapsed = time.time() - start_time
            time.sleep(0.1)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"\n⚠️  Process still running after {elapsed:.1f} seconds")
            print("   This might indicate blocking, or the script is just slow")
            process.terminate()
            try:
                process.wait(timeout=5)
            except:
                process.kill()
            return False
        
        elapsed = time.time() - start_time
        return_code = process.returncode
        
        # Get remaining output
        remaining_stderr, remaining_stdout = process.communicate(timeout=5)
        if remaining_stderr:
            stderr_lines.append(remaining_stderr)
        if remaining_stdout:
            stdout_lines.append(remaining_stdout)
        
        print("")
        print(f"⏱️  Process completed in {elapsed:.2f} seconds")
        print(f"📊 Return code: {return_code}")
        print(f"📝 Stderr lines: {len(stderr_lines)}")
        print(f"📝 Stdout lines: {len(stdout_lines)}")
        print("")
        
        # Check if we got past the problematic point
        all_stderr = "".join(stderr_lines)
        if "📍 [main_async] Function called" in all_stderr:
            print("✅ SUCCESS: Script got past 'Function called'")
            
            # Check for subsequent messages
            success_indicators = [
                "🚀 AUTOMATION STARTING",
                "📍 [main_async] After initial log prints",
                "📍 [main_async] About to get URL",
                "📍 [main_async] URL:",
            ]
            
            found_indicators = []
            for indicator in success_indicators:
                if indicator in all_stderr:
                    found_indicators.append(indicator)
            
            if found_indicators:
                print(f"✅ Found {len(found_indicators)} subsequent log messages:")
                for ind in found_indicators:
                    print(f"   - {ind}")
                print("")
                print("🎉 FIX VERIFIED: Script is not blocking on pipe writes!")
                return True
            else:
                print("⚠️  Got past 'Function called' but no subsequent messages found")
                print("   This might be OK if the script failed for other reasons")
                return True  # Still a success for the blocking fix
        else:
            print("❌ FAILED: Script did not get past 'Function called'")
            print("   This might indicate the fix didn't work, or script failed earlier")
            return False
        
    except subprocess.TimeoutExpired:
        print("❌ FAILED: Process timed out - likely still blocking")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ FAILED: Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            os.unlink(template_path)
        except:
            pass

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 Testing form_discovery.py Pipe Blocking Fix")
    print("=" * 80)
    print("")
    
    success = test_script_non_blocking()
    
    print("")
    print("=" * 80)
    if success:
        print("✅ TEST PASSED: Fix appears to be working")
        sys.exit(0)
    else:
        print("❌ TEST FAILED: Fix may not be working correctly")
        sys.exit(1)

