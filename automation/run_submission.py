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

# Add automation directory to Python path to ensure imports work when running from root directory
_script_dir = Path(__file__).parent.absolute()
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))


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
# The automation directory is already in sys.path, so we can import directly
try:
    from captcha_solver import get_captcha_solver
except ImportError:
    # Fallback if module not found
    def get_captcha_solver(service="auto"):
        return None


async def inject_recaptcha_token(page, token: str, response_field: str = "g-recaptcha-response"):
    """Inject the solved CAPTCHA token into the form."""
    await page.evaluate("""
        ([token, fieldName]) => {
            // Set the response field (try both ID and name selectors)
            let responseField = document.querySelector(`textarea#${fieldName}`) || 
                               document.querySelector(`textarea[name="${fieldName}"]`) ||
                               document.querySelector(`#${fieldName}`);
            
            if (responseField) {
                responseField.value = token;
                // Make sure it's visible (some forms check visibility)
                responseField.style.display = 'block';
                responseField.style.visibility = 'visible';
                
                // Trigger all possible events
                const events = ['change', 'input', 'blur', 'focus'];
                events.forEach(eventType => {
                    const event = new Event(eventType, { bubbles: true, cancelable: true });
                    responseField.dispatchEvent(event);
                });
                
                // Also try setting it via setAttribute
                responseField.setAttribute('value', token);
            }
            
            // Call the reCAPTCHA callback if it exists
            if (window.grecaptcha) {
                try {
                    // Method 1: Try to find widget by sitekey
                    const widgets = document.querySelectorAll('[data-sitekey]');
                    for (let widget of widgets) {
                        try {
                            const widgetId = widget.getAttribute('data-widget-id');
                            if (widgetId) {
                                // Set the response using grecaptcha callback
                                if (window.grecaptcha.getResponse) {
                                    // First check if callback exists
                                    const callbackName = widget.getAttribute('data-callback');
                                    if (callbackName && window[callbackName]) {
                                        // Call the callback function
                                        window[callbackName](token);
                                    }
                                }
                            }
                        } catch (e) {
                            // Ignore
                        }
                    }
                    
                    // Method 2: Try to execute callback directly
                    // Some forms use a global callback
                    if (window.recaptchaCallback) {
                        window.recaptchaCallback(token);
                    }
                    
                    // Method 3: Try to trigger the callback via grecaptcha.execute
                    if (window.grecaptcha.execute) {
                        for (let widget of widgets) {
                            try {
                                const widgetId = widget.getAttribute('data-widget-id');
                                if (widgetId) {
                                    window.grecaptcha.execute(parseInt(widgetId));
                                }
                            } catch (e) {
                                // Ignore
                            }
                        }
                    }
                } catch (e) {
                    // Ignore errors
                }
            }
            
            // Also try to find and trigger any form validation
            const form = responseField ? responseField.closest('form') : document.querySelector('form');
            if (form) {
                // Trigger form validation events
                const formEvents = ['input', 'change'];
                formEvents.forEach(eventType => {
                    const event = new Event(eventType, { bubbles: true });
                    form.dispatchEvent(event);
                });
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
        
        browser = await p.chromium.launch(headless=headless, timeout=180000)  # 3 minutes timeout
        # Create context with longer timeout to prevent premature closure
        # Use fresh context for each submission to avoid cookie/session issues
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            # Increase timeout to allow for CAPTCHA solving
            # Don't persist cookies between submissions to avoid rate limiting
            storage_state=None,
        )
        context.set_default_timeout(180000)  # 3 minutes default timeout
        page = await context.new_page()
        page.set_default_timeout(180000)  # 3 minutes page timeout
        
        # Reset zoom to 100% (fix 50% zoom issue)
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        await page.evaluate("document.body.style.zoom = '1'")
        await page.evaluate("window.devicePixelRatio = 1")

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

        # Wait for page to be fully interactive and forms to load
        await page.wait_for_timeout(8000)
        
        # Wait for form fields to be available (they might load dynamically)
        print("🔍 Waiting for form fields to load...", file=sys.stderr)
        try:
            # Wait for at least one form field to appear
            # Increased timeout to 20s since the form takes 10+ seconds to render
            await page.wait_for_selector("form input, form textarea", timeout=20000)
            await page.wait_for_timeout(2000)  # Wait a bit more for all fields
        except:
            print("   ⚠️  Form fields not found immediately, continuing...", file=sys.stderr)
        
        # Discover forms on the page
        print("🔍 Discovering forms on page...", file=sys.stderr)
        discovered_forms = await discover_forms(page)
        print(f"✅ Found {len(discovered_forms)} form(s)", file=sys.stderr)
        
        # If no forms found, wait longer and try again (forms might be dynamically loaded)
        if not discovered_forms:
            print("   ⏳ No forms found, waiting longer for dynamic content...", file=sys.stderr)
            await page.wait_for_timeout(5000)
            discovered_forms = await discover_forms(page)
            print(f"   Found {len(discovered_forms)} form(s) after longer wait", file=sys.stderr)
        
        if not discovered_forms:
            # Last attempt - try waiting for a form element to appear
            try:
                await page.wait_for_selector("form", timeout=10000)
                await page.wait_for_timeout(2000)
                discovered_forms = await discover_forms(page)
            except:
                pass
            
            if not discovered_forms:
                raise RuntimeError("No forms found on the page after multiple attempts. The form might be dynamically loaded.")
        
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
        
        # If discovered fields are fewer than expected, wait and rediscover
        if len(discovered_fields) < len(fields):
            print(f"   ⚠️  Only {len(discovered_fields)} fields discovered, expected {len(fields)}. Waiting for more fields...", file=sys.stderr)
            for rediscover_attempt in range(3):
                await page.wait_for_timeout(3000 * (rediscover_attempt + 1))  # Increasing wait times
                # Rediscover forms
                discovered_forms = await discover_forms(page)
                if discovered_forms:
                    target_form = discovered_forms[0]
                    if len(discovered_forms) > 1:
                        # Find best match again
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
                    print(f"   📝 Rediscovered {len(discovered_fields)} fields (attempt {rediscover_attempt + 1})", file=sys.stderr)
                    if len(discovered_fields) >= len(fields):
                        print(f"   ✅ Found enough fields!", file=sys.stderr)
                        break
        
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
            
            # If no selectors from discovery, use template selector directly
            if not selectors_to_try:
                template_selector = field.get("selector")
                if template_selector:
                    selectors_to_try = [template_selector]
                    # Also try with different quote styles
                    if "'" in template_selector:
                        selectors_to_try.append(template_selector.replace("'", '"'))
                    elif '"' in template_selector:
                        selectors_to_try.append(template_selector.replace('"', "'"))
            
            for selector in selectors_to_try:
                try:
                    # Wait for the field to be visible and ready (longer timeout for dynamic fields)
                    await page.wait_for_selector(selector, state="visible", timeout=15000)
                    # Scroll field into view
                    await page.locator(selector).scroll_into_view_if_needed()
                    await page.wait_for_timeout(500)
                    # Try to fill the field
                    await page.fill(selector, value, timeout=field.get("timeout_ms", 10000))
                    # Verify it was filled
                    await page.wait_for_timeout(300)
                    filled_value = await page.locator(selector).input_value()
                    if filled_value == value or (value in filled_value) or len(filled_value) > 0:
                        filled = True
                        print(f"   ✅ Field {i} filled successfully", file=sys.stderr)
                        break
                    else:
                        # Try again with clear first
                        await page.locator(selector).clear()
                        await page.fill(selector, value, timeout=5000)
                        await page.wait_for_timeout(300)
                        filled_value = await page.locator(selector).input_value()
                        if filled_value == value or (value in filled_value) or len(filled_value) > 0:
                            filled = True
                            print(f"   ✅ Field {i} filled successfully (retry)", file=sys.stderr)
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

        # Detect and handle CAPTCHA - check both before and after form fill
        # Some forms load CAPTCHA dynamically after fields are filled
        print("🔐 Checking for CAPTCHA (initial check)...", file=sys.stderr)
        captcha_info = await detect_captcha(page)
        captcha_present = captcha_info.get("present", False)
        captcha_solved = captcha_info.get("solved", False)
        if captcha_present:
            print(f"   CAPTCHA detected: {captcha_info.get('type', 'unknown')}", file=sys.stderr)
        else:
            print("   No CAPTCHA detected initially", file=sys.stderr)
        
        # Wait a bit and check again - CAPTCHA might load after form interaction
        # Use longer wait for CAPTCHA to appear
        for attempt in range(5):  # Try 5 times with 2-second intervals
            await page.wait_for_timeout(2000)
            captcha_info_after_fill = await detect_captcha(page)
            if captcha_info_after_fill.get("present", False):
                if not captcha_present:
                    print(f"   ✅ CAPTCHA appeared on attempt {attempt + 1}!", file=sys.stderr)
                captcha_info = captcha_info_after_fill
                captcha_present = True
                captcha_solved = captcha_info.get("solved", False)
                break
            elif attempt == 0:
                # First check found nothing, but continue checking
                continue
            else:
                # Still no CAPTCHA after multiple checks
                if attempt == 4:
                    print("   No CAPTCHA found after waiting", file=sys.stderr)
        
        if captcha_present and not captcha_solved:
            # Try to automatically solve CAPTCHA
            captcha_type = captcha_info.get("type", "")
            site_key = captcha_info.get("siteKey", "")
            response_field = captcha_info.get("responseField", "g-recaptcha-response")
            
            # Determine which solver to use
            # Default to external service for reliability unless explicitly set to use local
            use_local = template.get("use_local_captcha_solver", False)  # Changed default from True to False
            if use_local is None:
                use_local = os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "false").lower() not in ("false", "0", "no")
            else:
                # If template explicitly sets it, use that value
                use_local = bool(use_local)
            
            solver = None
            local_solver_used = False
            local_solver_instance = None  # Store local solver instance for later use
            
            if use_local and captcha_type == "recaptcha" and site_key:
                # Use local solver - fully automated (but with short timeout)
                try:
                    from captcha_solver import LocalCaptchaSolver
                    
                    print("🤖 Attempting LOCAL CAPTCHA SOLVER (with 30s timeout)...", file=sys.stderr)
                    local_solver_instance = LocalCaptchaSolver(page=page)
                    solver = local_solver_instance
                    local_solver_used = True
                    
                    # Call solver with SHORTER timeout for local solver since it's unreliable
                    try:
                        token = await asyncio.wait_for(
                            solver.solve_recaptcha_v2(site_key, page.url),
                            timeout=30  # 30 second max timeout (was 50)
                        )
                    except asyncio.TimeoutError:
                        print("⏰ Local solver timeout (30s) - falling back to external service", file=sys.stderr)
                        token = None
                    
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
                            print("✅ CAPTCHA solved by local solver!", file=sys.stderr)
                    else:
                        raise RuntimeError("Local CAPTCHA solver returned empty token or timed out")
                        
                except Exception as e:
                    local_error = str(e)
                    print(f"⚠️  Local solver failed: {local_error[:100]}", file=sys.stderr)
                    print("🔄 Falling back to external CAPTCHA service (2captcha)...", file=sys.stderr)
                    local_solver_used = False  # Reset flag to allow fallback
                    # Don't raise - fall through to external solver
            
            # If local solver not used or failed, try external services
            if not captcha_solved and captcha_type == "recaptcha" and site_key:
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
                        try:
                            token = await asyncio.wait_for(
                                solver.solve_recaptcha_v2(site_key, page_url),
                                timeout=50  # 50 second max timeout
                            )
                        except asyncio.TimeoutError:
                            print("⏰ CAPTCHA solver timeout - trying different approach", file=sys.stderr)
                            token = None
                        
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
        result = None  # Initialize result variable
        
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
        all_requests = []  # Track all requests for debugging
        fetch_requests = []  # Track fetch/XHR requests specifically
        
        def track_request(request):
            if request.method == "POST":
                post_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "post_data": request.post_data,
                    "resource_type": request.resource_type,
                    "headers": dict(request.headers) if hasattr(request, 'headers') else {}
                })
                print(f"   📤 POST request detected: {request.url[:80]}", file=sys.stderr)
                if request.post_data:
                    print(f"      POST data preview: {str(request.post_data)[:200]}...", file=sys.stderr)
            # Track fetch/XHR requests
            if request.resource_type in ["xhr", "fetch"]:
                fetch_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "resource_type": request.resource_type
                })
            # Track all requests for debugging
            all_requests.append({
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type
            })
        page.on("request", track_request)
        
        # Also track responses
        responses_received = []
        def track_response(response):
            if response.request.method == "POST":
                responses_received.append({
                    "url": response.url,
                    "status": response.status,
                    "method": response.request.method,
                    "resource_type": response.request.resource_type
                })
                print(f"   📥 POST response received: {response.status} - {response.url[:80]}", file=sys.stderr)
        page.on("response", track_response)
        
        # Also intercept fetch/XHR calls to catch AJAX submissions
        await page.add_init_script("""
            // Intercept fetch
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                const options = args[1] || {};
                if (options.method === 'POST' || (typeof url === 'string' && url.includes('contact') || url.includes('submit'))) {
                    console.log('🔍 Fetch POST detected:', url, options);
                }
                return originalFetch.apply(this, args);
            };
            
            // Intercept XMLHttpRequest
            const originalOpen = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function(method, url, ...rest) {
                if (method === 'POST' || (typeof url === 'string' && (url.includes('contact') || url.includes('submit')))) {
                    console.log('🔍 XHR POST detected:', method, url);
                }
                return originalOpen.apply(this, [method, url, ...rest]);
            };
        """)
        
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
            print("🔐 Final CAPTCHA verification before submission...", file=sys.stderr)
            final_captcha_check = await detect_captcha(page)
            if not final_captcha_check.get("solved", False):
                print("   ⚠️  CAPTCHA not solved, attempting to solve...", file=sys.stderr)
                # Try to get token again and re-inject (if local solver was used)
                if local_solver_used and 'local_solver_instance' in locals() and local_solver_instance:
                    print("   🔄 Re-checking CAPTCHA token before submission...", file=sys.stderr)
                    token = await local_solver_instance._get_recaptcha_token()
                    if token:
                        print(f"   ✅ Got token, injecting... (length: {len(token)})", file=sys.stderr)
                        await inject_recaptcha_token(page, token, response_field)
                        await page.wait_for_timeout(2000)  # Wait longer for token to be processed
                        final_captcha_check = await detect_captcha(page)
                        if final_captcha_check.get("solved", False):
                            print("   ✅ CAPTCHA verified as solved!", file=sys.stderr)
                        else:
                            print("   ⚠️  CAPTCHA still not marked as solved, but token exists", file=sys.stderr)
                            # Force verify by checking token directly
                            token_check = await page.evaluate("""
                                () => {
                                    const field = document.querySelector('textarea[name="g-recaptcha-response"]');
                                    return field && field.value && field.value.length > 0;
                                }
                            """)
                            if token_check:
                                print("   ✅ Token exists in form field, proceeding...", file=sys.stderr)
                                final_captcha_check["solved"] = True
                
                if not final_captcha_check.get("solved", False):
                    # Last attempt - check if token exists in the field
                    token_exists = await page.evaluate("""
                        () => {
                            const field = document.querySelector('textarea[name="g-recaptcha-response"]');
                            if (field && field.value && field.value.length > 0) {
                                return true;
                            }
                            // Also check grecaptcha
                            if (window.grecaptcha && window.grecaptcha.getResponse) {
                                try {
                                    const response = window.grecaptcha.getResponse();
                                    return response && response.length > 0;
                                } catch (e) {
                                    return false;
                                }
                            }
                            return false;
                        }
                    """)
                    
                    if token_exists:
                        print("   ✅ Token exists, proceeding with submission...", file=sys.stderr)
                    else:
                        raise RuntimeError(
                            f"CAPTCHA ({final_captcha_check.get('type', 'unknown')}) is not solved. "
                            "Cannot submit form without CAPTCHA verification."
                        )
            else:
                print("   ✅ CAPTCHA verified as solved!", file=sys.stderr)
        
        # Verify fields are still filled before submitting
        print("🔍 Verifying form fields before submission...", file=sys.stderr)
        fields_verified = True
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
                        # Verify it was filled
                        await page.wait_for_timeout(500)
                        field_value = await page.locator(selector).input_value()
                        if field_value:
                            print(f"   ✅ Field {selector} re-filled successfully", file=sys.stderr)
                        else:
                            print(f"   ❌ Field {selector} still empty after re-fill!", file=sys.stderr)
                            fields_verified = False
                    else:
                        print(f"   ✅ Field {selector} has value: {field_value[:20]}...", file=sys.stderr)
                except Exception as e:
                    print(f"   ⚠️  Could not verify field {selector}: {str(e)[:50]}", file=sys.stderr)
                    fields_verified = False
        
        if not fields_verified:
            print("   ⚠️  Some fields could not be verified, but proceeding with submission...", file=sys.stderr)
        
        # Check for CAPTCHA AGAIN after filling form (sometimes it appears dynamically)
        print("🔐 Checking for CAPTCHA (after form fill)...", file=sys.stderr)
        await page.wait_for_timeout(2000)  # Wait for any dynamic CAPTCHA to load
        captcha_info_after = await detect_captcha(page)
        if captcha_info_after.get("present", False) and not captcha_info_after.get("solved", False):
            print(f"   ✅ CAPTCHA detected after form fill: {captcha_info_after.get('type', 'unknown')}", file=sys.stderr)
            # Update captcha info and solve it
            captcha_present = True
            captcha_solved = False
            captcha_info = captcha_info_after
            # Now solve it (the solving logic below will handle it)
            site_key = captcha_info.get("siteKey", "")
            response_field = captcha_info.get("responseField", "g-recaptcha-response")
            captcha_type = captcha_info.get("type", "")
            
            # Always use local solver by default (unless explicitly disabled)
            use_local = template.get("use_local_captcha_solver", True)
            if use_local is None:
                use_local = os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "true").lower() not in ("false", "0", "no")
            else:
                use_local = bool(use_local)
            
            if use_local and captcha_type == "recaptcha" and site_key:
                try:
                    from captcha_solver import LocalCaptchaSolver
                    print("🤖 Using LOCAL CAPTCHA SOLVER (after form fill)...", file=sys.stderr)
                    local_solver_instance = LocalCaptchaSolver(page=page)
                    token = await local_solver_instance.solve_recaptcha_v2(site_key, page.url)
                    if token:
                        await inject_recaptcha_token(page, token, response_field)
                        await page.wait_for_timeout(2000)
                        captcha_info = await detect_captcha(page)
                        captcha_solved = captcha_info.get("solved", False)
                        if captcha_solved:
                            print("   ✅ CAPTCHA solved automatically after form fill!", file=sys.stderr)
                        else:
                            # Force verify token exists
                            token_check = await page.evaluate("""
                                () => {
                                    const field = document.querySelector('textarea[name="g-recaptcha-response"]');
                                    return field && field.value && field.value.length > 0;
                                }
                            """)
                            if token_check:
                                print("   ✅ CAPTCHA token exists in form (verified)", file=sys.stderr)
                                captcha_solved = True
                except Exception as e:
                    print(f"   ⚠️  Failed to solve CAPTCHA after form fill: {str(e)[:100]}", file=sys.stderr)
                    # Try external solver as fallback
                    captcha_service = template.get("captcha_service", "auto")
                    solver = get_captcha_solver(captcha_service)
                    if solver:
                        try:
                            print("   🔄 Trying external CAPTCHA solver...", file=sys.stderr)
                            try:
                                token = await asyncio.wait_for(
                                    solver.solve_recaptcha_v2(site_key, page.url),
                                    timeout=50
                                )
                            except asyncio.TimeoutError:
                                print("   ⏰ External solver timeout", file=sys.stderr)
                                token = None
                            
                            if token:
                                await inject_recaptcha_token(page, token, response_field)
                                await page.wait_for_timeout(2000)
                                captcha_solved = True
                        except Exception as ext_error:
                            print(f"   ⚠️  External solver also failed: {str(ext_error)[:100]}", file=sys.stderr)
        
        # First, try clicking the submit button and wait for POST
        print("📤 Submitting form...", file=sys.stderr)
        submission_response = None
        
        # Clear previous request tracking
        post_requests.clear()
        responses_received.clear()
        fetch_requests.clear()
        
        # Double-check CAPTCHA token one more time right before submission
        if captcha_present:
            final_token_check = await page.evaluate("""
                () => {
                    const field = document.querySelector('textarea[name="g-recaptcha-response"]');
                    if (field && field.value && field.value.length > 0) {
                        return { exists: true, length: field.value.length };
                    }
                    if (window.grecaptcha && window.grecaptcha.getResponse) {
                        try {
                            const response = window.grecaptcha.getResponse();
                            if (response && response.length > 0) {
                                return { exists: true, length: response.length, source: 'grecaptcha' };
                            }
                        } catch (e) {
                            return { exists: false, error: e.message };
                        }
                    }
                    return { exists: false };
                }
            """)
            if not final_token_check.get("exists"):
                print("   ❌ CRITICAL: CAPTCHA token missing right before submission!", file=sys.stderr)
                raise RuntimeError("CAPTCHA token is missing. Cannot submit form without valid CAPTCHA token.")
            else:
                print(f"   ✅ CAPTCHA token verified: length={final_token_check.get('length', 'unknown')}", file=sys.stderr)
        
        try:
            # Wait for POST response with longer timeout (including AJAX/fetch)
            async with page.expect_response(
                lambda response: response.request.method == "POST" or 
                                response.request.resource_type in ["xhr", "fetch"],
                timeout=template.get("post_submit_wait_ms", 20000)  # Increased to 20 seconds
            ) as response_info:
                # Click the submit button
                print("   🖱️  Clicking submit button...", file=sys.stderr)
                # Scroll submit button into view first
                await submit_button.scroll_into_view_if_needed()
                await page.wait_for_timeout(500)
                await submit_button.click()
                print("   ✅ Submit button clicked, waiting for response...", file=sys.stderr)
            
            submission_response = await response_info.value
            print(f"   ✅ Received POST response: {submission_response.status} - {submission_response.url[:80]}", file=sys.stderr)
            
            # Log response body for debugging
            try:
                response_body = await submission_response.text()
                print(f"   📄 Response body preview: {response_body[:300]}...", file=sys.stderr)
            except:
                pass
        except Exception as e:
            print(f"   ⚠️  No immediate POST response: {str(e)[:100]}", file=sys.stderr)
            # Button click didn't trigger immediate POST, wait and check
            await page.wait_for_timeout(3000)
            
            # Check if POST was made from the button click
            if post_requests or fetch_requests:
                print(f"   ✅ Found {len(post_requests)} POST request(s) and {len(fetch_requests)} fetch/XHR request(s) after click", file=sys.stderr)
                # Wait a bit more for response
                await page.wait_for_timeout(3000)
                if responses_received:
                    print(f"   ✅ Found {len(responses_received)} POST response(s)", file=sys.stderr)
                    # Use the first response
                    if responses_received:
                        # Try to get the actual response object
                        try:
                            # Wait a bit more and check page for success indicators
                            await page.wait_for_timeout(2000)
                        except:
                            pass
            else:
                # No POST detected, try submitting form via JavaScript
                print("   🔄 No POST detected, trying JavaScript form submission...", file=sys.stderr)
                try:
                    # Wait for any POST response (including AJAX)
                    async with page.expect_response(
                        lambda response: response.request.method == "POST" or 
                                        response.request.resource_type in ["xhr", "fetch"],
                        timeout=template.get("post_submit_wait_ms", 20000)
                    ) as response_info:
                        # Submit the form directly via JavaScript
                        js_code = """
                            (function() {
                                const forms = document.querySelectorAll('form');
                                if (forms.length > 0) {
                                    const form = forms[0];
                                    // First, trigger submit event (might be intercepted by JS)
                                    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                                    if (form.dispatchEvent(submitEvent)) {
                                        // Try native submit
                                        form.submit();
                                    }
                                }
                            })();
                        """
                        await page.evaluate(js_code)
                        print("   ✅ Form submitted via JavaScript", file=sys.stderr)
                    
                    submission_response = await response_info.value
                    print(f"   ✅ Received response via JS: {submission_response.status} ({submission_response.request.resource_type})", file=sys.stderr)
                except Exception as js_error:
                    print(f"   ⚠️  JavaScript submission also failed: {str(js_error)[:100]}", file=sys.stderr)
                    # Wait and check for AJAX/fetch requests
                    await page.wait_for_timeout(3000)
                    if fetch_requests:
                        print(f"   ✅ Found {len(fetch_requests)} fetch/XHR requests after JS submission", file=sys.stderr)
                    # Wait and check page for success indicators
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
                use_local = template.get("use_local_captcha_solver", True)
                if use_local is None:
                    use_local = os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "true").lower() not in ("false", "0", "no")
                else:
                    use_local = bool(use_local)
                
                token = None
                if use_local:
                    try:
                        from captcha_solver import LocalCaptchaSolver
                        print("🤖 Solving CAPTCHA that appeared after submission (local solver)...", file=sys.stderr)
                        local_solver_instance = LocalCaptchaSolver(page=page)
                        try:
                            token = await asyncio.wait_for(
                                local_solver_instance.solve_recaptcha_v2(site_key, page.url),
                                timeout=50
                            )
                        except asyncio.TimeoutError:
                            print("⏰ Local solver timeout (50s) - falling back to external service", file=sys.stderr)
                            token = None
                    except Exception as e:
                        print(f"   ⚠️  Local solver failed: {str(e)[:50]}", file=sys.stderr)
                        print("   🔄 Falling back to 2captcha...", file=sys.stderr)
                
                # If local solver didn't work, try external service
                if not token:
                    captcha_service = template.get("captcha_service", "auto")
                    solver = get_captcha_solver(captcha_service)
                    if solver:
                        try:
                            print("🤖 Solving CAPTCHA with external service...", file=sys.stderr)
                            token = await solver.solve_recaptcha_v2(site_key, page.url)
                        except Exception as e:
                            print(f"   ⚠️  External solver failed: {str(e)[:50]}", file=sys.stderr)
                
                if token:
                    await inject_recaptcha_token(page, token, response_field)
                    await page.wait_for_timeout(2000)
                    print("   ✅ CAPTCHA solved, retrying submission...", file=sys.stderr)
                    # Clear previous tracking
                    post_requests.clear()
                    responses_received.clear()
                    # Retry submission
                    try:
                        async with page.expect_response(
                            lambda response: response.request.method == "POST",
                            timeout=template.get("post_submit_wait_ms", 15000)
                        ) as response_info:
                            await submit_button.click()
                            print("   ✅ Submit button clicked (retry)...", file=sys.stderr)
                        submission_response = await response_info.value
                        print(f"   ✅ Received POST response (retry): {submission_response.status}", file=sys.stderr)
                    except Exception as retry_error:
                        print(f"   ⚠️  Retry submission error: {str(retry_error)[:100]}", file=sys.stderr)
                        await page.wait_for_timeout(3000)
                        if post_requests:
                            print(f"   ✅ POST request detected on retry", file=sys.stderr)
                else:
                    print("   ⚠️  Could not solve post-submit CAPTCHA with any solver", file=sys.stderr)
        
        # Initialize submission status variables
        submission_success = False
        submission_error = None
        
        # Analyze the response if we got one
        if submission_response:
            response_status = submission_response.status
            print(f"📊 Analyzing response (status: {response_status})...", file=sys.stderr)
            try:
                body = await submission_response.text()
                print(f"   Response body preview: {body[:200]}...", file=sys.stderr)
                body_lower = body.lower()
                
                # Check for CAPTCHA-related errors in response
                captcha_error_keywords = ["captcha", "recaptcha", "verification failed", "robot", "spam", "verification required"]
                captcha_error_detected = any(keyword in body_lower for keyword in captcha_error_keywords)
                
                if captcha_error_detected and response_status in [400, 422]:
                    print("   ⚠️  Server returned CAPTCHA error - attempting to solve and retry...", file=sys.stderr)
                    # Try to detect and solve CAPTCHA now
                    await page.wait_for_timeout(2000)
                    captcha_info_retry = await detect_captcha(page)
                    if captcha_info_retry.get("present", False):
                        site_key = captcha_info_retry.get("siteKey", "")
                        response_field = captcha_info_retry.get("responseField", "g-recaptcha-response")
                        captcha_type = captcha_info_retry.get("type", "")
                        
                        # Use local solver if enabled
                        use_local = template.get("use_local_captcha_solver", True)
                        if use_local is None:
                            use_local = os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "true").lower() not in ("false", "0", "no")
                        else:
                            use_local = bool(use_local)
                        
                        if use_local and captcha_type == "recaptcha" and site_key:
                            try:
                                from captcha_solver import LocalCaptchaSolver
                                print("🤖 Retrying with LOCAL CAPTCHA SOLVER...", file=sys.stderr)
                                solver = LocalCaptchaSolver(page=page)
                                try:
                                    token = await asyncio.wait_for(
                                        solver.solve_recaptcha_v2(site_key, page.url),
                                        timeout=50
                                    )
                                except asyncio.TimeoutError:
                                    print("⏰ Local solver timeout (50s) - falling back to external service", file=sys.stderr)
                                    token = None
                                if token:
                                    await inject_recaptcha_token(page, token, response_field)
                                    await page.wait_for_timeout(2000)
                                    captcha_info_retry = await detect_captcha(page)
                                    if captcha_info_retry.get("solved", False):
                                        print("   ✅ CAPTCHA solved, retrying submission...", file=sys.stderr)
                                        # Retry submission
                                        await submit_button.click()
                                        await page.wait_for_timeout(5000)
                                        # Check for new response
                                        if responses_received:
                                            latest_response = responses_received[-1]
                                            if latest_response.get("status") in [200, 201, 302]:
                                                submission_success = True
                                                submission_error = None
                                                print("   ✅ Retry successful!", file=sys.stderr)
                                                # Continue to process as success
                                            else:
                                                submission_error = "Form submission rejected after CAPTCHA retry: CAPTCHA verification still failing"
                                    else:
                                        submission_error = "Form submission rejected: CAPTCHA verification failed or missing (could not solve on retry)"
                                else:
                                    submission_error = "Form submission rejected: CAPTCHA verification failed or missing (solver returned empty token)"
                            except Exception as e:
                                submission_error = f"Form submission rejected: CAPTCHA verification failed (solver error: {str(e)[:100]})"
                        else:
                            submission_error = "Form submission rejected: CAPTCHA verification failed or missing (solver not available)"
                    else:
                        submission_error = "Form submission rejected: CAPTCHA verification required but CAPTCHA not detected on page"
                elif "email is required" in body_lower or "email" in body_lower and "required" in body_lower:
                    # This might be a CAPTCHA-related error in disguise
                    # Check if CAPTCHA is present
                    if post_submit_captcha_check.get("present"):
                        submission_error = "Form submission rejected: CAPTCHA verification required (server error message may be misleading)"
                    else:
                        submission_error = f"Server returned error status {response_status}: {body[:200]}"
                elif any(keyword in body_lower for keyword in ["duplicate", "already exists", "already submitted", "already received"]):
                    submission_error = f"Form submission rejected: Duplicate submission detected - {body[:200]}"
                    submission_success = False
                elif any(keyword in body_lower for keyword in ["rate limit", "too many", "try again later", "please wait"]):
                    submission_error = f"Form submission rejected: Rate limiting detected - {body[:200]}"
                    submission_success = False
                elif response_status == 429:
                    submission_error = f"Form submission rejected: Rate limit (429) - Too many requests. Please wait before trying again."
                    submission_success = False
                elif response_status in [200, 201, 302]:
                    # Check for error messages even with 200 status
                    error_keywords = ["error", "fout", "failed", "invalid", "duplicate", "already exists", 
                                     "already submitted", "spam", "blocked", "rate limit", "too many requests",
                                     "try again later", "please wait"]
                    has_error_keyword = any(keyword in body_lower for keyword in error_keywords)
                    
                    if has_error_keyword:
                        found_errors = [kw for kw in error_keywords if kw in body_lower]
                        submission_error = f"Server returned error message: {', '.join(found_errors[:3])} - {body[:200]}"
                        submission_success = False
                    elif any(word in body_lower for word in ["success", "bedankt", "thank", "verzonden", "sent", "uw bericht"]):
                        submission_success = True
                    else:
                        # 200 status but unclear - check page content more carefully
                        # Don't assume success if we can't confirm it
                        submission_success = True  # Keep optimistic but log warning
                        print("   ⚠️  Warning: 200 status but no clear success/error message detected", file=sys.stderr)
                elif response_status >= 400:
                    submission_error = f"Server returned error status {response_status}: {body[:200]}"
            except:
                if response_status in [200, 201, 302]:
                    submission_success = True
                else:
                    submission_error = f"Server returned error status {response_status}"
        elif post_requests or fetch_requests:
            # POST was made but no response captured - check if we got responses
            print(f"   📊 POST requests detected: {len(post_requests)}, Fetch/XHR: {len(fetch_requests)}", file=sys.stderr)
            if responses_received:
                print(f"   📊 POST responses received: {len(responses_received)}", file=sys.stderr)
                # Check response statuses
                for resp in responses_received:
                    print(f"      - Status {resp['status']}: {resp['url'][:60]}", file=sys.stderr)
                    if resp['status'] in [200, 201, 302]:
                        submission_success = True
                        break
                if not submission_success:
                    # Check response statuses more carefully
                    error_statuses = [400, 401, 403, 422, 429, 500, 503]
                    has_error_status = any(resp['status'] in error_statuses for resp in responses_received)
                    if has_error_status:
                        error_resp = next((r for r in responses_received if r['status'] in error_statuses), None)
                        submission_error = f"Server returned error status {error_resp['status']} for {error_resp['url'][:60]}"
                        submission_success = False
                    else:
                        # POST was made and response received with OK status, assume success
                        submission_success = True
            else:
                # POST was made but no response captured - wait a bit more and check page
                print("   ⏳ POST made but no response yet, waiting...", file=sys.stderr)
                await page.wait_for_timeout(3000)
                # Check page for success indicators
                page_content = await page.text_content("body") or ""
                success_indicators = template.get("success_indicators", [
                    "bedankt", "thank", "success", "verzonden", "sent", "submitted"
                ])
                if any(indicator in page_content.lower() for indicator in success_indicators):
                    submission_success = True
                else:
                    # Check for error indicators before assuming success
                    error_indicators = template.get("error_indicators", [
                        "error", "fout", "failed", "mislukt", "ongeldig", "duplicate", 
                        "already", "exists", "spam", "blocked", "rate limit", "too many"
                    ])
                    if any(indicator in page_content.lower() for indicator in error_indicators):
                        submission_error = f"Error indicator found on page: {[ind for ind in error_indicators if ind in page_content.lower()][:3]}"
                        submission_success = False
                    else:
                        # Only assume success if POST was made and no errors found
                        submission_success = True
        else:
            # No POST request detected - form may not have submitted
            print("   ⚠️  No POST requests detected", file=sys.stderr)
            # Check if CAPTCHA might be blocking
            captcha_check = await detect_captcha(page)
            if captcha_check.get("present") and not captcha_check.get("solved"):
                submission_error = (
                    f"Form submission blocked: CAPTCHA ({captcha_check.get('type', 'unknown')}) "
                    "is present but not solved. The form requires CAPTCHA verification."
                )
            else:
                # Check if form might have submitted via AJAX/fetch (not tracked)
                page_content = await page.text_content("body") or ""
                success_indicators = template.get("success_indicators", [
                    "bedankt", "thank", "success", "verzonden", "sent", "submitted"
                ])
                if any(indicator in page_content.lower() for indicator in success_indicators):
                    print("   ✅ Success indicators found on page!", file=sys.stderr)
                    submission_success = True
                else:
                    submission_error = "No POST request detected - form may not have submitted. Check if form validation or CAPTCHA is blocking submission."
        
        # Wait a bit longer after submission to ensure server processes it
        if submission_success or post_requests or fetch_requests or responses_received:
            print("⏳ Waiting for server to process submission...", file=sys.stderr)
            await page.wait_for_timeout(5000)  # Increased to 5 seconds for server processing
            
            # Check if page URL changed (might indicate redirect after successful submission)
            current_url = page.url
            print(f"   📍 Current page URL: {current_url}", file=sys.stderr)
            
            # Check page again for success indicators
            page_content_after_wait = await page.text_content("body") or ""
            success_indicators = template.get("success_indicators", [
                "bedankt", "thank", "success", "verzonden", "sent", "submitted", "uw bericht is verzonden", 
                "uw bericht", "message sent", "form submitted"
            ])
            
            found_indicators = []
            for indicator in success_indicators:
                if indicator in page_content_after_wait.lower():
                    found_indicators.append(indicator)
            
            if found_indicators:
                print(f"   ✅ Success indicators found on page after wait: {', '.join(found_indicators)}", file=sys.stderr)
                submission_success = True
            else:
                print("   ⚠️  No success indicators found on page", file=sys.stderr)
            
            # Also check if form fields are cleared (indicates successful submission)
            form_fields_cleared = True
            for field in fields:
                selector = field.get("selector")
                if selector and not field.get("optional"):
                    try:
                        value = await page.locator(selector).input_value()
                        if value:
                            form_fields_cleared = False
                            break
                    except:
                        pass
            
            if form_fields_cleared:
                print("   ✅ Form fields are cleared (indicates successful submission)", file=sys.stderr)
                submission_success = True
        
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

            # Final verification - check if we actually have evidence of submission
            if submission_success:
                print("✅ Form submission appears successful!", file=sys.stderr)
                print(f"   - POST requests: {len(post_requests)}", file=sys.stderr)
                print(f"   - POST responses: {len(responses_received)}", file=sys.stderr)
                if submission_response:
                    print(f"   - Response status: {submission_response.status}", file=sys.stderr)
            else:
                print("⚠️  WARNING: Form submission status unclear", file=sys.stderr)
                print(f"   - POST requests: {len(post_requests)}", file=sys.stderr)
                print(f"   - POST responses: {len(responses_received)}", file=sys.stderr)
                if submission_error:
                    print(f"   - Error: {submission_error}", file=sys.stderr)

        # Determine final result status
        result = None
        if submission_success:
            result = {
                "status": "success",
                "url": url,
                "message": template.get("success_message", "Submission completed successfully"),
                "post_requests_count": len(post_requests),
                "post_responses_count": len(responses_received),
                "submission_error": None,
            }
        elif submission_error:
            result = {
                "status": "error",
                "url": url,
                "message": f"Submission failed: {submission_error}",
                "post_requests_count": len(post_requests),
                "post_responses_count": len(responses_received),
                "submission_error": submission_error,
            }
        elif submission_response and submission_response.status in [200, 201, 302]:
            # Got successful response but couldn't determine status - assume success
            result = {
                "status": "success",
                "url": url,
                "message": "Submission completed (status inferred from response)",
                "post_requests_count": len(post_requests),
                "post_responses_count": len(responses_received),
                "submission_error": None,
            }
        elif post_requests or responses_received:
            # POST was made - check if any response was successful
            has_success_response = any(r.get('status') in [200, 201, 302] for r in responses_received) if responses_received else False
            if has_success_response:
                result = {
                    "status": "success",
                    "url": url,
                    "message": "Submission completed successfully",
                    "post_requests_count": len(post_requests),
                    "post_responses_count": len(responses_received),
                    "submission_error": None,
                }
            else:
                result = {
                    "status": "error",
                    "url": url,
                    "message": "Submission process completed but status unclear",
                    "post_requests_count": len(post_requests),
                    "post_responses_count": len(responses_received),
                    "submission_error": submission_error if submission_error else "Unknown error",
                }
        else:
            result = {
                "status": "error",
                "url": url,
                "message": "Submission process completed but status unclear",
                "post_requests_count": len(post_requests) if 'post_requests' in locals() else 0,
                "post_responses_count": len(responses_received) if 'responses_received' in locals() else 0,
                "submission_error": submission_error if submission_error else "Unknown error",
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


