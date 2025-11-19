#!/usr/bin/env python3
"""
CAPTCHA Solver Interface
Supports multiple CAPTCHA solving services and can be extended.
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, Optional
from urllib.parse import urlencode
from urllib.request import urlopen
import urllib.request
import urllib.error


class CaptchaSolver:
    """Base class for CAPTCHA solvers."""
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA v2. Returns token or None."""
        raise NotImplementedError("Subclass must implement solve_recaptcha_v2")
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCaptcha. Returns token or None."""
        raise NotImplementedError("Subclass must implement solve_hcaptcha")


class TwoCaptchaSolver(CaptchaSolver):
    """2captcha.com CAPTCHA solver."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA v2 using 2captcha."""
        if not self.api_key:
            return None
        
        try:
            # Submit CAPTCHA
            submit_url = f"{self.base_url}/in.php"
            submit_params = {
                "key": self.api_key,
                "method": "userrecaptcha",
                "googlekey": site_key,
                "pageurl": page_url,
                "json": 1
            }
            
            submit_response = urlopen(f"{submit_url}?{urlencode(submit_params)}", timeout=30)
            submit_data = json.loads(submit_response.read().decode())
            
            if submit_data.get("status") != 1:
                raise RuntimeError(f"2captcha submit failed: {submit_data.get('request', 'Unknown error')}")
            
            captcha_id = submit_data.get("request")
            
            # Poll for solution (max 2 minutes)
            get_url = f"{self.base_url}/res.php"
            max_attempts = 40
            for attempt in range(max_attempts):
                await asyncio.sleep(5)  # Wait 5 seconds between checks
                
                get_params = {
                    "key": self.api_key,
                    "action": "get",
                    "id": captcha_id,
                    "json": 1
                }
                
                get_response = urlopen(f"{get_url}?{urlencode(get_params)}", timeout=30)
                get_data = json.loads(get_response.read().decode())
                
                if get_data.get("status") == 1:
                    return get_data.get("request")  # Solution token
                
                if get_data.get("request") == "CAPCHA_NOT_READY":
                    continue
                
                raise RuntimeError(f"2captcha solve failed: {get_data.get('request', 'Unknown error')}")
            
            raise RuntimeError("2captcha timeout: Solution not ready after 200 seconds")
            
        except Exception as e:
            raise RuntimeError(f"2captcha API error: {str(e)}")
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCaptcha using 2captcha."""
        if not self.api_key:
            return None
        
        try:
            submit_url = f"{self.base_url}/in.php"
            submit_params = {
                "key": self.api_key,
                "method": "hcaptcha",
                "sitekey": site_key,
                "pageurl": page_url,
                "json": 1
            }
            
            submit_response = urlopen(f"{submit_url}?{urlencode(submit_params)}", timeout=30)
            submit_data = json.loads(submit_response.read().decode())
            
            if submit_data.get("status") != 1:
                raise RuntimeError(f"2captcha submit failed: {submit_data.get('request', 'Unknown error')}")
            
            captcha_id = submit_data.get("request")
            
            # Poll for solution
            get_url = f"{self.base_url}/res.php"
            max_attempts = 40
            for attempt in range(max_attempts):
                await asyncio.sleep(5)
                
                get_params = {
                    "key": self.api_key,
                    "action": "get",
                    "id": captcha_id,
                    "json": 1
                }
                
                get_response = urlopen(f"{get_url}?{urlencode(get_params)}", timeout=30)
                get_data = json.loads(get_response.read().decode())
                
                if get_data.get("status") == 1:
                    return get_data.get("request")
                
                if get_data.get("request") == "CAPCHA_NOT_READY":
                    continue
                
                raise RuntimeError(f"2captcha solve failed: {get_data.get('request', 'Unknown error')}")
            
            raise RuntimeError("2captcha timeout")
            
        except Exception as e:
            raise RuntimeError(f"2captcha API error: {str(e)}")


class AntiCaptchaSolver(CaptchaSolver):
    """AntiCaptcha.com CAPTCHA solver."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anti-captcha.com"
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA v2 using AntiCaptcha."""
        if not self.api_key:
            return None
        
        try:
            import urllib.request
            import urllib.parse
            
            # Create task
            create_task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "NoCaptchaTaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": site_key
                }
            }
            
            create_url = f"{self.base_url}/createTask"
            req = urllib.request.Request(
                create_url,
                data=json.dumps(create_task_data).encode(),
                headers={"Content-Type": "application/json"}
            )
            
            response = urlopen(req, timeout=30)
            result = json.loads(response.read().decode())
            
            if result.get("errorId") != 0:
                raise RuntimeError(f"AntiCaptcha create task failed: {result.get('errorDescription', 'Unknown error')}")
            
            task_id = result.get("taskId")
            
            # Poll for solution
            get_result_url = f"{self.base_url}/getTaskResult"
            max_attempts = 40
            for attempt in range(max_attempts):
                await asyncio.sleep(5)
                
                get_result_data = {
                    "clientKey": self.api_key,
                    "taskId": task_id
                }
                
                req = urllib.request.Request(
                    get_result_url,
                    data=json.dumps(get_result_data).encode(),
                    headers={"Content-Type": "application/json"}
                )
                
                response = urlopen(req, timeout=30)
                result = json.loads(response.read().decode())
                
                if result.get("errorId") != 0:
                    raise RuntimeError(f"AntiCaptcha get result failed: {result.get('errorDescription', 'Unknown error')}")
                
                if result.get("status") == "ready":
                    return result.get("solution", {}).get("gRecaptchaResponse")
                
                if result.get("status") == "processing":
                    continue
                
                raise RuntimeError(f"AntiCaptcha unexpected status: {result.get('status')}")
            
            raise RuntimeError("AntiCaptcha timeout")
            
        except Exception as e:
            raise RuntimeError(f"AntiCaptcha API error: {str(e)}")
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCaptcha using AntiCaptcha."""
        # Similar implementation to recaptcha but with HCaptchaTaskProxyless
        raise NotImplementedError("hCaptcha solving not yet implemented for AntiCaptcha")


