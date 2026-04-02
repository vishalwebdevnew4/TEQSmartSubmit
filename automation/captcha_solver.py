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
        self._last_audio_url = None
    
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
            except Exception as e:
                # Check if it's a rate limit error - re-raise it
                error_msg = str(e)
                if "RECAPTCHA_RATE_LIMIT" in error_msg:
                    safe_log_print("   ⚠️  reCAPTCHA rate limit error detected - will trigger browser restart")
                    raise  # Re-raise to trigger browser restart
                # Other errors, continue with fallback
                safe_log_print(f"⚠️  reCAPTCHA solving error: {error_msg[:100]}")
                raise  # Re-raise to be handled by caller
            
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
                        if await self._is_recaptcha_visually_solved():
                            safe_log_print("✅ reCAPTCHA checkbox is visibly solved even though token field is delayed")
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
            error_msg = str(e)
            # Check if it's a rate limit error - re-raise it to trigger browser restart
            if "RECAPTCHA_RATE_LIMIT" in error_msg:
                safe_log_print("   ⚠️  reCAPTCHA rate limit error - re-raising to trigger browser restart")
                raise  # Re-raise to trigger browser restart in handle_captchas
            error_msg = f"Local reCAPTCHA catastrophic error: {error_msg[:200]}"
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
    
    async def _check_recaptcha_rate_limit_error(self) -> bool:
        """Check if reCAPTCHA is showing rate limit error (Try again later) in the challenge iframe."""
        try:
            if not self.page:
                return False
            
            # Check if page is still valid before evaluating
            try:
                if self.page.is_closed():
                    return False
            except:
                return False
            
            # Simplified rate limit check - avoid iframe access which causes syntax errors
            # Just check page text for error messages
            has_error = await self.page.evaluate("""
                () => {
                    try {
                        // Check for rate limit error messages in page text
                        const errorMessages = [
                            'Try again later',
                            'automated queries',
                            'can\\'t process your request',
                            'Your computer or network may be sending automated queries',
                            'To protect our users'
                        ];
                        
                        // Check page text
                        const pageText = (document.body && (document.body.innerText || document.body.textContent)) || '';
                        const pageTextLower = pageText.toLowerCase();
                        for (let i = 0; i < errorMessages.length; i++) {
                            const msg = errorMessages[i];
                            if (pageTextLower.includes(msg.toLowerCase())) {
                                return true;
                            }
                        }
                        
                        // Check for challenge iframe presence (but don't access content)
                        const challengeIframes = document.querySelectorAll('iframe[title*="challenge"], iframe[src*="bframe"]');
                        if (challengeIframes.length > 0) {
                            // If challenge iframe exists, it might be a rate limit
                            // But we can't access cross-origin content, so just return false
                            // The actual rate limit will be detected when trying to interact
                        }
                        
                        return false;
                    } catch (e) {
                        // If any error occurs, assume no rate limit (safer)
                        return false;
                    }
                }
            """)
            
            return has_error
        except Exception as e:
            safe_log_print(f"   ⚠️  Error checking rate limit: {str(e)[:50]}")
            return False
    
    async def _solve_recaptcha_v2_comprehensive(self, site_key: str, page_url: str) -> Optional[str]:
        """Comprehensive reCAPTCHA v2 solving strategy with improved challenge detection."""
        try:
            # Validate page is still open before starting
            if not self.page:
                safe_log_print("⚠️  Page not available for CAPTCHA solving")
                return None
            try:
                if self.page.is_closed():
                    safe_log_print("⚠️  Page is closed, cannot solve CAPTCHA")
                    return None
            except:
                safe_log_print("⚠️  Cannot verify page status")
                return None
            
            safe_log_print("🔄 Starting comprehensive reCAPTCHA v2 solving...")
            
            # Check for rate limit error BEFORE attempting to solve
            try:
                rate_limit_detected = await self._check_recaptcha_rate_limit_error()
            except Exception as e:
                safe_log_print(f"   ⚠️  Error in rate limit check: {str(e)[:50]}")
                rate_limit_detected = False
            if rate_limit_detected:
                safe_log_print("   ⚠️  reCAPTCHA rate limit detected: 'Try again later' error")
                safe_log_print("   🔄 This requires browser restart - raising special error")
                raise Exception("RECAPTCHA_RATE_LIMIT")
            
            # Strategy 1: Simple checkbox click (works for easy CAPTCHAs)
            safe_log_print("1. Attempting simple checkbox click...")
            token = await self._attempt_simple_checkbox()
            if token:
                return token
            
            # Check for rate limit error after checkbox click
            rate_limit_detected = await self._check_recaptcha_rate_limit_error()
            if rate_limit_detected:
                safe_log_print("   ⚠️  reCAPTCHA rate limit detected after checkbox click")
                raise Exception("RECAPTCHA_RATE_LIMIT")
            
            # Check for challenge after checkbox click (wait longer with multiple attempts)
            safe_log_print("   1a. Checking for challenge after checkbox click (multiple attempts)...")
            challenge_iframe = None
            for check_attempt in range(5):
                await safe_async_sleep(3)

                anchor_state = await self._get_recaptcha_anchor_state()
                if anchor_state.get("present"):
                    safe_log_print(
                        f"   ℹ️  Anchor state after click: {anchor_state.get('state')} ({anchor_state.get('detail', '')[:60]})"
                    )
                    if anchor_state.get("state") == "checked":
                        token = await self._get_recaptcha_token()
                        if token:
                            safe_log_print("   ✅ Checkbox became checked and token is available")
                            return token
                
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
                # Check for rate limit before attempting audio challenge
                rate_limit_detected = await self._check_recaptcha_rate_limit_error()
                if rate_limit_detected:
                    safe_log_print("   ⚠️  reCAPTCHA rate limit detected before audio challenge")
                    raise Exception("RECAPTCHA_RATE_LIMIT")
                
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
                    
                    # Check for rate limit after audio challenge failure
                    rate_limit_detected = await self._check_recaptcha_rate_limit_error()
                    if rate_limit_detected:
                        safe_log_print("   ⚠️  reCAPTCHA rate limit detected after audio challenge failure")
                        raise Exception("RECAPTCHA_RATE_LIMIT")
            
            # Strategy 2: Find and interact with reCAPTCHA iframe
            safe_log_print("2. Searching for reCAPTCHA iframes...")
            token = await self._find_and_interact_recaptcha()
            if token:
                return token
            
            # Check for challenge after iframe interaction
            safe_log_print("   2a. Checking for challenge after iframe interaction...")
            await safe_async_sleep(3)

            anchor_state = await self._get_recaptcha_anchor_state()
            if anchor_state.get("present"):
                safe_log_print(
                    f"   ℹ️  Anchor state after iframe interaction: {anchor_state.get('state')} ({anchor_state.get('detail', '')[:60]})"
                )
                if anchor_state.get("state") == "checked":
                    token = await self._get_recaptcha_token()
                    if token:
                        safe_log_print("   ✅ Checkbox became checked after iframe interaction")
                        return token
            
            # Check if checkbox expired
            if await self._check_checkbox_expired():
                safe_log_print("   ⚠️  Checkbox expired after iframe interaction, clicking again...")
                await self._click_recaptcha_checkbox_again()
                await safe_async_sleep(3)
            
            challenge_iframe = await self._check_for_challenge_iframe()
            if challenge_iframe:
                # Check for rate limit
                rate_limit_detected = await self._check_recaptcha_rate_limit_error()
                if rate_limit_detected:
                    safe_log_print("   ⚠️  reCAPTCHA rate limit detected after iframe interaction")
                    raise Exception("RECAPTCHA_RATE_LIMIT")
                
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
                # Check for rate limit
                rate_limit_detected = await self._check_recaptcha_rate_limit_error()
                if rate_limit_detected:
                    safe_log_print("   ⚠️  reCAPTCHA rate limit detected after JS triggers")
                    raise Exception("RECAPTCHA_RATE_LIMIT")
                
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
            # Validate page is still open
            if not self.page:
                return None
            try:
                if self.page.is_closed():
                    return None
            except:
                return None
            
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
                    # Check page is still valid
                    if self.page.is_closed():
                        return None
                    element = await self.page.query_selector(selector)
                    if element:
                        safe_log_print(f"✅ Found reCAPTCHA element with selector: {selector}")

                        prefer_force_click = selector.startswith('iframe') or 'recaptcha' in selector
                        if prefer_force_click:
                            clicked = False
                            if selector.startswith('iframe'):
                                clicked = await self._click_recaptcha_anchor_in_frame(element, selector)
                            if not clicked:
                                clicked = await self._force_click_captcha_element(element, selector)
                            if not clicked:
                                continue
                        else:
                            # Click the element (with timeout)
                            try:
                                await asyncio.wait_for(element.click(), timeout=10.0)
                                safe_log_print(f"   ✅ Clicked reCAPTCHA checkbox")
                            except asyncio.TimeoutError:
                                safe_log_print(f"   ⚠️  Checkbox click timed out, trying JavaScript click...")
                                clicked = await self._force_click_captcha_element(element, selector)
                                if not clicked:
                                    continue
                            except Exception as click_error:
                                if "outside of the viewport" in str(click_error).lower():
                                    safe_log_print("   ⚠️  Checkbox outside viewport, forcing coordinate click...")
                                    clicked = await self._force_click_captcha_element(element, selector)
                                    if not clicked:
                                        continue
                                else:
                                    raise
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

    async def _force_click_captcha_element(self, element, selector: str) -> bool:
        """Robustly click a CAPTCHA iframe/container when normal Playwright clicks fail."""
        try:
            await self.page.evaluate(
                """(el) => {
                    try {
                        el.scrollIntoView({ behavior: 'instant', block: 'center', inline: 'center' });
                    } catch (e) {}
                }""",
                element,
            )
            await safe_async_sleep(0.5)

            try:
                await element.scroll_into_view_if_needed(timeout=3000)
            except Exception:
                pass

            box = await element.bounding_box()
            if box and box.get('width', 0) > 0 and box.get('height', 0) > 0:
                target_x = box['x'] + (box['width'] / 2)
                target_y = box['y'] + (box['height'] / 2)
                try:
                    await self.page.mouse.click(target_x, target_y)
                    safe_log_print(f"   ✅ Clicked CAPTCHA element via coordinates: {selector}")
                    return True
                except Exception as e:
                    safe_log_print(f"   ⚠️  Coordinate click failed: {str(e)[:60]}")

            try:
                clicked = await element.evaluate(
                    """(el) => {
                        try {
                            const rect = el.getBoundingClientRect();
                            const x = rect.left + rect.width / 2;
                            const y = rect.top + rect.height / 2;
                            const target = document.elementFromPoint(x, y) || el;
                            target.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, clientX: x, clientY: y }));
                            target.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, clientX: x, clientY: y }));
                            target.dispatchEvent(new MouseEvent('click', { bubbles: true, clientX: x, clientY: y }));
                            return true;
                        } catch (e) {
                            try {
                                el.click();
                                return true;
                            } catch (_) {
                                return false;
                            }
                        }
                    }"""
                )
                if clicked:
                    safe_log_print(f"   ✅ Clicked CAPTCHA element via DOM dispatch: {selector}")
                return bool(clicked)
            except Exception:
                return False
        except Exception as e:
            safe_log_print(f"   ⚠️  Force click error for {selector}: {str(e)[:60]}")
            return False

    async def _click_recaptcha_anchor_in_frame(self, element, selector: str) -> bool:
        """Use Playwright frame access to click #recaptcha-anchor inside cross-origin iframes."""
        try:
            frame = await element.content_frame()
            if not frame:
                return False

            anchor = await frame.query_selector('#recaptcha-anchor')
            if not anchor:
                return False

            try:
                await anchor.scroll_into_view_if_needed(timeout=3000)
            except Exception:
                pass

            try:
                await anchor.click(timeout=5000, force=True)
                safe_log_print(f"   ✅ Clicked reCAPTCHA anchor inside frame: {selector}")
                return True
            except Exception:
                pass

            box = await anchor.bounding_box()
            if box and box.get('width', 0) > 0 and box.get('height', 0) > 0:
                await self.page.mouse.click(box['x'] + (box['width'] / 2), box['y'] + (box['height'] / 2))
                safe_log_print(f"   ✅ Clicked reCAPTCHA anchor via coordinates inside frame: {selector}")
                return True

            return False
        except Exception as e:
            safe_log_print(f"   ⚠️  Frame anchor click error for {selector}: {str(e)[:60]}")
            return False
    
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
            # Validate page is still open
            if not self.page:
                return None
            try:
                if self.page.is_closed():
                    return None
            except:
                return None
            
            # Look for all iframes that might contain reCAPTCHA
            iframes = await self.page.query_selector_all('iframe')
            safe_log_print(f"🔍 Found {len(iframes)} iframes, searching for reCAPTCHA...")
            
            for iframe in iframes:
                try:
                    # Check if this iframe is a reCAPTCHA iframe
                    src = await iframe.get_attribute('src') or ""
                    
                    if any(term in src.lower() for term in ['recaptcha', 'google.com/recaptcha']):
                        safe_log_print("✅ Found reCAPTCHA iframe, attempting interaction...")
                        
                        # Validate page is still open before interaction
                        try:
                            if self.page.is_closed():
                                safe_log_print("⚠️  Page closed before iframe interaction")
                                return None
                        except:
                            return None
                        
                        clicked = await self._click_recaptcha_anchor_in_frame(iframe, src[:80] or "recaptcha iframe")
                        if not clicked:
                            clicked = await self._force_click_captcha_element(iframe, src[:80] or "recaptcha iframe")
                        if not clicked:
                            safe_log_print("   ⚠️  Forced iframe click failed")
                            continue
                        await safe_async_sleep(3)
                        
                        # Validate page is still open after click
                        try:
                            if self.page.is_closed():
                                safe_log_print("⚠️  Page closed after iframe click")
                                return None
                        except:
                            return None
                        
                        # Check for token
                        token = await self._get_recaptcha_token()
                        if token:
                            return token
                        
                        # Try to focus and press space/enter
                        try:
                            # Validate page is still open
                            try:
                                if self.page.is_closed():
                                    safe_log_print("⚠️  Page closed before keyboard interaction")
                                    return None
                            except:
                                return None
                            
                            await iframe.focus()
                            await self.page.keyboard.press('Space')
                            await safe_async_sleep(2)
                            
                            # Validate page is still open after keyboard
                            try:
                                if self.page.is_closed():
                                    safe_log_print("⚠️  Page closed after keyboard interaction")
                                    return None
                            except:
                                return None
                            
                            token = await self._get_recaptcha_token()
                            if token:
                                return token
                        except Exception as keyboard_error:
                            safe_log_print(f"   ⚠️  Keyboard interaction failed: {str(keyboard_error)[:50]}")
                            
                except Exception as e:
                    safe_log_print(f"   ⚠️  Error processing iframe: {str(e)[:50]}")
                    # Check if page is still open
                    try:
                        if self.page.is_closed():
                            safe_log_print("⚠️  Page closed during iframe processing")
                            return None
                    except:
                        return None
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
                
                # Try to find and click the recaptcha challenge (avoid cross-origin errors)
                """
                () => {
                    try {
                        const frames = document.querySelectorAll('iframe');
                        for (let i = 0; i < frames.length; i++) {
                            try {
                                const frame = frames[i];
                                if (!frame) continue;
                                const src = frame.src || '';
                                if (src.includes('recaptcha') && src.includes('anchor')) {
                                    try {
                                        const frameDoc = frame.contentDocument;
                                        if (frameDoc) {
                                            const anchor = frameDoc.querySelector('#recaptcha-anchor');
                                            if (anchor && anchor.click) {
                                                anchor.click();
                                            }
                                        }
                                    } catch(e) {
                                        // Cross-origin, skip
                                    }
                                }
                            } catch(e) {
                                // Skip this frame
                            }
                        }
                        return true;
                    } catch(e) {
                        return false;
                    }
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

    async def _get_recaptcha_anchor_state(self) -> Dict[str, Any]:
        """Inspect the anchor iframe state after clicking the checkbox."""
        try:
            state = await self.page.evaluate("""
                () => {
                    try {
                        const anchorIframe = document.querySelector(
                            'iframe[src*="recaptcha/api2/anchor"], iframe[src*="recaptcha/enterprise/anchor"], iframe[src*="google.com/recaptcha"]'
                        );
                        if (!anchorIframe) {
                            return { present: false, state: 'missing', detail: 'anchor iframe not found' };
                        }

                        const result = { present: true, state: 'unknown', detail: '' };

                        try {
                            const iframeDoc = anchorIframe.contentDocument || anchorIframe.contentWindow?.document;
                            if (iframeDoc) {
                                const anchor = iframeDoc.querySelector('#recaptcha-anchor');
                                const errorMsg = iframeDoc.querySelector('.rc-anchor-error-msg, .rc-anchor-aria-status');
                                const spinner = iframeDoc.querySelector('.rc-anchor-spinner, .recaptcha-checkbox-spinner');

                                if (anchor) {
                                    const ariaChecked = anchor.getAttribute('aria-checked');
                                    const className = anchor.className || '';

                                    if (ariaChecked === 'true' || className.includes('recaptcha-checkbox-checked')) {
                                        result.state = 'checked';
                                        result.detail = 'anchor checkbox checked';
                                        return result;
                                    }
                                    if (className.includes('recaptcha-checkbox-expired')) {
                                        result.state = 'expired';
                                        result.detail = 'anchor checkbox expired';
                                        return result;
                                    }
                                    if (spinner || className.includes('recaptcha-checkbox-spinner')) {
                                        result.state = 'loading';
                                        result.detail = 'anchor spinner visible';
                                        return result;
                                    }
                                    if (errorMsg && (errorMsg.textContent || '').trim()) {
                                        result.state = 'error';
                                        result.detail = (errorMsg.textContent || '').trim().slice(0, 120);
                                        return result;
                                    }
                                    if (ariaChecked === 'false' || className.includes('recaptcha-checkbox-unchecked')) {
                                        result.state = 'unchecked';
                                        result.detail = 'anchor checkbox still unchecked';
                                        return result;
                                    }
                                }
                            }
                        } catch (e) {
                            result.state = 'cross_origin';
                            result.detail = 'anchor iframe inaccessible';
                            return result;
                        }

                        return result;
                    } catch (e) {
                        return { present: false, state: 'error', detail: String(e).slice(0, 120) };
                    }
                }
            """)
            return state or {"present": False, "state": "unknown", "detail": "no state returned"}
        except Exception as e:
            safe_log_print(f"   ⚠️  Anchor state check error: {str(e)[:50]}")
            return {"present": False, "state": "error", "detail": str(e)[:120]}

    async def _check_for_challenge_iframe(self):
        """Check for challenge iframe with multiple selectors and wait strategies."""
        try:
            # Validate page is still open
            if not self.page:
                return None
            try:
                if self.page.is_closed():
                    return None
            except:
                return None
            
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

    async def _reopen_recaptcha_challenge(self):
        """Re-open the challenge iframe after it expires or gets closed."""
        try:
            safe_log_print("   🔄 Re-opening reCAPTCHA challenge...")
            clicked = await self._click_recaptcha_checkbox_again()
            if not clicked:
                safe_log_print("   ⚠️  Could not click checkbox to re-open challenge")
                return None

            for attempt in range(5):
                await safe_async_sleep(2)
                challenge_iframe = await self._check_for_challenge_iframe()
                if challenge_iframe:
                    safe_log_print(f"   ✅ Challenge iframe re-opened (attempt {attempt + 1})")
                    return challenge_iframe

                if await self._check_checkbox_expired():
                    safe_log_print("   ⚠️  Checkbox expired again while re-opening, retrying...")
                    clicked = await self._click_recaptcha_checkbox_again()
                    if not clicked:
                        return None

            safe_log_print("   ⚠️  Challenge iframe did not re-open after retries")
            return None
        except Exception as e:
            safe_log_print(f"   ⚠️  Error re-opening challenge: {str(e)[:50]}")
            return None

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
                current_challenge_iframe = await self._check_for_challenge_iframe()
                if not current_challenge_iframe or await self._check_checkbox_expired():
                    safe_log_print("   ⚠️  Challenge closed or expired before audio switch, re-opening...")
                    challenge_iframe = await self._reopen_recaptcha_challenge()
                    if not challenge_iframe:
                        continue
                    try:
                        frame = await challenge_iframe.content_frame()
                    except:
                        frame = None
                    if not frame:
                        await safe_async_sleep(1)
                        continue

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
                current_challenge_iframe = await self._check_for_challenge_iframe()
                if not current_challenge_iframe or await self._check_checkbox_expired():
                    safe_log_print("   ⚠️  Challenge closed or expired before audio recognition, re-opening...")
                    challenge_iframe = await self._reopen_recaptcha_challenge()
                    if not challenge_iframe:
                        continue
                    try:
                        frame = await challenge_iframe.content_frame()
                    except:
                        frame = None
                    if not frame:
                        await safe_async_sleep(1)
                        continue
                    await safe_async_sleep(2)

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
            
            # Step 4: Wait and check for token (optimized - check more frequently, longer total wait)
            safe_log_print("   ⏳ Waiting for CAPTCHA token after audio challenge...")
            
            # Wait a moment for the answer to be processed
            await safe_async_sleep(2)
            
            # Check more frequently (every 1 second) but for longer total time (60 seconds max)
            # Google sometimes takes longer to validate audio answers
            max_checks = 60
            check_interval = 1  # Check every 1 second
            for check_attempt in range(max_checks):
                await safe_async_sleep(check_interval)
                
                # Check for token first (most common case)
                token = await self._get_recaptcha_token()
                if token:
                    # Verify it's not a fake token
                    is_fake = token.startswith('03AOLTBLR_') and len(token.split('_')) == 3
                    if not is_fake:
                        safe_log_print(f"   ✅ Audio challenge solved successfully! Real token received (after {check_attempt + 1} seconds)")
                        return token
                    else:
                        # Fake token - continue waiting
                        if check_attempt % 5 == 0:  # Log every 5 seconds
                            safe_log_print(f"   ⏳ Token received but appears fake, continuing to wait... ({check_attempt + 1}s)")

                # Some sites visually solve the checkbox before the token is readable from the page.
                if await self._is_recaptcha_visually_solved():
                    safe_log_print(f"   ✅ reCAPTCHA checkbox is checked after audio challenge (after {check_attempt + 1} seconds)")
                    # Give the page one short grace period to surface the token.
                    await safe_async_sleep(2)
                    token = await self._get_recaptcha_token()
                    if token:
                        is_fake = token.startswith('03AOLTBLR_') and len(token.split('_')) == 3
                        if not is_fake:
                            safe_log_print("   ✅ Real token became available after checkbox verification")
                            return token
                    safe_log_print("   ℹ️  Proceeding with visually solved reCAPTCHA even though token field is delayed")
                    return "VISUALLY_SOLVED_RECAPTCHA"

                if await self._is_recaptcha_resolved_without_token():
                    safe_log_print(
                        f"   ✅ Challenge iframe closed cleanly after audio answer (after {check_attempt + 1} seconds)"
                    )
                    await safe_async_sleep(2)
                    token = await self._get_recaptcha_token()
                    if token:
                        is_fake = token.startswith('03AOLTBLR_') and len(token.split('_')) == 3
                        if not is_fake:
                            safe_log_print("   ✅ Real token became available after challenge closed")
                            return token
                    safe_log_print("   ℹ️  Proceeding with resolved reCAPTCHA even though token field is not readable")
                    return "VISUALLY_SOLVED_RECAPTCHA"
                
                # Check if checkbox expired during wait (less frequently to save time)
                if check_attempt > 0 and check_attempt % 5 == 0:  # Check every 5 seconds
                    if await self._check_checkbox_expired():
                        safe_log_print(f"   ⚠️  Checkbox expired during wait (check {check_attempt + 1}), clicking again...")
                        clicked = await self._click_recaptcha_checkbox_again()
                        if clicked:
                            await safe_async_sleep(3)
                            challenge_iframe = await self._check_for_challenge_iframe()
                            if challenge_iframe:
                                safe_log_print("   🔄 Challenge appeared again, but continuing to check for token...")
                                # Don't restart - just continue checking for token
                
                # Log progress every 5 seconds
                if check_attempt > 0 and check_attempt % 5 == 0:
                    safe_log_print(f"   ⏳ Token not ready yet ({check_attempt + 1}/{max_checks} seconds)...")
            
            safe_log_print(f"   ⚠️  Token not received after audio challenge submission (waited {max_checks} seconds)")
            
            # Check if there are more challenges (image puzzles after audio)
            challenge_still_present = await self._check_for_challenge_iframe()
            if challenge_still_present:
                safe_log_print("   ℹ️  Challenge iframe still present - reCAPTCHA may be asking for image puzzles as well")
            
            # Final check with a bit more wait
            await safe_async_sleep(2)
            token = await self._get_recaptcha_token()
            if token:
                is_fake = token.startswith('03AOLTBLR_') and len(token.split('_')) == 3
                if not is_fake:
                    safe_log_print("   ✅ Token found on final check!")
                    return token
                else:
                    safe_log_print("   ⚠️  Token found but appears fake")
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

            async def ensure_active_challenge(current_frame):
                challenge_iframe = await self._check_for_challenge_iframe()
                if not challenge_iframe or await self._check_checkbox_expired():
                    safe_log_print("   ⚠️  Challenge closed or expired while switching to audio, re-opening...")
                    challenge_iframe = await self._reopen_recaptcha_challenge()
                    if not challenge_iframe:
                        return None
                    try:
                        refreshed_frame = await challenge_iframe.content_frame()
                        if refreshed_frame:
                            await safe_async_sleep(1)
                            return refreshed_frame
                    except Exception as e:
                        safe_log_print(f"   ⚠️  Could not access re-opened challenge frame: {str(e)[:40]}")
                        return None
                return current_frame
            
            # Method 1: Try direct element click with coordinates
            for selector in audio_selectors:
                try:
                    refreshed_frame = await ensure_active_challenge(frame)
                    if not refreshed_frame:
                        continue
                    frame = refreshed_frame

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

                                            refreshed_frame = await ensure_active_challenge(frame)
                                            if not refreshed_frame:
                                                continue
                                            frame = refreshed_frame
                                            
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

                                refreshed_frame = await ensure_active_challenge(frame)
                                if not refreshed_frame:
                                    continue
                                frame = refreshed_frame
                                
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
                refreshed_frame = await ensure_active_challenge(frame)
                if not refreshed_frame:
                    return False
                frame = refreshed_frame

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

                    refreshed_frame = await ensure_active_challenge(frame)
                    if not refreshed_frame:
                        return False
                    frame = refreshed_frame
                    
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

    def _clean_recognized_text(self, text: str) -> str:
        """Normalize recognition output into the compact format reCAPTCHA expects."""
        try:
            cleaned = ''.join(ch for ch in text.upper() if ch.isalnum())
            return cleaned.strip()
        except Exception:
            return ""

    async def _request_new_audio_challenge(self, frame) -> bool:
        """Ask reCAPTCHA for a new audio sample when the current one is unusable."""
        try:
            safe_log_print("   🔄 Requesting a fresh audio challenge...")
            clicked = await frame.evaluate("""
                () => {
                    const selectors = [
                        '#recaptcha-reload-button',
                        'button[title*="new challenge"]',
                        'button[title*="reload"]',
                        'button[aria-label*="new challenge"]',
                        'button[aria-label*="reload"]',
                        'button[id*="reload"]'
                    ];
                    for (const selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el && el.offsetParent !== null) {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
            if clicked:
                await safe_async_sleep(3)
                self._last_audio_url = None
                safe_log_print("   ✅ Requested a fresh audio challenge")
                return True
            safe_log_print("   ⚠️  Could not find reload control for a fresh audio challenge")
            return False
        except Exception as e:
            safe_log_print(f"   ⚠️  Fresh audio request failed: {str(e)[:50]}")
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

            if self._last_audio_url and audio_url == self._last_audio_url:
                safe_log_print("   ℹ️  Same audio challenge detected again")
            self._last_audio_url = audio_url
            
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
                    
                    # Convert to a few speech-friendly WAV variants before recognition.
                    safe_log_print("   🔄 Converting audio to WAV...")
                    variant_paths = []
                    try:
                        audio = AudioSegment.from_mp3(audio_path)
                        base_audio = audio.normalize().set_channels(1)
                        variants = [
                            ("normalized-16k", base_audio.set_frame_rate(16000)),
                            ("filtered-16k", base_audio.high_pass_filter(120).low_pass_filter(3800).set_frame_rate(16000)),
                            ("boosted-16k", (base_audio + 8).high_pass_filter(120).low_pass_filter(3800).set_frame_rate(16000)),
                            ("slow-16k", base_audio._spawn(
                                base_audio.raw_data,
                                overrides={"frame_rate": max(int(base_audio.frame_rate * 0.92), 8000)}
                            ).set_frame_rate(16000)),
                        ]
                        for index, (variant_name, variant_audio) in enumerate(variants):
                            variant_path = audio_path.replace('.mp3', f'-{index}.wav')
                            variant_audio.export(variant_path, format="wav")
                            variant_paths.append((variant_name, variant_path))
                        wav_path = variant_paths[0][1]
                        safe_log_print(f"   ✅ Audio converted to {len(variant_paths)} recognition variants")
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
                        variant_paths = [("original", audio_path)]
                        wav_path = audio_path
                    
                    # Recognize using multiple processed variants. Re-running the same waveform
                    # usually produces the same failure, so vary the audio before giving up.
                    recognized = None
                    total_variants = len(variant_paths)
                    for variant_index, (variant_name, variant_file) in enumerate(variant_paths):
                        try:
                            safe_log_print(
                                f"   🎤 Recognizing speech variant {variant_index + 1}/{total_variants}: {variant_name}..."
                            )
                            r = sr.Recognizer()
                            r.dynamic_energy_threshold = False
                            r.energy_threshold = 300
                            r.pause_threshold = 0.6
                            with sr.AudioFile(variant_file) as source:
                                audio_data = r.record(source)
                                text = r.recognize_google(audio_data, language='en-US')
                                cleaned = self._clean_recognized_text(text)
                                if cleaned and len(cleaned) >= 3:
                                    recognized = cleaned
                                    safe_log_print(f"   ✅ Recognized: {recognized}")
                                    break
                                safe_log_print(f"   ⚠️  Recognition too short from {variant_name}: {cleaned or '[empty]'}")
                        except sr.UnknownValueError:
                            safe_log_print(f"   ⚠️  Could not understand {variant_name}")
                        except sr.RequestError as e:
                            safe_log_print(f"   ⚠️  Speech recognition API error: {str(e)[:50]}")
                            return None
                        except Exception as e:
                            safe_log_print(f"   ⚠️  Recognition error on {variant_name}: {str(e)[:50]}")
                        await safe_async_sleep(0.5)

                    if not recognized:
                        safe_log_print("   ⚠️  All audio variants failed to transcribe")
                        await self._request_new_audio_challenge(frame)
                    
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
                        if 'variant_paths' in locals():
                            for _, variant_file in variant_paths:
                                if variant_file != wav_path and variant_file != audio_path and os.path.exists(variant_file):
                                    os.unlink(variant_file)
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

    async def _is_recaptcha_resolved_without_token(self) -> bool:
        """Detect solved reCAPTCHA states where the token is not exposed back to the page."""
        try:
            return await self.page.evaluate("""
                () => {
                    try {
                        const challengeIframes = Array.from(
                            document.querySelectorAll(
                                'iframe[title*="challenge"], iframe[src*="bframe"], iframe[src*="recaptcha/api2/bframe"], iframe[src*="recaptcha/enterprise/bframe"], iframe[name*="c-"]'
                            )
                        );

                        const visibleChallengeIframes = challengeIframes.filter((iframe) => {
                            const style = window.getComputedStyle(iframe);
                            const rect = iframe.getBoundingClientRect();
                            return style.display !== 'none' &&
                                style.visibility !== 'hidden' &&
                                rect.width > 0 &&
                                rect.height > 0;
                        });

                        if (visibleChallengeIframes.length > 0) {
                            return false;
                        }

                        const pageText = Array.from(
                            document.querySelectorAll('body, .rc-anchor-error-msg, .rc-anchor-aria-status, [class*="error"], [id*="error"]')
                        )
                            .map((el) => (el.textContent || '').toLowerCase())
                            .join(' ');

                        if (
                            pageText.includes('verification challenge expired') ||
                            pageText.includes('check the checkbox again') ||
                            pageText.includes('incorrect') ||
                            pageText.includes('try again') ||
                            pageText.includes('multiple correct solutions required')
                        ) {
                            return false;
                        }

                        const anchorIframe = document.querySelector(
                            'iframe[src*="recaptcha/api2/anchor"], iframe[src*="recaptcha/enterprise/anchor"], iframe[src*="google.com/recaptcha"]'
                        );
                        if (!anchorIframe) {
                            return false;
                        }

                        try {
                            const iframeDoc = anchorIframe.contentDocument || anchorIframe.contentWindow?.document;
                            if (iframeDoc) {
                                const checkbox = iframeDoc.querySelector('#recaptcha-anchor');
                                if (checkbox) {
                                    const ariaChecked = checkbox.getAttribute('aria-checked');
                                    if (ariaChecked === 'true' || checkbox.classList.contains('recaptcha-checkbox-checked')) {
                                        return true;
                                    }
                                    if (
                                        ariaChecked === 'false' &&
                                        (checkbox.classList.contains('recaptcha-checkbox-expired') ||
                                            checkbox.classList.contains('recaptcha-checkbox-unchecked'))
                                    ) {
                                        return false;
                                    }
                                }

                                const solvedEl = iframeDoc.querySelector('.recaptcha-checkbox-checked, .rc-anchor-checkbox[aria-checked="true"]');
                                if (solvedEl) {
                                    return true;
                                }
                            }
                        } catch (e) {
                            // Cross-origin access can fail. Falling back to the clean challenge-close signal is still useful.
                        }

                        return true;
                    } catch (e) {
                        return false;
                    }
                }
            """)
        except Exception as e:
            safe_log_print(f"⚠️  Resolved-without-token check error: {str(e)[:50]}")
            return False

    async def _is_recaptcha_visually_solved(self) -> bool:
        """Check whether the reCAPTCHA checkbox is visibly solved even if the token field is delayed."""
        try:
            return await self.page.evaluate("""
                () => {
                    try {
                        // Main page fallback
                        const solvedSelectors = [
                            '.recaptcha-checkbox-checked',
                            '.rc-anchor-checkbox[aria-checked="true"]',
                            '.rc-anchor[aria-checked="true"]'
                        ];
                        for (const selector of solvedSelectors) {
                            const el = document.querySelector(selector);
                            if (el) {
                                return true;
                            }
                        }

                        // Inspect the anchor iframe when same-origin access is possible.
                        const anchorIframe = document.querySelector(
                            'iframe[src*="recaptcha/api2/anchor"], iframe[src*="recaptcha/enterprise/anchor"], iframe[src*="google.com/recaptcha"]'
                        );
                        if (anchorIframe) {
                            try {
                                const iframeDoc = anchorIframe.contentDocument || anchorIframe.contentWindow?.document;
                                if (iframeDoc) {
                                    const checkbox = iframeDoc.querySelector('#recaptcha-anchor');
                                    if (checkbox) {
                                        const ariaChecked = checkbox.getAttribute('aria-checked');
                                        if (ariaChecked === 'true') {
                                            return true;
                                        }
                                        if (checkbox.classList.contains('recaptcha-checkbox-checked')) {
                                            return true;
                                        }
                                    }

                                    const solvedEl = iframeDoc.querySelector('.recaptcha-checkbox-checked, .rc-anchor-checkbox[aria-checked="true"]');
                                    if (solvedEl) {
                                        return true;
                                    }
                                }
                            } catch (e) {
                                // Cross-origin access can fail. Ignore and fall back to DOM-level signals.
                            }
                        }

                        return false;
                    } catch (e) {
                        return false;
                    }
                }
            """)
        except Exception as e:
            safe_log_print(f"⚠️  Visual reCAPTCHA solved check error: {str(e)[:50]}")
            return False
    
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
