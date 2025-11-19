#!/usr/bin/env python3
"""
Test all three websites in headless mode.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

# Add the automation directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Test URLs
TEST_SITES = [
    "https://teqtopaustralia.xcelanceweb.com/contact",
    "https://petpointmedia.com/contact-us/",
    "https://interiordesign.xcelanceweb.com/"
]

async def test_site(url):
    """Test a single site."""
    print("\n" + "="*80)
    print(f"Testing: {url}")
    print("="*80)
    
    script_path = Path(__file__).parent / "test_local_solver_website.py"
    
    try:
        # Run the test script
        result = subprocess.run(
            [sys.executable, str(script_path), url],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per site
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"\n✅ SUCCESS: {url}")
            return True
        else:
            print(f"\n❌ FAILED: {url} (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n⏰ TIMEOUT: {url} (exceeded 10 minutes)")
        return False
    except Exception as e:
        print(f"\n❌ ERROR testing {url}: {e}")
        return False

async def main():
    """Test all sites."""
    print("\n" + "="*80)
    print("Testing All Sites in Headless Mode")
    print("="*80)
    
    results = {}
    
    for url in TEST_SITES:
        success = await test_site(url)
        results[url] = success
        # Brief pause between sites
        await asyncio.sleep(2)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for url, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {url}")
    
    total = len(results)
    passed = sum(1 for s in results.values() if s)
    failed = total - passed
    
    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

