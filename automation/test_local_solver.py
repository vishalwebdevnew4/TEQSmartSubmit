#!/usr/bin/env python3
"""
Test script specifically for Local Captcha Solver.
Tests with a real Playwright browser instance.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the automation directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from captcha_solver import LocalCaptchaSolver


async def test_local_solver_initialization():
    """Test LocalCaptchaSolver initialization."""
    print("🧪 Testing LocalCaptchaSolver initialization...")
    
    # Test initialization without page
    solver = LocalCaptchaSolver()
    assert solver.page is None, "Page should be None initially"
    print("   ✅ LocalCaptchaSolver initialized without page")
    
    # Test that it requires page for solving
    try:
        await solver.solve_recaptcha_v2("test_key", "https://example.com")
        print("   ❌ Should have raised RuntimeError when page is None")
        return False
    except RuntimeError as e:
        if "requires a Playwright page object" in str(e):
            print("   ✅ Correctly raises RuntimeError when page is None")
            return True
        else:
            print(f"   ⚠️  Unexpected error message: {e}")
            return False
    except Exception as e:
        print(f"   ⚠️  Unexpected exception type: {type(e).__name__}: {e}")
        return False


async def test_local_solver_with_page():
    """Test LocalCaptchaSolver with a real Playwright page."""
    print("\n🧪 Testing LocalCaptchaSolver with Playwright page...")
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # Launch browser in headless mode
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Create test HTML page with reCAPTCHA
            test_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test reCAPTCHA Page</title>
                <script src="https://www.google.com/recaptcha/api.js" async defer></script>
            </head>
            <body>
                <h1>Test Page with reCAPTCHA</h1>
                <form>
                    <div class="g-recaptcha" data-sitekey="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"></div>
                    <textarea name="g-recaptcha-response" style="display:none;"></textarea>
                </form>
            </body>
            </html>
            """
            
            # Load the test page
            await page.set_content(test_html)
            await page.wait_for_timeout(2000)  # Wait for reCAPTCHA to load
            
            print("   ✅ Test page loaded with reCAPTCHA")
            
            # Initialize solver with page
            solver = LocalCaptchaSolver(page=page)
            assert solver.page is not None, "Page should be set"
            print("   ✅ LocalCaptchaSolver initialized with page")
            
            # Test helper methods
            print("\n   Testing helper methods...")
            
            # Test _check_challenge_present (should be False initially)
            challenge_present = await solver._check_challenge_present()
            print(f"   ✅ _check_challenge_present() returned: {challenge_present}")
            
            # Test _get_recaptcha_token (should return None initially)
            token = await solver._get_recaptcha_token()
            assert token is None or len(token) == 0, "Token should be None or empty initially"
            print(f"   ✅ _get_recaptcha_token() returned: {token if token else 'None'}")
            
            # Test that reCAPTCHA iframe exists
            iframe_exists = await page.evaluate("""
                () => {
                    const iframe = document.querySelector('iframe[src*="recaptcha"]');
                    return iframe !== null;
                }
            """)
            print(f"   ✅ reCAPTCHA iframe exists: {iframe_exists}")
            
            # Test _click_recaptcha_checkbox (should not raise error)
            try:
                await solver._click_recaptcha_checkbox()
                print("   ✅ _click_recaptcha_checkbox() executed without error")
                await page.wait_for_timeout(2000)  # Wait for potential challenge
                
                # Check if challenge appeared
                challenge_present_after = await solver._check_challenge_present()
                print(f"   ✅ Challenge present after click: {challenge_present_after}")
                
            except Exception as e:
                print(f"   ⚠️  _click_recaptcha_checkbox() error (expected in test): {str(e)[:50]}")
            
            # Clean up
            await browser.close()
            print("\n   ✅ Browser closed successfully")
            
        return True
        
    except ImportError:
        print("   ⚠️  Playwright not installed. Install with: pip install playwright")
        print("   ⚠️  Then run: playwright install chromium")
        return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_local_solver_methods_exist():
    """Test that all required methods exist."""
    print("\n🧪 Testing LocalCaptchaSolver methods exist...")
    
    solver = LocalCaptchaSolver()
    
    required_methods = [
        'solve_recaptcha_v2',
        'solve_hcaptcha',
        '_click_recaptcha_checkbox',
        '_check_challenge_present',
        '_solve_audio_challenge',
        '_solve_challenge',
        '_get_recaptcha_token',
        '_recognize_audio'
    ]
    
    all_exist = True
    for method_name in required_methods:
        if hasattr(solver, method_name):
            method = getattr(solver, method_name)
            if callable(method):
                print(f"   ✅ Method '{method_name}' exists and is callable")
            else:
                print(f"   ❌ Method '{method_name}' exists but is not callable")
                all_exist = False
        else:
            print(f"   ❌ Method '{method_name}' does not exist")
            all_exist = False
    
    return all_exist


async def test_solver_integration():
    """Test solver integration with run_submission pattern."""
    print("\n🧪 Testing LocalCaptchaSolver integration...")
    
    # Test that get_captcha_solver returns LocalCaptchaSolver
    from captcha_solver import get_captcha_solver
    
    # Clear any API keys to test local solver
    original_keys = {}
    for key in ["CAPTCHA_2CAPTCHA_API_KEY", "CAPTCHA_AI4CAP_API_KEY", "TEQ_CAPTCHA_API_KEY"]:
        original_keys[key] = os.environ.get(key)
        if key in os.environ:
            del os.environ[key]
    
    # Enable local solver
    original_local = os.environ.get("TEQ_USE_LOCAL_CAPTCHA_SOLVER")
    os.environ["TEQ_USE_LOCAL_CAPTCHA_SOLVER"] = "true"
    
    try:
        solver = get_captcha_solver("local")
        assert solver is not None, "Local solver should be returned"
        assert isinstance(solver, LocalCaptchaSolver), "Should return LocalCaptchaSolver instance"
        print("   ✅ get_captcha_solver('local') returns LocalCaptchaSolver")
        
        # Test auto detection with local enabled
        solver_auto = get_captcha_solver("auto")
        if solver_auto and isinstance(solver_auto, LocalCaptchaSolver):
            print("   ✅ get_captcha_solver('auto') returns LocalCaptchaSolver when enabled")
        else:
            print(f"   ⚠️  get_captcha_solver('auto') returned: {type(solver_auto).__name__ if solver_auto else None}")
        
    finally:
        # Restore original environment
        for key, value in original_keys.items():
            if value:
                os.environ[key] = value
        if original_local:
            os.environ["TEQ_USE_LOCAL_CAPTCHA_SOLVER"] = original_local
        elif "TEQ_USE_LOCAL_CAPTCHA_SOLVER" in os.environ:
            del os.environ["TEQ_USE_LOCAL_CAPTCHA_SOLVER"]
    
    return True


async def main():
    """Run all Local Solver tests."""
    print("=" * 60)
    print("Local Captcha Solver Test Suite")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Initialization", await test_local_solver_initialization()))
        results.append(("Methods Exist", await test_local_solver_methods_exist()))
        results.append(("Integration", await test_solver_integration()))
        results.append(("With Playwright Page", await test_local_solver_with_page()))
        
        print("\n" + "=" * 60)
        print("Test Results Summary:")
        print("=" * 60)
        
        all_passed = True
        for test_name, passed in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  {test_name:.<40} {status}")
            if not passed:
                all_passed = False
        
        print("=" * 60)
        if all_passed:
            print("✅ All Local Solver tests passed!")
        else:
            print("⚠️  Some tests failed or were skipped")
        print("=" * 60)
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

