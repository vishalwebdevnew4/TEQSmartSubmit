#!/usr/bin/env python3
"""
More detailed inspection of form elements
"""

import asyncio
from playwright.async_api import async_playwright

async def detailed_inspection():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating...")
        await page.goto("https://interiordesign.xcelanceweb.com/", wait_until="load")
        
        # Wait for JS to render
        print("Waiting 12 seconds for JS rendering...")
        await page.wait_for_timeout(12000)
        
        print("\n=== INPUT FIELDS ===")
        inputs = await page.query_selector_all('input')
        print(f"Total inputs: {len(inputs)}")
        for inp in inputs:
            name = await inp.get_attribute('name')
            inp_type = await inp.get_attribute('type')
            print(f"  input[name='{name}', type='{inp_type}']")
        
        print("\n=== TEXTAREAS ===")
        textareas = await page.query_selector_all('textarea')
        print(f"Total textareas: {len(textareas)}")
        for ta in textareas:
            name = await ta.get_attribute('name')
            print(f"  textarea[name='{name}']")
        
        print("\n=== BUTTONS ===")
        buttons = await page.query_selector_all('button')
        print(f"Total buttons: {len(buttons)}")
        for btn in buttons:
            text = await btn.inner_text()
            btn_type = await btn.get_attribute('type')
            btn_id = await btn.get_attribute('id')
            print(f"  button[type='{btn_type}', id='{btn_id}'] text='{text[:60]}'")
        
        print("\n=== FORMS ===")
        forms = await page.query_selector_all('form')
        print(f"Total forms: {len(forms)}")
        for form in forms:
            form_id = await form.get_attribute('id')
            form_class = await form.get_attribute('class')
            # Count inputs in this form
            form_inputs = await form.query_selector_all('input')
            form_textareas = await form.query_selector_all('textarea')
            print(f"  form[id='{form_id}'] class='{form_class}' - {len(form_inputs)} inputs, {len(form_textareas)} textareas")
        
        print("\n=== TRYING TO FIND FORM SELECTORS ===")
        # Check for form elements
        name_input = await page.query_selector('input[name="name"]')
        email_input = await page.query_selector('input[name="email"]')
        phone_input = await page.query_selector('input[name="phone"]')
        comment_textarea = await page.query_selector('textarea[name="comment"]')
        submit_btn = await page.query_selector('button[type="submit"]')
        bericht_btn = await page.query_selector('button:has-text("Bericht verzenden")')
        
        print(f"input[name='name']: {bool(name_input)}")
        print(f"input[name='email']: {bool(email_input)}")
        print(f"input[name='phone']: {bool(phone_input)}")
        print(f"textarea[name='comment']: {bool(comment_textarea)}")
        print(f"button[type='submit']: {bool(submit_btn)}")
        print(f"button with 'Bericht verzenden': {bool(bericht_btn)}")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(detailed_inspection())