class CapSolverSolver(CaptchaSolver):
    """CapSolver.com CAPTCHA solver."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.capsolver.com"
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA v2 using CapSolver."""
        if not self.api_key:
            return None
        
        try:
            import urllib.request
            
            # Create task
            create_task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ReCaptchaV2TaskProxyLess",
                    "websiteURL": page_url,
                    "websiteKey": site_key
                }
            }
            
            create_url = f"{self.base_url}/createTask"
            req = urllib.request.Request(
                create_url,
                data=json.dumps(create_task_data).encode(),
                headers={"Content-Type": "application/json"}
            )
            
            response = urlopen(req, timeout=30)
            result = json.loads(response.read().decode())
            
            if result.get("errorId") != 0:
                raise RuntimeError(f"CapSolver create task failed: {result.get('errorDescription', 'Unknown error')}")
            
            task_id = result.get("taskId")
            
            # Poll for solution
            get_result_url = f"{self.base_url}/getTaskResult"
            max_attempts = 40
            for attempt in range(max_attempts):
                await asyncio.sleep(5)
                
                get_result_data = {
                    "clientKey": self.api_key,
                    "taskId": task_id
                }
                
                req = urllib.request.Request(
                    get_result_url,
                    data=json.dumps(get_result_data).encode(),
                    headers={"Content-Type": "application/json"}
                )
                
                response = urlopen(req, timeout=30)
                result = json.loads(response.read().decode())
                
                if result.get("errorId") != 0:
                    raise RuntimeError(f"CapSolver get result failed: {result.get('errorDescription', 'Unknown error')}")
                
                if result.get("status") == "ready":
                    return result.get("solution", {}).get("gRecaptchaResponse")
                
                if result.get("status") == "processing":
                    continue
                
                raise RuntimeError(f"CapSolver unexpected status: {result.get('status')}")
            
            raise RuntimeError("CapSolver timeout")
            
        except Exception as e:
            raise RuntimeError(f"CapSolver API error: {str(e)}")
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCaptcha using CapSolver."""
        raise NotImplementedError("hCaptcha solving not yet implemented for CapSolver")


class AI4CAPSolver(CaptchaSolver):
    """AI4CAP.com CAPTCHA solver (free trial available)."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.ai4cap.com"
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA v2 using AI4CAP REST API."""
        if not self.api_key:
            return None
        
        try:
            print("🤖 Using AI4CAP service (free trial)...", file=sys.stderr)
            
            # Step 1: Submit CAPTCHA task
            submit_url = f"{self.base_url}/api/captcha/solve"
            submit_data = {
                "type": "recaptcha_v2",
                "siteKey": site_key,
                "pageUrl": page_url
            }
            
            req = urllib.request.Request(
                submit_url,
                data=json.dumps(submit_data).encode(),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            print("   📤 Submitting CAPTCHA to AI4CAP...", file=sys.stderr)
            response = urlopen(req, timeout=30)
            result = json.loads(response.read().decode())
            
            # Check for errors in response
            if result.get("error"):
                raise RuntimeError(f"AI4CAP submit failed: {result.get('error', 'Unknown error')}")
            
            task_id = result.get("taskId")
            if not task_id:
                raise RuntimeError(f"AI4CAP did not return taskId: {result}")
            
            print(f"   ✅ Task submitted, ID: {task_id[:20]}...", file=sys.stderr)
            
            # Step 2: Poll for solution
            get_result_url = f"{self.base_url}/api/captcha/result/{task_id}"
            max_attempts = 60  # 2 minutes max (60 * 2 seconds)
            timeout = 120
            
            start_time = time.time()
            for attempt in range(max_attempts):
                await asyncio.sleep(2)  # Poll every 2 seconds
                
                # Check timeout
                if time.time() - start_time > timeout:
                    raise RuntimeError(f"AI4CAP timeout: Solution not ready after {timeout} seconds")
                
                try:
                    get_req = urllib.request.Request(
                        get_result_url,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        }
                    )
                    
                    get_response = urlopen(get_req, timeout=30)
                    result_data = json.loads(get_response.read().decode())
                    
                    status = result_data.get("status")
                    
                    if status == "completed":
                        solution = result_data.get("solution", {})
                        token = solution.get("gRecaptchaResponse")
                        if token:
                            print(f"   ✅ CAPTCHA solved by AI4CAP! (attempt {attempt + 1})", file=sys.stderr)
                            return token
                        else:
                            raise RuntimeError("AI4CAP returned completed status but no token in solution")
                    
                    elif status == "failed":
                        error_msg = result_data.get("error", "Unknown error")
                        raise RuntimeError(f"AI4CAP task failed: {error_msg}")
                    
                    elif status == "processing" or status == "pending":
                        # Still processing, continue polling
                        if attempt % 10 == 0:  # Print every 10 attempts (20 seconds)
                            print(f"   ⏳ Waiting for solution... ({attempt + 1}/{max_attempts})", file=sys.stderr)
                        continue
                    
                    else:
                        # Unknown status
                        print(f"   ⚠️  Unknown status: {status}, continuing...", file=sys.stderr)
                        continue
                        
                except urllib.error.HTTPError as http_err:
                    if http_err.code == 404:
                        # Task not found, might still be processing
                        continue
                    else:
                        error_body = http_err.read().decode() if http_err.fp else "Unknown error"
                        raise RuntimeError(f"AI4CAP HTTP error {http_err.code}: {error_body}")
                except Exception as poll_error:
                    # Continue polling on other errors
                    if attempt % 10 == 0:
                        print(f"   ⚠️  Polling error: {str(poll_error)[:50]}, retrying...", file=sys.stderr)
                    continue
            
            raise RuntimeError(f"AI4CAP timeout: Solution not ready after {max_attempts} polling attempts")
                
        except Exception as e:
            raise RuntimeError(f"AI4CAP API error: {str(e)}")
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCaptcha using AI4CAP REST API."""
        if not self.api_key:
            return None
        
        try:
            print("🤖 Using AI4CAP service for hCaptcha...", file=sys.stderr)
            
            # Submit hCaptcha task
            submit_url = f"{self.base_url}/api/captcha/solve"
            submit_data = {
                "type": "hcaptcha",
                "siteKey": site_key,
                "pageUrl": page_url
            }
            
            req = urllib.request.Request(
                submit_url,
                data=json.dumps(submit_data).encode(),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            response = urlopen(req, timeout=30)
            result = json.loads(response.read().decode())
            
            if result.get("error"):
                raise RuntimeError(f"AI4CAP submit failed: {result.get('error', 'Unknown error')}")
            
            task_id = result.get("taskId")
            if not task_id:
                raise RuntimeError(f"AI4CAP did not return taskId: {result}")
            
            # Poll for solution
            get_result_url = f"{self.base_url}/api/captcha/result/{task_id}"
            max_attempts = 60
            timeout = 120
            start_time = time.time()
            
            for attempt in range(max_attempts):
                await asyncio.sleep(2)
                
                if time.time() - start_time > timeout:
                    raise RuntimeError(f"AI4CAP timeout after {timeout} seconds")
                
                get_req = urllib.request.Request(
                    get_result_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                get_response = urlopen(get_req, timeout=30)
                result_data = json.loads(get_response.read().decode())
                
                status = result_data.get("status")
                
                if status == "completed":
                    solution = result_data.get("solution", {})
                    return solution.get("gRecaptchaResponse") or solution.get("token")
                elif status == "failed":
                    raise RuntimeError(f"AI4CAP task failed: {result_data.get('error', 'Unknown error')}")
                elif status in ["processing", "pending"]:
                    continue
            
            raise RuntimeError("AI4CAP timeout: Solution not ready")
            
        except Exception as e:
            raise RuntimeError(f"AI4CAP API error: {str(e)}")


class LocalCaptchaSolver(CaptchaSolver):
    """
    Fully automated local CAPTCHA solver.
    Uses browser automation and audio/image recognition to solve CAPTCHAs.
    """
    
    def __init__(self, page=None):
        """
        Initialize local solver.
        
        Args:
            page: Playwright page object (required for solving)
        """
        self.page = page
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """
        Automatically solve reCAPTCHA v2 using browser automation.
        
        Strategy:
        1. Find and click the reCAPTCHA checkbox
        2. Wait for token (sometimes no challenge appears)
        3. If challenge appears, solve it using audio/image recognition
        4. Return the solved token
        """
        if not self.page:
            raise RuntimeError("LocalCaptchaSolver requires a Playwright page object")
        
        try:
            # Step 1: Find and click the reCAPTCHA checkbox
            print("🖱️  Clicking reCAPTCHA checkbox...", file=sys.stderr)
            try:
                await self._click_recaptcha_checkbox()
            except Exception as e:
                print(f"⚠️  Error clicking checkbox: {str(e)[:50]}", file=sys.stderr)
                # Continue anyway - checkbox might already be clicked
            
            # Step 2: Quickly check if token is already available (no challenge)
            # Sometimes reCAPTCHA solves immediately without challenge
            for i in range(3):
                await asyncio.sleep(0.5)  # Faster polling
                token = await self._get_recaptcha_token()
                if token:
                    print(f"✅ CAPTCHA solved without challenge! (checked {i+1} times)", file=sys.stderr)
                    return token
            
            # Step 3: Wait a bit for challenge to appear, then check
            print("🔍 Waiting for challenge to appear...", file=sys.stderr)
            await asyncio.sleep(2)  # Wait for challenge iframe to load
            challenge_present = await self._check_challenge_present()
            
            if challenge_present:
                print("🎯 Challenge detected, attempting to solve...", file=sys.stderr)
                
                # Wait for challenge frame to be fully loaded
                await asyncio.sleep(1)
                
                # Get the challenge frame
                challenge_frame = await self.page.query_selector('iframe[title*="challenge"], iframe[src*="bframe"]')
                if not challenge_frame:
                    # Try waiting a bit more
                    await asyncio.sleep(2)
                    challenge_frame = await self.page.query_selector('iframe[title*="challenge"], iframe[src*="bframe"]')
                
                if challenge_frame:
                    frame = await challenge_frame.content_frame()
                    if frame:
                        # Wait for frame content to load
                        await asyncio.sleep(1)
                        
                        # Check if it's an image challenge and switch to audio
                        is_image_challenge = await frame.evaluate("""
                            () => {
                                const grid = document.querySelector('.rc-imageselect-grid, .rc-imageselect-tile, .rc-imageselect-challenge');
                                return grid !== null;
                            }
                        """)
                        
                        if is_image_challenge:
                            print("🖼️  Image challenge detected, switching to audio...", file=sys.stderr)
                            # Use a more comprehensive approach to switch to audio
                            audio_switched = await self._switch_to_audio_challenge(frame)
                            if audio_switched:
                                print("   ✅ Successfully switched to audio challenge", file=sys.stderr)
                                await asyncio.sleep(2)  # Wait for audio challenge to load
                            else:
                                print("   ⚠️  Could not switch to audio, will try anyway", file=sys.stderr)
                
                # Try audio challenge solving
                print("🎧 Attempting to solve audio challenge...", file=sys.stderr)
                solved = await self._solve_audio_challenge()
                
                # After solving attempt, wait and check for token
                # This is critical - sometimes the token appears after a delay
                print("⏳ Waiting for CAPTCHA token after solving attempt...", file=sys.stderr)
                max_wait_attempts = 20  # Wait up to 20 seconds
                for i in range(max_wait_attempts):
                    await asyncio.sleep(1)
                    token = await self._get_recaptcha_token()
                    if token:
                        print(f"✅ Token received! (waited {i+1}s)", file=sys.stderr)
                        return token
                    
                    # Every 5 seconds, check if challenge is still present
                    if i % 5 == 0 and i > 0:
                        challenge_still_present = await self._check_challenge_present()
                        if not challenge_still_present:
                            print(f"   ✅ Challenge iframe disappeared, checking for token...", file=sys.stderr)
                            # Challenge closed, token should be available
                            token = await self._get_recaptcha_token()
                            if token:
                                print(f"✅ Token found after challenge closed!", file=sys.stderr)
                                return token
                        print(f"   Still waiting for token... ({i+1}/{max_wait_attempts})", file=sys.stderr)
                
                # If audio solving reported success but no token yet, try one more time
                if solved:
                    print("   ⚠️  Audio solving reported success but token not found, retrying...", file=sys.stderr)
                    await asyncio.sleep(3)
                    token = await self._get_recaptcha_token()
                    if token:
                        print("✅ Token found on retry!", file=sys.stderr)
                        return token
                
                # If audio failed, try image challenge as last resort
                if not solved:
                    print("🖼️  Audio failed, trying image challenge as last resort...", file=sys.stderr)
                    solved = await self._solve_challenge()
                    if solved:
                        # Wait for token after image challenge
                        for i in range(10):
                            await asyncio.sleep(1)
                            token = await self._get_recaptcha_token()
                            if token:
                                print(f"✅ Token received after image challenge! (waited {i+1}s)", file=sys.stderr)
                                return token
                
                # Final attempt - check one more time
                print("🔍 Final token check...", file=sys.stderr)
                await asyncio.sleep(2)
                token = await self._get_recaptcha_token()
                if token:
                    print("✅ Token found on final check!", file=sys.stderr)
                    return token
                
                print("⚠️  Warning: Could not retrieve CAPTCHA token after solving attempt", file=sys.stderr)
                return None
            
        except Exception as e:
            print(f"❌ Local CAPTCHA solving error: {e}", file=sys.stderr)
            raise RuntimeError(f"Local CAPTCHA solving failed: {str(e)}")
    
    async def _click_recaptcha_checkbox(self):
        """Click the reCAPTCHA checkbox using multiple strategies."""
        print("   🔍 Looking for reCAPTCHA checkbox...", file=sys.stderr)
        
        try:
            # First, wait for reCAPTCHA to be loaded
            print("   ⏳ Waiting for reCAPTCHA to load...", file=sys.stderr)
            await asyncio.sleep(2)
            
            # Check if reCAPTCHA is already solved
            token = await self._get_recaptcha_token()
            if token:
                print("   ✅ CAPTCHA already solved!", file=sys.stderr)
                return
            
            # Strategy 1: Find and click the checkbox in the iframe (most reliable)
            print("   📋 Strategy 1: Looking for reCAPTCHA iframe...", file=sys.stderr)
            iframe_selectors = [
                'iframe[src*="recaptcha"][src*="anchor"]',
                'iframe[title*="reCAPTCHA"]',
                'iframe[title*="recaptcha"]',
                '.g-recaptcha iframe',
                'iframe[src*="google.com/recaptcha"]'
            ]
            
            iframe = None
            for selector in iframe_selectors:
                try:
                    iframe = await self.page.query_selector(selector)
                    if iframe:
                        print(f"   ✅ Found iframe with selector: {selector}", file=sys.stderr)
                        break
                except:
                    continue
            
            if iframe:
                try:
                    print("   🔄 Accessing iframe content...", file=sys.stderr)
                    frame = await iframe.content_frame()
                    if frame:
                        print("   ✅ Iframe content accessible", file=sys.stderr)
                        # Wait for checkbox to be ready
                        try:
                            await frame.wait_for_selector('#recaptcha-anchor', timeout=10000)
                            print("   ✅ Checkbox element found in iframe", file=sys.stderr)
                        except:
                            print("   ⚠️  Checkbox selector not found, trying alternative...", file=sys.stderr)
                        
                        checkbox = await frame.query_selector('#recaptcha-anchor')
                        if not checkbox:
                            # Try alternative selectors
                            checkbox = await frame.query_selector('.recaptcha-checkbox')
                            if not checkbox:
                                checkbox = await frame.query_selector('[role="checkbox"]')
                        
                        if checkbox:
                            print("   🖱️  Clicking checkbox...", file=sys.stderr)
                            # Scroll into view
                            await checkbox.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)
                            
                            # Try multiple click methods
                            try:
                                await checkbox.click(timeout=5000)
                                print("   ✅ Checkbox clicked successfully!", file=sys.stderr)
                            except:
                                # Try JavaScript click
                                await frame.evaluate("""
                                    () => {
                                        const checkbox = document.querySelector('#recaptcha-anchor') || 
                                                         document.querySelector('.recaptcha-checkbox') ||
                                                         document.querySelector('[role="checkbox"]');
                                        if (checkbox) {
                                            checkbox.click();
                                        }
                                    }
                                """)
                                print("   ✅ Checkbox clicked via JavaScript!", file=sys.stderr)
                            
                            await asyncio.sleep(3)  # Wait for response
                            return
                        else:
                            print("   ⚠️  Checkbox element not found in iframe", file=sys.stderr)
                except Exception as e:
                    print(f"   ⚠️  Error accessing iframe: {str(e)[:100]}", file=sys.stderr)
            
            # Strategy 2: Click via JavaScript directly on the page
            print("   📋 Strategy 2: Trying JavaScript click on page...", file=sys.stderr)
            click_result = await self.page.evaluate("""
                () => {
                    // Find the reCAPTCHA container
                    const recaptchaDiv = document.querySelector('.g-recaptcha');
                    if (recaptchaDiv) {
                        const iframe = recaptchaDiv.querySelector('iframe');
                        if (iframe) {
                            // Try to access iframe and click
                            try {
                                const frame = iframe.contentWindow || iframe.contentDocument;
                                if (frame && frame.document) {
                                    const checkbox = frame.document.querySelector('#recaptcha-anchor');
                                    if (checkbox) {
                                        checkbox.click();
                                        return { success: true, method: 'iframe-content' };
                                    }
                                }
                            } catch (e) {
                                // Cross-origin, can't access
                            }
                            
                            // Click on iframe position
                            const rect = iframe.getBoundingClientRect();
                            const x = rect.left + rect.width / 2;
                            const y = rect.top + rect.height / 2;
                            
                            // Create click event at iframe center
                            const clickEvent = new MouseEvent('click', {
                                view: window,
                                bubbles: true,
                                cancelable: true,
                                clientX: x,
                                clientY: y,
                                button: 0
                            });
                            
                            // Dispatch on iframe
                            iframe.dispatchEvent(clickEvent);
                            
                            // Also try clicking the div container
                            recaptchaDiv.dispatchEvent(clickEvent);
                            
                            return { success: true, method: 'iframe-position', x: x, y: y };
                        }
                    }
                    return { success: false, error: 'No reCAPTCHA found' };
                }
            """)
            
            if click_result.get("success"):
                print(f"   ✅ JavaScript click executed: {click_result.get('method')}", file=sys.stderr)
                await asyncio.sleep(3)
                return
            else:
                print(f"   ⚠️  JavaScript click failed: {click_result.get('error', 'Unknown')}", file=sys.stderr)
            
            # Strategy 3: Use Playwright's click on iframe element directly
            print("   📋 Strategy 3: Trying direct iframe click...", file=sys.stderr)
            iframe = await self.page.query_selector('iframe[src*="recaptcha"]')
            if iframe:
                try:
                    # Get iframe position and click there
                    box = await iframe.bounding_box()
                    if box:
                        x = box['x'] + box['width'] / 2
                        y = box['y'] + box['height'] / 2
                        print(f"   🖱️  Clicking at iframe center: ({x}, {y})", file=sys.stderr)
                        await self.page.mouse.click(x, y)
                        await asyncio.sleep(3)
                        print("   ✅ Direct click executed!", file=sys.stderr)
                        return
                except Exception as e:
                    print(f"   ⚠️  Direct click failed: {str(e)[:100]}", file=sys.stderr)
            
            # If all strategies failed, raise error
            raise RuntimeError("Could not find or click reCAPTCHA checkbox after trying all strategies")
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Failed to click reCAPTCHA checkbox: {error_msg[:200]}", file=sys.stderr)
            raise RuntimeError(f"Failed to click reCAPTCHA checkbox: {error_msg}")
    
    async def _check_challenge_present(self) -> bool:
        """Check if a challenge (audio/image) is present."""
        try:
            result = await self.page.evaluate("""
                () => {
                    // Check for challenge iframe
                    const challengeFrame = document.querySelector('iframe[title*="challenge"], iframe[src*="bframe"]');
                    return challengeFrame !== null;
                }
            """)
            return result
        except:
            return False
    
    async def _switch_to_audio_challenge(self, frame) -> bool:
        """Switch from image challenge to audio challenge."""
        try:
            # Comprehensive list of audio button selectors
            audio_selectors = [
                '#recaptcha-audio-button',
                'button[title*="audio"]',
                'button[title*="Audio"]',
                '.rc-button-audio',
                'button.rc-button-audio',
                'button[aria-label*="audio"]',
                'button[aria-label*="Audio"]',
                'button[id*="audio"]',
                'div[role="button"][aria-label*="audio"]',
                'div[role="button"][aria-label*="Audio"]',
                'a.rc-audiochallenge-tdownload',
                'a[href*="audio"]',
                '[class*="audio"]',
                '[id*="audio"]'
            ]
            
            # Try direct selector clicks first
            for selector in audio_selectors:
                try:
                    audio_btn = await frame.query_selector(selector)
                    if audio_btn:
                        is_visible = await audio_btn.is_visible()
                        if is_visible:
                            print(f"   ✅ Found audio button: {selector}, clicking...", file=sys.stderr)
                            await audio_btn.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)
                            await audio_btn.click()
                            await asyncio.sleep(2)
                            return True
                except Exception as e:
                    continue
            
            # If direct clicks failed, try JavaScript approach
            print("   🔄 Trying JavaScript to find and click audio button...", file=sys.stderr)
            try:
                switched = await frame.evaluate("""
                    () => {
                        // Try all possible elements
                        const allElements = document.querySelectorAll('button, a, div[role="button"], span[role="button"]');
                        for (const el of allElements) {
                            const text = (el.textContent || el.innerText || '').toLowerCase();
                            const title = (el.getAttribute('title') || '').toLowerCase();
                            const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
                            const id = (el.id || '').toLowerCase();
                            const className = (el.className || '').toLowerCase();
                            const href = (el.getAttribute('href') || '').toLowerCase();
                            
                            // Check if it's an audio button
                            if (text.includes('audio') || title.includes('audio') || 
                                ariaLabel.includes('audio') || id.includes('audio') ||
                                className.includes('audio') || href.includes('audio') ||
                                id === 'recaptcha-audio-button') {
                                // Try to click it
                                try {
                                    el.click();
                                    return true;
                                } catch (e) {
                                    // Try dispatchEvent as fallback
                                    const clickEvent = new MouseEvent('click', { bubbles: true, cancelable: true });
                                    el.dispatchEvent(clickEvent);
                                    return true;
                                }
                            }
                        }
                        return false;
                    }
                """)
                if switched:
                    print("   ✅ Audio button clicked via JavaScript!", file=sys.stderr)
                    await asyncio.sleep(2)
                    return True
            except Exception as e:
                print(f"   ⚠️  JavaScript click failed: {str(e)[:50]}", file=sys.stderr)
            
            return False
        except Exception as e:
            print(f"   ⚠️  Error switching to audio: {str(e)[:50]}", file=sys.stderr)
            return False
    
    async def _solve_audio_challenge(self) -> bool:
        """Solve audio CAPTCHA challenge - SIMPLIFIED VERSION."""
        try:
            # Quick timeout wrapper to prevent hanging
            # Increase timeout for headless mode (audio challenges take longer without display)
            # Check if page is in headless mode by checking if it has a display
            is_headless = True  # Default to headless
            try:
                # Try to check if we're in headless mode
                # In headless mode, some operations might behave differently
                if self.page:
                    # Check viewport size - headless often uses default sizes
                    viewport = await self.page.viewport_size()
                    # This is a heuristic - adjust as needed
                    is_headless = viewport is None or viewport.get('width', 0) < 800
            except:
                pass
            
            timeout = 90 if is_headless else 55  # 90 seconds for headless, 55 for visible
            print(f"   ⏱️  Audio challenge timeout: {timeout}s ({'headless' if is_headless else 'visible'} mode)", file=sys.stderr)
            result = await asyncio.wait_for(self._solve_audio_impl(), timeout=timeout)
            return result
        except asyncio.TimeoutError:
            print(f"   ⏰ Audio solving timeout ({timeout}s)", file=sys.stderr)
            return False
        except Exception as e:
            print(f"   ❌ Audio solving error: {str(e)[:80]}", file=sys.stderr)
            return False
    
    async def _solve_audio_impl(self) -> bool:
        """Internal audio solving implementation."""
        try:
            if not self.page:
                print("   ❌ Page object is None", file=sys.stderr)
                return False
            
            try:
                # Quick check if page is still open
                await self.page.evaluate("() => document.title")
            except Exception as e:
                print(f"   ❌ Page is closed or invalid: {str(e)[:50]}", file=sys.stderr)
                return False
            
            print("   🎧 Starting audio challenge solving...", file=sys.stderr)
            # Switch to challenge iframe
            challenge_frame = await self.page.query_selector('iframe[title*="challenge"], iframe[src*="bframe"]')
            if not challenge_frame:
                print("   ⚠️  Challenge iframe not found", file=sys.stderr)
                return False
            
            frame = await challenge_frame.content_frame()
            if not frame:
                print("   ⚠️  Could not access challenge iframe content", file=sys.stderr)
                return False
            
            # Wait for challenge to load
            await asyncio.sleep(2)
            
            # First, check if Buster extension is available (simpler approach)
            # Note: Buster's solver-button is now in a shadow DOM (issue #273)
            # We'll try multiple approaches to access it
            print("   🔍 Checking for Buster extension...", file=sys.stderr)
            
            # Try to find Buster button (may be in shadow DOM)
            buster_found = await frame.evaluate("""
                () => {
                    // Try direct selector first
                    let button = document.querySelector('#solver-button, button[id*="solver"], button[class*="solver"]');
                    if (button) return true;
                    
                    // Try to access shadow DOM
                    const recaptchaContainer = document.querySelector('.rc-audiochallenge-tdownload, .rc-audiochallenge-response-field');
                    if (recaptchaContainer) {
                        // Check if there's a shadow root
                        if (recaptchaContainer.shadowRoot) {
                            button = recaptchaContainer.shadowRoot.querySelector('#solver-button, button[id*="solver"]');
                            if (button) return true;
                        }
                    }
                    
                    // Check all elements with shadow roots
                    const allElements = document.querySelectorAll('*');
                    for (let el of allElements) {
                        if (el.shadowRoot) {
                            button = el.shadowRoot.querySelector('#solver-button, button[id*="solver"]');
                            if (button) return true;
                        }
                    }
                    
                    return false;
                }
            """)
            
            if buster_found:
                try:
                    print("   🤖 Buster extension detected, attempting to use it...", file=sys.stderr)
                    # Try clicking via JavaScript to handle shadow DOM
                    clicked = await frame.evaluate("""
                        () => {
                            // Try direct click first
                            let button = document.querySelector('#solver-button, button[id*="solver"], button[class*="solver"]');
                            if (button) {
                                button.click();
                                return true;
                            }
                            
                            // Try shadow DOM access
                            const allElements = document.querySelectorAll('*');
                            for (let el of allElements) {
                                if (el.shadowRoot) {
                                    button = el.shadowRoot.querySelector('#solver-button, button[id*="solver"]');
                                    if (button) {
                                        button.click();
                                        return true;
                                    }
                                }
                            }
                            
                            return false;
                        }
                    """)
                    
                    if clicked:
                        print("   ✅ Buster solver button clicked, waiting for solution...", file=sys.stderr)
                        await asyncio.sleep(3)  # Reduced from 5 to 3 seconds
                        # Check if token appeared
                        token = await self._get_recaptcha_token()
                        if token:
                            print("   ✅ CAPTCHA solved by Buster extension!", file=sys.stderr)
                            return True
                    else:
                        print("   ⚠️  Buster detected but button not accessible (may be in closed shadow DOM)", file=sys.stderr)
                        print("   💡 Note: Buster's solver-button is now in shadow DOM (see issue #273)", file=sys.stderr)
                except Exception as e:
                    print(f"   ⚠️  Buster button click failed: {str(e)[:50]}, falling back to manual solving...", file=sys.stderr)
            
            # Check if we're already in audio challenge mode
            is_audio_challenge = await frame.evaluate("""
                () => {
                    // Check for audio challenge elements
                    const audioInput = document.querySelector('#audio-response, input[name="audio-response"]');
                    const audioDownload = document.querySelector('.rc-audiochallenge-tdownload, a[href*="audio"]');
                    const audioButton = document.querySelector('#recaptcha-audio-button');
                    return audioInput !== null || audioDownload !== null || audioButton !== null;
                }
            """)
            
            if not is_audio_challenge:
                # We need to switch to audio challenge
                print("   🔘 Switching to audio challenge...", file=sys.stderr)
                audio_button_selectors = [
                    '#recaptcha-audio-button',
                    'button[title*="audio"]',
                    'button[title*="Audio"]',
                    '.rc-button-audio',
                    'button.rc-button-audio',
                    'button[id*="audio"]',
                    'div[role="button"][aria-label*="audio"]',
                    'div[role="button"][aria-label*="Audio"]',
                    'a[href*="audio"]'
                ]
                
                audio_clicked = False
                for selector in audio_button_selectors:
                    try:
                        audio_button = await frame.query_selector(selector)
                        if audio_button:
                            is_visible = await audio_button.is_visible()
                            if is_visible:
                                print(f"   ✅ Found audio button: {selector}, clicking...", file=sys.stderr)
                                await audio_button.scroll_into_view_if_needed()
                                await asyncio.sleep(0.5)
                                await audio_button.click()
                                print("   ✅ Audio button clicked, waiting for audio challenge to load...", file=sys.stderr)
                                await asyncio.sleep(3)  # Wait for audio challenge to load
                                audio_clicked = True
                                break
                    except Exception as e:
                        print(f"   ⚠️  Failed to click audio button {selector}: {str(e)[:50]}", file=sys.stderr)
                        continue
                
                # Try JavaScript if direct click failed
                if not audio_clicked:
                    print("   🔄 Trying JavaScript to click audio button...", file=sys.stderr)
                    try:
                        clicked = await frame.evaluate("""
                            () => {
                                const buttons = document.querySelectorAll('button, a, div[role="button"]');
                                for (const btn of buttons) {
                                    const text = (btn.textContent || '').toLowerCase();
                                    const title = (btn.getAttribute('title') || '').toLowerCase();
                                    const id = (btn.id || '').toLowerCase();
                                    if (text.includes('audio') || title.includes('audio') || id.includes('audio')) {
                                        btn.click();
                                        return true;
                                    }
                                }
                                return false;
                            }
                        """)
                        if clicked:
                            print("   ✅ Audio button clicked via JavaScript!", file=sys.stderr)
                            await asyncio.sleep(3)
                            audio_clicked = True
                    except:
                        pass
                
                if not audio_clicked:
                    print("   ⚠️  Could not switch to audio challenge, but continuing anyway...", file=sys.stderr)
            else:
                print("   ✅ Already in audio challenge mode", file=sys.stderr)
            
            # Set up network request monitoring at page level to capture audio URLs
            audio_urls_from_network = []
            
            def handle_page_request(request):
                try:
                    url = request.url
                    # Check if this request is related to audio/recaptcha
                    url_lower = url.lower()
                    if 'recaptcha' in url_lower and ('audio' in url_lower or 'mp3' in url_lower or 'wav' in url_lower or 'sound' in url_lower or 'tts' in url_lower or 'bframe' in url_lower):
                        if url not in audio_urls_from_network:
                            audio_urls_from_network.append(url)
                            print(f"   📡 Network request detected: {url[:70]}...", file=sys.stderr)
                except:
                    pass
            
            def handle_page_response(response):
                try:
                    url = response.url
                    content_type = response.headers.get('content-type', '').lower()
                    url_lower = url.lower()
                    # Check if this response is for an audio file
                    is_audio = (
                        ('recaptcha' in url_lower and ('audio' in url_lower or 'mp3' in url_lower or 'wav' in url_lower or 'sound' in url_lower or 'tts' in url_lower)) or
                        ('audio' in content_type or 'mp3' in content_type or 'wav' in content_type) or
                        (url_lower.endswith('.mp3') or url_lower.endswith('.wav'))
                    )
                    if is_audio:
                        if url not in audio_urls_from_network:
                            audio_urls_from_network.append(url)
                            print(f"   📡 Network response detected: {url[:70]}...", file=sys.stderr)
                except:
                    pass
            
            # Monitor network requests at page level (frames don't have event handlers)
            # Remove existing handlers first to avoid duplicates
            try:
                self.page.remove_listener("request", handle_page_request)
            except:
                pass
            try:
                self.page.remove_listener("response", handle_page_response)
            except:
                pass
            
            self.page.on("request", handle_page_request)
            self.page.on("response", handle_page_response)
            
            # Wait longer for audio challenge to fully load and for network requests
            print("   ⏳ Waiting for audio challenge to fully load (checking network requests)...", file=sys.stderr)
            # Wait and check if audio elements appear - wait longer for iframe to fully load
            audio_ready = False
            for wait_attempt in range(15):  # Wait up to 15 seconds
                await asyncio.sleep(1)
                
                # Check if page is still valid
                try:
                    await self.page.evaluate("() => document.title")
                except:
                    print(f"   ⚠️  Page closed during wait (attempt {wait_attempt + 1})", file=sys.stderr)
                    break
                
                # Check if audio elements are now present
                try:
                    has_audio = await frame.evaluate("""
                        () => {
                            // Check for audio challenge UI elements
                            const audioInput = document.querySelector('#audio-response, input[name="audio-response"], input#audio-response');
                            const audioDownload = document.querySelector('.rc-audiochallenge-tdownload, a[href*="audio"], a.rc-audiochallenge-tdownload');
                            const audioElement = document.querySelector('audio');
                            const audioButton = document.querySelector('#recaptcha-audio-button');
                            const audioChallenge = document.querySelector('.rc-audiochallenge');
                            
                            // Also check if there's any content in the frame
                            const hasContent = document.body && document.body.children.length > 0;
                            
                            return {
                                hasAudioInput: audioInput !== null,
                                hasAudioDownload: audioDownload !== null,
                                hasAudioElement: audioElement !== null,
                                hasAudioButton: audioButton !== null,
                                hasAudioChallenge: audioChallenge !== null,
                                hasContent: hasContent,
                                bodyChildren: document.body ? document.body.children.length : 0
                            };
                        }
                    """)
                    
                    if has_audio.get('hasAudioInput') or has_audio.get('hasAudioDownload') or has_audio.get('hasAudioElement') or has_audio.get('hasAudioChallenge'):
                        print(f"   ✅ Audio challenge elements appeared after {wait_attempt + 1} seconds", file=sys.stderr)
                        print(f"      Details: {has_audio}", file=sys.stderr)
                        audio_ready = True
                        break
                    elif has_audio.get('hasContent'):
                        # Frame has content, might be loading
                        if wait_attempt % 3 == 0:
                            print(f"   ⏳ Frame has content ({has_audio.get('bodyChildren')} elements), waiting for audio... ({wait_attempt + 1}/15)", file=sys.stderr)
                    else:
                        # Frame might be empty or still loading
                        if wait_attempt % 3 == 0:
                            print(f"   ⏳ Still waiting for audio challenge to load... ({wait_attempt + 1}/15)", file=sys.stderr)
                except Exception as e:
                    if "closed" in str(e).lower() or "target" in str(e).lower():
                        print(f"   ⚠️  Frame closed during check (attempt {wait_attempt + 1})", file=sys.stderr)
                        # Try to get frame again
                        try:
                            challenge_frame = await self.page.query_selector('iframe[title*="challenge"], iframe[src*="bframe"]')
                            if challenge_frame:
                                frame = await challenge_frame.content_frame()
                        except:
                            pass
                    continue
            
            if not audio_ready:
                print("   ⚠️  Audio elements not fully detected, but continuing anyway...", file=sys.stderr)
                # Check what's actually in the frame
                try:
                    frame_info = await frame.evaluate("""
                        () => {
                            return {
                                html: document.body ? document.body.innerHTML.substring(0, 500) : 'no body',
                                allElements: document.querySelectorAll('*').length,
                                links: document.querySelectorAll('a').length,
                                buttons: document.querySelectorAll('button').length,
                                inputs: document.querySelectorAll('input').length
                            };
                        }
                    """)
                    print(f"   📊 Frame content info: {frame_info}", file=sys.stderr)
                except:
                    pass
            
            # Try to click play/download button if it exists - CRITICAL: Must play audio
            print("   🎵 Looking for audio play/download button...", file=sys.stderr)
            audio_played = False
            try:
                play_button_selectors = [
                    'a.rc-audiochallenge-tdownload',  # Download link (most common)
                    '.rc-audiochallenge-play-button',
                    'button[title*="play" i]',
                    'button[aria-label*="play" i]',
                    'a[href*="audio"]',
                    'a[class*="download"]',
                    '[class*="play"][class*="button"]',
                    '[id*="play"]',
                    '[id*="audio"]'
                ]
                for selector in play_button_selectors:
                    try:
                        play_btn = await frame.query_selector(selector)
                        if play_btn:
                            is_visible = await play_btn.is_visible()
                            if is_visible:
                                print(f"   ▶️  Found play/download button: {selector}, clicking to play audio...", file=sys.stderr)
                                # Scroll into view first
                                await play_btn.scroll_into_view_if_needed()
                                await asyncio.sleep(0.5)
                                
                                # Try multiple click methods
                                try:
                                    await play_btn.click(timeout=5000)
                                    print("   ✅ Play button clicked!", file=sys.stderr)
                                    audio_played = True
                                except:
                                    # Try JavaScript click
                                    await frame.evaluate("""
                                        (selector) => {
                                            const btn = document.querySelector(selector);
                                            if (btn) {
                                                btn.click();
                                                // Also try to trigger play if it's an audio element
                                                const audio = btn.closest('.rc-audiochallenge')?.querySelector('audio');
                                                if (audio) {
                                                    audio.play();
                                                }
                                            }
                                        }
                                    """, selector)
                                    print("   ✅ Play button clicked via JavaScript!", file=sys.stderr)
                                    audio_played = True
                                
                                await asyncio.sleep(3)  # Wait for audio to start playing
                                break
                    except Exception as e:
                        print(f"   ⚠️  Error with selector {selector}: {str(e)[:50]}", file=sys.stderr)
                        continue
            except Exception as e:
                print(f"   ⚠️  Error finding play button: {str(e)[:50]}", file=sys.stderr)
            
            # If no button found, try JavaScript to find and click any play/download element
            if not audio_played:
                print("   🔄 Trying JavaScript to find and play audio...", file=sys.stderr)
                try:
                    played = await frame.evaluate("""
                        () => {
                            // PRIORITY 1: Try to find and play audio element directly FIRST
                            const audio = document.querySelector('audio');
                            if (audio) {
                                // Try to play it
                                audio.play().catch(() => {});
                                // Also trigger load
                                audio.load();
                                return { played: true, method: 'audio-element-direct' };
                            }
                            
                            // PRIORITY 2: Find download link (most reliable for reCAPTCHA)
                            const downloadLink = document.querySelector('a.rc-audiochallenge-tdownload, a[href*="audio"]');
                            if (downloadLink) {
                                // Click it multiple times to ensure it triggers
                                downloadLink.click();
                                // Also try to get the URL and trigger download
                                const href = downloadLink.getAttribute('href');
                                if (href) {
                                    // Trigger download programmatically
                                    const link = document.createElement('a');
                                    link.href = href;
                                    link.click();
                                }
                                return { played: true, method: 'download-link' };
                            }
                            
                            // PRIORITY 3: Find play button
                            const playBtn = document.querySelector('.rc-audiochallenge-play-button, button[title*="play" i], button[aria-label*="play" i]');
                            if (playBtn) {
                                playBtn.click();
                                // Also try to find audio and play it
                                const audio = playBtn.closest('.rc-audiochallenge')?.querySelector('audio');
                                if (audio) {
                                    audio.play().catch(() => {});
                                }
                                return { played: true, method: 'play-button' };
                            }
                            
                            // PRIORITY 4: Try clicking anywhere in challenge area
                            const challenge = document.querySelector('.rc-audiochallenge');
                            if (challenge) {
                                challenge.click();
                                // Also try to find and play audio
                                const audio = challenge.querySelector('audio');
                                if (audio) {
                                    audio.play().catch(() => {});
                                }
                                return { played: true, method: 'challenge-area' };
                            }
                            
                            return { played: false };
                        }
                    """)
                    if played.get("played"):
                        print(f"   ✅ Audio triggered via JavaScript: {played.get('method')}", file=sys.stderr)
                        audio_played = True
                        await asyncio.sleep(5)  # Wait longer for audio to actually start playing
                    else:
                        print("   ⚠️  Could not find play button via JavaScript", file=sys.stderr)
                except Exception as e:
                    print(f"   ⚠️  JavaScript play failed: {str(e)[:50]}", file=sys.stderr)
            
            # Final attempt: Force play audio element if it exists
            if not audio_played:
                print("   🔄 Final attempt: Trying to force play audio element...", file=sys.stderr)
                try:
                    forced = await frame.evaluate("""
                        () => {
                            const audio = document.querySelector('audio');
                            if (audio) {
                                audio.play().catch(() => {});
                                // Also try to set src and play
                                if (!audio.src) {
                                    // Try to get src from download link
                                    const link = document.querySelector('a.rc-audiochallenge-tdownload');
                                    if (link && link.href) {
                                        audio.src = link.href;
                                        audio.load();
                                        audio.play().catch(() => {});
                                    }
                                }
                                return true;
                            }
                            return false;
                        }
                    """)
                    if forced:
                        print("   ✅ Forced audio element to play!", file=sys.stderr)
                        audio_played = True
                        await asyncio.sleep(3)
                except Exception as e:
                    print(f"   ⚠️  Force play failed: {str(e)[:50]}", file=sys.stderr)
            
            # Get audio source - prioritize download links (reCAPTCHA's preferred method)
            print("   📥 Getting audio source (checking download links first)...", file=sys.stderr)
            
            # First, try to trigger audio load by interacting with the challenge
            print("   ▶️  Trying to trigger audio download/load...", file=sys.stderr)
            try:
                # Try multiple methods to trigger audio
                triggered = await frame.evaluate("""
                    () => {
                        // Method 1: Try clicking any download/play link
                        const downloadLink = document.querySelector('a.rc-audiochallenge-tdownload, a[href*="audio"], a[class*="download"]');
                        if (downloadLink) {
                            downloadLink.click();
                            return true;
                        }
                        
                        // Method 2: Try play button
                        const playBtn = document.querySelector('.rc-audiochallenge-play-button, button[title*="play"], button[aria-label*="play"]');
                        if (playBtn) {
                            playBtn.click();
                            return true;
                        }
                        
                        // Method 3: Try to trigger audio via JavaScript events
                        // Sometimes audio is loaded via JavaScript, so trigger events
                        const audioInput = document.querySelector('#audio-response, input[name="audio-response"]');
                        if (audioInput) {
                            // Focus on input to trigger audio load
                            audioInput.focus();
                            audioInput.click();
                            // Trigger input event
                            const inputEvent = new Event('input', { bubbles: true });
                            audioInput.dispatchEvent(inputEvent);
                            return true;
                        }
                        
                        // Method 4: Try clicking anywhere in the challenge area
                        const challengeArea = document.querySelector('.rc-audiochallenge, .rc-audiochallenge-response-field');
                        if (challengeArea) {
                            challengeArea.click();
                            return true;
                        }
                        
                        return false;
                    }
                """)
                if triggered:
                    print("   ✅ Triggered audio load, waiting for audio to play...", file=sys.stderr)
                    await asyncio.sleep(5)  # Wait longer for audio to load after trigger
                else:
                    print("   ⚠️  Could not trigger audio load, will try to extract URL anyway", file=sys.stderr)
            except Exception as e:
                print(f"   ⚠️  Error triggering audio: {str(e)[:50]}", file=sys.stderr)
            
            # Verify audio is actually playing
            if audio_played:
                print("   🎧 Checking if audio is playing...", file=sys.stderr)
                try:
                    is_playing = await frame.evaluate("""
                        () => {
                            const audio = document.querySelector('audio');
                            if (audio) {
                                return !audio.paused && audio.currentTime > 0;
                            }
                            // Check if download link was clicked (audio might be downloading)
                            const downloadLink = document.querySelector('a.rc-audiochallenge-tdownload');
                            if (downloadLink) {
                                return downloadLink.getAttribute('href') !== null;
                            }
                            return false;
                        }
                    """)
                    if is_playing:
                        print("   ✅ Audio is playing!", file=sys.stderr)
                    else:
                        print("   ⚠️  Audio might not be playing, but continuing...", file=sys.stderr)
                except Exception as e:
                    print(f"   ⚠️  Error checking audio playback: {str(e)[:50]}", file=sys.stderr)
            
            audio_src = None
            for attempt in range(20):  # Increased to 20 attempts with longer waits
                # Check if page is still valid before each attempt
                try:
                    await self.page.evaluate("() => document.title")
                except Exception:
                    print(f"   ❌ Page closed during audio source check (attempt {attempt + 1})", file=sys.stderr)
                    return False
                
                try:
                    # Check network requests first (most reliable)
                    if audio_urls_from_network:
                        audio_src = audio_urls_from_network[0]
                        print(f"   ✅ Got audio URL from network request!", file=sys.stderr)
                        break
                    
                    # Check download links FIRST (reCAPTCHA audio challenges use this)
                    audio_src = await frame.evaluate("""
                    () => {
                        // PRIORITY 0: Try to extract audio URL from JavaScript variables or window object
                        try {
                            // Check if audio URL is stored in window or global variables
                            if (window.audioUrl || window.audio_url || window.recaptchaAudioUrl) {
                                return window.audioUrl || window.audio_url || window.recaptchaAudioUrl;
                            }
                            // Check if there's a global audio source
                            const audioSource = window.audioSource || window.audio_source;
                            if (audioSource) return audioSource;
                            // Check for reCAPTCHA-specific variables
                            if (window.grecaptcha && window.grecaptcha.audioUrl) {
                                return window.grecaptcha.audioUrl;
                            }
                        } catch (e) {
                            // Ignore
                        }
                        
                        // PRIORITY 1: Check for reCAPTCHA audio download link (most common)
                        const downloadLink = document.querySelector('a.rc-audiochallenge-tdownload, a[class*="tdownload"], a[class*="download"]');
                        if (downloadLink) {
                            let href = downloadLink.getAttribute('href');
                            if (href && href.length > 0) {
                                // If relative URL, try to make it absolute
                                if (!href.startsWith('http')) {
                                    // Check if link has a data attribute or onclick with URL
                                    const onclick = downloadLink.getAttribute('onclick');
                                    if (onclick) {
                                        const urlMatch = onclick.match(/https?:\/\/[^\s'"]+/);
                                        if (urlMatch) href = urlMatch[0];
                                    }
                                    // Or try to get from the link's click handler
                                    try {
                                        const url = new URL(href, window.location.href);
                                        href = url.href;
                                    } catch (e) {
                                        // Keep original href if URL construction fails
                                    }
                                }
                                return href;
                            }
                            // If no href, try to get URL from data attributes
                            const dataUrl = downloadLink.getAttribute('data-url') || downloadLink.getAttribute('data-audio-url');
                            if (dataUrl) return dataUrl;
                        }
                        
                        // PRIORITY 2: Check for any link with audio/recaptcha in href
                        const allLinks = document.querySelectorAll('a[href]');
                        for (const link of allLinks) {
                            const href = link.getAttribute('href');
                            if (href && (href.includes('audio') || href.includes('recaptcha') || href.includes('tts'))) {
                                // Verify it looks like an audio URL
                                if (href.includes('mp3') || href.includes('wav') || href.includes('sound') || href.startsWith('http') || href.startsWith('/')) {
                                    // Make absolute if relative
                                    let absHref = href;
                                    if (!absHref.startsWith('http')) {
                                        try {
                                            absHref = new URL(href, window.location.href).href;
                                        } catch (e) {
                                            absHref = href;
                                        }
                                    }
                                    return absHref;
                                }
                            }
                        }
                        
                        // PRIORITY 3: Check audio elements (less common in reCAPTCHA)
                        const audioElements = document.querySelectorAll('audio, source');
                        for (const audioEl of audioElements) {
                            const src = audioEl.src || audioEl.currentSrc || audioEl.getAttribute('src');
                            if (src && src.length > 0) {
                                return src;
                            }
                        }
                        
                        // PRIORITY 4: Try specific audio source selectors
                        const selectors = [
                            '#audio-source',
                            'audio source',
                            'audio',
                            '#audio-source source',
                            'source[src*="audio"]',
                            'audio[src]'
                        ];
                        
                        for (const selector of selectors) {
                            const el = document.querySelector(selector);
                            if (el) {
                                const src = el.src || el.getAttribute('src') || el.getAttribute('href');
                                if (src && src.length > 0) {
                                    return src;
                                }
                            }
                        }
                        
                        return null;
                    }
                """)
                except Exception as e:
                    # Frame might be invalid, try to get it again
                    if "closed" in str(e).lower() or "target" in str(e).lower():
                        print(f"   ⚠️  Frame invalid during attempt {attempt + 1}, trying to recover...", file=sys.stderr)
                        # Try to get the challenge frame again
                        try:
                            challenge_frame = await self.page.query_selector('iframe[title*="challenge"], iframe[src*="bframe"]')
                            if challenge_frame:
                                frame = await challenge_frame.content_frame()
                                if not frame:
                                    print("   ❌ Could not recover frame", file=sys.stderr)
                                    return False
                        except:
                            print("   ❌ Could not recover, aborting", file=sys.stderr)
                            return False
                    continue
                
                if audio_src:
                    print(f"   ✅ Got audio source on attempt {attempt + 1}!", file=sys.stderr)
                    break
                
                # Check network requests again
                if audio_urls_from_network:
                    audio_src = audio_urls_from_network[0]
                    print(f"   ✅ Got audio URL from network on attempt {attempt + 1}!", file=sys.stderr)
                    break
                
                if attempt < 19:
                    if attempt % 3 == 0:  # Print every 3 attempts to reduce spam
                        print(f"   ⏳ Audio not ready, waiting... ({attempt + 1}/20)", file=sys.stderr)
                    await asyncio.sleep(2)  # Wait 2 seconds between attempts
                    
                    # Try clicking download link again if it exists
                    if attempt % 5 == 0 and attempt > 0:
                        try:
                            await frame.evaluate("""
                                () => {
                                    const link = document.querySelector('a.rc-audiochallenge-tdownload, a[href*="audio"]');
                                    if (link) link.click();
                                }
                            """)
                        except:
                            pass
            
            # Final attempt: wait longer and check network requests + all possible sources
            if not audio_src:
                print("   ❌ Could not get audio source URL after multiple attempts", file=sys.stderr)
                print("   ⏳ Final attempt - trying to extract from page source, JavaScript, and network...", file=sys.stderr)
                
                # Try to get the audio URL from JavaScript execution
                try:
                    js_audio_url = await frame.evaluate("""
                        () => {
                            // Try to execute any audio loading functions
                            try {
                                // Check if there are any functions that load audio
                                if (typeof loadAudio === 'function') {
                                    loadAudio();
                                }
                                if (typeof playAudio === 'function') {
                                    playAudio();
                                }
                            } catch (e) {}
                            
                            // Check all possible JavaScript variables again
                            const checks = [
                                window.audioUrl,
                                window.audio_url,
                                window.recaptchaAudioUrl,
                                window.audioSource,
                                window.audio_source,
                                window.grecaptcha?.audioUrl,
                                window.__audioUrl,
                                window._audioUrl
                            ];
                            for (const check of checks) {
                                if (check && typeof check === 'string' && check.startsWith('http')) {
                                    return check;
                                }
                            }
                            
                            // Try to find audio URL in script tags (but be careful - might be incomplete)
                            const scripts = document.querySelectorAll('script');
                            for (const script of scripts) {
                                const content = script.textContent || script.innerHTML;
                                // Look for complete audio URLs (must end with .mp3 or have proper path)
                                const urlMatch = content.match(/https?:\/\/[^"\'\\s]+(?:recaptcha|audio)[^"\'\\s]+(?:\.mp3|\.wav|audio[^"\'\\s]*)/i);
                                if (urlMatch) {
                                    const url = urlMatch[0];
                                    // Only return if it looks like a complete URL (has /audio/ or ends with .mp3/.wav)
                                    if (url.includes('/audio/') || url.endsWith('.mp3') || url.endsWith('.wav') || url.includes('audio?') || url.includes('audio&')) {
                                        return url;
                                    }
                                }
                            }
                            
                            return null;
                        }
                    """)
                    if js_audio_url:
                        # Validate that the URL is complete (not truncated)
                        if len(js_audio_url) > 50 and ('/audio/' in js_audio_url or js_audio_url.endswith('.mp3') or js_audio_url.endswith('.wav') or 'audio?' in js_audio_url):
                            audio_src = js_audio_url
                            print(f"   ✅ Found audio URL via JavaScript: {audio_src[:50]}...", file=sys.stderr)
                        else:
                            print(f"   ⚠️  Audio URL from JavaScript looks incomplete (length: {len(js_audio_url)}), ignoring...", file=sys.stderr)
                            audio_src = None
                except Exception as e:
                    print(f"   ⚠️  Could not extract from JavaScript: {str(e)[:50]}", file=sys.stderr)
                
                # Try to get the audio URL from the page HTML source
                if not audio_src:
                    try:
                        page_source = await frame.content()
                        import re
                        # Look for audio URLs in the HTML
                        audio_url_patterns = [
                            r'https?://[^"\'\\s]+audio[^"\'\\s]+\.(mp3|wav)',
                            r'https?://[^"\'\\s]+recaptcha[^"\'\\s]+audio[^"\'\\s]+',
                            r'src=["\']([^"\']*audio[^"\']*)["\']',
                            r'href=["\']([^"\']*audio[^"\']*)["\']',
                        ]
                        for pattern in audio_url_patterns:
                            matches = re.findall(pattern, page_source, re.IGNORECASE)
                            if matches:
                                audio_src = matches[0] if isinstance(matches[0], str) else matches[0][0] if matches[0] else None
                                if audio_src and not audio_src.startswith('http'):
                                    # Try to make it absolute
                                    try:
                                        from urllib.parse import urljoin
                                        frame_url = frame.url
                                        audio_src = urljoin(frame_url, audio_src)
                                    except:
                                        pass
                                if audio_src:
                                    print(f"   ✅ Found audio URL in page source: {audio_src[:50]}...", file=sys.stderr)
                                    break
                    except Exception as e:
                        print(f"   ⚠️  Could not extract from page source: {str(e)[:50]}", file=sys.stderr)
                
                # Check network requests one more time
                if not audio_src and audio_urls_from_network:
                    audio_src = audio_urls_from_network[0]
                    print(f"   ✅ Got audio URL from network in final attempt!", file=sys.stderr)
                elif not audio_src:
                    await asyncio.sleep(5)  # Wait a bit more
                    # Check network again after waiting
                    if audio_urls_from_network:
                        # Filter for actual audio URLs (not just bframe URLs)
                        valid_audio_urls = [url for url in audio_urls_from_network if ('/audio/' in url or url.endswith('.mp3') or url.endswith('.wav') or 'audio?' in url or 'audio&' in url)]
                        if valid_audio_urls:
                            audio_src = valid_audio_urls[0]
                            print(f"   ✅ Found valid audio URL from network after final wait: {audio_src[:50]}...", file=sys.stderr)
                        elif audio_urls_from_network:
                            # Use the first one anyway if no valid ones found
                            audio_src = audio_urls_from_network[0]
                            print(f"   ⚠️  Using network URL (may need validation): {audio_src[:50]}...", file=sys.stderr)
            
            # Before giving up, wait a bit more and check network requests one final time
            if not audio_src:
                print("   ⏳ Final check - waiting 5 more seconds for network requests...", file=sys.stderr)
                await asyncio.sleep(5)
                if audio_urls_from_network:
                    # Filter for actual audio URLs (not just bframe URLs)
                    valid_audio_urls = [url for url in audio_urls_from_network if ('/audio/' in url or url.endswith('.mp3') or url.endswith('.wav') or 'audio?' in url or 'audio&' in url)]
                    if valid_audio_urls:
                        audio_src = valid_audio_urls[0]
                        print(f"   ✅ Found valid audio URL from network after final wait: {audio_src[:50]}...", file=sys.stderr)
                    elif audio_urls_from_network:
                        # Use the first one anyway if no valid ones found
                        audio_src = audio_urls_from_network[0]
                        print(f"   ⚠️  Using network URL (may need validation): {audio_src[:50]}...", file=sys.stderr)
                
            if not audio_src:
                print("   ❌ Audio source still not available after all attempts", file=sys.stderr)
                print("   💡 Debugging info:", file=sys.stderr)
                try:
                    # Get debug info about what's in the frame
                    debug_info = await frame.evaluate("""
                        () => {
                            const allLinks = Array.from(document.querySelectorAll('a'));
                            const allButtons = Array.from(document.querySelectorAll('button'));
                            const allInputs = Array.from(document.querySelectorAll('input'));
                            
                            return {
                                hasAudioElements: document.querySelectorAll('audio').length > 0,
                                hasSourceElements: document.querySelectorAll('source').length > 0,
                                hasDownloadLinks: document.querySelectorAll('a[href*="audio"], a[href*="recaptcha"]').length > 0,
                                hasRecaptchaDownload: document.querySelector('a.rc-audiochallenge-tdownload') !== null,
                                allLinksCount: allLinks.length,
                                allButtonsCount: allButtons.length,
                                allInputsCount: allInputs.length,
                                allLinks: allLinks.slice(0, 10).map(a => ({
                                    href: a.getAttribute('href'),
                                    className: a.className,
                                    text: a.textContent.substring(0, 30)
                                })),
                                allButtons: allButtons.slice(0, 5).map(b => ({
                                    id: b.id,
                                    className: b.className,
                                    text: b.textContent.substring(0, 30),
                                    title: b.getAttribute('title')
                                })),
                                bodyHTML: document.body ? document.body.innerHTML.substring(0, 300) : 'no body',
                                frameURL: window.location.href
                            };
                        }
                    """)
                    print(f"   📊 Frame debug: {debug_info}", file=sys.stderr)
                    
                    # If we have network URLs, use the first one
                    if audio_urls_from_network:
                        audio_src = audio_urls_from_network[0]
                        print(f"   ✅ Using audio URL from network monitoring: {audio_src[:50]}...", file=sys.stderr)
                    else:
                        print("   💡 The audio challenge might need manual solving or the page structure has changed", file=sys.stderr)
                        print("   💡 Network monitoring found no audio URLs - audio might be loaded via JavaScript", file=sys.stderr)
                        return False
                except Exception as e:
                    print(f"   ⚠️  Error getting debug info: {str(e)[:50]}", file=sys.stderr)
                    if audio_urls_from_network:
                        audio_src = audio_urls_from_network[0]
                        print(f"   ✅ Using audio URL from network: {audio_src[:50]}...", file=sys.stderr)
                    else:
                        return False
            
            print(f"   ✅ Got audio source: {audio_src[:50]}...", file=sys.stderr)
            
            # Download and process audio
            print("   🎤 Recognizing audio...", file=sys.stderr)
            audio_text = await self._recognize_audio(audio_src)
            
            if not audio_text:
                print("   ❌ Audio recognition failed or returned empty", file=sys.stderr)
                return False
            
            print(f"   ✅ Recognized text: {audio_text}", file=sys.stderr)
            
            # Enter the text
            print("   ⌨️  Entering recognized text...", file=sys.stderr)
            input_selectors = ['#audio-response', 'input[name="audio-response"]', '#audio-response-input', 'input#audio-response']
            text_entered = False
            for selector in input_selectors:
                try:
                    input_field = await frame.query_selector(selector)
                    if input_field:
                        print(f"   ✅ Found input field: {selector}", file=sys.stderr)
                        # Try multiple methods to ensure text is entered
                        try:
                            await input_field.fill(audio_text)
                        except:
                            # Try JavaScript as fallback
                            await frame.evaluate("""
                                (selector, text) => {
                                    const field = document.querySelector(selector);
                                    if (field) {
                                        field.value = text;
                                        field.dispatchEvent(new Event('input', { bubbles: true }));
                                        field.dispatchEvent(new Event('change', { bubbles: true }));
                                    }
                                }
                            """, selector, audio_text)
                        
                        # Verify text was entered
                        await asyncio.sleep(0.5)
                        entered_value = await input_field.input_value()
                        if entered_value == audio_text or entered_value.strip().upper() == audio_text.strip().upper():
                            print(f"   ✅ Text entered successfully: '{entered_value}'", file=sys.stderr)
                            text_entered = True
                            break
                        else:
                            print(f"   ⚠️  Text mismatch - expected '{audio_text}', got '{entered_value}'", file=sys.stderr)
                            # Try again with JavaScript
                            await frame.evaluate("""
                                (selector, text) => {
                                    const field = document.querySelector(selector);
                                    if (field) {
                                        field.value = text;
                                        field.focus();
                                        field.dispatchEvent(new Event('input', { bubbles: true }));
                                        field.dispatchEvent(new Event('change', { bubbles: true }));
                                    }
                                }
                            """, selector, audio_text)
                            await asyncio.sleep(0.5)
                            entered_value = await input_field.input_value()
                            if entered_value == audio_text or entered_value.strip().upper() == audio_text.strip().upper():
                                print(f"   ✅ Text entered on retry: '{entered_value}'", file=sys.stderr)
                                text_entered = True
                                break
                except Exception as e:
                    print(f"   ⚠️  Failed to fill input {selector}: {str(e)[:50]}", file=sys.stderr)
                    continue
            
            if not text_entered:
                print("   ❌ Could not enter text", file=sys.stderr)
                return False
            
            # Click verify button - try multiple strategies
            print("   ✅ Clicking verify button...", file=sys.stderr)
            verify_selectors = [
                '#recaptcha-verify-button',
                'button[title*="Verify"]',
                'button[title*="verify"]',
                'button.rc-button-default',
                'button[type="submit"]',
                'button#recaptcha-verify-button',
                '.rc-button-default-go',
                'button.rc-button-default-go',
                'button[aria-label*="Verify"]',
                'button[aria-label*="verify"]',
                'button:has-text("Verify")',
                'button:has-text("verify")',
            ]
            
            verify_clicked = False
            for verify_selector in verify_selectors:
                try:
                    verify_button = await frame.query_selector(verify_selector)
                    if verify_button:
                        is_visible = await verify_button.is_visible()
                        is_enabled = await verify_button.is_enabled()
                        if is_visible and is_enabled:
                            print(f"   ✅ Found verify button: {verify_selector} (visible={is_visible}, enabled={is_enabled})", file=sys.stderr)
                            # Scroll into view first
                            await verify_button.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)
                            # Try clicking multiple ways
                            try:
                                await verify_button.click()
                            except:
                                # Try JavaScript click as fallback
                                await frame.evaluate("""
                                    (selector) => {
                                        const btn = document.querySelector(selector);
                                        if (btn) btn.click();
                                    }
                                """, verify_selector)
                            print("   ✅ Verify button clicked, waiting for verification...", file=sys.stderr)
                            await asyncio.sleep(5)  # Wait longer for verification
                            verify_clicked = True
                            print("   ✅ Audio challenge solved!", file=sys.stderr)
                            break
                        else:
                            print(f"   ⚠️  Verify button found but not clickable: visible={is_visible}, enabled={is_enabled}", file=sys.stderr)
                except Exception as e:
                    print(f"   ⚠️  Failed to click verify {verify_selector}: {str(e)[:50]}", file=sys.stderr)
                    continue
            
            if not verify_clicked:
                # Last resort: try JavaScript click on any verify button
                print("   🔄 Trying JavaScript click on verify button...", file=sys.stderr)
                try:
                    clicked = await frame.evaluate("""
                        () => {
                            // Try all buttons and clickable elements
                            const allClickable = document.querySelectorAll('button, div[role="button"], span[role="button"], a');
                            for (const btn of allClickable) {
                                const text = (btn.textContent || btn.innerText || '').toLowerCase();
                                const title = (btn.getAttribute('title') || '').toLowerCase();
                                const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                                const id = (btn.id || '').toLowerCase();
                                const className = (btn.className || '').toLowerCase();
                                
                                // Check if it's a verify button
                                if (text.includes('verify') || title.includes('verify') || 
                                    ariaLabel.includes('verify') || id.includes('verify') ||
                                    className.includes('verify') || id === 'recaptcha-verify-button') {
                                    // Try multiple click methods
                                    try {
                                        btn.click();
                                    } catch (e) {
                                        // Try dispatchEvent
                                        const clickEvent = new MouseEvent('click', { bubbles: true, cancelable: true });
                                        btn.dispatchEvent(clickEvent);
                                    }
                                    return true;
                                }
                            }
                            return false;
                        }
                    """)
                    if clicked:
                        print("   ✅ Verify button clicked via JavaScript!", file=sys.stderr)
                        await asyncio.sleep(5)
                        verify_clicked = True
                    else:
                        # Try clicking the default button (sometimes it's the verify button)
                        print("   🔄 Trying to click default button as verify...", file=sys.stderr)
                        try:
                            default_clicked = await frame.evaluate("""
                                () => {
                                    const defaultBtn = document.querySelector('.rc-button-default, .rc-button-default-go, button.rc-button-default');
                                    if (defaultBtn) {
                                        defaultBtn.click();
                                        return true;
                                    }
                                    return false;
                                }
                            """)
                            if default_clicked:
                                print("   ✅ Default button clicked!", file=sys.stderr)
                                await asyncio.sleep(5)
                                verify_clicked = True
                        except:
                            pass
                except Exception as e:
                    print(f"   ⚠️  JavaScript click failed: {str(e)[:50]}", file=sys.stderr)
            
            if not verify_clicked:
                print("   ⚠️  Could not click verify button, but continuing - token might still appear", file=sys.stderr)
                # Don't return False immediately - sometimes token appears even without clicking verify
                # Wait a bit and check for token
                await asyncio.sleep(3)
                token = await self._get_recaptcha_token()
                if token:
                    print("   ✅ Token found even without verify click!", file=sys.stderr)
                    return True
            
            # Wait a bit after verify click to ensure token is generated
            await asyncio.sleep(2)
            return True
            
        except Exception as e:
            print(f"   ❌ Audio challenge solving failed: {e}", file=sys.stderr)
            import traceback
            print(f"   Traceback: {traceback.format_exc()[:200]}", file=sys.stderr)
            return False
    
    async def _recognize_audio(self, audio_url: str) -> Optional[str]:
        """Recognize audio CAPTCHA using speech recognition."""
        try:
            import urllib.request
            import tempfile
            import os
            
            print(f"   📥 Downloading audio from: {audio_url[:50]}...", file=sys.stderr)
            # Download audio file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                urllib.request.urlretrieve(audio_url, tmp_file.name)
                audio_path = tmp_file.name
            
            print(f"   ✅ Audio downloaded to: {audio_path}", file=sys.stderr)
            
            try:
                # Try using speech_recognition library (free, uses Google's API)
                try:
                    import speech_recognition as sr
                    from pydub import AudioSegment
                    
                    print("   🔄 Converting audio to WAV format...", file=sys.stderr)
                    # Convert to WAV if needed
                    audio = AudioSegment.from_mp3(audio_path)
                    wav_path = audio_path.replace('.mp3', '.wav')
                    audio.export(wav_path, format="wav")
                    print("   ✅ Audio converted to WAV", file=sys.stderr)
                    
                    # Recognize speech using Google's free API
                    print("   🎤 Recognizing speech using Google API...", file=sys.stderr)
                    r = sr.Recognizer()
                    with sr.AudioFile(wav_path) as source:
                        # Adjust for ambient noise
                        r.adjust_for_ambient_noise(source, duration=0.5)
                        audio_data = r.record(source)
                        text = r.recognize_google(audio_data, language='en-US')
                        recognized = text.strip().upper()  # CAPTCHA audio is usually uppercase
                        print(f"   ✅ Recognized text: {recognized}", file=sys.stderr)
                        return recognized
                        
                except ImportError:
                    print("   ⚠️  speech_recognition or pydub not installed. Install with: pip install SpeechRecognition pydub", file=sys.stderr)
                    return None
                except sr.UnknownValueError:
                    print("   ⚠️  Google Speech Recognition could not understand the audio", file=sys.stderr)
                    return None
                except sr.RequestError as e:
                    print(f"   ⚠️  Could not request results from Google Speech Recognition service: {e}", file=sys.stderr)
                    return None
                except Exception as e:
                    print(f"   ⚠️  Speech recognition error: {e}", file=sys.stderr)
                    return None
                
            finally:
                # Clean up
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                wav_path = audio_path.replace('.mp3', '.wav')
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
            
        except Exception as e:
            print(f"   ❌ Audio recognition failed: {e}", file=sys.stderr)
            import traceback
            print(f"   Traceback: {traceback.format_exc()[:300]}", file=sys.stderr)
            return None
    
    async def _solve_challenge(self) -> bool:
        """Attempt to solve image challenge - always try to switch to audio first."""
        try:
            print("   🖼️  Image challenge detected, attempting to solve...", file=sys.stderr)
            challenge_frame = await self.page.query_selector('iframe[title*="challenge"], iframe[src*="bframe"]')
            if not challenge_frame:
                print("   ⚠️  Challenge iframe not found", file=sys.stderr)
                return False
            
            frame = await challenge_frame.content_frame()
            if not frame:
                print("   ⚠️  Could not access challenge iframe", file=sys.stderr)
                return False
            
            # Wait for challenge to load
            await asyncio.sleep(2)
            
            # Strategy 1: ALWAYS try to switch to audio challenge first (more reliable)
            print("   🎧 Attempting to switch to audio challenge...", file=sys.stderr)
            audio_selectors = [
                '#recaptcha-audio-button',
                'button[title*="audio"]',
                'button[title*="Audio"]',
                '.rc-button-audio',
                'button.rc-button-audio',
                'button[aria-label*="audio"]',
                'button[id*="audio"]',
                'div[role="button"][aria-label*="audio"]',
                'div[role="button"][aria-label*="Audio"]'
            ]
            
            for selector in audio_selectors:
                try:
                    audio_btn = await frame.query_selector(selector)
                    if audio_btn:
                        # Check if button is visible
                        is_visible = await audio_btn.is_visible()
                        if is_visible:
                            print(f"   ✅ Found audio button: {selector}", file=sys.stderr)
                            await audio_btn.click()
                            print("   ✅ Audio button clicked, switching to audio challenge...", file=sys.stderr)
                            await asyncio.sleep(3)  # Wait for audio challenge to load
                            # Now try to solve audio
                            return await self._solve_audio_challenge()
                except Exception as e:
                    print(f"   ⚠️  Failed to click audio button {selector}: {str(e)[:50]}", file=sys.stderr)
                    continue
            
            print("   ⚠️  Could not find audio button, trying image challenge strategies...", file=sys.stderr)
            
            # Strategy 2: For image challenges, try to get the prompt and images
            # Extract challenge prompt/question
            prompt = await frame.evaluate("""
                () => {
                    // Try to find the challenge prompt/question
                    const promptEl = document.querySelector('.rc-imageselect-desc-text, .rc-imageselect-desc-no-canonical, .rc-imageselect-desc');
                    return promptEl ? promptEl.textContent.trim() : null;
                }
            """)
            
            if prompt:
                print(f"   📝 Challenge prompt: {prompt}", file=sys.stderr)
            
            # Check if it's an image grid challenge
            image_grid = await frame.evaluate("""
                () => {
                    // Check for image grid
                    const grid = document.querySelector('.rc-imageselect-grid, .rc-imageselect-tile');
                    return grid !== null;
                }
            """)
            
            if image_grid:
                print("   🖼️  Image grid detected", file=sys.stderr)
                
                # Get the challenge prompt
                prompt = await frame.evaluate("""
                    () => {
                        const promptEl = document.querySelector('.rc-imageselect-desc-text, .rc-imageselect-desc-no-canonical, .rc-imageselect-desc');
                        return promptEl ? promptEl.textContent.trim() : null;
                    }
                """)
                
                if prompt:
                    print(f"   📝 Challenge: {prompt}", file=sys.stderr)
                
                # Try to solve image challenge (basic implementation)
                # For full automation, this would need ML model
                try:
                    # Try to import image challenge solver
                    try:
                        from automation.image_challenge_solver import solve_image_challenge
                        solved = await solve_image_challenge(frame, self.page)
                        if solved:
                            print("   ✅ Image challenge solved!", file=sys.stderr)
                            return True
                    except ImportError:
                        pass
                except Exception as e:
                    print(f"   ⚠️  Image challenge solver error: {str(e)[:50]}", file=sys.stderr)
                
                # Image challenges cannot be solved automatically without ML models
                print("   ❌ Image challenge cannot be solved automatically", file=sys.stderr)
                print("   💡 Options:", file=sys.stderr)
                print("      1. Set HEADLESS=false to solve manually", file=sys.stderr)
                print("      2. Use external CAPTCHA solving service (2captcha, etc.)", file=sys.stderr)
                print("      3. Implement ML-based image recognition", file=sys.stderr)
                return False
            
            # Strategy 3: Try clicking verify button (sometimes works if challenge is easy)
            verify_selectors = [
                '#recaptcha-verify-button',
                'button[title*="Verify"]',
                'button.rc-button-default',
                'button[type="submit"]',
                '.rc-button-default',
                'button#recaptcha-verify-button'
            ]
            
            for selector in verify_selectors:
                try:
                    verify_btn = await frame.query_selector(selector)
                    if verify_btn and await verify_btn.is_visible():
                        print(f"   ✅ Found verify button: {selector}", file=sys.stderr)
                        await verify_btn.click()
                        print("   ✅ Verify button clicked, waiting...", file=sys.stderr)
                        await asyncio.sleep(3)  # Reduced from 5 to 3 seconds
                        # Check if token appeared
                        token = await self._get_recaptcha_token()
                        if token:
                            print("   ✅ Token found after verify click!", file=sys.stderr)
                            return True
                except Exception as e:
                    print(f"   ⚠️  Failed to click verify {selector}: {str(e)[:50]}", file=sys.stderr)
                    continue
            
            # Strategy 4: Try clicking "Skip" or "Next" buttons
            skip_selectors = [
                'button[title*="Skip"]',
                'button[title*="Next"]',
                'button[aria-label*="Skip"]',
                '.rc-button-default'
            ]
            
            for selector in skip_selectors:
                try:
                    button = await frame.query_selector(selector)
                    if button and await button.is_visible():
                        print(f"   ✅ Found skip/next button: {selector}", file=sys.stderr)
                        await button.click()
                        await asyncio.sleep(3)
                        # Check if challenge completed
                        token = await self._get_recaptcha_token()
                        if token:
                            return True
                except:
                    continue
            
            print("   ⚠️  Image challenge solving failed - no valid strategy worked", file=sys.stderr)
            return False
            
        except Exception as e:
            print(f"   ❌ Challenge solving error: {e}", file=sys.stderr)
            import traceback
            print(f"   Traceback: {traceback.format_exc()[:200]}", file=sys.stderr)
            return False
    
    async def _get_recaptcha_token(self) -> Optional[str]:
        """Get the solved reCAPTCHA token using multiple strategies."""
        try:
            # Strategy 1: Get token from the response field
            token = await self.page.evaluate("""
                () => {
                    const responseField = document.querySelector('textarea[name="g-recaptcha-response"]');
                    if (responseField && responseField.value && responseField.value.length > 0) {
                        return responseField.value;
                    }
                    return null;
                }
            """)
            
            if token and len(token) > 0:
                return token
            
            # Strategy 2: Try to get token from grecaptcha callback
            token = await self.page.evaluate("""
                () => {
                    // Try to get token from grecaptcha if available
                    if (window.grecaptcha && window.grecaptcha.getResponse) {
                        try {
                            // Find all widgets
                            const widgets = document.querySelectorAll('[data-sitekey]');
                            for (let widget of widgets) {
                                const widgetId = widget.getAttribute('data-widget-id');
                                if (widgetId) {
                                    const response = window.grecaptcha.getResponse(widgetId);
                                    if (response && response.length > 0) {
                                        return response;
                                    }
                                }
                            }
                            // Try without widget ID
                            const response = window.grecaptcha.getResponse();
                            if (response && response.length > 0) {
                                return response;
                            }
                        } catch (e) {
                            // Ignore errors
                        }
                    }
                    return null;
                }
            """)
            
            if token and len(token) > 0:
                return token
            
            # Strategy 3: Check if checkbox is checked and trigger callback
            token = await self.page.evaluate("""
                () => {
                    // Check if checkbox is checked
                    const iframe = document.querySelector('iframe[src*="recaptcha"][src*="anchor"]');
                    if (iframe) {
                        // Try to trigger callback manually
                        if (window.grecaptcha && window.grecaptcha.execute) {
                            try {
                                const widgets = document.querySelectorAll('[data-sitekey]');
                                for (let widget of widgets) {
                                    const widgetId = widget.getAttribute('data-widget-id');
                                    if (widgetId) {
                                        window.grecaptcha.execute(widgetId);
                                    }
                                }
                            } catch (e) {
                                // Ignore
                            }
                        }
                    }
                    return null;
                }
            """)
            
            # Wait a bit for callback to execute
            await asyncio.sleep(1)
            
            # Strategy 4: Check response field again (might have been updated)
            token = await self.page.evaluate("""
                () => {
                    const responseField = document.querySelector('textarea[name="g-recaptcha-response"]');
                    if (responseField && responseField.value && responseField.value.length > 0) {
                        return responseField.value;
                    }
                    // Also check grecaptcha again
                    if (window.grecaptcha && window.grecaptcha.getResponse) {
                        try {
                            const response = window.grecaptcha.getResponse();
                            if (response && response.length > 0) {
                                return response;
                            }
                        } catch (e) {
                            // Ignore
                        }
                    }
                    return null;
                }
            """)
            
            return token if token and len(token) > 0 else None
            
        except Exception as e:
            print(f"⚠️  Error getting token: {e}", file=sys.stderr)
            return None
    
    async def _click_hcaptcha_checkbox(self) -> bool:
        """Click the hCaptcha checkbox to trigger challenge."""
        try:
            print("🖱️ Looking for hCaptcha checkbox...", file=sys.stderr)
            
            # Wait for hCaptcha to load
            await asyncio.sleep(2)
            
            # Find hCaptcha iframe
            hcaptcha_iframe = await self.page.query_selector('iframe[src*="hcaptcha.com"]')
            if not hcaptcha_iframe:
                print("   ⚠️  hCaptcha iframe not found", file=sys.stderr)
                return False
            
            frame = await hcaptcha_iframe.content_frame()
            if not frame:
                print("   ⚠️  Could not access hCaptcha iframe", file=sys.stderr)
                return False
            
            # Wait for checkbox to appear
            await asyncio.sleep(1)
            
            # Find and click the checkbox
            checkbox_selectors = [
                '#checkbox',
                '.checkbox',
                'div[role="checkbox"]',
                'div.checkbox',
                '[id*="checkbox"]'
            ]
            
            for selector in checkbox_selectors:
                try:
                    checkbox = await frame.query_selector(selector)
                    if checkbox:
                        is_visible = await checkbox.is_visible()
                        if is_visible:
                            print(f"   ✅ Found hCaptcha checkbox: {selector}", file=sys.stderr)
                            await checkbox.click()
                            print("   ✅ hCaptcha checkbox clicked!", file=sys.stderr)
                            await asyncio.sleep(2)  # Wait for challenge to appear
                            return True
                except Exception as e:
                    continue
            
            # Try JavaScript click as fallback
            clicked = await frame.evaluate("""
                () => {
                    const checkbox = document.querySelector('#checkbox, .checkbox, div[role="checkbox"]');
                    if (checkbox) {
                        checkbox.click();
                        return true;
                    }
                    return false;
                }
            """)
            
            if clicked:
                print("   ✅ hCaptcha checkbox clicked via JavaScript!", file=sys.stderr)
                await asyncio.sleep(2)
                return True
            
            print("   ⚠️  Could not find or click hCaptcha checkbox", file=sys.stderr)
            return False
            
        except Exception as e:
            print(f"   ❌ Error clicking hCaptcha checkbox: {e}", file=sys.stderr)
            return False
    
    async def _get_hcaptcha_token(self) -> Optional[str]:
        """Get the solved hCaptcha token."""
        try:
            # Strategy 1: Get token from the response field
            token = await self.page.evaluate("""
                () => {
                    const responseField = document.querySelector('textarea[name="h-captcha-response"]');
                    if (responseField && responseField.value && responseField.value.length > 0) {
                        return responseField.value;
                    }
                    return null;
                }
            """)
            
            if token and len(token) > 0:
                return token
            
            # Strategy 2: Try to get token from hcaptcha callback
            token = await self.page.evaluate("""
                () => {
                    // Try to get token from hcaptcha if available
                    if (window.hcaptcha && window.hcaptcha.getResponse) {
                        try {
                            // Find all widgets
                            const widgets = document.querySelectorAll('[data-sitekey]');
                            for (let widget of widgets) {
                                const widgetId = widget.getAttribute('data-hcaptcha-widget-id') || 
                                                widget.getAttribute('id');
                                if (widgetId) {
                                    const response = window.hcaptcha.getResponse(widgetId);
                                    if (response && response.length > 0) {
                                        return response;
                                    }
                                }
                            }
                            // Try without widget ID
                            const response = window.hcaptcha.getResponse();
                            if (response && response.length > 0) {
                                return response;
                            }
                        } catch (e) {
                            // Ignore errors
                        }
                    }
                    return null;
                }
            """)
            
            if token and len(token) > 0:
                return token
            
            return None
            
        except Exception as e:
            print(f"⚠️  Error getting hCaptcha token: {e}", file=sys.stderr)
            return None
    
    async def _solve_hcaptcha_challenge(self) -> bool:
        """Attempt to solve hCaptcha challenge (image or audio)."""
        try:
            print("   🖼️  hCaptcha challenge detected, attempting to solve...", file=sys.stderr)
            
            # Find challenge iframe
            challenge_iframe = await self.page.query_selector('iframe[src*="hcaptcha.com"][src*="challenge"]')
            if not challenge_iframe:
                print("   ⚠️  Challenge iframe not found", file=sys.stderr)
                return False
            
            frame = await challenge_iframe.content_frame()
            if not frame:
                print("   ⚠️  Could not access challenge iframe", file=sys.stderr)
                return False
            
            await asyncio.sleep(2)
            
            # Try to find and click audio button (similar to reCAPTCHA)
            audio_selectors = [
                'button[aria-label*="audio"]',
                'button[aria-label*="Audio"]',
                'button[title*="audio"]',
                'button[title*="Audio"]',
                '.audio-button',
                'button.audio-button'
            ]
            
            for selector in audio_selectors:
                try:
                    audio_btn = await frame.query_selector(selector)
                    if audio_btn:
                        is_visible = await audio_btn.is_visible()
                        if is_visible:
                            print(f"   ✅ Found audio button: {selector}", file=sys.stderr)
                            await audio_btn.click()
                            print("   ✅ Audio button clicked!", file=sys.stderr)
                            await asyncio.sleep(3)
                            # Try to solve audio challenge (similar to reCAPTCHA)
                            return await self._solve_audio_challenge()
                except:
                    continue
            
            # For image challenges, we would need image recognition
            # For now, return False and let the user know
            print("   ⚠️  Image challenge detected - image solving not yet implemented", file=sys.stderr)
            print("   💡 Tip: Try refreshing to get an audio challenge", file=sys.stderr)
            return False
            
        except Exception as e:
            print(f"   ❌ Error solving hCaptcha challenge: {e}", file=sys.stderr)
            return False
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCaptcha using local methods."""
        if not self.page:
            raise RuntimeError("LocalCaptchaSolver requires a Playwright page object")
        
        try:
            print(f"🎯 Solving hCaptcha...", file=sys.stderr)
            print(f"   Site Key: {site_key[:30]}..." if site_key else "   (No site key found)", file=sys.stderr)
            
            # Step 1: Click the checkbox
            print("\n🖱️  Clicking hCaptcha checkbox...", file=sys.stderr)
            clicked = await self._click_hcaptcha_checkbox()
            
            if not clicked:
                print("   ⚠️  Could not click checkbox, trying alternative method...", file=sys.stderr)
                # Try clicking the iframe directly
                hcaptcha_iframe = await self.page.query_selector('iframe[src*="hcaptcha.com"]')
                if hcaptcha_iframe:
                    await hcaptcha_iframe.click()
                    await asyncio.sleep(2)
            
            # Step 2: Check if challenge appeared
            await asyncio.sleep(2)
            challenge_present = await self.page.evaluate("""
                () => {
                    const challengeFrame = document.querySelector('iframe[src*="hcaptcha.com"][src*="challenge"]');
                    return challengeFrame !== null;
                }
            """)
            
            if challenge_present:
                print("   ✅ Challenge appeared!", file=sys.stderr)
                # Try to solve the challenge
                solved = await self._solve_hcaptcha_challenge()
                if not solved:
                    print("   ⚠️  Challenge solving failed, but checking for token...", file=sys.stderr)
            else:
                print("   ℹ️  No challenge appeared (might be solved automatically)", file=sys.stderr)
            
            # Step 3: Wait and check for token
            await asyncio.sleep(3)
            token = await self._get_hcaptcha_token()
            
            if token:
                print(f"\n✅ hCaptcha solved successfully!", file=sys.stderr)
                print(f"   Token length: {len(token)}", file=sys.stderr)
                return token
            else:
                print("\n⚠️  hCaptcha token not found yet", file=sys.stderr)
                # Wait a bit more and try again
                await asyncio.sleep(3)
                token = await self._get_hcaptcha_token()
                if token:
                    print(f"   ✅ Got token on retry! Token length: {len(token)}", file=sys.stderr)
                    return token
                
                print("   ❌ Could not get hCaptcha token", file=sys.stderr)
                return None
                
        except Exception as e:
            print(f"❌ Error solving hCaptcha: {e}", file=sys.stderr)
            import traceback
            print(f"Traceback: {traceback.format_exc()[:300]}", file=sys.stderr)
            return None


def get_captcha_solver(service: str = "auto") -> Optional[CaptchaSolver]:
    """
    Get a CAPTCHA solver instance based on configuration.
    
    Args:
        service: Service name ("2captcha", "anticaptcha", "capsolver", "local", or "auto")
    
    Returns:
        CaptchaSolver instance or None
    """
    if service == "auto":
        # Always default to local solver unless explicitly disabled
        use_local = os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "true").lower() not in ("false", "0", "no")
        if use_local:
            return LocalCaptchaSolver()
        
        # Only check external services if local solver is explicitly disabled
        # Check for AI4CAP first (keys start with "sk_")
        ai4cap_key = os.getenv("CAPTCHA_AI4CAP_API_KEY") or os.getenv("CAPTCHA_2CAPTCHA_API_KEY") or os.getenv("TEQ_CAPTCHA_API_KEY")
        if ai4cap_key and ai4cap_key.startswith("sk_"):
            service = "ai4cap"
        elif os.getenv("CAPTCHA_2CAPTCHA_API_KEY") or os.getenv("TEQ_CAPTCHA_API_KEY"):
            service = "2captcha"
        elif os.getenv("CAPTCHA_ANTICAPTCHA_API_KEY"):
            service = "anticaptcha"
        elif os.getenv("CAPTCHA_CAPSOLVER_API_KEY"):
            service = "capsolver"
        else:
            # Fallback to local solver if no external service available
            return LocalCaptchaSolver()
    
    if service == "ai4cap":
        api_key = os.getenv("CAPTCHA_AI4CAP_API_KEY") or os.getenv("CAPTCHA_2CAPTCHA_API_KEY") or os.getenv("TEQ_CAPTCHA_API_KEY")
        # Only use if it's an AI4CAP key (starts with "sk_")
        if api_key and api_key.startswith("sk_"):
            return AI4CAPSolver(api_key)
        # If not AI4CAP key, fall through to 2captcha
    
    if service == "2captcha":
        api_key = os.getenv("CAPTCHA_2CAPTCHA_API_KEY") or os.getenv("TEQ_CAPTCHA_API_KEY")
        # Skip if it's an AI4CAP key
        if api_key and not api_key.startswith("sk_"):
            return TwoCaptchaSolver(api_key)
    
    elif service == "anticaptcha":
        api_key = os.getenv("CAPTCHA_ANTICAPTCHA_API_KEY")
        if api_key:
            return AntiCaptchaSolver(api_key)
    
    elif service == "capsolver":
        api_key = os.getenv("CAPTCHA_CAPSOLVER_API_KEY")
        if api_key:
            return CapSolverSolver(api_key)
    
    elif service == "local":
        # Local solver - will be initialized with page object by caller
        return LocalCaptchaSolver()
    
    return None

