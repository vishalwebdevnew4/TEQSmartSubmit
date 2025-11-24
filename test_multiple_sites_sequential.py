#!/usr/bin/env python3
"""
Sequential Multi-Site reCAPTCHA Audio Challenge Solver
- Tests 5 different sites one at a time (single tab)
- Fills forms, solves CAPTCHA, submits
- Continues until all sites succeed
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json
import random
import time

sys.path.insert(0, str(Path(__file__).parent / "automation"))

from playwright.async_api import async_playwright
from captcha_solver import UltimateLocalCaptchaSolver
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def random_delay(min_seconds=1.0, max_seconds=3.0):
    """Random delay to simulate human behavior."""
    return random.uniform(min_seconds, max_seconds)


async def human_type(page, selector, text, delay_range=(0.05, 0.2)):
    """Type text with human-like delays between keystrokes."""
    field = await page.query_selector(selector)
    if field:
        await field.click()
        await asyncio.sleep(random_delay(0.2, 0.5))
        
        for char in text:
            await field.type(char, delay=random.uniform(*delay_range))
            if random.random() < 0.1:  # 10% chance of longer pause
                await asyncio.sleep(random_delay(0.3, 0.8))
        
        await asyncio.sleep(random_delay(0.2, 0.5))


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


async def test_single_site(site_num: int, url: str, headless: bool = False):
    """
    Test a single site: fill form, solve CAPTCHA, submit.
    
    Returns:
        dict with results
    """
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
            print(f"🌐 SITE {site_num}/5: {url}")
            print(f"{'='*80}\n")
            
            # Navigate
            print(f"[Site {site_num}] ⏳ Navigating...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random_delay(2, 4))
            
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
            
            # Fill form fields
            print(f"[Site {site_num}] 📝 Filling form fields...")
            form_data = {
                'name': f'Test User {site_num}',
                'email': f'test{site_num}@example.com',
                'phone': f'555-{1000 + site_num}-4567',
                'message': f'This is automated test submission #{site_num} from sequential CAPTCHA solver.',
            }
            
            fields_filled = 0
            
            # Fill name
            name_selectors = ['input[name="name"]', 'input[id*="name"]', 'input[type="text"]:first-of-type']
            for selector in name_selectors:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await human_type(page, selector, form_data['name'])
                        fields_filled += 1
                        await asyncio.sleep(random_delay(0.5, 1.0))
                        break
                except:
                    continue
            
            # Fill email
            email_selectors = ['input[name="email"]', 'input[type="email"]', 'input[id*="email"]']
            for selector in email_selectors:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await human_type(page, selector, form_data['email'])
                        fields_filled += 1
                        await asyncio.sleep(random_delay(0.5, 1.0))
                        break
                except:
                    continue
            
            # Fill phone
            phone_selectors = ['input[name="phone"]', 'input[type="tel"]', 'input[id*="phone"]']
            for selector in phone_selectors:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await human_type(page, selector, form_data['phone'])
                        fields_filled += 1
                        await asyncio.sleep(random_delay(0.5, 1.0))
                        break
                except:
                    continue
            
            # Fill message
            message_selectors = ['textarea[name="message"]', 'textarea[name="comment"]', 'textarea']
            for selector in message_selectors:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await human_type(page, selector, form_data['message'], delay_range=(0.08, 0.25))
                        fields_filled += 1
                        await asyncio.sleep(random_delay(1, 2))
                        break
                except:
                    continue
            
            result['fields_filled'] = fields_filled
            print(f"[Site {site_num}] ✅ Filled {fields_filled} fields")
            
            # Wait before CAPTCHA
            await asyncio.sleep(random_delay(2, 4))
            
            # Get site key
            site_key = await page.evaluate("""
                () => {
                    const recaptchaDiv = document.querySelector('.g-recaptcha, [data-sitekey]');
                    return recaptchaDiv ? recaptchaDiv.getAttribute('data-sitekey') : null;
                }
            """)
            
            # Solve reCAPTCHA
            print(f"[Site {site_num}] 🔐 Solving CAPTCHA...")
            solver = UltimateLocalCaptchaSolver(page=page)
            captcha_result = await solver.solve_recaptcha_v2(
                site_key=site_key or "",
                page_url=url
            )
            
            if captcha_result.get("success"):
                result['captcha_solved'] = True
                print(f"[Site {site_num}] ✅ CAPTCHA solved!")
                
                # Submit form
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Send")',
                    'button:has-text("Verzenden")'
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_btn = await page.query_selector(selector)
                        if submit_btn:
                            is_visible = await submit_btn.is_visible()
                            if is_visible:
                                await submit_btn.click()
                                result['form_submitted'] = True
                                print(f"[Site {site_num}] ✅ Form submitted!")
                                await asyncio.sleep(random_delay(3, 5))
                                break
                    except:
                        continue
                
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


async def test_all_sites_until_success(sites: list, headless: bool = False, max_retries: int = 3):
    """
    Test all sites sequentially until all succeed.
    
    Args:
        sites: List of URLs to test
        headless: Whether to run in headless mode
        max_retries: Maximum retries per site
    """
    print("=" * 80)
    print("🌐 SEQUENTIAL MULTI-SITE RECAPTCHA SOLVER")
    print("=" * 80)
    print(f"\n📍 Sites to test: {len(sites)}")
    print(f"🖥️  Headless: {headless}")
    print(f"🔄 Max retries per site: {max_retries}")
    print("\n" + "=" * 80 + "\n")
    
    all_results = []
    successful_sites = set()
    
    for attempt in range(max_retries):
        print(f"\n{'='*80}")
        print(f"🔄 ATTEMPT {attempt + 1}/{max_retries}")
        print(f"{'='*80}\n")
        
        for i, url in enumerate(sites, 1):
            if i in successful_sites:
                print(f"\n[Site {i}] ⏭️  Already successful, skipping...")
                continue
            
            result = await test_single_site(i, url, headless)
            all_results.append(result)
            
            if result['success']:
                successful_sites.add(i)
                print(f"\n[Site {i}] ✅ SUCCESS!")
            else:
                print(f"\n[Site {i}] ❌ FAILED: {result.get('error', 'Unknown error')}")
            
            # Delay between sites
            if i < len(sites):
                delay = random_delay(5, 10)
                print(f"\n⏳ Waiting {delay:.1f}s before next site...")
                await asyncio.sleep(delay)
        
        # Check if all sites succeeded
        if len(successful_sites) == len(sites):
            print(f"\n{'='*80}")
            print("✅ ALL SITES SUCCEEDED!")
            print(f"{'='*80}\n")
            break
        
        if attempt < max_retries - 1:
            delay = random_delay(30, 60)
            print(f"\n⏳ Waiting {delay:.1f}s before retry attempt...")
            await asyncio.sleep(delay)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS SUMMARY")
    print("=" * 80)
    
    for i, url in enumerate(sites, 1):
        site_results = [r for r in all_results if r['site_num'] == i]
        if site_results:
            last_result = site_results[-1]
            status = "✅ SUCCESS" if last_result['success'] else "❌ FAILED"
            print(f"\n[Site {i}] {status}")
            print(f"   URL: {url}")
            print(f"   Duration: {last_result['duration']:.2f}s")
            print(f"   Fields filled: {last_result['fields_filled']}")
            print(f"   CAPTCHA solved: {'Yes' if last_result['captcha_solved'] else 'No'}")
            print(f"   Form submitted: {'Yes' if last_result['form_submitted'] else 'No'}")
            if last_result.get('error'):
                print(f"   Error: {last_result['error']}")
    
    print("\n" + "=" * 80)
    print("📈 STATISTICS")
    print("=" * 80)
    successful_count = len(successful_sites)
    print(f"✅ Successful: {successful_count}/{len(sites)}")
    print(f"❌ Failed: {len(sites) - successful_count}/{len(sites)}")
    total_time = sum(r['duration'] for r in all_results)
    print(f"⏱️  Total time: {total_time:.2f}s")
    print("=" * 80)
    
    # Save results
    results_file = Path(__file__).parent / f"multi_site_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    
    success = await test_all_sites_until_success(sites, headless=False, max_retries=3)
    
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

