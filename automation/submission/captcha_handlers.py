"""CAPTCHA detection and handling functions."""

from typing import Any, Dict


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

