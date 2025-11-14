#!/usr/bin/env python3
"""
Minimal test - Just click the checkbox and see what happens.
No audio solving, just basics.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "automation"))

async def minimal_test():
    """Minimal test without complex solving."""
    from playwright.async_api import async_playwright
    
    url = "https://interiordesign.xcelanceweb.com/"
    
    print("\n" + "=" * 70)
    print("MINIMAL CAPTCHA TEST - JUST CLICK CHECKBOX")
    print("=" * 70 + "\n")
    
    async with async_playwright() as p:
        # Set headless=False so you can watch
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        page.set_default_timeout(30000)
        
        try:
            print("1️⃣  Loading page...\n")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            print("   ✅ Page loaded\n")
            
            print("2️⃣  Looking for reCAPTCHA checkbox...\n")
            
            # Find the checkbox iframe
            iframe = await page.query_selector('iframe[src*="recaptcha"][src*="anchor"]')
            if not iframe:
                print("   ❌ Could not find reCAPTCHA iframe\n")
                return
            
            print("   ✅ Found reCAPTCHA iframe\n")
            
            # Get the frame and click checkbox
            frame = await iframe.content_frame()
            if frame:
                print("3️⃣  Clicking checkbox inside iframe...\n")
                
                checkbox = await frame.query_selector('#recaptcha-anchor')
                if checkbox:
                    await checkbox.click()
                    print("   ✅ Checkbox clicked\n")
                    
                    print("4️⃣  Waiting 10 seconds to see if challenge appears...\n")
                    print("   👀 Look at the browser window!\n")
                    
                    for i in range(10):
                        await page.wait_for_timeout(1000)
                        
                        # Check if challenge frame appeared
                        challenge = await page.query_selector('iframe[title*="challenge"]')
                        if challenge:
                            print(f"   ⚠️  AUDIO CHALLENGE APPEARED! (after {i+1} seconds)\n")
                            print("   The challenge iframe is now open.")
                            print("   ⏳ Waiting 20 more seconds for audio to load...\n")
                            
                            await page.wait_for_timeout(20000)
                            
                            # Check for audio elements
                            challenge_frame = await challenge.content_frame()
                            if challenge_frame:
                                audio_check = await challenge_frame.evaluate("""
                                    () => {
                                        const audio = document.querySelector('audio');
                                        const download = document.querySelector('a.rc-audiochallenge-tdownload');
                                        const input = document.querySelector('input[placeholder*="response"], input[placeholder*="text"]');
                                        
                                        return {
                                            audio_element: audio !== null,
                                            download_link: download !== null,
                                            text_input: input !== null
                                        };
                                    }
                                """)
                                
                                print(f"   Audio element: {audio_check['audio_element']}")
                                print(f"   Download link: {audio_check['download_link']}")
                                print(f"   Text input: {audio_check['text_input']}\n")
                            break
                        
                        if i == 9:
                            print(f"   ℹ️  No challenge after 10 seconds\n")
                            
                            # Check if CAPTCHA was solved without challenge
                            response_field = await page.evaluate("""
                                () => {
                                    const field = document.querySelector('textarea[name="g-recaptcha-response"]');
                                    return field ? field.value.length : 0;
                                }
                            """)
                            
                            if response_field > 0:
                                print(f"   ✅ CAPTCHA SOLVED WITHOUT CHALLENGE!")
                                print(f"   Token in response field: {response_field} characters\n")
                            else:
                                print(f"   ❌ No challenge, but also no token\n")
                else:
                    print("   ❌ Could not find checkbox element\n")
            
            print("=" * 70)
            print("TEST COMPLETE - Keep browser open if needed")
            print("=" * 70 + "\n")
            
            print("What to do next:")
            print("1. If you see 'CAPTCHA SOLVED WITHOUT CHALLENGE' - Your solver is working!")
            print("2. If you see 'AUDIO CHALLENGE APPEARED' - Audio solving needs testing")
            print("3. If neither - CAPTCHA may behave differently, check browser window\n")
            
            print("Press Enter to close browser...\n")
            input()
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(minimal_test())
