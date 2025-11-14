#!/usr/bin/env python3
"""
Inspect the target form website to understand its structure
"""

import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to form...")
        await page.goto("https://interiordesign.xcelanceweb.com/", wait_until="load")
        
        print("\n1. Page title:", await page.title())
        print("\n2. All forms on page:")
        forms = await page.query_selector_all('form')
        print(f"   Found {len(forms)} form(s)")
        
        for i, form in enumerate(forms):
            form_id = await form.get_attribute('id')
            form_class = await form.get_attribute('class')
            print(f"   Form {i+1}: id={form_id}, class={form_class}")
        
        print("\n3. All input fields on page:")
        inputs = await page.query_selector_all('input')
        print(f"   Found {len(inputs)} input(s)")
        for inp in inputs[:10]:  # Show first 10
            name = await inp.get_attribute('name')
            inp_type = await inp.get_attribute('type')
            placeholder = await inp.get_attribute('placeholder')
            print(f"   <input name={name} type={inp_type} placeholder={placeholder}>")
        
        print("\n4. All textareas on page:")
        textareas = await page.query_selector_all('textarea')
        print(f"   Found {len(textareas)} textarea(s)")
        for ta in textareas[:5]:
            name = await ta.get_attribute('name')
            placeholder = await ta.get_attribute('placeholder')
            print(f"   <textarea name={name} placeholder={placeholder}>")
        
        print("\n5. All buttons on page:")
        buttons = await page.query_selector_all('button')
        print(f"   Found {len(buttons)} button(s)")
        for btn in buttons[:10]:
            btn_type = await btn.get_attribute('type')
            text = await btn.inner_text()
            print(f"   <button type={btn_type}>: {text[:50]}")
        
        print("\n6. reCAPTCHA elements:")
        captchas = await page.query_selector_all('div[class*="recaptcha"], iframe[src*="recaptcha"]')
        print(f"   Found {len(captchas)} reCAPTCHA element(s)")
        
        print("\n7. Page body content length:", len(await page.content()))
        
        print("\n8. Checking if form is in a visible container:")
        visible_forms = []
        for form in forms:
            is_visible = await page.evaluate('el => window.getComputedStyle(el).display !== "none"', form)
            print(f"   Form visible: {is_visible}")
            if is_visible:
                visible_forms.append(form)
        
        print(f"\n9. Visible forms: {len(visible_forms)}")
        
        print("\n10. Taking screenshot...")
        await page.screenshot(path='/tmp/form_page.png')
        print("    Screenshot saved to /tmp/form_page.png")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(inspect())
