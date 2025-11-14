#!/usr/bin/env python3
"""
Real-world test: Actually fill the form and try to submit it.
This should trigger the CAPTCHA on the target website.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "automation"))

async def test_form_submission_with_captcha():
    """Test real form submission that triggers CAPTCHA."""
    from playwright.async_api import async_playwright
    from captcha_solver import LocalCaptchaSolver, get_captcha_solver
    
    url = "https://interiordesign.xcelanceweb.com/"
    
    print("=" * 80)
    print("FORM SUBMISSION TEST - WILL TRIGGER CAPTCHA")
    print("=" * 80)
    print(f"\n🌐 Website: {url}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        try:
            # Step 1: Load page
            print("⏳ Step 1: Loading website...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(2000)
            print("✅ Page loaded\n")
            
            # Step 2: Find form fields
            print("⏳ Step 2: Finding form fields...")
            form_info = await page.evaluate("""
                () => {
                    const form = document.querySelector('form');
                    if (!form) return { fields: [], submitButton: null };
                    
                    const inputs = form.querySelectorAll('input, textarea, select');
                    const buttons = form.querySelectorAll('button, input[type="submit"]');
                    
                    return {
                        fields: Array.from(inputs).map(i => ({
                            type: i.type || i.tagName,
                            name: i.name,
                            id: i.id,
                            value: i.value,
                            required: i.required,
                            selector: i.id ? `#${i.id}` : `${i.tagName}[name="${i.name}"]`
                        })),
                        submitButton: buttons.length > 0 ? {
                            selector: buttons[0].id ? `#${buttons[0].id}` : `button[type="submit"]`,
                            text: buttons[0].textContent
                        } : null
                    };
                }
            """)
            
            print(f"   Found {len(form_info['fields'])} form fields:")
            for field in form_info['fields']:
                print(f"      - {field['type']} [{field['name']}] (required: {field['required']})")
            print()
            
            # Step 3: Fill form fields with test data
            print("⏳ Step 3: Filling form fields...")
            test_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '+1234567890',
                'message': 'This is a test submission',
                'subject': 'Test Subject'
            }
            
            filled_count = 0
            for field in form_info['fields']:
                field_name = field['name'].lower()
                
                # Look for matching test data
                for key, value in test_data.items():
                    if key in field_name or field_name in key:
                        try:
                            await page.fill(field['selector'], value)
                            print(f"   ✅ Filled {field['name']} = {value}")
                            filled_count += 1
                            break
                        except Exception as e:
                            print(f"   ⚠️  Could not fill {field['name']}: {str(e)[:50]}")
                            break
                
                # If no matching test data, fill with placeholder based on type
                if field_name not in ' '.join(test_data.keys()).lower():
                    if field['type'] == 'email':
                        try:
                            await page.fill(field['selector'], 'test@example.com')
                            filled_count += 1
                        except:
                            pass
                    elif 'phone' in field_name or 'tel' in field_name:
                        try:
                            await page.fill(field['selector'], '+1234567890')
                            filled_count += 1
                        except:
                            pass
            
            print(f"\n   Filled {filled_count} field(s)\n")
            
            # Step 4: Check for CAPTCHA before submit
            print("⏳ Step 4: Checking for CAPTCHA before submit...")
            captcha_before = await detect_simple_captcha(page)
            if captcha_before['present']:
                print(f"   ⚠️  CAPTCHA already on page: {captcha_before['type']}")
            else:
                print("   ℹ️  No CAPTCHA on page yet\n")
            
            # Step 5: Attempt form submission
            print("⏳ Step 5: Attempting form submission...")
            if form_info['submitButton']:
                try:
                    await page.click(form_info['submitButton']['selector'])
                    print(f"   ✅ Clicked submit button\n")
                except Exception as e:
                    print(f"   ⚠️  Could not click button: {str(e)[:50]}\n")
            else:
                # Try programmatic submit
                try:
                    await page.evaluate("""
                        () => {
                            const form = document.querySelector('form');
                            if (form) form.submit();
                        }
                    """)
                    print("   ✅ Form submitted programmatically\n")
                except Exception as e:
                    print(f"   ⚠️  Could not submit form: {str(e)[:50]}\n")
            
            # Wait for potential CAPTCHA or response
            print("⏳ Step 6: Waiting for page response (3 seconds)...")
            await page.wait_for_timeout(3000)
            print()
            
            # Step 6: Check for CAPTCHA after submit
            print("⏳ Step 7: Checking for CAPTCHA after submit...")
            captcha_after = await detect_simple_captcha(page)
            
            if captcha_after['present']:
                print(f"   ✅ CAPTCHA DETECTED: {captcha_after['type']}")
                print(f"      Site Key: {captcha_after.get('siteKey', 'N/A')[:40]}...\n")
                
                # Step 7: Attempt to solve CAPTCHA
                print("⏳ Step 8: Attempting to solve CAPTCHA...")
                
                site_key = captcha_after.get('siteKey')
                if site_key:
                    # Check if local solver is enabled
                    use_local = os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "true").lower() != "false"
                    print(f"   Using local solver: {use_local}\n")
                    
                    solver = LocalCaptchaSolver(page=page) if use_local else get_captcha_solver("auto")
                    
                    if solver:
                        print("   🤖 Starting CAPTCHA solver...")
                        print("      This may take 10-120 seconds...\n")
                        
                        try:
                            token = await solver.solve_recaptcha_v2(site_key, page.url)
                            
                            if token:
                                print(f"\n   ✅ CAPTCHA SOLVED!")
                                print(f"      Token: {token[:50]}...\n")
                                
                                # Check if token was injected
                                response_value = await page.evaluate("""
                                    () => {
                                        const field = document.querySelector('textarea[name="g-recaptcha-response"]');
                                        return field ? field.value.length : 0;
                                    }
                                """)
                                
                                if response_value > 0:
                                    print(f"   ✅ Token injected in form ({response_value} chars)\n")
                                    
                                    # Step 8: Try to submit again
                                    print("⏳ Step 9: Attempting to submit form with CAPTCHA token...")
                                    
                                    if form_info['submitButton']:
                                        try:
                                            await page.click(form_info['submitButton']['selector'])
                                            print("   ✅ Submit button clicked\n")
                                        except:
                                            try:
                                                await page.evaluate("""
                                                    () => {
                                                        const form = document.querySelector('form');
                                                        if (form) form.submit();
                                                    }
                                                """)
                                                print("   ✅ Form submitted\n")
                                            except Exception as e:
                                                print(f"   ⚠️  Submit failed: {str(e)[:50]}\n")
                                    
                                    # Wait for response
                                    await page.wait_for_timeout(3000)
                                    
                                    # Check final result
                                    print("⏳ Step 10: Checking submission result...")
                                    final_page = await page.evaluate("""
                                        () => {
                                            return {
                                                url: window.location.href,
                                                title: document.title,
                                                bodyText: document.body.textContent.substring(0, 200)
                                            };
                                        }
                                    """)
                                    
                                    print(f"   Final URL: {final_page['url']}")
                                    print(f"   Page title: {final_page['title']}\n")
                                    
                                    if 'thank' in final_page['bodyText'].lower() or 'success' in final_page['bodyText'].lower():
                                        print("✅ ✅ ✅ FORM SUBMITTED SUCCESSFULLY!")
                                    else:
                                        print("⚠️  Submission status unclear, check console output above")
                                else:
                                    print("   ❌ Token not injected in form\n")
                            else:
                                print("\n   ❌ CAPTCHA solver returned no token\n")
                        
                        except Exception as e:
                            print(f"\n   ❌ CAPTCHA solving error: {e}\n")
                            import traceback
                            traceback.print_exc()
                    else:
                        print("   ❌ No solver available\n")
                else:
                    print("   ❌ Could not extract site key\n")
            else:
                print("   ℹ️  No CAPTCHA appeared after form submission")
                print("      The form may have been accepted or shows a different validation\n")
                
                # Show page content
                page_text = await page.evaluate("""
                    () => document.body.textContent.substring(0, 300)
                """)
                print(f"   Page content: {page_text}...\n")
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()
            print("\n" + "=" * 80)


async def detect_simple_captcha(page):
    """Simple CAPTCHA detection."""
    try:
        result = await page.evaluate("""
            () => {
                // Check for reCAPTCHA v2
                const recaptchaV2 = document.querySelector('iframe[src*="recaptcha"]');
                const responseField = document.querySelector('textarea[name="g-recaptcha-response"]');
                
                if (recaptchaV2 || responseField) {
                    let siteKey = '';
                    const siteKeyEl = document.querySelector('[data-sitekey]');
                    if (siteKeyEl) siteKey = siteKeyEl.getAttribute('data-sitekey');
                    
                    return {
                        present: true,
                        type: 'recaptcha_v2',
                        siteKey: siteKey
                    };
                }
                
                // Check for hCaptcha
                if (document.querySelector('iframe[src*="hcaptcha"]')) {
                    return {
                        present: true,
                        type: 'hcaptcha',
                        siteKey: document.querySelector('[data-sitekey]')?.getAttribute('data-sitekey')
                    };
                }
                
                return { present: false, type: 'none' };
            }
        """)
        return result
    except:
        return {'present': False, 'type': 'none'}


async def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + "REAL FORM SUBMISSION TEST".center(78) + "║")
    print("║" + "(This will attempt to submit a real form and solve CAPTCHA)".center(78) + "║")
    print("╚" + "=" * 78 + "╝\n")
    
    await test_form_submission_with_captcha()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)
