#!/usr/bin/env python3
"""
Parallel reCAPTCHA Audio Challenge Solver
- Fills 5 forms simultaneously
- Each instance solves CAPTCHA independently
- Tracks results for all instances
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

logging.basicConfig(level=logging.WARNING)  # Reduce logging noise for parallel execution
logger = logging.getLogger(__name__)


def random_delay(min_seconds=0.5, max_seconds=2.0):
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
            # Occasionally add a longer pause (like human thinking)
            if random.random() < 0.1:  # 10% chance
                await asyncio.sleep(random_delay(0.3, 0.8))
        
        # Small delay after typing
        await asyncio.sleep(random_delay(0.2, 0.5))


def get_random_user_agent():
    """Get a random realistic user agent."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    return random.choice(user_agents)


async def fill_form_and_solve_captcha(instance_id: int, url: str, headless: bool = False):
    """
    Fill form and solve CAPTCHA for a single instance.
    
    Args:
        instance_id: Unique ID for this instance (1-5)
        url: URL to test
        headless: Whether to run in headless mode
    
    Returns:
        dict with results
    """
    start_time = datetime.now()
    result = {
        'instance_id': instance_id,
        'success': False,
        'error': None,
        'duration': 0,
        'fields_filled': 0,
        'captcha_solved': False,
        'form_submitted': False
    }
    
    async with async_playwright() as p:
        # Use realistic browser context with random user agent
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
        
        # Remove webdriver property
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        page = await context.new_page()
        
        try:
            print(f"[Instance {instance_id}] ⏳ Starting...")
            
            # Navigate with human-like behavior
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random_delay(2, 4))  # Random wait after page load
            
            # Simulate reading the page
            await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
            await asyncio.sleep(random_delay(1, 2))
            
            # Handle cookie banner with human-like delay
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
                # Move mouse to button first (human-like)
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
            
            # Fill form fields
            form_data = {
                'name': f'Test User {instance_id}',
                'email': f'test{instance_id}@example.com',
                'phone': f'555-{1000 + instance_id}-4567',
                'message': f'This is automated test submission #{instance_id} from parallel CAPTCHA solver.',
            }
            
            fields_filled = 0
            
            # Fill name with human-like typing
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
            
            # Fill email with human-like typing
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
            
            # Fill phone with human-like typing
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
            
            # Fill message with human-like typing (slower for longer text)
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
            
            # Simulate reading the form before CAPTCHA
            await asyncio.sleep(random_delay(2, 4))
            
            result['fields_filled'] = fields_filled
            print(f"[Instance {instance_id}] ✅ Filled {fields_filled} fields")
            
            # Get site key
            site_key = await page.evaluate("""
                () => {
                    const recaptchaDiv = document.querySelector('.g-recaptcha, [data-sitekey]');
                    return recaptchaDiv ? recaptchaDiv.getAttribute('data-sitekey') : null;
                }
            """)
            
            # Solve reCAPTCHA
            print(f"[Instance {instance_id}] 🔐 Solving CAPTCHA...")
            solver = UltimateLocalCaptchaSolver(page=page)
            captcha_result = await solver.solve_recaptcha_v2(
                site_key=site_key or "",
                page_url=url
            )
            
            if captcha_result.get("success"):
                result['captcha_solved'] = True
                print(f"[Instance {instance_id}] ✅ CAPTCHA solved!")
                
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
                                print(f"[Instance {instance_id}] ✅ Form submitted!")
                                await asyncio.sleep(3)
                                break
                    except:
                        continue
                
                result['success'] = True
            else:
                result['error'] = captcha_result.get("error", "CAPTCHA solving failed")
                print(f"[Instance {instance_id}] ❌ CAPTCHA failed: {result['error']}")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"[Instance {instance_id}] ❌ Error: {e}")
        finally:
            end_time = datetime.now()
            result['duration'] = (end_time - start_time).total_seconds()
            await browser.close()
    
    return result


