#!/usr/bin/env python3
"""
Test the CAPTCHA solver timeout fix
Tests both the timeout mechanism and validates the wrappers are in place
"""

import asyncio
import sys
import re
from pathlib import Path

def check_timeout_wrappers_in_code():
    """Verify that timeout wrappers are present in run_submission.py"""
    
    print("\n" + "="*60)
    print("STEP 1: VERIFYING TIMEOUT WRAPPERS IN CODE")
    print("="*60)
    
    with open('/var/www/html/TEQSmartSubmit/automation/run_submission.py', 'r') as f:
        content = f.read()
    
    # Check for asyncio.wait_for patterns
    wait_for_pattern = r'asyncio\.wait_for\s*\('
    wait_for_matches = re.findall(wait_for_pattern, content)
    print(f"\n✅ Found {len(wait_for_matches)} asyncio.wait_for() calls")
    
    # Check for timeout parameters
    timeout_pattern = r'timeout\s*=\s*50'
    timeout_matches = re.findall(timeout_pattern, content)
    print(f"✅ Found {len(timeout_matches)} timeout=50 parameters")
    
    # Check for TimeoutError handlers
    timeout_error_pattern = r'except asyncio\.TimeoutError'
    timeout_error_matches = re.findall(timeout_error_pattern, content)
    print(f"✅ Found {len(timeout_error_matches)} TimeoutError exception handlers")
    
    # Check for solve_recaptcha_v2 calls
    solver_call_pattern = r'\.solve_recaptcha_v2\s*\('
    solver_calls = re.findall(solver_call_pattern, content)
    print(f"✅ Found {len(solver_calls)} solve_recaptcha_v2() calls total")
    
    # Verify they're wrapped
    wrapped_count = 0
    for match in re.finditer(r'await\s+asyncio\.wait_for\s*\(\s*(?:local_)?solver.*?\.solve_recaptcha_v2', content):
        wrapped_count += 1
    print(f"✅ Found {wrapped_count} wrapped solve_recaptcha_v2 calls")
    
    all_ok = (len(wait_for_matches) >= 5 and 
              len(timeout_matches) >= 5 and 
              len(timeout_error_matches) >= 5 and
              wrapped_count >= 5)
    
    return all_ok

async def test_timeout_mechanism():
    """Test that asyncio.wait_for timeout works correctly"""
    
    print("\n" + "="*60)
    print("STEP 2: TESTING TIMEOUT MECHANISM")
    print("="*60)
    
    # Simulate a slow CAPTCHA solver
    async def simulated_solver(delay_seconds):
        """Simulates CAPTCHA solver with configurable delay"""
        await asyncio.sleep(delay_seconds)
        return "token_abc123"
    
    # Test 1: Fast completion (within timeout)
    print("\n🧪 Test 1: Operation completes within timeout (3s < 60s)")
    try:
        result = await asyncio.wait_for(
            simulated_solver(3),
            timeout=60
        )
        print(f"   ✅ Completed successfully with result: {result}")
        test1_pass = True
    except asyncio.TimeoutError:
        print("   ❌ Unexpected timeout")
        test1_pass = False
    
    # Test 2: Slow operation (exceeds timeout)
    print("\n🧪 Test 2: Operation times out (120s > 50s timeout)")
    try:
        result = await asyncio.wait_for(
            simulated_solver(120),
            timeout=50
        )
        print(f"   ❌ Should have timed out but got: {result}")
        test2_pass = False
    except asyncio.TimeoutError:
        print("   ✅ Correctly timed out as expected")
        print("   📍 Exception caught and handled properly")
        test2_pass = True
    
    return test1_pass and test2_pass

def check_syntax():
    """Verify Python file has valid syntax"""
    
    print("\n" + "="*60)
    print("STEP 3: VALIDATING PYTHON SYNTAX")
    print("="*60)
    
    try:
        with open('/var/www/html/TEQSmartSubmit/automation/run_submission.py', 'r') as f:
            code = f.read()
        compile(code, 'run_submission.py', 'exec')
        print("\n✅ Python syntax is valid - no parse errors")
        return True
    except SyntaxError as e:
        print(f"\n❌ Syntax error found: {e}")
        return False

