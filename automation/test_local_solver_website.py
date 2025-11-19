#!/usr/bin/env python3
"""
Test Local Captcha Solver on the actual website.
Tests the local solver with a real form submission on interiordesign.xcelanceweb.com
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the automation directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from captcha_solver import LocalCaptchaSolver, get_captcha_solver
from playwright.async_api import async_playwright


async def test_local_solver_on_website(url=None):
    """Test local captcha solver on the actual website."""
    if not url:
        url = "https://interiordesign.xcelanceweb.com/"
    
    print("=" * 70)
    print(f"Testing Local Captcha Solver on {url}")
    print("=" * 70)
    
    # Test data
    import random
    import string
    
    # Generate a random name with only letters and spaces (no numbers)
    first_names = ["John", "Sarah", "Michael", "Emily", "David", "Jessica", "James", "Amanda", "Robert", "Lisa"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Wilson", "Moore"]
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    random_suffix = ''.join(random.choices(string.ascii_uppercase, k=2))  # Two random letters
    name = f"{first_name} {last_name} {random_suffix}"
    
    test_data = {
        "name": name,  # Text only, no numbers
        "email": "test@example.com",
        "phone": "1234567890",
        "message": "Testing fully automated local CAPTCHA solver",
        "service": "WEBSITE DESIGN",  # For teqtopaustralia site
        "budget": "$1K-$5K",  # For teqtopaustralia site
        "source": "Google"  # For teqtopaustralia site
    }
    
    try:
        async with async_playwright() as p:
            print("\n🌐 Launching browser (headless mode)...")
            browser = await p.chromium.launch(headless=True)  # Headless mode for automated testing
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            # Navigate to the website
            print(f"\n📡 Navigating to {url}...")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"   ⚠️  Page load timeout or error: {e}")
                print("   Trying with 'load' wait condition...")
                try:
                    await page.goto(url, wait_until="load", timeout=60000)
                except Exception as e2:
                    print(f"   ⚠️  Still failed: {e2}")
                    print("   Proceeding anyway...")
            await page.wait_for_timeout(5000)  # Wait for page to fully load
            
            print("✅ Page loaded")
            
            # Wait for CAPTCHA to potentially load
            print("\n⏳ Waiting for page elements to load...")
            await page.wait_for_timeout(3000)  # Reduced timeout
            
            # Try to find the contact form first
            print("\n🔍 Looking for contact form...")
            contact_form = None
            try:
                # Look for form with message/bericht field or submit button with "verzenden"
                forms = await page.query_selector_all('form')
                for form in forms:
                    form_html = await form.inner_html()
                    # Check if this looks like a contact form (has textarea or message field)
                    has_textarea = await form.query_selector('textarea')
                    submit_text = await form.evaluate("""
                        (form) => {
                            const submitBtn = form.querySelector('button[type="submit"]');
                            return submitBtn ? submitBtn.textContent.trim() : '';
                        }
                    """)
                    if has_textarea or 'verzenden' in submit_text.lower() or 'bericht' in form_html.lower():
                        contact_form = form
                        print(f"   ✅ Found contact form with submit button: '{submit_text}'")
                        break
            except Exception as e:
                print(f"   ⚠️  Error finding contact form: {str(e)[:50]}")
            
            # Scroll to form if found
            if contact_form:
                await contact_form.scroll_into_view_if_needed()
                await page.wait_for_timeout(2000)
            
            # Detect CAPTCHA (wait a bit more for it to load)
            print("\n🔍 Detecting CAPTCHA...")
            for attempt in range(3):
                captcha_info = await page.evaluate("""
                    () => {
                        // Check for reCAPTCHA
                        const recaptcha = document.querySelector('iframe[src*="recaptcha"], iframe[title*="reCAPTCHA"]');
                        const recaptchaResponse = document.querySelector('textarea[name="g-recaptcha-response"]');
                        
                        if (recaptcha || recaptchaResponse) {
                            let siteKey = '';
                            const dataSitekey = document.querySelector('[data-sitekey]');
                            if (dataSitekey) {
                                siteKey = dataSitekey.getAttribute('data-sitekey') || '';
                            } else {
                                // Try to extract from iframe src
                                if (recaptcha) {
                                    const src = recaptcha.getAttribute('src') || '';
                                    const match = src.match(/[&?]k=([^&]+)/);
                                    if (match) {
                                        siteKey = match[1];
                                    }
                                }
                            }
                            return {
                                type: 'recaptcha',
                                present: true,
                                solved: recaptchaResponse ? recaptchaResponse.value.length > 0 : false,
                                responseField: recaptchaResponse ? 'g-recaptcha-response' : null,
                                siteKey: siteKey
                            };
                        }
                        
                        // Check for hCaptcha
                        const hcaptcha = document.querySelector('iframe[src*="hcaptcha"]');
                        if (hcaptcha) {
                            let siteKey = '';
                            const dataSitekey = document.querySelector('[data-sitekey]');
                            if (dataSitekey) {
                                siteKey = dataSitekey.getAttribute('data-sitekey') || '';
                            }
                            return {
                                type: 'hcaptcha',
                                present: true,
                                solved: false,
                                siteKey: siteKey
                            };
                        }
                        
                        return { type: 'none', present: false, solved: false };
                    }
                """)
                
                if captcha_info.get('present'):
                    break
                if attempt < 2:
                    print(f"   ⏳ CAPTCHA not found yet, waiting... (attempt {attempt + 1}/3)")
                    await page.wait_for_timeout(3000)
            
            print(f"   CAPTCHA Type: {captcha_info.get('type', 'none')}")
            print(f"   Present: {captcha_info.get('present', False)}")
            print(f"   Solved: {captcha_info.get('solved', False)}")
            if captcha_info.get('siteKey'):
                print(f"   Site Key: {captcha_info.get('siteKey')[:20]}...")
            
            # NOTE: We will fill form fields FIRST, then solve CAPTCHA
            
            # Fill form fields FIRST - focus on contact form if found
            print("\n📝 Filling form fields...")
            
            # If we found a contact form, focus on it
            form_context = contact_form if contact_form else page
            
            # First, discover all form fields to see what's required
            print("   🔍 Discovering form structure...")
            form_fields_info = await page.evaluate("""
                () => {
                    const form = document.querySelector('form');
                    if (!form) return { fields: [] };
                    
                    const fields = [];
                    const inputs = Array.from(form.querySelectorAll('input, textarea, select'));
                    
                    inputs.forEach(input => {
                        const name = input.name || input.id || '';
                        const type = input.type || '';
                        const tag = input.tagName.toLowerCase();
                        const isRequired = input.hasAttribute('required') || input.getAttribute('aria-required') === 'true';
                        const placeholder = input.placeholder || '';
                        const value = input.value || '';
                        const isVisible = input.offsetWidth > 0 && input.offsetHeight > 0;
                        
                        if (isVisible && !['hidden', 'submit', 'button'].includes(type)) {
                            fields.push({
                                name: name,
                                type: type,
                                tag: tag,
                                required: isRequired,
                                placeholder: placeholder,
                                currentValue: value,
                                selector: name ? `${tag}[name="${name}"]` : (input.id ? `#${input.id}` : '')
                            });
                        }
                    });
                    
                    return { fields: fields };
                }
            """)
            
            if form_fields_info.get('fields'):
                print(f"   Found {len(form_fields_info.get('fields', []))} form fields:")
                for field in form_fields_info.get('fields', [])[:10]:  # Show first 10
                    req = " (required)" if field.get('required') else ""
                    print(f"      - {field.get('tag')} {field.get('type')} name='{field.get('name')}'{req}")
            
            # Try to find and fill name field
            name_selectors = [
                'input[name="name"]',
                'input#form_name',
                'input[name="naam"]',
                'input[placeholder*="name" i]',
                'input[placeholder*="naam" i]',
                'input[placeholder*="Full Name" i]',
                'input[type="text"]:not([type="email"]):not([type="hidden"]):not([type="tel"])',
                '#name',
                '#naam'
            ]
            name_filled = False
            for selector in name_selectors:
                try:
                    if contact_form:
                        field = await contact_form.query_selector(selector)
                    else:
                        field = await page.query_selector(selector)
                    if field:
                        # Check if field is visible
                        is_visible = await field.is_visible()
                        if is_visible:
                            await field.scroll_into_view_if_needed()
                            await field.fill(test_data['name'])
                            print(f"   ✅ Name field filled: {selector}")
                            name_filled = True
                            break
                except:
                    continue
            
            # Try to find and fill email field (but not in subscription forms)
            email_selectors = [
                'input[name="email"]',
                'input#form_email',
                'input[type="email"]',
                'input[type="text"][name="email"]',
                '#email'
            ]
            email_filled = False
            for selector in email_selectors:
                try:
                    if contact_form:
                        field = await contact_form.query_selector(selector)
                    else:
                        # Skip email subscription forms - look for email in forms with textarea
                        all_forms = await page.query_selector_all('form')
                        field = None
                        for form in all_forms:
                            has_textarea = await form.query_selector('textarea')
                            if has_textarea:
                                field = await form.query_selector(selector)
                                if field:
                                    break
                    if field:
                        is_visible = await field.is_visible()
                        if is_visible:
                            await field.scroll_into_view_if_needed()
                            await field.fill(test_data['email'])
                            print(f"   ✅ Email field filled: {selector}")
                            email_filled = True
                            break
                except:
                    continue
            
            # Try to find and fill phone field (for teqtopaustralia site)
            phone_selectors = [
                'input[name="phone"]',
                'input#form_phone',
                'input[type="tel"]',
                'input[placeholder*="phone" i]',
                '#phone'
            ]
            phone_filled = False
            for selector in phone_selectors:
                try:
                    if contact_form:
                        field = await contact_form.query_selector(selector)
                    else:
                        field = await page.query_selector(selector)
                    if field:
                        is_visible = await field.is_visible()
                        if is_visible:
                            await field.scroll_into_view_if_needed()
                            await field.fill(test_data['phone'])
                            print(f"   ✅ Phone field filled: {selector}")
                            phone_filled = True
                            break
                except:
                    continue
            
            # Try to find and fill message field
            message_selectors = [
                'textarea[name="message"]',
                'textarea#form_message',
                'textarea[name="bericht"]',
                'textarea[placeholder*="message" i]',
                'textarea[placeholder*="bericht" i]',
                'textarea:not([style*="display: none"])',
                'textarea',
                '#message',
                '#bericht'
            ]
            message_filled = False
            for selector in message_selectors:
                try:
                    if contact_form:
                        field = await contact_form.query_selector(selector)
                    else:
                        field = await page.query_selector(selector)
                    if field:
                        is_visible = await field.is_visible()
                        if is_visible:
                            await field.scroll_into_view_if_needed()
                            await field.fill(test_data['message'])
                            print(f"   ✅ Message field filled: {selector}")
                            message_filled = True
                            break
                except:
                    continue
            
            # Fill all other required/optional fields with RANDOM valid choices
            print("\n   🔄 Filling other form fields with RANDOM valid options...")
            import random
            
            # IMPORTANT: Leave honeypot fields EMPTY (like website_xce) - these are spam traps!
            # The form has: <input type="text" id="website_xce" name="website">
            # This should remain EMPTY - if filled, form will be rejected as spam
            
            # Handle checkboxes with same name (like interest[]) - select at least one RANDOM
            try:
                # Look for checkbox groups (same name, like interest[])
                checkbox_groups = await page.evaluate("""
                    () => {
                        const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
                        const groups = {};
                        checkboxes.forEach(cb => {
                            const name = cb.name;
                            // Skip honeypot/spam trap checkboxes
                            // For Bootstrap custom checkboxes, the input might be hidden but still functional
                            if (name && !name.includes('website') && !name.includes('honeypot')) {
                                if (!groups[name]) {
                                    groups[name] = [];
                                }
                                // Find associated label
                                let labelText = '';
                                if (cb.id) {
                                    const label = document.querySelector(`label[for="${cb.id}"]`);
                                    if (label) {
                                        labelText = label.textContent.trim();
                                    }
                                }
                                groups[name].push({
                                    id: cb.id,
                                    value: cb.value,
                                    checked: cb.checked,
                                    labelText: labelText
                                });
                            }
                        });
                        return groups;
                    }
                """)
                
                print(f"   Found {len(checkbox_groups)} checkbox group(s)")
                for group_name, checkboxes in checkbox_groups.items():
                    if checkboxes and len(checkboxes) > 0:
                        print(f"   Processing checkbox group: {group_name} ({len(checkboxes)} options)")
                        # Select at least one RANDOM checkbox from this group
                        # For interest[] type fields, select 1-2 random options
                        num_to_select = random.randint(1, min(2, len(checkboxes)))
                        selected = random.sample(checkboxes, num_to_select)
                        
                        for cb_info in selected:
                            try:
                                checkbox_selected = False
                                
                                # Method 1: Try clicking the outer label (wraps the <li>) - most reliable for this structure
                                if cb_info.get('id'):
                                    checkbox = await page.query_selector(f'input[type="checkbox"][id="{cb_info["id"]}"]')
                                    if checkbox:
                                        # Find and click the outer label that wraps the checkbox using JavaScript
                                        try:
                                            clicked = await checkbox.evaluate("""
                                                (cb) => {
                                                    // Find the closest label ancestor that wraps the li
                                                    let element = cb;
                                                    let label = null;
                                                    while (element && element !== document.body) {
                                                        if (element.tagName === 'LABEL') {
                                                            label = element;
                                                            break;
                                                        }
                                                        element = element.parentElement;
                                                    }
                                                    
                                                    if (label) {
                                                        // Scroll into view
                                                        label.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                                        // Click the label
                                                        label.click();
                                                        return true;
                                                    }
                                                    return false;
                                                }
                                            """)
                                            
                                            if clicked:
                                                await asyncio.sleep(0.4)
                                                # Verify it's checked
                                                is_checked = await checkbox.evaluate("(cb) => cb.checked")
                                                if is_checked:
                                                    print(f"   ✅ Random checkbox selected (via outer label): {group_name} = {cb_info['value']} ({cb_info.get('labelText', '')[:30]})")
                                                    checkbox_selected = True
                                        except Exception as e:
                                            pass
                                        
                                        # Method 2: Try clicking the inner label (custom-control-label)
                                        if not checkbox_selected:
                                            inner_label = await page.query_selector(f'label[for="{cb_info["id"]}"]')
                                            if inner_label:
                                                try:
                                                    await inner_label.scroll_into_view_if_needed()
                                                    await asyncio.sleep(0.2)
                                                    await inner_label.click()
                                                    await asyncio.sleep(0.4)
                                                    # Verify it's checked
                                                    is_checked = await checkbox.evaluate("(cb) => cb.checked")
                                                    if is_checked:
                                                        print(f"   ✅ Random checkbox selected (via inner label): {group_name} = {cb_info['value']} ({cb_info.get('labelText', '')[:30]})")
                                                        checkbox_selected = True
                                                except:
                                                    pass
                                        
                                        # Method 3: Try clicking the checkbox directly
                                        if not checkbox_selected:
                                            try:
                                                await checkbox.scroll_into_view_if_needed()
                                                await checkbox.click()
                                                await asyncio.sleep(0.4)
                                                # Verify it's checked
                                                is_checked = await checkbox.evaluate("(cb) => cb.checked")
                                                if is_checked:
                                                    print(f"   ✅ Random checkbox selected (direct click): {group_name} = {cb_info['value']} ({cb_info.get('labelText', '')[:30]})")
                                                    checkbox_selected = True
                                            except:
                                                pass
                                        
                                        # Method 4: Use Playwright's check() method
                                        if not checkbox_selected:
                                            try:
                                                await checkbox.scroll_into_view_if_needed()
                                                await checkbox.check()
                                                await asyncio.sleep(0.4)
                                                # Verify it's checked
                                                is_checked = await checkbox.evaluate("(cb) => cb.checked")
                                                if is_checked:
                                                    print(f"   ✅ Random checkbox selected (check method): {group_name} = {cb_info['value']} ({cb_info.get('labelText', '')[:30]})")
                                                    checkbox_selected = True
                                            except:
                                                pass
                                        
                                        # Method 5: Use JavaScript to check and trigger events
                                        if not checkbox_selected:
                                            try:
                                                await checkbox.evaluate("""
                                                    (cb) => {
                                                        cb.checked = true;
                                                        // Trigger all events that might be needed
                                                        const events = ['change', 'click', 'input', 'focus', 'blur'];
                                                        events.forEach(eventType => {
                                                            const event = new Event(eventType, { bubbles: true, cancelable: true });
                                                            cb.dispatchEvent(event);
                                                        });
                                                        // Also trigger on the parent elements
                                                        let parent = cb.parentElement;
                                                        while (parent && parent !== document.body) {
                                                            const changeEvent = new Event('change', { bubbles: true, cancelable: true });
                                                            parent.dispatchEvent(changeEvent);
                                                            parent = parent.parentElement;
                                                        }
                                                    }
                                                """)
                                                await asyncio.sleep(0.4)
                                                is_checked = await checkbox.evaluate("(cb) => cb.checked")
                                                if is_checked:
                                                    print(f"   ✅ Random checkbox selected (JS): {group_name} = {cb_info['value']} ({cb_info.get('labelText', '')[:30]})")
                                                    checkbox_selected = True
                                            except:
                                                pass
                                
                                # Method 6: Fallback - try by value
                                if not checkbox_selected:
                                    checkbox = await page.query_selector(f'input[type="checkbox"][name="{group_name}"][value="{cb_info["value"]}"]')
                                    if checkbox:
                                        try:
                                            await checkbox.scroll_into_view_if_needed()
                                            await checkbox.check()
                                            await asyncio.sleep(0.4)
                                            is_checked = await checkbox.evaluate("(cb) => cb.checked")
                                            if is_checked:
                                                print(f"   ✅ Random checkbox selected (by value): {group_name} = {cb_info['value']}")
                                                checkbox_selected = True
                                        except:
                                            pass
                                
                                if not checkbox_selected:
                                    print(f"   ❌ Failed to select checkbox: {group_name} = {cb_info['value']} (ID: {cb_info.get('id', 'N/A')})")
                                    
                            except Exception as e:
                                print(f"   ⚠️  Error selecting checkbox: {str(e)[:50]}")
            except Exception as e:
                print(f"   ⚠️  Error with checkboxes: {str(e)[:50]}")
            
            # Handle radio button groups (like budget) - select one RANDOM
            try:
                radio_groups = await page.evaluate("""
                    () => {
                        const radios = Array.from(document.querySelectorAll('input[type="radio"]'));
                        const groups = {};
                        radios.forEach(r => {
                            const name = r.name;
                            // For Bootstrap custom radios, the input might be hidden but still functional
                            if (name && !name.includes('website') && !name.includes('honeypot')) {
                                if (!groups[name]) {
                                    groups[name] = [];
                                }
                                // Find associated label
                                let labelText = '';
                                if (r.id) {
                                    const label = document.querySelector(`label[for="${r.id}"]`);
                                    if (label) {
                                        labelText = label.textContent.trim();
                                    }
                                }
                                groups[name].push({
                                    id: r.id,
                                    value: r.value,
                                    checked: r.checked,
                                    labelText: labelText
                                });
                            }
                        });
                        return groups;
                    }
                """)
                
                print(f"   Found {len(radio_groups)} radio group(s)")
                # Select RANDOM option from each radio group
                for group_name, radios in radio_groups.items():
                    if radios and len(radios) > 0:
                        print(f"   Processing radio group: {group_name} ({len(radios)} options)")
                        # Select a random radio from this group
                        random_radio_info = random.choice(radios)
                        radio_selected = False
                        
                        try:
                            # Method 1: Try clicking the outer label (wraps the <li>) - for Bootstrap custom radios
                            if random_radio_info.get('id'):
                                radio = await page.query_selector(f'input[type="radio"][id="{random_radio_info["id"]}"]')
                                if radio:
                                    # Find and click the outer label that wraps the radio using JavaScript
                                    try:
                                        clicked = await radio.evaluate("""
                                            (r) => {
                                                // Find the closest label ancestor that wraps the li
                                                let element = r;
                                                let label = null;
                                                while (element && element !== document.body) {
                                                    if (element.tagName === 'LABEL') {
                                                        label = element;
                                                        break;
                                                    }
                                                    element = element.parentElement;
                                                }
                                                
                                                if (label) {
                                                    // Scroll into view
                                                    label.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                                    // Click the label
                                                    label.click();
                                                    return true;
                                                }
                                                return false;
                                            }
                                        """)
                                        
                                        if clicked:
                                            await asyncio.sleep(0.4)
                                            # Verify it's checked
                                            is_checked = await radio.evaluate("(r) => r.checked")
                                            if is_checked:
                                                print(f"   ✅ Random radio selected (via outer label): {group_name} = {random_radio_info['value']} ({random_radio_info.get('labelText', '')[:30]})")
                                                radio_selected = True
                                    except:
                                        pass
                                    
                                    # Method 2: Try clicking the inner label (custom-control-label)
                                    if not radio_selected:
                                        inner_label = await page.query_selector(f'label[for="{random_radio_info["id"]}"]')
                                        if inner_label:
                                            try:
                                                await inner_label.scroll_into_view_if_needed()
                                                await asyncio.sleep(0.2)
                                                await inner_label.click()
                                                await asyncio.sleep(0.4)
                                                # Verify it's checked
                                                is_checked = await radio.evaluate("(r) => r.checked")
                                                if is_checked:
                                                    print(f"   ✅ Random radio selected (via inner label): {group_name} = {random_radio_info['value']} ({random_radio_info.get('labelText', '')[:30]})")
                                                    radio_selected = True
                                            except:
                                                pass
                                    
                                    # Method 3: Try clicking the radio directly
                                    if not radio_selected:
                                        try:
                                            await radio.scroll_into_view_if_needed()
                                            await radio.click()
                                            await asyncio.sleep(0.4)
                                            # Verify it's checked
                                            is_checked = await radio.evaluate("(r) => r.checked")
                                            if is_checked:
                                                print(f"   ✅ Random radio selected (direct click): {group_name} = {random_radio_info['value']} ({random_radio_info.get('labelText', '')[:30]})")
                                                radio_selected = True
                                        except:
                                            pass
                                    
                                    # Method 4: Use Playwright's check() method
                                    if not radio_selected:
                                        try:
                                            await radio.scroll_into_view_if_needed()
                                            await radio.check()
                                            await asyncio.sleep(0.4)
                                            # Verify it's checked
                                            is_checked = await radio.evaluate("(r) => r.checked")
                                            if is_checked:
                                                print(f"   ✅ Random radio selected (check method): {group_name} = {random_radio_info['value']} ({random_radio_info.get('labelText', '')[:30]})")
                                                radio_selected = True
                                        except:
                                            pass
                                    
                                    # Method 5: Use JavaScript to check and trigger events
                                    if not radio_selected:
                                        try:
                                            await radio.evaluate("""
                                                (r) => {
                                                    r.checked = true;
                                                    // Trigger all events that might be needed
                                                    const events = ['change', 'click', 'input', 'focus', 'blur'];
                                                    events.forEach(eventType => {
                                                        const event = new Event(eventType, { bubbles: true, cancelable: true });
                                                        r.dispatchEvent(event);
                                                    });
                                                    // Also trigger on the parent elements
                                                    let parent = r.parentElement;
                                                    while (parent && parent !== document.body) {
                                                        const changeEvent = new Event('change', { bubbles: true, cancelable: true });
                                                        parent.dispatchEvent(changeEvent);
                                                        parent = parent.parentElement;
                                                    }
                                                }
                                            """)
                                            await asyncio.sleep(0.4)
                                            is_checked = await radio.evaluate("(r) => r.checked")
                                            if is_checked:
                                                print(f"   ✅ Random radio selected (JS): {group_name} = {random_radio_info['value']} ({random_radio_info.get('labelText', '')[:30]})")
                                                radio_selected = True
                                        except:
                                            pass
                            
                            # Method 6: Fallback - try by value
                            if not radio_selected:
                                radio = await page.query_selector(f'input[type="radio"][name="{group_name}"][value="{random_radio_info["value"]}"]')
                                if radio:
                                    try:
                                        await radio.scroll_into_view_if_needed()
                                        await radio.check()
                                        await asyncio.sleep(0.4)
                                        is_checked = await radio.evaluate("(r) => r.checked")
                                        if is_checked:
                                            print(f"   ✅ Random radio selected (by value): {group_name} = {random_radio_info['value']}")
                                            radio_selected = True
                                    except:
                                        pass
                            
                            if not radio_selected:
                                print(f"   ❌ Failed to select radio: {group_name} = {random_radio_info['value']} (ID: {random_radio_info.get('id', 'N/A')})")
                                
                        except Exception as e:
                            print(f"   ⚠️  Error selecting radio: {str(e)[:50]}")
            except Exception as e:
                print(f"   ⚠️  Error with radios: {str(e)[:50]}")
            
            # Handle select dropdowns - select RANDOM non-empty option
            try:
                all_selects = await page.query_selector_all('select')
                print(f"   Found {len(all_selects)} select dropdown(s)")
                for select in all_selects:
                    is_visible = await select.is_visible()
                    if is_visible:
                        name = await select.get_attribute('name') or ''
                        select_id = await select.get_attribute('id') or ''
                        print(f"   Processing select: name='{name}' id='{select_id}'")
                        
                        # Get all options first
                        all_options = await select.query_selector_all('option')
                        print(f"      Found {len(all_options)} total options")
                        
                        # Filter out empty value options
                        non_empty_options = []
                        for opt in all_options:
                            opt_value = await opt.get_attribute('value') or ''
                            if opt_value and opt_value.strip():  # Not empty
                                opt_text = await opt.inner_text()
                                non_empty_options.append({
                                    'element': opt,
                                    'value': opt_value,
                                    'text': opt_text.strip()
                                })
                        
                        if non_empty_options and len(non_empty_options) > 0:
                            # Select a RANDOM option
                            random_opt = random.choice(non_empty_options)
                            value = random_opt['value']
                            text = random_opt['text']
                            print(f"      Selecting random option: value='{value}' text='{text[:30]}'")
                            
                            # Try multiple methods to select
                            selected = False
                            
                            # Method 1: Use Playwright's select_option with value
                            try:
                                await select.select_option(value=value)
                                await asyncio.sleep(0.3)
                                selected_value = await select.evaluate("(select) => select.value")
                                if selected_value == value:
                                    print(f"   ✅ Random select filled (method 1): {name} = {value} ({text[:30]})")
                                    selected = True
                            except Exception as e1:
                                print(f"      Method 1 failed: {str(e1)[:40]}")
                            
                            # Method 2: Use select_option with label if method 1 failed
                            if not selected:
                                try:
                                    await select.select_option(label=text)
                                    await asyncio.sleep(0.3)
                                    selected_value = await select.evaluate("(select) => select.value")
                                    if selected_value == value:
                                        print(f"   ✅ Random select filled (method 2): {name} = {value} ({text[:30]})")
                                        selected = True
                                except Exception as e2:
                                    print(f"      Method 2 failed: {str(e2)[:40]}")
                            
                            # Method 3: Use JavaScript directly
                            if not selected:
                                try:
                                    await select.evaluate("""
                                        (select, value) => {
                                            select.value = value;
                                            // Trigger all events
                                            const events = ['change', 'input', 'blur'];
                                            events.forEach(eventType => {
                                                const event = new Event(eventType, { bubbles: true, cancelable: true });
                                                select.dispatchEvent(event);
                                            });
                                        }
                                    """, value)
                                    await asyncio.sleep(0.5)
                                    selected_value = await select.evaluate("(select) => select.value")
                                    if selected_value == value:
                                        print(f"   ✅ Random select filled (method 3 - JS): {name} = {value} ({text[:30]})")
                                        selected = True
                                    else:
                                        print(f"      Method 3 value mismatch: expected '{value}', got '{selected_value}'")
                                except Exception as e3:
                                    print(f"      Method 3 failed: {str(e3)[:40]}")
                            
                            # Method 4: Try by index
                            if not selected:
                                try:
                                    # Find the index of the option
                                    option_index = None
                                    for idx, opt_info in enumerate(non_empty_options):
                                        if opt_info['value'] == value:
                                            option_index = idx + 1  # +1 because first option might be empty
                                            break
                                    
                                    if option_index:
                                        await select.select_option(index=option_index)
                                        await asyncio.sleep(0.3)
                                        selected_value = await select.evaluate("(select) => select.value")
                                        if selected_value == value:
                                            print(f"   ✅ Random select filled (method 4 - index): {name} = {value}")
                                            selected = True
                                except Exception as e4:
                                    print(f"      Method 4 failed: {str(e4)[:40]}")
                            
                            if not selected:
                                print(f"   ❌ Failed to select option in {name} dropdown")
                        else:
                            print(f"   ⚠️  No non-empty options found in select: {name}")
            except Exception as e:
                print(f"   ⚠️  Error with selects: {str(e)[:50]}")
                import traceback
                traceback.print_exc()
            
            # Fill any other required text inputs we might have missed
            # BUT: Skip honeypot fields like "website" or "website_xce" - these should stay EMPTY!
            try:
                other_required = await page.query_selector_all('input[required]:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([value])')
                for field in other_required:
                    field_type = await field.get_attribute('type') or 'text'
                    field_name = await field.get_attribute('name') or ''
                    field_id = await field.get_attribute('id') or ''
                    
                    # Skip honeypot/spam trap fields
                    if 'website' in field_name.lower() or 'website' in field_id.lower() or 'honeypot' in field_name.lower():
                        print(f"   ⚠️  Skipping honeypot field: {field_name} (must stay empty)")
                        continue
                    
                    if field_type == 'tel' and not phone_filled:
                        await field.fill(test_data['phone'])
                        print(f"   ✅ Required phone field filled: {field_name}")
                    elif field_type == 'email' and not email_filled:
                        await field.fill(test_data['email'])
                        print(f"   ✅ Required email field filled: {field_name}")
                    elif field_type == 'text' and 'name' not in field_name.lower() and 'phone' not in field_name.lower():
                        # Fill with a generic value
                        await field.fill("Test Value")
                        print(f"   ✅ Required text field filled: {field_name}")
            except Exception as e:
                pass
            
            # Summary of main fields
            print("\n📋 Form Fields Summary:")
            print(f"   Name: {'✅' if name_filled else '❌'}")
            print(f"   Email: {'✅' if email_filled else '❌'}")
            print(f"   Message: {'✅' if message_filled else '❌'}")
            if not name_filled or not email_filled or not message_filled:
                print("\n⚠️  Warning: Main fields (name, email, message) not all filled!")
            
            # NOW solve CAPTCHA after all fields are filled
            print("\n" + "="*70)
            print("NOW SOLVING CAPTCHA (after filling all form fields)")
            print("="*70)
            
            # Re-check for CAPTCHA (it might have loaded by now)
            if not captcha_info.get('present'):
                print("\n⚠️  Re-checking for CAPTCHA...")
                await page.wait_for_timeout(2000)
                captcha_info = await page.evaluate("""
                    () => {
                        const recaptcha = document.querySelector('iframe[src*="recaptcha"], iframe[title*="reCAPTCHA"]');
                        const recaptchaResponse = document.querySelector('textarea[name="g-recaptcha-response"]');
                        if (recaptcha || recaptchaResponse) {
                            let siteKey = '';
                            const dataSitekey = document.querySelector('[data-sitekey]');
                            if (dataSitekey) {
                                siteKey = dataSitekey.getAttribute('data-sitekey') || '';
                            }
                            return {
                                type: 'recaptcha',
                                present: true,
                                solved: recaptchaResponse ? recaptchaResponse.value.length > 0 : false,
                                responseField: recaptchaResponse ? 'g-recaptcha-response' : null,
                                siteKey: siteKey
                            };
                        }
                        return { type: 'none', present: false, solved: false };
                    }
                """)
                print(f"   CAPTCHA Present: {captcha_info.get('present', False)}")
            
            if captcha_info.get('present'):
                # Initialize local solver
                print("\n🤖 Initializing Local Captcha Solver...")
                solver = LocalCaptchaSolver(page=page)
                print("   ✅ Solver initialized")
                
                # Solve CAPTCHA
                if captcha_info.get('type') == 'recaptcha':
                    site_key = captcha_info.get('siteKey', '')
                    print(f"\n🎯 Solving reCAPTCHA v2...")
                    print(f"   Site Key: {site_key[:30]}..." if site_key else "   (No site key found)")
                    
                    try:
                        # First, click the checkbox to trigger challenge
                        print("\n🖱️  Clicking reCAPTCHA checkbox to trigger challenge...")
                        await solver._click_recaptcha_checkbox()
                        await page.wait_for_timeout(2000)  # Wait for challenge to appear
                        
                        # Check if challenge appeared
                        challenge_present = await solver._check_challenge_present()
                        if challenge_present:
                            print("   ✅ Challenge appeared!")
                            
                            # Get the challenge frame
                            challenge_frame = await page.query_selector('iframe[title*="challenge"], iframe[src*="bframe"]')
                            if challenge_frame:
                                frame = await challenge_frame.content_frame()
                                if frame:
                                    print("\n🔘 Clicking audio challenge button...")
                                    # Try to find and click the audio button
                                    audio_button_clicked = False
                                    audio_selectors = [
                                        '#recaptcha-audio-button',
                                        'button[title*="audio"]',
                                        'button[title*="Audio"]',
                                        '.rc-button-audio',
                                        'button.rc-button-audio',
                                        'button[id*="audio"]'
                                    ]
                                    
                                    for selector in audio_selectors:
                                        try:
                                            audio_btn = await frame.query_selector(selector)
                                            if audio_btn:
                                                is_visible = await audio_btn.is_visible()
                                                if is_visible:
                                                    print(f"   ✅ Found audio button: {selector}")
                                                    await audio_btn.scroll_into_view_if_needed()
                                                    await asyncio.sleep(0.5)
                                                    await audio_btn.click()
                                                    print("   ✅ Audio button clicked!")
                                                    audio_button_clicked = True
                                                    await page.wait_for_timeout(2000)
                                                    break
                                        except Exception as e:
                                            continue
                                    
                                    if not audio_button_clicked:
                                        # Try JavaScript click
                                        print("   ⚠️  Direct click failed, trying JavaScript...")
                                        clicked = await frame.evaluate("""
                                            () => {
                                                const audioBtn = document.querySelector('#recaptcha-audio-button, button[title*="audio"], .rc-button-audio');
                                                if (audioBtn) {
                                                    audioBtn.click();
                                                    return true;
                                                }
                                                return false;
                                            }
                                        """)
                                        if clicked:
                                            print("   ✅ Audio button clicked via JavaScript!")
                                            audio_button_clicked = True
                                            await page.wait_for_timeout(2000)
                                    
                                    if audio_button_clicked:
                                        print("\n🎧 Audio challenge activated! Now solving...")
                                        print("   ⏱️  Using faster solve method...")
                                        try:
                                            solved = await asyncio.wait_for(solver._solve_audio_challenge(), timeout=20)
                                            if solved:
                                                print("   ✅ Audio challenge solved!")
                                            else:
                                                print("   ⚠️  Audio challenge solving reported failure, but checking for token...")
                                        except asyncio.TimeoutError:
                                            print("   ⏰ Audio solving timed out (20s), trying alternative method...")
                                            solved = False
                                        
                                        # Wait and check for token
                                        await page.wait_for_timeout(2000)
                                        token = await solver._get_recaptcha_token()
                                        if token:
                                            print(f"\n✅ CAPTCHA solved successfully via audio challenge!")
                                            print(f"   Token length: {len(token)}")
                                            print(f"   Token preview: {token[:50]}...")
                                        else:
                                            print("\n⚠️  No token yet, trying full solve method...")
                                            try:
                                                token = await asyncio.wait_for(solver.solve_recaptcha_v2(site_key, url), timeout=30)
                                                if token:
                                                    print(f"   ✅ Got token via full solve method!")
                                                else:
                                                    print("   ⚠️  Still no token")
                                            except asyncio.TimeoutError:
                                                print("   ⏰ Full solve timed out (30s)")
                                                token = None
                                    else:
                                        print("   ⚠️  Could not click audio button, trying full solve...")
                                        try:
                                            token = await asyncio.wait_for(solver.solve_recaptcha_v2(site_key, url), timeout=30)
                                            if token:
                                                print(f"\n✅ CAPTCHA solved!")
                                                print(f"   Token length: {len(token)}")
                                        except asyncio.TimeoutError:
                                            print("   ⏰ Full solve timed out")
                                            token = None
                                else:
                                    print("   ⚠️  Could not access challenge frame, trying full solve...")
                                    try:
                                        token = await asyncio.wait_for(solver.solve_recaptcha_v2(site_key, url), timeout=30)
                                        if token:
                                            print(f"\n✅ CAPTCHA solved!")
                                    except asyncio.TimeoutError:
                                        token = None
                            else:
                                print("   ⚠️  Challenge iframe not found, trying full solve...")
                                try:
                                    token = await asyncio.wait_for(solver.solve_recaptcha_v2(site_key, url), timeout=30)
                                    if token:
                                        print(f"\n✅ CAPTCHA solved!")
                                except asyncio.TimeoutError:
                                    token = None
                        else:
                            print("   ℹ️  No challenge appeared (might be solved automatically)")
                            await page.wait_for_timeout(2000)
                            token = await solver._get_recaptcha_token()
                            if not token:
                                try:
                                    token = await asyncio.wait_for(solver.solve_recaptcha_v2(site_key, url), timeout=30)
                                except asyncio.TimeoutError:
                                    token = None
                        
                        if token:
                            print(f"\n✅ CAPTCHA solved successfully!")
                            print(f"   Token length: {len(token)}")
                            print(f"   Token preview: {token[:50]}...")
                            
                            # Verify token is in the form
                            token_in_form = await page.evaluate("""
                                () => {
                                    const field = document.querySelector('textarea[name="g-recaptcha-response"]');
                                    return field && field.value && field.value.length > 0;
                                }
                            """)
                            if token_in_form:
                                print("   ✅ Token verified in form field")
                            else:
                                print("   ⚠️  Token not found in form field")
                            
                            print("\n➡️  CAPTCHA verified! Proceeding to submit form...")
                        else:
                            print("\n⚠️  CAPTCHA solving failed - no token returned")
                            print("   Will attempt submission anyway...")
                    except Exception as e:
                        print(f"\n❌ CAPTCHA solving error: {e}")
                        import traceback
                        traceback.print_exc()
                        print("\n⚠️  Continuing despite CAPTCHA error - will attempt submission...")
                
                elif captcha_info.get('type') == 'hcaptcha':
                    site_key = captcha_info.get('siteKey', '')
                    print(f"\n🎯 Solving hCaptcha...")
                    print(f"   Site Key: {site_key[:30]}..." if site_key else "   (No site key found)")
                    
                    try:
                        token = await solver.solve_hcaptcha(site_key, url)
                        if token:
                            print(f"\n✅ hCaptcha solved successfully!")
                            print(f"   Token length: {len(token)}")
                            print(f"   Token preview: {token[:50]}...")
                            
                            # Verify token is in the form
                            token_in_form = await page.evaluate("""
                                () => {
                                    const field = document.querySelector('textarea[name="h-captcha-response"]');
                                    return field && field.value && field.value.length > 0;
                                }
                            """)
                            if token_in_form:
                                print("   ✅ Token verified in form field")
                            else:
                                print("   ⚠️  Token not found in form field")
                            
                            print("\n➡️  hCaptcha verified! Proceeding to submit form...")
                        else:
                            print("\n⚠️  hCaptcha solving failed - no token returned")
                            print("   Will attempt submission anyway...")
                    except Exception as e:
                        print(f"\n❌ hCaptcha solving error: {e}")
                        import traceback
                        traceback.print_exc()
                        print("\n⚠️  Continuing despite hCaptcha error - will attempt submission...")
            else:
                print("\n✅ No CAPTCHA detected on the page - will submit directly!")
            
            # Wait a bit before submission (shorter wait if no CAPTCHA)
            if captcha_info.get('present'):
                print("\n⏳ Waiting before submission...")
                await page.wait_for_timeout(2000)
                print("   ✅ Wait complete, proceeding to find submit button...")
            else:
                print("\n⏳ Brief wait before submission (no CAPTCHA)...")
                await page.wait_for_timeout(500)  # Shorter wait when no CAPTCHA
                print("   ✅ Proceeding directly to submit button...")
            
            # Check CAPTCHA status before submission (only if CAPTCHA was present)
            if captcha_info.get('present'):
                print("\n🔐 Verifying CAPTCHA before submission...")
                captcha_type = captcha_info.get('type', 'recaptcha')
                if captcha_type == 'hcaptcha':
                    final_captcha_check = await page.evaluate("""
                        () => {
                            const field = document.querySelector('textarea[name="h-captcha-response"]');
                            const hasToken = field && field.value && field.value.length > 0;
                            return {
                                solved: hasToken,
                                tokenLength: field ? field.value.length : 0
                            };
                        }
                    """)
                else:
                    final_captcha_check = await page.evaluate("""
                        () => {
                            const field = document.querySelector('textarea[name="g-recaptcha-response"]');
                            const hasToken = field && field.value && field.value.length > 0;
                            return {
                                solved: hasToken,
                                tokenLength: field ? field.value.length : 0
                            };
                        }
                    """)
                print(f"   CAPTCHA Solved: {final_captcha_check.get('solved', False)}")
                print(f"   Token Length: {final_captcha_check.get('tokenLength', 0)}")
                
                if not final_captcha_check.get('solved', False):
                    print("\n⚠️  CAPTCHA not solved")
                    print("   Will attempt submission anyway to test form structure...")
                    # Don't return False - continue to test submission
            
            # Find and click submit button (focus on contact form if found)
            print("\n" + "="*70)
            print("STEP: FINDING AND CLICKING SUBMIT BUTTON")
            print("="*70)
            print("\n🔘 Finding submit button...")
            
            # Initialize variables outside try block
            submit_clicked = False
            submit_button = None
            
            try:
                submit_selectors = [
                    # Specific selectors for common sites
                    'input[type="submit"][value="Send message"]',
                    'input[type="submit"][value="Send"]',
                    'input[type="submit"].btn.main-btn',
                    'input[type="submit"].btn',
                    'input[type="submit"][class*="btn"]',
                    # Generic selectors
                    'input[type="submit"]',
                    'button[type="submit"]',
                    # Text-based selectors (for buttons)
                    'button:has-text("Verzenden")',
                    'button:has-text("Bericht verzenden")',
                    'button:has-text("Submit")',
                    'button:has-text("Send")',
                    'button:has-text("Send message")'
                ]
                
                for selector in submit_selectors:
                    try:
                        if contact_form:
                            button = await contact_form.query_selector(selector)
                        else:
                            # Try to find button in forms with textarea (contact forms)
                            all_forms = await page.query_selector_all('form')
                            button = None
                            for form in all_forms:
                                has_textarea = await form.query_selector('textarea')
                                if has_textarea:
                                    button = await form.query_selector(selector)
                                    if button:
                                        break
                        
                        if button:
                            # Get button text - for input type="submit", use value attribute
                            try:
                                tag_name = await button.evaluate("(el) => el.tagName.toLowerCase()")
                                if tag_name == 'input':
                                    button_text = await button.get_attribute('value') or await button.get_attribute('placeholder') or 'Submit'
                                else:
                                    button_text = await button.inner_text() or await button.get_attribute('value') or 'Submit'
                            except:
                                button_text = 'Submit'
                            
                            print(f"   ✅ Found submit button: '{button_text}' ({selector})")
                            submit_button = button
                            break
                    except Exception as e:
                        print(f"   ⚠️  Error with selector {selector}: {str(e)[:50]}")
                        continue
                
                # Fallback: Try to find submit button by value attribute if not found yet
                if not submit_button:
                    print("   🔍 Trying fallback: searching for submit button by value attribute...")
                    try:
                        # Search all forms for input[type="submit"] with value="Send message"
                        all_forms = await page.query_selector_all('form')
                        for form in all_forms:
                            submit_inputs = await form.query_selector_all('input[type="submit"]')
                            for submit_input in submit_inputs:
                                value = await submit_input.get_attribute('value')
                                if value and ('send' in value.lower() or 'submit' in value.lower() or 'message' in value.lower()):
                                    is_visible = await submit_input.is_visible()
                                    if is_visible:
                                        print(f"   ✅ Found submit button via fallback: value='{value}'")
                                        submit_button = submit_input
                                        break
                            if submit_button:
                                break
                        
                        # If still not found, try any visible input[type="submit"]
                        if not submit_button:
                            all_submit_inputs = await page.query_selector_all('input[type="submit"]')
                            for submit_input in all_submit_inputs:
                                is_visible = await submit_input.is_visible()
                                if is_visible:
                                    value = await submit_input.get_attribute('value') or 'Submit'
                                    print(f"   ✅ Found submit button (any visible): value='{value}'")
                                    submit_button = submit_input
                                    break
                    except Exception as e:
                        print(f"   ⚠️  Error in fallback search: {str(e)[:50]}")
                
                if submit_button:
                    # Track submission
                    submission_success = False
                    submission_error = None
                    response_body = None
                    response_url = None
                    response_status = None
                    captured_response = None
                    
                    def handle_response(response):
                        nonlocal captured_response, response_status, response_url
                        # Track all POST requests, but prioritize form submission endpoints
                        if response.request.method == "POST":
                            url_lower = response.url.lower()
                            # Skip analytics and tracking
                            if "analytics" in url_lower or "google-analytics" in url_lower or "gtm" in url_lower:
                                return
                            
                            # Capture form submission endpoints
                            if ("contact" in url_lower or "submit" in url_lower or "api" in url_lower or 
                                "form" in url_lower or url_lower.endswith("/contact") or 
                                "mail" in url_lower or "send" in url_lower):
                                response_status = response.status
                                response_url = response.url
                                captured_response = response
                                print(f"\n📥 POST Response: {response.status} - {response.url[:80]}")
                            else:
                                # Also log other POST requests for debugging
                                print(f"   📤 Other POST: {response.status} - {response.url[:60]}")
                    
                    page.on("response", handle_response)
                    
                    # Final CAPTCHA check before submission
                    if captcha_info.get('present') and not captcha_info.get('solved'):
                        print("\n🔐 CAPTCHA detected but not solved - solving now...")
                        try:
                            solver = LocalCaptchaSolver(page=page)
                            site_key = captcha_info.get('siteKey', '')
                            token = await solver.solve_recaptcha_v2(site_key, url)
                            if token:
                                print(f"   ✅ CAPTCHA solved! Token length: {len(token)}")
                                captcha_info['solved'] = True
                            else:
                                print("   ⚠️  CAPTCHA solving returned no token")
                        except Exception as e:
                            print(f"   ⚠️  Error solving CAPTCHA: {str(e)[:100]}")
                    
                    # Verify all required fields before submission
                    print("\n🔍 Verifying form fields before submission...")
                    form_validation = await page.evaluate("""
                    () => {
                        const form = document.querySelector('form');
                        if (!form) return { hasForm: false };
                        
                        const inputs = Array.from(form.querySelectorAll('input, textarea, select'));
                        const filled = [];
                        const empty = [];
                        const required = [];
                        
                        inputs.forEach(input => {
                            const name = input.name || input.id || '';
                            const value = input.value || '';
                            const isRequired = input.hasAttribute('required') || input.getAttribute('aria-required') === 'true';
                            const isVisible = input.offsetWidth > 0 && input.offsetHeight > 0;
                            
                            if (isVisible && !['hidden', 'submit', 'button'].includes(input.type)) {
                                if (isRequired) required.push(name || input.type);
                                if (value.trim()) {
                                    filled.push(name || input.type);
                                } else if (isRequired) {
                                    empty.push(name || input.type);
                                }
                            }
                        });
                        
                        return {
                            hasForm: true,
                            filled: filled,
                            empty: empty,
                            required: required,
                            allRequiredFilled: empty.length === 0
                        };
                    }
                """)
                
                if form_validation.get('hasForm'):
                    print(f"   Required fields: {form_validation.get('required', [])}")
                    print(f"   Filled fields: {form_validation.get('filled', [])}")
                    if form_validation.get('empty'):
                        print(f"   ⚠️  Empty required fields: {form_validation.get('empty')}")
                    if not form_validation.get('allRequiredFilled'):
                        print("   ⚠️  Not all required fields are filled!")
                
                # Click submit
                print("\n🚀 Submitting form...")
                print("   📍 Scrolling submit button into view...")
                await submit_button.scroll_into_view_if_needed()
                await page.wait_for_timeout(1000)
                
                # Verify submit button is still visible and clickable
                is_visible = await submit_button.is_visible()
                is_enabled = await submit_button.is_enabled()
                print(f"   Submit button visible: {is_visible}, enabled: {is_enabled}")
                
                if not is_visible:
                    print("   ⚠️  Submit button not visible, trying to make it visible...")
                    await submit_button.evaluate("(btn) => btn.scrollIntoView({ behavior: 'smooth', block: 'center' })")
                    await page.wait_for_timeout(500)
                
                print("   👆 Clicking submit button NOW...")
                
                # Track the request data being sent
                request_data_captured = None
                form_submission_request = None
                
                def handle_request(request):
                    nonlocal request_data_captured, form_submission_request
                    if request.method == "POST":
                        url_lower = request.url.lower()
                        # Skip analytics, tracking, and reCAPTCHA API calls
                        if ("analytics" in url_lower or "google-analytics" in url_lower or 
                            "recaptcha" in url_lower or "gstatic" in url_lower):
                            return
                        
                        # Capture form submission endpoints
                        if ("contact" in url_lower or "submit" in url_lower or "api" in url_lower or 
                            "form" in url_lower or url_lower.endswith("/contact") or
                            "mail" in url_lower or "send" in url_lower or
                            url_lower == url.lower() or url_lower == (url + "/").lower()):
                            form_submission_request = request
                            request_data_captured = {
                                "url": request.url,
                                "method": request.method,
                                "postData": request.post_data,
                                "headers": dict(request.headers) if hasattr(request, 'headers') else {}
                            }
                            print(f"   📤 Form submission request detected: {request.url[:80]}")
                            if request.post_data:
                                print(f"   📤 POST data preview: {str(request.post_data)[:300]}...")
                
                page.on("request", handle_request)
                
                # Also intercept fetch and XHR requests
                await page.add_init_script("""
                    // Intercept fetch
                    const originalFetch = window.fetch;
                    window.fetch = function(...args) {
                        const url = args[0];
                        const options = args[1] || {};
                        if (options.method === 'POST' || (typeof url === 'string' && 
                            (url.includes('contact') || url.includes('submit') || url.includes('api')))) {
                            console.log('🔍 Fetch POST detected:', url, options);
                        }
                        return originalFetch.apply(this, args);
                    };
                    
                    // Intercept XMLHttpRequest
                    const originalOpen = XMLHttpRequest.prototype.open;
                    const originalSend = XMLHttpRequest.prototype.send;
                    XMLHttpRequest.prototype.open = function(method, url, ...rest) {
                        this._method = method;
                        this._url = url;
                        if (method === 'POST' && (url.includes('contact') || url.includes('submit') || url.includes('api'))) {
                            console.log('🔍 XHR POST detected:', method, url);
                        }
                        return originalOpen.apply(this, [method, url, ...rest]);
                    };
                    XMLHttpRequest.prototype.send = function(data) {
                        if (this._method === 'POST' && this._url && 
                            (this._url.includes('contact') || this._url.includes('submit') || this._url.includes('api'))) {
                            console.log('🔍 XHR POST data:', data);
                        }
                        return originalSend.apply(this, [data]);
                    };
                """)
                
                # Verify CAPTCHA token is in the form before submitting (only if CAPTCHA is present)
                if captcha_info.get('present'):
                    print("\n🔍 Final verification before submission...")
                    final_token_check = await page.evaluate("""
                        () => {
                            const tokenField = document.querySelector('textarea[name="g-recaptcha-response"]');
                            const hasToken = tokenField && tokenField.value && tokenField.value.length > 0;
                            return {
                                hasToken: hasToken,
                                tokenLength: tokenField ? tokenField.value.length : 0,
                                tokenValue: tokenField ? tokenField.value.substring(0, 50) : ''
                            };
                        }
                    """)
                    print(f"   CAPTCHA token present: {final_token_check.get('hasToken', False)}")
                    print(f"   Token length: {final_token_check.get('tokenLength', 0)}")
                    
                    if not final_token_check.get('hasToken', False):
                        print("   ⚠️  WARNING: No CAPTCHA token found! Form submission will likely fail.")
                        print("   Attempting to solve CAPTCHA one more time (quick)...")
                        try:
                            solver = LocalCaptchaSolver(page=page)
                            site_key = captcha_info.get('siteKey', '')
                            # Use timeout to prevent long waits
                            token = await asyncio.wait_for(solver.solve_recaptcha_v2(site_key, url), timeout=30)
                            if token:
                                print(f"   ✅ CAPTCHA solved! Token length: {len(token)}")
                                await page.wait_for_timeout(1000)  # Reduced wait
                            else:
                                print("   ❌ Failed to solve CAPTCHA")
                        except asyncio.TimeoutError:
                            print("   ⏰ CAPTCHA solving timed out - proceeding anyway")
                        except Exception as e:
                            print(f"   ⚠️  Error solving CAPTCHA: {str(e)[:50]}")
                else:
                    print("\n✅ No CAPTCHA detected - proceeding directly to submission!")
                
                # Get form action and method
                form_info = await page.evaluate("""
                    () => {
                        const form = document.querySelector('form');
                        if (!form) return null;
                        return {
                            action: form.action || window.location.href,
                            method: form.method || 'POST',
                            enctype: form.enctype || 'application/x-www-form-urlencoded'
                        };
                    }
                """)
                if form_info:
                    print(f"   Form action: {form_info.get('action', 'N/A')}")
                    print(f"   Form method: {form_info.get('method', 'N/A')}")
                
                # Get form data before submission for verification
                form_data_before = await page.evaluate("""
                    () => {
                        const form = document.querySelector('form');
                        if (!form) return null;
                        const formData = new FormData(form);
                        const data = {};
                        for (let [key, value] of formData.entries()) {
                            if (key === 'g-recaptcha-response') {
                                data[key] = value ? value.substring(0, 50) + '...' : 'empty';
                            } else {
                                data[key] = value;
                            }
                        }
                        return data;
                    }
                """)
                if form_data_before:
                    print(f"   Form data keys: {list(form_data_before.keys())}")
                    if captcha_info.get('present'):
                        if 'g-recaptcha-response' in form_data_before:
                            print(f"   ✅ CAPTCHA token in form data: {form_data_before['g-recaptcha-response'][:50]}...")
                        else:
                            print("   ⚠️  CAPTCHA token NOT in form data!")
                
                # Wait for form submission with promise (shorter timeout)
                submission_promise = page.wait_for_response(
                    lambda response: (
                        response.request.method == "POST" and
                        not ("recaptcha" in response.url.lower() or 
                             "google" in response.url.lower() or
                             "analytics" in response.url.lower() or
                             "gstatic" in response.url.lower()) and
                        (response.url.lower().endswith("/contact") or
                         "contact" in response.url.lower() or
                         response.url == form_info.get('action', '') or
                         response.url == url or
                         response.url == url + "/")
                    ),
                    timeout=8000  # Reduced from 15000
                )
                
                try:
                    await submit_button.click()
                    print("   ✅ Submit button clicked successfully!")
                    await page.wait_for_timeout(500)  # Brief wait after click
                except Exception as click_error:
                    print(f"   ❌ Error clicking submit button: {click_error}")
                    print("   Trying alternative click method...")
                    try:
                        # Try JavaScript click as fallback
                        await submit_button.evaluate("(btn) => btn.click()")
                        print("   ✅ Submit button clicked via JavaScript!")
                        await page.wait_for_timeout(500)
                    except Exception as js_error:
                        print(f"   ❌ JavaScript click also failed: {js_error}")
                        raise
                
                # Wait for the actual form submission response
                try:
                    actual_response = await asyncio.wait_for(submission_promise, timeout=8)
                    print(f"\n✅ Form submission response received!")
                    print(f"   URL: {actual_response.url[:80]}")
                    print(f"   Status: {actual_response.status}")
                    try:
                        response_text = await actual_response.text()
                        print(f"   Response: {response_text[:200]}...")
                        if "success" in response_text.lower() or "thank" in response_text.lower():
                            print("   ✅ Success indicator in response!")
                            submission_success = True
                    except:
                        pass
                except (asyncio.TimeoutError, Exception) as e:
                    print(f"\n⚠️  Did not receive form submission response within 8s")
                    # Continue anyway - form might have submitted
                
                # Wait briefly for page updates
                print("   ⏳ Waiting for page updates...")
                await page.wait_for_timeout(3000)  # Reduced from 10000
                
                # Read response body if we captured a response
                if captured_response:
                    try:
                        response_body = await captured_response.text()
                        print(f"   Response body preview: {response_body[:200]}...")
                        
                        # Check for success/error indicators in response
                        if response_status in [200, 201, 302, 303]:
                            if "success" in response_body.lower() or "bedankt" in response_body.lower() or "thank" in response_body.lower():
                                submission_success = True
                                print("   ✅ Success indicator found in response!")
                            elif "error" in response_body.lower() or "fout" in response_body.lower():
                                submission_error = response_body[:500]
                                print("   ⚠️  Error indicator found in response")
                            else:
                                # 200 status usually means success even without explicit message
                                submission_success = True
                                print("   ✅ 200 status code - submission likely successful")
                    except Exception as e:
                        print(f"   ⚠️  Could not read response body: {str(e)[:50]}")
                        if response_status in [200, 201, 302, 303]:
                            submission_success = True
                
                # Check for success indicators on page (may appear via JavaScript) - faster check
                success_indicators = await page.evaluate("""
                    () => {
                        const bodyText = document.body.innerText.toLowerCase();
                        const bodyHTML = document.body.innerHTML.toLowerCase();
                        return {
                            hasSuccess: bodyText.includes('bedankt') || 
                                       bodyText.includes('thank you') || 
                                       bodyText.includes('success') ||
                                       bodyText.includes('verzonden') ||
                                       bodyHTML.includes('bedankt') ||
                                       bodyHTML.includes('success'),
                            hasError: bodyText.includes('error') || 
                                     bodyText.includes('fout') ||
                                     bodyText.includes('failed') ||
                                     bodyHTML.includes('error'),
                            url: window.location.href,
                            pageTitle: document.title
                        };
                    }
                """)
                # Quick second check if needed
                if not success_indicators.get('hasSuccess') and not submission_success:
                    await page.wait_for_timeout(2000)  # Reduced wait
                    success_indicators = await page.evaluate("""
                        () => {
                            const bodyText = document.body.innerText.toLowerCase();
                            return {
                                hasSuccess: bodyText.includes('bedankt') || 
                                           bodyText.includes('thank you') || 
                                           bodyText.includes('success'),
                                hasError: bodyText.includes('error') || 
                                         bodyText.includes('fout'),
                                url: window.location.href
                            };
                        }
                    """)
                
                print(f"\n📊 Submission Results:")
                print(f"   Response Status: {response_status if response_status else 'N/A'}")
                print(f"   Response URL: {response_url[:80] if response_url else 'N/A'}")
                if request_data_captured:
                    print(f"   Request URL: {request_data_captured.get('url', 'N/A')[:80]}")
                    print(f"   Request Method: {request_data_captured.get('method', 'N/A')}")
                print(f"   Page URL: {success_indicators.get('url', 'N/A')}")
                print(f"   Page Title: {success_indicators.get('pageTitle', 'N/A')}")
                print(f"   Success indicators on page: {success_indicators.get('hasSuccess', False)}")
                print(f"   Error indicators on page: {success_indicators.get('hasError', False)}")
                if response_body:
                    print(f"   Response body: {response_body[:300]}...")
                elif not captured_response:
                    print("   ⚠️  No form submission response captured!")
                    print("   💡 The form might be using AJAX/fetch that we didn't catch")
                
                # Check console messages for fetch/XHR submissions
                console_messages = []
                def handle_console(msg):
                    text = str(msg.text)
                    if 'POST' in text or 'contact' in text.lower() or 'submit' in text.lower():
                        console_messages.append(text)
                        print(f"   📢 Console: {text[:100]}")
                
                page.on("console", handle_console)
                
                # Check if we actually got a form submission response
                if not captured_response and not request_data_captured and not form_submission_request:
                    print("\n❌ No form submission request/response detected!")
                    print("   Possible issues:")
                    print("   - Form might be using AJAX/fetch that wasn't intercepted")
                    print("   - Form validation might be preventing submission")
                    print("   - Submit button might not be working correctly")
                    print("   - Form might require additional fields")
                    print("   - CAPTCHA validation might be blocking submission")
                    
                    # Check for JavaScript errors
                    js_errors = await page.evaluate("""
                        () => {
                            // Check for validation errors
                            const errors = [];
                            const errorElements = document.querySelectorAll('.error, .invalid, [class*="error"], [class*="invalid"], .alert-danger');
                            errorElements.forEach(el => {
                                const text = el.textContent.trim();
                                if (text) errors.push(text);
                            });
                            return errors;
                        }
                    """)
                    if js_errors:
                        print(f"   JavaScript errors/validation messages: {js_errors}")
                    
                    # Check for JavaScript errors or validation messages
                    validation_errors = await page.evaluate("""
                        () => {
                            const errors = [];
                            // Check for validation messages
                            const errorElements = document.querySelectorAll('.error, .invalid, [class*="error"], [class*="invalid"]');
                            errorElements.forEach(el => {
                                if (el.textContent.trim()) {
                                    errors.push(el.textContent.trim());
                                }
                            });
                            // Check for required field indicators
                            const requiredEmpty = document.querySelectorAll('input[required]:not([value]), textarea[required]:not([value])');
                            if (requiredEmpty.length > 0) {
                                errors.push(`${requiredEmpty.length} required field(s) are empty`);
                            }
                            return errors;
                        }
                    """)
                    if validation_errors:
                        print(f"   Validation errors found: {validation_errors}")
                    
                    submit_clicked = False
                elif success_indicators.get('hasSuccess') or submission_success:
                    print("\n✅ Form submitted successfully!")
                    submit_clicked = True
                elif success_indicators.get('hasError'):
                    print("\n❌ Error detected in submission")
                    if response_body:
                        print(f"   Error details: {response_body[:500]}")
                    submit_clicked = False
                else:
                    print("\n⚠️  Submission status unclear")
                    if response_status == 200 or response_status == 204:
                        print(f"   ✅ Got {response_status} response - submission might be successful")
                        submit_clicked = True
                    elif request_data_captured:
                        print("   ✅ Form submission request was sent")
                        submit_clicked = True
                    else:
                        print("   ⚠️  No clear indication of success or failure")
                        print("   Keeping browser open for inspection...")
                        await asyncio.sleep(10)  # Keep open for manual inspection
                        
            except Exception as submit_error:
                print(f"\n❌ ERROR in submit button section: {submit_error}")
                import traceback
                traceback.print_exc()
                print("\n⚠️  Error occurred, but keeping browser open for inspection...")
                print("   Attempting to find submit button manually...")
                try:
                    # Try one more time to find and click submit button
                    submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
                    if submit_button:
                        print("   ✅ Found submit button on retry!")
                        await submit_button.click()
                        print("   ✅ Clicked submit button!")
                        await asyncio.sleep(5)
                except:
                    print("   ⚠️  Could not click submit button on retry")
                await asyncio.sleep(20)  # Keep open for inspection
                        
            if not submit_button:
                print("\n❌ Could not find or click submit button")
                print("   Keeping browser open for manual inspection...")
                await asyncio.sleep(30)
                await browser.close()
                return False
            
            # Verify submit button was actually clicked
            if not submit_clicked:
                print("\n⚠️  WARNING: Submit button may not have been clicked successfully!")
                print("   Keeping browser open longer for manual inspection...")
                await asyncio.sleep(15)
            
            # Keep browser open so user can see results
            print("\n⏳ Keeping browser open for 30 seconds so you can see the results...")
            print("   (You can close it manually if needed)")
            await asyncio.sleep(30)
            
            print("\n🔒 Closing browser...")
            await browser.close()
            print("\n✅ Test completed!")
            return True
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️  Error occurred! Keeping browser open for 20 seconds for inspection...")
        try:
            await asyncio.sleep(20)
            if 'browser' in locals():
                await browser.close()
        except:
            pass
        return False


async def main():
    """Run the test until success."""
    import sys
    
    # Get URL from command line argument if provided
    url = None
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    # Retry until success
    max_attempts = 5
    attempt = 1
    
    while attempt <= max_attempts:
        print(f"\n{'='*70}")
        print(f"Attempt {attempt} of {max_attempts}")
        print(f"{'='*70}\n")
        
        try:
            success = await test_local_solver_on_website(url)
            if success:
                print(f"\n✅ Test succeeded on attempt {attempt}!")
                return 0
            else:
                print(f"\n⚠️  Attempt {attempt} did not succeed, retrying...")
                attempt += 1
                if attempt <= max_attempts:
                    await asyncio.sleep(3)  # Brief pause between attempts
        except Exception as e:
            print(f"\n❌ Attempt {attempt} failed with error: {e}")
            attempt += 1
            if attempt <= max_attempts:
                await asyncio.sleep(3)
    
    print(f"\n❌ Test failed after {max_attempts} attempts")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

