#!/usr/bin/env python3
"""
Improved Manual Automation for Google reCAPTCHA with Audio Challenge Solving
- Properly clicks inside reCAPTCHA iframe
- Handles audio challenges
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


async def click_recaptcha_checkbox(page):
    """Properly click the reCAPTCHA checkbox inside the iframe."""
    try:
        print("🖱️  Attempting to click reCAPTCHA checkbox...")
        
        # Find the reCAPTCHA anchor iframe
        anchor_iframe = None
        iframe_selectors = [
            'iframe[src*="recaptcha/api2/anchor"]',
            'iframe[src*="recaptcha/enterprise/anchor"]',
            'iframe[title*="reCAPTCHA"]',
            'iframe[src*="google.com/recaptcha"]'
        ]
        
        for selector in iframe_selectors:
            try:
                iframe = await page.query_selector(selector)
                if iframe:
                    src = await iframe.get_attribute('src')
                    if src and ('anchor' in src or 'recaptcha' in src.lower()):
                        anchor_iframe = iframe
                        print(f"   ✅ Found anchor iframe: {selector}")
                        break
            except:
                continue
        
        if not anchor_iframe:
            print("   ⚠️  Could not find reCAPTCHA anchor iframe")
            return False
        
        # Get the iframe's content frame
        try:
            frame = await anchor_iframe.content_frame()
            if not frame:
                print("   ⚠️  Could not access iframe content")
                return False
        except Exception as e:
            print(f"   ⚠️  Error accessing iframe: {e}")
            return False
        
        # Wait for the checkbox to be ready
        print("   ⏳ Waiting for checkbox to be ready...")
        await asyncio.sleep(2)
        
        # Try multiple methods to click the checkbox
        checkbox_selectors = [
            '#recaptcha-anchor',
            'span#recaptcha-anchor',
            'div#recaptcha-anchor',
            '[id="recaptcha-anchor"]',
            '.recaptcha-checkbox',
            'span.recaptcha-checkbox-border'
        ]
        
        clicked = False
        for selector in checkbox_selectors:
            try:
                checkbox = await frame.query_selector(selector)
                if checkbox:
                    print(f"   ✅ Found checkbox with selector: {selector}")
                    
                    # Try clicking using coordinates
                    try:
                        box = await checkbox.bounding_box()
                        if box:
                            # Click in the center of the checkbox
                            await page.mouse.click(
                                box['x'] + box['width'] / 2,
                                box['y'] + box['height'] / 2
                            )
                            print("   ✅ Clicked checkbox using coordinates")
                            clicked = True
                            break
                    except:
                        pass
                    
                    # Fallback: regular click
                    try:
                        await checkbox.click(timeout=5000)
                        print("   ✅ Clicked checkbox")
                        clicked = True
                        break
                    except:
                        pass
                    
                    # Fallback: JavaScript click
                    try:
                        await checkbox.evaluate("el => el.click()")
                        print("   ✅ Clicked checkbox via JavaScript")
                        clicked = True
                        break
                    except:
                        pass
            except:
                continue
        
        if not clicked:
            # Last resort: click using JavaScript in the frame
            try:
                clicked = await frame.evaluate("""
                () => {
                    const checkbox = document.querySelector('#recaptcha-anchor');
                    if (checkbox) {
                        checkbox.click();
                        return true;
                    }
                    return false;
                }
                """)
                if clicked:
                    print("   ✅ Clicked checkbox via frame JavaScript")
            except:
                pass
        
        if clicked:
            print("   ✅ Checkbox click successful!")
            await asyncio.sleep(3)  # Wait for challenge to appear
            return True
        else:
            print("   ❌ Could not click checkbox")
            return False
            
    except Exception as e:
        print(f"   ❌ Error clicking checkbox: {e}")
        import traceback
        traceback.print_exc()
        return False


async def solve_recaptcha_with_audio_improved(url: str, headless: bool = False):
    """
    Improved reCAPTCHA solving with proper iframe handling.
    """
    
    print("=" * 80)
    print("🤖 IMPROVED GOOGLE RECAPTCHA AUDIO CHALLENGE SOLVER")
    print("=" * 80)
    print(f"\n📍 URL: {url}")
    print(f"🖥️  Headless Mode: {headless} (False = Visible Browser)")
    print(f"🎧 Audio Challenge: Enabled")
    print(f"✅ Verification: Enabled")
    print("\n" + "=" * 80 + "\n")
    
    async with async_playwright() as p:
        # Launch browser in visible mode
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
                const recaptchaElements = document.querySelectorAll(
                    '.g-recaptcha, .recaptcha, iframe[src*="recaptcha"], iframe[src*="google.com/recaptcha"]'
                );
                return recaptchaElements.length > 0;
            }
            """)
            
            if not recaptcha_found:
                print("⚠️  No Google reCAPTCHA found initially, waiting for dynamic content...")
                await page.wait_for_timeout(10000)
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
                screenshot_path = Path(__file__).parent / "recaptcha_not_found.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"📸 Screenshot saved: {screenshot_path}")
                return False
            
            print("✅ Google reCAPTCHA detected!")
            
            # Get site key
            site_key = await page.evaluate("""
            () => {
                const recaptchaDiv = document.querySelector('.g-recaptcha, [data-sitekey]');
                if (recaptchaDiv) {
                    return recaptchaDiv.getAttribute('data-sitekey') || null;
                }
                return null;
            }
            """)
            
            page_url = page.url
            print(f"   Site Key: {site_key or 'Not found'}")
            print(f"   Page URL: {page_url}")
            
            # Step 1: Click the checkbox manually (improved method)
            print("\n" + "-" * 80)
            print("STEP 1: Clicking reCAPTCHA checkbox")
            print("-" * 80)
            checkbox_clicked = await click_recaptcha_checkbox(page)
            
            if not checkbox_clicked:
                print("⚠️  Could not click checkbox, trying solver's method...")
            
            # Step 2: Check if challenge appeared or if we got a token
            print("\n" + "-" * 80)
            print("STEP 2: Checking for challenge or token")
            print("-" * 80)
            
            # Check for token first
            token = await page.evaluate("""
            () => {
                const textarea = document.querySelector('textarea[name="g-recaptcha-response"]');
                return textarea ? textarea.value : null;
            }
            """)
            
            if token and len(token) > 50:
                print(f"✅ reCAPTCHA solved without challenge! Token length: {len(token)}")
                screenshot_path = Path(__file__).parent / "recaptcha_solved_no_challenge.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"📸 Screenshot saved: {screenshot_path}")
                
                print("\n⏸️  Keeping browser open for 30 seconds...")
                await page.wait_for_timeout(30000)
                return True
            
            # Check for challenge iframe
            print("   🔍 Checking for challenge iframe...")
            challenge_iframe = None
            for attempt in range(5):
                await asyncio.sleep(2)
                challenge_iframe = await page.query_selector('iframe[src*="recaptcha/api2/bframe"], iframe[src*="recaptcha/enterprise/bframe"]')
                if challenge_iframe:
                    print(f"   ✅ Challenge iframe detected! (attempt {attempt + 1})")
                    break
                print(f"   ⏳ No challenge yet (attempt {attempt + 1}/5)...")
            
            if not challenge_iframe:
                print("   ⚠️  No challenge iframe detected - reCAPTCHA may have passed without challenge")
                print("   ⏳ Waiting a bit more and checking for token...")
                await asyncio.sleep(5)
                
                token = await page.evaluate("""
                () => {
                    const textarea = document.querySelector('textarea[name="g-recaptcha-response"]');
                    return textarea ? textarea.value : null;
                }
                """)
                
                if token and len(token) > 50:
                    print(f"✅ reCAPTCHA solved! Token length: {len(token)}")
                    screenshot_path = Path(__file__).parent / "recaptcha_solved.png"
                    await page.screenshot(path=str(screenshot_path))
                    print(f"📸 Screenshot saved: {screenshot_path}")
                    await page.wait_for_timeout(30000)
                    return True
                else:
                    print("   ❌ No token found")
                    screenshot_path = Path(__file__).parent / "recaptcha_no_token.png"
                    await page.screenshot(path=str(screenshot_path))
                    print(f"📸 Screenshot saved: {screenshot_path}")
                    await page.wait_for_timeout(30000)
                    return False
            
            # Wait for challenge iframe to be fully loaded and stable
            print("   ⏳ Waiting for challenge iframe to be fully loaded...")
            await asyncio.sleep(5)
            
            # Verify challenge iframe is still there and accessible
            challenge_iframe = await page.query_selector('iframe[src*="recaptcha/api2/bframe"], iframe[src*="recaptcha/enterprise/bframe"], iframe[title*="challenge"]')
            if not challenge_iframe:
                print("   ⚠️  Challenge iframe disappeared, checking for token...")
                await asyncio.sleep(3)
                token = await page.evaluate("""
                () => {
                    const textarea = document.querySelector('textarea[name="g-recaptcha-response"]');
                    return textarea ? textarea.value : null;
                }
                """)
                if token and len(token) > 50:
                    print(f"✅ reCAPTCHA solved! Token length: {len(token)}")
                    return True
            
            # Step 3: Solve audio challenge
            print("\n" + "-" * 80)
            print("STEP 3: Solving audio challenge")
            print("-" * 80)
            
            print("🤖 Using UltimateLocalCaptchaSolver for audio challenge...")
            solver = UltimateLocalCaptchaSolver(page=page)
            
            # Use the full solving process - it should detect the challenge iframe
            print("   🎧 Challenge iframe detected, solving audio challenge...")
            result = await solver.solve_recaptcha_v2(
                site_key=site_key or "",
                page_url=page_url
            )
            
            # Step 4: Verify result
            print("\n" + "-" * 80)
            print("STEP 4: Verifying result")
            print("-" * 80)
            
            if result.get("success"):
                token = result.get("token")
                print(f"✅ SUCCESS! reCAPTCHA solved!")
                print(f"   Token: {token[:50]}..." if token and len(token) > 50 else f"   Token: {token}")
                print(f"   Token Length: {len(token) if token else 0} characters")
                
                # Verify token in page
                token_in_page = await page.evaluate("""
                () => {
                    const textarea = document.querySelector('textarea[name="g-recaptcha-response"]');
                    return textarea ? textarea.value : null;
                }
                """)
                
                if token_in_page:
                    print(f"   ✅ Token verified in page!")
                    print(f"   Token matches: {token_in_page == token if token else 'N/A'}")
                
                screenshot_path = Path(__file__).parent / "recaptcha_solved.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"📸 Success screenshot saved: {screenshot_path}")
                
                print("\n⏸️  Keeping browser open for 60 seconds for inspection...")
                await page.wait_for_timeout(60000)
                return True
            else:
                error = result.get("error", "Unknown error")
                print(f"❌ FAILED to solve reCAPTCHA")
                print(f"   Error: {error}")
                
                screenshot_path = Path(__file__).parent / "recaptcha_failed.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"📸 Failure screenshot saved: {screenshot_path}")
                
                print("\n⏸️  Keeping browser open for 30 seconds...")
                await page.wait_for_timeout(30000)
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
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
    """Main function."""
    url = "https://interiordesign.xcelanceweb.com/contact"
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    success = await solve_recaptcha_with_audio_improved(url, headless=False)
    
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