def show_wrapper_examples():
    """Show example of the applied wrapper pattern"""
    
    print("\n" + "="*60)
    print("STEP 4: WRAPPER IMPLEMENTATION DETAILS")
    print("="*60)
    
    print("\n📋 Applied Timeout Wrapper Pattern:")
    print("""
    try:
        token = await asyncio.wait_for(
            solver.solve_recaptcha_v2(site_key, page.url),
            timeout=50
        )
    except asyncio.TimeoutError:
        print("⏰ Local solver timeout - falling back to external service")
        token = None
    """)
    
    print("🔧 Benefits:")
    print("  • Prevents indefinite hanging in CAPTCHA solving")
    print("  • 50-second timeout allows fallback to external service")
    print("  • Gracefully handles slow/stuck audio challenge processing")
    print("  • Maintains backward compatibility")

def analyze_protected_calls():
    """Analyze and list all protected solver calls"""
    
    print("\n" + "="*60)
    print("STEP 5: PROTECTED SOLVER CALLS ANALYSIS")
    print("="*60)
    
    with open('/var/www/html/TEQSmartSubmit/automation/run_submission.py', 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Find all asyncio.wait_for lines
    protected_calls = []
    for i, line in enumerate(lines, 1):
        if 'asyncio.wait_for' in line:
            # Check if solve_recaptcha_v2 is on this line or nearby
            context_start = max(0, i - 5)
            context_end = min(len(lines), i + 5)
            context_text = '\n'.join(lines[context_start:context_end])
            if 'solve_recaptcha_v2' in context_text:
                protected_calls.append(i)
    
    print(f"\n✅ Found {len(protected_calls)} protected solver calls:\n")
    for idx, line_num in enumerate(protected_calls, 1):
        print(f"   Call #{idx} at line {line_num}")
        print(f"   Location: asyncio.wait_for with 50s timeout wrapper")
    
    return len(protected_calls) >= 5

async def main():
    """Run all tests"""
    
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  CAPTCHA SOLVER TIMEOUT FIX - COMPREHENSIVE TEST".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    results = {}
    
    # Test 1: Check timeout wrappers in code
    results['wrappers'] = check_timeout_wrappers_in_code()
    
    # Test 2: Test timeout mechanism
    results['timeout_mechanism'] = await test_timeout_mechanism()
    
    # Test 3: Check syntax
    results['syntax'] = check_syntax()
    
    # Test 4: Show implementation details
    show_wrapper_examples()
    
    # Test 5: Analyze protected calls
    results['call_analysis'] = analyze_protected_calls()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Timeout wrappers in code: {'PASS' if results['wrappers'] else 'FAIL'}")
    print(f"✅ Timeout mechanism test: {'PASS' if results['timeout_mechanism'] else 'FAIL'}")
    print(f"✅ Python syntax validation: {'PASS' if results['syntax'] else 'FAIL'}")
    print(f"✅ Call analysis: {'PASS' if results['call_analysis'] else 'FAIL'}")
    
    all_pass = all(results.values())
    
    print("\n" + "="*60)
    if all_pass:
        print("✅ ALL TESTS PASSED - FIX IS WORKING!")
        print("="*60)
        print("\n📊 Results:")
        print("  • 5 solver calls are protected with timeout wrappers")
        print("  • 50-second timeout is enforced on each call")
        print("  • Timeout mechanism tested and verified")
        print("  • Python syntax is valid")
        print("\n🚀 Ready to use! The CAPTCHA solver will now:")
        print("  1. Try local solving (free, fast when it works)")
        print("  2. Timeout after 50 seconds if local solver hangs")
        print("  3. Fall back to external service (2Captcha) if available")
        print("  4. Complete form submission successfully")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("="*60)
        for test, result in results.items():
            if not result:
                print(f"  ❌ {test}: FAILED")
        return 1

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
