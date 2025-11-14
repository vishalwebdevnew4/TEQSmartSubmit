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
            
            # Step 2: Wait a bit and check if token is already available (no challenge)
            await asyncio.sleep(3)
            token = await self._get_recaptcha_token()
            if token:
                print("✅ CAPTCHA solved without challenge!", file=sys.stderr)
                return token
            
            # Step 3: Check if challenge appeared
            print("🔍 Checking for challenge...", file=sys.stderr)
            challenge_present = await self._check_challenge_present()
            
            if challenge_present:
                print("🎯 Challenge detected, attempting to solve...", file=sys.stderr)
            
            # First, check if it's already an image challenge - if so, try to switch to audio immediately
            challenge_frame = await self.page.query_selector('iframe[title*="challenge"], iframe[src*="bframe"]')
            if challenge_frame:
                frame = await challenge_frame.content_frame()
                if frame:
                    # Check if it's an image challenge
                    is_image_challenge = await frame.evaluate("""
                        () => {
                            const grid = document.querySelector('.rc-imageselect-grid, .rc-imageselect-tile');
                            return grid !== null;
                        }
                    """)
                    
                    if is_image_challenge:
                        print("🖼️  Image challenge detected, switching to audio...", file=sys.stderr)
                        # Try to switch to audio immediately
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
                                if audio_btn and await audio_btn.is_visible():
                                    print(f"   ✅ Found audio button: {selector}, clicking...", file=sys.stderr)
                                    await audio_btn.click()
                                    await asyncio.sleep(3)  # Wait for audio challenge to load
                                    break
                            except:
                                continue
            
            # Try audio challenge first (more reliable)
            print("🎧 Trying audio challenge...", file=sys.stderr)
            solved = await self._solve_audio_challenge()
            
            if not solved:
                # If audio failed, try image challenge (but this will likely fail without ML)
                print("🖼️  Audio failed or not available, checking image challenge...", file=sys.stderr)
                solved = await self._solve_challenge()
                
                # Wait for token after solving challenge (or even if solving reported failure)
                # Sometimes the challenge is solved but the flag isn't set correctly
                print("⏳ Waiting for token after challenge attempt...", file=sys.stderr)
                for i in range(20):  # Wait up to 40 seconds
                    await asyncio.sleep(2)
                    token = await self._get_recaptcha_token()
                    if token:
                        print(f"✅ Token retrieved on attempt {i+1}!", file=sys.stderr)
                        return token
                    if i < 19:  # Don't print on last attempt
                        if i % 3 == 0:  # Print every 3rd attempt to reduce spam
                            print(f"   Still waiting... ({i+1}/20)", file=sys.stderr)
                
                # Final check - sometimes reCAPTCHA auto-verifies after a delay
                print("   ⏳ Final check for token...", file=sys.stderr)
                await asyncio.sleep(5)
                token = await self._get_recaptcha_token()
                if token:
                    print("✅ Token found on final check!", file=sys.stderr)
                    return token
            else:
                # No challenge, but token might take longer to appear
                print("⏳ No challenge detected, waiting for token...", file=sys.stderr)
                for i in range(5):  # Wait up to 10 seconds
                    await asyncio.sleep(2)
                    token = await self._get_recaptcha_token()
                    if token:
                        print("✅ Token received!", file=sys.stderr)
                        return token
            
            # Final attempt to get token - try multiple times with longer waits
            print("🔍 Attempting to retrieve token...", file=sys.stderr)
            for attempt in range(10):
                token = await self._get_recaptcha_token()
                if token:
                    print(f"✅ Token retrieved on attempt {attempt + 1}", file=sys.stderr)
                    return token
                await asyncio.sleep(2)
                if attempt < 9:
                    print(f"   Retrying token retrieval... ({attempt + 1}/10)", file=sys.stderr)
            
            print("⚠️  Warning: Could not retrieve CAPTCHA token after multiple attempts", file=sys.stderr)
            # Try one more time with a longer wait
            await asyncio.sleep(5)
            token = await self._get_recaptcha_token()
            return token
            
        except Exception as e:
            print(f"❌ Local CAPTCHA solving error: {e}", file=sys.stderr)
            raise RuntimeError(f"Local CAPTCHA solving failed: {str(e)}")
    
    async def _click_recaptcha_checkbox(self):
        """Click the reCAPTCHA checkbox using multiple strategies."""
        try:
            # Strategy 1: Find and click the checkbox in the iframe
            iframe = await self.page.query_selector('iframe[src*="recaptcha"][src*="anchor"]')
            if iframe:
                try:
                    frame = await iframe.content_frame()
                    if frame:
                        # Wait for checkbox to be ready
                        await frame.wait_for_selector('#recaptcha-anchor', timeout=5000)
                        checkbox = await frame.query_selector('#recaptcha-anchor')
                        if checkbox:
                            # Scroll into view and click
                            await checkbox.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)
                            await checkbox.click()
                            await asyncio.sleep(2)
                            return
                except:
                    pass
            
            # Strategy 2: Click via JavaScript in the iframe
            iframe = await self.page.query_selector('iframe[src*="recaptcha"]')
            if iframe:
                try:
                    frame = await iframe.content_frame()
                    if frame:
                        await frame.evaluate("""
                            () => {
                                const checkbox = document.querySelector('#recaptcha-anchor');
                                if (checkbox) {
                                    checkbox.click();
                                }
                            }
                        """)
                        await asyncio.sleep(2)
                        return
                except:
                    pass
            
            # Strategy 3: Click the iframe container
            await self.page.evaluate("""
                () => {
                    const iframe = document.querySelector('iframe[src*="recaptcha"]');
                    if (iframe) {
                        const rect = iframe.getBoundingClientRect();
                        const x = rect.left + rect.width / 2;
                        const y = rect.top + rect.height / 2;
                        const clickEvent = new MouseEvent('click', {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: x,
                            clientY: y
                        });
                        iframe.dispatchEvent(clickEvent);
                    }
                }
            """)
            await asyncio.sleep(2)
            
        except Exception as e:
            raise RuntimeError(f"Failed to click reCAPTCHA checkbox: {str(e)}")
    
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
    
    async def _solve_audio_challenge(self) -> bool:
        """Solve audio CAPTCHA challenge using speech recognition."""
        try:
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
            
            # Click audio button
            print("   🔘 Looking for audio button...", file=sys.stderr)
            audio_button_selectors = [
                '#recaptcha-audio-button',
                'button[title*="audio"]',
                'button[title*="Audio"]',
                '.rc-button-audio',
                'button.rc-button-audio',
                'button[id*="audio"]'
            ]
            
            audio_clicked = False
            for selector in audio_button_selectors:
                try:
                    audio_button = await frame.query_selector(selector)
                    if audio_button:
                        print(f"   ✅ Found audio button: {selector}", file=sys.stderr)
                        await audio_button.click()
                        print("   ✅ Audio button clicked, waiting for audio to load...", file=sys.stderr)
                        await asyncio.sleep(5)  # Wait longer for audio to load
                        audio_clicked = True
                        break
                except Exception as e:
                    print(f"   ⚠️  Failed to click audio button {selector}: {str(e)[:50]}", file=sys.stderr)
                    continue
            
            if not audio_clicked:
                print("   ❌ Could not click audio button", file=sys.stderr)
                return False
            
            # Get audio source - try multiple methods with longer waits
            print("   📥 Getting audio source...", file=sys.stderr)
            
            # Wait for audio to load (can take a few seconds)
            audio_src = None
            for attempt in range(10):
                audio_src = await frame.evaluate("""
                    () => {
                        // Try multiple selectors for audio source
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
                        
                        // Also check all audio elements
                        const audioElements = document.querySelectorAll('audio, source');
                        for (const audioEl of audioElements) {
                            const src = audioEl.src || audioEl.getAttribute('src') || audioEl.getAttribute('href');
                            if (src && src.length > 0 && (src.includes('audio') || src.includes('mp3') || src.includes('wav'))) {
                                return src;
                            }
                        }
                        
                        return null;
                    }
                """)
                
                if audio_src:
                    print(f"   ✅ Got audio source on attempt {attempt + 1}", file=sys.stderr)
                    break
                
                if attempt < 9:
                    print(f"   ⏳ Audio not ready, waiting... ({attempt + 1}/10)", file=sys.stderr)
                    await asyncio.sleep(2)
            
            if not audio_src:
                print("   ❌ Could not get audio source URL after multiple attempts", file=sys.stderr)
                # Try one more time with a longer wait
                print("   ⏳ Final attempt - waiting 5 more seconds...", file=sys.stderr)
                await asyncio.sleep(5)
                audio_src = await frame.evaluate("""
                    () => {
                        const audio = document.querySelector('audio');
                        if (audio) {
                            return audio.src || audio.currentSrc || audio.getAttribute('src');
                        }
                        const source = document.querySelector('source');
                        if (source) {
                            return source.src || source.getAttribute('src');
                        }
                        return null;
                    }
                """)
                
                if not audio_src:
                    print("   ❌ Audio source still not available", file=sys.stderr)
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
                        await input_field.fill(audio_text)
                        await asyncio.sleep(1)
                        text_entered = True
                        break
                except Exception as e:
                    print(f"   ⚠️  Failed to fill input {selector}: {str(e)[:50]}", file=sys.stderr)
                    continue
            
            if not text_entered:
                print("   ❌ Could not enter text", file=sys.stderr)
                return False
            
            # Click verify button
            print("   ✅ Clicking verify button...", file=sys.stderr)
            verify_selectors = [
                '#recaptcha-verify-button',
                'button[title*="Verify"]',
                'button.rc-button-default',
                'button[type="submit"]',
                'button#recaptcha-verify-button'
            ]
            
            for verify_selector in verify_selectors:
                try:
                    verify_button = await frame.query_selector(verify_selector)
                    if verify_button:
                        print(f"   ✅ Found verify button: {verify_selector}", file=sys.stderr)
                        await verify_button.click()
                        print("   ✅ Verify button clicked, waiting for verification...", file=sys.stderr)
                        await asyncio.sleep(5)  # Wait longer for verification
                        print("   ✅ Audio challenge solved!", file=sys.stderr)
                        return True
                except Exception as e:
                    print(f"   ⚠️  Failed to click verify {verify_selector}: {str(e)[:50]}", file=sys.stderr)
                    continue
            
            print("   ❌ Could not click verify button", file=sys.stderr)
            return False
            
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
                        await asyncio.sleep(5)
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
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCaptcha using local methods."""
        if not self.page:
            raise RuntimeError("LocalCaptchaSolver requires a Playwright page object")
        
        # Similar implementation to reCAPTCHA but for hCaptcha
        # This is a placeholder - hCaptcha solving would need similar logic
        raise NotImplementedError("hCaptcha local solving not yet fully implemented")


def get_captcha_solver(service: str = "auto") -> Optional[CaptchaSolver]:
    """
    Get a CAPTCHA solver instance based on configuration.
    
    Args:
        service: Service name ("2captcha", "anticaptcha", "capsolver", "local", or "auto")
    
    Returns:
        CaptchaSolver instance or None
    """
    if service == "auto":
        # Try to detect which service to use based on available API keys
        if os.getenv("CAPTCHA_2CAPTCHA_API_KEY") or os.getenv("TEQ_CAPTCHA_API_KEY"):
            service = "2captcha"
        elif os.getenv("CAPTCHA_ANTICAPTCHA_API_KEY"):
            service = "anticaptcha"
        elif os.getenv("CAPTCHA_CAPSOLVER_API_KEY"):
            service = "capsolver"
        else:
            return None
    
    if service == "2captcha":
        api_key = os.getenv("CAPTCHA_2CAPTCHA_API_KEY") or os.getenv("TEQ_CAPTCHA_API_KEY")
        if api_key:
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
    
    # Auto-detect local solver if no API keys found and local is preferred
    if service == "auto":
        use_local = os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "false").lower() in ("true", "1", "yes")
        if use_local:
            return LocalCaptchaSolver()
    
    return None

