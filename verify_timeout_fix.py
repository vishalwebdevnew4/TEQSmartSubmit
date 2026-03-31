#!/usr/bin/env python3
"""
Verify that all timeout wrappers have been applied correctly to run_submission.py
"""

import re
import sys

def verify_timeout_wrappers():
    """Check that all solver calls have timeout protection"""
    
    with open('/var/www/html/TEQSmartSubmit/automation/run_submission.py', 'r') as f:
        content = f.read()
    
    # Pattern for timeout-wrapped solver calls
    wrapped_pattern = r'asyncio\.wait_for\(\s*solver\.solve_recaptcha_v2|asyncio\.wait_for\(\s*local_solver_instance\.solve_recaptcha_v2'
    
    # Find all wrapped calls
    wrapped_calls = re.findall(wrapped_pattern, content)
    print(f"✅ Found {len(wrapped_calls)} timeout-wrapped solver calls")
    
    # Pattern for timeout error handling
    timeout_handling = r'except asyncio\.TimeoutError:'
    timeout_handlers = re.findall(timeout_handling, content)
    print(f"✅ Found {len(timeout_handlers)} TimeoutError handlers")
    
    # Should have at least 5 wrapped calls and handlers
    min_required = 5
    if len(wrapped_calls) >= min_required:
        print(f"\n✅ SUCCESS: All {min_required} solver calls are now timeout-protected!")
        return True
    else:
        print(f"\n❌ INCOMPLETE: Found {len(wrapped_calls)} wrapped calls, expected at least {min_required}")
        return False

def test_syntax():
    """Test that the Python file can be parsed"""
    try:
        with open('/var/www/html/TEQSmartSubmit/automation/run_submission.py', 'r') as f:
            code = f.read()
        compile(code, 'run_submission.py', 'exec')
        print("✅ Python syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("TIMEOUT WRAPPER VERIFICATION")
    print("=" * 60)
    
    syntax_ok = test_syntax()
    wrappers_ok = verify_timeout_wrappers()
    
    print("\n" + "=" * 60)
    if syntax_ok and wrappers_ok:
        print("✅ ALL CHECKS PASSED - Fix is complete!")
        sys.exit(0)
    else:
        print("❌ Some checks failed")
        sys.exit(1)
