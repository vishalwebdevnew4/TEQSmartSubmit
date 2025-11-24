#!/usr/bin/env python3
"""
Simple Manual Automation for Google reCAPTCHA with Audio Challenge
- Clicks checkbox manually
- Handles audio challenge step by step
- Verifies result
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "automation"))

from playwright.async_api import async_playwright
from captcha_solver import UltimateLocalCaptchaSolver
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def main():
    url = "https://interiordesign.xcelanceweb.com/contact"
    
    print("=" * 80)
    print("🤖 SIMPLE RECAPTCHA AUDIO CHALLENGE SOLVER")
    print("=" * 80)
    print(f"\n📍 URL: {url}")
    print(f"🖥️  Headless: False (Visible Browser)")
    print("\n" + "=" * 80 + "\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            print("⏳ Navigating...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)
            print("✅ Page loaded\n")
            
            # Handle cookie banner first
            print("STEP 0: Handling cookie banner...")
            cookie_accepted = False
            
            # Common cookie banner selectors
            cookie_selectors = [
                'button:has-text("Accept")',
                'button:has-text("Accept All")',
                'button:has-text("Alles accepteren")',
                'button:has-text("Accepteren")',
                'button:has-text("I Accept")',
                'button:has-text("Agree")',
                'button[id*="accept"]',
                'button[class*="accept"]',
                'button[data-consent*="accept"]',
                '#cookie-accept',
                '.cookie-accept',
                '[id*="cookie"] button',
                '[class*="cookie"] button',
                '[id*="consent"] button',
                '[class*="consent"] button'
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_button = await page.query_selector(selector)
                    if cookie_button:
                        is_visible = await cookie_button.is_visible()
                        if is_visible:
                            await cookie_button.click(timeout=5000)
                            print(f"   ✅ Clicked cookie banner: {selector}")
                            cookie_accepted = True
                            await asyncio.sleep(2)
                            break
                except:
                    continue
            
            # Also try JavaScript click for cookie banners
            if not cookie_accepted:
                cookie_clicked = await page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    for (const btn of buttons) {
                        const text = btn.textContent.toLowerCase();
                        if (text.includes('accept') || text.includes('accepteren') || 
                            text.includes('agree') || text.includes('ok') ||
                            btn.id.toLowerCase().includes('accept') ||
                            btn.className.toLowerCase().includes('accept')) {
                            if (btn.offsetParent !== null) { // Visible
                                btn.click();
                                return true;
                            }
                        }
                    }
                    return false;
                }
                """)
                if cookie_clicked:
                    print("   ✅ Clicked cookie banner via JavaScript")
                    cookie_accepted = True
                    await asyncio.sleep(2)
            
            if cookie_accepted:
                print("   ✅ Cookie banner handled\n")
            else:
                print("   ⚠️  No cookie banner found (or already accepted)\n")
            
            # Click checkbox
            print("STEP 1: Clicking reCAPTCHA checkbox...")
            anchor_iframe = await page.query_selector('iframe[src*="recaptcha/api2/anchor"]')
            if not anchor_iframe:
                print("❌ Could not find reCAPTCHA")
                return False
            
            # Scroll to iframe
            await anchor_iframe.scroll_into_view_if_needed()
            await asyncio.sleep(1)
            
            frame = await anchor_iframe.content_frame()
            if not frame:
                print("❌ Could not access iframe")
                return False
            
            await asyncio.sleep(2)
            
            # Try multiple methods to click the checkbox
            checkbox_clicked = False
            
            # Method 1: Direct click on checkbox element
            checkbox = await frame.query_selector('#recaptcha-anchor')
            if checkbox:
                try:
                    await checkbox.click(timeout=5000)
                    print("   ✅ Clicked checkbox (method 1: direct click)")
                    checkbox_clicked = True
                except:
                    pass
            
            # Method 2: Click using coordinates
            if not checkbox_clicked and checkbox:
                try:
                    box = await checkbox.bounding_box()
                    if box:
                        # Get iframe position
                        iframe_box = await anchor_iframe.bounding_box()
                        if iframe_box:
                            # Calculate absolute coordinates
                            abs_x = iframe_box['x'] + box['x'] + box['width']/2
                            abs_y = iframe_box['y'] + box['y'] + box['height']/2
                            await page.mouse.click(abs_x, abs_y)
                            print("   ✅ Clicked checkbox (method 2: coordinates)")
                            checkbox_clicked = True
                except Exception as e:
                    print(f"   ⚠️  Coordinate click failed: {e}")
            
            # Method 3: JavaScript click
            if not checkbox_clicked:
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
                        print("   ✅ Clicked checkbox (method 3: JavaScript)")
                        checkbox_clicked = True
                except:
                    pass
            
            # Method 4: Click on the iframe itself
            if not checkbox_clicked:
                try:
                    iframe_box = await anchor_iframe.bounding_box()
                    if iframe_box:
                        await page.mouse.click(
                            iframe_box['x'] + iframe_box['width']/2,
                            iframe_box['y'] + iframe_box['height']/2
                        )
                        print("   ✅ Clicked checkbox (method 4: iframe center)")
                        checkbox_clicked = True
                except:
                    pass
            
            if checkbox_clicked:
                print("✅ Checkbox click attempted")
                
                # Verify checkbox state changed
                for check in range(5):
                    await asyncio.sleep(2)
                    checkbox_state = await frame.evaluate("""
                        () => {
                            const checkbox = document.querySelector('#recaptcha-anchor');
                            if (checkbox) {
                                return checkbox.getAttribute('aria-checked');
                            }
                            return null;
                        }
                    """)
                    if checkbox_state == 'true':
                        print(f"   ✅ Checkbox is now checked! (after {check + 1} checks)")
                        break
                    elif check < 4:
                        print(f"   ⏳ Checkbox still unchecked, waiting... (check {check + 1}/5)")
                
                print("   ⏳ Waiting for challenge or token...\n")
                await asyncio.sleep(5)  # Additional wait
            else:
                print("❌ Could not click checkbox with any method")
                print("   Trying solver's built-in method...")
                
                # Use solver's method as fallback
                solver = UltimateLocalCaptchaSolver(page=page)
                token = await solver._attempt_simple_checkbox()
                if token:
                    print("✅ Solver's method worked!")
                    await page.screenshot(path="recaptcha_solved.png")
                    await page.wait_for_timeout(30000)
                    return True
                
                await page.screenshot(path="recaptcha_click_failed.png")
                await page.wait_for_timeout(30000)
                return False
            
            # Check for challenge
            print("STEP 2: Checking for challenge or token...")
            
            # First check if we got a token (reCAPTCHA passed without challenge)
            token = await page.evaluate("""
                () => {
                    const ta = document.querySelector('textarea[name="g-recaptcha-response"]');
                    return ta ? ta.value : null;
                }
            """)
            
            if token and len(token) > 50:
                print(f"✅ reCAPTCHA solved without challenge!")
                print(f"   Token length: {len(token)} characters")
                await page.screenshot(path="recaptcha_solved_no_challenge.png")
                print("   📸 Screenshot saved: recaptcha_solved_no_challenge.png")
                await page.wait_for_timeout(30000)
                return True
            
            # Check for challenge iframe
            challenge_iframe = None
            print("   🔍 Looking for challenge iframe...")
            
            for i in range(20):  # Check for 20 seconds
                # Try multiple selectors
                selectors = [
                    'iframe[src*="recaptcha/api2/bframe"]',
                    'iframe[src*="recaptcha/enterprise/bframe"]',
                    'iframe[title*="challenge"]',
                    'iframe[src*="bframe"]',
                    'iframe[name*="c-"]'
                ]
                
                for selector in selectors:
                    try:
                        iframe = await page.query_selector(selector)
                        if iframe:
                            is_visible = await iframe.is_visible()
                            if is_visible:
                                challenge_iframe = iframe
                                print(f"   ✅ Challenge detected! (attempt {i+1}, selector: {selector})\n")
                                break
                    except:
                        continue
                
                if challenge_iframe:
                    break
                
                # Also check for token periodically
                if i % 3 == 0 and i > 0:
                    token = await page.evaluate("""
                        () => {
                            const ta = document.querySelector('textarea[name="g-recaptcha-response"]');
                            return ta ? ta.value : null;
                        }
                    """)
                    if token and len(token) > 50:
                        print(f"✅ reCAPTCHA solved! Token received during wait.")
                        await page.screenshot(path="recaptcha_solved.png")
                        await page.wait_for_timeout(30000)
                        return True
                    
                await asyncio.sleep(1)
            
            if not challenge_iframe:
                # Final token check
                await asyncio.sleep(2)
                token = await page.evaluate("""
                    () => {
                        const ta = document.querySelector('textarea[name="g-recaptcha-response"]');
                        return ta ? ta.value : null;
                    }
                """)
                if token and len(token) > 50:
                    print("✅ reCAPTCHA solved! (token found on final check)")
                    await page.screenshot(path="recaptcha_solved.png")
                    await page.wait_for_timeout(30000)
                    return True
                else:
                    print("❌ No challenge iframe detected and no token found")
                    print("   Taking screenshot for debugging...")
                    await page.screenshot(path="recaptcha_no_challenge.png")
                    print("   📸 Screenshot saved: recaptcha_no_challenge.png")
                    
                    # Debug: Check checkbox state
                    checkbox_state = await frame.evaluate("""
                        () => {
                            const checkbox = document.querySelector('#recaptcha-anchor');
                            if (checkbox) {
                                return {
                                    checked: checkbox.getAttribute('aria-checked'),
                                    className: checkbox.className
                                };
                            }
                            return null;
                        }
                    """)
                    print(f"   Checkbox state: {checkbox_state}")
                    
                    await page.wait_for_timeout(30000)
                    return False
            
            # Wait for challenge to fully load
            print("   ⏳ Waiting for challenge to fully load...")
            await asyncio.sleep(5)
            
            # Verify challenge iframe is still accessible
            is_visible = await challenge_iframe.is_visible()
            if not is_visible:
                print("   ⚠️  Challenge iframe became invisible, re-detecting...")
                challenge_iframe = await page.query_selector('iframe[src*="bframe"], iframe[title*="challenge"]')
                if not challenge_iframe:
                    print("   ❌ Challenge iframe lost")
                    await page.wait_for_timeout(30000)
                    return False
            
            # Solve audio challenge
            print("STEP 3: Solving audio challenge...")
            print("   Using UltimateLocalCaptchaSolver...\n")
            
            solver = UltimateLocalCaptchaSolver(page=page)
            
            # Try multiple times with increasing waits
            token = None
            for attempt in range(3):
                if attempt > 0:
                    print(f"   Retry attempt {attempt + 1}...")
                    await asyncio.sleep(5)
                
                # Call the audio challenge handler
                token = await solver._handle_audio_challenge()
                if token:
                    break
            
            if token:
                print(f"\n✅ SUCCESS! Token: {token[:50]}...")
                print(f"   Token length: {len(token)} characters")
                
                # Verify
                token_in_page = await page.evaluate("""
                    () => {
                        const ta = document.querySelector('textarea[name="g-recaptcha-response"]');
                        return ta ? ta.value : null;
                    }
                """)
                
                if token_in_page:
                    print("   ✅ Token verified in page!")
                
                await page.screenshot(path="recaptcha_solved.png")
                print("   📸 Screenshot saved: recaptcha_solved.png")
                
                print("\n⏸️  Browser open for 60 seconds...")
                await page.wait_for_timeout(60000)
                return True
            else:
                print("\n❌ Audio challenge solving failed")
                await page.screenshot(path="recaptcha_failed.png")
                print("   📸 Screenshot saved: recaptcha_failed.png")
                print("\n⏸️  Browser open for 30 seconds...")
                await page.wait_for_timeout(30000)
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="recaptcha_error.png")
            return False
        finally:
            await browser.close()


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
        sys.exit(1)

