#!/usr/bin/env python3
"""
Test actual form submission and capture the result
"""

import asyncio
import json
import sys
import time

async def test_manual_submission():
    """Test submitting a form manually to see what happens"""
    
    print("\n" + "="*80)
    print("MANUAL FORM SUBMISSION TEST")
    print("="*80)
    
    try:
        from playwright.async_api import async_playwright
        
        config = {
            "url": "https://interiordesign.xcelanceweb.com/",
            "form_data": {
                "name": "Test Submission",
                "email": "testuser@example.com",
                "phone": "+31612345678",
                "comment": "This is a test message to verify submissions are being received."
            }
        }
        
        print(f"\n📋 Form Data to Submit:")
        for key, value in config['form_data'].items():
            print(f"  {key}: {value}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print(f"\n🚀 Step 1: Navigate to form")
            await page.goto(config['url'], wait_until='networkidle')
            await page.wait_for_timeout(2000)
            print(f"✅ Page loaded")
            
            print(f"\n📝 Step 2: Fill form fields")
            
            # Fill name
            await page.fill('input[name="name"]', config['form_data']['name'])
            print(f"✅ Name: {config['form_data']['name']}")
            
            # Fill email
            await page.fill('input[name="email"]', config['form_data']['email'])
            print(f"✅ Email: {config['form_data']['email']}")
            
            # Fill phone
            await page.fill('input[name="phone"]', config['form_data']['phone'])
            print(f"✅ Phone: {config['form_data']['phone']}")
            
            # Fill message
            await page.fill('textarea[name="comment"]', config['form_data']['comment'])
            print(f"✅ Message: {config['form_data']['comment'][:50]}...")
            
            print(f"\n🤖 Step 3: Handle CAPTCHA")
            
            # Check for CAPTCHA
            captcha_frame = await page.query_selector('iframe[title*="reCAPTCHA"]')
            if captcha_frame:
                print(f"✅ reCAPTCHA detected")
                print(f"\n⚠️  MANUAL INTERACTION REQUIRED")
                print(f"    A browser window will open. Please:")
                print(f"    1. Solve the CAPTCHA manually")
                print(f"    2. The form will be automatically submitted")
                print(f"    3. Watch for success confirmation")
                
                # Show browser for manual CAPTCHA solving
                print(f"\n    Switching to headed mode...")
                await browser.close()
                
                # Relaunch with visible browser
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
                
                print(f"    Reloading form...")
                await page.goto(config['url'], wait_until='networkidle')
                await page.wait_for_timeout(2000)
                
                # Refill form
                await page.fill('input[name="name"]', config['form_data']['name'])
                await page.fill('input[name="email"]', config['form_data']['email'])
                await page.fill('input[name="phone"]', config['form_data']['phone'])
                await page.fill('textarea[name="comment"]', config['form_data']['comment'])
                
                print(f"\n    Waiting for CAPTCHA to be solved (60 seconds)...")
                
                # Wait for CAPTCHA solution
                start = time.time()
                while time.time() - start < 60:
                    try:
                        token_element = await page.query_selector('textarea[name="g-recaptcha-response"]')
                        if token_element:
                            token = await token_element.input_value()
                            if token:
                                print(f"✅ CAPTCHA solved!")
                                break
                    except:
                        pass
                    await page.wait_for_timeout(1000)
            else:
                print(f"⚠️  No CAPTCHA detected on form")
            
            print(f"\n✅ Step 4: Submit form")
            
            # Get submit button
            submit_btn = await page.query_selector('button:has-text("Bericht verzenden")')
            if not submit_btn:
                print(f"❌ Submit button not found!")
                return False
            
            # Intercept network requests to see what's being sent
            submitted_data = None
            
            def handle_response(response):
                nonlocal submitted_data
                if 'contact' in response.url or 'submit' in response.url or 'api' in response.url:
                    submitted_data = {
                        'url': response.url,
                        'status': response.status
                    }
            
            page.on('response', handle_response)
            
            # Click submit
            await submit_btn.click()
            print(f"✅ Submit button clicked")
            
            # Wait for response
            print(f"⏳ Waiting for server response...")
            await page.wait_for_timeout(5000)
            
            print(f"\n📊 Step 5: Check submission result")
            
            # Check for success message
            try:
                success_msg = await page.query_selector('text=/success|submitted|dank|bedankt|merci/i')
                if success_msg:
                    text = await success_msg.inner_text()
                    print(f"✅ SUCCESS MESSAGE FOUND:")
                    print(f"   {text}")
                    return True
            except:
                pass
            
            # Check URL change
            current_url = page.url
            if current_url != config['url']:
                print(f"✅ Page redirected to: {current_url}")
                return True
            
            # Check form cleared
            form_cleared = False
            try:
                name_value = await page.input_value('input[name="name"]')
                if not name_value or name_value == '':
                    form_cleared = True
                    print(f"✅ Form was cleared (success indicator)")
            except:
                pass
            
            if submitted_data:
                print(f"✅ Network request detected:")
                print(f"   URL: {submitted_data.get('url')}")
                print(f"   Status: {submitted_data.get('status')}")
            
            # Keep browser open for inspection
            print(f"\n🔍 Keeping browser open for 30 seconds for inspection...")
            await page.wait_for_timeout(30000)
            
            await browser.close()
            
            return form_cleared or submitted_data is not None
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test"""
    
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "TESTING ACTUAL FORM SUBMISSION".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    print("\n📌 This test will:")
    print("  1. Fill the contact form with test data")
    print("  2. Wait for you to solve the CAPTCHA manually")
    print("  3. Submit the form")
    print("  4. Verify the submission was received")
    
    success = await test_manual_submission()
    
    print("\n" + "="*80)
    if success:
        print("✅ SUBMISSION TEST PASSED")
        print("   Form submission appears to be working!")
    else:
        print("⚠️  SUBMISSION STATUS UNCLEAR")
        print("   Check browser console for errors")
    print("="*80)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏸️  Test interrupted")
        sys.exit(1)
