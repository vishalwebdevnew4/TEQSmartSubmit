#!/usr/bin/env python3
"""
Comprehensive test for the CAPTCHA solver system.
Tests all components and integrations.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    try:
        from automation.captcha_solver import (
            CaptchaSolver,
            TwoCaptchaSolver,
            AntiCaptchaSolver,
            CapSolverSolver,
            LocalCaptchaSolver,
            get_captcha_solver
        )
        print("✅ All CAPTCHA solver classes imported")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_solver_initialization():
    """Test solver initialization."""
    print("\n" + "=" * 60)
    print("TEST 2: Solver Initialization")
    print("=" * 60)
    
    try:
        from automation.captcha_solver import TwoCaptchaSolver, get_captcha_solver
        
        # Test with API key
        solver = TwoCaptchaSolver("test-key-123")
        print("✅ TwoCaptchaSolver initialized")
        
        # Test auto-detection
        solver_auto = get_captcha_solver("auto")
        if solver_auto:
            print(f"✅ Auto-detected solver: {type(solver_auto).__name__}")
        else:
            print("ℹ️  No API keys found (expected)")
        
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


def test_integration():
    """Test integration with main automation script."""
    print("\n" + "=" * 60)
    print("TEST 3: Integration with Automation Script")
    print("=" * 60)
    
    try:
        from automation.run_submission import (
            detect_captcha,
            inject_recaptcha_token,
            get_captcha_solver
        )
        print("✅ Main script imports CAPTCHA solver correctly")
        
        # Test solver is accessible
        solver = get_captcha_solver("auto")
        print(f"✅ Solver accessible from main script: {solver is not None or 'No API key'}")
        
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_captcha_detection():
    """Test CAPTCHA detection on a real page."""
    print("\n" + "=" * 60)
    print("TEST 4: CAPTCHA Detection (Real Page)")
    print("=" * 60)
    
    try:
        from playwright.async_api import async_playwright
        from automation.run_submission import detect_captcha
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print("Loading test page...")
            await page.goto('https://interiordesign.xcelanceweb.com/', timeout=60000, wait_until='load')
            await asyncio.sleep(3)
            
            captcha_info = await detect_captcha(page)
            
            print(f"✅ Detection function works")
            print(f"   Type: {captcha_info.get('type', 'none')}")
            print(f"   Present: {captcha_info.get('present', False)}")
            if captcha_info.get('siteKey'):
                print(f"   Site Key: {captcha_info.get('siteKey')[:30]}...")
            
            await browser.close()
            return True
            
    except Exception as e:
        print(f"❌ Detection test failed: {e}")
        return False


def test_configuration():
    """Test configuration options."""
    print("\n" + "=" * 60)
    print("TEST 5: Configuration Options")
    print("=" * 60)
    
    try:
        from automation.captcha_solver import get_captcha_solver
        
        # Test different service configurations
        services = ["2captcha", "anticaptcha", "capsolver", "auto"]
        
        for service in services:
            solver = get_captcha_solver(service)
            status = "✅" if solver or service == "auto" else "⚠️"
            print(f"{status} Service '{service}': {'Available' if solver else 'No API key'}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 CAPTCHA SOLVER SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Solver Initialization", test_solver_initialization()))
    results.append(("Integration", test_integration()))
    results.append(("Configuration", test_configuration()))
    results.append(("CAPTCHA Detection", asyncio.run(test_captcha_detection())))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! CAPTCHA solver system is ready.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

