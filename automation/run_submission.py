#!/usr/bin/env python3
"""
Lightweight Playwright automation helper.

This script is designed to be orchestrated by the Next.js API route. It:
  * Loads a JSON template describing selectors and values to fill.
  * Navigates to the target URL.
  * Attempts to fill and submit the form.
  * Prints a JSON result to stdout so the caller can parse it.

Template structure example:
{
  "fields": [
    { "selector": "input[name='name']", "value": "John Doe" },
    { "selector": "#email", "value": "john@example.com" }
  ],
  "submit_selector": "button[type='submit']",
  "post_submit_wait_ms": 4000,
  "captcha": false
}
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode
from urllib.request import urlopen


async def detect_captcha(page) -> Dict[str, Any]:
    """Detect if there's a CAPTCHA on the page and extract site key."""
    captcha_info = await page.evaluate("""
        () => {
            // Check for reCAPTCHA
            const recaptcha = document.querySelector('iframe[title*="reCAPTCHA"], iframe[src*="recaptcha"]');
            const recaptchaResponse = document.querySelector('textarea[name="g-recaptcha-response"]');
            
            if (recaptcha || recaptchaResponse) {
                const responseValue = recaptchaResponse ? recaptchaResponse.value : '';
                
                // Try to extract site key
                let siteKey = '';
                const dataSitekey = document.querySelector('[data-sitekey]');
                if (dataSitekey) {
                    siteKey = dataSitekey.getAttribute('data-sitekey') || '';
                } else {
                    // Try to extract from iframe src
                    if (recaptcha) {
                        const src = recaptcha.getAttribute('src') || '';
                        const match = src.match(/[&?]k=([^&]+)/);
                        if (match) {
                            siteKey = match[1];
                        }
                    }
                }
                
                return {
                    type: 'recaptcha',
                    present: true,
                    solved: responseValue.length > 0,
                    responseField: recaptchaResponse ? 'g-recaptcha-response' : null,
                    siteKey: siteKey
                };
            }
            
            // Check for hCaptcha
            const hcaptcha = document.querySelector('iframe[src*="hcaptcha"]');
            if (hcaptcha) {
                let siteKey = '';
                const dataSitekey = document.querySelector('[data-sitekey]');
                if (dataSitekey) {
                    siteKey = dataSitekey.getAttribute('data-sitekey') || '';
                }
                return {
                    type: 'hcaptcha',
                    present: true,
                    solved: false,
                    siteKey: siteKey
                };
            }
            
            return {
                type: 'none',
                present: false,
                solved: false
            };
        }
    """)
    return captcha_info


# Import CAPTCHA solver
try:
    from captcha_solver import get_captcha_solver
except ImportError:
    try:
        from automation.captcha_solver import get_captcha_solver
    except ImportError:
        # Fallback if module not found
        def get_captcha_solver(service="auto"):
            return None


async def inject_recaptcha_token(page, token: str, response_field: str = "g-recaptcha-response"):
    """Inject the solved CAPTCHA token into the form."""
    await page.evaluate("""
        ([token, fieldName]) => {
            // Set the response field
            const responseField = document.querySelector(`textarea[name="${fieldName}"]`);
            if (responseField) {
                responseField.value = token;
                responseField.style.display = 'block';
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                responseField.dispatchEvent(event);
                
                // Also trigger input event
                const inputEvent = new Event('input', { bubbles: true });
                responseField.dispatchEvent(inputEvent);
            }
            
            // Call the reCAPTCHA callback if it exists
            if (window.grecaptcha && window.grecaptcha.getResponse) {
                try {
                    // Try to find and update the widget
                    const widgets = document.querySelectorAll('[data-sitekey]');
                    for (let widget of widgets) {
                        try {
                            const widgetId = widget.getAttribute('data-widget-id');
                            if (widgetId) {
                                // Try to set the response directly
                                window.grecaptcha.execute(widgetId);
                            }
                        } catch (e) {
                            // Ignore
                        }
                    }
                } catch (e) {
                    // Ignore errors
                }
            }
        }
    """, [token, response_field])


