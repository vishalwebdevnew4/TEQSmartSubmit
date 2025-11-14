#!/usr/bin/env python3
"""
Test script for CAPTCHA resolver.
Tests basic functionality and integration.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the automation directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from captcha_solver import get_captcha_solver, LocalCaptchaSolver


async def test_get_captcha_solver():
    """Test getting captcha solver instances."""
    print("🧪 Testing get_captcha_solver()...")
    
    # Test auto detection
    print("\n1. Testing auto detection (no API keys)...")
    solver = get_captcha_solver("auto")
    if solver is None:
        print("   ✅ Correctly returned None when no API keys found")
    else:
        print(f"   ⚠️  Unexpected solver returned: {type(solver).__name__}")
    
    # Test 2captcha
    print("\n2. Testing 2captcha service...")
    original_key = os.environ.get("CAPTCHA_2CAPTCHA_API_KEY")
    os.environ["CAPTCHA_2CAPTCHA_API_KEY"] = "test_key_123"
    solver = get_captcha_solver("2captcha")
    if solver and hasattr(solver, 'api_key') and solver.api_key == "test_key_123":
        print("   ✅ 2captcha solver created correctly")
    else:
        print("   ❌ 2captcha solver not created correctly")
    
    # Restore original key
    if original_key:
        os.environ["CAPTCHA_2CAPTCHA_API_KEY"] = original_key
    else:
        os.environ.pop("CAPTCHA_2CAPTCHA_API_KEY", None)
    
    # Test AI4CAP detection
    print("\n3. Testing AI4CAP detection (sk_ prefix)...")
    os.environ["CAPTCHA_AI4CAP_API_KEY"] = "sk_test_key_123"
    solver = get_captcha_solver("auto")
    if solver and type(solver).__name__ == "AI4CAPSolver":
        print("   ✅ AI4CAP solver auto-detected correctly")
    else:
        print(f"   ⚠️  Expected AI4CAPSolver, got: {type(solver).__name__ if solver else None}")
    os.environ.pop("CAPTCHA_AI4CAP_API_KEY", None)
    
    # Test local solver
    print("\n4. Testing local solver...")
    solver = get_captcha_solver("local")
    if solver and isinstance(solver, LocalCaptchaSolver):
        print("   ✅ Local solver created correctly")
    else:
        print("   ❌ Local solver not created correctly")
    
    print("\n✅ get_captcha_solver() tests completed\n")


async def test_solver_initialization():
    """Test solver initialization."""
    print("🧪 Testing solver initialization...")
    
    # Test TwoCaptchaSolver
    try:
        from captcha_solver import TwoCaptchaSolver
        solver = TwoCaptchaSolver("test_key")
        assert solver.api_key == "test_key"
        assert solver.base_url == "http://2captcha.com"
        print("   ✅ TwoCaptchaSolver initialized correctly")
    except Exception as e:
        print(f"   ❌ TwoCaptchaSolver initialization failed: {e}")
    
    # Test AI4CAPSolver
    try:
        from captcha_solver import AI4CAPSolver
        solver = AI4CAPSolver("sk_test_key")
        assert solver.api_key == "sk_test_key"
        assert solver.base_url == "https://api.ai4cap.com"
        print("   ✅ AI4CAPSolver initialized correctly")
    except Exception as e:
        print(f"   ❌ AI4CAPSolver initialization failed: {e}")
    
    # Test LocalCaptchaSolver
    try:
        solver = LocalCaptchaSolver()
        assert solver.page is None
        print("   ✅ LocalCaptchaSolver initialized correctly")
    except Exception as e:
        print(f"   ❌ LocalCaptchaSolver initialization failed: {e}")
    
    print("\n✅ Solver initialization tests completed\n")


async def test_api_methods():
    """Test API methods (without actual API calls)."""
    print("🧪 Testing API methods (syntax only)...")
    
    # Test that methods exist and are callable
    try:
        from captcha_solver import TwoCaptchaSolver
        solver = TwoCaptchaSolver("test_key")
        
        # Check method exists
        assert hasattr(solver, 'solve_recaptcha_v2')
        assert hasattr(solver, 'solve_hcaptcha')
        assert callable(solver.solve_recaptcha_v2)
        assert callable(solver.solve_hcaptcha)
        print("   ✅ TwoCaptchaSolver methods exist and are callable")
        
        # Test with None API key (should return None without making API call)
        solver_no_key = TwoCaptchaSolver("")
        result = await solver_no_key.solve_recaptcha_v2("test_site_key", "https://example.com")
        assert result is None, "Should return None when API key is empty"
        print("   ✅ TwoCaptchaSolver returns None when API key is empty")
        
    except Exception as e:
        print(f"   ❌ API method test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ API methods tests completed\n")


async def test_error_handling():
    """Test error handling."""
    print("🧪 Testing error handling...")
    
    try:
        from captcha_solver import LocalCaptchaSolver
        solver = LocalCaptchaSolver()
        
        # Test that it raises error when page is None
        try:
            await solver.solve_recaptcha_v2("test_key", "https://example.com")
            print("   ⚠️  Should have raised RuntimeError when page is None")
        except RuntimeError as e:
            if "requires a Playwright page object" in str(e):
                print("   ✅ Correctly raises RuntimeError when page is None")
            else:
                print(f"   ⚠️  Unexpected error message: {e}")
        except Exception as e:
            print(f"   ⚠️  Unexpected exception type: {type(e).__name__}: {e}")
            
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Error handling tests completed\n")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("CAPTCHA Solver Test Suite")
    print("=" * 60)
    
    try:
        await test_get_captcha_solver()
        await test_solver_initialization()
        await test_api_methods()
        await test_error_handling()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

