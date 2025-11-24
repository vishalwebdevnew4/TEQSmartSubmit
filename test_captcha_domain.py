#!/usr/bin/env python3
"""
Test CAPTCHA solver on a specific domain.
Tests the captcha detection and solving capabilities on https://interiordesign.xcelanceweb.com/contact
"""

import asyncio
import sys
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent / "automation"))

from playwright.async_api import async_playwright
from run_submission import UniversalCaptchaSolver, LocalCaptchaSolver
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_captcha_on_domain():
    """Test CAPTCHA detection and solving on the specified domain."""
    
    url = "https://interiordesign.xcelanceweb.com/contact"
    
    print("=" * 80)
    print("🧪 CAPTCHA SOLVER TEST")
    print("=" * 80)
    print(f"\n📍 Testing URL: {url}")
    print(f"🔍 Testing CAPTCHA detection and solving capabilities")
    print("\n" + "=" * 80 + "\n")
    
    async with async_playwright() as p:
        # Launch browser in visible mode for testing
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to the page
            print("⏳ Navigating to page...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            print("✅ Page loaded successfully")
            
            # Wait a bit for any dynamic content to load
            await page.wait_for_timeout(3000)
            
            # Initialize CAPTCHA solver
            solver = UniversalCaptchaSolver()
            
            # Detect CAPTCHA elements
            print("\n🔍 Detecting CAPTCHA elements...")
            captcha_elements = await solver.detect_captcha_fields(page)
            
            print(f"\n📊 Detection Results:")
            print(f"   Found {len(captcha_elements)} CAPTCHA element(s)")
            
            if captcha_elements:
                for i, element in enumerate(captcha_elements, 1):
                    print(f"\n   Element {i}:")
                    print(f"      Type: {element.get('type', 'unknown')}")
                    print(f"      Selector: {element.get('selector', 'N/A')}")
            else:
                print("   ⚠️  No CAPTCHA elements detected")
            
            # Take a screenshot for inspection
            screenshot_path = Path(__file__).parent / "captcha_test_screenshot.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"\n📸 Screenshot saved to: {screenshot_path}")
            
            # Try to solve detected CAPTCHAs
            if captcha_elements:
                print("\n🔧 Attempting to solve CAPTCHA...")
                for i, element in enumerate(captcha_elements, 1):
                    print(f"\n   Solving element {i}...")
                    solution = await solver.solve_captcha(page, element)
                    
                    if solution:
                        print(f"   ✅ CAPTCHA solved: {solution}")
                        
                        # Try to find and fill the CAPTCHA input field
                        captcha_input = await page.evaluate("""
                        () => {
                            const inputs = Array.from(document.querySelectorAll('input'));
                            const captchaInput = inputs.find(input => {
                                const name = input.name.toLowerCase();
                                const id = input.id.toLowerCase();
                                const placeholder = input.placeholder.toLowerCase();
                                
                                return name.includes('captcha') || id.includes('captcha') || 
                                       placeholder.includes('captcha') || placeholder.includes('security code') ||
                                       name.includes('verification') || id.includes('verif');
                            });
                            
                            return captchaInput ? {
                                name: captchaInput.name,
                                id: captchaInput.id,
                                selector: `input[name="${captchaInput.name}"]`
                            } : null;
                        }
                        """)
                        
                        if captcha_input:
                            print(f"   📝 Found CAPTCHA input field: {captcha_input.get('name', 'N/A')}")
                            try:
                                selector = captcha_input.get('selector', f"input[name='{captcha_input.get('name')}']")
                                await page.fill(selector, solution)
                                print(f"   ✅ Filled CAPTCHA input with solution: {solution}")
                            except Exception as e:
                                print(f"   ⚠️  Could not fill CAPTCHA input: {e}")
                    else:
                        print(f"   ❌ Could not solve CAPTCHA")
            
            # Check for any images that might be CAPTCHAs
            print("\n🖼️  Checking for CAPTCHA images...")
            images = await page.evaluate("""
            () => {
                const imgs = Array.from(document.querySelectorAll('img'));
                return imgs.map(img => ({
                    src: img.src,
                    alt: img.alt,
                    width: img.width,
                    height: img.height,
                    className: img.className
                })).filter(img => {
                    const src = img.src.toLowerCase();
                    const alt = img.alt.toLowerCase();
                    return src.includes('captcha') || alt.includes('captcha') || 
                           src.includes('securo') || alt.includes('verification') ||
                           (img.width > 0 && img.height > 0 && img.width < 200 && img.height < 100);
                });
            }
            """)
            
            if images:
                print(f"   Found {len(images)} potential CAPTCHA image(s):")
                for i, img in enumerate(images, 1):
                    print(f"      Image {i}:")
                    print(f"         Src: {img['src'][:100]}...")
                    print(f"         Alt: {img['alt']}")
                    print(f"         Size: {img['width']}x{img['height']}")
                    
                    # Try to solve if it's a data URL
                    if img['src'].startswith('data:image'):
                        print(f"         🔧 Attempting to solve...")
                        local_solver = LocalCaptchaSolver()
                        solution = local_solver.solve_captcha_from_base64(img['src'])
                        if solution:
                            print(f"         ✅ Solved: {solution}")
                        else:
                            print(f"         ❌ Could not solve")
            else:
                print("   No potential CAPTCHA images found")
            
            # Wait a bit to keep browser open for inspection
            print("\n" + "=" * 80)
            print("⏸️  Keeping browser open for 30 seconds for manual inspection...")
            print("=" * 80)
            await page.wait_for_timeout(30000)
            
            print("\n✅ Test completed!")
            
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(test_captcha_on_domain())
        print("\n✅ Test script completed")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