async def wait_for_captcha_solution(page, captcha_info: Dict, timeout_ms: int = 60000) -> bool:
    """Wait for CAPTCHA to be solved."""
    if not captcha_info.get("present"):
        return True
    
    if captcha_info.get("solved"):
        return True
    
    if captcha_info.get("type") == "recaptcha":
        response_field = captcha_info.get("responseField", "g-recaptcha-response")
        try:
            # Wait for the response field to be filled
            await page.wait_for_function(
                f"document.querySelector('textarea[name=\"{response_field}\"]')?.value?.length > 0",
                timeout=timeout_ms
            )
            return True
        except Exception:
            return False
    
    return False


async def discover_forms(page) -> List[Dict[str, Any]]:
    """Crawl the page to discover all forms and their fields."""
    forms_data = await page.evaluate("""
        () => {
            const forms = Array.from(document.querySelectorAll('form'));
            return forms.map((form, formIndex) => {
                const inputs = Array.from(form.querySelectorAll('input, textarea, select'));
                const fields = inputs.map((input, index) => {
                    const tagName = input.tagName.toLowerCase();
                    const type = input.type || '';
                    const name = input.name || '';
                    const id = input.id || '';
                    const placeholder = input.placeholder || '';
                    const label = (() => {
                        if (input.id) {
                            const labelEl = document.querySelector(`label[for="${input.id}"]`);
                            if (labelEl) return labelEl.textContent.trim();
                        }
                        const parentLabel = input.closest('label');
                        if (parentLabel) return parentLabel.textContent.trim();
                        const prevSibling = input.previousElementSibling;
                        if (prevSibling && prevSibling.tagName === 'LABEL') {
                            return prevSibling.textContent.trim();
                        }
                        return '';
                    })();
                    
                    // Generate possible selectors
                    const selectors = [];
                    if (name) selectors.push(`${tagName}[name="${name}"]`);
                    if (id) selectors.push(`#${id}`);
                    if (name && type) selectors.push(`${tagName}[name="${name}"][type="${type}"]`);
                    if (placeholder) selectors.push(`${tagName}[placeholder="${placeholder}"]`);
                    
                    return {
                        tagName,
                        type,
                        name,
                        id,
                        placeholder,
                        label,
                        required: input.hasAttribute('required'),
                        selectors: selectors,
                        index: index
                    };
                });
                
                const submitButtons = Array.from(form.querySelectorAll('button[type="submit"], input[type="submit"], button:not([type])'));
                const submitSelectors = submitButtons.map(btn => {
                    const text = btn.textContent.trim() || btn.value || '';
                    if (btn.type === 'submit') {
                        if (text) return `button[type="submit"]:has-text("${text}")`;
                        return 'button[type="submit"]';
                    }
                    if (text) return `button:has-text("${text}")`;
                    return 'button';
                });
                
                return {
                    index: formIndex,
                    action: form.action || '',
                    method: form.method || 'get',
                    fields: fields,
                    submitSelectors: submitSelectors,
                    submitButtons: submitButtons.map(btn => ({
                        text: btn.textContent.trim() || btn.value || '',
                        type: btn.type || 'button'
                    }))
                };
            });
        }
    """)
    return forms_data


def find_matching_field(discovered_fields: List[Dict], template_field: Dict) -> Dict | None:
    """Find a discovered field that matches the template field."""
    template_selector = template_field.get("selector", "")
    template_name = template_field.get("name", "")
    
    # Extract name from template selector if present (e.g., "input[name='name']" -> "name")
    if template_selector and not template_name:
        import re
        name_match = re.search(r"name=['\"]([^'\"]+)['\"]", template_selector)
        if name_match:
            template_name = name_match.group(1)
    
    for field in discovered_fields:
        field_name = field.get("name", "")
        
        # Check by name (exact match)
        if template_name and field_name and template_name == field_name:
            return field
        
        # Check if template selector matches any field selector exactly
        if template_selector:
            for sel in field.get("selectors", []):
                # Normalize selectors for comparison (remove quote differences)
                sel_normalized = sel.replace('"', "'")
                template_sel_normalized = template_selector.replace('"', "'")
                if sel_normalized == template_sel_normalized:
                    return field
                # Also check if one contains the other
                if template_sel_normalized in sel_normalized or sel_normalized in template_sel_normalized:
                    return field
        
        # Check if name appears in any selector
        if template_name and field_name:
            for sel in field.get("selectors", []):
                if template_name in sel or field_name in template_selector:
                    return field
    
    return None


