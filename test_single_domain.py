#!/usr/bin/env python3
"""
Single Domain Test - Universal Form Filler with reCAPTCHA
Tests one domain with all features:
- Auto-detects and fills ALL form fields
- Handles Google automation detection (refresh & retry)
- Retries CAPTCHA on timeout
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json
import random
import string

sys.path.insert(0, str(Path(__file__).parent / "automation"))

from playwright.async_api import async_playwright
from captcha_solver import UltimateLocalCaptchaSolver
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def random_delay(min_seconds=1.0, max_seconds=3.0):
    """Random delay to simulate human behavior."""
    return random.uniform(min_seconds, max_seconds)


async def human_type(page, field, text, delay_range=(0.05, 0.2)):
    """Type text with human-like delays."""
    await field.click()
    await asyncio.sleep(random_delay(0.2, 0.5))
    
    for char in text:
        await field.type(char, delay=random.uniform(*delay_range))
        if random.random() < 0.1:
            await asyncio.sleep(random_delay(0.3, 0.8))
    
    await asyncio.sleep(random_delay(0.2, 0.5))


def generate_random_data(field_type: str, field_name: str = ""):
    """Generate random data based on field type and name."""
    name_lower = field_name.lower()
    
    # Email fields
    if field_type == "email" or "email" in name_lower or "mail" in name_lower:
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com"]
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@{random.choice(domains)}"
    
    # Phone fields
    if field_type == "tel" or "phone" in name_lower or "mobile" in name_lower or "cell" in name_lower or "number" in name_lower:
        formats = [
            f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            f"({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
        ]
        return random.choice(formats)
    
    # Name fields
    if "name" in name_lower or "first" in name_lower or "last" in name_lower:
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "James", "Emma"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        if "first" in name_lower or (name_lower and "last" not in name_lower and "name" in name_lower):
            return random.choice(first_names)
        elif "last" in name_lower:
            return random.choice(last_names)
        else:
            return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    # Company/Organization fields
    if "company" in name_lower or "organization" in name_lower or "org" in name_lower or "business" in name_lower:
        companies = ["Tech Solutions", "Digital Services", "Global Corp", "Innovation Labs", "Smart Systems"]
        return f"{random.choice(['ABC', 'XYZ', 'Tech', 'Digital', 'Global'])} {random.choice(companies)}"
    
    # Message/Comment fields
    if "message" in name_lower or "comment" in name_lower or "description" in name_lower or "notes" in name_lower or "about" in name_lower or "tell" in name_lower:
        messages = [
            "I would like to know more about your services.",
            "Please contact me regarding your products.",
            "I am interested in learning more.",
            "Thank you for your time and consideration.",
            "Looking forward to hearing from you."
        ]
        return random.choice(messages)
    
    # Default text for text inputs
    if field_type == "text":
        return ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 15)))
    
    # Default for unknown types
    return ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 20)))


async def fill_all_form_fields(page):
    """Auto-detect and fill ALL form fields with appropriate random data."""
    print("   📝 Auto-detecting and filling all form fields...")
    
    fields_info = await page.evaluate("""
        () => {
            const fields = [];
            
            // Get all input fields
            const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="checkbox"]):not([type="radio"])'));
            inputs.forEach(input => {
                if (input.offsetParent !== null) { // Visible
                    fields.push({
                        type: 'input',
                        tag: 'input',
                        fieldType: input.type || 'text',
                        name: input.name || '',
                        id: input.id || '',
                        placeholder: input.placeholder || '',
                        selector: `input[name="${input.name}"], input[id="${input.id}"]`
                    });
                }
            });
            
            // Get all textarea fields
            const textareas = Array.from(document.querySelectorAll('textarea'));
            textareas.forEach(textarea => {
                if (textarea.offsetParent !== null) { // Visible
                    fields.push({
                        type: 'textarea',
                        tag: 'textarea',
                        fieldType: 'textarea',
                        name: textarea.name || '',
                        id: textarea.id || '',
                        placeholder: textarea.placeholder || '',
                        selector: `textarea[name="${textarea.name}"], textarea[id="${textarea.id}"]`
                    });
                }
            });
            
            // Get all select fields
            const selects = Array.from(document.querySelectorAll('select'));
            selects.forEach(select => {
                if (select.offsetParent !== null) { // Visible
                    const options = Array.from(select.options).filter(opt => opt.value && opt.value !== '');
                    if (options.length > 0) {
                        fields.push({
                            type: 'select',
                            tag: 'select',
                            fieldType: 'select',
                            name: select.name || '',
                            id: select.id || '',
                            placeholder: '',
                            selector: `select[name="${select.name}"], select[id="${select.id}"]`,
                            options: options.map(opt => opt.value)
                        });
                    }
                }
            });
            
            return fields;
        }
    """)
    
    fields_filled = 0
    
    for field_info in fields_info:
        try:
            # Generate appropriate data
            field_name = field_info.get('name', '') or field_info.get('id', '') or field_info.get('placeholder', '')
            field_type = field_info.get('fieldType', 'text')
            data = generate_random_data(field_type, field_name)
            
            # Find and fill the field
            selector = field_info.get('selector', '')
            if selector:
                field = await page.query_selector(selector)
                if field:
                    if field_info.get('type') == 'select':
                        # Select a random option
                        options = field_info.get('options', [])
                        if options:
                            await field.select_option(random.choice(options))
                            fields_filled += 1
                            print(f"      ✅ Filled select: {field_name or 'unnamed'} = {random.choice(options)}")
                    else:
                        # Fill input or textarea
                        await human_type(page, field, data)
                        fields_filled += 1
                        field_display = field_name or field_info.get('id', '') or 'unnamed'
                        print(f"      ✅ Filled {field_type}: {field_display} = {data[:30]}...")
                    
                    await asyncio.sleep(random_delay(0.5, 1.0))
        except Exception as e:
            continue
    
    print(f"   ✅ Filled {fields_filled} field(s)")
    return fields_filled


def get_random_user_agent():
    """Get a random realistic user agent."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    return random.choice(user_agents)


