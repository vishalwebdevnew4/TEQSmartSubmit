"""Form and field discovery functions."""

import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union


async def discover_forms(page) -> List[Dict[str, Any]]:
    """Crawl the page to discover all forms and their fields."""
    # Verify page is still valid before attempting form discovery
    if not page:
        raise RuntimeError("Page is None - cannot discover forms")
    
    # Check if page is closed - try multiple times with small delays
    max_checks = 3
    for check_attempt in range(max_checks):
        try:
            _ = page.url
            break  # Page is valid, continue
        except Exception as e:
            error_str = str(e)
            if "has been closed" in error_str or "Target" in error_str or "closed" in error_str.lower():
                if check_attempt < max_checks - 1:
                    # Wait a bit and try again - page might be in transition
                    import asyncio
                    await asyncio.sleep(0.1)
                    continue
                raise RuntimeError(f"Page was closed during form discovery: {error_str}")
            raise
    
    # Now try to evaluate - wrap in try-catch for better error handling
    # Add a small delay to ensure page is stable before evaluate
    import asyncio
    await asyncio.sleep(0.1)  # Small delay to ensure page is stable
    
    # Double-check page is still valid right before evaluate
    try:
        _ = page.url
    except Exception as final_check:
        error_str = str(final_check)
        if "has been closed" in error_str or "Target" in error_str or "closed" in error_str.lower():
            raise RuntimeError(f"Page was closed right before form discovery evaluate: {error_str}")
        raise
    
    try:
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
    except Exception as e:
        error_str = str(e)
        if "has been closed" in error_str or "Target" in error_str or "closed" in error_str.lower():
            raise RuntimeError(f"Page was closed during form discovery: Page.evaluate: {error_str}")
        # Re-raise other errors as-is
        raise


def find_matching_field(discovered_fields: List[Dict], template_field: Dict) -> Optional[Dict]:
    """Find a discovered field that matches the template field."""
    import re
    
    template_selector = template_field.get("selector", "")
    template_name = template_field.get("name", "")
    
    # Extract name from template selector if present (e.g., "input[name='name']" -> "name")
    if template_selector and not template_name:
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


def auto_detect_field_type(field: Dict) -> Optional[str]:
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

