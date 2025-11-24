#!/usr/bin/env python3
"""
Manual Automation for Google reCAPTCHA with Audio Challenge Solving
- Headless mode: OFF (visible browser)
- Automatically solves audio challenges
- Verifies CAPTCHA is solved
"""

import asyncio
import sys
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent / "automation"))

from playwright.async_api import async_playwright
from captcha_solver import UltimateLocalCaptchaSolver
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def solve_recaptcha_with_audio(url: str, headless: bool = False):
    """
    Solve Google reCAPTCHA with audio challenge on a given URL.
    
    Args:
        url: The URL to test
        headless: Whether to run in headless mode (False = visible browser)
    """
    
    print("=" * 80)
    print("🤖 GOOGLE RECAPTCHA AUDIO CHALLENGE SOLVER")
    print("=" * 80)
    print(f"\n📍 URL: {url}")
    print(f"🖥️  Headless Mode: {headless} (False = Visible Browser)")
    print(f"🎧 Audio Challenge: Enabled")
    print(f"✅ Verification: Enabled")
    print("\n" + "=" * 80 + "\n")
    
    async with async_playwright() as p:
        # Launch browser in visible mode for manual inspection
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            # Navigate to the page
            print("⏳ Navigating to page...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            print("✅ Page loaded successfully")
            
            # Wait for page to fully load
            await page.wait_for_timeout(3000)
            
            # Check for reCAPTCHA
            print("\n🔍 Checking for Google reCAPTCHA...")
            recaptcha_found = await page.evaluate("""
            () => {
                // Check for reCAPTCHA elements
                const recaptchaElements = document.querySelectorAll(
                    '.g-recaptcha, .recaptcha, iframe[src*="recaptcha"], iframe[src*="google.com/recaptcha"]'
                );
                return recaptchaElements.length > 0;
            }
            """)
            
            if not recaptcha_found:
                print("⚠️  No Google reCAPTCHA found on this page")
                print("   The page may not have reCAPTCHA, or it loads dynamically.")
                print("   Waiting 10 seconds for dynamic content...")
                await page.wait_for_timeout(10000)
                
                # Check again
                recaptcha_found = await page.evaluate("""
                () => {
                    const recaptchaElements = document.querySelectorAll(
                        '.g-recaptcha, .recaptcha, iframe[src*="recaptcha"], iframe[src*="google.com/recaptcha"]'
                    );
                    return recaptchaElements.length > 0;
                }
                """)
            
            if not recaptcha_found:
                print("❌ No Google reCAPTCHA detected on this page")
                print("   Taking screenshot for inspection...")
                screenshot_path = Path(__file__).parent / "recaptcha_not_found.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"   Screenshot saved: {screenshot_path}")
                return False
            
            print("✅ Google reCAPTCHA detected!")
            
            # Get reCAPTCHA site key and page URL
            site_key = await page.evaluate("""
            () => {
                // Try to find site key from data-sitekey attribute
                const recaptchaDiv = document.querySelector('.g-recaptcha, [data-sitekey]');
                if (recaptchaDiv) {
                    return recaptchaDiv.getAttribute('data-sitekey') || null;
                }
                
                // Try to extract from iframe src
                const iframes = document.querySelectorAll('iframe[src*="recaptcha"]');
                for (let iframe of iframes) {
                    const src = iframe.src;
                    const match = src.match(/[&?]k=([^&]+)/);
                    if (match) return match[1];
                }
                
                return null;
            }
            """)
            
            page_url = page.url
            print(f"   Site Key: {site_key or 'Not found (will use default)'}")
            print(f"   Page URL: {page_url}")
            
            # Initialize CAPTCHA solver
            print("\n🤖 Initializing reCAPTCHA solver with audio challenge support...")
            solver = UltimateLocalCaptchaSolver(page=page)
            
            # Solve reCAPTCHA with audio challenge
            print("\n🎯 Starting reCAPTCHA solving process...")
            print("   Steps:")
            print("   1. Click reCAPTCHA checkbox")
            print("   2. Detect audio challenge (if presented)")
            print("   3. Download and solve audio challenge")
            print("   4. Submit answer and verify")
            print("\n" + "-" * 80 + "\n")
            
            result = await solver.solve_recaptcha_v2(
                site_key=site_key or "",
                page_url=page_url
            )
            
            print("\n" + "-" * 80)
            print("📊 SOLVING RESULTS")
            print("-" * 80)
            
            if result.get("success"):
                token = result.get("token")
                print(f"✅ SUCCESS! reCAPTCHA solved!")
                print(f"   Token: {token[:50]}..." if token and len(token) > 50 else f"   Token: {token}")
                print(f"   Token Length: {len(token) if token else 0} characters")
                print(f"   Solver Used: {result.get('solver_used', 'Unknown')}")
                
                # Verify token is in the page
                print("\n🔍 Verifying token in page...")
                token_in_page = await page.evaluate("""
                () => {
                    // Check for token in textarea
                    const textarea = document.querySelector('textarea[name="g-recaptcha-response"]');
                    if (textarea && textarea.value) {
                        return textarea.value;
                    }
                    
                    // Check in all textareas
                    const textareas = document.querySelectorAll('textarea');
                    for (let ta of textareas) {
                        if (ta.value && ta.value.length > 50) {
                            return ta.value;
                        }
                    }
                    
                    // Check in hidden inputs
                    const inputs = document.querySelectorAll('input[type="hidden"]');
                    for (let input of inputs) {
                        if (input.value && input.value.length > 50) {
                            return input.value;
                        }
                    }
                    
                    return null;
                }
                """)
                
                if token_in_page:
                    print(f"   ✅ Token found in page!")
                    print(f"   Token matches: {token_in_page == token if token else 'N/A'}")
                else:
                    print("   ⚠️  Token not found in page (may be in iframe)")
                
                # Check if reCAPTCHA checkbox is checked
                checkbox_checked = await page.evaluate("""
                () => {
                    const iframes = document.querySelectorAll('iframe[src*="recaptcha"]');
                    for (let iframe of iframes) {
                        try {
                            const frame = iframe.contentDocument || iframe.contentWindow.document;
                            const checkbox = frame.querySelector('#recaptcha-anchor');
                            if (checkbox) {
                                return checkbox.getAttribute('aria-checked') === 'true';
                            }
                        } catch(e) {}
                    }
                    return false;
                }
                """)
                
                if checkbox_checked:
                    print("   ✅ reCAPTCHA checkbox is checked")
                else:
                    print("   ⚠️  reCAPTCHA checkbox status unknown (may be in iframe)")
                
                # Take success screenshot
                screenshot_path = Path(__file__).parent / "recaptcha_solved.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"\n📸 Success screenshot saved: {screenshot_path}")
                
                print("\n" + "=" * 80)
                print("✅ VERIFICATION COMPLETE - CAPTCHA IS SOLVED!")
                print("=" * 80)
                
                # Keep browser open for inspection
                print("\n⏸️  Keeping browser open for 60 seconds for manual inspection...")
                print("   You can verify the CAPTCHA is solved in the visible browser window.")
                await page.wait_for_timeout(60000)
                
                return True
            else:
                error = result.get("error", "Unknown error")
                print(f"❌ FAILED to solve reCAPTCHA")
                print(f"   Error: {error}")
                print(f"   Error Type: {result.get('error_type', 'Unknown')}")
                print(f"   Solver Used: {result.get('solver_used', 'Unknown')}")
                
                # Take failure screenshot
                screenshot_path = Path(__file__).parent / "recaptcha_failed.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"\n📸 Failure screenshot saved: {screenshot_path}")
                
                print("\n" + "=" * 80)
                print("⚠️  CAPTCHA SOLVING FAILED")
                print("=" * 80)
                print("\nPossible reasons:")
                print("  - Audio challenge dependencies not installed")
                print("  - Audio recognition failed")
                print("  - Network issues")
                print("  - reCAPTCHA detected automation")
                print("\nTo install audio dependencies:")
                print("  pip install SpeechRecognition pydub")
                print("  sudo apt-get install ffmpeg  # Linux")
                
                # Keep browser open for inspection
                print("\n⏸️  Keeping browser open for 30 seconds for manual inspection...")
                await page.wait_for_timeout(30000)
                
                return False
                
        except Exception as e:
            print(f"\n❌ Error during reCAPTCHA solving: {e}")
            import traceback
            traceback.print_exc()
            
            # Take error screenshot
            try:
                screenshot_path = Path(__file__).parent / "recaptcha_error.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"📸 Error screenshot saved: {screenshot_path}")
            except:
                pass
            
            return False
        finally:
            await browser.close()


async def main():
    """Main function to run the reCAPTCHA audio solver."""
    
    # Default URL
    url = "https://interiordesign.xcelanceweb.com/contact"
    
    # Check for command line argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    # Run in non-headless mode (visible browser)
    success = await solve_recaptcha_with_audio(url, headless=False)
    
    if success:
        print("\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

