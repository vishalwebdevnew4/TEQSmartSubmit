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
    from captcha_solver import get_captcha_solver, LocalCaptchaSolver
except ImportError:
    # Fallback if module not found
    def get_captcha_solver(service="auto"):
        return None
    LocalCaptchaSolver = None  # Type placeholder


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
                    
                    // Check if field is actually visible (not hidden by CSS or display:none)
                    const rect = input.getBoundingClientRect();
                    const style = window.getComputedStyle(input);
                    const isVisible = rect.width > 0 && rect.height > 0 && 
                                     style.display !== 'none' && 
                                     style.visibility !== 'hidden' &&
                                     style.opacity !== '0';
                    
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
                        // Look for label text near the input
                        const parent = input.parentElement;
                        if (parent) {
                            const labelInParent = parent.querySelector('label');
                            if (labelInParent) return labelInParent.textContent.trim();
                        }
                        return '';
                    })();
                    
                    // Get options for select elements
                    let options = [];
                    if (tagName === 'select') {
                        options = Array.from(input.options).map(opt => ({
                            value: opt.value,
                            text: opt.text.trim(),
                            selected: opt.selected
                        }));
                    }
                    
                    // Get value for radio/checkbox
                    const value = input.value || '';
                    const checked = input.checked || false;
                    
                    // Generate possible selectors
                    const selectors = [];
                    if (name) {
                        selectors.push(`${tagName}[name="${name}"]`);
                        if (type) {
                            selectors.push(`${tagName}[name="${name}"][type="${type}"]`);
                        }
                        if (value && (type === 'radio' || type === 'checkbox')) {
                            selectors.push(`${tagName}[name="${name}"][value="${value}"]`);
                        }
                    }
                    if (id) selectors.push(`#${id}`);
                    if (placeholder) selectors.push(`${tagName}[placeholder="${placeholder}"]`);
                    
                    return {
                        tagName,
                        type,
                        name,
                        id,
                        placeholder,
                        label,
                        value: value,
                        checked: checked,
                        options: options,
                        required: input.hasAttribute('required'),
                        selectors: selectors,
                        index: index,
                        isVisible: isVisible,
                        isHidden: type === 'hidden' || !isVisible,
                        multiple: input.hasAttribute('multiple') || (tagName === 'select' && input.multiple)
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
    
    # Normalize template name for comparison
    template_name_normalized = template_name.lower().strip() if template_name else ""
    
    for field in discovered_fields:
        field_name = field.get("name", "").lower().strip()
        field_label = field.get("label", "").lower()
        field_placeholder = field.get("placeholder", "").lower()
        field_type = field.get("type", "").lower()
        field_tag = field.get("tagName", "").lower()
        
        # Skip hidden fields, CSRF tokens, and honeypot fields
        field_is_hidden = field.get("isHidden", False) or field.get("type", "").lower() == "hidden"
        if (field_is_hidden or
            field_type == "hidden" or 
            "_token" in field_name or 
            "csrf" in field_name or 
            "token" in field_name or
            field_name == "website" or  # Common honeypot field name
            "honeypot" in field_name.lower()):
            continue
        
        # Priority 1: Exact name match (most reliable)
        if template_name_normalized and field_name and template_name_normalized == field_name:
            return field
        
        # Priority 2: Exact selector match
        if template_selector:
            for sel in field.get("selectors", []):
                # Normalize selectors for comparison (remove quote differences)
                sel_normalized = sel.replace('"', "'").lower()
                template_sel_normalized = template_selector.replace('"', "'").lower()
                if sel_normalized == template_sel_normalized:
                    return field
        
        # Priority 3: Check if template selector contains the exact field name attribute
        # e.g., template_selector = "input[name='name']" should match field with name="name"
        if template_selector and field_name:
            # Extract the name from template selector
            import re
            template_name_in_selector = re.search(r"name=['\"]([^'\"]+)['\"]", template_selector, re.IGNORECASE)
            if template_name_in_selector:
                extracted_name = template_name_in_selector.group(1).lower().strip()
                if extracted_name == field_name:
                    return field
        
        # Priority 4: Check if field selector contains template name (but be careful - avoid partial matches)
        # Only match if the template name is a complete word in the selector
        if template_name_normalized and field_name:
            for sel in field.get("selectors", []):
                sel_lower = sel.lower()
                # Check if template name appears as a complete attribute value, not just as a substring
                # e.g., "name='name'" should match, but "name='website'" should NOT match "name"
                if f"name=['\"]{template_name_normalized}['\"]" in sel_lower:
                    return field
    
    return None


def auto_detect_field_type(field: Dict) -> str | None:
    """Auto-detect what type of field this is (name, email, phone, message, etc.) based on common patterns."""
    field_name = field.get("name", "").lower().strip()
    field_label = field.get("label", "").lower().strip()
    field_placeholder = field.get("placeholder", "").lower().strip()
    field_type = field.get("type", "").lower().strip()
    field_id = field.get("id", "").lower().strip()
    field_tag = field.get("tagName", "").lower().strip()
    
    # Skip hidden fields, tokens, and honeypot fields
    field_is_hidden = field.get("isHidden", False) or field.get("type", "").lower() == "hidden"
    if (field_is_hidden or
        field_type == "hidden" or 
        "_token" in field_name or 
        "csrf" in field_name or 
        "token" in field_name or
        field_name == "website" or  # Common honeypot field
        "honeypot" in field_name or
        "from_url" in field_name or  # Common tracking field
        "curnt_url" in field_name or
        field_type == "file"):  # Skip file uploads for now
        return None
    
    # Combine all text for matching
    all_text = f"{field_name} {field_label} {field_placeholder} {field_id}"
    
    # Email field patterns (check type first - most reliable)
    if field_type == "email" or "email" in all_text or "e-mail" in all_text or "mail" in all_text:
        return "email"
    
    # Phone field patterns
    if field_type == "tel" or "phone" in all_text or "mobile" in all_text or "telephone" in all_text:
        return "phone"
    
    # URL/Website field patterns
    if field_type == "url" or "url" in all_text or "website" in all_text or "web" in all_text:
        return "url"
    
    # Name field patterns
    if any(pattern in all_text for pattern in ["name", "fullname", "full name", "firstname", "first name", "lastname", "last name"]):
        return "name"
    
    # Message/comment field patterns
    if field_tag == "textarea" or any(pattern in all_text for pattern in ["message", "comment", "notes", "description", "details", "inquiry", "query"]):
        return "message"
    
    # Subject field patterns
    if "subject" in all_text or "topic" in all_text:
        return "subject"
    
    # Company field patterns
    if "company" in all_text or "organization" in all_text or "org" in all_text:
        return "company"
    
    # Date fields
    if field_type in ["date", "datetime-local", "month", "week"]:
        return "date"
    
    # Time fields
    if field_type == "time":
        return "time"
    
    # Number fields
    if field_type == "number" or "number" in all_text or "quantity" in all_text or "amount" in all_text:
        return "number"
    
    # Password fields (usually skip, but can detect)
    if field_type == "password":
        return "password"
    
    # Select dropdowns - try to detect type from options or name
    if field_tag == "select":
        options = field.get("options", [])
        option_texts = " ".join([opt.get("text", "").lower() for opt in options])
        if "gender" in all_text or "sex" in all_text:
            return "gender"
        elif "country" in all_text:
            return "country"
        elif "state" in all_text or "province" in all_text:
            return "state"
        elif "city" in all_text:
            return "city"
        else:
            return "select"  # Generic select
    
    # Radio buttons
    if field_type == "radio":
        if "gender" in all_text or "sex" in all_text:
            return "gender"
        else:
            return "radio"  # Generic radio
    
    # Checkboxes
    if field_type == "checkbox":
        # Consent/terms checkboxes - check these automatically
        consent_keywords = ["agree", "terms", "accept", "consent", "gdpr", "privacy", "policy", 
                          "conditions", "terms and conditions", "i agree", "i accept", 
                          "accept terms", "agree to", "consent to", "acknowledge", "confirm"]
        if any(keyword in all_text for keyword in consent_keywords):
            return "agree_terms"
        elif "newsletter" in all_text or "subscribe" in all_text:
            return "newsletter"
        else:
            return "checkbox"  # Generic checkbox
    
    # Generic text field (fallback)
    if field_type == "text" or field_tag == "input":
        return "text"
    
    return None


def auto_fill_form_without_template(discovered_fields: List[Dict], test_data: Dict[str, Any] = None) -> List[Dict]:
    """Automatically fill form fields without requiring a template by detecting field types."""
    from datetime import datetime, timedelta
    
    if test_data is None:
        test_data = {
            "name": "TEQ QA User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": "This is an automated test submission.",
            "subject": "Test Inquiry",
            "company": "Test Company",
            "url": "https://example.com",
            "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "number": "123",
            "password": "TestPassword123",
            "gender": "male",
            "agree_terms": True,
            "newsletter": False,
            "select": "one",  # First option
            "radio": "male",  # First option
            "checkbox": True,
            "text": "Test Text"
        }
    
    auto_fields = []
    used_field_types = set()
    
    # First pass: Try to detect known field types
    for field in discovered_fields:
        field_type = auto_detect_field_type(field)
        
        if not field_type:
            continue
        
        # Handle special cases where we want to fill multiple fields of same type
        # (e.g., multiple text fields, but only one name/email)
        if field_type in ["name", "email", "phone", "message", "subject", "company"]:
            if field_type in used_field_types:
                continue  # Only fill first occurrence
        elif field_type in ["text"]:
            # Allow multiple text fields, but track by name to avoid duplicates
            field_name = field.get("name", "")
            if field_name in [f.get("original_name", "") for f in auto_fields if f.get("field_type") == "text"]:
                continue
        
        used_field_types.add(field_type)
        
        # Use the first available selector
        selector = field.get("selectors", [""])[0] if field.get("selectors") else None
        if not selector and field.get("name"):
            tag = field.get("tagName", "input").lower()
            field_type_attr = field.get("type", "")
            if field_type_attr:
                selector = f"{tag}[name='{field['name']}'][type='{field_type_attr}']"
            else:
                selector = f"{tag}[name='{field['name']}']"
        
        if not selector:
            continue
        
        # Determine value based on field type
        value = None
        field_tag = field.get("tagName", "").lower()
        field_input_type = field.get("type", "").lower()
        
        if field_type in test_data:
            value = test_data[field_type]
        elif field_tag == "select":
            # For select, use first option value
            options = field.get("options", [])
            if options and len(options) > 0:
                # Skip empty option
                for opt in options:
                    if opt.get("value") and opt.get("value").strip():
                        value = opt.get("value")
                        break
                if not value and options:
                    value = options[0].get("value", "")
        elif field_input_type == "radio":
            # For radio, use the field's value (it's already set)
            value = field.get("value", "")
            if not value:
                continue  # Skip if no value
        elif field_input_type == "checkbox":
            # For checkbox, check if we should check it
            if field_type == "agree_terms":
                value = True  # Always check consent/terms checkboxes
            elif field_type == "newsletter":
                value = False  # Don't subscribe to newsletter by default
            else:
                # Check if it looks like a consent checkbox by name/id
                field_name = field.get("name", "").lower()
                field_id = field.get("id", "").lower()
                consent_keywords = ["agree", "terms", "accept", "consent", "gdpr", "privacy", "policy"]
                if any(keyword in field_name or keyword in field_id for keyword in consent_keywords):
                    value = True  # Check consent checkboxes
                else:
                    value = True  # Check other checkboxes by default (to be safe)
        elif field_input_type in ["date", "datetime-local", "month", "week"]:
            # Use current date + 7 days for date fields
            if field_input_type == "date":
                value = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            elif field_input_type == "datetime-local":
                value = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")
            elif field_input_type == "month":
                value = (datetime.now() + timedelta(days=30)).strftime("%Y-%m")
            elif field_input_type == "week":
                # ISO week format: YYYY-Www
                week_date = datetime.now() + timedelta(days=7)
                year, week, _ = week_date.isocalendar()
                value = f"{year}-W{week:02d}"
        elif field_input_type == "time":
            value = datetime.now().strftime("%H:%M")
        elif field_input_type == "number":
            value = "123"
        elif field_input_type == "url":
            value = "https://example.com"
        elif field_input_type == "password":
            value = "TestPassword123"
        else:
            # Generic text field
            value = f"Test {field_type.title()}"
        
        if value is not None:
            auto_fields.append({
                "name": field_type,
                "selector": selector,
                "value": str(value) if not isinstance(value, bool) else value,
                "auto_detected": True,
                "field_type": field_type,
                "original_name": field.get("name", ""),
                "tag": field_tag,
                "input_type": field_input_type,
                "is_checkbox": field_input_type == "checkbox",
                "is_radio": field_input_type == "radio",
                "is_select": field_tag == "select",
                "options": field.get("options", []) if field_tag == "select" else []
            })
    
    # Second pass: If no fields were detected, fill any visible text/textarea fields as fallback
    if len(auto_fields) == 0:
        print("   ⚠️  No fields detected by type matching, using fallback: filling ANY text/textarea fields (ignoring visibility check)", file=sys.stderr)
        visible_text_fields = []
        for field in discovered_fields:
            # Skip ONLY explicitly hidden fields and honeypots
            field_type_attr = field.get("type", "").lower()
            if field_type_attr == "hidden":
                continue
            field_name_lower = field.get("name", "").lower()
            if field_name_lower in ["_token", "csrf", "token", "website", "honeypot", "from_url", "curnt_url", "g-recaptcha-response"]:
                continue
            
            field_tag = field.get("tagName", "").lower()
            field_type = field.get("type", "").lower()
            
            # Fill ANY text input or textarea (ignore isVisible check in fallback mode)
            # This is more aggressive - we'll try to fill fields even if they appear "invisible"
            if (field_tag == "textarea" or (field_tag == "input" and field_type in ["text", "email", "tel", ""])):
                # In fallback mode, ignore visibility - just check if it's a fillable field type
                # Many forms use CSS to hide/show fields, but they're still fillable
                selector = field.get("selectors", [""])[0] if field.get("selectors") else None
                if not selector:
                    # Try to build selector from available info
                    if field.get("name"):
                        tag = field.get("tagName", "input").lower()
                        selector = f"{tag}[name='{field['name']}']"
                    elif field.get("id"):
                        selector = f"#{field['id']}"
                    elif field.get("placeholder"):
                        tag = field.get("tagName", "input").lower()
                        selector = f"{tag}[placeholder='{field['placeholder']}']"
                    else:
                        # Last resort: use index-based selector
                        tag = field.get("tagName", "input").lower()
                        field_index = field.get("index", 0)
                        # Try to find by position in form
                        selector = f"{tag}:nth-of-type({field_index + 1})"
                
                if selector:
                    print(f"   🔍 Fallback: Found field - tag: {field_tag}, type: {field_type}, name: {field.get('name', 'no-name')}, selector: {selector[:50]}", file=sys.stderr)
                    # Determine value based on field position and type
                    if field_tag == "textarea":
                        value = test_data.get("message", "This is an automated test submission.")
                    elif field_type == "email" or "email" in (field.get("name", "") + field.get("placeholder", "")).lower():
                        value = test_data.get("email", "test@example.com")
                    elif field_type == "tel" or "phone" in (field.get("name", "") + field.get("placeholder", "")).lower():
                        value = test_data.get("phone", "+1234567890")
                    else:
                        # Fill with name, then email, then message based on position
                        field_index = len(visible_text_fields)
                        if field_index == 0:
                            value = test_data.get("name", "Test User")
                        elif field_index == 1:
                            value = test_data.get("email", "test@example.com")
                        elif field_index == 2:
                            value = test_data.get("phone", "+1234567890")
                        else:
                            value = test_data.get("message", "Test message")
                    
                    visible_text_fields.append({
                        "name": field.get("name", f"field_{len(visible_text_fields)}"),
                        "selector": selector,
                        "value": str(value),
                        "field_type": "text",
                        "original_name": field.get("name", ""),
                        "auto_detected": True
                    })
        
        # Add visible text fields to auto_fields (limit to first 5 to avoid filling too many)
        if visible_text_fields:
            auto_fields.extend(visible_text_fields[:5])
            print(f"   ✅ Fallback: Found {len(visible_text_fields[:5])} visible text/textarea fields to fill", file=sys.stderr)
    
    return auto_fields


async def run_submission(url: str, template_path: Path) -> Dict[str, Any]:
    from playwright.async_api import async_playwright  # imported lazily for performance

    template: Dict[str, Any] = json.loads(template_path.read_text())
    
    # Handle both snake_case and camelCase property names for compatibility
    fields: List[Dict[str, str]] = template.get("fields", [])
    pre_actions: List[Dict[str, Any]] = template.get("pre_actions", []) or template.get("preActions", [])
    submit_selector: str | None = template.get("submit_selector") or template.get("submitSelector")
    use_auto_detect: bool = template.get("use_auto_detect", False) or template.get("useAutoDetect", False)  # Enable auto-detection mode
    
    # Ensure submit_selector has a default if not provided
    if not submit_selector:
        submit_selector = "button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Send'), button:has-text('Send message')"

    # Add progress logging
    print("🚀 Starting automation...", file=sys.stderr)
    print(f"   URL: {url}", file=sys.stderr)
    print(f"   Fields to fill: {len(fields)}", file=sys.stderr)

    async with async_playwright() as p:
        # Check if we should run in headless mode
        # Priority: 1) Template setting, 2) Environment variable, 3) Auto-detect display availability
        headless = None
        
        # First, check template setting
        if template.get("headless") is not None:
            headless = template.get("headless", True)
        # Then check environment variable
        elif os.getenv("HEADLESS") is not None:
            headless = os.getenv("HEADLESS", "true").lower() not in ("false", "0", "no")
        elif os.getenv("TEQ_PLAYWRIGHT_HEADLESS") is not None:
            headless = os.getenv("TEQ_PLAYWRIGHT_HEADLESS", "true").lower() not in ("false", "0", "no")
        else:
            # Auto-detect: Check if we have a display available
            # On remote servers without X11/display, we need headless mode
            has_display = os.getenv("DISPLAY") is not None and os.getenv("DISPLAY") != ""
            # Also check if we're in a containerized environment that might not have display
            is_container = os.path.exists("/.dockerenv") or os.getenv("container") is not None
            
            if has_display and not is_container:
                # We have a display, can run non-headless for better CAPTCHA solving
                headless = False
                print("🖥️  Display detected - running with visible browser for better CAPTCHA solving", file=sys.stderr)
            else:
                # No display or in container - use headless mode (this is EXPECTED and CORRECT for remote servers)
                headless = True
                print("🖥️  No display detected - running in HEADLESS mode (expected for remote servers)", file=sys.stderr)
                print("   ℹ️  This is normal! Headless mode works perfectly for automation.", file=sys.stderr)
        
        # Final fallback
        if headless is None:
            headless = True
        
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
        
        # Add stealth scripts to hide automation
        await context.add_init_script("""
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override chrome object
            window.chrome = {
                runtime: {}
            };
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Mock getBattery
            if (navigator.getBattery) {
                navigator.getBattery = () => Promise.resolve({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 1
                });
            }
        """)
        
        page = await context.new_page()
        page.set_default_timeout(180000)  # 3 minutes page timeout
        
        # Set viewport and ensure proper zoom (100%)
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        # Zoom will be reset after page load to ensure it works

        # Use "domcontentloaded" for fastest loading (faster than "load")
        wait_until = template.get("wait_until", "domcontentloaded")
        print("📄 Loading page...", file=sys.stderr)
        await page.goto(url, wait_until=wait_until, timeout=30000)  # Reduced from 60s to 30s
        print("✅ Page loaded", file=sys.stderr)

        # Fix zoom and positioning issues - ensure 100% zoom and centered
        print("🔧 Fixing zoom and positioning...", file=sys.stderr)
        await page.evaluate("""
            () => {
                // Reset zoom to 100%
                document.body.style.zoom = '1';
                document.documentElement.style.zoom = '1';
                
                // Reset transform
                document.body.style.transform = 'scale(1)';
                document.documentElement.style.transform = 'scale(1)';
                
                // Ensure page is at top-left
                window.scrollTo(0, 0);
                
                // Reset device pixel ratio
                if (window.devicePixelRatio) {
                    Object.defineProperty(window, 'devicePixelRatio', {
                        get: function() { return 1; }
                    });
                }
            }
        """)
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        # Removed sleep - not needed for speed optimization
        
        # Automatically detect and close overlay banners, cookie consent, modals, etc.
        print("🔍 Checking for overlay banners, cookie consent, and modals...", file=sys.stderr)
        overlays_closed = await page.evaluate("""
                () => {
                    let closedCount = 0;
                    const keywords = ['cookie', 'consent', 'accept', 'agree', 'close', 'dismiss', 'got it', 
                                    'i agree', 'allow', 'ok', 'continue', 'x', '×'];
                    
                    // Find and close overlays
                    const selectors = [
                        // Cookie consent
                        '[id*="cookie"]', '[class*="cookie"]', '[id*="consent"]', '[class*="consent"]',
                        '[id*="gdpr"]', '[class*="gdpr"]', '[id*="privacy"]', '[class*="privacy"]',
                        // Common overlay classes
                        '.overlay', '.modal', '.popup', '.banner', '.notification',
                        '[role="dialog"]', '[role="alertdialog"]',
                        // Common IDs
                        '#cookie-banner', '#consent-banner', '#cookie-notice', '#consent-notice',
                        '#cookie-consent', '#gdpr-consent', '#privacy-notice'
                    ];
                    
                    for (const selector of selectors) {
                        try {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const text = (el.textContent || el.innerText || '').toLowerCase();
                                const isVisible = el.offsetParent !== null && 
                                                 window.getComputedStyle(el).display !== 'none' &&
                                                 window.getComputedStyle(el).visibility !== 'hidden';
                                
                                if (isVisible && keywords.some(kw => text.includes(kw))) {
                                    // Try to find close button inside
                                    const closeBtn = el.querySelector('button[aria-label*="close" i], ' +
                                                                    'button[aria-label*="dismiss" i], ' +
                                                                    'button[class*="close"], ' +
                                                                    'button[class*="dismiss"], ' +
                                                                    '.close, .dismiss, [class*="close-button"], ' +
                                                                    '[class*="dismiss-button"]');
                                    
                                    if (closeBtn) {
                                        closeBtn.click();
                                        closedCount++;
                                        continue;
                                    }
                                    
                                    // Try to find accept/agree button
                                    const acceptBtn = Array.from(el.querySelectorAll('button, a')).find(btn => {
                                        const btnText = (btn.textContent || btn.innerText || '').toLowerCase();
                                        return keywords.some(kw => btnText.includes(kw) && 
                                                           (btnText.includes('accept') || btnText.includes('agree') || 
                                                            btnText.includes('ok') || btnText.includes('continue')));
                                    });
                                    
                                    if (acceptBtn) {
                                        acceptBtn.click();
                                        closedCount++;
                                        continue;
                                    }
                                    
                                    // If no button found, try to hide the element
                                    el.style.display = 'none';
                                    el.style.visibility = 'hidden';
                                    closedCount++;
                                }
                            }
                        } catch (e) {
                            // Continue with next selector
                        }
                    }
                    
                    // Also try to close any visible modals/overlays by clicking outside or pressing Escape
                    const modals = document.querySelectorAll('[role="dialog"], .modal, .overlay, .popup');
                    for (const modal of modals) {
                        const style = window.getComputedStyle(modal);
                        if (style.display !== 'none' && style.visibility !== 'hidden') {
                            // Try Escape key simulation
                            const escEvent = new KeyboardEvent('keydown', { key: 'Escape', keyCode: 27, bubbles: true });
                            modal.dispatchEvent(escEvent);
                            
                            // Try clicking backdrop/overlay
                            const backdrop = modal.closest('.modal-backdrop, .overlay-backdrop, [class*="backdrop"]');
                            if (backdrop) {
                                backdrop.click();
                            }
                        }
                    }
                    
                    return closedCount;
                }
        """)
        
        if overlays_closed > 0:
            print(f"   ✅ Closed {overlays_closed} overlay(s)/banner(s)", file=sys.stderr)
            await page.wait_for_timeout(500)  # Reduced from 1000ms to 500ms for speed
        else:
            print("   ℹ️  No overlays found or already closed", file=sys.stderr)
        
        # Run pre-actions (like cookie consent) - user-defined
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

        # Wait for page to be fully interactive and forms to load (reduced for speed)
        await page.wait_for_timeout(2000)  # Reduced from 8000ms to 2000ms
        
        # Wait for form fields to be available (they might load dynamically)
        print("🔍 Waiting for form fields to load...", file=sys.stderr)
        try:
            # Wait for at least one form field to appear (reduced timeout for speed)
            await page.wait_for_selector("form input, form textarea", timeout=10000)  # Reduced from 20s to 10s
            await page.wait_for_timeout(500)  # Reduced from 2000ms to 500ms
        except:
            print("   ⚠️  Form fields not found immediately, continuing...", file=sys.stderr)
        
        # Discover forms on the page
        print("🔍 Discovering forms on page...", file=sys.stderr)
        discovered_forms = await discover_forms(page)
        print(f"✅ Found {len(discovered_forms)} form(s)", file=sys.stderr)
        
        # If no forms found, wait longer and try again (forms might be dynamically loaded)
        if not discovered_forms:
            print("   ⏳ No forms found, waiting longer for dynamic content...", file=sys.stderr)
            await page.wait_for_timeout(2000)  # Reduced from 5000ms to 2000ms
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
                # Try one more time with even longer wait
                print("   ⏳ Last attempt: waiting 10 seconds for dynamic forms...", file=sys.stderr)
                await page.wait_for_timeout(10000)
                discovered_forms = await discover_forms(page)
                if not discovered_forms:
                    # Don't fail - try to continue anyway and look for any input fields
                    print("   ⚠️  No forms found, but will try to find and fill fields directly...", file=sys.stderr)
                    # Create a dummy form structure with discovered fields
                    all_fields = await page.evaluate("""
                        () => {
                            const fields = [];
                            document.querySelectorAll('input, textarea, select').forEach(el => {
                                if (el.type !== 'hidden' && el.type !== 'submit' && el.type !== 'button') {
                                    fields.push({
                                        name: el.name || el.id || '',
                                        type: el.type || el.tagName.toLowerCase(),
                                        tagName: el.tagName.toLowerCase(),
                                        selector: el.name ? `[name="${el.name}"]` : (el.id ? `#${el.id}` : ''),
                                        isHidden: el.type === 'hidden' || el.offsetParent === null
                                    });
                                }
                            });
                            return fields;
                        }
                    """)
                    if all_fields:
                        discovered_forms = [{"fields": all_fields, "action": "", "method": "post"}]
                        print(f"   ✅ Found {len(all_fields)} fields directly (no form wrapper)", file=sys.stderr)
                    else:
                        raise RuntimeError("No forms or fields found on the page after multiple attempts.")
        
        # Use the first form (or find the best match)
        # Prefer contact forms over newsletter forms
        target_form = discovered_forms[0]
        if len(discovered_forms) > 1:
            # Try to find form with most matching fields
            # Also prefer forms with more fields (contact forms usually have more fields than newsletter)
            best_match = target_form
            best_score = 0
            for form in discovered_forms:
                score = 0
                form_fields = form.get("fields", [])
                
                # Prefer forms with more visible fields (contact forms have more fields)
                visible_fields = [f for f in form_fields if not f.get("isHidden", False) and f.get("type", "").lower() != "hidden"]
                score += len(visible_fields) * 2  # Weight by number of visible fields
                
                # Prefer forms that match template fields
                for field in fields:
                    if find_matching_field(form_fields, field):
                        score += 10  # Higher weight for matching fields
                
                # Prefer forms with textarea (contact forms usually have message fields)
                has_textarea = any(f.get("tagName", "").lower() == "textarea" for f in form_fields)
                if has_textarea:
                    score += 5
                
                # Avoid forms with only email field (likely newsletter)
                if len(visible_fields) == 1 and any("email" in f.get("name", "").lower() for f in visible_fields):
                    score -= 10  # Penalize newsletter forms
                
                if score > best_score:
                    best_score = score
                    best_match = form
            target_form = best_match
            print(f"   📋 Selected form with {len(target_form.get('fields', []))} fields (score: {best_score})", file=sys.stderr)
        
        discovered_fields = target_form.get("fields", [])
        print(f"📝 Found {len(discovered_fields)} fields in target form", file=sys.stderr)
        
        # Auto-detect mode: If enabled and no fields in template, auto-detect fields
        if use_auto_detect and (not fields or len(fields) == 0):
            print("🤖 Auto-detect mode enabled: Automatically detecting form fields...", file=sys.stderr)
            test_data = template.get("test_data") or template.get("testData") or {}
            fields = auto_fill_form_without_template(discovered_fields, test_data)
            if fields:
                field_names = [f.get('name', f.get('field_type', 'unknown')) for f in fields[:5]]
                print(f"   ✅ Auto-detected {len(fields)} fields: {', '.join(field_names)}", file=sys.stderr)
            else:
                print("   ⚠️  Could not auto-detect any fillable fields.", file=sys.stderr)
                # Debug: Show what fields were discovered
                visible_fields = [f for f in discovered_fields if f.get("isVisible", True) and f.get("type", "").lower() != "hidden"]
                print(f"   📊 Debug: Found {len(visible_fields)} visible fields in discovered_fields", file=sys.stderr)
                if visible_fields:
                    print(f"   📊 Debug: First 3 visible field names: {[f.get('name', 'no-name') for f in visible_fields[:3]]}", file=sys.stderr)
                    print(f"   📊 Debug: First 3 visible field types: {[f.get('type', 'no-type') for f in visible_fields[:3]]}", file=sys.stderr)
                    print(f"   📊 Debug: First 3 visible field tags: {[f.get('tagName', 'no-tag') for f in visible_fields[:3]]}", file=sys.stderr)
        
        # If discovered fields are fewer than expected, wait and rediscover
        if fields and len(discovered_fields) < len(fields):
            print(f"   ⚠️  Only {len(discovered_fields)} fields discovered, expected {len(fields)}. Waiting for more fields...", file=sys.stderr)
            for rediscover_attempt in range(3):
                await page.wait_for_timeout(3000 * (rediscover_attempt + 1))  # Increasing wait times
                # Rediscover forms
                discovered_forms = await discover_forms(page)
                if discovered_forms:
                    target_form = discovered_forms[0]
                    if len(discovered_forms) > 1:
                        # Find best match again (same logic as initial selection)
                        best_match = target_form
                        best_score = 0
                        for form in discovered_forms:
                            score = 0
                            form_fields = form.get("fields", [])
                            visible_fields = [f for f in form_fields if not f.get("isHidden", False) and f.get("type", "").lower() != "hidden"]
                            score += len(visible_fields) * 2
                            for field in fields:
                                if find_matching_field(form_fields, field):
                                    score += 10
                            has_textarea = any(f.get("tagName", "").lower() == "textarea" for f in form_fields)
                            if has_textarea:
                                score += 5
                            if len(visible_fields) == 1 and any("email" in f.get("name", "").lower() for f in visible_fields):
                                score -= 10
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
        if not fields:
            print("⚠️  No fields to fill. Skipping form fill.", file=sys.stderr)
        else:
            print(f"✍️  Filling {len(fields)} form fields...", file=sys.stderr)
            for i, field in enumerate(fields, 1):
                field_name = field.get("selector", field.get("name", f"field_{i}"))
                print(f"   Field {i}/{len(fields)}: {field_name[:50]}...", file=sys.stderr)
                value = field.get("value") or field.get("testValue") or ""
                if not value:
                    continue
                
                # Initialize variables
                discovered_field = None
                selectors_to_try = []
                
                # If field has a selector from auto-detection, use it directly (highest priority)
                # This avoids trying variations that might not exist
                if field.get("auto_detected") and field.get("selector"):
                    selectors_to_try = [field.get("selector")]
                    # Also try with different quote styles
                    template_selector = field.get("selector")
                    if "'" in template_selector:
                        selectors_to_try.append(template_selector.replace("'", '"'))
                    elif '"' in template_selector:
                        selectors_to_try.append(template_selector.replace('"', "'"))
                else:
                    # Try to find matching discovered field
                    discovered_field = find_matching_field(discovered_fields, field)
                    
                    if discovered_field:
                        # Use the first available selector from discovered field
                        selectors_to_try = discovered_field.get("selectors", [])
                        if not selectors_to_try and discovered_field.get("name"):
                            tag = discovered_field.get("tagName", "input").lower()
                            selectors_to_try = [
                                f"{tag}[name='{discovered_field['name']}']",
                                f"{tag}[name=\"{discovered_field['name']}\"]",
                            ]
                            if discovered_field.get("id"):
                                selectors_to_try.append(f"#{discovered_field['id']}")
                    else:
                        # Fall back to template selector, but also try common field name variations
                        template_selector = field.get("selector")
                        template_field_name = field.get("name", "").lower()
                        selectors_to_try = []
                        
                        if template_selector:
                            selectors_to_try.append(template_selector)
                            # Also try with different quote styles
                            if "'" in template_selector:
                                selectors_to_try.append(template_selector.replace("'", '"'))
                            elif '"' in template_selector:
                                selectors_to_try.append(template_selector.replace('"', "'"))
                    
                    # Try common field name variations based on field type
                    if template_field_name:
                        # Extract tag from template selector or use common ones
                        import re
                        tag_match = re.search(r"^(input|textarea|select)", template_selector or "", re.IGNORECASE)
                        tag = tag_match.group(1).lower() if tag_match else "input"
                        
                        # Common variations for message/comment fields
                        if template_field_name in ["comment", "message", "notes", "description"]:
                            for var_name in ["message", "comment", "notes", "description", "details", "inquiry", "query"]:
                                selectors_to_try.extend([
                                    f"textarea[name='{var_name}']",
                                    f"textarea[name=\"{var_name}\"]",
                                    f"input[name='{var_name}']",
                                    f"input[name=\"{var_name}\"]",
                                ])
                        # Common variations for name fields
                        elif template_field_name in ["name", "fullname", "full_name"]:
                            for var_name in ["name", "fullname", "full_name", "firstname", "first_name"]:
                                selectors_to_try.extend([
                                    f"input[name='{var_name}']",
                                    f"input[name=\"{var_name}\"]",
                                ])
                        # Common variations for email
                        elif template_field_name in ["email", "e-mail", "mail"]:
                            for var_name in ["email", "e-mail", "mail", "email_address"]:
                                selectors_to_try.extend([
                                    f"input[name='{var_name}']",
                                    f"input[name=\"{var_name}\"]",
                                    f"input[type='email']",
                                ])
                        # Common variations for phone
                        elif template_field_name in ["phone", "telephone", "mobile"]:
                            for var_name in ["phone", "telephone", "mobile", "phone_number"]:
                                selectors_to_try.extend([
                                    f"input[name='{var_name}']",
                                    f"input[name=\"{var_name}\"]",
                                    f"input[type='tel']",
                                ])
                
                # Try each selector until one works
                filled = False
                last_error = None
                
                # Remove duplicates while preserving order
                seen = set()
                selectors_to_try = [s for s in selectors_to_try if s not in seen and not seen.add(s)]
                
                for selector in selectors_to_try:
                    try:
                        # First, check if selector exists (don't wait for visibility yet)
                        # This handles cases where elements exist but might be hidden initially
                        element_exists = await page.evaluate("""
                            (sel) => {
                                return document.querySelectorAll(sel).length > 0;
                            }
                        """, selector)
                        
                        if not element_exists:
                            continue
                        
                        # Use JavaScript to find the first visible element matching the selector
                        # This handles cases where multiple forms have the same field (e.g., newsletter + contact)
                        element_info = await page.evaluate("""
                            (sel) => {
                                const elements = Array.from(document.querySelectorAll(sel));
                                // Find first visible element (not hidden, has dimensions)
                                for (const el of elements) {
                                    const rect = el.getBoundingClientRect();
                                    const style = window.getComputedStyle(el);
                                    // More lenient visibility check - just check if it's not explicitly hidden
                                    if (style.display !== 'none' && 
                                        style.visibility !== 'hidden' &&
                                        style.opacity !== '0') {
                                        // Prefer elements in contact forms (forms with more fields)
                                        const form = el.closest('form');
                                        if (form) {
                                            const formInputs = form.querySelectorAll('input, textarea, select');
                                            const visibleInputs = Array.from(formInputs).filter(inp => {
                                                const r = inp.getBoundingClientRect();
                                                const s = window.getComputedStyle(inp);
                                                return s.display !== 'none' && s.visibility !== 'hidden';
                                            });
                                            // Prefer forms with more visible fields (contact forms)
                                            if (visibleInputs.length > 1) {
                                                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                                return { found: true, selector: sel, id: el.id || null };
                                            }
                                        }
                                    }
                                }
                                // Fallback to first element that's not explicitly hidden
                                for (const el of elements) {
                                    const style = window.getComputedStyle(el);
                                    if (style.display !== 'none' && style.visibility !== 'hidden') {
                                        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                        return { found: true, selector: sel, id: el.id || null };
                                    }
                                }
                                // Last resort: use first element
                                if (elements[0]) {
                                    elements[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                                    return { found: true, selector: sel, id: elements[0].id || null };
                                }
                                return { found: false };
                            }
                        """, selector)
                        
                        if not element_info.get("found"):
                            continue
                        
                        # If we found an element with an ID, try using that selector (more reliable)
                        if element_info.get("id"):
                            id_selector = f"#{element_info['id']}"
                            # Try ID selector first if available
                            try:
                                await page.wait_for_selector(id_selector, state="attached", timeout=5000)
                                selector = id_selector  # Use ID selector instead
                            except:
                                pass  # Fall back to original selector
                        
                        # Now wait for the element to be attached (not necessarily visible)
                        await page.wait_for_selector(selector, state="attached", timeout=10000)
                        
                        await page.wait_for_timeout(500)
                        
                        # Get field metadata to determine how to fill it
                        is_checkbox = field.get("is_checkbox", False)
                        is_radio = field.get("is_radio", False)
                        is_select = field.get("is_select", False)
                        field_tag = field.get("tag", "input")
                        input_type = field.get("input_type", "")
                        
                        # Fill the field based on its type
                        if is_checkbox:
                            # Handle checkbox - check or uncheck based on value
                            fill_result = await page.evaluate("""
                                ([sel, shouldCheck]) => {
                                    const elements = Array.from(document.querySelectorAll(sel));
                                    for (const el of elements) {
                                        const rect = el.getBoundingClientRect();
                                        const style = window.getComputedStyle(el);
                                        if (rect.width > 0 && rect.height > 0 && 
                                            style.display !== 'none' && 
                                            style.visibility !== 'hidden') {
                                            const form = el.closest('form');
                                            if (form) {
                                                const formInputs = form.querySelectorAll('input, textarea, select');
                                                const visibleInputs = Array.from(formInputs).filter(inp => {
                                                    const r = inp.getBoundingClientRect();
                                                    const s = window.getComputedStyle(inp);
                                                    return r.width > 0 && r.height > 0 && s.display !== 'none';
                                                });
                                                if (visibleInputs.length > 1) {
                                                    el.checked = shouldCheck;
                                                    el.dispatchEvent(new Event('change', { bubbles: true }));
                                                    el.dispatchEvent(new Event('click', { bubbles: true }));
                                                    return { filled: true, checked: el.checked };
                                                }
                                            }
                                        }
                                    }
                                    if (elements[0]) {
                                        elements[0].checked = shouldCheck;
                                        elements[0].dispatchEvent(new Event('change', { bubbles: true }));
                                        elements[0].dispatchEvent(new Event('click', { bubbles: true }));
                                        return { filled: true, checked: elements[0].checked };
                                    }
                                    return { filled: false };
                                }
                            """, [selector, bool(value)])
                        elif is_radio:
                            # Handle radio button - select the matching value
                            fill_result = await page.evaluate("""
                                ([sel, val]) => {
                                    const elements = Array.from(document.querySelectorAll(sel));
                                    for (const el of elements) {
                                        const rect = el.getBoundingClientRect();
                                        const style = window.getComputedStyle(el);
                                        if (rect.width > 0 && rect.height > 0 && 
                                            style.display !== 'none' && 
                                            style.visibility !== 'hidden') {
                                            // For radio, check if value matches
                                            if (el.value === val || el.value === String(val)) {
                                                const form = el.closest('form');
                                                if (form) {
                                                    el.checked = true;
                                                    el.dispatchEvent(new Event('change', { bubbles: true }));
                                                    el.dispatchEvent(new Event('click', { bubbles: true }));
                                                    return { filled: true, checked: el.checked };
                                                }
                                            }
                                        }
                                    }
                                    // Fallback: check first matching radio
                                    for (const el of elements) {
                                        if (el.value === val || el.value === String(val)) {
                                            el.checked = true;
                                            el.dispatchEvent(new Event('change', { bubbles: true }));
                                            el.dispatchEvent(new Event('click', { bubbles: true }));
                                            return { filled: true, checked: el.checked };
                                        }
                                    }
                                    return { filled: false };
                                }
                            """, [selector, str(value)])
                        elif is_select:
                            # Handle select dropdown - use select_option
                            try:
                                # Try using Playwright's select_option for better compatibility
                                await page.select_option(selector, str(value), timeout=10000)
                                fill_result = {"filled": True, "value": str(value)}
                            except:
                                # Fallback to JavaScript
                                fill_result = await page.evaluate("""
                                    ([sel, val]) => {
                                        const elements = Array.from(document.querySelectorAll(sel));
                                        for (const el of elements) {
                                            const rect = el.getBoundingClientRect();
                                            const style = window.getComputedStyle(el);
                                            if (rect.width > 0 && rect.height > 0 && 
                                                style.display !== 'none' && 
                                                style.visibility !== 'hidden') {
                                                const form = el.closest('form');
                                                if (form) {
                                                    const formInputs = form.querySelectorAll('input, textarea, select');
                                                    const visibleInputs = Array.from(formInputs).filter(inp => {
                                                        const r = inp.getBoundingClientRect();
                                                        const s = window.getComputedStyle(inp);
                                                        return r.width > 0 && r.height > 0 && s.display !== 'none';
                                                    });
                                                    if (visibleInputs.length > 1) {
                                                        el.value = val;
                                                        el.dispatchEvent(new Event('change', { bubbles: true }));
                                                        el.dispatchEvent(new Event('input', { bubbles: true }));
                                                        return { filled: true, value: el.value };
                                                    }
                                                }
                                            }
                                        }
                                        if (elements[0]) {
                                            elements[0].value = val;
                                            elements[0].dispatchEvent(new Event('change', { bubbles: true }));
                                            elements[0].dispatchEvent(new Event('input', { bubbles: true }));
                                            return { filled: true, value: elements[0].value };
                                        }
                                        return { filled: false };
                                    }
                                """, [selector, str(value)])
                        else:
                            # Handle regular input fields (text, email, tel, date, time, number, url, etc.)
                            fill_result = await page.evaluate("""
                                ([sel, val]) => {
                                    const elements = Array.from(document.querySelectorAll(sel));
                                    for (const el of elements) {
                                        const rect = el.getBoundingClientRect();
                                        const style = window.getComputedStyle(el);
                                        if (rect.width > 0 && rect.height > 0 && 
                                            style.display !== 'none' && 
                                            style.visibility !== 'hidden') {
                                            const form = el.closest('form');
                                            if (form) {
                                                const formInputs = form.querySelectorAll('input, textarea, select');
                                                const visibleInputs = Array.from(formInputs).filter(inp => {
                                                    const r = inp.getBoundingClientRect();
                                                    const s = window.getComputedStyle(inp);
                                                    return r.width > 0 && r.height > 0 && s.display !== 'none';
                                                });
                                                // Prefer forms with more visible fields (contact forms)
                                                if (visibleInputs.length > 1) {
                                                    el.value = val;
                                                    el.dispatchEvent(new Event('input', { bubbles: true }));
                                                    el.dispatchEvent(new Event('change', { bubbles: true }));
                                                    return { filled: true, value: el.value };
                                                }
                                            }
                                        }
                                    }
                                    // Fallback to first element
                                    if (elements[0]) {
                                        elements[0].value = val;
                                        elements[0].dispatchEvent(new Event('input', { bubbles: true }));
                                        elements[0].dispatchEvent(new Event('change', { bubbles: true }));
                                        return { filled: true, value: elements[0].value };
                                    }
                                    return { filled: false };
                                }
                            """, [selector, str(value)])
                        
                        # Verify it was filled
                        await page.wait_for_timeout(300)
                        if is_checkbox or is_radio:
                            filled = fill_result.get("filled", False) and fill_result.get("checked", False) == bool(value)
                        else:
                            filled_value = fill_result.get("value", "") if fill_result.get("filled") else ""
                            filled = filled_value == str(value) or (str(value) in filled_value) or len(filled_value) > 0
                        
                        if filled:
                            print(f"   ✅ Field {i} filled successfully", file=sys.stderr)
                            break
                        else:
                            # Try again with direct JavaScript fill (retry logic)
                            if is_checkbox:
                                fill_result = await page.evaluate("""
                                    ([sel, shouldCheck]) => {
                                        const el = document.querySelector(sel);
                                        if (el) {
                                            el.checked = shouldCheck;
                                            el.dispatchEvent(new Event('change', { bubbles: true }));
                                            el.dispatchEvent(new Event('click', { bubbles: true }));
                                            return { filled: true, checked: el.checked };
                                        }
                                        return { filled: false };
                                    }
                                """, [selector, bool(value)])
                                filled = fill_result.get("filled", False) and fill_result.get("checked", False) == bool(value)
                            elif is_radio:
                                fill_result = await page.evaluate("""
                                    ([sel, val]) => {
                                        const elements = Array.from(document.querySelectorAll(sel));
                                        for (const el of elements) {
                                            if (el.value === val || el.value === String(val)) {
                                                el.checked = true;
                                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                                el.dispatchEvent(new Event('click', { bubbles: true }));
                                                return { filled: true, checked: el.checked };
                                            }
                                        }
                                        return { filled: false };
                                    }
                                """, [selector, str(value)])
                                filled = fill_result.get("filled", False) and fill_result.get("checked", False)
                            elif is_select:
                                try:
                                    await page.select_option(selector, str(value), timeout=5000)
                                    filled = True
                                except:
                                    fill_result = await page.evaluate("""
                                        ([sel, val]) => {
                                            const el = document.querySelector(sel);
                                            if (el) {
                                                el.value = val;
                                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                                return { filled: true, value: el.value };
                                            }
                                            return { filled: false };
                                        }
                                    """, [selector, str(value)])
                                    filled = fill_result.get("filled", False)
                            else:
                                fill_result = await page.evaluate("""
                                    ([sel, val]) => {
                                        const el = document.querySelector(sel);
                                        if (el) {
                                            el.value = '';
                                            el.value = val;
                                            el.dispatchEvent(new Event('input', { bubbles: true }));
                                            el.dispatchEvent(new Event('change', { bubbles: true }));
                                            return { filled: true, value: el.value };
                                        }
                                        return { filled: false };
                                    }
                                """, [selector, str(value)])
                                filled_value = fill_result.get("value", "") if fill_result.get("filled") else ""
                                filled = filled_value == str(value) or (str(value) in filled_value) or len(filled_value) > 0
                            
                            await page.wait_for_timeout(300)
                            if filled:
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

        # Check for and close any overlays that appeared after form filling (before CAPTCHA)
        print("🔍 Checking for overlays that might block CAPTCHA...", file=sys.stderr)
        await page.evaluate("""
            () => {
                // Close any overlays that might have appeared
                const overlays = document.querySelectorAll('.overlay, .modal, .popup, [role="dialog"]');
                for (const overlay of overlays) {
                    const style = window.getComputedStyle(overlay);
                    if (style.display !== 'none' && style.visibility !== 'hidden') {
                        // Try to find and click close button
                        const closeBtn = overlay.querySelector('button[class*="close"], .close, [aria-label*="close" i]');
                        if (closeBtn) {
                            closeBtn.click();
                        } else {
                            // Hide it
                            overlay.style.display = 'none';
                        }
                    }
                }
            }
        """)
        await page.wait_for_timeout(500)
        
        # Automatically check all consent/terms checkboxes
        print("✅ Checking consent/terms checkboxes automatically...", file=sys.stderr)
        consent_checkboxes_checked = await page.evaluate("""
            () => {
                const consentKeywords = ['agree', 'terms', 'accept', 'consent', 'gdpr', 'privacy', 'policy', 
                                       'conditions', 'acknowledge', 'confirm', 'i agree', 'i accept'];
                const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
                let checkedCount = 0;
                
                for (const checkbox of checkboxes) {
                    // Skip if already checked
                    if (checkbox.checked) {
                        continue;
                    }
                    
                    // Skip hidden checkboxes
                    const rect = checkbox.getBoundingClientRect();
                    const style = window.getComputedStyle(checkbox);
                    if (rect.width === 0 || rect.height === 0 || 
                        style.display === 'none' || style.visibility === 'hidden') {
                        continue;
                    }
                    
                    // Check if it's a consent checkbox by looking at nearby text
                    const label = checkbox.closest('label') || 
                                 document.querySelector(`label[for="${checkbox.id}"]`) ||
                                 checkbox.parentElement;
                    const labelText = (label ? label.textContent || label.innerText : '').toLowerCase();
                    const name = (checkbox.name || '').toLowerCase();
                    const id = (checkbox.id || '').toLowerCase();
                    const allText = labelText + ' ' + name + ' ' + id;
                    
                    // Check if it matches consent keywords
                    const isConsent = consentKeywords.some(keyword => allText.includes(keyword));
                    
                    if (isConsent) {
                        checkbox.checked = true;
                        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                        checkbox.dispatchEvent(new Event('click', { bubbles: true }));
                        checkedCount++;
                    }
                }
                
                return checkedCount;
            }
        """)
        
        if consent_checkboxes_checked > 0:
            print(f"   ✅ Checked {consent_checkboxes_checked} consent checkbox(es)", file=sys.stderr)
            await page.wait_for_timeout(500)  # Brief pause after checking
        else:
            print("   ℹ️  No unchecked consent checkboxes found", file=sys.stderr)
        
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
            
            # Use local solver only by default (no hybrid mode)
            # Handle both snake_case and camelCase
            use_local = template.get("use_local_captcha_solver")
            if use_local is None:
                use_local = template.get("useLocalCaptchaSolver")
            if use_local is None:
                use_local = os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "true").lower() not in ("false", "0", "no")
            else:
                use_local = bool(use_local)
            # Default to True if still not specified
            if use_local is None:
                use_local = True
            
            # Check if we should use hybrid mode (try local, fallback to external)
            # Default to False - use ONLY local solver
            # Handle both snake_case and camelCase
            use_hybrid = template.get("use_hybrid_captcha_solver")
            if use_hybrid is None:
                use_hybrid = template.get("useHybridCaptchaSolver")
            if use_hybrid is None:
                use_hybrid = os.getenv("TEQ_USE_HYBRID_CAPTCHA_SOLVER", "false").lower() not in ("false", "0", "no")
            else:
                use_hybrid = bool(use_hybrid)
            # Default to False if still not specified
            if use_hybrid is None:
                use_hybrid = False
            
            solver = None
            local_solver_used = False
            local_solver_failed = False
            local_solver_error = None  # Store the actual error message
            local_solver_instance = None  # Store local solver instance for later use
            
            # Step 1: Try local solver first (if enabled)
            print(f"🔍 CAPTCHA solving check: use_local={use_local}, captcha_type={captcha_type}, site_key={'present' if site_key else 'missing'}", file=sys.stderr)
            
            # Also try hCaptcha if it's hCaptcha
            if use_local and captcha_type == "hcaptcha" and site_key:
                try:
                    from captcha_solver import LocalCaptchaSolver
                    
                    print("🤖 Step 1: Trying LOCAL CAPTCHA SOLVER for hCaptcha (fully automated)...", file=sys.stderr)
                    print(f"   Site key: {site_key[:20]}...", file=sys.stderr)
                    print(f"   Page URL: {page.url}", file=sys.stderr)
                    local_solver_instance = LocalCaptchaSolver(page=page)
                    solver = local_solver_instance
                    local_solver_used = True
                    
                    # Use longer timeout for headless mode
                    is_headless_mode = headless
                    timeout_seconds = 180 if is_headless_mode else 120
                    
                    try:
                        token = await asyncio.wait_for(
                            solver.solve_hcaptcha(site_key, page.url),
                            timeout=timeout_seconds
                        )
                    except asyncio.TimeoutError:
                        print(f"   ⏰ Local solver timeout ({timeout_seconds}s) for hCaptcha", file=sys.stderr)
                        token = None
                        local_solver_failed = True
                        local_solver_error = f"Timeout after {timeout_seconds} seconds"
                    
                    if token:
                        # Inject hCaptcha token
                        await page.evaluate("""
                            ([token]) => {
                                const field = document.querySelector('textarea[name="h-captcha-response"]');
                                if (field) {
                                    field.value = token;
                                    field.dispatchEvent(new Event('change', { bubbles: true }));
                                    field.dispatchEvent(new Event('input', { bubbles: true }));
                                }
                            }
                        """, [token])
                        await page.wait_for_timeout(2000)
                        captcha_info = await detect_captcha(page)
                        captcha_solved = captcha_info.get("solved", False)
                        
                        if captcha_solved:
                            print("✅ hCaptcha solved automatically by local solver!", file=sys.stderr)
                    else:
                        local_solver_failed = True
                        local_solver_error = "Solver returned empty token for hCaptcha"
                        if not use_hybrid:
                            raise RuntimeError("Local hCaptcha solver returned empty token")
                        
                except Exception as e:
                    import traceback
                    local_error = str(e)
                    error_trace = traceback.format_exc()
                    print(f"⚠️  Local hCaptcha solver failed: {local_error}", file=sys.stderr)
                    print(f"📋 Full error trace:", file=sys.stderr)
                    print(error_trace, file=sys.stderr)
                    local_solver_failed = True
                    local_solver_error = local_error[:200]
            
            if use_local and captcha_type == "recaptcha" and site_key:
                try:
                    from captcha_solver import LocalCaptchaSolver
                    
                    print("🤖 Step 1: Trying LOCAL CAPTCHA SOLVER (fully automated)...", file=sys.stderr)
                    print(f"   Site key: {site_key[:20]}...", file=sys.stderr)
                    print(f"   Page URL: {page.url}", file=sys.stderr)
                    local_solver_instance = LocalCaptchaSolver(page=page)
                    solver = local_solver_instance
                    local_solver_used = True
                    
                    # Try with timeout to prevent hanging
                    # Increase timeout for headless mode (CAPTCHA solving takes longer without display)
                    # Check if we're in headless mode
                    is_headless_mode = headless
                    timeout_seconds = 180 if is_headless_mode else 120  # 3 minutes for headless, 2 minutes for visible
                    
                    print(f"   ⏱️  Using timeout: {timeout_seconds}s ({'headless' if is_headless_mode else 'visible'} mode)", file=sys.stderr)
                    
                    try:
                        token = await asyncio.wait_for(
                            solver.solve_recaptcha_v2(site_key, page.url),
                            timeout=timeout_seconds
                        )
                    except asyncio.TimeoutError:
                        print(f"   ⏰ Local solver timeout ({timeout_seconds}s)", file=sys.stderr)
                        if use_hybrid:
                            print("   Will try external service...", file=sys.stderr)
                        else:
                            print("   Hybrid mode disabled - will not try external services", file=sys.stderr)
                        token = None
                        local_solver_failed = True
                        local_solver_error = "Timeout after 120 seconds"
                    
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
                        local_solver_failed = True
                        local_solver_error = "Solver returned empty token"
                        if not use_hybrid:
                            raise RuntimeError("Local CAPTCHA solver returned empty token")
                        else:
                            print("   ⚠️  Local solver returned empty token, will try external service...", file=sys.stderr)
                        
                except Exception as e:
                    import traceback
                    local_error = str(e)
                    error_trace = traceback.format_exc()
                    print(f"⚠️  Local solver failed: {local_error}", file=sys.stderr)
                    print(f"📋 Full error trace:", file=sys.stderr)
                    print(error_trace, file=sys.stderr)
                    local_solver_failed = True
                    local_solver_error = local_error[:200]  # Store first 200 chars of error
                    if not use_hybrid:
                        print("❌ Local solver failed and hybrid mode is disabled. Will not try external services.", file=sys.stderr)
                    else:
                        print("🔄 Step 2: Falling back to external CAPTCHA service...", file=sys.stderr)
            
            # Step 2: If local solver failed or not used, try external services (if hybrid mode or local disabled)
            if (not captcha_solved and (local_solver_failed or not use_local or use_hybrid)) and captcha_type == "recaptcha" and site_key:
                # Get CAPTCHA solver service preference
                captcha_service = template.get("captcha_service", "auto")
                captcha_api_key = template.get("captcha_api_key")  # Can override service-specific keys
                
                # If local solver already failed and service is "auto", try to get external service explicitly
                # to avoid getting LocalCaptchaSolver again
                if local_solver_failed and captcha_service == "auto":
                    # Try to find an external service with API keys
                    if os.getenv("CAPTCHA_2CAPTCHA_API_KEY") or os.getenv("TEQ_CAPTCHA_API_KEY"):
                        captcha_service = "2captcha"
                    elif os.getenv("CAPTCHA_ANTICAPTCHA_API_KEY"):
                        captcha_service = "anticaptcha"
                    elif os.getenv("CAPTCHA_CAPSOLVER_API_KEY"):
                        captcha_service = "capsolver"
                    else:
                        # No external service available, skip to manual mode
                        captcha_service = None
                
                # Get solver instance (only if we have a valid service)
                solver = None
                if captcha_service:
                    solver = get_captcha_solver(captcha_service)
                    # If we got LocalCaptchaSolver again but local already failed, skip it
                    if local_solver_failed and solver and LocalCaptchaSolver and isinstance(solver, LocalCaptchaSolver):
                        print("   ⚠️  Local solver already failed, skipping external fallback (no API keys)", file=sys.stderr)
                        solver = None
                
                # If local solver, set the page object
                if solver and hasattr(solver, 'page'):
                    solver.page = page
                
                if solver:
                    try:
                        print(f"🤖 Step 2: Trying external CAPTCHA service ({captcha_service})...", file=sys.stderr)
                        # Solve reCAPTCHA using configured solver
                        page_url = page.url
                        try:
                            token = await asyncio.wait_for(
                                solver.solve_recaptcha_v2(site_key, page_url),
                                timeout=120  # 120 second max timeout (increased for complex CAPTCHAs)
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
                            
                            if captcha_solved:
                                print("✅ CAPTCHA solved by external service!", file=sys.stderr)
                        else:
                            # External solver returned empty token - don't raise error if hybrid mode, just log
                            if use_hybrid:
                                print("⚠️  External solver returned empty token, but continuing (hybrid mode)", file=sys.stderr)
                            else:
                                raise RuntimeError("CAPTCHA solver returned empty token")
                            
                    except Exception as e:
                        # If hybrid mode, don't raise error - let it fall through to manual mode
                        if use_hybrid:
                            print(f"⚠️  External solver failed: {str(e)[:100]}, will try manual mode if available", file=sys.stderr)
                        else:
                            raise RuntimeError(
                                f"Failed to solve CAPTCHA automatically: {str(e)}. "
                                f"Please check your {captcha_service} API key or solve manually."
                            )
                else:
                    # No solver available
                    if use_hybrid:
                        print("⚠️  No external CAPTCHA solver available (no API keys configured), will try manual mode if available", file=sys.stderr)
                    else:
                        print("⚠️  No CAPTCHA solver available. Please configure API keys or enable manual solving.", file=sys.stderr)
            
            # If still not solved, fall back to manual mode (if in non-headless mode)
            if captcha_type == "recaptcha" and not captcha_solved:
                # Check if we're in development/test mode (non-headless)
                if not headless:
                    # Development mode: wait for manual solving
                    print("⚠️  All automated CAPTCHA solvers failed. Waiting for manual CAPTCHA solving...", file=sys.stderr)
                    print("⚠️  Please solve the CAPTCHA manually in the browser window.", file=sys.stderr)
                    print("⚠️  Waiting up to 5 minutes for manual CAPTCHA solving...", file=sys.stderr)
                    captcha_timeout = template.get("captcha_timeout_ms", 600000)  # 10 minutes for manual solving (increased)
                    captcha_solved = await wait_for_captcha_solution(page, captcha_info, captcha_timeout)
                    
                    if captcha_solved:
                        print("✅ CAPTCHA solved manually!", file=sys.stderr)
                    else:
                        raise RuntimeError(
                            "CAPTCHA not solved within timeout. "
                            "Please solve it manually in the browser window, or configure CAPTCHA solver API keys."
                        )
                else:
                    # Headless mode - can't do manual solving
                    error_msg = "reCAPTCHA detected but all automated solvers failed."
                    if local_solver_failed:
                        error_msg += " Local solver failed"
                        if local_solver_error:
                            error_msg += f" ({local_solver_error})"
                        error_msg += "."
                    if not solver:
                        error_msg += " No external solver available (no API keys configured)."
                    error_msg += " Options: 1) Enable local solver with 'use_local_captcha_solver': true (already enabled), 2) Set CAPTCHA API keys, 3) Use test mode with 'headless': false for manual solving"
                    raise RuntimeError(error_msg)
            
            # Check for missing site key
            if captcha_type == "recaptcha" and not site_key and not captcha_solved:
                raise RuntimeError(
                    "reCAPTCHA detected but site key could not be extracted. "
                    "Please check the form structure."
                )
            
            # Final check - if CAPTCHA still not solved after all attempts
            if captcha_type == "recaptcha" and not captcha_solved:
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
            try:
                final_captcha_check = await detect_captcha(page)
            except Exception as e:
                # Page might have navigated after submission, ignore this check
                print(f"   ⚠️  Could not verify CAPTCHA (page may have navigated): {str(e)[:50]}", file=sys.stderr)
                final_captcha_check = {"type": None, "solved": True}  # Assume solved if we got this far
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
                        try:
                            final_captcha_check = await detect_captcha(page)
                        except Exception as e:
                            print(f"   ⚠️  Could not verify CAPTCHA after re-injection: {str(e)[:50]}", file=sys.stderr)
                            final_captcha_check = {"type": None, "solved": True}
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
                    # Handle both snake_case and camelCase
                    captcha_service = template.get("captcha_service") or template.get("captchaService") or "auto"
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
                # Handle both snake_case and camelCase
                use_local = template.get("use_local_captcha_solver") or template.get("useLocalCaptchaSolver") or True
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
                    # Handle both snake_case and camelCase
                    captcha_service = template.get("captcha_service") or template.get("captchaService") or "auto"
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
                        # Handle both snake_case and camelCase
                        use_local = template.get("use_local_captcha_solver") or template.get("useLocalCaptchaSolver") or True
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
        
        # Wait a bit longer after submission to ensure server processes it (reduced for speed)
        if submission_success or post_requests or fetch_requests or responses_received:
            print("⏳ Waiting for server to process submission...", file=sys.stderr)
            await page.wait_for_timeout(2000)  # Reduced from 5000ms to 2000ms for speed
            
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

        # Close browser/tab after submission (always close, even on errors)
        print("🔒 Closing browser after submission...", file=sys.stderr)
        try:
            if page:
                await page.close()
                await asyncio.sleep(0.3)  # Brief pause for cleanup
        except Exception as e:
            print(f"   ⚠️  Error closing page: {str(e)[:50]}", file=sys.stderr)
        try:
            if context:
                await context.close()
                await asyncio.sleep(0.3)
        except Exception as e:
            print(f"   ⚠️  Error closing context: {str(e)[:50]}", file=sys.stderr)
        try:
            if browser:
                await browser.close()
        except Exception as e:
            print(f"   ⚠️  Error closing browser: {str(e)[:50]}", file=sys.stderr)
        print("   ✅ Browser closed", file=sys.stderr)
        
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



