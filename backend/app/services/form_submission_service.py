#!/usr/bin/env python3
"""
Enhanced Form Submission Service - Multi-domain form submission with CAPTCHA solving,
retry logic, proxy rotation, and comprehensive logging.
"""

import json
import sys
import os
import argparse
import asyncio
import random
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from playwright.async_api import async_playwright
except ImportError:
    print(json.dumps({"error": "playwright not installed. Run: pip install playwright && playwright install chromium"}))
    sys.exit(1)


class FormSubmissionService:
    """Enhanced form submission with CAPTCHA solving and retry logic."""
    
    def __init__(
        self,
        captcha_api_key: Optional[str] = None,
        use_proxy: bool = False,
        proxy_list: Optional[List[str]] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        self.captcha_api_key = captcha_api_key or os.getenv("CAPTCHA_2CAPTCHA_API_KEY")
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy from the list."""
        if not self.use_proxy or not self.proxy_list:
            return None
        
        proxy_url = random.choice(self.proxy_list)
        # Parse proxy URL (format: http://user:pass@host:port)
        return {"server": proxy_url}
    
    async def solve_captcha(self, page, captcha_type: str, site_key: str) -> Optional[str]:
        """Solve CAPTCHA using external service."""
        if not self.captcha_api_key:
            return None
        
        try:
            if captcha_type == "recaptcha":
                # Use 2captcha API
                import requests
                
                # Submit CAPTCHA
                submit_url = "http://2captcha.com/in.php"
                submit_data = {
                    "key": self.captcha_api_key,
                    "method": "userrecaptcha",
                    "googlekey": site_key,
                    "pageurl": page.url,
                    "json": 1,
                }
                
                response = requests.post(submit_url, data=submit_data, timeout=10)
                result = response.json()
                
                if result.get("status") != 1:
                    return None
                
                captcha_id = result.get("request")
                
                # Wait for solution
                get_url = "http://2captcha.com/res.php"
                for _ in range(60):  # Wait up to 5 minutes
                    await asyncio.sleep(5)
                    get_data = {
                        "key": self.captcha_api_key,
                        "action": "get",
                        "id": captcha_id,
                        "json": 1,
                    }
                    response = requests.get(get_url, params=get_data, timeout=10)
                    result = response.json()
                    
                    if result.get("status") == 1:
                        return result.get("request")
                    elif result.get("request") == "CAPCHA_NOT_READY":
                        continue
                    else:
                        return None
                
                return None
            elif captcha_type == "hcaptcha":
                # Similar for hCaptcha
                import requests
                
                submit_url = "http://2captcha.com/in.php"
                submit_data = {
                    "key": self.captcha_api_key,
                    "method": "hcaptcha",
                    "sitekey": site_key,
                    "pageurl": page.url,
                    "json": 1,
                }
                
                response = requests.post(submit_url, data=submit_data, timeout=10)
                result = response.json()
                
                if result.get("status") != 1:
                    return None
                
                captcha_id = result.get("request")
                
                # Wait for solution
                get_url = "http://2captcha.com/res.php"
                for _ in range(60):
                    await asyncio.sleep(5)
                    get_data = {
                        "key": self.captcha_api_key,
                        "action": "get",
                        "id": captcha_id,
                        "json": 1,
                    }
                    response = requests.get(get_url, params=get_data, timeout=10)
                    result = response.json()
                    
                    if result.get("status") == 1:
                        return result.get("request")
                    elif result.get("request") == "CAPCHA_NOT_READY":
                        continue
                    else:
                        return None
                
                return None
        except Exception as e:
            print(f"CAPTCHA solving error: {e}", file=sys.stderr)
            return None
    
    async def detect_contact_form(self, page) -> Optional[Dict[str, Any]]:
        """Detect contact form on the page."""
        form_info = await page.evaluate("""
            () => {
                const forms = document.querySelectorAll('form');
                for (const form of forms) {
                    const inputs = form.querySelectorAll('input, textarea, select');
                    const hasEmail = Array.from(inputs).some(inp => 
                        inp.type === 'email' || 
                        inp.name?.toLowerCase().includes('email') ||
                        inp.id?.toLowerCase().includes('email')
                    );
                    const hasMessage = Array.from(inputs).some(inp => 
                        inp.tagName === 'TEXTAREA' ||
                        inp.name?.toLowerCase().includes('message') ||
                        inp.id?.toLowerCase().includes('message')
                    );
                    
                    if (hasEmail || hasMessage) {
                        return {
                            found: true,
                            formSelector: form.id ? `#${form.id}` : `form:nth-of-type(${Array.from(document.querySelectorAll('form')).indexOf(form) + 1})`,
                            hasEmail,
                            hasMessage,
                            action: form.action || '',
                            method: form.method || 'get',
                        };
                    }
                }
                return { found: false };
            }
        """)
        return form_info if form_info.get("found") else None
    
    async def fill_form(
        self,
        page,
        form_info: Dict[str, Any],
        business_data: Dict[str, Any],
        message: str,
        website_url: Optional[str] = None,
    ) -> bool:
        """Fill the contact form with business data."""
        try:
            # Fill email field
            email_selectors = [
                'input[type="email"]',
                'input[name*="email" i]',
                'input[id*="email" i]',
            ]
            
            for selector in email_selectors:
                try:
                    email_field = await page.query_selector(selector)
                    if email_field:
                        await email_field.fill(business_data.get("email", "contact@example.com"))
                        break
                except:
                    continue
            
            # Fill name field
            name_selectors = [
                'input[name*="name" i]',
                'input[id*="name" i]',
                'input[placeholder*="name" i]',
            ]
            
            for selector in name_selectors:
                try:
                    name_field = await page.query_selector(selector)
                    if name_field:
                        await name_field.fill(business_data.get("name", ""))
                        break
                except:
                    continue
            
            # Fill phone field
            phone_selectors = [
                'input[type="tel"]',
                'input[name*="phone" i]',
                'input[id*="phone" i]',
            ]
            
            if business_data.get("phone"):
                for selector in phone_selectors:
                    try:
                        phone_field = await page.query_selector(selector)
                        if phone_field:
                            await phone_field.fill(business_data.get("phone"))
                            break
                    except:
                        continue
            
            # Fill message field
            message_selectors = [
                'textarea[name*="message" i]',
                'textarea[id*="message" i]',
                'textarea[placeholder*="message" i]',
                'textarea',
            ]
            
            full_message = message
            if website_url:
                full_message += f"\n\nPreview: {website_url}"
            
            for selector in message_selectors:
                try:
                    message_field = await page.query_selector(selector)
                    if message_field:
                        await message_field.fill(full_message)
                        break
                except:
                    continue
            
            return True
        except Exception as e:
            print(f"Form filling error: {e}", file=sys.stderr)
            return False
    
    async def submit_form(
        self,
        domain_url: str,
        business_data: Dict[str, Any],
        message: str,
        website_url: Optional[str] = None,
        contact_page_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit form to a domain with retry logic and CAPTCHA solving.
        
        Returns:
            Dict with submission status and details
        """
        result = {
            "success": False,
            "domain_url": domain_url,
            "contact_page_url": contact_page_url,
            "status": "failed",
            "captcha_type": None,
            "captcha_solved": False,
            "retry_count": 0,
            "error_message": None,
            "response_html": None,
            "submitted_at": None,
        }
        
        target_url = contact_page_url or domain_url
        
        for attempt in range(self.max_retries):
            result["retry_count"] = attempt + 1
            
            try:
                async with async_playwright() as p:
                    proxy = self.get_proxy()
                    browser = await p.chromium.launch(
                        headless=True,
                        proxy=proxy,
                    )
                    
                    context = await browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    )
                    page = await context.new_page()
                    
                    # Navigate to page
                    await page.goto(target_url, wait_until="networkidle", timeout=30000)
                    
                    # Human-like delay
                    await asyncio.sleep(random.uniform(2, 5))
                    
                    # Detect contact form
                    form_info = await self.detect_contact_form(page)
                    if not form_info:
                        result["error_message"] = "No contact form found"
                        await browser.close()
                        break
                    
                    # Fill form
                    fill_success = await self.fill_form(page, form_info, business_data, message, website_url)
                    if not fill_success:
                        result["error_message"] = "Failed to fill form"
                        await browser.close()
                        break
                    
                    # Check for CAPTCHA
                    captcha_info = await page.evaluate("""
                        () => {
                            const recaptcha = document.querySelector('iframe[src*="recaptcha"]');
                            const hcaptcha = document.querySelector('iframe[src*="hcaptcha"]');
                            
                            if (recaptcha) {
                                const sitekey = document.querySelector('[data-sitekey]')?.getAttribute('data-sitekey') || '';
                                return { type: 'recaptcha', present: true, sitekey };
                            }
                            if (hcaptcha) {
                                const sitekey = document.querySelector('[data-sitekey]')?.getAttribute('data-sitekey') || '';
                                return { type: 'hcaptcha', present: true, sitekey };
                            }
                            return { type: 'none', present: false };
                        }
                    """)
                    
                    if captcha_info.get("present"):
                        result["captcha_type"] = captcha_info.get("type")
                        token = await self.solve_captcha(
                            page,
                            captcha_info.get("type"),
                            captcha_info.get("sitekey", ""),
                        )
                        
                        if token:
                            # Inject token
                            if captcha_info.get("type") == "recaptcha":
                                await page.evaluate(f"""
                                    () => {{
                                        const field = document.querySelector('textarea[name="g-recaptcha-response"]');
                                        if (field) {{
                                            field.value = '{token}';
                                            field.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                        }}
                                    }}
                                """)
                            result["captcha_solved"] = True
                        else:
                            result["error_message"] = "Failed to solve CAPTCHA"
                            await browser.close()
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(self.retry_delay)
                            continue
                    
                    # Submit form
                    await page.evaluate(f"""
                        () => {{
                            const form = document.querySelector('{form_info["formSelector"]}');
                            if (form) {{
                                form.submit();
                            }}
                        }}
                    """)
                    
                    # Wait for response
                    try:
                        await page.wait_for_load_state("networkidle", timeout=15000)
                        await asyncio.sleep(2)
                        
                        result["response_html"] = await page.content()
                        result["submitted_at"] = datetime.utcnow().isoformat()
                        result["success"] = True
                        result["status"] = "success"
                        
                        await browser.close()
                        break
                    except:
                        # Check if we got a success message
                        page_text = await page.inner_text("body")
                        if any(word in page_text.lower() for word in ["thank", "success", "sent", "received"]):
                            result["success"] = True
                            result["status"] = "success"
                            result["response_html"] = await page.content()
                            result["submitted_at"] = datetime.utcnow().isoformat()
                            await browser.close()
                            break
                        
                        result["error_message"] = "Form submission timeout"
                        await browser.close()
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay)
                            continue
                        
            except Exception as e:
                result["error_message"] = str(e)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
        
        return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Submit form to domain")
    parser.add_argument("--domain-url", required=True, help="Domain URL")
    parser.add_argument("--contact-page-url", help="Contact page URL")
    parser.add_argument("--business-data", required=True, help="JSON string with business data")
    parser.add_argument("--message", required=True, help="Submission message")
    parser.add_argument("--website-url", help="Website preview URL")
    parser.add_argument("--max-retries", type=int, default=3, help="Max retry attempts")
    parser.add_argument("--use-proxy", action="store_true", help="Use proxy rotation")
    
    args = parser.parse_args()
    
    try:
        business_data = json.loads(args.business_data)
        
        service = FormSubmissionService(
            max_retries=args.max_retries,
            use_proxy=args.use_proxy,
        )
        
        result = asyncio.run(
            service.submit_form(
                args.domain_url,
                business_data,
                args.message,
                args.website_url,
                args.contact_page_url,
            )
        )
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

