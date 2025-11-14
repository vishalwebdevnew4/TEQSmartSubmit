#!/usr/bin/env python3
"""
Check the raw HTML of the page
"""

import asyncio
from playwright.async_api import async_playwright

async def check_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://interiordesign.xcelanceweb.com/", wait_until="load")
        
        # Wait for potential dynamic content
        await page.wait_for_timeout(5000)
        
        html = await page.content()
        print("Page HTML (first 2000 chars):")
        print(html[:2000])
        print("\n...")
        print("Page HTML (last 1000 chars):")
        print(html[-1000:])
        
        # Check for specific strings
        print("\n\nSearching for keywords:")
        print(f"Contains 'form': {'form' in html.lower()}")
        print(f"Contains 'input': {'input' in html.lower()}")
        print(f"Contains 'recaptcha': {'recaptcha' in html.lower()}")
        print(f"Contains 'contact': {'contact' in html.lower()}")
        print(f"Contains 'bericht': {'bericht' in html.lower()}")
        
        # Check if there's JavaScript
        print(f"Contains 'script': {'<script' in html}")
        print(f"Contains 'React': {'React' in html}")
        print(f"Contains 'Next.js': {'Next.js' in html}")
        
        # Try waiting longer
        print("\n\nWaiting additional time for dynamic content...")
        await page.wait_for_timeout(10000)
        
        html2 = await page.content()
        print(f"After 10s wait, HTML length: {len(html2)}")
        if len(html2) > len(html):
            print(f"HTML content grew! Now: {len(html2)} bytes (was {len(html)})")
            print("New content (first 500 chars):")
            print(html2[:500])
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(check_html())