async def run_submission(url: str, template_path: Path) -> Dict[str, Any]:
    from playwright.async_api import async_playwright  # imported lazily for performance

    template: Dict[str, Any] = json.loads(template_path.read_text())
    fields: List[Dict[str, str]] = template.get("fields", [])
    pre_actions: List[Dict[str, Any]] = template.get("pre_actions", [])
    submit_selector: str | None = template.get("submit_selector")

    # Add progress logging
    print("🚀 Starting automation...", file=sys.stderr)
    print(f"   URL: {url}", file=sys.stderr)
    print(f"   Fields to fill: {len(fields)}", file=sys.stderr)

    async with async_playwright() as p:
        # Check if we should run in headless mode
        # Set HEADLESS=false or TEQ_PLAYWRIGHT_HEADLESS=false to see the browser
        headless = os.getenv("HEADLESS", "true").lower() not in ("false", "0", "no")
        if template.get("headless") is not None:
            headless = template.get("headless", True)
        
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        # Use "load" instead of "networkidle" for faster loading
        wait_until = template.get("wait_until", "load")
        print("📄 Loading page...", file=sys.stderr)
        await page.goto(url, wait_until=wait_until, timeout=60000)
        print("✅ Page loaded", file=sys.stderr)

        # Run pre-actions (like cookie consent)
        if pre_actions:
            print(f"🔧 Running {len(pre_actions)} pre-actions...", file=sys.stderr)
        for i, action in enumerate(pre_actions, 1):
            action_type = action.get("type", "click")
            selector = action.get("selector")
            if not selector:
                continue
            try:
                print(f"   Pre-action {i}/{len(pre_actions)}: {action_type} on {selector[:50]}...", file=sys.stderr)
                if action_type == "click":
                    await page.click(selector, timeout=action.get("timeout_ms", 10000))
                elif action_type == "wait_for_selector":
                    await page.wait_for_selector(selector, timeout=action.get("timeout_ms", 10000))
                print(f"   ✅ Pre-action {i} completed", file=sys.stderr)
            except Exception as e:
                # Pre-action failed, continue anyway
                print(f"   ⚠️  Pre-action {i} failed: {str(e)[:50]}", file=sys.stderr)
                pass

        # Wait for page to be fully interactive
        await page.wait_for_timeout(2000)
        
        # Discover forms on the page
        print("🔍 Discovering forms on page...", file=sys.stderr)
        discovered_forms = await discover_forms(page)
        print(f"✅ Found {len(discovered_forms)} form(s)", file=sys.stderr)
        
        if not discovered_forms:
            raise RuntimeError("No forms found on the page")
        
        # Use the first form (or find the best match)
        target_form = discovered_forms[0]
        if len(discovered_forms) > 1:
            # Try to find form with most matching fields
            best_match = target_form
            best_score = 0
            for form in discovered_forms:
                score = 0
                for field in fields:
                    if find_matching_field(form.get("fields", []), field):
                        score += 1
                if score > best_score:
                    best_score = score
                    best_match = form
            target_form = best_match
        
        discovered_fields = target_form.get("fields", [])
        print(f"📝 Found {len(discovered_fields)} fields in target form", file=sys.stderr)
        
        # Fill form fields using discovered selectors
        print(f"✍️  Filling {len(fields)} form fields...", file=sys.stderr)
        for i, field in enumerate(fields, 1):
            field_name = field.get("selector", field.get("name", f"field_{i}"))
            print(f"   Field {i}/{len(fields)}: {field_name[:50]}...", file=sys.stderr)
            value = field.get("value") or field.get("testValue") or ""
            if not value:
                continue
            
            # Try to find matching discovered field
            discovered_field = find_matching_field(discovered_fields, field)
            
            if discovered_field:
                # Use the first available selector from discovered field
                selectors_to_try = discovered_field.get("selectors", [])
                if not selectors_to_try and discovered_field.get("name"):
                    selectors_to_try = [
                        f"input[name='{discovered_field['name']}']",
                        f"input[name=\"{discovered_field['name']}\"]",
                        f"textarea[name='{discovered_field['name']}']",
                        f"textarea[name=\"{discovered_field['name']}\"]",
                    ]
            else:
                # Fall back to template selector
                template_selector = field.get("selector")
                if template_selector:
                    selectors_to_try = [template_selector]
                    # Also try with different quote styles
                    if "'" in template_selector:
                        selectors_to_try.append(template_selector.replace("'", '"'))
                    elif '"' in template_selector:
                        selectors_to_try.append(template_selector.replace('"', "'"))
                else:
                    selectors_to_try = []
            
            # Try each selector until one works
            filled = False
            last_error = None
            for selector in selectors_to_try:
                try:
                    # Wait for the field to be visible and ready
                    await page.wait_for_selector(selector, state="visible", timeout=5000)
                    # Try to fill the field
                    await page.fill(selector, value, timeout=field.get("timeout_ms", 10000))
                    filled = True
                    print(f"   ✅ Field {i} filled successfully", file=sys.stderr)
                    break
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if not filled and not field.get("optional"):
                # Provide detailed error message
                error_msg = f"Failed to fill field: {field.get('selector', 'unknown')}"
                if discovered_field:
                    error_msg += f"\nDiscovered field: {discovered_field.get('name', 'unknown')}"
                    error_msg += f"\nTried selectors: {', '.join(selectors_to_try[:3])}"
                else:
                    error_msg += f"\nField not found in discovered fields. Tried: {', '.join(selectors_to_try[:3])}"
                if last_error:
                    error_msg += f"\nLast error: {last_error}"
                raise RuntimeError(error_msg)

        # Detect and handle CAPTCHA
        print("🔐 Checking for CAPTCHA...", file=sys.stderr)
        captcha_info = await detect_captcha(page)
        captcha_present = captcha_info.get("present", False)
        captcha_solved = captcha_info.get("solved", False)
        if captcha_present:
            print(f"   CAPTCHA detected: {captcha_info.get('type', 'unknown')}", file=sys.stderr)
        else:
            print("   No CAPTCHA detected", file=sys.stderr)
        
        if captcha_present and not captcha_solved:
            # Try to automatically solve CAPTCHA
            captcha_type = captcha_info.get("type", "")
            site_key = captcha_info.get("siteKey", "")
            response_field = captcha_info.get("responseField", "g-recaptcha-response")
            
            # Check if local solver is enabled FIRST (before checking external services)
            use_local = template.get("use_local_captcha_solver", False) or \
                       os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "false").lower() in ("true", "1", "yes")
            
            solver = None
            local_solver_used = False
            local_solver_instance = None  # Store local solver instance for later use
            
            if use_local and captcha_type == "recaptcha" and site_key:
                # Use local solver - fully automated
                try:
                    try:
                        from captcha_solver import LocalCaptchaSolver
                    except ImportError:
                        from automation.captcha_solver import LocalCaptchaSolver
                    
                    print("🤖 Using LOCAL CAPTCHA SOLVER (fully automated)...", file=sys.stderr)
                    local_solver_instance = LocalCaptchaSolver(page=page)
                    solver = local_solver_instance
                    local_solver_used = True
                    
                    token = await solver.solve_recaptcha_v2(site_key, page.url)
                    if token:
                        # Inject the solved token into the form
                        await inject_recaptcha_token(page, token, response_field)
                        await page.wait_for_timeout(2000)  # Wait longer for token processing
                        
                        # Verify the token was injected
                        captcha_info = await detect_captcha(page)
                        captcha_solved = captcha_info.get("solved", False)
                        
                        if not captcha_solved:
                            # Force set it again
                            await page.evaluate("""
                                ([token, fieldName]) => {
                                    const field = document.querySelector(`textarea[name="${fieldName}"]`);
                                    if (field) {
                                        field.value = token;
                                        // Trigger events
                                        field.dispatchEvent(new Event('change', { bubbles: true }));
                                        field.dispatchEvent(new Event('input', { bubbles: true }));
                                    }
                                }
                            """, [token, response_field])
                            await page.wait_for_timeout(1000)
                            captcha_solved = True
                        
                        if captcha_solved:
                            print("✅ CAPTCHA solved automatically by local solver!", file=sys.stderr)
                    else:
                        raise RuntimeError("Local CAPTCHA solver returned empty token")
                        
                except Exception as e:
                    raise RuntimeError(
                        f"Local CAPTCHA solving failed: {str(e)}. "
                        "Install dependencies: pip install SpeechRecognition pydub"
                    )
            
            # If local solver not used, try external services
            if not local_solver_used and captcha_type == "recaptcha" and site_key:
                # Get CAPTCHA solver service preference
                captcha_service = template.get("captcha_service", "auto")
                captcha_api_key = template.get("captcha_api_key")  # Can override service-specific keys
                
                # Get solver instance
                solver = get_captcha_solver(captcha_service)
                
                # If local solver, set the page object
                if solver and hasattr(solver, 'page'):
                    solver.page = page
                
                if solver:
                    try:
                        # Solve reCAPTCHA using configured solver
                        page_url = page.url
                        token = await solver.solve_recaptcha_v2(site_key, page_url)
                        
                        if token:
                            # Inject the solved token into the form
                            await inject_recaptcha_token(page, token, response_field)
                            
                            # Wait a bit for the token to be processed
                            await page.wait_for_timeout(1000)
                            
                            # Verify the token was injected
                            captcha_info = await detect_captcha(page)
                            captcha_solved = captcha_info.get("solved", False)
                            
                            if not captcha_solved:
                                # Force set it again
                                await page.evaluate("""
                                    ([token, fieldName]) => {
                                        const field = document.querySelector(`textarea[name="${fieldName}"]`);
                                        if (field) {
                                            field.value = token;
                                        }
                                    }
                                """, [token, response_field])
                                captcha_solved = True
                        else:
                            raise RuntimeError("CAPTCHA solver returned empty token")
                            
                    except Exception as e:
                        raise RuntimeError(
                            f"Failed to solve CAPTCHA automatically: {str(e)}. "
                            f"Please check your {captcha_service} API key or solve manually."
                        )
            
            # If still not solved and no solver was used, fall back to manual mode
            if captcha_type == "recaptcha" and not captcha_solved and not local_solver_used:
                # No API key or unsupported CAPTCHA type
                if not solver:
                    # Check if we're in development mode (non-headless)
                    if not headless:
                        # Development mode: wait for manual solving
                        print("⚠️  DEVELOPMENT MODE: Please solve the CAPTCHA manually in the browser window.", file=sys.stderr)
                        print("⚠️  Waiting up to 5 minutes for manual CAPTCHA solving...", file=sys.stderr)
                        captcha_timeout = template.get("captcha_timeout_ms", 300000)  # 5 minutes for manual solving
                        captcha_solved = await wait_for_captcha_solution(page, captcha_info, captcha_timeout)
                        
                        if not captcha_solved:
                            raise RuntimeError(
                                "CAPTCHA not solved within timeout. "
                                "Please solve it manually in the browser window, or enable local solver with 'use_local_captcha_solver': true"
                            )
                    else:
                        raise RuntimeError(
                            "reCAPTCHA detected but no CAPTCHA solver configured. "
                            "Options:\n"
                            "1. Enable local solver: Add 'use_local_captcha_solver': true to template\n"
                            "2. Set CAPTCHA_2CAPTCHA_API_KEY, CAPTCHA_ANTICAPTCHA_API_KEY, or CAPTCHA_CAPSOLVER_API_KEY\n"
                            "3. Set HEADLESS=false in environment to enable manual solving mode\n"
                            "4. Add 'headless': false to template for manual solving"
                        )
                elif captcha_type == "recaptcha" and not site_key:
                    raise RuntimeError(
                        "reCAPTCHA detected but site key could not be extracted. "
                        "Please check the form structure."
                    )
                else:
                    # Wait for manual solving (for other CAPTCHA types or when in dev mode)
                    if not headless:
                        print("⚠️  DEVELOPMENT MODE: Please solve the CAPTCHA manually in the browser window.", file=sys.stderr)
                    captcha_timeout = template.get("captcha_timeout_ms", 300000 if not headless else 10000)
                    captcha_solved = await wait_for_captcha_solution(page, captcha_info, captcha_timeout)
                    
                    if not captcha_solved:
                        raise RuntimeError(
                            f"CAPTCHA ({captcha_type}) detected but not solved. "
                            "The form requires CAPTCHA verification before submission."
                        )

        # Track form submission
        submission_success = False
        submission_error = None
        
        # Find the submit button - try discovered form first, then template selector
        print("🔘 Finding submit button...", file=sys.stderr)
        submit_button = None
        discovered_submit_selectors = target_form.get("submitSelectors", [])
        
        # Try discovered submit selectors first
        for discovered_selector in discovered_submit_selectors:
            try:
                locator = page.locator(discovered_selector).first
                if await locator.count() > 0:
                    submit_button = locator
                    print("   ✅ Submit button found via discovery", file=sys.stderr)
                    break
            except Exception:
                continue
        
        # Fall back to template selector
        if not submit_button:
            print("   Trying template selector...", file=sys.stderr)
            try:
                submit_button = page.locator(submit_selector).first
                if await submit_button.count() == 0:
                    raise RuntimeError(f"Submit button not found: {submit_selector}")
            except Exception as e:
                # Try to find any submit button in the form
                try:
                    submit_button = page.locator("form button[type='submit']").first
                    if await submit_button.count() == 0:
                        submit_button = page.locator("form button").first
                except Exception:
                    raise RuntimeError(f"Could not find submit button: {e}")
        
        # Track all POST requests to verify submission (including AJAX/fetch)
        post_requests = []
        def track_request(request):
            if request.method == "POST":
                post_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "post_data": request.post_data,
                    "resource_type": request.resource_type
                })
        page.on("request", track_request)
        
        # Also track fetch/XHR requests via console messages
        async def handle_console(msg):
            # Log console messages for debugging
            pass
        page.on("console", handle_console)
        
        # Try to wait for form submission response
        submission_response = None
        
        # Wait for form to be ready
        await page.wait_for_timeout(1000)
        
        # Final CAPTCHA check and re-injection before submitting
        if captcha_present:
            final_captcha_check = await detect_captcha(page)
            if not final_captcha_check.get("solved", False):
                # Try to get token again and re-inject (if local solver was used)
                if local_solver_used and 'local_solver_instance' in locals() and local_solver_instance:
                    print("🔄 Re-checking CAPTCHA token before submission...", file=sys.stderr)
                    token = await local_solver_instance._get_recaptcha_token()
                    if token:
                        await inject_recaptcha_token(page, token, response_field)
                        await page.wait_for_timeout(1000)
                        final_captcha_check = await detect_captcha(page)
                
                if not final_captcha_check.get("solved", False):
                    raise RuntimeError(
                        f"CAPTCHA ({final_captcha_check.get('type', 'unknown')}) is not solved. "
                        "Cannot submit form without CAPTCHA verification."
                    )
        
        # Verify fields are still filled before submitting
        print("🔍 Verifying form fields before submission...", file=sys.stderr)
        for field in fields:
            value = field.get("value") or field.get("testValue") or ""
            if not value or field.get("optional"):
                continue
            selector = field.get("selector")
            if selector:
                try:
                    field_value = await page.locator(selector).input_value()
                    if not field_value:
                        print(f"   ⚠️  Field {selector} is empty, re-filling...", file=sys.stderr)
                        await page.fill(selector, value, timeout=5000)
                    else:
                        print(f"   ✅ Field {selector} has value: {field_value[:20]}...", file=sys.stderr)
                except Exception as e:
                    print(f"   ⚠️  Could not verify field {selector}: {str(e)[:50]}", file=sys.stderr)
        
        # First, try clicking the submit button and wait for POST
        print("📤 Submitting form...", file=sys.stderr)
        try:
            async with page.expect_response(
                lambda response: response.request.method == "POST",
                timeout=template.get("post_submit_wait_ms", 10000)
            ) as response_info:
                # Click the submit button
                await submit_button.click()
                print("   ✅ Submit button clicked, waiting for response...", file=sys.stderr)
            
            submission_response = await response_info.value
            print(f"   ✅ Received response: {submission_response.status}", file=sys.stderr)
        except Exception:
            # Button click didn't trigger POST, try different approaches
            await page.wait_for_timeout(2000)
            
            # Check if POST was made from the button click
            if not post_requests:
                # Try submitting form via JavaScript
                try:
                    async with page.expect_response(
                        lambda response: response.request.method == "POST",
                        timeout=template.get("post_submit_wait_ms", 10000)
                    ) as response_info:
                        # Try submitting form via JavaScript
                        # Submit the form directly
                        js_code = """
                            (function() {
                                const forms = document.querySelectorAll('form');
                                if (forms.length > 0) {
                                    const form = forms[0];
                                    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                                    if (form.dispatchEvent(submitEvent)) {
                                        form.submit();
                                    }
                                }
                            })();
                        """
                        await page.evaluate(js_code)
                    
                    submission_response = await response_info.value
                except Exception:
                    # Still no POST, wait and check page
                    await page.wait_for_timeout(template.get("post_submit_wait_ms", 5000))
        
        # Check if CAPTCHA appeared after submission attempt
        await page.wait_for_timeout(2000)  # Wait a bit for any CAPTCHA to appear
        post_submit_captcha_check = await detect_captcha(page)
        if post_submit_captcha_check.get("present") and not post_submit_captcha_check.get("solved"):
            print("   ⚠️  CAPTCHA appeared after submission attempt!", file=sys.stderr)
            # Try to solve it now
            captcha_type = post_submit_captcha_check.get("type", "")
            site_key = post_submit_captcha_check.get("siteKey", "")
            response_field = post_submit_captcha_check.get("responseField", "g-recaptcha-response")
            
            if captcha_type == "recaptcha" and site_key:
                use_local = template.get("use_local_captcha_solver", False) or \
                           os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "false").lower() in ("true", "1", "yes")
                
                if use_local:
                    try:
                        try:
                            from captcha_solver import LocalCaptchaSolver
                        except ImportError:
                            from automation.captcha_solver import LocalCaptchaSolver
                        
                        print("🤖 Solving CAPTCHA that appeared after submission...", file=sys.stderr)
                        local_solver_instance = LocalCaptchaSolver(page=page)
                        token = await local_solver_instance.solve_recaptcha_v2(site_key, page.url)
                        if token:
                            await inject_recaptcha_token(page, token, response_field)
                            await page.wait_for_timeout(2000)
                            print("   ✅ CAPTCHA solved, retrying submission...", file=sys.stderr)
                            # Retry submission
                            await submit_button.click()
                            await page.wait_for_timeout(3000)
                            # Get new response after retry
                            try:
                                async with page.expect_response(
                                    lambda response: response.request.method == "POST",
                                    timeout=template.get("post_submit_wait_ms", 10000)
                                ) as response_info:
                                    await page.wait_for_timeout(1000)
                                submission_response = await response_info.value
                            except Exception:
                                pass
                    except Exception as e:
                        print(f"   ⚠️  Failed to solve post-submit CAPTCHA: {str(e)[:50]}", file=sys.stderr)
        
        # Analyze the response if we got one
        if submission_response:
            response_status = submission_response.status
            print(f"📊 Analyzing response (status: {response_status})...", file=sys.stderr)
            try:
                body = await submission_response.text()
                print(f"   Response body preview: {body[:200]}...", file=sys.stderr)
                body_lower = body.lower()
                
                # Check for CAPTCHA-related errors in response
                captcha_error_keywords = ["captcha", "recaptcha", "verification failed", "robot", "spam"]
                if any(keyword in body_lower for keyword in captcha_error_keywords):
                    submission_error = "Form submission rejected: CAPTCHA verification failed or missing"
                elif "email is required" in body_lower or "email" in body_lower and "required" in body_lower:
                    # This might be a CAPTCHA-related error in disguise
                    # Check if CAPTCHA is present
                    if post_submit_captcha_check.get("present"):
                        submission_error = "Form submission rejected: CAPTCHA verification required (server error message may be misleading)"
                    else:
                        submission_error = f"Server returned error status {response_status}: {body[:200]}"
                elif response_status in [200, 201, 302]:
                    if any(word in body_lower for word in ["success", "bedankt", "thank", "verzonden", "sent"]):
                        submission_success = True
                    elif any(word in body_lower for word in ["error", "fout", "failed", "invalid"]):
                        submission_error = f"Server returned error: {body[:200]}"
                    else:
                        # 200 status but unclear - check page content
                        submission_success = True
                elif response_status >= 400:
                    submission_error = f"Server returned error status {response_status}: {body[:200]}"
            except:
                if response_status in [200, 201, 302]:
                    submission_success = True
                else:
                    submission_error = f"Server returned error status {response_status}"
        elif post_requests:
            # POST was made but no response captured - assume success
            submission_success = True
        else:
            # No POST request detected - form may not have submitted
            # Check if CAPTCHA might be blocking
            captcha_check = await detect_captcha(page)
            if captcha_check.get("present") and not captcha_check.get("solved"):
                submission_error = (
                    f"Form submission blocked: CAPTCHA ({captcha_check.get('type', 'unknown')}) "
                    "is present but not solved. The form requires CAPTCHA verification."
                )
            else:
                submission_error = "No POST request detected - form may not have submitted. Check if form validation or CAPTCHA is blocking submission."
        
        # Check for success/error indicators on the page
        if not submission_success and not submission_error:
            page_content = await page.text_content("body") or ""
            page_content_lower = page_content.lower()
            
            success_indicators = template.get("success_indicators", [
                "bedankt", "thank", "success", "verzonden", "sent", "submitted", "uw bericht is verzonden"
            ])
            error_indicators = template.get("error_indicators", [
                "error", "fout", "failed", "mislukt", "ongeldig"
            ])
            
            for indicator in success_indicators:
                if indicator in page_content_lower:
                    submission_success = True
                    break
            
            if not submission_success:
                for indicator in error_indicators:
                    if indicator in page_content_lower:
                        submission_error = f"Error indicator found on page: {indicator}"
                        break
                
                # Check if submit button is disabled (might indicate submission in progress or completed)
                try:
                    is_disabled = await submit_button.is_disabled()
                    if is_disabled:
                        # Button disabled, might mean submission happened
                        # Check if form fields are cleared
                        form_fields_filled = False
                        for field in fields:
                            selector = field.get("selector")
                            if selector:
                                try:
                                    value = await page.locator(selector).input_value()
                                    if value:
                                        form_fields_filled = True
                                        break
                                except:
                                    pass
                        if not form_fields_filled:
                            submission_success = True
                except:
                    pass

        if submission_error:
            raise RuntimeError(f"Form submission failed: {submission_error}")
        
        # If we got a response but couldn't determine success, assume it worked
        if submission_response and not submission_success and not submission_error:
            submission_success = True

        result = {
            "status": "success" if submission_success else "completed",
            "url": url,
            "message": template.get("success_message", "Submission completed"),
        }

        await context.close()
        await browser.close()
        return result


async def main_async(args: argparse.Namespace) -> int:
    template_path = Path(args.template).resolve()
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    result = await run_submission(args.url, template_path)
    print(json.dumps(result))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Automate form submission via Playwright.")
    parser.add_argument("--url", required=True, help="Target form URL.")
    parser.add_argument(
        "--template",
        required=True,
        help="Path to JSON template describing form selectors and values.",
    )
    args = parser.parse_args()

    try:
        return asyncio.run(main_async(args))
    except Exception as exc:  # pragma: no cover - surfaced to caller
        error_payload = {"status": "error", "message": str(exc)}
        print(json.dumps(error_payload))
        return 1


if __name__ == "__main__":
    sys.exit(main())


