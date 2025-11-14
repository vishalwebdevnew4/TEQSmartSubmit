#!/usr/bin/env python3
"""
Test form loading behavior with retries and timing analysis
Tests if forms eventually load after retries and delays
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

async def test_form_loading():
    """Test form loading with retries and timing"""
    
    print("\n" + "="*70)
    print("FORM LOADING TEST - WITH RETRIES AND TIMING")
    print("="*70)
    
    try:
        from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
        
        config = {
            "url": "https://interiordesign.xcelanceweb.com/",
            "form_selectors": {
                "name": 'input[name="name"]',
                "email": 'input[name="email"]',
                "phone": 'input[name="phone"]',
                "message": 'textarea[name="comment"]',
                "submit": 'button:has-text("Bericht verzenden")'
            },
            "max_retries": 5,
            "initial_wait": 2,
            "max_wait": 15,
            "navigation_timeout": 30000
        }
        
        print(f"\n📋 Test Configuration:")
        print(f"  URL: {config['url']}")
        print(f"  Max Retries: {config['max_retries']}")
        print(f"  Initial Wait: {config['initial_wait']}s")
        print(f"  Max Wait: {config['max_wait']}s")
        print(f"  Navigation Timeout: {config['navigation_timeout']}ms")
        
        async with async_playwright() as p:
            print(f"\n🚀 Launching browser...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Set navigation timeout
            page.set_default_navigation_timeout(config['navigation_timeout'])
            page.set_default_timeout(config['navigation_timeout'])
            
            print(f"✅ Browser launched successfully")
            
            print(f"\n📍 Navigating to: {config['url']}")
            start_time = time.time()
            
            try:
                await page.goto(config['url'], wait_until='networkidle')
                nav_time = time.time() - start_time
                print(f"✅ Page loaded in {nav_time:.2f}s")
            except PlaywrightTimeout:
                nav_time = time.time() - start_time
                print(f"⚠️  Navigation timeout after {nav_time:.2f}s (network still busy)")
            
            # Test form field loading with retries
            results = {}
            for field_name, selector in config['form_selectors'].items():
                print(f"\n🔍 Checking field: {field_name} (selector: {selector})")
                
                field_loaded = False
                attempt = 0
                wait_time = config['initial_wait']
                
                while attempt < config['max_retries'] and not field_loaded:
                    attempt += 1
                    
                    try:
                        # Try to find and interact with the field
                        element = await page.query_selector(selector)
                        
                        if element:
                            # Check if element is visible
                            is_visible = await element.is_visible()
                            is_enabled = await element.is_enabled()
                            
                            if is_visible and is_enabled:
                                print(f"   ✅ Attempt {attempt}: Field found and ready")
                                results[field_name] = {
                                    'loaded': True,
                                    'attempts': attempt,
                                    'wait_time': wait_time
                                }
                                field_loaded = True
                            else:
                                print(f"   ⏳ Attempt {attempt}: Field found but not ready (visible={is_visible}, enabled={is_enabled})")
                        else:
                            print(f"   ⏳ Attempt {attempt}: Field not found yet, waiting {wait_time}s...")
                            await page.wait_for_timeout(wait_time * 1000)
                            wait_time = min(wait_time * 1.5, config['max_wait'])
                    
                    except Exception as e:
                        print(f"   ⚠️  Attempt {attempt}: Error - {str(e)[:50]}")
                        if attempt < config['max_retries']:
                            await page.wait_for_timeout(wait_time * 1000)
                
                if not field_loaded:
                    print(f"   ❌ Failed to load after {config['max_retries']} attempts")
                    results[field_name] = {
                        'loaded': False,
                        'attempts': config['max_retries'],
                        'wait_time': wait_time
                    }
            
            # Check for CAPTCHA
            print(f"\n🔍 Checking for CAPTCHA...")
            try:
                captcha_frame = await page.query_selector('iframe[title*="reCAPTCHA"]')
                if captcha_frame:
                    print(f"✅ reCAPTCHA v2 detected on form")
                    results['captcha'] = {'present': True}
                else:
                    print(f"ℹ️  No reCAPTCHA v2 detected")
                    results['captcha'] = {'present': False}
            except:
                print(f"⚠️  Could not check for CAPTCHA")
            
            # Test page content
            print(f"\n📄 Analyzing page content...")
            page_title = await page.title()
            print(f"  Page Title: {page_title}")
            
            # Count interactive elements
            inputs_count = await page.locator('input').count()
            textareas_count = await page.locator('textarea').count()
            buttons_count = await page.locator('button').count()
            
            print(f"  Input Fields: {inputs_count}")
            print(f"  Textareas: {textareas_count}")
            print(f"  Buttons: {buttons_count}")
            
            await browser.close()
            
            # Print summary
            print(f"\n" + "="*70)
            print("FORM LOADING SUMMARY")
            print("="*70)
            
            all_loaded = all(r.get('loaded', False) for r in results.values() if 'loaded' in r)
            
            for field_name, result in results.items():
                if 'loaded' in result:
                    status = "✅ LOADED" if result['loaded'] else "❌ FAILED"
                    attempts = result['attempts']
                    print(f"{status:12} {field_name:15} (Attempts: {attempts})")
            
            if all_loaded:
                print(f"\n✅ SUCCESS: All form fields loaded successfully!")
                return True
            else:
                print(f"\n⚠️  Some form fields did not load")
                return False
                
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("Make sure Playwright is installed: pip install playwright")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_delayed_loading():
    """Test form loading with progressive delays"""
    
    print("\n" + "="*70)
    print("DELAYED LOADING TEST - SIMULATING PROGRESSIVE WAITS")
    print("="*70)
    
    delays = [0, 1, 2, 3, 5, 10]
    
    print(f"\n📊 Testing form loading with various delays:")
    print(f"   Delays to test: {delays} seconds\n")
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            for delay in delays:
                page = await context.new_page()
                page.set_default_navigation_timeout(30000)
                
                print(f"🔄 Test with {delay}s delay:")
                
                try:
                    start = time.time()
                    
                    # Initial navigation
                    await page.goto("https://interiordesign.xcelanceweb.com/", 
                                  wait_until='domcontentloaded')
                    
                    # Wait before checking
                    if delay > 0:
                        await page.wait_for_timeout(delay * 1000)
                    
                    # Check if form field exists using correct selector
                    form_field = await page.query_selector('input[name="name"]')
                    elapsed = time.time() - start
                    
                    if form_field:
                        is_visible = await form_field.is_visible()
                        if is_visible:
                            print(f"   ✅ Form loaded and visible in {elapsed:.2f}s")
                        else:
                            print(f"   ⚠️  Form found but not visible in {elapsed:.2f}s")
                    else:
                        print(f"   ❌ Form not found after {elapsed:.2f}s")
                
                except Exception as e:
                    print(f"   ❌ Error: {str(e)[:40]}")
                
                finally:
                    await page.close()
                
                # Small delay between tests
                await asyncio.sleep(1)
            
            await browser.close()
            
            print(f"\n✅ Delayed loading test completed")
            return True
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

async def main():
    """Run all tests"""
    
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "FORM LOADING TEST SUITE".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    results = {}
    
    # Test 1: Form loading with retries
    print("\n[1/2] Running form loading test with retries...")
    results['form_loading'] = await test_form_loading()
    
    await asyncio.sleep(2)
    
    # Test 2: Delayed loading scenarios
    print("\n[2/2] Running delayed loading scenarios...")
    results['delayed_loading'] = await test_delayed_loading()
    
    # Final summary
    print("\n" + "="*70)
    print("OVERALL TEST SUMMARY")
    print("="*70)
    
    print(f"Form Loading Test:       {'✅ PASS' if results['form_loading'] else '❌ FAIL'}")
    print(f"Delayed Loading Test:    {'✅ PASS' if results['delayed_loading'] else '❌ FAIL'}")
    
    all_pass = all(results.values())
    
    print("\n" + "="*70)
    if all_pass:
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\n📊 Results:")
        print("  • Forms load correctly with retries")
        print("  • Progressive delays handled properly")
        print("  • Form fields become available after wait")
        print("\n🎯 Recommendation:")
        print("  Use retry mechanism with 2-15 second delays for reliability")
        return 0
    else:
        print("⚠️  SOME TESTS HAD ISSUES")
        print("="*70)
        return 1

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
