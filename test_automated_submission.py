#!/usr/bin/env python3
"""
Test why automated form submission is not working
Check if the form is actually submitting when button is clicked
"""

import asyncio
import sys
import json
from pathlib import Path

async def test_automated_submission():
    """Test automated form submission"""
    
    print("\n" + "="*80)
    print("AUTOMATED FORM SUBMISSION TEST")
    print("="*80)
    
    try:
        from playwright.async_api import async_playwright
        
        template = {
            "url": "https://interiordesign.xcelanceweb.com/",
            "fields": [
                {"selector": 'input[name="name"]', "value": "Auto Test User"},
                {"selector": 'input[name="email"]', "value": "autotest@example.com"},
                {"selector": 'input[name="phone"]', "value": "+31612345670"},
                {"selector": 'textarea[name="comment"]', "value": "This is an automated form submission test"}
            ],
            "use_local_captcha_solver": False,  # Disable to see if form submits without CAPTCHA
            "headless": False
        }
        
        print(f"\n📋 Test Configuration:")
        print(f"  URL: {template['url']}")
        print(f"  Local Solver: {template['use_local_captcha_solver']}")
        print(f"  Headless: {template['headless']}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=template['headless'])
            page = await browser.new_page()
            
            print(f"\n🚀 Step 1: Navigate to form")
            await page.goto(template['url'], wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_timeout(3000)
            print(f"✅ Page loaded")
            
            print(f"\n📝 Step 2: Fill form fields")
            
            for field in template['fields']:
                selector = field['selector']
                value = field['value']
                await page.fill(selector, value)
                print(f"✅ {selector}: filled")
            
            print(f"\n🔍 Step 3: Check form structure")
            
            # Check what form we're actually submitting
            forms = await page.query_selector_all('form')
            print(f"✅ Found {len(forms)} form(s)")
            
            # Get form details
            for i, form in enumerate(forms):
                form_id = await form.get_attribute('id')
                form_action = await form.get_attribute('action')
                form_method = await form.get_attribute('method')
                print(f"   Form {i+1}: id={form_id}, action={form_action}, method={form_method}")
            
            print(f"\n🔘 Step 4: Find submit button")
            
            # Try different button selectors
            selectors_to_try = [
                'button:has-text("Bericht verzenden")',
                'button[type="submit"]',
                'input[type="submit"]',
                'form button',
                'form input[type="submit"]'
            ]
            
            submit_button = None
            for selector in selectors_to_try:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        button_text = await button.inner_text() if hasattr(button, 'inner_text') else "N/A"
                        print(f"✅ Found with '{selector}': {button_text}")
                        submit_button = button
                        break
                except:
                    pass
            
            if not submit_button:
                print(f"❌ No submit button found!")
                return False
            
            print(f"\n📤 Step 5: Track network requests")
            
            # Track all requests
            all_posts = []
            
            def on_request(request):
                if request.method == 'POST':
                    all_posts.append({
                        'url': request.url,
                        'method': request.method,
                        'post_data': str(request.post_data)[:200] if request.post_data else 'None'
                    })
                    print(f"   📤 POST: {request.url}")
            
            page.on('request', on_request)
            
            print(f"\n🖱️  Step 6: Click submit button")
            
            # Get button position and text for debugging
            button_text = await page.evaluate('el => el.innerText', submit_button)
            print(f"Button text: '{button_text}'")
            print(f"Button type: {await submit_button.get_attribute('type')}")
            
            # Close any modals that might be blocking
            print("  Checking for modal overlays...")
            modals = await page.query_selector_all('div[class*="modal"], div[class*="overlay"], div.fixed.inset-0')
            if modals:
                print(f"  Found {len(modals)} potential modals, trying to close...")
                for modal in modals:
                    # Look for close buttons
                    close_btn = await modal.query_selector('button[aria-label="close"], button:has-text("×"), .close, [data-dismiss]')
                    if close_btn:
                        try:
                            await close_btn.click()
                            await page.wait_for_timeout(500)
                            print("  ✅ Closed modal")
                        except:
                            pass
            
            # Scroll button into view
            await submit_button.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)
            
            # Click the button - use force to bypass modal
            try:
                await submit_button.click(force=True)
            except:
                # If force click fails, try regular click
                await submit_button.click()
            print(f"✅ Submit button clicked")
            
            print(f"\n⏳ Step 7: Wait for form submission")
            
            # Wait for any network activity
            await page.wait_for_timeout(5000)
            
            print(f"\n📊 Step 8: Check results")
            
            if all_posts:
                print(f"✅ POST requests detected: {len(all_posts)}")
                for post in all_posts:
                    print(f"   - {post['url']}")
                    if post['post_data'] != 'None':
                        print(f"     Data: {post['post_data']}")
            else:
                print(f"⚠️  No POST requests detected!")
            
            # Check if page changed
            current_url = page.url
            print(f"\nCurrent URL: {current_url}")
            if current_url != template['url']:
                print(f"✅ Page redirected (possible success)")
            
            # Check page content for success/error messages
            page_content = await page.content()
            
            if 'success' in page_content.lower() or 'bedankt' in page_content.lower():
                print(f"✅ Success message detected in page")
            elif 'error' in page_content.lower() or 'fout' in page_content.lower():
                print(f"⚠️  Error message detected in page")
            
            # Check form fields
            name_value = await page.input_value('input[name="name"]')
            if name_value == '':
                print(f"✅ Form was cleared (likely submitted)")
            else:
                print(f"⚠️  Form still has data (may not have submitted): {name_value}")
            
            print(f"\n🔍 Step 9: Check page console")
            
            console_logs = []
            page.on('console', lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))
            
            await page.wait_for_timeout(3000)
            
            if console_logs:
                print(f"Console messages ({len(console_logs)}):")
                for log in console_logs[-10:]:  # Show last 10
                    print(f"  {log}")
            
            print(f"\n⏳ Keeping browser open for 30 seconds for inspection...")
            await page.wait_for_timeout(30000)
            
            await browser.close()
            
            return len(all_posts) > 0
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run test"""
    
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "DEBUGGING AUTOMATED FORM SUBMISSION".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    success = await test_automated_submission()
    
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)
    
    if success:
        print("\n✅ Form submission POST detected!")
        print("   The form is being submitted to the backend.")
        print("   Next step: Verify backend is receiving and recording the data.")
    else:
        print("\n❌ Form submission POST NOT detected!")
        print("   The form is not being submitted to any backend.")
        print("   Possible causes:")
        print("   1. CAPTCHA is required and blocking submission")
        print("   2. Form requires specific field values or validation")
        print("   3. Submit button click is not working properly")
        print("   4. Form uses custom JavaScript that prevents submission")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏸️  Interrupted")
        sys.exit(1)
