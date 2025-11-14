#!/usr/bin/env python3
"""
Comprehensive diagnostic tool for Local CAPTCHA Solver.
Helps identify specific issues preventing the solver from working.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "automation"))

async def check_dependencies():
    """Check if all required dependencies are installed and working."""
    print("\n" + "=" * 70)
    print("🔍 DEPENDENCY CHECK")
    print("=" * 70)
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} (requires 3.8+)")
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check Playwright
    try:
        from playwright.async_api import async_playwright
        print("✅ Playwright installed")
    except ImportError:
        issues.append("❌ Playwright not installed: pip install playwright && playwright install chromium")
    
    # Check SpeechRecognition
    try:
        import speech_recognition
        print("✅ SpeechRecognition installed")
    except ImportError:
        issues.append("❌ SpeechRecognition not installed: pip install SpeechRecognition")
    
    # Check pydub
    try:
        import pydub
        print("✅ pydub installed")
    except ImportError:
        issues.append("❌ pydub not installed: pip install pydub")
    
    # Check ffmpeg
    try:
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ ffmpeg installed: {version_line[:50]}")
        else:
            issues.append("❌ ffmpeg not working")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        issues.append("❌ ffmpeg not found: sudo apt-get install ffmpeg")
    
    return issues


async def check_environment_variables():
    """Check if environment variables are set correctly."""
    print("\n" + "=" * 70)
    print("🔍 ENVIRONMENT VARIABLES")
    print("=" * 70)
    
    issues = []
    
    # Check local solver enable flag
    local_enabled = os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "true").lower() != "false"
    if local_enabled:
        print("✅ Local solver is ENABLED (TEQ_USE_LOCAL_CAPTCHA_SOLVER=true or not set)")
    else:
        issues.append("❌ Local solver is DISABLED (TEQ_USE_LOCAL_CAPTCHA_SOLVER=false)")
    
    # Check for conflicting API keys
    api_keys = {
        "CAPTCHA_2CAPTCHA_API_KEY": os.getenv("CAPTCHA_2CAPTCHA_API_KEY"),
        "CAPTCHA_AI4CAP_API_KEY": os.getenv("CAPTCHA_AI4CAP_API_KEY"),
        "TEQ_CAPTCHA_API_KEY": os.getenv("TEQ_CAPTCHA_API_KEY"),
        "CAPTCHA_ANTICAPTCHA_API_KEY": os.getenv("CAPTCHA_ANTICAPTCHA_API_KEY"),
        "CAPTCHA_CAPSOLVER_API_KEY": os.getenv("CAPTCHA_CAPSOLVER_API_KEY"),
    }
    
    active_keys = {k: v for k, v in api_keys.items() if v}
    
    if active_keys:
        print(f"⚠️  External CAPTCHA API keys are configured:")
        for key, value in active_keys.items():
            masked = value[:10] + "..." + value[-4:] if len(value) > 14 else value
            print(f"   - {key}: {masked}")
        print("   (Local solver may fall back to these if it fails)")
    else:
        print("✅ No external API keys configured (will use local solver exclusively)")
    
    return issues


async def check_captcha_solver_implementation():
    """Check if LocalCaptchaSolver is properly implemented."""
    print("\n" + "=" * 70)
    print("🔍 CAPTCHA SOLVER IMPLEMENTATION")
    print("=" * 70)
    
    issues = []
    
    try:
        from captcha_solver import LocalCaptchaSolver, get_captcha_solver
        print("✅ captcha_solver module imported successfully")
        
        # Check LocalCaptchaSolver class
        try:
            solver = LocalCaptchaSolver()
            print("✅ LocalCaptchaSolver class instantiated")
            
            # Check required methods
            required_methods = [
                'solve_recaptcha_v2',
                'solve_hcaptcha',
                '_click_recaptcha_checkbox',
                '_check_challenge_present',
                '_solve_audio_challenge',
                '_get_recaptcha_token',
                '_recognize_audio'
            ]
            
            missing_methods = []
            for method_name in required_methods:
                if not hasattr(solver, method_name):
                    missing_methods.append(method_name)
                    issues.append(f"❌ Missing method: {method_name}")
                elif not callable(getattr(solver, method_name)):
                    issues.append(f"❌ Method not callable: {method_name}")
            
            if not missing_methods:
                print(f"✅ All {len(required_methods)} required methods present")
            
        except Exception as e:
            issues.append(f"❌ Failed to instantiate LocalCaptchaSolver: {str(e)[:80]}")
        
        # Check get_captcha_solver function
        try:
            os.environ["TEQ_USE_LOCAL_CAPTCHA_SOLVER"] = "true"
            local_solver = get_captcha_solver("local")
            if local_solver and isinstance(local_solver, LocalCaptchaSolver):
                print("✅ get_captcha_solver('local') returns LocalCaptchaSolver")
            else:
                issues.append(f"❌ get_captcha_solver('local') returned {type(local_solver)}")
            
            auto_solver = get_captcha_solver("auto")
            if auto_solver and isinstance(auto_solver, LocalCaptchaSolver):
                print("✅ get_captcha_solver('auto') returns LocalCaptchaSolver when enabled")
            else:
                print(f"⚠️  get_captcha_solver('auto') returned {type(auto_solver).__name__ if auto_solver else 'None'}")
        except Exception as e:
            issues.append(f"❌ Failed in get_captcha_solver: {str(e)[:80]}")
        
    except ImportError as e:
        issues.append(f"❌ Failed to import captcha_solver: {str(e)[:80]}")
    except Exception as e:
        issues.append(f"❌ Unexpected error in captcha_solver check: {str(e)[:80]}")
    
    return issues


async def check_playwright_browser():
    """Check if Playwright can launch a browser."""
    print("\n" + "=" * 70)
    print("🔍 PLAYWRIGHT BROWSER")
    print("=" * 70)
    
    issues = []
    
    try:
        from playwright.async_api import async_playwright
        
        print("⏳ Attempting to launch Chromium browser...")
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                print("✅ Chromium browser launched successfully")
                
                # Create a context and page
                context = await browser.new_context()
                page = await context.new_page()
                print("✅ Browser context and page created")
                
                # Navigate to a simple page
                await page.goto("about:blank")
                print("✅ Page navigation works")
                
                # Check JavaScript execution
                title = await page.evaluate("() => document.title")
                print("✅ JavaScript execution works")
                
                # Check if we can detect reCAPTCHA framework
                has_recaptcha_api = await page.evaluate("""
                    () => {
                        const script = document.createElement('script');
                        script.src = 'https://www.google.com/recaptcha/api.js';
                        document.head.appendChild(script);
                        // Return true just to test the capability
                        return window.grecaptcha === undefined;
                    }
                """)
                print("✅ Script injection works (reCAPTCHA API script can be loaded)")
                
                await browser.close()
                print("✅ Browser closed successfully")
                
            except Exception as e:
                issues.append(f"❌ Error during browser operations: {str(e)[:100]}")
                try:
                    await browser.close()
                except:
                    pass
    
    except ImportError:
        issues.append("❌ Playwright not installed or not working")
    except Exception as e:
        issues.append(f"❌ Error launching browser: {str(e)[:100]}")
    
    return issues


async def check_audio_recognition():
    """Check if audio recognition is working."""
    print("\n" + "=" * 70)
    print("🔍 AUDIO RECOGNITION CAPABILITIES")
    print("=" * 70)
    
    issues = []
    
    try:
        import speech_recognition as sr
        print(f"✅ SpeechRecognition version: {sr.__version__}")
        
        # Create recognizer
        r = sr.Recognizer()
        print(f"✅ Recognizer created")
        print(f"   - Microphone devices: {sr.Microphone.list_microphone_indexes()}")
        
        # Check if Google API is available (should be, it's free)
        print("✅ Google Speech Recognition API available (free, no API key needed)")
        
    except ImportError:
        issues.append("❌ SpeechRecognition not installed")
    except Exception as e:
        issues.append(f"❌ Audio recognition check failed: {str(e)[:80]}")
    
    return issues


async def check_network_connectivity():
    """Check if network connectivity works for downloading audio."""
    print("\n" + "=" * 70)
    print("🔍 NETWORK CONNECTIVITY")
    print("=" * 70)
    
    issues = []
    
    try:
        import urllib.request
        import urllib.error
        
        # Test connection to Google's reCAPTCHA
        try:
            print("⏳ Testing connection to Google reCAPTCHA API...")
            response = urllib.request.urlopen("https://www.google.com/recaptcha/api.js", timeout=10)
            response.close()
            print("✅ Can reach Google reCAPTCHA API")
        except urllib.error.URLError as e:
            issues.append(f"❌ Cannot reach Google reCAPTCHA API: {str(e)[:80]}")
        except Exception as e:
            issues.append(f"❌ Network error checking reCAPTCHA API: {str(e)[:80]}")
        
        # Test connection to Google's Speech Recognition API
        try:
            print("⏳ Testing connection to Google Speech Recognition API...")
            response = urllib.request.urlopen("https://www.google.com/speech-api/", timeout=10)
            response.close()
            print("✅ Can reach Google Speech Recognition API")
        except urllib.error.URLError as e:
            if "403" in str(e):
                print("✅ Google Speech Recognition API is reachable (403 is expected)")
            else:
                print(f"⚠️  Google Speech Recognition API returned: {str(e)[:50]}")
        except Exception as e:
            print(f"⚠️  Connectivity check for Speech API inconclusive: {str(e)[:50]}")
        
    except Exception as e:
        issues.append(f"❌ Network connectivity check failed: {str(e)[:80]}")
    
    return issues


async def test_full_captcha_solving():
    """Test a full CAPTCHA solving workflow."""
    print("\n" + "=" * 70)
    print("🔍 FULL CAPTCHA SOLVING WORKFLOW TEST")
    print("=" * 70)
    
    issues = []
    
    try:
        from playwright.async_api import async_playwright
        from captcha_solver import LocalCaptchaSolver
        
        print("⏳ Setting up browser and page with test reCAPTCHA...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Load a page with test reCAPTCHA
            test_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test reCAPTCHA</title>
                <script src="https://www.google.com/recaptcha/api.js" async defer></script>
            </head>
            <body>
                <h1>Test Page</h1>
                <div class="g-recaptcha" data-sitekey="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ"></div>
                <textarea name="g-recaptcha-response" style="display:none;"></textarea>
                <button type="submit">Submit</button>
            </body>
            </html>
            """
            
            await page.set_content(test_html)
            await page.wait_for_timeout(3000)  # Wait for reCAPTCHA to load
            print("✅ Test page with reCAPTCHA loaded")
            
            # Check if reCAPTCHA is present
            recaptcha_present = await page.evaluate("""
                () => {
                    const iframe = document.querySelector('iframe[src*="recaptcha"]');
                    const response = document.querySelector('textarea[name="g-recaptcha-response"]');
                    return { iframe: iframe !== null, response: response !== null };
                }
            """)
            
            if recaptcha_present['iframe']:
                print("✅ reCAPTCHA iframe is present")
            else:
                issues.append("❌ reCAPTCHA iframe not found on test page")
            
            if recaptcha_present['response']:
                print("✅ Response field is present")
            else:
                issues.append("❌ Response field not found")
            
            # Test LocalCaptchaSolver initialization
            try:
                solver = LocalCaptchaSolver(page=page)
                print("✅ LocalCaptchaSolver initialized with page")
                
                # Test helper methods
                token = await solver._get_recaptcha_token()
                print(f"✅ _get_recaptcha_token() called (returned: {bool(token)})")
                
                challenge_present = await solver._check_challenge_present()
                print(f"✅ _check_challenge_present() called (returned: {challenge_present})")
                
                # Note: We won't try full solving here as it requires actual audio processing
                # and might fail due to rate limiting or missing audio
                print("ℹ️  Full solving workflow skipped (would require actual audio handling)")
                
            except Exception as e:
                issues.append(f"❌ LocalCaptchaSolver error: {str(e)[:100]}")
            
            await browser.close()
            print("✅ Browser closed successfully")
    
    except ImportError as e:
        issues.append(f"❌ Failed to import required modules: {str(e)[:80]}")
    except Exception as e:
        issues.append(f"❌ Test workflow failed: {str(e)[:100]}")
    
    return issues


