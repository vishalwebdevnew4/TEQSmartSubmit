#!/usr/bin/env python3
"""
Quick test to verify local CAPTCHA solver is working end-to-end.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "automation"))

async def test_with_real_website():
    """Test local solver with an actual website that has reCAPTCHA."""
    print("=" * 70)
    print("TESTING LOCAL CAPTCHA SOLVER WITH REAL WEBSITE")
    print("=" * 70)
    
    from playwright.async_api import async_playwright
    from captcha_solver import LocalCaptchaSolver
    
    # Using Google's test reCAPTCHA page (public demo)
    test_url = "https://www.google.com/recaptcha/api2/demo"
    
    print(f"\n🌐 Loading: {test_url}")
    print("⏳ This will demonstrate the local solver in action...\n")
    
    async with async_playwright() as p:
        # Launch browser - set headless=False to watch the automation
        print("🖥️  Launching browser (headless=True - no visual, fast)")
        print("    To watch the automation live, change headless=False\n")
        
        browser = await p.chromium.launch(headless=True)  # Change to False to watch
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to page
            await page.goto(test_url, wait_until="networkidle")
            print("✅ Page loaded")
            
            # Initialize solver
            solver = LocalCaptchaSolver(page=page)
            print("✅ Local solver initialized")
            
            # Check for reCAPTCHA
            captcha_info = await page.evaluate("""
                () => {
                    const iframe = document.querySelector('iframe[src*="recaptcha"]');
                    const sitekey = document.querySelector('[data-sitekey]')?.getAttribute('data-sitekey');
                    return {
                        present: iframe !== null,
                        sitekey: sitekey
                    };
                }
            """)
            
            if captcha_info['present'] and captcha_info['sitekey']:
                print(f"✅ reCAPTCHA v2 detected")
                print(f"   Site Key: {captcha_info['sitekey'][:20]}...\n")
                
                # Try to solve
                print("🤖 Attempting to solve CAPTCHA (this may take 10-120 seconds)...\n")
                token = await solver.solve_recaptcha_v2(
                    captcha_info['sitekey'], 
                    page.url
                )
                
                if token:
                    print(f"\n✅ SUCCESS! CAPTCHA solved!")
                    print(f"   Token length: {len(token)} characters")
                    print(f"   Token preview: {token[:50]}...")
                    print("\n✅ Your local CAPTCHA solver is working perfectly!")
                else:
                    print("\n❌ No token returned")
            else:
                print("❌ reCAPTCHA not detected on page")
                print("   The test page may have changed or not loaded correctly")
        
        except KeyboardInterrupt:
            print("\n⏸️  Test interrupted by user")
        except Exception as e:
            print(f"\n⚠️  Error during test: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()
            print("\n" + "=" * 70)


async def main():
    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  LOCAL CAPTCHA SOLVER - REAL WEBSITE TEST                     ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    await test_with_real_website()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        sys.exit(0)
