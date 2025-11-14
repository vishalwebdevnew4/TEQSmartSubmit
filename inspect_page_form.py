#!/usr/bin/env python3
"""
Inspect the form on the website to find correct selectors
"""

import asyncio
import sys
import json

async def inspect_form():
    """Inspect form and find correct selectors"""
    
    print("\n" + "="*70)
    print("FORM INSPECTION - FINDING CORRECT SELECTORS")
    print("="*70)
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print(f"\n🌐 Loading page: https://interiordesign.xcelanceweb.com/")
            await page.goto("https://interiordesign.xcelanceweb.com/", wait_until='networkidle')
            print(f"✅ Page loaded")
            
            # Wait a bit for dynamic content
            await page.wait_for_timeout(3000)
            
            # Find all form elements
            print(f"\n📋 Scanning for form elements...\n")
            
            # Look for input fields
            inputs = await page.query_selector_all('input')
            print(f"Found {len(inputs)} input fields:")
            for i, inp in enumerate(inputs):
                try:
                    name = await inp.get_attribute('name')
                    id_attr = await inp.get_attribute('id')
                    type_attr = await inp.get_attribute('type')
                    placeholder = await inp.get_attribute('placeholder')
                    visible = await inp.is_visible()
                    print(f"  [{i+1}] name={name}, id={id_attr}, type={type_attr}, placeholder={placeholder}, visible={visible}")
                except:
                    pass
            
            # Look for textareas
            textareas = await page.query_selector_all('textarea')
            print(f"\nFound {len(textareas)} textarea fields:")
            for i, ta in enumerate(textareas):
                try:
                    name = await ta.get_attribute('name')
                    id_attr = await ta.get_attribute('id')
                    placeholder = await ta.get_attribute('placeholder')
                    visible = await ta.is_visible()
                    print(f"  [{i+1}] name={name}, id={id_attr}, placeholder={placeholder}, visible={visible}")
                except:
                    pass
            
            # Look for form elements
            forms = await page.query_selector_all('form')
            print(f"\nFound {len(forms)} form elements:")
            for i, form in enumerate(forms):
                try:
                    id_attr = await form.get_attribute('id')
                    name = await form.get_attribute('name')
                    visible = await form.is_visible()
                    print(f"  [{i+1}] id={id_attr}, name={name}, visible={visible}")
                except:
                    pass
            
            # Look for submit buttons
            buttons = await page.query_selector_all('button[type="submit"]')
            print(f"\nFound {len(buttons)} submit buttons:")
            for i, btn in enumerate(buttons):
                try:
                    text = await btn.inner_text()
                    id_attr = await btn.get_attribute('id')
                    name = await btn.get_attribute('name')
                    visible = await btn.is_visible()
                    print(f"  [{i+1}] text='{text}', id={id_attr}, name={name}, visible={visible}")
                except:
                    pass
            
            # Look for iframes
            iframes = await page.query_selector_all('iframe')
            print(f"\nFound {len(iframes)} iframes:")
            for i, iframe in enumerate(iframes):
                try:
                    title = await iframe.get_attribute('title')
                    src = await iframe.get_attribute('src')
                    id_attr = await iframe.get_attribute('id')
                    print(f"  [{i+1}] title='{title}', id={id_attr}, src={src[:50] if src else 'none'}...")
                except:
                    pass
            
            # Get page HTML snippet (first 5000 chars)
            print(f"\n📄 Page title: {await page.title()}")
            
            # Try to find form-related divs or sections
            print(f"\n🔍 Looking for common form containers...\n")
            
            form_like = await page.query_selector_all('[class*="form"], [id*="form"], [class*="contact"], [id*="contact"]')
            print(f"Found {len(form_like)} form-like elements:")
            for i, elem in enumerate(form_like[:10]):  # Show first 10
                try:
                    id_attr = await elem.get_attribute('id')
                    class_attr = await elem.get_attribute('class')
                    tag = await page.evaluate(f'() => document.querySelector("[id=\\"{id_attr}\\"]").tagName')
                    visible = await elem.is_visible()
                    print(f"  [{i+1}] tag={tag}, id={id_attr}, class={class_attr[:50] if class_attr else 'none'}, visible={visible}")
                except:
                    pass
            
            await browser.close()
            return True
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        asyncio.run(inspect_form())
    except KeyboardInterrupt:
        print("\n⏸️  Interrupted")
        sys.exit(1)
