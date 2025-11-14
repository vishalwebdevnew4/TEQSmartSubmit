#!/usr/bin/env python3
"""
Test script to debug CAPTCHA detection and solving on the actual target website.
Shows step-by-step what's happening.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "automation"))

async def test_captcha_on_target_site():
    """Test CAPTCHA detection and solving on the target website."""
    from playwright.async_api import async_playwright
    from captcha_solver import LocalCaptchaSolver
    
    url = "https://interiordesign.xcelanceweb.com/"
    
    print("=" * 80)
    print("DEBUGGING CAPTCHA ON TARGET WEBSITE")
    print("=" * 80)
    print(f"\n🌐 Website: {url}")
    print("⏳ Launching browser and loading page...\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Set longer timeouts
        page.set_default_timeout(30000)
        page.set_default_navigation_timeout(30000)
        
        try:
            # Navigate to the site
            print("Step 1: Loading website...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)  # Give page time to render
            print("✅ Website loaded\n")
            
            # Check initial page content
            print("Step 2: Checking for forms on page...")
            forms = await page.query_selector_all("form")
            print(f"✅ Found {len(forms)} form(s) on page\n")
            
            # Check for CAPTCHA before interaction
            print("Step 3: Checking for CAPTCHA on initial page...")
            initial_captcha = await detect_captcha_detailed(page)
            print(f"   CAPTCHA present: {initial_captcha['present']}")
            print(f"   CAPTCHA type: {initial_captcha['type']}")
            print(f"   Site key: {initial_captcha.get('siteKey', 'N/A')}")
            print()
            
            # Print first form if exists
            if forms:
                print("Step 4: Analyzing first form...")
                form_info = await page.evaluate("""
                    () => {
                        const form = document.querySelector('form');
                        if (!form) return null;
                        
                        const inputs = form.querySelectorAll('input, textarea, select');
                        const buttons = form.querySelectorAll('button, input[type="submit"]');
                        
                        return {
                            id: form.id,
                            action: form.action,
                            method: form.method,
                            fields: Array.from(inputs).map(i => ({
                                type: i.type || i.tagName,
                                name: i.name,
                                id: i.id,
                                required: i.required,
                                placeholder: i.placeholder
                            })),
                            submitButtons: Array.from(buttons).map(b => ({
                                type: b.type,
                                text: b.textContent,
                                id: b.id,
                                name: b.name
                            }))
                        };
                    }
                """)
                
                if form_info:
                    print(f"   Form ID: {form_info.get('id', 'N/A')}")
                    print(f"   Form action: {form_info.get('action', 'N/A')}")
                    print(f"   Form method: {form_info.get('method', 'post').upper()}")
                    print(f"   Fields found: {len(form_info.get('fields', []))}")
                    for i, field in enumerate(form_info.get('fields', [])[:5], 1):
                        print(f"      {i}. {field['type']} - {field['name'] or field['id']} (required: {field['required']})")
                    if len(form_info.get('fields', [])) > 5:
                        print(f"      ... and {len(form_info.get('fields', [])) - 5} more fields")
                    print(f"   Submit buttons: {len(form_info.get('submitButtons', []))}")
                print()
            
            # Now let's try to interact with the form (which might trigger CAPTCHA)
            print("Step 5: Attempting to trigger CAPTCHA by focusing on form...")
            await page.evaluate("""
                () => {
                    const input = document.querySelector('input[type="text"], input[type="email"], input[type="name"]');
                    if (input) input.focus();
                }
            """)
            await page.wait_for_timeout(2000)
            print("✅ Form interaction attempted\n")
            
            # Check for CAPTCHA after interaction
            print("Step 6: Checking for CAPTCHA after interaction...")
            after_interaction = await detect_captcha_detailed(page)
            print(f"   CAPTCHA present: {after_interaction['present']}")
            print(f"   CAPTCHA type: {after_interaction['type']}")
            if after_interaction.get('siteKey'):
                print(f"   Site key: {after_interaction.get('siteKey', 'N/A')}")
            print()
            
            # If CAPTCHA is present, show the iframes on page
            print("Step 7: Checking all iframes on page...")
            iframes_info = await page.evaluate("""
                () => {
                    const iframes = document.querySelectorAll('iframe');
                    return Array.from(iframes).map((i, idx) => ({
                        index: idx,
                        src: i.src,
                        title: i.title,
                        id: i.id,
                        visible: i.offsetParent !== null,
                        width: i.offsetWidth,
                        height: i.offsetHeight
                    }));
                }
            """)
            print(f"   Total iframes: {len(iframes_info)}")
            for iframe in iframes_info[:10]:
                print(f"      {iframe['index']}. {iframe['src'][:60] if iframe['src'] else iframe['title'] or 'No src/title'}")
                print(f"         Visible: {iframe['visible']}, Size: {iframe['width']}x{iframe['height']}")
            print()
            
            # Now try to solve if CAPTCHA exists
            if after_interaction['present']:
                print("Step 8: CAPTCHA DETECTED - Attempting to solve...\n")
                
                solver = LocalCaptchaSolver(page=page)
                site_key = after_interaction.get('siteKey')
                
                if site_key:
                    print(f"   Using site key: {site_key[:30]}...\n")
                    print("   🤖 Starting CAPTCHA solver (this may take up to 2 minutes)...\n")
                    
                    try:
                        token = await solver.solve_recaptcha_v2(site_key, page.url)
                        
                        if token:
                            print(f"\n   ✅ CAPTCHA SOLVED!")
                            print(f"      Token length: {len(token)}")
                            print(f"      Token preview: {token[:50]}...\n")
                            
                            # Verify token was injected
                            response_field = await page.evaluate("""
                                () => {
                                    const field = document.querySelector('textarea[name="g-recaptcha-response"]');
                                    return field ? field.value : null;
                                }
                            """)
                            
                            if response_field:
                                print(f"   ✅ Token injected in form field\n")
                            
                            # Now try to submit form
                            print("Step 9: Attempting to submit form after CAPTCHA solve...\n")
                            
                            submit_result = await submit_form(page)
                            print(f"\n   Submit result:")
                            print(f"      Submitted: {submit_result['submitted']}")
                            print(f"      Navigation: {submit_result['navigation']}")
                            print(f"      Final URL: {submit_result['final_url']}\n")
                            
                            if submit_result['submitted']:
                                print("✅ FORM SUBMITTED SUCCESSFULLY!")
                            else:
                                print("⚠️  Form was not submitted")
                        else:
                            print("   ❌ CAPTCHA solver returned no token\n")
                            print("   Possible causes:")
                            print("   - Audio challenge could not be solved")
                            print("   - Network connection issue")
                            print("   - CAPTCHA UI changed")
                    
                    except Exception as e:
                        print(f"   ❌ CAPTCHA solving error: {e}\n")
                        import traceback
                        traceback.print_exc()
                else:
                    print("   ⚠️  CAPTCHA detected but site key not found\n")
                    print("   Debugging info:")
                    page_html = await page.evaluate("""
                        () => {
                            const recaptcha = document.querySelector('iframe[src*="recaptcha"]');
                            if (recaptcha) {
                                return {
                                    src: recaptcha.src,
                                    title: recaptcha.title,
                                    outerHTML: recaptcha.outerHTML.substring(0, 200)
                                };
                            }
                            return null;
                        }
                    """)
                    if page_html:
                        print(f"      {json.dumps(page_html, indent=6)}\n")
            else:
                print("✅ No CAPTCHA detected on this page")
                print("   The page is ready to submit without CAPTCHA solving\n")
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()


async def detect_captcha_detailed(page):
    """Detailed CAPTCHA detection."""
    result = await page.evaluate("""
        () => {
            // Check for reCAPTCHA v2
            const recaptchaV2 = document.querySelector('iframe[src*="recaptcha"][src*="anchor"]');
            const recaptchaResponse = document.querySelector('textarea[name="g-recaptcha-response"]');
            
            if (recaptchaV2 || recaptchaResponse) {
                // Try to get site key
                let siteKey = '';
                const siteKeyEl = document.querySelector('[data-sitekey]');
                if (siteKeyEl) {
                    siteKey = siteKeyEl.getAttribute('data-sitekey');
                } else if (recaptchaV2) {
                    const src = recaptchaV2.src;
                    const match = src.match(/[&?]k=([^&]+)/);
                    if (match) siteKey = match[1];
                }
                
                return {
                    present: true,
                    type: 'recaptcha_v2',
                    siteKey: siteKey,
                    solved: recaptchaResponse && recaptchaResponse.value.length > 0,
                    iframeFound: recaptchaV2 !== null,
                    responseFieldFound: recaptchaResponse !== null
                };
            }
            
            // Check for hCaptcha
            const hcaptcha = document.querySelector('iframe[src*="hcaptcha"]');
            if (hcaptcha) {
                let siteKey = '';
                const siteKeyEl = document.querySelector('[data-sitekey]');
                if (siteKeyEl) {
                    siteKey = siteKeyEl.getAttribute('data-sitekey');
                }
                return {
                    present: true,
                    type: 'hcaptcha',
                    siteKey: siteKey,
                    iframeFound: true
                };
            }
            
            // Check for any recaptcha in page
            const anyRecaptcha = document.querySelector('script[src*="recaptcha"]');
            const anyRecaptchaDiv = document.querySelector('[class*="recaptcha"], [id*="recaptcha"]');
            
            return {
                present: false,
                type: 'none',
                anyRecaptchaScriptFound: anyRecaptcha !== null,
                anyRecaptchaDivFound: anyRecaptchaDiv !== null,
                recaptchaDivInfo: anyRecaptchaDiv ? {
                    class: anyRecaptchaDiv.className,
                    id: anyRecaptchaDiv.id
                } : null
            };
        }
    """)
    return result


async def submit_form(page):
    """Attempt to submit the form."""
    result = {
        'submitted': False,
        'navigation': False,
        'final_url': page.url
    }
    
    try:
        # Listen for navigation
        nav_promise = page.wait_for_load_state("networkidle", timeout=30000)
        
        # Try to find and click submit button
        submit_button = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Send")')
        
        if submit_button:
            await submit_button.click()
            result['submitted'] = True
        else:
            # Try to submit form programmatically
            await page.evaluate("""
                () => {
                    const form = document.querySelector('form');
                    if (form) form.submit();
                }
            """)
            result['submitted'] = True
        
        # Wait for navigation
        try:
            await nav_promise
            result['navigation'] = True
            result['final_url'] = page.url
        except:
            pass
    
    except Exception as e:
        print(f"      Error submitting: {str(e)[:80]}")
    
    return result


async def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + "CAPTCHA DEBUG - TARGET WEBSITE".center(78) + "║")
    print("╚" + "=" * 78 + "╝\n")
    
    await test_captcha_on_target_site()
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)