async def check_automation_detected(page):
    """Check if Google detected automation or shows error messages."""
    try:
        page_text = await page.evaluate("() => document.body.textContent.toLowerCase()")
        
        automation_indicators = [
            "your computer or network may be sending automated queries",
            "automated queries",
            "try again later",
            "unusual traffic",
            "verify you're not a robot",
            "can't process your request right now",
            "to protect our users",
            "for more details visit our help page",
            "we can't process your request",
            "please try again later"
        ]
        
        for indicator in automation_indicators:
            if indicator in page_text:
                return True
        
        # Also check in iframes (reCAPTCHA iframes)
        try:
            iframes = await page.query_selector_all('iframe')
            for iframe in iframes:
                try:
                    frame = await iframe.content_frame()
                    if frame:
                        iframe_text = await frame.evaluate("() => document.body.textContent.toLowerCase()")
                        for indicator in automation_indicators:
                            if indicator in iframe_text:
                                return True
                except:
                    continue
        except:
            pass
        
        return False
    except:
        return False


async def solve_captcha_with_retry(page, url, max_retries=5):
    """Solve CAPTCHA with retry on timeout or automation detection."""
    for attempt in range(max_retries):
        try:
            # Check for automation detection BEFORE solving
            if await check_automation_detected(page):
                print(f"   ⚠️  Google error detected (attempt {attempt + 1}): 'Try again later' or 'automated queries'")
                print(f"   🔄 Refreshing page and waiting...")
                await page.reload(wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(random_delay(5, 10))
                
                # Re-fill form fields after refresh
                print(f"   📝 Re-filling form fields after refresh...")
                await fill_all_form_fields(page)
                await asyncio.sleep(random_delay(2, 4))
                continue
            
            # Get site key
            site_key = await page.evaluate("""
                () => {
                    const recaptchaDiv = document.querySelector('.g-recaptcha, [data-sitekey]');
                    return recaptchaDiv ? recaptchaDiv.getAttribute('data-sitekey') : null;
                }
            """)
            
            # Check for automation detection again before solving
            if await check_automation_detected(page):
                print(f"   ⚠️  Google error still present (attempt {attempt + 1}), refreshing again...")
                await page.reload(wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(random_delay(5, 10))
                await fill_all_form_fields(page)
                await asyncio.sleep(random_delay(2, 4))
                continue
            
            # Solve reCAPTCHA
            print(f"   🔐 Attempting to solve CAPTCHA (attempt {attempt + 1}/{max_retries})...")
            solver = UltimateLocalCaptchaSolver(page=page)
            result = await solver.solve_recaptcha_v2(
                site_key=site_key or "",
                page_url=url
            )
            
            # Check for automation detection AFTER solving attempt
            if await check_automation_detected(page):
                print(f"   ⚠️  Google error appeared after CAPTCHA attempt (attempt {attempt + 1})")
                print(f"   🔄 Refreshing page and retrying...")
                await page.reload(wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(random_delay(5, 10))
                await fill_all_form_fields(page)
                await asyncio.sleep(random_delay(2, 4))
                continue
            
            if result.get("success"):
                return result
            
            # If failed, check if it's a timeout and retry
            error = result.get("error", "")
            if "timeout" in error.lower() and attempt < max_retries - 1:
                print(f"   ⚠️  CAPTCHA timeout (attempt {attempt + 1}), clicking CAPTCHA again...")
                # Try clicking CAPTCHA again
                anchor_iframe = await page.query_selector('iframe[src*="recaptcha/api2/anchor"]')
                if anchor_iframe:
                    frame = await anchor_iframe.content_frame()
                    if frame:
                        checkbox = await frame.query_selector('#recaptcha-anchor')
                        if checkbox:
                            box = await checkbox.bounding_box()
                            if box:
                                iframe_box = await anchor_iframe.bounding_box()
                                if iframe_box:
                                    abs_x = iframe_box['x'] + box['x'] + box['width']/2
                                    abs_y = iframe_box['y'] + box['y'] + box['height']/2
                                    await page.mouse.click(abs_x, abs_y)
                                    await asyncio.sleep(random_delay(3, 5))
                continue
            
            return result
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"   ⚠️  Error (attempt {attempt + 1}): {str(e)[:50]}")
                await asyncio.sleep(random_delay(2, 4))
                continue
            raise
    
    return {"success": False, "error": "Max retries exceeded"}


async def test_single_domain(url: str, headless: bool = False):
    """Test a single domain with universal form filling."""
    start_time = datetime.now()
    
    print("=" * 80)
    print("🌐 SINGLE DOMAIN TEST - UNIVERSAL FORM SOLVER")
    print("=" * 80)
    print(f"\n📍 URL: {url}")
    print(f"🖥️  Headless: {headless}")
    print(f"🔧 Features:")
    print(f"   - Auto-detects and fills ALL form fields")
    print(f"   - Handles Google automation detection (refresh & retry)")
    print(f"   - Retries CAPTCHA on timeout")
    print("\n" + "=" * 80 + "\n")
    
    async with async_playwright() as p:
        user_agent = get_random_user_agent()
        viewport_width = random.choice([1920, 1366, 1536, 1440])
        viewport_height = random.choice([1080, 768, 864, 900])
        
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': viewport_width, 'height': viewport_height},
            user_agent=user_agent,
            locale='en-US',
            timezone_id='America/New_York',
            permissions=[],
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
        )
        
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        page = await context.new_page()
        
        try:
            # Navigate with retry on automation detection
            print("⏳ Navigating...")
            for nav_attempt in range(3):
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(random_delay(2, 4))
                
                # Check for automation detection immediately
                if await check_automation_detected(page):
                    if nav_attempt < 2:
                        print("⚠️  Google error detected on page load, refreshing...")
                        await asyncio.sleep(random_delay(5, 10))
                        continue
                    else:
                        print("⚠️  Google error persists after 3 attempts")
                else:
                    break
            
            # Simulate reading
            await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
            await asyncio.sleep(random_delay(1, 2))
            print("✅ Page loaded")
            
            # Handle cookie banner and popups
            print("🔍 Checking for popups/banners...")
            
            # Close newsletter/subscribe popups
            popup_closed = False
            popup_selectors = [
                'button[aria-label*="close" i]',
                'button[aria-label*="dismiss" i]',
                'button.close',
                'button[class*="close"]',
                '[class*="popup"] button',
                '[class*="modal"] button',
                '[class*="newsletter"] button',
                '[class*="subscribe"] button',
                '[id*="popup"] button',
                '[id*="modal"] button',
                '[id*="newsletter"] button',
                '[id*="subscribe"] button',
                'button:has-text("×")',
                'button:has-text("✕")',
                'button:has-text("Close")',
                'button:has-text("Dismiss")',
                'button:has-text("No Thanks")',
                'button:has-text("Not Now")',
                'button:has-text("Maybe Later")',
                '.close-button',
                '.popup-close',
                '.modal-close'
            ]
            
            for selector in popup_selectors:
                try:
                    close_btn = await page.query_selector(selector)
                    if close_btn:
                        is_visible = await close_btn.is_visible()
                        if is_visible:
                            box = await close_btn.bounding_box()
                            if box:
                                await page.mouse.move(
                                    box['x'] + box['width']/2,
                                    box['y'] + box['height']/2
                                )
                                await asyncio.sleep(random_delay(0.3, 0.7))
                                await close_btn.click()
                                popup_closed = True
                                print(f"   ✅ Closed popup/banner: {selector}")
                                await asyncio.sleep(random_delay(1, 2))
                                break
                except:
                    continue
            
            # Also try JavaScript to close popups
            if not popup_closed:
                closed = await page.evaluate("""
                    () => {
                        // Find and close popups/modals
                        const closeButtons = Array.from(document.querySelectorAll('button, [role="button"]'));
                        for (const btn of closeButtons) {
                            const text = btn.textContent.toLowerCase();
                            const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                            const className = btn.className.toLowerCase();
                            
                            if ((text.includes('close') || text.includes('×') || text.includes('✕') ||
                                 text.includes('dismiss') || text.includes('no thanks') ||
                                 ariaLabel.includes('close') || ariaLabel.includes('dismiss') ||
                                 className.includes('close')) &&
                                btn.offsetParent !== null) {
                                btn.click();
                                return true;
                            }
                        }
                        
                        // Try to find and close by class/id
                        const popups = document.querySelectorAll('[class*="popup"], [class*="modal"], [class*="newsletter"], [id*="popup"], [id*="modal"]');
                        for (const popup of popups) {
                            const style = window.getComputedStyle(popup);
                            if (style.display !== 'none' && style.visibility !== 'hidden') {
                                const closeBtn = popup.querySelector('button, [class*="close"], [aria-label*="close" i]');
                                if (closeBtn) {
                                    closeBtn.click();
                                    return true;
                                }
                            }
                        }
                        
                        return false;
                    }
                """)
                if closed:
                    print("   ✅ Closed popup/banner via JavaScript")
                    await asyncio.sleep(random_delay(1, 2))
                    popup_closed = True
            
            # Handle cookie banner
            cookie_clicked = await page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    for (const btn of buttons) {
                        const text = btn.textContent.toLowerCase();
                        if ((text.includes('accept') || text.includes('accepteren') || 
                             text.includes('agree') || text.includes('ok')) &&
                            btn.offsetParent !== null) {
                            return true;
                        }
                    }
                    return false;
                }
            """)
            
            if cookie_clicked:
                button = await page.query_selector('button:has-text("Accept"), button:has-text("Accepteren")')
                if button:
                    box = await button.bounding_box()
                    if box:
                        await page.mouse.move(
                            box['x'] + box['width']/2 + random.randint(-5, 5),
                            box['y'] + box['height']/2 + random.randint(-5, 5)
                        )
                        await asyncio.sleep(random_delay(0.5, 1.5))
                        await button.click()
                        await asyncio.sleep(random_delay(1, 2))
                        print("✅ Cookie banner handled")
            
            # Wait a bit after handling popups
            if popup_closed or cookie_clicked:
                await asyncio.sleep(random_delay(1, 2))
            
            # Fill ALL form fields automatically
            fields_filled = await fill_all_form_fields(page)
            
            if fields_filled == 0:
                print("⚠️  No form fields found")
            
            # Wait before CAPTCHA
            await asyncio.sleep(random_delay(2, 4))
            
            # Solve reCAPTCHA with retry
            print("\n🔐 Solving CAPTCHA...")
            captcha_result = await solve_captcha_with_retry(page, url, max_retries=5)
            
            if captcha_result.get("success"):
                print("✅ CAPTCHA solved!")
                
                # Wait a bit before submitting
                await asyncio.sleep(random_delay(1, 2))
                
                # Submit form
                print("\n📤 Submitting form...")
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Send")',
                    'button:has-text("Verzenden")',
                    'button:has-text("Send Message")',
                    'button:has-text("Submit Form")',
                    'form button:last-of-type'
                ]
                
                submitted = False
                submit_button = None
                
                for selector in submit_selectors:
                    try:
                        submit_btn = await page.query_selector(selector)
                        if submit_btn:
                            is_visible = await submit_btn.is_visible()
                            if is_visible:
                                submit_button = submit_btn
                                # Scroll to button
                                await submit_btn.scroll_into_view_if_needed()
                                await asyncio.sleep(random_delay(0.5, 1.0))
                                
                                # Click submit button
                                await submit_btn.click()
                                submitted = True
                                print(f"   ✅ Clicked submit button: {selector}")
                                break
                    except:
                        continue
                
                if not submitted:
                    # Try JavaScript submit as fallback
                    try:
                        submitted = await page.evaluate("""
                            () => {
                                const forms = document.querySelectorAll('form');
                                for (const form of forms) {
                                    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                                    if (submitBtn && submitBtn.offsetParent !== null) {
                                        submitBtn.click();
                                        return true;
                                    }
                                }
                                return false;
                            }
                        """)
                        if submitted:
                            print("   ✅ Form submitted via JavaScript")
                    except:
                        pass
                
                if not submitted:
                    print("   ⚠️  Could not find or click submit button")
                else:
                    # Track network requests to verify actual submission
                    print("   ⏳ Waiting for form submission to process...")
                    
                    # Set up request tracking
                    form_submission_detected = False
                    form_post_request = None
                    
                    def handle_request(request):
                        nonlocal form_submission_detected, form_post_request
                        if request.method == "POST":
                            url_lower = request.url.lower()
                            # Exclude analytics/tracking
                            excluded = ['google-analytics', 'googletagmanager', 'google.com', 'pagead', 
                                       'clarity', 'facebook', 'twitter', 'doubleclick', 'analytics', 'gtm']
                            is_excluded = any(ex in url_lower for ex in excluded)
                            
                            if not is_excluded:
                                try:
                                    post_data = request.post_data
                                    if post_data:
                                        # Check if it contains form fields
                                        if any(field in post_data.lower() for field in ['name=', 'email=', 'message=', 'phone=', '_token=']):
                                            form_submission_detected = True
                                            form_post_request = {
                                                'url': request.url,
                                                'has_data': True
                                            }
                                            print(f"   📤 Form POST request detected: {request.url[:80]}")
                                except:
                                    pass
                    
                    page.on("request", handle_request)
                    
                    # Wait longer for submission to process
                    await asyncio.sleep(random_delay(8, 12))
                    
                    # Remove listener
                    page.remove_listener("request", handle_request)
                    
                    # Verify submission was successful
                    print("   🔍 Verifying form submission...")
                    
                    # Check 1: Look for success messages
                    success_found = await page.evaluate("""
                        () => {
                            const bodyText = document.body.textContent.toLowerCase();
                            const successIndicators = [
                                'thank you', 'bedankt', 'success', 'verzonden',
                                'message sent', 'form submitted', 'submitted successfully',
                                'we received', 'we\'ll be in touch', 'contact you soon',
                                'submission received', 'form received'
                            ];
                            
                            for (const indicator of successIndicators) {
                                if (bodyText.includes(indicator)) {
                                    return true;
                                }
                            }
                            return false;
                        }
                    """)
                    
                    # Check 2: Check if form fields are cleared (indicates submission)
                    form_cleared = await page.evaluate("""
                        () => {
                            const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), textarea'));
                            let filledCount = 0;
                            let emptyCount = 0;
                            
                            for (const input of inputs) {
                                if (input.value && input.value.trim().length > 0) {
                                    filledCount++;
                                } else {
                                    emptyCount++;
                                }
                            }
                            
                            // If most fields are empty, form was likely submitted
                            return emptyCount > filledCount && inputs.length > 0;
                        }
                    """)
                    
                    # Check 3: Check URL change (some forms redirect after submission)
                    current_url = page.url
                    url_changed = current_url != url and ('success' in current_url.lower() or 'thank' in current_url.lower())
                    
                    # Check 4: Look for error messages
                    error_found = await page.evaluate("""
                        () => {
                            const bodyText = document.body.textContent.toLowerCase();
                            const errorIndicators = [
                                'error', 'failed', 'fout', 'mislukt',
                                'please try again', 'something went wrong',
                                'invalid', 'required field', 'missing'
                            ];
                            
                            for (const indicator of errorIndicators) {
                                if (bodyText.includes(indicator)) {
                                    return true;
                                }
                            }
                            return false;
                        }
                    """)
                    
                    # Check 5: Check if submit button is disabled (indicates processing)
                    submit_disabled = False
                    if submit_button:
                        try:
                            submit_disabled = await submit_button.is_disabled()
                        except:
                            pass
                    
                    print(f"   📊 Verification results:")
                    print(f"      Success message found: {'Yes' if success_found else 'No'}")
                    print(f"      Form fields cleared: {'Yes' if form_cleared else 'No'}")
                    print(f"      URL changed: {'Yes' if url_changed else 'No'}")
                    print(f"      Error message found: {'Yes' if error_found else 'No'}")
                    print(f"      Submit button disabled: {'Yes' if submit_disabled else 'No'}")
                    
                    # Determine if submission was actually successful
                    submission_verified = success_found or (form_cleared and not error_found) or url_changed
                    
                    if submission_verified:
                        print("   ✅ Form submission VERIFIED!")
                    elif error_found:
                        print("   ⚠️  Error detected - submission may have failed")
                    else:
                        print("   ⚠️  Could not verify submission - may need manual check")
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print("\n" + "=" * 80)
                if submitted:
                    print("✅ FORM SUBMITTED!")
                else:
                    print("⚠️  SUBMISSION ATTEMPTED")
                print("=" * 80)
                print(f"Duration: {duration:.2f}s")
                print(f"Fields filled: {fields_filled}")
                print(f"CAPTCHA solved: Yes")
                print(f"Submit button clicked: {'Yes' if submitted else 'No'}")
                if submitted:
                    print(f"Submission verified: {'Yes' if submission_verified else 'Uncertain'}")
                print("=" * 80)
                
                print("\n⏸️  Browser open for 30 seconds for inspection...")
                await asyncio.sleep(30)
                return submitted and submission_verified
            else:
                error = captcha_result.get("error", "CAPTCHA solving failed")
                print(f"\n❌ CAPTCHA failed: {error}")
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print("\n" + "=" * 80)
                print("❌ FAILED")
                print("=" * 80)
                print(f"Duration: {duration:.2f}s")
                print(f"Fields filled: {fields_filled}")
                print(f"Error: {error}")
                print("=" * 80)
                
                print("\n⏸️  Browser open for 30 seconds...")
                await asyncio.sleep(30)
                return False
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="test_error.png")
            return False
        finally:
            await browser.close()


async def main():
    """Main function."""
    url = "https://petpointmedia.com/contact-us/"
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    success = await test_single_domain(url, headless=False)
    
    if success:
        print("\n✅ TEST SUCCESSFUL!")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

