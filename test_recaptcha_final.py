#!/usr/bin/env python3
"""
Final reCAPTCHA Audio Challenge Solver
- Handles cookie banner
- Uses UltimateLocalCaptchaSolver for full automation
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
    print("🤖 FINAL RECAPTCHA AUDIO CHALLENGE SOLVER")
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
            
            # Handle cookie banner
            print("STEP 0: Handling cookie banner...")
            cookie_clicked = await page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    for (const btn of buttons) {
                        const text = btn.textContent.toLowerCase();
                        if ((text.includes('accept') || text.includes('accepteren') || 
                             text.includes('agree') || text.includes('ok')) &&
                            btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
            if cookie_clicked:
                print("   ✅ Cookie banner handled\n")
                await asyncio.sleep(2)
            
            # STEP 1: Fill form fields first
            print("STEP 1: Filling form fields...")
            
            # Common form field selectors
            form_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '555-123-4567',
                'message': 'This is a test message from automated CAPTCHA solver.',
                'subject': 'Test Submission',
                'company': 'Test Company'
            }
            
            # Try to find and fill name field
            name_filled = False
            name_selectors = [
                'input[name="name"]',
                'input[id*="name"]',
                'input[placeholder*="name" i]',
                'input[type="text"]:first-of-type'
            ]
            for selector in name_selectors:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await field.fill(form_data['name'])
                        print(f"   ✅ Filled name field: {selector}")
                        name_filled = True
                        break
                except:
                    continue
            
            # Try to find and fill email field
            email_filled = False
            email_selectors = [
                'input[name="email"]',
                'input[type="email"]',
                'input[id*="email"]',
                'input[placeholder*="email" i]'
            ]
            for selector in email_selectors:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await field.fill(form_data['email'])
                        print(f"   ✅ Filled email field: {selector}")
                        email_filled = True
                        break
                except:
                    continue
            
            # Try to find and fill phone field (optional)
            phone_selectors = [
                'input[name="phone"]',
                'input[type="tel"]',
                'input[id*="phone"]',
                'input[placeholder*="phone" i]'
            ]
            for selector in phone_selectors:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await field.fill(form_data['phone'])
                        print(f"   ✅ Filled phone field: {selector}")
                        break
                except:
                    continue
            
            # Try to find and fill message/comment field
            message_filled = False
            message_selectors = [
                'textarea[name="message"]',
                'textarea[name="comment"]',
                'textarea[id*="message"]',
                'textarea[id*="comment"]',
                'textarea[placeholder*="message" i]',
                'textarea[placeholder*="comment" i]',
                'textarea'
            ]
            for selector in message_selectors:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await field.fill(form_data['message'])
                        print(f"   ✅ Filled message field: {selector}")
                        message_filled = True
                        break
                except:
                    continue
            
            # Try to find and fill subject field (optional)
            subject_selectors = [
                'input[name="subject"]',
                'input[id*="subject"]',
                'input[placeholder*="subject" i]'
            ]
            for selector in subject_selectors:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await field.fill(form_data['subject'])
                        print(f"   ✅ Filled subject field: {selector}")
                        break
                except:
                    continue
            
            if name_filled or email_filled or message_filled:
                print("   ✅ Form fields filled\n")
            else:
                print("   ⚠️  Could not find form fields (may need different selectors)\n")
            
            await asyncio.sleep(1)  # Small delay after filling fields
            
            # Get site key
            site_key = await page.evaluate("""
                () => {
                    const recaptchaDiv = document.querySelector('.g-recaptcha, [data-sitekey]');
                    return recaptchaDiv ? recaptchaDiv.getAttribute('data-sitekey') : null;
                }
            """)
            
            # STEP 2: Solve reCAPTCHA with audio challenge
            print(f"STEP 2: Solving reCAPTCHA with audio challenge...")
            print(f"   Site Key: {site_key or 'Not found'}")
            print(f"   Using UltimateLocalCaptchaSolver...\n")
            
            solver = UltimateLocalCaptchaSolver(page=page)
            
            # Solve reCAPTCHA
            result = await solver.solve_recaptcha_v2(
                site_key=site_key or "",
                page_url=url
            )
            
            print("\n" + "=" * 80)
            print("RESULTS")
            print("=" * 80)
            
            if result.get("success"):
                token = result.get("token")
                print(f"✅ SUCCESS! reCAPTCHA solved!")
                print(f"   Token: {token[:50]}..." if token and len(token) > 50 else f"   Token: {token}")
                print(f"   Token Length: {len(token) if token else 0} characters")
                print(f"   Solver: {result.get('solver_used', 'Unknown')}")
                
                # Verify token in page
                token_in_page = await page.evaluate("""
                    () => {
                        const ta = document.querySelector('textarea[name="g-recaptcha-response"]');
                        return ta ? ta.value : null;
                    }
                """)
                
                if token_in_page:
                    print(f"   ✅ Token verified in page!")
                    print(f"   Token matches: {token_in_page == token if token else 'N/A'}")
                
                await page.screenshot(path="recaptcha_solved.png")
                print(f"\n📸 Screenshot saved: recaptcha_solved.png")
                
                # STEP 3: Submit the form
                print("\nSTEP 3: Submitting form...")
                submit_clicked = False
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Send")',
                    'button:has-text("Verzenden")',
                    'button[id*="submit"]',
                    'button[class*="submit"]',
                    'form button[type="button"]:last-of-type'
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_btn = await page.query_selector(selector)
                        if submit_btn:
                            is_visible = await submit_btn.is_visible()
                            if is_visible:
                                await submit_btn.click()
                                print(f"   ✅ Form submitted: {selector}")
                                submit_clicked = True
                                break
                    except:
                        continue
                
                if not submit_clicked:
                    # Try JavaScript submit
                    try:
                        submitted = await page.evaluate("""
                            () => {
                                const forms = document.querySelectorAll('form');
                                for (const form of forms) {
                                    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                                    if (submitBtn) {
                                        submitBtn.click();
                                        return true;
                                    }
                                }
                                return false;
                            }
                        """)
                        if submitted:
                            print("   ✅ Form submitted via JavaScript")
                            submit_clicked = True
                    except:
                        pass
                
                if submit_clicked:
                    print("   ⏳ Waiting for form submission response...")
                    await asyncio.sleep(5)
                    
                    # Check for success message
                    success_indicators = await page.evaluate("""
                        () => {
                            const bodyText = document.body.textContent.toLowerCase();
                            return {
                                hasThankYou: bodyText.includes('thank') || bodyText.includes('bedankt'),
                                hasSuccess: bodyText.includes('success') || bodyText.includes('verzonden'),
                                hasError: bodyText.includes('error') || bodyText.includes('fout')
                            };
                        }
                    """)
                    
                    if success_indicators.get('hasThankYou') or success_indicators.get('hasSuccess'):
                        print("   ✅ Form submission appears successful!")
                    elif success_indicators.get('hasError'):
                        print("   ⚠️  Form submission may have failed (error detected)")
                    else:
                        print("   ℹ️  Form submission status unclear")
                else:
                    print("   ⚠️  Could not find submit button")
                
                print("\n⏸️  Browser open for 60 seconds for inspection...")
                await page.wait_for_timeout(60000)
                return True
            else:
                error = result.get("error", "Unknown error")
                print(f"❌ FAILED to solve reCAPTCHA")
                print(f"   Error: {error}")
                print(f"   Error Type: {result.get('error_type', 'Unknown')}")
                
                await page.screenshot(path="recaptcha_failed.png")
                print(f"\n📸 Screenshot saved: recaptcha_failed.png")
                
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
        if success:
            print("\n✅ TEST SUCCESSFUL!")
        else:
            print("\n❌ TEST FAILED!")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
        sys.exit(1)

