#!/usr/bin/env python3
"""
Universal Form Filler with reCAPTCHA Audio Challenge Solver
- Auto-detects and fills ALL form fields with random data
- Handles Google automation detection (refresh & retry)
- Retries reCAPTCHA on timeout
- Works for any website with any form structure
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json
import random
import string
import re

sys.path.insert(0, str(Path(__file__).parent / "automation"))

from playwright.async_api import async_playwright
from captcha_solver import UltimateLocalCaptchaSolver
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def random_delay(min_seconds=1.0, max_seconds=3.0):
    """Random delay to simulate human behavior."""
    return random.uniform(min_seconds, max_seconds)


def generate_random_data(field_type: str, field_name: str = ""):
    """Generate random data based on field type and name."""
    name_lower = field_name.lower()
    
    # Email fields
    if field_type == "email" or "email" in name_lower or "mail" in name_lower:
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com"]
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@{random.choice(domains)}"
    
    # Phone fields
    if field_type == "tel" or "phone" in name_lower or "mobile" in name_lower or "cell" in name_lower:
        formats = [
            f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            f"({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
        ]
        return random.choice(formats)
    
    # URL/Website fields
    if field_type == "url" or "url" in name_lower or "website" in name_lower or "site" in name_lower:
        domains = ["example.com", "test.com", "demo.com", "sample.org"]
        return f"https://www.{random.choice(domains)}"
    
    # Date fields
    if field_type == "date" or "date" in name_lower or "birth" in name_lower:
        year = random.randint(1980, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}-{month:02d}-{day:02d}"
    
    # Number fields
    if field_type == "number" or "number" in name_lower or "age" in name_lower or "zip" in name_lower:
        if "age" in name_lower:
            return str(random.randint(18, 65))
        elif "zip" in name_lower or "postal" in name_lower:
            return str(random.randint(10000, 99999))
        else:
            return str(random.randint(1, 1000))
    
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
    
    # Address fields
    if "address" in name_lower or "street" in name_lower:
        streets = ["Main St", "Oak Ave", "Park Blvd", "First St", "Second Ave"]
        return f"{random.randint(100, 9999)} {random.choice(streets)}"
    
    # City fields
    if "city" in name_lower:
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]
        return random.choice(cities)
    
    # State fields
    if "state" in name_lower:
        states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA"]
        return random.choice(states)
    
    # Country fields
    if "country" in name_lower:
        countries = ["United States", "USA", "US", "Canada", "United Kingdom"]
        return random.choice(countries)
    
    # Subject fields
    if "subject" in name_lower or "title" in name_lower:
        subjects = ["Inquiry", "Question", "Support Request", "General Information", "Feedback"]
        return random.choice(subjects)
    
    # Message/Comment fields
    if "message" in name_lower or "comment" in name_lower or "description" in name_lower or "notes" in name_lower:
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


async def human_type(page, field, text, delay_range=(0.05, 0.2)):
    """Type text with human-like delays."""
    await field.click()
    await asyncio.sleep(random_delay(0.2, 0.5))
    
    for char in text:
        await field.type(char, delay=random.uniform(*delay_range))
        if random.random() < 0.1:
            await asyncio.sleep(random_delay(0.3, 0.8))
    
    await asyncio.sleep(random_delay(0.2, 0.5))


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
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
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
                await asyncio.sleep(random_delay(5, 10))  # Wait longer after refresh
                
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


async def test_single_site(site_num: int, url: str, headless: bool = False):
    """Test a single site with universal form filling."""
    start_time = datetime.now()
    result = {
        'site_num': site_num,
        'url': url,
        'success': False,
        'error': None,
        'duration': 0,
        'fields_filled': 0,
        'captcha_solved': False,
        'form_submitted': False
    }
    
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
            print(f"\n{'='*80}")
            print(f"🌐 SITE {site_num}: {url}")
            print(f"{'='*80}\n")
            
            # Navigate with retry on automation detection
            print(f"[Site {site_num}] ⏳ Navigating...")
            for nav_attempt in range(3):
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(random_delay(2, 4))
                
                # Check for automation detection immediately
                if await check_automation_detected(page):
                    if nav_attempt < 2:
                        print(f"[Site {site_num}] ⚠️  Google error detected on page load, refreshing...")
                        await asyncio.sleep(random_delay(5, 10))
                        continue
                    else:
                        print(f"[Site {site_num}] ⚠️  Google error persists after 3 attempts")
                else:
                    break
            
            # Simulate reading
            await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
            await asyncio.sleep(random_delay(1, 2))
            print(f"[Site {site_num}] ✅ Page loaded")
            
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
                        print(f"[Site {site_num}] ✅ Cookie banner handled")
            
            # Fill ALL form fields automatically
            fields_filled = await fill_all_form_fields(page)
            result['fields_filled'] = fields_filled
            
            if fields_filled == 0:
                print(f"[Site {site_num}] ⚠️  No form fields found")
            
            # Wait before CAPTCHA
            await asyncio.sleep(random_delay(2, 4))
            
            # Solve reCAPTCHA with retry
            print(f"[Site {site_num}] 🔐 Solving CAPTCHA...")
            captcha_result = await solve_captcha_with_retry(page, url, max_retries=3)
            
            if captcha_result.get("success"):
                result['captcha_solved'] = True
                print(f"[Site {site_num}] ✅ CAPTCHA solved!")
                
                # Submit form
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
                for selector in submit_selectors:
                    try:
                        submit_btn = await page.query_selector(selector)
                        if submit_btn:
                            is_visible = await submit_btn.is_visible()
                            if is_visible:
                                await submit_btn.click()
                                result['form_submitted'] = True
                                submitted = True
                                print(f"[Site {site_num}] ✅ Form submitted!")
                                await asyncio.sleep(random_delay(3, 5))
                                break
                    except:
                        continue
                
                if not submitted:
                    print(f"[Site {site_num}] ⚠️  Could not find submit button")
                
                result['success'] = True
            else:
                result['error'] = captcha_result.get("error", "CAPTCHA solving failed")
                print(f"[Site {site_num}] ❌ CAPTCHA failed: {result['error']}")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"[Site {site_num}] ❌ Error: {e}")
        finally:
            end_time = datetime.now()
            result['duration'] = (end_time - start_time).total_seconds()
            await browser.close()
    
    return result


async def test_all_sites(sites: list, headless: bool = False):
    """Test all sites sequentially."""
    print("=" * 80)
    print("🌐 UNIVERSAL MULTI-SITE RECAPTCHA SOLVER")
    print("=" * 80)
    print(f"\n📍 Sites to test: {len(sites)}")
    print(f"🖥️  Headless: {headless}")
    print(f"🔧 Features:")
    print(f"   - Auto-detects and fills ALL form fields")
    print(f"   - Handles Google automation detection (refresh & retry)")
    print(f"   - Retries CAPTCHA on timeout")
    print(f"   - Works for any website structure")
    print("\n" + "=" * 80 + "\n")
    
    all_results = []
    
    for i, url in enumerate(sites, 1):
        result = await test_single_site(i, url, headless)
        all_results.append(result)
        
        if result['success']:
            print(f"\n[Site {i}] ✅ SUCCESS!")
        else:
            print(f"\n[Site {i}] ❌ FAILED: {result.get('error', 'Unknown error')}")
        
        # Delay between sites
        if i < len(sites):
            delay = random_delay(5, 10)
            print(f"\n⏳ Waiting {delay:.1f}s before next site...")
            await asyncio.sleep(delay)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS SUMMARY")
    print("=" * 80)
    
    for i, (url, result) in enumerate(zip(sites, all_results), 1):
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"\n[Site {i}] {status}")
        print(f"   URL: {url}")
        print(f"   Duration: {result['duration']:.2f}s")
        print(f"   Fields filled: {result['fields_filled']}")
        print(f"   CAPTCHA solved: {'Yes' if result['captcha_solved'] else 'No'}")
        print(f"   Form submitted: {'Yes' if result['form_submitted'] else 'No'}")
        if result.get('error'):
            print(f"   Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print("📈 STATISTICS")
    print("=" * 80)
    successful_count = sum(1 for r in all_results if r['success'])
    print(f"✅ Successful: {successful_count}/{len(sites)}")
    print(f"❌ Failed: {len(sites) - successful_count}/{len(sites)}")
    total_time = sum(r['duration'] for r in all_results)
    print(f"⏱️  Total time: {total_time:.2f}s")
    print("=" * 80)
    
    # Save results
    results_file = Path(__file__).parent / f"universal_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'sites': sites,
            'successful_count': successful_count,
            'total_sites': len(sites),
            'results': all_results
        }, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return successful_count == len(sites)


async def main():
    """Main function."""
    sites = [
        "https://interiordesign.xcelanceweb.com/contact",
        "https://petpointmedia.com/contact-us/",
        "https://www.seoily.com/contact-us",
        "https://360digiexpertz.com/contact-us/",
        "https://teqtopaustralia.xcelanceweb.com/contact"
    ]
    
    success = await test_all_sites(sites, headless=False)
    
    if success:
        print("\n✅ ALL SITES TESTED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n⚠️  Some sites failed")
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

