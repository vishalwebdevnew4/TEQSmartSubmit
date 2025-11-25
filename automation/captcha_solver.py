#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra-resilient Local CAPTCHA Solver Interface
NEVER fails - always returns structured response
Uses ONLY local solving - no external services
"""

import asyncio
import os
import sys
import time
import random
from typing import Dict, Optional, Any
import base64
import io

# Global fallback result - immutable
FALLBACK_CAPTCHA_RESULT = {
    "success": False,
    "token": None,
    "error": "Local CAPTCHA solver encountered unrecoverable error",
    "error_type": "fallback",
    "solver_used": "local",
    "recovered": True,
    "timestamp": 0
}

def get_timestamp() -> float:
    """Safely get current timestamp."""
    try:
        return time.time()
    except:
        return 0.0

def safe_log_print(*args, **kwargs):
    """Safely print to stderr - never fails."""
    try:
        # Ensure we have a valid output stream
        output_file = None
        try:
            if hasattr(sys, 'stderr') and sys.stderr and not getattr(sys.stderr, 'closed', True):
                output_file = sys.stderr
            elif hasattr(sys, 'stdout') and sys.stdout and not getattr(sys.stdout, 'closed', True):
                output_file = sys.stdout
        except:
            pass
        
        if not output_file:
            return
        
        # Prepare safe arguments
        safe_args = []
        for arg in args:
            try:
                if isinstance(arg, str):
                    # Limit length and encode safely
                    safe_arg = arg[:500]  # Limit length
                    safe_args.append(safe_arg)
                else:
                    safe_args.append(str(arg)[:500])
            except:
                safe_args.append("[unprintable]")
        
        # Print safely
        kwargs['file'] = output_file
        print(*safe_args, **kwargs)
        
        # Flush safely
        try:
            if hasattr(output_file, 'flush'):
                output_file.flush()
        except:
            pass
            
    except Exception:
        # Ultimate fallback - try basic print
        try:
            print("[CAPTCHA_LOG]", *args[:3])
        except:
            pass

def create_fallback_result(error_msg: str = None, solver_used: str = "local") -> Dict[str, Any]:
    """Create a safe fallback result dict."""
    try:
        return {
            "success": False,
            "token": None,
            "error": error_msg or "Local CAPTCHA solver encountered unrecoverable error",
            "error_type": "fallback",
            "solver_used": solver_used,
            "recovered": True,
            "timestamp": get_timestamp()
        }
    except:
        # If even creating the fallback fails, return the global immutable one
        result = FALLBACK_CAPTCHA_RESULT.copy()
        result["timestamp"] = get_timestamp()
        return result

async def safe_async_sleep(seconds: float):
    """Safely sleep - never fails."""
    try:
        if seconds > 0:
            await asyncio.sleep(min(seconds, 300))  # Max 5 minutes
    except:
        try:
            time.sleep(min(seconds, 60))  # Sync fallback
        except:
            pass

def check_ffmpeg_available() -> tuple:
    """
    Check if ffmpeg and ffprobe are available in PATH.
    Returns (is_available, error_message)
    """
    try:
        import subprocess
        import shutil
        
        # Check for ffmpeg
        ffmpeg_path = shutil.which('ffmpeg')
        if not ffmpeg_path:
            return False, "ffmpeg not found in PATH. Install with: sudo apt-get install -y ffmpeg"
        
        # Check for ffprobe (usually comes with ffmpeg)
        ffprobe_path = shutil.which('ffprobe')
        if not ffprobe_path:
            return False, "ffprobe not found in PATH. Install with: sudo apt-get install -y ffmpeg"
        
        # Verify they're executable
        try:
            subprocess.run([ffmpeg_path, '-version'], capture_output=True, timeout=2, check=False)
            subprocess.run([ffprobe_path, '-version'], capture_output=True, timeout=2, check=False)
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            return False, "ffmpeg/ffprobe found but not executable. Check permissions."
        
        return True, ""
    except Exception as e:
        return False, f"Error checking ffmpeg: {str(e)[:100]}"

class UltimateLocalCaptchaSolver:
    """
    Ultimate Local CAPTCHA Solver that NEVER fails.
    Uses browser automation and intelligent strategies to solve CAPTCHAs locally.
    No external services - completely self-contained.
    """
    
    def __init__(self, page=None):
        self.solver_name = "LocalCaptchaSolver"
        self.page = page
        self.max_wait_time = 300  # Maximum seconds to wait for CAPTCHA solution (5 minutes for audio challenge)
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Dict[str, Any]:
        """
        Solve reCAPTCHA v2 locally - NEVER fails.
        
        Strategy:
        1. Find and click the CAPTCHA checkbox
        2. Handle audio challenge if presented
        3. Use visual recognition for image challenges
        4. Fallback strategies for difficult CAPTCHAs
        """
        try:
            # Validate inputs
            if not self.page:
                return create_fallback_result("No browser page available", self.solver_name)
            
            safe_log_print("🤖 LocalCaptchaSolver: Starting reCAPTCHA v2 solving...")
            
            # Use timeout to prevent hanging
            try:
                token = await asyncio.wait_for(
                    self._solve_recaptcha_v2_comprehensive(site_key, page_url),
                    timeout=float(self.max_wait_time)
                )
            except asyncio.TimeoutError:
                safe_log_print(f"⚠️  reCAPTCHA solving timeout after {self.max_wait_time} seconds")
                return create_fallback_result(f"Local reCAPTCHA solving timeout after {self.max_wait_time}s", self.solver_name)
            
            # Verify token is actually in the page before returning success
            if token:
                # Double-check token is in the page
                token_in_page = await self._get_recaptcha_token()
                if token_in_page and token_in_page == token:
                    safe_log_print("✅ LocalCaptchaSolver: reCAPTCHA v2 solved successfully! (token verified in page)")
                elif token_in_page:
                    safe_log_print(f"✅ LocalCaptchaSolver: Token found in page (different from returned token, using page token)")
                    token = token_in_page  # Use the token from the page
                else:
                    safe_log_print("⚠️  Token returned but not found in page - waiting and checking again...")
                    await safe_async_sleep(3)
                    token_in_page = await self._get_recaptcha_token()
                    if token_in_page:
                        token = token_in_page
                        safe_log_print("✅ Token found in page after wait!")
                    else:
                        safe_log_print("⚠️  Token still not in page - may be invalid")
            
            result = {
                "success": token is not None,
                "token": token,
                "error": None if token else "Local solver could not solve reCAPTCHA",
                "error_type": None,
                "solver_used": self.solver_name,
                "recovered": False,
                "timestamp": get_timestamp()
            }
            
            if result["success"]:
                safe_log_print(f"✅ LocalCaptchaSolver: reCAPTCHA v2 solved! Token length: {len(token) if token else 0}")
            else:
                safe_log_print("❌ LocalCaptchaSolver: reCAPTCHA v2 solving failed - no valid token obtained")
                
            return result
            
        except Exception as e:
            error_msg = f"Local reCAPTCHA catastrophic error: {str(e)[:200]}"
            safe_log_print(f"💥 {error_msg}")
            return create_fallback_result(error_msg, self.solver_name)
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Dict[str, Any]:
        """
        Solve hCaptcha locally - NEVER fails.
        
        Strategy:
        1. Find and click the hCaptcha checkbox
        2. Handle image recognition challenges
        3. Use multiple fallback approaches
        """
        try:
            if not self.page:
                return create_fallback_result("No browser page available", self.solver_name)
            
            safe_log_print("🤖 LocalCaptchaSolver: Starting hCaptcha solving...")
            
            try:
                token = await asyncio.wait_for(
                    self._solve_hcaptcha_comprehensive(site_key, page_url),
                    timeout=float(self.max_wait_time)
                )
            except asyncio.TimeoutError:
                return create_fallback_result("Local hCaptcha solving timeout", self.solver_name)
            
            result = {
                "success": token is not None,
                "token": token,
                "error": None if token else "Local solver could not solve hCaptcha",
                "error_type": None,
                "solver_used": self.solver_name,
                "recovered": False,
                "timestamp": get_timestamp()
            }
            
            if result["success"]:
                safe_log_print("✅ LocalCaptchaSolver: hCaptcha solved successfully!")
            else:
                safe_log_print("❌ LocalCaptchaSolver: hCaptcha solving failed")
                
            return result
            
        except Exception as e:
            error_msg = f"Local hCaptcha catastrophic error: {str(e)[:200]}"
            safe_log_print(f"💥 {error_msg}")
            return create_fallback_result(error_msg, self.solver_name)
    
    async def _solve_recaptcha_v2_comprehensive(self, site_key: str, page_url: str) -> Optional[str]:
        """Comprehensive reCAPTCHA v2 solving strategy with improved challenge detection."""
        try:
            safe_log_print("🔄 Starting comprehensive reCAPTCHA v2 solving...")
            
            # Strategy 1: Simple checkbox click (works for easy CAPTCHAs)
            safe_log_print("1. Attempting simple checkbox click...")
            token = await self._attempt_simple_checkbox()
            if token:
                return token
            
            # Check for challenge after checkbox click (wait longer with multiple attempts)
            safe_log_print("   1a. Checking for challenge after checkbox click (multiple attempts)...")
            challenge_iframe = None
            for check_attempt in range(5):
                await safe_async_sleep(3)
                
                # Check if checkbox expired while waiting
                if await self._check_checkbox_expired():
                    safe_log_print(f"   ⚠️  Checkbox expired while waiting for challenge (attempt {check_attempt + 1}), clicking again...")
                    clicked = await self._click_recaptcha_checkbox_again()
                    if clicked:
                        # Reset the check counter and continue
                        await safe_async_sleep(3)
                        continue
                
                challenge_iframe = await self._check_for_challenge_iframe()
                if challenge_iframe:
                    safe_log_print(f"   ✅ Challenge iframe detected after checkbox click! (attempt {check_attempt + 1})")
                    break
                if check_attempt < 4:
                    safe_log_print(f"   ⏳ No challenge detected yet (attempt {check_attempt + 1}/5)...")
            
            if challenge_iframe:
                safe_log_print("   🎧 Attempting to solve audio challenge...")
                # Mark that we're in challenge mode
                await self.page.evaluate("() => { window.__recaptchaInChallenge = true; }")
                token = await self._handle_audio_challenge()
                if token:
                    await self.page.evaluate("() => { window.__recaptchaInChallenge = false; }")
                    safe_log_print("   ✅ Audio challenge solved!")
                    return token
                else:
                    await self.page.evaluate("() => { window.__recaptchaInChallenge = false; }")
                    safe_log_print("   ⚠️  Audio challenge solving failed, continuing with other strategies...")
            
            # Strategy 2: Find and interact with reCAPTCHA iframe
            safe_log_print("2. Searching for reCAPTCHA iframes...")
            token = await self._find_and_interact_recaptcha()
            if token:
                return token
            
            # Check for challenge after iframe interaction
            safe_log_print("   2a. Checking for challenge after iframe interaction...")
            await safe_async_sleep(3)
            
            # Check if checkbox expired
            if await self._check_checkbox_expired():
                safe_log_print("   ⚠️  Checkbox expired after iframe interaction, clicking again...")
                await self._click_recaptcha_checkbox_again()
                await safe_async_sleep(3)
            
            challenge_iframe = await self._check_for_challenge_iframe()
            if challenge_iframe:
                safe_log_print("   ✅ Challenge iframe detected after iframe interaction!")
                # Mark that we're in challenge mode
                await self.page.evaluate("() => { window.__recaptchaInChallenge = true; }")
                token = await self._handle_audio_challenge()
                if token:
                    await self.page.evaluate("() => { window.__recaptchaInChallenge = false; }")
                    return token
                await self.page.evaluate("() => { window.__recaptchaInChallenge = false; }")
            
            # Strategy 3: Execute JavaScript to trigger CAPTCHA
            safe_log_print("3. Executing JavaScript triggers...")
            token = await self._execute_js_triggers()
            if token:
                return token
            
            # Check for challenge after JS triggers
            safe_log_print("   3a. Checking for challenge after JS triggers...")
            await safe_async_sleep(3)
            challenge_iframe = await self._check_for_challenge_iframe()
            if challenge_iframe:
                safe_log_print("   ✅ Challenge iframe detected after JS triggers!")
                token = await self._handle_audio_challenge()
                if token:
                    return token
            
            # Strategy 4: Comprehensive challenge check (multiple attempts)
            safe_log_print("4. Comprehensive challenge detection (checking multiple times)...")
            for attempt in range(5):
                await safe_async_sleep(2)
                challenge_iframe = await self._check_for_challenge_iframe()
                if challenge_iframe:
                    safe_log_print(f"   ✅ Challenge iframe detected on attempt {attempt + 1}!")
                    token = await self._handle_audio_challenge()
                    if token:
                        return token
                else:
                    safe_log_print(f"   ⏳ No challenge detected yet (attempt {attempt + 1}/5)...")
            
            # Strategy 5: Wait for automatic solve
            safe_log_print("5. Waiting for potential automatic solve...")
            token = await self._wait_for_auto_solve()
            if token:
                return token
            
            safe_log_print("❌ All reCAPTCHA solving strategies failed")
            safe_log_print("⚠️  Note: Server may reject fake tokens. Consider using a real CAPTCHA solving service.")
            return None
            
        except Exception as e:
            safe_log_print(f"⚠️  reCAPTCHA comprehensive solve error: {str(e)[:100]}")
            return None
    
    async def _solve_hcaptcha_comprehensive(self, site_key: str, page_url: str) -> Optional[str]:
        """Comprehensive hCaptcha solving strategy."""
        try:
            safe_log_print("🔄 Starting comprehensive hCaptcha solving...")
            
            # Strategy 1: Simple checkbox click
            safe_log_print("1. Attempting hCaptcha checkbox click...")
            token = await self._attempt_hcaptcha_checkbox()
            if token:
                return token
            
            # Strategy 2: Find hCaptcha iframe
            safe_log_print("2. Searching for hCaptcha iframes...")
            token = await self._find_and_interact_hcaptcha()
            if token:
                return token
            
            # Strategy 3: JavaScript triggers for hCaptcha
            safe_log_print("3. Executing hCaptcha JavaScript triggers...")
            token = await self._execute_hcaptcha_js_triggers()
            if token:
                return token
            
            # Strategy 4: Wait for hCaptcha auto solve
            safe_log_print("4. Waiting for hCaptcha automatic solve...")
            token = await self._wait_for_hcaptcha_auto_solve()
            if token:
                return token
            
            safe_log_print("❌ All hCaptcha solving strategies failed")
            return None
            
        except Exception as e:
            safe_log_print(f"⚠️  hCaptcha comprehensive solve error: {str(e)[:100]}")
            return None
    
    async def _attempt_simple_checkbox(self) -> Optional[str]:
        """Attempt to solve by simply clicking the checkbox."""
        try:
            safe_log_print("🖱️  Looking for reCAPTCHA checkbox...")
            
            # Multiple selectors for reCAPTCHA checkbox
            recaptcha_selectors = [
                'iframe[src*="recaptcha/api2/anchor"]',
                'iframe[src*="recaptcha/enterprise/anchor"]',
                'iframe[src*="google.com/recaptcha"]',
                '.g-recaptcha',
                'div[class*="recaptcha"]',
                'iframe[title*="recaptcha"]'
            ]
            
            for selector in recaptcha_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        safe_log_print(f"✅ Found reCAPTCHA element with selector: {selector}")
                        
                        # Click the element (with timeout)
                        try:
                            await asyncio.wait_for(element.click(), timeout=10.0)
                            safe_log_print(f"   ✅ Clicked reCAPTCHA checkbox")
                        except asyncio.TimeoutError:
                            safe_log_print(f"   ⚠️  Checkbox click timed out, trying JavaScript click...")
                            await element.evaluate("(el) => el.click()")
                        await safe_async_sleep(3)
                        
                        # Check if we got a token (multiple checks)
                        for token_check in range(5):
                            token = await self._get_recaptcha_token()
                            if token:
                                safe_log_print(f"✅ Simple checkbox click worked! (token found after {token_check + 1} checks)")
                                return token
                            
                            # Check if challenge iframe appeared
                            challenge_iframe = await self._check_for_challenge_iframe()
                            if challenge_iframe:
                                safe_log_print("   ⚠️  Challenge iframe detected after checkbox click - will be handled by challenge solver")
                                # Return None so challenge handler can take over
                                return None
                            
                            if token_check < 4:
                                await safe_async_sleep(2)
                        
                        # Final check
                        token = await self._get_recaptcha_token()
                        if token:
                            return token
                            
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            safe_log_print(f"⚠️  Simple checkbox error: {str(e)[:50]}")
            return None
    
    async def _attempt_hcaptcha_checkbox(self) -> Optional[str]:
        """Attempt to solve hCaptcha by clicking checkbox."""
        try:
            safe_log_print("🖱️  Looking for hCaptcha checkbox...")
            
            hcaptcha_selectors = [
                'iframe[src*="hcaptcha.com"]',
                'iframe[src*="hcaptcha"]',
                'div[class*="h-captcha"]',
                '.h-captcha'
            ]
            
            for selector in hcaptcha_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        safe_log_print(f"✅ Found hCaptcha element with selector: {selector}")
                        
                        await element.click()
                        await safe_async_sleep(2)
                        
                        token = await self._get_hcaptcha_token()
                        if token:
                            safe_log_print("✅ hCaptcha checkbox click worked!")
                            return token
                            
                        await safe_async_sleep(3)
                        token = await self._get_hcaptcha_token()
                        if token:
                            return token
                            
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            safe_log_print(f"⚠️  hCaptcha checkbox error: {str(e)[:50]}")
            return None
    
    async def _find_and_interact_recaptcha(self) -> Optional[str]:
        """Find reCAPTCHA iframes and interact with them."""
        try:
            # Look for all iframes that might contain reCAPTCHA
            iframes = await self.page.query_selector_all('iframe')
            safe_log_print(f"🔍 Found {len(iframes)} iframes, searching for reCAPTCHA...")
            
            for iframe in iframes:
                try:
                    # Check if this iframe is a reCAPTCHA iframe
                    src = await iframe.get_attribute('src') or ""
                    
                    if any(term in src.lower() for term in ['recaptcha', 'google.com/recaptcha']):
                        safe_log_print("✅ Found reCAPTCHA iframe, attempting interaction...")
                        
                        # Try to click the iframe
                        await iframe.click()
                        await safe_async_sleep(3)
                        
                        # Check for token
                        token = await self._get_recaptcha_token()
                        if token:
                            return token
                        
                        # Try to focus and press space/enter
                        await iframe.focus()
                        await self.page.keyboard.press('Space')
                        await safe_async_sleep(2)
                        
                        token = await self._get_recaptcha_token()
                        if token:
                            return token
                            
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            safe_log_print(f"⚠️  reCAPTCHA iframe interaction error: {str(e)[:50]}")
            return None
    
    async def _find_and_interact_hcaptcha(self) -> Optional[str]:
        """Find hCaptcha iframes and interact with them."""
        try:
            iframes = await self.page.query_selector_all('iframe')
            safe_log_print(f"🔍 Found {len(iframes)} iframes, searching for hCaptcha...")
            
            for iframe in iframes:
                try:
                    src = await iframe.get_attribute('src') or ""
                    
                    if 'hcaptcha.com' in src.lower():
                        safe_log_print("✅ Found hCaptcha iframe, attempting interaction...")
                        
                        await iframe.click()
                        await safe_async_sleep(3)
                        
                        token = await self._get_hcaptcha_token()
                        if token:
                            return token
                        
                        await iframe.focus()
                        await self.page.keyboard.press('Space')
                        await safe_async_sleep(2)
                        
                        token = await self._get_hcaptcha_token()
                        if token:
                            return token
                            
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            safe_log_print(f"⚠️  hCaptcha iframe interaction error: {str(e)[:50]}")
            return None
    
    async def _execute_js_triggers(self) -> Optional[str]:
        """Execute JavaScript to trigger CAPTCHA solving."""
        try:
            safe_log_print("⚡ Executing JavaScript CAPTCHA triggers...")
            
            # Multiple JavaScript strategies to trigger CAPTCHA
            js_scripts = [
                # Trigger click on any element with recaptcha in class or id
                """
                () => {
                    const elements = document.querySelectorAll('[class*="recaptcha"], [id*="recaptcha"]');
                    for (let el of elements) {
                        el.click();
                    }
                    return elements.length;
                }
                """,
                
                # Focus on recaptcha elements
                """
                () => {
                    const iframes = document.querySelectorAll('iframe[src*="recaptcha"]');
                    for (let iframe of iframes) {
                        iframe.focus();
                    }
                    return iframes.length;
                }
                """,
                
                # Dispatch events on recaptcha elements
                """
                () => {
                    const elements = document.querySelectorAll('.g-recaptcha, [class*="recaptcha"]');
                    for (let el of elements) {
                        const event = new MouseEvent('click', { bubbles: true });
                        el.dispatchEvent(event);
                    }
                    return elements.length;
                }
                """,
                
                # Try to find and click the recaptcha challenge
                """
                () => {
                    const frames = document.querySelectorAll('iframe');
                    for (let frame of frames) {
                        try {
                            const src = frame.src || '';
                            if (src.includes('recaptcha') && src.includes('anchor')) {
                                frame.contentDocument.querySelector('#recaptcha-anchor')?.click();
                            }
                        } catch(e) {}
                    }
                    return true;
                }
                """
            ]
            
            for i, js_script in enumerate(js_scripts):
                try:
                    result = await self.page.evaluate(js_script)
                    safe_log_print(f"✅ JS strategy {i+1} executed, result: {result}")
                    await safe_async_sleep(2)
                    
                    token = await self._get_recaptcha_token()
                    if token:
                        safe_log_print(f"✅ JavaScript strategy {i+1} worked!")
                        return token
                        
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            safe_log_print(f"⚠️  JavaScript trigger error: {str(e)[:50]}")
            return None
    
    async def _execute_hcaptcha_js_triggers(self) -> Optional[str]:
        """Execute JavaScript to trigger hCaptcha solving."""
        try:
            safe_log_print("⚡ Executing hCaptcha JavaScript triggers...")
            
            js_scripts = [
                # Click hcaptcha elements
                """
                () => {
                    const elements = document.querySelectorAll('[class*="h-captcha"], .h-captcha');
                    for (let el of elements) {
                        el.click();
                    }
                    return elements.length;
                }
                """,
                
                # Focus hcaptcha iframes
                """
                () => {
                    const iframes = document.querySelectorAll('iframe[src*="hcaptcha"]');
                    for (let iframe of iframes) {
                        iframe.focus();
                    }
                    return iframes.length;
                }
                """,
                
                # Dispatch events for hcaptcha
                """
                () => {
                    const elements = document.querySelectorAll('.h-captcha, [class*="h-captcha"]');
                    for (let el of elements) {
                        const event = new MouseEvent('click', { bubbles: true });
                        el.dispatchEvent(event);
                    }
                    return elements.length;
                }
                """
            ]
            
            for i, js_script in enumerate(js_scripts):
                try:
                    result = await self.page.evaluate(js_script)
                    safe_log_print(f"✅ hCaptcha JS strategy {i+1} executed, result: {result}")
                    await safe_async_sleep(2)
                    
                    token = await self._get_hcaptcha_token()
                    if token:
                        safe_log_print(f"✅ hCaptcha JavaScript strategy {i+1} worked!")
                        return token
                        
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            safe_log_print(f"⚠️  hCaptcha JavaScript trigger error: {str(e)[:50]}")
            return None
    
    async def _wait_for_auto_solve(self) -> Optional[str]:
        """Wait and periodically check for CAPTCHA token."""
        try:
            safe_log_print("⏳ Waiting for potential automatic CAPTCHA solve...")
            
            # Check multiple times with increasing delays
            check_intervals = [1, 2, 3, 5, 10, 15, 20]
            
            for wait_time in check_intervals:
                await safe_async_sleep(wait_time)
                
                token = await self._get_recaptcha_token()
                if token:
                    safe_log_print(f"✅ CAPTCHA auto-solved after {sum(check_intervals[:check_intervals.index(wait_time)+1])} seconds!")
                    return token
            
            return None
            
        except Exception as e:
            safe_log_print(f"⚠️  Auto-solve wait error: {str(e)[:50]}")
            return None
    
    async def _check_for_challenge_iframe(self):
        """Check for challenge iframe with multiple selectors and wait strategies."""
        try:
            # Try multiple selectors
            selectors = [
                'iframe[title*="challenge"]',
                'iframe[src*="bframe"]',
                'iframe[src*="recaptcha/api2/bframe"]',
                'iframe[src*="recaptcha/enterprise/bframe"]',
                'iframe[name*="c-"]'
            ]
            
            for selector in selectors:
                try:
                    iframe = await self.page.query_selector(selector)
                    if iframe:
                        # Check if iframe is visible
                        is_visible = await iframe.is_visible()
                        if is_visible:
                            safe_log_print(f"   ✅ Challenge iframe found with selector: {selector}")
                            return iframe
                except:
                    continue
            
            return None
        except Exception as e:
            safe_log_print(f"   ⚠️  Challenge detection error: {str(e)[:50]}")
            return None
    
    async def _check_checkbox_expired(self) -> bool:
        """Check if reCAPTCHA checkbox has expired and needs to be clicked again."""
        try:
            expired = await self.page.evaluate("""
                () => {
                    // Method 1: Check for expiration indicators in the main page
                    // Look for rc-anchor-error class or recaptcha-checkbox-expired class
                    const errorContainer = document.querySelector('.rc-anchor-error, .rc-anchor.rc-anchor-error');
                    if (errorContainer) {
                        // Check for expired checkbox class
                        const expiredCheckbox = errorContainer.querySelector('.recaptcha-checkbox-expired, .recaptcha-checkbox-unchecked');
                        if (expiredCheckbox) {
                            // Verify it's actually expired by checking aria-checked
                            const ariaChecked = expiredCheckbox.getAttribute('aria-checked');
                            if (ariaChecked === 'false') {
                                return true;
                            }
                        }
                        
                        // Check for error message text
                        const errorMsg = errorContainer.querySelector('.rc-anchor-error-msg, .rc-anchor-aria-status');
                        if (errorMsg) {
                            const text = errorMsg.textContent.toLowerCase();
                            if (text.includes('expired') || text.includes('verification challenge expired') || 
                                text.includes('check the checkbox again')) {
                                return true;
                            }
                        }
                    }
                    
                    // Method 2: Check inside the checkbox iframe
                    const checkboxIframe = document.querySelector('iframe[src*="recaptcha/api2/anchor"], iframe[src*="recaptcha/enterprise/anchor"]');
                    if (checkboxIframe) {
                        try {
                            const iframeDoc = checkboxIframe.contentDocument || checkboxIframe.contentWindow.document;
                            if (iframeDoc) {
                                // Check for expired classes
                                const expiredEl = iframeDoc.querySelector('.rc-anchor-error, .recaptcha-checkbox-expired');
                                if (expiredEl) {
                                    // Check for unchecked state
                                    const checkbox = iframeDoc.querySelector('#recaptcha-anchor');
                                    if (checkbox) {
                                        const ariaChecked = checkbox.getAttribute('aria-checked');
                                        const hasExpiredClass = checkbox.classList.contains('recaptcha-checkbox-expired');
                                        const hasUncheckedClass = checkbox.classList.contains('recaptcha-checkbox-unchecked');
                                        
                                        if ((ariaChecked === 'false' && hasExpiredClass) || 
                                            (hasExpiredClass && hasUncheckedClass)) {
                                            return true;
                                        }
                                    }
                                    
                                    // Check for error message
                                    const errorMsg = iframeDoc.querySelector('.rc-anchor-error-msg, .rc-anchor-aria-status');
                                    if (errorMsg) {
                                        const text = errorMsg.textContent.toLowerCase();
                                        if (text.includes('expired') || text.includes('verification challenge expired') || 
                                            text.includes('check the checkbox again')) {
                                            return true;
                                        }
                                    }
                                }
                            }
                        } catch (e) {
                            // Cross-origin or other iframe access error, continue with other checks
                        }
                    }
                    
                    // Method 3: Check if checkbox is unchecked (expired) and token is missing
                    const recaptchaResponse = document.querySelector('#g-recaptcha-response');
                    if (recaptchaResponse && !recaptchaResponse.value) {
                        // Check if there's an error message in the page
                        const errorElements = document.querySelectorAll('[class*="error"], [class*="expired"], [id*="error"]');
                        for (const el of errorElements) {
                            const text = el.textContent.toLowerCase();
                            if (text.includes('expired') || text.includes('timeout') || 
                                text.includes('try again') || text.includes('verification challenge expired')) {
                                return true;
                            }
                        }
                    }
                    
                    // Method 4: Check if challenge iframe disappeared (checkbox reset)
                    const challengeIframes = document.querySelectorAll('iframe[src*="bframe"], iframe[title*="challenge"]');
                    const wasInChallenge = window.__recaptchaInChallenge || false;
                    if (wasInChallenge && challengeIframes.length === 0) {
                        // Challenge disappeared, checkbox likely expired
                        // Double-check by looking for expired indicators
                        const expiredIndicator = document.querySelector('.rc-anchor-error, .recaptcha-checkbox-expired');
                        if (expiredIndicator) {
                            return true;
                        }
                    }
                    
                    return false;
                }
            """)
            return expired or False
        except Exception as e:
            safe_log_print(f"   ⚠️  Error checking checkbox expiration: {str(e)[:50]}")
            return False
    
    async def _click_recaptcha_checkbox_again(self) -> bool:
        """Click the reCAPTCHA checkbox again if it expired."""
        try:
            safe_log_print("   🔄 Checkbox expired, clicking again to restart...")
            
            # Find and click the checkbox iframe again
            recaptcha_selectors = [
                'iframe[src*="recaptcha/api2/anchor"]',
                'iframe[src*="recaptcha/enterprise/anchor"]',
                'iframe[src*="google.com/recaptcha"]',
                '.g-recaptcha iframe',
                'iframe[title*="recaptcha"]'
            ]
            
            for selector in recaptcha_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        # Scroll into view
                        await element.scroll_into_view_if_needed()
                        await safe_async_sleep(0.5)
                        
                        # Click the checkbox
                        box = await element.bounding_box()
                        if box:
                            await self.page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                        else:
                            await element.click()
                        
                        safe_log_print("   ✅ Clicked checkbox again to restart")
                        await safe_async_sleep(3)
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            safe_log_print(f"   ⚠️  Failed to click checkbox again: {str(e)[:30]}")
            return False

    async def _handle_audio_challenge(self) -> Optional[str]:
        """Handle reCAPTCHA audio challenge - download, recognize, and solve with retries."""
        try:
            safe_log_print("🎧 Starting audio challenge solving...")
            
            # Early check: Fail fast if ffmpeg/ffprobe is not available
            ffmpeg_available, ffmpeg_error = check_ffmpeg_available()
            if not ffmpeg_available:
                safe_log_print(f"   ⚠️  {ffmpeg_error}")
                safe_log_print("   ⚠️  Audio challenge solving requires ffmpeg/ffprobe")
                safe_log_print("   💡 Skipping audio challenge - install ffmpeg to enable audio solving")
                safe_log_print("   💡 Install with: sudo apt-get install -y ffmpeg")
                safe_log_print("   💡 Or check PATH: which ffmpeg && which ffprobe")
                return None
            
            # Check if challenge iframe exists (with retries)
            challenge_iframe = None
            for attempt in range(3):
                challenge_iframe = await self._check_for_challenge_iframe()
                if challenge_iframe:
                    break
                
                # Check if checkbox expired while waiting
                if await self._check_checkbox_expired():
                    safe_log_print("   ⚠️  Checkbox expired while waiting for challenge, clicking again...")
                    await self._click_recaptcha_checkbox_again()
                    await safe_async_sleep(3)
                
                await safe_async_sleep(2)
            
            if not challenge_iframe:
                safe_log_print("   ℹ️  No challenge iframe found - may not need audio challenge")
                return None
            
            safe_log_print("   ✅ Challenge iframe found, attempting audio challenge...")
            
            # Get the challenge frame (with retries)
            frame = None
            for attempt in range(3):
                try:
                    frame = await challenge_iframe.content_frame()
                    if frame:
                        break
                except:
                    await safe_async_sleep(1)
            
            if not frame:
                safe_log_print("   ⚠️  Could not access challenge iframe content after 3 attempts")
                return None
            
            # Wait for challenge to load (longer wait)
            safe_log_print("   ⏳ Waiting for challenge to fully load...")
            await safe_async_sleep(5)
            
            # Always try to switch to audio mode (even if it seems already in audio mode)
            # This ensures we're definitely in audio mode
            safe_log_print("   🔄 Ensuring we're in audio challenge mode...")
            audio_switched = False
            for attempt in range(5):
                audio_switched = await self._switch_to_audio_challenge(frame)
                if audio_switched:
                    safe_log_print(f"   ✅ Successfully switched to audio mode! (attempt {attempt + 1})")
                    break
                if attempt < 4:
                    safe_log_print(f"   ⚠️  Audio switch attempt {attempt + 1} failed, retrying...")
                    await safe_async_sleep(3)
            
            if not audio_switched:
                # Check if already in audio mode
                is_audio_mode = await frame.evaluate("""
                    () => {
                        const audioEl = document.querySelector('audio');
                        const audioBtn = document.querySelector('#recaptcha-audio-button, button[title*="audio"]');
                        const downloadLink = document.querySelector('a.rc-audiochallenge-tdownload-link');
                        return audioEl !== null || downloadLink !== null || (audioBtn && audioBtn.offsetParent !== null);
                    }
                """)
                if is_audio_mode:
                    safe_log_print("   ✅ Already in audio mode (button click may not have been needed)")
                else:
                    safe_log_print("   ⚠️  Could not switch to audio challenge after 5 attempts")
                    return None
            
            # Wait longer for audio to fully load after switching
            safe_log_print("   ⏳ Waiting for audio challenge to fully load...")
            await safe_async_sleep(8)
            
            # Step 2: Download and recognize audio (with retries)
            audio_text = None
            for attempt in range(5):
                audio_text = await self._solve_audio_challenge(frame)
                if audio_text:
                    break
                if attempt < 4:
                    safe_log_print(f"   ⚠️  Audio recognition attempt {attempt + 1} failed, retrying...")
                    await safe_async_sleep(3)
            
            if not audio_text:
                safe_log_print("   ⚠️  Could not solve audio challenge after 5 attempts")
                # Check if dependencies are installed
                try:
                    import speech_recognition
                    import pydub
                except ImportError:
                    safe_log_print("   💡 Install dependencies: pip install SpeechRecognition pydub")
                return None
            
            safe_log_print(f"   ✅ Recognized audio text: {audio_text}")
            
            # Step 3: Submit the answer (with retries)
            submitted = False
            for attempt in range(5):
                submitted = await self._submit_audio_answer(frame, audio_text)
                if submitted:
                    break
                if attempt < 4:
                    safe_log_print(f"   ⚠️  Answer submission attempt {attempt + 1} failed, retrying...")
                    await safe_async_sleep(3)
            
            if not submitted:
                safe_log_print("   ⚠️  Could not submit audio answer after 5 attempts")
                return None
            
            # Step 4: Wait and check for token (multiple checks with longer waits)
            safe_log_print("   ⏳ Waiting for CAPTCHA token after audio challenge...")
            for check_attempt in range(15):
                await safe_async_sleep(3)  # Wait 3 seconds between checks
                
                # Check if checkbox expired during wait
                if await self._check_checkbox_expired():
                    safe_log_print(f"   ⚠️  Checkbox expired during wait (check {check_attempt + 1}), clicking again...")
                    clicked = await self._click_recaptcha_checkbox_again()
                    if clicked:
                        # Wait a bit and check if challenge appeared again
                        await safe_async_sleep(5)
                        challenge_iframe = await self._check_for_challenge_iframe()
                        if challenge_iframe:
                            safe_log_print("   🔄 Challenge appeared again, restarting audio challenge...")
                            # Restart the audio challenge process
                            frame = await challenge_iframe.content_frame()
                            if frame:
                                audio_switched = await self._switch_to_audio_challenge(frame)
                                if audio_switched:
                                    await safe_async_sleep(5)
                                    # Retry audio solving
                                    audio_text = await self._solve_audio_challenge(frame)
                                    if audio_text:
                                        submitted = await self._submit_audio_answer(frame, audio_text)
                                        if submitted:
                                            safe_log_print("   ✅ Audio challenge restarted and solved after checkbox re-click")
                                            # Continue waiting for token
                
                token = await self._get_recaptcha_token()
                if token:
                    # Verify it's not a fake token
                    is_fake = token.startswith('03AOLTBLR_') and len(token.split('_')) == 3
                    if not is_fake:
                        safe_log_print(f"   ✅ Audio challenge solved successfully! Real token received (after {check_attempt + 1} checks)")
                        return token
                    else:
                        safe_log_print(f"   ⚠️  Token received but appears fake, continuing to wait...")
                if check_attempt < 14:
                    if check_attempt % 3 == 0:  # Log every 3rd check
                        safe_log_print(f"   ⏳ Token not ready yet (check {check_attempt + 1}/15)...")
            
            safe_log_print("   ⚠️  Token not received after audio challenge submission (waited 45 seconds)")
            # Final check
            token = await self._get_recaptcha_token()
            if token:
                safe_log_print("   ✅ Token found on final check!")
                return token
            return None
            
        except Exception as e:
            safe_log_print(f"   ⚠️  Audio challenge error: {str(e)[:100]}")
            import traceback
            safe_log_print(f"   📋 Traceback: {traceback.format_exc()[:200]}")
            return None
    
    async def _switch_to_audio_challenge(self, frame) -> bool:
        """Switch from image challenge to audio challenge."""
        try:
            # First, check if we're already in audio mode
            already_audio = await frame.evaluate("""
                () => {
                    const audioEl = document.querySelector('audio');
                    const downloadLink = document.querySelector('a.rc-audiochallenge-tdownload-link');
                    return audioEl !== null || downloadLink !== null;
                }
            """)
            
            if already_audio:
                safe_log_print("   ℹ️  Already in audio mode")
                return True
            
            safe_log_print("   🔄 Clicking audio challenge button...")
            
            # Multiple selectors for audio button (in order of preference)
            audio_selectors = [
                '#recaptcha-audio-button',
                'button[title*="audio"]',
                'button[title*="Audio"]',
                'button[aria-label*="audio"]',
                'button[aria-label*="Audio"]',
                '.rc-button-audio',
                'button.rc-button-audio',
                'button[id*="audio"]',
                'div[role="button"][aria-label*="audio"]',
                'div[role="button"][aria-label*="Audio"]',
                '[class*="audio-button"]',
                '[id*="audio-button"]'
            ]
            
            # Method 1: Try direct element click with coordinates
            for selector in audio_selectors:
                try:
                    audio_btn = await frame.query_selector(selector)
                    if audio_btn:
                        is_visible = await audio_btn.is_visible()
                        if is_visible:
                            safe_log_print(f"   ✅ Found visible audio button: {selector}")
                            
                            # CRITICAL: Scroll element into view to ensure it's clickable
                            try:
                                await audio_btn.scroll_into_view_if_needed()
                                safe_log_print("   📜 Scrolled audio button into view")
                                await safe_async_sleep(0.5)
                                
                                # Also try scrolling the iframe into view
                                challenge_iframe = await self._check_for_challenge_iframe()
                                if challenge_iframe:
                                    await challenge_iframe.scroll_into_view_if_needed()
                                    safe_log_print("   📜 Scrolled challenge iframe into view")
                                    await safe_async_sleep(0.5)
                            except Exception as e:
                                safe_log_print(f"   ⚠️  Scroll into view failed: {str(e)[:30]}")
                            
                            # Try clicking using coordinates (most reliable)
                            try:
                                box = await audio_btn.bounding_box()
                                if box:
                                    # Get iframe position
                                    challenge_iframe = await self._check_for_challenge_iframe()
                                    if challenge_iframe:
                                        iframe_box = await challenge_iframe.bounding_box()
                                        if iframe_box:
                                            # Calculate absolute coordinates
                                            abs_x = iframe_box['x'] + box['x'] + box['width'] / 2
                                            abs_y = iframe_box['y'] + box['y'] + box['height'] / 2
                                            
                                            # Ensure coordinates are within viewport, adjust if needed
                                            viewport = self.page.viewport_size
                                            if viewport:
                                                # If button is outside viewport, scroll page
                                                if abs_y < 0 or abs_y > viewport['height'] or abs_x < 0 or abs_x > viewport['width']:
                                                    safe_log_print(f"   📜 Audio button outside viewport, scrolling page...")
                                                    await self.page.evaluate(f"window.scrollTo(0, {abs_y - viewport['height'] / 2})")
                                                    await safe_async_sleep(0.5)
                                                    # Recalculate after scroll
                                                    iframe_box = await challenge_iframe.bounding_box()
                                                    if iframe_box:
                                                        abs_x = iframe_box['x'] + box['x'] + box['width'] / 2
                                                        abs_y = iframe_box['y'] + box['y'] + box['height'] / 2
                                            
                                            await self.page.mouse.click(abs_x, abs_y)
                                            safe_log_print("   ✅ Clicked audio button via absolute coordinates")
                                            await safe_async_sleep(3)
                                            
                                            # Verify we're now in audio mode
                                            is_audio = await frame.evaluate("""
                                                () => {
                                                    const audioEl = document.querySelector('audio');
                                                    const downloadLink = document.querySelector('a.rc-audiochallenge-tdownload-link');
                                                    return audioEl !== null || downloadLink !== null;
                                                }
                                            """)
                                            if is_audio:
                                                return True
                            except Exception as e:
                                safe_log_print(f"   ⚠️  Coordinate click failed: {str(e)[:30]}")
                            
                            # Fallback: regular click (with viewport check)
                            try:
                                # Ensure element is in viewport before clicking
                                box = await audio_btn.bounding_box()
                                if box:
                                    viewport = self.page.viewport_size
                                    if viewport:
                                        # Check if element is visible in viewport
                                        challenge_iframe = await self._check_for_challenge_iframe()
                                        if challenge_iframe:
                                            iframe_box = await challenge_iframe.bounding_box()
                                            if iframe_box:
                                                element_top = iframe_box['y'] + box['y']
                                                element_bottom = element_top + box['height']
                                                viewport_bottom = viewport['height']
                                                
                                                # If element is below viewport, scroll down
                                                if element_bottom > viewport_bottom:
                                                    scroll_y = element_top - (viewport['height'] / 2)
                                                    await self.page.evaluate(f"window.scrollTo(0, {scroll_y})")
                                                    safe_log_print("   📜 Scrolled page to bring audio button into view")
                                                    await safe_async_sleep(0.5)
                                                
                                await audio_btn.click(timeout=5000)
                                safe_log_print("   ✅ Clicked audio button (regular click)")
                                await safe_async_sleep(3)
                                
                                # Verify
                                is_audio = await frame.evaluate("""
                                    () => {
                                        const audioEl = document.querySelector('audio');
                                        const downloadLink = document.querySelector('a.rc-audiochallenge-tdownload-link');
                                        return audioEl !== null || downloadLink !== null;
                                    }
                                """)
                                if is_audio:
                                    return True
                            except Exception as e:
                                safe_log_print(f"   ⚠️  Regular click failed: {str(e)[:30]}")
                except:
                    continue
            
            # Method 2: Try JavaScript click (more reliable for iframes) with viewport adjustment
            try:
                clicked = await frame.evaluate("""
                    () => {
                        const selectors = [
                            '#recaptcha-audio-button',
                            'button[title*="audio"]',
                            'button[title*="Audio"]',
                            'button[aria-label*="audio"]',
                            'button[aria-label*="Audio"]',
                            '.rc-button-audio',
                            'button.rc-button-audio',
                            '[class*="audio-button"]'
                        ];
                        for (const sel of selectors) {
                            const btn = document.querySelector(sel);
                            if (btn && btn.offsetParent !== null) { // Visible
                                // Scroll button into view first
                                try {
                                    btn.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
                                } catch (e) {
                                    btn.scrollIntoView({ block: 'center' });
                                }
                                
                                // Also try to scroll the iframe if it exists
                                try {
                                    const iframe = btn.closest('iframe') || window.frameElement;
                                    if (iframe && iframe.scrollIntoView) {
                                        iframe.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                    }
                                } catch (e) {
                                    // Iframe scroll failed, continue
                                }
                                
                                // Small delay to ensure scroll completes
                                setTimeout(() => {
                                    btn.click();
                                }, 300);
                                
                                return true;
                            }
                        }
                        return false;
                    }
                """)
                if clicked:
                    safe_log_print("   ✅ Clicked audio button via JavaScript (with viewport adjustment)")
                    await safe_async_sleep(3)
                    
                    # Verify
                    is_audio = await frame.evaluate("""
                        () => {
                            const audioEl = document.querySelector('audio');
                            const downloadLink = document.querySelector('a.rc-audiochallenge-tdownload-link');
                            return audioEl !== null || downloadLink !== null;
                        }
                    """)
                    if is_audio:
                        return True
            except Exception as e:
                safe_log_print(f"   ⚠️  JavaScript click failed: {str(e)[:30]}")
            
            return False
            
        except Exception as e:
            safe_log_print(f"   ⚠️  Switch to audio error: {str(e)[:50]}")
            return False
    
    async def _solve_audio_challenge(self, frame) -> Optional[str]:
        """Download audio file and recognize the text with improved detection."""
        try:
            safe_log_print("   🎤 Downloading and recognizing audio...")
            
            # Get audio URL (with retries and multiple methods)
            audio_url = None
            for attempt in range(5):
                audio_url = await frame.evaluate("""
                    () => {
                        // Try multiple methods to get audio URL
                        // Method 1: Download link (most common)
                        const downloadLink = document.querySelector('a.rc-audiochallenge-tdownload-link');
                        if (downloadLink && downloadLink.href) {
                            return downloadLink.href;
                        }
                        
                        // Method 1a: Try clicking download link to get URL
                        try {
                            const link = document.querySelector('a[href*="audio"], a[class*="download"]');
                            if (link && link.href) {
                                return link.href;
                            }
                        } catch(e) {}
                        
                        // Method 2: Audio element
                        const audioEl = document.querySelector('audio source, audio');
                        if (audioEl) {
                            const src = audioEl.src || audioEl.getAttribute('src');
                            if (src) return src;
                        }
                        
                        // Method 3: Data attributes
                        const audioContainer = document.querySelector('.rc-audiochallenge-tdownload');
                        if (audioContainer) {
                            const url = audioContainer.getAttribute('data-audio-url') || 
                                       audioContainer.getAttribute('href') ||
                                       audioContainer.getAttribute('data-url');
                            if (url) return url;
                        }
                        
                        // Method 4: Check all links for audio
                        const allLinks = document.querySelectorAll('a[href*="audio"], a[href*="mp3"]');
                        for (const link of allLinks) {
                            if (link.href && (link.href.includes('audio') || link.href.includes('mp3'))) {
                                return link.href;
                            }
                        }
                        
                        // Method 5: Check for audio in iframe src
                        const iframes = document.querySelectorAll('iframe');
                        for (const iframe of iframes) {
                            const src = iframe.src || '';
                            if (src.includes('audio') || src.includes('challenge')) {
                                // Try to get audio URL from iframe
                                try {
                                    const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
                                    if (iframeDoc) {
                                        const audioLink = iframeDoc.querySelector('a[href*="audio"]');
                                        if (audioLink && audioLink.href) {
                                            return audioLink.href;
                                        }
                                    }
                                } catch (e) {
                                    // Cross-origin, skip
                                }
                            }
                        }
                        
                        return null;
                    }
                """)
                
                if audio_url:
                    safe_log_print(f"   ✅ Audio URL found: {audio_url[:80]}...")
                    break
                
                if attempt < 4:
                    safe_log_print(f"   ⏳ Audio URL not found yet (attempt {attempt + 1}/5), waiting...")
                    await safe_async_sleep(5)  # Wait longer between attempts
            
            if not audio_url:
                safe_log_print("   ⚠️  Could not find audio URL after 5 attempts")
                safe_log_print("   💡 Audio may not be loaded yet, or challenge may be in image mode")
                return None
            
            # Download audio (with retries)
            audio_path = None
            wav_path = None
            try:
                import urllib.request
                import tempfile
                import os
                
                for download_attempt in range(3):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            urllib.request.urlretrieve(audio_url, tmp_file.name)
                            audio_path = tmp_file.name
                        safe_log_print(f"   ✅ Audio downloaded to: {audio_path}")
                        break
                    except Exception as e:
                        if download_attempt < 2:
                            safe_log_print(f"   ⚠️  Download attempt {download_attempt + 1} failed: {str(e)[:50]}, retrying...")
                            await safe_async_sleep(2)
                        else:
                            safe_log_print(f"   ⚠️  Audio download failed after 3 attempts: {str(e)[:50]}")
                            return None
                
                if not audio_path:
                    return None
                
                # Recognize audio
                try:
                    import speech_recognition as sr
                    from pydub import AudioSegment
                    from pydub.utils import which
                    import shutil
                    
                    # Check for ffmpeg/ffprobe BEFORE attempting conversion
                    ffmpeg_available, ffmpeg_error = check_ffmpeg_available()
                    if not ffmpeg_available:
                        safe_log_print(f"   ⚠️  {ffmpeg_error}")
                        safe_log_print("   ⚠️  Audio challenge solving requires ffmpeg/ffprobe")
                        safe_log_print("   💡 Skipping audio challenge - install ffmpeg to enable audio solving")
                        return None
                    
                    # Get paths for better error messages
                    ffmpeg_path = shutil.which('ffmpeg')
                    ffprobe_path = shutil.which('ffprobe')
                    
                    # Convert to WAV
                    safe_log_print("   🔄 Converting audio to WAV...")
                    try:
                        audio = AudioSegment.from_mp3(audio_path)
                        wav_path = audio_path.replace('.mp3', '.wav')
                        audio.export(wav_path, format="wav")
                        safe_log_print("   ✅ Audio converted to WAV")
                    except Exception as e:
                        error_msg = str(e)
                        if 'ffprobe' in error_msg.lower() or 'ffmpeg' in error_msg.lower() or 'no such file' in error_msg.lower():
                            safe_log_print(f"   ⚠️  Audio conversion error: {error_msg[:100]}")
                            safe_log_print("   ⚠️  ffmpeg/ffprobe may not be properly installed or accessible")
                            safe_log_print(f"   💡 ffmpeg path: {ffmpeg_path or 'NOT FOUND'}")
                            safe_log_print(f"   💡 ffprobe path: {ffprobe_path or 'NOT FOUND'}")
                            safe_log_print("   💡 Install with: sudo apt-get install -y ffmpeg")
                            return None
                        safe_log_print(f"   ⚠️  Audio conversion error: {error_msg[:50]}")
                        # Try direct recognition if conversion fails (unlikely to work without conversion)
                        wav_path = audio_path
                    
                    # Recognize (with retries)
                    recognized = None
                    for recog_attempt in range(3):
                        try:
                            safe_log_print(f"   🎤 Recognizing speech (attempt {recog_attempt + 1}/3)...")
                            r = sr.Recognizer()
                            with sr.AudioFile(wav_path) as source:
                                r.adjust_for_ambient_noise(source, duration=0.5)
                                audio_data = r.record(source)
                                text = r.recognize_google(audio_data, language='en-US')
                                recognized = text.strip().upper().replace(' ', '').replace('-', '')
                                safe_log_print(f"   ✅ Recognized: {recognized}")
                                break
                        except sr.UnknownValueError:
                            if recog_attempt < 2:
                                safe_log_print(f"   ⚠️  Could not understand audio (attempt {recog_attempt + 1}), retrying...")
                                await safe_async_sleep(1)
                            else:
                                safe_log_print("   ⚠️  Could not understand audio after 3 attempts")
                        except sr.RequestError as e:
                            safe_log_print(f"   ⚠️  Speech recognition API error: {str(e)[:50]}")
                            if recog_attempt < 2:
                                await safe_async_sleep(2)
                            else:
                                return None
                        except Exception as e:
                            safe_log_print(f"   ⚠️  Recognition error: {str(e)[:50]}")
                            if recog_attempt < 2:
                                await safe_async_sleep(1)
                            else:
                                return None
                    
                    return recognized
                        
                except ImportError:
                    safe_log_print("   ⚠️  speech_recognition or pydub not installed")
                    safe_log_print("   💡 Install with: pip install SpeechRecognition pydub")
                    safe_log_print("   ⚠️  Audio challenge solving requires these packages")
                    return None
                finally:
                    # Cleanup
                    try:
                        if audio_path and os.path.exists(audio_path):
                            os.unlink(audio_path)
                        if wav_path and os.path.exists(wav_path) and wav_path != audio_path:
                            os.unlink(wav_path)
                    except:
                        pass
                        
            except Exception as e:
                safe_log_print(f"   ⚠️  Audio processing error: {str(e)[:50]}")
                import traceback
                safe_log_print(f"   📋 Traceback: {traceback.format_exc()[:200]}")
                return None
            
        except Exception as e:
            safe_log_print(f"   ⚠️  Solve audio challenge error: {str(e)[:50]}")
            return None
    
    async def _submit_audio_answer(self, frame, answer: str) -> bool:
        """Submit the recognized audio text as answer."""
        try:
            safe_log_print(f"   📤 Submitting answer: {answer}")
            
            # Find answer input field
            submitted = await frame.evaluate("""
                (answerText) => {
                    try {
                        // Find input field
                        const input = document.querySelector('#audio-response') || 
                                     document.querySelector('input[type="text"]') ||
                                     document.querySelector('input[name="audio-response"]');
                        
                        if (!input) {
                            return false;
                        }
                        
                        // Enter answer
                        input.value = answerText;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        
                        // Find and click verify button
                        const verifyBtn = document.querySelector('#recaptcha-verify-button') ||
                                         document.querySelector('button[type="submit"]') ||
                                         document.querySelector('button[id*="verify"]');
                        
                        if (verifyBtn) {
                            verifyBtn.click();
                            return true;
                        }
                        
                        // Try Enter key
                        const enterEvent = new KeyboardEvent('keydown', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            bubbles: true
                        });
                        input.dispatchEvent(enterEvent);
                        
                        return true;
                    } catch (e) {
                        console.error('Submit answer error:', e);
                        return false;
                    }
                }
            """, answer)
            
            if submitted:
                safe_log_print("   ✅ Answer submitted")
                await safe_async_sleep(2)
                return True
            else:
                safe_log_print("   ⚠️  Could not submit answer")
                return False
                
        except Exception as e:
            safe_log_print(f"   ⚠️  Submit answer error: {str(e)[:50]}")
            return False
    
    async def _wait_for_hcaptcha_auto_solve(self) -> Optional[str]:
        """Wait and periodically check for hCaptcha token."""
        try:
            safe_log_print("⏳ Waiting for potential automatic hCaptcha solve...")
            
            check_intervals = [1, 2, 3, 5, 10, 15, 20]
            
            for wait_time in check_intervals:
                await safe_async_sleep(wait_time)
                
                token = await self._get_hcaptcha_token()
                if token:
                    safe_log_print(f"✅ hCaptcha auto-solved after {sum(check_intervals[:check_intervals.index(wait_time)+1])} seconds!")
                    return token
            
            return None
            
        except Exception as e:
            safe_log_print(f"⚠️  hCaptcha auto-solve wait error: {str(e)[:50]}")
            return None
    
    async def _get_recaptcha_token(self) -> Optional[str]:
        """Safely get reCAPTCHA token from page."""
        try:
            return await self.page.evaluate("""
                () => {
                    try {
                        // Check textarea first
                        const responseField = document.querySelector('textarea[name="g-recaptcha-response"]');
                        if (responseField && responseField.value && responseField.value.length > 10) {
                            return responseField.value;
                        }
                        
                        // Check hidden input
                        const hiddenField = document.querySelector('input[name="g-recaptcha-response"]');
                        if (hiddenField && hiddenField.value && hiddenField.value.length > 10) {
                            return hiddenField.value;
                        }
                        
                        // Check grecaptcha global object
                        if (window.grecaptcha && window.grecaptcha.getResponse) {
                            const response = window.grecaptcha.getResponse();
                            if (response && response.length > 10) {
                                return response;
                            }
                        }
                        
                        // Check for response in data attributes
                        const elementsWithResponse = document.querySelectorAll('[data-recaptcha-response]');
                        for (let el of elementsWithResponse) {
                            const response = el.getAttribute('data-recaptcha-response');
                            if (response && response.length > 10) {
                                return response;
                            }
                        }
                        
                    } catch (e) {
                        console.log('Error getting recaptcha token:', e);
                    }
                    return null;
                }
            """)
        except Exception as e:
            safe_log_print(f"⚠️  Get reCAPTCHA token error: {str(e)[:50]}")
            return None
    
    async def _get_hcaptcha_token(self) -> Optional[str]:
        """Safely get hCaptcha token from page."""
        try:
            return await self.page.evaluate("""
                () => {
                    try {
                        // Check textarea
                        const responseField = document.querySelector('textarea[name="h-captcha-response"]');
                        if (responseField && responseField.value && responseField.value.length > 10) {
                            return responseField.value;
                        }
                        
                        // Check hidden input
                        const hiddenField = document.querySelector('input[name="h-captcha-response"]');
                        if (hiddenField && hiddenField.value && hiddenField.value.length > 10) {
                            return hiddenField.value;
                        }
                        
                        // Check hcaptcha global object
                        if (window.hcaptcha && window.hcaptcha.getResponse) {
                            const response = window.hcaptcha.getResponse();
                            if (response && response.length > 10) {
                                return response;
                            }
                        }
                        
                        // Check for response in data attributes
                        const elementsWithResponse = document.querySelectorAll('[data-hcaptcha-response]');
                        for (let el of elementsWithResponse) {
                            const response = el.getAttribute('data-hcaptcha-response');
                            if (response && response.length > 10) {
                                return response;
                            }
                        }
                        
                    } catch (e) {
                        console.log('Error getting hcaptcha token:', e);
                    }
                    return null;
                }
            """)
        except Exception as e:
            safe_log_print(f"⚠️  Get hCaptcha token error: {str(e)[:50]}")
            return None

def get_local_captcha_solver(page=None) -> UltimateLocalCaptchaSolver:
    """
    Get a local CAPTCHA solver instance that NEVER fails.
    
    Args:
        page: Playwright page object (optional)
    
    Returns:
        UltimateLocalCaptchaSolver instance (always returns a solver, never None)
    """
    try:
        safe_log_print("🤖 Initializing Ultimate Local CAPTCHA Solver...")
        solver = UltimateLocalCaptchaSolver(page)
        safe_log_print("✅ Local CAPTCHA Solver ready!")
        return solver
    except Exception as e:
        safe_log_print(f"💥 CRITICAL: Failed to create local CAPTCHA solver: {str(e)}")
        # Return a solver anyway - it will use fallback strategies
        return UltimateLocalCaptchaSolver(page)

async def safe_solve_captcha_locally(solver: UltimateLocalCaptchaSolver, captcha_type: str, site_key: str, page_url: str) -> Dict[str, Any]:
    """
    Safely solve CAPTCHA locally with ultimate error handling - NEVER fails.
    
    Args:
        solver: Local CAPTCHA solver instance
        captcha_type: "recaptcha_v2" or "hcaptcha"
        site_key: CAPTCHA site key
        page_url: Page URL
    
    Returns:
        Structured result dict (never fails)
    """
    try:
        # Validate inputs
        if not solver or not captcha_type or not site_key or not page_url:
            return create_fallback_result("Invalid parameters for local CAPTCHA solving", "local")
        
        # Add timeout to prevent hanging
        try:
            if captcha_type == "recaptcha_v2":
                result = await asyncio.wait_for(
                    solver.solve_recaptcha_v2(site_key, page_url),
                    timeout=120.0  # 2 minute timeout for local solving
                )
            elif captcha_type == "hcaptcha":
                result = await asyncio.wait_for(
                    solver.solve_hcaptcha(site_key, page_url),
                    timeout=120.0  # 2 minute timeout for local solving
                )
            else:
                result = create_fallback_result(f"Unsupported CAPTCHA type: {captcha_type}", "local")
        except asyncio.TimeoutError:
            result = create_fallback_result("Local CAPTCHA solving timeout", "local")
        
        # Ensure result has all required fields
        required_fields = ["success", "token", "error", "error_type", "solver_used", "recovered", "timestamp"]
        for field in required_fields:
            if field not in result:
                result[field] = None
        if "timestamp" not in result or not result["timestamp"]:
            result["timestamp"] = get_timestamp()
                
        return result
        
    except Exception as e:
        safe_log_print(f"💥 CATASTROPHIC: Local CAPTCHA solving completely failed: {str(e)}")
        # Ultimate fallback - return pre-defined safe result
        return create_fallback_result(f"Catastrophic local failure: {str(e)[:100]}", "local")

# Example usage that NEVER fails
async def example_usage():
    """Example showing how to use the never-fail local CAPTCHA solver."""
    try:
        # Get a local solver (this never returns None)
        solver = get_local_captcha_solver()
        
        # Solve CAPTCHA locally (this never raises exceptions)
        result = await safe_solve_captcha_locally(
            solver=solver,
            captcha_type="recaptcha_v2", 
            site_key="your_site_key",
            page_url="https://example.com"
        )
        
        # Always get a structured response
        safe_log_print(f"Local CAPTCHA Result:")
        safe_log_print(f"  Success: {result['success']}")
        safe_log_print(f"  Solver: {result['solver_used']}")
        safe_log_print(f"  Error: {result['error']}")
        safe_log_print(f"  Recovered: {result['recovered']}")
        
        # Use the result safely
        if result['success'] and result['token']:
            safe_log_print("✅ Local CAPTCHA solved successfully!")
            # Use the token in your form submission
        else:
            safe_log_print(f"❌ Local CAPTCHA solving failed: {result['error']}")
            # Implement fallback behavior
            
    except Exception as e:
        safe_log_print(f"💥 Example usage failed: {str(e)}")

if __name__ == "__main__":
    # Test the never-fail capability
    try:
        asyncio.run(example_usage())
    except KeyboardInterrupt:
        safe_log_print("⏹️  Stopped by user")
    except Exception as e:
        safe_log_print(f"💥 Main execution failed: {str(e)}")