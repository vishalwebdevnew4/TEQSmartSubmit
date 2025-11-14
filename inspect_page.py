#!/usr/bin/env python3
"""
Inspect the actual page structure to understand what's happening.
"""

import asyncio
from playwright.async_api import async_playwright

async def inspect_page():
    url = "https://interiordesign.xcelanceweb.com/"
    
    print(f"\n🔍 Inspecting: {url}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Watch what's happening
        page = await browser.new_page()
        page.set_default_timeout(60000)
        
        try:
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # Get page structure
            page_structure = await page.evaluate("""
                () => {
                    return {
                        title: document.title,
                        url: window.location.href,
                        forms: document.querySelectorAll('form').length,
                        inputs: document.querySelectorAll('input').length,
                        iframes: document.querySelectorAll('iframe').length,
                        scripts: document.querySelectorAll('script').length,
                        bodyClasses: document.body.className,
                        isNextApp: window.__NEXT_DATA__ !== undefined,
                        nextData: window.__NEXT_DATA__ ? JSON.stringify(window.__NEXT_DATA__).substring(0, 200) : null
                    };
                }
            """)
            
            print("Page Structure:")
            print(f"  Title: {page_structure['title']}")
            print(f"  URL: {page_structure['url']}")
            print(f"  Forms: {page_structure['forms']}")
            print(f"  Inputs: {page_structure['inputs']}")
            print(f"  iFrames: {page_structure['iframes']}")
            print(f"  Scripts: {page_structure['scripts']}")
            print(f"  Is Next.js: {page_structure['isNextApp']}\n")
            
            if page_structure['forms'] > 0:
                forms_info = await page.evaluate("""
                    () => {
                        const forms = document.querySelectorAll('form');
                        return Array.from(forms).map((form, idx) => ({
                            index: idx,
                            id: form.id,
                            name: form.name,
                            action: form.action,
                            method: form.method,
                            inputs: form.querySelectorAll('input').length,
                            buttons: form.querySelectorAll('button, input[type="submit"]').length,
                            html: form.outerHTML.substring(0, 300)
                        }));
                    }
                """)
                
                for form in forms_info:
                    print(f"Form {form['index']}:")
                    print(f"  ID: {form['id']}")
                    print(f"  Action: {form['action']}")
                    print(f"  Inputs: {form['inputs']}, Buttons: {form['buttons']}")
                    print(f"  HTML: {form['html']}...\n")
            
            # Look for contact form or submission mechanism
            print("Looking for contact elements...")
            contact_elements = await page.evaluate("""
                () => {
                    return {
                        hasContactForm: document.querySelector('[id*="contact"]') !== null,
                        hasEmailInput: document.querySelector('input[type="email"]') !== null,
                        hasSubmitButton: document.querySelector('button[type="submit"], button:has-text("Submit"), button:has-text("Send")') !== null,
                        allButtons: Array.from(document.querySelectorAll('button')).slice(0, 5).map(b => ({
                            text: b.textContent,
                            type: b.type,
                            id: b.id,
                            className: b.className
                        }))
                    };
                }
            """)
            
            print(f"Contact elements found:")
            print(f"  Contact form div: {contact_elements['hasContactForm']}")
            print(f"  Email input: {contact_elements['hasEmailInput']}")
            print(f"  Submit button: {contact_elements['hasSubmitButton']}\n")
            
            print("Buttons on page:")
            for btn in contact_elements['allButtons']:
                print(f"  - {btn['text'][:40]} (type: {btn['type']}, id: {btn['id']})")
            
            print("\n" + "="*60)
            print("The browser window is now open. You can interact manually")
            print("to understand the page better. Press Enter to continue...")
            print("="*60)
            input()
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_page())