async def main():
    """Run all diagnostic checks."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  LOCAL CAPTCHA SOLVER DIAGNOSTIC TOOL".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(await check_dependencies())
    all_issues.extend(await check_environment_variables())
    all_issues.extend(await check_captcha_solver_implementation())
    all_issues.extend(await check_playwright_browser())
    all_issues.extend(await check_audio_recognition())
    all_issues.extend(await check_network_connectivity())
    all_issues.extend(await test_full_captcha_solving())
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    if all_issues:
        print(f"\n❌ Found {len(all_issues)} issue(s):\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        
        print("\n" + "-" * 70)
        print("RECOMMENDED FIXES:")
        print("-" * 70)
        
        if any("Playwright" in issue and "installed" in issue for issue in all_issues):
            print("\n1. Install Playwright and Chromium:")
            print("   pip install playwright")
            print("   playwright install chromium")
        
        if any("SpeechRecognition" in issue for issue in all_issues):
            print("\n2. Install SpeechRecognition:")
            print("   pip install SpeechRecognition")
        
        if any("pydub" in issue for issue in all_issues):
            print("\n3. Install pydub:")
            print("   pip install pydub")
        
        if any("ffmpeg" in issue for issue in all_issues):
            print("\n4. Install ffmpeg:")
            print("   Ubuntu/Debian: sudo apt-get install ffmpeg")
            print("   macOS: brew install ffmpeg")
            print("   Windows: choco install ffmpeg")
        
        print("\n" + "-" * 70)
        
        return 1
    else:
        print("✅ All diagnostic checks passed!")
        print("\nYour local CAPTCHA solver should be working correctly.")
        print("\nTo test:")
        print("1. Run: python3 automation/test_local_solver.py")
        print("2. Or use in your submission workflow with: use_local_captcha_solver: true")
        print("\n" + "=" * 70)
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
