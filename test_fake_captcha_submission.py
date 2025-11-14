#!/usr/bin/env python3
"""
Test form submission without CAPTCHA (manually inject token)
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Loading page...")
        await page.goto("https://interiordesign.xcelanceweb.com/", wait_until="load")
        await page.wait_for_timeout(12000)  # Wait for JS rendering
        
        print("\nFilling form fields...")
        await page.fill('input[name="name"]', 'Test User')
        await page.fill('input[name="email"]', 'test@example.com')
        await page.fill('input[name="phone"]', '+31600000000')
        await page.fill('textarea[name="comment"]', 'Test submission')
        
        print("Fields filled")
        
        print("\nInjecting fake CAPTCHA token...")
        # Use JavaScript to set the token (can't use fill() on hidden elements)
        fake_token = "fake_token_for_testing_" + "x" * 100
        await page.evaluate("""
            ([token]) => {
                const field = document.querySelector('textarea[name="g-recaptcha-response"]');
                if (field) {
                    field.value = token;
                    field.dispatchEvent(new Event('change', { bubbles: true }));
                    field.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
        """, [fake_token])
        
        print("\nTracking requests...")
        posts = []
        def track(request):
            if request.method == 'POST':
                posts.append(request.url)
                print(f"  POST: {request.url}")
        
        page.on('request', track)
        
        print("\nClicking submit button...")
        await page.click('button:has-text("Bericht verzenden")')
        
        print("\nWaiting for responses...")
        await page.wait_for_timeout(10000)
        
        if posts:
            print(f"\n✅ {len(posts)} POST request(s) detected!")
            for post in posts:
                print(f"   - {post}")
        else:
            print("\n❌ No POST requests detected")
        
        print("\nPage content after click:")
        current_url = page.url
        print(f"  URL: {current_url}")
        
        # Check for error/success messages
        body_text = await page.evaluate("() => document.body.innerText")
        if 'error' in body_text.lower() or 'fout' in body_text.lower():
            print("  ⚠️  Error detected on page")
        if 'success' in body_text.lower() or 'bedankt' in body_text.lower():
            print("  ✅ Success message detected!")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test())