async def run_parallel_submissions(num_instances: int = 5, url: str = None, headless: bool = False):
    """
    Run multiple form submissions in parallel.
    
    Args:
        num_instances: Number of parallel instances (default: 5)
        url: URL to test (default: interiordesign.xcelanceweb.com/contact)
        headless: Whether to run in headless mode
    """
    if url is None:
        url = "https://interiordesign.xcelanceweb.com/contact"
    
    print("=" * 80)
    print("🚀 PARALLEL RECAPTCHA AUDIO CHALLENGE SOLVER")
    print("=" * 80)
    print(f"\n📍 URL: {url}")
    print(f"🔢 Instances: {num_instances}")
    print(f"🖥️  Headless: {headless}")
    print(f"⚡ Running in parallel for maximum speed!")
    print("\n" + "=" * 80 + "\n")
    
    start_time = datetime.now()
    
    # Create tasks with staggered start to avoid resource contention
    async def create_task_with_delay(instance_id, delay):
        """Create a task with a small delay to stagger starts."""
        if delay > 0:
            await asyncio.sleep(delay)
        return await fill_form_and_solve_captcha(instance_id, url, headless)
    
    # Stagger starts by 30-60 seconds between each instance to avoid detection
    print(f"🚀 Launching {num_instances} parallel instances (staggered start for safety)...\n")
    base_delay = 30  # Minimum 30 seconds between instances
    tasks = [
        create_task_with_delay(i + 1, i * base_delay + random.randint(0, 30))  # 30-60s, 60-90s, 90-120s, etc.
        for i in range(num_instances)
    ]
    
    # Run all tasks in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    # Process results
    print("\n" + "=" * 80)
    print("📊 RESULTS SUMMARY")
    print("=" * 80)
    
    successful = 0
    failed = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"\n[Instance {i+1}] ❌ Exception: {result}")
            failed += 1
            continue
        
        instance_id = result.get('instance_id', i + 1)
        success = result.get('success', False)
        duration = result.get('duration', 0)
        fields_filled = result.get('fields_filled', 0)
        captcha_solved = result.get('captcha_solved', False)
        form_submitted = result.get('form_submitted', False)
        error = result.get('error')
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"\n[Instance {instance_id}] {status}")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Fields filled: {fields_filled}")
        print(f"   CAPTCHA solved: {'Yes' if captcha_solved else 'No'}")
        print(f"   Form submitted: {'Yes' if form_submitted else 'No'}")
        if error:
            print(f"   Error: {error}")
        
        if success:
            successful += 1
        else:
            failed += 1
    
    print("\n" + "=" * 80)
    print("📈 STATISTICS")
    print("=" * 80)
    print(f"✅ Successful: {successful}/{num_instances}")
    print(f"❌ Failed: {failed}/{num_instances}")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    print(f"⚡ Average time per instance: {total_duration/num_instances:.2f}s")
    print(f"🚀 Speed improvement: ~{num_instances}x faster than sequential")
    print("=" * 80)
    
    # Save results to JSON
    results_file = Path(__file__).parent / f"parallel_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'total_instances': num_instances,
            'successful': successful,
            'failed': failed,
            'total_duration': total_duration,
            'results': results
        }, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return successful == num_instances


async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parallel reCAPTCHA solver')
    parser.add_argument('-n', '--num-instances', type=int, default=5, help='Number of parallel instances (default: 5)')
    parser.add_argument('-u', '--url', type=str, help='URL to test (default: interiordesign.xcelanceweb.com/contact)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    args = parser.parse_args()
    
    success = await run_parallel_submissions(
        num_instances=args.num_instances,
        url=args.url,
        headless=args.headless
    )
    
    if success:
        print("\n✅ ALL INSTANCES SUCCESSFUL!")
        sys.exit(0)
    else:
        print("\n⚠️  Some instances failed")
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

